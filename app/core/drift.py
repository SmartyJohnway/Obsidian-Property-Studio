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
    MISSING_REQUIRED_RELATIONSHIP = "missing_required_relationship"


def is_canonical_navigable_path(path: str) -> tuple[bool, str | None]:
    """Validate if a note path is a safe, canonical relative Vault Markdown path (HA-F12)."""
    if not path or not isinstance(path, str):
        return False, "Empty or non-string note path."
    p = path.strip()
    if p.startswith("![[") or p.startswith("[[") or "·" in p:
        return False, "Path contains wikilink or list formatting marker."
    if not p.endswith(".md"):
        return False, "Target is not a Markdown file (.md)."
    if p.startswith("/") or p.startswith("\\") or ".." in p or (len(p) > 1 and p[1] == ":"):
        return False, "Path traversal or non-relative path rejected."
    return True, None


@dataclass
class NoteDriftFinding:
    note_path: str
    category: DriftCategory
    property_key: str
    detail: str
    expected: Any = None
    actual: Any = None
    navigation_available: bool = True
    navigation_reason: str | None = None

    def __post_init__(self) -> None:
        nav_ok, reason = is_canonical_navigable_path(self.note_path)
        if not nav_ok:
            object.__setattr__(self, "navigation_available", False)
            object.__setattr__(self, "navigation_reason", reason)

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_path": self.note_path,
            "category": self.category.value,
            "property_key": self.property_key,
            "detail": self.detail,
            "expected": self.expected,
            "actual": self.actual,
            "navigation_available": self.navigation_available,
            "navigation_reason": self.navigation_reason,
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
    schema_version: str | None = None,
) -> SchemaDriftReport:
    """Analyze notes in scope against schema properties, calculating drift findings."""
    import re
    from datetime import date, datetime

    schema_map = {p.get("name", "").strip(): p for p in schema_properties if p.get("name")}
    findings: list[NoteDriftFinding] = []
    drifted_note_paths: set[str] = set()

    for note in notes:
        prop_map = note.properties if (hasattr(note, "properties") and isinstance(note.properties, dict)) else {}
        props = {}
        types_map = {}
        for k, v in prop_map.items():
            if hasattr(v, "raw"):
                props[k] = v.raw
                types_map[k] = v.storage_type.value if hasattr(v, "storage_type") else "text"
            else:
                props[k] = v
                types_map[k] = "text"
        if not props and hasattr(note, "frontmatter") and isinstance(note.frontmatter, dict):
            props = note.frontmatter
            types_map = {k: "text" for k in props}
        has_critical_drift = False

        # 0. Check Schema Version Mismatch (REQ-045: exclusively use dedicated schema_version key)
        if schema_version:
            note_ver = props.get("schema_version")
            if note_ver is not None and str(note_ver).strip() != str(schema_version).strip():
                findings.append(
                    NoteDriftFinding(
                        note_path=note.path,
                        category=DriftCategory.SCHEMA_VERSION_MISMATCH,
                        property_key="schema_version",
                        detail=f"Note declares schema version '{note_ver}', expected '{schema_version}'.",
                        expected=str(schema_version),
                        actual=str(note_ver),
                    )
                )
                has_critical_drift = True

        # 1. Schema properties evaluation
        for name, sp in schema_map.items():
            required = bool(sp.get("required", False))
            exp_type = str(sp.get("storage_type") or "text").lower()
            ctrl = str(sp.get("ui_control") or "plain").lower()
            allowed = sp.get("allowed_values")

            if name not in props:
                if required:
                    if ctrl in ("note_link", "note_link_list"):
                        findings.append(
                            NoteDriftFinding(
                                note_path=note.path,
                                category=DriftCategory.MISSING_REQUIRED_RELATIONSHIP,
                                property_key=name,
                                detail=f"Required relationship '{name}' is missing.",
                                expected=ctrl,
                                actual=None,
                            )
                        )
                    else:
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
                actual_type = types_map.get(name, "text")

                # Relationship check: if ui_control is note_link or note_link_list
                if ctrl in ("note_link", "note_link_list") and required:
                    if val is None or val == "":
                        findings.append(
                            NoteDriftFinding(
                                note_path=note.path,
                                category=DriftCategory.MISSING_REQUIRED_RELATIONSHIP,
                                property_key=name,
                                detail=f"Required relationship '{name}' is missing or empty.",
                                expected=ctrl,
                                actual=None,
                            )
                        )
                        has_critical_drift = True
                    elif ctrl == "note_link":
                        if not re.search(r"\[\[.+?\]\]", str(val)):
                            findings.append(
                                NoteDriftFinding(
                                    note_path=note.path,
                                    category=DriftCategory.MISSING_REQUIRED_RELATIONSHIP,
                                    property_key=name,
                                    detail=f"Required relationship '{name}' does not contain a valid note link: '{val}'.",
                                    expected="[[target_note]]",
                                    actual=str(val),
                                )
                            )
                            has_critical_drift = True
                    elif ctrl == "note_link_list":
                        is_list = isinstance(val, (list, tuple)) and len(val) > 0
                        all_wikilinks = is_list and all(re.search(r"\[\[.+?\]\]", str(item)) for item in val)
                        if not is_list or not all_wikilinks:
                            findings.append(
                                NoteDriftFinding(
                                    note_path=note.path,
                                    category=DriftCategory.MISSING_REQUIRED_RELATIONSHIP,
                                    property_key=name,
                                    detail=f"Required relationship list '{name}' must be a non-empty list of note links: '{val}'.",
                                    expected="[[link_1]], [[link_2]]",
                                    actual=str(val),
                                )
                            )
                            has_critical_drift = True

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

                # Check storage type mismatch using canonical PropertyValue.storage_type (REQ-045)
                type_matched = True
                if exp_type in ("number", "integer"):
                    type_matched = (actual_type in ("number", "integer"))
                elif exp_type in ("checkbox", "boolean"):
                    type_matched = (actual_type in ("checkbox", "boolean"))
                elif exp_type == "list":
                    type_matched = (actual_type == "list")
                elif exp_type == "tags":
                    type_matched = (actual_type == "tags")
                elif exp_type == "date":
                    type_matched = (actual_type == "date")
                elif exp_type == "datetime":
                    type_matched = (actual_type == "datetime")
                elif exp_type == "text":
                    type_matched = (actual_type == "text")
                else:
                    type_matched = (actual_type == exp_type)

                if not type_matched:
                    findings.append(
                        NoteDriftFinding(
                            note_path=note.path,
                            category=DriftCategory.TYPE_MISMATCH,
                            property_key=name,
                            detail=f"Expected storage type '{exp_type}', but note has '{actual_type}' (value: {repr(val)}).",
                            expected=exp_type,
                            actual=actual_type,
                        )
                    )
                    has_critical_drift = True

        # 2. Unexpected properties
        # Exclude internal metadata properties such as schema_version
        IGNORED_UNEXPECTED = {"schema_version"}
        for k in props.keys():
            if k not in schema_map and k not in IGNORED_UNEXPECTED:
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
