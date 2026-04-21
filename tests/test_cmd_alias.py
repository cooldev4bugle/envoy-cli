import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_alias import alias_group


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_set_alias(runner):
    with patch("envoy.cmd_alias.set_alias") as mock_set:
        result = runner.invoke(alias_group, ["set", "prod", "myapp", "production"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "myapp/production" in result.output
    mock_set.assert_called_once_with("prod", "myapp", "production")


def test_cmd_remove_existing(runner):
    with patch("envoy.cmd_alias.remove_alias", return_value=True):
        result = runner.invoke(alias_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cmd_remove_missing(runner):
    with patch("envoy.cmd_alias.remove_alias", return_value=False):
        result = runner.invoke(alias_group, ["remove", "ghost"])
    assert "not found" in result.output


def test_cmd_resolve_found(runner):
    with patch("envoy.cmd_alias.resolve_alias", return_value=("myapp", "production")):
        result = runner.invoke(alias_group, ["resolve", "prod"])
    assert result.exit_code == 0
    assert "myapp/production" in result.output


def test_cmd_resolve_not_found(runner):
    with patch("envoy.cmd_alias.resolve_alias", return_value=None):
        result = runner.invoke(alias_group, ["resolve", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_cmd_list_empty(runner):
    with patch("envoy.cmd_alias.list_aliases", return_value={}):
        result = runner.invoke(alias_group, ["list"])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_cmd_list_with_entries(runner):
    aliases = {
        "prod": ("myapp", "production"),
        "dev": ("myapp", "development"),
    }
    with patch("envoy.cmd_alias.list_aliases", return_value=aliases):
        result = runner.invoke(alias_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "myapp/production" in result.output
    assert "dev" in result.output
    assert "myapp/development" in result.output
