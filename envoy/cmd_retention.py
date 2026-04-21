"""CLI commands for managing retention policies."""

import click

from envoy.retention import get_policy, list_policies, remove_policy, set_policy


@click.group(name="retention")
def retention_group():
    """Manage retention policies for snapshots and history."""


@retention_group.command("set")
@click.argument("project")
@click.option("--max-snapshots", type=int, default=None, help="Max number of snapshots to keep.")
@click.option("--max-history", type=int, default=None, help="Max number of history entries to keep.")
def cmd_set(project, max_snapshots, max_history):
    """Set retention policy for a project."""
    if max_snapshots is None and max_history is None:
        raise click.UsageError("Provide at least one of --max-snapshots or --max-history.")
    try:
        set_policy(project, max_snapshots=max_snapshots, max_history=max_history)
        click.echo(f"Retention policy updated for '{project}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@retention_group.command("get")
@click.argument("project")
def cmd_get(project):
    """Show the retention policy for a project."""
    policy = get_policy(project)
    click.echo(f"Project: {project}")
    click.echo(f"  max_snapshots : {policy['max_snapshots']}")
    click.echo(f"  max_history   : {policy['max_history']}")


@retention_group.command("remove")
@click.argument("project")
def cmd_remove(project):
    """Remove the retention policy for a project (resets to defaults)."""
    removed = remove_policy(project)
    if removed:
        click.echo(f"Retention policy removed for '{project}'.")
    else:
        click.echo(f"No policy found for '{project}'.")


@retention_group.command("list")
def cmd_list():
    """List all projects with explicit retention policies."""
    policies = list_policies()
    if not policies:
        click.echo("No retention policies set.")
        return
    for project, entry in policies.items():
        snap = entry.get("max_snapshots", "-")
        hist = entry.get("max_history", "-")
        click.echo(f"{project}  snapshots={snap}  history={hist}")
