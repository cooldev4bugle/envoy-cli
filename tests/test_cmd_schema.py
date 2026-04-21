import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envoy.cmd_schema import schema_group


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_set_rule(runner):
    with patch("envoy.cmd_schema.set_rule") as mock_set:
        result = runner.invoke(schema_group, ["set", "myapp", "API_KEY", "--required", "--pattern", r"\w+"])
        assert result.exit_code == 0
        assert "Rule set" in result.output
        mock_set.assert_called_once_with("myapp", "API_KEY", required=True, pattern=r"\w+", description="")


def test_cmd_remove_existing(runner):
    with patch("envoy.cmd_schema.remove_rule", return_value=True):
        result = runner.invoke(schema_group, ["remove", "myapp", "API_KEY"])
        assert result.exit_code == 0
        assert "removed" in result.output


def test_cmd_remove_missing(runner):
    with patch("envoy.cmd_schema.remove_rule", return_value=False):
        result = runner.invoke(schema_group, ["remove", "myapp", "GHOST"])
        assert result.exit_code == 0
        assert "No rule found" in result.output


def test_cmd_list_no_rules(runner):
    with patch("envoy.cmd_schema.get_rules", return_value={}):
        result = runner.invoke(schema_group, ["list", "myapp"])
        assert result.exit_code == 0
        assert "No rules" in result.output


def test_cmd_list_shows_rules(runner):
    rules = {"DB_URL": {"required": True, "pattern": "postgres://.+", "description": "db"}}
    with patch("envoy.cmd_schema.get_rules", return_value=rules):
        result = runner.invoke(schema_group, ["list", "myapp"])
        assert "DB_URL" in result.output
        assert "required" in result.output


def test_cmd_validate_passes(runner):
    with patch("envoy.cmd_schema.pull", return_value={"KEY": "val"}), \
         patch("envoy.cmd_schema.validate", return_value=[]):
        result = runner.invoke(schema_group, ["validate", "myapp", "prod", "--passphrase", "secret"])
        assert result.exit_code == 0
        assert "passed" in result.output


def test_cmd_validate_fails(runner):
    with patch("envoy.cmd_schema.pull", return_value={}), \
         patch("envoy.cmd_schema.validate", return_value=["Missing required key: DB_URL"]):
        result = runner.invoke(schema_group, ["validate", "myapp", "prod", "--passphrase", "secret"])
        assert result.exit_code == 1
        assert "DB_URL" in result.output
