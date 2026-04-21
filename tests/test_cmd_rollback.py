"""Tests for envoy.cmd_rollback CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_rollback import rollback_group

SNAPS = [
    {"label": "snap-a", "created_at": "2024-01-01T00:00:00"},
    {"label": "snap-b", "created_at": "2024-06-01T00:00:00"},
]


@pytest.fixture
def runner():
    return CliRunner()


@patch("envoy.cmd_rollback.rollback.rollback_to_snapshot")
def test_cmd_to_success(mock_rb, runner):
    result = runner.invoke(
        rollback_group, ["to", "proj", "dev", "snap-a", "--passphrase", "secret"]
    )
    assert result.exit_code == 0
    assert "snap-a" in result.output
    mock_rb.assert_called_once_with("proj", "dev", "snap-a", "secret")


@patch(
    "envoy.cmd_rollback.rollback.rollback_to_snapshot",
    side_effect=KeyError("snap-x"),
)
def test_cmd_to_not_found(mock_rb, runner):
    result = runner.invoke(
        rollback_group, ["to", "proj", "dev", "snap-x", "--passphrase", "s"]
    )
    assert result.exit_code == 1
    assert "Error" in result.output


@patch("envoy.cmd_rollback.rollback.rollback_to_nth")
def test_cmd_nth_success(mock_rb, runner):
    result = runner.invoke(
        rollback_group, ["nth", "proj", "dev", "1", "--passphrase", "secret"]
    )
    assert result.exit_code == 0
    assert "#1" in result.output
    mock_rb.assert_called_once_with("proj", "dev", 1, "secret")


@patch(
    "envoy.cmd_rollback.rollback.rollback_to_nth",
    side_effect=IndexError("out of range"),
)
def test_cmd_nth_out_of_range(mock_rb, runner):
    result = runner.invoke(
        rollback_group, ["nth", "proj", "dev", "99", "--passphrase", "s"]
    )
    assert result.exit_code == 1


@patch("envoy.cmd_rollback.rollback.list_rollback_points", return_value=SNAPS)
def test_cmd_list_shows_points(mock_list, runner):
    result = runner.invoke(rollback_group, ["list", "proj", "dev"])
    assert result.exit_code == 0
    assert "snap-a" in result.output
    assert "snap-b" in result.output


@patch("envoy.cmd_rollback.rollback.list_rollback_points", return_value=[])
def test_cmd_list_empty(mock_list, runner):
    result = runner.invoke(rollback_group, ["list", "proj", "dev"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output
