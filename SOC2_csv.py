import asyncio
from operator import delitem
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi import kpi_query 
import jira_item
import csv

### This is to collect the SOC to changes in jira and produce a  csv to send.

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
        mob = {'project':'MOB'}
        trackedProjects.append(hcmat)
        trackedProjects.append(fc)
        trackedProjects.append(mob)

        print ("Start")
        for proj in trackedProjects:
            data = []
            issues = []
            projectName = proj['project']
            data = await kpi_query.get_all_soc2_stories(projectName, '2023-03-01', '2023-03-31', False)
            # go through the list of responeses ( need to pull issues from each one.)
            print ("Data Acquired")

            for issue in data['issues']:
                tickets.append(jira_ticket.parse_issue_type(issue, False))
        
            rows = []
            row = ['Ticket Key', 'Issue Type', 'Priority', 'Summary',  'Ticket Id', 'Status', 'last updated', 'created', 'assignee']
            rows.append(row)
            for ticket in tickets:
                row = [str(ticket.key), str(ticket.issuetype), str(ticket.priority), str(ticket.summary).replace(",", ""), str(ticket.id), str(ticket.status), str(ticket.lastUpdated), str(ticket.createdDate), str(ticket.assignee)]
                rows.append(row)

            with open (f'soc2-{projectName}.csv', 'w', newline='') as csvfile:
                spamwriter  = csv.writer(csvfile, delimiter=',', quotechar='!', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerows(rows)
            rows.clear()
            tickets.clear()
        print ("Done")

if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())