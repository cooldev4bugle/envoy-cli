"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir

AUDIT_FILE = "audit.log"


def _audit_path() -> Path:
    return get_store_dir() / AUDIT_FILE


def log_event(
    action: str,
    project: str,
    env: str,
    user: Optional[str] = None,
    note: Optional[str] = None,
) -> None:
    """Append a structured audit event to the log."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "project": project,
        "env": env,
        "user": user or os.environ.get("USER", "unknown"),
        "note": note,
    }
    path = _audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(event) + "\n")


def read_events(
    project: Optional[str] = None,
    env: Optional[str] = None,
    limit: int = 100,
) -> list[dict]:
    """Read audit events, optionally filtered by project/env."""
    path = _audit_path()
    if not path.exists():
        return []
    events = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if project and event.get("project") != project:
                continue
            if env and event.get("env") != env:
                continue
            events.append(event)
    return events[-limit:]


def clear_log() -> None:
    """Remove the audit log file."""
    path = _audit_path()
    if path.exists():
        path.unlink()
