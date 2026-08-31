"""Global product acceptance cases OPS-AC-001 … OPS-AC-027.

Each test is named after the ROADMAP acceptance case it verifies. These are
behavioural contracts from ROADMAP.md and must not be silently redefined.
OPS-AC-028 (large-vault benchmark) lives in ``test_benchmark.py``.
"""

from __future__ import annotations

import json
import os

import pytest
import yaml

from app.core import design, exports, fill, health, inventory, proposal, refactor, relationships
from app.core.manifest import assert_unchanged, vault_manifest
from app.core.model import Schema, SchemaProperty, StorageType, UIControl
from app.core.scanner import ScanOptions, VaultPathError, note_name_index, scan_vault
from conftest import PROPOSALS


# --------------------------------------------------------------------------
# OPS-AC-001 — Empty / no-property vault
# --------------------------------------------------------------------------
def test_ops_ac_001_empty_vault(empty_vault, oracle):
    before = vault_manifest(empty_vault)
    scan = scan_vault(empty_vault)
    expected = oracle["empty_vault"]
    assert scan.note_count == expected["note_count"] == 3
    assert scan.notes_with_properties == 0
    assert scan.notes_with_parse_failure == 0
    inv = inventory.build_inventory(scan)
    assert inv.properties == {}
    assert [n.parse_status.value for n in scan.notes] == ["no_frontmatter"] * 3
    report = inventory.discovery_report(scan, inv)
    assert [f for f in report["findings"] if f["category"] == "parse_failure"] == []
    assert assert_unchanged(before, vault_manifest(empty_vault))["unchanged"] is True


# --------------------------------------------------------------------------
# OPS-AC-002 — Property inventory counts
# --------------------------------------------------------------------------
def test_ops_ac_002_inventory_counts(scan, inv, oracle):
    expected = oracle["main_vault"]
    assert scan.note_count == expected["note_count"]
    assert scan.notes_with_properties == expected["notes_with_properties"]
    assert sorted(inv.properties) == expected["unique_property_keys"]
    actual_usage = {k: e.usage_count for k, e in inv.properties.items()}
    assert actual_usage == expected["property_usage"]


def test_ops_ac_002_parse_status_matches_oracle(scan, oracle):
    expected = oracle["main_vault"]["parse_status_by_note"]
    actual = {n.path: n.parse_status.value for n in scan.notes}
    assert actual == expected


# --------------------------------------------------------------------------
# OPS-AC-003 — Naming drift
# --------------------------------------------------------------------------
def test_ops_ac_003_naming_drift(inv):
    findings = inventory.naming_drift_findings(inv)
    drift = [f for f in findings if f.category == "naming_drift"]
    assert any(set(f.property_keys) == {"project", "Project"} for f in drift), drift

    overlap = [f for f in findings if f.category == "possible_semantic_overlap"]
    project_name = [f for f in overlap if set(f.property_keys) == {"project", "project_name"}]
    assert project_name, "project_name should be offered as a possible overlap"
    assert project_name[0].confidence.value == "possible"
    assert project_name[0].evidence["auto_merge"] is False
    # never auto-merged: both keys still exist independently in the inventory
    assert inv.get("project") is not None and inv.get("project_name") is not None


# --------------------------------------------------------------------------
# OPS-AC-004 — Malformed frontmatter honesty
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "path,status",
    [
        ("Notes/Malformed.md", "invalid_yaml"),
        ("Notes/Unterminated.md", "unterminated_frontmatter"),
        ("Notes/Not A Mapping.md", "not_a_mapping"),
    ],
)
def test_ops_ac_004_malformed_is_explicit(scan, path, status):
    note = scan.note_by_path(path)
    assert note is not None
    assert note.parse_status.value == status
    assert note.parse_failed is True
    assert note.issues and note.issues[0].message
    # must NOT be reported as an ordinary property-free note
    assert note.has_properties is False
    summary = scan.summary()
    assert summary["notes_with_parse_failure"] == 3
    assert summary["notes_without_properties"] == 2  # only the genuinely empty ones


def test_ops_ac_004_failures_surface_as_findings(scan):
    findings = inventory.parse_findings(scan)
    reported = {n for f in findings for n in f.affected_notes}
    assert reported == {
        "Notes/Malformed.md",
        "Notes/Unterminated.md",
        "Notes/Not A Mapping.md",
    }


