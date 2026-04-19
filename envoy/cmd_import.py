"""CLI commands for importing env variables from external sources."""
import click
from envoy import vault
from envoy.import_env import from_shell, from_json, from_docker_env, merge_into
from envoy.cli import get_passphrase


@click.group("import")
def import_group():
    """Import env variables from external sources."""


@import_group.command("shell")
@click.argument("project")
@click.argument("env")
@click.option("--keys", "-k", multiple=True, help="Specific keys to import")
@click.option("--overwrite", is_flag=True, default=False)
def cmd_shell(project, env, keys, overwrite):
    """Import variables from the current shell environment."""
    passphrase = get_passphrase()
    incoming = from_shell(list(keys) if keys else None)
    try:
        existing = vault.pull(project, env, passphrase)
    except FileNotFoundError:
        existing = {}
    merged = merge_into(existing, incoming, overwrite=overwrite)
    vault.push(project, env, merged, passphrase)
    click.echo(f"Imported {len(incoming)} variable(s) into {project}/{env}.")


@import_group.command("json")
@click.argument("project")
@click.argument("env")
@click.argument("file", type=click.Path(exists=True))
@click.option("--overwrite", is_flag=True, default=False)
def cmd_json(project, env, file, overwrite):
    """Import variables from a JSON file."""
    passphrase = get_passphrase()
    incoming = from_json(file)
    try:
        existing = vault.pull(project, env, passphrase)
    except FileNotFoundError:
        existing = {}
    merged = merge_into(existing, incoming, overwrite=overwrite)
    vault.push(project, env, merged, passphrase)
    click.echo(f"Imported {len(incoming)} variable(s) from {file} into {project}/{env}.")


@import_group.command("docker")
@click.argument("project")
@click.argument("env")
@click.argument("file", type=click.Path(exists=True))
@click.option("--overwrite", is_flag=True, default=False)
def cmd_docker(project, env, file, overwrite):
    """Import variables from a Docker env-file."""
    passphrase = get_passphrase()
    incoming = from_docker_env(file)
    try:
        existing = vault.pull(project, env, passphrase)
    except FileNotFoundError:
        existing = {}
    merged = merge_into(existing, incoming, overwrite=overwrite)
    vault.push(project, env, merged, passphrase)
    click.echo(f"Imported {len(incoming)} variable(s) from {file} into {project}/{env}.")
