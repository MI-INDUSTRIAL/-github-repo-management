import os
import sys
import requests

token = os.environ["GITHUB_TOKEN"]
repo = os.environ["REPOSITORY"]
org = os.environ["ORG_NAME"]
confirmation = os.environ["CONFIRMATION"]

if confirmation != "DELETE":
    print("Deletion not confirmed.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

repo_url = f"https://api.github.com/repos/{org}/{repo}"

# Validation

check = requests.get(repo_url, headers=headers)

if check.status_code != 200:
    print("Repository not found.")
    sys.exit(1)

repo_data = check.json()

# Safety Validation

if not repo_data.get("archived"):
    print(
        "Repository must be archived before deletion."
    )
    sys.exit(1)

response = requests.delete(
    repo_url,
    headers=headers
)

if response.status_code == 204:
    print(f"SUCCESS: Repository '{repo}' deleted")
else:
    print(response.text)
    sys.exit(1)
