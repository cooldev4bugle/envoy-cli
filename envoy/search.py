"""Search across stored env variables by key or value."""

from envoy import storage, crypto


def search_by_key(project: str, passphrase: str, pattern: str) -> dict[str, dict]:
    """Return all envs in a project where any key matches pattern."""
    results = {}
    envs = storage.list_environments(project)
    for env in envs:
        data = _load_env(project, env, passphrase)
        matched = {k: v for k, v in data.items() if pattern.lower() in k.lower()}
        if matched:
            results[env] = matched
    return results


def search_by_value(project: str, passphrase: str, pattern: str) -> dict[str, dict]:
    """Return all envs in a project where any value matches pattern."""
    results = {}
    envs = storage.list_environments(project)
    for env in envs:
        data = _load_env(project, env, passphrase)
        matched = {k: v for k, v in data.items() if pattern.lower() in v.lower()}
        if matched:
            results[env] = matched
    return results


def search_key_across_projects(passphrase: str, pattern: str) -> dict[str, dict]:
    """Search for a key pattern across all projects and envs."""
    results = {}
    projects = storage.list_projects()
    for project in projects:
        matches = search_by_key(project, passphrase, pattern)
        if matches:
            results[project] = matches
    return results


def _load_env(project: str, env: str, passphrase: str) -> dict:
    try:
        ciphertext = storage.load(project, env)
        from envoy.env_file import parse
        plaintext = crypto.decrypt(ciphertext, passphrase)
        return parse(plaintext)
    except Exception:
        return {}
