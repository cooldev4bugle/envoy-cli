"""Compliance checks: validate env files against a set of required keys and rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy import vault


@dataclass
class ComplianceResult:
    project: str
    env: str
    missing_required: List[str] = field(default_factory=list)
    disallowed_present: List[str] = field(default_factory=list)
    pattern_violations: Dict[str, str] = field(default_factory=dict)  # key -> reason

    @property
    def passed(self) -> bool:
        return (
            not self.missing_required
            and not self.disallowed_present
            and not self.pattern_violations
        )

    def as_dict(self) -> dict:
        return {
            "project": self.project,
            "env": self.env,
            "passed": self.passed,
            "missing_required": self.missing_required,
            "disallowed_present": self.disallowed_present,
            "pattern_violations": self.pattern_violations,
        }


def check(
    project: str,
    env: str,
    passphrase: str,
    required_keys: Optional[List[str]] = None,
    disallowed_keys: Optional[List[str]] = None,
    non_empty_keys: Optional[List[str]] = None,
) -> ComplianceResult:
    """Run compliance checks against a stored env."""
    data = vault.pull(project, env, passphrase)
    result = ComplianceResult(project=project, env=env)

    for key in required_keys or []:
        if key not in data:
            result.missing_required.append(key)

    for key in disallowed_keys or []:
        if key in data:
            result.disallowed_present.append(key)

    for key in non_empty_keys or []:
        if key in data and not data[key].strip():
            result.pattern_violations[key] = "must not be empty"

    return result


def check_all_envs(
    project: str,
    passphrase: str,
    envs: List[str],
    **kwargs,
) -> List[ComplianceResult]:
    """Run compliance checks across multiple envs for a project."""
    return [check(project, env, passphrase, **kwargs) for env in envs]
