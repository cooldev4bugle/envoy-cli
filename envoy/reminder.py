"""Reminder module: schedule and check env rotation reminders."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _reminder_path() -> Path:
    return get_store_dir() / "reminders.json"


def _load_reminders() -> dict:
    path = _reminder_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_reminders(data: dict) -> None:
    _reminder_path().write_text(json.dumps(data, indent=2))


def set_reminder(project: str, env: str, days: int) -> datetime:
    """Set a rotation reminder for a project/env, due in `days` days."""
    data = _load_reminders()
    due = datetime.utcnow() + timedelta(days=days)
    key = f"{project}/{env}"
    data[key] = {"project": project, "env": env, "due": due.isoformat(), "days": days}
    _save_reminders(data)
    return due


def remove_reminder(project: str, env: str) -> bool:
    """Remove a reminder. Returns True if it existed."""
    data = _load_reminders()
    key = f"{project}/{env}"
    if key not in data:
        return False
    del data[key]
    _save_reminders(data)
    return True


def get_reminder(project: str, env: str) -> Optional[dict]:
    """Return reminder info or None."""
    return _load_reminders().get(f"{project}/{env}")


def list_due(project: Optional[str] = None) -> list[dict]:
    """Return all reminders that are due (or overdue)."""
    now = datetime.utcnow()
    results = []
    for entry in _load_reminders().values():
        if project and entry["project"] != project:
            continue
        if datetime.fromisoformat(entry["due"]) <= now:
            results.append(entry)
    return results


def list_all(project: Optional[str] = None) -> list[dict]:
    """Return all reminders, optionally filtered by project."""
    entries = list(_load_reminders().values())
    if project:
        entries = [e for e in entries if e["project"] == project]
    return entries
