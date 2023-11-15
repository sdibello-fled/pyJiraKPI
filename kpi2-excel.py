import os
import operator as op
import asyncio
import datetime as dt
from excelkpi import excel
from kpi import kpi_month
from dotenv import load_dotenv
from jira_api.velocity_report import jira_velocity_report
from jira_api import sprint_velocity_store
from art import *

## There is an ask to create averaged KPIs for the staff meeting.  I was thinking about capturing all the important KPIs in a local spreadsheet and having it do the work.


def removeCommonWords(name_list):
        com=[]
        removed = ""
        sent1=list(name_list[0].split())
        sent2=list(name_list[1].split())
        sent_org=list(name_list[0].split())
        for i in sent_org:
                if op.countOf(sent2,i)>0:
                        sent1.remove(i)
                        sent2.remove(i)
                        if len(removed) == 0:
                                removed = i
                        else:
                                removed = f'{removed} {i}' 
        return removed, ''.join(sent1), ''.join(sent2)

async def main(p_month, p_year):
        load_dotenv()

        year = p_year
        mon = p_month
        trackedProjects = []
        trackedProjects.append({ 'project':'HCMAT', 'view':'588', 'teams':2 })
        trackedProjects.append({ 'project':'FC', 'view':'464', 'teams':2 })
        trackedProjects.append({ 'project':'MOB', 'view':'509', 'teams':1 })
        sprint_black_list = [3152]

        xls = excel.excel_kpi('C:\\Users\\sdibello\\OneDrive - Frontline\\KPIs\\KPIAutomation.xlsx')

        for proj in trackedProjects:
                name_list = []
                name_list2 = []

                sprint_id_list = await kpi_month.get_sprint_ids_by_month(proj['project'], year, mon, sprint_black_list) 

                #loading all the velocity reports
                all_sprints_month = kpi_month.kpi_month(proj['project'], year, mon, proj['teams'], None)
                for id in sprint_id_list:
                   veloReport = jira_velocity_report()
                   raw_velocity = await veloReport.get_sprint_velocity_report(os.environ.get('JIRA_USER'), os.environ.get('JIRA_API_KEY'), id, proj['view'])
                   velocity = await veloReport.velocity_report_parse(raw_velocity)
                   #await printVelocity(velocity)
                   all_sprints_month.velocity_reports.append(velocity)

                # filter the velocity reports
                us_team = kpi_month.kpi_month(proj['project'], year, mon, proj['teams'], "")
                noida_team = kpi_month.kpi_month(proj['project'], year, mon, proj['teams'], "GL")
                for v1 in all_sprints_month.velocity_reports:
                        if 'US ' in v1.name: 
                               us_team.velocity_reports.append(v1)
                        elif 'Noida ' in v1.name:
                                noida_team.velocity_reports.append(v1)
                        elif 'Mobile ' in v1.name:
                               us_team.velocity_reports.append(v1)                              
                        else:
                                print(f"error in categorizing sprint - {v1}")                

                # group level stuff, can be on either 'team'
                await us_team.acquire_group_data()
                # team level stuff

                if len(us_team.velocity_reports) > 0:
                       await us_team.calculate_kpis()
                       noida_team.copy_group_data(us_team)
                       print('us team sprints')
                       for v2 in us_team.velocity_reports:
                               #Art = text2art(v2.name)
                               name_list.append(v2.name)

                       clean_name = removeCommonWords(name_list)
                       stringArt = '  '.join(clean_name)
                       print(text2art(stringArt))

                       us_team.print_kpis()
                       xls.set_data(us_team)
                       xls.save_file()


                if len(noida_team.velocity_reports) > 0:
                        await noida_team.calculate_kpis()
                        print('noida team sprints')
                        for v3 in noida_team.velocity_reports:
                                name_list2.append(v3.name)

                        clean_name2 = removeCommonWords(name_list2)
                        stringArt2 = '  '.join(clean_name2)
                        print(text2art(stringArt2))

                        noida_team.print_kpis()
                        xls.set_data(noida_team)
                        xls.save_file()


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main(10, 2023))