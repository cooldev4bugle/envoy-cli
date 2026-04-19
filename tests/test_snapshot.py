"""Tests for envoy.snapshot."""

from unittest.mock import patch, MagicMock

import pytest

from envoy import snapshot


SAMPLE = {"KEY": "value", "OTHER": "123"}


@patch("envoy.snapshot.vault.push")
@patch("envoy.snapshot.vault.pull", return_value=SAMPLE)
def test_create_uses_label(mock_pull, mock_push):
    label = snapshot.create("proj", "dev", "pass", label="v1")
    assert label == "v1"
    mock_pull.assert_called_once_with("proj", "dev", "pass")
    mock_push.assert_called_once_with("proj", "__snapshot__v1", SAMPLE, "pass")


@patch("envoy.snapshot.vault.push")
@patch("envoy.snapshot.vault.pull", return_value=SAMPLE)
def test_create_auto_label_is_timestamp(mock_pull, mock_push):
    label = snapshot.create("proj", "dev", "pass")
    assert label.isdigit()


@patch("envoy.snapshot.vault.push")
@patch("envoy.snapshot.vault.pull", return_value=SAMPLE)
def test_restore_pulls_snapshot_and_pushes_env(mock_pull, mock_push):
    snapshot.restore("proj", "dev", "pass", "v1")
    mock_pull.assert_called_once_with("proj", "__snapshot__v1", "pass")
    mock_push.assert_called_once_with("proj", "dev", SAMPLE, "pass")


@patch("envoy.snapshot.storage.list_environments",
       return_value=["dev", "__snapshot__v1", "__snapshot__v2", "prod"])
def test_list_snapshots_filters_correctly(mock_list):
    labels = snapshot.list_snapshots("proj")
    assert labels == ["v1", "v2"]


@patch("envoy.snapshot.storage.list_environments", return_value=["dev"])
def test_list_snapshots_empty(mock_list):
    assert snapshot.list_snapshots("proj") == []


@patch("envoy.snapshot.vault.remove")
def test_delete_calls_remove(mock_remove):
    snapshot.delete("proj", "v1")
    mock_remove.assert_called_once_with("proj", "__snapshot__v1")
