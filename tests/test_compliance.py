"""Tests for envoy.compliance."""
from unittest.mock import patch
import pytest
from envoy import compliance
from envoy.compliance import ComplianceResult


FAKE_DATA = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123", "EMPTY_KEY": ""}


def _patch_pull(data=None):
    return patch("envoy.compliance.vault.pull", return_value=data or FAKE_DATA)


def test_passed_when_no_rules():
    with _patch_pull():
        result = compliance.check("myapp", "prod", "pass")
    assert result.passed
    assert result.missing_required == []
    assert result.disallowed_present == []
    assert result.pattern_violations == {}


def test_missing_required_key():
    with _patch_pull():
        result = compliance.check("myapp", "prod", "pass", required_keys=["DB_HOST", "MISSING_KEY"])
    assert not result.passed
    assert "MISSING_KEY" in result.missing_required
    assert "DB_HOST" not in result.missing_required


def test_disallowed_key_present():
    with _patch_pull():
        result = compliance.check("myapp", "prod", "pass", disallowed_keys=["SECRET", "NOPE"])
    assert not result.passed
    assert "SECRET" in result.disallowed_present
    assert "NOPE" not in result.disallowed_present


def test_non_empty_violation():
    with _patch_pull():
        result = compliance.check("myapp", "prod", "pass", non_empty_keys=["EMPTY_KEY", "DB_HOST"])
    assert not result.passed
    assert "EMPTY_KEY" in result.pattern_violations
    assert "DB_HOST" not in result.pattern_violations


def test_all_rules_combined():
    with _patch_pull():
        result = compliance.check(
            "myapp", "prod", "pass",
            required_keys=["DB_HOST", "MISSING"],
            disallowed_keys=["SECRET"],
            non_empty_keys=["EMPTY_KEY"],
        )
    assert not result.passed
    assert "MISSING" in result.missing_required
    assert "SECRET" in result.disallowed_present
    assert "EMPTY_KEY" in result.pattern_violations


def test_as_dict_structure():
    with _patch_pull():
        result = compliance.check("myapp", "prod", "pass", required_keys=["MISSING"])
    d = result.as_dict()
    assert d["project"] == "myapp"
    assert d["env"] == "prod"
    assert d["passed"] is False
    assert "MISSING" in d["missing_required"]


def test_check_all_envs_returns_list():
    with _patch_pull():
        results = compliance.check_all_envs(
            "myapp", "pass", ["prod", "staging"],
            required_keys=["DB_HOST"],
        )
    assert len(results) == 2
    assert all(isinstance(r, ComplianceResult) for r in results)
    assert all(r.passed for r in results)


def test_check_all_envs_detects_failure():
    with _patch_pull():
        results = compliance.check_all_envs(
            "myapp", "pass", ["prod"],
            required_keys=["NONEXISTENT"],
        )
    assert len(results) == 1
    assert not results[0].passed
