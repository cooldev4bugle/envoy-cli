"""Tests for envoy.lineage."""

import pytest

from envoy import lineage


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.lineage.get_store_dir", lambda: tmp_path)


def test_get_origin_returns_none_when_unset():
    assert lineage.get_origin("myapp", "production", "DB_URL") is None


def test_set_and_get_origin():
    entry = lineage.set_origin(
        "myapp", "production", "DB_URL",
        source_project="shared", source_env="base",
        note="copied during migration",
    )
    assert entry["source_project"] == "shared"
    assert entry["source_env"] == "base"
    assert entry["note"] == "copied during migration"

    result = lineage.get_origin("myapp", "production", "DB_URL")
    assert result == entry


def test_set_origin_no_note_defaults_to_empty_string():
    lineage.set_origin("proj", "dev", "SECRET_KEY", "shared", "global")
    result = lineage.get_origin("proj", "dev", "SECRET_KEY")
    assert result["note"] == ""


def test_set_origin_overwrites_existing():
    lineage.set_origin("proj", "dev", "API_KEY", "old", "staging")
    lineage.set_origin("proj", "dev", "API_KEY", "new", "prod", note="updated")
    result = lineage.get_origin("proj", "dev", "API_KEY")
    assert result["source_project"] == "new"
    assert result["source_env"] == "prod"


def test_remove_origin_returns_true_when_exists():
    lineage.set_origin("proj", "dev", "TOKEN", "src", "env")
    assert lineage.remove_origin("proj", "dev", "TOKEN") is True
    assert lineage.get_origin("proj", "dev", "TOKEN") is None


def test_remove_origin_returns_false_when_missing():
    assert lineage.remove_origin("proj", "dev", "NONEXISTENT") is False


def test_list_lineage_returns_only_matching_env():
    lineage.set_origin("proj", "dev", "DB_URL", "shared", "base")
    lineage.set_origin("proj", "dev", "API_KEY", "shared", "base")
    lineage.set_origin("proj", "prod", "DB_URL", "shared", "prod-base")

    result = lineage.list_lineage("proj", "dev")
    assert set(result.keys()) == {"DB_URL", "API_KEY"}
    assert result["DB_URL"]["source_env"] == "base"


def test_list_lineage_empty_when_no_entries():
    result = lineage.list_lineage("proj", "staging")
    assert result == {}


def test_lineage_persists_across_calls():
    lineage.set_origin("app", "ci", "REDIS_URL", "infra", "shared")
    # Re-call get to verify it reads from disk
    fetched = lineage.get_origin("app", "ci", "REDIS_URL")
    assert fetched["source_project"] == "infra"
