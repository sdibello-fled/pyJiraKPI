import os
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from collections import namedtuple

jira_prisev = namedtuple('JiraKey', ['project', 'severity', 'priority'])


hcmat_user = [
    ("557058:ad419beb-61cf-4589-a3b5-b2ebe3372753", "Greg Addams"),
    ("712020:18104bf1-c9b7-492c-90b3-ab2bb0c69091", "Kevin Coyle"),
    ("712020:1a50b056-6078-41eb-9e06-873395803717", "Dillon Smith"),
]

# this will list all tickets touched by a user 
def create_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def split_list(input_list, size):
    return [input_list[i:i + size] for i in range(0, len(input_list), size)]

def combine_lists(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

def shorten_name(full_name):
    parts = full_name.split()
    if len(parts) > 1:
        return f'{parts[0][0]}{parts[-1]}'
    else:
        return full_name

async def process(user_guid, user_name, start_date, end_date):
        issues = []
        tickets_worked_on = []

        ## this works but not always set up right.
        data = await pull_monthly_user_touched_tickets('HCMAT', user_guid, start_date, end_date)

        # pull the list with logged work        
        if data == None:
            print ("No data returned")
        elif (len(data) > 0):
            for issue in data['issues']:
                key = issue['key'] 
                issues.append(key)
        
            chunks = split_list(issues, 100)
            # get all the work in one statement 
            for chunk in chunks:
                ticket_data = await get_mutiple_keys(chunk)
                if (ticket_data['issues'] != []):
                    tickets_worked_on.append(ticket_data['issues'])
            tickets = combine_lists(tickets_worked_on)
            # get the story points worked on.
            if len(tickets_worked_on) > 0:
                story_points, full_count, empty_count = jira_ticket.sum_points(tickets)
                print (
                    "{0}, {1} - points {2}, pointed/unpointed count {3}/{4}".format(
                        user_name,
                        str(len(tickets)),
                        story_points,
                        full_count,
                        empty_count,
                    )
                )
                for t in tickets:
                    if t['fields']['customfield_10021'] != None:
                        print (f"\t - \t{t['key']} - {t['fields']['summary']}")    

async def main():
    load_dotenv()
    for user_guid, user_name in hcmat_user:
        await process(user_guid, user_name, '2025-07-01', '2025-09-15')


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())    

        
