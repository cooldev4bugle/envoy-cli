import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envoy.cmd_export import export_group

SAMPLE_DATA = {"API_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, subcmd, extra_args=None, passphrase="secret"):
    args = [subcmd, "myproject", "production", "--passphrase", passphrase]
    if extra_args:
        args.extend(extra_args)
    return runner.invoke(export_group, args)


@patch("envoy.cmd_export.vault.pull", return_value=SAMPLE_DATA)
def test_cmd_shell_outputs_exports(mock_pull, runner):
    result = _invoke(runner, "shell")
    assert result.exit_code == 0
    assert "export API_KEY=" in result.output
    assert "export DEBUG=" in result.output
    mock_pull.assert_called_once_with("myproject", "production", "secret")


@patch("envoy.cmd_export.vault.pull", return_value=SAMPLE_DATA)
def test_cmd_docker_outputs_env_file_format(mock_pull, runner):
    result = _invoke(runner, "docker")
    assert result.exit_code == 0
    assert "API_KEY=abc123" in result.output
    assert "DEBUG=true" in result.output


@patch("envoy.cmd_export.vault.pull", return_value=SAMPLE_DATA)
def test_cmd_json_outputs_valid_json(mock_pull, runner):
    import json
    result = _invoke(runner, "json")
    assert result.exit_code == 0
    parsed = json.loads(result.output.strip())
    assert parsed["API_KEY"] == "abc123"
    assert parsed["DEBUG"] == "true"


@patch("envoy.cmd_export.vault.pull", return_value=SAMPLE_DATA)
def test_cmd_dotenv_outputs_dotenv_format(mock_pull, runner):
    result = _invoke(runner, "dotenv")
    assert result.exit_code == 0
    assert "API_KEY=" in result.output
    assert "DEBUG=" in result.output


@patch("envoy.cmd_export.vault.pull", return_value=SAMPLE_DATA)
def test_cmd_shell_writes_to_file(mock_pull, runner, tmp_path):
    out_file = tmp_path / "env.sh"
    result = _invoke(runner, "shell", ["--output", str(out_file)])
    assert result.exit_code == 0
    assert f"Written to {out_file}" in result.output
    content = out_file.read_text()
    assert "export API_KEY=" in content


@patch("envoy.cmd_export.vault.pull", return_value=SAMPLE_DATA)
def test_cmd_json_writes_to_file(mock_pull, runner, tmp_path):
    import json
    out_file = tmp_path / "env.json"
    result = _invoke(runner, "json", ["--output", str(out_file)])
    assert result.exit_code == 0
    parsed = json.loads(out_file.read_text())
    assert parsed["API_KEY"] == "abc123"
