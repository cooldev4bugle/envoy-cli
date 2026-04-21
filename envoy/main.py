"""Entry point for the envoy CLI."""

import click

from envoy.cli import get_passphrase, cmd_push, cmd_pull, cmd_list, cmd_remove
from envoy.cmd_audit import audit_group
from envoy.cmd_sync import sync_group
from envoy.cmd_profile import profile_group
from envoy.cmd_rotate import rotate_group
from envoy.cmd_template import template_group
from envoy.cmd_history import history_group
from envoy.cmd_search import search_group
from envoy.cmd_compare import compare_group
from envoy.cmd_lock import lock_group
from envoy.cmd_tag import tag_group
from envoy.cmd_snapshot import snapshot_group
from envoy.cmd_import import import_group
from envoy.cmd_pin import pin_group
from envoy.cmd_export import export_group
from envoy.cmd_reminder import reminder_group
from envoy.cmd_access import access_group
from envoy.cmd_quota import quota_group
from envoy.cmd_webhook import webhook_group


@click.group()
def cli():
    """envoy — manage and sync .env files securely."""


cli.add_command(cmd_push, name="push")
cli.add_command(cmd_pull, name="pull")
cli.add_command(cmd_list, name="list")
cli.add_command(cmd_remove, name="remove")
cli.add_command(audit_group)
cli.add_command(sync_group)
cli.add_command(profile_group)
cli.add_command(rotate_group)
cli.add_command(template_group)
cli.add_command(history_group)
cli.add_command(search_group)
cli.add_command(compare_group)
cli.add_command(lock_group)
cli.add_command(tag_group)
cli.add_command(snapshot_group)
cli.add_command(import_group)
cli.add_command(pin_group)
cli.add_command(export_group)
cli.add_command(reminder_group)
cli.add_command(access_group)
cli.add_command(quota_group)
cli.add_command(webhook_group)


if __name__ == "__main__":
    cli()
