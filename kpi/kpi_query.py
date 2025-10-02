import json
import aiohttp
import math
import os
from datetime import datetime
from utils.wrappers import simpleDebug


_headers = {
"Accept": "application/json",
"Content-Type": "application/json"
}

#get the count of bugs.
#added "clones" check, as noida was cloning items multiple times to keep things up to date
@simpleDebug
async def get_escape_velocity(project, start_date, end_date):
        jql = f'project="{project}" and createdDate >= "{start_date}" and createdDate < "{end_date}" and type = "bug" and status != Canceled'
        print(jql)
        return await run_generic_jql_count(jql)

async def get_escape_velocity_HCMCS(start_date, end_date):
        jql = f'project = HCMCS AND type = "Support Defect" AND "Zendesk Brand[Short text]" ~ "Frontline Absence Management"  and createdDate >= "{start_date}" and createdDate < "{end_date}"'
        print(jql)
        return await run_generic_jql_count(jql)

#get a list of all tickets that are tagged with "Cypress"
async def get_automation_tickets(project, start_date, end_date):
        jql = f'project = "{project}" AND summary ~ cypress AND issuetype = Story and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" and statusCategory in ("Done") '
        print(jql)
        return await combinational_paging_manager_generic_jql(jql)

#get the count of all items touched.
async def get_escape_velocity_comparitor(project, start_date, end_date):
        jql = f'project in ("{project}", HCMCS) and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" and statusCategory in ("In Progress", "Done") and type Not in (Sub-task, Test, Epic)'
        return await run_generic_jql_count(jql)

async def get_gherkin_format(project, sprint_id_array):
        ## count the total number of stories in the sprint that are in the gherkin format.
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) AND text ~ "Given*When*Then" and type = "Story" and (summary !~ "\\[Defect\\]" or summary !~ "\\[QA\\]" or summary !~ "\\[Stage\\]")'
        return await run_generic_jql_count(jql)

async def get_total_bug_count(project):
        ## get a list of all sprints
        jql = f'project="{project}" and statusCategory != Done and type in ("bug")'
        return await run_generic_jql_count(jql)

async def get_all_stories(project, sprint_id_array):
        ## get a list of all stories - excluding regression bugs with [defect], [qa], [stage] in the summary
        stringlist = map(str, sprint_id_array)
        list_of_ids = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in  ({list_of_ids}) AND  type = "Story" and (summary !~ "\\[Defect\\]" or summary !~ "\\[QA\\]" or summary !~ "\\[Stage\\]")'
        return await run_generic_jql_count(jql)

# gvien a month
async def get_dtwindow_user_udpated(project, user, start_date, end_date):
    jql = (
    f'project in ({project}, HCMCS) '
    f'AND issuekey in updatedBy({user}, "{start_date}", "{end_date}")'
    )
    try:
        data = await combinational_paging_manager_generic_jql(jql, False)
    except (TypeError, ValueError, KeyError):
        print ("failed {0}".format(user))
        data = None

    return data 

async def get_monthly_tickets_by_selection(project, user, month_start_offset, month_count):
    if month_count is None:
        jql = f'project = {project} AND assignee was in ("{user}")  AND statusCategory = Done AND ( statusCategoryChangedDate >= startOfMonth({month_start_offset})  )'
    else:
        month_end = month_start_offset + month_count
        jql = f'project = {project} AND ( assignee was in ("{user}") OR status changed by "{user}" OR  reporter was in ("{user}"))  AND statusCategory = Done AND statusCategoryChangedDate >= startOfMonth({month_start_offset}) and statusCategoryChangedDate <= endOfMonth({month_end})'
        
    print(jql)
    return await combinational_paging_manager_generic_jql(jql)

async def get_monthly_tickets_by_updatedBy(project, user, start_date, end_date):
    if end_date is None:
        jql = f'project = {project} AND issuekey in updatedBy({user}, "{start_date}")'
    else:
        jql = f'project = {project} AND issuekey in updatedBy({user}, "{start_date}", "{end_date}")'
        
    print(jql)
    return await combinational_paging_manager_generic_jql(jql)

async def get_mutiple_keys(key_list):
    if len(key_list) == 0:
        return None
    key_string = ','.join(key_list)
    jql = f'key in ({key_string})'
    return await combinational_paging_manager_generic_jql(jql)

