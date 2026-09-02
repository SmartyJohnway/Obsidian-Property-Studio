"""
v1.1.0 Regression Contract V11-018:
Comprehensive Vault Byte-for-Byte Read-Only Verification across all v1.1.0 workflows.
"""

from __future__ import annotations

import os
from app.core.body_links import analyze_body_wikilinks
from app.core.exports import export_artifact
from app.core.health import health_report
from app.core.inventory import build_inventory, discovery_report
from app.core.manifest import assert_unchanged, vault_manifest
from app.core.note_workspace import (
    compute_workspace_diff_and_frontmatter,
    find_candidate_notes,
    inspect_note_for_workspace,
)
from app.core.refactor import plan_merge, plan_normalize, plan_rename
from app.core.relationships import build_inbox
from app.core.saved_checks import SavedCheck, SavedChecksStore
from app.core.scanner import scan_vault
from app.core.scope import ScopeMode, ScopeSpec, filter_scan_by_scope


def test_v11_018_comprehensive_vault_readonly_across_all_v11_workflows(
    main_vault: str, tmp_path: any
) -> None:
    """V11-018: Pre/post SHA-256 manifest comparison proves Vault remains 100% byte-for-byte identical across ALL v1.1.0 workflows."""
    manifest_before = vault_manifest(main_vault)

    # 1. Scan vault
    scan = scan_vault(main_vault)
    inv = build_inventory(scan)
    _ = discovery_report(scan, inv)

    # 2. Scope filtering in-memory
    scope = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["People", "Projects"], include_subfolders=True)
    scoped_scan = filter_scan_by_scope(scan, scope)
    scoped_inv = build_inventory(scoped_scan)

    # 3. Health analysis
    report = health_report(scoped_scan, scoped_inv)
    assert report is not None

    # 4. Note Workspace (Inspect & Diff)
    candidates = find_candidate_notes(scan, "Ada")
    if candidates:
        inspect_res = inspect_note_for_workspace(scan, candidates[0]["path"])
        assert inspect_res.can_edit is True
        sample_note = next(n for n in scan.notes if n.path == candidates[0]["path"])
        diff_res = compute_workspace_diff_and_frontmatter(
            sample_note,
            updated_values={"status": "in-progress", "role": "Lead"},
        )
        assert diff_res.valid is True

    # 5. Scope-Aware Relationships (Property links)
    rel_inbox = build_inbox(
        scan,
        source_scope=scope,
        target_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Organizations"]),
    )
    assert rel_inbox is not None

    # 6. Body Wikilinks analysis
    body_res = analyze_body_wikilinks(
        scan,
        source_scope=scope,
        target_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Organizations"]),
    )
    assert body_res is not None

    # 7. Saved checks execution & round-trip
    chk = SavedCheck(
        id="v11-chk-001",
        name="Integration Check",
        link_type="body",
        source_scope=scope,
    )
    store = SavedChecksStore([chk])
    exec_res = store.execute_check(scan, "v11-chk-001")
    assert exec_res is not None

    # 8. Scope-Aware Refactor Planning
    plan1 = plan_rename(scan, "status", "state", scope=scope)
    plan2 = plan_normalize(scan, "status", scope=scope)
    assert plan1 is not None and plan2 is not None

    # 9. Exports strictly outside vault
    export_out = str(tmp_path / "exports")
    os.makedirs(export_out, exist_ok=True)
    res_export = export_artifact("health", report, vault_path=main_vault, output_dir=export_out)
    assert res_export["verification"]["no_silent_omission"] is True

    # 10. Manifest Verification: Assert 0 bytes changed in Vault
    manifest_after = vault_manifest(main_vault)
    diff = assert_unchanged(manifest_before, manifest_after)
    assert diff["unchanged"] is True
    assert diff["files_created"] == 0
    assert diff["files_deleted"] == 0
    assert diff["files_modified"] == 0
