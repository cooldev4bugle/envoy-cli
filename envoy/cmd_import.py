"""CLI commands for importing .env variables from external formats."""

import json
import sys

import click

from envoy import vault
from envoy.cli import get_passphrase
from envoy.import_env import from_shell, from_json, from_docker_env, merge_into


@click.group(name="import")
def import_group():
    """Import environment variables from external sources."""


@import_group.command("shell")
@click.argument("project")
@click.argument("env")
@click.option("--file", "filepath", default=None, help="Path to shell export file (stdin if omitted).")
@click.option("--keys", default=None, help="Comma-separated list of keys to import.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def cmd_shell(project, env, filepath, keys, overwrite):
    """Import variables from a shell export file or stdin."""
    filter_keys = [k.strip() for k in keys.split(",")] if keys else None

    if filepath:
        with open(filepath, "r") as f:
            text = f.read()
    else:
        if sys.stdin.isatty():
            click.echo("Reading from stdin... (pipe data or use --file)")
        text = sys.stdin.read()

    try:
        imported = from_shell(text, filter_keys=filter_keys)
    except ValueError as e:
        click.echo(f"Error parsing shell input: {e}", err=True)
        raise SystemExit(1)

    passphrase = get_passphrase()

    try:
        existing = vault.pull(project, env, passphrase)
    except FileNotFoundError:
        existing = {}

    merged = merge_into(existing, imported, overwrite=overwrite)
    vault.push(project, env, merged, passphrase)

    click.echo(f"Imported {len(imported)} key(s) into {project}/{env}.")


@import_group.command("json")
@click.argument("project")
@click.argument("env")
@click.option("--file", "filepath", default=None, help="Path to JSON file (stdin if omitted).")
@click.option("--keys", default=None, help="Comma-separated list of keys to import.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def cmd_json(project, env, filepath, keys, overwrite):
    """Import variables from a JSON object file or stdin."""
    filter_keys = [k.strip() for k in keys.split(",")] if keys else None

    if filepath:
        with open(filepath, "r") as f:
            text = f.read()
    else:
        if sys.stdin.isatty():
            click.echo("Reading from stdin... (pipe data or use --file)")
        text = sys.stdin.read()

    try:
        imported = from_json(text, filter_keys=filter_keys)
    except (ValueError, json.JSONDecodeError) as e:
        click.echo(f"Error parsing JSON input: {e}", err=True)
        raise SystemExit(1)

    passphrase = get_passphrase()

    try:
        existing = vault.pull(project, env, passphrase)
    except FileNotFoundError:
        existing = {}

    merged = merge_into(existing, imported, overwrite=overwrite)
    vault.push(project, env, merged, passphrase)

    click.echo(f"Imported {len(imported)} key(s) into {project}/{env}.")


@import_group.command("docker")
@click.argument("project")
@click.argument("env")
@click.option("--file", "filepath", default=None, help="Path to docker --env-file (stdin if omitted).")
@click.option("--keys", default=None, help="Comma-separated list of keys to import.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def cmd_docker(project, env, filepath, keys, overwrite):
    """Import variables from a Docker-style env file (KEY=VALUE lines)."""
    filter_keys = [k.strip() for k in keys.split(",")] if keys else None

    if filepath:
        with open(filepath, "r") as f:
            text = f.read()
    else:
        if sys.stdin.isatty():
            click.echo("Reading from stdin... (pipe data or use --file)")
        text = sys.stdin.read()

    try:
        imported = from_docker_env(text, filter_keys=filter_keys)
    except ValueError as e:
        click.echo(f"Error parsing Docker env input: {e}", err=True)
        raise SystemExit(1)

    passphrase = get_passphrase()

    try:
        existing = vault.pull(project, env, passphrase)
    except FileNotFoundError:
        existing = {}

    merged = merge_into(existing, imported, overwrite=overwrite)
    vault.push(project, env, merged, passphrase)

    click.echo(f"Imported {len(imported)} key(s) into {project}/{env}.")
