import os
import json
import aiohttp
import asyncio
import calendar
import sys
import datetime as dt
import kpi_store
import sprint_velocity_store
from dotenv import load_dotenv


## https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/rapid/charts/sprintreport?rapidViewId=260&sprintId=1728

### massive call here, use carefully
async def get_sprint_details(sprintId, maxresults = 1000):
        url = f'https://frontlinetechnologies.atlassian.net/rest/agile/1.0/sprint/{sprintId}/issue?maxResults={maxresults}'
        return 

async def run_generic_jql(project, jql):
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response        


async def get_backlog_issues(project):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project = {project} and statusCategory = "To Do" and "Story Points[Number]" > 0'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response        

async def get_all_backlog_by_pri(project, priority):
        ## get a list of all sprints
        count = 0
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project = {project} and statusCategory = "To Do" and type not in (test, epic) and priority = {priority}'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
                count = response["total"]
        return count

async def created_support_defects(store, priority):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and createdDate >= "{store.start_date_string}" and createdDate < "{store.end_date_string}" and type = "Support Defect" and priority = "{priority}"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response["total"]

async def completed_support_defects(store, priority):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and statusCategoryChangedDate >= "{store.start_date_string}" and statusCategoryChangedDate < "{store.end_date_string}" and statusCategory = Done and type = "Support Defect" and priority = "{priority}"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response["total"]

async def get_sprint_list(project):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/integration/teamcalendars/sprint/list?jql=project={project}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response                        

async def get_sprint_velocity_report(id, view):        
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/rapid/charts/sprintreport?rapidViewId={view}&sprintId={id}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response                        

async def get_tech_debt(project, sprint_id_array):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" and Sprint in ({listi}) and type = "Technical Debt"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print('jql=> ' + jql)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response        

async def get_gherkin_format(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project = "{project}" AND Sprint in  ({listi}) AND text ~ "Given*When*Then" and type = "Story"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print('jql=> ' + jql)
        aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response      

async def get_all_stories(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project = "{project}" AND Sprint in  ({listi}) AND type = "Story"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print('jql=> ' + jql)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response            

async def calculate_technical_debt(data):
        issues = data['issues']
        total = 0
        for i in issues:
                if 'customfield_10021' in i['fields']:
                        if i['fields']['customfield_10021'] != None:
                                total += i['fields']['customfield_10021']                
        return total

async def get_planning(project):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project = {project} and statusCategory != done and "Story Points[Number]" < 13 and "Story Points[Number]" > 0 and statusCategory = "To Do"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print('jql=> ' + jql)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response["total"]      

async def get_large_planning(project):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project = {project} and statusCategory != done and "Story Points[Number]" >= 13 and statusCategory = "To Do"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response["total"]      

async def count_issues(data):
        issues = data['issues']
        return len(issues)

async def get_sprints_by_month(store):
        jsondata = await get_sprint_list(store.project)
        sprints = jsondata['sprints']
        id_list = []
        for sprint in sprints:
                enddate = sprint['end']
                SprintId = sprint['id']
                s1 = slice(0,8)
                date_time_obj = dt.datetime.strptime(enddate[s1], '%d%m%Y')
                if date_time_obj.month == int(store.month) and date_time_obj.year == int(store.year):
                        if SprintId not in store.sprint_black_list:
                                id_list.append(SprintId)
        
        for id in id_list:
                response = await get_sprint_velocity_report(id, store.rapid_view)
                vstore = await velocity_report_parse(response)
                store.sprints.append(vstore)

        return store

async def velocity_report_parse(sprintsdata):
        data = sprintsdata['contents']
        details = sprintsdata['sprint']
        id = details['id']
        store = sprint_velocity_store.sprint_velocity_store( id )

        if 'value' in data['completedIssuesInitialEstimateSum']:
                store.completed_issue_initial_estimate_sum = data['completedIssuesInitialEstimateSum']['value']
        else:
                store.completed_issue_initial_estimate_sum = 0

        if 'value' in data['completedIssuesEstimateSum']:
               store.completed_issue_estimate_sum = data['completedIssuesEstimateSum']['value']
        else:
                store.completed_issue_estimate_sum= 0

        if 'value' in data['issuesNotCompletedInitialEstimateSum']:
                store.issues_compelted_in_another_sprint_initial_estimate_sum = data['issuesNotCompletedInitialEstimateSum']['value']
        else:
                store.issues_compelted_in_another_sprint_initial_estimate_sum= 0

        if 'value' in data['issuesNotCompletedEstimateSum']:
                store.not_completed_estimate_sum = data['issuesNotCompletedEstimateSum']['value']
        else:
                store.not_completed_estimate_sum= 0

        if 'value' in data['allIssuesEstimateSum']:
                store.all_issue_estimate_sum = data['allIssuesEstimateSum']['value']
        else:
                store.all_issue_estimate_sum= 0

        if 'value' in data['puntedIssuesInitialEstimateSum']:
                store.punted_issue_initial_estimate_sum = data['puntedIssuesInitialEstimateSum']['value']
        else:
                store.punted_issue_initial_estimate_sum= 0

        if 'value' in data['puntedIssuesEstimateSum']:
                store.punted_issue_estimate_sum = data['puntedIssuesEstimateSum']['value']
        else:
                store.punted_issue_estimate_sum= 0

        if 'value' in data['issuesCompletedInAnotherSprintInitialEstimateSum']:
                store.issues_compelted_in_another_sprint_initial_estimate_sum = data['issuesCompletedInAnotherSprintInitialEstimateSum']['value']
        else:
                store.issues_compelted_in_another_sprint_initial_estimate_sum = 0

        if 'value' in data['issuesCompletedInAnotherSprintEstimateSum']:
                store.issues_compelted_in_another_sprint_estimate_sum = data['issuesCompletedInAnotherSprintEstimateSum']['value']
        else:
                store.issues_compelted_in_another_sprint_estimate_sum = 0

        if 'value' in data['issuesNotCompletedInitialEstimateSum']:
                store.not_completed_initial_estimate_sum = data['issuesNotCompletedInitialEstimateSum']['value']
        else:
                store.not_completed_initial_estimate_sum = 0

        details = sprintsdata['sprint']
        store.sprintId = details['id']
        store.sprintName = details['name']
        store.compelted_issues = data['completedIssues']
        store.completed_issue_count = len(store.compelted_issues)
        store.not_completed_issues = data['issuesNotCompletedInCurrentSprint']
        store.not_completed_issue_count = len(store.not_completed_issues)
        store.punted_issues = data['puntedIssues'] 
        store.punted_issue_count =  len(store.punted_issues )
        store.complete_in_another_sprint = data['issuesCompletedInAnotherSprint']
        store.issues_completed_in_another_sprint_count = len(store.complete_in_another_sprint)
        store.issues_added = data['issueKeysAddedDuringSprint']
        store.issues_added_count = len(store.issues_added)

        return store

async def get_escape_velocity(store):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and createdDate >= "{store.start_date_string}" and createdDate < "{store.end_date_string}" and type = "Support Defect"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)

        return response          

async def monthly_bug_count(store):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and createdDate >= "{store.start_date_string}" and createdDate < "{store.end_date_string}" and type = "Bug"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)

        return response                  

