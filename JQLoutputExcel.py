import os
import operator as op
import asyncio
import datetime as dt
from openpyxl import Workbook
from dotenv import load_dotenv
from kpi import kpi_query as kpi

## There is an ask to create averaged KPIs for the staff meeting.  I was thinking about capturing all the important KPIs in a local spreadsheet and having it do the work.



async def main(jql, filename ):
        load_dotenv()

        jqlresult = await kpi.combinational_paging_manager_generic_jql(jql, 100, 0)
        data = jqlresult['issues']

        # Create a new workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Jira Issues"

        # Write the header row
        headers = ['Key', 'Summary', 'Status', 'Assignee']
        ws.append(headers)

        # Loop through the issues and write the data to the worksheet
        for issue in data:
                issue_key = issue['key']
                issue_summary = issue['fields']['summary']
                issue_status = issue['fields']['status']['name']
                issue_assignee = issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned'
                ws.append([issue_key, issue_summary, issue_status, issue_assignee])

        # Save the workbook to a file
        wb.save(filename)

if __name__ == '__main__':
        jql = 'Project = HCMAT and creator = 557058:a01b4872-0086-4bc3-903e-23f26637afa2 '
        file = 'C:\\data\\PyData.xlsx'
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main(jql, file))