"""CLI commands for rollback."""

import click
from envoy import rollback
from envoy.cli import get_passphrase


@click.group("rollback", help="Rollback an env to a previous snapshot.")
def rollback_group():
    pass


@rollback_group.command("to")
@click.argument("project")
@click.argument("env")
@click.argument("label")
@click.option("--passphrase", default=None, help="Encryption passphrase.")
def cmd_to(project, env, label, passphrase):
    """Restore PROJECT/ENV to snapshot LABEL."""
    passphrase = passphrase or get_passphrase()
    try:
        rollback.rollback_to_snapshot(project, env, label, passphrase)
        click.echo(f"Rolled back {project}/{env} to snapshot '{label}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rollback_group.command("nth")
@click.argument("project")
@click.argument("env")
@click.argument("n", type=int)
@click.option("--passphrase", default=None, help="Encryption passphrase.")
def cmd_nth(project, env, n, passphrase):
    """Restore PROJECT/ENV to the Nth most-recent snapshot (1 = latest)."""
    passphrase = passphrase or get_passphrase()
    try:
        rollback.rollback_to_nth(project, env, n, passphrase)
        click.echo(f"Rolled back {project}/{env} to snapshot #{n}.")
    except (ValueError, IndexError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rollback_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project, env):
    """List available rollback points for PROJECT/ENV."""
    points = rollback.list_rollback_points(project, env)
    if not points:
        click.echo("No snapshots available.")
        return
    for i, snap in enumerate(points, 1):
        click.echo(f"  {i:>3}  {snap['label']}  ({snap.get('created_at', 'unknown')})")