async def get_monthly_tickets_by_worklog(project, user, month_start_offset, month_count):
    if month_count is None:
        jql = f'project = "{project}" and worklogAuthor = {user} AND worklogDate >= startOfMonth({month_start_offset}) and type not in (Sub-Task)'
    else:
        jql = f'project = "{project}" and worklogAuthor = {user} AND worklogDate >= startOfMonth({month_start_offset}) AND worklogDate <= endOfMonth({month_count}) and type not in (Sub-Task)'
        
    return await combinational_paging_manager_generic_jql(jql)

async def get_yearly_tickets_by_worklog(project, user, year_start_offset, year_count):
    if year_count is None:
        jql = f'project = "{project}" and worklogAuthor = {user} AND worklogDate >= startOfYear({year_start_offset}) and type not in (Sub-Task)'
    else:
        year_end = year_start_offset + year_count
        jql = f'project = "{project}" and worklogAuthor = {user} AND worklogDate >= startOfYear({year_start_offset}) AND worklogDate <= endOfYear({year_end}) and type not in (Sub-Task)'
        
    return await combinational_paging_manager_generic_jql(jql)

async def get_all_soc2_stories(project, start_date, end_date):
    jql = f'project = "{project}" and type not in (test, feature, Sub-task)  and statusCategory = Done and status != Canceled and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" order by key'
    print(jql)
    return await combinational_paging_manager_generic_jql(jql)

async def get_all_backlog_stories(project):
        jql = f'project = {project} and statusCategory = "To Do" and "Story Points[Number]" > 0 and type = "Story"'
        return await combinational_paging_manager_generic_jql(jql)

async def get_all_open_bugs(project):
        jql = f'project = {project} and statusCategory != Done and type = bug'
        return await combinational_paging_manager_generic_jql(jql)

async def get_all_tech_debt(project, sprint_id_array):
    ## get a list of all sprints
    stringlist = map(str, sprint_id_array)
    list_of_ids = ",".join(stringlist)
    jql = f'project = "{project}" and Sprint in ({list_of_ids}) and type = "Technical Debt"'
    return await combinational_paging_manager_generic_jql(jql)

async def get_created_support_defects(project, start_date, end_date):
    jql = f'project="{project}" and createdDate >= "{start_date}" and createdDate < "{end_date}" and type in ("bug", "Support Request")'
    return await combinational_paging_manager_generic_jql(jql)

async def get_completed_support_defects(project, start_date, end_date):
    jql = f'project="{project}" and statusCategoryChangedDate >= "{start_date}" and statusCategoryChangedDate < "{end_date}" and statusCategory = Done and type in ("bug", "Support Request")'
    return await combinational_paging_manager_generic_jql(jql)

