"""Freeze/unfreeze environments to prevent accidental modifications."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from envoy.storage import get_store_dir


def _freeze_path() -> Path:
    return get_store_dir() / "freezes.json"


def _load() -> dict:
    p = _freeze_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _freeze_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def freeze_env(project: str, env: str, reason: str = "") -> dict:
    """Freeze an environment. Returns the freeze record."""
    data = _load()
    k = _key(project, env)
    record = {
        "project": project,
        "env": env,
        "reason": reason,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
    }
    data[k] = record
    _save(data)
    return record


def unfreeze_env(project: str, env: str) -> bool:
    """Unfreeze an environment. Returns True if it was frozen, False otherwise."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def is_frozen(project: str, env: str) -> bool:
    """Return True if the environment is currently frozen."""
    data = _load()
    return _key(project, env) in data


def get_freeze_info(project: str, env: str) -> dict | None:
    """Return freeze metadata or None if not frozen."""
    data = _load()
    return data.get(_key(project, env))


def list_frozen(project: str | None = None) -> list[dict]:
    """List all frozen environments, optionally filtered by project."""
    data = _load()
    records = list(data.values())
    if project is not None:
        records = [r for r in records if r["project"] == project]
    return sorted(records, key=lambda r: r["frozen_at"])
