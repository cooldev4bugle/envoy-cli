"""CLI commands for managing environment quotas per project."""

import click

from envoy.quota import set_quota, get_quota, remove_quota, check_quota, DEFAULT_QUOTA


@click.group(name="quota")
def quota_group():
    """Manage per-project environment quotas."""


@quota_group.command("set")
@click.argument("project")
@click.argument("limit", type=int)
def cmd_set(project: str, limit: int):
    """Set the max number of environments for PROJECT."""
    try:
        set_quota(project, limit)
        click.echo(f"Quota for '{project}' set to {limit}.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@quota_group.command("get")
@click.argument("project")
def cmd_get(project: str):
    """Show the current quota for PROJECT."""
    limit = get_quota(project)
    source = "custom" if limit != DEFAULT_QUOTA else "default"
    click.echo(f"{project}: {limit} environments ({source})")


@quota_group.command("remove")
@click.argument("project")
def cmd_remove(project: str):
    """Remove a custom quota for PROJECT (reverts to default)."""
    removed = remove_quota(project)
    if removed:
        click.echo(f"Custom quota for '{project}' removed (reverted to default {DEFAULT_QUOTA}).")
    else:
        click.echo(f"No custom quota found for '{project}'.")


@quota_group.command("status")
@click.argument("project")
def cmd_status(project: str):
    """Show current usage vs quota for PROJECT."""
    count, limit, ok = check_quota(project)
    bar = "OK" if ok else "EXCEEDED"
    click.echo(f"{project}: {count}/{limit} environments [{bar}]")
