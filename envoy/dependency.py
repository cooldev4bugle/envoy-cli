"""Track key dependencies between envs — define which keys must exist before others."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envoy.storage import get_store_dir


def _dep_path() -> Path:
    return get_store_dir() / "dependencies.json"


def _load() -> Dict[str, Dict[str, List[str]]]:
    p = _dep_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, Dict[str, List[str]]]) -> None:
    _dep_path().write_text(json.dumps(data, indent=2))


def add_dependency(project: str, key: str, depends_on: List[str]) -> None:
    """Record that *key* in *project* depends on the given keys."""
    data = _load()
    project_deps = data.setdefault(project, {})
    existing = set(project_deps.get(key, []))
    existing.update(depends_on)
    project_deps[key] = sorted(existing)
    _save(data)


def remove_dependency(project: str, key: str, depends_on: str) -> bool:
    """Remove a single dependency edge. Returns True if it existed."""
    data = _load()
    deps = data.get(project, {}).get(key, [])
    if depends_on not in deps:
        return False
    deps.remove(depends_on)
    if not deps:
        del data[project][key]
        if not data[project]:
            del data[project]
    else:
        data[project][key] = deps
    _save(data)
    return True


def get_dependencies(project: str, key: str) -> List[str]:
    """Return the list of keys that *key* depends on."""
    return _load().get(project, {}).get(key, [])


def get_all(project: str) -> Dict[str, List[str]]:
    """Return the full dependency map for a project."""
    return _load().get(project, {})


def validate(project: str, env_keys: List[str]) -> Dict[str, List[str]]:
    """Check which dependencies are unmet given the current set of env keys.

    Returns a dict mapping each key to its list of *missing* dependencies.
    An empty dict means all dependencies are satisfied.
    """
    key_set = set(env_keys)
    violations: Dict[str, List[str]] = {}
    for key, deps in get_all(project).items():
        missing = [d for d in deps if d not in key_set]
        if missing:
            violations[key] = missing
    return violations
