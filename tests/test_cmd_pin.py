"""Tests for envoy.cmd_pin CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.cmd_pin import pin_group
from envoy import pin as pin_module


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(pin_module, "get_store_dir", lambda: tmp_path)


def test_cmd_add_single_key(runner):
    result = runner.invoke(pin_group, ["add", "myapp", "prod", "DB_PASS"])
    assert result.exit_code == 0
    assert "Pinned 'DB_PASS'" in result.output
    assert pin_module.is_pinned("myapp", "prod", "DB_PASS")


def test_cmd_add_multiple_keys(runner):
    result = runner.invoke(pin_group, ["add", "myapp", "prod", "KEY1", "KEY2"])
    assert result.exit_code == 0
    assert "Pinned 'KEY1'" in result.output
    assert "Pinned 'KEY2'" in result.output


def test_cmd_remove_key(runner):
    pin_module.pin_key("myapp", "prod", "TOKEN")
    result = runner.invoke(pin_group, ["remove", "myapp", "prod", "TOKEN"])
    assert result.exit_code == 0
    assert "Unpinned 'TOKEN'" in result.output
    assert not pin_module.is_pinned("myapp", "prod", "TOKEN")


def test_cmd_list_no_pins(runner):
    result = runner.invoke(pin_group, ["list", "myapp", "dev"])
    assert result.exit_code == 0
    assert "No pinned keys" in result.output


def test_cmd_list_shows_pins(runner):
    pin_module.pin_key("myapp", "dev", "SECRET")
    pin_module.pin_key("myapp", "dev", "API_KEY")
    result = runner.invoke(pin_group, ["list", "myapp", "dev"])
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "API_KEY" in result.output
