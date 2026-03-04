"""
Phase 4: API Clients
=====================
Make a live call to the GitHub API and print all repository names
associated with the authenticated user.
"""

import requests
import os
from dotenv import load_dotenv

# Load .env file so os.getenv() can read our secrets
load_dotenv()

# Pull the token from .env (never hardcode secrets in code)
token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

if not token:
    raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not found in .env")

# Every GitHub API request needs this header to authenticate
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

# Make the live API call
url = "https://api.github.com/user/repos"
response = requests.get(url, headers=headers)

# Check the HTTP status code — 200 means success
print(f"Status code: {response.status_code}")

# Parse JSON response and print each repo name
repos = response.json()
print(f"\nFound {len(repos)} repositories:\n")
for repo in repos:
    print(f"  - {repo['name']}")
