"""Entry point: registers all command groups."""

import click
from envoy.cli import cmd_push, cmd_pull, cmd_list, cmd_remove, cmd_diff
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
from envoy.cmd_export import export_group
from envoy.cmd_pin import pin_group
from envoy.cmd_webhook import webhook_group
from envoy.cmd_quota import quota_group
from envoy.cmd_access import access_group
from envoy.cmd_schema import schema_group
from envoy.cmd_retention import retention_group
from envoy.cmd_notify import notify_group
from envoy.cmd_dependency import dependency_group
from envoy.cmd_rollback import rollback_group


@click.group()
def cli():
    """envoy — manage and sync .env files securely."""
    pass


cli.add_command(cmd_push, "push")
cli.add_command(cmd_pull, "pull")
cli.add_command(cmd_list, "list")
cli.add_command(cmd_remove, "remove")
cli.add_command(cmd_diff, "diff")
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
cli.add_command(export_group)
cli.add_command(pin_group)
cli.add_command(webhook_group)
cli.add_command(quota_group)
cli.add_command(access_group)
cli.add_command(schema_group)
cli.add_command(retention_group)
cli.add_command(notify_group)
cli.add_command(dependency_group)
cli.add_command(rollback_group)


if __name__ == "__main__":
    cli()
