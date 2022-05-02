import asyncio
from operator import delitem
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi import kpi_query 
import jira_item
import csv


async def main():
        load_dotenv()
        year = 2022
        mon = 3
        debugFlag = False
        trackedProjects = []
        issues = []
        tickets = []
        hcmat = {'project':'HCMAT'}
        fc = {'project':'FC'}
        #trackedProjects.append(hcmat)
        trackedProjects.append(fc)

        for proj in trackedProjects:
            data = await kpi_query.get_all_soc2_stories(proj['project'], '2021-06-01', '2022-03-31', False)
            # go through the list of responeses ( need to pull issues from each one.)
            for api_response in data:
                if api_response['issues']:
                    issues = issues + api_response['issues']

            for issue in issues:
                tickets.append(jira_ticket.parse_issue_type(issue, False))
        
        rows = []
        row = ['Ticket Key', 'Issue Type', 'Priority', 'Summary',  'Ticket Id', 'Status', 'last updated', 'created', 'assignee']
        rows.append(row)
        for ticket in tickets:
            row = [str(ticket.key), str(ticket.issuetype), str(ticket.priority), str(ticket.summary).replace(",", ""), str(ticket.id), str(ticket.status), str(ticket.lastUpdated), str(ticket.createdDate), str(ticket.assignee)]
            rows.append(row)
        #for ticket in tickets:
        #    print(f"{ticket.key},{ticket.issuetype},{ticket.priority},{ticket.summary},{ticket.priority},{ticket.id},{ticket.status},{ticket.sprint}")

        with open ('soc2.csv', 'w', newline='') as csvfile:
            spamwriter  = csv.writer(csvfile, delimiter=',', quotechar='!', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerows(rows)

if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())