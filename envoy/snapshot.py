"""Snapshot: capture and restore point-in-time copies of an env."""

from __future__ import annotations

import time
from typing import Optional

from envoy import vault, storage


def _snapshot_key(label: str) -> str:
    return f"__snapshot__{label}"


def create(project: str, env: str, passphrase: str, label: Optional[str] = None) -> str:
    """Save a snapshot of *env* under an auto or user-supplied label."""
    label = label or str(int(time.time()))
    data = vault.pull(project, env, passphrase)
    snap_env = _snapshot_key(label)
    vault.push(project, snap_env, data, passphrase)
    return label


def restore(project: str, env: str, passphrase: str, label: str) -> None:
    """Overwrite *env* with the contents of the named snapshot."""
    snap_env = _snapshot_key(label)
    data = vault.pull(project, snap_env, passphrase)
    vault.push(project, env, data, passphrase)


def list_snapshots(project: str) -> list[str]:
    """Return snapshot labels available for *project*."""
    prefix = "__snapshot__"
    envs = storage.list_environments(project)
    return [e[len(prefix):] for e in envs if e.startswith(prefix)]


def delete(project: str, label: str) -> None:
    """Remove a snapshot."""
    vault.remove(project, _snapshot_key(label))