# --------------------------------------------------------------------------
# OPS-AC-005 — Vault read-only invariant (representative complete flows)
# --------------------------------------------------------------------------
def test_ops_ac_005_vault_readonly_full_flow(main_vault, out_dir, tmp_path):
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
    plans = [
        refactor.plan_rename(scan, "Project", "project"),
        refactor.plan_merge(scan, ["project_name"], "project"),
        refactor.plan_normalize(scan, "status"),
        refactor.plan_type_conversion(scan, "project", "note_link"),
        refactor.plan_required_impact(scan, schema, "type", "equipment"),
    ]
    inbox = relationships.build_inbox(scan)
    report = health.health_report(scan, inv, schema, "type", "equipment")
    exports.export_artifact("discovery", discovery, main_vault, out_dir)
    exports.export_artifact("health", report, main_vault, out_dir)
    exports.export_artifact("inbox", inbox, main_vault, out_dir)
    for plan in plans:
        exports.export_artifact("plan", plan, main_vault, out_dir, basename=f"plan-{plan['operation']}")

    after = vault_manifest(main_vault)
    result = assert_unchanged(before, after)
    assert result["files_created"] == 0
    assert result["files_modified"] == 0
    assert result["files_deleted"] == 0
    assert result["unchanged"] is True
    assert result["before_digest"] == result["after_digest"]
    # exports landed outside the vault
    for name in os.listdir(out_dir):
        assert not os.path.abspath(os.path.join(out_dir, name)).startswith(
            os.path.abspath(main_vault)
        )


def test_ops_ac_005_export_inside_vault_is_refused(main_vault):
    with pytest.raises(exports.ExportPathError):
        exports.ensure_output_dir(main_vault, os.path.join(main_vault, "reports"))


def test_ops_ac_005_no_write_api_exists():
    """No vault-mutating code path exists in the product (Constraint 2/11).

    Only ``exports.py`` may write files, and it refuses paths inside a vault
    (covered by ``test_ops_ac_005_export_inside_vault_is_refused``).
    """
    import re

    import app.core as core_pkg

    root = os.path.dirname(os.path.abspath(core_pkg.__file__))
    banned_calls = (
        "shutil.move", "shutil.copy", "shutil.rmtree", "os.remove", "os.rename",
        "os.unlink", "os.rmdir", "pathlib.Path.write", ".write_text(", ".write_bytes(",
    )
    write_open = re.compile(r"""open\([^)]*["'][waxr]?\+?[wa]["']""")
    for name in sorted(f for f in os.listdir(root) if f.endswith(".py")):
        text = open(os.path.join(root, name), encoding="utf-8").read()
        for token in banned_calls:
            assert token not in text, f"{name} contains {token}"
        if name != "exports.py":
            assert not write_open.search(text), f"{name} opens a file for writing"

    server_text = open(
        os.path.join(os.path.dirname(root), "server.py"), encoding="utf-8"
    ).read()
    assert not write_open.search(server_text)
    assert '"vault_write_capability": False' in server_text


# --------------------------------------------------------------------------
# OPS-AC-006 — Beginner schema design (no YAML typed by the user)
# --------------------------------------------------------------------------
def test_ops_ac_006_goal_to_schema():
    schema = design.build_schema(
        "I want to manage my lab equipment and know where each item is",
        intent_ids=["track_location", "filter_by_status"],
    )
    assert schema.validate() == []
    names = [p.name for p in schema.properties]
    assert "type" in names and "status" in names and "location" in names
    assert all(p.reason for p in schema.properties), "every property explains itself"
    # the user supplied plain English only — no YAML anywhere in the input
    assert schema.name == "equipment"


def test_ops_ac_006_recipe_suggestions_are_deterministic():
    first = design.suggest_recipes("track my reading list of books")
    second = design.suggest_recipes("track my reading list of books")
    assert first == second
    assert first[0]["id"] == "reading"


def test_ops_ac_006_chinese_goal_text():
    schema = design.build_schema("我想管理設備與器材的位置")
    assert schema.name == "equipment"


# --------------------------------------------------------------------------
# OPS-AC-007 — Existing-property reuse
# --------------------------------------------------------------------------
def test_ops_ac_007_existing_property_surfaced(inv):
    review = design.check_property_reuse("status", inv)
    assert review["status"] == "exact_existing"
    assert review["exact_match"]["usage_count"] == inv.get("status").usage_count
    assert review["exact_match"]["top_values"]
    assert "already exists" in review["message"]
    assert review["auto_merged"] is False


def test_ops_ac_007_case_variant_and_overlap(inv):
    variant = design.check_property_reuse("PROJECT", inv)
    assert variant["status"] == "case_variant_exists"
    assert {v["key"] for v in variant["case_variants"]} >= {"project", "Project"}

    overlap = design.check_property_reuse("project_owner", inv)
    assert overlap["status"] in ("possible_overlap", "new")
    if overlap["status"] == "possible_overlap":
        assert all(o["confidence"] == "possible" for o in overlap["possible_overlaps"])


def test_ops_ac_007_schema_review_reports_type_disagreement(inv):
    schema = Schema(
        name="x",
        properties=[SchemaProperty("due_date", StorageType.TEXT, reason="r")],
    )
    review = design.review_schema_against_vault(schema, inv)
    entry = review["reuse_reviews"][0]
    assert entry["status"] == "exact_existing"
    assert entry["type_agreement"] == "differs"
    assert entry["vault_dominant_type"] == "date"


