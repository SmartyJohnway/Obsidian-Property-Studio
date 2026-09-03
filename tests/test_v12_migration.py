"""Test suite for M021 Schema Versioning & Migration Planner."""

from __future__ import annotations

import pytest
from app.core.migration import MigrationChangeType, plan_schema_migration


def test_v12_mig_001_non_breaking_changes_patch_minor():
    src_props = [
        {"name": "title", "storage_type": "text", "required": True},
        {"name": "status", "storage_type": "text", "ui_control": "plain"},
    ]
    tgt_props = [
        {"name": "title", "storage_type": "text", "required": True},
        {"name": "status", "storage_type": "text", "ui_control": "single_choice"},  # Non-breaking UI change
        {"name": "tags", "storage_type": "list", "required": False},  # Non-breaking optional add
    ]

    plan = plan_schema_migration(src_props, tgt_props, "1.0.0", "1.1.0")
    assert plan.is_breaking is False
    assert plan.suggested_bump == "minor"
    assert len(plan.changes) == 2


def test_v12_mig_002_breaking_changes_major():
    src_props = [
        {"name": "author", "storage_type": "text"},
        {"name": "rating", "storage_type": "text"},
    ]
    tgt_props = [
        {"name": "author", "storage_type": "list"},  # Breaking storage type change
        # rating deleted (Breaking delete)
        {"name": "published_year", "storage_type": "number", "required": True},  # Breaking required add
    ]

    plan = plan_schema_migration(src_props, tgt_props, "1.0.0", "2.0.0")
    assert plan.is_breaking is True
    assert plan.suggested_bump == "major"
    assert len(plan.migration_steps) >= 2
