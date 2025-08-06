import os
import asyncio
from datetime import timedelta, date, datetime
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi.kpi_query import *
from collections import namedtuple

jira_prisev = namedtuple('JiraKey', ['project', 'severity', 'priority'])

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

def process(data):

    issues_list = []
    chunks = []
    tickets_worked_on = []
    story_points = 0
    print(f"count{1}".format(len(data)))

    if (len(data) > 0):
        for issue in data['issues']:
            key = issue['key']
            issues_list.append(key)
    
        chunks = split_list(issues_list, 100)
        # get all the work in one statement 
        for chunk in chunks:
            ticket_data = get_mutiple_keys(chunk)
            if (ticket_data['issues'] != []):
                tickets_worked_on.append(ticket_data['issues'])

        tickets = combine_lists(tickets_worked_on)
        # get the story points worked on.
        if len(tickets_worked_on) > 0:
            story_points, full_count, empty_count = jira_ticket.sum_points(tickets)
            print ("{0}, {1} - points {2}, full/empty count {3}/{4}".format(user["displayName"], str(len(tickets)), story_points, full_count, empty_count))
            for t in tickets:
                if t['fields']['customfield_10021'] != None:
                    print (f"\t - \t{t['key']} - {story_points}, {t['fields']['summary']}")    


async def main():       
    load_dotenv()
    data = await pull_user_touched_tickets('HCMAT', '712020:18104bf1-c9b7-492c-90b3-ab2bb0c69091' )
    process(data)


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())    

        