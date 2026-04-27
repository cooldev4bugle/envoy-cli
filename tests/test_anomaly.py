"""Tests for envoy.anomaly module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envoy.anomaly import detect, record_report, get_report, clear_reports, AnomalyReport


@pytest.fixture(autouse=True)
def tmp_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.anomaly.get_store_dir", lambda: tmp_path)
    yield tmp_path


def test_detect_clean_env_has_no_flags():
    report = detect("myapp", "production", {"HOST": "localhost", "PORT": "8080"})
    assert report.passed()
    assert report.flags == []


def test_detect_empty_sensitive_value_flagged():
    report = detect("myapp", "dev", {"API_SECRET": "", "HOST": "localhost"})
    assert not report.passed()
    assert any("API_SECRET" in f for f in report.flags)


def test_detect_long_value_flagged():
    long_val = "x" * 1001
    report = detect("myapp", "dev", {"DATA": long_val})
    assert not report.passed()
    assert any("DATA" in f and "unusually long" in f for f in report.flags)


def test_detect_newline_in_value_flagged():
    report = detect("myapp", "dev", {"CERT": "line1\nline2"})
    assert not report.passed()
    assert any("CERT" in f and "newline" in f for f in report.flags)


def test_detect_empty_env_flagged():
    report = detect("myapp", "dev", {})
    assert not report.passed()
    assert any("no variables" in f for f in report.flags)


def test_detect_multiple_flags():
    report = detect("myapp", "dev", {"DB_PASSWORD": "", "TOKEN": "a" * 1002})
    assert len(report.flags) >= 2


def test_record_and_get_report():
    report = detect("myapp", "staging", {"API_KEY": ""})
    record_report(report)
    loaded = get_report("myapp", "staging")
    assert loaded is not None
    assert loaded.project == "myapp"
    assert loaded.env == "staging"
    assert not loaded.passed()


def test_get_report_returns_none_when_missing():
    result = get_report("ghost", "nowhere")
    assert result is None


def test_clear_reports_all():
    r1 = detect("proj1", "dev", {})
    r2 = detect("proj2", "dev", {})
    record_report(r1)
    record_report(r2)
    clear_reports()
    assert get_report("proj1", "dev") is None
    assert get_report("proj2", "dev") is None


def test_clear_reports_by_project():
    r1 = detect("proj1", "dev", {})
    r2 = detect("proj2", "dev", {})
    record_report(r1)
    record_report(r2)
    clear_reports(project="proj1")
    assert get_report("proj1", "dev") is None
    assert get_report("proj2", "dev") is not None


def test_as_dict_structure():
    report = AnomalyReport(project="p", env="e", flags=["some flag"])
    d = report.as_dict()
    assert d["project"] == "p"
    assert d["env"] == "e"
    assert d["flags"] == ["some flag"]
