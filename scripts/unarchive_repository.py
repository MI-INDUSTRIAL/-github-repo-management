import os
import sys
import requests

token = os.environ["GITHUB_TOKEN"]
repo = os.environ["REPOSITORY"]
org = os.environ["ORG_NAME"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

repo_url = f"https://api.github.com/repos/{org}/{repo}"

check = requests.get(repo_url, headers=headers)

if check.status_code != 200:
    print(f"Repository '{repo}' not found")
    sys.exit(1)

response = requests.patch(
    repo_url,
    headers=headers,
    json={"archived": False}
)

if response.status_code == 200:
    print(f"SUCCESS: Repository '{repo}' unarchived")
else:
    print(response.text)
    sys.exit(1)
