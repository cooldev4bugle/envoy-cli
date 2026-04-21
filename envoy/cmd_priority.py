"""CLI commands for managing environment priority levels."""

import click

from envoy.priority import (
    VALID_LEVELS,
    get_priority,
    list_priorities,
    remove_priority,
    set_priority,
)


@click.group("priority")
def priority_group():
    """Manage priority levels for environments."""


@priority_group.command("set")
@click.argument("project")
@click.argument("env")
@click.argument("level", type=click.Choice(VALID_LEVELS))
def cmd_set(project: str, env: str, level: str):
    """Set the priority level for an environment."""
    try:
        set_priority(project, env, level)
        click.echo(f"Priority for {project}/{env} set to '{level}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@priority_group.command("get")
@click.argument("project")
@click.argument("env")
def cmd_get(project: str, env: str):
    """Get the priority level of an environment."""
    level = get_priority(project, env)
    click.echo(f"{project}/{env}: {level}")


@priority_group.command("remove")
@click.argument("project")
@click.argument("env")
def cmd_remove(project: str, env: str):
    """Remove a custom priority (resets to 'normal')."""
    removed = remove_priority(project, env)
    if removed:
        click.echo(f"Priority for {project}/{env} removed (reset to 'normal').")
    else:
        click.echo(f"No custom priority set for {project}/{env}.")


@priority_group.command("list")
@click.option("--project", default=None, help="Filter by project.")
def cmd_list(project):
    """List all environments with custom priority levels."""
    entries = list_priorities(project=project)
    if not entries:
        click.echo("No custom priorities set.")
        return
    for e in entries:
        click.echo(f"[{e['level'].upper():8s}] {e['project']}/{e['env']}")
