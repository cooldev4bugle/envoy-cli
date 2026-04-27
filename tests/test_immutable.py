"""Tests for envoy.immutable."""

import pytest

from envoy import immutable as imm


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.immutable._immutable_path", lambda: tmp_path / "immutable.json")
    yield tmp_path


def test_is_immutable_false_by_default():
    assert imm.is_immutable("proj", "prod", "SECRET") is False


def test_mark_immutable_creates_entry():
    imm.mark_immutable("proj", "prod", "SECRET")
    assert imm.is_immutable("proj", "prod", "SECRET") is True


def test_mark_immutable_stores_reason():
    imm.mark_immutable("proj", "prod", "SECRET", reason="Do not change in prod")
    keys = imm.get_immutable_keys("proj", "prod")
    assert any(k["key"] == "SECRET" and "Do not change" in k["reason"] for k in keys)


def test_mark_immutable_empty_reason():
    imm.mark_immutable("proj", "prod", "KEY")
    keys = imm.get_immutable_keys("proj", "prod")
    assert any(k["key"] == "KEY" and k["reason"] == "" for k in keys)


def test_unmark_immutable_returns_true_when_exists():
    imm.mark_immutable("proj", "prod", "KEY")
    assert imm.unmark_immutable("proj", "prod", "KEY") is True
    assert imm.is_immutable("proj", "prod", "KEY") is False


def test_unmark_immutable_returns_false_when_missing():
    assert imm.unmark_immutable("proj", "prod", "GHOST") is False


def test_get_immutable_keys_multiple():
    imm.mark_immutable("proj", "prod", "A")
    imm.mark_immutable("proj", "prod", "B")
    imm.mark_immutable("proj", "staging", "C")
    keys = imm.get_immutable_keys("proj", "prod")
    names = [k["key"] for k in keys]
    assert "A" in names
    assert "B" in names
    assert "C" not in names


def test_get_immutable_keys_empty():
    assert imm.get_immutable_keys("proj", "prod") == []


def test_assert_mutable_raises_on_violation():
    imm.mark_immutable("proj", "prod", "DB_PASS")
    with pytest.raises(ValueError, match="DB_PASS"):
        imm.assert_mutable("proj", "prod", {"DB_PASS": "newval", "OTHER": "ok"})


def test_assert_mutable_passes_when_clean():
    imm.mark_immutable("proj", "prod", "DB_PASS")
    # Should not raise
    imm.assert_mutable("proj", "prod", {"OTHER": "ok", "SAFE": "yes"})
