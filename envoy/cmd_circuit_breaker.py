"""CLI commands for managing circuit breakers."""

import click

from envoy import circuit_breaker as cb


@click.group("breaker")
def breaker_group():
    """Manage circuit breakers for env operations."""


@breaker_group.command("status")
@click.argument("project")
@click.argument("env")
@click.option("--timeout", default=cb.DEFAULT_TIMEOUT, show_default=True, help="Half-open timeout in seconds.")
def cmd_status(project: str, env: str, timeout: int):
    """Show circuit breaker state for a project/env."""
    entry = cb.get_state(project, env)
    open_flag = cb.is_open(project, env, timeout=timeout)
    state_label = entry["state"]
    click.echo(f"Project : {project}")
    click.echo(f"Env     : {env}")
    click.echo(f"State   : {state_label}")
    click.echo(f"Failures: {entry['failures']}")
    click.echo(f"Blocked : {'yes' if open_flag else 'no'}")


@breaker_group.command("reset")
@click.argument("project")
@click.argument("env")
def cmd_reset(project: str, env: str):
    """Reset (close) the circuit breaker for a project/env."""
    cb.reset(project, env)
    click.echo(f"Circuit breaker reset for {project}/{env}.")


@breaker_group.command("trip")
@click.argument("project")
@click.argument("env")
@click.option("--threshold", default=cb.DEFAULT_THRESHOLD, show_default=True)
def cmd_trip(project: str, env: str, threshold: int):
    """Manually record a failure (for testing/debugging)."""
    entry = cb.record_failure(project, env, threshold=threshold)
    click.echo(f"Failure recorded. State: {entry['state']}, Failures: {entry['failures']}")
