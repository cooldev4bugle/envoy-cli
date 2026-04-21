"""Expiry management for env entries — set and check expiration dates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _expiry_path() -> Path:
    return get_store_dir() / "expiry.json"


def _load() -> dict:
    p = _expiry_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _expiry_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def set_expiry(project: str, env: str, expires_at: datetime) -> None:
    """Record an expiry datetime (UTC) for a given project/env."""
    if expires_at.tzinfo is None:
        raise ValueError("expires_at must be timezone-aware")
    data = _load()
    data[_key(project, env)] = expires_at.strftime(_DATE_FMT)
    _save(data)


def get_expiry(project: str, env: str) -> Optional[datetime]:
    """Return the expiry datetime for a project/env, or None if not set."""
    data = _load()
    raw = data.get(_key(project, env))
    if raw is None:
        return None
    return datetime.strptime(raw, _DATE_FMT).replace(tzinfo=timezone.utc)


def remove_expiry(project: str, env: str) -> bool:
    """Remove expiry for a project/env. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def is_expired(project: str, env: str) -> bool:
    """Return True if the env has an expiry that is in the past."""
    exp = get_expiry(project, env)
    if exp is None:
        return False
    return datetime.now(tz=timezone.utc) >= exp


def list_expiring(project: str) -> list[dict]:
    """List all envs for a project that have an expiry set."""
    data = _load()
    prefix = f"{project}::"
    results = []
    for k, v in data.items():
        if k.startswith(prefix):
            env = k[len(prefix):]
            exp = datetime.strptime(v, _DATE_FMT).replace(tzinfo=timezone.utc)
            results.append({"env": env, "expires_at": exp, "expired": datetime.now(tz=timezone.utc) >= exp})
    return results
