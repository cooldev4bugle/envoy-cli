"""CLI commands for audit log inspection."""

import click
from envoy.audit import read_events, clear_log


@click.group("audit")
def audit_group():
    """View and manage the audit log."""


@audit_group.command("log")
@click.option("--project", "-p", default=None, help="Filter by project name")
@click.option("--env", "-e", default=None, help="Filter by environment name")
@click.option("--limit", "-n", default=50, show_default=True, help="Max entries to show")
def cmd_log(project, env, limit):
    """Display recent audit log entries."""
    events = read_events(project=project, env=env, limit=limit)
    if not events:
        click.echo("No audit events found.")
        return
    for e in events:
        note = f" — {e['note']}" if e.get("note") else ""
        click.echo(
            f"[{e['timestamp']}] {e['user']:12s} {e['action']:8s} "
            f"{e['project']}/{e['env']}{note}"
        )


@audit_group.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def cmd_clear():
    """Permanently delete the audit log."""
    clear_log()
    click.echo("Audit log cleared.")
