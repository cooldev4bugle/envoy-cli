"""Rate limiting for vault operations per project/env."""

import json
import time
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

_DEFAULT_LIMIT = 60  # max operations per window
_DEFAULT_WINDOW = 3600  # seconds (1 hour)


def _rate_path() -> Path:
    return get_store_dir() / "rate_limits.json"


def _load() -> dict:
    p = _rate_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _rate_path().write_text(json.dumps(data, indent=2))


def set_limit(project: str, limit: int, window: int = _DEFAULT_WINDOW) -> None:
    """Configure rate limit for a project."""
    if limit <= 0:
        raise ValueError("limit must be a positive integer")
    if window <= 0:
        raise ValueError("window must be a positive integer")
    data = _load()
    data.setdefault(project, {})["config"] = {"limit": limit, "window": window}
    _save(data)


def get_limit(project: str) -> dict:
    """Return the rate limit config for a project."""
    data = _load()
    return data.get(project, {}).get("config", {"limit": _DEFAULT_LIMIT, "window": _DEFAULT_WINDOW})


def record_operation(project: str, env: str) -> None:
    """Record a vault operation for rate-limit tracking."""
    data = _load()
    key = f"{project}:{env}"
    now = time.time()
    ops = data.setdefault(project, {}).setdefault("ops", {}).setdefault(key, [])
    ops.append(now)
    _save(data)


def check_rate_limit(project: str, env: str) -> tuple[bool, int]:
    """Return (allowed, remaining) for the given project/env."""
    data = _load()
    cfg = data.get(project, {}).get("config", {"limit": _DEFAULT_LIMIT, "window": _DEFAULT_WINDOW})
    limit = cfg["limit"]
    window = cfg["window"]
    key = f"{project}:{env}"
    now = time.time()
    ops = data.get(project, {}).get("ops", {}).get(key, [])
    recent = [t for t in ops if now - t < window]
    remaining = max(0, limit - len(recent))
    return remaining > 0, remaining


def reset_limit(project: str, env: Optional[str] = None) -> None:
    """Clear recorded operations for a project or specific env."""
    data = _load()
    if project not in data:
        return
    if env is None:
        data[project].pop("ops", None)
    else:
        data[project].get("ops", {}).pop(f"{project}:{env}", None)
    _save(data)
