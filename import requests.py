import requests
from datetime import datetime, timedelta

# GitHub organization name
org_name = 'org_name'
# Personal token
token = 'token'

# Headers for the API request
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

# Get the current date
now = datetime.now()

# Get all repositories in the organization
response = requests.get(f'https://api.github.com/orgs/{org_name}/repos', headers=headers)
repos = response.json()

# Iterate over all repositories
for repo in repos:
    # Get the repository name
    repo_name = repo['name']
    # Get all branches
    response = requests.get(f'https://api.github.com/repos/{org_name}/{repo_name}/branches', headers=headers)
    branches = response.json()

    # Iterate over all branches
    for branch in branches:
        # Get the branch name
        branch_name = branch['name']
        # Get the commit at the tip of the branch
        commit_sha = branch['commit']['sha']
        # Get the commit details
        commit_response = requests.get(f'https://api.github.com/repos/{org_name}/{repo_name}/commits/{commit_sha}', headers=headers)
        commit = commit_response.json()
        # Get the date of the commit
        commit_date = datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
        # If the commit is older than 2 years, delete the branch
        if now - commit_date > timedelta(days=2*365):
            delete_response = requests.delete(f'https://api.github.com/repos/{org_name}/{repo_name}/git/refs/heads/{branch_name}', headers=headers)
            print(f'Deleted branch {branch_name} in repository {repo_name}')