"""Governance Profile Import/Export Engine (REQ-047, DEC-032).

Bundles Named Schema Library, Scope Governance assignments, and Personal Glossary
overrides into a single portable, verifiable JSON artifact with SHA-256 checksum.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.core.named_schemas import NAMED_SCHEMA_LIBRARY
from app.core.scope_governance import SCOPE_GOVERNANCE_STORE
from app.core.user_glossary import USER_GLOSSARY_STORE, UserGlossaryOverride

PROFILE_FORMAT_VERSION = "1.0"


def compute_profile_checksum(payload: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 checksum over canonical JSON bytes."""
    data_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data_bytes).hexdigest()


def export_governance_profile() -> dict[str, Any]:
    """Export all app-local governance entities into a signed profile package."""
    from datetime import datetime, timezone

    schemas = NAMED_SCHEMA_LIBRARY.list_schemas()
    scope_assignments = SCOPE_GOVERNANCE_STORE.list_assignments()
    glossary_overrides = USER_GLOSSARY_STORE.list_overrides()

    data_payload = {
        "format_version": PROFILE_FORMAT_VERSION,
        "named_schemas": schemas,
        "scope_assignments": scope_assignments,
        "user_glossary": glossary_overrides,
    }

    checksum = compute_profile_checksum(data_payload)

    return {
        "profile_metadata": {
            "format_version": PROFILE_FORMAT_VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "sha256_checksum": checksum,
            "schema_count": len(schemas),
            "assignment_count": len(scope_assignments),
            "glossary_count": len(glossary_overrides),
        },
        "data": data_payload,
    }


def validate_governance_profile(profile_data: dict[str, Any]) -> dict[str, Any]:
    """Validate a governance profile package and return structured preview before applying (REQ-047)."""
    if not isinstance(profile_data, dict):
        return {"valid": False, "error": "Profile data must be a JSON object."}

    data = profile_data.get("data")
    if not isinstance(data, dict):
        return {"valid": False, "error": "Invalid profile format: missing 'data' object."}

    fmt = data.get("format_version")
    if fmt != PROFILE_FORMAT_VERSION:
        return {"valid": False, "error": f"Unsupported profile format_version '{fmt}'. Supported: {PROFILE_FORMAT_VERSION}"}

    meta = profile_data.get("profile_metadata") or {}
    expected_hash = meta.get("sha256_checksum")
    if expected_hash:
        actual_hash = compute_profile_checksum(data)
        if expected_hash != actual_hash:
            return {"valid": False, "error": f"Profile checksum mismatch. Expected: {expected_hash}, got: {actual_hash}"}

    schemas = data.get("named_schemas") or []
    assignments = data.get("scope_assignments") or {}
    glossary = data.get("user_glossary") or {}
    saved_checks = data.get("saved_checks") or []

    schemas_preview = [
        {"id": s.get("id"), "name": s.get("name"), "version": s.get("version"), "property_count": len(s.get("properties", []))}
        for s in schemas if isinstance(s, dict)
    ]

    return {
        "valid": True,
        "format_version": fmt,
        "schema_count": len(schemas),
        "assignment_count": len(assignments),
        "glossary_count": len(glossary),
        "saved_checks_count": len(saved_checks),
        "schemas_preview": schemas_preview,
        "exported_at": meta.get("exported_at"),
    }


def import_governance_profile(profile_data: dict[str, Any], mode: str = "merge") -> dict[str, Any]:
    """Validate and import a governance profile package with real merge or replace behavior (REQ-047)."""
    val_report = validate_governance_profile(profile_data)
    if not val_report.get("valid"):
        raise ValueError(val_report.get("error", "Invalid profile."))

    data = profile_data["data"]
    schemas = data.get("named_schemas") or []
    assignments = data.get("scope_assignments") or {}
    glossary = data.get("user_glossary") or {}

    # If replace mode, clear existing app-local governance stores first
    if mode == "replace":
        NAMED_SCHEMA_LIBRARY.storage.save({})
        SCOPE_GOVERNANCE_STORE.storage.save({})
        USER_GLOSSARY_STORE.storage.save({})

    imported_schemas = 0
    imported_assignments = 0
    imported_glossary = 0

    # 1. Import schemas
    for s in schemas:
        if isinstance(s, dict) and s.get("id") and s.get("name"):
            NAMED_SCHEMA_LIBRARY.save_schema(s)
            imported_schemas += 1

    # 2. Import scope assignments
    for scope_key, asgn in assignments.items():
        if isinstance(asgn, dict) and asgn.get("schema_id"):
            SCOPE_GOVERNANCE_STORE.assign_schema(
                scope_key=scope_key,
                schema_id=asgn["schema_id"],
                schema_name=asgn.get("schema_name", ""),
            )
            imported_assignments += 1

    # 3. Import glossary overrides
    for key, ov in glossary.items():
        if isinstance(ov, dict) and ov.get("canonical_key"):
            USER_GLOSSARY_STORE.save_override(
                UserGlossaryOverride.from_dict(ov)
            )
            imported_glossary += 1

    return {
        "status": "imported",
        "mode": mode,
        "imported": {
            "schemas": imported_schemas,
            "scope_assignments": imported_assignments,
            "glossary_overrides": imported_glossary,
        },
    }
