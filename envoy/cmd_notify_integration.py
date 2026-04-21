"""Integration helpers: fire notifications as a side-effect of vault operations."""

from __future__ import annotations

from typing import Any

from envoy import notify as _notify


def fire(project: str, event: str, details: dict[str, Any] | None = None) -> None:
    """Dispatch a notification for a vault event and print to stdout if configured."""
    message = _build_message(project, event, details or {})
    channels = _notify.notify(project, event, message)
    if "stdout" in channels:
        _emit_stdout(project, event, message)


def _build_message(project: str, event: str, details: dict[str, Any]) -> str:
    parts = [f"[{project}] event={event}"]
    for k, v in sorted(details.items()):
        parts.append(f"{k}={v}")
    return " ".join(parts)


def _emit_stdout(project: str, event: str, message: str) -> None:
    import click
    click.echo(f"\U0001f514 notify: {message}")


# ---------------------------------------------------------------------------
# Convenience wrappers used by other commands
# ---------------------------------------------------------------------------

def on_push(project: str, env: str) -> None:
    fire(project, "push", {"env": env})


def on_pull(project: str, env: str) -> None:
    fire(project, "pull", {"env": env})


def on_remove(project: str, env: str) -> None:
    fire(project, "remove", {"env": env})


def on_rotate(project: str, env: str | None = None) -> None:
    details: dict[str, Any] = {}
    if env:
        details["env"] = env
    fire(project, "rotate", details)


def on_lock(project: str, env: str) -> None:
    fire(project, "lock", {"env": env})


def on_unlock(project: str, env: str) -> None:
    fire(project, "unlock", {"env": env})
