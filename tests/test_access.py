"""Tests for envoy/access.py."""

from __future__ import annotations

import pytest

from envoy import access as ac


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.access.get_store_dir", lambda: tmp_path)
    return tmp_path


def test_grant_adds_user():
    ac.grant("myapp", "production", "alice")
    assert ac.is_allowed("myapp", "production", "alice")


def test_is_allowed_false_by_default():
    assert not ac.is_allowed("myapp", "staging", "bob")


def test_grant_multiple_users():
    ac.grant("myapp", "staging", "alice")
    ac.grant("myapp", "staging", "bob")
    rules = ac.list_access("myapp", "staging")
    assert sorted(rules["staging"]) == ["alice", "bob"]


def test_grant_idempotent():
    ac.grant("myapp", "dev", "alice")
    ac.grant("myapp", "dev", "alice")
    rules = ac.list_access("myapp", "dev")
    assert rules["dev"].count("alice") == 1


def test_revoke_removes_user():
    ac.grant("myapp", "production", "alice")
    result = ac.revoke("myapp", "production", "alice")
    assert result is True
    assert not ac.is_allowed("myapp", "production", "alice")


def test_revoke_missing_user_returns_false():
    result = ac.revoke("myapp", "production", "ghost")
    assert result is False


def test_list_access_all_envs():
    ac.grant("myapp", "dev", "alice")
    ac.grant("myapp", "prod", "bob")
    rules = ac.list_access("myapp")
    assert "dev" in rules
    assert "prod" in rules


def test_list_access_filtered_env():
    ac.grant("myapp", "dev", "alice")
    ac.grant("myapp", "prod", "bob")
    rules = ac.list_access("myapp", env="dev")
    assert "dev" in rules
    assert "prod" not in rules


def test_clear_access_removes_env_rules():
    ac.grant("myapp", "staging", "alice")
    ac.clear_access("myapp", "staging")
    rules = ac.list_access("myapp", "staging")
    assert rules.get("staging", []) == []


def test_clear_access_nonexistent_env_is_safe():
    ac.clear_access("myapp", "nonexistent")  # should not raise
