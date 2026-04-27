"""Tests for envoy.cmd_immutable CLI commands."""

import pytest
from click.testing import CliRunner

from envoy.cmd_immutable import immutable_group
from envoy import immutable as imm


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.immutable._immutable_path", lambda: tmp_path / "immutable.json")
    yield tmp_path


def test_cmd_add_marks_key(runner):
    result = runner.invoke(immutable_group, ["add", "myapp", "prod", "API_KEY"])
    assert result.exit_code == 0
    assert "marked as immutable" in result.output
    assert imm.is_immutable("myapp", "prod", "API_KEY")


def test_cmd_add_with_reason(runner):
    result = runner.invoke(
        immutable_group, ["add", "myapp", "prod", "API_KEY", "--reason", "critical"]
    )
    assert result.exit_code == 0
    assert "critical" in result.output


def test_cmd_remove_existing(runner):
    imm.mark_immutable("myapp", "prod", "API_KEY")
    result = runner.invoke(immutable_group, ["remove", "myapp", "prod", "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output
    assert not imm.is_immutable("myapp", "prod", "API_KEY")


def test_cmd_remove_not_found(runner):
    result = runner.invoke(immutable_group, ["remove", "myapp", "prod", "GHOST"])
    assert result.exit_code == 0
    assert "not marked immutable" in result.output


def test_cmd_list_no_keys(runner):
    result = runner.invoke(immutable_group, ["list", "myapp", "prod"])
    assert result.exit_code == 0
    assert "No immutable keys" in result.output


def test_cmd_list_shows_keys(runner):
    imm.mark_immutable("myapp", "prod", "SECRET", reason="never change")
    result = runner.invoke(immutable_group, ["list", "myapp", "prod"])
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "never change" in result.output


def test_cmd_check_immutable(runner):
    imm.mark_immutable("myapp", "prod", "KEY")
    result = runner.invoke(immutable_group, ["check", "myapp", "prod", "KEY"])
    assert result.exit_code == 0
    assert "IMMUTABLE" in result.output


def test_cmd_check_mutable(runner):
    result = runner.invoke(immutable_group, ["check", "myapp", "prod", "KEY"])
    assert result.exit_code == 0
    assert "mutable" in result.output
