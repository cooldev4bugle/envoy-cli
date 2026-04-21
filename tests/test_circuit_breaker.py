"""Tests for envoy.circuit_breaker."""

import time
import pytest
from unittest.mock import patch

from envoy import circuit_breaker as cb


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.circuit_breaker._cb_path", lambda: tmp_path / "circuit_breakers.json")


def test_initial_state_is_closed():
    entry = cb.get_state("myapp", "production")
    assert entry["state"] == cb.STATE_CLOSED
    assert entry["failures"] == 0


def test_record_failure_increments_count():
    cb.record_failure("myapp", "production", threshold=5)
    entry = cb.get_state("myapp", "production")
    assert entry["failures"] == 1
    assert entry["state"] == cb.STATE_CLOSED


def test_record_failure_opens_at_threshold():
    for _ in range(5):
        cb.record_failure("myapp", "production", threshold=5)
    entry = cb.get_state("myapp", "production")
    assert entry["state"] == cb.STATE_OPEN
    assert entry["opened_at"] is not None


def test_is_open_returns_true_when_open():
    for _ in range(5):
        cb.record_failure("myapp", "production", threshold=5)
    assert cb.is_open("myapp", "production", timeout=9999) is True


def test_is_open_returns_false_when_closed():
    assert cb.is_open("myapp", "staging") is False


def test_is_open_transitions_to_half_open_after_timeout():
    for _ in range(5):
        cb.record_failure("myapp", "production", threshold=5)
    # Patch opened_at to be in the past
    import json
    from envoy.circuit_breaker import _cb_path, _key
    data = json.loads(_cb_path().read_text())
    data[_key("myapp", "production")]["opened_at"] = time.time() - 9999
    _cb_path().write_text(json.dumps(data))
    assert cb.is_open("myapp", "production", timeout=60) is False
    entry = cb.get_state("myapp", "production")
    assert entry["state"] == cb.STATE_HALF_OPEN


def test_record_success_resets_state():
    for _ in range(5):
        cb.record_failure("myapp", "production", threshold=5)
    cb.record_success("myapp", "production")
    entry = cb.get_state("myapp", "production")
    assert entry["state"] == cb.STATE_CLOSED
    assert entry["failures"] == 0


def test_reset_removes_entry():
    cb.record_failure("myapp", "production")
    cb.reset("myapp", "production")
    entry = cb.get_state("myapp", "production")
    assert entry["state"] == cb.STATE_CLOSED
    assert entry["failures"] == 0


def test_multiple_projects_isolated():
    for _ in range(5):
        cb.record_failure("proj_a", "prod", threshold=5)
    assert cb.is_open("proj_a", "prod") is True
    assert cb.is_open("proj_b", "prod") is False
