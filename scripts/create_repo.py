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


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

parser = argparse.ArgumentParser(
    description="Provision GitHub repositories from the repository registry."
)

parser.add_argument(
    "registry_file",
    nargs="?",
    default="requests/repository-requests.yml",
    help="Path to the repository request registry YAML file.",
)

args = parser.parse_args()


ORG = os.getenv(
    "GITHUB_ORG",
    "MI-INDUSTRIAL",
)


# ---------------------------------------------------------
# Load repository registry
# ---------------------------------------------------------

repositories = load_registry(
    args.registry_file
)


# ---------------------------------------------------------
# Nothing to provision
# ---------------------------------------------------------

if not repositories:

    print("=" * 60)
    print("Repository Provisioning")
    print("=" * 60)

    print("Repository registry contains no requests.")
    print("Nothing to provision.")

    sys.exit(0)


# ---------------------------------------------------------
# GitHub App authentication
# ---------------------------------------------------------

TOKEN = os.environ.get(
    "GITHUB_APP_TOKEN"
)


if not TOKEN:

    print(
        "ERROR: GITHUB_APP_TOKEN is not available."
    )

    print(
        "Confirm that the GitHub App token is generated "
        "before running this script."
    )

    sys.exit(1)


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}


# ---------------------------------------------------------
# Counters
# ---------------------------------------------------------

created_count = 0
skipped_count = 0


# ---------------------------------------------------------
# Process repository requests
# ---------------------------------------------------------

for repository in repositories:

    # Validate repository entry
    repository = validate_repository(
        repository
    )

    # Generate repository name
    name = repo_name(
        repository
    )

    print()
    print("=" * 60)
    print(f"Repository: {ORG}/{name}")
    print("=" * 60)


    # -----------------------------------------------------
    # Check whether repository already exists
    # -----------------------------------------------------

    repo_url = (
        f"https://api.github.com/repos/"
        f"{ORG}/{name}"
    )


    try:

        check = requests.get(
            repo_url,
            headers=HEADERS,
            timeout=30,
        )

    except requests.RequestException as exc:

        print(
            "ERROR: Unable to connect to GitHub API."
        )

        print(str(exc))

        sys.exit(1)


    # Repository already exists
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


    # Expected response when repository does not exist
    if check.status_code != 404:

        print(
            "ERROR: Unable to check repository."
        )

        print(
            f"HTTP Status: {check.status_code}"
        )

        print(check.text)

        sys.exit(1)


    # -----------------------------------------------------
    # Create repository
    # -----------------------------------------------------

    payload = {
        "name": name,
        "description": repository[
            "description"
        ].strip(),
        "visibility": repository[
            "visibility"
        ],
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


    try:

        response = requests.post(
            f"https://api.github.com/"
            f"orgs/{ORG}/repos",
            headers=HEADERS,
            json=payload,
            timeout=30,
        )

    except requests.RequestException as exc:

        print(
            "ERROR: GitHub API request failed "
            "while creating repository."
        )

        print(str(exc))

        sys.exit(1)


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


    # -----------------------------------------------------
    # Retrieve main branch
    # -----------------------------------------------------

    main_url = (
        f"https://api.github.com/repos/"
        f"{ORG}/{name}/git/ref/heads/main"
    )


    main = None


    for attempt in range(1, 6):

        try:

            main = requests.get(
                main_url,
                headers=HEADERS,
                timeout=30,
            )

        except requests.RequestException as exc:

            print(
                "ERROR: Unable to retrieve "
                "main branch."
            )

            print(str(exc))

            sys.exit(1)


        if main.status_code == 200:

            break


        print(
            f"Waiting for main branch "
            f"(attempt {attempt}/5)..."
        )

        time.sleep(2)


    if (
        main is None
        or main.status_code != 200
    ):

        print(
            "ERROR: Could not retrieve "
            "main branch."
        )

        if main is not None:

            print(
                f"HTTP Status: "
                f"{main.status_code}"
            )

            print(main.text)

        sys.exit(1)


    main_sha = main.json()[
        "object"
    ][
        "sha"
    ]


    print(
        f"main branch found."
    )


    # -----------------------------------------------------
    # Create dev branch from main
    # -----------------------------------------------------

    print(
        "Creating dev branch from main..."
    )


    try:

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

    except requests.RequestException as exc:

        print(
            "ERROR: GitHub API request failed "
            "while creating dev branch."
        )

        print(str(exc))

        sys.exit(1)


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
            "ERROR: Unable to create "
            "dev branch."
        )

        print(
            f"HTTP Status: "
            f"{dev_response.status_code}"
        )

        print(dev_response.text)

        sys.exit(1)


    created_count += 1


# ---------------------------------------------------------
# Final summary
# ---------------------------------------------------------

print()
print("=" * 60)
print("Provisioning Summary")
print("=" * 60)

print(
    f"Organization: {ORG}"
)

print(
    f"Created: {created_count}"
)

print(
    f"Existing / skipped: {skipped_count}"
)

print(
    f"Total registry entries: "
    f"{len(repositories)}"
)

print("=" * 60)
