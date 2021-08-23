import json
import aiohttp
import os
import datetime as dt

class kpi_month:
    year=0
    month=0
    velocity_reports = []

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
                        if SprintId not in black_list:
                                id_list.append(SprintId)
    
        return id_list

async def get_sprint_list(project):
        ## get a list of all sprints
        auth = aiohttp.BasicAuth(login = os.environ.get('JIRA_USER'), password = os.environ.get('JIRA_API_KEY'))
        url = f'https://frontlinetechnologies.atlassian.net/rest/greenhopper/1.0/integration/teamcalendars/sprint/list?jql=project={project}'
        print(url)
        async with aiohttp.ClientSession(auth=auth) as session:
                raw = await session.get(url)
                response = await raw.text()
                response = json.loads(response)
        return response          