"""Retention policy management for env snapshots and history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

_DEFAULT_MAX_SNAPSHOTS = 10
_DEFAULT_MAX_HISTORY = 50


def _retention_path() -> Path:
    return get_store_dir() / "retention.json"


def _load() -> dict:
    p = _retention_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _retention_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_policy(project: str, max_snapshots: Optional[int] = None, max_history: Optional[int] = None) -> None:
    """Set retention limits for a project."""
    if max_snapshots is not None and max_snapshots < 1:
        raise ValueError("max_snapshots must be at least 1")
    if max_history is not None and max_history < 1:
        raise ValueError("max_history must be at least 1")
    data = _load()
    entry = data.get(project, {})
    if max_snapshots is not None:
        entry["max_snapshots"] = max_snapshots
    if max_history is not None:
        entry["max_history"] = max_history
    data[project] = entry
    _save(data)


def get_policy(project: str) -> dict:
    """Return the retention policy for a project, with defaults."""
    data = _load()
    entry = data.get(project, {})
    return {
        "max_snapshots": entry.get("max_snapshots", _DEFAULT_MAX_SNAPSHOTS),
        "max_history": entry.get("max_history", _DEFAULT_MAX_HISTORY),
    }


def remove_policy(project: str) -> bool:
    """Remove the retention policy for a project. Returns True if it existed."""
    data = _load()
    if project not in data:
        return False
    del data[project]
    _save(data)
    return True


def list_policies() -> dict:
    """Return all explicitly set retention policies."""
    return _load()
