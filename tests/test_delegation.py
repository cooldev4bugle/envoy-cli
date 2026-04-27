"""Tests for envoy.delegation."""

import pytest

from envoy import delegation


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(delegation, "get_store_dir", lambda: tmp_path)


def test_grant_adds_delegate():
    delegation.grant_delegation("alice", "bob", "myapp", "production")
    delegates = delegation.list_delegates("alice", "myapp", "production")
    assert "bob" in delegates
    assert delegates["bob"] == ["read"]


def test_grant_custom_permissions():
    delegation.grant_delegation("alice", "bob", "myapp", "staging", ["read", "write"])
    perms = delegation.get_permissions("alice", "bob", "myapp", "staging")
    assert "read" in perms
    assert "write" in perms


def test_grant_idempotent_with_same_permissions():
    delegation.grant_delegation("alice", "bob", "myapp", "dev", ["read"])
    delegation.grant_delegation("alice", "bob", "myapp", "dev", ["read"])
    perms = delegation.get_permissions("alice", "bob", "myapp", "dev")
    assert perms.count("read") == 1


def test_revoke_removes_delegate():
    delegation.grant_delegation("alice", "bob", "myapp", "production")
    removed = delegation.revoke_delegation("alice", "bob", "myapp", "production")
    assert removed is True
    delegates = delegation.list_delegates("alice", "myapp", "production")
    assert "bob" not in delegates


def test_revoke_nonexistent_returns_false():
    result = delegation.revoke_delegation("alice", "ghost", "myapp", "production")
    assert result is False


def test_can_act_true_when_permitted():
    delegation.grant_delegation("alice", "bob", "myapp", "production", ["read", "push"])
    assert delegation.can_act("alice", "bob", "myapp", "production", "push") is True


def test_can_act_false_when_not_permitted():
    delegation.grant_delegation("alice", "bob", "myapp", "production", ["read"])
    assert delegation.can_act("alice", "bob", "myapp", "production", "delete") is False


def test_can_act_false_when_no_delegation():
    assert delegation.can_act("alice", "nobody", "myapp", "production", "read") is False


def test_list_delegates_empty_when_none():
    result = delegation.list_delegates("alice", "myapp", "production")
    assert result == {}


def test_multiple_delegates_for_same_scope():
    delegation.grant_delegation("alice", "bob", "myapp", "staging", ["read"])
    delegation.grant_delegation("alice", "carol", "myapp", "staging", ["read", "write"])
    delegates = delegation.list_delegates("alice", "myapp", "staging")
    assert "bob" in delegates
    assert "carol" in delegates
