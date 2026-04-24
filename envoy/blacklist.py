"""Blacklist: prevent specific keys from being pushed/pulled for a project/env."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envoy.storage import get_store_dir


def _blacklist_path() -> Path:
    return get_store_dir() / "blacklists.json"


def _load() -> dict:
    p = _blacklist_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _blacklist_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def add_key(project: str, env: str, key: str) -> List[str]:
    """Add a key to the blacklist for the given project/env. Returns updated list."""
    data = _load()
    k = _key(project, env)
    keys = data.get(k, [])
    if key not in keys:
        keys.append(key)
    data[k] = keys
    _save(data)
    return keys


def remove_key(project: str, env: str, key: str) -> bool:
    """Remove a key from the blacklist. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    keys = data.get(k, [])
    if key not in keys:
        return False
    keys.remove(key)
    data[k] = keys
    _save(data)
    return True


def get_blacklist(project: str, env: str) -> List[str]:
    """Return all blacklisted keys for a project/env."""
    data = _load()
    return list(data.get(_key(project, env), []))


def is_blacklisted(project: str, env: str, key: str) -> bool:
    """Return True if the key is blacklisted."""
    return key in get_blacklist(project, env)


def clear_blacklist(project: str, env: str) -> None:
    """Remove all blacklisted keys for a project/env."""
    data = _load()
    data.pop(_key(project, env), None)
    _save(data)
