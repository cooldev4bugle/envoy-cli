"""Tests for envoy.trust."""
import pytest

from envoy import trust as t


@pytest.fixture(autouse=True)
tmp_store(tmp_path, monkeypatch):
    pass


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "_trust_path", lambda: tmp_path / "trust.json")


def test_get_trust_returns_untrusted_by_default():
    info = t.get_trust("myapp", "production")
    assert info["level"] == "untrusted"
    assert info["note"] == ""


def test_set_and_get_trust():
    t.set_trust("myapp", "staging", "medium", note="reviewed")
    info = t.get_trust("myapp", "staging")
    assert info["level"] == "medium"
    assert info["note"] == "reviewed"


def test_set_trust_invalid_level_raises():
    with pytest.raises(ValueError, match="Invalid trust level"):
        t.set_trust("myapp", "dev", "super")


def test_set_trust_overwrites_existing():
    t.set_trust("myapp", "dev", "low")
    t.set_trust("myapp", "dev", "high", note="promoted")
    info = t.get_trust("myapp", "dev")
    assert info["level"] == "high"
    assert info["note"] == "promoted"


def test_remove_trust_returns_true_when_exists():
    t.set_trust("myapp", "qa", "low")
    assert t.remove_trust("myapp", "qa") is True
    assert t.get_trust("myapp", "qa")["level"] == "untrusted"


def test_remove_trust_returns_false_when_missing():
    assert t.remove_trust("myapp", "ghost") is False


def test_list_trusted_returns_sorted_entries():
    t.set_trust("proj", "prod", "high")
    t.set_trust("proj", "dev", "low")
    t.set_trust("other", "staging", "medium")  # different project, should be excluded
    entries = t.list_trusted("proj")
    assert len(entries) == 2
    assert entries[0]["env"] == "dev"
    assert entries[1]["env"] == "prod"


def test_list_trusted_empty():
    assert t.list_trusted("unknown") == []


def test_is_trusted_meets_minimum():
    t.set_trust("app", "env", "high")
    assert t.is_trusted("app", "env", min_level="medium") is True
    assert t.is_trusted("app", "env", min_level="high") is True
    assert t.is_trusted("app", "env", min_level="verified") is False


def test_is_trusted_default_untrusted_fails_medium():
    assert t.is_trusted("app", "missing", min_level="medium") is False


def test_is_trusted_invalid_min_level_raises():
    with pytest.raises(ValueError, match="Invalid trust level"):
        t.is_trusted("app", "env", min_level="bogus")
