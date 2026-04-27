"""Trust level management for environments."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

LEVELS = ("untrusted", "low", "medium", "high", "verified")


def _trust_path() -> Path:
    return get_store_dir() / "trust.json"


def _load() -> dict:
    p = _trust_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _trust_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def set_trust(project: str, env: str, level: str, note: str = "") -> None:
    """Assign a trust level to an environment."""
    if level not in LEVELS:
        raise ValueError(f"Invalid trust level '{level}'. Choose from: {', '.join(LEVELS)}")
    data = _load()
    data[_key(project, env)] = {"level": level, "note": note}
    _save(data)


def get_trust(project: str, env: str) -> dict:
    """Return trust info for an environment; defaults to 'untrusted'."""
    data = _load()
    return data.get(_key(project, env), {"level": "untrusted", "note": ""})


def remove_trust(project: str, env: str) -> bool:
    """Remove trust record. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_trusted(project: str) -> list[dict]:
    """Return all trust entries for a project."""
    data = _load()
    prefix = f"{project}::"
    results = []
    for k, v in data.items():
        if k.startswith(prefix):
            env = k[len(prefix):]
            results.append({"env": env, **v})
    return sorted(results, key=lambda x: x["env"])


def is_trusted(project: str, env: str, min_level: str = "medium") -> bool:
    """Return True if the env's trust level meets the minimum required."""
    if min_level not in LEVELS:
        raise ValueError(f"Invalid trust level '{min_level}'.")
    info = get_trust(project, env)
    return LEVELS.index(info["level"]) >= LEVELS.index(min_level)
