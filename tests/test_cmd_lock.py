import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_lock import lock_group


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_lock_success(runner):
    with patch("envoy.cmd_lock.is_locked", return_value=False), \
         patch("envoy.cmd_lock.lock_env") as mock_lock:
        result = runner.invoke(lock_group, ["set", "myapp", "production"])
        assert result.exit_code == 0
        assert "Locked" in result.output
        mock_lock.assert_called_once_with("myapp", "production")


def test_cmd_lock_already_locked(runner):
    with patch("envoy.cmd_lock.is_locked", return_value=True):
        result = runner.invoke(lock_group, ["set", "myapp", "production"])
        assert "already locked" in result.output


def test_cmd_unlock_success(runner):
    with patch("envoy.cmd_lock.is_locked", return_value=True), \
         patch("envoy.cmd_lock.unlock_env") as mock_unlock:
        result = runner.invoke(lock_group, ["unset", "myapp", "production"])
        assert "Unlocked" in result.output
        mock_unlock.assert_called_once_with("myapp", "production")


def test_cmd_unlock_not_locked(runner):
    with patch("envoy.cmd_lock.is_locked", return_value=False):
        result = runner.invoke(lock_group, ["unset", "myapp", "production"])
        assert "not locked" in result.output


def test_cmd_list_locked_shows_envs(runner):
    with patch("envoy.cmd_lock.list_locked", return_value=["production", "staging"]):
        result = runner.invoke(lock_group, ["list", "myapp"])
        assert "production" in result.output
        assert "staging" in result.output


def test_cmd_list_locked_empty(runner):
    with patch("envoy.cmd_lock.list_locked", return_value=[]):
        result = runner.invoke(lock_group, ["list", "myapp"])
        assert "No locked" in result.output
