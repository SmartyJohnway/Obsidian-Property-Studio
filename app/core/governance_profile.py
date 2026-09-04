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
from app.storage.local_storage import EntityStorage

PROFILE_FORMAT_VERSION = "1.0"
PREFERENCES_STORAGE = EntityStorage("governance_preferences", "config/preferences.json")


def compute_profile_checksum(payload: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 checksum over canonical JSON bytes."""
    data_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data_bytes).hexdigest()


def export_governance_profile(
    saved_checks_list: list[dict[str, Any]] | None = None,
    preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Export all app-local governance entities into a signed profile package."""
    from datetime import datetime, timezone

    schemas = NAMED_SCHEMA_LIBRARY.list_schemas()
    scope_assignments = SCOPE_GOVERNANCE_STORE.list_assignments()
    glossary_overrides = USER_GLOSSARY_STORE.list_overrides()
    checks = saved_checks_list or []
    
    stored_prefs = PREFERENCES_STORAGE.load().get("data") or {}
    raw_prefs = preferences or stored_prefs or {"locale": "zh-Hant", "theme": "system"}
    # Whitelist portable governance preferences only (exclude internal runtime state like _legacy_migrated)
    PORTABLE_PREF_KEYS = {"locale", "theme"}
    prefs = {k: v for k, v in raw_prefs.items() if k in PORTABLE_PREF_KEYS}
    if not prefs:
        prefs = {"locale": "zh-Hant", "theme": "system"}

    data_payload = {
        "format_version": PROFILE_FORMAT_VERSION,
        "named_schemas": schemas,
        "scope_assignments": scope_assignments,
        "user_glossary": glossary_overrides,
        "saved_checks": checks,
        "governance_preferences": prefs,
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
            "saved_checks_count": len(checks),
        },
        "data": data_payload,
    }


