"""Track and manage obsolete (deprecated) keys across environments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _obsolete_path() -> Path:
    return get_store_dir() / "obsolete_keys.json"


def _load() -> dict:
    p = _obsolete_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _obsolete_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, key: str) -> str:
    return f"{project}::{env}::{key}"


def mark_obsolete(project: str, env: str, key: str, reason: str = "") -> None:
    """Mark a key as obsolete with an optional reason."""
    data = _load()
    data[_key(project, env, key)] = {"project": project, "env": env, "key": key, "reason": reason}
    _save(data)


def unmark_obsolete(project: str, env: str, key: str) -> bool:
    """Remove a key from the obsolete list. Returns True if it existed."""
    data = _load()
    k = _key(project, env, key)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def is_obsolete(project: str, env: str, key: str) -> bool:
    """Return True if the key is marked obsolete."""
    data = _load()
    return _key(project, env, key) in data


def get_obsolete_keys(project: str, env: Optional[str] = None) -> list[dict]:
    """Return all obsolete key entries for a project, optionally filtered by env."""
    data = _load()
    results = [v for v in data.values() if v["project"] == project]
    if env is not None:
        results = [v for v in results if v["env"] == env]
    return results


def clear_obsolete(project: str, env: str) -> int:
    """Remove all obsolete keys for a project/env. Returns count removed."""
    data = _load()
    before = len(data)
    data = {k: v for k, v in data.items() if not (v["project"] == project and v["env"] == env)}
    _save(data)
    return before - len(data)
