"""CLI commands for template rendering."""

import click
from envoy import vault, env_file, template as tmpl


@click.group(name="template")
def template_group():
    """Render .env templates with variable substitution."""


@template_group.command("render")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--set", "overrides", multiple=True, metavar="KEY=VALUE",
              help="Override or supply template variables.")
@click.option("--out", default=None, help="Write result to file instead of stdout.")
def cmd_render(project, env, passphrase, overrides, out):
    """Render a stored env template, filling {{PLACEHOLDERS}}."""
    data = vault.pull(project, env, passphrase)
    override_dict = {}
    for item in overrides:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, v = item.split("=", 1)
        override_dict[k.strip()] = v.strip()
    try:
        rendered = tmpl.apply_template(data, override_dict)
    except KeyError as e:
        raise click.ClickException(str(e))

    content = env_file.serialize(rendered)
    if out:
        env_file.write(out, rendered)
        click.echo(f"Written to {out}")
    else:
        click.echo(content)


@template_group.command("placeholders")
@click.argument("project")
@click.argument("env")
@click.option("--passphrase", prompt=True, hide_input=True)
def cmd_placeholders(project, env, passphrase):
    """List all {{PLACEHOLDER}} variables found in a stored env."""
    data = vault.pull(project, env, passphrase)
    names = tmpl.find_placeholders(data)
    if not names:
        click.echo("No placeholders found.")
    else:
        for name in names:
            click.echo(name)
