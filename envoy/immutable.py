"""Immutable env keys — once set, a key cannot be overwritten without explicit unpin."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _immutable_path() -> Path:
    return get_store_dir() / "immutable.json"


def _load() -> dict:
    p = _immutable_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _immutable_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, key: str) -> str:
    return f"{project}::{env}::{key}"


def mark_immutable(project: str, env: str, key: str, reason: str = "") -> None:
    """Mark a key as immutable for the given project/env."""
    data = _load()
    data[_key(project, env, key)] = {"reason": reason}
    _save(data)


def unmark_immutable(project: str, env: str, key: str) -> bool:
    """Remove immutability from a key. Returns True if it existed."""
    data = _load()
    k = _key(project, env, key)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def is_immutable(project: str, env: str, key: str) -> bool:
    """Return True if the key is marked immutable."""
    return _key(project, env, key) in _load()


def get_immutable_keys(project: str, env: str) -> list[dict]:
    """Return all immutable keys for a given project/env."""
    data = _load()
    prefix = f"{project}::{env}::"
    results = []
    for k, meta in data.items():
        if k.startswith(prefix):
            key_name = k[len(prefix):]
            results.append({"key": key_name, "reason": meta.get("reason", "")})
    return results


def assert_mutable(project: str, env: str, env_vars: dict) -> None:
    """Raise ValueError if any key in env_vars is immutable."""
    violations = [k for k in env_vars if is_immutable(project, env, k)]
    if violations:
        raise ValueError(
            f"Cannot overwrite immutable key(s): {', '.join(sorted(violations))}"
        )