def validate_governance_profile(profile_data: dict[str, Any]) -> dict[str, Any]:
    """Validate a profile package structure and checksum before import (REQ-047)."""
    if not isinstance(profile_data, dict):
        return {"valid": False, "error": "Invalid profile format: must be a JSON object."}

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

    prefs = data.get("governance_preferences") or {}
    current_prefs = PREFERENCES_STORAGE.load().get("data") or {}
    preferences_preview = {
        "profile": prefs,
        "current": current_prefs,
        "has_changes": bool(prefs and (prefs.get("locale") != current_prefs.get("locale") or prefs.get("theme") != current_prefs.get("theme"))),
        "locale": {"from": current_prefs.get("locale"), "to": prefs.get("locale")} if prefs.get("locale") else None,
        "theme": {"from": current_prefs.get("theme"), "to": prefs.get("theme")} if prefs.get("theme") else None,
    }

    # Compute detailed changeset for all entities (HA-F18)
    # 1. Named Schemas
    current_schemas = NAMED_SCHEMA_LIBRARY.storage.load().get("data") or {}
    schemas_changeset = {"add": [], "update": [], "unchanged": [], "conflict": [], "remove": []}
    profile_schema_ids = set()
    for s in schemas:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        sname = s.get("name")
        sver = str(s.get("version") or "1.0")
        if sid:
            profile_schema_ids.add(sid)
        matching_id = current_schemas.get(sid) if sid else None
        matching_name_ver = None
        for cur in current_schemas.values():
            if cur.get("name") == sname and str(cur.get("version") or "1.0") == sver:
                matching_name_ver = cur
                break
        target = matching_id or matching_name_ver
        if not target:
            schemas_changeset["add"].append({"name": sname, "version": sver, "id": sid})
        else:
            is_same_props = (target.get("properties") == s.get("properties"))
            is_same_desc = (target.get("description") == s.get("description"))
            if is_same_props and is_same_desc:
                schemas_changeset["unchanged"].append({"name": sname, "version": sver, "id": sid})
            else:
                if matching_name_ver and matching_id and matching_name_ver.get("id") != matching_id.get("id"):
                    schemas_changeset["conflict"].append({"name": sname, "version": sver, "id": sid})
                else:
                    schemas_changeset["update"].append({"name": sname, "version": sver, "id": sid})
    for cid, cur in current_schemas.items():
        if cid not in profile_schema_ids:
            schemas_changeset["remove"].append({"name": cur.get("name"), "version": cur.get("version"), "id": cid})

    # 2. Scope Assignments
    current_assignments = SCOPE_GOVERNANCE_STORE.storage.load().get("data") or {}
    assignments_changeset = {"add": [], "update": [], "unchanged": [], "remove": []}
    for k, v in assignments.items():
        if k not in current_assignments:
            assignments_changeset["add"].append({"scope_key": k, "schema_id": v.get("schema_id")})
        elif current_assignments[k].get("schema_id") == v.get("schema_id"):
            assignments_changeset["unchanged"].append({"scope_key": k, "schema_id": v.get("schema_id")})
        else:
            assignments_changeset["update"].append({"scope_key": k, "from": current_assignments[k].get("schema_id"), "to": v.get("schema_id")})
    for k, v in current_assignments.items():
        if k not in assignments:
            assignments_changeset["remove"].append({"scope_key": k, "schema_id": v.get("schema_id")})

    # 3. User Glossary
    current_glossary = USER_GLOSSARY_STORE.storage.load().get("data") or {}
    glossary_changeset = {"add": [], "update": [], "unchanged": [], "remove": []}
    for k, v in glossary.items():
        ckey = v.get("canonical_key") or k
        if ckey not in current_glossary:
            glossary_changeset["add"].append({"canonical_key": ckey, "label": v.get("label_zh") or v.get("label_en") or ckey})
        elif current_glossary[ckey] == v:
            glossary_changeset["unchanged"].append({"canonical_key": ckey, "label": v.get("label_zh") or v.get("label_en") or ckey})
        else:
            glossary_changeset["update"].append({"canonical_key": ckey, "label": v.get("label_zh") or v.get("label_en") or ckey})
    for k, v in current_glossary.items():
        if k not in glossary:
            glossary_changeset["remove"].append({"canonical_key": k, "label": v.get("label_zh") or v.get("label_en") or k})

    # 4. Saved Checks
    current_checks_storage = EntityStorage("saved_checks", "saved_checks/saved_relationship_checks.json")
    cur_checks_data = current_checks_storage.load().get("data") or []
    current_checks_map = {c.get("id"): c for c in cur_checks_data if isinstance(c, dict) and c.get("id")}
    checks_changeset = {"add": [], "update": [], "unchanged": [], "remove": []}
    for c in saved_checks:
        cid = c.get("id")
        if cid not in current_checks_map:
            checks_changeset["add"].append({"id": cid, "name": c.get("name")})
        elif current_checks_map[cid] == c:
            checks_changeset["unchanged"].append({"id": cid, "name": c.get("name")})
        else:
            checks_changeset["update"].append({"id": cid, "name": c.get("name")})
    for cid, c in current_checks_map.items():
        if not any(sc.get("id") == cid for sc in saved_checks):
            checks_changeset["remove"].append({"id": cid, "name": c.get("name")})

    return {
        "valid": True,
        "format_version": fmt,
        "schema_count": len(schemas),
        "assignment_count": len(assignments),
        "glossary_count": len(glossary),
        "saved_checks_count": len(saved_checks),
        "schemas_preview": schemas_preview,
        "preferences_preview": preferences_preview,
        "changeset": {
            "schemas": schemas_changeset,
            "assignments": assignments_changeset,
            "glossary": glossary_changeset,
            "checks": checks_changeset,
        },
        "exported_at": meta.get("exported_at"),
    }


