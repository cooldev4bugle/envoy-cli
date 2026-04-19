"""CLI commands for env snapshots."""

import click

from envoy import snapshot
from envoy.cli import get_passphrase


@click.group("snapshot")
def snapshot_group():
    """Create and restore env snapshots."""


@snapshot_group.command("create")
@click.argument("project")
@click.argument("env")
@click.option("--label", default=None, help="Human-readable snapshot label.")
def cmd_create(project: str, env: str, label):
    """Snapshot PROJECT/ENV."""
    passphrase = get_passphrase()
    saved_label = snapshot.create(project, env, passphrase, label)
    click.echo(f"Snapshot '{saved_label}' created for {project}/{env}.")


@snapshot_group.command("restore")
@click.argument("project")
@click.argument("env")
@click.argument("label")
def cmd_restore(project: str, env: str, label: str):
    """Restore PROJECT/ENV from snapshot LABEL."""
    passphrase = get_passphrase()
    snapshot.restore(project, env, passphrase, label)
    click.echo(f"Restored {project}/{env} from snapshot '{label}'.")


@snapshot_group.command("list")
@click.argument("project")
def cmd_list(project: str):
    """List snapshots for PROJECT."""
    labels = snapshot.list_snapshots(project)
    if not labels:
        click.echo("No snapshots found.")
    else:
        for lbl in labels:
            click.echo(lbl)


@snapshot_group.command("delete")
@click.argument("project")
@click.argument("label")
def cmd_delete(project: str, label: str):
    """Delete a snapshot."""
    snapshot.delete(project, label)
    click.echo(f"Snapshot '{label}' deleted.")
