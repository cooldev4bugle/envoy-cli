"""Tests for envoy.scoring."""

from unittest.mock import patch, MagicMock

import pytest

from envoy.scoring import score_env, ScoreReport, _grade, SCORE_MAX


# ---------------------------------------------------------------------------
# _grade helper
# ---------------------------------------------------------------------------

def test_grade_a():
    assert _grade(95) == "A"
    assert _grade(90) == "A"


def test_grade_b():
    assert _grade(80) == "B"


def test_grade_c():
    assert _grade(65) == "C"


def test_grade_d():
    assert _grade(50) == "D"


def test_grade_f():
    assert _grade(30) == "F"
    assert _grade(0) == "F"


# ---------------------------------------------------------------------------
# score_env
# ---------------------------------------------------------------------------

def _patch_deps(is_locked=True, env_data=None, blacklisted=None, schema_rules=None):
    """Return a context-manager stack that patches all external calls."""
    env_data = env_data or {"KEY": "val"}
    blacklisted = blacklisted or []
    schema_rules = schema_rules or {}

    return [
        patch("envoy.scoring.lock.is_locked", return_value=is_locked),
        patch("envoy.scoring.pull", return_value=env_data),
        patch("envoy.scoring.blacklist.list_keys", return_value=blacklisted),
        patch("envoy.scoring.schema._load_schema", return_value=schema_rules),
    ]


def _run_score(is_locked=True, env_data=None, blacklisted=None, schema_rules=None):
    patches = _patch_deps(is_locked, env_data, blacklisted, schema_rules)
    ctx = [p.start() for p in patches]
    try:
        report = score_env("proj", "dev", "secret")
    finally:
        for p in patches:
            p.stop()
    return report


def test_perfect_score_when_no_issues():
    report = _run_score()
    assert report.score == SCORE_MAX
    assert report.grade == "A"
    assert report.issues == []


def test_unlocked_env_reduces_score():
    report = _run_score(is_locked=False)
    assert report.score < SCORE_MAX
    assert any("not locked" in i for i in report.issues)


def test_blacklisted_keys_reduce_score():
    report = _run_score(env_data={"SECRET": "x"}, blacklisted=["SECRET"])
    assert report.score < SCORE_MAX
    assert any("Blacklisted" in i for i in report.issues)


def test_missing_required_keys_reduce_score():
    rules = {"REQUIRED_KEY": {"required": True}}
    report = _run_score(env_data={"OTHER": "v"}, schema_rules=rules)
    assert report.score < SCORE_MAX
    assert any("Missing required" in i for i in report.issues)


def test_multiple_issues_accumulate_penalty():
    rules = {"MUST": {"required": True}}
    report = _run_score(
        is_locked=False,
        env_data={"BAD": "v"},
        blacklisted=["BAD"],
        schema_rules=rules,
    )
    assert report.score < 40
    assert len(report.issues) >= 3


def test_score_never_goes_below_zero():
    rules = {"K1": {"required": True}, "K2": {"required": True}}
    report = _run_score(
        is_locked=False,
        env_data={"BAD": "v"},
        blacklisted=["BAD"],
        schema_rules=rules,
    )
    assert report.score >= 0


def test_report_as_dict_has_expected_keys():
    report = _run_score()
    d = report.as_dict()
    assert set(d.keys()) == {"project", "env", "score", "grade", "issues"}
