"""Tests for envoy.cascade."""

from unittest.mock import patch, call
import pytest
from envoy.cascade import cascade_key, cascade_env


DEFAULT_PASS = "secret"


def _patch_vault(pull_side_effect=None, pull_return=None):
    """Return a context manager that patches vault.push and vault.pull."""
    return (
        patch("envoy.cascade.vault.pull", side_effect=pull_side_effect, return_value=pull_return),
        patch("envoy.cascade.vault.push"),
    )


# ---------------------------------------------------------------------------
# cascade_key
# ---------------------------------------------------------------------------

def test_cascade_key_creates_new_key():
    with patch("envoy.cascade.vault.pull", return_value={}) as mock_pull, \
         patch("envoy.cascade.vault.push") as mock_push:
        results = cascade_key("proj", "DB", "postgres", DEFAULT_PASS, "dev", ["staging"])
    assert results["staging"] == "created"
    mock_push.assert_called_once_with("proj", "staging", {"DB": "postgres"}, DEFAULT_PASS)


def test_cascade_key_updates_existing_with_overwrite():
    with patch("envoy.cascade.vault.pull", return_value={"DB": "old"}) as mock_pull, \
         patch("envoy.cascade.vault.push") as mock_push:
        results = cascade_key("proj", "DB", "new", DEFAULT_PASS, "dev", ["staging"], overwrite=True)
    assert results["staging"] == "updated"


def test_cascade_key_skips_existing_without_overwrite():
    with patch("envoy.cascade.vault.pull", return_value={"DB": "old"}), \
         patch("envoy.cascade.vault.push") as mock_push:
        results = cascade_key("proj", "DB", "new", DEFAULT_PASS, "dev", ["staging"])
    assert results["staging"] == "skipped"
    mock_push.assert_not_called()


def test_cascade_key_skips_source_env():
    with patch("envoy.cascade.vault.pull", return_value={}), \
         patch("envoy.cascade.vault.push") as mock_push:
        results = cascade_key("proj", "DB", "v", DEFAULT_PASS, "dev", ["dev", "staging"])
    assert results["dev"] == "skipped (source)"
    assert results["staging"] == "created"


def test_cascade_key_handles_missing_target_env():
    """If vault.pull raises KeyError the env is treated as empty."""
    with patch("envoy.cascade.vault.pull", side_effect=KeyError), \
         patch("envoy.cascade.vault.push") as mock_push:
        results = cascade_key("proj", "DB", "v", DEFAULT_PASS, "dev", ["prod"])
    assert results["prod"] == "created"


# ---------------------------------------------------------------------------
# cascade_env
# ---------------------------------------------------------------------------

def test_cascade_env_propagates_all_keys():
    source = {"A": "1", "B": "2"}
    with patch("envoy.cascade.vault.pull", side_effect=[source, {}, {}]), \
         patch("envoy.cascade.vault.push"):
        results = cascade_env("proj", "dev", ["staging", "prod"], DEFAULT_PASS)
    assert set(results["staging"].keys()) == {"A", "B"}
    assert set(results["prod"].keys()) == {"A", "B"}


def test_cascade_env_limits_to_selected_keys():
    source = {"A": "1", "B": "2", "C": "3"}
    with patch("envoy.cascade.vault.pull", side_effect=[source, {}, {}]), \
         patch("envoy.cascade.vault.push"):
        results = cascade_env("proj", "dev", ["staging"], DEFAULT_PASS, keys=["A", "C"])
    assert "B" not in results["staging"]
    assert "A" in results["staging"]
    assert "C" in results["staging"]
