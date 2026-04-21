"""Tests for envoy.cmd_circuit_breaker CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envoy.cmd_circuit_breaker import breaker_group
from envoy import circuit_breaker as cb


@pytest.fixture
def runner():
    return CliRunner()


def _closed_entry():
    return {"state": cb.STATE_CLOSED, "failures": 0, "opened_at": None}


def _open_entry():
    return {"state": cb.STATE_OPEN, "failures": 5, "opened_at": 1700000000.0}


def test_cmd_status_closed(runner):
    with patch("envoy.cmd_circuit_breaker.cb.get_state", return_value=_closed_entry()), \
         patch("envoy.cmd_circuit_breaker.cb.is_open", return_value=False):
        result = runner.invoke(breaker_group, ["status", "myapp", "production"])
    assert result.exit_code == 0
    assert "closed" in result.output
    assert "Blocked : no" in result.output


def test_cmd_status_open(runner):
    with patch("envoy.cmd_circuit_breaker.cb.get_state", return_value=_open_entry()), \
         patch("envoy.cmd_circuit_breaker.cb.is_open", return_value=True):
        result = runner.invoke(breaker_group, ["status", "myapp", "production"])
    assert result.exit_code == 0
    assert "open" in result.output
    assert "Blocked : yes" in result.output
    assert "Failures: 5" in result.output


def test_cmd_reset_success(runner):
    with patch("envoy.cmd_circuit_breaker.cb.reset") as mock_reset:
        result = runner.invoke(breaker_group, ["reset", "myapp", "staging"])
    assert result.exit_code == 0
    assert "reset" in result.output
    mock_reset.assert_called_once_with("myapp", "staging")


def test_cmd_trip_records_failure(runner):
    with patch("envoy.cmd_circuit_breaker.cb.record_failure", return_value=_closed_entry()) as mock_fail:
        result = runner.invoke(breaker_group, ["trip", "myapp", "staging"])
    assert result.exit_code == 0
    assert "Failure recorded" in result.output
    mock_fail.assert_called_once_with("myapp", "staging", threshold=cb.DEFAULT_THRESHOLD)


def test_cmd_trip_with_custom_threshold(runner):
    with patch("envoy.cmd_circuit_breaker.cb.record_failure", return_value=_open_entry()) as mock_fail:
        result = runner.invoke(breaker_group, ["trip", "myapp", "prod", "--threshold", "3"])
    assert result.exit_code == 0
    mock_fail.assert_called_once_with("myapp", "prod", threshold=3)
    assert "open" in result.output
