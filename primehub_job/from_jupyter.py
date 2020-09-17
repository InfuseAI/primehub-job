import os
import os.path
import requests
import inspect
import shelve
import time
from functools import wraps
from types import ModuleType
from datetime import datetime
from cloudpickle import CloudPickler

# MUST: API_TOKEN, GROUP_ID, GROUP_NAME, JUPYTERHUB_USER, INSTANCE_TYPE, IMAGE_NAME
from primehub_job.utils import PRIMEHUB_DOMAIN_NAME, __post_api_graphql
from primehub_job.view import get_view_by_id

REQUIRED_ENVS = ['API_TOKEN', 'GROUP_ID', 'GROUP_NAME', 'JUPYTERHUB_USER', 'INSTANCE_TYPE', 'IMAGE_NAME']


def __check_env_requirements(keys):
    for key in keys:
        if key not in os.environ:
            raise RuntimeError('You must set your {} environment variable.'.format(key))


__check_env_requirements(REQUIRED_ENVS)


CODE_TO_INJECT = \
"""
import shelve
import os
data_in_shelve = shelve.open('shelve_in.dat')

for env_key in data_in_shelve['os_env'].keys():
    if env_key not in os.environ:
        os.environ[env_key] = data_in_shelve['os_env'][env_key]

for key in data_in_shelve:
    if key != 'os_env':
        globals()[key] = data_in_shelve[key]

result = {}.__wrapped__(*args, **kwargs)
data_in_shelve.close()

import os.path
from cloudpickle import CloudPickler
shelve.Pickler = CloudPickler
try:
    data_for_shelve = shelve.open(os.path.join('{}', 'shelve_out.dat'))
    data_for_shelve['result'] = result
    data_for_shelve.close()
except:
    raise RuntimeError("The return value cannot be serialized. If you are going to return a model, please use the framework's saver to save model into file and return the saved path in the function.")
"""


def __check_and_install_primehub_job_code(code_folder):
    check_and_install_code = \
"""
try:
    import primehub_job
except:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', '--user', 'primehub_job'])
"""
    with open(os.path.join(code_folder, 'check_and_install_primehub_job.py'), 'w') as tmp:
        tmp.writelines(check_and_install_code)


def __get_group_volume_name():
    group_name = os.environ['GROUP_NAME']
    return group_name.lower().replace('_', '-')


def __get_phjob_user_folder_path():
    group_volume_name = __get_group_volume_name()
    user_folder = '/home/jovyan/' + group_volume_name + '/phjobs/' + os.environ['JUPYTERHUB_USER']
    return user_folder


def __create_phjob(name, group_id, instance_type, image, command):
    variables = '''{{
                    "data": {{
                        "instanceType": "{}",
                        "groupId": "{}",
                        "image": "{}",
                        "displayName": "{}",
                        "command": "{}"
                    }}
                }}'''.format(instance_type, group_id, image, name, command)
    query = '''mutation ($data: PhJobCreateInput!) {
                    createPhJob(data: $data) {
                        id
                    }
                }'''
    create_job_result = __post_api_graphql(query, variables)
    try:
        create_job_result = create_job_result.json()
        job_id = create_job_result['data']['createPhJob']['id']
    except Exception as e:
        print("Job creation failed due to: {}".format(e))
        print("Please check your API token and instance type name are correct.")
        if create_job_result:
            print("The server response is: ")
            print(create_job_result)
        raise RuntimeError("Job creation failed")

    return job_id


def __get_function_return(job_id):
    data_in_shelve = shelve.open(os.path.join(get_phjob_folder_path(job_id), 'shelve_out.dat'))
    if 'result' not in data_in_shelve:
        raise RuntimeError('We cannot find the return value. Your job might not execute correctly.')
    else:
        return data_in_shelve['result']


