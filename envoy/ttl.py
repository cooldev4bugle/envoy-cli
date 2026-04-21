"""TTL (time-to-live) management for env entries.

Allows setting expiry timestamps on environments so they can be
automatically flagged or removed after a given duration.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _ttl_path() -> Path:
    return get_store_dir() / "ttl.json"


def _load_ttls() -> dict:
    p = _ttl_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttls(data: dict) -> None:
    _ttl_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def set_ttl(project: str, env: str, seconds: int) -> datetime:
    """Set a TTL for the given env. Returns the expiry datetime."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    data = _load_ttls()
    data[_key(project, env)] = expires_at.isoformat()
    _save_ttls(data)
    return expires_at


def get_ttl(project: str, env: str) -> Optional[datetime]:
    """Return the expiry datetime for the given env, or None if not set."""
    data = _load_ttls()
    raw = data.get(_key(project, env))
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_ttl(project: str, env: str) -> bool:
    """Remove the TTL for the given env. Returns True if it existed."""
    data = _load_ttls()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save_ttls(data)
    return True


def is_expired(project: str, env: str) -> bool:
    """Return True if the env has a TTL that has already passed."""
    expiry = get_ttl(project, env)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expiring(project: str) -> list[dict]:
    """Return all envs for a project that have a TTL set, with their expiry."""
    data = _load_ttls()
    prefix = f"{project}::"
    results = []
    for k, v in data.items():
        if k.startswith(prefix):
            env = k[len(prefix):]
            expiry = datetime.fromisoformat(v)
            results.append({"env": env, "expires_at": expiry, "expired": datetime.now(timezone.utc) >= expiry})
    return results
