"""CLI commands for managing env rotation reminders."""

import click
from envoy import reminder as rem


@click.group("reminder")
def reminder_group():
    """Manage rotation reminders for environments."""


@reminder_group.command("set")
@click.argument("project")
@click.argument("env")
@click.option("--days", default=30, show_default=True, help="Days until reminder is due.")
def cmd_set(project, env, days):
    """Set a rotation reminder for PROJECT/ENV."""
    due = rem.set_reminder(project, env, days)
    click.echo(f"Reminder set for {project}/{env} — due {due.strftime('%Y-%m-%d')} ({days}d)")


@reminder_group.command("remove")
@click.argument("project")
@click.argument("env")
def cmd_remove(project, env):
    """Remove a reminder for PROJECT/ENV."""
    removed = rem.remove_reminder(project, env)
    if removed:
        click.echo(f"Reminder for {project}/{env} removed.")
    else:
        click.echo(f"No reminder found for {project}/{env}.")


@reminder_group.command("list")
@click.option("--project", default=None, help="Filter by project.")
@click.option("--due", is_flag=True, default=False, help="Show only due reminders.")
def cmd_list(project, due):
    """List reminders, optionally filtered."""
    entries = rem.list_due(project=project) if due else rem.list_all(project=project)
    if not entries:
        click.echo("No reminders found.")
        return
    for e in entries:
        click.echo(f"  {e['project']}/{e['env']}  due={e['due'][:10]}  every={e['days']}d")


@reminder_group.command("check")
@click.option("--project", default=None, help="Filter by project.")
def cmd_check(project):
    """Print a warning for each overdue reminder."""
    due_entries = rem.list_due(project=project)
    if not due_entries:
        click.echo("All clear — no overdue reminders.")
        return
    click.echo(f"⚠️  {len(due_entries)} overdue reminder(s):")
    for e in due_entries:
        click.echo(f"  {e['project']}/{e['env']}  was due {e['due'][:10]}")
