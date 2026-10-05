import argparse 
import os 
import sys 
import time 
import requests 
from common import load_request, repo_name 
 
parser = argparse.ArgumentParser() 
parser.add_argument("request_file") 
args = parser.parse_args() 
 
org = os.getenv("GITHUB_ORG", "MI-INDUSTRIAL") 
token = os.environ["ORG_ADMIN_TOKEN"] 
data = load_request(args.request_file) 
name = repo_name(data) 
 
headers = { 
    "Authorization": f"Bearer {token}", 
    "Accept": "application/vnd.github+json", 
    "X-GitHub-Api-Version": "2026-03-10", 
} 
 
repo_url = f"https://api.github.com/repos/{org}/{name}" 
check = requests.get(repo_url, headers=headers, timeout=30) 
if check.status_code == 200: 
    print(f"Repository already exists: {org}/{name}. Nothing to do.") 
    sys.exit(0) 
if check.status_code != 404: 
    print(f"Repository check failed. HTTP {check.status_code}: {check.text}") 
    sys.exit(1) 
 
payload = { 
    "name": name, 
    "description": data["description"].strip(), 
    "visibility": data["visibility"], 
    "auto_init": True, 
    "has_issues": True, 
    "has_projects": False, 
    "has_wiki": False, 
    "delete_branch_on_merge": True, 
} 
created = requests.post( 
    f"https://api.github.com/orgs/{org}/repos", 
    headers=headers, json=payload, timeout=30 
) 
if created.status_code != 201: 
    print(f"Repository creation failed. HTTP {created.status_code}: {created.text}") 
    sys.exit(1) 
print(f"Created: {created.json()['html_url']}") 
 
# auto_init creates main. Retry briefly because the initial Git ref may not be 
# immediately readable after repository creation. 
main_url = f"https://api.github.com/repos/{org}/{name}/git/ref/heads/main" 
main = None 
for _ in range(5): 
    main = requests.get(main_url, headers=headers, timeout=30) 
    if main.status_code == 200: 
        break 
    time.sleep(2) 
if main is None or main.status_code != 200: 
    print(f"Could not read main. HTTP {main.status_code}: {main.text}") 
    sys.exit(1) 
 
sha = main.json()["object"]["sha"] 
dev = requests.post( 
    f"https://api.github.com/repos/{org}/{name}/git/refs", 
    headers=headers, 
    json={"ref": "refs/heads/dev", "sha": sha}, 
    timeout=30, 
) 
if dev.status_code not in (201, 422): 
    print(f"Could not create dev. HTTP {dev.status_code}: {dev.text}") 
    sys.exit(1) 
 
print("main and dev are ready") 
print("LILLE working branch examples:") 
print("  feature/LILLE-123-camera-service") 
print("  bugfix/LILLE-343-stream-timeout")
