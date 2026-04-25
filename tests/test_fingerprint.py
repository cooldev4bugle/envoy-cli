"""Tests for envoy.fingerprint."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import envoy.fingerprint as fp


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "get_store_dir", lambda: tmp_path)
    return tmp_path


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432"}
ENV_B = {"DB_HOST": "remotehost", "DB_PORT": "5432"}


def test_compute_returns_hex_string():
    digest = fp.compute(ENV_A)
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_compute_is_stable():
    assert fp.compute(ENV_A) == fp.compute(ENV_A)


def test_compute_order_independent():
    shuffled = {"DB_PORT": "5432", "DB_HOST": "localhost"}
    assert fp.compute(ENV_A) == fp.compute(shuffled)


def test_compute_differs_for_different_data():
    assert fp.compute(ENV_A) != fp.compute(ENV_B)


def test_record_and_get():
    digest = fp.record("myapp", "production", ENV_A)
    assert fp.get_fingerprint("myapp", "production") == digest


def test_get_fingerprint_returns_none_when_missing():
    assert fp.get_fingerprint("ghost", "staging") is None


def test_verify_returns_true_when_matching():
    fp.record("myapp", "staging", ENV_A)
    assert fp.verify("myapp", "staging", ENV_A) is True


def test_verify_returns_false_when_tampered():
    fp.record("myapp", "staging", ENV_A)
    assert fp.verify("myapp", "staging", ENV_B) is False


def test_verify_returns_false_when_no_record():
    assert fp.verify("new_project", "dev", ENV_A) is False


def test_remove_fingerprint_returns_true_when_exists():
    fp.record("myapp", "dev", ENV_A)
    assert fp.remove_fingerprint("myapp", "dev") is True
    assert fp.get_fingerprint("myapp", "dev") is None


def test_remove_fingerprint_returns_false_when_missing():
    assert fp.remove_fingerprint("ghost", "dev") is False


def test_record_overwrites_existing():
    fp.record("myapp", "prod", ENV_A)
    digest_b = fp.record("myapp", "prod", ENV_B)
    assert fp.get_fingerprint("myapp", "prod") == digest_b
