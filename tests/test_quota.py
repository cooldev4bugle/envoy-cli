"""Tests for envoy.quota."""

import pytest
from unittest.mock import patch

from envoy import quota as q


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "get_store_dir", lambda: tmp_path)
    return tmp_path


def test_get_quota_returns_default_when_unset():
    assert q.get_quota("myproject") == q.DEFAULT_QUOTA


def test_set_and_get_quota():
    q.set_quota("myproject", 5)
    assert q.get_quota("myproject") == 5


def test_set_quota_raises_on_zero():
    with pytest.raises(ValueError):
        q.set_quota("myproject", 0)


def test_set_quota_raises_on_negative():
    with pytest.raises(ValueError):
        q.set_quota("myproject", -3)


def test_remove_quota_returns_true_when_exists():
    q.set_quota("proj", 3)
    assert q.remove_quota("proj") is True
    assert q.get_quota("proj") == q.DEFAULT_QUOTA


def test_remove_quota_returns_false_when_missing():
    assert q.remove_quota("ghost") is False


def test_check_quota_within_limit():
    q.set_quota("proj", 5)
    with patch("envoy.quota.list_environments", return_value=["dev", "staging"]):
        count, limit, ok = q.check_quota("proj")
    assert count == 2
    assert limit == 5
    assert ok is True


def test_check_quota_exceeded():
    q.set_quota("proj", 2)
    with patch("envoy.quota.list_environments", return_value=["dev", "staging"]):
        count, limit, ok = q.check_quota("proj")
    assert ok is False


def test_check_quota_missing_project_treats_as_zero():
    with patch("envoy.quota.list_environments", side_effect=FileNotFoundError):
        count, limit, ok = q.check_quota("newproject")
    assert count == 0
    assert ok is True


def test_enforce_quota_raises_when_exceeded():
    q.set_quota("proj", 1)
    with patch("envoy.quota.list_environments", return_value=["dev", "prod"]):
        with pytest.raises(RuntimeError, match="quota"):
            q.enforce_quota("proj")


def test_enforce_quota_passes_when_within_limit():
    q.set_quota("proj", 5)
    with patch("envoy.quota.list_environments", return_value=["dev"]):
        q.enforce_quota("proj")  # should not raise