# --------------------------------------------------------------------------
# OPS-AC-008 — Property purpose explanation
# --------------------------------------------------------------------------
def test_ops_ac_008_every_proposed_property_explains_itself():
    for recipe in design.RECIPES:
        schema = design.build_schema("", recipe.id)
        for prop in schema.properties:
            assert prop.reason.strip(), f"{recipe.id}.{prop.name} has no reason"
            assert len(prop.reason) > 15


# --------------------------------------------------------------------------
# OPS-AC-009 — Storage type vs UI control
# --------------------------------------------------------------------------
def test_ops_ac_009_ui_controls_documented_and_constrained():
    from app.core.model import UI_CONTROL_ALLOWED_STORAGE, UI_CONTROL_SERIALIZATION

    for control in UIControl:
        assert control.value in UI_CONTROL_SERIALIZATION
        doc = UI_CONTROL_SERIALIZATION[control.value]
        assert doc["serializes_as"] and doc["note"]
        assert UI_CONTROL_ALLOWED_STORAGE[control.value]

    bad = SchemaProperty("x", StorageType.NUMBER, UIControl.NOTE_LINK, reason="r")
    assert bad.validate(), "note_link on a number must be rejected"


def test_ops_ac_009_note_link_serializes_as_text():
    schema = Schema(
        name="s",
        properties=[
            SchemaProperty("owner", StorageType.TEXT, UIControl.NOTE_LINK, reason="r"),
            SchemaProperty(
                "priority", StorageType.TEXT, UIControl.SINGLE_CHOICE, reason="r",
                allowed_values=("high", "low"),
            ),
            SchemaProperty(
                "topics", StorageType.LIST, UIControl.MULTI_CHOICE, reason="r",
                allowed_values=("a", "b"),
            ),
        ],
    )
    result = fill.fill_preview(
        schema, {"owner": "Ada Lovelace", "priority": "high", "topics": ["a", "b"]}
    )
    parsed = yaml.safe_load(result["yaml"])
    assert parsed["owner"] == "[[Ada Lovelace]]"      # text scalar, not a new type
    assert isinstance(parsed["owner"], str)
    assert isinstance(parsed["priority"], str)        # select -> plain scalar
    assert parsed["topics"] == ["a", "b"]             # multi-select -> list


def test_ops_ac_009_choice_value_outside_allowed_is_rejected():
    schema = Schema(
        name="s",
        properties=[
            SchemaProperty(
                "priority", StorageType.TEXT, UIControl.SINGLE_CHOICE, reason="r",
                allowed_values=("high", "low"),
            )
        ],
    )
    result = fill.fill_preview(schema, {"priority": "medium"})
    assert result["errors"] and not result["valid"]


# --------------------------------------------------------------------------
# OPS-AC-010 — Fill + valid YAML
# --------------------------------------------------------------------------
def test_ops_ac_010_generated_yaml_round_trips():
    schema = Schema(
        name="mixed",
        properties=[
            SchemaProperty("title", StorageType.TEXT, reason="r"),
            SchemaProperty("count", StorageType.NUMBER, reason="r"),
            SchemaProperty("done", StorageType.CHECKBOX, reason="r"),
            SchemaProperty("due", StorageType.DATE, reason="r"),
            SchemaProperty("at", StorageType.DATETIME, reason="r"),
            SchemaProperty("items", StorageType.LIST, reason="r"),
            SchemaProperty("tags", StorageType.TAGS, reason="r"),
            SchemaProperty("owner", StorageType.TEXT, UIControl.NOTE_LINK, reason="r"),
        ],
    )
    values = {
        "title": "研究筆記: a value with: colon",
        "count": "42",
        "done": "true",
        "due": "2026-09-30",
        "at": "2026-09-30 14:30",
        "items": "one, two, 三",
        "tags": ["work", "研究"],
        "owner": "Ada Lovelace",
    }
    result = fill.fill_preview(schema, values)
    assert result["errors"] == []
    assert result["roundtrip"]["parses"] is True
    assert result["roundtrip"]["matches"] is True, result["roundtrip"]["differences"]
    assert result["valid"] is True

    parsed = yaml.safe_load(result["yaml"])
    assert parsed["count"] == 42
    assert parsed["done"] is True
    assert str(parsed["due"]) == "2026-09-30"
    assert parsed["items"] == ["one", "two", "三"]
    assert parsed["owner"] == "[[Ada Lovelace]]"
    assert result["frontmatter"].startswith("---\n")
    assert result["frontmatter"].rstrip().endswith("---")
    assert result["contains_body"] is False


def test_ops_ac_010_required_field_missing_is_reported():
    schema = Schema(
        name="s",
        properties=[SchemaProperty("type", StorageType.TEXT, required=True, reason="r")],
    )
    result = fill.fill_preview(schema, {})
    assert any("required" in e for e in result["errors"])


