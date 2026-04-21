"""Rollback support: restore a previous snapshot or history entry."""

from typing import Optional
from envoy import snapshot, history, vault


def rollback_to_snapshot(
    project: str,
    env: str,
    label: str,
    passphrase: str,
) -> dict:
    """Restore env to a named snapshot. Returns the restored data."""
    snaps = snapshot.list_snapshots(project, env)
    match = next((s for s in snaps if s["label"] == label), None)
    if match is None:
        raise KeyError(f"Snapshot '{label}' not found for {project}/{env}")
    data = snapshot.restore(project, env, label, passphrase)
    history.record(project, env, "rollback", {"label": label})
    return data


def rollback_to_nth(
    project: str,
    env: str,
    n: int,
    passphrase: str,
) -> dict:
    """Restore env to the Nth most-recent snapshot (1 = latest)."""
    snaps = snapshot.list_snapshots(project, env)
    if not snaps:
        raise ValueError(f"No snapshots found for {project}/{env}")
    if n < 1 or n > len(snaps):
        raise IndexError(f"Index {n} out of range (1–{len(snaps)})")
    label = snaps[-n]["label"]
    return rollback_to_snapshot(project, env, label, passphrase)


def list_rollback_points(project: str, env: str) -> list:
    """Return snapshots available for rollback, newest first."""
    snaps = snapshot.list_snapshots(project, env)
    return list(reversed(snaps))
