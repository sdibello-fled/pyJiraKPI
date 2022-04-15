import os
import json
import aiohttp
import asyncio
import datetime as dt
from kpi import kpi_month
from dotenv import load_dotenv
from jira_velocity.velocity_report import *

async def printVelocity(velo):
    print ("============== report ===================")
    print ("completedIssuesInitialEstimateSum - {} ".format(velo.completedIssuesInitialEstimateSum))
    print ("completedIssuesEstimateSum - {} ".format(velo.completedIssuesEstimateSum))
    print ("issuesNotCompletedInitialEstimateSum - {} ".format(velo.issuesNotCompletedInitialEstimateSum))
    print ("issuesNotCompletedEstimateSum - {}".format(velo.issuesNotCompletedEstimateSum))
    print ("SprintID - {}".format(velo.sprintId))
    print ("Name - {}".format(velo.name))
    #print (velo.completedIssues) 
    #print (velo.issuesNotCompletedInCurrentSprint) 
    #print (velo.puntedIssues)
    #print (velo.issuesCompletedInAnotherSprint)
    #print ("issueKeysAddedDuringSprint - {}".format(velo.issueKeysAddedDuringSprint))
    print ("issuesNotCompletedInitialEstimateSum - {}".format(velo.issuesNotCompletedInitialEstimateSum))
    print ("issuesCompletedInAnotherSprintEstimateSum - {}".format(velo.issuesCompletedInAnotherSprintEstimateSum))
    print ("issuesCompletedInAnotherSprintInitialEstimateSum - {}".format(velo.issuesCompletedInAnotherSprintInitialEstimateSum))
    print ("puntedIssuesEstimateSum - {}".format(velo.puntedIssuesEstimateSum))
    print ("puntedIssuesInitialEstimateSum - {}".format(velo.puntedIssuesInitialEstimateSum))
    print ("allIssuesEstimateSum - {}".format(velo.allIssuesEstimateSum))
    return 

async def main():
        load_dotenv()

        year = 2022
        mon = 3
        debugFlag = False
        trackedProjects = []
        hcmat = {
                'project':'HCMAT',
                'view':'588'
        }
        fc = {
                'project':'FC',
                'view':'464'
        }
        trackedProjects.append(hcmat)
        trackedProjects.append(fc)

        sprint_black_list = [3152]
        #TODO
        #sprints_white_list = []
        for proj in trackedProjects:
               sprint_id_list = await kpi_month.get_sprint_ids_by_month(proj['project'], year, mon, sprint_black_list) 

               #loading all the velocity reports
               all_sprints_month = kpi_month.kpi_month(proj['project'], year, mon, debugFlag)
               for id in sprint_id_list:
                   veloReport = jira_velocity_report(debugFlag)
                   raw_velocity = await veloReport.get_sprint_velocity_report(os.environ.get('JIRA_USER'), os.environ.get('JIRA_API_KEY'), id, proj['view'])
                   velocity = await veloReport.velocity_report_parse(raw_velocity)
                   #await printVelocity(velocity)
                   all_sprints_month.velocity_reports.append(velocity)



               # filter the velocity reports
               us_team = kpi_month.kpi_month(proj['project'], year, mon, debugFlag)
               noida_team = kpi_month.kpi_month(proj['project'], year, mon, debugFlag)
               for v1 in all_sprints_month.velocity_reports:
                       if 'US ' in v1.name: 
                               us_team.velocity_reports.append(v1)

                       elif 'Noida ' in v1.name:
                               noida_team.velocity_reports.append(v1)                

               await us_team.calculate_kpis()

               await noida_team.calculate_kpis()

               #calculate team level items, like escape
               totalCompletedIssues = us_team.monthly_count_completedIssues
               totalCompletedIssues += noida_team.monthly_count_completedIssues
               escape_velocity = us_team.Escape_Velocity
               escape_rate = escape_velocity / totalCompletedIssues
               us_team.Escape_Velocity_Rate = escape_rate
               noida_team.Escape_Velocity_Rate = escape_rate

               print('us team sprints')
               for v2 in us_team.velocity_reports:
                       print(v2.name)


               us_team.print_kpis()

               print('noida team sprints')
               for v3 in noida_team.velocity_reports:
                       print(v3.name)

               noida_team.print_kpis()

if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())