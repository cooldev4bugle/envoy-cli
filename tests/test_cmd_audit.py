"""Tests for audit CLI commands."""

from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_audit import audit_group


def _make_event(action="push", project="proj", env="dev", user="bob", note=None):
    return {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": action,
        "project": project,
        "env": env,
        "user": user,
        "note": note,
    }


def test_cmd_log_no_events():
    runner = CliRunner()
    with patch("envoy.cmd_audit.read_events", return_value=[]):
        result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_cmd_log_shows_events():
    runner = CliRunner()
    events = [_make_event(action="pull", note="test note")]
    with patch("envoy.cmd_audit.read_events", return_value=events):
        result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "pull" in result.output
    assert "proj/dev" in result.output
    assert "test note" in result.output


def test_cmd_log_passes_filters():
    runner = CliRunner()
    with patch("envoy.cmd_audit.read_events", return_value=[]) as mock_read:
        runner.invoke(audit_group, ["log", "-p", "myapp", "-e", "prod", "-n", "10"])
        mock_read.assert_called_once_with(project="myapp", env="prod", limit=10)


def test_cmd_clear_confirmed():
    runner = CliRunner()
    with patch("envoy.cmd_audit.clear_log") as mock_clear:
        result = runner.invoke(audit_group, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    mock_clear.assert_called_once()


def test_cmd_clear_aborted():
    runner = CliRunner()
    with patch("envoy.cmd_audit.clear_log") as mock_clear:
        result = runner.invoke(audit_group, ["clear"], input="n\n")
    assert result.exit_code != 0 or "Aborted" in result.output
    mock_clear.assert_not_called()
