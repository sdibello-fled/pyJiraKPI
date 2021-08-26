import json
import aiohttp
import math
import os

async def get_escape_velocity(project, start_date, end_date, debug = False):
        jql = f'project="{project}" and createdDate >= "{start_date}" and createdDate < "{end_date}" and type = "bug" and "Zendesk Ticket Count[Number]" > 0'
        return await run_generic_jql_count(jql, debug)

async def get_gherkin_format(project, sprint_id_array, debug = False):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) AND text ~ "Given*When*Then" and type = "Story"'
        return await run_generic_jql_count(jql, debug)

async def get_all_stories(project, sprint_id_array, debug = False):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) and type = "Story"'
        return await run_generic_jql_count(jql, debug)

async def get_all_backlog_issues(project, debug):
        jql = f'project = {project} and statusCategory = "To Do" and "Story Points[Number]" > 0'
        return await paging_manager_generic_jql(jql, debug)


async def get_all_tech_debt(project, sprint_id_array, debug):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        jql = f'project = "{project}" and Sprint in ({list_of_ids}) and type = "Technical Debt"'
        return await paging_manager_generic_jql(jql, debug)


async def run_generic_jql_count(jql, debug = False):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'

    if debug:
        print(jql)
        print(url)
    
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url)
        response = await raw.text()
        response = json.loads(response)
    
    return response["total"]        

#https://frontlinetechnologies.atlassian.net/rest/api/2/search?maxResults=150&jql=project%20=%20%22HCMAT%22%20AND%20Sprint%20in%20%20(3223,3224,3420)%20and%20type%20=%20%22Story%22&MaxResults=200
#https://frontlinetechnologies.atlassian.net/rest/api/2/search?startAt=1&jql=project%20=%20%22HCMAT%22%20AND%20Sprint%20in%20%20(3223,3224,3420)%20and%20type%20=%20%22Story%22&MaxResults=200


async def paging_manager_generic_jql(jql, debug = False, maxresults=100, page=0):
    all_results = []
    first_response = await run_generic_jql(jql, debug, maxresults, page)
    totalPossible = first_response["total"]
    resultCount = first_response["maxResults"]
    resultPage = first_response["startAt"]
    all_results.append(first_response)
    page_num = 0

    for x in range(math.ceil(totalPossible/resultCount)-1):
        page_num = page_num + 1
        additional_response = await run_generic_jql(jql, debug, maxresults, page_num)
        all_results.append(additional_response)
    return all_results


async def run_generic_jql(jql, debug, maxresults, page):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?maxResults={maxresults}&startAt={page}&jql={jql}'

    if debug:
        print(jql)
        print(url)
    
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url)
        response = await raw.text()
        response = json.loads(response)
    
    return response        