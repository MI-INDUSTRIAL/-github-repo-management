import argparse
import os
import sys
import time

import requests

from common import (
    load_registry,
    validate_repository,
    repo_name,
)


parser = argparse.ArgumentParser()

parser.add_argument(
    "registry_file",
    nargs="?",
    default="requests/repository-requests.yml",
)

args = parser.parse_args()


ORG = os.getenv(
    "GITHUB_ORG",
    "MI-INDUSTRIAL",
)

TOKEN = os.environ.get(
    "ORG_ADMIN_TOKEN"
)


if not TOKEN:

    print(
        "ERROR: ORG_ADMIN_TOKEN is not configured."
    )

    sys.exit(1)


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}


repositories = load_registry(
    args.registry_file
)


if not repositories:

    print(
        "Repository registry contains no requests."
    )

    print(
        "Nothing to provision."
    )

    sys.exit(0)


created_count = 0
skipped_count = 0


for repository in repositories:

    repository = validate_repository(
        repository
    )

    name = repo_name(
        repository
    )

    print()
    print("=" * 60)
    print(f"Repository: {name}")
    print("=" * 60)

    repo_url = (
        f"https://api.github.com/repos/"
        f"{ORG}/{name}"
    )

    check = requests.get(
        repo_url,
        headers=HEADERS,
        timeout=30,
    )


    # Repository already exists.
    if check.status_code == 200:

        print(
            f"Repository already exists: "
            f"{ORG}/{name}"
        )

        print(
            "Skipping existing repository."
        )

        skipped_count += 1

        continue


    if check.status_code != 404:

        print(
            "ERROR: Unable to check repository."
        )

        print(
            f"HTTP Status: {check.status_code}"
        )

        print(check.text)

        sys.exit(1)


    payload = {
        "name": name,
        "description":
            repository["description"].strip(),
        "visibility":
            repository["visibility"],
        "auto_init": True,
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False,
        "delete_branch_on_merge": True,
    }


    print(
        f"Creating repository "
        f"{ORG}/{name}..."
    )


    response = requests.post(
        f"https://api.github.com/"
        f"orgs/{ORG}/repos",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )


    if response.status_code != 201:

        print(
            "ERROR: Repository creation failed."
        )

        print(
            f"HTTP Status: "
            f"{response.status_code}"
        )

        print(response.text)

        sys.exit(1)


    repo = response.json()

    print(
        f"Repository created successfully: "
        f"{repo['html_url']}"
    )


    # -----------------------------------------
    # Read main branch
    # -----------------------------------------

    main_url = (
        f"https://api.github.com/repos/"
        f"{ORG}/{name}/git/ref/heads/main"
    )


    main = None


    for attempt in range(1, 6):

        main = requests.get(
            main_url,
            headers=HEADERS,
            timeout=30,
        )

        if main.status_code == 200:
            break

        print(
            f"Waiting for main branch "
            f"(attempt {attempt}/5)..."
        )

        time.sleep(2)


    if main is None or main.status_code != 200:

        print(
            "ERROR: Could not retrieve main branch."
        )

        if main is not None:
            print(main.text)

        sys.exit(1)


    main_sha = main.json()["object"]["sha"]


    # -----------------------------------------
    # Create dev branch
    # -----------------------------------------

    dev_response = requests.post(
        f"https://api.github.com/repos/"
        f"{ORG}/{name}/git/refs",
        headers=HEADERS,
        json={
            "ref": "refs/heads/dev",
            "sha": main_sha,
        },
        timeout=30,
    )


    if dev_response.status_code == 201:

        print(
            "dev branch created successfully."
        )


    elif dev_response.status_code == 422:

        print(
            "dev branch already exists."
        )


    else:

        print(
            "ERROR: Unable to create dev branch."
        )

        print(
            f"HTTP Status: "
            f"{dev_response.status_code}"
        )

        print(dev_response.text)

        sys.exit(1)


    created_count += 1


print()
print("=" * 60)
print("Provisioning Summary")
print("=" * 60)

print(
    f"Created: {created_count}"
)

print(
    f"Existing / skipped: {skipped_count}"
)

print(
    f"Total registry entries: {len(repositories)}"
)
