"""Export .env data to various formats (shell, docker, json)."""

import json
from typing import Dict


def to_shell(env: Dict[str, str]) -> str:
    """Export env vars as shell export statements."""
    lines = []
    for key, value in env.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def to_docker(env: Dict[str, str]) -> str:
    """Export env vars as docker --env flags."""
    lines = []
    for key, value in env.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'--env {key}="{escaped}"')
    return " \\\n  ".join(lines)


def to_json(env: Dict[str, str]) -> str:
    """Export env vars as a JSON object."""
    return json.dumps(env, indent=2)


def to_dotenv(env: Dict[str, str]) -> str:
    """Export env vars back to .env format."""
    lines = []
    for key, value in env.items():
        if any(c in value for c in [' ', '#', '"', "'", '=']):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f'{key}={value}')
    return "\n".join(lines)


FORMATS = {
    "shell": to_shell,
    "docker": to_docker,
    "json": to_json,
    "dotenv": to_dotenv,
}


def export(env: Dict[str, str], fmt: str) -> str:
    """Export env dict to the given format string."""
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {', '.join(FORMATS)}")
    return FORMATS[fmt](env)
