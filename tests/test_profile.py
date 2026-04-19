import pytest
from unittest.mock import patch, MagicMock
from envoy import profile


SAMPLE_VARS = {"KEY1": "val1", "KEY2": "val2"}


@pytest.fixture
def mock_storage(tmp_path):
    store: dict = {}

    def fake_load(project, env):
        key = (project, env)
        if key not in store:
            raise FileNotFoundError
        return store[key]

    def fake_save(project, env, data):
        store[(project, env)] = data

    with patch("envoy.profile.storage.load", side_effect=fake_load), \
         patch("envoy.profile.storage.save", side_effect=fake_save):
        yield store


def test_list_profiles_empty(mock_storage):
    assert profile.list_profiles("proj", "dev") == []


def test_save_and_list_profile(mock_storage):
    mock_storage[("proj", "dev")] = {}
    with patch("envoy.profile.vault.pull", return_value=SAMPLE_VARS):
        profile.save_profile("proj", "dev", "baseline", "pass")
    names = profile.list_profiles("proj", "dev")
    assert "baseline" in names


def test_load_profile(mock_storage):
    mock_storage[("proj", "dev")] = {"__profiles__": {"snap": SAMPLE_VARS}}
    result = profile.load_profile("proj", "dev", "snap")
    assert result == SAMPLE_VARS


def test_load_profile_missing_raises(mock_storage):
    mock_storage[("proj", "dev")] = {"__profiles__": {}}
    with pytest.raises(KeyError, match="nope"):
        profile.load_profile("proj", "dev", "nope")


def test_delete_profile(mock_storage):
    mock_storage[("proj", "dev")] = {"__profiles__": {"old": SAMPLE_VARS}}
    profile.delete_profile("proj", "dev", "old")
    assert "old" not in mock_storage[("proj", "dev")]["__profiles__"]


def test_apply_profile_replace(mock_storage):
    mock_storage[("proj", "dev")] = {"__profiles__": {"snap": SAMPLE_VARS}}
    with patch("envoy.profile.vault.push") as mock_push:
        profile.apply_profile("proj", "dev", "snap", "pass", merge=False)
        mock_push.assert_called_once_with("proj", "dev", SAMPLE_VARS, "pass")


def test_apply_profile_merge(mock_storage):
    existing = {"KEY1": "old", "KEY3": "keep"}
    mock_storage[("proj", "dev")] = {"__profiles__": {"snap": SAMPLE_VARS}}
    with patch("envoy.profile.vault.pull", return_value=existing), \
         patch("envoy.profile.vault.push") as mock_push:
        profile.apply_profile("proj", "dev", "snap", "pass", merge=True)
        merged = {**existing, **SAMPLE_VARS}
        mock_push.assert_called_once_with("proj", "dev", merged, "pass")
