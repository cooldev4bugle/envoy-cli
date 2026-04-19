"""Import .env variables from external sources (shell environment, JSON, Docker)."""
import json
import os
from typing import Optional


def from_shell(keys: Optional[list] = None) -> dict:
    """Import variables from the current shell environment.
    If keys is provided, only import those keys."""
    env = dict(os.environ)
    if keys:
        return {k: env[k] for k in keys if k in env}
    return env


def from_json(path: str) -> dict:
    """Import variables from a JSON file (flat key-value object)."""
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON file must contain a top-level object")
    return {str(k): str(v) for k, v in data.items()}


def from_docker_env(path: str) -> dict:
    """Import variables from a Docker-style --env-file (KEY=VALUE lines)."""
    result = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


def merge_into(existing: dict, incoming: dict, overwrite: bool = False) -> dict:
    """Merge incoming variables into existing dict.
    If overwrite is False, existing keys are preserved."""
    result = dict(existing)
    for k, v in incoming.items():
        if overwrite or k not in result:
            result[k] = v
    return result
