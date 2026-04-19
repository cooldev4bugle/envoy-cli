"""CLI commands for comparing environments."""
import click
from envoy.compare import compare_envs, summary
from envoy.cli import get_passphrase


@click.group("compare")
def compare_group():
    """Compare .env files across environments."""


@compare_group.command("envs")
@click.argument("project")
@click.argument("env_a")
@click.argument("env_b")
@click.option("--passphrase", "-p", default=None, help="Encryption passphrase")
@click.option("--summary-only", is_flag=True, default=False)
def cmd_compare_envs(project, env_a, env_b, passphrase, summary_only):
    """Compare two environments within a project."""
    passphrase = passphrase or get_passphrase()
    try:
        diff = compare_envs(project, env_a, env_b, passphrase)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not diff:
        click.echo("Environments are identical.")
        return

    if summary_only:
        s = summary(diff)
        click.echo(
            f"Changed: {s['changed']}  Only in {env_a}: {s['only_in_a']}  Only in {env_b}: {s['only_in_b']}"
        )
        return

    for key, (va, vb) in diff.items():
        if va is None:
            click.echo(f"+ {key}={vb}  (only in {env_b})")
        elif vb is None:
            click.echo(f"- {key}={va}  (only in {env_a})")
        else:
            click.echo(f"~ {key}: {va!r} -> {vb!r}")
