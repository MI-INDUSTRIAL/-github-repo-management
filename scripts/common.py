import re
from pathlib import Path

import yaml


ALLOWED_VISIBILITY = {"private", "internal", "public"}

REQUIRED_FIELDS = {
    "product",
    "purpose",
    "service",
    "description",
    "visibility",
}


def normalize(value: str) -> str:
    """
    Convert a repository-name component into lowercase,
    hyphen-separated format.
    """

    value = value.strip().lower()

    value = re.sub(
        r"[^a-z0-9-]",
        "-",
        value,
    )

    value = re.sub(
        r"-+",
        "-",
        value,
    )

    return value.strip("-")


def load_registry(path: str) -> list:
    """
    Load repositories from the unified YAML registry.
    """

    file_path = Path(path)

    if not file_path.exists():
        raise ValueError(
            f"Registry file does not exist: {path}"
        )

    data = yaml.safe_load(
        file_path.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Registry YAML must contain a mapping."
        )

    repositories = data.get("repositories")

    if repositories is None:
        raise ValueError(
            "YAML must contain a 'repositories' key."
        )

    if not isinstance(repositories, list):
        raise ValueError(
            "'repositories' must be a list."
        )

    return repositories


def validate_repository(data: dict) -> dict:
    """
    Validate a single repository request.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Each repository entry must be a mapping."
        )

    missing = REQUIRED_FIELDS - set(data)

    if missing:
        raise ValueError(
            "Missing required fields: "
            + ", ".join(sorted(missing))
        )

    for key in REQUIRED_FIELDS:

        if not isinstance(data[key], str):
            raise ValueError(
                f"{key} must be a string."
            )

        if not data[key].strip():
            raise ValueError(
                f"{key} cannot be empty."
            )

    visibility = data["visibility"].strip().lower()

    if visibility not in ALLOWED_VISIBILITY:
        raise ValueError(
            "visibility must be private, internal, or public."
        )

    data["visibility"] = visibility

    return data


def repo_name(data: dict) -> str:
    """
    Generate repository name using:

    Product-purpose-service
    """

    product = normalize(data["product"])
    purpose = normalize(data["purpose"])
    service = normalize(data["service"])

    if not product:
        raise ValueError("Invalid product.")

    if not purpose:
        raise ValueError("Invalid purpose.")

    if not service:
        raise ValueError("Invalid service.")

    return f"{product}-{purpose}-{service}"
