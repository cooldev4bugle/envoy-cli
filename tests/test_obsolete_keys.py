"""Tests for envoy.ObsoleteKeys."""

import pytest

import envoy.ObsoleteKeys as obs
from envoy.storage import get_store_dir


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage._store_dir", tmp_path)
    monkeypatch.setattr("envoy.ObsoleteKeys._obsolete_path", lambda: tmp_path / "obsolete_keys.json")
    yield tmp_path


def test_is_obsolete_false_by_default():
    assert obs.is_obsolete("myapp", "prod", "OLD_KEY") is False


def test_mark_obsolete_creates_entry():
    obs.mark_obsolete("myapp", "prod", "OLD_KEY", reason="no longer used")
    assert obs.is_obsolete("myapp", "prod", "OLD_KEY") is True


def test_mark_obsolete_stores_reason():
    obs.mark_obsolete("myapp", "prod", "LEGACY_URL", reason="replaced by API_URL")
    entries = obs.get_obsolete_keys("myapp", env="prod")
    assert any(e["key"] == "LEGACY_URL" and e["reason"] == "replaced by API_URL" for e in entries)


def test_mark_obsolete_empty_reason():
    obs.mark_obsolete("myapp", "prod", "OLD_KEY")
    entries = obs.get_obsolete_keys("myapp", env="prod")
    assert entries[0]["reason"] == ""


def test_unmark_obsolete_removes_entry():
    obs.mark_obsolete("myapp", "prod", "OLD_KEY")
    result = obs.unmark_obsolete("myapp", "prod", "OLD_KEY")
    assert result is True
    assert obs.is_obsolete("myapp", "prod", "OLD_KEY") is False


def test_unmark_obsolete_returns_false_when_missing():
    result = obs.unmark_obsolete("myapp", "prod", "NONEXISTENT")
    assert result is False


def test_get_obsolete_keys_filters_by_env():
    obs.mark_obsolete("myapp", "prod", "KEY_A")
    obs.mark_obsolete("myapp", "staging", "KEY_B")
    prod_keys = obs.get_obsolete_keys("myapp", env="prod")
    assert len(prod_keys) == 1
    assert prod_keys[0]["key"] == "KEY_A"


def test_get_obsolete_keys_all_envs():
    obs.mark_obsolete("myapp", "prod", "KEY_A")
    obs.mark_obsolete("myapp", "staging", "KEY_B")
    all_keys = obs.get_obsolete_keys("myapp")
    assert len(all_keys) == 2


def test_get_obsolete_keys_scoped_to_project():
    obs.mark_obsolete("myapp", "prod", "KEY_A")
    obs.mark_obsolete("otherapp", "prod", "KEY_B")
    keys = obs.get_obsolete_keys("myapp")
    assert all(e["project"] == "myapp" for e in keys)


def test_clear_obsolete_removes_all_for_env():
    obs.mark_obsolete("myapp", "prod", "KEY_A")
    obs.mark_obsolete("myapp", "prod", "KEY_B")
    obs.mark_obsolete("myapp", "staging", "KEY_C")
    removed = obs.clear_obsolete("myapp", "prod")
    assert removed == 2
    assert obs.get_obsolete_keys("myapp", env="prod") == []
    assert len(obs.get_obsolete_keys("myapp", env="staging")) == 1
