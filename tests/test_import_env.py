"""Tests for envoy/import_env.py"""
import json
import os
import pytest
from envoy.import_env import from_shell, from_json, from_docker_env, merge_into


def test_from_shell_all(monkeypatch):
    monkeypatch.setenv("TEST_FOO", "bar")
    result = from_shell()
    assert "TEST_FOO" in result
    assert result["TEST_FOO"] == "bar"


def test_from_shell_filter_keys(monkeypatch):
    monkeypatch.setenv("TEST_A", "1")
    monkeypatch.setenv("TEST_B", "2")
    result = from_shell(["TEST_A"])
    assert "TEST_A" in result
    assert "TEST_B" not in result


def test_from_shell_missing_key_ignored(monkeypatch):
    result = from_shell(["DEFINITELY_NOT_SET_XYZ"])
    assert result == {}


def test_from_json_basic(tmp_path):
    data = {"KEY1": "val1", "KEY2": "val2"}
    f = tmp_path / "vars.json"
    f.write_text(json.dumps(data))
    result = from_json(str(f))
    assert result == {"KEY1": "val1", "KEY2": "val2"}


def test_from_json_non_dict_raises(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps(["a", "b"]))
    with pytest.raises(ValueError):
        from_json(str(f))


def test_from_docker_env_basic(tmp_path):
    content = "# comment\nFOO=bar\nBAZ=qux\n"
    f = tmp_path / "docker.env"
    f.write_text(content)
    result = from_docker_env(str(f))
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_from_docker_env_ignores_blank_and_comments(tmp_path):
    content = "\n# skip\nKEY=value\n"
    f = tmp_path / "d.env"
    f.write_text(content)
    result = from_docker_env(str(f))
    assert list(result.keys()) == ["KEY"]


def test_merge_into_no_overwrite():
    existing = {"A": "1", "B": "2"}
    incoming = {"B": "99", "C": "3"}
    result = merge_into(existing, incoming, overwrite=False)
    assert result["B"] == "2"
    assert result["C"] == "3"


def test_merge_into_with_overwrite():
    existing = {"A": "1", "B": "2"}
    incoming = {"B": "99", "C": "3"}
    result = merge_into(existing, incoming, overwrite=True)
    assert result["B"] == "99"
    assert result["C"] == "3"
