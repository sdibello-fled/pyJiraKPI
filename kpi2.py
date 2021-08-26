import os
import json
import aiohttp
import asyncio
import datetime as dt
from kpi import kpi_month
from dotenv import load_dotenv
from jira_velocity.velocity_report import *

async def main():
        load_dotenv()

        year = 2021
        mon = 6
        debugFlag = False
        project = 'HCMAT'
        rapid_view = '588'
        #project = 'FC'
        #rapid_view = '464'

        sprint_black_list = [3152]
        #Todo
        #sprints_white_list = []
        sprint_id_list = await kpi_month.get_sprint_ids_by_month(project, year, mon, sprint_black_list) 
        
        #loading all the velocity reports
        all_sprints_month = kpi_month.kpi_month(project, year, mon, debugFlag)
        for id in sprint_id_list:
            veloReport = jira_velocity_report(debugFlag)
            raw_velocity = await veloReport.get_sprint_velocity_report(os.environ.get('JIRA_USER'), os.environ.get('JIRA_API_KEY'), id, rapid_view)
            velocity = await veloReport.velocity_report_parse(raw_velocity)
            all_sprints_month.velocity_reports.append(velocity)

        # filter the velocity reports
        us_team = kpi_month.kpi_month(project, year, mon, debugFlag)
        noida_team = kpi_month.kpi_month(project, year, mon, debugFlag)
        for v1 in all_sprints_month.velocity_reports:
                if 'US ' in v1.name: 
                        us_team.velocity_reports.append(v1)

                elif 'Noida ' in v1.name:
                        noida_team.velocity_reports.append(v1)

        print('us team sprints')
        for v2 in us_team.velocity_reports:
                print(v2.name)

        await us_team.calculate_kpis()
        
        us_team.print_kpis()

        print('noida team sprints')
        for v3 in noida_team.velocity_reports:
                print(v3.name)
        
        await noida_team.calculate_kpis()
        noida_team.print_kpis()

if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())