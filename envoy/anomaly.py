"""Anomaly detection for env file changes — flags unusual patterns."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir

_SENSITIVE_PATTERNS = ("key", "secret", "token", "password", "pass", "pwd", "auth")


def _anomaly_path() -> Path:
    return get_store_dir() / "anomalies.json"


def _load() -> dict:
    p = _anomaly_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: dict) -> None:
    _anomaly_path().write_text(json.dumps(data, indent=2))


@dataclass
class AnomalyReport:
    project: str
    env: str
    flags: list[str]

    def passed(self) -> bool:
        return len(self.flags) == 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect(project: str, env: str, variables: dict[str, str]) -> AnomalyReport:
    """Inspect variables for anomalous patterns and return a report."""
    flags: list[str] = []

    for key, value in variables.items():
        lower = key.lower()
        if any(p in lower for p in _SENSITIVE_PATTERNS) and not value.strip():
            flags.append(f"sensitive key '{key}' has an empty value")
        if len(value) > 1000:
            flags.append(f"key '{key}' has an unusually long value ({len(value)} chars)")
        if "\n" in value:
            flags.append(f"key '{key}' contains a newline character")

    if len(variables) == 0:
        flags.append("environment has no variables")

    return AnomalyReport(project=project, env=env, flags=flags)


def record_report(report: AnomalyReport) -> None:
    """Persist an anomaly report for later inspection."""
    data = _load()
    key = f"{report.project}:{report.env}"
    data[key] = report.as_dict()
    _save(data)


def get_report(project: str, env: str) -> AnomalyReport | None:
    data = _load()
    key = f"{project}:{env}"
    if key not in data:
        return None
    raw = data[key]
    return AnomalyReport(**raw)


def clear_reports(project: str | None = None) -> None:
    if project is None:
        _save({})
        return
    data = _load()
    keys_to_remove = [k for k in data if k.startswith(f"{project}:")]
    for k in keys_to_remove:
        del data[k]
    _save(data)
