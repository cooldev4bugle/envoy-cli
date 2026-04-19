"""Tests for envoy.cmd_rotate CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_rotate import rotate_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_cmd_rotate_project_success(runner):
    with patch("envoy.cmd_rotate.rotate.rotate_project", return_value=["prod", "staging"]) as mock_rot, \
         patch("envoy.cmd_rotate.audit.log_event") as mock_audit:
        result = runner.invoke(
            rotate_group,
            ["project", "myapp",
             "--old-passphrase", "old",
             "--new-passphrase", "new"],
            input="new\n",  # confirm
        )
        assert result.exit_code == 0, result.output
        assert "2 environment(s)" in result.output
        mock_rot.assert_called_once_with("myapp", "old", "new")
        mock_audit.assert_called_once()


def test_cmd_rotate_project_passphrase_mismatch(runner):
    result = runner.invoke(
        rotate_group,
        ["project", "myapp",
         "--old-passphrase", "old",
         "--new-passphrase", "new"],
        input="wrong\n",  # bad confirm
    )
    assert result.exit_code != 0
    assert "do not match" in result.output


def test_cmd_rotate_env_success(runner):
    with patch("envoy.cmd_rotate.rotate.rotate_env") as mock_rot, \
         patch("envoy.cmd_rotate.audit.log_event"):
        result = runner.invoke(
            rotate_group,
            ["env", "myapp", "production",
             "--old-passphrase", "old",
             "--new-passphrase", "new"],
            input="new\n",
        )
        assert result.exit_code == 0, result.output
        assert "production" in result.output
        mock_rot.assert_called_once_with("myapp", "production", "old", "new")


def test_cmd_rotate_env_error_shown(runner):
    with patch("envoy.cmd_rotate.rotate.rotate_env", side_effect=ValueError("bad decrypt")):
        result = runner.invoke(
            rotate_group,
            ["env", "myapp", "production",
             "--old-passphrase", "old",
             "--new-passphrase", "new"],
            input="new\n",
        )
        assert result.exit_code != 0
        assert "bad decrypt" in result.output
