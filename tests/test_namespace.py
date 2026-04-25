"""Tests for envoy.namespace."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import envoy.namespace as ns_mod


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(ns_mod, "get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_assign_creates_namespace():
    ns_mod.assign("myapp", "dev", "development")
    result = ns_mod.list_namespaces("myapp")
    assert "development" in result
    assert "dev" in result["development"]


def test_assign_no_duplicates():
    ns_mod.assign("myapp", "dev", "development")
    ns_mod.assign("myapp", "dev", "development")
    result = ns_mod.envs_in_namespace("myapp", "development")
    assert result.count("dev") == 1


def test_assign_multiple_envs_to_namespace():
    ns_mod.assign("myapp", "dev", "development")
    ns_mod.assign("myapp", "staging", "development")
    result = ns_mod.envs_in_namespace("myapp", "development")
    assert "dev" in result
    assert "staging" in result


def test_unassign_removes_env():
    ns_mod.assign("myapp", "dev", "development")
    removed = ns_mod.unassign("myapp", "dev", "development")
    assert removed is True
    assert ns_mod.envs_in_namespace("myapp", "development") == []


def test_unassign_nonexistent_returns_false():
    result = ns_mod.unassign("myapp", "ghost", "development")
    assert result is False


def test_unassign_cleans_up_empty_namespace():
    ns_mod.assign("myapp", "dev", "development")
    ns_mod.unassign("myapp", "dev", "development")
    assert "development" not in ns_mod.list_namespaces("myapp")


def test_get_namespace_returns_correct_ns():
    ns_mod.assign("myapp", "prod", "production")
    result = ns_mod.get_namespace("myapp", "prod")
    assert result == "production"


def test_get_namespace_returns_none_when_unassigned():
    result = ns_mod.get_namespace("myapp", "unknown")
    assert result is None


def test_list_namespaces_empty_project():
    result = ns_mod.list_namespaces("nonexistent")
    assert result == {}


def test_multiple_projects_isolated():
    ns_mod.assign("app1", "dev", "development")
    ns_mod.assign("app2", "dev", "staging")
    assert ns_mod.get_namespace("app1", "dev") == "development"
    assert ns_mod.get_namespace("app2", "dev") == "staging"


def test_assign_env_to_different_namespaces():
    """An env reassigned to a new namespace should only appear in the new one."""
    ns_mod.assign("myapp", "dev", "development")
    ns_mod.assign("myapp", "dev", "staging")
    # dev should now be in staging
    assert "dev" in ns_mod.envs_in_namespace("myapp", "staging")
    # dev should no longer be in development after reassignment
    assert "dev" not in ns_mod.envs_in_namespace("myapp", "development")
