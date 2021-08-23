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
        kpi_month_data = kpi_month
        sprint_filter_strings = ['US ', 'Noida ']
        rapid_view = '464'
        sprint_black_list = [3152]
        sprints_white_list = []
        sprint_id_list = await get_sprint_ids_by_month(project, year, month, sprint_black_list) 
        
        #loading the velocity reports
        for id in sprint_id_list:
            veloReport = jira_velocity_report(debugFlag)
            raw_velocity = await veloReport.get_sprint_velocity_report(os.environ.get('JIRA_USER'), os.environ.get('JIRA_API_KEY'), id, rapid_view)
            velocity = await veloReport.velocity_report_parse(raw_velocity)
            kpi_month_data.velocity_reports.append(velocity)

        #debug printing
        if (debugFlag == True):
                for vel in kpi_month_data.velocity_reports:
                        print(vel.name)

        


if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main()) 