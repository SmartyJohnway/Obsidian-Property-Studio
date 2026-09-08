"""Test suite for M018 Health Finding Drilldown to Note Workspace."""

from __future__ import annotations

import pytest
from app.core.state_transfer import NavigationContext, NavigationIntent, StateTransferEngine


def test_v12_hlt_001_health_finding_drilldown_intent():
    engine = StateTransferEngine()
    
    # Simulate user clicking a health finding item in Health list
    finding_context = NavigationContext(
        target_module="workspace",
        intent=NavigationIntent.INSPECT_FINDING,
        note_path="Archive/Meeting_2026.md",
        finding_id="HLT-PROP-TYPE-001",
        finding_type="type_mismatch",
        property_key="created_at",
    )
    engine.set_pending(finding_context)

    # Note workspace consumes finding context upon navigation
    assert engine.has_pending("workspace") is True
    consumed = engine.consume_pending("workspace")
    assert consumed is not None
    assert consumed.intent == NavigationIntent.INSPECT_FINDING
    assert consumed.note_path == "Archive/Meeting_2026.md"
    assert consumed.property_key == "created_at"
    assert consumed.finding_id == "HLT-PROP-TYPE-001"

    # Consumed context cannot be replayed
    assert engine.consume_pending("workspace") is None
