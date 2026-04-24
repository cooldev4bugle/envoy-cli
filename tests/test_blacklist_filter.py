"""Tests for envoy.blacklist_filter."""

from __future__ import annotations

import pytest

from envoy import blacklist as bl
from envoy.blacklist_filter import assert_no_blacklisted, filter_env


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.blacklist._blacklist_path", lambda: tmp_path / "blacklists.json")
    yield tmp_path


def test_filter_env_removes_blacklisted_keys():
    bl.add_key("app", "prod", "SECRET")
    data = {"SECRET": "abc", "SAFE": "xyz"}
    filtered, removed = filter_env("app", "prod", data)
    assert "SECRET" not in filtered
    assert "SAFE" in filtered
    assert removed == ["SECRET"]


def test_filter_env_no_blacklist_returns_all():
    data = {"A": "1", "B": "2"}
    filtered, removed = filter_env("app", "dev", data)
    assert filtered == data
    assert removed == []


def test_filter_env_multiple_blacklisted():
    bl.add_key("app", "prod", "K1")
    bl.add_key("app", "prod", "K2")
    data = {"K1": "a", "K2": "b", "K3": "c"}
    filtered, removed = filter_env("app", "prod", data)
    assert set(removed) == {"K1", "K2"}
    assert list(filtered.keys()) == ["K3"]


def test_assert_no_blacklisted_raises_when_present():
    bl.add_key("app", "prod", "DANGER")
    with pytest.raises(ValueError, match="DANGER"):
        assert_no_blacklisted("app", "prod", {"DANGER": "oops", "OK": "fine"})


def test_assert_no_blacklisted_passes_when_clean():
    bl.add_key("app", "prod", "DANGER")
    # should not raise
    assert_no_blacklisted("app", "prod", {"SAFE": "value"})


def test_assert_no_blacklisted_empty_data():
    assert_no_blacklisted("app", "prod", {})
