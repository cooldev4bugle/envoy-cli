"""CLI commands for managing env schema validation rules."""

import click
from envoy.schema import set_rule, remove_rule, get_rules, validate
from envoy.vault import pull


@click.group(name="schema")
def schema_group():
    """Manage schema validation rules for a project."""


@schema_group.command("set")
@click.argument("project")
@click.argument("key")
@click.option("--required", is_flag=True, default=False, help="Mark key as required.")
@click.option("--pattern", default=None, help="Regex pattern the value must match.")
@click.option("--description", default="", help="Human-readable description of the rule.")
def cmd_set(project, key, required, pattern, description):
    """Add or update a validation rule for KEY in PROJECT."""
    set_rule(project, key, required=required, pattern=pattern, description=description)
    click.echo(f"Rule set for '{key}' in project '{project}'.")


@schema_group.command("remove")
@click.argument("project")
@click.argument("key")
def cmd_remove(project, key):
    """Remove a validation rule for KEY."""
    removed = remove_rule(project, key)
    if removed:
        click.echo(f"Rule for '{key}' removed.")
    else:
        click.echo(f"No rule found for '{key}'.")


@schema_group.command("list")
@click.argument("project")
def cmd_list(project):
    """List all validation rules for PROJECT."""
    rules = get_rules(project)
    if not rules:
        click.echo("No rules defined.")
        return
    for key, rule in rules.items():
        req = "required" if rule.get("required") else "optional"
        pattern = rule.get("pattern") or "*"
        desc = rule.get("description") or ""
        click.echo(f"  {key}  [{req}]  pattern={pattern}  {desc}")


@schema_group.command("validate")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True)
def cmd_validate(project, env, passphrase):
    """Validate ENV against the schema for PROJECT."""
    env_data = pull(project, env, passphrase)
    errors = validate(project, env_data)
    if not errors:
        click.echo("Validation passed. No issues found.")
    else:
        click.echo(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            click.echo(f"  - {err}")
        raise SystemExit(1)
