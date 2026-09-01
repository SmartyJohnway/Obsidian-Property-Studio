"""Note Properties Workspace domain model and diff engine (M006).

REQ-026 / REQ-027 / DEC-022 / DEC-023:
Supports:
1. Inspecting existing notes' frontmatter.
2. Editing existing properties while preserving unrelated properties across edits (V11-006).
3. Fail-closed protection against corrupt frontmatter and duplicate keys (V11-007).
4. Generating semantic diffs and copyable frontmatter with copy button fail-closed (V11-008).
5. Disambiguating duplicate base names across folders (V11-005).
6. Blank note frontmatter generation (v1.0.0 flow).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from app.core.model import FAILED_PARSE_STATUSES, Note, ParseStatus, Schema, VaultScan


@dataclass
class NoteWorkspaceInspectResult:
    note_path: str
    name: str
    parse_status: str
    can_edit: bool
    error_reason: str | None = None
    original_properties: dict[str, Any] = field(default_factory=dict)
    duplicate_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_path": self.note_path,
            "name": self.name,
            "parse_status": self.parse_status,
            "can_edit": self.can_edit,
            "error_reason": self.error_reason,
            "original_properties": self.original_properties,
            "duplicate_keys": self.duplicate_keys,
        }


@dataclass
class PropertyDiff:
    key: str
    change_type: str  # "added" | "modified" | "deleted" | "preserved"
    old_value: Any = None
    new_value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class NoteWorkspaceDiffResult:
    note_path: str | None
    valid: bool
    can_copy: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    diffs: list[PropertyDiff] = field(default_factory=list)
    merged_properties: dict[str, Any] = field(default_factory=dict)
    frontmatter_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_path": self.note_path,
            "valid": self.valid,
            "can_copy": self.can_copy,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "diffs": [d.to_dict() for d in self.diffs],
            "merged_properties": self.merged_properties,
            "frontmatter_preview": self.frontmatter_preview,
        }


def find_candidate_notes(scan: VaultScan, query: str = "") -> list[dict[str, Any]]:
    """Find notes matching query with explicit path ambiguity detection (V11-005)."""
    q = query.strip().casefold()
    matches = []
    basename_counts: dict[str, int] = {}

    for note in scan.notes:
        base = note.name.casefold()
        basename_counts[base] = basename_counts.get(base, 0) + 1

    for note in scan.notes:
        if q and q not in note.name.casefold() and q not in note.path.casefold():
            continue
        is_ambiguous = basename_counts.get(note.name.casefold(), 0) > 1
        matches.append({
            "path": note.path,
            "name": note.name,
            "has_properties": note.has_properties,
            "is_ambiguous_basename": is_ambiguous,
            "display_label": f"{note.name} ({note.path})" if is_ambiguous else note.name,
        })
        if len(matches) >= 100:
            break

    return matches


def inspect_note_for_workspace(scan: VaultScan, note_path: str) -> NoteWorkspaceInspectResult:
    """Inspect a note for editing, failing closed on duplicate keys or corruption (V11-007)."""
    note = scan.note_by_path(note_path)
    if note is None:
        return NoteWorkspaceInspectResult(
            note_path=note_path,
            name=note_path.rsplit("/", 1)[-1].replace(".md", ""),
            parse_status="not_found",
            can_edit=False,
            error_reason=f"Note '{note_path}' not found in current scan/scope.",
        )

    # Check parse status fail-closed (V11-007)
    if note.parse_status in FAILED_PARSE_STATUSES:
        return NoteWorkspaceInspectResult(
            note_path=note.path,
            name=note.name,
            parse_status=note.parse_status.value,
            can_edit=False,
            error_reason=f"Note has malformed or unreadable frontmatter ({note.parse_status.value}). Editing is blocked to prevent data corruption.",
        )

    # Check duplicate keys fail-closed (V11-007)
    if note.duplicate_keys:
        dup_list = ", ".join(note.duplicate_keys)
        return NoteWorkspaceInspectResult(
            note_path=note.path,
            name=note.name,
            parse_status=note.parse_status.value,
            can_edit=False,
            error_reason=f"Note contains duplicate YAML keys ({dup_list}). Property Studio refuses to guess which value to keep.",
            duplicate_keys=list(note.duplicate_keys),
        )

    orig_props = {}
    for k, v in note.properties.items():
        orig_props[k] = v.raw

    return NoteWorkspaceInspectResult(
        note_path=note.path,
        name=note.name,
        parse_status=note.parse_status.value,
        can_edit=True,
        original_properties=orig_props,
    )


def compute_workspace_diff_and_frontmatter(
    original_note: Note | None,
    updated_values: dict[str, Any],
    schema: Schema | None = None,
    deleted_keys: list[str] | None = None,
) -> NoteWorkspaceDiffResult:
    """Compute semantic property diff and serialize valid frontmatter (V11-006, V11-008)."""
    deleted_set = set(deleted_keys or [])
    errors: list[str] = []
    warnings: list[str] = []
    diffs: list[PropertyDiff] = []

    # If original_note is provided and corrupted/duplicate-key, fail closed (V11-007)
    if original_note is not None:
        if original_note.parse_status in FAILED_PARSE_STATUSES:
            errors.append(f"Cannot edit note with corrupt frontmatter: {original_note.parse_status.value}")
            return NoteWorkspaceDiffResult(
                note_path=original_note.path,
                valid=False,
                can_copy=False,
                errors=errors,
                frontmatter_preview="",
            )
        if original_note.duplicate_keys:
            errors.append(f"Cannot edit note with duplicate keys: {', '.join(original_note.duplicate_keys)}")
            return NoteWorkspaceDiffResult(
                note_path=original_note.path,
                valid=False,
                can_copy=False,
                errors=errors,
                frontmatter_preview="",
            )

    orig_map: dict[str, Any] = {}
    if original_note is not None:
        orig_map = {k: v.raw for k, v in original_note.properties.items()}

    # Check required fields from schema if schema provided
    if schema is not None:
        for prop in schema.properties:
            if prop.required:
                val = updated_values.get(prop.name)
                if val is None or (isinstance(val, str) and not val.strip()):
                    # check if existing note had a non-empty value that was not deleted
                    if prop.name not in orig_map or prop.name in deleted_set:
                        errors.append(f"Required property '{prop.name}' is missing or empty.")

    # Build merged dictionary (V11-006: preserve unrelated properties)
    merged: dict[str, Any] = {}
    all_keys = sorted(set(orig_map.keys()) | set(updated_values.keys()))

    for key in all_keys:
        if key in deleted_set:
            if key in orig_map:
                diffs.append(PropertyDiff(key=key, change_type="deleted", old_value=orig_map[key]))
            continue

        if key in updated_values and key in orig_map:
            new_val = updated_values[key]
            old_val = orig_map[key]
            if new_val != old_val:
                diffs.append(PropertyDiff(key=key, change_type="modified", old_value=old_val, new_value=new_val))
                merged[key] = new_val
            else:
                diffs.append(PropertyDiff(key=key, change_type="preserved", old_value=old_val, new_value=new_val))
                merged[key] = old_val
        elif key in updated_values:
            new_val = updated_values[key]
            diffs.append(PropertyDiff(key=key, change_type="added", new_value=new_val))
            merged[key] = new_val
        else:
            # Preserved unrelated property from existing note (V11-006)
            old_val = orig_map[key]
            diffs.append(PropertyDiff(key=key, change_type="preserved", old_value=old_val, new_value=old_val))
            merged[key] = old_val

    is_valid = len(errors) == 0
    can_copy = is_valid

    # Generate YAML frontmatter
    fm_lines = ["---"]
    for k, v in merged.items():
        if v is None or v == "":
            fm_lines.append(f"{k}:")
        elif isinstance(v, bool):
            fm_lines.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, (int, float)):
            fm_lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            fm_lines.append(f"{k}:")
            for item in v:
                fm_lines.append(f"  - {item}")
        else:
            s_val = str(v)
            if "\n" in s_val:
                fm_lines.append(f"{k}: |-\n  " + s_val.replace("\n", "\n  "))
            elif ":" in s_val or "#" in s_val or s_val.startswith("[[") or s_val.startswith('"') or s_val.startswith("'"):
                # If already starts with quotes, format cleanly
                if (s_val.startswith('"') and s_val.endswith('"')) or (s_val.startswith("'") and s_val.endswith("'")):
                    fm_lines.append(f"{k}: {s_val}")
                else:
                    escaped = s_val.replace('"', '\\"')
                    fm_lines.append(f'{k}: "{escaped}"')
            else:
                fm_lines.append(f"{k}: {s_val}")
    fm_lines.append("---")
    frontmatter_text = "\n".join(fm_lines) + "\n"

    return NoteWorkspaceDiffResult(
        note_path=original_note.path if original_note else None,
        valid=is_valid,
        can_copy=can_copy,
        errors=errors,
        warnings=warnings,
        diffs=diffs,
        merged_properties=merged,
        frontmatter_preview=frontmatter_text,
    )