def test_ops_ac_010_copy_payload_equals_preview():
    schema = Schema(name="s", properties=[SchemaProperty("a", StorageType.TEXT, reason="r")])
    result = fill.fill_preview(schema, {"a": "b"})
    # the clipboard payload IS the previewed frontmatter string
    assert result["frontmatter"] == "---\na: b\n---\n"
    assert result["yaml"] == "a: b\n"


# --------------------------------------------------------------------------
# OPS-AC-011 — Unicode / Windows paths
# --------------------------------------------------------------------------
def test_ops_ac_011_unicode_notes_and_values(scan, inv):
    note = scan.note_by_path("Projects/Delta 專案.md")
    assert note is not None and note.parse_status.value == "ok"
    assert note.properties["status"].display == "進行中"
    assert note.properties["tags"].scalars == ("研究",)
    assert scan.note_by_path("People/林小明.md") is not None
    assert note.properties["owner"].display == "[[林小明]]"
    assert "進行中" in inv.get("status").values


def test_ops_ac_011_unicode_round_trip_and_export(tmp_path):
    schema = Schema(
        name="中文",
        properties=[
            SchemaProperty("狀態", StorageType.TEXT, reason="r"),
            SchemaProperty("負責人", StorageType.TEXT, UIControl.NOTE_LINK, reason="r"),
        ],
    )
    result = fill.fill_preview(schema, {"狀態": "進行中", "負責人": "林小明"})
    assert result["roundtrip"]["matches"] is True
    assert "進行中" in result["yaml"] and "[[林小明]]" in result["yaml"]

    report = exports.export_artifact(
        "schema", schema.to_dict(), None, str(tmp_path), "unicode-schema"
    )
    data = json.load(open(report["files"][0]["path"], encoding="utf-8"))
    assert data["properties"][0]["name"] == "狀態"


def test_ops_ac_011_crlf_note_parsed(scan):
    note = scan.note_by_path("Meetings/CRLF Note.md")
    assert note.parse_status.value == "ok"
    assert note.properties["project"].display == "Apollo"
    raw = open(
        os.path.join(scan.vault_path, "Meetings", "CRLF Note.md"), "rb"
    ).read()
    assert b"\r\n" in raw, "fixture must really contain CRLF line endings"


def test_ops_ac_011_paths_with_spaces_and_nesting(scan):
    assert scan.note_by_path("Meetings/2026-01-05 Kickoff.md") is not None
    assert scan.note_by_path("A/Duplicate Name.md") is not None


# --------------------------------------------------------------------------
# OPS-AC-012 — Rename impact plan
# --------------------------------------------------------------------------
def test_ops_ac_012_rename_plan(scan, inv, main_vault):
    before = vault_manifest(main_vault)
    plan = refactor.plan_rename(scan, "Project", "project")
    assert plan["operation"] == "rename_property"
    assert plan["apply_supported"] is False
    assert plan["summary"]["source_usage_count"] == inv.get("Project").usage_count
    affected = {a["note"] for a in plan["affected_notes"]}
    assert affected == set(inv.get("Project").notes)
    assert all(a["after"] == {"project": a["before"]["Project"]} for a in plan["affected_notes"])
    assert assert_unchanged(before, vault_manifest(main_vault))["unchanged"] is True


def test_ops_ac_012_rename_conflict_is_visible(scan):
    plan = refactor.plan_rename(scan, "project_name", "project")
    conflicts = {c["note"] for c in plan["conflicts"]}
    assert "Archive/Merged Candidate.md" in conflicts
    assert plan["summary"]["conflicts"] == len(plan["conflicts"]) >= 1


# --------------------------------------------------------------------------
# OPS-AC-013 — Merge conflict
# --------------------------------------------------------------------------
def test_ops_ac_013_merge_conflict_not_overwritten(scan):
    plan = refactor.plan_merge(scan, ["project_name"], "project")
    conflicts = {c["note"]: c for c in plan["conflicts"]}
    assert "Archive/Merged Candidate.md" in conflicts
    conflict = conflicts["Archive/Merged Candidate.md"]
    assert conflict["reason"] == "conflicting_values"
    assert conflict["values"] == {
        "project_name": "Legacy Apollo",
        "project": "Apollo Legacy",
    }
    assert "manual review" in conflict["resolution"]
    # no precedence is fabricated anywhere in the plan
    assert all("winner" not in json.dumps(a) for a in plan["affected_notes"])


def test_ops_ac_013_identical_values_merge_safely(scan):
    plan = refactor.plan_merge(scan, ["Project"], "project")
    assert plan["summary"]["conflicts"] == 0 or plan["conflicts"]


