"""Tests for envoy/ttl.py"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

import envoy.ttl as ttl_mod


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(ttl_mod, "get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_set_ttl_creates_entry():
    expiry = ttl_mod.set_ttl("myapp", "staging", 3600)
    assert isinstance(expiry, datetime)
    data = json.loads((tmp_store.__wrapped__ if hasattr(tmp_store, '__wrapped__') else ttl_mod._ttl_path()).read_text())
    assert "myapp::staging" in data


def test_set_ttl_creates_entry_direct(tmp_path):
    ttl_mod.set_ttl("myapp", "staging", 3600)
    data = json.loads(ttl_mod._ttl_path().read_text())
    assert "myapp::staging" in data


def test_set_ttl_raises_on_zero():
    with pytest.raises(ValueError, match="positive"):
        ttl_mod.set_ttl("myapp", "staging", 0)


def test_set_ttl_raises_on_negative():
    with pytest.raises(ValueError):
        ttl_mod.set_ttl("myapp", "staging", -10)


def test_get_ttl_returns_none_when_unset():
    result = ttl_mod.get_ttl("myapp", "prod")
    assert result is None


def test_get_ttl_returns_expiry():
    ttl_mod.set_ttl("myapp", "prod", 60)
    result = ttl_mod.get_ttl("myapp", "prod")
    assert isinstance(result, datetime)
    assert result > datetime.now(timezone.utc)


def test_remove_ttl_returns_true_when_exists():
    ttl_mod.set_ttl("myapp", "dev", 100)
    assert ttl_mod.remove_ttl("myapp", "dev") is True
    assert ttl_mod.get_ttl("myapp", "dev") is None


def test_remove_ttl_returns_false_when_missing():
    assert ttl_mod.remove_ttl("myapp", "ghost") is False


def test_is_expired_false_when_no_ttl():
    assert ttl_mod.is_expired("myapp", "staging") is False


def test_is_expired_false_when_future():
    ttl_mod.set_ttl("myapp", "staging", 9999)
    assert ttl_mod.is_expired("myapp", "staging") is False


def test_is_expired_true_when_past():
    past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    data = {"myapp::staging": past}
    ttl_mod._ttl_path().write_text(json.dumps(data))
    assert ttl_mod.is_expired("myapp", "staging") is True


def test_list_expiring_filters_by_project():
    ttl_mod.set_ttl("myapp", "staging", 500)
    ttl_mod.set_ttl("myapp", "prod", 1000)
    ttl_mod.set_ttl("other", "dev", 200)
    results = ttl_mod.list_expiring("myapp")
    envs = {r["env"] for r in results}
    assert envs == {"staging", "prod"}


def test_list_expiring_marks_expired():
    past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    ttl_mod._ttl_path().write_text(json.dumps({"myapp::old": past}))
    results = ttl_mod.list_expiring("myapp")
    assert results[0]["expired"] is True


def test_list_expiring_empty_when_none_set():
    assert ttl_mod.list_expiring("myapp") == []
