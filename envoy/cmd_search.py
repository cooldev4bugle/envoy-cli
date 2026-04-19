import click
from envoy import search


@click.group(name="search")
def search_group():
    """Search across environments and projects."""
    pass


@search_group.command("key")
@click.argument("project")
@click.argument("env")
@click.argument("pattern")
@click.option("--passphrase", prompt=True, hide_input=True)
def cmd_key(project, env, pattern, passphrase):
    """Search for keys matching PATTERN in an environment."""
    results = search.search_by_key(project, env, pattern, passphrase)
    if not results:
        click.echo("No matching keys found.")
    else:
        for k, v in results.items():
            click.echo(f"{k}={v}")


@search_group.command("value")
@click.argument("project")
@click.argument("env")
@click.argument("pattern")
@click.option("--passphrase", prompt=True, hide_input=True)
def cmd_value(project, env, pattern, passphrase):
    """Search for keys whose values match PATTERN."""
    results = search.search_by_value(project, env, pattern, passphrase)
    if not results:
        click.echo("No matching values found.")
    else:
        for k, v in results.items():
            click.echo(f"{k}={v}")


@search_group.command("global")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
def cmd_global(key, passphrase):
    """Search for a key across all projects and environments."""
    results = search.search_key_across_projects(key, passphrase)
    if not results:
        click.echo("Key not found in any project.")
    else:
        for project, env, value in results:
            click.echo(f"{project}  {env}  {key}={value}")
