"""Cascade: propagate env key updates across multiple environments."""

from typing import Optional
from envoy import vault


def cascade_key(
    project: str,
    key: str,
    value: str,
    passphrase: str,
    source_env: str,
    target_envs: list[str],
    overwrite: bool = False,
) -> dict[str, str]:
    """Push a single key/value into each target environment.

    Returns a dict mapping env name -> 'updated' | 'skipped' | 'created'.
    """
    results: dict[str, str] = {}

    for env in target_envs:
        if env == source_env:
            results[env] = "skipped (source)"
            continue
        try:
            data = vault.pull(project, env, passphrase)
        except KeyError:
            data = {}

        if key in data and not overwrite:
            results[env] = "skipped"
            continue

        status = "updated" if key in data else "created"
        data[key] = value
        vault.push(project, env, data, passphrase)
        results[env] = status

    return results


def cascade_env(
    project: str,
    source_env: str,
    target_envs: list[str],
    passphrase: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> dict[str, dict[str, str]]:
    """Cascade all (or selected) keys from source_env into each target env.

    Returns a nested dict: {env: {key: status}}.
    """
    source_data = vault.pull(project, source_env, passphrase)
    if keys is not None:
        source_data = {k: v for k, v in source_data.items() if k in keys}

    results: dict[str, dict[str, str]] = {}
    for env in target_envs:
        env_results: dict[str, str] = {}
        for key, value in source_data.items():
            single = cascade_key(
                project, key, value, passphrase, source_env, [env], overwrite
            )
            env_results[key] = single.get(env, "skipped")
        results[env] = env_results
    return results
