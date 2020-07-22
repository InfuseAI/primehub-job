import os
import os.path
import requests
import inspect
import shelve
import time
from types import ModuleType
from datetime import datetime
from cloudpickle import CloudPickler

# MUST: API_TOKEN, GROUP_ID, GROUP_NAME, JUPYTERHUB_USER, INSTANCE_TYPE, IMAGE_NAME
# OPTIONAL: PRIMEHUB_DOMAIN_NAME

PRIMEHUB_DOMAIN_NAME = 'primehub-graphql.hub.svc.cluster.local'
if 'PRIMEHUB_DOMAIN_NAME' in os.environ:
    PRIMEHUB_DOMAIN_NAME = os.environ['PRIMEHUB_DOMAIN_NAME']

code_to_inject = \
"""
import shelve
data_in_shelve = shelve.open('shelve_in.dat')
for key in data_in_shelve:
    globals()[key] = data_in_shelve[key]
result = {}(*args, **kwargs)
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

def __post_api_graphql(query, variables):
    url = 'http://{}/api/graphql'.format(PRIMEHUB_DOMAIN_NAME)
    
    if not 'API_TOKEN' in os.environ:
        raise RuntimeWarning('You must set your API TOKEN in the API_TOKEN environment variable.')
        
    post_data = {
        'variables': variables,
        'query': query
    }
    response = requests.post(url, data=post_data, headers={'authorization': 'Bearer ' + os.environ['API_TOKEN']})
    return response

def __get_api_phjob_logs(job_id, tail_lines=2000):
    url = 'http://{}/api/logs/namespaces/hub/phjobs/{}?tailLines={}'.format(PRIMEHUB_DOMAIN_NAME, job_id, tail_lines)
    
    if not 'API_TOKEN' in os.environ:
        raise RuntimeWarning('You must set your API TOKEN in the API_TOKEN environment variable.')
    
    response = requests.get(url, headers={'authorization': 'Bearer ' + os.environ['API_TOKEN']})
    return response
    
def __get_phjob_status(job_id):
    query = '''
        query ($where: PhJobWhereUniqueInput!) {
          phJob(where: $where) {
            id
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
    job_status = __post_api_graphql(query, variables).json()['data']['phJob']
    return job_status

def __get_phjob_user_folder_path():
    group_name = os.environ['GROUP_NAME']
    user_folder = '/home/jovyan/' + group_name + '/phjobs/' + os.environ['JUPYTERHUB_USER']
    return user_folder

def get_phjob_folder_path(job_id):
    return os.path.join(__get_phjob_user_folder_path(), job_id)

def submit_phjob(name='job_submit_from_jupyter', instance_type=os.environ['INSTANCE_TYPE'], image=os.environ['IMAGE_NAME']):
    def decorator(func):
        def warp(*args, **kwargs):
            group_name = os.environ['GROUP_NAME']
            group_id = os.environ['GROUP_ID']
            
            if not os.path.exists('/home/jovyan/' + group_name):
                raise RuntimeWarning('You must have a group shared volume folder.')
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
                if not key.startswith('_') and not key in ['In', 'Out', 'exit', 'quit', 'get_ipython', 'submit_phjob', 'get_phjob_result', 'wait_and_get_phjob_result', 'get_phjob_logs', 'get_phjob_folder_path'] and key != func.__name__:
                    if isinstance(global_vars[key], ModuleType) or type(global_vars[key]).__name__ in ['module', 'type', 'function']:
                        data_for_shelve[key] = global_vars[key]
            data_for_shelve.close()
            
            function_code = 'def ' + inspect.getsource(func).split('def ')[1]
            execute_code = function_code + code_to_inject.format(func.__name__, code_folder)
            
            with open(os.path.join(code_folder, 'main.py'), 'w') as tmp:
                tmp.writelines(execute_code)
                
            variables = '''{{
                                "data": {{
                                    "instanceType": "{}",
                                    "groupId": "{}",
                                    "image": "{}",
                                    "displayName": "{}",
                                    "command": "{}"
                                }}
                            }}'''.format(instance_type, group_id, image, name, "cd " + code_folder + "; python main.py")
            query = '''mutation ($data: PhJobCreateInput!) {
                            createPhJob(data: $data) {
                                id
                            }
                        }'''
            create_job_result = __post_api_graphql(query, variables)
            job_id = create_job_result.json()['data']['createPhJob']['id']
            os.symlink(code_folder, os.path.join(user_folder, job_id))
            
            return job_id
        return warp
    return decorator

def get_phjob_result(job_id):
    job_status = __get_phjob_status(job_id)
    if job_status['phase'] == 'Succeeded':
        data_in_shelve = shelve.open(os.path.join(get_phjob_folder_path(job_id), 'shelve_out.dat'))
        return data_in_shelve['result']
    else:
        print("The job is {}. (Reason: {}, Message: {})".format(job_status['phase'], job_status['reason'], job_status['message']))

        
def wait_and_get_phjob_result(job_id):
    last_phase = ''
    last_reason = ''
    last_message = ''
    
    while True:
        job_status = __get_phjob_status(job_id)
        if job_status['phase'] == 'Succeeded':
            data_in_shelve = shelve.open(os.path.join(get_phjob_folder_path(job_id), 'shelve_out.dat'))
            return data_in_shelve['result']
        else:
            if last_phase != job_status['phase'] or last_reason != job_status['reason'] or last_message != job_status['message']:
                print("The job is {}. (Reason: {}, Message: {})".format(job_status['phase'], job_status['reason'], job_status['message']))
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
    response = __get_api_phjob_logs(job_id, tail_lines)
    return response.text