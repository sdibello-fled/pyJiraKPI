import json
import aiohttp
import math
import os

#get the count of bugs.
async def get_escape_velocity(project, start_date, end_date, debug = False):
        jql = f'project="{project}" and createdDate >= "{start_date}" and createdDate < "{end_date}" and type = "bug" and status != Canceled '
        return await run_generic_jql_count(jql, debug)

#get the count of all items touched.
async def get_escape_velocity_comparitor(project, start_date, end_date, debug = False):
        jql = f'project="{project}" and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" and statusCategory in ("In Progress", "Done") and type Not in (Sub-task, Test, Feature)'
        return await run_generic_jql_count(jql, debug)

async def get_gherkin_format(project, sprint_id_array, debug = False):
        ## count the total number of stories in the sprint that are in the gherkin format.
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) AND text ~ "Given*When*Then" and type = "Story" and (summary !~ "\\[Defect\\]" or summary !~ "\\[QA\\]" or summary !~ "\\[Stage\\]")'
        return await run_generic_jql_count(jql, debug)

async def get_total_bug_count(project, debug):
        ## get a list of all sprints
        jql = f'project="{project}" and statusCategory != Done and type in ("bug")'
        return await run_generic_jql_count(jql, debug)

async def get_all_stories(project, sprint_id_array, debug = False):
        ## get a list of all stories - excluding regression bugs with [defect], [qa], [stage] in the summary
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        ##jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) and type = "Story"'
        jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) AND  type = "Story" and (summary !~ "\\[Defect\\]" or summary !~ "\\[QA\\]" or summary !~ "\\[Stage\\]")'
        return await run_generic_jql_count(jql, debug)

async def get_all_soc2_stories(project, start_date, end_date, debug):
    jql = f'project = "{project}" and type not in (test, feature, Sub-task)  and statusCategory = Done and status != Canceled and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" order by key'
    if debug:
        print(f'get-get_all_soc2_stories jql - {jql}')
    return await paging_manager_generic_jql(jql, debug)

async def get_all_backlog_stories(project, debug):
        jql = f'project = {project} and statusCategory = "To Do" and "Story Points[Number]" > 0 and type = "Story"'
        return await combinational_paging_manager_generic_jql(jql, debug)

async def get_all_open_bugs(project, debug):
        jql = f'project = {project} and statusCategory != Done and type = bug'
        return await combinational_paging_manager_generic_jql(jql, debug)

async def get_all_tech_debt(project, sprint_id_array, debug):
    ## get a list of all sprints
    stringlist = map(str, sprint_id_array)
    list_of_ids = ",".join(stringlist)
    jql = f'project = "{project}" and Sprint in ({list_of_ids}) and type = "Technical Debt"'
    return await combinational_paging_manager_generic_jql(jql, debug)

async def get_created_support_defects(project, start_date, end_date, debug):
    jql = f'project="{project}" and createdDate >= "{start_date}" and createdDate < "{end_date}" and type in ("bug", "Support Request")'
    return await combinational_paging_manager_generic_jql(jql, debug)

async def get_completed_support_defects(project, start_date, end_date, debug):
    jql = f'project="{project}" and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" and statusCategory = Done and type in ("bug", "Support Request")'
    return await combinational_paging_manager_generic_jql(jql, debug)

# used in staff meeting only
async def get_bugs_requests_in_sprint_list(project, sprint_id_array, debug = False):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and type in ("Support Request", "Bug")'
        return await combinational_paging_manager_generic_jql(jql, debug)

async def get_big_list_of_all_support(project, debug = False):
    jql = f'project = "{project}" AND (issueType in (Bug) AND "Zendesk Ticket IDs[Paragraph]" is not EMPTY OR issueType in ("Support Request")) AND status not in (Canceled, "Live in Production", Done, Rejected) AND priority in ("P1 - Highest", "P2 - High", "P3 - Medium", "P4 - Low") ORDER BY created DESC, priority'
    return await combinational_paging_manager_generic_jql(jql, debug)

async def get_big_list_of_all_support_requests(project, debug = False):
    jql = f'project = "{project}" AND (issueType in (Bug) AND "Zendesk Ticket IDs[Paragraph]" is not EMPTY OR issueType in ("Support Request")) AND status not in (Canceled, "Live in Production", Done, Rejected) AND priority in ("P1 - Highest", "P2 - High", "P3 - Medium", "P4 - Low") ORDER BY created DESC, priority'
    return await combinational_paging_manager_generic_jql(jql, debug)

async def run_specific_url_count(url, debug = False):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))

    if debug:
        print(url)
    
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url.replace('\\','\\\\'))
        response = await raw.text()
        response = json.loads(response)
     
    return response["total"]        


async def run_generic_jql_count(jql, debug = False):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'

    if debug:
        print(url)
    
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url.replace('\\','\\\\'))
        response = await raw.text()
        response = json.loads(response)
    
    return response["total"]        


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
        startat = page_num * 100 + 1
        additional_response = await run_generic_jql(jql, debug, maxresults, startat)
        all_results.append(additional_response)

    return all_results

### takes the first request of a paging result, and adds the other "issues" results to that one.
### this looks more like a single result with all the issues in it - rather then a list of results that must be paged though
async def combinational_paging_manager_generic_jql(jql, debug = False, maxresults=100, page=0):
    all_issues = []
    first_response = await run_generic_jql(jql, debug, maxresults, page)
    totalPossible = first_response["total"]
    resultCount = first_response["maxResults"]
    all_issues.extend(first_response['issues'])
    page_num = 0

    for x in range(math.ceil(totalPossible/resultCount)-1):
        page_num = page_num + 1
        startat = page_num * 100 + 1
        additional_response = await run_generic_jql(jql, debug, maxresults, startat)
        all_issues.extend(additional_response['issues'])

    first_response['issues'] = all_issues
    return first_response    



async def run_generic_jql(jql, debug , maxresults, page):
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