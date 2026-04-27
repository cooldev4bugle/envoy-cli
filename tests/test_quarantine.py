"""Tests for envoy.quarantine."""

from __future__ import annotations

import pytest

from envoy import quarantine


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.quarantine._quarantine_path", lambda: tmp_path / "quarantine.json")
    yield tmp_path


def test_is_quarantined_false_by_default():
    assert quarantine.is_quarantined("myapp", "production") is False


def test_quarantine_env_creates_entry():
    entry = quarantine.quarantine_env("myapp", "production", reason="suspicious keys")
    assert entry["project"] == "myapp"
    assert entry["env"] == "production"
    assert entry["reason"] == "suspicious keys"
    assert "quarantined_at" in entry


def test_quarantine_env_marks_as_quarantined():
    quarantine.quarantine_env("myapp", "staging")
    assert quarantine.is_quarantined("myapp", "staging") is True


def test_quarantine_env_empty_reason():
    entry = quarantine.quarantine_env("myapp", "dev")
    assert entry["reason"] == ""


def test_get_entry_returns_none_when_missing():
    assert quarantine.get_entry("myapp", "nonexistent") is None


def test_get_entry_returns_correct_entry():
    quarantine.quarantine_env("myapp", "production", reason="test")
    entry = quarantine.get_entry("myapp", "production")
    assert entry is not None
    assert entry["reason"] == "test"


def test_release_env_returns_true_when_quarantined():
    quarantine.quarantine_env("myapp", "production")
    result = quarantine.release_env("myapp", "production")
    assert result is True


def test_release_env_removes_quarantine():
    quarantine.quarantine_env("myapp", "production")
    quarantine.release_env("myapp", "production")
    assert quarantine.is_quarantined("myapp", "production") is False


def test_release_env_returns_false_when_not_quarantined():
    result = quarantine.release_env("myapp", "production")
    assert result is False


def test_list_quarantined_returns_all():
    quarantine.quarantine_env("myapp", "production")
    quarantine.quarantine_env("myapp", "staging")
    quarantine.quarantine_env("otherapp", "dev")
    entries = quarantine.list_quarantined()
    assert len(entries) == 3


def test_list_quarantined_filters_by_project():
    quarantine.quarantine_env("myapp", "production")
    quarantine.quarantine_env("myapp", "staging")
    quarantine.quarantine_env("otherapp", "dev")
    entries = quarantine.list_quarantined(project="myapp")
    assert len(entries) == 2
    assert all(e["project"] == "myapp" for e in entries)


def test_list_quarantined_empty():
    assert quarantine.list_quarantined() == []


def test_quarantine_overwrites_existing():
    quarantine.quarantine_env("myapp", "production", reason="first")
    quarantine.quarantine_env("myapp", "production", reason="second")
    entry = quarantine.get_entry("myapp", "production")
    assert entry["reason"] == "second"
    assert len(quarantine.list_quarantined()) == 1
