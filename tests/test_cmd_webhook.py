"""Tests for envoy.cmd_webhook CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envoy.cmd_webhook import webhook_group


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_add_registers_webhook(runner):
    with patch("envoy.cmd_webhook.webhook.register") as mock_reg:
        result = runner.invoke(webhook_group, ["add", "myapp", "https://ex.com"])
    assert result.exit_code == 0
    mock_reg.assert_called_once_with("myapp", "https://ex.com", ["push", "pull", "remove"])
    assert "registered" in result.output


def test_cmd_add_custom_events(runner):
    with patch("envoy.cmd_webhook.webhook.register") as mock_reg:
        result = runner.invoke(webhook_group, ["add", "myapp", "https://ex.com", "--events", "push"])
    assert result.exit_code == 0
    mock_reg.assert_called_once_with("myapp", "https://ex.com", ["push"])


def test_cmd_remove_existing(runner):
    with patch("envoy.cmd_webhook.webhook.unregister", return_value=True):
        result = runner.invoke(webhook_group, ["remove", "myapp", "https://ex.com"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cmd_remove_not_found(runner):
    with patch("envoy.cmd_webhook.webhook.unregister", return_value=False):
        result = runner.invoke(webhook_group, ["remove", "myapp", "https://ex.com"])
    assert result.exit_code == 0
    assert "No webhook found" in result.output


def test_cmd_list_shows_hooks(runner):
    hooks = {"https://ex.com": ["push", "pull"]}
    with patch("envoy.cmd_webhook.webhook.list_webhooks", return_value=hooks):
        result = runner.invoke(webhook_group, ["list", "myapp"])
    assert result.exit_code == 0
    assert "https://ex.com" in result.output
    assert "push" in result.output


def test_cmd_list_empty(runner):
    with patch("envoy.cmd_webhook.webhook.list_webhooks", return_value={}):
        result = runner.invoke(webhook_group, ["list", "myapp"])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_cmd_test_success(runner):
    with patch("envoy.cmd_webhook.webhook.notify", return_value=[]):
        result = runner.invoke(webhook_group, ["test", "myapp"])
    assert result.exit_code == 0
    assert "successfully" in result.output


def test_cmd_test_with_failures(runner):
    with patch("envoy.cmd_webhook.webhook.notify", return_value=["https://bad.url"]):
        result = runner.invoke(webhook_group, ["test", "myapp"])
    assert result.exit_code == 0
    assert "Failed" in result.output
    assert "https://bad.url" in result.output
