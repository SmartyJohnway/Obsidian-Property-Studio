"""Cross-Module Canonical Consistency Gate (M008).

Proves that parsing, ambiguity, and provenance semantics remain consistent
across Scan -> Inventory -> Design -> Fill -> Refactor -> Relationship -> Health -> Export.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import pytest

from app.core import design, exports, fill, health, inventory, manifest, refactor, relationships
from app.core.model import Schema, SchemaProperty, StorageType, UIControl
from app.core.scanner import note_name_index, scan_vault


def test_m008_malformed_trace_across_modules(main_vault: str, out_dir: str) -> None:
    """M008-T01: Trace malformed note across all modules."""
    scan = scan_vault(main_vault)
    malformed = scan.note_by_path("Notes/Malformed.md")
    assert malformed is not None and malformed.parse_failed is True
    
    # 1. Scan/Inventory: must be in parse failures, NOT in notes_without_properties
    unreadable_notes = [n.path for n in scan.notes if n.parse_failed]
    assert "Notes/Malformed.md" in unreadable_notes
    assert "Notes/Malformed.md" not in [n.path for n in scan.notes if n.parse_status.value == "no_frontmatter"]
    assert scan.summary()["notes_with_parse_failure"] == 3
    
    # 2. Refactor: must appear in unreadable_notes in plan
    plan = refactor.plan_rename(scan, "project", "project_new")
    assert any(n["note"] == "Notes/Malformed.md" for n in plan["unreadable_notes"])
    
    # 3. Health: must appear in parse_failure findings
    inv = inventory.build_inventory(scan)
    report = health.health_report(scan, inv)
    parse_failures = [f for f in report["findings"] if f["category"] == "parse_failure"]
    assert any("Notes/Malformed.md" in f["affected_notes"] for f in parse_failures)
    
    # 4. Export: survives into export JSON
    res = exports.export_artifact("health", report, main_vault, out_dir)
    data = json.load(open(res["files"][0]["path"], encoding="utf-8"))
    exp_failures = [f for f in data["findings"] if f["category"] == "parse_failure"]
    assert any("Notes/Malformed.md" in f["affected_notes"] for f in exp_failures)


def test_m008_duplicate_key_trace_across_modules(main_vault: str, out_dir: str) -> None:
    """M008-T02: Trace duplicate-key note across all modules."""
    scan = scan_vault(main_vault)
    dup_note = scan.note_by_path("Notes/Duplicate Key.md")
    assert dup_note is not None and "status" in dup_note.duplicate_keys
    
    # 1. Inventory: duplicate status key recorded
    inv = inventory.build_inventory(scan)
    status_entry = inv.get("status")
    assert status_entry is not None
    assert "Notes/Duplicate Key.md" in status_entry.ambiguous_notes
    
    # 2. Refactor: excluded from automated changes with fail-closed reason
    plan = refactor.plan_normalize(scan, "status")
    assert any(e["note"] == "Notes/Duplicate Key.md" for e in plan["excluded"])
    
    # 3. Health: surfaced as ambiguous_property finding
    report = health.health_report(scan, inv)
    ambig_findings = [f for f in report["findings"] if f["category"] == "ambiguous_property"]
    assert any("Notes/Duplicate Key.md" in f["affected_notes"] for f in ambig_findings)


def test_m008_ambiguous_identity_trace_across_modules(main_vault: str, tmp_path: Path, out_dir: str) -> None:
    """M008-T03: Trace ambiguous ACME / Duplicate Name across Fill, Relationships, Health, Export."""
    scan = scan_vault(main_vault)
    note_idx = note_name_index(scan)
    
    # 1. Fill: generic ambiguous target fails closed
    schema = Schema(
        name="test",
        properties=[SchemaProperty("project", StorageType.TEXT, UIControl.NOTE_LINK, reason="r")],
    )
    fill_res = fill.fill_preview(schema, {"project": "Duplicate Name"}, note_index=note_idx)
    assert not fill_res["valid"]
    assert len(fill_res["errors"]) > 0
    
    # Explicit choice passes
    fill_exp = fill.fill_preview(schema, {"project": "A/Duplicate Name"}, note_index=note_idx)
    assert fill_exp["valid"]
    
    # 2. Relationships: ambiguous link is never auto-resolved
    inbox = relationships.build_inbox(scan)
    ambig_item = next(i for i in inbox["items"] if i["note"] == "Inbox/Ambiguous Target.md")
    assert ambig_item["kind"] == "ambiguous_link"
    assert ambig_item["confidence"] == "ambiguous"
    assert ambig_item["auto_resolved"] is False
    assert ambig_item["proposed_value"] is None
    
    # 3. Export: ambiguity preserved in exported inbox artifact
    res = exports.export_artifact("inbox", inbox, main_vault, out_dir)
    data = json.load(open(res["files"][0]["path"], encoding="utf-8"))
    exp_item = next(i for i in data["items"] if i["note"] == "Inbox/Ambiguous Target.md")
    assert exp_item["confidence"] == "ambiguous"
    assert exp_item["auto_resolved"] is False


def test_m008_broken_relationship_trace(main_vault: str, out_dir: str) -> None:
    """M008-T04: Trace broken relationship across relationships, health, and exports."""
    scan = scan_vault(main_vault)
    inv = inventory.build_inventory(scan)
    
    # 1. Relationships Inbox
    inbox = relationships.build_inbox(scan)
    broken_items = [i for i in inbox["items"] if i["kind"] == "broken_link"]
    assert len(broken_items) == 1
    assert broken_items[0]["value"] == "[[Missing Person]]"
    assert broken_items[0]["note"] == "Meetings/2026-01-05 Kickoff.md"
    
    # 2. Health report
    report = health.health_report(scan, inv)
    broken_findings = [f for f in report["findings"] if f["category"] == "broken_relationship"]
    assert len(broken_findings) == 1
    assert "Meetings/2026-01-05 Kickoff.md" in broken_findings[0]["affected_notes"]
    
    # 3. Export artifact
    res = exports.export_artifact("health", report, main_vault, out_dir)
    data = json.load(open(res["files"][0]["path"], encoding="utf-8"))
    exp_broken = [f for f in data["findings"] if f["category"] == "broken_relationship"]
    assert len(exp_broken) == 1


def test_m008_canonical_target_provenance(main_vault: str) -> None:
    """M008-T05: Verify canonical target refers to entity note, never source note."""
    scan = scan_vault(main_vault)
    inbox = relationships.build_inbox(scan)
    for item in inbox["items"]:
        if item["kind"] == "link_upgrade_candidate":
            source = item["note"]
            candidates = item["candidates"]
            for target in candidates:
                assert target != source, f"Target {target} should not be source note {source}"


def test_m008_export_parity(main_vault: str, out_dir: str) -> None:
    """M008-T08: Direct API vs exported artifact parity."""
    scan = scan_vault(main_vault)
    inv = inventory.build_inventory(scan)
    disc = inventory.discovery_report(scan, inv)
    
    res = exports.export_artifact("discovery", disc, main_vault, out_dir)
    data = json.load(open(res["files"][0]["path"], encoding="utf-8"))
    
    assert data["summary"] == disc["summary"]
    assert len(data["findings"]) == len(disc["findings"])