# used in staff meeting only
async def get_bugs_requests_in_sprint_list(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and type in ("Support Request", "Bug")'
        return await combinational_paging_manager_generic_jql(jql)

async def get_big_list_of_all_support(project):
    jql = f'project = "{project}" AND (issueType in (Bug) AND "Zendesk Ticket IDs[Paragraph]" is not EMPTY OR issueType in ("Support Request")) AND status not in (Canceled, "Live in Production", Done, Rejected) AND priority in ("P1 - Highest", "P2 - High", "P3 - Medium", "P4 - Low") ORDER BY created DESC, priority'
    return await combinational_paging_manager_generic_jql(jql)

async def get_big_list_of_all_support_requests(project):
    jql = f'project = "{project}" AND (issueType in (Bug) AND "Zendesk Ticket IDs[Paragraph]" is not EMPTY OR issueType in ("Support Request")) AND status not in (Canceled, "Live in Production", Done, Rejected) AND priority in ("P1 - Highest", "P2 - High", "P3 - Medium", "P4 - Low") ORDER BY created DESC, priority'
    return await combinational_paging_manager_generic_jql(jql)

## year offset would be -1 for last year, -2 for the year before
async def get_all_remaps(yearOffset):
    year = str(yearOffset)
    jql = f'created >= startOfyear({year}) AND created <= endOfYear({year}) AND text ~ Remap and project = HCMAT'
    return await combinational_paging_manager_generic_jql(jql)

## unused at the momnt.
async def get_support_in_year_range(project, year_offset, year_gap = 1):
    first_year = str(year_offset)
    behind_first_year = str(year_offset + year_gap)
    jql = f'project = {project} and type in ("Support request", "bug")  and statusCategory = Done and status != Canceled and statusCategoryChangedDate > startOfYear({first_year}) and statusCategoryChangedDate < startOfYear({behind_first_year})'
    return await combinational_paging_manager_generic_jql(jql)

## year offset is relative to the current year.  Should be negative.
async def pull_yearly_user_touched_tickets(project, user_guid, year_offset = 0):
    if year_offset > 0:
        print("A positive year offset doesn't make sense, unless you have a time machine.")
        year_offset = year_offset * -1

    year = str(year_offset)
    jql = f'project = {project} and statusCategoryChangedDate > startOfYear({year}) and statusCategoryChangedDate < endOfYear({year}) and ( worklogAuthor = {user_guid} or assignee = {user_guid})  and type not in (Sub-task) order by statusCategoryChangedDate desc'
    return await combinational_paging_manager_generic_jql(jql)
    
## year offset is relative to the current year.  Should be negative.
async def pull_monthly_user_touched_tickets(project, user_guid, start_date, end_date):
    # Convert a calendar month number (1-12) to a JQL month offset
    # relative to the current month. If an offset (e.g., -1) is passed,
    # use it directly.

    ##jql = (
    ##    f'project in ({project}, HCMCS)'
    ##    f'AND ( worklogAuthor = "{user_guid}" AND worklogDate >= "{start_date}" AND worklogDate < "{end_date}"  '
    ##    f'     OR status CHANGED BY "{user_guid}" AFTER "{start_date}" BEFORE "{end_date}" '
    ##    f'     ) ORDER BY updated DESC'        
    ##)

    jql = (
        f'project in ({project}, HCMCS) '
        f'AND (('
        f'    worklogAuthor = "{user_guid}" '
        f'    AND worklogDate >= {start_date} '
        f'    AND worklogDate <  {end_date} ) '
        f'  OR  ( assignee WAS "{user_guid}" DURING ({start_date}, {end_date}) '
        f' AND ( statusCategory != Done AND statusCategoryChangedDate < startOfYear() ) )  '
        f'  OR  status CHANGED BY "{user_guid}" AFTER  {start_date} BEFORE {end_date} ) '
        #f' AND issuetype NOT IN ("Sub-task")'
        f' ORDER BY updated DESC '
     )
    print(jql)

    return await combinational_paging_manager_generic_jql(jql)

async def run_specific_url_count(url):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url.replace('\\','\\\\'))
        response = await raw.text()
        response = json.loads(response)
     
    return response["total"]        

async def run_issue_by_key_expanded(key: str, expand: str):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest/api/3/issue/{key}?expand={expand}'
  
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url.replace('\\','\\\\'))
        response = await raw.text()
        response = json.loads(response)
    
    return response

async def run_issue_by_key(key):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest/api/3/issue/{key}'
  
    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.get(url.replace('\\','\\\\'))
        response = await raw.text()
        response = json.loads(response)
    
    return response      

async def run_generic_jql_count(jql):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest//rest/api/3/search/approximate-count'
    
    payload = json.dumps( {
    "jql": jql,
    } )

    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.post(url, data=payload, headers=_headers) 
        response = await raw.text()
        response = json.loads(response)

    total = response['count']    

    return total        


### takes the first request of a paging result, and adds the other "issues" results to that one.
### this looks more like a single result with all the issues in it - rather then a list of results that must be paged though
async def combinational_paging_manager_generic_jql(jql, npt=None):
    all_issues = []
    current_response = await run_generic_jql(jql, npt)

    # did the query run
    if "errorMessages" in current_response:
        if current_response['errorMessages'] != None:
            print ("Error in JQL query {0} - {1}".format(jql, current_response['errorMessages']))
            return None

    all_issues.extend(current_response['issues'])

    if current_response['isLast'] == False:
        npt = current_response['nextPageToken']
        current_response = await run_generic_jql(jql, npt)
        all_issues.extend(current_response['issues'])

    current_response['issues'] = all_issues
    return current_response    

async def run_generic_jql(jql, npt=None):
    auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
    url = f'https://frontlinetechnologies.atlassian.net/rest/api/3/search/jql'

    # changing the maxResults doesn't actually seem to do anything.
    # -comment     don't get the comments
    # -attachment  don't get the attachments.
    payload_data =  {
    "expand": "renderedFields",
    "fields": [
        "*all",
        "-comment",
        "-attachment"
    ],
    "fieldsByKeys": "true",
    "jql": jql,
    "maxResults": 100,
    } 

    if npt is not None:
        payload_data["nextPageToken"] = npt

    payload = json.dumps(payload_data)

    async with aiohttp.ClientSession(auth=auth) as session:
        raw = await session.post(url, data=payload, headers=_headers) 
        response = await raw.text()
        response = json.loads(response)
    
    return response        
