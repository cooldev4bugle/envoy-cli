import pytest
from unittest.mock import patch, MagicMock
from envoy import search


FAKE_DATA = {
    "dev": {"DATABASE_URL": "postgres://localhost/dev", "SECRET_KEY": "abc123"},
    "prod": {"DATABASE_URL": "postgres://prod-host/app", "API_KEY": "xyz789"},
}


def _make_mocks(monkeypatch):
    monkeypatch.setattr("envoy.storage.list_environments", lambda p: list(FAKE_DATA.keys()))
    monkeypatch.setattr("envoy.storage.list_projects", lambda: ["myapp"])
    monkeypatch.setattr("envoy.search._load_env", lambda project, env, passphrase: FAKE_DATA[env])


def test_search_by_key_finds_match(monkeypatch):
    _make_mocks(monkeypatch)
    results = search.search_by_key("myapp", "pass", "DATABASE")
    assert "dev" in results
    assert "prod" in results
    assert "DATABASE_URL" in results["dev"]


def test_search_by_key_no_match(monkeypatch):
    _make_mocks(monkeypatch)
    results = search.search_by_key("myapp", "pass", "NONEXISTENT")
    assert results == {}


def test_search_by_key_partial_match(monkeypatch):
    _make_mocks(monkeypatch)
    results = search.search_by_key("myapp", "pass", "KEY")
    assert "prod" in results
    assert "API_KEY" in results["prod"]
    assert "dev" in results
    assert "SECRET_KEY" in results["dev"]


def test_search_by_value_finds_match(monkeypatch):
    _make_mocks(monkeypatch)
    results = search.search_by_value("myapp", "pass", "postgres")
    assert "dev" in results
    assert "prod" in results


def test_search_by_value_no_match(monkeypatch):
    _make_mocks(monkeypatch)
    results = search.search_by_value("myapp", "pass", "mysql")
    assert results == {}


def test_search_key_across_projects(monkeypatch):
    _make_mocks(monkeypatch)
    results = search.search_key_across_projects("pass", "API_KEY")
    assert "myapp" in results
    assert "prod" in results["myapp"]


def test_load_env_returns_empty_on_error(monkeypatch):
    monkeypatch.setattr("envoy.storage.load", lambda p, e: (_ for _ in ()).throw(FileNotFoundError()))
    result = search._load_env("proj", "env", "pass")
    assert result == {}
