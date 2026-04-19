import pytest
from unittest.mock import patch, MagicMock

from envoy import vault


PASSPHRASE = "test-secret"
PROJECT = "myapp"
ENV = "staging"
FILEPATH = ".env"
RAW_ENV = "API_KEY=abc\nDEBUG=true\n"


@patch("envoy.vault.storage")
@patch("envoy.vault.crypto")
@patch("envoy.vault.env_file")
def test_push(mock_env_file, mock_crypto, mock_storage):
    mock_env_file.read.return_value = RAW_ENV
    mock_crypto.encrypt.return_value = "ciphertext"
    vault.push(PROJECT, ENV, FILEPATH, PASSPHRASE)
    mock_env_file.read.assert_called_once_with(FILEPATH)
    mock_crypto.encrypt.assert_called_once_with(RAW_ENV, PASSPHRASE)
    mock_storage.save.assert_called_once_with(PROJECT, ENV, "ciphertext")


@patch("envoy.vault.storage")
@patch("envoy.vault.crypto")
@patch("envoy.vault.env_file")
def test_pull(mock_env_file, mock_crypto, mock_storage):
    mock_storage.load.return_value = "ciphertext"
    mock_crypto.decrypt.return_value = RAW_ENV
    vault.pull(PROJECT, ENV, FILEPATH, PASSPHRASE)
    mock_crypto.decrypt.assert_called_once_with("ciphertext", PASSPHRASE)
    mock_env_file.write.assert_called_once_with(FILEPATH, RAW_ENV)


@patch("envoy.vault.storage")
def test_list_envs(mock_storage):
    mock_storage.list_environments.return_value = ["dev", "prod"]
    result = vault.list_envs(PROJECT)
    assert result == ["dev", "prod"]


@patch("envoy.vault.storage")
def test_remove(mock_storage):
    mock_storage.delete.return_value = True
    assert vault.remove(PROJECT, ENV) is True


@patch("envoy.vault.storage")
@patch("envoy.vault.crypto")
@patch("envoy.vault.env_file")
def test_diff_detects_changes(mock_env_file, mock_crypto, mock_storage):
    mock_storage.load.return_value = "cipher"
    mock_crypto.decrypt.return_value = "API_KEY=old\nSHARED=same\n"
    mock_env_file.parse.side_effect = [
        {"API_KEY": "old", "SHARED": "same"},
        {"API_KEY": "new", "SHARED": "same", "NEW_VAR": "x"},
    ]
    mock_env_file.read.return_value = "API_KEY=new\nSHARED=same\nNEW_VAR=x\n"
    result = vault.diff(PROJECT, ENV, FILEPATH, PASSPHRASE)
    assert "API_KEY" in result["changed"]
    assert "NEW_VAR" in result["added"]
    assert result["removed"] == {}
