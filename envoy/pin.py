"""Pin specific env vars to prevent them from being overwritten during push/pull."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _pin_path() -> Path:
    return get_store_dir() / "pins.json"


def _load_pins() -> dict:
    p = _pin_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(data: dict) -> None:
    _pin_path().write_text(json.dumps(data, indent=2))


def pin_key(project: str, env: str, key: str) -> None:
    """Mark a key as pinned for a given project/env."""
    data = _load_pins()
    bucket = data.setdefault(project, {}).setdefault(env, [])
    if key not in bucket:
        bucket.append(key)
    _save_pins(data)


def unpin_key(project: str, env: str, key: str) -> None:
    """Remove a pin from a key. No-op if not pinned."""
    data = _load_pins()
    try:
        data[project][env].remove(key)
    except (KeyError, ValueError):
        pass
    else:
        _save_pins(data)


def get_pinned(project: str, env: str) -> list[str]:
    """Return list of pinned keys for a project/env."""
    data = _load_pins()
    return list(data.get(project, {}).get(env, []))


def is_pinned(project: str, env: str, key: str) -> bool:
    return key in get_pinned(project, env)


def apply_pins(project: str, env: str, incoming: dict, current: dict) -> dict:
    """Merge incoming vars but keep pinned keys from current."""
    pinned = get_pinned(project, env)
    merged = {**incoming}
    for key in pinned:
        if key in current:
            merged[key] = current[key]
    return merged
