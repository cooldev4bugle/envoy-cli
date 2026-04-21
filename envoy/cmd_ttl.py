import click
from envoy import ttl as ttl_mod


@click.group(name="ttl")
def ttl_group():
    """Manage TTL (time-to-live) expiry for environment variables."""


@ttl_group.command("set")
@click.argument("project")
@click.argument("env")
@click.argument("key")
@click.argument("seconds", type=int)
def cmd_set(project, env, key, seconds):
    """Set a TTL in seconds for a key in an env."""
    try:
        ttl_mod.set_ttl(project, env, key, seconds)
        click.echo(f"TTL set: {project}/{env}/{key} expires in {seconds}s")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ttl_group.command("get")
@click.argument("project")
@click.argument("env")
@click.argument("key")
def cmd_get(project, env, key):
    """Get the TTL entry for a key."""
    entry = ttl_mod.get_ttl(project, env, key)
    if entry is None:
        click.echo(f"No TTL set for {project}/{env}/{key}")
    else:
        click.echo(f"key={entry['key']}  seconds={entry['seconds']}  set_at={entry['set_at']}")


@ttl_group.command("remove")
@click.argument("project")
@click.argument("env")
@click.argument("key")
def cmd_remove(project, env, key):
    """Remove the TTL for a key."""
    removed = ttl_mod.remove_ttl(project, env, key)
    if removed:
        click.echo(f"TTL removed for {project}/{env}/{key}")
    else:
        click.echo(f"No TTL found for {project}/{env}/{key}")


@ttl_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project, env):
    """List all TTL entries for an env."""
    entries = ttl_mod.list_ttls(project, env)
    if not entries:
        click.echo("No TTL entries found.")
        return
    for entry in entries:
        click.echo(f"{entry['key']}  {entry['seconds']}s  set_at={entry['set_at']}")


@ttl_group.command("expired")
@click.argument("project")
@click.argument("env")
def cmd_expired(project, env):
    """Show keys whose TTL has expired."""
    entries = ttl_mod.get_expired(project, env)
    if not entries:
        click.echo("No expired keys.")
        return
    for entry in entries:
        click.echo(f"{entry['key']}  expired (ttl={entry['seconds']}s, set_at={entry['set_at']})")
