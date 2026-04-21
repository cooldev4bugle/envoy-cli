"""Broadcast a message or alert to all environments in a project."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envoy import storage, vault


def _broadcast_path(project: str) -> str:
    return str(storage._project_path(project) / "broadcasts.json")


def _load(project: str) -> list[dict]:
    import json
    from pathlib import Path

    path = Path(_broadcast_path(project))
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save(project: str, records: list[dict]) -> None:
    import json
    from pathlib import Path

    path = Path(_broadcast_path(project))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2))


def send(
    project: str,
    message: str,
    severity: str = "info",
    author: Optional[str] = None,
) -> dict:
    """Record a broadcast message for all environments in a project."""
    if severity not in ("info", "warning", "critical"):
        raise ValueError(f"Invalid severity: {severity!r}. Must be info, warning, or critical.")

    envs = vault.list_envs(project)
    record = {
        "message": message,
        "severity": severity,
        "author": author,
        "environments": envs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    records = _load(project)
    records.append(record)
    _save(project, records)
    return record


def get_broadcasts(
    project: str,
    severity: Optional[str] = None,
) -> list[dict]:
    """Return broadcasts for a project, optionally filtered by severity."""
    records = _load(project)
    if severity:
        records = [r for r in records if r["severity"] == severity]
    return records


def clear_broadcasts(project: str) -> int:
    """Delete all broadcasts for a project. Returns count removed."""
    records = _load(project)
    _save(project, [])
    return len(records)
