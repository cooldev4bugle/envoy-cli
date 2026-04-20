"""CLI commands for access control."""

from __future__ import annotations

import click

from envoy import access as ac


@click.group("access")
def access_group() -> None:
    """Manage per-environment user access rules."""


@access_group.command("grant")
@click.argument("project")
@click.argument("env")
@click.argument("user")
def cmd_grant(project: str, env: str, user: str) -> None:
    """Grant USER access to ENV in PROJECT."""
    ac.grant(project, env, user)
    click.echo(f"Granted '{user}' access to '{project}/{env}'.")


@access_group.command("revoke")
@click.argument("project")
@click.argument("env")
@click.argument("user")
def cmd_revoke(project: str, env: str, user: str) -> None:
    """Revoke USER access to ENV in PROJECT."""
    removed = ac.revoke(project, env, user)
    if removed:
        click.echo(f"Revoked '{user}' access to '{project}/{env}'.")
    else:
        click.echo(f"'{user}' did not have access to '{project}/{env}'.")


@access_group.command("check")
@click.argument("project")
@click.argument("env")
@click.argument("user")
def cmd_check(project: str, env: str, user: str) -> None:
    """Check whether USER can access ENV in PROJECT."""
    if ac.is_allowed(project, env, user):
        click.echo(f"'{user}' has access to '{project}/{env}'.")
    else:
        click.echo(f"'{user}' does NOT have access to '{project}/{env}'.")


@access_group.command("list")
@click.argument("project")
@click.option("--env", default=None, help="Filter to a specific environment.")
def cmd_list(project: str, env: str | None) -> None:
    """List access rules for PROJECT."""
    rules = ac.list_access(project, env)
    if not rules:
        click.echo("No access rules found.")
        return
    for e, users in sorted(rules.items()):
        users_str = ", ".join(users) if users else "(none)"
        click.echo(f"  {e}: {users_str}")


@access_group.command("clear")
@click.argument("project")
@click.argument("env")
@click.confirmation_option(prompt="Remove all access rules for this env?")
def cmd_clear(project: str, env: str) -> None:
    """Clear all access rules for ENV in PROJECT."""
    ac.clear_access(project, env)
    click.echo(f"Cleared access rules for '{project}/{env}'.")