async def bug_count(store):
        ## get a list of all bugs for a project that are no closed.
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and statusCategory != Done and type = "Bug"'
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url) 
                response = await raw.text()
                response = json.loads(response)

        return response                  


async def print_csv(store):
        print(' '.join(('sprintId,',
                'sprintName,',
                'completed_issue_count,',
                'completed_issue_initial_estimate_sum,',
                'issuesNotCompletedInitialEstimateSum,',
                'issuesNotCompletedEstimateSum,',
                'allIssuesEstimateSum,',
                'puntedIssuesInitialEstimateSum,',
                'puntedIssuesEstimateSum,',
                'issuesCompletedInAnotherSprintInitialEstimateSum,',
                'issuesCompletedInAnotherSprintEstimateSum,',
                'completedCount,',
                'issuesNotCompletedInCurrentSprintCount,',
                'puntedIssuesCount,',
                'issuesCompletedInAnotherSprintCount,',
                'issueKeysAddedDuringSprint,',
                'escape_issue_count,',
                'escape_rate,',
                'bug_count,',
                'velocity,',
                'first_time_right,',
                'tech_debt_sp,',
                'planned_less_than_thirteen,',
                'planned_more_than_thirteen,',
                'type_story_count,'
                'gherkin_format_count,',
                'gherkin_kpi,',
                'sprint_churn,',
                'story_points_on_backlog,',
                'sprint_readiness,',
                'created_support_highest,',
                'created_support_high,',
                'created_support_medium,',
                'created_support_low,',
                'completed_support_highest,',
                'completed_support_high,',
                'completed_support_medium,',
                'completed_support_low,'
                'completion_rate'
                )))


        for sprint in store.sprints:
                out_str = ''.join((str(sprint.sprintId),',',
                        sprint.sprintName,',',
                        str(sprint.completed_issue_count),',',
                        str(sprint.completed_issue_initial_estimate_sum),',',
                        str(sprint.not_completed_initial_estimate_sum),',',
                        str(sprint.not_completed_estimate_sum),',',
                        str(sprint.all_issue_estimate_sum),',',
                        str(sprint.punted_issue_initial_estimate_sum),',',
                        str(sprint.punted_issue_estimate_sum),',',
                        str(sprint.issues_compelted_in_another_sprint_initial_estimate_sum),',',
                        str(sprint.issues_compelted_in_another_sprint_estimate_sum),',',
                        str(sprint.completed_issue_count),',',
                        str(sprint.not_completed_issue_count),',',
                        str(sprint.punted_issue_count),',',
                        str(sprint.issues_completed_in_another_sprint_count),',',
                        str(sprint.issues_added_count),',',
                        str(store.escape_velocity_count),',',
                        str(store.escape_velocity_percent),',',
                        str(store.bug_count),',',
                        str(store.velocity),',',
                        str(store.first_time_right),',',
                        str(store.tech_debt_sum),',', 
                        str(store.stories_less_then_thirteen),',',
                        str(store.stories_more_then_thirteen),',',
                        str(store.type_story_count),',',
                        str(store.gherkin_format_count),',',
                        str(store.gherkin_kpi),',',
                        str(store.sprint_churn),',',
                        str(store.sp_total_on_backlog),',',
                        str(store.sprint_readiness),',',
                        str(store.created_support_highest),',',
                        str(store.created_support_high),',',
                        str(store.created_support_medium),',',
                        str(store.created_support_low),',',
                        str(store.completed_support_highest),',',
                        str(store.completed_support_high),',',
                        str(store.completed_support_medium),',',
                        str(store.completed_support_low),',',
                        str(store.completion_rate)
                        ))
                print(out_str)

