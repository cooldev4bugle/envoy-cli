"""Tests for envoy.dependency."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from envoy import dependency as dep


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.dependency.get_store_dir", lambda: tmp_path)
    return tmp_path


def test_add_dependency_creates_entry():
    dep.add_dependency("myapp", "DATABASE_URL", ["DB_HOST", "DB_PORT"])
    result = dep.get_dependencies("myapp", "DATABASE_URL")
    assert "DB_HOST" in result
    assert "DB_PORT" in result


def test_add_dependency_no_duplicates():
    dep.add_dependency("myapp", "KEY", ["A", "B"])
    dep.add_dependency("myapp", "KEY", ["A", "C"])
    result = dep.get_dependencies("myapp", "KEY")
    assert result.count("A") == 1
    assert "B" in result
    assert "C" in result


def test_remove_dependency_returns_true_when_exists():
    dep.add_dependency("myapp", "KEY", ["A", "B"])
    removed = dep.remove_dependency("myapp", "KEY", "A")
    assert removed is True
    assert "A" not in dep.get_dependencies("myapp", "KEY")
    assert "B" in dep.get_dependencies("myapp", "KEY")


def test_remove_dependency_returns_false_when_missing():
    dep.add_dependency("myapp", "KEY", ["A"])
    result = dep.remove_dependency("myapp", "KEY", "NOPE")
    assert result is False


def test_remove_last_dep_cleans_up_key():
    dep.add_dependency("myapp", "KEY", ["A"])
    dep.remove_dependency("myapp", "KEY", "A")
    assert dep.get_all("myapp") == {}


def test_get_dependencies_missing_returns_empty():
    assert dep.get_dependencies("ghost", "NOTHING") == []


def test_get_all_returns_project_map():
    dep.add_dependency("proj", "X", ["Y"])
    dep.add_dependency("proj", "Z", ["W"])
    all_deps = dep.get_all("proj")
    assert "X" in all_deps
    assert "Z" in all_deps


def test_validate_no_violations():
    dep.add_dependency("proj", "APP_URL", ["HOST", "PORT"])
    violations = dep.validate("proj", ["HOST", "PORT", "APP_URL"])
    assert violations == {}


def test_validate_detects_missing_keys():
    dep.add_dependency("proj", "APP_URL", ["HOST", "PORT"])
    violations = dep.validate("proj", ["APP_URL"])
    assert "APP_URL" in violations
    assert "HOST" in violations["APP_URL"]
    assert "PORT" in violations["APP_URL"]


def test_validate_partial_missing():
    dep.add_dependency("proj", "APP_URL", ["HOST", "PORT"])
    violations = dep.validate("proj", ["APP_URL", "HOST"])
    assert violations["APP_URL"] == ["PORT"]
