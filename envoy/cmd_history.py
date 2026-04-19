"""CLI commands for viewing env history."""
import click
from envoy.history import get_history, clear_history


@click.group(name="history")
def history_group():
    """View and manage push/pull history."""


@history_group.command("log")
@click.argument("project")
@click.option("--env", default=None, help="Filter by environment name")
@click.option("--action", default=None, help="Filter by action (push/pull)")
@click.option("--limit", default=20, show_default=True, help="Max entries to show")
def cmd_log(project: str, env, action, limit: int):
    """Show history for a project."""
    entries = get_history(project, env=env, action=action, limit=limit)
    if not entries:
        click.echo("No history found.")
        return
    for e in entries:
        note = f"  ({e['note']})" if e.get("note") else ""
        click.echo(f"[{e['ts']}] {e['action']:6s}  {e['env']}{note}")


@history_group.command("clear")
@click.argument("project")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def cmd_clear(project: str, yes: bool):
    """Clear history for a project."""
    if not yes:
        click.confirm(f"Clear all history for '{project}'?", abort=True)
    clear_history(project)
    click.echo(f"History cleared for '{project}'.")
