import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- JIRA Configuration ---
JIRA_DOMAIN = "your-domain.atlassian.net"
EMAIL = "your-email@example.com"
API_TOKEN = "your-api-token"
JQL_QUERY = "assignee=currentUser()"  # Adjust as needed
MAX_RESULTS = 50  # Increase if needed

# --- Google Sheets Configuration ---
GOOGLE_SHEET_NAME = "JIRA Tickets with All Comments"

# --- Authenticate with Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

# --- Authenticate with JIRA and fetch tickets ---
search_url = f"https://{JIRA_DOMAIN}/rest/api/3/search"
headers = {"Accept": "application/json"}
auth = (EMAIL, API_TOKEN)
params = {
    "jql": JQL_QUERY,
    "maxResults": MAX_RESULTS,
    "fields": "key,summary,status,assignee"
}

response = requests.get(search_url, headers=headers, params=params, auth=auth)
data = response.json()

# --- Prepare the sheet ---
sheet.clear()
sheet.append_row(["Key", "Summary", "Status", "Assignee", "All Comments"])

# --- Loop through issues ---
for issue in data["issues"]:
    key = issue["key"]
    summary = issue["fields"]["summary"]
    status = issue["fields"]["status"]["name"]
    assignee = issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned"

    # --- Fetch all comments for this issue ---
    comments_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{key}/comment"
    comments_response = requests.get(comments_url, headers=headers, auth=auth)
    comments_data = comments_response.json()

    comment_list = []

    for comment in comments_data.get("comments", []):
        author = comment["author"]["displayName"]
        created = comment["created"]
        body_content = comment["body"]["content"]
        comment_text = ""

        for block in body_content:
            for part in block.get("content", []):
                comment_text += part.get("text", "")

        formatted = f"{author} on {created}:\n{comment_text.strip()}"
        comment_list.append(formatted)

    all_comments = "\n\n---\n\n".join(comment_list) if comment_list else "No comments"

    # --- Write to Google Sheet ---
    sheet.append_row([key, summary, status, assignee, all_comments])

print("All JIRA comments have been written to Google Sheets.")
