import json
import aiohttp
import os
import datetime as dt
import calendar
from . import kpi_query 
import numpy as np  

class count_by_severity:
    def __init__(self):
        self.low = 0
        self.medium = 0
        self.high = 0
        self.highest = 0

class kpi_month:
    overall_velocity = 0

    def __init__(self, project, year, month, debug):
        self.project = project
        self.year=year
        self.month=month
        self.debug = debug
        self.sprint_id_list = []
        self.abilityToEstimateValue = []

        #kpis from spreadsheet
        self.velocity_reports = []
        self.debug = debug
        self.Escape_Velocity = 0
        self.Escape_Velocity_Rate = 0
        self.First_Time_Right = 0

        self.Number_of_Stories = 0
        self.Security_Focus = 0
        self.Sprint_Churn = 0
        self.Sprint_Completion_Rate = 0
        self.Sprint_Readiness = 0
        self.Sprint_Readiness_Ratio = 0
        self.Story_Completion_Rate = 0
        self.Tech_Debt_Paydown = 0
        self.Tech_Debt_Paydown_Ratio = 0
        self.Test_Automation = 0
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

    def calculate_sprint_completion_rate(self):
        self.Sprint_Completion_Rate = self.monthly_completedIssuesEstimateSum / self.monthly_completedIssuesInitialEstimateSum 

    async def calculate_sprint_readiness(self):
        data = await kpi_query.get_all_backlog_stories(self.project, self.debug)
        for response in data:
            self.Sprint_Readiness += self.total_story_points(response)

    async def calculate_completed_support_tickets(self):
        counts = []
        total_overallCount = 0
        total_highestCount = 0
        total_highCount = 0
        total_mediumCount = 0
        total_lowCount = 0
        data = await kpi_query.get_completed_support_defects(self.project, self.start_date, self.end_date, self.debug )
        for response in data:
            counts.append(self.parse_out_all_bugs(response))
        for count in counts:
            total_overallCount =+ count[0]
            total_highestCount =+ count[1]
            total_highCount =+ count[2]
            total_mediumCount =+ count[3]
            total_lowCount =+ count[4]

        tupCounts = (total_overallCount, total_highestCount, total_highCount, total_mediumCount, total_lowCount)
        return tupCounts


    async def calculate_created_support_tickets(self):
        counts = []
        total_overallCount = 0
        total_highestCount = 0
        total_highCount = 0
        total_mediumCount = 0
        total_lowCount = 0
        data = await kpi_query.get_created_support_defects(self.project, self.start_date, self.end_date, self.debug )
        for response in data:
            counts.append(self.parse_out_all_bugs(response))
        for count in counts:
            total_overallCount =+ count[0]
            total_highestCount =+ count[1]
            total_highCount =+ count[2]
            total_mediumCount =+ count[3]
            total_lowCount =+ count[4]

        tupCounts = (total_overallCount, total_highestCount, total_highCount, total_mediumCount, total_lowCount)
        return tupCounts
        

    def parse_out_all_bugs(self, data):
        overallCount = 0
        highestCount = 0
        highCount = 0
        mediumCount = 0
        lowCount = 0
        for i in data['issues']:
            overallCount += 1
            if 'priority' in i['fields']:
                if i['fields']['priority'] != None:
                    if i['fields']['priority']['name'] == " P2 - High":
                        highCount += 1
                    elif i['fields']['priority']['name'] == "P1 - Highest":
                        highestCount += 1
                    elif i['fields']['priority']['name'] == "P3 - Medium":
                        mediumCount += 1
                    elif i['fields']['priority']['name'] == "P4 - Lowest":
                        lowCount += 1

        tuple1 = (overallCount, highestCount, highCount, mediumCount, lowCount)
        return tuple1

    async def calculate_tech_debt(self):
        data = await kpi_query.get_all_tech_debt(self.project, self.sprint_id_list, self.debug)
        for response in data:
            self.Tech_Debt_Paydown += self.total_story_points(response)
    
    def calculate_sprint_readiness_ratio(self):
        self.Sprint_Readiness_Ratio = self.Sprint_Readiness / self.Velocity

    def calculate_tech_debt_ratio(self):
        self.Tech_Debt_Paydown_Ratio = self.Tech_Debt_Paydown / self.Velocity

    def total_story_points(self, data):
            issues = data['issues']
            total = 0
            for i in issues:
                    if 'customfield_10021' in i['fields']:
                            if i['fields']['customfield_10021'] != None:
                                    total += i['fields']['customfield_10021']                
            return total

    async def acquire_pre_data(self):
        self.create_id_list()
        self.Escape_Velocity = await kpi_query.get_escape_velocity(self.project, self.start_date, self.end_date, self.debug)
        self.Number_Stories_Gherkin_Format = await kpi_query.get_gherkin_format(self.project, self.sprint_id_list, self.debug)
        self.Number_of_Stories = await kpi_query.get_all_stories(self.project, self.sprint_id_list, self.debug)
        self.Gherkin_Story_Rate = self.Number_Stories_Gherkin_Format / self.Number_of_Stories
        self.TotalBugCount = await kpi_query.get_total_bug_count(self.project, self.debug)

    async def calculate_kpis(self):
        #acquire any missing data
        await self.acquire_pre_data()
        #sum up the values from the velocity reports
        for vel in self.velocity_reports:
                self.monthly_completedIssuesInitialEstimateSum =+ vel.completedIssuesInitialEstimateSum
                self.monthly_completedIssuesEstimateSum =+ vel.completedIssuesEstimateSum
                self.monthly_issuesNotCompletedInitialEstimateSum =+ vel.issuesNotCompletedInitialEstimateSum
                self.monthly_issuesNotCompletedEstimateSum =+ vel.issuesNotCompletedEstimateSum
                self.monthly_allIssuesEstimateSum =+ vel.allIssuesEstimateSum 
                self.monthly_puntedIssuesInitialEstimateSum =+ vel.puntedIssuesInitialEstimateSum
                self.monthly_puntedIssuesEstimateSum =+ vel.puntedIssuesEstimateSum
                self.monthly_issuesCompletedInAnotherSprintInitialEstimateSum =+ vel.issuesCompletedInAnotherSprintInitialEstimateSum
                self.monthly_issuesCompletedInAnotherSprintEstimateSum =+ vel.issuesCompletedInAnotherSprintEstimateSum
                self.monthly_count_completedIssues =+ len(vel.completedIssues)
                self.monthly_count_issuesNotCompletedInCurrentSprint =+ len(vel.issuesNotCompletedInCurrentSprint)
                self.monthly_count_puntedIssues =+ len(vel.puntedIssues)
                self.monthly_count_issuesCompletedInAnotherSprint =+ len(vel.issuesCompletedInAnotherSprint)
                self.monthly_count_issueKeysAddedDuringSprint =+ len(vel.issueKeysAddedDuringSprint)
                self.abilityToEstimateValue.append(vel.kpi_abilityToEstimate)
        
        self.Velocity = self.monthly_completedIssuesEstimateSum / (len(self.velocity_reports)/2)
        kpi_month.overall_velocity =+ self.Velocity
        #Todo - find a better way to manage the team count
        
        self.Total_Count_Stories_Worked_On = await kpi_query.get_escape_velocity_comparitor(self.project, self.start_date, self.end_date, self.debug)
        self.Escape_Velocity_Rate = self.Escape_Velocity / self.Total_Count_Stories_Worked_On
        self.calculate_first_time_right()
        self.calculate_sprint_churn()
        await self.calculate_sprint_readiness()
        await self.calculate_tech_debt()
        self.calculate_sprint_completion_rate()
        self.calculate_sprint_readiness_ratio()
        self.calculate_tech_debt_ratio()
        self.monthly_calc_abilityToEstimate = np.average(self.abilityToEstimateValue)
        self.CreatedSupportTicketsDuringSprints = await self.calculate_created_support_tickets()
        self.CompletedSupportTicketsDuringSprints = await self.calculate_completed_support_tickets()


    def print_kpis(self):
        stringlist = map(str, self.sprint_id_list)
        list_of_ids = ",".join(stringlist)
        print("-------------------------------------------")
        print("sprints = " + list_of_ids)
        print("monthly_completedIssuesInitialEstimateSum = " + str(self.monthly_completedIssuesInitialEstimateSum))
        print("monthly_completedIssuesEstimateSum = " + str(self.monthly_completedIssuesEstimateSum))
        print("monthly_issuesNotCompletedInitialEstimateSum = " + str(self.monthly_issuesNotCompletedInitialEstimateSum))
        print("monthly_issuesNotCompletedEstimateSum = " + str(self.monthly_issuesNotCompletedEstimateSum))
        print("monthly_allIssuesEstimateSum = " + str(self.monthly_allIssuesEstimateSum))
        print("monthly_puntedIssuesInitialEstimateSum = " + str(self.monthly_puntedIssuesInitialEstimateSum))
        print("monthly_puntedIssuesEstimateSum = " + str(self.monthly_puntedIssuesEstimateSum))
        print("monthly_issuesCompletedInAnotherSprintInitialEstimateSum = " + str(self.monthly_issuesCompletedInAnotherSprintInitialEstimateSum))
        print("monthly_issuesCompletedInAnotherSprintEstimateSum = " + str(self.monthly_issuesCompletedInAnotherSprintEstimateSum))
        print("....")
        print("monthly_count_completedIssues = " + str(self.monthly_count_completedIssues))
        print("monthly_count_issuesNotCompletedInCurrentSprint = " + str(self.monthly_count_issuesNotCompletedInCurrentSprint))
        print("monthly_count_puntedIssues = " + str(self.monthly_count_puntedIssues))
        print("monthly_count_issuesCompletedInAnotherSprint = " + str(self.monthly_count_issuesCompletedInAnotherSprint))
        print("monthly_count_issueKeysAddedDuringSprint = " + str(self.monthly_count_issueKeysAddedDuringSprint))
        print("....")
        print("Team Velocity = " + str(self.Velocity))
        print("Escape_Velocity = " + str(self.Escape_Velocity))
        print("Escape_Velocity Rate = " + str(self.Escape_Velocity_Rate))
        print("First Time Right Percent = " + str(self.First_Time_Right))
        print("Meetings Overhead = " )
        print("# in Gherkin Format = " + str(self.Number_Stories_Gherkin_Format) )
        print("Gherkin Format API = " + str(self.Gherkin_Story_Rate) )
        print("Release Delivery = " )
        print("Release on Time = " )
        print("Sprint Churn = " + str(self.Sprint_Churn))
        print("Sprint Completion Rate = (" + str(self.monthly_completedIssuesEstimateSum) + " / " + str(self.monthly_completedIssuesInitialEstimateSum) + " ) " + str(self.Sprint_Completion_Rate))
        print("Spread Readiness = " + str(self.Sprint_Readiness))
        print("Spread Readiness Ratio = " + str(self.Sprint_Readiness_Ratio))
        print("Tech Debt Paydown (SP) = " + str(self.Tech_Debt_Paydown))
        print("Tech Debt Paydown Ratio = " + str(self.Tech_Debt_Paydown_Ratio))
        print("Ability To Estimate = {}".format(str(self.monthly_calc_abilityToEstimate)))
        print("Testability = " )
        print("Total Bug Count = " + str(self.TotalBugCount))
        print("Created Support Tickets = total-" + str(self.CreatedSupportTicketsDuringSprints[0]) + "-" + str(self.CreatedSupportTicketsDuringSprints[1]) + ":" + str(self.CreatedSupportTicketsDuringSprints[2]) + ":" + str(self.CreatedSupportTicketsDuringSprints[3]) + ":" + str(self.CreatedSupportTicketsDuringSprints[4]) )
        print("Completed Support Tickets = total-" + str(self.CompletedSupportTicketsDuringSprints[0]) + "-" + str(self.CompletedSupportTicketsDuringSprints[1]) + ":" + str(self.CompletedSupportTicketsDuringSprints[2]) + ":" + str(self.CompletedSupportTicketsDuringSprints[3]) + ":" + str(self.CompletedSupportTicketsDuringSprints[4]) )
        print("-------------------------------------------")

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

