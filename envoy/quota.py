"""Quota management: limit the number of environments per project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir, list_environments

DEFAULT_QUOTA = 10
_QUOTA_FILE = "quotas.json"


def _quota_path() -> Path:
    return get_store_dir() / _QUOTA_FILE


def _load_quotas() -> dict:
    p = _quota_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quotas(data: dict) -> None:
    _quota_path().write_text(json.dumps(data, indent=2))


def set_quota(project: str, limit: int) -> None:
    """Set the maximum number of environments allowed for a project."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    data = _load_quotas()
    data[project] = limit
    _save_quotas(data)


def get_quota(project: str) -> int:
    """Return the quota for a project, falling back to the default."""
    data = _load_quotas()
    return data.get(project, DEFAULT_QUOTA)


def remove_quota(project: str) -> bool:
    """Remove a custom quota for a project. Returns True if it existed."""
    data = _load_quotas()
    if project in data:
        del data[project]
        _save_quotas(data)
        return True
    return False


def check_quota(project: str) -> tuple[int, int, bool]:
    """Return (current_count, limit, within_quota) for a project."""
    try:
        envs = list_environments(project)
    except FileNotFoundError:
        envs = []
    limit = get_quota(project)
    return len(envs), limit, len(envs) < limit


def enforce_quota(project: str) -> None:
    """Raise RuntimeError if the project has reached its quota."""
    count, limit, ok = check_quota(project)
    if not ok:
        raise RuntimeError(
            f"Project '{project}' has reached its environment quota ({count}/{limit})."
        )
