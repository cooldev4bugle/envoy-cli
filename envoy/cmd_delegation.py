"""CLI commands for managing delegations."""

import click

from envoy import delegation


@click.group(name="delegation")
def delegation_group():
    """Manage user delegations for project environments."""


@delegation_group.command("grant")
@click.argument("delegator")
@click.argument("delegate")
@click.argument("project")
@click.argument("env")
@click.option("--permission", "-p", multiple=True, default=["read"], show_default=True)
def cmd_grant(delegator, delegate, project, env, permission):
    """Grant DELEGATE the ability to act for DELEGATOR on PROJECT/ENV."""
    perms = list(permission)
    entry = delegation.grant_delegation(delegator, delegate, project, env, perms)
    granted = ", ".join(entry["delegates"][delegate])
    click.echo(f"Granted [{granted}] to '{delegate}' acting for '{delegator}' on {project}/{env}.")


@delegation_group.command("revoke")
@click.argument("delegator")
@click.argument("delegate")
@click.argument("project")
@click.argument("env")
def cmd_revoke(delegator, delegate, project, env):
    """Revoke DELEGATE's delegation for DELEGATOR on PROJECT/ENV."""
    removed = delegation.revoke_delegation(delegator, delegate, project, env)
    if removed:
        click.echo(f"Revoked delegation for '{delegate}' (was acting for '{delegator}') on {project}/{env}.")
    else:
        click.echo(f"No delegation found for '{delegate}' on {project}/{env}.")


@delegation_group.command("list")
@click.argument("delegator")
@click.argument("project")
@click.argument("env")
def cmd_list(delegator, project, env):
    """List all delegates for DELEGATOR on PROJECT/ENV."""
    delegates = delegation.list_delegates(delegator, project, env)
    if not delegates:
        click.echo(f"No delegates for '{delegator}' on {project}/{env}.")
        return
    for user, perms in delegates.items():
        click.echo(f"  {user}: {', '.join(perms)}")


@delegation_group.command("check")
@click.argument("delegator")
@click.argument("delegate")
@click.argument("project")
@click.argument("env")
@click.argument("permission")
def cmd_check(delegator, delegate, project, env, permission):
    """Check if DELEGATE can perform PERMISSION for DELEGATOR on PROJECT/ENV."""
    allowed = delegation.can_act(delegator, delegate, project, env, permission)
    if allowed:
        click.echo(f"'{delegate}' CAN perform '{permission}' for '{delegator}' on {project}/{env}.")
    else:
        click.echo(f"'{delegate}' CANNOT perform '{permission}' for '{delegator}' on {project}/{env}.")
