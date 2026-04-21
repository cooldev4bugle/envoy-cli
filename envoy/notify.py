"""Notification preferences: control how and when users are notified of env changes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir

VALID_EVENTS = {"push", "pull", "remove", "rotate", "lock", "unlock"}
VALID_CHANNELS = {"stdout", "webhook", "file"}


def _notify_path() -> Path:
    return get_store_dir() / "notifications.json"


def _load() -> dict[str, Any]:
    p = _notify_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict[str, Any]) -> None:
    _notify_path().write_text(json.dumps(data, indent=2))


def set_preference(project: str, event: str, channel: str, enabled: bool = True) -> None:
    if event not in VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid: {sorted(VALID_EVENTS)}")
    if channel not in VALID_CHANNELS:
        raise ValueError(f"Unknown channel '{channel}'. Valid: {sorted(VALID_CHANNELS)}")
    data = _load()
    data.setdefault(project, {})
    data[project].setdefault(event, {})
    data[project][event][channel] = enabled
    _save(data)


def get_preference(project: str, event: str, channel: str) -> bool:
    data = _load()
    return data.get(project, {}).get(event, {}).get(channel, False)


def get_project_preferences(project: str) -> dict[str, Any]:
    return _load().get(project, {})


def clear_preferences(project: str) -> None:
    data = _load()
    data.pop(project, None)
    _save(data)


def notify(project: str, event: str, message: str) -> list[str]:
    """Dispatch a notification for the given project/event. Returns list of channels used."""
    prefs = get_project_preferences(project)
    channels_used: list[str] = []
    event_prefs = prefs.get(event, {})
    for channel, enabled in event_prefs.items():
        if enabled:
            channels_used.append(channel)
    return channels_used
