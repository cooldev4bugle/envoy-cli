"""CLI commands for compliance checking."""
import json
import click
from envoy import compliance, vault
from envoy.cli import get_passphrase


@click.group("compliance")
def compliance_group():
    """Validate env files against compliance rules."""


@compliance_group.command("check")
@click.argument("project")
@click.argument("env")
@click.option("--require", "-r", multiple=True, metavar="KEY", help="Required key(s).")
@click.option("--disallow", "-d", multiple=True, metavar="KEY", help="Disallowed key(s).")
@click.option("--non-empty", "-n", multiple=True, metavar="KEY", help="Keys that must not be empty.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def cmd_check(project, env, require, disallow, non_empty, as_json):
    """Check a single env for compliance."""
    passphrase = get_passphrase()
    try:
        result = compliance.check(
            project, env, passphrase,
            required_keys=list(require),
            disallowed_keys=list(disallow),
            non_empty_keys=list(non_empty),
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if as_json:
        click.echo(json.dumps(result.as_dict(), indent=2))
        return

    status = click.style("PASSED", fg="green") if result.passed else click.style("FAILED", fg="red")
    click.echo(f"[{status}] {project}/{env}")
    for key in result.missing_required:
        click.echo(f"  missing required key: {key}")
    for key in result.disallowed_present:
        click.echo(f"  disallowed key present: {key}")
    for key, reason in result.pattern_violations.items():
        click.echo(f"  violation on '{key}': {reason}")

    if not result.passed:
        raise SystemExit(1)


@compliance_group.command("check-all")
@click.argument("project")
@click.option("--require", "-r", multiple=True, metavar="KEY")
@click.option("--disallow", "-d", multiple=True, metavar="KEY")
@click.option("--non-empty", "-n", multiple=True, metavar="KEY")
@click.option("--json", "as_json", is_flag=True)
def cmd_check_all(project, require, disallow, non_empty, as_json):
    """Check all envs in a project for compliance."""
    passphrase = get_passphrase()
    try:
        envs = vault.list_envs(project)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    results = compliance.check_all_envs(
        project, passphrase, envs,
        required_keys=list(require),
        disallowed_keys=list(disallow),
        non_empty_keys=list(non_empty),
    )

    if as_json:
        click.echo(json.dumps([r.as_dict() for r in results], indent=2))
        return

    any_failed = False
    for result in results:
        status = click.style("PASSED", fg="green") if result.passed else click.style("FAILED", fg="red")
        click.echo(f"  [{status}] {result.env}")
        for key in result.missing_required:
            click.echo(f"    missing required key: {key}")
        for key in result.disallowed_present:
            click.echo(f"    disallowed key present: {key}")
        for key, reason in result.pattern_violations.items():
            click.echo(f"    violation on '{key}': {reason}")
        if not result.passed:
            any_failed = True

    if any_failed:
        raise SystemExit(1)
