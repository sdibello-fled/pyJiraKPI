import asyncio
from openpyxl import Workbook
from dotenv import load_dotenv
from kpi import kpi_query as kpi
import time

## There is an ask to create averaged KPIs for the staff meeting.  I was thinking about capturing all the important KPIs in a local spreadsheet and having it do the work.



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
    headers = ['Key', 'Summary', 'Status', 'Assignee', 'Parent']
    ws.append(headers)

    # Loop through the issues and write the data to the worksheet
    for issue in data:
        fields = issue.get('fields', {})
        assignee = fields.get('assignee')
        parent = fields.get('parent')
        ws.append([
            issue.get('key', 'N/A'),
            fields.get('summary', 'N/A'),
            fields.get('status', {}).get('name', 'N/A'),
            assignee['displayName'] if assignee else 'Unassigned',
            parent['key'] if parent else 'No Parent'
        ])

    # Save the workbook to a file
    wb.save(filename)
    elapsed_time = time.time() - start_time
    print(f'The process took {elapsed_time:.2f} seconds to run.')

if __name__ == '__main__':
    jql = 'Project = HCMAT and creator = 557058:a01b4872-0086-4bc3-903e-23f26637afa2'  ## eveything created by Zendesk
    file = 'C:\\data\\PyData.xlsx'
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(jql, file))