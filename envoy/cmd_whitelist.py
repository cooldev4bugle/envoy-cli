"""CLI commands for managing per-env key whitelists."""

from __future__ import annotations

import click

from envoy import whitelist as wl


@click.group("whitelist")
def whitelist_group() -> None:
    """Restrict which keys are allowed for a project/environment."""


@whitelist_group.command("add")
@click.argument("project")
@click.argument("env")
@click.argument("keys", nargs=-1, required=True)
def cmd_add(project: str, env: str, keys: tuple) -> None:
    """Add one or more keys to the whitelist."""
    for key in keys:
        wl.add_key(project, env, key)
    click.echo(f"Added {len(keys)} key(s) to whitelist for {project}/{env}.")


@whitelist_group.command("remove")
@click.argument("project")
@click.argument("env")
@click.argument("key")
def cmd_remove(project: str, env: str, key: str) -> None:
    """Remove a key from the whitelist."""
    removed = wl.remove_key(project, env, key)
    if removed:
        click.echo(f"Removed '{key}' from whitelist for {project}/{env}.")
    else:
        click.echo(f"Key '{key}' was not in the whitelist for {project}/{env}.")


@whitelist_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project: str, env: str) -> None:
    """List all whitelisted keys for a project/env."""
    keys = wl.get_keys(project, env)
    if not keys:
        click.echo(f"No whitelist set for {project}/{env} — all keys are allowed.")
        return
    click.echo(f"Whitelisted keys for {project}/{env}:")
    for k in keys:
        click.echo(f"  {k}")


@whitelist_group.command("clear")
@click.argument("project")
@click.argument("env")
@click.confirmation_option(prompt="Clear the entire whitelist?")
def cmd_clear(project: str, env: str) -> None:
    """Remove the whitelist for a project/env entirely."""
    wl.clear(project, env)
    click.echo(f"Whitelist cleared for {project}/{env}.")
