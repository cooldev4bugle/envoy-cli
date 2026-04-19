"""Track push/pull history for env files."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from envoy.storage import get_store_dir


def _history_path(project: str) -> Path:
    return get_store_dir() / project / "history.json"


def _load_raw(project: str) -> list[dict]:
    p = _history_path(project)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def record(project: str, env: str, action: str, note: str = "") -> None:
    """Append a history entry for the given project/env."""
    entries = _load_raw(project)
    entries.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "env": env,
        "action": action,
        "note": note,
    })
    p = _history_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(entries, indent=2))


def get_history(
    project: str,
    env: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """Return history entries, optionally filtered."""
    entries = _load_raw(project)
    if env:
        entries = [e for e in entries if e["env"] == env]
    if action:
        entries = [e for e in entries if e["action"] == action]
    return entries[-limit:]


def clear_history(project: str) -> None:
    """Delete history for a project."""
    p = _history_path(project)
    if p.exists():
        p.unlink()
