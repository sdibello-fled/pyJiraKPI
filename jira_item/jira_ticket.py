from tkinter import N


class jira_ticket_store:

    # properties
    key = ""
    issuetype = ""
    priority = ""
    summary = ""
    id = 0
    priority = ""
    status = ""
    lastUpdated = ""
    assignee = ""
    createdDate = ""

    def __init__(self, debugFlag): 
        # constructor
        debugFlag = debugFlag

# helper function to help parse out the api response.
def parse_jira_api_response(data, debugFlag):
    items = jira_ticket_store(debugFlag)
    items = []
    for item in data:
        ticket = parse_issue_type(item, debugFlag)
        items.append(ticket)
    
    return items

# returns a dictionary of the "type" of the issue, and the count to how many of that type there where.
def count_by_type(data):
    count = 0
    memory_list = dict()

    for ticket in data:
        if ticket['fields']['issuetype'] != None:
            value = str(ticket['fields']['issuetype']['name'])
            if value in  memory_list:
                memory_list[value] = int(memory_list[value]) + 1
            else:
                memory_list[value] = 1
    return memory_list

# gives you back a tuple with the count of the priority of all the tickes in data
def count_priority(data):
    highest = 0
    high = 0
    medium = 0
    low = 0
    memory_list = dict()

    for ticket in data:
        if ticket['fields']['priority'] != None:
            value = str(ticket['fields']['priority']['name'])
            if value in  memory_list:
                memory_list[value] = int(memory_list[value]) + 1
            else:
                memory_list[value] = 1

    if "P1 - Highest" in memory_list:
        highest = memory_list["P1 - Highest"]
    else:
        highest = 0

    if " P2 - High" in memory_list:
        high = memory_list[" P2 - High"]
    else:
        high = 0

    if "P3 - Medium" in memory_list:
        medium = memory_list["P3 - Medium"]
    else:
        medium = 0

    if "P4 - Lowest" in memory_list:
        low = memory_list["P4 - Lowest"]
    else:
        low = 0
    
    return highest, high, medium, low

def parse_only_date_information(response, debugFlag):
    issuetype = ""
    jira = jira_ticket_store(debugFlag)
    jira.key = response['key']
    jira.lastUpdated = response['fields']['updated']
    jira.createdDate = response['fields']['created']
    return jira    

def parse_issue_type(response, debugFlag):
    issuetype = ""
    jira = jira_ticket_store(debugFlag)
    jira.key = response['key']
    jira.issuetype = response['fields']['issuetype']['name']
    jira.priority = response['fields']['priority']['name']

    jira.summary = response['fields']['summary']
    jira.id = response['id']
    jira.priority = response['fields']['priority']['name']
    jira.status = response['fields']['status']['name']

    if isinstance(response['fields']['customfield_10019'], list):
        for sprint in response['fields']['customfield_10019']:
            jira.sprint = sprint['name']    # should be the last one.
    else:
        if response['fields']['customfield_10019'] != None:
            jira.sprint = response['fields']['customfield_10019']['name']

    jira.lastUpdated = response['fields']['updated']
    jira.createdDate = response['fields']['created']
    
    if response['fields']['assignee'] != None:
        jira.assignee = response['fields']['assignee']['displayName']


    return jira