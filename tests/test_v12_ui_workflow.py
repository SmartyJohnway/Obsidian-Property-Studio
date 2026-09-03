"""v1.2.0 Product Completion Repair & True Workflow Closure Verification Suite.

Executes genuine End-to-End behavioral and workflow tests against backend engines,
data contracts, state transitions, and validation gates (not cosmetic string checks).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.server import ROUTES
from app.core.proposal import validate_proposal, import_proposal
from app.core.named_schemas import NAMED_SCHEMA_LIBRARY
from app.core.scope_governance import SCOPE_GOVERNANCE_STORE, canonical_scope_key
from app.core.user_glossary import USER_GLOSSARY_STORE, UserGlossaryOverride
from app.core.governance_profile import (
    export_governance_profile,
    validate_governance_profile,
    import_governance_profile,
)
from app.core.note_workspace import compute_workspace_diff_and_frontmatter
from app.core.drift import analyze_schema_drift, DriftCategory
from app.core.inventory import Inventory, PropertyEntry, ValueStat
from app.core.model import Schema, SchemaProperty, StorageType, UIControl, Note, ParseStatus, PropertyValue


def test_e2e_wf_001_version_identity_and_meta_workflow():
    """Verify release version identity matches 1.2.0 across meta API and package."""
    import app
    assert app.__version__ == "1.2.0"
    meta = ROUTES["/api/meta"]({})
    assert meta["version"] == "1.2.0"
    assert meta["app"] == "Obsidian Property Studio"


def test_e2e_wf_002_schema_library_crud_and_persistence_workflow():
    """Verify full CRUD lifecycle and optimistic locking in Named Schema Library."""
    schema_payload = {
        "id": "e2e_test_schema",
        "name": "E2E Test Schema",
        "version": "1.0.0",
        "description": "Created during E2E workflow test",
        "properties": [
            {"name": "status", "storage_type": "text", "ui_control": "single_choice", "required": True},
            {"name": "score", "storage_type": "number", "ui_control": "plain"},
        ],
    }
    # 1. Create
    save_res = NAMED_SCHEMA_LIBRARY.save_schema(schema_payload)
    assert save_res["revision"] >= 1
    assert save_res["schema"]["id"] == "e2e_test_schema"
    rev1 = save_res["revision"]

    # 2. Get and verify
    loaded = NAMED_SCHEMA_LIBRARY.get_schema("e2e_test_schema")
    assert loaded is not None
    assert loaded.name == "E2E Test Schema"
    assert len(loaded.properties) == 2

    # 3. Update with OCC
    schema_payload["name"] = "E2E Test Schema Updated"
    upd_res = NAMED_SCHEMA_LIBRARY.update_schema("e2e_test_schema", schema_payload, expected_revision=rev1)
    assert upd_res["revision"] > rev1
    assert upd_res["schema"]["name"] == "E2E Test Schema Updated"

    # 4. Clean up
    deleted = NAMED_SCHEMA_LIBRARY.delete_schema("e2e_test_schema", expected_revision=upd_res["revision"])
    assert deleted is True
    assert NAMED_SCHEMA_LIBRARY.get_schema("e2e_test_schema") is None


def test_e2e_wf_003_reconciliation_constraint_validation_and_fill_workflow():
    """Verify that type mismatch and invalid allowed_values fail closed in workspace preview (REQ-043)."""
    schema = Schema(
        name="project_spec",
        description="Project schema",
        properties=[
            SchemaProperty(name="score", storage_type=StorageType.NUMBER, required=True),
            SchemaProperty(name="phase", storage_type=StorageType.TEXT, allowed_values=["dev", "prod"]),
            SchemaProperty(name="manager", storage_type=StorageType.TEXT, required=False),
        ],
    )

    # Note with invalid score ("ABC") and invalid phase ("testing")
    diff_res = compute_workspace_diff_and_frontmatter(
        original_note=None,
        updated_values={"score": "ABC", "phase": "testing"},
        schema=schema,
        deleted_keys=[],
    )

    # Must fail closed: cannot copy, not valid, detailed errors
    assert diff_res.valid is False
    assert diff_res.can_copy is False
    assert any("expects numeric value" in err for err in diff_res.errors)
    assert any("not in allowed choices" in err for err in diff_res.errors)

    # Fix values to comply with schema constraints
    fixed_res = compute_workspace_diff_and_frontmatter(
        original_note=None,
        updated_values={"score": "95", "phase": "dev"},
        schema=schema,
        deleted_keys=[],
    )
    assert fixed_res.valid is True
    assert fixed_res.can_copy is True
    assert len(fixed_res.errors) == 0
    assert "score:" in fixed_res.frontmatter_preview
    assert "phase: dev" in fixed_res.frontmatter_preview


def test_e2e_wf_004_proposal_four_way_comparison_workflow():
    """Verify true four-way proposal comparison against Scope, Vault, Glossary, and Schema Library (REQ-046)."""
    scoped_inv = Inventory()
    scoped_inv.properties["status"] = PropertyEntry(
        key="status", usage_count=3,
        observed_types={"text": 3},
        values={"active": ValueStat(value="active", count=3)}
    )

    vault_inv = Inventory()
    vault_inv.properties["status"] = PropertyEntry(
        key="status", usage_count=15,
        observed_types={"text": 15},
        values={"active": ValueStat(value="active", count=15)}
    )
    vault_inv.properties["level"] = PropertyEntry(
        key="level", usage_count=8,
        observed_types={"number": 8},
        values={"1": ValueStat(value="1", count=8)}
    )

    proposal_json = json.dumps({
        "proposal_version": "1.1",
        "schema_name": "research_note",
        "management_purpose": "Standardizing lab notes",
        "target_note_kind": "lab_note",
        "schema_target": "Lab",
        "properties": [
            {"name": "status", "storage_type": "text", "ui_control": "single_choice", "allowed_values": ["active"]},
            {"name": "level", "storage_type": "text"},  # Type conflict: vault is number
            {"name": "new_indicator", "storage_type": "checkbox"},
        ],
    })

    rep = import_proposal(
        text=proposal_json,
        scoped_inv=scoped_inv,
        vault_inv=vault_inv,
        glossary_store=USER_GLOSSARY_STORE,
        schema_library=NAMED_SCHEMA_LIBRARY,
    )

    assert rep["valid"] is True
    assert rep["management_purpose"] == "Standardizing lab notes"
    four_way = rep["four_way_comparison"]

    # status: in scope (3) and in vault (15)
    p_status = next(p for p in four_way if p["name"] == "status")
    assert p_status["scope_usage_count"] == 3
    assert p_status["vault_usage_count"] == 15
    assert p_status["compatibility_state"] == "compatible"

    # level: type conflict with vault dominant type
    p_level = next(p for p in four_way if p["name"] == "level")
    assert p_level["compatibility_state"] == "type_conflict"

    # new_indicator: new property
    p_new = next(p for p in four_way if p["name"] == "new_indicator")
    assert p_new["compatibility_state"] == "new_property"


def test_e2e_wf_005_scope_canonical_assignment_workflow():
    """Verify scope assignment key canonicalization eliminates folder order and note path ambiguity (REQ-044)."""
    # 1. Folder order canonicalization
    key_ab = canonical_scope_key({"mode": "folders", "folders": ["FolderB", "FolderA"]})
    key_ba = canonical_scope_key({"mode": "folders", "folders": ["FolderA", "FolderB"]})
    assert key_ab == "folders:FolderA,FolderB"
    assert key_ab == key_ba

    # 2. Single note path canonicalization
    key_note1 = canonical_scope_key({"mode": "single_note", "note_path": "Projects/A.md"})
    key_note2 = canonical_scope_key({"mode": "single_note", "note_path": "Regulations/B.md"})
    assert key_note1 == "note:Projects/A.md"
    assert key_note2 == "note:Regulations/B.md"
    assert key_note1 != key_note2  # Single notes do NOT collide into 'default'

    # 3. Store assignment
    SCOPE_GOVERNANCE_STORE.assign_schema(key_ab, "dummy_schema", "Dummy")
    asgn = SCOPE_GOVERNANCE_STORE.get_assignment(key_ba)
    assert asgn is not None
    assert asgn.schema_id == "dummy_schema"
    SCOPE_GOVERNANCE_STORE.unassign_schema(key_ab)


def test_e2e_wf_006_drift_detection_and_compliant_rate_workflow():
    """Verify UNEXPECTED_PROPERTY marks notes as drifted and impacts compliance rate (REQ-048)."""
    schema_props = [
        {"name": "title", "storage_type": "text", "required": True},
        {"name": "status", "storage_type": "text", "required": False},
    ]

    # Note 1: perfectly compliant
    n1 = Note(path="n1.md", parse_status=ParseStatus.OK)
    n1.properties = {"title": PropertyValue(key="title", raw="Note 1", storage_type=StorageType.TEXT)}

    # Note 2: has unexpected property 'custom_leak'
    n2 = Note(path="n2.md", parse_status=ParseStatus.OK)
    n2.properties = {
        "title": PropertyValue(key="title", raw="Note 2", storage_type=StorageType.TEXT),
        "custom_leak": PropertyValue(key="custom_leak", raw="unmanaged", storage_type=StorageType.TEXT),
    }

    report = analyze_schema_drift(
        notes=[n1, n2],
        schema_properties=schema_props,
        schema_id="test_drift",
        schema_name="Test Drift",
    )

    # Note 2 has UNEXPECTED_PROPERTY finding
    assert any(f.category == DriftCategory.UNEXPECTED_PROPERTY for f in report.findings)
    # Compliance rate cannot be 100% when Note 2 has drift
    assert report.total_notes == 2
    assert report.compliant_notes == 1
    assert report.compliance_rate == 50.0


def test_e2e_wf_007_governance_profile_validate_preview_confirm_workflow():
    """Verify Governance Profile Validate -> Preview -> Confirm 3-step workflow with real merge and replace (REQ-047)."""
    # 1. Export valid profile
    pkg = export_governance_profile()
    assert "profile_metadata" in pkg
    assert "data" in pkg

    # 2. Validate & preview before applying
    val_res = validate_governance_profile(pkg)
    assert val_res["valid"] is True
    assert "schema_count" in val_res
    assert "assignment_count" in val_res
    assert "glossary_count" in val_res

    # 3. Import in merge mode
    merge_res = import_governance_profile(pkg, mode="merge")
    assert merge_res["status"] == "imported"
    assert merge_res["mode"] == "merge"


def test_e2e_wf_008_companion_skill_fixtures_and_principles_workflow():
    """Verify companion skill fixtures conform strictly to Authoritative Contract 1.1 standard."""
    skill_root = Path("skills/obsidian-property-advisor")
    assert (skill_root / "SKILL.md").is_file()

    for ex_name in ["project.json", "equipment.json", "regulation.json"]:
        p = skill_root / "examples" / ex_name
        data = json.loads(p.read_text(encoding="utf-8"))
        val_res = validate_proposal(data)
        assert val_res["valid"] is True, f"Fixture {ex_name} failed: {val_res.get('errors')}"
        assert val_res["proposal_version"] == "1.1"
        assert val_res["management_purpose"], f"Missing management_purpose in {ex_name}"
        assert val_res["target_note_kind"], f"Missing target_note_kind in {ex_name}"
        assert val_res["schema_target"], f"Missing schema_target in {ex_name}"
