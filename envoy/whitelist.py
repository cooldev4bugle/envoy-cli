"""Whitelist: only allow specific keys to be pushed/pulled for a project+env."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envoy.storage import get_store_dir


def _whitelist_path() -> Path:
    return get_store_dir() / "whitelists.json"


def _load() -> Dict[str, List[str]]:
    p = _whitelist_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, List[str]]) -> None:
    _whitelist_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def add_key(project: str, env: str, key: str) -> None:
    """Add a key to the whitelist for project+env."""
    data = _load()
    k = _key(project, env)
    existing = data.get(k, [])
    if key not in existing:
        existing.append(key)
    data[k] = existing
    _save(data)


def remove_key(project: str, env: str, key: str) -> bool:
    """Remove a key from the whitelist. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    keys = data.get(k, [])
    if key not in keys:
        return False
    keys.remove(key)
    data[k] = keys
    _save(data)
    return True


def get_keys(project: str, env: str) -> List[str]:
    """Return the whitelist for project+env, or empty list if none set."""
    return _load().get(_key(project, env), [])


def clear(project: str, env: str) -> None:
    """Remove the entire whitelist entry for project+env."""
    data = _load()
    data.pop(_key(project, env), None)
    _save(data)


def filter_env(project: str, env: str, variables: dict) -> dict:
    """Return only whitelisted keys from variables. If no whitelist set, return all."""
    allowed = get_keys(project, env)
    if not allowed:
        return dict(variables)
    return {k: v for k, v in variables.items() if k in allowed}
