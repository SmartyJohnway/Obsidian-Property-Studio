"""
v1.1.0 Regression Contracts V11-002, V11-003, V11-004:
Formal Scope Domain Model and In-Memory Filtering Engine.
"""

from __future__ import annotations

from app.core.model import Note, ParseStatus, VaultScan
from app.core.scope import (
    ScopeMode,
    ScopeSpec,
    extract_vault_folders,
    filter_notes_by_scope,
    filter_scan_by_scope,
    is_note_in_scope,
)


def _make_dummy_notes() -> list[Note]:
    paths = [
        "RootNote.md",
        "Projects/Alpha/plan.md",
        "Projects/Alpha/todo.md",
        "Projects/Beta/summary.md",
        "Archive/2025/report.md",
        "Archive/2026/Q1/summary.md",
        "Daily/2026-09-01.md",
    ]
    return [
        Note(
            path=p,
            parse_status=ParseStatus.OK,
            properties={"type": "note"} if "plan" in p or "summary" in p else {},
        )
        for p in paths
    ]


def test_v11_002_multi_folder_scope_union_and_deduplication() -> None:
    """V11-002: Multi-folder Scope correctly calculates union of selected folders
    and deduplicates overlapping notes."""
    notes = _make_dummy_notes()

    # Scope selecting both Projects/Alpha and Projects
    scope = ScopeSpec(
        mode=ScopeMode.FOLDERS,
        folders=["Projects/Alpha", "Projects"],
        include_subfolders=True,
    )

    filtered = filter_notes_by_scope(notes, scope)
    paths = [n.path for n in filtered]

    # Should contain Projects/Alpha/plan.md, Projects/Alpha/todo.md, Projects/Beta/summary.md
    expected = [
        "Projects/Alpha/plan.md",
        "Projects/Alpha/todo.md",
        "Projects/Beta/summary.md",
    ]
    assert sorted(paths) == sorted(expected)
    # Deduplication: no duplicate items
    assert len(paths) == len(set(paths))


def test_v11_003_nested_folder_include_subfolders_semantics() -> None:
    """V11-003: Nested folder include_subfolders true/false filter semantics correctly enforced."""
    notes = _make_dummy_notes()

    # Case A: Archive with include_subfolders = True
    scope_sub = ScopeSpec(
        mode=ScopeMode.FOLDERS,
        folders=["Archive"],
        include_subfolders=True,
    )
    filtered_sub = filter_notes_by_scope(notes, scope_sub)
    paths_sub = [n.path for n in filtered_sub]
    assert sorted(paths_sub) == ["Archive/2025/report.md", "Archive/2026/Q1/summary.md"]

    # Case B: Archive/2026 with include_subfolders = False -> only direct notes in Archive/2026
    # (Q1/summary.md is in Archive/2026/Q1, so it shouldn't match if include_subfolders=False)
    scope_no_sub = ScopeSpec(
        mode=ScopeMode.FOLDERS,
        folders=["Archive/2026"],
        include_subfolders=False,
    )
    filtered_no_sub = filter_notes_by_scope(notes, scope_no_sub)
    assert [n.path for n in filtered_no_sub] == []

    # Case C: Archive/2026 with include_subfolders = True -> matches Q1/summary.md
    scope_2026_sub = ScopeSpec(
        mode=ScopeMode.FOLDERS,
        folders=["Archive/2026"],
        include_subfolders=True,
    )
    filtered_2026 = filter_notes_by_scope(notes, scope_2026_sub)
    assert [n.path for n in filtered_2026] == ["Archive/2026/Q1/summary.md"]


def test_v11_004_in_memory_scope_filter_no_disk_rescan() -> None:
    """V11-004: Scope filtering operates in-memory over VaultScan without triggering full Vault disk rescan."""
    notes = _make_dummy_notes()
    scan = VaultScan(vault_path="dummy/path", notes=notes)

    scope = ScopeSpec(
        mode=ScopeMode.FOLDERS,
        folders=["Projects/Alpha"],
        include_subfolders=True,
    )

    # Filtering should derive from scan.notes in-memory
    scoped_scan = filter_scan_by_scope(scan, scope)

    assert scoped_scan.vault_path == scan.vault_path
    assert scoped_scan.note_count == 2
    assert scoped_scan.notes_with_properties == 1
    assert [n.path for n in scoped_scan.notes] == [
        "Projects/Alpha/plan.md",
        "Projects/Alpha/todo.md",
    ]


def test_extract_vault_folders() -> None:
    """Folder extraction lists all ancestor folders accurately."""
    notes = _make_dummy_notes()
    folders = extract_vault_folders(notes)
    expected = [
        "Archive",
        "Archive/2025",
        "Archive/2026",
        "Archive/2026/Q1",
        "Daily",
        "Projects",
        "Projects/Alpha",
        "Projects/Beta",
    ]
    assert folders == expected


def test_single_note_scope() -> None:
    """Single note scope isolates exactly the requested note."""
    notes = _make_dummy_notes()
    scope = ScopeSpec(
        mode=ScopeMode.SINGLE_NOTE,
        note_path="Projects/Beta/summary.md",
    )
    filtered = filter_notes_by_scope(notes, scope)
    assert len(filtered) == 1
    assert filtered[0].path == "Projects/Beta/summary.md"
