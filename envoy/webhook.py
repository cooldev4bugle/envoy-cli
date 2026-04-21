"""Webhook notification support for env push/pull events."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Optional

from envoy.storage import get_store_dir

_WEBHOOK_FILE = "webhooks.json"


def _webhook_path() -> str:
    import os
    return os.path.join(get_store_dir(), _WEBHOOK_FILE)


def _load_webhooks() -> dict:
    import os
    path = _webhook_path()
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save_webhooks(data: dict) -> None:
    with open(_webhook_path(), "w") as f:
        json.dump(data, f, indent=2)


def register(project: str, url: str, events: Optional[list[str]] = None) -> None:
    """Register a webhook URL for a project."""
    data = _load_webhooks()
    data.setdefault(project, {})
    data[project][url] = events or ["push", "pull", "remove"]
    _save_webhooks(data)


def unregister(project: str, url: str) -> bool:
    """Remove a webhook. Returns True if it existed."""
    data = _load_webhooks()
    if project in data and url in data[project]:
        del data[project][url]
        if not data[project]:
            del data[project]
        _save_webhooks(data)
        return True
    return False


def list_webhooks(project: str) -> dict[str, list[str]]:
    """Return {url: [events]} for a project."""
    return _load_webhooks().get(project, {})


def notify(project: str, event: str, payload: dict) -> list[str]:
    """Fire webhooks for a project/event. Returns list of failed URLs."""
    hooks = _load_webhooks().get(project, {})
    failed = []
    body = json.dumps({"project": project, "event": event, **payload}).encode()
    for url, events in hooks.items():
        if event not in events:
            continue
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=5)
        except (urllib.error.URLError, OSError):
            failed.append(url)
    return failed
