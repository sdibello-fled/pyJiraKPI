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
    total_story_points = 0
    zero_story_points_count = 0
    
    for parent_key in quarterly_work:
        # Get subtasks for each parent
        jql = f'parent = "{parent_key}"'
        try:
            result = await combinational_paging_manager_generic_jql(jql, 100, 0)
            if result and 'issues' in result:
                subtasks = result['issues']
                parent_story_points = 0
                parent_zero_count = 0
                
                for subtask in subtasks:
                    # Get story points (usually customfield_10021)
                    story_points = subtask['fields'].get('customfield_10021', 0) or 0
                    parent_story_points += story_points
                    
                    if story_points == 0:
                        zero_story_points_count += 1
                        parent_zero_count += 1
                    
                    all_subtasks.append({
                        'parent': parent_key,
                        'key': subtask['key'],
                        'summary': subtask['fields']['summary'],
                        'status': subtask['fields']['status']['name'],
                        'assignee': subtask['fields']['assignee']['displayName'] if subtask['fields']['assignee'] else 'Unassigned',
                        'story_points': story_points
                    })
                
                total_story_points += parent_story_points
                print(f"Found {len(subtasks)} subtasks for {parent_key} - {parent_story_points} story points ({parent_zero_count} with 0 SP)")
        except Exception as e:
            print(f"Error getting subtasks for {parent_key}: {e}")
    
    return all_subtasks, total_story_points, zero_story_points_count

async def main():
    load_dotenv()
    subtasks, total_points, zero_count = await get_all_subtasks()
    
    print(f"\nTotal subtasks found: {len(subtasks)}")
    print(f"Total story points: {total_points}")
    print(f"Stories with 0 story points: {zero_count}")
    
    for subtask in subtasks:
        print(f"{subtask['parent']} -> {subtask['key']}: {subtask['summary']} [{subtask['status']}] - {subtask['assignee']} - {subtask['story_points']} SP")

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
