"""Tests for envoy.alias."""

from __future__ import annotations

import pytest

from envoy import alias as alias_mod


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(alias_mod, "get_store_dir", lambda: tmp_path)
    return tmp_path


def test_set_and_resolve_alias():
    alias_mod.set_alias("prod", "myapp", "production")
    result = alias_mod.resolve_alias("prod")
    assert result == ("myapp", "production")


def test_resolve_missing_alias_returns_none():
    result = alias_mod.resolve_alias("nonexistent")
    assert result is None


def test_set_alias_overwrites_existing():
    alias_mod.set_alias("staging", "myapp", "staging")
    alias_mod.set_alias("staging", "otherapp", "prod")
    project, env = alias_mod.resolve_alias("staging")
    assert project == "otherapp"
    assert env == "prod"


def test_remove_alias_returns_true_when_exists():
    alias_mod.set_alias("dev", "myapp", "development")
    assert alias_mod.remove_alias("dev") is True
    assert alias_mod.resolve_alias("dev") is None


def test_remove_alias_returns_false_when_missing():
    assert alias_mod.remove_alias("ghost") is False


def test_list_aliases_empty():
    assert alias_mod.list_aliases() == []


def test_list_aliases_sorted():
    alias_mod.set_alias("z-alias", "proj", "env1")
    alias_mod.set_alias("a-alias", "proj", "env2")
    alias_mod.set_alias("m-alias", "proj", "env3")
    names = [entry["alias"] for entry in alias_mod.list_aliases()]
    assert names == ["a-alias", "m-alias", "z-alias"]


def test_list_aliases_contains_all_fields():
    alias_mod.set_alias("myalias", "coolproject", "production")
    entries = alias_mod.list_aliases()
    assert len(entries) == 1
    assert entries[0] == {"alias": "myalias", "project": "coolproject", "env": "production"}
