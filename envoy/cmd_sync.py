"""CLI commands for syncing environments."""

import click
from envoy.cli import get_passphrase
from envoy import sync


@click.group("sync")
def sync_group():
    """Sync, copy, or rename environments."""


@sync_group.command("merge")
@click.argument("project")
@click.argument("src_env")
@click.argument("dst_env")
def cmd_merge(project, src_env, dst_env):
    """Merge SRC_ENV into DST_ENV (dst wins on conflict)."""
    passphrase = get_passphrase()
    result = sync.sync_envs(project, src_env, dst_env, passphrase)
    added = result["added"]
    if added:
        click.echo(f"Added {len(added)} key(s) to '{dst_env}': {', '.join(added.keys())}")
    else:
        click.echo(f"No new keys to add from '{src_env}' into '{dst_env}'.")


@sync_group.command("copy")
@click.argument("project")
@click.argument("src_env")
@click.argument("dst_env")
def cmd_copy(project, src_env, dst_env):
    """Overwrite DST_ENV with an exact copy of SRC_ENV."""
    passphrase = get_passphrase()
    data = sync.copy_env(project, src_env, dst_env, passphrase)
    click.echo(f"Copied '{src_env}' -> '{dst_env}' ({len(data)} key(s)).")


@sync_group.command("rename")
@click.argument("project")
@click.argument("old_env")
@click.argument("new_env")
def cmd_rename(project, old_env, new_env):
    """Rename OLD_ENV to NEW_ENV."""
    passphrase = get_passphrase()
    sync.rename_env(project, old_env, new_env, passphrase)
    click.echo(f"Renamed '{old_env}' -> '{new_env}'.")
