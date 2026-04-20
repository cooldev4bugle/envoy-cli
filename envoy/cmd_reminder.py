"""CLI commands for managing env rotation reminders."""

import click
from datetime import datetime
from envoy import reminder


@click.group(name="reminder")
def reminder_group():
    """Manage rotation reminders for environments."""
    pass


@reminder_group.command("set")
@click.argument("project")
@click.argument("env")
@click.option("--days", default=30, show_default=True, help="Remind after N days.")
@click.option("--note", default="", help="Optional note to attach to the reminder.")
def cmd_set(project, env, days, note):
    """Set a rotation reminder for PROJECT/ENV."""
    reminder.set_reminder(project, env, days=days, note=note)
    click.echo(f"Reminder set for '{project}/{env}' — every {days} day(s).")


@reminder_group.command("remove")
@click.argument("project")
@click.argument("env")
def cmd_remove(project, env):
    """Remove the reminder for PROJECT/ENV."""
    removed = reminder.remove_reminder(project, env)
    if removed:
        click.echo(f"Reminder removed for '{project}/{env}'.")
    else:
        click.echo(f"No reminder found for '{project}/{env}'.")


@reminder_group.command("list")
@click.argument("project")
def cmd_list(project):
    """List all reminders for PROJECT."""
    reminders = reminder.list_reminders(project)
    if not reminders:
        click.echo(f"No reminders set for project '{project}'.")
        return
    click.echo(f"Reminders for '{project}':")
    for r in reminders:
        due = r.get("due_date", "unknown")
        note = r.get("note", "")
        env = r.get("env", "?")
        line = f"  {env:<20} due: {due}"
        if note:
            line += f"  ({note})"
        click.echo(line)


@reminder_group.command("check")
@click.argument("project")
@click.option("--all-projects", "all_projects", is_flag=True, help="Check reminders across all projects.")
def cmd_check(project, all_projects):
    """Check which reminders are due for PROJECT."""
    today = datetime.utcnow().date()

    if all_projects:
        due = reminder.get_due_reminders()
    else:
        due = reminder.get_due_reminders(project=project)

    if not due:
        click.echo("No reminders are currently due.")
        return

    click.echo("Due reminders:")
    for r in due:
        proj = r.get("project", "?")
        env = r.get("env", "?")
        due_date = r.get("due_date", "unknown")
        note = r.get("note", "")
        line = f"  [{proj}] {env:<20} was due: {due_date}"
        if note:
            line += f"  — {note}"
        click.echo(line)
