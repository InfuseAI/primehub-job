import requests
import json


def fetch_from_graphql(api_endpoint, api_token, query, variables='{}'):
    body = {
        'variables': variables,
        'query': query
    }
    response = requests.post(api_endpoint, headers={'Authorization': 'Bearer ' + api_token}, data=body)
    return json.loads(response.text)


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

