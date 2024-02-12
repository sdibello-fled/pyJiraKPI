import requests
from datetime import datetime, timedelta

# GitHub credentials
username = 'username'
token = 'token'

# Repository owner and name
owner = 'owner'
repo = 'repo'

# Headers for the API request
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {token}',
}

# Get all branches
response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/branches', headers=headers)
branches = response.json()

# Current date
now = datetime.now()

# Iterate over all branches
for branch in branches:
    # Get the last commit on the branch
    commit_response = requests.get(branch['commit']['url'], headers=headers)
    commit = commit_response.json()

    # Get the date of the last commit
    commit_date = datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')

    # If the last commit is older than 2 years, delete the branch
    if now - commit_date > timedelta(days=365*2):
        delete_response = requests.delete(f'https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch["name"]}', headers=headers)
        print(f'Deleted branch {branch["name"]}')