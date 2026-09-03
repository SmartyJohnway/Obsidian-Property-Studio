"""Schema Drift Analysis Engine (REQ-045, DEC-028).

Evaluates notes in a scope against an assigned Expected Schema:
- Missing Required Properties
- Type Mismatches
- Value Drift (values not in allowed_values)
- Unexpected Properties (outside schema)
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

from .model import Note, VaultScan


class DriftCategory(str, enum.Enum):
    MISSING_REQUIRED = "missing_required"
    MISSING_EXPECTED = "missing_expected"
    TYPE_MISMATCH = "type_mismatch"
    VALUE_DRIFT = "value_drift"
    UNEXPECTED_PROPERTY = "unexpected_property"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"


@dataclass
class NoteDriftFinding:
    note_path: str
    category: DriftCategory
    property_key: str
    detail: str
    expected: Any = None
    actual: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_path": self.note_path,
            "category": self.category.value,
            "property_key": self.property_key,
            "detail": self.detail,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class SchemaDriftReport:
    schema_id: str
    schema_name: str
    scope_key: str
    total_notes: int
    compliant_notes: int
    compliance_rate: float
    findings: list[NoteDriftFinding] = field(default_factory=list)
    by_category: dict[str, int] = field(default_factory=dict)
    by_property: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "schema_name": self.schema_name,
            "scope_key": self.scope_key,
            "total_notes": self.total_notes,
            "compliant_notes": self.compliant_notes,
            "compliance_rate": round(self.compliance_rate, 2),
            "findings": [f.to_dict() for f in self.findings],
            "by_category": self.by_category,
            "by_property": self.by_property,
        }


def analyze_schema_drift(
    notes: list[Note],
    schema_properties: list[dict[str, Any]],
    schema_id: str,
    schema_name: str,
    scope_key: str = "default",
) -> SchemaDriftReport:
    """Analyze notes in scope against schema properties, calculating drift findings."""
    schema_map = {p.get("name", "").strip(): p for p in schema_properties if p.get("name")}
    findings: list[NoteDriftFinding] = []
    drifted_note_paths: set[str] = set()

    for note in notes:
        if hasattr(note, "properties") and isinstance(note.properties, dict):
            props = {k: (v.raw if hasattr(v, "raw") else v) for k, v in note.properties.items()}
        elif hasattr(note, "frontmatter") and isinstance(note.frontmatter, dict):
            props = note.frontmatter
        else:
            props = {}
        has_critical_drift = False

        # 1. Schema properties evaluation
        for name, sp in schema_map.items():
            required = bool(sp.get("required", False))
            exp_type = str(sp.get("storage_type") or "text")
            allowed = sp.get("allowed_values")

            if name not in props:
                if required:
                    findings.append(
                        NoteDriftFinding(
                            note_path=note.path,
                            category=DriftCategory.MISSING_REQUIRED,
                            property_key=name,
                            detail=f"Required property '{name}' is missing.",
                            expected=exp_type,
                            actual=None,
                        )
                    )
                    has_critical_drift = True
                else:
                    # Optional schema property not populated in note - record for information, but does NOT invalidate note compliance
                    findings.append(
                        NoteDriftFinding(
                            note_path=note.path,
                            category=DriftCategory.MISSING_EXPECTED,
                            property_key=name,
                            detail=f"Optional expected property '{name}' is not present in note.",
                            expected=exp_type,
                            actual=None,
                        )
                    )
            else:
                val = props[name]
                # Check allowed values
                if allowed and isinstance(allowed, list) and len(allowed) > 0:
                    if isinstance(val, (list, tuple)):
                        invalid = [v for v in val if str(v) not in allowed]
                        if invalid:
                            findings.append(
                                NoteDriftFinding(
                                    note_path=note.path,
                                    category=DriftCategory.VALUE_DRIFT,
                                    property_key=name,
                                    detail=f"Values {invalid} not in allowed options: {allowed}.",
                                    expected=allowed,
                                    actual=val,
                                )
                            )
                            has_critical_drift = True
                    elif str(val) not in allowed:
                        findings.append(
                            NoteDriftFinding(
                                note_path=note.path,
                                category=DriftCategory.VALUE_DRIFT,
                                property_key=name,
                                detail=f"Value '{val}' not in allowed options: {allowed}.",
                                expected=allowed,
                                actual=val,
                            )
                        )
                        has_critical_drift = True

                # Check type mismatch
                if exp_type in ("number", "integer"):
                    if not isinstance(val, (int, float)) and not str(val).replace(".", "", 1).isdigit():
                        findings.append(
                            NoteDriftFinding(
                                note_path=note.path,
                                category=DriftCategory.TYPE_MISMATCH,
                                property_key=name,
                                detail=f"Expected numeric value, got '{val}'.",
                                expected=exp_type,
                                actual=type(val).__name__,
                            )
                        )
                        has_critical_drift = True
                elif exp_type in ("checkbox", "boolean"):
                    if not isinstance(val, bool) and str(val).lower() not in ("true", "false"):
                        findings.append(
                            NoteDriftFinding(
                                note_path=note.path,
                                category=DriftCategory.TYPE_MISMATCH,
                                property_key=name,
                                detail=f"Expected boolean, got '{val}'.",
                                expected=exp_type,
                                actual=type(val).__name__,
                            )
                        )
                        has_critical_drift = True

        # 2. Unexpected properties
        for k in props.keys():
            if k not in schema_map:
                findings.append(
                    NoteDriftFinding(
                        note_path=note.path,
                        category=DriftCategory.UNEXPECTED_PROPERTY,
                        property_key=k,
                        detail=f"Property '{k}' is outside defined schema.",
                        expected=None,
                        actual=props[k],
                    )
                )
                has_critical_drift = True

        if has_critical_drift:
            drifted_note_paths.add(note.path)

    total_notes = len(notes)
    compliant_notes = max(0, total_notes - len(drifted_note_paths))
    rate = (compliant_notes / total_notes * 100.0) if total_notes > 0 else 100.0

    by_cat: dict[str, int] = {}
    by_prop: dict[str, int] = {}
    for f in findings:
        cat = f.category.value
        by_cat[cat] = by_cat.get(cat, 0) + 1
        by_prop[f.property_key] = by_prop.get(f.property_key, 0) + 1

    return SchemaDriftReport(
        schema_id=schema_id,
        schema_name=schema_name,
        scope_key=scope_key,
        total_notes=total_notes,
        compliant_notes=compliant_notes,
        compliance_rate=rate,
        findings=findings,
        by_category=by_cat,
        by_property=by_prop,
    )
