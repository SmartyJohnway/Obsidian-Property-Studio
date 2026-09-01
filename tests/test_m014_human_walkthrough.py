import json
import pytest
from pathlib import Path
from app.core.scanner import scan_vault
from app.core.inventory import build_inventory
from app.core.scope import ScopeSpec
from app.core import design, note_workspace, refactor
from app import server


@pytest.fixture
def sample_vault(tmp_path: Path):
    vault = tmp_path / "m014_vault"
    vault.mkdir()
    (vault / "FolderA").mkdir()
    (vault / "FolderB").mkdir()

    # Note with duplicate basename
    (vault / "FolderA" / "ProjectX.md").write_text(
        "---\ntype: project\nstatus: active\nowner: Alice\n---\n# Project X in A",
        encoding="utf-8",
    )
    (vault / "FolderB" / "ProjectX.md").write_text(
        "---\ntype: project\nstatus: on hold\nowner: Bob\n---\n# Project X in B",
        encoding="utf-8",
    )
    # Another note
    (vault / "Equipment01.md").write_text(
        "---\ntype: equipment\nlocation: Lab 1\n---\n# Equip 01",
        encoding="utf-8",
    )
    return vault


def test_m014_001_searchable_combobox_and_browse_candidates(sample_vault: Path):
    scan = scan_vault(sample_vault)
    scope = ScopeSpec.from_dict({"mode": "folders", "folders": ["FolderA"], "include_subfolders": True})
    candidates = note_workspace.find_candidate_notes(scan, "", current_scope=scope)
    assert len(candidates) == 3
    in_scope_candidates = [c for c in candidates if c["in_current_scope"]]
    assert len(in_scope_candidates) == 1
    assert in_scope_candidates[0]["path"] == "FolderA/ProjectX.md"



def test_m014_002_duplicate_basename_shows_relative_path(sample_vault: Path):
    scan = scan_vault(sample_vault)
    candidates = note_workspace.find_candidate_notes(scan, "ProjectX", current_scope=None)
    assert len(candidates) == 2
    for c in candidates:
        assert c["is_ambiguous_basename"] is True
        assert "/" in c["path"]


def test_m014_003_structured_management_objects_and_needs():
    assert len(design.OBJECT_PRESETS) >= 12
    assert "equipment" in design.OBJECT_PRESETS
    assert "project" in design.OBJECT_PRESETS
    assert "sop" in design.OBJECT_PRESETS

    assert len(design.NEED_PRESETS) >= 12
    assert "maintenance" in design.NEED_PRESETS
    assert "location" in design.NEED_PRESETS
    assert "compliance" in design.NEED_PRESETS


def test_m014_004_build_schema_from_structured_inputs(sample_vault: Path):
    scan = scan_vault(sample_vault)
    inv = build_inventory(scan)
    schema = design.build_schema_from_structured_inputs(
        objects=["equipment"],
        needs=["location", "maintenance"],
        extra_text="Need supplier note link",
        inv=inv,
    )
    prop_names = [p.name for p in schema.properties]
    assert "type" in prop_names
    assert "status" in prop_names
    assert "location" in prop_names
    assert "last_service_date" in prop_names
    assert "next_service_date" in prop_names
    assert "tags" in prop_names


def test_m014_005_schema_review_i18n_keys(sample_vault: Path):
    scan = scan_vault(sample_vault)
    inv = build_inventory(scan)
    schema = design.build_schema_from_structured_inputs(
        objects=["equipment"],
        needs=["location"],
        inv=inv,
    )
    rev = design.review_schema_against_vault(schema, inv)
    for r in rev["reuse_reviews"]:
        assert "status_key" in r
        assert "message_key" in r
        assert r["status_key"].startswith("schema.status_")
        assert r["message_key"].startswith("schema.msg_")


def test_m014_006_adopt_schema_selection_and_pruning(sample_vault: Path):
    scan = scan_vault(sample_vault)
    inv = build_inventory(scan)
    schema = design.build_schema_from_structured_inputs(
        objects=["project"],
        needs=["dates"],
        inv=inv,
    )
    retained_names = {"type", "status", "due_date"}
    pruned_props = [p for p in schema.properties if p.name in retained_names]
    adopted = design.Schema(name=schema.name, description=schema.description, properties=pruned_props)
    assert len(adopted.properties) == 3
    assert {p.name for p in adopted.properties} == retained_names


