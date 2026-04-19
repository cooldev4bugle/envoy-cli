import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import tempfile
import os

import envoy.lock as lock_mod


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(lock_mod, "get_store_dir", lambda: tmp_path)
    return tmp_path


def test_lock_env_creates_entry(tmp_store):
    lock_mod.lock_env("myapp", "production")
    assert lock_mod.is_locked("myapp", "production")


def test_unlock_env_removes_entry(tmp_store):
    lock_mod.lock_env("myapp", "production")
    lock_mod.unlock_env("myapp", "production")
    assert not lock_mod.is_locked("myapp", "production")


def test_unlock_nonexistent_does_nothing(tmp_store):
    lock_mod.unlock_env("myapp", "staging")  # should not raise


def test_is_locked_false_by_default(tmp_store):
    assert not lock_mod.is_locked("myapp", "staging")


def test_list_locked_returns_sorted(tmp_store):
    lock_mod.lock_env("myapp", "production")
    lock_mod.lock_env("myapp", "staging")
    result = lock_mod.list_locked("myapp")
    assert result == ["production", "staging"]


def test_list_locked_empty_project(tmp_store):
    assert lock_mod.list_locked("ghost") == []


def test_assert_unlocked_raises_if_locked(tmp_store):
    lock_mod.lock_env("myapp", "production")
    with pytest.raises(PermissionError, match="locked"):
        lock_mod.assert_unlocked("myapp", "production")


def test_assert_unlocked_passes_if_not_locked(tmp_store):
    lock_mod.assert_unlocked("myapp", "staging")  # no exception


def test_duplicate_lock_not_duplicated(tmp_store):
    lock_mod.lock_env("myapp", "production")
    lock_mod.lock_env("myapp", "production")
    assert lock_mod.list_locked("myapp") == ["production"]
