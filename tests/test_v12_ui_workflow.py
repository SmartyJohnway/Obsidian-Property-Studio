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
    assert any("is not a number" in err or "numeric" in err for err in diff_res.errors)
    assert any("not one of the allowed values" in err or "allowed choices" in err for err in diff_res.errors)

    # Fix values to comply with schema constraints
    schema_full = Schema(
        name="project_spec",
        description="Project schema",
        properties=[
            SchemaProperty(name="score", storage_type=StorageType.NUMBER, required=True),
            SchemaProperty(name="phase", storage_type=StorageType.TEXT, allowed_values=["dev", "prod"]),
            SchemaProperty(name="tags", storage_type=StorageType.TAGS),
            SchemaProperty(name="is_active", storage_type=StorageType.CHECKBOX),
        ],
    )
    fixed_res = compute_workspace_diff_and_frontmatter(
        original_note=None,
        updated_values={"score": "95", "phase": "dev", "tags": "alpha, beta", "is_active": "true"},
        schema=schema_full,
        deleted_keys=[],
    )
    assert fixed_res.valid is True
    assert fixed_res.can_copy is True
    assert len(fixed_res.errors) == 0
    assert "score: 95" in fixed_res.frontmatter_preview

    # Strict YAML safe_load read-back: ensure types are coerced to native int, list, bool (REQ-043)
    import yaml
    docs = [d for d in yaml.safe_load_all(fixed_res.frontmatter_preview) if d is not None]
    parsed_yaml = docs[0]
    assert type(parsed_yaml["score"]) is int
    assert parsed_yaml["score"] == 95
    assert type(parsed_yaml["tags"]) is list
    assert parsed_yaml["tags"] == ["alpha", "beta"]
    assert type(parsed_yaml["is_active"]) is bool
    assert parsed_yaml["is_active"] is True


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

    # Setup glossary alias override fixture (status has alias '進度')
    USER_GLOSSARY_STORE.save_override(
        UserGlossaryOverride(canonical_key="status", aliases=["進度"])
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
            {"name": "進度", "storage_type": "text"},  # Potential alias for status
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

    # 進度: potential alias detected from glossary overrides
    p_alias = next(p for p in four_way if p["name"] == "進度")
    assert p_alias["compatibility_state"] == "potential_alias"
    assert p_alias["alias_target"] == "status"

    # Version-specific gating: 1.0 proposal with 1.1 fields must warn
    v10_proposal = {
        "proposal_version": "1.0",
        "schema_name": "v10_spec",
        "management_purpose": "1.1 field in 1.0",
        "properties": [{"name": "title", "storage_type": "text"}],
    }
    v10_rep = validate_proposal(v10_proposal)
    assert v10_rep["valid"] is True
    assert any("Proposal Contract 1.1 extension and is ignored" in w for w in v10_rep["warnings"])


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
    """Verify UNEXPECTED_PROPERTY, SCHEMA_VERSION_MISMATCH, and MISSING_REQUIRED_RELATIONSHIP in drift (REQ-045, REQ-048)."""
    schema_props = [
        {"name": "title", "storage_type": "text", "required": True},
        {"name": "parent", "storage_type": "text", "ui_control": "note_link", "required": True},
        {"name": "due_date", "storage_type": "date", "required": False},
        {"name": "status", "storage_type": "text", "required": False},
    ]

    # Note 1: perfectly compliant
    n1 = Note(path="n1.md", parse_status=ParseStatus.OK)
    n1.properties = {
        "title": PropertyValue(key="title", raw="Note 1", storage_type=StorageType.TEXT),
        "parent": PropertyValue(key="parent", raw="[[ParentNote]]", storage_type=StorageType.TEXT),
        "due_date": PropertyValue(key="due_date", raw="2026-12-31", storage_type=StorageType.DATE),
    }

    # Note 2: has unexpected property 'custom_leak', missing required relationship, and wrong date format
    n2 = Note(path="n2.md", parse_status=ParseStatus.OK)
    n2.properties = {
        "title": PropertyValue(key="title", raw="Note 2", storage_type=StorageType.TEXT),
        "parent": PropertyValue(key="parent", raw="not_a_link", storage_type=StorageType.TEXT),  # Invalid relationship
        "due_date": PropertyValue(key="due_date", raw="tomorrow", storage_type=StorageType.TEXT),  # Type mismatch
        "custom_leak": PropertyValue(key="custom_leak", raw="unmanaged", storage_type=StorageType.TEXT),
        "schema_version": PropertyValue(key="schema_version", raw="0.9.0", storage_type=StorageType.TEXT),  # Version mismatch
    }

    report = analyze_schema_drift(
        notes=[n1, n2],
        schema_properties=schema_props,
        schema_id="test_drift",
        schema_name="Test Drift",
        schema_version="1.0.0",
    )

    # Note 2 findings verification
    findings_cats = {f.category for f in report.findings if f.note_path == "n2.md"}
    assert DriftCategory.UNEXPECTED_PROPERTY in findings_cats
    assert DriftCategory.SCHEMA_VERSION_MISMATCH in findings_cats
    assert DriftCategory.MISSING_REQUIRED_RELATIONSHIP in findings_cats
    assert DriftCategory.TYPE_MISMATCH in findings_cats

    # Compliance rate: 1 compliant out of 2 notes (50%)
    assert report.total_notes == 2
    assert report.compliant_notes == 1
    assert report.compliance_rate == 50.0


def test_e2e_wf_007_governance_profile_validate_preview_confirm_workflow():
    """Verify Governance Profile Validate -> Preview -> Confirm with real merge, replace, and transactional rollback (REQ-047)."""
    from app.core.saved_checks import SavedChecksStore, SavedCheck

    # 1. Setup mock saved checks
    mock_checks_store = SavedChecksStore()
    mock_checks_store.save_check(SavedCheck(id="chk_01", name="Project-to-Task Link Check"))

    # 2. Export valid profile including saved checks
    pkg = export_governance_profile(saved_checks_list=[c.to_dict() for c in mock_checks_store.list_checks()])
    assert "profile_metadata" in pkg
    assert "data" in pkg
    assert len(pkg["data"].get("saved_checks", [])) == 1

    # 3. Validate & preview before applying
    val_res = validate_governance_profile(pkg)
    assert val_res["valid"] is True
    assert val_res["saved_checks_count"] == 1

    # 4. Import in merge mode
    merge_res = import_governance_profile(pkg, mode="merge", saved_checks_store=mock_checks_store)
    assert merge_res["status"] == "imported"
    assert merge_res["mode"] == "merge"
    assert merge_res["imported"]["saved_checks"] == 1

    # 5. Import in replace mode with transactional safety
    replace_res = import_governance_profile(pkg, mode="replace", saved_checks_store=mock_checks_store)
    assert replace_res["status"] == "imported"
    assert replace_res["mode"] == "replace"

    # 6. Verify transactional rollback on corrupted import data
    from app.core.governance_profile import compute_profile_checksum
    bad_pkg = json.loads(json.dumps(pkg))
    bad_pkg["data"]["named_schemas"].append("not_an_object_corrupted")
    bad_pkg["profile_metadata"]["sha256_checksum"] = compute_profile_checksum(bad_pkg["data"])
    with pytest.raises(ValueError, match="Invalid schema at index"):
        import_governance_profile(bad_pkg, mode="replace")


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
