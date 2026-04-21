"""Schema validation for .env files — enforce required keys, types, and patterns."""

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir


def _schema_path(project: str) -> Path:
    return get_store_dir() / project / "schema.json"


def _load_schema(project: str) -> dict:
    p = _schema_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schema(project: str, schema: dict) -> None:
    p = _schema_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(schema, indent=2))


def set_rule(project: str, key: str, *, required: bool = False, pattern: str | None = None, description: str = "") -> None:
    """Add or update a validation rule for a key."""
    schema = _load_schema(project)
    schema[key] = {
        "required": required,
        "pattern": pattern,
        "description": description,
    }
    _save_schema(project, schema)


def remove_rule(project: str, key: str) -> bool:
    schema = _load_schema(project)
    if key not in schema:
        return False
    del schema[key]
    _save_schema(project, schema)
    return True


def get_rules(project: str) -> dict:
    return _load_schema(project)


def validate(project: str, env_data: dict[str, Any]) -> list[str]:
    """Validate env_data against the project schema. Returns a list of error messages."""
    schema = _load_schema(project)
    errors: list[str] = []

    for key, rule in schema.items():
        if rule.get("required") and key not in env_data:
            errors.append(f"Missing required key: {key}")
            continue
        if key in env_data and rule.get("pattern"):
            value = env_data[key]
            if not re.fullmatch(rule["pattern"], value):
                errors.append(f"Key '{key}' value {value!r} does not match pattern '{rule['pattern']}'")

    return errors
