import click
from envoy import history


@click.group(name="history")
def history_group():
    """View and manage push/pull history for environments."""
    pass


@history_group.command(name="log")
@click.argument("project")
@click.option("--env", default=None, help="Filter by environment name.")
@click.option("--action", default=None, help="Filter by action (push/pull/delete).")
@click.option("--limit", default=20, show_default=True, help="Max number of entries to show.")
def cmd_log(project, env, action, limit):
    """Show history log for a project."""
    events = history.get_history(project, env=env, action=action)
    if not events:
        click.echo("No history found.")
        return
    for entry in events[-limit:]:
        ts = entry.get("timestamp", "?")
        act = entry.get("action", "?")
        ev = entry.get("env", "?")
        user = entry.get("user", "unknown")
        click.echo(f"[{ts}] {act.upper():6s}  env={ev}  user={user}")


@history_group.command(name="clear")
@click.argument("project")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def cmd_clear(project, yes):
    """Clear history log for a project."""
    if not yes:
        click.confirm(f"Clear all history for '{project}'?", abort=True)
    history.clear_history(project)
    click.echo(f"History cleared for '{project}'.")
