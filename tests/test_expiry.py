"""Tests for envoy/expiry.py"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

import envoy.expiry as expiry_mod


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(expiry_mod, "get_store_dir", lambda: tmp_path)


_FUTURE = datetime.now(tz=timezone.utc) + timedelta(days=30)
_PAST = datetime.now(tz=timezone.utc) - timedelta(days=1)


def test_set_and_get_expiry():
    expiry_mod.set_expiry("myapp", "production", _FUTURE)
    result = expiry_mod.get_expiry("myapp", "production")
    assert result is not None
    assert result.tzinfo == timezone.utc
    assert abs((result - _FUTURE).total_seconds()) < 2


def test_get_expiry_returns_none_when_unset():
    result = expiry_mod.get_expiry("myapp", "staging")
    assert result is None


def test_set_expiry_requires_aware_datetime():
    naive = datetime(2030, 1, 1)
    with pytest.raises(ValueError, match="timezone-aware"):
        expiry_mod.set_expiry("myapp", "dev", naive)


def test_remove_expiry_returns_true_when_exists():
    expiry_mod.set_expiry("proj", "env", _FUTURE)
    assert expiry_mod.remove_expiry("proj", "env") is True
    assert expiry_mod.get_expiry("proj", "env") is None


def test_remove_expiry_returns_false_when_missing():
    assert expiry_mod.remove_expiry("proj", "ghost") is False


def test_is_expired_false_for_future():
    expiry_mod.set_expiry("proj", "env", _FUTURE)
    assert expiry_mod.is_expired("proj", "env") is False


def test_is_expired_true_for_past():
    expiry_mod.set_expiry("proj", "env", _PAST)
    assert expiry_mod.is_expired("proj", "env") is True


def test_is_expired_false_when_no_expiry_set():
    assert expiry_mod.is_expired("proj", "noexpiry") is False


def test_list_expiring_returns_correct_envs():
    expiry_mod.set_expiry("app", "prod", _FUTURE)
    expiry_mod.set_expiry("app", "dev", _PAST)
    expiry_mod.set_expiry("other", "staging", _FUTURE)

    results = expiry_mod.list_expiring("app")
    envs = {r["env"] for r in results}
    assert envs == {"prod", "dev"}


def test_list_expiring_marks_expired_correctly():
    expiry_mod.set_expiry("app", "prod", _FUTURE)
    expiry_mod.set_expiry("app", "dev", _PAST)

    results = {r["env"]: r for r in expiry_mod.list_expiring("app")}
    assert results["prod"]["expired"] is False
    assert results["dev"]["expired"] is True


def test_list_expiring_empty_for_unknown_project():
    assert expiry_mod.list_expiring("unknown") == []
