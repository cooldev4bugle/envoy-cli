"""Track the lineage (origin/derivation chain) of environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _lineage_path() -> Path:
    return get_store_dir() / "lineage.json"


def _load() -> dict:
    p = _lineage_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _lineage_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, variable: str) -> str:
    return f"{project}::{env}::{variable}"


def set_origin(
    project: str,
    env: str,
    variable: str,
    source_project: str,
    source_env: str,
    note: Optional[str] = None,
) -> dict:
    """Record that a variable was derived from another project/env."""
    data = _load()
    entry = {
        "source_project": source_project,
        "source_env": source_env,
        "note": note or "",
    }
    data[_key(project, env, variable)] = entry
    _save(data)
    return entry


def get_origin(
    project: str, env: str, variable: str
) -> Optional[dict]:
    """Return the lineage entry for a variable, or None if untracked."""
    data = _load()
    return data.get(_key(project, env, variable))


def remove_origin(project: str, env: str, variable: str) -> bool:
    """Remove lineage record. Returns True if it existed."""
    data = _load()
    k = _key(project, env, variable)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_lineage(project: str, env: str) -> dict[str, dict]:
    """Return all lineage entries for a given project+env."""
    data = _load()
    prefix = f"{project}::{env}::"
    return {
        k.split("::", 2)[2]: v
        for k, v in data.items()
        if k.startswith(prefix)
    }
