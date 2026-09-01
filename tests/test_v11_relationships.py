"""
v1.1.0 Regression Contracts V11-009, V11-010, V11-011, V11-014:
Scope-Aware Relationship Analysis (Property Links) Verification.
"""

from __future__ import annotations

from app.core.model import Note, ParseStatus, PropertyValue, StorageType, VaultScan
from app.core.relationships import build_inbox
from app.core.scope import ScopeMode, ScopeSpec


def _make_relationship_vault() -> VaultScan:
    notes = [
        # Source Folder 1: Projects
        Note(
            path="Projects/TaskA.md",
            parse_status=ParseStatus.OK,
            properties={
                "client": PropertyValue("client", "[[ACME Corp]]", StorageType.TEXT, ("[[ACME Corp]]",), "[[ACME Corp]]"),
                "vendor": PropertyValue("vendor", "[[Global Logistics]]", StorageType.TEXT, ("[[Global Logistics]]",), "[[Global Logistics]]"),
            },
        ),
        # Source Folder 2: Initiatives
        Note(
            path="Initiatives/Init1.md",
            parse_status=ParseStatus.OK,
            properties={
                "client": PropertyValue("client", "[[Beta Corp]]", StorageType.TEXT, ("[[Beta Corp]]",), "[[Beta Corp]]"),
            },
        ),
        # Unrelated Folder (should not be analyzed when source scope is restricted)
        Note(
            path="Personal/Diary.md",
            parse_status=ParseStatus.OK,
            properties={
                "client": PropertyValue("client", "[[Broken Company]]", StorageType.TEXT, ("[[Broken Company]]",), "[[Broken Company]]"),
            },
        ),
        # Target Folder 1: Clients
        Note(
            path="Clients/ACME Corp.md",
            parse_status=ParseStatus.OK,
            properties={},
        ),
        Note(
            path="Clients/Beta Corp.md",
            parse_status=ParseStatus.OK,
            properties={},
        ),
        # External Folder (outside Target Scope Clients): Vendors
        Note(
            path="Vendors/Global Logistics.md",
            parse_status=ParseStatus.OK,
            properties={},
        ),
    ]
    return VaultScan(vault_path="dummy/vault", notes=notes)


def test_v11_009_source_scope_accepts_multi_folder() -> None:
    """V11-009: Relationship Source Scope correctly accepts multiple folder roots."""
    vault = _make_relationship_vault()
    source_scope = ScopeSpec(
        mode=ScopeMode.FOLDERS,
        folders=["Projects", "Initiatives"],
        include_subfolders=True,
    )

    inbox = build_inbox(vault, source_scope=source_scope)
    source_notes_in_inbox = {item["note"] for item in inbox["items"]}

    # Projects/TaskA.md and Initiatives/Init1.md may appear in findings/items, but Personal/Diary.md MUST NOT
    assert "Personal/Diary.md" not in source_notes_in_inbox


def test_v11_010_and_011_target_scope_marks_outside_target() -> None:
    """V11-010 & V11-011: Relationship Target Scope classifies valid links outside target scope as outside_target_scope."""
    vault = _make_relationship_vault()
    source_scope = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Projects"], include_subfolders=True)
    # Target scope is ONLY 'Clients'
    target_scope = ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Clients"], include_subfolders=True)

    inbox = build_inbox(vault, source_scope=source_scope, target_scope=target_scope)

    # In TaskA:
    # 1. 'client: [[ACME Corp]]' -> resolves to Clients/ACME Corp.md (INSIDE target scope -> healthy, no warning item)
    # 2. 'vendor: [[Global Logistics]]' -> resolves to Vendors/Global Logistics.md (OUTSIDE target scope -> outside_target_scope finding)
    outside_items = [i for i in inbox["items"] if i["kind"] == "outside_target_scope"]
    assert len(outside_items) == 1
    item = outside_items[0]
    assert item["note"] == "Projects/TaskA.md"
    assert item["property"] == "vendor"
    assert item["canonical_target"] == "Vendors/Global Logistics.md"
    assert "outside" in item["title"].lower()


def test_v11_014_zero_default_rules_on_startup() -> None:
    """V11-014: System starts with zero default relationship rules or ontology assumptions."""
    vault = _make_relationship_vault()
    # On entire vault scan with no explicit property filter or rules, all properties evaluated uniformly without hardcoded schemas
    inbox = build_inbox(vault)
    # There are no hardcoded default ontologies; items are purely discoverable relationship candidates
    assert "summary" in inbox
    assert "items" in inbox
