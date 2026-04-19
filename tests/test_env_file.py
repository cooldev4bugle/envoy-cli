"""Tests for envoy.env_file module."""

import pytest
from pathlib import Path
from envoy.env_file import parse, serialize, read, write


SAMPLE_CONTENT = """
# This is a comment
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD="p@ss w0rd"
API_KEY='mykey'
EMPTY_VAR=
"""


def test_parse_basic():
    result = parse(SAMPLE_CONTENT)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_parse_strips_quotes():
    result = parse(SAMPLE_CONTENT)
    assert result["DB_PASSWORD"] == "p@ss w0rd"
    assert result["API_KEY"] == "mykey"


def test_parse_ignores_comments():
    result = parse(SAMPLE_CONTENT)
    assert not any(k.startswith("#") for k in result)


def test_parse_empty_value():
    result = parse(SAMPLE_CONTENT)
    assert result["EMPTY_VAR"] == ""


def test_serialize_roundtrip():
    original = {"FOO": "bar", "BAZ": "qux"}
    content = serialize(original)
    parsed = parse(content)
    assert parsed == original


def test_serialize_quotes_values_with_spaces():
    content = serialize({"KEY": "hello world"})
    assert '"hello world"' in content


def test_read_write_roundtrip(tmp_path: Path):
    env_path = tmp_path / ".env"
    original = {"SECRET": "abc123", "HOST": "example.com"}
    write(env_path, original)
    loaded = read(env_path)
    assert loaded == original
