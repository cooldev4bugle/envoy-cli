"""Tests for envoy.endorsement."""

import json
import pytest

from envoy import endorsement


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.endorsement._endorsement_path",
                        lambda: tmp_path / "endorsements.json")
    yield tmp_path


def test_get_endorsers_returns_empty_by_default():
    assert endorsement.get_endorsers("proj", "dev") == []


def test_endorse_adds_user():
    endorsers = endorsement.endorse("proj", "dev", "alice")
    assert "alice" in endorsers


def test_endorse_no_duplicates():
    endorsement.endorse("proj", "dev", "alice")
    result = endorsement.endorse("proj", "dev", "alice")
    assert result.count("alice") == 1


def test_endorse_multiple_users():
    endorsement.endorse("proj", "dev", "alice")
    endorsement.endorse("proj", "dev", "bob")
    endorsers = endorsement.get_endorsers("proj", "dev")
    assert "alice" in endorsers
    assert "bob" in endorsers


def test_is_endorsed_by_true():
    endorsement.endorse("proj", "dev", "alice")
    assert endorsement.is_endorsed_by("proj", "dev", "alice") is True


def test_is_endorsed_by_false():
    assert endorsement.is_endorsed_by("proj", "dev", "ghost") is False


def test_endorsement_count():
    endorsement.endorse("proj", "dev", "alice")
    endorsement.endorse("proj", "dev", "bob")
    assert endorsement.endorsement_count("proj", "dev") == 2


def test_unendorse_removes_user():
    endorsement.endorse("proj", "dev", "alice")
    removed = endorsement.unendorse("proj", "dev", "alice")
    assert removed is True
    assert endorsement.is_endorsed_by("proj", "dev", "alice") is False


def test_unendorse_nonexistent_returns_false():
    result = endorsement.unendorse("proj", "dev", "nobody")
    assert result is False


def test_list_endorsed_all():
    endorsement.endorse("proj", "dev", "alice")
    endorsement.endorse("other", "staging", "bob")
    all_entries = endorsement.list_endorsed()
    assert len(all_entries) == 2


def test_list_endorsed_filtered_by_project():
    endorsement.endorse("proj", "dev", "alice")
    endorsement.endorse("other", "staging", "bob")
    results = endorsement.list_endorsed(project="proj")
    assert len(results) == 1
    assert results[0]["project"] == "proj"


def test_endorsement_persists(tmp_path):
    endorsement.endorse("proj", "prod", "carol")
    raw = json.loads((tmp_path / "endorsements.json").read_text())
    assert any("carol" in v["endorsers"] for v in raw.values())