def get_phjob(job_id):
    if len(job_id) <= 0:
        raise RuntimeError("Job id length must longer than 0")
    query = '''
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            id
            startTime
            finishTime
            displayName
            phase
            reason
            message
          }
        }
    '''
    variables = '''
        {{
          "where": {{
            "id": "{}"
          }}
        }}
    '''.format(job_id)
    get_job_result = __post_api_graphql(query, variables)
    try:
        get_job_result = get_job_result.json()
        job_info = get_job_result['data']['phJob']
    except Exception as e:
        print("Get job info failed due to: {}".format(e))
        print("Please check your API token and job id are correct.")
        if get_job_result:
            print("The server response is: ")
            print(get_job_result)
        raise RuntimeError("Get job info failed")
    return job_info


def get_phjob_folder_path(job_id):
    return os.path.join(__get_phjob_user_folder_path(), job_id)


def submit_phjob(name='job_submit_from_jupyter', instance_type=os.environ['INSTANCE_TYPE'], image=os.environ['IMAGE_NAME']):
    def decorator(func):
        @wraps(func)
        def warp(*args, **kwargs):
            group_volume_name = __get_group_volume_name()
            group_id = os.environ['GROUP_ID']
            
            if not os.path.exists('/home/jovyan/' + group_volume_name):
                raise RuntimeError('You must have a group shared volume folder.')
            user_folder = __get_phjob_user_folder_path()
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            time_string = datetime.now().strftime("%Y%m%d%H%M%S%f")
            code_folder = os.path.join(user_folder, time_string)
            os.makedirs(code_folder)
            
            shelve.Pickler = CloudPickler
            data_for_shelve = shelve.open(os.path.join(code_folder, 'shelve_in.dat'))
            data_for_shelve['args'] = args
            data_for_shelve['kwargs'] = kwargs
            global_keys = func.__globals__.keys()
            global_vars = func.__globals__
            for key in global_keys:
                if not key.startswith('_') and not key in ['In', 'Out', 'exit', 'quit', 'get_ipython']:
                    if isinstance(global_vars[key], ModuleType) or type(global_vars[key]).__name__ in ['module', 'type', 'function']:
                        data_for_shelve[key] = global_vars[key]
            data_for_shelve['os_env'] = os.environ
            data_for_shelve.close()
            
            execute_code = CODE_TO_INJECT.format(func.__name__, code_folder)
            
            with open(os.path.join(code_folder, 'main.py'), 'w') as tmp:
                tmp.writelines(execute_code)
            
            __check_and_install_primehub_job_code(code_folder)

            job_id = __create_phjob(name, group_id, instance_type, image, "cd " + code_folder + "; python check_and_install_primehub_job.py; python main.py")
            os.symlink(code_folder, os.path.join(user_folder, job_id))
            return job_id
            
        return warp
    return decorator


def get_phjob_result(job_id):
    job_status = get_phjob(job_id)
    if job_status['phase'] == 'Succeeded':
        get_view_by_id(job_id).show(job_status)
        return __get_function_return(job_id)
    else:
        get_view_by_id(job_id).show(job_status)

        
def wait_and_get_phjob_result(job_id):
    last_phase = ''
    last_reason = ''
    last_message = ''
    
    while True:
        job_status = get_phjob(job_id)
        if job_status['phase'] == 'Succeeded':
            get_view_by_id(job_id).show(job_status)
            return __get_function_return(job_id)
        else:
            if last_phase != job_status['phase'] or last_reason != job_status['reason'] or last_message != job_status['message']:
                get_view_by_id(job_id).show(job_status)
                last_phase = job_status['phase']
                last_reason = job_status['reason']
                last_message = job_status['message']
        if last_phase == 'Failed':
            return
        elif last_phase != 'Running':
            time.sleep(10)
        else:
            time.sleep(30)


def get_phjob_logs(job_id, tail_lines=2000):
    url = 'http://{}/api/logs/namespaces/hub/phjobs/{}?tailLines={}'.format(PRIMEHUB_DOMAIN_NAME, job_id, tail_lines)
    response = requests.get(url, headers={'authorization': 'Bearer ' + os.environ['API_TOKEN']})
    return response.text