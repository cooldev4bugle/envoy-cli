"""Circuit breaker for protecting against repeated failures on env operations."""

import json
import time
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

STATE_CLOSED = "closed"
STATE_OPEN = "open"
STATE_HALF_OPEN = "half_open"

DEFAULT_THRESHOLD = 5
DEFAULT_TIMEOUT = 60  # seconds


def _cb_path() -> Path:
    return get_store_dir() / "circuit_breakers.json"


def _load() -> dict:
    p = _cb_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _cb_path().write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def get_state(project: str, env: str) -> dict:
    data = _load()
    k = _key(project, env)
    return data.get(k, {"state": STATE_CLOSED, "failures": 0, "opened_at": None})


def record_failure(project: str, env: str, threshold: int = DEFAULT_THRESHOLD) -> dict:
    data = _load()
    k = _key(project, env)
    entry = data.get(k, {"state": STATE_CLOSED, "failures": 0, "opened_at": None})
    entry["failures"] += 1
    if entry["failures"] >= threshold and entry["state"] == STATE_CLOSED:
        entry["state"] = STATE_OPEN
        entry["opened_at"] = time.time()
    data[k] = entry
    _save(data)
    return entry


def record_success(project: str, env: str) -> dict:
    data = _load()
    k = _key(project, env)
    entry = {"state": STATE_CLOSED, "failures": 0, "opened_at": None}
    data[k] = entry
    _save(data)
    return entry


def is_open(project: str, env: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    entry = get_state(project, env)
    if entry["state"] == STATE_CLOSED:
        return False
    if entry["state"] == STATE_OPEN:
        opened_at = entry.get("opened_at") or 0
        if time.time() - opened_at >= timeout:
            _transition_half_open(project, env)
            return False
        return True
    return False  # half_open allows one attempt


def _transition_half_open(project: str, env: str) -> None:
    data = _load()
    k = _key(project, env)
    if k in data:
        data[k]["state"] = STATE_HALF_OPEN
        _save(data)


def reset(project: str, env: str) -> None:
    data = _load()
    k = _key(project, env)
    data.pop(k, None)
    _save(data)
