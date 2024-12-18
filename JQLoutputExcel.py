import asyncio
from openpyxl import Workbook
from dotenv import load_dotenv
from datetime import datetime
from kpi import kpi_query as kpi
import time

## There is an ask to create averaged KPIs for the staff meeting.  I was thinking about capturing all the important KPIs in a local spreadsheet and having it do the work.


def getCreationAndResolutionDate(histories : list) -> tuple:
        resolutiondate = None
        createddate = None
        for item in histories:
                historyevents = item.get('items', [])
                for events in historyevents:
                      if events['field'] == 'resolution':
                           resolutiondate = datetime.strptime(item['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
                           break
        createddate = datetime.strptime(histories[-1]['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
        return (createddate, resolutiondate)

async def main(jql: str, filename: str) -> None:
    load_dotenv()
    start_time = time.time()

    jqlresult = await kpi.combinational_paging_manager_generic_jql(jql, 100, 0)
    data = jqlresult['issues']

    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Jira Issues"

    # Write the header row
    headers = ['Key', 'Summary', 'Status', 'Assignee', 'Parent', 'date_difference_hours', 'createdDate', 'resolutionDate']
    ws.append(headers)

    # Loop through the issues and write the data to the worksheet
    for issue in data:
        fields = issue.get('fields', {})
        assignee = fields.get('assignee')
        parent = fields.get('parent')

        key = issue.get('key')
        issueResult = await kpi.run_issue_by_key_expanded(key, 'changelog')
        issuefields = issueResult['fields']
        issueChangelog = issueResult['changelog']
        histories = issueChangelog.get('histories', [])
        #dates are reversed.
        firstdate = datetime.strptime(histories[-1]['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
        lastdate = datetime.strptime(histories[0]['created'], '%Y-%m-%dT%H:%M:%S.%f%z')

        dateinfo = getCreationAndResolutionDate(histories)
        if dateinfo and dateinfo[1] is not None:
            date_difference = (dateinfo[1] - dateinfo[0]).total_seconds() / 3600
        else:
            date_difference = 0
              
        ws.append([
            issue.get('key', 'N/A'),
            fields.get('summary', 'N/A'),
            fields.get('status', {}).get('name', 'N/A'),
            assignee['displayName'] if assignee else 'Unassigned',
            parent['key'] if parent else 'No Parent',
            date_difference,
            dateinfo[0].strftime('%Y-%m-%d %H:%M:%S') if dateinfo else 'N/A',
            dateinfo[1].strftime('%Y-%m-%d %H:%M:%S') if dateinfo and dateinfo[1] else 'N/A'
        ])

    # Save the workbook to a file
    wb.save(filename)
    elapsed_time = time.time() - start_time
    print(f'The process took {elapsed_time:.2f} seconds to run.')

if __name__ == '__main__':
    jql = 'Project = HCMAT and creator = 557058:a01b4872-0086-4bc3-903e-23f26637afa2'  ## eveything created by Zendesk
    ##jql = 'key = "HCMAT-63032"'
    file = 'C:\\data\\PyData1.xlsx'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(jql, file))