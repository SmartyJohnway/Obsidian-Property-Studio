"""Schema Versioning & Migration Planner (REQ-046, DEC-031).

Compares two schema versions, categorizes changes, detects breaking differences,
and computes a structured migration plan without writing to the Vault.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class MigrationChangeType(str, enum.Enum):
    ADDED_PROPERTY = "added_property"
    DELETED_PROPERTY = "deleted_property"
    STORAGE_TYPE_CHANGED = "storage_type_changed"
    UI_CONTROL_CHANGED = "ui_control_changed"
    REQUIRED_CHANGED = "required_changed"
    ALLOWED_VALUES_CHANGED = "allowed_values_changed"


@dataclass
class PropertyChangeDetail:
    property_name: str
    change_type: MigrationChangeType
    is_breaking: bool
    description: str
    old_value: Any = None
    new_value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "property_name": self.property_name,
            "change_type": self.change_type.value,
            "is_breaking": self.is_breaking,
            "description": self.description,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class MigrationPlan:
    source_version: str
    target_version: str
    is_breaking: bool
    suggested_bump: str  # "major" | "minor" | "patch"
    changes: list[PropertyChangeDetail] = field(default_factory=list)
    migration_steps: list[str] = field(default_factory=list)
    scope_notes_total: int = 0
    scope_affected_notes_count: int = 0
    affected_notes_by_property: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_version": self.source_version,
            "target_version": self.target_version,
            "is_breaking": self.is_breaking,
            "suggested_bump": self.suggested_bump,
            "changes": [c.to_dict() for c in self.changes],
            "migration_steps": self.migration_steps,
            "scope_notes_total": self.scope_notes_total,
            "scope_affected_notes_count": self.scope_affected_notes_count,
            "affected_notes_by_property": self.affected_notes_by_property,
        }


def plan_schema_migration(
    source_properties: list[dict[str, Any]],
    target_properties: list[dict[str, Any]],
    source_version: str = "1.0.0",
    target_version: str = "1.1.0",
    notes: list[Any] | None = None,
) -> MigrationPlan:
    """Analyze differences between two schema property sets and compute a Scope-aware migration plan (DEC-031)."""
    src_map = {p.get("name", "").strip(): p for p in source_properties if p.get("name")}
    tgt_map = {p.get("name", "").strip(): p for p in target_properties if p.get("name")}

    changes: list[PropertyChangeDetail] = []
    has_breaking = False
    steps: list[str] = []

    # 1. Check added properties
    for name, tp in tgt_map.items():
        if name not in src_map:
            req = bool(tp.get("required", False))
            is_breaking = req  # Adding a required property can break existing notes
            if is_breaking:
                has_breaking = True
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.ADDED_PROPERTY,
                    is_breaking=is_breaking,
                    description=f"Added property '{name}' (required={req}).",
                    new_value=tp,
                )
            )

    # 2. Check deleted properties
    for name, sp in src_map.items():
        if name not in tgt_map:
            # Deleting a property is breaking
            has_breaking = True
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.DELETED_PROPERTY,
                    is_breaking=True,
                    description=f"Removed property '{name}' from target schema.",
                    old_value=sp,
                )
            )

    # 3. Check modified properties
    for name in src_map.keys() & tgt_map.keys():
        sp = src_map[name]
        tp = tgt_map[name]

        # Storage type change
        src_type = str(sp.get("storage_type") or "text")
        tgt_type = str(tp.get("storage_type") or "text")
        if src_type != tgt_type:
            has_breaking = True
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.STORAGE_TYPE_CHANGED,
                    is_breaking=True,
                    description=f"Storage type changed from '{src_type}' to '{tgt_type}'.",
                    old_value=src_type,
                    new_value=tgt_type,
                )
            )

        # Required flag changed
        src_req = bool(sp.get("required", False))
        tgt_req = bool(tp.get("required", False))
        if not src_req and tgt_req:
            has_breaking = True
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.REQUIRED_CHANGED,
                    is_breaking=True,
                    description=f"Property '{name}' became required.",
                    old_value=False,
                    new_value=True,
                )
            )
        elif src_req and not tgt_req:
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.REQUIRED_CHANGED,
                    is_breaking=False,
                    description=f"Property '{name}' is now optional.",
                    old_value=True,
                    new_value=False,
                )
            )

        # Allowed values
        src_allowed = sp.get("allowed_values") or []
        tgt_allowed = tp.get("allowed_values") or []
        if src_allowed != tgt_allowed:
            # Check if narrowed
            narrowed = bool(set(src_allowed) - set(tgt_allowed))
            if narrowed:
                has_breaking = True
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.ALLOWED_VALUES_CHANGED,
                    is_breaking=narrowed,
                    description=f"Allowed values changed from {src_allowed} to {tgt_allowed}.",
                    old_value=src_allowed,
                    new_value=tgt_allowed,
                )
            )

        # UI control
        src_ctrl = str(sp.get("ui_control") or "plain")
        tgt_ctrl = str(tp.get("ui_control") or "plain")
        if src_ctrl != tgt_ctrl:
            changes.append(
                PropertyChangeDetail(
                    property_name=name,
                    change_type=MigrationChangeType.UI_CONTROL_CHANGED,
                    is_breaking=False,
                    description=f"UI control widget changed from '{src_ctrl}' to '{tgt_ctrl}'.",
                    old_value=src_ctrl,
                    new_value=tgt_ctrl,
                )
            )

    # Derive suggested SemVer bump
    if has_breaking:
        bump = "major"
    elif any(c.change_type == MigrationChangeType.ADDED_PROPERTY for c in changes):
        bump = "minor"
    else:
        bump = "patch"

    # Derive migration steps
    for c in changes:
        if c.change_type == MigrationChangeType.DELETED_PROPERTY:
            steps.append(f"Inspect notes containing '{c.property_name}' to preserve or migrate values before schema adoption.")
        elif c.change_type == MigrationChangeType.STORAGE_TYPE_CHANGED:
            steps.append(f"Convert '{c.property_name}' values from {c.old_value} to {c.new_value}.")
        elif c.change_type == MigrationChangeType.ADDED_PROPERTY and c.is_breaking:
            steps.append(f"Populate newly required property '{c.property_name}' across existing notes.")

    # Scope-aware evaluation if notes are provided (DEC-031)
    affected_by_prop: dict[str, list[str]] = {}
    all_affected_notes: set[str] = set()
    total_notes_count = len(notes) if notes is not None else 0

    if notes:
        for n in notes:
            n_props = {}
            if hasattr(n, "properties") and isinstance(n.properties, dict):
                n_props = {k: (v.raw if hasattr(v, "raw") else v) for k, v in n.properties.items()}
            elif hasattr(n, "frontmatter") and isinstance(n.frontmatter, dict):
                n_props = n.frontmatter

            for c in changes:
                pname = c.property_name
                # Note has property that is deleted or modified
                if pname in n_props:
                    if c.change_type in (MigrationChangeType.DELETED_PROPERTY, MigrationChangeType.STORAGE_TYPE_CHANGED, MigrationChangeType.ALLOWED_VALUES_CHANGED):
                        affected_by_prop.setdefault(pname, []).append(n.path)
                        all_affected_notes.add(n.path)
                # Note is missing newly required property
                elif c.change_type == MigrationChangeType.ADDED_PROPERTY and c.is_breaking:
                    affected_by_prop.setdefault(pname, []).append(n.path)
                    all_affected_notes.add(n.path)

        if all_affected_notes:
            steps.insert(0, f"Scope evaluation: Found {len(all_affected_notes)} out of {total_notes_count} notes in current Scope requiring migration attention.")

    return MigrationPlan(
        source_version=source_version,
        target_version=target_version,
        is_breaking=has_breaking,
        suggested_bump=bump,
        changes=changes,
        migration_steps=steps,
        scope_notes_total=total_notes_count,
        scope_affected_notes_count=len(all_affected_notes),
        affected_notes_by_property=affected_by_prop,
    )

