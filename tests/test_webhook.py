"""Tests for envoy.webhook."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

import envoy.webhook as wh


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(wh, "get_store_dir", lambda: str(tmp_path))
    yield tmp_path


def test_register_creates_entry(tmp_store):
    wh.register("myapp", "https://example.com/hook")
    hooks = wh.list_webhooks("myapp")
    assert "https://example.com/hook" in hooks
    assert "push" in hooks["https://example.com/hook"]


def test_register_custom_events(tmp_store):
    wh.register("myapp", "https://example.com/hook", ["push"])
    hooks = wh.list_webhooks("myapp")
    assert hooks["https://example.com/hook"] == ["push"]


def test_register_multiple_urls(tmp_store):
    wh.register("proj", "https://a.com")
    wh.register("proj", "https://b.com")
    hooks = wh.list_webhooks("proj")
    assert len(hooks) == 2


def test_unregister_existing(tmp_store):
    wh.register("proj", "https://a.com")
    result = wh.unregister("proj", "https://a.com")
    assert result is True
    assert wh.list_webhooks("proj") == {}


def test_unregister_nonexistent(tmp_store):
    result = wh.unregister("proj", "https://ghost.com")
    assert result is False


def test_list_webhooks_empty(tmp_store):
    assert wh.list_webhooks("unknown") == {}


def test_notify_calls_registered_url(tmp_store):
    wh.register("proj", "https://hook.example.com", ["push"])
    mock_resp = MagicMock()
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        failed = wh.notify("proj", "push", {"env": "production"})
    assert failed == []
    mock_open.assert_called_once()


def test_notify_skips_unsubscribed_event(tmp_store):
    wh.register("proj", "https://hook.example.com", ["push"])
    with patch("urllib.request.urlopen") as mock_open:
        failed = wh.notify("proj", "pull", {"env": "production"})
    mock_open.assert_not_called()
    assert failed == []


def test_notify_returns_failed_on_error(tmp_store):
    import urllib.error
    wh.register("proj", "https://bad.url", ["push"])
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("err")):
        failed = wh.notify("proj", "push", {})
    assert "https://bad.url" in failed
