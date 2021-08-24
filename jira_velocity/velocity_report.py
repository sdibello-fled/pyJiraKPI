import json
import aiohttp
import datetime as dt

class jira_velocity_report:
    # lists of issues
    completedIssues = []
    issuesNotCompletedInCurrentSprint = []
    puntedIssues = []
    issuesCompletedInAnotherSprint = []
    issueKeysAddedDuringSprint = []

    # jira calculated sums
    completedIssuesInitialEstimateSum = 0
    completedIssuesEstimateSum = 0
    issuesNotCompletedInitialEstimateSum = 0
    issuesNotCompletedEstimateSum = 0
    allIssuesEstimateSum = 0
    puntedIssuesInitialEstimateSum = 0
    puntedIssuesEstimateSum = 0
    issuesCompletedInAnotherSprintInitialEstimateSum = 0
    issuesCompletedInAnotherSprintEstimateSum = 0

    # properties
    id = 0
    view = 0
    sequence = 0
    name = ""
    state = ""
    startDate = ""
    endDate = ""
    completeDate = ""
    isoStartDate = ""
    isoEndDate = ""
    isoCompleteDate = ""
    daysRemaining = 0
    debugFlag = False

    def __init__(self, debugFlag): 
        # constructor
        debugFlag = debugFlag
        

    async def get_sprint_velocity_report(self, jira_user, jira_api_key, id, view):        
            auth = aiohttp.BasicAuth(login = jira_user, password = jira_api_key)
            url = f'https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/rapid/charts/sprintreport?rapidViewId={view}&sprintId={id}'
            if (self.debugFlag == True):
                print(url)
            async with aiohttp.ClientSession(auth=auth) as session:
                    raw = await session.get(url)
                    response = await raw.text()
                    response = json.loads(response)
            return response   

    async def velocity_report_parse(self, sprintsdata):
            data = sprintsdata['contents']
            details = sprintsdata['sprint']

            if 'value' in data['completedIssuesInitialEstimateSum']:
                self.completedIssuesInitialEstimateSum = data['completedIssuesInitialEstimateSum']['value']
            else:
                self.completedIssuesInitialEstimateSum = 0

            if 'value' in data['completedIssuesEstimateSum']:
                self.completedIssuesEstimateSum = data['completedIssuesEstimateSum']['value']
            else:
                self.completedIssuesEstimateSum= 0

            if 'value' in data['issuesNotCompletedInitialEstimateSum']:
                self.issuesNotCompletedInitialEstimateSum = data['issuesNotCompletedInitialEstimateSum']['value']
            else:
                self.issuesNotCompletedInitialEstimateSum= 0

            if 'value' in data['issuesNotCompletedEstimateSum']:
                self.issuesNotCompletedEstimateSum = data['issuesNotCompletedEstimateSum']['value']
            else:
                self.issuesNotCompletedEstimateSum= 0

            if 'value' in data['allIssuesEstimateSum']:
                self.allIssuesEstimateSum = data['allIssuesEstimateSum']['value']
            else:
                self.allIssuesEstimateSum= 0

            if 'value' in data['puntedIssuesInitialEstimateSum']:
                self.puntedIssuesInitialEstimateSum = data['puntedIssuesInitialEstimateSum']['value']
            else:
                self.puntedIssuesInitialEstimateSum= 0

            if 'value' in data['puntedIssuesEstimateSum']:
                self.puntedIssuesEstimateSum = data['puntedIssuesEstimateSum']['value']
            else:
                self.puntedIssuesEstimateSum = 0

            if 'value' in data['issuesCompletedInAnotherSprintInitialEstimateSum']:
                self.issuesCompletedInAnotherSprintInitialEstimateSum = data['issuesCompletedInAnotherSprintInitialEstimateSum']['value']
            else:
                self.issuesCompletedInAnotherSprintInitialEstimateSum = 0

            if 'value' in data['issuesCompletedInAnotherSprintEstimateSum']:
                self.issuesCompletedInAnotherSprintEstimateSum = data['issuesCompletedInAnotherSprintEstimateSum']['value']
            else:
                self.issuesCompletedInAnotherSprintEstimateSum = 0

            if 'value' in data['issuesNotCompletedInitialEstimateSum']:
                self.issuesNotCompletedInitialEstimateSum = data['issuesNotCompletedInitialEstimateSum']['value']
            else:
                self.issuesNotCompletedInitialEstimateSum = 0

            self.sprintId = details['id']
            self.name = details['name']
            self.completedIssues = data['completedIssues']
            self.issuesNotCompletedInCurrentSprint = data['issuesNotCompletedInCurrentSprint']
            self.puntedIssues = data['puntedIssues'] 
            self.issuesCompletedInAnotherSprint = data['issuesCompletedInAnotherSprint']
            self.issueKeysAddedDuringSprint = data['issueKeysAddedDuringSprint']            

            return self



# https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/rapid/charts/sprintreport?rapidViewId=464&sprintId=3325


#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/board/663/version
#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/board/663

#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/board

# lists some sprints on FC, but not a recent one.
#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/board/464/sprint


#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/sprint/1323

#- issues for a sprint
#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/sprint/1323/issue

#https://frontlinetechnologies.atlassian.net/rest/api/2/issue/HCMAT-6805


#https://jira.atlassian.com/rest/api/2/search?jql=project=anerds%20and%20resolution=Duplicate
#https://frontlinetechnologies.atlassian.net/rest/agile/1.0/board/464/settings/refined-velocity

