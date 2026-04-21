"""CLI commands for managing vault operation rate limits."""

import click

from envoy.rate_limit import check_rate_limit, get_limit, reset_limit, set_limit


@click.group("rate-limit", help="Manage operation rate limits per project.")
def rate_limit_group():
    pass


@rate_limit_group.command("set")
@click.argument("project")
@click.option("--limit", "-l", required=True, type=int, help="Max operations per window.")
@click.option("--window", "-w", default=3600, show_default=True, type=int, help="Window in seconds.")
def cmd_set(project, limit, window):
    """Set rate limit for PROJECT."""
    try:
        set_limit(project, limit, window)
        click.echo(f"Rate limit set: {limit} ops / {window}s for '{project}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@rate_limit_group.command("get")
@click.argument("project")
def cmd_get(project):
    """Show rate limit config for PROJECT."""
    cfg = get_limit(project)
    click.echo(f"Project : {project}")
    click.echo(f"Limit   : {cfg['limit']} ops")
    click.echo(f"Window  : {cfg['window']}s")


@rate_limit_group.command("status")
@click.argument("project")
@click.argument("env")
def cmd_status(project, env):
    """Check remaining operations for PROJECT / ENV."""
    allowed, remaining = check_rate_limit(project, env)
    status = "OK" if allowed else "BLOCKED"
    click.echo(f"[{status}] {project}/{env} — {remaining} operations remaining in window.")


@rate_limit_group.command("reset")
@click.argument("project")
@click.option("--env", "-e", default=None, help="Specific env to reset (omit for all).")
def cmd_reset(project, env):
    """Reset recorded operations for PROJECT (optionally scoped to ENV)."""
    reset_limit(project, env)
    scope = f"/{env}" if env else ""
    click.echo(f"Rate limit counters reset for '{project}{scope}'.")
