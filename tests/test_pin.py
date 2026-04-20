"""Tests for envoy.pin."""

from __future__ import annotations

import pytest

from envoy import pin as pin_module


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(pin_module, "get_store_dir", lambda: tmp_path)


def test_pin_key_adds_entry():
    pin_module.pin_key("myapp", "prod", "DB_PASSWORD")
    assert "DB_PASSWORD" in pin_module.get_pinned("myapp", "prod")


def test_pin_key_no_duplicates():
    pin_module.pin_key("myapp", "prod", "SECRET")
    pin_module.pin_key("myapp", "prod", "SECRET")
    assert pin_module.get_pinned("myapp", "prod").count("SECRET") == 1


def test_unpin_key_removes_entry():
    pin_module.pin_key("myapp", "prod", "API_KEY")
    pin_module.unpin_key("myapp", "prod", "API_KEY")
    assert "API_KEY" not in pin_module.get_pinned("myapp", "prod")


def test_unpin_nonexistent_does_nothing():
    # should not raise
    pin_module.unpin_key("myapp", "prod", "GHOST_KEY")


def test_is_pinned_true():
    pin_module.pin_key("myapp", "staging", "TOKEN")
    assert pin_module.is_pinned("myapp", "staging", "TOKEN") is True


def test_is_pinned_false_by_default():
    assert pin_module.is_pinned("myapp", "staging", "MISSING") is False


def test_apply_pins_keeps_pinned_values():
    pin_module.pin_key("myapp", "prod", "DB_PASS")
    current = {"DB_PASS": "secret123", "HOST": "old-host"}
    incoming = {"DB_PASS": "new-pass", "HOST": "new-host"}
    result = pin_module.apply_pins("myapp", "prod", incoming, current)
    assert result["DB_PASS"] == "secret123"
    assert result["HOST"] == "new-host"


def test_apply_pins_no_pins_returns_incoming():
    current = {"A": "old"}
    incoming = {"A": "new", "B": "added"}
    result = pin_module.apply_pins("myapp", "dev", incoming, current)
    assert result == incoming


def test_apply_pins_pinned_key_missing_from_current():
    pin_module.pin_key("myapp", "prod", "ORPHAN")
    current = {}
    incoming = {"ORPHAN": "from-remote"}
    result = pin_module.apply_pins("myapp", "prod", incoming, current)
    # pinned but not in current — incoming value survives
    assert result["ORPHAN"] == "from-remote"
