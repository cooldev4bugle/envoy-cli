"""Tests for envoy.freeze."""

import pytest

from envoy import freeze as freeze_mod


@pytest.fixture(autouse=True)
tmp_store(tmp_path, monkeypatch):
    pass


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(freeze_mod, "get_store_dir", lambda: tmp_path)


def test_is_frozen_false_by_default():
    assert freeze_mod.is_frozen("myapp", "production") is False


def test_freeze_env_creates_entry():
    record = freeze_mod.freeze_env("myapp", "production", reason="release window")
    assert record["project"] == "myapp"
    assert record["env"] == "production"
    assert record["reason"] == "release window"
    assert "frozen_at" in record


def test_freeze_env_marks_as_frozen():
    freeze_mod.freeze_env("myapp", "staging")
    assert freeze_mod.is_frozen("myapp", "staging") is True


def test_freeze_env_empty_reason():
    freeze_mod.freeze_env("myapp", "dev")
    info = freeze_mod.get_freeze_info("myapp", "dev")
    assert info["reason"] == ""


def test_unfreeze_env_removes_entry():
    freeze_mod.freeze_env("myapp", "production")
    result = freeze_mod.unfreeze_env("myapp", "production")
    assert result is True
    assert freeze_mod.is_frozen("myapp", "production") is False


def test_unfreeze_nonexistent_returns_false():
    result = freeze_mod.unfreeze_env("myapp", "ghost")
    assert result is False


def test_get_freeze_info_returns_none_when_not_frozen():
    assert freeze_mod.get_freeze_info("myapp", "dev") is None


def test_get_freeze_info_returns_record():
    freeze_mod.freeze_env("myapp", "production", reason="hotfix")
    info = freeze_mod.get_freeze_info("myapp", "production")
    assert info is not None
    assert info["reason"] == "hotfix"


def test_list_frozen_returns_all():
    freeze_mod.freeze_env("alpha", "prod")
    freeze_mod.freeze_env("beta", "prod")
    results = freeze_mod.list_frozen()
    assert len(results) == 2


def test_list_frozen_filters_by_project():
    freeze_mod.freeze_env("alpha", "prod")
    freeze_mod.freeze_env("alpha", "staging")
    freeze_mod.freeze_env("beta", "prod")
    results = freeze_mod.list_frozen(project="alpha")
    assert len(results) == 2
    assert all(r["project"] == "alpha" for r in results)


def test_freeze_overwrites_existing():
    freeze_mod.freeze_env("myapp", "prod", reason="first")
    freeze_mod.freeze_env("myapp", "prod", reason="second")
    info = freeze_mod.get_freeze_info("myapp", "prod")
    assert info["reason"] == "second"
    assert len(freeze_mod.list_frozen()) == 1
