import asyncio
from operator import delitem
from dotenv import load_dotenv
from kpi import kpi_query 


async def main():
    load_dotenv()

    data = []
    totalTime = 0

    year = str(-1)
    jql = f'created >= startOfyear({year}) AND created <= endOfYear({year}) AND text ~ Remap and project = HCMAT'
    data =  await kpi_query.combinational_paging_manager_generic_jql(jql, False )

    ## data = await kpi_query.get_all_remaps(False, -1)
    # go through the list of responeses ( need to pull issues from each one.)
    for issue in data['issues']:
        if ( issue['fields']['timespent'] != None ):
            time = issue['fields']['timespent']
            key = issue['key']
            ##print (f'{key} has {time}')
            totalTime = totalTime + int(time)
        ##else:
            ##print ( 'empty ')

    print ( f'{totalTime} Seconds' )
    minutes = totalTime / 60
    print ( f'{minutes} Minutes' )
    hours = minutes / 60
    print ( f'{hours} Hours' )


if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())