"""External AI/Agent schema proposal import (M009).

The core application never calls an LLM. A proposal is *untrusted advisory
input* (DEC-009/DEC-010, AGENTS 33): it is versioned, schema-validated,
compared against the real vault, and can never modify the vault.
"""

from __future__ import annotations

import json
from typing import Any

from .design import check_property_reuse
from .inventory import Inventory
from .model import (
    Schema,
    SchemaProperty,
    StorageType,
    UIControl,
    UI_CONTROL_ALLOWED_STORAGE,
)

PROPOSAL_CONTRACT_VERSION = "1.0"
SUPPORTED_PROPOSAL_VERSIONS = ("1.0",)

KNOWN_TOP_LEVEL = {
    "proposal_version",
    "schema_name",
    "description",
    "properties",
    "generated_by",
    "provenance",
    "notes",
}
KNOWN_PROPERTY_FIELDS = {
    "name",
    "storage_type",
    "ui_control",
    "required",
    "reason",
    "allowed_values",
    "confidence",
    "evidence",
    "provenance",
}


class ProposalError(ValueError):
    pass


def parse_proposal_text(text: str) -> dict[str, Any]:
    """Parse raw text into JSON, failing honestly (OPS-AC-023)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProposalError(
            f"The proposal file is not valid JSON (line {exc.lineno}, "
            f"column {exc.colno}): {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise ProposalError(
            "The proposal must be a JSON object with 'proposal_version', "
            f"'schema_name' and 'properties' — found {type(data).__name__}."
        )
    return data


def validate_proposal(data: dict[str, Any]) -> dict[str, Any]:
    """Validate a parsed proposal. Returns a report; never raises for content."""
    errors: list[str] = []
    warnings: list[str] = []

    version = data.get("proposal_version")
    if version is None:
        errors.append("Missing required field 'proposal_version'.")
    elif not isinstance(version, str):
        errors.append("'proposal_version' must be a string.")
    elif version not in SUPPORTED_PROPOSAL_VERSIONS:
        errors.append(
            f"Unsupported proposal_version '{version}'. Supported: "
            f"{', '.join(SUPPORTED_PROPOSAL_VERSIONS)}."
        )

    name = data.get("schema_name")
    if not isinstance(name, str) or not name.strip():
        errors.append("'schema_name' must be a non-empty string.")

    for key in sorted(set(data) - KNOWN_TOP_LEVEL):
        warnings.append(f"Unknown top-level field '{key}' was ignored.")

    properties = data.get("properties")
    props: list[SchemaProperty] = []
    extras: list[dict[str, Any]] = []
    if not isinstance(properties, list) or not properties:
        errors.append("'properties' must be a non-empty list.")
        properties = []

    seen: set[str] = set()
    for index, raw in enumerate(properties):
        label = f"properties[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{label} must be an object.")
            continue
        prop_name = raw.get("name")
        if not isinstance(prop_name, str) or not prop_name.strip():
            errors.append(f"{label}.name must be a non-empty string.")
            continue
        if prop_name in seen:
            errors.append(f"{label}.name '{prop_name}' is declared more than once.")
            continue
        seen.add(prop_name)

        storage_raw = raw.get("storage_type")
        try:
            storage = StorageType(str(storage_raw))
        except ValueError:
            errors.append(
                f"{label}.storage_type '{storage_raw}' is not a supported Obsidian "
                "property type "
                f"({', '.join(t.value for t in StorageType if t is not StorageType.UNSUPPORTED)})."
            )
            continue
        if storage in (StorageType.UNSUPPORTED, StorageType.EMPTY):
            errors.append(
                f"{label}.storage_type '{storage.value}' cannot be requested by a "
                "proposal."
            )
            continue

        control_raw = raw.get("ui_control") or "plain"
        try:
            control = UIControl(str(control_raw))
        except ValueError:
            errors.append(
                f"{label}.ui_control '{control_raw}' is not supported "
                f"({', '.join(c.value for c in UIControl)})."
            )
            continue
        if storage.value not in UI_CONTROL_ALLOWED_STORAGE[control.value]:
            errors.append(
                f"{label}: ui_control '{control.value}' is not compatible with "
                f"storage_type '{storage.value}'."
            )
            continue

        required = raw.get("required", False)
        if not isinstance(required, bool):
            errors.append(f"{label}.required must be true or false.")
            continue

        allowed = raw.get("allowed_values")
        if allowed is not None:
            if not isinstance(allowed, list) or not all(
                isinstance(a, (str, int, float)) for a in allowed
            ):
                errors.append(f"{label}.allowed_values must be null or a list of scalars.")
                continue
            allowed = tuple(str(a) for a in allowed)

        confidence = raw.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(f"{label}.confidence must be null or a number.")
                continue
            if not 0.0 <= float(confidence) <= 1.0:
                errors.append(f"{label}.confidence must be between 0 and 1.")
                continue
            confidence = float(confidence)

        for key in sorted(set(raw) - KNOWN_PROPERTY_FIELDS):
            warnings.append(f"Unknown field '{key}' in {label} was ignored.")

        prop = SchemaProperty(
            name=prop_name,
            storage_type=storage,
            ui_control=control,
            required=required,
            reason=str(raw.get("reason", "") or ""),
            allowed_values=allowed,
            origin=f"proposal:{data.get('schema_name', 'unnamed')}",
            confidence=confidence,
        )
        prop_errors = prop.validate()
        if prop_errors:
            errors.extend(f"{label}: {e}" for e in prop_errors)
            continue
        props.append(prop)
        extras.append(
            {
                "name": prop_name,
                "reason": prop.reason,
                "confidence": prop.confidence,
                "evidence": raw.get("evidence"),
                "provenance": raw.get("provenance"),
            }
        )

    schema = Schema(
        name=str(name) if isinstance(name, str) else "",
        description=str(data.get("description", "") or ""),
        properties=props,
    )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "proposal_version": version,
        "contract_version": PROPOSAL_CONTRACT_VERSION,
        "schema": schema.to_dict() if not errors else None,
        "_schema_obj": schema if not errors else None,
        "provenance": {
            "generated_by": data.get("generated_by"),
            "provenance": data.get("provenance"),
            "notes": data.get("notes"),
            "per_property": extras,
        },
        "vault_modified": False,
        "trust": "advisory — validated locally against your vault; never applied automatically",
    }


def compare_with_vault(schema: Schema, inv: Inventory) -> list[dict[str, Any]]:
    comparisons = []
    for prop in schema.properties:
        review = check_property_reuse(prop.name, inv)
        entry = inv.get(prop.name)
        review["proposed_storage_type"] = prop.storage_type.value
        review["proposed_ui_control"] = prop.ui_control.value
        review["proposed_required"] = prop.required
        review["reason"] = prop.reason
        review["confidence"] = prop.confidence
        if entry is not None:
            review["vault_dominant_type"] = entry.dominant_type
            review["type_agreement"] = (
                "matches" if entry.dominant_type == prop.storage_type.value else "differs"
            )
        comparisons.append(review)
    return comparisons


def import_proposal(text: str, inv: Inventory | None) -> dict[str, Any]:
    """Full import pipeline used by the API/UI."""
    try:
        data = parse_proposal_text(text)
    except ProposalError as exc:
        return {
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "schema": None,
            "comparison": [],
            "vault_modified": False,
        }
    report = validate_proposal(data)
    schema_obj = report.pop("_schema_obj", None)
    report["comparison"] = (
        compare_with_vault(schema_obj, inv)
        if (schema_obj is not None and inv is not None)
        else []
    )
    return report
