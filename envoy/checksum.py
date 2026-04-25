"""Checksum tracking for env files — detect tampering or unexpected changes."""

import hashlib
import json
from pathlib import Path

from envoy.storage import get_store_dir


def _checksum_path() -> Path:
    return get_store_dir() / "checksums.json"


def _load() -> dict:
    p = _checksum_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    p = _checksum_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str) -> str:
    return f"{project}::{env}"


def compute(env_data: dict) -> str:
    """Return a stable SHA-256 hex digest for the given env dict."""
    canonical = json.dumps(env_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def record(project: str, env: str, env_data: dict) -> str:
    """Compute and store the checksum for project/env. Returns the digest."""
    digest = compute(env_data)
    data = _load()
    data[_key(project, env)] = digest
    _save(data)
    return digest


def get_checksum(project: str, env: str) -> str | None:
    """Return the stored checksum, or None if not recorded yet."""
    return _load().get(_key(project, env))


def verify(project: str, env: str, env_data: dict) -> bool:
    """Return True if env_data matches the stored checksum."""
    stored = get_checksum(project, env)
    if stored is None:
        return False
    return stored == compute(env_data)


def remove_checksum(project: str, env: str) -> bool:
    """Delete the stored checksum. Returns True if it existed."""
    data = _load()
    k = _key(project, env)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_checksums(project: str) -> dict:
    """Return {env: digest} for all envs recorded under project."""
    prefix = f"{project}::"
    return {
        k[len(prefix):]: v
        for k, v in _load().items()
        if k.startswith(prefix)
    }
