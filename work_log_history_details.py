import asyncio
from operator import delitem
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi import kpi_query 
from jira_api import jira_user
from nameparser import HumanName
import jira_item
import csv

class sprint_user_summary:
    #properties
    sprint = ""
    userKey = ""
    tickets = []
    ticketCount = 0
    storyPointTotal = 0

    def __init__(self, sprint, userKey): 
        # constructor
        self.sprint = sprint
        self.userKey = userKey
        self.ticketCount = 0
        self.storyPointTotal = 0

    def add_ticket(self,  ticket:jira_ticket.jira_ticket_store):
        ticket.parse_item_story_points()
        self.tickets.append(ticket)
        self.ticketCount = self.ticketCount + 1
        self.storyPointTotal = self.storyPointTotal + ticket.storyPoints       
         

class query_user_summary:

    # properties
    userName = ""
    userKey= ""
    total_storyPoints = 0
    sus = []

    def __init__(self, name, key): 
        # constructor
        self.userName = name
        self.userKey = key
        self.total_storyPoints = 0

    #def add_ticket(self,  ticket:jira_ticket.jira_ticket_store):
        # find if sprint exists.

        #for spi in self.sus:
             
        
async def main():
        load_dotenv()
        project = 'FC'
        #filter_whitelist = {""}
        filter_blacklist = {}
        users = await jira_user.list_of_user_by_role("FC", 10400)

        print ("Start")
        for user in users:
            #u = query_user_summary(user[0], user[1])
            data = []
            details = []
            memory_list = dict()
            count_list = dict()
            noSprintList = []
            totalStoryPoints = 0
            storyPoints = 0
            fullCount = 0
            emptyCount = 0
            #data = await kpi_query.get_monthly_tickets_by_worklog(project, user["actorUser"]["accountId"], -3, None, False)
            name_parts = HumanName(user["displayName"])
            name_key = name_parts.first[0] + name_parts.last
            #print(name_key)

            if len(filter_whitelist) > 0:
                if name_key not in filter_whitelist:
                     continue
            data = await kpi_query.get_monthly_user_udpated(project, name_key, '2023/06/19', '2023/06/30', False)

            # pull the list with logged work
            if data:
                if 'issues' in data:
                    for issue in data['issues']:
                        issuelog = ""
                        detail = jira_ticket.jira_ticket_store(False)
                        detail.set_raw(issue)
                        detail.parse_item_story_points()
                        detail.parse_item_last_sprint()
                        details.append(detail)
                        #u.add_ticket(details)

                        if detail.storyPoints != None:
                            if detail.sprintName in  memory_list:
                                    memory_list[detail.sprintName] = str(int(memory_list[detail.sprintName]) + int(detail.storyPoints))
                                    count_list[detail.sprintName] = str(int(count_list[detail.sprintName]) + 1)
                            else:
                                memory_list[detail.sprintName] = detail.storyPoints
                                count_list[detail.sprintName] = 1

                            totalStoryPoints = totalStoryPoints + detail.storyPoints
                        else:
                            noSprintList.append(detail.id)
                            if "NoSprint" in memory_list:
                                if detail.storyPoints is not None:
                                    memory_list["NoSprint"] = str(int(memory_list["NoSprint"]) + int(detail.storyPoints))
                                count_list["NoSprint"] = str(int(count_list["NoSprint"]) + 1)
                            else:
                                count_list["NoSprint"] = 1
                                if detail.storyPoints is None:
                                    memory_list["NoSprint"] = '0'
                                else: 
                                    memory_list["NoSprint"] = detail.storyPoints
                             
 
                print( '{0}'.format(user["displayName"]))
                print( 'total tickets worked on {0}'.format(len(data['issues'])))
                print( 'total story points worked on {0}'.format(totalStoryPoints))
                print( 'all non sprint items {0}'.format(noSprintList))
            for sprint_stats in memory_list:
                 print(">> {0} - {1} SP / {2} #".format(sprint_stats, memory_list[sprint_stats], count_list[sprint_stats] ))


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())

