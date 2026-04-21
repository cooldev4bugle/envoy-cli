"""CLI commands for managing webhooks."""

import click

from envoy import webhook


@click.group(name="webhook")
def webhook_group():
    """Manage webhook notifications."""


@webhook_group.command("add")
@click.argument("project")
@click.argument("url")
@click.option("--events", default="push,pull,remove", show_default=True,
              help="Comma-separated list of events to subscribe to.")
def cmd_add(project: str, url: str, events: str) -> None:
    """Register a webhook URL for PROJECT."""
    event_list = [e.strip() for e in events.split(",") if e.strip()]
    webhook.register(project, url, event_list)
    click.echo(f"Webhook registered for '{project}': {url}")
    click.echo(f"Events: {', '.join(event_list)}")


@webhook_group.command("remove")
@click.argument("project")
@click.argument("url")
def cmd_remove(project: str, url: str) -> None:
    """Unregister a webhook URL from PROJECT."""
    removed = webhook.unregister(project, url)
    if removed:
        click.echo(f"Webhook removed from '{project}': {url}")
    else:
        click.echo(f"No webhook found for '{project}': {url}", err=True)


@webhook_group.command("list")
@click.argument("project")
def cmd_list(project: str) -> None:
    """List registered webhooks for PROJECT."""
    hooks = webhook.list_webhooks(project)
    if not hooks:
        click.echo(f"No webhooks registered for '{project}'.")
        return
    for url, events in hooks.items():
        click.echo(f"  {url}  [{', '.join(events)}]")


@webhook_group.command("test")
@click.argument("project")
@click.option("--event", default="push", show_default=True)
def cmd_test(project: str, event: str) -> None:
    """Send a test notification for PROJECT."""
    failed = webhook.notify(project, event, {"env": "__test__", "test": True})
    if not failed:
        click.echo("All webhooks notified successfully.")
    else:
        click.echo(f"Failed to reach {len(failed)} webhook(s):")
        for url in failed:
            click.echo(f"  {url}")
