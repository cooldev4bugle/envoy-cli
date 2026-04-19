"""CLI commands for locking/unlocking environments."""

import click
from envoy.lock import lock_env, unlock_env, list_locked, is_locked


@click.group(name="lock")
def lock_group():
    """Lock or unlock environments to prevent changes."""


@lock_group.command("set")
@click.argument("project")
@click.argument("env")
def cmd_lock(project: str, env: str):
    """Lock an environment."""
    if is_locked(project, env):
        click.echo(f"{env} is already locked.")
        return
    lock_env(project, env)
    click.echo(f"Locked {project}/{env}.")


@lock_group.command("unset")
@click.argument("project")
@click.argument("env")
def cmd_unlock(project: str, env: str):
    """Unlock an environment."""
    if not is_locked(project, env):
        click.echo(f"{env} is not locked.")
        return
    unlock_env(project, env)
    click.echo(f"Unlocked {project}/{env}.")


@lock_group.command("list")
@click.argument("project")
def cmd_list_locked(project: str):
    """List locked environments for a project."""
    locked = list_locked(project)
    if not locked:
        click.echo("No locked environments.")
    else:
        for env in locked:
            click.echo(f"  🔒 {env}")
