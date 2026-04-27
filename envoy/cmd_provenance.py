"""CLI commands for managing env provenance records."""

import click

from envoy import provenance


@click.group("provenance")
def provenance_group():
    """Track and inspect env provenance (author, source, notes)."""


@provenance_group.command("set")
@click.argument("project")
@click.argument("env")
@click.option("--author", required=True, help="Who created or owns this env.")
@click.option("--source", default="manual", show_default=True, help="Origin source (e.g. manual, ci, import).")
@click.option("--note", default="", help="Optional free-text note.")
def cmd_set(project, env, author, source, note):
    """Record provenance for PROJECT/ENV."""
    entry = provenance.set_provenance(project, env, author=author, source=source, note=note)
    click.echo(f"Provenance recorded for {project}/{env}")
    click.echo(f"  author : {entry['author']}")
    click.echo(f"  source : {entry['source']}")
    click.echo(f"  at     : {entry['recorded_at']}")
    if entry["note"]:
        click.echo(f"  note   : {entry['note']}")


@provenance_group.command("get")
@click.argument("project")
@click.argument("env")
def cmd_get(project, env):
    """Show provenance for PROJECT/ENV."""
    entry = provenance.get_provenance(project, env)
    if entry is None:
        click.echo(f"No provenance recorded for {project}/{env}")
        return
    click.echo(f"author : {entry['author']}")
    click.echo(f"source : {entry['source']}")
    click.echo(f"at     : {entry['recorded_at']}")
    if entry.get("note"):
        click.echo(f"note   : {entry['note']}")


@provenance_group.command("remove")
@click.argument("project")
@click.argument("env")
def cmd_remove(project, env):
    """Remove provenance record for PROJECT/ENV."""
    removed = provenance.remove_provenance(project, env)
    if removed:
        click.echo(f"Provenance removed for {project}/{env}")
    else:
        click.echo(f"No provenance found for {project}/{env}")


@provenance_group.command("list")
@click.argument("project")
def cmd_list(project):
    """List all provenance records for PROJECT."""
    records = provenance.list_provenance(project)
    if not records:
        click.echo(f"No provenance records for project '{project}'")
        return
    for env, entry in sorted(records.items()):
        click.echo(f"{env}: author={entry['author']} source={entry['source']} at={entry['recorded_at']}")
