"""Tests for envoy.replication."""

from unittest.mock import patch, call
import pytest

from envoy import replication


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: str(tmp_path))
    monkeypatch.setattr("envoy.replication._rep_path",
                        lambda: str(tmp_path / "replication.json"))


def test_add_rule_creates_entry():
    replication.add_rule("proj_a", "prod", "proj_b", "prod")
    rules = replication.list_rules()
    assert len(rules) == 1
    assert rules[0]["src_project"] == "proj_a"
    assert rules[0]["src_env"] == "prod"
    assert rules[0]["dst_project"] == "proj_b"
    assert rules[0]["dst_env"] == "prod"


def test_add_rule_overwrites_existing():
    replication.add_rule("proj_a", "prod", "proj_b", "prod")
    replication.add_rule("proj_a", "prod", "proj_c", "staging")
    rules = replication.list_rules()
    assert len(rules) == 1
    assert rules[0]["dst_project"] == "proj_c"


def test_remove_rule_returns_true_when_exists():
    replication.add_rule("proj_a", "prod", "proj_b", "prod")
    assert replication.remove_rule("proj_a", "prod") is True
    assert replication.list_rules() == []


def test_remove_rule_returns_false_when_missing():
    assert replication.remove_rule("proj_x", "dev") is False


def test_list_rules_empty():
    assert replication.list_rules() == []


def test_list_rules_multiple():
    replication.add_rule("a", "prod", "b", "prod")
    replication.add_rule("a", "staging", "c", "staging")
    rules = replication.list_rules()
    assert len(rules) == 2
    src_envs = {r["src_env"] for r in rules}
    assert src_envs == {"prod", "staging"}


def test_replicate_calls_pull_and_push():
    replication.add_rule("proj_a", "prod", "proj_b", "prod")
    env_data = {"KEY": "value"}
    with patch("envoy.replication.vault.pull", return_value=env_data) as mock_pull, \
         patch("envoy.replication.vault.push") as mock_push:
        result = replication.replicate("proj_a", "prod", "secret")
    assert result is True
    mock_pull.assert_called_once_with("proj_a", "prod", "secret")
    mock_push.assert_called_once_with("proj_b", "prod", env_data, "secret")


def test_replicate_uses_dst_passphrase_when_provided():
    replication.add_rule("proj_a", "prod", "proj_b", "prod")
    with patch("envoy.replication.vault.pull", return_value={}) as mock_pull, \
         patch("envoy.replication.vault.push") as mock_push:
        replication.replicate("proj_a", "prod", "src_pass", dst_passphrase="dst_pass")
    mock_push.assert_called_once_with("proj_b", "prod", {}, "dst_pass")


def test_replicate_returns_false_when_no_rule():
    result = replication.replicate("proj_x", "dev", "secret")
    assert result is False
