import asyncio
from operator import delitem
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi import kpi_query 
from datetime import datetime, timezone
import jira_item
import csv

class jira_analytic_year_support:

    # properties
    year = ""
    lastUpdated = ""
    createdDate = ""
    time_open_seconds = ""

    def __init__(self, debugFlag): 
        # constructor
        debugFlag = debugFlag


async def main():
        load_dotenv()      
        trackedProjects = []
        issues = []
        years = []
        tickets = []
        hcmat = {'project':'HCMAT'}
        fc = {'project':'FC'}
        trackedProjects.append(hcmat)
        trackedProjects.append(fc)
        year1 = datetime.now().year
        years = range(year1, year1 - 8, -1)

        for proj in trackedProjects: 
            data = []
            issues = []
            data = await kpi_query.get_big_list_of_all_support(proj['project'])
            # go through the list of responeses ( need to pull issues from each one.)

            for year in years:
                print("====================")
                print(year)
                print("====================")
                startDate = datetime(year, 1, 1).replace(tzinfo=timezone.utc)
                endDate = datetime(year, 12, 31).replace(tzinfo=timezone.utc)
                for issue in data['issues']:
                    ticket = jira_ticket.parse_only_date_information(issue, False)
                    TicketCreated = datetime.strptime(ticket.createdDate, '%Y-%m-%dT%H:%M:%S.%f%z')
                    TicketUpdated = datetime.strptime(ticket.lastUpdated, '%Y-%m-%dT%H:%M:%S.%f%z')
                    if (startDate <= TicketCreated) and (endDate >= TicketCreated):
                        days_diff = abs((TicketCreated - TicketUpdated).days)
                        print(f'{ticket.key} has been open for {days_diff} days')




if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())