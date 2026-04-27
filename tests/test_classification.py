"""Tests for envoy.classification."""

import pytest

import envoy.classification as cls_mod
from envoy.classification import (
    classify,
    classify_env,
    get_classification,
    list_classified,
    remove_classification,
)


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(cls_mod, "_classification_path", lambda: tmp_path / "classifications.json")


def test_get_classification_returns_none_when_unset():
    assert get_classification("proj", "dev", "API_KEY") is None


def test_classify_and_get():
    classify("proj", "dev", "API_KEY", "secret", note="super secret")
    result = get_classification("proj", "dev", "API_KEY")
    assert result is not None
    assert result["level"] == "secret"
    assert result["note"] == "super secret"


def test_classify_invalid_level_raises():
    with pytest.raises(ValueError, match="Invalid level"):
        classify("proj", "dev", "KEY", "ultra-secret")


def test_classify_overwrites_existing():
    classify("proj", "dev", "DB_PASS", "confidential")
    classify("proj", "dev", "DB_PASS", "secret", note="updated")
    result = get_classification("proj", "dev", "DB_PASS")
    assert result["level"] == "secret"
    assert result["note"] == "updated"


def test_remove_classification_returns_true_when_exists():
    classify("proj", "dev", "TOKEN", "internal")
    assert remove_classification("proj", "dev", "TOKEN") is True
    assert get_classification("proj", "dev", "TOKEN") is None


def test_remove_classification_returns_false_when_missing():
    assert remove_classification("proj", "dev", "GHOST") is False


def test_list_classified_returns_sorted():
    classify("proj", "dev", "Z_KEY", "public")
    classify("proj", "dev", "A_KEY", "secret")
    classify("proj", "dev", "M_KEY", "internal")
    results = list_classified("proj", "dev")
    keys = [r["key"] for r in results]
    assert keys == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_classified_filters_by_project_env():
    classify("proj", "dev", "KEY1", "public")
    classify("other", "dev", "KEY2", "secret")
    classify("proj", "prod", "KEY3", "internal")
    results = list_classified("proj", "dev")
    assert len(results) == 1
    assert results[0]["key"] == "KEY1"


def test_list_classified_empty():
    assert list_classified("proj", "dev") == []


def test_classify_env_bulk():
    pairs = {"API_KEY": "abc", "DB_PASS": "xyz", "PORT": "8080"}
    classify_env("proj", "dev", pairs, "confidential")
    for key in pairs:
        result = get_classification("proj", "dev", key)
        assert result is not None
        assert result["level"] == "confidential"


def test_all_valid_levels_accepted():
    from envoy.classification import LEVELS
    for level in LEVELS:
        classify("proj", "dev", f"KEY_{level}", level)
        r = get_classification("proj", "dev", f"KEY_{level}")
        assert r["level"] == level
