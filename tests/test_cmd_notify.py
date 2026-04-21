"""Tests for envoy.cmd_notify CLI commands."""

import pytest
from click.testing import CliRunner

from envoy.cmd_notify import notify_group
from envoy import notify


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.notify._notify_path", lambda: tmp_path / "notifications.json")
    yield tmp_path


def test_cmd_set_enables_preference(runner):
    result = runner.invoke(notify_group, ["set", "myapp", "push", "stdout"])
    assert result.exit_code == 0
    assert "enabled" in result.output
    assert notify.get_preference("myapp", "push", "stdout") is True


def test_cmd_set_disables_preference(runner):
    notify.set_preference("myapp", "push", "stdout", enabled=True)
    result = runner.invoke(notify_group, ["set", "myapp", "push", "stdout", "--disable"])
    assert result.exit_code == 0
    assert "disabled" in result.output
    assert notify.get_preference("myapp", "push", "stdout") is False


def test_cmd_set_invalid_event_shows_error(runner):
    result = runner.invoke(notify_group, ["set", "myapp", "explode", "stdout"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cmd_get_shows_enabled(runner):
    notify.set_preference("myapp", "pull", "webhook", enabled=True)
    result = runner.invoke(notify_group, ["get", "myapp", "pull", "webhook"])
    assert result.exit_code == 0
    assert "enabled" in result.output


def test_cmd_get_shows_disabled(runner):
    result = runner.invoke(notify_group, ["get", "myapp", "pull", "webhook"])
    assert result.exit_code == 0
    assert "disabled" in result.output


def test_cmd_list_no_preferences(runner):
    result = runner.invoke(notify_group, ["list", "ghost"])
    assert result.exit_code == 0
    assert "No notification" in result.output


def test_cmd_list_shows_preferences(runner):
    notify.set_preference("proj", "push", "stdout", enabled=True)
    notify.set_preference("proj", "remove", "file", enabled=False)
    result = runner.invoke(notify_group, ["list", "proj"])
    assert result.exit_code == 0
    assert "push" in result.output
    assert "stdout" in result.output


def test_cmd_clear_confirmed(runner):
    notify.set_preference("proj", "push", "stdout", enabled=True)
    result = runner.invoke(notify_group, ["clear", "proj"], input="y\n")
    assert result.exit_code == 0
    assert "Cleared" in result.output
    assert notify.get_project_preferences("proj") == {}


def test_cmd_clear_aborted(runner):
    notify.set_preference("proj", "push", "stdout", enabled=True)
    result = runner.invoke(notify_group, ["clear", "proj"], input="n\n")
    assert notify.get_preference("proj", "push", "stdout") is True
