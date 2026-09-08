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


def compute_concrete_changeset(profile_data: dict[str, Any], mode: str = "merge") -> dict[str, list[dict[str, Any]]]:
    """Compute deterministic, per-entity change-set plan for merge or replace mode (HA-F18)."""
    data = profile_data.get("data") or {}
    schemas = data.get("named_schemas") or []
    assignments = data.get("scope_assignments") or {}
    glossary = data.get("user_glossary") or {}
    saved_checks = data.get("saved_checks") or []
    prefs = data.get("governance_preferences") or {}

    # 1. Named Schemas
    # Authority: schema_id, or name + version
    current_schemas = NAMED_SCHEMA_LIBRARY.storage.load().get("data") or {}
    schema_entries: list[dict[str, Any]] = []
    seen_cur_schema_ids = set()

    for s in schemas:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        sname = s.get("name") or "Unnamed"
        sver = str(s.get("version") or "1.0")
        props = s.get("properties") or []
        desc = s.get("description") or ""

        target_cur = None
        if sid and sid in current_schemas:
            target_cur = current_schemas[sid]
            seen_cur_schema_ids.add(sid)
        else:
            for cid, cur in current_schemas.items():
                if cur.get("name") == sname and str(cur.get("version") or "1.0") == sver:
                    target_cur = cur
                    seen_cur_schema_ids.add(cid)
                    break

        disp = f"{sname} v{sver}"
        if not target_cur:
            schema_entries.append({
                "action": "add",
                "identity": sid or f"{sname}:{sver}",
                "display_name": disp,
                "before": None,
                "after": f"{len(props)} properties",
                "reason": "New schema to be created",
            })
        else:
            cur_props = target_cur.get("properties") or []
            cur_desc = target_cur.get("description") or ""
            if cur_props == props and cur_desc == desc:
                schema_entries.append({
                    "action": "unchanged",
                    "identity": sid or target_cur.get("id"),
                    "display_name": disp,
                    "before": f"{len(cur_props)} properties",
                    "after": f"{len(props)} properties",
                    "reason": "Identical schema content",
                })
            else:
                schema_entries.append({
                    "action": "update",
                    "identity": sid or target_cur.get("id"),
                    "display_name": disp,
                    "before": f"{len(cur_props)} properties",
                    "after": f"{len(props)} properties",
                    "reason": "Schema properties or description modified",
                })

    for cid, cur in current_schemas.items():
        if cid not in seen_cur_schema_ids:
            cname = cur.get("name") or "Unnamed"
            cver = str(cur.get("version") or "1.0")
            cprops = cur.get("properties") or []
            disp = f"{cname} v{cver}"
            if mode == "replace":
                schema_entries.append({
                    "action": "remove",
                    "identity": cid,
                    "display_name": disp,
                    "before": f"{len(cprops)} properties",
                    "after": None,
                    "reason": "Existing schema omitted from profile (replace mode)",
                })
            else:
                schema_entries.append({
                    "action": "retained",
                    "identity": cid,
                    "display_name": disp,
                    "before": f"{len(cprops)} properties",
                    "after": f"{len(cprops)} properties",
                    "reason": "Existing local schema retained (merge mode)",
                })

    schema_entries.sort(key=lambda x: (x["display_name"], x["action"]))

    # 2. Scope Assignments
    current_assignments = SCOPE_GOVERNANCE_STORE.storage.load().get("data") or {}
    scope_entries: list[dict[str, Any]] = []
    seen_cur_scopes = set()

    for k, v in assignments.items():
        sid = v.get("schema_id") if isinstance(v, dict) else str(v)
        sname = v.get("schema_name") if isinstance(v, dict) else ""
        after_disp = f"{sname} ({sid})" if sname else sid
        disp_key = "Entire Vault" if k == "entire_vault" else k

        if k not in current_assignments:
            scope_entries.append({
                "action": "add",
                "identity": k,
                "display_name": disp_key,
                "before": None,
                "after": after_disp,
                "reason": "New scope assignment",
            })
        else:
            seen_cur_scopes.add(k)
            cur_v = current_assignments[k]
            cur_sid = cur_v.get("schema_id") if isinstance(cur_v, dict) else str(cur_v)
            cur_sname = cur_v.get("schema_name") if isinstance(cur_v, dict) else ""
            before_disp = f"{cur_sname} ({cur_sid})" if cur_sname else cur_sid
            if cur_sid == sid:
                scope_entries.append({
                    "action": "unchanged",
                    "identity": k,
                    "display_name": disp_key,
                    "before": before_disp,
                    "after": after_disp,
                    "reason": "Identical scope assignment",
                })
            else:
                scope_entries.append({
                    "action": "update",
                    "identity": k,
                    "display_name": disp_key,
                    "before": before_disp,
                    "after": after_disp,
                    "reason": "Scope assignment target changed",
                })

    for k, v in current_assignments.items():
        if k not in seen_cur_scopes:
            cur_sid = v.get("schema_id") if isinstance(v, dict) else str(v)
            cur_sname = v.get("schema_name") if isinstance(v, dict) else ""
            disp_key = "Entire Vault" if k == "entire_vault" else k
            before_disp = f"{cur_sname} ({cur_sid})" if cur_sname else cur_sid
            if mode == "replace":
                scope_entries.append({
                    "action": "remove",
                    "identity": k,
                    "display_name": disp_key,
                    "before": before_disp,
                    "after": None,
                    "reason": "Existing assignment removed (replace mode)",
                })
            else:
                scope_entries.append({
                    "action": "retained",
                    "identity": k,
                    "display_name": disp_key,
                    "before": before_disp,
                    "after": before_disp,
                    "reason": "Existing assignment retained (merge mode)",
                })

    scope_entries.sort(key=lambda x: (x["display_name"], x["action"]))

    # 3. User Glossary
    current_glossary = USER_GLOSSARY_STORE.storage.load().get("data") or {}
    glossary_entries: list[dict[str, Any]] = []
    seen_cur_glossary = set()

    for k, v in glossary.items():
        ckey = v.get("canonical_key") if isinstance(v, dict) else k
        clabel = (v.get("label_zh") or v.get("label_en") or ckey) if isinstance(v, dict) else str(v)
        if ckey not in current_glossary:
            glossary_entries.append({
                "action": "add",
                "identity": ckey,
                "display_name": ckey,
                "before": None,
                "after": clabel,
                "reason": "New glossary override",
            })
        else:
            seen_cur_glossary.add(ckey)
            cur_raw = current_glossary[ckey]
            cur_label = (cur_raw.get("label_zh") or cur_raw.get("label_en") or ckey) if isinstance(cur_raw, dict) else str(cur_raw)
            if cur_raw == v:
                glossary_entries.append({
                    "action": "unchanged",
                    "identity": ckey,
                    "display_name": ckey,
                    "before": cur_label,
                    "after": clabel,
                    "reason": "Identical glossary override",
                })
            else:
                glossary_entries.append({
                    "action": "update",
                    "identity": ckey,
                    "display_name": ckey,
                    "before": cur_label,
                    "after": clabel,
                    "reason": "Glossary override content updated",
                })

    for k, v in current_glossary.items():
        if k not in seen_cur_glossary:
            cur_label = (v.get("label_zh") or v.get("label_en") or k) if isinstance(v, dict) else str(v)
            if mode == "replace":
                glossary_entries.append({
                    "action": "remove",
                    "identity": k,
                    "display_name": k,
                    "before": cur_label,
                    "after": None,
                    "reason": "User override removed (replace mode)",
                })
            else:
                glossary_entries.append({
                    "action": "retained",
                    "identity": k,
                    "display_name": k,
                    "before": cur_label,
                    "after": cur_label,
                    "reason": "User override retained (merge mode)",
                })

    glossary_entries.sort(key=lambda x: (x["display_name"], x["action"]))

    # 4. Saved Checks
    current_checks_storage = EntityStorage("saved_checks", "saved_checks/saved_relationship_checks.json")
    cur_checks_data = current_checks_storage.load().get("data") or []
    current_checks_map = {c.get("id"): c for c in cur_checks_data if isinstance(c, dict) and c.get("id")}
    check_entries: list[dict[str, Any]] = []
    seen_cur_checks = set()

    for c in saved_checks:
        cid = c.get("id") if isinstance(c, dict) else None
        cname = c.get("name") if isinstance(c, dict) else str(c)
        if not cid or cid not in current_checks_map:
            check_entries.append({
                "action": "add",
                "identity": cid or cname,
                "display_name": cname,
                "before": None,
                "after": cname,
                "reason": "New relationship check",
            })
        else:
            seen_cur_checks.add(cid)
            cur_c = current_checks_map[cid]
            cur_cname = cur_c.get("name") if isinstance(cur_c, dict) else str(cur_c)
            if cur_c == c:
                check_entries.append({
                    "action": "unchanged",
                    "identity": cid,
                    "display_name": cname,
                    "before": cur_cname,
                    "after": cname,
                    "reason": "Identical relationship check",
                })
            else:
                check_entries.append({
                    "action": "update",
                    "identity": cid,
                    "display_name": cname,
                    "before": cur_cname,
                    "after": cname,
                    "reason": "Relationship check query updated",
                })

    for cid, c in current_checks_map.items():
        if cid not in seen_cur_checks:
            cname = c.get("name") if isinstance(c, dict) else str(c)
            if mode == "replace":
                check_entries.append({
                    "action": "remove",
                    "identity": cid,
                    "display_name": cname,
                    "before": cname,
                    "after": None,
                    "reason": "Saved check removed (replace mode)",
                })
            else:
                check_entries.append({
                    "action": "retained",
                    "identity": cid,
                    "display_name": cname,
                    "before": cname,
                    "after": cname,
                    "reason": "Saved check retained (merge mode)",
                })

    check_entries.sort(key=lambda x: (x["display_name"], x["action"]))

    # 5. Governance Preferences (portable keys only: locale, theme; exclude internal _legacy_migrated, HA-F17)
    current_prefs = PREFERENCES_STORAGE.load().get("data") or {}
    pref_entries: list[dict[str, Any]] = []

    for pref_key in ("locale", "theme"):
        cur_val = current_prefs.get(pref_key)
        incoming_val = prefs.get(pref_key)

        if incoming_val is not None:
            if cur_val == incoming_val:
                pref_entries.append({
                    "action": "unchanged",
                    "identity": pref_key,
                    "display_name": pref_key,
                    "before": cur_val,
                    "after": incoming_val,
                    "reason": f"Preference {pref_key} unchanged",
                })
            elif cur_val is None:
                pref_entries.append({
                    "action": "add",
                    "identity": pref_key,
                    "display_name": pref_key,
                    "before": None,
                    "after": incoming_val,
                    "reason": f"Preference {pref_key} set",
                })
            else:
                pref_entries.append({
                    "action": "update",
                    "identity": pref_key,
                    "display_name": pref_key,
                    "before": cur_val,
                    "after": incoming_val,
                    "reason": f"Preference {pref_key} updated",
                })
        elif cur_val is not None:
            if mode == "replace":
                pref_entries.append({
                    "action": "remove",
                    "identity": pref_key,
                    "display_name": pref_key,
                    "before": cur_val,
                    "after": None,
                    "reason": f"Preference {pref_key} cleared in replace mode",
                })
            else:
                pref_entries.append({
                    "action": "retained",
                    "identity": pref_key,
                    "display_name": pref_key,
                    "before": cur_val,
                    "after": cur_val,
                    "reason": f"Preference {pref_key} retained",
                })

    return {
        "schemas": schema_entries,
        "scope_assignments": scope_entries,
        "glossary": glossary_entries,
        "saved_checks": check_entries,
        "preferences": pref_entries,
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

    # Pre-compute concrete plans for both merge and replace modes (HA-F18)
    plans = {
        "merge": compute_concrete_changeset(profile_data, mode="merge"),
        "replace": compute_concrete_changeset(profile_data, mode="replace"),
    }

    # Aggregate summaries for backward-compatible counts
    def build_summary(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        res = {"add": [], "update": [], "unchanged": [], "conflict": [], "remove": []}
        for e in entries:
            act = e.get("action")
            if act in res:
                res[act].append(e)
        return res

    merge_plan = plans["merge"]
    schemas_changeset = build_summary(merge_plan["schemas"])
    assignments_changeset = build_summary(merge_plan["scope_assignments"])
    glossary_changeset = build_summary(merge_plan["glossary"])
    checks_changeset = build_summary(merge_plan["saved_checks"])

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
            "scope_assignments": assignments_changeset,
            "glossary": glossary_changeset,
            "glossary_overrides": glossary_changeset,
            "checks": checks_changeset,
            "saved_checks": checks_changeset,
        },
        "plans": plans,
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
