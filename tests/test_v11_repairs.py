"""Comprehensive Release Closure In-Place Repair Suite (R02 ~ R08).

Validates:
- R02: True i18n dictionary parity, rendered UI text, zero fake bilingual side-by-side labels.
- R03: Relationships 4-state contract (VALID, BROKEN, AMBIGUOUS, OUTSIDE SELECTED TARGET) + Saved Checks outside vault.
- R04: Scope fail-closed validation on unknown modes, empty folders, missing single notes.
- R05: Single Note Scope + Note Workspace whole-vault search with ambiguity disclosure.
- R06: Scope-aware export consistency (What user sees = What export contains).
- R07: Design dual context (Scope inventory vs Whole Vault inventory).
- R08: Note Workspace strict YAML round-trip semantic gate.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import pytest

from app.core import body_links, design, exports, fill, health, inventory, note_workspace, refactor, relationships, saved_checks
from app.core.model import Schema, SchemaProperty, StorageType, UIControl, VaultScan
from app.core.scanner import scan_vault
from app.core.scope import (
    ScopeMode,
    ScopeSpec,
    ScopeValidationError,
    filter_scan_by_scope,
    is_note_in_scope,
)
from app.server import ROUTES, STORE, ApiError


# =========================================================================
# R02: True i18n Repair
# =========================================================================
def test_r02_true_i18n_locales_and_no_side_by_side():
    ui_dir = Path(__file__).parent.parent / "app" / "ui"
    zh_path = ui_dir / "locales" / "zh-Hant.json"
    en_path = ui_dir / "locales" / "en.json"

    assert zh_path.exists() and en_path.exists()
    zh = json.loads(zh_path.read_text(encoding="utf-8"))
    en = json.loads(en_path.read_text(encoding="utf-8"))

    # Verify key symmetry
    assert set(zh.keys()) == set(en.keys())

    # Verify no fake bilingual label like "總覽 · Overview" in zh-Hant prose
    for key, text in zh.items():
        if key.startswith("nav.") or key.startswith("overview.") or key.startswith("action."):
            assert "· Overview" not in text
            assert "· Vault" not in text
            assert "· Scope" not in text
            assert "· Design" not in text
            assert "· Fill" not in text

    # Verify index.html references only valid keys
    html_text = (ui_dir / "index.html").read_text(encoding="utf-8")
    import re
    i18n_keys = re.findall(r'data-i18n="([^"]+)"', html_text)
    for k in i18n_keys:
        assert k in zh, f"Key '{k}' in index.html is missing in zh-Hant.json"

    # Verify all I18N.t(...) JavaScript calls reference valid keys
    t_keys = re.findall(r'I18N\.t\(["\']([^"\']+)["\']', html_text)
    for k in t_keys:
        assert k in zh, f"JavaScript I18N.t key '{k}' missing in zh-Hant.json"
        assert k in en, f"JavaScript I18N.t key '{k}' missing in en.json"



# =========================================================================
# R03: Relationships 4-State Contract & Saved Checks
# =========================================================================
def test_r03_relationships_four_state_and_saved_checks(main_vault: str, tmp_path: Path):
    scan = scan_vault(main_vault)

    # 1. Test 4-state property inbox
    source_scope = ScopeSpec(mode=ScopeMode.ENTIRE_VAULT)
    target_scope = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["People"], include_subfolders=True)
    inbox = relationships.build_inbox(scan, source_scope=source_scope, target_scope=target_scope)

    assert "four_state_counts" in inbox["summary"]
    counts = inbox["summary"]["four_state_counts"]
    assert "VALID" in counts
    assert "BROKEN" in counts
    assert "AMBIGUOUS" in counts
    assert "OUTSIDE_SELECTED_TARGET" in counts
    assert counts["VALID"] >= 0
    assert counts["OUTSIDE_SELECTED_TARGET"] >= 1

    # 2. Test Body Wikilinks 4-state
    body_res = body_links.analyze_body_wikilinks(scan, source_scope=source_scope, target_scope=target_scope)
    assert "four_state_counts" in body_res["summary"]
    for f in body_res["findings"]:
        assert f["classification"] in ("VALID", "BROKEN", "AMBIGUOUS", "OUTSIDE_SELECTED_TARGET")

    # 3. Test Saved Checks external persistence
    store = saved_checks.SavedChecksStore()
    chk = saved_checks.SavedCheck(
        id="chk-test-01",
        name="People check",
        notes="Important relations",
        link_type="property_link",
        property_name="project",
        source_scope=source_scope,
        target_scope=target_scope,
    )
    store.save_check(chk)
    assert len(store.list_checks()) == 1

    # Execute check
    exec_res = store.execute_check(scan, "chk-test-01")
    assert exec_res["check_id"] == "chk-test-01"
    assert "four_state_counts" in exec_res["results"]["summary"]


# =========================================================================
# R04: Scope Fail-Closed Repair
# =========================================================================
def test_r04_scope_fail_closed_validation():
    # Unknown mode must raise ScopeValidationError (never fallback)
    with pytest.raises(ScopeValidationError):
        ScopeSpec.from_dict({"mode": "invalid_mode_unknown"})

    # Folders mode with empty folder list must raise ScopeValidationError
    with pytest.raises(ScopeValidationError):
        ScopeSpec.from_dict({"mode": "folders", "folders": []})

    with pytest.raises(ScopeValidationError):
        ScopeSpec.from_dict({"mode": "folders", "folders": ["   "]})

    # Single Note mode with missing or empty note_path must raise ScopeValidationError
    with pytest.raises(ScopeValidationError):
        ScopeSpec.from_dict({"mode": "single_note", "note_path": ""})

    with pytest.raises(ScopeValidationError):
        ScopeSpec.from_dict({"mode": "single_note", "note_path": None})

    # Non-dict payload
    with pytest.raises(ScopeValidationError):
        ScopeSpec.from_dict(["not", "a", "dict"])


def test_r04_scope_filter_never_broadens_on_invalid(main_vault: str):
    scan = scan_vault(main_vault)
    bad_spec = ScopeSpec(mode=ScopeMode.FOLDERS, folders=[])
    with pytest.raises(ScopeValidationError):
        filter_scan_by_scope(scan, bad_spec)


# =========================================================================
# R05: Single Note Scope + Whole-Vault Note Search
# =========================================================================
def test_r05_single_note_scope_and_whole_vault_search(main_vault: str):
    scan = scan_vault(main_vault)

    # 1. Single Note Scope
    spec = ScopeSpec(mode=ScopeMode.SINGLE_NOTE, note_path="People/Ada Lovelace.md")
    scoped = filter_scan_by_scope(scan, spec)
    assert scoped.note_count == 1
    assert scoped.notes[0].name == "Ada Lovelace"

    # 2. Whole Vault Note Search with Scope Priority
    candidates = note_workspace.find_candidate_notes(scan, query="Duplicate Name", current_scope=spec)
    assert len(candidates) >= 2
    for c in candidates:
        assert c["is_ambiguous_basename"] is True
        assert "path" in c


# =========================================================================
# R06: Scope-Aware Export Consistency
# =========================================================================
def test_r06_scope_aware_export_consistency(main_vault: str, out_dir: str):
    ROUTES["/api/scan"]({"vault_path": main_vault})

    # Set Scope to 'Inbox'
    ROUTES["/api/scope/apply"]({"scope": {"mode": "folders", "folders": ["Inbox"], "include_subfolders": True}})

    # Discovery report in UI
    disc_ui = ROUTES["/api/discovery"]({})
    assert disc_ui["scope"]["mode"] == "folders"

    # Export Discovery
    res = ROUTES["/api/export"]({"kind": "discovery", "output_dir": out_dir})
    json_file = next(f["path"] for f in res["files"] if f["path"].endswith(".json"))
    with open(json_file, "r", encoding="utf-8") as fh:
        exp_data = json.load(fh)

    # What user sees == what export contains
    assert exp_data["scope"] == disc_ui["scope"]
    assert exp_data["notes_in_scope"] == disc_ui["notes_in_scope"]
    assert exp_data["total_vault_notes"] == disc_ui["total_vault_notes"]


# =========================================================================
# R07: Design Dual Context (Scope vs Vault)
# =========================================================================
def test_r07_design_dual_context(main_vault: str):
    scan = scan_vault(main_vault)
    scope = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["People"], include_subfolders=True)
    scoped_scan = filter_scan_by_scope(scan, scope)

    scoped_inv = inventory.build_inventory(scoped_scan)
    global_inv = inventory.build_inventory(scan)

    # 'status' is in People (Scope)
    res_in_scope = design.check_property_reuse("status", scoped_inv, global_inv=global_inv)
    assert res_in_scope["status"] == "exact_existing"
    assert res_in_scope["in_scope"] is True

    # 'location' or 'owner' is outside People (in Equipment)
    res_outside = design.check_property_reuse("location", scoped_inv, global_inv=global_inv)
    assert res_outside["status"] == "exact_existing_in_vault_only"
    assert res_outside["in_scope"] is False
    assert res_outside["in_vault_only"] is True



# =========================================================================
# R08: Note Workspace YAML Round-Trip Safety Gate
# =========================================================================
def test_r08_yaml_roundtrip_safety_gate():
    # Test matrix of special values and types
    test_values = {
        "is_active": True,
        "is_hidden": False,
        "null_val": None,
        "numeric_int": 42,
        "numeric_float": 3.14,
        "scientific": "1e3",
        "iso_date": "2026-09-01",
        "colon_in_str": "Meeting: Quarterly Planning",
        "comment_in_str": "Price #2",
        "wikilink_str": "[[Ada Lovelace]]",
        "unicode_chinese": "繁體中文測試標籤",
        "multiline": "Line 1\nLine 2\nLine 3",
        "tags_list": ["tag1", "tag:with:colon", "tag#hash"],
    }

    res = note_workspace.compute_workspace_diff_and_frontmatter(
        original_note=None,
        updated_values=test_values,
    )

    assert res.valid is True
    assert res.can_copy is True
    assert res.roundtrip_matches is True
    assert len(res.errors) == 0
    assert "繁體中文測試標籤" in res.frontmatter_preview
