"""Lock/unlock environments to prevent accidental overwrites."""

from envoy.storage import get_store_dir
from pathlib import Path
import json


def _lock_path() -> Path:
    return get_store_dir() / ".locks.json"


def _load_locks() -> dict:
    p = _lock_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_locks(locks: dict) -> None:
    _lock_path().write_text(json.dumps(locks, indent=2))


def lock_env(project: str, env: str) -> None:
    locks = _load_locks()
    locks.setdefault(project, []).append(env)
    locks[project] = list(set(locks[project]))
    _save_locks(locks)


def unlock_env(project: str, env: str) -> None:
    locks = _load_locks()
    if project in locks and env in locks[project]:
        locks[project].remove(env)
        if not locks[project]:
            del locks[project]
        _save_locks(locks)


def is_locked(project: str, env: str) -> bool:
    locks = _load_locks()
    return env in locks.get(project, [])


def list_locked(project: str) -> list[str]:
    locks = _load_locks()
    return sorted(locks.get(project, []))


def assert_unlocked(project: str, env: str) -> None:
    if is_locked(project, env):
        raise PermissionError(f"Environment '{env}' in project '{project}' is locked.")
