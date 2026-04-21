"""Watermark support: embed metadata into stored env snapshots."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from envoy import storage

_WATERMARK_FILE = "watermarks.json"


def _watermark_path() -> Path:
    return storage.get_store_dir() / _WATERMARK_FILE


def _load() -> dict:
    p = _watermark_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _watermark_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def set_watermark(project: str, env: str, author: str, note: str = "") -> dict[str, Any]:
    """Attach a watermark (author + timestamp + note) to a project/env."""
    data = _load()
    k = _key(project, env)
    entry: dict[str, Any] = {
        "author": author,
        "note": note,
        "timestamp": time.time(),
    }
    data[k] = entry
    _save(data)
    return entry


def get_watermark(project: str, env: str) -> dict[str, Any] | None:
    """Return the watermark for a project/env, or None if not set."""
    data = _load()
    return data.get(_key(project, env))


def remove_watermark(project: str, env: str) -> bool:
    """Remove a watermark. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_watermarks(project: str | None = None) -> list[dict[str, Any]]:
    """List all watermarks, optionally filtered by project."""
    data = _load()
    results = []
    for k, v in data.items():
        proj, env = k.split("::", 1)
        if project and proj != project:
            continue
        results.append({"project": proj, "env": env, **v})
    return results
