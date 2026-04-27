"""Endorsement module: track peer approvals for env changes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _endorsement_path() -> Path:
    return get_store_dir() / "endorsements.json"


def _load() -> dict:
    p = _endorsement_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _endorsement_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def endorse(project: str, env: str, user: str) -> list[str]:
    """Add user endorsement for a project/env. Returns updated endorser list."""
    data = _load()
    k = _key(project, env)
    endorsers: list[str] = data.get(k, {}).get("endorsers", [])
    if user not in endorsers:
        endorsers.append(user)
    data[k] = {"project": project, "env": env, "endorsers": endorsers}
    _save(data)
    return endorsers


def unendorse(project: str, env: str, user: str) -> bool:
    """Remove user endorsement. Returns True if the user was present."""
    data = _load()
    k = _key(project, env)
    entry = data.get(k)
    if not entry or user not in entry["endorsers"]:
        return False
    entry["endorsers"].remove(user)
    data[k] = entry
    _save(data)
    return True


def get_endorsers(project: str, env: str) -> list[str]:
    """Return list of users who have endorsed this env."""
    data = _load()
    return data.get(_key(project, env), {}).get("endorsers", [])


def is_endorsed_by(project: str, env: str, user: str) -> bool:
    return user in get_endorsers(project, env)


def endorsement_count(project: str, env: str) -> int:
    return len(get_endorsers(project, env))


def list_endorsed(project: Optional[str] = None) -> list[dict]:
    """Return all endorsement entries, optionally filtered by project."""
    data = _load()
    results = list(data.values())
    if project:
        results = [r for r in results if r["project"] == project]
    return results
