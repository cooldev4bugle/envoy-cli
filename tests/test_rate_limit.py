"""Tests for envoy.rate_limit."""

import time
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from envoy.rate_limit import (
    check_rate_limit,
    get_limit,
    record_operation,
    reset_limit,
    set_limit,
)
from envoy.cmd_rate_limit import rate_limit_group


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.rate_limit.get_store_dir", lambda: tmp_path)


# --- unit tests ---

def test_get_limit_returns_defaults_when_unset():
    cfg = get_limit("myproject")
    assert cfg["limit"] == 60
    assert cfg["window"] == 3600


def test_set_and_get_limit():
    set_limit("myproject", limit=10, window=60)
    cfg = get_limit("myproject")
    assert cfg["limit"] == 10
    assert cfg["window"] == 60


def test_set_limit_raises_on_zero_limit():
    with pytest.raises(ValueError, match="limit"):
        set_limit("p", limit=0)


def test_set_limit_raises_on_negative_window():
    with pytest.raises(ValueError, match="window"):
        set_limit("p", limit=5, window=-1)


def test_check_rate_limit_allows_within_quota():
    set_limit("proj", limit=5, window=60)
    for _ in range(3):
        record_operation("proj", "dev")
    allowed, remaining = check_rate_limit("proj", "dev")
    assert allowed is True
    assert remaining == 2


def test_check_rate_limit_blocks_when_exceeded():
    set_limit("proj", limit=3, window=60)
    for _ in range(3):
        record_operation("proj", "dev")
    allowed, remaining = check_rate_limit("proj", "dev")
    assert allowed is False
    assert remaining == 0


def test_reset_limit_clears_all_ops():
    set_limit("proj", limit=3, window=60)
    for _ in range(3):
        record_operation("proj", "dev")
    reset_limit("proj")
    allowed, remaining = check_rate_limit("proj", "dev")
    assert allowed is True
    assert remaining == 3


def test_reset_limit_scoped_to_env():
    set_limit("proj", limit=3, window=60)
    for _ in range(3):
        record_operation("proj", "dev")
    record_operation("proj", "prod")
    reset_limit("proj", env="dev")
    _, remaining_dev = check_rate_limit("proj", "dev")
    _, remaining_prod = check_rate_limit("proj", "prod")
    assert remaining_dev == 3
    assert remaining_prod == 2


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cmd_set_success(runner):
    result = runner.invoke(rate_limit_group, ["set", "proj", "--limit", "20", "--window", "120"])
    assert result.exit_code == 0
    assert "20 ops / 120s" in result.output


def test_cmd_set_invalid_limit(runner):
    result = runner.invoke(rate_limit_group, ["set", "proj", "--limit", "0"])
    assert result.exit_code == 0
    assert "Error" in result.output


def test_cmd_get_shows_config(runner):
    set_limit("proj", limit=15, window=300)
    result = runner.invoke(rate_limit_group, ["get", "proj"])
    assert "15" in result.output
    assert "300" in result.output


def test_cmd_status_ok(runner):
    set_limit("proj", limit=10, window=60)
    result = runner.invoke(rate_limit_group, ["status", "proj", "dev"])
    assert "OK" in result.output


def test_cmd_reset(runner):
    set_limit("proj", limit=2, window=60)
    record_operation("proj", "dev")
    record_operation("proj", "dev")
    result = runner.invoke(rate_limit_group, ["reset", "proj"])
    assert result.exit_code == 0
    assert "reset" in result.output.lower()