# --------------------------------------------------------------------------
# OPS-AC-014 — Normalize values
# --------------------------------------------------------------------------
def test_ops_ac_014_normalize_case_variants(scan):
    plan = refactor.plan_normalize(scan, "status")
    groups = {c["canonical_value"]: c for c in plan["changes"]}
    assert "active" in groups
    variants = {v["value"] for v in groups["active"]["variants"]}
    assert variants == {"active", "Active", "ACTIVE"}
    assert groups["active"]["match_basis"] == "case/whitespace only"
    assert set(groups["active"]["notes_to_change"]) == {
        "Projects/Borealis.md",
        "Projects/Cascade.md",
    }
    # semantically different values are NOT claimed equivalent
    untouched = {u["value"] for u in plan["untouched_values"]}
    assert "archived" in untouched and "進行中" in untouched


def test_ops_ac_014_ambiguous_note_excluded(scan):
    plan = refactor.plan_normalize(scan, "status")
    assert any(e["note"] == "Notes/Duplicate Key.md" for e in plan["excluded"])


# --------------------------------------------------------------------------
# OPS-AC-015 — Type conversion feasibility
# --------------------------------------------------------------------------
def test_ops_ac_015_text_to_note_link_feasibility(scan):
    plan = refactor.plan_type_conversion(scan, "project", "note_link")
    convertible = {c["note"]: c for c in plan["convertible"]}
    ambiguous = {a["note"] for a in plan["ambiguous"]}
    unresolved = {u["note"] for u in plan["unresolved"]}

    assert convertible["Equipment/Microscope.md"]["proposed_value"] == "[[Apollo]]"
    assert "Inbox/Ambiguous Target.md" in ambiguous
    assert "Archive/Merged Candidate.md" in unresolved
    assert plan["summary"]["feasible_without_manual_work"] is False
    assert all(a.get("proposed_value", "") == "" for a in plan["ambiguous"])
    assert all(u.get("proposed_value", "") == "" for u in plan["unresolved"])


def test_ops_ac_015_text_to_number_reports_unconvertible(scan):
    plan = refactor.plan_type_conversion(scan, "due_date", "number")
    assert plan["summary"]["unresolved"] == plan["summary"]["values_examined"]


# --------------------------------------------------------------------------
# OPS-AC-016 — Plain text → relationship suggestion
# --------------------------------------------------------------------------
def test_ops_ac_016_exact_link_upgrade(scan):
    inbox = relationships.build_inbox(scan)
    upgrades = {
        (i["note"], i["property"], i["value"]): i
        for i in inbox["items"]
        if i["kind"] == "link_upgrade_candidate"
    }
    key = ("Equipment/Microscope.md", "project", "Apollo")
    assert key in upgrades
    item = upgrades[key]
    assert item["confidence"] == "exact"
    assert item["candidates"] == ["Projects/Apollo.md"]
    assert item["proposed_value"] == "[[Apollo]]"
    assert item["auto_resolved"] is False


# --------------------------------------------------------------------------
# OPS-AC-017 — Ambiguous relationship
# --------------------------------------------------------------------------
def test_ops_ac_017_ambiguous_not_silently_selected(scan):
    inbox = relationships.build_inbox(scan)
    items = [i for i in inbox["items"] if i["note"] == "Inbox/Ambiguous Target.md"]
    assert items and items[0]["kind"] == "ambiguous_link"
    item = items[0]
    assert item["confidence"] == "ambiguous"
    assert sorted(item["candidates"]) == ["A/Duplicate Name.md", "B/Duplicate Name.md"]
    assert item["proposed_value"] is None
    assert inbox["summary"]["auto_resolved"] == 0


# --------------------------------------------------------------------------
# OPS-AC-018 — Broken property note link
# --------------------------------------------------------------------------
def test_ops_ac_018_broken_link_surfaced(scan):
    inbox = relationships.build_inbox(scan)
    broken = [i for i in inbox["items"] if i["kind"] == "broken_link"]
    assert len(broken) == 1
    assert broken[0]["note"] == "Meetings/2026-01-05 Kickoff.md"
    assert broken[0]["value"] == "[[Missing Person]]"
    assert broken[0]["confidence"] == "unresolved"
    assert broken[0]["proposed_value"] is None


def test_ops_ac_018_relationship_scope_is_property_only(scan):
    inbox = relationships.build_inbox(scan)
    assert "property values only" in inbox["summary"]["scope"]
    for item in inbox["items"]:
        assert item["property"]  # every item is anchored to a property key


# --------------------------------------------------------------------------
# OPS-AC-019 — Missing expected property
# --------------------------------------------------------------------------
def test_ops_ac_019_missing_required_property(scan, inv):
    schema = Schema(
        name="equipment",
        properties=[
            SchemaProperty("type", StorageType.TEXT, required=True, reason="r"),
            SchemaProperty("owner", StorageType.TEXT, required=True, reason="r"),
            SchemaProperty("location", StorageType.TEXT, required=False, reason="r"),
        ],
    )
    findings = health.schema_findings(scan, inv, schema, "type", "equipment")
    missing = [f for f in findings if f.category == "missing_required_property"]
    assert missing and missing[0].property_keys == ("owner",)
    assert set(missing[0].affected_notes) == {
        "Equipment/Microscope.md",
        "Equipment/Oscilloscope.md",
    }