def test_m014_007_blank_note_empty_state_and_dynamic_controls(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.inventory = build_inventory(server.STORE.scan)
    server.STORE.vault_path = str(sample_vault)

    schema = design.build_schema_from_structured_inputs(objects=["task"], needs=["priority"])
    preview_res = server.api_fill_preview({
        "schema": schema.to_dict(),
        "values": {"type": "task", "status": "active", "priority": "high"},
    })
    assert preview_res["valid"] is True
    assert "type: task" in preview_res["frontmatter_preview"]
    assert "priority: high" in preview_res["frontmatter_preview"]


def test_m014_008_refactor_rename_conflict_warning(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.inventory = build_inventory(server.STORE.scan)
    server.STORE.vault_path = str(sample_vault)

    plan = server.api_refactor_plan({
        "operation": "rename",
        "source": "type",
        "target": "owner",
    })
    assert plan["target_already_exists"] is True
    assert plan["target_existing_usage_count"] == 2


def test_m014_009_refactor_empty_target_fail_closed(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.vault_path = str(sample_vault)

    with pytest.raises(server.ApiError) as exc:
        server.api_refactor_plan({
            "operation": "rename",
            "source": "type",
            "target": "   ",
        })
    assert "cannot be empty" in str(exc.value)


def test_m014_010_refactor_controlled_types_validation(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.vault_path = str(sample_vault)

    with pytest.raises(server.ApiError) as exc:
        server.api_refactor_plan({
            "operation": "convert_type",
            "property": "status",
            "target_type": "invalid_unknown_type",
        })
    assert "Target type must be one of" in str(exc.value)


def test_m014_011_refactor_human_readable_and_raw_json(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.inventory = build_inventory(server.STORE.scan)
    server.STORE.vault_path = str(sample_vault)

    plan = server.api_refactor_plan({
        "operation": "rename",
        "source": "owner",
        "target": "assignee",
    })
    assert "affected_notes" in plan
    assert len(plan["affected_notes"]) == 2
    affected_paths = [n["note"] if isinstance(n, dict) else n for n in plan["affected_notes"]]
    assert "FolderA/ProjectX.md" in affected_paths
    assert "FolderB/ProjectX.md" in affected_paths



def test_m014_012_server_presets_endpoint():
    res = server.api_design_presets({})
    assert "objects" in res
    assert "needs" in res
    assert len(res["objects"]) >= 12
    assert len(res["needs"]) >= 12
    assert any(o["id"] == "equipment" for o in res["objects"])


def test_m014_013_workspace_with_adopted_schema(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.vault_path = str(sample_vault)

    schema = design.build_schema_from_structured_inputs(objects=["equipment"], needs=["location"])
    res = server.api_workspace_preview({
        "note_path": "Equipment01.md",
        "values": {"type": "equipment", "location": "Room 101", "owner": "Charlie"},
        "schema": schema.to_dict(),
        "deleted_keys": [],
    })
    assert res["roundtrip_matches"] is True
    assert "location: Room 101" in res["frontmatter_preview"]


def test_m014_014_traditional_chinese_and_english_i18n_sync():
    root = Path(__file__).resolve().parent.parent
    zh_path = root / "app" / "ui" / "locales" / "zh-Hant.json"
    en_path = root / "app" / "ui" / "locales" / "en.json"

    zh_data = json.loads(zh_path.read_text(encoding="utf-8"))
    en_data = json.loads(en_path.read_text(encoding="utf-8"))

    m014_required_keys = [
        "design.objects_title",
        "design.needs_title",
        "design.adopt_btn",
        "design.next_actions_title",
        "design.next_apply_existing",
        "design.next_create_blank",
        "schema.status_in_scope",
        "schema.status_elsewhere",
        "schema.status_new",
        "schema.msg_in_scope",
        "fill.empty_title",
        "fill.empty_desc",
        "fill.go_to_design",
        "refactor.rename_target_conflict_warn",
        "refactor.human_summary_title",
        "ws.browse_placeholder",
    ]
    for key in m014_required_keys:
        assert key in zh_data, f"Missing key in zh-Hant.json: {key}"
        assert key in en_data, f"Missing key in en.json: {key}"


def test_m014_015_vault_safety_read_only_in_m014(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.baseline_manifest = server.vault_manifest(sample_vault)
    server.STORE.vault_path = str(sample_vault)

    server.api_design_presets({})
    verify_report = server.api_vault_verify({})
    assert verify_report["unchanged"] is True
    assert verify_report["files_checked"] == 3


def test_m014_016_refactor_controlled_target_and_new_name():
    html_text = (Path(__file__).resolve().parent.parent / "app" / "ui" / "index.html").read_text(encoding="utf-8")
    assert 'id="refactorTargetPropSelect"' in html_text
    assert 'id="refactorTargetNewNameInput"' in html_text
    assert 'id="refactorConflictWarnBanner"' in html_text
    assert 'id="refactorTargetTypeSelect"' in html_text


def test_m014_017_relations_controlled_property_filter():
    html_text = (Path(__file__).resolve().parent.parent / "app" / "ui" / "index.html").read_text(encoding="utf-8")
    assert 'id="relPropFilterSelect"' in html_text
    assert 'id="relPropFilterInput"' not in html_text


def test_m014_018_schema_design_selection_required_validation(sample_vault: Path):
    server.STORE.scan = scan_vault(sample_vault)
    server.STORE.vault_path = str(sample_vault)

    # Empty objects and needs with no goal
    res = server.api_design_build({"objects": [], "needs": [], "goal": ""})
    assert "schema" in res
    assert "reuse_reviews" in res

