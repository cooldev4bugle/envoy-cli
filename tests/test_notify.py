"""Tests for envoy.notify module."""

import pytest

from envoy import notify


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.notify._notify_path", lambda: tmp_path / "notifications.json")
    yield tmp_path


def test_get_preference_returns_false_by_default():
    assert notify.get_preference("myapp", "push", "stdout") is False


def test_set_and_get_preference():
    notify.set_preference("myapp", "push", "stdout", enabled=True)
    assert notify.get_preference("myapp", "push", "stdout") is True


def test_set_preference_disable():
    notify.set_preference("myapp", "push", "stdout", enabled=True)
    notify.set_preference("myapp", "push", "stdout", enabled=False)
    assert notify.get_preference("myapp", "push", "stdout") is False


def test_set_preference_invalid_event():
    with pytest.raises(ValueError, match="Unknown event"):
        notify.set_preference("myapp", "explode", "stdout")


def test_set_preference_invalid_channel():
    with pytest.raises(ValueError, match="Unknown channel"):
        notify.set_preference("myapp", "push", "telepathy")


def test_get_project_preferences_empty():
    assert notify.get_project_preferences("ghost") == {}


def test_get_project_preferences_returns_all():
    notify.set_preference("proj", "push", "stdout", enabled=True)
    notify.set_preference("proj", "pull", "webhook", enabled=True)
    prefs = notify.get_project_preferences("proj")
    assert prefs["push"]["stdout"] is True
    assert prefs["pull"]["webhook"] is True


def test_clear_preferences_removes_project():
    notify.set_preference("proj", "push", "stdout", enabled=True)
    notify.clear_preferences("proj")
    assert notify.get_project_preferences("proj") == {}


def test_clear_preferences_nonexistent_is_noop():
    notify.clear_preferences("nobody")  # should not raise


def test_notify_returns_enabled_channels():
    notify.set_preference("app", "rotate", "stdout", enabled=True)
    notify.set_preference("app", "rotate", "webhook", enabled=False)
    used = notify.notify("app", "rotate", "key rotated")
    assert "stdout" in used
    assert "webhook" not in used


def test_notify_no_prefs_returns_empty():
    used = notify.notify("ghost", "push", "something happened")
    assert used == []


def test_multiple_projects_isolated():
    notify.set_preference("alpha", "push", "stdout", enabled=True)
    notify.set_preference("beta", "push", "stdout", enabled=False)
    assert notify.get_preference("alpha", "push", "stdout") is True
    assert notify.get_preference("beta", "push", "stdout") is False
