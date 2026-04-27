"""Delegation: allow one user to act on behalf of another for specific projects/envs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.storage import get_store_dir


def _delegation_path() -> Path:
    return get_store_dir() / "delegations.json"


def _load() -> dict:
    p = _delegation_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _delegation_path().write_text(json.dumps(data, indent=2))


def _key(delegator: str, project: str, env: str) -> str:
    return f"{delegator}::{project}::{env}"


def grant_delegation(
    delegator: str,
    delegate: str,
    project: str,
    env: str,
    permissions: Optional[list[str]] = None,
) -> dict:
    """Allow *delegate* to act for *delegator* on project/env."""
    if permissions is None:
        permissions = ["read"]
    data = _load()
    k = _key(delegator, project, env)
    entry = data.get(k, {"delegates": {}})
    entry["delegates"][delegate] = sorted(set(permissions))
    data[k] = entry
    _save(data)
    return entry


def revoke_delegation(delegator: str, delegate: str, project: str, env: str) -> bool:
    data = _load()
    k = _key(delegator, project, env)
    if k not in data or delegate not in data[k].get("delegates", {}):
        return False
    del data[k]["delegates"][delegate]
    if not data[k]["delegates"]:
        del data[k]
    _save(data)
    return True


def get_permissions(delegator: str, delegate: str, project: str, env: str) -> list[str]:
    data = _load()
    k = _key(delegator, project, env)
    return data.get(k, {}).get("delegates", {}).get(delegate, [])


def can_act(delegator: str, delegate: str, project: str, env: str, permission: str) -> bool:
    return permission in get_permissions(delegator, delegate, project, env)


def list_delegates(delegator: str, project: str, env: str) -> dict[str, list[str]]:
    data = _load()
    k = _key(delegator, project, env)
    return dict(data.get(k, {}).get("delegates", {}))
