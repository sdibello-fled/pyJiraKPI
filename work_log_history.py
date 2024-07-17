import asyncio
from operator import delitem
from dotenv import load_dotenv
from jira_item import jira_ticket
from kpi import kpi_query 
from jira_api import jira_user
import csv

def create_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def split_list(input_list, size):
    return [input_list[i:i + size] for i in range(0, len(input_list), size)]

def combine_lists(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

def shorten_name(full_name):
    parts = full_name.split()
    if len(parts) > 1:
        return f'{parts[0][0]}{parts[-1]}'
    else:
        return full_name

hcmat_user =  [
        "557058:a91c81e3-530b-43bb-bbb9-d74e5e1a0abb",  # Don
        "557058:9b60215b-0419-46e4-a81e-f8b1d760fb73", # Krstin
        "712020:53f95827-14a5-476e-8154-96c5bcfce1ff", # Parvin
        "557058:ad419beb-61cf-4589-a3b5-b2ebe3372753", # Greg
        "557058:ca8c3562-f111-4a1d-9557-ec7fa208da2c", # Ben
        "557058:eb630a8d-35f5-4101-b96a-102f3b16cce8", #madhavi
        "557058:9f38ec04-7c4c-42a6-8ac5-9a6f89a4fbd3", #John
        "557058:70e9157e-f7f2-4e44-9da0-44857b01ac8c", #Justin
        "712020:a8d3e7f6-e8e9-4992-8d62-cc69ecf39e16", #Prateek
        #Thomas
        "61397cec70405d0068fd9ae5", #"Abhimanyu Kumar"
        "5db0aaea0343b80c307a6506", #Amar Srivastava
        "63ead859333d0e2ec16e4deb", #Shubham Singh
        "615f32b8c5388b00699abec4", #Sahil Sachdeva
        "5fca71d778f018007695e28b", #Kanhu Behera
        "60db23607d016900701d21a3", #Deepak Kanaujiya
        "604b9f60d7f56e0071c36e47", #M Raj Kumar
        "5e5fd1e01866460af8bd5986", #Monika Arora
        "615cb4db071a72007147dec3", #Urvashi Tiwari
        #Prakash Yadaw
        "605dfdb24b9135006aaae0cf", #Pragya Tiwari
        "61397cec70405d0068fd9ae5", #Abhimanyu Kumar
        "615cb4db071a72007147dec3" # Urvashi Tiwari
        # Rishi Raj Sani
        # Anu Gupta
        # Singh, Shubham
        
    ]

async def main():
        load_dotenv()
        users = await jira_user.list_of_user_by_role("HCMAT", 11504)

        print ("Start")
        for user in users:
            data = []
            issues = []
            chunks = []
            tickets_worked_on = []
            storyPoints = 0
            fullCount = 0
            emptyCount = 0

            if user["actorUser"]["accountId"] not in hcmat_user:
                continue

            # ("YYYY/MM/DD")
            shorten_n = shorten_name(user["displayName"],)
            #data = await kpi_query.get_monthly_tickets_by_updatedBy("HCMAT", user["actorUser"]["accountId"], "3/1/2024", None)
            #data = await kpi_query.get_monthly_tickets_by_updatedBy("HCMAT", shorten_n, "2024/03/01", None)
            
            #data = await kpi_query.get_monthly_tickets_by_selection("HCMAT", user["actorUser"]["accountId"], -1, None)
            data = await kpi_query.get_monthly_tickets_by_worklog("HCMAT", user["actorUser"]["accountId"], -1, None)
            # pull the list with logged work        

            if data == None:
                print ("No data returned for {0}".format(user["displayName"]))
            elif (len(data) > 0):
                for issue in data['issues']:
                    key = issue['key'] 
                    issues.append(key)
            
                #chu = create_chunks(issues, 125)
                chunks = split_list(issues, 100)
                # get all the work in one statement 
                for chu in chunks:
                    ticket_data = await kpi_query.get_mutiple_keys(chu)
                    if (ticket_data['issues'] != []):
                        tickets_worked_on.append(ticket_data['issues'])

                tickets = combine_lists(tickets_worked_on)
                # get the story points worked on.
                if len(tickets_worked_on) > 0:
                    storyPoints, fullCount, emptyCount = jira_ticket.sum_points(tickets)
                    print ("{0}, {1} - points {2}, full/empty count {3}/{4}".format(user["displayName"], str(len(tickets)), storyPoints, fullCount, emptyCount))
                    for t in tickets:
                        #print (f"\t - \t{t['key']} - {t['fields']['summary']}")    
                        if t['fields']['customfield_10021'] != None:
                            print (f"\t - \t{t['key']} - {t['fields']['summary']}")    
                             

if __name__ == '__main__':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())


