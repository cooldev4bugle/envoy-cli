import click
from envoy import vault, export as exp


@click.group(name="export")
def export_group():
    """Export environment variables in various formats."""
    pass


@export_group.command(name="shell")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase")
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout")
def cmd_shell(project, env, passphrase, output):
    """Export as shell export statements."""
    data = vault.pull(project, env, passphrase)
    result = exp.to_shell(data)
    if output:
        with open(output, "w") as f:
            f.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


@export_group.command(name="docker")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase")
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout")
def cmd_docker(project, env, passphrase, output):
    """Export as Docker --env-file format."""
    data = vault.pull(project, env, passphrase)
    result = exp.to_docker(data)
    if output:
        with open(output, "w") as f:
            f.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


@export_group.command(name="json")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase")
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout")
def cmd_json(project, env, passphrase, output):
    """Export as JSON."""
    data = vault.pull(project, env, passphrase)
    result = exp.to_json(data)
    if output:
        with open(output, "w") as f:
            f.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


@export_group.command(name="dotenv")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase")
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout")
def cmd_dotenv(project, env, passphrase, output):
    """Export as .env file format."""
    data = vault.pull(project, env, passphrase)
    result = exp.to_dotenv(data)
    if output:
        with open(output, "w") as f:
            f.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)
