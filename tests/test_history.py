"""Tests for envoy.history and cmd_history."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.history import record, get_history, clear_history
from envoy.cmd_history import history_group


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_record_and_get(tmp_store):
    record("myapp", "production", "push")
    entries = get_history("myapp")
    assert len(entries) == 1
    assert entries[0]["env"] == "production"
    assert entries[0]["action"] == "push"


def test_multiple_records(tmp_store):
    record("myapp", "staging", "push")
    record("myapp", "staging", "pull", note="sync")
    record("myapp", "production", "push")
    assert len(get_history("myapp")) == 3


def test_filter_by_env(tmp_store):
    record("myapp", "staging", "push")
    record("myapp", "production", "push")
    results = get_history("myapp", env="staging")
    assert len(results) == 1
    assert results[0]["env"] == "staging"


def test_filter_by_action(tmp_store):
    record("myapp", "staging", "push")
    record("myapp", "staging", "pull")
    results = get_history("myapp", action="pull")
    assert all(e["action"] == "pull" for e in results)


def test_limit(tmp_store):
    for i in range(10):
        record("myapp", f"env{i}", "push")
    assert len(get_history("myapp", limit=5)) == 5


def test_clear_history(tmp_store):
    record("myapp", "staging", "push")
    clear_history("myapp")
    assert get_history("myapp") == []


def test_no_history_empty(tmp_store):
    assert get_history("ghost") == []


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_log_no_events(runner, tmp_store):
    result = runner.invoke(history_group, ["log", "myapp"])
    assert result.exit_code == 0
    assert "No history" in result.output


def test_cmd_log_shows_entries(runner, tmp_store):
    record("myapp", "prod", "push", note="initial")
    result = runner.invoke(history_group, ["log", "myapp"])
    assert "push" in result.output
    assert "prod" in result.output
    assert "initial" in result.output


def test_cmd_clear_with_yes(runner, tmp_store):
    record("myapp", "prod", "push")
    result = runner.invoke(history_group, ["clear", "myapp", "--yes"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    assert get_history("myapp") == []