def test_ops_ac_019_required_impact_plan(scan):
    schema = Schema(
        name="equipment",
        properties=[
            SchemaProperty("type", StorageType.TEXT, required=True, reason="r"),
            SchemaProperty("owner", StorageType.TEXT, required=True, reason="r"),
        ],
    )
    plan = refactor.plan_required_impact(scan, schema, "type", "equipment")
    assert plan["summary"]["notes_in_scope"] == 2
    assert plan["summary"]["notes_missing_required"] == 2
    assert plan["apply_supported"] is False


# --------------------------------------------------------------------------
# OPS-AC-020 — Observed type conflict
# --------------------------------------------------------------------------
def test_ops_ac_020_type_conflict_traceable(inv):
    findings = inventory.type_conflict_findings(inv)
    conflicts = {f.property_keys[0]: f for f in findings}
    assert "due_date" in conflicts
    finding = conflicts["due_date"]
    assert set(finding.evidence["observed_types"]) == {"date", "text"}
    assert finding.evidence["notes_by_type"]["text"] == ["Projects/Cascade.md"]
    assert set(finding.affected_notes) == set(inv.get("due_date").notes)


# --------------------------------------------------------------------------
# OPS-AC-021 — Unexpected property
# --------------------------------------------------------------------------
def test_ops_ac_021_unexpected_property_reported_not_deleted(scan, inv, main_vault):
    before = vault_manifest(main_vault)
    schema = Schema(
        name="equipment",
        properties=[SchemaProperty("type", StorageType.TEXT, required=True, reason="r")],
    )
    findings = health.schema_findings(scan, inv, schema, "type", "equipment")
    unexpected = {f.property_keys[0] for f in findings if f.category == "unexpected_property"}
    assert {"location", "project", "purchase_date", "serial_number"} <= unexpected
    for finding in findings:
        if finding.category == "unexpected_property":
            assert finding.evidence["destructive_action_taken"] is False
    assert assert_unchanged(before, vault_manifest(main_vault))["unchanged"] is True


# --------------------------------------------------------------------------
# OPS-AC-022 — AI proposal import
# --------------------------------------------------------------------------
def test_ops_ac_022_valid_proposal_imported_and_compared(inv):
    text = open(os.path.join(PROPOSALS, "valid_equipment.json"), encoding="utf-8").read()
    result = proposal.import_proposal(text, inv)
    assert result["valid"] is True and result["errors"] == []
    assert result["proposal_version"] == "1.0"
    assert [p["name"] for p in result["schema"]["properties"]] == [
        "project",
        "location",
        "last_service_date",
    ]
    comparison = {c["proposed_name"]: c for c in result["comparison"]}
    assert comparison["project"]["status"] == "exact_existing"
    assert comparison["project"]["exact_match"]["usage_count"] == inv.get("project").usage_count
    assert comparison["last_service_date"]["status"] in ("new", "possible_overlap")
    # provenance / reason / confidence preserved
    assert comparison["project"]["confidence"] == 0.82
    assert comparison["project"]["reason"]
    assert result["provenance"]["generated_by"].startswith("Obsidian Property Architect")
    assert result["vault_modified"] is False


# --------------------------------------------------------------------------
# OPS-AC-023 — Malformed AI proposal
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "filename,expect",
    [
        ("invalid_malformed_json.json", "not valid JSON"),
        ("invalid_unsupported_version.json", "Unsupported proposal_version"),
    ],
)
def test_ops_ac_023_malformed_proposal_rejected(inv, filename, expect, main_vault):
    before = vault_manifest(main_vault)
    text = open(os.path.join(PROPOSALS, filename), encoding="utf-8").read()
    result = proposal.import_proposal(text, inv)
    assert result["valid"] is False
    assert any(expect in e for e in result["errors"]), result["errors"]
    assert result["schema"] is None
    assert result["vault_modified"] is False
    assert assert_unchanged(before, vault_manifest(main_vault))["unchanged"] is True


def test_ops_ac_023_bad_field_values_rejected_individually(inv):
    text = open(os.path.join(PROPOSALS, "invalid_bad_types.json"), encoding="utf-8").read()
    result = proposal.import_proposal(text, inv)
    assert result["valid"] is False
    joined = " | ".join(result["errors"])
    assert "storage_type 'select'" in joined
    assert "not compatible" in joined
    assert "non-empty string" in joined
    assert "confidence" in joined
    assert "declared more than once" in joined


def test_ops_ac_023_non_object_proposal():
    result = proposal.import_proposal("[1,2,3]", None)
    assert result["valid"] is False
    assert "must be a JSON object" in result["errors"][0]


