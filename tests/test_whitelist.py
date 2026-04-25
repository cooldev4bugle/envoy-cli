"""Tests for envoy.whitelist."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envoy import whitelist as wl
from envoy.cmd_whitelist import whitelist_group


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.whitelist.get_store_dir", lambda: tmp_path)


def test_add_key_creates_entry():
    wl.add_key("myapp", "prod", "DATABASE_URL")
    assert "DATABASE_URL" in wl.get_keys("myapp", "prod")


def test_add_key_no_duplicates():
    wl.add_key("myapp", "prod", "SECRET_KEY")
    wl.add_key("myapp", "prod", "SECRET_KEY")
    assert wl.get_keys("myapp", "prod").count("SECRET_KEY") == 1


def test_add_multiple_keys():
    wl.add_key("myapp", "staging", "A")
    wl.add_key("myapp", "staging", "B")
    keys = wl.get_keys("myapp", "staging")
    assert "A" in keys and "B" in keys


def test_remove_key_returns_true_when_exists():
    wl.add_key("myapp", "prod", "REMOVE_ME")
    assert wl.remove_key("myapp", "prod", "REMOVE_ME") is True
    assert "REMOVE_ME" not in wl.get_keys("myapp", "prod")


def test_remove_key_returns_false_when_missing():
    assert wl.remove_key("myapp", "prod", "GHOST") is False


def test_get_keys_returns_empty_when_unset():
    assert wl.get_keys("unknown", "env") == []


def test_clear_removes_all_keys():
    wl.add_key("myapp", "dev", "X")
    wl.add_key("myapp", "dev", "Y")
    wl.clear("myapp", "dev")
    assert wl.get_keys("myapp", "dev") == []


def test_filter_env_returns_only_whitelisted():
    wl.add_key("myapp", "prod", "ALLOWED")
    result = wl.filter_env("myapp", "prod", {"ALLOWED": "yes", "BLOCKED": "no"})
    assert result == {"ALLOWED": "yes"}


def test_filter_env_no_whitelist_returns_all():
    variables = {"A": "1", "B": "2"}
    result = wl.filter_env("noapp", "env", variables)
    assert result == variables


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_add_single_key(runner):
    result = runner.invoke(whitelist_group, ["add", "myapp", "prod", "API_KEY"])
    assert result.exit_code == 0
    assert "1 key(s)" in result.output


def test_cmd_list_shows_keys(runner):
    wl.add_key("myapp", "prod", "DB_URL")
    result = runner.invoke(whitelist_group, ["list", "myapp", "prod"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_cmd_list_empty(runner):
    result = runner.invoke(whitelist_group, ["list", "ghost", "env"])
    assert result.exit_code == 0
    assert "all keys are allowed" in result.output


def test_cmd_remove_existing(runner):
    wl.add_key("myapp", "prod", "TO_REMOVE")
    result = runner.invoke(whitelist_group, ["remove", "myapp", "prod", "TO_REMOVE"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cmd_remove_missing(runner):
    result = runner.invoke(whitelist_group, ["remove", "myapp", "prod", "GHOST"])
    assert result.exit_code == 0
    assert "not in the whitelist" in result.output
