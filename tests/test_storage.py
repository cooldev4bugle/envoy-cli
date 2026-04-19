import pytest
import json
from pathlib import Path
from unittest.mock import patch

from envoy import storage


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    yield tmp_path


def test_save_and_load(tmp_store):
    storage.save("myapp", "production", "enc_data_abc")
    result = storage.load("myapp", "production")
    assert result == "enc_data_abc"


def test_load_missing_project_raises():
    with pytest.raises(KeyError):
        storage.load("ghost", "staging")


def test_load_missing_env_raises():
    storage.save("myapp", "dev", "somedata")
    with pytest.raises(KeyError):
        storage.load("myapp", "staging")


def test_list_environments():
    storage.save("myapp", "dev", "d1")
    storage.save("myapp", "prod", "d2")
    envs = storage.list_environments("myapp")
    assert set(envs) == {"dev", "prod"}


def test_list_empty_project():
    assert storage.list_environments("unknown") == []


def test_delete_existing():
    storage.save("myapp", "dev", "data")
    assert storage.delete("myapp", "dev") is True
    assert "dev" not in storage.list_environments("myapp")


def test_delete_nonexistent():
    assert storage.delete("myapp", "ghost") is False


def test_overwrite_environment():
    storage.save("myapp", "dev", "v1")
    storage.save("myapp", "dev", "v2")
    assert storage.load("myapp", "dev") == "v2"
