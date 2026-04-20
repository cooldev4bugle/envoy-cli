"""Access control: restrict which users/roles can read or write specific envs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from envoy.storage import get_store_dir


def _access_path(project: str) -> Path:
    return get_store_dir() / project / "access.json"


def _load_rules(project: str) -> dict:
    path = _access_path(project)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_rules(project: str, rules: dict) -> None:
    path = _access_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rules, indent=2))


def grant(project: str, env: str, user: str) -> None:
    """Grant a user access to an environment."""
    rules = _load_rules(project)
    allowed = set(rules.get(env, []))
    allowed.add(user)
    rules[env] = sorted(allowed)
    _save_rules(project, rules)


def revoke(project: str, env: str, user: str) -> bool:
    """Revoke a user's access. Returns True if user was present."""
    rules = _load_rules(project)
    allowed = set(rules.get(env, []))
    if user not in allowed:
        return False
    allowed.discard(user)
    rules[env] = sorted(allowed)
    _save_rules(project, rules)
    return True


def is_allowed(project: str, env: str, user: str) -> bool:
    """Return True if user has access to the environment."""
    rules = _load_rules(project)
    allowed = rules.get(env, [])
    return user in allowed


def list_access(project: str, env: Optional[str] = None) -> dict:
    """Return access rules, optionally filtered to a single env."""
    rules = _load_rules(project)
    if env is not None:
        return {env: rules.get(env, [])}
    return rules


def clear_access(project: str, env: str) -> None:
    """Remove all access rules for an environment."""
    rules = _load_rules(project)
    rules.pop(env, None)
    _save_rules(project, rules)