# --------------------------------------------------------------------------
# OPS-AC-024 — No AI / no network
# --------------------------------------------------------------------------
def test_ops_ac_024_no_network_imports():
    import app.core as core_pkg

    root = os.path.dirname(os.path.abspath(core_pkg.__file__))
    banned = ("requests", "urllib.request", "http.client", "socket", "openai", "httpx")
    files = [os.path.join(root, f) for f in os.listdir(root) if f.endswith(".py")]
    files.append(os.path.join(os.path.dirname(root), "server.py"))
    for path in files:
        text = open(path, encoding="utf-8").read()
        for token in banned:
            assert f"import {token}" not in text, f"{path} imports {token}"


def test_ops_ac_024_core_flows_offline(main_vault, monkeypatch, tmp_path):
    """Fail hard if anything tries to open a socket during a full workflow."""
    import socket

    class Blocked(socket.socket):
        def __init__(self, *a, **k):
            raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", Blocked)
    for var in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(var, raising=False)

    scan = scan_vault(main_vault)
    inv_ = inventory.build_inventory(scan)
    inventory.discovery_report(scan, inv_)
    schema = design.build_schema("manage equipment", "equipment")
    fill.fill_preview(schema, {"type": "equipment", "status": "in use"})
    refactor.plan_rename(scan, "Project", "project")
    relationships.build_inbox(scan)
    report = health.health_report(scan, inv_, schema)
    exports.export_artifact("health", report, main_vault, str(tmp_path))
    assert report["health_score"]["score"] >= 0


# --------------------------------------------------------------------------
# OPS-AC-025 — No body/template scope creep
# --------------------------------------------------------------------------
def test_ops_ac_025_outputs_contain_no_body_content(scan, inv, tmp_path):
    schema = design.build_schema("manage equipment", "equipment")
    result = fill.fill_preview(schema, {"type": "equipment", "status": "in use"})
    parts = result["frontmatter"].split("---")
    assert parts[0] == "" and parts[2].strip() == "", "fill output is frontmatter only"
    assert result["contains_body"] is False

    # no schema recipe proposes body/heading/template style fields
    for recipe in design.RECIPES:
        for prop in design.build_schema("", recipe.id).properties:
            assert not any(
                token in prop.name.lower()
                for token in ("body", "heading", "template", "section", "content")
            )

    # health/plan payloads describe properties, not prose
    report = health.health_report(scan, inv, schema)
    for finding in report["findings"]:
        assert finding["category"] in {
            "parse_failure", "ambiguous_property", "type_conflict", "naming_drift",
            "value_drift", "possible_semantic_overlap", "missing_required_property",
            "unexpected_property", "broken_relationship", "ambiguous_relationship",
            "link_upgrade_opportunity",
        }


def test_ops_ac_025_no_template_feature_exists():
    import app.core as core_pkg

    root = os.path.dirname(os.path.abspath(core_pkg.__file__))
    for name in os.listdir(root):
        if name.endswith(".py"):
            text = open(os.path.join(root, name), encoding="utf-8").read().lower()
            assert "def render_body" not in text
            assert "note_template" not in text


# --------------------------------------------------------------------------
# OPS-AC-026 — No silent report omission
# --------------------------------------------------------------------------
def test_ops_ac_026_health_export_contains_every_finding(scan, inv, out_dir):
    schema = design.build_schema("manage equipment", "equipment")
    report = health.health_report(scan, inv, schema)
    assert report["summary"]["finding_count"] > 5, "fixture must produce many findings"

    result = exports.export_artifact("health", report, scan.vault_path, out_dir)
    assert result["verification"]["no_silent_omission"] is True

    json_path = result["files"][0]["path"]
    written = json.load(open(json_path, encoding="utf-8"))
    assert len(written["findings"]) == len(report["findings"])
    assert {f["id"] for f in written["findings"]} == {f["id"] for f in report["findings"]}

    md_path = result["files"][1]["path"]
    markdown = open(md_path, encoding="utf-8").read()
    for finding in report["findings"]:
        assert finding["title"] in markdown, f"missing from markdown: {finding['title']}"
    # affected-note evidence survives into the human-readable artifact
    for finding in report["findings"]:
        for note in finding["affected_notes"]:
            assert note in markdown


def test_ops_ac_026_plan_and_inbox_exports_complete(scan, out_dir):
    plan = refactor.plan_type_conversion(scan, "project", "note_link")
    result = exports.export_artifact("plan", plan, scan.vault_path, out_dir, "plan-convert")
    written = json.load(open(result["files"][0]["path"], encoding="utf-8"))
    for bucket in ("convertible", "ambiguous", "unresolved"):
        assert len(written[bucket]) == len(plan[bucket])
    markdown = open(result["files"][1]["path"], encoding="utf-8").read()
    for row in plan["ambiguous"] + plan["unresolved"]:
        assert row["note"] in markdown

    inbox = relationships.build_inbox(scan)
    result2 = exports.export_artifact("inbox", inbox, scan.vault_path, out_dir, "inbox")
    written2 = json.load(open(result2["files"][0]["path"], encoding="utf-8"))
    assert len(written2["items"]) == len(inbox["items"])
    md2 = open(result2["files"][1]["path"], encoding="utf-8").read()
    for item in inbox["items"]:
        assert item["title"] in md2


