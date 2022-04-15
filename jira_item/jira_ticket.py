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


def parse_jira_api_response(data, debugFlag):
    items = jira_ticket_store(debugFlag)
    items = []
    for item in data:
        ticket = parse_issue_type(item, debugFlag)
        items.append(ticket)
    
    return items

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