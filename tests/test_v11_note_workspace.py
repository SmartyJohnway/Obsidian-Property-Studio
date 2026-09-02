"""
v1.1.0 Regression Contracts V11-005, V11-006, V11-007, V11-008:
Note Properties Workspace (Existing Note & Blank Modes) Verification.
"""

from __future__ import annotations

from app.core.model import Note, ParseIssue, ParseStatus, PropertyValue, Schema, SchemaProperty, Severity, StorageType, VaultScan
from app.core.note_workspace import (
    compute_workspace_diff_and_frontmatter,
    find_candidate_notes,
    inspect_note_for_workspace,
)


def _make_sample_vault() -> VaultScan:
    notes = [
        # Ambiguous base name notes across different folders
        Note(
            path="Projects/Alpha/Overview.md",
            parse_status=ParseStatus.OK,
            properties={
                "project": PropertyValue("project", "Alpha", StorageType.TEXT, ("Alpha",), "Alpha"),
                "status": PropertyValue("status", "active", StorageType.TEXT, ("active",), "active"),
                "author": PropertyValue("author", "Alice", StorageType.TEXT, ("Alice",), "Alice"),
            },
        ),
        Note(
            path="Archive/2025/Overview.md",
            parse_status=ParseStatus.OK,
            properties={
                "project": PropertyValue("project", "Old", StorageType.TEXT, ("Old",), "Old"),
                "archived": PropertyValue("archived", True, StorageType.CHECKBOX, ("true",), "true"),
            },
        ),
        # Corrupt frontmatter note
        Note(
            path="Broken/CorruptYaml.md",
            parse_status=ParseStatus.INVALID_YAML,
            issues=(
                ParseIssue(
                    note_path="Broken/CorruptYaml.md",
                    status=ParseStatus.INVALID_YAML,
                    severity=Severity.HIGH,
                    message="Malformed YAML",
                ),
            ),
        ),
        # Duplicate keys note
        Note(
            path="Broken/DuplicateKeys.md",
            parse_status=ParseStatus.OK,
            properties={
                "tag": PropertyValue("tag", "work", StorageType.TEXT, ("work",), "work"),
            },
            duplicate_keys=("tag",),
        ),
    ]
    return VaultScan(vault_path="dummy/vault", notes=notes)


def test_v11_005_note_selector_handles_duplicate_base_names() -> None:
    """V11-005: Note selector marks ambiguous duplicate base names with explicit paths."""
    vault = _make_sample_vault()
    candidates = find_candidate_notes(vault, "Overview")

    assert len(candidates) == 2
    for c in candidates:
        assert c["name"] == "Overview"
        assert c["is_ambiguous_basename"] is True
        assert c["path"] in c["display_label"]


def test_v11_006_preserves_unrelated_frontmatter_properties() -> None:
    """V11-006: Existing Note Property Workspace preserves unrelated properties across edits and diffs."""
    vault = _make_sample_vault()
    note = vault.note_by_path("Projects/Alpha/Overview.md")
    assert note is not None

    # We only edit 'status' to 'completed', leaving 'project' and 'author' untouched
    new_values = {"status": "completed"}
    diff_res = compute_workspace_diff_and_frontmatter(original_note=note, updated_values=new_values)

    assert diff_res.valid is True
    assert diff_res.can_copy is True
    # 'project' and 'author' must be preserved in merged properties
    assert diff_res.merged_properties["status"] == "completed"
    assert diff_res.merged_properties["project"] == "Alpha"
    assert diff_res.merged_properties["author"] == "Alice"

    # In diffs: status is modified, project and author are preserved
    diff_types = {d.key: d.change_type for d in diff_res.diffs}
    assert diff_types["status"] == "modified"
    assert diff_types["project"] == "preserved"
    assert diff_types["author"] == "preserved"

    # Frontmatter text must contain all 3 properties
    assert "status: completed" in diff_res.frontmatter_preview
    assert "project: Alpha" in diff_res.frontmatter_preview
    assert "author: Alice" in diff_res.frontmatter_preview


def test_v11_007_fails_closed_on_duplicate_keys_and_corrupt_frontmatter() -> None:
    """V11-007: Existing Note Property Workspace fails closed on notes with duplicate keys or malformed frontmatter."""
    vault = _make_sample_vault()

    # Case A: Corrupt YAML
    insp_corrupt = inspect_note_for_workspace(vault, "Broken/CorruptYaml.md")
    assert insp_corrupt.can_edit is False
    assert "malformed" in (insp_corrupt.error_reason or "").lower()

    diff_corrupt = compute_workspace_diff_and_frontmatter(
        original_note=vault.note_by_path("Broken/CorruptYaml.md"),
        updated_values={"tag": "fixed"},
    )
    assert diff_corrupt.valid is False
    assert diff_corrupt.can_copy is False

    # Case B: Duplicate YAML Keys
    insp_dup = inspect_note_for_workspace(vault, "Broken/DuplicateKeys.md")
    assert insp_dup.can_edit is False
    assert "duplicate" in (insp_dup.error_reason or "").lower()

    diff_dup = compute_workspace_diff_and_frontmatter(
        original_note=vault.note_by_path("Broken/DuplicateKeys.md"),
        updated_values={"tag": "fixed"},
    )
    assert diff_dup.valid is False
    assert diff_dup.can_copy is False


def test_v11_008_disables_copy_action_on_invalid_fill() -> None:
    """V11-008: Note Property Workspace disables Copy action when frontmatter validation is invalid."""
    schema = Schema(
        name="strict_task",
        properties=[
            SchemaProperty(name="title", storage_type=StorageType.TEXT, required=True),
            SchemaProperty(name="due_date", storage_type=StorageType.DATE, required=True),
        ],
    )

    # Missing required 'due_date'
    diff_res = compute_workspace_diff_and_frontmatter(
        original_note=None,
        updated_values={"title": "My Task"},
        schema=schema,
    )

    assert diff_res.valid is False
    assert diff_res.can_copy is False
    assert any("due_date" in err for err in diff_res.errors)
