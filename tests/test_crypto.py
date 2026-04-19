"""Tests for envoy.crypto module."""

import pytest
from cryptography.exceptions import InvalidTag
from envoy.crypto import encrypt, decrypt


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "DB_PASSWORD=hunter2\nAPI_KEY=abc123\n"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(result, str)
    assert result != PLAINTEXT


def test_decrypt_roundtrip():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    decoded = decrypt(encoded, PASSPHRASE)
    assert decoded == PLAINTEXT


def test_different_passphrases_produce_different_ciphertext():
    enc1 = encrypt(PLAINTEXT, "passphrase-one")
    enc2 = encrypt(PLAINTEXT, "passphrase-two")
    assert enc1 != enc2


def test_encrypt_produces_unique_ciphertext_each_call():
    enc1 = encrypt(PLAINTEXT, PASSPHRASE)
    enc2 = encrypt(PLAINTEXT, PASSPHRASE)
    assert enc1 != enc2  # different nonce/salt each time


def test_decrypt_wrong_passphrase_raises():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises((InvalidTag, Exception)):
        decrypt(encoded, "wrong-passphrase")


def test_decrypt_tampered_data_raises():
    encoded = encrypt(PLAINTEXT, PASSPHRASE)
    tampered = encoded[:-4] + "AAAA"
    with pytest.raises(Exception):
        decrypt(tampered, PASSPHRASE)
