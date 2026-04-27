"""Track deprecated keys across projects and environments."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _deprecation_path() -> Path:
    return get_store_dir() / "deprecations.json"


def _load() -> dict:
    p = _deprecation_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _deprecation_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, key: str) -> str:
    return f"{project}::{env}::{key}"


def mark_deprecated(
    project: str,
    env: str,
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
) -> None:
    """Mark a key as deprecated with an optional reason and replacement."""
    data = _load()
    entry = {
        "reason": reason,
        "replacement": replacement,
        "deprecated_at": datetime.now(timezone.utc).isoformat(),
    }
    data[_key(project, env, key)] = entry
    _save(data)


def unmark_deprecated(project: str, env: str, key: str) -> bool:
    """Remove deprecation marker. Returns True if it existed."""
    data = _load()
    k = _key(project, env, key)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def is_deprecated(project: str, env: str, key: str) -> bool:
    data = _load()
    return _key(project, env, key) in data


def get_deprecation(project: str, env: str, key: str) -> Optional[dict]:
    """Return deprecation info dict or None if not deprecated."""
    data = _load()
    return data.get(_key(project, env, key))


def list_deprecated(project: str, env: str) -> list[dict]:
    """Return all deprecated keys for a given project/env."""
    data = _load()
    prefix = f"{project}::{env}::"
    results = []
    for k, v in data.items():
        if k.startswith(prefix):
            key_name = k[len(prefix):]
            results.append({"key": key_name, **v})
    return results
