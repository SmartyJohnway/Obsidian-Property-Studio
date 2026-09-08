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
SUPPORTED_PROPOSAL_VERSIONS = ("1.0", "1.1")

KNOWN_TOP_LEVEL_V10 = {
    "proposal_version",
    "schema_name",
    "description",
    "properties",
    "generated_by",
    "provenance",
    "notes",
}

# Authoritative Proposal Contract 1.1 additions (REQ-046, Spec Section 2)
ADDITIVE_FIELDS_V11 = {
    "management_purpose",
    "source_context",
    "target_note_kind",
    "proposal_notes",
    "schema_target",
}

# Compatibility aliases
COMPATIBILITY_ALIASES = {
    "target_note",
    "target_scope",
    "rationale",
    "proposed_migration",
}

KNOWN_TOP_LEVEL_V11 = KNOWN_TOP_LEVEL_V10 | ADDITIVE_FIELDS_V11 | COMPATIBILITY_ALIASES
KNOWN_TOP_LEVEL = KNOWN_TOP_LEVEL_V11

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

    # Version-specific top-level field enforcement
    known_for_ver = KNOWN_TOP_LEVEL_V11 if version == "1.1" else KNOWN_TOP_LEVEL_V10
    for key in sorted(set(data) - known_for_ver):
        if version == "1.0" and key in (ADDITIVE_FIELDS_V11 | COMPATIBILITY_ALIASES):
            warnings.append(
                f"Field '{key}' is a Proposal Contract 1.1 extension and is ignored under proposal_version '1.0'."
            )
        else:
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
        # Authoritative Proposal Contract 1.1 fields (REQ-046) - populated only for 1.1 proposals
        "management_purpose": (data.get("management_purpose") or data.get("rationale")) if version == "1.1" else None,
        "source_context": data.get("source_context") if version == "1.1" else None,
        "target_note_kind": data.get("target_note_kind") if version == "1.1" else None,
        "proposal_notes": (data.get("proposal_notes") or data.get("notes")) if version == "1.1" else None,
        "schema_target": (data.get("schema_target") or data.get("target_scope")) if version == "1.1" else None,
        # Backward compatibility aliases
        "target_note": data.get("target_note") if version == "1.1" else None,
        "target_scope": (data.get("target_scope") or data.get("schema_target")) if version == "1.1" else None,
        "rationale": (data.get("rationale") or data.get("management_purpose")) if version == "1.1" else None,
        "proposed_migration": data.get("proposed_migration") if version == "1.1" else None,
        "provenance": {
            "generated_by": data.get("generated_by"),
            "provenance": data.get("provenance"),
            "notes": (data.get("notes") or data.get("proposal_notes")) if version == "1.1" else data.get("notes"),
            "per_property": extras,
        },
        "vault_modified": False,
        "trust": "advisory — validated locally against your vault; never applied automatically",
    }


