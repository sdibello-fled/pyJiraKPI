import json
import os
import aiohttp

# this set of functions allows me to figure out who to quiery when looking at a overall project, i.e. when seeing what all users for a jira project are doing. 
# it was better then maintaning a list of all users that have done anything in a project


# allows me to pull a list of all users on a project that have a specific role, defauled to Developer here (10400)
async def list_of_user_by_role(project, role_key = 11504):
        data = await get_user_by_role(project, role_key)
        actors = data['actors']
        return actors

# call the API to get a list of users on a project in a role
# https://frontlinetechnologies.atlassian.net/rest/api/latest/project/FC/role/10400
async def get_user_by_role(project, key):
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/latest/project/{project}/role/{key}'
        #print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response

# get a list of all roles in a project
# not currently used, just making sure we can see this as the role ID is needed in get_user_by_role
# https://frontlinetechnologies.atlassian.net/rest/api/latest/project/FC/role
# this list is scary - as there doesn't seem any ryhm or reason to what is named what. trial and error to find 10400
async def get_roles(project):
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/latest/project/{project}/role/'
        id_list = []
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response
