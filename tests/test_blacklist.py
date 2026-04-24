"""Tests for envoy.blacklist."""

from __future__ import annotations

import pytest

from envoy import blacklist as bl


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.blacklist._blacklist_path", lambda: tmp_path / "blacklists.json")
    yield tmp_path


def test_add_key_creates_entry():
    result = bl.add_key("myapp", "prod", "SECRET_KEY")
    assert "SECRET_KEY" in result


def test_add_key_no_duplicates():
    bl.add_key("myapp", "prod", "SECRET_KEY")
    result = bl.add_key("myapp", "prod", "SECRET_KEY")
    assert result.count("SECRET_KEY") == 1


def test_add_multiple_keys():
    bl.add_key("myapp", "prod", "KEY_A")
    bl.add_key("myapp", "prod", "KEY_B")
    keys = bl.get_blacklist("myapp", "prod")
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_remove_key_returns_true_when_exists():
    bl.add_key("myapp", "prod", "SECRET")
    assert bl.remove_key("myapp", "prod", "SECRET") is True
    assert "SECRET" not in bl.get_blacklist("myapp", "prod")


def test_remove_key_returns_false_when_missing():
    assert bl.remove_key("myapp", "prod", "GHOST") is False


def test_get_blacklist_empty_by_default():
    assert bl.get_blacklist("myapp", "staging") == []


def test_is_blacklisted_true():
    bl.add_key("myapp", "prod", "DB_PASS")
    assert bl.is_blacklisted("myapp", "prod", "DB_PASS") is True


def test_is_blacklisted_false():
    assert bl.is_blacklisted("myapp", "prod", "SAFE_KEY") is False


def test_clear_blacklist():
    bl.add_key("myapp", "prod", "KEY_A")
    bl.add_key("myapp", "prod", "KEY_B")
    bl.clear_blacklist("myapp", "prod")
    assert bl.get_blacklist("myapp", "prod") == []


def test_different_envs_are_isolated():
    bl.add_key("myapp", "prod", "ONLY_PROD")
    assert not bl.is_blacklisted("myapp", "staging", "ONLY_PROD")
