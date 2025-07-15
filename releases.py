import requests
import os
from openpyxl import Workbook
from dotenv import load_dotenv


# Jira API credentials
#JIRA_EMAIL = "sdibello@frontlineed.com"
#JIRA_API_TOKEN = "byyIcdw88dK0TqkXXsfdACF1"
JIRA_URL = "https://frontlinetechnologies.atlassian.net/rest/api/3/project/HCMAT/versions"

load_dotenv()

# Fetch data from Jira
response = requests.get(
    JIRA_URL,
    auth=(os.environ.get('JIRA_USER'), os.environ.get('JIRA_API_KEY')),
    headers={"Accept": "application/json"}
)
response.raise_for_status()
versions = response.json()

# Create Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "Versions"

# Write header
headers = ["id", "name", "description", "released", "releaseDate"]
ws.append(headers)

# Write version data
for v in versions:
    ws.append([
        v.get("id"),
        v.get("name"),
        v.get("description", ""),
        v.get("released"),
        v.get("releaseDate", "")
    ])

# Save to file
wb.save("HCMAT_versions.xlsx")
print("Exported to HCMAT_versions.xlsx")