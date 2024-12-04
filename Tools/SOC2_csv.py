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
            data = await kpi_query.get_all_soc2_stories(projectName, '2023-06-01', '2024-06-01')
            # go through the list of responeses ( need to pull issues from each one.)
            print ("Data Acquired")

            for issue in data['issues']:
                tickets.append(jira_ticket.parse_issue_type(issue))
        
            rows = []
            row = ['Ticket Key', 'Issue Type', 'Priority', 'Summary',  'Ticket Id', 'Status', 'last updated', 'created', 'assignee']
            rows.append(row)
            for ticket in tickets:
                row = [str(ticket.key).replace(u'\u200b', ''), str(ticket.issuetype).replace(u'\u200b', ''), str(ticket.priority).replace(u'\u200b', ''), str(ticket.summary).replace(",", "").replace(u'\u200b', ''), str(ticket.id).replace(u'\u200b', ''), str(ticket.status).replace(u'\u200b', ''), str(ticket.lastUpdated).replace(u'\u200b', ''), str(ticket.createdDate).replace(u'\u200b', ''), str(ticket.assignee).replace(u'\u200b', '')]
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