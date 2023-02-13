from tkinter import N

from numpy import isin


class jira_ticket_store:

    # properties
    project = ""
    issuetype = ""
    priority = ""
    summary = ""
    parent_key = ""
    id = ""
    priority = ""
    status = ""
    lastUpdated = ""
    assignee = ""
    createdDate = ""
    severity = ""
    raw = ""
    debugFlag = False

    def __init__(self, debugFlag): 
        # constructor
        self.debugFlag = debugFlag

    def set_raw(self, data):
        self.raw = data

        if self.raw['key'] != None:
            self.id = self.raw['key']

        self.project = str(self.id).split("-")[0]

        return str(self.id)
            
    def parse_item_priority(self):

        if self.raw['fields']['priority'] != None:
            value = str(self.raw['fields']['priority']['name'])
            if self.debugFlag == True:
                print( f'{self.id}, Priority -> {value}')
            self.priority = value            

        return value

    def parse_item_severity(self):
        value = "Null"
        if 'customfield_13760' in self.raw['fields']:
            if self.raw['fields']['customfield_13760'] != None:
                if self.raw['fields']['customfield_13760']['value'] != None:
                    value = self.raw['fields']['customfield_13760']['value']
                if self.debugFlag == True:
                    print( f'{self.id}, Severity -> {value}')
        self.severity = value
        return value

    def parse_item_parent_key(self):
        value = "Null"
        if 'parent' in self.raw['fields']:
            if self.raw['fields']['parent']['key'] != None:
                value = self.raw['fields']['parent']['key']
            if self.debugFlag == True:
                print( f'{self.id}, pareny -> {value}')
        self.parent_key = value
        return value



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
def count_priority(data, debugFlag):
    highest = 0
    high = 0
    medium = 0
    low = 0
    memory_list = dict()

    # allow user to send in a list of issues, or the entire response. 
    # if the entire response - then we need to pull out the issues.
    if not isinstance(data, list):
        data = data['issues']

    for ticket in data:
        if ticket['fields']['priority'] != None:
            value = str(ticket['fields']['priority']['name'])
            id = ticket['key']
            if debugFlag == True:
                print( f'{id}, -> {value}')
            if value in  memory_list:
                memory_list[value] = int(memory_list[value]) + 1
            else:
                memory_list[value] = 1

    if "P1 - Highest" in memory_list:
        highest = memory_list["P1 - Highest"]
    else:
        highest = 0

    if "P2 - High" in memory_list:
        high = memory_list["P2 - High"]
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
    
    if debugFlag == True:
        print(f'{highest} - {high} - {medium} - {low}')

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