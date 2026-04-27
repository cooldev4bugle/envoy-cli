"""Key classification: assign sensitivity tiers to env keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir

LEVELS = ("public", "internal", "confidential", "secret")


def _classification_path() -> Path:
    return get_store_dir() / "classifications.json"


def _load() -> Dict[str, Dict[str, str]]:
    p = _classification_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, Dict[str, str]]) -> None:
    p = _classification_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def _key(project: str, env: str, key: str) -> str:
    return f"{project}::{env}::{key}"


def classify(project: str, env: str, key: str, level: str, note: str = "") -> None:
    """Assign a classification level to a key."""
    if level not in LEVELS:
        raise ValueError(f"Invalid level {level!r}. Choose from: {', '.join(LEVELS)}")
    data = _load()
    data[_key(project, env, key)] = {"level": level, "note": note}
    _save(data)


def get_classification(project: str, env: str, key: str) -> Optional[Dict[str, str]]:
    """Return classification entry or None if unset."""
    return _load().get(_key(project, env, key))


def remove_classification(project: str, env: str, key: str) -> bool:
    """Remove classification for a key. Returns True if it existed."""
    data = _load()
    k = _key(project, env, key)
    if k not in data:
        return False
    del data[k]
    _save(data)
    return True


def list_classified(project: str, env: str) -> List[Dict[str, str]]:
    """Return all classified keys for a given project/env."""
    prefix = f"{project}::{env}::"
    data = _load()
    results = []
    for k, v in data.items():
        if k.startswith(prefix):
            key_name = k[len(prefix):]
            results.append({"key": key_name, **v})
    return sorted(results, key=lambda x: x["key"])


def classify_env(project: str, env: str, pairs: Dict[str, str], level: str) -> None:
    """Bulk-classify all keys in pairs at the given level."""
    for key in pairs:
        classify(project, env, key, level)
