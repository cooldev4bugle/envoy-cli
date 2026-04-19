"""Tests for envoy.rotate."""

import pytest
from unittest.mock import patch, MagicMock
from envoy import rotate, crypto, env_file


SAMPLE_PAIRS = {"KEY": "value", "SECRET": "s3cr3t"}
OLD_PASS = "old-passphrase"
NEW_PASS = "new-passphrase"


def _make_ciphertext(pairs, passphrase):
    return crypto.encrypt(env_file.serialize(pairs), passphrase)


@pytest.fixture()
def mock_storage(monkeypatch):
    store = {}

    def fake_save(project, env_name, data):
        store[(project, env_name)] = data

    def fake_load(project, env_name):
        return store[(project, env_name)]

    def fake_list(project):
        return [k[1] for k in store if k[0] == project]

    monkeypatch.setattr("envoy.rotate.storage.save", fake_save)
    monkeypatch.setattr("envoy.rotate.storage.load", fake_load)
    monkeypatch.setattr("envoy.rotate.storage.list_environments", fake_list)
    return store


def test_rotate_env_decrypts_and_reencrypts(mock_storage):
    ct = _make_ciphertext(SAMPLE_PAIRS, OLD_PASS)
    mock_storage[("myapp", "production")] = ct

    rotate.rotate_env("myapp", "production", OLD_PASS, NEW_PASS)

    new_ct = mock_storage[("myapp", "production")]
    assert new_ct != ct
    decrypted = crypto.decrypt(new_ct, NEW_PASS)
    assert env_file.parse(decrypted) == SAMPLE_PAIRS


def test_rotate_project_rotates_all_envs(mock_storage):
    for env in ("staging", "production"):
        mock_storage[("proj", env)] = _make_ciphertext(SAMPLE_PAIRS, OLD_PASS)

    rotated = rotate.rotate_project("proj", OLD_PASS, NEW_PASS)

    assert set(rotated) == {"staging", "production"}
    for env in rotated:
        plaintext = crypto.decrypt(mock_storage[("proj", env)], NEW_PASS)
        assert env_file.parse(plaintext) == SAMPLE_PAIRS


def test_rotate_project_no_envs_raises(mock_storage):
    with pytest.raises(ValueError, match="No environments"):
        rotate.rotate_project("ghost", OLD_PASS, NEW_PASS)


def test_rotate_env_wrong_old_passphrase_raises(mock_storage):
    ct = _make_ciphertext(SAMPLE_PAIRS, OLD_PASS)
    mock_storage[("myapp", "dev")] = ct

    with pytest.raises(Exception):
        rotate.rotate_env("myapp", "dev", "wrong-pass", NEW_PASS)
