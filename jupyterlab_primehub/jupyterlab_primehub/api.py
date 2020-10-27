import requests
import json
import os

def fetch_from_graphql(api_endpoint, api_token, query, variables='{}'):
    body = {
        'variables': variables,
        'query': query
    }
    response = requests.post(api_endpoint, headers={'Authorization': 'Bearer ' + api_token}, data=body)
    try:
        result = json.loads(response.text)
    except Exception as e:
        print(response.text)
        print(e)
        raise RuntimeError('Failed to get graphql response')
    return json.loads(response.text)

def check_function_set(api_endpoint, api_token):
    function_set = {
        'job': False
    }
    # check job function
    query = '''{
        phJobs {
            id
        }
    }'''
    result = fetch_from_graphql(api_endpoint, api_token, query)
    if "data" in result and "error" not in result:
        function_set['job'] = True
    
    return function_set

def group_info(api_endpoint, api_token, group_id):
    query = '''{
            me {
                effectiveGroups {
                    id
                    name
                    displayName
                    quotaCpu
                    quotaGpu
                    quotaMemory
                    projectQuotaCpu
                    projectQuotaGpu
                    projectQuotaMemory
                    instanceTypes {
                        id
                        name
                        displayName
                        description
                        spec
                    }
                    images {
                        id
                        name
                        displayName
                        description
                        useImagePullSecret
                        spec
                    }
                }
            }
        }'''

    result = fetch_from_graphql(api_endpoint, api_token, query)
    effective_groups = result.get('data', {}).get('me', {}).get('effectiveGroups', [])
    for group in effective_groups:
        if group['id'] == group_id:
            return group

    return {}

def submit_job(api_endpoint, api_token, name, group_id, instance_type, image, command):
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
    create_job_result = fetch_from_graphql(api_endpoint, api_token, query, variables)
    try:
        job_id = create_job_result['data']['createPhJob']['id']
    except Exception as e:
        print("Job creation failed due to: {}".format(e))
        print("Please check your API token and instance type name are correct.")
        if create_job_result:
            print("The server response is: ")
            print(create_job_result)
        return {
            'status': 'failed',
            'error': e,
            'server_response': create_job_result
        }

    return {
        'status': 'success',
        'job_id': job_id
    }

def get_env():
    return {
        'group': os.environ.get('GROUP_NAME'),
        'instanceType': os.environ.get('INSTANCE_TYPE'),
        'image': os.environ.get('IMAGE_NAME')
    }
