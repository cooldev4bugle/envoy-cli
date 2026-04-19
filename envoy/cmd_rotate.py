"""CLI commands for key rotation."""

import click
from envoy.cli import get_passphrase
from envoy import rotate, audit


@click.group(name="rotate")
def rotate_group():
    """Rotate encryption passphrases."""


@rotate_group.command("project")
@click.argument("project")
@click.option("--old-passphrase", envvar="ENVOY_OLD_PASSPHRASE", default=None)
@click.option("--new-passphrase", envvar="ENVOY_NEW_PASSPHRASE", default=None)
def cmd_rotate_project(project, old_passphrase, new_passphrase):
    """Re-encrypt ALL environments in PROJECT with a new passphrase."""
    old_passphrase = old_passphrase or get_passphrase("Current passphrase: ")
    new_passphrase = new_passphrase or get_passphrase("New passphrase: ")
    confirm = get_passphrase("Confirm new passphrase: ")
    if new_passphrase != confirm:
        raise click.ClickException("Passphrases do not match.")
    try:
        rotated = rotate.rotate_project(project, old_passphrase, new_passphrase)
        audit.log_event(project, "rotate_project", {"envs": rotated})
        click.echo(f"Rotated {len(rotated)} environment(s): {', '.join(rotated)}")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@rotate_group.command("env")
@click.argument("project")
@click.argument("env_name")
@click.option("--old-passphrase", envvar="ENVOY_OLD_PASSPHRASE", default=None)
@click.option("--new-passphrase", envvar="ENVOY_NEW_PASSPHRASE", default=None)
def cmd_rotate_env(project, env_name, old_passphrase, new_passphrase):
    """Re-encrypt a single ENV_NAME in PROJECT with a new passphrase."""
    old_passphrase = old_passphrase or get_passphrase("Current passphrase: ")
    new_passphrase = new_passphrase or get_passphrase("New passphrase: ")
    confirm = get_passphrase("Confirm new passphrase: ")
    if new_passphrase != confirm:
        raise click.ClickException("Passphrases do not match.")
    try:
        rotate.rotate_env(project, env_name, old_passphrase, new_passphrase)
        audit.log_event(project, "rotate_env", {"env": env_name})
        click.echo(f"Rotated '{env_name}' in project '{project}'.")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
