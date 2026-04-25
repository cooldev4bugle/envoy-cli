"""Env health scoring — rates an environment based on various risk signals."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envoy import lock, ttl, expiry, blacklist, pin, schema
from envoy.vault import pull


SCORE_MAX = 100

_PENALTIES = {
    "has_blacklisted_keys": 30,
    "has_expired_keys": 20,
    "has_expiring_soon_keys": 10,
    "is_unlocked": 15,
    "missing_required_keys": 25,
}


@dataclass
class ScoreReport:
    project: str
    env: str
    score: int
    grade: str
    issues: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "project": self.project,
            "env": self.env,
            "score": self.score,
            "grade": self.grade,
            "issues": self.issues,
        }


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score_env(
    project: str,
    env: str,
    passphrase: str,
    days_warning: int = 7,
) -> ScoreReport:
    """Compute a health score for a single environment."""
    import datetime

    issues: list[str] = []
    penalty = 0

    # locked?
    if not lock.is_locked(project, env):
        issues.append("Environment is not locked")
        penalty += _PENALTIES["is_unlocked"]

    # blacklisted keys present?
    try:
        env_data = pull(project, env, passphrase)
        bl = blacklist.list_keys(project)
        bad = [k for k in env_data if k in bl]
        if bad:
            issues.append(f"Blacklisted keys present: {', '.join(bad)}")
            penalty += _PENALTIES["has_blacklisted_keys"]
    except Exception:
        env_data = {}

    # schema — missing required keys?
    try:
        rules = schema._load_schema(project)
        required = [k for k, r in rules.items() if r.get("required")]
        missing = [k for k in required if k not in env_data]
        if missing:
            issues.append(f"Missing required keys: {', '.join(missing)}")
            penalty += _PENALTIES["missing_required_keys"]
    except Exception:
        pass

    score = max(0, SCORE_MAX - penalty)
    return ScoreReport(
        project=project,
        env=env,
        score=score,
        grade=_grade(score),
        issues=issues,
    )
