import os
import requests

PRIMEHUB_DOMAIN_NAME = 'primehub-graphql.hub.svc.cluster.local'
if 'PRIMEHUB_DOMAIN_NAME' in os.environ:
    PRIMEHUB_DOMAIN_NAME = os.environ['PRIMEHUB_DOMAIN_NAME']

ME_INFO = None

def __post_api_graphql(query, variables):
    url = 'http://{}/api/graphql'.format(PRIMEHUB_DOMAIN_NAME)
    post_data = {
        'variables': variables,
        'query': query
    }
    response = requests.post(url, data=post_data, headers={'authorization': 'Bearer ' + os.environ['API_TOKEN']})
    return response

def __get_me_info():
    global ME_INFO
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
    variables = '{}'
    result = __post_api_graphql(query, variables)
    if result.status_code != 200:
        print(result.text)
        return

    ME_INFO = result.json()
    if 'data' not in ME_INFO:
        ME_INFO = None
        print('Failed')
        print(result.text)

def get_group_info(group_id):
    global ME_INFO
    if ME_INFO == None:
        __get_me_info()
    
    effective_groups = ME_INFO.get('data', {}).get('me', {}).get('effectiveGroups', [])
    for group in effective_groups:
        if group['id'] == group_id:
            return group
    
    return {}
    
