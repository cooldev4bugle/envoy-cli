"""Read, write, and parse .env files."""

from pathlib import Path
from typing import Dict


def parse(content: str) -> Dict[str, str]:
    """Parse .env file content into a key-value dict."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def serialize(env_vars: Dict[str, str]) -> str:
    """Serialize a key-value dict back into .env file content."""
    lines = []
    for key, value in sorted(env_vars.items()):
        if any(c in value for c in (" ", "#", "'", '"')):
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def read(path: str | Path) -> Dict[str, str]:
    """Read and parse a .env file from disk."""
    content = Path(path).read_text(encoding="utf-8")
    return parse(content)


def write(path: str | Path, env_vars: Dict[str, str]) -> None:
    """Serialize and write env vars to a .env file on disk."""
    Path(path).write_text(serialize(env_vars), encoding="utf-8")
