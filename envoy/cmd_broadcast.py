import click
from envoy.broadcast import send, get_broadcasts, mark_read


@click.group(name="broadcast")
def broadcast_group():
    """Manage broadcast messages across environments."""


@broadcast_group.command(name="send")
@click.argument("project")
@click.argument("message")
@click.option("--severity", default="info", show_default=True,
              type=click.Choice(["info", "warning", "critical"]),
              help="Severity level of the broadcast.")
def cmd_send(project, message, severity):
    """Send a broadcast message to all envs in a project."""
    try:
        record = send(project, message, severity=severity)
        click.echo(f"[{severity.upper()}] Broadcast sent to project '{project}'.")
        click.echo(f"  ID      : {record['id']}")
        click.echo(f"  Message : {record['message']}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@broadcast_group.command(name="list")
@click.argument("project")
@click.option("--unread-only", is_flag=True, default=False,
              help="Show only unread broadcasts.")
@click.option("--severity", default=None,
              type=click.Choice(["info", "warning", "critical"]),
              help="Filter by severity.")
def cmd_list(project, unread_only, severity):
    """List broadcasts for a project."""
    records = get_broadcasts(project, unread_only=unread_only, severity=severity)
    if not records:
        click.echo("No broadcasts found.")
        return
    for rec in records:
        status = "UNREAD" if not rec.get("read") else "read"
        click.echo(f"[{rec['severity'].upper()}] [{status}] {rec['timestamp']}  {rec['message']}  (id={rec['id']})")


@broadcast_group.command(name="read")
@click.argument("project")
@click.argument("broadcast_id")
def cmd_read(project, broadcast_id):
    """Mark a broadcast as read."""
    changed = mark_read(project, broadcast_id)
    if changed:
        click.echo(f"Broadcast '{broadcast_id}' marked as read.")
    else:
        click.echo(f"Broadcast '{broadcast_id}' not found or already read.", err=True)
        raise SystemExit(1)
