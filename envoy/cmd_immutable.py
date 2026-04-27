"""CLI commands for managing immutable env keys."""

import click

from envoy import immutable as imm


@click.group(name="immutable")
def immutable_group():
    """Manage immutable (write-protected) env keys."""


@immutable_group.command("add")
@click.argument("project")
@click.argument("env")
@click.argument("key")
@click.option("--reason", default="", help="Optional reason for immutability.")
def cmd_add(project: str, env: str, key: str, reason: str) -> None:
    """Mark KEY as immutable in PROJECT/ENV."""
    imm.mark_immutable(project, env, key, reason=reason)
    click.echo(f"Key '{key}' in {project}/{env} marked as immutable.")
    if reason:
        click.echo(f"Reason: {reason}")


@immutable_group.command("remove")
@click.argument("project")
@click.argument("env")
@click.argument("key")
def cmd_remove(project: str, env: str, key: str) -> None:
    """Remove immutability from KEY in PROJECT/ENV."""
    removed = imm.unmark_immutable(project, env, key)
    if removed:
        click.echo(f"Immutability removed from '{key}' in {project}/{env}.")
    else:
        click.echo(f"Key '{key}' in {project}/{env} was not marked immutable.")


@immutable_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project: str, env: str) -> None:
    """List all immutable keys for PROJECT/ENV."""
    keys = imm.get_immutable_keys(project, env)
    if not keys:
        click.echo(f"No immutable keys found for {project}/{env}.")
        return
    for entry in keys:
        reason_str = f"  ({entry['reason']})" if entry["reason"] else ""
        click.echo(f"  {entry['key']}{reason_str}")


@immutable_group.command("check")
@click.argument("project")
@click.argument("env")
@click.argument("key")
def cmd_check(project: str, env: str, key: str) -> None:
    """Check whether KEY in PROJECT/ENV is immutable."""
    if imm.is_immutable(project, env, key):
        click.echo(f"'{key}' is IMMUTABLE in {project}/{env}.")
    else:
        click.echo(f"'{key}' is mutable in {project}/{env}.")
