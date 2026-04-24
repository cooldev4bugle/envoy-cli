"""Utility to strip blacklisted keys from env dicts before push/pull."""

from __future__ import annotations

from typing import Dict, List, Tuple

from envoy.blacklist import get_blacklist


def filter_env(
    project: str, env: str, data: Dict[str, str]
) -> Tuple[Dict[str, str], List[str]]:
    """Remove blacklisted keys from *data*.

    Returns:
        (filtered_dict, list_of_removed_keys)
    """
    blocked = get_blacklist(project, env)
    removed = [k for k in data if k in blocked]
    filtered = {k: v for k, v in data.items() if k not in blocked}
    return filtered, removed


def assert_no_blacklisted(
    project: str, env: str, data: Dict[str, str]
) -> None:
    """Raise ValueError if *data* contains any blacklisted key."""
    blocked = get_blacklist(project, env)
    hits = [k for k in data if k in blocked]
    if hits:
        raise ValueError(
            f"Refused: blacklisted key(s) present for {project}/{env}: "
            + ", ".join(hits)
        )
