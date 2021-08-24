import os
import json
import aiohttp
import asyncio
import datetime as dt
import jira_sprint
from dotenv import load_dotenv
from jira_velocity.velocity_report import *
from kpi.month import *
         

async def main():
        load_dotenv()

        year = 2021
        month = 7
        debugFlag = True
        #store.project = 'HCMAT'
        #store.rapid_view = '588'
        project = 'FC'

        rapid_view = '464'
        sprint_black_list = [3152]
        #Todo
        #sprints_white_list = []
        sprint_id_list = await get_sprint_ids_by_month(project, year, month, sprint_black_list) 
        
        #loading all the velocity reports
        all_sprints_month = kpi_month(debugFlag)
        for id in sprint_id_list:
            veloReport = jira_velocity_report(debugFlag)
            raw_velocity = await veloReport.get_sprint_velocity_report(os.environ.get('JIRA_USER'), os.environ.get('JIRA_API_KEY'), id, rapid_view)
            velocity = await veloReport.velocity_report_parse(raw_velocity)
            all_sprints_month.velocity_reports.append(velocity)

        #debug printing
        #if (debugFlag == True):
        #       for vel in all_sprints_month.velocity_reports:
        #                print(vel.name)

        us_team = kpi_month(False)
        noida_team = kpi_month(False)
        for v1 in all_sprints_month.velocity_reports:
                if 'US ' in v1.name: 
                        us_team.velocity_reports.append(v1)
                        print('*')
                elif 'Noida ' in v1.name:
                        noida_team.velocity_reports.append(v1)
                        print('*')

        print('us team sprints')
        for v2 in us_team.velocity_reports:
                print(v2.name)

        print('noida team sprints')
        for v3 in noida_team.velocity_reports:
                print(v3.name)


if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())