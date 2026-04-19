"""Profile management: named sets of env vars that can be applied/stacked."""
from __future__ import annotations
from typing import Optional
from envoy import storage, vault


def list_profiles(project: str, env: str) -> list[str]:
    """Return profile names stored for a given project/env."""
    try:
        data = storage.load(project, env)
    except FileNotFoundError:
        return []
    return list(data.get("__profiles__", {}).keys())


def save_profile(project: str, env: str, name: str, passphrase: str) -> None:
    """Snapshot current env vars into a named profile."""
    current = vault.pull(project, env, passphrase)
    data = storage.load(project, env)
    profiles = data.get("__profiles__", {})
    profiles[name] = current
    data["__profiles__"] = profiles
    storage.save(project, env, data)


def load_profile(project: str, env: str, name: str) -> dict[str, str]:
    """Return the vars stored in a named profile."""
    data = storage.load(project, env)
    profiles = data.get("__profiles__", {})
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found for {project}/{env}")
    return profiles[name]


def delete_profile(project: str, env: str, name: str) -> None:
    """Remove a named profile."""
    data = storage.load(project, env)
    profiles = data.get("__profiles__", {})
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found for {project}/{env}")
    del profiles[name]
    data["__profiles__"] = profiles
    storage.save(project, env, data)


def apply_profile(
    project: str, env: str, name: str, passphrase: str, merge: bool = False
) -> None:
    """Push profile vars into the active env, optionally merging."""
    profile_vars = load_profile(project, env, name)
    if merge:
        current = vault.pull(project, env, passphrase)
        current.update(profile_vars)
        profile_vars = current
    vault.push(project, env, profile_vars, passphrase)
