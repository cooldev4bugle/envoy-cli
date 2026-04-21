"""Tests for envoy.broadcast."""
from unittest.mock import patch

import pytest

from envoy import broadcast


PROJECT = "acme"
ENVS = ["production", "staging", "dev"]


def _patch_vault(envs=None):
    return patch("envoy.broadcast.vault.list_envs", return_value=envs or ENVS)


def _patch_storage(tmp_path):
    fake_project_path = tmp_path / PROJECT
    fake_project_path.mkdir(parents=True, exist_ok=True)
    return patch(
        "envoy.broadcast._broadcast_path",
        return_value=str(fake_project_path / "broadcasts.json"),
    )


def test_send_creates_record(tmp_path):
    with _patch_vault(), _patch_storage(tmp_path):
        record = broadcast.send(PROJECT, "Deploy complete", severity="info", author="alice")

    assert record["message"] == "Deploy complete"
    assert record["severity"] == "info"
    assert record["author"] == "alice"
    assert record["environments"] == ENVS
    assert "timestamp" in record


def test_send_persists(tmp_path):
    with _patch_vault(), _patch_storage(tmp_path):
        broadcast.send(PROJECT, "First", severity="info")
        broadcast.send(PROJECT, "Second", severity="warning")
        records = broadcast.get_broadcasts(PROJECT)

    assert len(records) == 2
    assert records[0]["message"] == "First"
    assert records[1]["message"] == "Second"


def test_send_invalid_severity_raises(tmp_path):
    with _patch_vault(), _patch_storage(tmp_path):
        with pytest.raises(ValueError, match="Invalid severity"):
            broadcast.send(PROJECT, "Oops", severity="debug")


def test_get_broadcasts_filter_by_severity(tmp_path):
    with _patch_vault(), _patch_storage(tmp_path):
        broadcast.send(PROJECT, "Info msg", severity="info")
        broadcast.send(PROJECT, "Crit msg", severity="critical")
        infos = broadcast.get_broadcasts(PROJECT, severity="info")
        crits = broadcast.get_broadcasts(PROJECT, severity="critical")

    assert len(infos) == 1
    assert infos[0]["message"] == "Info msg"
    assert len(crits) == 1
    assert crits[0]["message"] == "Crit msg"


def test_get_broadcasts_empty_when_none(tmp_path):
    with _patch_vault(), _patch_storage(tmp_path):
        records = broadcast.get_broadcasts(PROJECT)
    assert records == []


def test_clear_broadcasts_returns_count(tmp_path):
    with _patch_vault(), _patch_storage(tmp_path):
        broadcast.send(PROJECT, "A", severity="info")
        broadcast.send(PROJECT, "B", severity="warning")
        removed = broadcast.clear_broadcasts(PROJECT)
        remaining = broadcast.get_broadcasts(PROJECT)

    assert removed == 2
    assert remaining == []
