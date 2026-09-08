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


def test_v12_prp_002_contract_11_authoritative_extensions():
    """Proposal Contract 1.1 supports management_purpose, source_context, target_note_kind, proposal_notes, schema_target (REQ-046)."""
    p11 = {
        "proposal_version": "1.1",
        "schema_name": "advanced_research",
        "management_purpose": "Standardizing academic paper metadata across research vault.",
        "source_context": "Machine Learning literature review",
        "target_note_kind": "paper",
        "proposal_notes": "Advisory note: use ISO dates for published_date.",
        "schema_target": "Research",
        "properties": [
            {"name": "authors", "storage_type": "list", "ui_control": "plain"},
            {"name": "published_date", "storage_type": "date"},
        ],
    }
    res = validate_proposal(p11)
    assert res["valid"] is True
    assert res["proposal_version"] == "1.1"
    assert res["management_purpose"] == "Standardizing academic paper metadata across research vault."
    assert res["source_context"] == "Machine Learning literature review"
    assert res["target_note_kind"] == "paper"
    assert "ISO dates" in res["proposal_notes"]
    assert res["schema_target"] == "Research"
    assert len(res["warnings"]) == 0


def test_v12_prp_003_unsupported_version_fails_honestly():
    p_invalid = {
        "proposal_version": "9.9",
        "schema_name": "future_schema",
        "properties": [{"name": "title", "storage_type": "text"}],
    }
    res = validate_proposal(p_invalid)
    assert res["valid"] is False
    assert any("Unsupported proposal_version" in e for e in res["errors"])


def test_v12_prp_004_four_way_comparison_and_compatibility():
    """Verify authoritative four-way comparison and compatibility state engine (REQ-046)."""
    from app.core.inventory import Inventory, PropertyEntry, ValueStat
    from app.core.proposal import import_proposal

    # Mock scoped inventory
    scoped_inv = Inventory()
    scoped_inv.properties["status"] = PropertyEntry(
        key="status",
        usage_count=5,
        observed_types={"text": 5},
        values={"active": ValueStat(value="active", count=5)},
    )

    # Mock vault inventory with a type mismatch on 'rating'
    vault_inv = Inventory()
    vault_inv.properties["status"] = PropertyEntry(
        key="status",
        usage_count=20,
        observed_types={"text": 20},
        values={"active": ValueStat(value="active", count=20)},
    )
    vault_inv.properties["rating"] = PropertyEntry(
        key="rating",
        usage_count=10,
        observed_types={"number": 10},
        values={"5": ValueStat(value="5", count=10)},
    )

    proposal_text = """{
        "proposal_version": "1.1",
        "schema_name": "test_four_way",
        "management_purpose": "Testing four-way comparison",
        "properties": [
            {"name": "status", "storage_type": "text"},
            {"name": "rating", "storage_type": "text"},
            {"name": "brand_new_prop", "storage_type": "text"}
        ]
    }"""

    report = import_proposal(
        text=proposal_text,
        scoped_inv=scoped_inv,
        vault_inv=vault_inv,
        glossary_store=None,
        schema_library=None,
    )

    assert report["valid"] is True
    four_way = report["four_way_comparison"]
    assert len(four_way) == 3

    status_item = next(i for i in four_way if i["name"] == "status")
    assert status_item["scope_usage_count"] == 5
    assert status_item["vault_usage_count"] == 20
    assert status_item["compatibility_state"] == "compatible"

    rating_item = next(i for i in four_way if i["name"] == "rating")
    assert rating_item["compatibility_state"] == "type_conflict"
    assert "Vault dominant type is 'number'" in rating_item["compatibility_detail"]

    new_item = next(i for i in four_way if i["name"] == "brand_new_prop")
    assert new_item["compatibility_state"] == "new_property"


def test_v12_prp_005_sk_f01_proposal_compatibility_matrix():
    """Regression test for SK-F01: Proposal Contract pre-output validation matrix.

    Validates that:
    1. Known Claude failure (storage_type='text', ui_control='note_link_list') is rejected.
    2. Corrected pair (storage_type='list', ui_control='note_link_list') is accepted.
    3. Entire authoritative compatibility matrix is enforced deterministically by validate_proposal.
    """
    # 1. Known Claude failure: text + note_link_list must fail closed
    failing_proposal = {
        "proposal_version": "1.1",
        "schema_name": "claude_failed_proposal",
        "properties": [
            {
                "name": "related_tools",
                "storage_type": "text",
                "ui_control": "note_link_list",
            }
        ],
    }
    res_fail = validate_proposal(failing_proposal)
    assert res_fail["valid"] is False
    assert any(
        "ui_control 'note_link_list' is not compatible with storage_type 'text'" in err
        for err in res_fail["errors"]
    )

    # 2. Corrected proposal: list + note_link_list must pass
    valid_proposal = {
        "proposal_version": "1.1",
        "schema_name": "corrected_proposal",
        "properties": [
            {
                "name": "related_tools",
                "storage_type": "list",
                "ui_control": "note_link_list",
            }
        ],
    }
    res_pass = validate_proposal(valid_proposal)
    assert res_pass["valid"] is True
    assert len(res_pass["errors"]) == 0

    # 3. Single wikilink picker: note_link requires storage_type='text'
    link_valid = {
        "proposal_version": "1.1",
        "schema_name": "note_link_valid",
        "properties": [
            {
                "name": "lead_architect",
                "storage_type": "text",
                "ui_control": "note_link",
            }
        ],
    }
    assert validate_proposal(link_valid)["valid"] is True

    link_invalid = {
        "proposal_version": "1.1",
        "schema_name": "note_link_invalid",
        "properties": [
            {
                "name": "lead_architect",
                "storage_type": "list",
                "ui_control": "note_link",
            }
        ],
    }
    res_link_inv = validate_proposal(link_invalid)
    assert res_link_inv["valid"] is False
    assert any(
        "ui_control 'note_link' is not compatible with storage_type 'list'" in err
        for err in res_link_inv["errors"]
    )

    # 4. Choice controls compatibility
    single_choice_invalid = {
        "proposal_version": "1.1",
        "schema_name": "choice_invalid",
        "properties": [
            {
                "name": "status",
                "storage_type": "list",
                "ui_control": "single_choice",
                "allowed_values": ["active", "completed"],
            }
        ],
    }
    res_sc_inv = validate_proposal(single_choice_invalid)
    assert res_sc_inv["valid"] is False
    assert any(
        "ui_control 'single_choice' is not compatible with storage_type 'list'" in err
        for err in res_sc_inv["errors"]
    )


