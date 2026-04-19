"""Tag environments with labels for easier organization and filtering."""

from envoy import storage

_TAG_KEY = "__tags__"


def _tag_path(project: str) -> dict:
    """Load raw store dict for a project."""
    try:
        return storage.load_all(project)
    except FileNotFoundError:
        return {}


def add_tag(project: str, env: str, tag: str) -> list[str]:
    """Add a tag to an environment. Returns updated tag list."""
    data = storage.load(project, env)
    tags = [t for t in data.get(_TAG_KEY, "").split(",") if t]
    if tag not in tags:
        tags.append(tag)
    data[_TAG_KEY] = ",".join(sorted(tags))
    storage.save(project, env, data)
    return sorted(tags)


def remove_tag(project: str, env: str, tag: str) -> list[str]:
    """Remove a tag from an environment. Returns updated tag list."""
    data = storage.load(project, env)
    tags = [t for t in data.get(_TAG_KEY, "").split(",") if t and t != tag]
    data[_TAG_KEY] = ",".join(sorted(tags))
    storage.save(project, env, data)
    return sorted(tags)


def get_tags(project: str, env: str) -> list[str]:
    """Return current tags for an environment."""
    data = storage.load(project, env)
    return [t for t in data.get(_TAG_KEY, "").split(",") if t]


def find_by_tag(project: str, tag: str) -> list[str]:
    """Return list of env names in a project that have the given tag."""
    envs = storage.list_environments(project)
    matches = []
    for env in envs:
        if tag in get_tags(project, env):
            matches.append(env)
    return matches
