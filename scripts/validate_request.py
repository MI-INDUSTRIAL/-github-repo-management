import argparse

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


repositories = load_registry(args.registry_file)


if not repositories:

    print("Repository registry is valid.")
    print("Repositories found: 0")
    print("No repository requests currently exist.")

    raise SystemExit(0)


names = set()


for index, repository in enumerate(
    repositories,
    start=1,
):

    repository = validate_repository(repository)

    name = repo_name(repository)

    if name in names:
        raise ValueError(
            f"Duplicate repository request detected: {name}"
        )

    names.add(name)

    print(
        f"[{index}] VALID: "
        f"{name} "
        f"({repository['visibility']})"
    )


print()
print(
    f"Registry validation successful. "
    f"Total repositories: {len(repositories)}"
)
