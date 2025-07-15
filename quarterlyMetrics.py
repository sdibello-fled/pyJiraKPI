## parent=HCMAT-47799 ORDER BY rank
## requirements. 
# Grab all the epics in the Quarter ( via planning spreadsheet.. maybe use the spreadsheet.)
# Calculate number of stories, SP, etc - that are currently planned for the quarter.

import asyncio
from dotenv import load_dotenv  
from kpi.kpi_query import *

quarterly_work =  [
"HCMAT-66198",
"HCMAT-68985",
"OPS-78771",
"HCMAT-58963",
"HCMAT-70144",
"HCMAT-69570",
"HCMAT-70028",
"HCMAT-70046",
"HCMAT-69680",
"HCMAT-70860",
"HCMAT-69677",
"HCMAT-47799",
"HCMAT-63758",
"HCMAT-41023",
"HCMAT-65718",
"HCMAT-63761",
"HCMAT-63766",
"HCMAT-63768",
"HCMAT-70028",
"OPS-71119"]

async def get_all_subtasks():
    all_subtasks = []
    
    for parent_key in quarterly_work:
        # Get subtasks for each parent
        jql = f'parent = "{parent_key}"'
        try:
            result = await combinational_paging_manager_generic_jql(jql, 100, 0)
            if result and 'issues' in result:
                subtasks = result['issues']
                for subtask in subtasks:
                    all_subtasks.append({
                        'parent': parent_key,
                        'key': subtask['key'],
                        'summary': subtask['fields']['summary'],
                        'status': subtask['fields']['status']['name'],
                        'assignee': subtask['fields']['assignee']['displayName'] if subtask['fields']['assignee'] else 'Unassigned'
                    })
                print(f"Found {len(subtasks)} subtasks for {parent_key}")
        except Exception as e:
            print(f"Error getting subtasks for {parent_key}: {e}")
    
    return all_subtasks

async def main():
    load_dotenv()
    subtasks = await get_all_subtasks()
    
    print(f"\nTotal subtasks found: {len(subtasks)}")
    for subtask in subtasks:
        print(f"{subtask['parent']} -> {subtask['key']}: {subtask['summary']} [{subtask['status']}] - {subtask['assignee']}")

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())