"""Tests for envoy.reminder module."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

import envoy.reminder as rem


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(rem, "get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_set_reminder_creates_entry():
    due = rem.set_reminder("myapp", "production", 7)
    assert isinstance(due, datetime)
    entry = rem.get_reminder("myapp", "production")
    assert entry is not None
    assert entry["project"] == "myapp"
    assert entry["env"] == "production"
    assert entry["days"] == 7


def test_set_reminder_overwrites_existing():
    rem.set_reminder("myapp", "production", 30)
    rem.set_reminder("myapp", "production", 7)
    entry = rem.get_reminder("myapp", "production")
    assert entry["days"] == 7


def test_remove_reminder_returns_true_when_exists():
    rem.set_reminder("myapp", "staging", 14)
    result = rem.remove_reminder("myapp", "staging")
    assert result is True
    assert rem.get_reminder("myapp", "staging") is None


def test_remove_reminder_returns_false_when_missing():
    result = rem.remove_reminder("ghost", "nope")
    assert result is False


def test_list_all_returns_all_entries():
    rem.set_reminder("a", "dev", 10)
    rem.set_reminder("b", "prod", 20)
    entries = rem.list_all()
    assert len(entries) == 2


def test_list_all_filters_by_project():
    rem.set_reminder("a", "dev", 10)
    rem.set_reminder("b", "prod", 20)
    entries = rem.list_all(project="a")
    assert len(entries) == 1
    assert entries[0]["project"] == "a"


def test_list_due_returns_overdue_entries(tmp_store):
    rem.set_reminder("x", "env", 30)
    # Manually backdate the due date
    path = tmp_store / "reminders.json"
    data = json.loads(path.read_text())
    data["x/env"]["due"] = (datetime.utcnow() - timedelta(days=1)).isoformat()
    path.write_text(json.dumps(data))

    due = rem.list_due()
    assert len(due) == 1
    assert due[0]["env"] == "env"


def test_list_due_excludes_future_entries():
    rem.set_reminder("future", "env", 90)
    due = rem.list_due()
    assert all(e["project"] != "future" for e in due)
