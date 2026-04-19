"""CLI commands for profile management."""
import click
from envoy import profile
from envoy.cli import get_passphrase


@click.group(name="profile")
def profile_group():
    """Manage named env profiles."""


@profile_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project, env):
    """List saved profiles for PROJECT/ENV."""
    names = profile.list_profiles(project, env)
    if not names:
        click.echo("No profiles saved.")
    else:
        for n in names:
            click.echo(n)


@profile_group.command("save")
@click.argument("project")
@click.argument("env")
@click.argument("name")
def cmd_save(project, env, name):
    """Snapshot current ENV vars into profile NAME."""
    passphrase = get_passphrase()
    profile.save_profile(project, env, name, passphrase)
    click.echo(f"Profile '{name}' saved for {project}/{env}.")


@profile_group.command("apply")
@click.argument("project")
@click.argument("env")
@click.argument("name")
@click.option("--merge", is_flag=True, help="Merge with current vars instead of replacing.")
def cmd_apply(project, env, name, merge):
    """Apply profile NAME to PROJECT/ENV."""
    passphrase = get_passphrase()
    try:
        profile.apply_profile(project, env, name, passphrase, merge=merge)
        click.echo(f"Profile '{name}' applied to {project}/{env}.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_group.command("delete")
@click.argument("project")
@click.argument("env")
@click.argument("name")
def cmd_delete(project, env, name):
    """Delete a saved profile."""
    try:
        profile.delete_profile(project, env, name)
        click.echo(f"Profile '{name}' deleted.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
