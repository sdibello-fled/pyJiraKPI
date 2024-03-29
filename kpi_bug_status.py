import os
import json
import aiohttp
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv

class kpi_bug_status_store:
    start_date = ""
    end_date = ""
    month = ""
    year = ""
    rapid_view = ""
    project = ""
    teams = 1
    sprints = []
    active_sprints = []
    sprint_white_list = []
    sprint_black_list = []
    total_bugs_resolved_last4 = 0
    total_bugs_resolved_last1 = 0
    total_bugs_unresolved = 0


### massive call here, use carefully
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

async def analyze_sprints(store):
        jsondata = await get_sprint_list(store.project)
        sprints = jsondata['sprints']
        for sprint in sprints:
                sprint_enddate = sprint['end']    # example 08012018045900
                sprint_id = sprint['id']
                is_closed = sprint['closed']
                date_time_obj = datetime.strptime(sprint_enddate, '%d%m%Y%H%M%S')
                # if the sprint is NOT closed - add it to the active sprint list ( there should be 1 per team)
                if is_closed == False:
                        if sprint_id not in store.sprint_black_list:
                                store.active_sprints.append(int(sprint_id))
                # if the sprint is closed, and the end date of the sprint, is greater then the end date in the store object
                elif date_time_obj >= store.end_date: 
                        if sprint_id not in store.sprint_black_list:
                                store.sprints.append(int(sprint_id))
        return store

async def run_generic_jql(project, jql):
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/api/2/search?jql={jql}'
        #print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response        

async def bug_count(store):
        ## get a list of all bugs for a project that are no closed.
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and statusCategory != Done and issuetype = bug'
        return await run_generic_jql(store.project, jql)
           
async def get_all_tickets_in_sprints(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and issuetype = bug'
        return await run_generic_jql(project, jql)

async def get_defects_tickets_in_sprints(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and type in ("Support Request", "Bug")'
        return await run_generic_jql(project, jql)

async def get_requests_tickets_in_sprints(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and type in ("Support Request", "Bug")'
        return await run_generic_jql(project, jql)

async def get_priority_tickets_in_sprints(project, sprint_id_array, priority):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) AND issuetype in ("Support Request", "Bug") AND priority = "{priority}"'
        return await run_generic_jql(project, jql)

async def get_priority_tickets_not_done(project, priority):
        ## get a list of all sprints
        jql = f'project = "{project}" and issuetype in ("Support Request", "Bug") and StatusCategory = "In Progress" And priority = "{priority}"'
        return await run_generic_jql(project, jql)

async def process(data):
        data = await analyze_sprints(data)
        data.sprints.sort()
        data.active_sprints.sort()

        sprint_number = data.teams * 4
        last_four = data.sprints[-sprint_number:]
        last_four_requests = 0
        last_four_defects = 0
        last_one_requests = 0
        last_one_defects = 0

        last_complete = data.sprints[-data.teams:]

        print(data.sprints)
        print(data.active_sprints)

        if data.project == 'HCMAT':
                last_four =  await get_defects_tickets_in_sprints(data.project, last_four)
                last_four_count = int(last_four['total'])
                data.total_bugs_resolved_last4 = last_four_count

        elif data.project == 'FC':
                last_four =  await get_all_tickets_in_sprints(data.project, last_four)
                last_four_count = int(last_four['total'])
                data.total_bugs_resolved_last4 = last_four_count

        requests_data =  await get_requests_tickets_in_sprints(data.project, last_complete)
        last_one_requests = int(requests_data['total'])
        defects_data =  await get_defects_tickets_in_sprints(data.project, last_complete)
        last_one_defects = int(defects_data['total'])

        last_two =  await get_all_tickets_in_sprints(data.project, last_complete)
        last_two_count = int(last_two['total'])
        data.total_bugs_resolved_last1 = last_two_count

        total_bug = await bug_count(data)
        total_bug_count = int(total_bug['total'])
        data.total_bugs_unresolved = total_bug_count

        print(f'resolved {data.project} tickets on the last four sprints {data.total_bugs_resolved_last4} ({last_four_defects}/{last_four_requests})')
        print(f'resolved {data.project} tickets on the last sprint {data.total_bugs_resolved_last1} ({last_one_defects}/{last_one_requests})' )
        print(f'unresolved {data.project} tickets  {data.total_bugs_unresolved}')

        issues = last_two['issues']

        # API fails if you try to run them all in one jql because the maxresults doesn't work on this API.. poo!
        highest =  await get_priority_tickets_in_sprints(data.project, last_complete, "P1 - Highest")
        last_P1_count = int(highest['total'])
        high =  await get_priority_tickets_in_sprints(data.project, last_complete, "P2 - High")
        last_P2_count = int(high['total'])
        Medium =  await get_priority_tickets_in_sprints(data.project, last_complete, "P3 - Medium")
        last_P3_count = int(Medium['total'])
        Low =  await get_priority_tickets_in_sprints(data.project, last_complete, "P4 - Low")
        last_P4_count = int(Low['total'])

        print(f'[RESOLVED] last sprint {data.project} P1 tickets P1:{last_P1_count} P2:{last_P2_count}, P3:{last_P3_count}, P4:{last_P4_count}')

        # API fails if you try to run them all in one jql because the maxresults doesn't work on this API.. poo!
        undone_highest =  await get_priority_tickets_not_done(data.project, "P1 - Highest")
        undone_P1_count = int(undone_highest['total'])
        undone_high =  await get_priority_tickets_not_done(data.project, "P2 - High")
        undone_P2_count = int(undone_high['total'])
        undone_medium =  await get_priority_tickets_not_done(data.project, "P3 - Medium")
        undone_P3_count = int(undone_medium['total'])
        undone_low =  await get_priority_tickets_not_done(data.project, "P4 - Low")
        undone_P4_count = int(undone_low['total'])

        print(f'[IN PROGRESS] {data.project} P1 tickets P1:{undone_P1_count} P2:{undone_P2_count}, P3:{undone_P3_count}, P4:{undone_P4_count}')

async def main():
        load_dotenv()
        data = kpi_bug_status_store()

        # set to how many overall team do work, needed to calculate last four sprints
        data.teams = 2
        # dates reversed, start date is today, or the start date, end date is going back in time.                  
        now = datetime.today()
        enddate = now + timedelta(days=-70)
        data.start_date = now
        data.end_date = enddate

        #data.project = 'HCMAT'
        data.project = 'FC'
        data.sprint_black_list = [3152, 1301]
        data.sprint_white_list = []
        data.sprints = []
        last_four_count = 0

        await process(data)

if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
