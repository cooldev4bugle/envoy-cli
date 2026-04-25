import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import envoy.checksum as checksum_mod
from envoy.checksum import compute, record, get_checksum, verify, remove_checksum, list_checksums


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(checksum_mod, "get_store_dir", lambda: tmp_path)
    return tmp_path


ENV_A = {"DB_HOST": "localhost", "PORT": "5432"}
ENV_B = {"DB_HOST": "prod.example.com", "PORT": "5432"}


def test_compute_returns_hex_string():
    digest = compute(ENV_A)
    assert isinstance(digest, str)
    assert len(digest) == 64  # SHA-256 hex


def test_compute_is_stable():
    assert compute(ENV_A) == compute(ENV_A)


def test_compute_differs_for_different_data():
    assert compute(ENV_A) != compute(ENV_B)


def test_compute_order_independent():
    d1 = {"A": "1", "B": "2"}
    d2 = {"B": "2", "A": "1"}
    assert compute(d1) == compute(d2)


def test_record_and_get(tmp_store):
    digest = record("myapp", "production", ENV_A)
    assert get_checksum("myapp", "production") == digest


def test_get_checksum_returns_none_when_unset(tmp_store):
    assert get_checksum("ghost", "staging") is None


def test_verify_returns_true_when_matching(tmp_store):
    record("myapp", "staging", ENV_A)
    assert verify("myapp", "staging", ENV_A) is True


def test_verify_returns_false_when_tampered(tmp_store):
    record("myapp", "staging", ENV_A)
    assert verify("myapp", "staging", ENV_B) is False


def test_verify_returns_false_when_no_record(tmp_store):
    assert verify("myapp", "nope", ENV_A) is False


def test_remove_checksum_returns_true_when_exists(tmp_store):
    record("myapp", "dev", ENV_A)
    assert remove_checksum("myapp", "dev") is True
    assert get_checksum("myapp", "dev") is None


def test_remove_checksum_returns_false_when_missing(tmp_store):
    assert remove_checksum("myapp", "ghost") is False


def test_list_checksums_returns_all_envs(tmp_store):
    record("myapp", "dev", ENV_A)
    record("myapp", "prod", ENV_B)
    record("other", "dev", ENV_A)
    result = list_checksums("myapp")
    assert set(result.keys()) == {"dev", "prod"}


def test_list_checksums_empty_when_no_entries(tmp_store):
    assert list_checksums("nothing") == {}
