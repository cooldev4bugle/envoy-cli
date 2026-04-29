"""Tests for envoy.ownership."""

import pytest

from envoy import ownership


@pytest.fixture(autouse=True)
tmp_store(tmp_path, monkeypatch):
    pass


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.ownership.get_store_dir", lambda: tmp_path)


def test_get_owner_returns_none_when_unset():
    assert ownership.get_owner("proj", "prod", "API_KEY") is None


def test_set_and_get_owner():
    ownership.set_owner("proj", "prod", "API_KEY", "alice")
    result = ownership.get_owner("proj", "prod", "API_KEY")
    assert result is not None
    assert result["owner"] == "alice"
    assert result["note"] == ""


def test_set_owner_with_note():
    ownership.set_owner("proj", "prod", "DB_PASS", "bob", note="rotated 2024")
    result = ownership.get_owner("proj", "prod", "DB_PASS")
    assert result["note"] == "rotated 2024"


def test_set_owner_overwrites_existing():
    ownership.set_owner("proj", "prod", "API_KEY", "alice")
    ownership.set_owner("proj", "prod", "API_KEY", "charlie")
    result = ownership.get_owner("proj", "prod", "API_KEY")
    assert result["owner"] == "charlie"


def test_remove_owner_returns_true_when_exists():
    ownership.set_owner("proj", "prod", "API_KEY", "alice")
    assert ownership.remove_owner("proj", "prod", "API_KEY") is True
    assert ownership.get_owner("proj", "prod", "API_KEY") is None


def test_remove_owner_returns_false_when_missing():
    assert ownership.remove_owner("proj", "prod", "GHOST") is False


def test_list_owned_by_returns_matching_entries():
    ownership.set_owner("proj", "prod", "API_KEY", "alice")
    ownership.set_owner("proj", "staging", "DB_PASS", "alice")
    ownership.set_owner("proj", "prod", "SECRET", "bob")
    results = ownership.list_owned_by("alice")
    keys = [(r["project"], r["env"], r["key"]) for r in results]
    assert ("proj", "prod", "API_KEY") in keys
    assert ("proj", "staging", "DB_PASS") in keys
    assert all(r["owner"] == "alice" for r in results)


def test_list_owned_by_returns_empty_when_none():
    assert ownership.list_owned_by("nobody") == []


def test_list_owners_for_env():
    ownership.set_owner("proj", "prod", "API_KEY", "alice")
    ownership.set_owner("proj", "prod", "DB_PASS", "bob")
    ownership.set_owner("proj", "staging", "API_KEY", "carol")
    results = ownership.list_owners_for_env("proj", "prod")
    assert len(results) == 2
    result_keys = {r["key"] for r in results}
    assert result_keys == {"API_KEY", "DB_PASS"}


def test_list_owners_for_env_empty():
    assert ownership.list_owners_for_env("proj", "empty") == []
