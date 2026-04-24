"""CLI commands for managing key blacklists."""

from __future__ import annotations

import click

from envoy import blacklist as bl


@click.group("blacklist")
def blacklist_group():
    """Manage blacklisted keys for a project/env."""


@blacklist_group.command("add")
@click.argument("project")
@click.argument("env")
@click.argument("keys", nargs=-1, required=True)
def cmd_add(project: str, env: str, keys: tuple):
    """Blacklist one or more KEYs from being synced."""
    for key in keys:
        updated = bl.add_key(project, env, key)
        click.echo(f"Blacklisted '{key}' for {project}/{env}. Total: {len(updated)}")


@blacklist_group.command("remove")
@click.argument("project")
@click.argument("env")
@click.argument("key")
def cmd_remove(project: str, env: str, key: str):
    """Remove a KEY from the blacklist."""
    removed = bl.remove_key(project, env, key)
    if removed:
        click.echo(f"Removed '{key}' from blacklist for {project}/{env}.")
    else:
        click.echo(f"Key '{key}' was not blacklisted for {project}/{env}.", err=True)


@blacklist_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project: str, env: str):
    """List all blacklisted keys for a project/env."""
    keys = bl.get_blacklist(project, env)
    if not keys:
        click.echo(f"No blacklisted keys for {project}/{env}.")
    else:
        for key in keys:
            click.echo(key)


@blacklist_group.command("clear")
@click.argument("project")
@click.argument("env")
@click.confirmation_option(prompt="Clear all blacklisted keys?")
def cmd_clear(project: str, env: str):
    """Clear the entire blacklist for a project/env."""
    bl.clear_blacklist(project, env)
    click.echo(f"Blacklist cleared for {project}/{env}.")
