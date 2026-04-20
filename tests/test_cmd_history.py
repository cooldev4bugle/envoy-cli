import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_history import history_group


@pytest.fixture
def runner():
    return CliRunner()


def _make_entry(action="push", env="production", user="alice", ts="2024-01-01T10:00:00"):
    return {"action": action, "env": env, "user": user, "timestamp": ts}


def test_cmd_log_no_events(runner):
    with patch("envoy.cmd_history.history.get_history", return_value=[]):
        result = runner.invoke(history_group, ["log", "myproject"])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_cmd_log_shows_events(runner):
    events = [_make_entry(action="push", env="staging", user="bob")]
    with patch("envoy.cmd_history.history.get_history", return_value=events):
        result = runner.invoke(history_group, ["log", "myproject"])
    assert result.exit_code == 0
    assert "PUSH" in result.output
    assert "staging" in result.output
    assert "bob" in result.output


def test_cmd_log_passes_filters(runner):
    with patch("envoy.cmd_history.history.get_history", return_value=[]) as mock_get:
        runner.invoke(history_group, ["log", "proj", "--env", "dev", "--action", "pull"])
        mock_get.assert_called_once_with("proj", env="dev", action="pull")


def test_cmd_log_respects_limit(runner):
    events = [_make_entry(ts=f"2024-01-0{i}T00:00:00") for i in range(1, 6)]
    with patch("envoy.cmd_history.history.get_history", return_value=events):
        result = runner.invoke(history_group, ["log", "proj", "--limit", "3"])
    assert result.exit_code == 0
    # only last 3 of 5 entries shown
    lines = [l for l in result.output.strip().splitlines() if l.startswith("[")]
    assert len(lines) == 3


def test_cmd_clear_confirmed(runner):
    with patch("envoy.cmd_history.history.clear_history") as mock_clear:
        result = runner.invoke(history_group, ["clear", "myproject", "--yes"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    mock_clear.assert_called_once_with("myproject")


def test_cmd_clear_aborts_without_confirmation(runner):
    with patch("envoy.cmd_history.history.clear_history") as mock_clear:
        result = runner.invoke(history_group, ["clear", "myproject"], input="n\n")
    assert result.exit_code != 0
    mock_clear.assert_not_called()
