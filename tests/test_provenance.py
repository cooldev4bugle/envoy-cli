"""Tests for envoy.provenance."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from envoy import provenance


@pytest.fixture()
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance, "_provenance_path", lambda: tmp_path / "provenance.json")
    return tmp_path


def test_get_provenance_returns_none_when_unset(tmp_store):
    assert provenance.get_provenance("myapp", "production") is None


def test_set_and_get_provenance(tmp_store):
    entry = provenance.set_provenance("myapp", "production", author="alice")
    result = provenance.get_provenance("myapp", "production")
    assert result is not None
    assert result["author"] == "alice"
    assert result["source"] == "manual"
    assert result["note"] == ""
    assert "recorded_at" in result


def test_set_provenance_custom_source_and_note(tmp_store):
    entry = provenance.set_provenance("myapp", "staging", author="ci-bot", source="ci", note="deployed via pipeline")
    result = provenance.get_provenance("myapp", "staging")
    assert result["source"] == "ci"
    assert result["note"] == "deployed via pipeline"


def test_set_provenance_overwrites_existing(tmp_store):
    provenance.set_provenance("myapp", "dev", author="alice")
    provenance.set_provenance("myapp", "dev", author="bob", source="import")
    result = provenance.get_provenance("myapp", "dev")
    assert result["author"] == "bob"
    assert result["source"] == "import"


def test_remove_provenance_returns_true_when_exists(tmp_store):
    provenance.set_provenance("myapp", "production", author="alice")
    assert provenance.remove_provenance("myapp", "production") is True
    assert provenance.get_provenance("myapp", "production") is None


def test_remove_provenance_returns_false_when_missing(tmp_store):
    assert provenance.remove_provenance("myapp", "ghost") is False


def test_list_provenance_returns_all_envs_for_project(tmp_store):
    provenance.set_provenance("myapp", "production", author="alice")
    provenance.set_provenance("myapp", "staging", author="bob")
    provenance.set_provenance("otherapp", "production", author="carol")
    records = provenance.list_provenance("myapp")
    assert set(records.keys()) == {"production", "staging"}
    assert records["production"]["author"] == "alice"
    assert records["staging"]["author"] == "bob"


def test_list_provenance_empty_when_no_records(tmp_store):
    assert provenance.list_provenance("nonexistent") == {}


def test_provenance_recorded_at_is_utc_iso(tmp_store):
    entry = provenance.set_provenance("myapp", "production", author="alice")
    assert "+00:00" in entry["recorded_at"] or entry["recorded_at"].endswith("Z")


def test_set_provenance_persists_to_disk(tmp_store):
    provenance.set_provenance("myapp", "production", author="alice")
    raw = json.loads((tmp_store / "provenance.json").read_text())
    assert "myapp::production" in raw
