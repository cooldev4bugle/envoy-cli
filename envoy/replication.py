"""Replication: mirror an env from one project to another, keeping them in sync."""

from __future__ import annotations

from typing import Optional

from envoy import vault, storage


_REPLICATION_FILE = "replication.json"


def _rep_path() -> str:
    import os
    return os.path.join(storage.get_store_dir(), _REPLICATION_FILE)


def _load() -> dict:
    import json, os
    p = _rep_path()
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def _save(data: dict) -> None:
    import json
    with open(_rep_path(), "w") as f:
        json.dump(data, f, indent=2)


def _rule_key(src_project: str, src_env: str) -> str:
    return f"{src_project}::{src_env}"


def add_rule(src_project: str, src_env: str, dst_project: str, dst_env: str) -> None:
    """Register a replication rule: src -> dst."""
    data = _load()
    key = _rule_key(src_project, src_env)
    data[key] = {"dst_project": dst_project, "dst_env": dst_env}
    _save(data)


def remove_rule(src_project: str, src_env: str) -> bool:
    """Remove a replication rule. Returns True if it existed."""
    data = _load()
    key = _rule_key(src_project, src_env)
    if key not in data:
        return False
    del data[key]
    _save(data)
    return True


def list_rules() -> list[dict]:
    """Return all replication rules as a list of dicts."""
    data = _load()
    result = []
    for key, val in data.items():
        src_project, src_env = key.split("::", 1)
        result.append({
            "src_project": src_project,
            "src_env": src_env,
            "dst_project": val["dst_project"],
            "dst_env": val["dst_env"],
        })
    return result


def replicate(src_project: str, src_env: str, passphrase: str,
              dst_passphrase: Optional[str] = None) -> bool:
    """Execute replication for a specific source. Returns True if a rule existed."""
    data = _load()
    key = _rule_key(src_project, src_env)
    if key not in data:
        return False
    rule = data[key]
    env_data = vault.pull(src_project, src_env, passphrase)
    vault.push(rule["dst_project"], rule["dst_env"],
               env_data, dst_passphrase or passphrase)
    return True
