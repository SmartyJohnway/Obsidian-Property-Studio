"""Integration Regression Oracle (M003).

Freezes the 10 Round 2 hidden-regression contracts (INT-R2-001 ... INT-R2-010).
These tests ensure no hidden regressions or donor defects are imported.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import pytest

from app.core import design, exports, fill, health, inventory, manifest, refactor, relationships
from app.core.manifest import assert_unchanged, vault_manifest
from app.core.model import Schema, SchemaProperty, StorageType, UIControl
from app.core.scanner import note_name_index, scan_vault


def test_int_r2_001_malformed_not_ordinary_no_properties(main_vault: str) -> None:
    """INT-R2-001: Malformed YAML is explicitly counted and not lumped into property-free notes."""
    scan = scan_vault(main_vault)
    inv = inventory.build_inventory(scan)
    
    summary = scan.summary()
    assert summary["notes_with_parse_failure"] == 3
    assert summary["notes_without_properties"] == 2  # Only genuine empty notes
    
    # Check individual unreadable notes
    unreadable_paths = {n.path for n in scan.notes if n.parse_failed}
    assert "Notes/Malformed.md" in unreadable_paths
    
    prop_free_paths = {n.path for n in scan.notes if n.parse_status.value == "no_frontmatter"}
    assert "Notes/No Properties.md" in prop_free_paths
    
    # Malformed notes must NOT be in notes_without_properties
    for p in unreadable_paths:
        assert p not in prop_free_paths, f"Malformed note {p} incorrectly listed in notes_without_properties"


def test_int_r2_002_duplicate_key_ambiguity_survives_refactor(main_vault: str) -> None:
    """INT-R2-002: A note with duplicate keys survives into manual review / excluded ambiguity."""
    scan = scan_vault(main_vault)
    plan = refactor.plan_normalize(
        scan,
        key="status",
        canonical_overrides={"draft": "draft", "active": "active"},
    )
    
    excluded_notes = {item["note"] for item in plan.get("excluded", [])}
    assert "Notes/Duplicate Key.md" in excluded_notes, (
        f"Duplicate key note must be excluded/marked for manual review, got {excluded_notes}"
    )


def test_int_r2_003_ambiguous_fill_fails_closed(tmp_path: Path) -> None:
    """INT-R2-003: When multiple same-name targets exist, fill must fail closed (require explicit path)."""
    vault_dir = str(tmp_path / "ambig_vault")
    os.makedirs(os.path.join(vault_dir, "Companies"), exist_ok=True)
    os.makedirs(os.path.join(vault_dir, "Vendors"), exist_ok=True)
    with open(os.path.join(vault_dir, "Companies", "ACME.md"), "w", encoding="utf-8") as f:
        f.write("---\nname: ACME Corp\n---\n")
    with open(os.path.join(vault_dir, "Vendors", "ACME.md"), "w", encoding="utf-8") as f:
        f.write("---\nname: ACME Supplies\n---\n")
    
    scan = scan_vault(vault_dir)
    note_idx = note_name_index(scan)
    
    schema = Schema(
        name="test_equipment",
        properties=[
            SchemaProperty(
                name="company",
                storage_type=StorageType.TEXT,
                ui_control=UIControl.NOTE_LINK,
                required=True,
                reason="Supplier company",
            )
        ],
    )
    
    # 1. Unresolved generic target "ACME" with note_index should fail-closed
    preview = fill.fill_preview(schema, {"company": "ACME"}, note_index=note_idx)
    assert not preview["valid"], "Ambiguous note-link Fill must fail closed (valid must be False)"
    assert any("ambiguous" in err.lower() or "matches 2 notes" in err.lower() or "matches" in err.lower() for err in preview["errors"]), (
        f"Expected ambiguity error in errors, got: {preview['errors']}"
    )
    
    # 2. When explicit target is given (e.g. Companies/ACME.md or Companies/ACME), it must succeed
    preview_explicit = fill.fill_preview(schema, {"company": "Companies/ACME"}, note_index=note_idx)
    assert preview_explicit["valid"], f"Explicit target must pass, got errors: {preview_explicit['errors']}"
    assert "[[Companies/ACME]]" in preview_explicit["yaml"] or "[[Companies/ACME.md]]" in preview_explicit["yaml"]


def test_int_r2_004_relationship_canonical_target_is_entity(main_vault: str) -> None:
    """INT-R2-004: Relationship canonical target must resolve to the entity note, not the source note."""
    scan = scan_vault(main_vault)
    inbox = relationships.build_inbox(scan)
    items = inbox.get("items", [])
    
    # Find suggestion for Equipment/Microscope.md project -> Apollo
    mic_item = next(
        (item for item in items if item["note"] == "Equipment/Microscope.md" and item["property"] == "project"),
        None,
    )
    assert mic_item is not None, f"Expected relationship item for Microscope project in {items}"
    
    candidates = mic_item.get("candidates", [])
    assert candidates == ["Projects/Apollo.md"]
    # The resolved target is the entity Projects/Apollo.md, NOT the source note Equipment/Microscope.md
    assert "Projects/Apollo.md" in candidates
    assert "Equipment/Microscope.md" not in candidates


def test_int_r2_005_no_false_confirmed_ambiguity(main_vault: str) -> None:
    """INT-R2-005: A relationship finding with multiple targets cannot be marked confirmed."""
    scan = scan_vault(main_vault)
    inbox = relationships.build_inbox(scan)
    items = inbox.get("items", [])
    
    # Inbox/Ambiguous Target.md has project: Duplicate Name which matches A/Duplicate Name and B/Duplicate Name
    ambig_item = next(
        (item for item in items if item["note"] == "Inbox/Ambiguous Target.md" and item["property"] == "project"),
        None,
    )
    assert ambig_item is not None, "Expected item for Inbox/Ambiguous Target.md"
    assert ambig_item["kind"] == "ambiguous_link"
    assert ambig_item["confidence"] == "ambiguous"
    assert ambig_item.get("auto_resolved") is False
    assert ambig_item.get("proposed_value") is None
    assert len(ambig_item.get("candidates", [])) == 2


def test_int_r2_006_equipment_goal_does_not_route_to_reading() -> None:
    """INT-R2-006: Equipment/procurement prompt does not incorrectly route to Reading/Books."""
    prompt = "I want to manage equipment by project, vendor, procurement status, and review date."
    recipes = design.suggest_recipes(prompt)
    assert recipes[0]["id"] == "equipment", f"Expected equipment recipe first, got {recipes[0]['id']}"
    
    schema = design.build_schema(prompt)
    assert schema.name == "equipment"
    assert "reading" not in schema.name.lower() and "book" not in schema.name.lower()


def test_int_r2_007_normalize_counts_affected_notes_coherently(main_vault: str) -> None:
    """INT-R2-007: Manual-review summary distinguishes affected notes count from occurrences."""
    scan = scan_vault(main_vault)
    plan = refactor.plan_normalize(scan, "status")
    
    summary = plan["summary"]
    notes_to_change = summary["notes_to_change"]
    # Verify notes_to_change represents the sum of unique notes to change in groups
    sum_unique_notes = sum(len(c["notes_to_change"]) for c in plan["changes"])
    assert notes_to_change == sum_unique_notes


def test_int_r2_008_output_completeness_readback(main_vault: str, out_dir: str) -> None:
    """INT-R2-008: Exported JSON and Markdown retain all findings without silent truncation."""
    scan = scan_vault(main_vault)
    inv = inventory.build_inventory(scan)
    schema = design.build_schema("equipment", "equipment")
    report = health.health_report(scan, inv, schema)
    
    export_res = exports.export_artifact("health", report, scan.vault_path, out_dir)
    assert export_res["verification"]["no_silent_omission"] is True
    
    json_path = export_res["files"][0]["path"]
    written = json.load(open(json_path, encoding="utf-8"))
    
    original_findings = report.get("findings", [])
    exported_findings = written.get("findings", [])
    assert len(original_findings) == len(exported_findings), (
        f"Exported findings ({len(exported_findings)}) != original ({len(original_findings)})"
    )


def test_int_r2_009_vault_byte_for_byte_readonly(main_vault: str, out_dir: str) -> None:
    """INT-R2-009: Representative workflows cause 0 created, 0 modified, 0 renamed, 0 deleted."""
    before = vault_manifest(main_vault)
    
    scan = scan_vault(main_vault)
    inv = inventory.build_inventory(scan)
    discovery = inventory.discovery_report(scan, inv)
    schema = design.build_schema("I want to manage my lab equipment", "equipment")
    design.review_schema_against_vault(schema, inv)
    fill.fill_preview(
        schema,
        {"type": "equipment", "status": "in use", "location": "lab", "owner": "Ada Lovelace"},
        note_name_index(scan),
    )
    plan = refactor.plan_rename(scan, "Project", "project")
    inbox = relationships.build_inbox(scan)
    report = health.health_report(scan, inv, schema, "type", "equipment")
    
    exports.export_artifact("discovery", discovery, main_vault, out_dir)
    exports.export_artifact("health", report, main_vault, out_dir)
    exports.export_artifact("inbox", inbox, main_vault, out_dir)
    exports.export_artifact("plan", plan, main_vault, out_dir)
    
    after = vault_manifest(main_vault)
    diff = assert_unchanged(before, after)
    
    assert diff["unchanged"] is True
    assert diff["files_created"] == 0
    assert diff["files_modified"] == 0
    assert diff["files_deleted"] == 0


def test_int_r2_010_deterministic_scan(main_vault: str) -> None:
    """INT-R2-010: Unchanged vault produces deterministic canonical scan results."""
    scan1 = scan_vault(main_vault)
    scan2 = scan_vault(main_vault)
    
    inv1 = inventory.build_inventory(scan1)
    inv2 = inventory.build_inventory(scan2)
    
    report1 = inventory.discovery_report(scan1, inv1)
    report2 = inventory.discovery_report(scan2, inv2)
    
    assert scan1.summary() == scan2.summary()
    assert sorted(inv1.properties.keys()) == sorted(inv2.properties.keys())
    assert report1 == report2
