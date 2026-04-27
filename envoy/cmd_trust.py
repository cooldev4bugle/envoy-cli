"""CLI commands for trust level management."""
import click

from envoy.trust import LEVELS, get_trust, is_trusted, list_trusted, remove_trust, set_trust


@click.group("trust")
def trust_group():
    """Manage trust levels for environments."""


@trust_group.command("set")
@click.argument("project")
@click.argument("env")
@click.argument("level", type=click.Choice(LEVELS))
@click.option("--note", default="", help="Optional note about this trust assignment.")
def cmd_set(project: str, env: str, level: str, note: str) -> None:
    """Assign a trust LEVEL to PROJECT/ENV."""
    set_trust(project, env, level, note=note)
    click.echo(f"Trust level for '{project}/{env}' set to '{level}'.")


@trust_group.command("get")
@click.argument("project")
@click.argument("env")
def cmd_get(project: str, env: str) -> None:
    """Show trust level for PROJECT/ENV."""
    info = get_trust(project, env)
    click.echo(f"level : {info['level']}")
    if info.get("note"):
        click.echo(f"note  : {info['note']}")


@trust_group.command("remove")
@click.argument("project")
@click.argument("env")
def cmd_remove(project: str, env: str) -> None:
    """Remove trust record for PROJECT/ENV."""
    removed = remove_trust(project, env)
    if removed:
        click.echo(f"Trust record for '{project}/{env}' removed.")
    else:
        click.echo(f"No trust record found for '{project}/{env}'.")


@trust_group.command("list")
@click.argument("project")
def cmd_list(project: str) -> None:
    """List all trust entries for PROJECT."""
    entries = list_trusted(project)
    if not entries:
        click.echo("No trust records found.")
        return
    for e in entries:
        note_part = f"  # {e['note']}" if e.get("note") else ""
        click.echo(f"  {e['env']:<20} {e['level']}{note_part}")


@trust_group.command("check")
@click.argument("project")
@click.argument("env")
@click.option("--min-level", default="medium", type=click.Choice(LEVELS), show_default=True)
def cmd_check(project: str, env: str, min_level: str) -> None:
    """Check whether PROJECT/ENV meets the minimum trust level."""
    ok = is_trusted(project, env, min_level=min_level)
    if ok:
        click.echo(f"PASS: '{project}/{env}' meets minimum trust level '{min_level}'.")
    else:
        info = get_trust(project, env)
        click.echo(
            f"FAIL: '{project}/{env}' has level '{info['level']}', "
            f"which is below '{min_level}'.",
            err=True,
        )
        raise SystemExit(1)
