"""Priority levels for environments — lets you mark envs as critical, high, normal, or low."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

VALID_LEVELS = ("critical", "high", "normal", "low")


def _priority_path() -> Path:
    return get_store_dir() / "priorities.json"


def _load() -> dict:
    p = _priority_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _priority_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def set_priority(project: str, env: str, level: str) -> None:
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid priority level '{level}'. Choose from: {', '.join(VALID_LEVELS)}")
    data = _load()
    data[_key(project, env)] = level
    _save(data)


def get_priority(project: str, env: str) -> str:
    data = _load()
    return data.get(_key(project, env), "normal")


def remove_priority(project: str, env: str) -> bool:
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_priorities(project: Optional[str] = None) -> list[dict]:
    data = _load()
    results = []
    for key, level in data.items():
        proj, env = key.split("::", 1)
        if project is None or proj == project:
            results.append({"project": proj, "env": env, "level": level})
    results.sort(key=lambda x: (VALID_LEVELS.index(x["level"]), x["project"], x["env"]))
    return results
