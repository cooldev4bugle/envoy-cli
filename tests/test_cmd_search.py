import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_search import search_group


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_key_finds_matches(runner):
    with patch("envoy.cmd_search.search.search_by_key", return_value={"DB_HOST": "localhost"}):
        result = runner.invoke(search_group, ["key", "proj", "dev", "DB", "--passphrase", "secret"])
        assert "DB_HOST=localhost" in result.output
        assert result.exit_code == 0


def test_cmd_key_no_matches(runner):
    with patch("envoy.cmd_search.search.search_by_key", return_value={}):
        result = runner.invoke(search_group, ["key", "proj", "dev", "MISSING", "--passphrase", "secret"])
        assert "No matching keys" in result.output
        assert result.exit_code == 0


def test_cmd_value_finds_matches(runner):
    with patch("envoy.cmd_search.search.search_by_value", return_value={"API_URL": "https://example.com"}):
        result = runner.invoke(search_group, ["value", "proj", "dev", "example", "--passphrase", "secret"])
        assert "API_URL=https://example.com" in result.output
        assert result.exit_code == 0


def test_cmd_value_no_matches(runner):
    with patch("envoy.cmd_search.search.search_by_value", return_value={}):
        result = runner.invoke(search_group, ["value", "proj", "dev", "nope", "--passphrase", "secret"])
        assert "No matching values" in result.output
        assert result.exit_code == 0


def test_cmd_global_finds_results(runner):
    with patch("envoy.cmd_search.search.search_key_across_projects",
               return_value=[("proj", "dev", "val1"), ("proj2", "staging", "val2")]):
        result = runner.invoke(search_group, ["global", "MY_KEY", "--passphrase", "secret"])
        assert "proj" in result.output
        assert "MY_KEY=val1" in result.output
        assert result.exit_code == 0


def test_cmd_global_no_results(runner):
    with patch("envoy.cmd_search.search.search_key_across_projects", return_value=[]):
        result = runner.invoke(search_group, ["global", "GHOST", "--passphrase", "secret"])
        assert "not found" in result.output
        assert result.exit_code == 0
