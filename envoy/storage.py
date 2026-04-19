"""Local storage backend for encrypted .env files."""

import os
import json
from pathlib import Path

DEFAULT_STORE_DIR = Path.home() / ".envoy" / "store"


def get_store_dir() -> Path:
    store = Path(os.environ.get("ENVOY_STORE_DIR", DEFAULT_STORE_DIR))
    store.mkdir(parents=True, exist_ok=True)
    return store


def _project_path(project: str) -> Path:
    return get_store_dir() / f"{project}.json"


def save(project: str, environment: str, ciphertext: str) -> None:
    """Save encrypted env data for a project/environment."""
    path = _project_path(project)
    data = load_all(project)
    data[environment] = ciphertext
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load(project: str, environment: str) -> str:
    """Load encrypted env data for a project/environment."""
    data = load_all(project)
    if environment not in data:
        raise KeyError(f"No data found for project '{project}' env '{environment}'")
    return data[environment]


def load_all(project: str) -> dict:
    """Return all environments stored for a project."""
    path = _project_path(project)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def delete(project: str, environment: str) -> bool:
    """Delete a specific environment entry. Returns True if deleted."""
    data = load_all(project)
    if environment not in data:
        return False
    del data[environment]
    path = _project_path(project)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return True


def list_environments(project: str) -> list:
    """List all stored environments for a project."""
    return list(load_all(project).keys())
