import click
from envoy.alias import set_alias, remove_alias, resolve_alias, list_aliases


@click.group(name="alias")
def alias_group():
    """Manage project/env aliases."""


@alias_group.command("set")
@click.argument("alias")
@click.argument("project")
@click.argument("env")
def cmd_set(alias: str, project: str, env: str):
    """Assign an alias to a project/env pair."""
    set_alias(alias, project, env)
    click.echo(f"Alias '{alias}' -> {project}/{env} saved.")


@alias_group.command("remove")
@click.argument("alias")
def cmd_remove(alias: str):
    """Remove an alias."""
    removed = remove_alias(alias)
    if removed:
        click.echo(f"Alias '{alias}' removed.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)


@alias_group.command("resolve")
@click.argument("alias")
def cmd_resolve(alias: str):
    """Resolve an alias to its project/env pair."""
    result = resolve_alias(alias)
    if result is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    project, env = result
    click.echo(f"{project}/{env}")


@alias_group.command("list")
def cmd_list():
    """List all defined aliases."""
    aliases = list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for name, (project, env) in sorted(aliases.items()):
        click.echo(f"  {name:20s} -> {project}/{env}")
