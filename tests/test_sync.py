"""Tests for envoy.sync module."""

import pytest
from unittest.mock import patch, MagicMock
from envoy import sync


PROJECT = "myapp"
PASS = "secret"


@patch("envoy.sync.audit.log_event")
@patch("envoy.sync.vault.push")
@patch("envoy.sync.vault.pull")
def test_sync_envs_merges(mock_pull, mock_push, mock_log):
    mock_pull.side_effect = [
        {"A": "1", "B": "2"},  # src
        {"B": "override", "C": "3"},  # dst
    ]
    result = sync.sync_envs(PROJECT, "dev", "staging", PASS)
    assert result["merged"]["A"] == "1"
    assert result["merged"]["B"] == "override"  # dst wins
    assert result["merged"]["C"] == "3"
    assert result["added"] == {"A": "1"}
    mock_push.assert_called_once()
    mock_log.assert_called_once()


@patch("envoy.sync.audit.log_event")
@patch("envoy.sync.vault.push")
@patch("envoy.sync.vault.pull")
def test_sync_envs_dst_missing(mock_pull, mock_push, mock_log):
    mock_pull.side_effect = [{"A": "1"}, FileNotFoundError]
    result = sync.sync_envs(PROJECT, "dev", "new-env", PASS)
    assert result["merged"] == {"A": "1"}
    assert result["added"] == {"A": "1"}


@patch("envoy.sync.audit.log_event")
@patch("envoy.sync.vault.push")
@patch("envoy.sync.vault.pull")
def test_copy_env(mock_pull, mock_push, mock_log):
    mock_pull.return_value = {"KEY": "val"}
    data = sync.copy_env(PROJECT, "dev", "prod", PASS)
    assert data == {"KEY": "val"}
    mock_push.assert_called_once_with(PROJECT, "prod", {"KEY": "val"}, PASS)
    mock_log.assert_called_once()


@patch("envoy.sync.audit.log_event")
@patch("envoy.sync.vault.remove")
@patch("envoy.sync.vault.push")
@patch("envoy.sync.vault.pull")
def test_rename_env(mock_pull, mock_push, mock_remove, mock_log):
    mock_pull.return_value = {"X": "y"}
    sync.rename_env(PROJECT, "old", "new", PASS)
    mock_push.assert_called_once_with(PROJECT, "new", {"X": "y"}, PASS)
    mock_remove.assert_called_once_with(PROJECT, "old")
    mock_log.assert_called_once()
