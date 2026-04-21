"""Tests for envoy/priority.py"""

import pytest

from envoy import priority as P


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "get_store_dir", lambda: tmp_path)


def test_get_priority_returns_normal_by_default():
    assert P.get_priority("myapp", "production") == "normal"


def test_set_and_get_priority():
    P.set_priority("myapp", "production", "critical")
    assert P.get_priority("myapp", "production") == "critical"


def test_set_priority_invalid_level_raises():
    with pytest.raises(ValueError, match="Invalid priority level"):
        P.set_priority("myapp", "staging", "urgent")


def test_set_priority_overwrites_existing():
    P.set_priority("myapp", "staging", "high")
    P.set_priority("myapp", "staging", "low")
    assert P.get_priority("myapp", "staging") == "low"


def test_remove_priority_returns_true_when_exists():
    P.set_priority("myapp", "dev", "high")
    assert P.remove_priority("myapp", "dev") is True
    assert P.get_priority("myapp", "dev") == "normal"


def test_remove_priority_returns_false_when_missing():
    assert P.remove_priority("myapp", "ghost") is False


def test_list_priorities_empty():
    assert P.list_priorities() == []


def test_list_priorities_returns_all():
    P.set_priority("app", "prod", "critical")
    P.set_priority("app", "dev", "low")
    results = P.list_priorities()
    levels = [r["level"] for r in results]
    assert "critical" in levels
    assert "low" in levels


def test_list_priorities_sorted_by_level():
    P.set_priority("app", "dev", "low")
    P.set_priority("app", "prod", "critical")
    P.set_priority("app", "staging", "high")
    results = P.list_priorities()
    assert results[0]["level"] == "critical"
    assert results[-1]["level"] == "low"


def test_list_priorities_filter_by_project():
    P.set_priority("alpha", "prod", "critical")
    P.set_priority("beta", "prod", "high")
    results = P.list_priorities(project="alpha")
    assert all(r["project"] == "alpha" for r in results)
    assert len(results) == 1


def test_all_valid_levels_accepted():
    for i, level in enumerate(P.VALID_LEVELS):
        P.set_priority("proj", f"env{i}", level)
        assert P.get_priority("proj", f"env{i}") == level
