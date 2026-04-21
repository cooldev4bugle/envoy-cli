"""Alias support: map short names to (project, env) pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _alias_path() -> Path:
    return get_store_dir() / "aliases.json"


def _load_aliases() -> dict[str, dict]:
    p = _alias_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(data: dict[str, dict]) -> None:
    _alias_path().write_text(json.dumps(data, indent=2))


def set_alias(alias: str, project: str, env: str) -> None:
    """Create or overwrite an alias pointing to (project, env)."""
    data = _load_aliases()
    data[alias] = {"project": project, "env": env}
    _save_aliases(data)


def remove_alias(alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    data = _load_aliases()
    if alias not in data:
        return False
    del data[alias]
    _save_aliases(data)
    return True


def resolve_alias(alias: str) -> Optional[tuple[str, str]]:
    """Return (project, env) for the alias, or None if not found."""
    data = _load_aliases()
    entry = data.get(alias)
    if entry is None:
        return None
    return entry["project"], entry["env"]


def list_aliases() -> list[dict]:
    """Return all aliases as a list of dicts with keys alias/project/env."""
    data = _load_aliases()
    return [
        {"alias": k, "project": v["project"], "env": v["env"]}
        for k, v in sorted(data.items())
    ]
