"""Note Properties Workspace domain model, search, and diff engine (M006).

REQ-026 / REQ-027 / DEC-022 / DEC-023:
Supports:
1. Inspecting existing notes' frontmatter.
2. Editing existing properties while preserving unrelated properties across edits (V11-006).
3. Fail-closed protection against corrupt frontmatter and duplicate keys (V11-007).
4. Generating semantic diffs and copyable frontmatter with copy button fail-closed (V11-008).
5. Disambiguating duplicate base names across folders and whole-vault search (V11-005, R05).
6. Strict YAML serialization round-trip verification gate (R08).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.fill import render_frontmatter, roundtrip_check
from app.core.model import FAILED_PARSE_STATUSES, Note, ParseStatus, Schema, SchemaProperty, VaultScan
from app.core.scope import ScopeSpec, is_note_in_scope


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
    roundtrip_matches: bool = True

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
            "roundtrip_matches": self.roundtrip_matches,
        }


def find_candidate_notes(
    scan: VaultScan, query: str = "", current_scope: ScopeSpec | None = None
) -> list[dict[str, Any]]:
    """Find notes across the whole vault with relative paths, ambiguity detection, and Scope priority (R05)."""
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
        in_scope = is_note_in_scope(note.path, current_scope) if current_scope else True
        matches.append({
            "path": note.path,
            "name": note.name,
            "has_properties": note.has_properties,
            "is_ambiguous_basename": is_ambiguous,
            "in_current_scope": in_scope,
            "display_label": f"{note.name} ({note.path})" if is_ambiguous else f"{note.name} — {note.path}",
        })

    # Prioritize in-scope notes first, then alphabetical by path
    matches.sort(key=lambda x: (not x["in_current_scope"], x["path"].casefold()))
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
            error_reason=f"Note '{note_path}' was not found in the vault scan.",
        )

    if note.parse_status in FAILED_PARSE_STATUSES or note.parse_failed:
        error_msg = (
            f"Frontmatter parse failed: {note.issues[0].message if note.issues else note.parse_status.value}."
        )
        return NoteWorkspaceInspectResult(
            note_path=note.path,
            name=note.name,
            parse_status=note.parse_status.value,
            can_edit=False,
            error_reason=error_msg,
        )

    if note.duplicate_keys:
        dup_list = ", ".join(sorted(note.duplicate_keys))
        return NoteWorkspaceInspectResult(
            note_path=note.path,
            name=note.name,
            parse_status=note.parse_status.value,
            can_edit=False,
            error_reason=f"Duplicate YAML keys detected ({dup_list}). Fail closed to avoid data corruption.",
            duplicate_keys=list(note.duplicate_keys),
            original_properties={k: v.raw for k, v in note.properties.items()},
        )

    props: dict[str, Any] = {}
    for key, val in note.properties.items():
        props[key] = val.raw

    return NoteWorkspaceInspectResult(
        note_path=note.path,
        name=note.name,
        parse_status=note.parse_status.value,
        can_edit=True,
        original_properties=props,
    )


def are_semantically_equal(val1: Any, val2: Any) -> bool:
    """Compare two property values for semantic equality ignoring display formatting differences (HA-F10)."""
    if val1 == val2:
        return True
    if val1 is None or val2 is None:
        return False
    # Boolean equality (e.g. True vs "true", "True")
    if isinstance(val1, bool) or isinstance(val2, bool):
        s1 = str(val1).strip().lower()
        s2 = str(val2).strip().lower()
        if s1 in ("true", "false") and s2 in ("true", "false"):
            return s1 == s2
    # Number equality (e.g. 100 vs 100.0 vs "100")
    try:
        if isinstance(val1, (int, float, str)) and isinstance(val2, (int, float, str)):
            f1 = float(str(val1).strip())
            f2 = float(str(val2).strip())
            if f1 == f2:
                return True
    except (ValueError, TypeError):
        pass
    # List / Tags / Note-link list equality (e.g. ['a', 'b'] vs "a, b" vs "a,b")
    items1 = None
    items2 = None
    if isinstance(val1, list):
        items1 = [str(x).strip() for x in val1 if str(x).strip()]
    elif isinstance(val1, str) and ("," in val1 or val1.strip()):
        items1 = [x.strip() for x in val1.split(",") if x.strip()]

    if isinstance(val2, list):
        items2 = [str(x).strip() for x in val2 if str(x).strip()]
    elif isinstance(val2, str) and ("," in val2 or val2.strip()):
        items2 = [x.strip() for x in val2.split(",") if x.strip()]

    if items1 is not None and items2 is not None:
        return items1 == items2

    return str(val1).strip() == str(val2).strip()


def compute_workspace_diff_and_frontmatter(
    original_note: Note | None,
    updated_values: dict[str, Any],
    schema: Schema | None = None,
    deleted_keys: list[str] | None = None,
    touched_keys: list[str] | None = None,
) -> NoteWorkspaceDiffResult:
    """Compute semantic diff, merge properties, and enforce YAML round-trip safety gate (R08)."""
    errors: list[str] = []
    warnings: list[str] = []
    diffs: list[PropertyDiff] = []
    deleted_set = set(deleted_keys or [])
    touched_set = set(touched_keys) if touched_keys is not None else None

    if original_note is not None:
        if original_note.parse_failed or original_note.parse_status in FAILED_PARSE_STATUSES:
            err_text = original_note.issues[0].message if original_note.issues else original_note.parse_status.value
            errors.append(f"Cannot edit note with parse failure: {err_text}")
            return NoteWorkspaceDiffResult(
                note_path=original_note.path,
                valid=False,
                can_copy=False,
                errors=errors,
                frontmatter_preview="",
                roundtrip_matches=False,
            )
        if original_note.duplicate_keys:
            errors.append(f"Cannot edit note with duplicate keys: {', '.join(original_note.duplicate_keys)}")
            return NoteWorkspaceDiffResult(
                note_path=original_note.path,
                valid=False,
                can_copy=False,
                errors=errors,
                frontmatter_preview="",
                roundtrip_matches=False,
            )

    orig_map: dict[str, Any] = {}
    if original_note is not None:
        orig_map = {k: v.raw for k, v in original_note.properties.items()}

    coerced_updates: dict[str, Any] = {}
    schema_prop_names: set[str] = set()

    # Canonical Schema constraint validation & type coercion (REQ-043)
    if schema is not None:
        from .fill import coerce_value
        schema_prop_names = {p.name for p in schema.properties}

        for prop in schema.properties:
            is_deleted = prop.name in deleted_set
            raw_val = updated_values.get(prop.name)

            # If the user touched or supplied the property
            if prop.name in updated_values and not is_deleted:
                coerced, prop_errs = coerce_value(prop, raw_val)
                if prop_errs:
                    errors.extend(prop_errs)
                elif coerced is not None:
                    coerced_updates[prop.name] = coerced
            elif prop.required and not is_deleted:
                if prop.name not in orig_map:
                    errors.append(f"Required property '{prop.name}' is missing or empty.")

    # Build merged dictionary (V11-006 & REQ-043: preserve outside-schema native types byte-faithfully)
    merged: dict[str, Any] = {}
    all_keys = sorted(set(orig_map.keys()) | set(updated_values.keys()))

    for key in all_keys:
        if key in deleted_set:
            if key in orig_map:
                diffs.append(PropertyDiff(key=key, change_type="deleted", old_value=orig_map[key]))
            continue

        if key in orig_map:
            old_val = orig_map[key]
            pv = original_note.properties[key] if original_note else None
            user_raw = updated_values.get(key)

            # Determine untouched status consistently across both schema & outside-schema properties (HA-F10)
            is_untouched = False
            if touched_set is not None:
                is_untouched = (key not in touched_set)
            else:
                if key not in updated_values:
                    is_untouched = True
                elif are_semantically_equal(old_val, user_raw):
                    is_untouched = True

            if is_untouched:
                # Untouched property: 100% byte-faithfully preserve original raw object
                diffs.append(PropertyDiff(key=key, change_type="preserved", old_value=old_val, new_value=old_val))
                merged[key] = old_val
                continue

            # User genuinely touched/modified this existing property
            if key in schema_prop_names and key in coerced_updates:
                new_val = coerced_updates[key]
            elif pv is not None:
                from .fill import coerce_value
                temp_prop = SchemaProperty(name=key, storage_type=pv.storage_type)
                coerced, prop_errs = coerce_value(temp_prop, user_raw)
                if prop_errs:
                    errors.extend(prop_errs)
                new_val = coerced if coerced is not None else user_raw
            else:
                new_val = user_raw

            if are_semantically_equal(old_val, new_val):
                diffs.append(PropertyDiff(key=key, change_type="preserved", old_value=old_val, new_value=old_val))
                merged[key] = old_val
            else:
                diffs.append(PropertyDiff(key=key, change_type="modified", old_value=old_val, new_value=new_val))
                merged[key] = new_val
            continue

        # Property is newly added (not in orig_map)
        new_val = coerced_updates[key] if key in coerced_updates else updated_values[key]
        diffs.append(PropertyDiff(key=key, change_type="added", new_value=new_val))
        merged[key] = new_val

    # Generate standard governed YAML frontmatter
    frontmatter_text = render_frontmatter(merged) if merged else ""

    # Strict YAML roundtrip verification gate (R08 / OPS-AC-010)
    rt_matches = True
    if frontmatter_text:
        rt = roundtrip_check(frontmatter_text, merged)
        rt_matches = rt.get("matches", False)
        if not rt_matches:
            for diff in rt.get("differences", []):
                errors.append(f"YAML round-trip semantic mismatch: {diff}")

    is_valid = len(errors) == 0 and rt_matches
    can_copy = is_valid

    return NoteWorkspaceDiffResult(
        note_path=original_note.path if original_note else None,
        valid=is_valid,
        can_copy=can_copy,
        errors=errors,
        warnings=warnings,
        diffs=diffs,
        merged_properties=merged,
        frontmatter_preview=frontmatter_text,
        roundtrip_matches=rt_matches,
    )
