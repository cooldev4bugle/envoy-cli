import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envoy.cmd_tag import tag_group


@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_add_single_tag(runner):
    with patch("envoy.cmd_tag.tag.add_tag") as mock_add:
        result = runner.invoke(tag_group, ["add", "myproject", "dev", "stable"])
        mock_add.assert_called_once_with("myproject", "dev", "stable")
        assert "stable" in result.output
        assert result.exit_code == 0


def test_cmd_add_multiple_tags(runner):
    with patch("envoy.cmd_tag.tag.add_tag") as mock_add:
        result = runner.invoke(tag_group, ["add", "myproject", "dev", "stable", "reviewed"])
        assert mock_add.call_count == 2
        assert result.exit_code == 0


def test_cmd_remove_tag(runner):
    with patch("envoy.cmd_tag.tag.remove_tag") as mock_remove:
        result = runner.invoke(tag_group, ["remove", "myproject", "dev", "stable"])
        mock_remove.assert_called_once_with("myproject", "dev", "stable")
        assert "Removed" in result.output
        assert result.exit_code == 0


def test_cmd_list_tags(runner):
    with patch("envoy.cmd_tag.tag.get_tags", return_value=["stable", "reviewed"]):
        result = runner.invoke(tag_group, ["list", "myproject", "dev"])
        assert "stable" in result.output
        assert "reviewed" in result.output
        assert result.exit_code == 0


def test_cmd_list_no_tags(runner):
    with patch("envoy.cmd_tag.tag.get_tags", return_value=[]):
        result = runner.invoke(tag_group, ["list", "myproject", "dev"])
        assert "No tags" in result.output
        assert result.exit_code == 0


def test_cmd_find_results(runner):
    with patch("envoy.cmd_tag.tag.find_by_tag", return_value=[("proj", "dev"), ("proj", "staging")]):
        result = runner.invoke(tag_group, ["find", "stable"])
        assert "proj" in result.output
        assert "dev" in result.output
        assert result.exit_code == 0


def test_cmd_find_no_results(runner):
    with patch("envoy.cmd_tag.tag.find_by_tag", return_value=[]):
        result = runner.invoke(tag_group, ["find", "nonexistent"])
        assert "No environments" in result.output
        assert result.exit_code == 0
