"""Regression and contract test suite for M016 Workflow Closure Foundation & State Transfer.

Covers V12-WFC-* requirements:
- Explicit context transfer across modules (schema_id, finding_id, note_path, proposal_candidate)
- Serialization and validation of navigation payloads
- No dead-end CTA routing state guarantees
"""

from __future__ import annotations

import os
import pytest
from app.core.state_transfer import (
    NavigationContext,
    NavigationIntent,
    StateTransferEngine,
    StateTransferError,
    validate_navigation_payload,
)


def test_v12_wfc_001_navigation_context_creation():
    """V12-WFC-001: Context payload creation with schema and note."""
    ctx = NavigationContext(
        target_module="workspace",
        intent=NavigationIntent.RECONCILE,
        schema_id="schema_proj_v1",
        note_path="Projects/Alpha.md",
        extra={"custom_flag": True},
    )
    data = ctx.to_dict()
    assert data["target_module"] == "workspace"
    assert data["intent"] == "reconcile"
    assert data["schema_id"] == "schema_proj_v1"
    assert data["note_path"] == "Projects/Alpha.md"
    assert data["extra"]["custom_flag"] is True

    # Roundtrip from dict
    restored = NavigationContext.from_dict(data)
    assert restored.target_module == ctx.target_module
    assert restored.intent == ctx.intent
    assert restored.schema_id == ctx.schema_id
    assert restored.note_path == ctx.note_path


def test_v12_wfc_002_health_finding_drilldown_context():
    """V12-WFC-002: Health finding context must preserve diagnostic metadata."""
    ctx = NavigationContext(
        target_module="workspace",
        intent=NavigationIntent.INSPECT_FINDING,
        note_path="Notes/Task1.md",
        finding_id="HLT-MISSING-STATUS-001",
        finding_type="missing_property",
        property_key="status",
        expected_schema_id="schema_task_v1",
    )
    validated = validate_navigation_payload(ctx.to_dict())
    assert validated["valid"] is True
    assert validated["context"]["finding_id"] == "HLT-MISSING-STATUS-001"
    assert validated["context"]["property_key"] == "status"
    assert validated["context"]["expected_schema_id"] == "schema_task_v1"


def test_v12_wfc_003_proposal_candidate_context():
    """V12-WFC-003: AI proposal candidate transfer to schema editor or workspace."""
    candidate_props = [
        {"name": "serial_number", "storage_type": "text", "ui_control": "plain", "required": True},
        {"name": "vendor", "storage_type": "text", "ui_control": "plain", "required": False},
    ]
    ctx = NavigationContext(
        target_module="design",
        intent=NavigationIntent.EDIT_CANDIDATE,
        schema_name="equipment_candidate",
        properties=candidate_props,
    )
    validated = validate_navigation_payload(ctx.to_dict())
    assert validated["valid"] is True
    assert validated["context"]["schema_name"] == "equipment_candidate"
    assert len(validated["context"]["properties"]) == 2


def test_v12_wfc_004_state_transfer_engine_queue_and_consume():
    """V12-WFC-004: Engine queues pending navigation and consumes once."""
    engine = StateTransferEngine()
    ctx = NavigationContext(
        target_module="workspace",
        intent=NavigationIntent.RECONCILE,
        schema_id="schema_123",
        note_path="Notes/A.md",
    )
    engine.set_pending(ctx)
    assert engine.has_pending("workspace") is True
    assert engine.has_pending("health") is False

    # Peek does not consume
    peeked = engine.peek_pending("workspace")
    assert peeked is not None
    assert peeked.schema_id == "schema_123"
    assert engine.has_pending("workspace") is True

    # Consume retrieves and clears
    consumed = engine.consume_pending("workspace")
    assert consumed is not None
    assert consumed.schema_id == "schema_123"
    assert engine.has_pending("workspace") is False

    # Second consume is None
    assert engine.consume_pending("workspace") is None


def test_v12_wfc_005_validation_fail_closed_on_corrupt_payload():
    """V12-WFC-005: Corrupt or malformed navigation payloads fail closed honestly."""
    # Missing target_module
    res = validate_navigation_payload({"intent": "reconcile"})
    assert res["valid"] is False
    assert "target_module" in res["error"]

    # Invalid intent string
    res = validate_navigation_payload({"target_module": "workspace", "intent": "invalid_intent_xyz"})
    assert res["valid"] is False
    assert "Unknown navigation intent" in res["error"]

    # Non-dict payload
    res = validate_navigation_payload("not_a_dict")
    assert res["valid"] is False


def test_v12_wfc_006_js_state_transfer_file_exists_and_valid():
    """V12-WFC-006: Ensure app/ui/state_transfer.js exists and has core methods."""
    js_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "app", "ui", "state_transfer.js"
    )
    assert os.path.isfile(js_path), "app/ui/state_transfer.js must exist"
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "StateTransfer" in content
    assert "setPending" in content
    assert "consumePending" in content
    assert "peekPending" in content
