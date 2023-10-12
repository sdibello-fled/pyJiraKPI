import os
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from collections import namedtuple

jira_prisev = namedtuple('JiraKey', ['project', 'severity', 'priority'])

# this will list all tickets touched by a user 


def process(data):

    ticket_list = []
    #for response in data:
    for i in data['issues']:
        ticket = jira_ticket.jira_ticket_store(False)
        key = ticket.set_raw (i)
        #priority = ticket.parse_item_priority()
        #severity = ticket.parse_item_severity()
        print(f'{key}')
        #ticket_list.append(ticket)

    #FC-14320
    #tuple1 = (overallCount, bugCount, supportRequestCount)
    return ticket_list

def project_rollup(project):
    dict = {}
    item_list = {}
    ticket = project[0]

    for ticket in project:
        key_tuple = jira_prisev(ticket.project, ticket.severity, ticket.priority) 
        if tuple(key_tuple) in dict.keys():
            dict[tuple(key_tuple)] = int(dict[tuple(key_tuple)]) + 1
            item_list[tuple(key_tuple)] = item_list[tuple(key_tuple)] + "," + str(ticket.id) 
        else:
            dict[tuple(key_tuple)] = 1
            item_list[tuple(key_tuple)] = str(ticket.id) 
        
    return dict, item_list

# Jared - 557058:319a2b5d-0cd0-48aa-bd12-14501d0cb896
# This lists all the tickets touched by a user in a year. 


async def main():       
    load_dotenv()
    debug = False
    data = await pull_user_touched_tickets(debug, 'FC', '557058:c1e2242a-4e62-4054-a2cb-91f416b60317', -1 )
    process(data)


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())    

        