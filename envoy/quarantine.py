"""Quarantine module: isolate env files flagged as potentially unsafe."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _quarantine_path() -> Path:
    return get_store_dir() / "quarantine.json"


def _load() -> dict:
    p = _quarantine_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _quarantine_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def quarantine_env(project: str, env: str, reason: str = "") -> dict:
    """Mark an env as quarantined. Returns the created entry."""
    data = _load()
    entry = {
        "project": project,
        "env": env,
        "reason": reason,
        "quarantined_at": datetime.now(timezone.utc).isoformat(),
    }
    data[_key(project, env)] = entry
    _save(data)
    return entry


def release_env(project: str, env: str) -> bool:
    """Remove an env from quarantine. Returns True if it was quarantined."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def is_quarantined(project: str, env: str) -> bool:
    """Return True if the env is currently quarantined."""
    return _key(project, env) in _load()


def get_entry(project: str, env: str) -> Optional[dict]:
    """Return the quarantine entry for an env, or None."""
    return _load().get(_key(project, env))


def list_quarantined(project: Optional[str] = None) -> list[dict]:
    """Return all quarantined envs, optionally filtered by project."""
    data = _load()
    entries = list(data.values())
    if project:
        entries = [e for e in entries if e["project"] == project]
    return sorted(entries, key=lambda e: e["quarantined_at"])
