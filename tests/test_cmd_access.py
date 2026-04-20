"""Tests for envoy/cmd_access.py."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.cmd_access import access_group
from envoy import access as ac


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.access.get_store_dir", lambda: tmp_path)
    return tmp_path


def test_cmd_grant_success(runner):
    result = runner.invoke(access_group, ["grant", "myapp", "prod", "alice"])
    assert result.exit_code == 0
    assert "Granted" in result.output
    assert ac.is_allowed("myapp", "prod", "alice")


def test_cmd_revoke_existing_user(runner):
    ac.grant("myapp", "prod", "alice")
    result = runner.invoke(access_group, ["revoke", "myapp", "prod", "alice"])
    assert result.exit_code == 0
    assert "Revoked" in result.output


def test_cmd_revoke_missing_user(runner):
    result = runner.invoke(access_group, ["revoke", "myapp", "prod", "ghost"])
    assert result.exit_code == 0
    assert "did not have access" in result.output


def test_cmd_check_allowed(runner):
    ac.grant("myapp", "staging", "bob")
    result = runner.invoke(access_group, ["check", "myapp", "staging", "bob"])
    assert result.exit_code == 0
    assert "has access" in result.output


def test_cmd_check_not_allowed(runner):
    result = runner.invoke(access_group, ["check", "myapp", "staging", "nobody"])
    assert result.exit_code == 0
    assert "does NOT have access" in result.output


def test_cmd_list_no_rules(runner):
    result = runner.invoke(access_group, ["list", "myapp"])
    assert result.exit_code == 0
    assert "No access rules" in result.output


def test_cmd_list_shows_users(runner):
    ac.grant("myapp", "dev", "alice")
    result = runner.invoke(access_group, ["list", "myapp"])
    assert result.exit_code == 0
    assert "alice" in result.output


def test_cmd_clear_confirmed(runner):
    ac.grant("myapp", "dev", "alice")
    result = runner.invoke(access_group, ["clear", "myapp", "dev"], input="y\n")
    assert result.exit_code == 0
    assert "Cleared" in result.output
    assert not ac.is_allowed("myapp", "dev", "alice")
