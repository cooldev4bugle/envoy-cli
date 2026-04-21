"""Tests for envoy.rollback."""

import pytest
from unittest.mock import patch, MagicMock
from envoy import rollback

SNAPS = [
    {"label": "v1", "created_at": "2024-01-01T00:00:00"},
    {"label": "v2", "created_at": "2024-06-01T00:00:00"},
    {"label": "v3", "created_at": "2024-12-01T00:00:00"},
]


@patch("envoy.rollback.history.record")
@patch("envoy.rollback.snapshot.restore", return_value={"KEY": "val"})
@patch("envoy.rollback.snapshot.list_snapshots", return_value=SNAPS)
def test_rollback_to_snapshot_success(mock_list, mock_restore, mock_record):
    data = rollback.rollback_to_snapshot("proj", "dev", "v2", "pass")
    assert data == {"KEY": "val"}
    mock_restore.assert_called_once_with("proj", "dev", "v2", "pass")
    mock_record.assert_called_once()


@patch("envoy.rollback.snapshot.list_snapshots", return_value=SNAPS)
def test_rollback_to_snapshot_not_found(mock_list):
    with pytest.raises(KeyError, match="missing"):
        rollback.rollback_to_snapshot("proj", "dev", "missing", "pass")


@patch("envoy.rollback.history.record")
@patch("envoy.rollback.snapshot.restore", return_value={"KEY": "val"})
@patch("envoy.rollback.snapshot.list_snapshots", return_value=SNAPS)
def test_rollback_to_nth_latest(mock_list, mock_restore, mock_record):
    rollback.rollback_to_nth("proj", "dev", 1, "pass")
    mock_restore.assert_called_once_with("proj", "dev", "v3", "pass")


@patch("envoy.rollback.history.record")
@patch("envoy.rollback.snapshot.restore", return_value={})
@patch("envoy.rollback.snapshot.list_snapshots", return_value=SNAPS)
def test_rollback_to_nth_oldest(mock_list, mock_restore, mock_record):
    rollback.rollback_to_nth("proj", "dev", 3, "pass")
    mock_restore.assert_called_once_with("proj", "dev", "v1", "pass")


@patch("envoy.rollback.snapshot.list_snapshots", return_value=[])
def test_rollback_to_nth_no_snapshots(mock_list):
    with pytest.raises(ValueError):
        rollback.rollback_to_nth("proj", "dev", 1, "pass")


@patch("envoy.rollback.snapshot.list_snapshots", return_value=SNAPS)
def test_rollback_to_nth_out_of_range(mock_list):
    with pytest.raises(IndexError):
        rollback.rollback_to_nth("proj", "dev", 99, "pass")


@patch("envoy.rollback.snapshot.list_snapshots", return_value=SNAPS)
def test_list_rollback_points_newest_first(mock_list):
    points = rollback.list_rollback_points("proj", "dev")
    assert points[0]["label"] == "v3"
    assert points[-1]["label"] == "v1"


@patch("envoy.rollback.snapshot.list_snapshots", return_value=[])
def test_list_rollback_points_empty(mock_list):
    assert rollback.list_rollback_points("proj", "dev") == []
