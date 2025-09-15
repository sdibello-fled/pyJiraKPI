import os
import json
import aiohttp
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from art import *
import jira_item

white_labels = ['ATGL', 'US_EWA', 'US_Availability', 'US_React']

# just gets the count of bugs and support requests in the set of data passed
def count_all_bugs_and_requests(data):
    for i in data['issues']:
        typeName = i['fields']['issuetype']['name']
        if typeName == 'Bug':
            bugCount += 1
        elif typeName == 'Support Request':
            supportRequestCount += 1
        else:
            print("Error - different type name then expected " + typeName)
        overallCount += 1
    tuple1 = (overallCount, bugCount, supportRequestCount)
    return tuple1

async def process(data):       
    data = combinational_paging_manager_generic_jql("project = 'HCMAT' and Sprint in openSprints()")
    for i in data['issues']:
        typeName = i['fields']['issuetype']['name']
        label_names = i['fields']['labels']
        status = i['fields']['status']['name']
        
 

async def main():
    load_dotenv()
    process()


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())