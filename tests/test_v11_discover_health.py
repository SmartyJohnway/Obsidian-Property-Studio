"""
v1.1.0 Regression Contract V11-016:
Scope-aware Discover and Property Health Isolation.
Calculates property inventories, health scores, and findings strictly from Scope notes
without cross-contamination from out-of-scope notes.
"""

from __future__ import annotations

from app.core.health import health_report
from app.core.inventory import build_inventory, discovery_report
from app.core.model import Note, ParseIssue, ParseStatus, PropertyValue, Severity, StorageType, VaultScan
from app.core.scope import ScopeMode, ScopeSpec, filter_scan_by_scope


def _make_cross_scope_vault() -> VaultScan:
    """Vault with FolderA (problematic) and FolderB (clean)."""
    notes = [
        # Clean notes in FolderB
        Note(
            path="FolderB/Note1.md",
            parse_status=ParseStatus.OK,
            properties={"status": PropertyValue("status", "active", StorageType.TEXT, ("active",), "active")},
        ),
        Note(
            path="FolderB/Note2.md",
            parse_status=ParseStatus.OK,
            properties={"status": PropertyValue("status", "done", StorageType.TEXT, ("done",), "done")},
        ),
        # Broken / conflict notes in FolderA
        Note(
            path="FolderA/Broken1.md",
            parse_status=ParseStatus.INVALID_YAML,
            issues=(
                ParseIssue(
                    note_path="FolderA/Broken1.md",
                    status=ParseStatus.INVALID_YAML,
                    severity=Severity.HIGH,
                    message="YAML syntax error in frontmatter",
                ),
            ),
        ),
        Note(
            path="FolderA/TypeConflict.md",
            parse_status=ParseStatus.OK,
            properties={"status": PropertyValue("status", 123, StorageType.NUMBER, ("123",), "123")},
        ),
    ]
    return VaultScan(
        vault_path="dummy/vault",
        notes=notes,
        issues=[
            ParseIssue(
                note_path="FolderA/Broken1.md",
                status=ParseStatus.INVALID_YAML,
                severity=Severity.HIGH,
                message="YAML syntax error in frontmatter",
            )
        ],
    )


def test_v11_016_scope_aware_health_isolation() -> None:
    """V11-016: Scope-aware Property Health calculates scores and findings strictly
    from Scope notes without cross-contamination."""
    vault = _make_cross_scope_vault()

    # Scope 1: FolderB only (Clean)
    scope_b = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["FolderB"], include_subfolders=True)
    scan_b = filter_scan_by_scope(vault, scope_b)
    inv_b = build_inventory(scan_b)
    rep_b = health_report(scan_b, inv_b)

    # Health score for FolderB should be clean 100
    assert rep_b["health_score"]["score"] == 100.0
    assert rep_b["summary"]["finding_count"] == 0
    # Discover in FolderB only sees 'status' with 2 text usages
    disc_b = discovery_report(scan_b, inv_b)
    assert disc_b["summary"]["note_count"] == 2
    prop_keys = [p["key"] for p in disc_b["inventory"]["properties"]]
    assert prop_keys == ["status"]
    status_entry = disc_b["inventory"]["properties"][0]
    assert status_entry["usage_count"] == 2
    assert status_entry["dominant_type"] == "text"

    # Scope 2: Entire Vault (includes FolderA with corruption and type conflict)
    scope_all = ScopeSpec(mode=ScopeMode.ENTIRE_VAULT)
    scan_all = filter_scan_by_scope(vault, scope_all)
    inv_all = build_inventory(scan_all)
    rep_all = health_report(scan_all, inv_all)

    # Entire vault has deductions from parse_failure and type_conflict
    assert rep_all["health_score"]["score"] < 100.0
    assert rep_all["summary"]["finding_count"] > 0
    affected = [n for f in rep_all["findings"] for n in f["affected_notes"]]
    assert any("FolderA" in p for p in affected)
    # FolderB notes themselves have no parse issues
    assert "FolderB/Note1.md" not in rep_all["findings"][0]["affected_notes"]
