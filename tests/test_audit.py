"""Tests for envoy.audit module."""

import pytest
from unittest.mock import patch
from pathlib import Path

from envoy import audit


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.audit.get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_log_event_creates_file(tmp_store):
    audit.log_event("push", "myapp", "production")
    assert (tmp_store / "audit.log").exists()


def test_log_event_content():
    audit.log_event("pull", "myapp", "staging", user="alice", note="routine sync")
    events = audit.read_events()
    assert len(events) == 1
    e = events[0]
    assert e["action"] == "pull"
    assert e["project"] == "myapp"
    assert e["env"] == "staging"
    assert e["user"] == "alice"
    assert e["note"] == "routine sync"
    assert "timestamp" in e


def test_multiple_events_appended():
    audit.log_event("push", "proj", "dev")
    audit.log_event("remove", "proj", "dev")
    events = audit.read_events()
    assert len(events) == 2
    assert events[0]["action"] == "push"
    assert events[1]["action"] == "remove"


def test_filter_by_project():
    audit.log_event("push", "alpha", "dev")
    audit.log_event("push", "beta", "dev")
    events = audit.read_events(project="alpha")
    assert len(events) == 1
    assert events[0]["project"] == "alpha"


def test_filter_by_env():
    audit.log_event("push", "proj", "dev")
    audit.log_event("push", "proj", "prod")
    events = audit.read_events(env="prod")
    assert len(events) == 1
    assert events[0]["env"] == "prod"


def test_read_events_empty_when_no_log():
    events = audit.read_events()
    assert events == []


def test_limit_parameter():
    for i in range(10):
        audit.log_event("push", "proj", f"env{i}")
    events = audit.read_events(limit=3)
    assert len(events) == 3


def test_clear_log():
    audit.log_event("push", "proj", "dev")
    audit.clear_log()
    assert audit.read_events() == []