def compare_proposal_four_way(
    schema: Schema,
    scoped_inv: Inventory | None = None,
    vault_inv: Inventory | None = None,
    glossary_store: Any | None = None,
    schema_library: Any | None = None,
) -> list[dict[str, Any]]:
    """Execute authoritative four-way comparison against Scope, Vault, Glossary, and Schema Library (REQ-046)."""
    comparisons = []
    schemas_list = schema_library.list_schemas() if schema_library and hasattr(schema_library, "list_schemas") else []

    # Build reverse alias index from built-in catalog and user glossary overrides
    reverse_alias_map: dict[str, str] = {}
    from .property_glossary import PROPERTY_GLOSSARY
    for entry in PROPERTY_GLOSSARY.values():
        for alias in getattr(entry, "aliases", []):
            if alias and alias.lower() != entry.canonical_key.lower():
                reverse_alias_map[alias.lower()] = entry.canonical_key

    if glossary_store and hasattr(glossary_store, "list_overrides"):
        try:
            ov_data = glossary_store.list_overrides()
            items = ov_data.values() if isinstance(ov_data, dict) else ov_data
            for item in items:
                ckey = getattr(item, "canonical_key", None)
                if not ckey and isinstance(item, dict):
                    ckey = item.get("canonical_key")
                aliases = getattr(item, "aliases", None)
                if aliases is None and isinstance(item, dict):
                    aliases = item.get("aliases")
                if ckey and aliases:
                    for alias in aliases:
                        alias_clean = str(alias).strip().lower()
                        ckey_clean = str(ckey).strip()
                        if alias_clean and alias_clean != ckey_clean.lower():
                            reverse_alias_map[alias_clean] = ckey_clean
        except Exception:
            pass

    for prop in schema.properties:
        name = prop.name
        scoped_entry = scoped_inv.get(name) if scoped_inv else None
        vault_entry = vault_inv.get(name) if vault_inv else None

        scope_usage = scoped_entry.usage_count if scoped_entry else 0
        vault_usage = vault_entry.usage_count if vault_entry else 0

        dt = None
        if vault_entry and vault_entry.dominant_type:
            dt = vault_entry.dominant_type
        elif scoped_entry and scoped_entry.dominant_type:
            dt = scoped_entry.dominant_type

        dominant_type_str = dt.value if hasattr(dt, "value") else (str(dt) if dt else None)

        # 1. Glossary Lookup
        glossary_meta = None
        if glossary_store and hasattr(glossary_store, "resolve_property"):
            try:
                glossary_meta = glossary_store.resolve_property(name)
            except Exception:
                pass

        is_known_glossary = bool(glossary_meta and glossary_meta.get("is_known", True))

        # 2. Reverse Alias Lookup
        alias_of = reverse_alias_map.get(name.lower())

        # 3. Schema Library Lookup
        schema_matches = [
            {"id": s.get("id"), "name": s.get("name"), "version": s.get("version")}
            for s in schemas_list
            if any(p.get("name") == name for p in s.get("properties", []))
        ]

        # 4. Compatibility State Determination (REQ-046)
        comp_state = "compatible"
        comp_detail = "Property aligns with vault and schema governance conventions."

        if alias_of and alias_of != name:
            comp_state = "potential_alias"
            comp_detail = f"Property '{name}' is declared as an alias of canonical property '{alias_of}'."
        elif dominant_type_str and dominant_type_str != prop.storage_type.value:
            comp_state = "type_conflict"
            comp_detail = f"Vault dominant type is '{dominant_type_str}', but proposal specifies '{prop.storage_type.value}'."
        elif prop.allowed_values and vault_entry:
            observed_vals = {str(v.value) for v in vault_entry.values.values() if v.value}
            unmatched = [ov for ov in observed_vals if ov not in prop.allowed_values]
            if unmatched:
                comp_state = "value_vocabulary_conflict"
                comp_detail = f"Observed vault values {unmatched[:3]} not in proposed allowed_values {prop.allowed_values}."
        elif vault_usage == 0 and scope_usage == 0 and not is_known_glossary and not schema_matches:
            comp_state = "new_property"
            comp_detail = f"New property '{name}' not previously recorded in vault, glossary, or schema library."

        # Base review using check_property_reuse for full v1.1 compatibility
        target_inv = vault_inv if vault_inv else scoped_inv
        review = check_property_reuse(name, target_inv) if target_inv else {}

        item = dict(review)
        item.update({
            "name": name,
            "proposed_name": name,
            "proposed_storage_type": prop.storage_type.value,
            "proposed_ui_control": prop.ui_control.value,
            "proposed_required": prop.required,
            "reason": prop.reason,
            "confidence": prop.confidence,
            "scope_usage_count": scope_usage,
            "vault_usage_count": vault_usage,
            "dominant_type": dominant_type_str,
            "glossary_entry": glossary_meta,
            "schema_library_matches": schema_matches,
            "compatibility_state": comp_state,
            "compatibility_detail": comp_detail,
            "alias_target": alias_of if (alias_of and alias_of != name) else None,
            # Legacy compatibility fields
            "exists_in_scope": scope_usage > 0,
            "in_scope_count": scope_usage,
            "exists_in_vault_only": (vault_usage > 0 and scope_usage == 0),
            "vault_count": vault_usage,
            "vault_dominant_type": dominant_type_str,
            "type_agreement": "matches" if dominant_type_str == prop.storage_type.value else ("differs" if dominant_type_str else "new"),
        })
        comparisons.append(item)

    return comparisons


def import_proposal(
    text: str,
    scoped_inv: Inventory | None = None,
    vault_inv: Inventory | None = None,
    glossary_store: Any | None = None,
    schema_library: Any | None = None,
) -> dict[str, Any]:
    """Full import and four-way comparison pipeline used by the API/UI."""
    try:
        data = parse_proposal_text(text)
    except ProposalError as exc:
        return {
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "schema": None,
            "comparison": [],
            "four_way_comparison": [],
            "vault_modified": False,
        }
    report = validate_proposal(data)
    schema_obj = report.pop("_schema_obj", None)
    
    four_way = (
        compare_proposal_four_way(
            schema=schema_obj,
            scoped_inv=scoped_inv,
            vault_inv=vault_inv,
            glossary_store=glossary_store,
            schema_library=schema_library,
        )
        if schema_obj is not None
        else []
    )
    report["comparison"] = four_way
    report["four_way_comparison"] = four_way
    return report
