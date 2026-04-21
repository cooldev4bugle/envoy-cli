"""Tests for envoy.retention module."""

import pytest

from envoy import retention
from envoy.retention import get_policy, list_policies, remove_policy, set_policy


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(retention, "get_store_dir", lambda: tmp_path)


def test_get_policy_returns_defaults_when_unset():
    policy = get_policy("myproject")
    assert policy["max_snapshots"] == 10
    assert policy["max_history"] == 50


def test_set_and_get_policy():
    set_policy("myproject", max_snapshots=5, max_history=20)
    policy = get_policy("myproject")
    assert policy["max_snapshots"] == 5
    assert policy["max_history"] == 20


def test_set_policy_partial_update():
    set_policy("myproject", max_snapshots=3)
    set_policy("myproject", max_history=15)
    policy = get_policy("myproject")
    assert policy["max_snapshots"] == 3
    assert policy["max_history"] == 15


def test_set_policy_raises_on_zero_snapshots():
    with pytest.raises(ValueError, match="max_snapshots"):
        set_policy("myproject", max_snapshots=0)


def test_set_policy_raises_on_negative_history():
    with pytest.raises(ValueError, match="max_history"):
        set_policy("myproject", max_history=-1)


def test_remove_policy_returns_true_when_exists():
    set_policy("myproject", max_snapshots=7)
    assert remove_policy("myproject") is True


def test_remove_policy_returns_false_when_missing():
    assert remove_policy("ghost") is False


def test_remove_policy_resets_to_defaults():
    set_policy("myproject", max_snapshots=2, max_history=5)
    remove_policy("myproject")
    policy = get_policy("myproject")
    assert policy["max_snapshots"] == 10
    assert policy["max_history"] == 50


def test_list_policies_empty():
    assert list_policies() == {}


def test_list_policies_shows_all():
    set_policy("alpha", max_snapshots=4)
    set_policy("beta", max_history=30)
    policies = list_policies()
    assert "alpha" in policies
    assert "beta" in policies
    assert policies["alpha"]["max_snapshots"] == 4
    assert policies["beta"]["max_history"] == 30
