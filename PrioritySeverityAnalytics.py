import os
import json
import aiohttp
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from collections import namedtuple
import jira_item

jira_prisev = namedtuple('JiraKey', ['project', 'severity', 'priority'])

async def get_HCM_all():
        jql = f'(project in ("HCM: Absence and Time", "Frontline Recruit ", "Frontline Teachers Teachers ", "Business Solutions Data Dev and Eng", "Frontline PG NEW", "ERP-CA (OL5)", "ERP-CA (OL6 / Portal)", "CW-0575 (Accelify)", "Frontline Central ", HRMS, "Frontline Identity Management", Morpheus, "Frontline APIs and Butler", Mobile, SEI-SEG-Tri-State, SEI-SEG-Enrich, SEI-SEG-V5, SEI-SEG-V3, "OH SIS", "EHR Health", "IM Refresh - IHDM", "Software Development", "TipWeb IT - IHDM(Hayes)", "TipWeb IT Mobile - IHDM(Hayes)", "TipWeb IM - IHDM(Hayes)", "Help Desk - IHDM(Hayes)") OR project in (Platform) AND component in ("Team: Rio") AND issuetype != Bug) AND issuetype in ("Support request", Bug, "Support Defect") AND (status in ("Backlog (Project)", Backlog) OR Sprint in (openSprints())) AND priority in ("P1 - Highest", "P2 - High", "P3 - Medium", "P4 - Low")  ORDER BY cf[11000] ASC, Severity ASC, priority DESC, created DESC'
        return await combinational_paging_manager_generic_jql(jql, False, 100, 0)

async def get_Mine_all():
        jql = f'project in ("HCMAT", "FC", "MOB") AND issuetype in ("Support request", Bug, "Support Defect") AND (status in ("Backlog (Project)", Backlog) OR Sprint in (openSprints())) AND priority in ("P1 - Highest", "P2 - High", "P3 - Medium", "P4 - Low") and StatusCategory != Done  ORDER BY cf[11000] ASC, Severity ASC, priority DESC, created DESC'
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

        