"""CLI commands for managing pinned env keys."""

from __future__ import annotations

import click

from envoy.pin import pin_key, unpin_key, get_pinned


@click.group("pin")
def pin_group():
    """Pin keys to protect them from being overwritten."""


@pin_group.command("add")
@click.argument("project")
@click.argument("env")
@click.argument("keys", nargs=-1, required=True)
def cmd_add(project: str, env: str, keys: tuple[str, ...]) -> None:
    """Pin one or more keys for PROJECT/ENV."""
    for key in keys:
        pin_key(project, env, key)
        click.echo(f"Pinned '{key}' in {project}/{env}")


@pin_group.command("remove")
@click.argument("project")
@click.argument("env")
@click.argument("keys", nargs=-1, required=True)
def cmd_remove(project: str, env: str, keys: tuple[str, ...]) -> None:
    """Unpin one or more keys for PROJECT/ENV."""
    for key in keys:
        unpin_key(project, env, key)
        click.echo(f"Unpinned '{key}' in {project}/{env}")


@pin_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project: str, env: str) -> None:
    """List all pinned keys for PROJECT/ENV."""
    pinned = get_pinned(project, env)
    if not pinned:
        click.echo(f"No pinned keys for {project}/{env}")
        return
    click.echo(f"Pinned keys for {project}/{env}:")
    for key in pinned:
        click.echo(f"  - {key}")
