"""Tests for envoy.compare."""
import pytest
from unittest.mock import patch
from envoy.compare import compare_envs, missing_keys, extra_keys, summary


ENV_A = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "DEBUG": "false"}


def _patch_pull(a, b):
    def _pull(project, env, passphrase):
        return a if env == "dev" else b
    return patch("envoy.compare.vault.pull", side_effect=_pull)


def test_compare_envs_detects_differences():
    with _patch_pull(ENV_A, ENV_B):
        diff = compare_envs("myapp", "dev", "prod", "pass")
    assert "HOST" in diff
    assert diff["HOST"] == ("localhost", "prod.example.com")


def test_compare_envs_ignores_equal_keys():
    with _patch_pull(ENV_A, ENV_B):
        diff = compare_envs("myapp", "dev", "prod", "pass")
    assert "PORT" not in diff


def test_compare_envs_missing_key_in_b():
    with _patch_pull(ENV_A, ENV_B):
        diff = compare_envs("myapp", "dev", "prod", "pass")
    assert "SECRET" in diff
    assert diff["SECRET"] == ("abc", None)


def test_compare_envs_extra_key_in_b():
    with _patch_pull(ENV_A, ENV_B):
        diff = compare_envs("myapp", "dev", "prod", "pass")
    assert "DEBUG" in diff
    assert diff["DEBUG"] == (None, "false")


def test_compare_envs_identical():
    with patch("envoy.compare.vault.pull", return_value={"K": "V"}):
        diff = compare_envs("myapp", "dev", "staging", "pass")
    assert diff == {}


def test_missing_keys():
    assert missing_keys(ENV_A, ENV_B) == ["SECRET"]


def test_extra_keys():
    assert extra_keys(ENV_A, ENV_B) == ["DEBUG"]


def test_summary():
    with _patch_pull(ENV_A, ENV_B):
        diff = compare_envs("myapp", "dev", "prod", "pass")
    s = summary(diff)
    assert s["changed"] == 1
    assert s["only_in_a"] == 1
    assert s["only_in_b"] == 1
