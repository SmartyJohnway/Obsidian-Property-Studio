"""Test suite for M020 Proposal Workflow and Contract 1.0 / 1.1 compatibility."""

from __future__ import annotations

import pytest
from app.core.proposal import validate_proposal


def test_v12_prp_001_contract_10_exact_backward_compatibility():
    """Proposal Contract 1.0 must be accepted without errors or deprecation failure."""
    p10 = {
        "proposal_version": "1.0",
        "schema_name": "legacy_project",
        "description": "Valid 1.0 proposal",
        "properties": [
            {"name": "status", "storage_type": "text", "required": True},
            {"name": "score", "storage_type": "number"},
        ],
    }
    res = validate_proposal(p10)
    assert res["valid"] is True
    assert res["proposal_version"] == "1.0"
    assert res["schema"]["schema_name"] == "legacy_project"
    assert len(res["schema"]["properties"]) == 2


def test_v12_prp_002_contract_11_extensions():
    """Proposal Contract 1.1 supports optional target_note, target_scope, rationale, proposed_migration."""
    p11 = {
        "proposal_version": "1.1",
        "schema_name": "advanced_research",
        "target_note": "Research/AI_2026.md",
        "target_scope": "Research",
        "rationale": "Standardizing academic paper metadata across research vault.",
        "proposed_migration": {
            "rename_keys": {"old_tag": "tags"},
        },
        "properties": [
            {"name": "authors", "storage_type": "list", "ui_control": "plain"},
            {"name": "published_date", "storage_type": "date"},
        ],
    }
    res = validate_proposal(p11)
    assert res["valid"] is True
    assert res["proposal_version"] == "1.1"
    assert res["target_note"] == "Research/AI_2026.md"
    assert res["target_scope"] == "Research"
    assert "Standardizing" in res["rationale"]
    assert res["proposed_migration"]["rename_keys"]["old_tag"] == "tags"


def test_v12_prp_003_unsupported_version_fails_honestly():
    p_invalid = {
        "proposal_version": "9.9",
        "schema_name": "future_schema",
        "properties": [{"name": "title", "storage_type": "text"}],
    }
    res = validate_proposal(p_invalid)
    assert res["valid"] is False
    assert any("Unsupported proposal_version" in e for e in res["errors"])
