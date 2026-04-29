"""Ownership tracking for env keys and environments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _ownership_path() -> Path:
    return get_store_dir() / "ownership.json"


def _load() -> dict:
    p = _ownership_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _ownership_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, key: str) -> str:
    return f"{project}::{env}::{key}"


def set_owner(project: str, env: str, key: str, owner: str, note: str = "") -> None:
    """Assign an owner to a specific key in an env."""
    data = _load()
    data[_key(project, env, key)] = {"owner": owner, "note": note}
    _save(data)


def get_owner(project: str, env: str, key: str) -> Optional[dict]:
    """Return ownership info for a key, or None if unset."""
    return _load().get(_key(project, env, key))


def remove_owner(project: str, env: str, key: str) -> bool:
    """Remove ownership record for a key. Returns True if it existed."""
    data = _load()
    k = _key(project, env, key)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_owned_by(owner: str) -> list[dict]:
    """Return all keys owned by a given owner across all projects/envs."""
    results = []
    for composite, record in _load().items():
        if record.get("owner") == owner:
            project, env, key = composite.split("::", 2)
            results.append({"project": project, "env": env, "key": key, **record})
    return results


def list_owners_for_env(project: str, env: str) -> list[dict]:
    """Return all ownership records for a specific project/env."""
    prefix = f"{project}::{env}::"
    results = []
    for composite, record in _load().items():
        if composite.startswith(prefix):
            key = composite[len(prefix):]
            results.append({"key": key, **record})
    return results
