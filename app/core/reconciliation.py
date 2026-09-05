"""Existing Note Reconciliation & 4-State Drift Engine (REQ-043, DEC-028, DEC-029).

Analyzes an existing note's frontmatter against an adopted or named schema:
1. MATCHES: Property exists and satisfies schema type/value constraints.
2. MISSING: Property defined in schema but absent from note.
3. CONFLICT: Property exists but has type mismatch, disallowed value, or validation error.
4. OUTSIDE_SCHEMA: Property exists in note but is not part of schema.
   Core Invariant (DEC-029): Outside-schema properties are strictly preserved
   and never silently deleted or discarded.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

from .model import Schema, SchemaProperty, StorageType, UIControl
from .fill import render_frontmatter


class PropertyReconcileState(str, enum.Enum):
    MATCHES = "matches"
    MISSING = "missing"
    CONFLICT = "conflict"
    OUTSIDE_SCHEMA = "outside_schema"


@dataclass
class PropertyReconcileItem:
    name: str
    state: PropertyReconcileState
    current_value: Any = None
    expected_type: str | None = None
    expected_control: str | None = None
    required: bool = False
    allowed_values: list[str] | None = None
    conflict_reason: str = ""
    suggested_value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "current_value": self.current_value,
            "expected_type": self.expected_type,
            "expected_control": self.expected_control,
            "required": self.required,
            "allowed_values": self.allowed_values,
            "conflict_reason": self.conflict_reason,
            "suggested_value": self.suggested_value,
        }


@dataclass
class ReconciliationReport:
    note_path: str
    schema_name: str
    schema_id: str | None
    items: list[PropertyReconcileItem] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_path": self.note_path,
            "schema_name": self.schema_name,
            "schema_id": self.schema_id,
            "items": [item.to_dict() for item in self.items],
            "summary": self.summary,
        }


def reconcile_note_frontmatter(
    note_properties: dict[str, Any],
    schema_properties: list[dict[str, Any]],
    schema_name: str = "adopted-schema",
    schema_id: str | None = None,
    note_path: str = "",
) -> ReconciliationReport:
    """Analyze note properties against schema properties, classifying into 4 states."""
    schema_props_map: dict[str, dict[str, Any]] = {
        p.get("name", "").strip(): p for p in schema_properties if p.get("name")
    }

    items: list[PropertyReconcileItem] = []
    seen_keys: set[str] = set()

    # 1. Evaluate schema-defined properties
    for name, sp in schema_props_map.items():
        seen_keys.add(name)
        exp_type = str(sp.get("storage_type") or "text")
        exp_control = str(sp.get("ui_control") or "plain")
        required = bool(sp.get("required", False))
        allowed = sp.get("allowed_values")

        if name not in note_properties:
            items.append(
                PropertyReconcileItem(
                    name=name,
                    state=PropertyReconcileState.MISSING,
                    current_value=None,
                    expected_type=exp_type,
                    expected_control=exp_control,
                    required=required,
                    allowed_values=allowed,
                    conflict_reason="Property is missing from note." if required else "Optional property not present.",
                )
            )
        else:
            val = note_properties[name]
            # Check for conflict
            is_conflict = False
            reason = ""

            # Check allowed values if specified
            if allowed and isinstance(allowed, list) and len(allowed) > 0:
                if isinstance(val, (list, tuple)):
                    invalid_vals = [v for v in val if str(v) not in allowed]
                    if invalid_vals:
                        is_conflict = True
                        reason = f"Values {invalid_vals} not in allowed options: {allowed}"
                elif str(val) not in allowed:
                    is_conflict = True
                    reason = f"Value '{val}' not in allowed options: {allowed}"

            # Check type conflicts
            if not is_conflict:
                if exp_type in ("number", "integer"):
                    if not isinstance(val, (int, float)) and not str(val).replace(".", "", 1).isdigit():
                        is_conflict = True
                        reason = f"Expected numeric value, got '{val}'."
                elif exp_type == "checkbox" or exp_type == "boolean":
                    if not isinstance(val, bool) and str(val).lower() not in ("true", "false"):
                        is_conflict = True
                        reason = f"Expected boolean, got '{val}'."
                elif exp_type in ("list", "multitext", "tags"):
                    if not isinstance(val, (list, tuple)):
                        is_conflict = True
                        reason = f"Expected list/array, got {type(val).__name__}."

            state = PropertyReconcileState.CONFLICT if is_conflict else PropertyReconcileState.MATCHES
            items.append(
                PropertyReconcileItem(
                    name=name,
                    state=state,
                    current_value=val,
                    expected_type=exp_type,
                    expected_control=exp_control,
                    required=required,
                    allowed_values=allowed,
                    conflict_reason=reason,
                )
            )

    # 2. Evaluate outside-schema properties (Must be preserved!)
    for name, val in note_properties.items():
        if name not in seen_keys:
            items.append(
                PropertyReconcileItem(
                    name=name,
                    state=PropertyReconcileState.OUTSIDE_SCHEMA,
                    current_value=val,
                    conflict_reason="Preserved non-schema property (never discarded).",
                )
            )

    summary = {
        "matches": sum(1 for i in items if i.state == PropertyReconcileState.MATCHES),
        "missing": sum(1 for i in items if i.state == PropertyReconcileState.MISSING),
        "conflict": sum(1 for i in items if i.state == PropertyReconcileState.CONFLICT),
        "outside_schema": sum(1 for i in items if i.state == PropertyReconcileState.OUTSIDE_SCHEMA),
        "total": len(items),
    }

    return ReconciliationReport(
        note_path=note_path,
        schema_name=schema_name,
        schema_id=schema_id,
        items=items,
        summary=summary,
    )


def preview_reconciled_frontmatter(
    original_properties: dict[str, Any],
    schema_properties: list[dict[str, Any]],
    resolved_values: dict[str, Any],
) -> dict[str, Any]:
    """Generate reconciled properties preserving outside-schema properties."""
    merged: dict[str, Any] = {}

    # 1. Copy outside-schema properties exactly as is
    schema_names = {p.get("name", "").strip() for p in schema_properties if p.get("name")}
    for k, v in original_properties.items():
        if k not in schema_names:
            merged[k] = v

    # 2. Add or update schema-defined properties
    for sp in schema_properties:
        name = sp.get("name", "").strip()
        if not name:
            continue
        if name in resolved_values:
            merged[name] = resolved_values[name]
        elif name in original_properties:
            merged[name] = original_properties[name]

    # Render YAML
    yaml_text = render_frontmatter(merged)

    # Compute diff
    diff_added = [k for k in merged if k not in original_properties]
    diff_modified = [k for k in merged if k in original_properties and merged[k] != original_properties[k]]
    diff_preserved = [k for k in merged if k in original_properties and merged[k] == original_properties[k]]

    return {
        "merged_properties": merged,
        "yaml_text": yaml_text,
        "diff": {
            "added": diff_added,
            "modified": diff_modified,
            "preserved": diff_preserved,
        },
    }
