"""
v1.1.0 Regression Contract V11-017:
Scope-Aware Property Refactor Planner Verification.
"""

from __future__ import annotations

from app.core.model import Note, ParseStatus, PropertyValue, StorageType, VaultScan
from app.core.refactor import plan_rename, plan_merge, plan_normalize
from app.core.scope import ScopeMode, ScopeSpec


def _make_refactor_vault() -> VaultScan:
    notes = [
        # In Scope Folder: Projects
        Note(
            path="Projects/Proj1.md",
            parse_status=ParseStatus.OK,
            properties={
                "tag": PropertyValue("tag", "work", StorageType.TEXT, ("work",), "work"),
                "status": PropertyValue("status", "active", StorageType.TEXT, ("active",), "active"),
            },
        ),
        Note(
            path="Projects/Proj2.md",
            parse_status=ParseStatus.OK,
            properties={
                "tag": PropertyValue("tag", "work", StorageType.TEXT, ("work",), "work"),
                "status": PropertyValue("status", "active", StorageType.TEXT, ("active",), "active"),
            },
        ),
        # Out of Scope Folder: Archive
        Note(
            path="Archive/Old1.md",
            parse_status=ParseStatus.OK,
            properties={
                "tag": PropertyValue("tag", "work", StorageType.TEXT, ("work",), "work"),
                "status": PropertyValue("status", "archived", StorageType.TEXT, ("archived",), "archived"),
            },
        ),
    ]
    return VaultScan(vault_path="dummy/vault", notes=notes)


def test_v11_017_refactor_planner_limits_to_active_scope_without_expansion() -> None:
    """V11-017: Scope-aware Refactor Planner limits plan strictly to Scope notes without silent expansion."""
    vault = _make_refactor_vault()
    scope = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Projects"], include_subfolders=True)

    # 1. Rename 'tag' -> 'tags' within Projects scope
    plan = plan_rename(vault, source="tag", target="tags", scope=scope)

    assert plan["summary"]["in_scope_notes_to_change"] == 2
    assert plan["summary"]["out_of_scope_notes_to_change"] == 1
    # Affected notes MUST only contain the 2 notes in Projects
    affected_paths = [a["note"] for a in plan["affected_notes"]]
    assert affected_paths == ["Projects/Proj1.md", "Projects/Proj2.md"]
    assert "Archive/Old1.md" not in affected_paths

    # 2. Entire vault rename (no scope restriction)
    full_plan = plan_rename(vault, source="tag", target="tags", scope=ScopeSpec(mode=ScopeMode.ENTIRE_VAULT))
    assert full_plan["summary"]["in_scope_notes_to_change"] == 3
    assert len(full_plan["affected_notes"]) == 3
    assert "Archive/Old1.md" in [a["note"] for a in full_plan["affected_notes"]]
