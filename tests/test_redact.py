"""Tests for envoy.redact."""

import pytest
from envoy.redact import (
    REDACT_PLACEHOLDER,
    is_sensitive,
    redact_env,
    redact_value,
    visible_keys,
)


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "PASSWORD", "db_password", "API_KEY", "api-key",
    "SECRET", "my_secret", "AUTH_TOKEN", "private_key",
    "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "CREDENTIALS",
])
def test_is_sensitive_matches_common_keys(key):
    assert is_sensitive(key) is True


@pytest.mark.parametrize("key", [
    "DATABASE_URL", "PORT", "HOST", "DEBUG", "APP_NAME",
])
def test_is_sensitive_ignores_non_sensitive_keys(key):
    assert is_sensitive(key) is False


def test_is_sensitive_with_extra_pattern():
    assert is_sensitive("MY_CUSTOM_FIELD", extra_patterns=[r".*custom.*"]) is True


def test_is_sensitive_extra_pattern_does_not_affect_unrelated():
    assert is_sensitive("PORT", extra_patterns=[r".*custom.*"]) is False


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_masks_sensitive():
    assert redact_value("API_KEY", "abc123") == REDACT_PLACEHOLDER


def test_redact_value_keeps_non_sensitive():
    assert redact_value("PORT", "8080") == "8080"


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_env_masks_sensitive_keys():
    env = {"API_KEY": "secret", "HOST": "localhost", "DB_PASSWORD": "pass"}
    result = redact_env(env)
    assert result["API_KEY"] == REDACT_PLACEHOLDER
    assert result["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result["HOST"] == "localhost"


def test_redact_env_reveal_keys_bypass_redaction():
    env = {"API_KEY": "mykey", "HOST": "localhost"}
    result = redact_env(env, reveal_keys=["API_KEY"])
    assert result["API_KEY"] == "mykey"


def test_redact_env_returns_copy():
    env = {"PORT": "3000"}
    result = redact_env(env)
    result["PORT"] = "changed"
    assert env["PORT"] == "3000"


def test_redact_env_empty():
    assert redact_env({}) == {}


# ---------------------------------------------------------------------------
# visible_keys
# ---------------------------------------------------------------------------

def test_visible_keys_excludes_sensitive():
    env = {"API_KEY": "x", "HOST": "h", "PORT": "80", "SECRET": "s"}
    assert visible_keys(env) == ["HOST", "PORT"]


def test_visible_keys_all_sensitive_returns_empty():
    env = {"API_KEY": "x", "PASSWORD": "p"}
    assert visible_keys(env) == []


def test_visible_keys_sorted():
    env = {"ZEBRA": "z", "ALPHA": "a", "TOKEN": "t"}
    keys = visible_keys(env)
    assert keys == sorted(keys)
    assert "TOKEN" not in keys
