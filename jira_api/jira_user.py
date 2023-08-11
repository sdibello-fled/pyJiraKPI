import json
import os
import aiohttp


async def list_of_user_by_role(project, role_key = 10400):
        data = await get_user_by_role(project, role_key)
        actors = data['actors']
        #for role in actors:
        #        print('{0} - {1}'.format(role["displayName"], role["actorUser"]["accountId"]))
        return actors

# https://frontlinetechnologies.atlassian.net/rest/api/latest/project/FC/role/10400
# 10400 is developer
async def get_user_by_role(project, key):
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/latest/project/{project}/role/{key}'
        #print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response

# https://frontlinetechnologies.atlassian.net/rest/api/latest/project/FC/role
async def get_roles(project):
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/latest/project/{project}/role/'
        id_list = []
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response
