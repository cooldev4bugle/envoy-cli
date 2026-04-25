"""CLI commands for env health scoring."""

import click

from envoy.scoring import score_env
from envoy.cli import get_passphrase


@click.group("score")
def scoring_group():
    """Health scoring for environments."""


@scoring_group.command("check")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", default=None, help="Encryption passphrase")
@click.option("--days-warning", default=7, show_default=True, help="Days before expiry to warn")
def cmd_check(project: str, env: str, passphrase: str | None, days_warning: int):
    """Score the health of an environment."""
    passphrase = passphrase or get_passphrase()
    report = score_env(project, env, passphrase, days_warning=days_warning)

    grade_color = {
        "A": "green",
        "B": "cyan",
        "C": "yellow",
        "D": "yellow",
        "F": "red",
    }.get(report.grade, "white")

    click.echo(f"Project : {report.project}")
    click.echo(f"Env     : {report.env}")
    click.echo(
        f"Score   : {report.score}/100  "
        + click.style(f"[{report.grade}]", fg=grade_color, bold=True)
    )

    if report.issues:
        click.echo("Issues:")
        for issue in report.issues:
            click.echo(f"  " + click.style("✗", fg="red") + f" {issue}")
    else:
        click.echo(click.style("  No issues found.", fg="green"))


@scoring_group.command("grade")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", default=None)
def cmd_grade(project: str, env: str, passphrase: str | None):
    """Print just the letter grade for an environment."""
    passphrase = passphrase or get_passphrase()
    report = score_env(project, env, passphrase)
    click.echo(report.grade)
