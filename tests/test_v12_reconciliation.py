"""Test suite for M018 Existing Note Reconciliation & Non-Schema Preservation."""

from __future__ import annotations

import pytest
from app.core.reconciliation import (
    PropertyReconcileState,
    preview_reconciled_frontmatter,
    reconcile_note_frontmatter,
)


def test_v12_rec_001_reconciliation_4_states():
    note_props = {
        "title": "Alpha Project",
        "status": "in_progress",
        "score": "not-a-number",  # Conflict with expected number
        "custom_note_tag": "preserve_me",  # Outside schema
    }

    schema_props = [
        {"name": "title", "storage_type": "text", "required": True},
        {"name": "status", "storage_type": "text", "allowed_values": ["planning", "in_progress", "done"]},
        {"name": "score", "storage_type": "number"},
        {"name": "due_date", "storage_type": "date", "required": True},  # Missing
    ]

    report = reconcile_note_frontmatter(note_props, schema_props, schema_name="project-schema")
    
    assert report.summary["matches"] == 2   # title, status
    assert report.summary["missing"] == 1   # due_date
    assert report.summary["conflict"] == 1  # score
    assert report.summary["outside_schema"] == 1  # custom_note_tag
    assert report.summary["total"] == 5

    items_by_name = {i.name: i for i in report.items}
    assert items_by_name["title"].state == PropertyReconcileState.MATCHES
    assert items_by_name["due_date"].state == PropertyReconcileState.MISSING
    assert items_by_name["score"].state == PropertyReconcileState.CONFLICT
    assert items_by_name["custom_note_tag"].state == PropertyReconcileState.OUTSIDE_SCHEMA


def test_v12_rec_002_outside_schema_properties_strictly_preserved():
    """DEC-029 Invariant: Properties outside the schema MUST NOT be discarded."""
    note_props = {
        "author": "Alice",
        "legacy_id": 12345,
        "arbitrary_field": {"nested": "value"},
    }

    schema_props = [
        {"name": "author", "storage_type": "text"},
        {"name": "department", "storage_type": "text"},
    ]

    resolved_values = {
        "author": "Alice",
        "department": "Engineering",
    }

    preview = preview_reconciled_frontmatter(note_props, schema_props, resolved_values)
    merged = preview["merged_properties"]

    assert merged["author"] == "Alice"
    assert merged["department"] == "Engineering"
    # Preserved outside-schema properties
    assert merged["legacy_id"] == 12345
    assert merged["arbitrary_field"] == {"nested": "value"}
    assert "legacy_id" in preview["diff"]["preserved"]
    assert "department" in preview["diff"]["added"]
