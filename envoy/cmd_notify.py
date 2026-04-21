"""CLI commands for managing notification preferences."""

import click

from envoy import notify as _notify


@click.group("notify")
def notify_group() -> None:
    """Manage notification preferences for env events."""


@notify_group.command("set")
@click.argument("project")
@click.argument("event")
@click.argument("channel")
@click.option("--disable", is_flag=True, default=False, help="Disable instead of enable.")
def cmd_set(project: str, event: str, channel: str, disable: bool) -> None:
    """Enable or disable a notification channel for a project event."""
    try:
        _notify.set_preference(project, event, channel, enabled=not disable)
        state = "disabled" if disable else "enabled"
        click.echo(f"Notification '{channel}' {state} for [{project}] on event '{event}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@notify_group.command("get")
@click.argument("project")
@click.argument("event")
@click.argument("channel")
def cmd_get(project: str, event: str, channel: str) -> None:
    """Check if a notification channel is enabled for a project event."""
    enabled = _notify.get_preference(project, event, channel)
    status = "enabled" if enabled else "disabled"
    click.echo(f"[{project}] {event}/{channel}: {status}")


@notify_group.command("list")
@click.argument("project")
def cmd_list(project: str) -> None:
    """List all notification preferences for a project."""
    prefs = _notify.get_project_preferences(project)
    if not prefs:
        click.echo(f"No notification preferences set for '{project}'.")
        return
    for event, channels in sorted(prefs.items()):
        for channel, enabled in sorted(channels.items()):
            state = "on" if enabled else "off"
            click.echo(f"  {event:12s}  {channel:10s}  {state}")


@notify_group.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="Clear all notification preferences for this project?")
def cmd_clear(project: str) -> None:
    """Remove all notification preferences for a project."""
    _notify.clear_preferences(project)
    click.echo(f"Cleared notification preferences for '{project}'.")
