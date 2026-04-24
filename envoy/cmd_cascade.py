"""CLI commands for the cascade feature."""

import click
from envoy.cascade import cascade_key, cascade_env
from envoy.cli import get_passphrase


@click.group("cascade")
def cascade_group() -> None:
    """Propagate env values across environments."""


@cascade_group.command("key")
@click.argument("project")
@click.argument("source_env")
@click.argument("key")
@click.argument("targets", nargs=-1, required=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--passphrase", default=None, envvar="ENVOY_PASSPHRASE")
def cmd_key(
    project: str,
    source_env: str,
    key: str,
    targets: tuple[str, ...],
    overwrite: bool,
    passphrase: str | None,
) -> None:
    """Cascade a single KEY from SOURCE_ENV into TARGETS."""
    from envoy import vault

    passphrase = get_passphrase(passphrase)
    source_data = vault.pull(project, source_env, passphrase)
    if key not in source_data:
        click.echo(f"Key '{key}' not found in {source_env}.", err=True)
        raise SystemExit(1)

    results = cascade_key(
        project, key, source_data[key], passphrase, source_env, list(targets), overwrite
    )
    for env, status in results.items():
        click.echo(f"  {env}: {status}")


@cascade_group.command("env")
@click.argument("project")
@click.argument("source_env")
@click.argument("targets", nargs=-1, required=True)
@click.option("-k", "--key", "keys", multiple=True, help="Limit to specific keys.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--passphrase", default=None, envvar="ENVOY_PASSPHRASE")
def cmd_env(
    project: str,
    source_env: str,
    targets: tuple[str, ...],
    keys: tuple[str, ...],
    overwrite: bool,
    passphrase: str | None,
) -> None:
    """Cascade all (or selected) keys from SOURCE_ENV into TARGETS."""
    passphrase = get_passphrase(passphrase)
    selected_keys = list(keys) if keys else None
    results = cascade_env(
        project, source_env, list(targets), passphrase, selected_keys, overwrite
    )
    for env, key_results in results.items():
        click.echo(f"[{env}]")
        for k, status in key_results.items():
            click.echo(f"  {k}: {status}")
