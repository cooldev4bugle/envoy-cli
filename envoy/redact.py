"""Redaction helpers — mask sensitive values before display or export."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# Keys whose values should always be redacted regardless of user config
_DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*password.*",
    r".*secret.*",
    r".*token.*",
    r".*api[_-]?key.*",
    r".*private[_-]?key.*",
    r".*auth.*",
    r".*credential.*",
]

REDACT_PLACEHOLDER = "***REDACTED***"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


_DEFAULT_COMPILED = _compile_patterns(_DEFAULT_SENSITIVE_PATTERNS)


def is_sensitive(key: str, extra_patterns: Optional[List[str]] = None) -> bool:
    """Return True if *key* matches any sensitive pattern."""
    patterns = _DEFAULT_COMPILED[:]
    if extra_patterns:
        patterns += _compile_patterns(extra_patterns)
    return any(p.fullmatch(key) for p in patterns)


def redact_value(key: str, value: str, extra_patterns: Optional[List[str]] = None) -> str:
    """Return REDACT_PLACEHOLDER if the key is sensitive, otherwise the original value."""
    if is_sensitive(key, extra_patterns):
        return REDACT_PLACEHOLDER
    return value


def redact_env(
    env: Dict[str, str],
    extra_patterns: Optional[List[str]] = None,
    reveal_keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by the placeholder.

    Keys listed in *reveal_keys* are never redacted even if they match a pattern.
    """
    reveal = set(reveal_keys or [])
    return {
        k: (v if k in reveal else redact_value(k, v, extra_patterns))
        for k, v in env.items()
    }


def visible_keys(env: Dict[str, str], extra_patterns: Optional[List[str]] = None) -> List[str]:
    """Return sorted list of keys whose values are NOT considered sensitive."""
    return sorted(k for k in env if not is_sensitive(k, extra_patterns))
