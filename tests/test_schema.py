import pytest
from unittest.mock import patch
from envoy.schema import set_rule, remove_rule, get_rules, validate


STORE_DIR = None


@pytest.fixture(autouse=True)
def tmp_store(tmp_path):
    with patch("envoy.schema.get_store_dir", return_value=tmp_path):
        yield tmp_path


def test_set_and_get_rule():
    set_rule("myapp", "DATABASE_URL", required=True, pattern=r"postgres://.+")
    rules = get_rules("myapp")
    assert "DATABASE_URL" in rules
    assert rules["DATABASE_URL"]["required"] is True
    assert rules["DATABASE_URL"]["pattern"] == r"postgres://.+"


def test_set_rule_defaults():
    set_rule("myapp", "OPTIONAL_KEY")
    rules = get_rules("myapp")
    assert rules["OPTIONAL_KEY"]["required"] is False
    assert rules["OPTIONAL_KEY"]["pattern"] is None


def test_remove_rule_existing():
    set_rule("myapp", "SECRET")
    removed = remove_rule("myapp", "SECRET")
    assert removed is True
    assert "SECRET" not in get_rules("myapp")


def test_remove_rule_missing():
    removed = remove_rule("myapp", "NONEXISTENT")
    assert removed is False


def test_validate_passes_when_no_rules():
    errors = validate("myapp", {"FOO": "bar"})
    assert errors == []


def test_validate_catches_missing_required():
    set_rule("myapp", "API_KEY", required=True)
    errors = validate("myapp", {})
    assert any("API_KEY" in e for e in errors)


def test_validate_passes_required_key_present():
    set_rule("myapp", "API_KEY", required=True)
    errors = validate("myapp", {"API_KEY": "abc123"})
    assert errors == []


def test_validate_pattern_match():
    set_rule("myapp", "PORT", pattern=r"\d+")
    errors = validate("myapp", {"PORT": "8080"})
    assert errors == []


def test_validate_pattern_mismatch():
    set_rule("myapp", "PORT", pattern=r"\d+")
    errors = validate("myapp", {"PORT": "not-a-number"})
    assert any("PORT" in e for e in errors)


def test_validate_multiple_errors():
    set_rule("myapp", "DB", required=True)
    set_rule("myapp", "PORT", pattern=r"\d+")
    errors = validate("myapp", {"PORT": "abc"})
    assert len(errors) == 2