async def process_additional_kpis(store):
        store.setdates()
        store.update_sums()
        ev_result = await get_escape_velocity(store) 
        store.escape_velocity_count = len(ev_result['issues'])
        store.calculate_escape_velocity()
        bug_result = await bug_count(store)
        store.bug_count = len(bug_result['issues'])
        store.calculate_velocity()
        store.calculate_first_time_right()

        ids = []
        for each in store.sprints:
                ids.append(each.sprintId)

        tech_debt_issues = await get_tech_debt(store.project, ids)
        store.tech_debt_sum = await calculate_technical_debt(tech_debt_issues)
        store.stories_less_then_thirteen = await get_planning(store.project)
        store.stories_more_then_thirteen = await get_large_planning(store.project)
        store.calcuate_ability_to_estimate()

        ## get the gherkin count
        gherkin_response = await get_gherkin_format(store.project, ids)
        store.gherkin_format_count = await count_issues(gherkin_response)

        ## get the count of all "story" type tickets in the sprints.
        story_response = await get_all_stories(store.project, ids)
        store.type_story_count = await count_issues(story_response)
        store.calcuate_gherkin_kpi()

        store.calculate_sprint_churn()

        ## get all backlog items.
        lots = await get_backlog_issues(store.project)
        store.sp_total_on_backlog  = await calculate_technical_debt(lots)

        store.calculate_sprint_readiness()
        store.calculate_completion_rate()
        store.backlog_count_highest = await get_all_backlog_by_pri(store.project, "Highest")
        store.backlog_count_high = await get_all_backlog_by_pri(store.project, "High")
        store.backlog_count_medium = await get_all_backlog_by_pri(store.project, "Medium")
        store.backlog_count_low = await get_all_backlog_by_pri(store.project, "Low")
        store.created_support_highest = await created_support_defects(store, "Highest")
        store.created_support_high = await created_support_defects(store, "High")
        store.created_support_medium = await created_support_defects(store, "Medium")
        store.created_support_low = await created_support_defects(store, "Low")
        store.completed_support_highest = await completed_support_defects(store, "Highest")
        store.completed_support_high = await completed_support_defects(store, "High")
        store.completed_support_medium = await completed_support_defects(store, "Medium")
        store.completed_support_low = await completed_support_defects(store, "Low")

async def main():
        load_dotenv()
        store = kpi_store.kpi_store()
        store.year = 2021
        store.month = 6
        #store.project = 'HCMAT'
        #store.rapid_view = '588'
        store.project = 'FC'
        store.rapid_view = '464'
        store.sprint_black_list = [3152]
        store.sprints = []
        store = await get_sprints_by_month(store)
        await process_additional_kpis(store)
        await print_csv(store)

if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

#asyncio.run(main())
