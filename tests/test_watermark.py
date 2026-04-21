"""Tests for envoy.watermark."""

from __future__ import annotations

import json
import time
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import envoy.watermark as wm


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.watermark._watermark_path", lambda: tmp_path / "watermarks.json")
    yield tmp_path


def test_set_watermark_creates_entry(tmp_store):
    entry = wm.set_watermark("myproject", "production", "alice", "initial deploy")
    assert entry["author"] == "alice"
    assert entry["note"] == "initial deploy"
    assert "timestamp" in entry


def test_set_watermark_persists(tmp_store):
    wm.set_watermark("myproject", "staging", "bob")
    result = wm.get_watermark("myproject", "staging")
    assert result is not None
    assert result["author"] == "bob"


def test_get_watermark_returns_none_when_missing(tmp_store):
    assert wm.get_watermark("ghost", "nowhere") is None


def test_set_watermark_overwrites_existing(tmp_store):
    wm.set_watermark("proj", "dev", "alice", "first")
    wm.set_watermark("proj", "dev", "bob", "second")
    result = wm.get_watermark("proj", "dev")
    assert result["author"] == "bob"
    assert result["note"] == "second"


def test_remove_watermark_returns_true_when_exists(tmp_store):
    wm.set_watermark("proj", "dev", "alice")
    assert wm.remove_watermark("proj", "dev") is True
    assert wm.get_watermark("proj", "dev") is None


def test_remove_watermark_returns_false_when_missing(tmp_store):
    assert wm.remove_watermark("proj", "ghost") is False


def test_list_watermarks_all(tmp_store):
    wm.set_watermark("alpha", "prod", "alice")
    wm.set_watermark("beta", "staging", "bob")
    results = wm.list_watermarks()
    assert len(results) == 2
    projects = {r["project"] for r in results}
    assert projects == {"alpha", "beta"}


def test_list_watermarks_filtered_by_project(tmp_store):
    wm.set_watermark("alpha", "prod", "alice")
    wm.set_watermark("alpha", "dev", "alice")
    wm.set_watermark("beta", "prod", "bob")
    results = wm.list_watermarks(project="alpha")
    assert len(results) == 2
    assert all(r["project"] == "alpha" for r in results)


def test_list_watermarks_empty(tmp_store):
    assert wm.list_watermarks() == []


def test_watermark_timestamp_is_recent(tmp_store):
    before = time.time()
    entry = wm.set_watermark("proj", "env", "user")
    after = time.time()
    assert before <= entry["timestamp"] <= after
