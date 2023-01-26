import os
import json
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from collections import namedtuple


jira_userList = namedtuple('user_List', ['username', 'id'])

async def get_all_issues_user_touched():
        jql = f'project = HCMAT and type in ("Support request", "bug")  and statusCategory = Done and status != Canceled and statusCategoryChangedDate > '2022-01-01' and statusCategoryChangedDate < '2022-12-31''
        return await combinational_paging_manager_generic_jql(jql, False, 100, 0)



def split_severity_project_priority(data):

    ticket_list = []
    #for response in data:
    for i in data['issues']:
        ticket = jira_ticket.jira_ticket_store(False)
        key = ticket.set_raw (i)
        priority = ticket.parse_item_priority()
        severity = ticket.parse_item_severity()
        #print(f'{key} - {priority}, {severity}')
        ticket_list.append(ticket)

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



async def main():       
    load_dotenv()
    #data = await get_HCM_all()
    data = await get_Mine_all()
    parsed_data_rollup = {}
    ticket_list_rollup = {}
    parsed_data = split_severity_project_priority(data)
    print(f'{len(parsed_data)} list')

    parsed_data_rollup, ticket_list_rollup = project_rollup(parsed_data)  
    mykeys = list(parsed_data_rollup.keys())
    mykeys.sort(key = lambda x:x[0])
    sorted_dict = {i: parsed_data_rollup[i] for i in mykeys}
    #print(sorted_dict)         

    for key in sorted_dict:
        print(f'{key} - {parsed_data_rollup[key]} = {ticket_list_rollup[key]}')



if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())    

        