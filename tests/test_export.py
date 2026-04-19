import json
import pytest
from envoy.export import export, to_shell, to_docker, to_json, to_dotenv


SAMPLE = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "abc123",
    "DATABASE_URL": "postgres://user:pass@localhost/db",
    "GREETING": 'say "hello"',
}


def test_to_shell_basic():
    result = to_shell({"FOO": "bar"})
    assert result == 'export FOO="bar"'


def test_to_shell_escapes_quotes():
    result = to_shell({"MSG": 'say "hi"'})
    assert '\\"' in result


def test_to_shell_multiple_keys():
    result = to_shell({"A": "1", "B": "2"})
    lines = result.splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("export A=")


def test_to_docker_format():
    result = to_docker({"FOO": "bar"})
    assert result.startswith("--env FOO=")


def test_to_docker_multiple_keys():
    result = to_docker({"A": "1", "B": "2"})
    assert "--env A=" in result
    assert "--env B=" in result


def test_to_json_valid():
    result = to_json({"KEY": "value"})
    parsed = json.loads(result)
    assert parsed["KEY"] == "value"


def test_to_dotenv_simple_value():
    result = to_dotenv({"FOO": "bar"})
    assert result == "FOO=bar"


def test_to_dotenv_quotes_value_with_spaces():
    result = to_dotenv({"MSG": "hello world"})
    assert result == 'MSG="hello world"'


def test_export_dispatches_correctly():
    result = export({"X": "1"}, "json")
    assert json.loads(result)["X"] == "1"


def test_export_unknown_format_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        export({"X": "1"}, "xml")


def test_export_shell_roundtrip_keys():
    result = export(SAMPLE, "shell")
    for key in SAMPLE:
        assert key in result
