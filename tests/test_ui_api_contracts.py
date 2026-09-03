"""UI-facing API Contract Verification Suite (R01).

Tests production server endpoints against real request/response payloads to guarantee
zero mismatch between frontend assumptions and backend implementations.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.core.model import StorageType, UIControl
from app.server import ROUTES, STORE, ApiError


@pytest.fixture(autouse=True)
def init_store_with_main_vault(main_vault: str):
    scan_handler = ROUTES["/api/scan"]
    scan_handler({"vault_path": main_vault, "hash_baseline": True})


def test_api_meta_contract():
    meta = ROUTES["/api/meta"]({})
    assert meta["app"] == "Obsidian Property Studio"
    assert meta["version"] in ("1.1.0", "1.2.0")
    assert meta["vault_write_capability"] is False
    assert meta["requires_network"] is False
    assert meta["requires_api_key"] is False
    assert isinstance(meta["storage_types"], dict)
    assert isinstance(meta["ui_controls"], dict)
    assert len(meta["recipes"]) >= 4


def test_api_discovery_scope_contract():
    disc = ROUTES["/api/discovery"]({})
    assert "scope" in disc
    assert "notes_in_scope" in disc
    assert "total_vault_notes" in disc
    assert disc["notes_in_scope"] == disc["total_vault_notes"]
    assert "inventory" in disc
    assert "findings" in disc


def test_api_property_detail_contract():
    det = ROUTES["/api/property"]({"key": "status"})
    assert "entry" in det
    assert det["entry"]["key"] == "status"
    assert "notes_by_type" in det
    assert isinstance(det["entry"]["values"], list)


def test_api_design_suggest_and_build_contract():
    sugg = ROUTES["/api/design/suggest"]({"goal": "Manage books and reading reviews"})
    assert len(sugg["recipes"]) >= 1
    assert any(r["id"] == "reading" for r in sugg["recipes"])

    built = ROUTES["/api/design/build"]({"goal": "Manage books", "recipe_id": "reading"})
    assert "schema" in built
    assert "reuse_reviews" in built
    assert "counts" in built
    assert "exact_existing_in_scope" in built["counts"]
    assert "exact_existing_in_vault_only" in built["counts"]


def test_api_workspace_candidates_and_inspect_contract():
    cand = ROUTES["/api/workspace/notes"]({"query": "Ada"})
    assert "candidates" in cand
    assert cand["total"] >= 1
    target_cand = cand["candidates"][0]
    assert "path" in target_cand
    assert "name" in target_cand
    assert "in_current_scope" in target_cand
    assert "is_ambiguous_basename" in target_cand

    insp = ROUTES["/api/workspace/inspect"]({"note_path": target_cand["path"]})
    assert insp["note_path"] == target_cand["path"]
    assert insp["can_edit"] is True
    assert isinstance(insp["original_properties"], dict)


def test_api_workspace_preview_roundtrip_contract():
    note_path = "People/Ada Lovelace.md"
    prev = ROUTES["/api/workspace/preview"]({
        "note_path": note_path,
        "values": {"status": "active", "aliases": "Ada, Countess", "notes": "Leading pioneer in computing"},
        "deleted_keys": []
    })
    assert prev["valid"] is True
    assert prev["can_copy"] is True
    assert prev["roundtrip_matches"] is True
    assert "---" in prev["frontmatter_preview"]
    assert len(prev["diffs"]) >= 1


def test_api_relationships_four_state_contract():
    rel = ROUTES["/api/relationships"]({
        "source_scope": {"mode": "entire_vault"},
        "target_scope": {"mode": "entire_vault"}
    })
    assert "summary" in rel
    assert "four_state_counts" in rel["summary"]
    assert "valid_count" in rel["summary"]
    assert "broken_count" in rel["summary"]
    assert "ambiguous_count" in rel["summary"]
    assert "outside_target_count" in rel["summary"]
    assert isinstance(rel["items"], list)
    assert isinstance(rel["valid_links"], list)


def test_api_relationships_body_contract():
    body_rel = ROUTES["/api/relationships/body"]({
        "source_scope": {"mode": "entire_vault"},
        "target_scope": {"mode": "entire_vault"}
    })
    assert body_rel["analysis_type"] == "body_wikilinks"
    assert "four_state_counts" in body_rel["summary"]
    assert isinstance(body_rel["findings"], list)


def test_api_saved_checks_lifecycle_contract():
    # 1. List (initially empty)
    res_list = ROUTES["/api/relationships/saved/list"]({})
    assert isinstance(res_list["checks"], list)

    # 2. Save
    chk_payload = {
        "name": "Test Check",
        "notes": "Verify people links",
        "link_type": "property_link",
        "property_name": "author",
        "source_scope": {"mode": "folders", "folders": ["People"], "include_subfolders": True},
        "target_scope": {"mode": "entire_vault"}
    }
    res_save = ROUTES["/api/relationships/saved/save"](chk_payload)
    assert res_save["status"] == "saved"
    chk_id = res_save["check"]["id"]

    # 3. Execute
    res_exec = ROUTES["/api/relationships/saved/execute"]({"id": chk_id})
    assert res_exec["check_id"] == chk_id
    assert "results" in res_exec

    # 4. Delete
    res_del = ROUTES["/api/relationships/saved/delete"]({"id": chk_id})
    assert res_del["deleted"] is True


def test_api_health_contract():
    rep = ROUTES["/api/health"]({})
    assert "health_score" in rep
    assert "score" in rep["health_score"]
    assert "summary" in rep
    assert "findings" in rep


def test_api_export_scope_aware_contract(out_dir: str):
    # Set scope to People folder
    ROUTES["/api/scope/apply"]({"scope": {"mode": "folders", "folders": ["People"], "include_subfolders": True}})

    # Export Discovery
    exp = ROUTES["/api/export"]({"kind": "discovery", "output_dir": out_dir})
    assert exp["kind"] == "discovery"
    assert len(exp["files"]) >= 2
    assert exp["verification"]["no_silent_omission"] is True

    # Read back JSON artifact and verify Scope in export
    json_path = next(f["path"] for f in exp["files"] if f["path"].endswith(".json"))
    with open(json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["scope"]["mode"] == "folders"
    assert "People" in data["scope"]["folders"]


def test_api_refactor_merge_contract():
    # Verify merge operation contract
    res = ROUTES["/api/refactor/plan"]({
        "operation": "merge",
        "sources": ["tag", "tags", "category"],
        "target": "topics",
    })
    assert "affected_notes" in res
    assert "conflicts" in res
    assert "summary" in res


