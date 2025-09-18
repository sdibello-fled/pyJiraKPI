import os
import json
import aiohttp
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from art import *
import jira_item

### this was for the Siva staff meeting, to allow me to collect data and update the slide.  This use has fallen off.

class kpi_bug_status_store:
    start_date = ""
    end_date = ""
    month = ""
    year = ""
    rapid_view = ""
    project = ""
    teams = 1
    total_issues_resolved_last4 = 0
    total_bugs_resolved_last4 = 0
    total_requests_resolved_last4 = 0
    total_issues_resolved_last1 = 0

    total_bugs_unresolved = 0
    sprints = []
    active_sprints = []
    sprint_white_list = []
    sprint_black_list = []
    tickets = []


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
        store.active_sprints = []
        store.sprints = []
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


async def bug_count(store):
        ## get a list of all bugs for a project that are no closed.
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        jql = f'project="{store.project}" and statusCategory not in ("Done") and type in ("Bug")'
        return await run_generic_jql(jql, 100, 0)
           
# moving away from sprints - as support is done out of sprints at times.
# not used
async def get_all_tickets_in_sprints(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and issuetype = bug'
        return await combinational_paging_manager_generic_jql(jql, 100, 0)

# moving away from sprints - as support is done out of sprints at times.
# not used
async def get_requests_tickets_not_done_in_sprints(project, sprint_id_array):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and type in ("Support Request", "Bug") and statusCategory != Done'
        return await combinational_paging_manager_generic_jql(jql, 100, 0)

# added a function that returns all of the items, then just counts the priority as a group because paging manager was added
# not used
async def get_priority_tickets_in_sprints(project, sprint_id_array, priority):
        ## get a list of all sprints
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) AND issuetype in ("Support Request", "Bug") AND priority = "{priority}"'
        return await run_generic_jql(jql, 100, 0)


async def get_priority_tickets_not_done(project):
        ## get a list of all sprints
        jql = f'project = "{project}" and issuetype in ("Support Request", "Bug") and statusCategory not in ("To Do", Done)'
        return await combinational_paging_manager_generic_jql(jql)

async def get_request_and_bug_tickets_done_in_sprints(project, sprint_id_array):
        ### HCMAT moved away from this due to use of kanban
        stringlist = map(str, sprint_id_array)
        listi = ",".join(stringlist)
        jql = f'project = "{project}" AND Sprint in ({listi}) and type in ("Support Request", "Bug") and statusCategory = "Done"'
        return await combinational_paging_manager_generic_jql(jql)

async def get_request_and_bug_tickets_done_in_days(project, daysBack):
        jql = f'project = {project} and statusCategory = Done and type in ("Support Request", Bug ) and statusCategoryChangedDate > "-{daysBack}d"'
        return await combinational_paging_manager_generic_jql(jql)

# just gets the count of bugs and support requests in the set of data passed
def count_all_bugs_and_requests(data):
    bugCount = 0
    supportRequestCount = 0
    requestCount = 0
    overallCount = 0
    #for response in data:
    for i in data['issues']:
        typeName = i['fields']['issuetype']['name']
        if typeName == 'Bug':
            bugCount += 1
        elif typeName == 'Support Request':
            supportRequestCount += 1
        else:
            print("Error - different type name then expected " + typeName)
        overallCount += 1
    tuple1 = (overallCount, bugCount, supportRequestCount)
    return tuple1

async def process(data):       
        data = await analyze_sprints(data)
        data.sprints.sort()
        data.active_sprints.sort()
        bugs_requests_data = []
        data.total_issues_resolved_last4 = 0
        data.total_bugs_resolved_last4 = 0
        data.total_requests_resolved_last4 = 0
        requests_bugs_data = []

        sprint_number = data.teams * 4
        # risky reliance on the number of the sprints to sort.
        last_four = data.sprints[-sprint_number:]
        last_four_requests = 0
        last_four_bugs = 0
        last_one_requests = 0
        last_one_defects = 0
        last_four_count = 0
        last_two_count = 0
        total_bug_count = 0
        last_P1_count = 0
        last_P2_count = 0
        last_P3_count = 0
        last_P4_count = 0
        

        last_complete = data.sprints[-data.teams:]

        print("last 5 closed sprints - " + str(data.sprints))
        print("active sprints - "  + str(data.active_sprints))

        #last four - is really last five. ( what i've done in the last sprint ( last 1 ) and the 2 monthes before that ( last 4 ) - 1 + 4 is five.)
        last_four_result = await get_request_and_bug_tickets_done_in_days(data.project, "56")
        data.total_issues_resolved_last4, data.total_bugs_resolved_last4, data.total_requests_resolved_last4 = count_all_bugs_and_requests(last_four_result)

        #last 1 - 14 day sprint - is really last five. ( what i've done in the last sprint ( last 1 ) and the 2 monthes before that ( last 4 ) - 1 + 4 is five.)
        last_one_result =  await get_request_and_bug_tickets_done_in_days(data.project, "14")
        data.total_issues_resolved_last1, data.last_one_defects, data.last_one_requests = count_all_bugs_and_requests(last_one_result)
        last_P1_count, last_P2_count, last_P3_count, last_P4_count = jira_ticket.count_priority(last_one_result)

        ## Don't need to page here, just need the total from the first call.
        total_bug = await bug_count(data)
        total_bug_count += int(total_bug['total'])
        data.total_bugs_unresolved = total_bug_count

        # issues that are not complete here.
        total_bug_notdone = await get_priority_tickets_not_done(data.project) 
        undone_P1_count, undone_P2_count, undone_P3_count, undone_P4_count = jira_ticket.count_priority(total_bug_notdone)

        print(f'resolved {data.project} tickets on the last four sprints {data.total_issues_resolved_last4} - requests = {data.total_requests_resolved_last4} - bugs - {data.total_bugs_resolved_last4} ')
        print(f'resolved {data.project} tickets on the last sprint {data.total_issues_resolved_last1} (defects - {data.last_one_defects}/ requests - {data.last_one_requests})' )
        print(f'unresolved {data.project} tickets  {data.total_bugs_unresolved}')
        print(f'[RESOLVED] last sprint {data.project} P1 tickets P1:{last_P1_count} P2:{last_P2_count}, P3:{last_P3_count}, P4:{last_P4_count}')
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

        data.project = 'FC'
        data.sprint_black_list = [3152, 1301]
        data.sprint_white_list = []
        data.sprints = []
        last_four_count = 0

        Art = text2art("Central")
        print(Art)
        await process(data)

        print ('===========================')

        data.project = 'HCMAT'
        Art = text2art(data.project)
        print(Art)
        await process(data)

        print ('===========================')

        data.project = 'MOB'
        Art = text2art(data.project)
        print(Art)
        await process(data)

if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())