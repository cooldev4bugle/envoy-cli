"""Track the provenance (origin metadata) of env files — who created them, when, and from what source."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy import storage


def _provenance_path() -> Path:
    return storage.get_store_dir() / "provenance.json"


def _load() -> dict:
    p = _provenance_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _provenance_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def set_provenance(
    project: str,
    env: str,
    author: str,
    source: str = "manual",
    note: str = "",
) -> dict:
    """Record provenance for a project/env combination."""
    data = _load()
    entry = {
        "author": author,
        "source": source,
        "note": note,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    data[_key(project, env)] = entry
    _save(data)
    return entry


def get_provenance(project: str, env: str) -> Optional[dict]:
    """Return provenance record or None if not set."""
    return _load().get(_key(project, env))


def remove_provenance(project: str, env: str) -> bool:
    """Remove provenance record. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_provenance(project: str) -> dict[str, dict]:
    """Return all provenance entries for a project keyed by env name."""
    prefix = f"{project}::"
    return {
        k[len(prefix):]: v
        for k, v in _load().items()
        if k.startswith(prefix)
    }
