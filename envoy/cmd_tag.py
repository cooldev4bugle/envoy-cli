import click
from envoy import tag


@click.group(name="tag")
def tag_group():
    """Manage tags on environments."""
    pass


@tag_group.command("add")
@click.argument("project")
@click.argument("env")
@click.argument("tags", nargs=-1, required=True)
def cmd_add(project, env, tags):
    """Add one or more tags to an environment."""
    for t in tags:
        tag.add_tag(project, env, t)
    click.echo(f"Tagged '{env}' in '{project}' with: {', '.join(tags)}")


@tag_group.command("remove")
@click.argument("project")
@click.argument("env")
@click.argument("tag_name")
def cmd_remove(project, env, tag_name):
    """Remove a tag from an environment."""
    tag.remove_tag(project, env, tag_name)
    click.echo(f"Removed tag '{tag_name}' from '{env}' in '{project}'")


@tag_group.command("list")
@click.argument("project")
@click.argument("env")
def cmd_list(project, env):
    """List tags for an environment."""
    tags = tag.get_tags(project, env)
    if not tags:
        click.echo("No tags found.")
    else:
        for t in tags:
            click.echo(t)


@tag_group.command("find")
@click.argument("tag_name")
def cmd_find(tag_name):
    """Find all environments with a given tag."""
    results = tag.find_by_tag(tag_name)
    if not results:
        click.echo("No environments found with that tag.")
    else:
        for project, env in results:
            click.echo(f"{project}  {env}")
