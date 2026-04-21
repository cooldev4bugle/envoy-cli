import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envoy.cmd_ttl import ttl_group


@pytest.fixture
def runner():
    return CliRunner()


def _entry(key="API_KEY", seconds=3600, set_at="2024-01-01T00:00:00"):
    return {"key": key, "seconds": seconds, "set_at": set_at}


def test_cmd_set_success(runner):
    with patch("envoy.cmd_ttl.ttl_mod.set_ttl") as mock_set:
        result = runner.invoke(ttl_group, ["set", "myapp", "prod", "API_KEY", "3600"])
    assert result.exit_code == 0
    assert "TTL set" in result.output
    assert "myapp/prod/API_KEY" in result.output
    mock_set.assert_called_once_with("myapp", "prod", "API_KEY", 3600)


def test_cmd_set_invalid_seconds_shows_error(runner):
    with patch("envoy.cmd_ttl.ttl_mod.set_ttl", side_effect=ValueError("seconds must be > 0")):
        result = runner.invoke(ttl_group, ["set", "myapp", "prod", "API_KEY", "0"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cmd_get_existing_entry(runner):
    entry = _entry()
    with patch("envoy.cmd_ttl.ttl_mod.get_ttl", return_value=entry):
        result = runner.invoke(ttl_group, ["get", "myapp", "prod", "API_KEY"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "3600" in result.output


def test_cmd_get_missing_entry(runner):
    with patch("envoy.cmd_ttl.ttl_mod.get_ttl", return_value=None):
        result = runner.invoke(ttl_group, ["get", "myapp", "prod", "MISSING"])
    assert result.exit_code == 0
    assert "No TTL set" in result.output


def test_cmd_remove_existing(runner):
    with patch("envoy.cmd_ttl.ttl_mod.remove_ttl", return_value=True):
        result = runner.invoke(ttl_group, ["remove", "myapp", "prod", "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cmd_remove_not_found(runner):
    with patch("envoy.cmd_ttl.ttl_mod.remove_ttl", return_value=False):
        result = runner.invoke(ttl_group, ["remove", "myapp", "prod", "GHOST"])
    assert result.exit_code == 0
    assert "No TTL found" in result.output


def test_cmd_list_with_entries(runner):
    entries = [_entry("API_KEY"), _entry("DB_PASS", seconds=60)]
    with patch("envoy.cmd_ttl.ttl_mod.list_ttls", return_value=entries):
        result = runner.invoke(ttl_group, ["list", "myapp", "prod"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_PASS" in result.output


def test_cmd_list_empty(runner):
    with patch("envoy.cmd_ttl.ttl_mod.list_ttls", return_value=[]):
        result = runner.invoke(ttl_group, ["list", "myapp", "prod"])
    assert result.exit_code == 0
    assert "No TTL entries" in result.output


def test_cmd_expired_with_entries(runner):
    entries = [_entry("OLD_KEY", seconds=10)]
    with patch("envoy.cmd_ttl.ttl_mod.get_expired", return_value=entries):
        result = runner.invoke(ttl_group, ["expired", "myapp", "prod"])
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output
    assert "expired" in result.output


def test_cmd_expired_none(runner):
    with patch("envoy.cmd_ttl.ttl_mod.get_expired", return_value=[]):
        result = runner.invoke(ttl_group, ["expired", "myapp", "prod"])
    assert result.exit_code == 0
    assert "No expired keys" in result.output
