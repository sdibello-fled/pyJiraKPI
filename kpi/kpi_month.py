import json
import aiohttp
import os
import datetime as dt
import calendar
from functools import wraps
from . import kpi_query 
import numpy as np  
from utils.wrappers import simpleDebug

# Utility 
class count_by_severity:
    def __init__(self):
        self.low = 0
        self.medium = 0
        self.high = 0
        self.highest = 0

class kpi_month:
    overall_velocity = 0

    def __init__(self, project, year, month, teams, team_desciptor,):
        self.project=project
        self.year=year
        self.month=month
        self.team_count = teams
        self.sprint_id_list = []
        self.abilityToEstimateValue = []
        self.team_descriptor = team_desciptor

        #kpis from spreadsheet
        self.velocity_reports = []
        self.Escape_Velocity = 0
        self.Escape_Velocity_HCMCS = 0
        self.Escape_Velocity_Rate = 0
        self.First_Time_Right = 0

        self.Number_of_Stories = 0
        self.Security_Focus = 0
        self.Sprint_Churn = 0
        self.Sprint_Completion_Rate = 0 
        self.Sprint_Readiness = 0
        self.Sprint_Readiness_Ratio =0
        self.Story_Completion_Rate = 0
        self.Tech_Debt_Paydown = 0
        self.Tech_Debt_Paydown_Ratio =0 
        self.Test_Automation = 0
        self.Test_Automation_Tickets = []
        self.Velocity = 0
        self.Total_Count_Stories_Worked_On = 0
        # items that are project in scope, not team.  Should be moved up
        self.Ability_to_Estimate = 0
        self.Bugs_Count = 0
        self.Gherkin_Story_Rate = 0
        self.Number_Stories_Gherkin_Format = 0
        self.TotalBugCount = 0
        self.CreatedSupportTicketsDuringSprints = None 
        self.CompletedSupportTicketsDuringSprints = None
        self.Tickets_Resolved = count_by_severity()
        self.Tickets_Received = count_by_severity()

        #summed items from the velocity reports
        self.monthly_completedIssuesInitialEstimateSum = 0
        self.monthly_completedIssuesEstimateSum = 0
        self.monthly_issuesNotCompletedInitialEstimateSum = 0
        self.monthly_issuesNotCompletedEstimateSum = 0
        self.monthly_allIssuesEstimateSum = 0
        self.monthly_puntedIssuesInitialEstimateSum = 0
        self.monthly_puntedIssuesEstimateSum = 0
        self.monthly_issuesCompletedInAnotherSprintInitialEstimateSum = 0
        self.monthly_issuesCompletedInAnotherSprintEstimateSum = 0
        self.monthly_count_completedIssues = 0
        self.monthly_count_issuesNotCompletedInCurrentSprint = 0
        self.monthly_count_puntedIssues = 0
        self.monthly_count_issuesCompletedInAnotherSprint = 0
        self.monthly_count_issueKeysAddedDuringSprint = 0
        self.monthly_calc_abilityToEstimate = 0

        #basic date stuff to get data
        last_day_of_month = calendar.monthrange(self.year, self.month)[1]
        self.start_date = f'{self.year}-{self.month}-01'
        self.end_date = f'{self.year}-{self.month}-{last_day_of_month}'


        #TODO - store data in a spreadsheet
        # - by month/year
        # - bulk import style headers

    def create_id_list(self):
        for each in self.velocity_reports:
                self.sprint_id_list.append(each.sprintId)

    def calculate_sprint_churn(self):
        self.Sprint_Churn =  self.monthly_count_puntedIssues / self.monthly_count_completedIssues

    def calculate_automation(self):
         self.Test_Automation = len(self.Test_Automation_Tickets)

    def calculate_sprint_completion_rate(self):
        self.Sprint_Completion_Rate = self.monthly_completedIssuesEstimateSum / self.monthly_completedIssuesInitialEstimateSum 

    # gets a complete list of all stories in the backlog with story points - as they are "ready"
    async def calculate_sprint_readiness(self):
        data = await kpi_query.get_all_backlog_stories(self.project)
        self.Sprint_Readiness += self.total_story_points(data['issues']) / self.Velocity

    # get the list of all the support tickets completed, returns tupal (total count, P1 count, P2 count, P3 count, P4 count)
    async def calculate_completed_support_tickets(self):
        counts = []
        total_overall_count = 0
        total_highest_count = 0
        total_high_count = 0
        total_medium_count = 0
        total_low_count = 0
        data = await kpi_query.get_completed_support_defects(self.project, self.start_date, self.end_date )
        counts.append(self.parse_out_all_bugs(data))
        for count in counts:
            total_overall_count += count[0]
            total_highest_count += count[1]
            total_high_count += count[2]
            total_medium_count += count[3]
            total_low_count += count[4]

        tupCounts = (total_overall_count, total_highest_count, total_high_count, total_medium_count, total_low_count)
        return tupCounts

    # get the list of all the support tickets created, returns tupal (total count, P1 count, P2 count, P3 count, P4 count)
    # basically a copy and paste from above 
    #TODO - refactor this with calculate_completed_support_tickets
    async def calculate_created_support_tickets(self):
        counts = []
        total_overall_count = 0
        total_highest_count = 0
        total_high_count = 0
        total_medium_count = 0
        total_low_count = 0
        data = await kpi_query.get_created_support_defects(self.project, self.start_date, self.end_date )
        counts.append(self.parse_out_all_bugs(data))
        for count in counts:
            total_overall_count += count[0]
            total_highest_count += count[1]
            total_high_count += count[2]
            total_medium_count += count[3]
            total_low_count += count[4]

        tupCounts = (total_overall_count, total_highest_count, total_high_count, total_medium_count, total_low_count)
        return tupCounts
        
    #API call save - instead of doing these as individual calls, just parse the json of a set of records and calculate.
    def parse_out_all_bugs(self, data):
        overall_count = 0
        highest_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        for i in data['issues']:
            overall_count += 1
            if 'priority' in i['fields']:
                if i['fields']['priority'] != None:
                    if i['fields']['priority']['name'] == "P2 - High":
                        high_count += 1
                    elif i['fields']['priority']['name'] == "P1 - Highest":
                        highest_count += 1
                    elif i['fields']['priority']['name'] == "P3 - Medium":
                        medium_count += 1
                    elif i['fields']['priority']['name'] == "P4 - Lowest":
                        low_count += 1

        tuple1 = (overall_count, highest_count, high_count, medium_count, low_count)
        return tuple1

    async def calculate_tech_debt(self):
        data = await kpi_query.get_all_tech_debt(self.project, self.sprint_id_list)
        self.Tech_Debt_Paydown += self.total_story_points(data['issues'])
    
    def calculate_sprint_readiness_ratio(self):
        self.Sprint_Readiness_Ratio = self.Sprint_Readiness / self.Velocity

    def calculate_tech_debt_ratio(self):
        self.Tech_Debt_Paydown_Ratio = self.Tech_Debt_Paydown / self.Velocity

    def total_story_points(self, data):
            total = 0
            for i in data:
                    if 'customfield_10021' in i['fields']:
                            if i['fields']['customfield_10021'] != None:
                                    total += i['fields']['customfield_10021']                
            return total

    async def acquire_group_data(self):
        self.create_id_list()
        self.Escape_Velocity = await kpi_query.get_escape_velocity(self.project, self.start_date, self.end_date)
        self.Escape_Velocity_HCMCS = await kpi_query.get_escape_velocity_HCMCS(self.start_date, self.end_date)
        ##self.Number_Stories_Gherkin_Format = await kpi_query.get_gherkin_format(self.project, self.sprint_id_list)
        ##self.Number_of_Stories = await kpi_query.get_all_stories(self.project, self.sprint_id_list)
        ##self.Gherkin_Story_Rate = self.Number_Stories_Gherkin_Format / self.Number_of_Stories
        self.TotalBugCount = await kpi_query.get_total_bug_count(self.project)
        self.Total_Count_Stories_Worked_On = await kpi_query.get_escape_velocity_comparitor(self.project, self.start_date, self.end_date)    
        ##self.Test_Automation_Tickets = await kpi_query.get_automation_tickets(self.project, self.start_date, self.end_date)   
        self.Escape_Velocity_Rate = (self.Escape_Velocity + self.Escape_Velocity_HCMCS) / self.Total_Count_Stories_Worked_On

    def copy_group_data(self, other):
        self.Escape_Velocity = other.Escape_Velocity
        self.Escape_Velocity_HCMCS = other.Escape_Velocity_HCMCS 
        #self.Number_Stories_Gherkin_Format = other.Number_Stories_Gherkin_Format 
        #self.Number_of_Stories = other.Number_of_Stories
        #self.Gherkin_Story_Rate = other.Gherkin_Story_Rate
        self.TotalBugCount = other.TotalBugCount
        self.Total_Count_Stories_Worked_On = other.Total_Count_Stories_Worked_On
        self.Escape_Velocity_Rate = other.Escape_Velocity_Rate 
        #self.Test_Automation = other.Test_Automation
        #self.Test_Automation_Tickets = other.Test_Automation_Tickets
        
    async def acquire_pre_data(self):
        self.create_id_list()

    @simpleDebug
    async def calculate_kpis(self):
        #acquire any missing data
        #sum up the values from the velocity reports
        await self.acquire_pre_data()
        for vel in self.velocity_reports:
                self.monthly_completedIssuesInitialEstimateSum += vel.completedIssuesInitialEstimateSum
                self.monthly_completedIssuesEstimateSum += vel.completedIssuesEstimateSum
                self.monthly_issuesNotCompletedInitialEstimateSum += vel.issuesNotCompletedInitialEstimateSum
                self.monthly_issuesNotCompletedEstimateSum += vel.issuesNotCompletedEstimateSum
                self.monthly_allIssuesEstimateSum += vel.allIssuesEstimateSum 
                self.monthly_puntedIssuesInitialEstimateSum += vel.puntedIssuesInitialEstimateSum
                self.monthly_puntedIssuesEstimateSum += vel.puntedIssuesEstimateSum
                self.monthly_issuesCompletedInAnotherSprintInitialEstimateSum += vel.issuesCompletedInAnotherSprintInitialEstimateSum
                self.monthly_issuesCompletedInAnotherSprintEstimateSum += vel.issuesCompletedInAnotherSprintEstimateSum
                self.monthly_count_completedIssues += len(vel.completedIssues)
                self.monthly_count_issuesNotCompletedInCurrentSprint += len(vel.issuesNotCompletedInCurrentSprint)
                self.monthly_count_puntedIssues += len(vel.puntedIssues)
                self.monthly_count_issuesCompletedInAnotherSprint += len(vel.issuesCompletedInAnotherSprint)
                self.monthly_count_issueKeysAddedDuringSprint += len(vel.issueKeysAddedDuringSprint)
                self.abilityToEstimateValue.append(vel.kpi_abilityToEstimate)
        
        #Mobile doesn't have a US / Noida team combination
        if self.team_count > 1:
            self.Velocity = self.monthly_completedIssuesEstimateSum / len(self.velocity_reports)
        else:
            self.Velocity = self.monthly_completedIssuesEstimateSum / (len(self.velocity_reports)/self.team_count)

        self.overall_velocity += self.Velocity
        
        #self.calculate_first_time_right()
        self.calculate_sprint_churn()
        #await self.calculate_sprint_readiness()
        #await self.calculate_tech_debt()
        self.calculate_sprint_completion_rate()
        self.calculate_sprint_readiness_ratio()
        #self.calculate_tech_debt_ratio()
        self.calculate_automation()
        self.monthly_calc_abilityToEstimate = np.average(self.abilityToEstimateValue)
        #self.CreatedSupportTicketsDuringSprints = await self.calculate_created_support_tickets()
        #self.CompletedSupportTicketsDuringSprints = await self.calculate_completed_support_tickets()


    def print_kpis(self):
        stringlist = map(str, self.sprint_id_list)
        list_of_ids = ",".join(stringlist)
        print("=========================================")
        print("sprints = " + list_of_ids)
        # print("monthly_completedIssuesInitialEstimateSum = " + str(self.monthly_completedIssuesInitialEstimateSum))
        # print("monthly_completedIssuesEstimateSum = " + str(self.monthly_completedIssuesEstimateSum))
        # print("monthly_issuesNotCompletedInitialEstimateSum = " + str(self.monthly_issuesNotCompletedInitialEstimateSum))
        # print("monthly_issuesNotCompletedEstimateSum = " + str(self.monthly_issuesNotCompletedEstimateSum))
        # print("monthly_allIssuesEstimateSum = " + str(self.monthly_allIssuesEstimateSum))
        # print("monthly_puntedIssuesInitialEstimateSum = " + str(self.monthly_puntedIssuesInitialEstimateSum))
        # print("monthly_puntedIssuesEstimateSum = " + str(self.monthly_puntedIssuesEstimateSum))
        # print("monthly_issuesCompletedInAnotherSprintInitialEstimateSum = " + str(self.monthly_issuesCompletedInAnotherSprintInitialEstimateSum))
        # print("monthly_issuesCompletedInAnotherSprintEstimateSum = " + str(self.monthly_issuesCompletedInAnotherSprintEstimateSum))
        # print("....")
        # print("monthly_count_completedIssues = " + str(self.monthly_count_completedIssues))
        # print("monthly_count_issuesNotCompletedInCurrentSprint = " + str(self.monthly_count_issuesNotCompletedInCurrentSprint))
        # print("monthly_count_puntedIssues = " + str(self.monthly_count_puntedIssues))
        # print("monthly_count_issuesCompletedInAnotherSprint = " + str(self.monthly_count_issuesCompletedInAnotherSprint))
        # print("monthly_count_issueKeysAddedDuringSprint = " + str(self.monthly_count_issueKeysAddedDuringSprint))
        print("....")
        print(f"Team Velocity = {self.Velocity}")
        #print("Escape_Velocity = " + str(self.Escape_Velocity))
        print(f"Escape_Velocity Rate = {self.Escape_Velocity_Rate:.4f} (({self.Escape_Velocity}+{self.Escape_Velocity_HCMCS}) / {self.Total_Count_Stories_Worked_On})")
        #print(f"First Time Right Percent = {self.First_Time_Right:.4f} ({self.monthly_completedIssuesInitialEstimateSum:.2f}/{self.monthly_completedIssuesEstimateSum:.2f})")
        #print("Meetings Overhead = " )
        #print(f"# in Gherkin Format = {self.Number_Stories_Gherkin_Format}")
        #print(f"Number of Stories (minus regression) = {self.Number_of_Stories}")
        #print(f"Gherkin Format KPI = {self.Gherkin_Story_Rate:.4f}")
        #print("Release Delivery = " )
        #print("Release on Time = " )
        print(f"Sprint Churn = {self.Sprint_Churn:.4f}")
        print(f"Sprint Completion Rate = {self.Sprint_Completion_Rate:.4f}  ({self.monthly_completedIssuesEstimateSum:.2f} / {self.monthly_completedIssuesInitialEstimateSum:.2f}")
        #print(f"Spread Readiness = {self.Sprint_Readiness}")
        #print(f"Spread Readiness Ratio = {self.Sprint_Readiness_Ratio:.4f}")
        #print(f"Tech Debt Paydown (SP) = {self.Tech_Debt_Paydown}")
        #print(f"Tech Debt Paydown Ratio = {self.Tech_Debt_Paydown_Ratio}")
        print(f"Ability To Estimate = {self.monthly_calc_abilityToEstimate:.4f}" )
        #print("Testability = " )
        #print("Automation Tickets = " + str(self.Test_Automation))
        print("Total Bug Count = " + str(self.TotalBugCount))
        #print(f"Created Support Tickets = total={self.CreatedSupportTicketsDuringSprints[0]}   ->  {self.CreatedSupportTicketsDuringSprints[1]}:{self.CreatedSupportTicketsDuringSprints[2]}:{self.CreatedSupportTicketsDuringSprints[3]}:{self.CreatedSupportTicketsDuringSprints[4]}")
        #print(f"Completed Support Tickets = total={self.CompletedSupportTicketsDuringSprints[0]}   ->  {self.CompletedSupportTicketsDuringSprints[1]}:{self.CompletedSupportTicketsDuringSprints[2]}:{self.CompletedSupportTicketsDuringSprints[3]}:{self.CompletedSupportTicketsDuringSprints[4]}") 
        print("=========================================")

    def calculate_first_time_right(self):
        self.First_Time_Right = (self.monthly_completedIssuesInitialEstimateSum / self.monthly_completedIssuesEstimateSum)

#end of class..

async def get_sprint_ids_by_month(project, year, month, black_list):
        jsondata = await get_sprint_list(project)
        sprints = jsondata['sprints']
        id_list = []
        for sprint in sprints:
                enddate = sprint['end']
                SprintId = sprint['id']
                s1 = slice(0,8)
                date_time_obj = dt.datetime.strptime(enddate[s1], '%d%m%Y')
                if date_time_obj.month == int(month) and date_time_obj.year == int(year):
                    for plist in sprint['projects']:
                        if plist['key'] == project:
                            if SprintId not in black_list:
                                id_list.append(SprintId)

        return id_list

async def get_sprint_list(project):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/integration/teamcalendars/sprint/list?jql=project={project}'
        #print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response

