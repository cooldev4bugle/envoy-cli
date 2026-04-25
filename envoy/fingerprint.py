"""Fingerprint module: generate and verify env file fingerprints for tamper detection."""

import hashlib
import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _fp_path() -> Path:
    return get_store_dir() / "fingerprints.json"


def _load() -> dict:
    p = _fp_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _fp_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def compute(env_data: dict) -> str:
    """Return a stable SHA-256 hex digest of the sorted env key-value pairs."""
    canonical = json.dumps(dict(sorted(env_data.items())), separators=(",", ":")
    ).encode()
    return hashlib.sha256(canonical).hexdigest()


def record(project: str, env: str, env_data: dict) -> str:
    """Compute and persist a fingerprint for the given env. Returns the digest."""
    digest = compute(env_data)
    data = _load()
    data[_key(project, env)] = digest
    _save(data)
    return digest


def get_fingerprint(project: str, env: str) -> Optional[str]:
    """Return the stored fingerprint or None if not recorded."""
    return _load().get(_key(project, env))


def verify(project: str, env: str, env_data: dict) -> bool:
    """Return True if the current env data matches the stored fingerprint."""
    stored = get_fingerprint(project, env)
    if stored is None:
        return False
    return compute(env_data) == stored


def remove_fingerprint(project: str, env: str) -> bool:
    """Delete the stored fingerprint. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True
