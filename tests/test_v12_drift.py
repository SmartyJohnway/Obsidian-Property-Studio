"""Test suite for M019 Schema Drift Diagnostic Engine."""

from __future__ import annotations

import pytest
from app.core.drift import DriftCategory, analyze_schema_drift
from app.core.model import Note, ParseStatus, PropertyValue, StorageType


def test_v12_drift_001_schema_drift_analysis():
    def make_pv(k, v):
        return PropertyValue(key=k, raw=v, storage_type=StorageType.TEXT)

    notes = [
        Note(path="Projects/A.md", parse_status=ParseStatus.OK, properties={"type": make_pv("type", "project"), "status": make_pv("status", "active")}),
        Note(path="Projects/B.md", parse_status=ParseStatus.OK, properties={"type": make_pv("type", "project")}),  # Missing required status
        Note(path="Projects/C.md", parse_status=ParseStatus.OK, properties={"type": make_pv("type", "project"), "status": make_pv("status", "invalid_status"), "extra": make_pv("extra", 1)}),  # Value drift + unexpected
    ]

    schema_props = [
        {"name": "type", "storage_type": "text", "required": True},
        {"name": "status", "storage_type": "text", "required": True, "allowed_values": ["active", "archived"]},
    ]

    report = analyze_schema_drift(
        notes=notes,
        schema_properties=schema_props,
        schema_id="schema_proj",
        schema_name="Project Schema",
        scope_key="Projects",
    )

    assert report.total_notes == 3
    assert report.compliant_notes == 1  # Note A is fully compliant
    assert report.by_category[DriftCategory.MISSING_REQUIRED.value] == 1  # Note B missing status
    assert report.by_category[DriftCategory.VALUE_DRIFT.value] == 1  # Note C invalid status
    assert report.by_category[DriftCategory.UNEXPECTED_PROPERTY.value] == 1  # Note C extra
