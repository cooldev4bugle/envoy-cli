"""Tests for envoy.sensitivity."""

import pytest

from envoy import sensitivity as S


@pytest.fixture(autouse=True)
tmp_store(tmp_path, monkeypatch):
    pass


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr(S, "get_store_dir", lambda: tmp_path)


def test_get_sensitivity_returns_none_when_unset(tmp_store):
    assert S.get_sensitivity("proj", "dev", "API_KEY") is None


def test_set_and_get_sensitivity(tmp_store):
    S.set_sensitivity("proj", "dev", "API_KEY", "secret")
    assert S.get_sensitivity("proj", "dev", "API_KEY") == "secret"


def test_set_sensitivity_invalid_level_raises(tmp_store):
    with pytest.raises(ValueError, match="Invalid level"):
        S.set_sensitivity("proj", "dev", "API_KEY", "ultra-secret")


def test_set_sensitivity_overwrites_existing(tmp_store):
    S.set_sensitivity("proj", "dev", "DB_PASS", "internal")
    S.set_sensitivity("proj", "dev", "DB_PASS", "confidential")
    assert S.get_sensitivity("proj", "dev", "DB_PASS") == "confidential"


def test_remove_sensitivity_returns_true_when_exists(tmp_store):
    S.set_sensitivity("proj", "dev", "TOKEN", "secret")
    assert S.remove_sensitivity("proj", "dev", "TOKEN") is True
    assert S.get_sensitivity("proj", "dev", "TOKEN") is None


def test_remove_sensitivity_returns_false_when_missing(tmp_store):
    assert S.remove_sensitivity("proj", "dev", "GHOST") is False


def test_list_sensitive_keys_empty(tmp_store):
    assert S.list_sensitive_keys("proj", "dev") == {}


def test_list_sensitive_keys_returns_all_for_env(tmp_store):
    S.set_sensitivity("proj", "dev", "API_KEY", "secret")
    S.set_sensitivity("proj", "dev", "LOG_LEVEL", "public")
    S.set_sensitivity("proj", "prod", "API_KEY", "confidential")
    result = S.list_sensitive_keys("proj", "dev")
    assert result == {"API_KEY": "secret", "LOG_LEVEL": "public"}


def test_filter_by_level_returns_at_or_above_threshold(tmp_store):
    S.set_sensitivity("proj", "dev", "A", "public")
    S.set_sensitivity("proj", "dev", "B", "internal")
    S.set_sensitivity("proj", "dev", "C", "confidential")
    S.set_sensitivity("proj", "dev", "D", "secret")
    result = S.filter_by_level("proj", "dev", "confidential")
    assert result == {"C": "confidential", "D": "secret"}


def test_filter_by_level_invalid_raises(tmp_store):
    with pytest.raises(ValueError, match="Invalid level"):
        S.filter_by_level("proj", "dev", "unknown")


def test_all_valid_levels_accepted(tmp_store):
    for level in S.VALID_LEVELS:
        S.set_sensitivity("proj", "dev", f"KEY_{level}", level)
        assert S.get_sensitivity("proj", "dev", f"KEY_{level}") == level