def import_governance_profile(
    profile_data: dict[str, Any],
    mode: str = "merge",
    saved_checks_store: Any | None = None,
) -> dict[str, Any]:
    """Validate and import a governance profile package with transactional safety (REQ-047)."""
    if mode not in ("merge", "replace"):
        raise ValueError(f"Invalid import mode '{mode}'. Supported modes are 'merge' and 'replace'.")

    val_report = validate_governance_profile(profile_data)
    if not val_report.get("valid"):
        raise ValueError(val_report.get("error", "Invalid profile."))

    data = profile_data["data"]
    schemas = data.get("named_schemas") or []
    assignments = data.get("scope_assignments") or {}
    glossary = data.get("user_glossary") or {}
    checks = data.get("saved_checks") or []
    prefs = data.get("governance_preferences")

    # Phase 1: Semantic Pre-validation (fail-closed before any mutation)
    for index, s in enumerate(schemas):
        if not isinstance(s, dict) or not s.get("name"):
            raise ValueError(f"Invalid schema at index {index}: must be object with 'name'.")
    for key, asgn in assignments.items():
        if not isinstance(asgn, dict) or not asgn.get("schema_id"):
            raise ValueError(f"Invalid scope assignment for '{key}': missing 'schema_id'.")
    for key, ov in glossary.items():
        if not isinstance(ov, dict) or not (ov.get("canonical_key") or key):
            raise ValueError(f"Invalid glossary override for '{key}': missing 'canonical_key'.")

    # Phase 2: Snapshot current state for rollback protection if in replace mode
    old_schemas = None
    old_assignments = None
    old_glossary = None
    old_checks = None
    old_preferences = None
    if mode == "replace":
        old_schemas = NAMED_SCHEMA_LIBRARY.storage.load().get("data", {})
        old_assignments = SCOPE_GOVERNANCE_STORE.storage.load().get("data", {})
        old_glossary = USER_GLOSSARY_STORE.storage.load().get("data", {})
        old_preferences = PREFERENCES_STORAGE.load().get("data", {})
        if saved_checks_store and hasattr(saved_checks_store, "list_checks"):
            old_checks = [c.to_dict() for c in saved_checks_store.list_checks()]

    imported_schemas = 0
    imported_assignments = 0
    imported_glossary = 0
    imported_checks = 0

    try:
        # Destructive clear occurs strictly within protected transaction boundary
        if mode == "replace":
            NAMED_SCHEMA_LIBRARY.storage.save({})
            SCOPE_GOVERNANCE_STORE.storage.save({})
            USER_GLOSSARY_STORE.storage.save({})
            PREFERENCES_STORAGE.save({})
            if saved_checks_store and hasattr(saved_checks_store, "clear"):
                saved_checks_store.clear()

        # 1. Import schemas
        for s in schemas:
            if isinstance(s, dict) and s.get("name"):
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
            if isinstance(ov, dict):
                ov_dict = dict(ov)
                if "canonical_key" not in ov_dict:
                    ov_dict["canonical_key"] = key
                USER_GLOSSARY_STORE.save_override(
                    UserGlossaryOverride.from_dict(ov_dict)
                )
                imported_glossary += 1

        # 4. Import saved relationship checks if store available
        if saved_checks_store and hasattr(saved_checks_store, "save_check"):
            from app.core.saved_checks import SavedCheck
            for c in checks:
                if isinstance(c, dict) and c.get("name"):
                    chk = SavedCheck.from_dict(c)
                    saved_checks_store.save_check(chk)
                    imported_checks += 1

        # 5. Import preferences if present (whitelist portable keys only, HA-F17)
        if isinstance(prefs, dict):
            current_p = dict(PREFERENCES_STORAGE.load().get("data") or {})
            for k in ("locale", "theme"):
                if k in prefs and prefs[k]:
                    current_p[k] = prefs[k]
            PREFERENCES_STORAGE.save(current_p)

    except Exception as exc:
        # True Transactional Rollback in replace mode if mutation failed mid-way
        if mode == "replace" and old_schemas is not None:
            NAMED_SCHEMA_LIBRARY.storage.save(old_schemas)
            SCOPE_GOVERNANCE_STORE.storage.save(old_assignments)
            USER_GLOSSARY_STORE.storage.save(old_glossary)
            if old_preferences is not None:
                PREFERENCES_STORAGE.save(old_preferences)
            if saved_checks_store and old_checks is not None:
                if hasattr(saved_checks_store, "clear"):
                    saved_checks_store.clear()
                from app.core.saved_checks import SavedCheck
                for c in old_checks:
                    saved_checks_store.save_check(SavedCheck.from_dict(c))
        raise ValueError(f"Import aborted and rolled back due to error: {exc}") from exc

    return {
        "status": "imported",
        "mode": mode,
        "imported": {
            "schemas": imported_schemas,
            "scope_assignments": imported_assignments,
            "glossary_overrides": imported_glossary,
            "user_glossary": imported_glossary,
            "saved_checks": imported_checks,
            "preferences": bool(prefs),
        },
    }
