"""Tests for envoy.deprecation."""

import json
import pytest
from unittest.mock import patch
from pathlib import Path

import envoy.deprecation as dep


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.deprecation._deprecation_path", lambda: tmp_path / "deprecations.json")
    return tmp_path


def test_is_deprecated_false_by_default(tmp_store):
    assert dep.is_deprecated("myapp", "prod", "OLD_KEY") is False


def test_mark_deprecated_creates_entry(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY", reason="no longer used")
    assert dep.is_deprecated("myapp", "prod", "OLD_KEY") is True


def test_mark_deprecated_stores_reason(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY", reason="replaced by NEW_KEY")
    info = dep.get_deprecation("myapp", "prod", "OLD_KEY")
    assert info is not None
    assert info["reason"] == "replaced by NEW_KEY"


def test_mark_deprecated_stores_replacement(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY", replacement="NEW_KEY")
    info = dep.get_deprecation("myapp", "prod", "OLD_KEY")
    assert info["replacement"] == "NEW_KEY"


def test_mark_deprecated_empty_reason(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY")
    info = dep.get_deprecation("myapp", "prod", "OLD_KEY")
    assert info["reason"] == ""
    assert info["replacement"] is None


def test_mark_deprecated_records_timestamp(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY")
    info = dep.get_deprecation("myapp", "prod", "OLD_KEY")
    assert "deprecated_at" in info
    assert "T" in info["deprecated_at"]  # ISO format


def test_unmark_deprecated_returns_true_when_exists(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY")
    result = dep.unmark_deprecated("myapp", "prod", "OLD_KEY")
    assert result is True
    assert dep.is_deprecated("myapp", "prod", "OLD_KEY") is False


def test_unmark_deprecated_returns_false_when_missing(tmp_store):
    result = dep.unmark_deprecated("myapp", "prod", "GHOST_KEY")
    assert result is False


def test_get_deprecation_returns_none_when_unset(tmp_store):
    assert dep.get_deprecation("myapp", "prod", "UNKNOWN") is None


def test_list_deprecated_returns_keys_for_env(tmp_store):
    dep.mark_deprecated("myapp", "prod", "KEY_A", reason="old")
    dep.mark_deprecated("myapp", "prod", "KEY_B", replacement="KEY_C")
    dep.mark_deprecated("myapp", "staging", "KEY_A")  # different env

    results = dep.list_deprecated("myapp", "prod")
    keys = [r["key"] for r in results]
    assert "KEY_A" in keys
    assert "KEY_B" in keys
    assert len(results) == 2


def test_list_deprecated_empty_when_none(tmp_store):
    assert dep.list_deprecated("myapp", "prod") == []


def test_mark_deprecated_overwrites_existing(tmp_store):
    dep.mark_deprecated("myapp", "prod", "OLD_KEY", reason="first")
    dep.mark_deprecated("myapp", "prod", "OLD_KEY", reason="updated")
    info = dep.get_deprecation("myapp", "prod", "OLD_KEY")
    assert info["reason"] == "updated"
