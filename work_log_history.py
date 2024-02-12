import asyncio
from operator import delitem
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi import kpi_query 
from jira_api import jira_user
import csv


async def main():
        load_dotenv()
        project = 'FC'
        users = await jira_user.list_of_user_by_role("FC", 10400)

        print ("Start")
        for user in users:
            data = []
            issues = []
            chu = []
            storyPoints = 0
            fullCount = 0
            emptyCount = 0
            data = await kpi_query.get_monthly_tickets_by_worklog(project, user["actorUser"]["accountId"], -6, None)
            # pull the list with logged work        

            for issue in data['issues']:
                key = issue['key'] 
                issues.append(key)
            
            chu = create_chunks(issues, 125)
            # get all the work in one statement 
            tickets_worked_on = await kpi_query.get_mutiple_keys(chu)

            # get the story points worked on.
            if tickets_worked_on != None:
                storyPoints, fullCount, emptyCount = jira_ticket.sum_points(tickets_worked_on['issues'])
                print ("{0}, {1} - points {2}, full/empty count {3}/{4}".format(user["displayName"], str(len(tickets_worked_on['issues'])), storyPoints, fullCount, emptyCount))
            

def create_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())


