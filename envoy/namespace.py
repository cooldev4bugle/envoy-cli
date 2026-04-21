"""Namespace support: group envs under logical namespaces per project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir


def _ns_path() -> Path:
    return get_store_dir() / "namespaces.json"


def _load() -> Dict[str, Dict[str, List[str]]]:
    p = _ns_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, Dict[str, List[str]]]) -> None:
    _ns_path().write_text(json.dumps(data, indent=2))


def assign(project: str, env: str, namespace: str) -> None:
    """Assign an env to a namespace within a project."""
    data = _load()
    project_ns = data.setdefault(project, {})
    envs = project_ns.setdefault(namespace, [])
    if env not in envs:
        envs.append(env)
    _save(data)


def unassign(project: str, env: str, namespace: str) -> bool:
    """Remove an env from a namespace. Returns True if it existed."""
    data = _load()
    try:
        envs = data[project][namespace]
    except KeyError:
        return False
    if env not in envs:
        return False
    envs.remove(env)
    if not envs:
        del data[project][namespace]
    if not data[project]:
        del data[project]
    _save(data)
    return True


def get_namespace(project: str, env: str) -> Optional[str]:
    """Return the namespace an env belongs to, or None."""
    data = _load()
    for ns, envs in data.get(project, {}).items():
        if env in envs:
            return ns
    return None


def list_namespaces(project: str) -> Dict[str, List[str]]:
    """Return all namespaces and their envs for a project."""
    return dict(_load().get(project, {}))


def envs_in_namespace(project: str, namespace: str) -> List[str]:
    """Return all envs assigned to a given namespace."""
    return list(_load().get(project, {}).get(namespace, []))