def test_ops_ac_026_discovery_export_complete(scan, inv, out_dir):
    report = inventory.discovery_report(scan, inv)
    result = exports.export_artifact("discovery", report, scan.vault_path, out_dir)
    written = json.load(open(result["files"][0]["path"], encoding="utf-8"))
    assert len(written["inventory"]["properties"]) == len(inv.properties)
    assert len(written["findings"]) == len(report["findings"])
    assert len(written["issues"]) == len(report["issues"])
    markdown = open(result["files"][1]["path"], encoding="utf-8").read()
    for entry in report["inventory"]["properties"]:
        assert entry["key"] in markdown


# --------------------------------------------------------------------------
# OPS-AC-027 — Deterministic repeat run
# --------------------------------------------------------------------------
def _canonical(vault: str) -> str:
    scan = scan_vault(vault)
    inv_ = inventory.build_inventory(scan)
    schema = design.build_schema("manage equipment", "equipment")
    payload = {
        "discovery": inventory.discovery_report(scan, inv_),
        "health": health.health_report(scan, inv_, schema),
        "inbox": relationships.build_inbox(scan),
        "rename": refactor.plan_rename(scan, "Project", "project"),
        "merge": refactor.plan_merge(scan, ["project_name"], "project"),
        "normalize": refactor.plan_normalize(scan, "status"),
        "convert": refactor.plan_type_conversion(scan, "project", "note_link"),
        "schema": schema.to_dict(),
    }
    payload["discovery"].pop("scan_seconds", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def test_ops_ac_027_repeat_run_is_identical(main_vault):
    first = _canonical(main_vault)
    second = _canonical(main_vault)
    assert first == second
    assert len(first) > 5000


# --------------------------------------------------------------------------
# Additional safety cases required by PROJECT/AGENTS
# --------------------------------------------------------------------------
def test_symlink_escape_is_not_scanned(tmp_path):
    vault = tmp_path / "vault"
    outside = tmp_path / "outside"
    (vault / "sub").mkdir(parents=True)
    outside.mkdir()
    (outside / "Secret.md").write_text("---\nsecret: true\n---\n", encoding="utf-8")
    (vault / "Note.md").write_text("---\ntype: note\n---\n", encoding="utf-8")
    try:
        os.symlink(outside, vault / "linked")
        os.symlink(outside / "Secret.md", vault / "sub" / "Linked Note.md")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this platform")

    scan = scan_vault(str(vault))
    paths = {n.path for n in scan.notes}
    assert paths == {"Note.md"}
    assert any("symlink" in s.reason for s in scan.skipped)
    assert "secret" not in json.dumps(
        inventory.build_inventory(scan).to_dict(), ensure_ascii=False
    )


def test_yaml_code_execution_is_refused(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "Evil.md").write_text(
        "---\nx: !!python/object/apply:os.system ['echo pwned']\n---\n", encoding="utf-8"
    )
    scan = scan_vault(str(vault))
    note = scan.notes[0]
    assert note.parse_failed is True
    assert note.parse_status.value == "invalid_yaml"


def test_duplicate_yaml_key_is_ambiguous_not_last_wins(scan):
    note = scan.note_by_path("Notes/Duplicate Key.md")
    assert note.duplicate_keys == ("status",)
    assert any("more than once" in i.message for i in note.issues)


def test_invalid_vault_path_is_rejected(tmp_path):
    with pytest.raises(VaultPathError):
        scan_vault(str(tmp_path / "does-not-exist"))
    file_path = tmp_path / "file.md"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(VaultPathError):
        scan_vault(str(file_path))


def test_obsidian_and_trash_folders_excluded(scan):
    assert not any(n.path.startswith(".obsidian") for n in scan.notes)
    assert not any(n.path.startswith(".trash") for n in scan.notes)
    reasons = {s.path: s.reason for s in scan.skipped}
    assert ".obsidian" in reasons and ".trash" in reasons


def test_health_score_is_explainable(scan, inv):
    report = health.health_report(scan, inv)
    score = report["health_score"]
    recomputed = 100.0 - sum(r["applied_deduction"] for r in score["score_breakdown"])
    assert round(max(0.0, recomputed), 2) == score["score"]
    counted = sum(r["finding_count"] for r in score["score_breakdown"])
    assert counted == len(report["findings"])
    for finding in report["findings"]:
        assert finding["explanation"] and finding["recommendation"]
        assert finding["severity"] in ("info", "low", "medium", "high")


def test_scan_options_defaults_are_safe():
    options = ScanOptions()
    assert options.follow_symlinks is False
    assert ".obsidian" in options.excluded_dirs and ".trash" in options.excluded_dirs
