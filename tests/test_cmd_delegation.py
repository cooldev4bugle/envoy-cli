"""Tests for envoy.cmd_delegation CLI commands."""

import pytest
from click.testing import CliRunner

from envoy import delegation
from envoy.cmd_delegation import delegation_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(delegation, "get_store_dir", lambda: tmp_path)


def test_cmd_grant_success(runner):
    result = runner.invoke(delegation_group, ["grant", "alice", "bob", "myapp", "prod"])
    assert result.exit_code == 0
    assert "bob" in result.output
    assert "alice" in result.output


def test_cmd_grant_custom_permissions(runner):
    result = runner.invoke(
        delegation_group,
        ["grant", "alice", "bob", "myapp", "prod", "-p", "read", "-p", "write"],
    )
    assert result.exit_code == 0
    assert "read" in result.output
    assert "write" in result.output


def test_cmd_revoke_existing(runner):
    delegation.grant_delegation("alice", "bob", "myapp", "prod")
    result = runner.invoke(delegation_group, ["revoke", "alice", "bob", "myapp", "prod"])
    assert result.exit_code == 0
    assert "Revoked" in result.output


def test_cmd_revoke_not_found(runner):
    result = runner.invoke(delegation_group, ["revoke", "alice", "ghost", "myapp", "prod"])
    assert result.exit_code == 0
    assert "No delegation found" in result.output


def test_cmd_list_shows_delegates(runner):
    delegation.grant_delegation("alice", "bob", "myapp", "prod", ["read"])
    result = runner.invoke(delegation_group, ["list", "alice", "myapp", "prod"])
    assert result.exit_code == 0
    assert "bob" in result.output


def test_cmd_list_no_delegates(runner):
    result = runner.invoke(delegation_group, ["list", "alice", "myapp", "prod"])
    assert result.exit_code == 0
    assert "No delegates" in result.output


def test_cmd_check_allowed(runner):
    delegation.grant_delegation("alice", "bob", "myapp", "prod", ["push"])
    result = runner.invoke(delegation_group, ["check", "alice", "bob", "myapp", "prod", "push"])
    assert result.exit_code == 0
    assert "CAN" in result.output


def test_cmd_check_not_allowed(runner):
    delegation.grant_delegation("alice", "bob", "myapp", "prod", ["read"])
    result = runner.invoke(delegation_group, ["check", "alice", "bob", "myapp", "prod", "delete"])
    assert result.exit_code == 0
    assert "CANNOT" in result.output
