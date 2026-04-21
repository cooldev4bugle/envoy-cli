"""CLI commands for managing key dependencies."""

from __future__ import annotations

import click

from envoy import dependency as dep
from envoy.vault import pull


@click.group("dependency", help="Manage key dependencies within a project.")
def dependency_group() -> None:
    pass


@dependency_group.command("add")
@click.argument("project")
@click.argument("key")
@click.argument("depends_on", nargs=-1, required=True)
def cmd_add(project: str, key: str, depends_on: tuple) -> None:
    """Add dependency edges: KEY depends on DEPENDS_ON keys."""
    dep.add_dependency(project, key, list(depends_on))
    deps_str = ", ".join(depends_on)
    click.echo(f"Added: {key} depends on [{deps_str}] in project '{project}'.")


@dependency_group.command("remove")
@click.argument("project")
@click.argument("key")
@click.argument("depends_on")
def cmd_remove(project: str, key: str, depends_on: str) -> None:
    """Remove a single dependency edge."""
    removed = dep.remove_dependency(project, key, depends_on)
    if removed:
        click.echo(f"Removed dependency: {key} -> {depends_on}.")
    else:
        click.echo(f"Dependency not found: {key} -> {depends_on}.")


@dependency_group.command("list")
@click.argument("project")
def cmd_list(project: str) -> None:
    """List all dependency rules for a project."""
    all_deps = dep.get_all(project)
    if not all_deps:
        click.echo(f"No dependencies defined for project '{project}'.")
        return
    for key, deps in sorted(all_deps.items()):
        click.echo(f"  {key} -> [{', '.join(deps)}]")


@dependency_group.command("validate")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True)
def cmd_validate(project: str, env: str, passphrase: str) -> None:
    """Validate that all dependencies are satisfied for a given env."""
    env_data = pull(project, env, passphrase)
    violations = dep.validate(project, list(env_data.keys()))
    if not violations:
        click.echo("All dependencies satisfied.")
        return
    click.echo("Unmet dependencies detected:", err=True)
    for key, missing in sorted(violations.items()):
        click.echo(f"  {key} requires: {', '.join(missing)}", err=True)
    raise SystemExit(1)
