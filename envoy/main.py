import click
from envoy.cli import cli
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


if __name__ == "__main__":
    cli()
