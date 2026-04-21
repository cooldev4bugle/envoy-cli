import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_broadcast import broadcast_group


@pytest.fixture
def runner():
    return CliRunner()


_SAMPLE_RECORD = {
    "id": "abc123",
    "project": "myapp",
    "message": "Deploying new build",
    "severity": "info",
    "timestamp": "2024-01-01T00:00:00",
    "read": False,
}


def test_cmd_send_success(runner):
    with patch("envoy.cmd_broadcast.send", return_value=_SAMPLE_RECORD) as mock_send:
        result = runner.invoke(broadcast_group, ["send", "myapp", "Deploying new build"])
    assert result.exit_code == 0
    assert "Broadcast sent to project 'myapp'" in result.output
    assert "abc123" in result.output
    mock_send.assert_called_once_with("myapp", "Deploying new build", severity="info")


def test_cmd_send_with_severity(runner):
    record = {**_SAMPLE_RECORD, "severity": "critical"}
    with patch("envoy.cmd_broadcast.send", return_value=record):
        result = runner.invoke(broadcast_group, ["send", "myapp", "ALERT", "--severity", "critical"])
    assert result.exit_code == 0
    assert "CRITICAL" in result.output


def test_cmd_send_invalid_severity(runner):
    result = runner.invoke(broadcast_group, ["send", "myapp", "msg", "--severity", "unknown"])
    assert result.exit_code != 0


def test_cmd_send_value_error_shown(runner):
    with patch("envoy.cmd_broadcast.send", side_effect=ValueError("bad severity")):
        result = runner.invoke(broadcast_group, ["send", "myapp", "msg"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_cmd_list_no_broadcasts(runner):
    with patch("envoy.cmd_broadcast.get_broadcasts", return_value=[]):
        result = runner.invoke(broadcast_group, ["list", "myapp"])
    assert result.exit_code == 0
    assert "No broadcasts found" in result.output


def test_cmd_list_shows_records(runner):
    with patch("envoy.cmd_broadcast.get_broadcasts", return_value=[_SAMPLE_RECORD]):
        result = runner.invoke(broadcast_group, ["list", "myapp"])
    assert result.exit_code == 0
    assert "Deploying new build" in result.output
    assert "UNREAD" in result.output


def test_cmd_list_unread_only_flag(runner):
    with patch("envoy.cmd_broadcast.get_broadcasts", return_value=[]) as mock_get:
        runner.invoke(broadcast_group, ["list", "myapp", "--unread-only"])
    mock_get.assert_called_once_with("myapp", unread_only=True, severity=None)


def test_cmd_read_success(runner):
    with patch("envoy.cmd_broadcast.mark_read", return_value=True):
        result = runner.invoke(broadcast_group, ["read", "myapp", "abc123"])
    assert result.exit_code == 0
    assert "marked as read" in result.output


def test_cmd_read_not_found(runner):
    with patch("envoy.cmd_broadcast.mark_read", return_value=False):
        result = runner.invoke(broadcast_group, ["read", "myapp", "missing"])
    assert result.exit_code == 1
