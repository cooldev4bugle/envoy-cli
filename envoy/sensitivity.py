"""Sensitivity level management for env keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy.storage import get_store_dir

VALID_LEVELS = ("public", "internal", "confidential", "secret")


def _sensitivity_path() -> Path:
    return get_store_dir() / "sensitivity.json"


def _load() -> Dict[str, Dict[str, str]]:
    p = _sensitivity_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, Dict[str, str]]) -> None:
    _sensitivity_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, key: str) -> str:
    return f"{project}::{env}::{key}"


def set_sensitivity(project: str, env: str, key: str, level: str) -> None:
    """Assign a sensitivity level to a specific key."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level '{level}'. Must be one of: {VALID_LEVELS}")
    data = _load()
    data[_key(project, env, key)] = {"level": level}
    _save(data)


def get_sensitivity(project: str, env: str, key: str) -> Optional[str]:
    """Return the sensitivity level for a key, or None if unset."""
    data = _load()
    entry = data.get(_key(project, env, key))
    return entry["level"] if entry else None


def remove_sensitivity(project: str, env: str, key: str) -> bool:
    """Remove a sensitivity entry. Returns True if it existed."""
    data = _load()
    k = _key(project, env, key)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_sensitive_keys(project: str, env: str) -> Dict[str, str]:
    """Return all keys with their sensitivity levels for a given project/env."""
    prefix = f"{project}::{env}::"
    data = _load()
    return {
        k[len(prefix):]: v["level"]
        for k, v in data.items()
        if k.startswith(prefix)
    }


def filter_by_level(project: str, env: str, min_level: str) -> Dict[str, str]:
    """Return keys at or above the given minimum sensitivity level."""
    if min_level not in VALID_LEVELS:
        raise ValueError(f"Invalid level '{min_level}'. Must be one of: {VALID_LEVELS}")
    threshold = VALID_LEVELS.index(min_level)
    return {
        k: lvl
        for k, lvl in list_sensitive_keys(project, env).items()
        if VALID_LEVELS.index(lvl) >= threshold
    }
