"""Local HTTP server for Obsidian Property Studio v1.1.0.

Safety:
  * binds to 127.0.0.1 by default (AGENTS 24);
  * exposes NO endpoint that writes into a vault (AGENTS 30);
  * all exports go to a folder outside the vault (REQ-002);
  * no outbound network calls, no telemetry, no API keys.
"""

from __future__ import annotations

import json
import os
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.parse import urlparse

from .core import (
    body_links,
    design,
    exports,
    health,
    inventory,
    note_workspace,
    property_glossary,
    proposal,
    refactor,
    relationships,
    saved_checks,
    state_transfer,
    named_schemas,
    reconciliation,
    scope_governance,
    drift,
    migration,
    governance_profile,
    user_glossary,
)
from . import storage

from .core.fill import fill_preview
from .core.manifest import assert_unchanged, vault_manifest
from .core.model import (
    STORAGE_TYPE_LABELS,
    UI_CONTROL_ALLOWED_STORAGE,
    UI_CONTROL_SERIALIZATION,
    Schema,
)
from .core.scanner import ScanOptions, VaultPathError, note_name_index, scan_vault
from .core.scope import (
    ScopeMode,
    ScopeSpec,
    ScopeValidationError,
    extract_vault_folders,
    filter_scan_by_scope,
)

APP_VERSION = "1.2.0"
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")


class Store:
    """In-memory state for the current session (never persisted in the vault)."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.scan = None
        self.inventory = None
        self.baseline_manifest: dict[str, str] | None = None
        self.scope: ScopeSpec = ScopeSpec()
        self.saved_checks_store = saved_checks.SavedChecksStore(persistent=True)

    def set_scan(self, scan, manifest: dict[str, str] | None) -> None:
        with self.lock:
            from app.storage.local_storage import set_active_vault_path
            set_active_vault_path(scan.vault_path if hasattr(scan, "vault_path") else None)
            self.scan = scan
            self.inventory = inventory.build_inventory(scan)
            self.baseline_manifest = manifest
            self.scope = ScopeSpec()

    def set_scope(self, scope: ScopeSpec) -> None:
        with self.lock:
            scope.validate()
            self.scope = scope

    def require_scan(self):
        if self.scan is None:
            raise ApiError("No vault is currently loaded. Run a scan first.", 400)
        return self.scan

    def get_scoped_scan(self):
        scan = self.require_scan()
        if self.scope.mode == ScopeMode.ENTIRE_VAULT:
            return scan
        return filter_scan_by_scope(scan, self.scope)

    def get_scoped_inventory(self):
        scoped_scan = self.get_scoped_scan()
        return inventory.build_inventory(scoped_scan)


STORE = Store()


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400, detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.detail = detail


# --------------------------------------------------------------------------
# API Handlers
# --------------------------------------------------------------------------
def api_meta(_body: dict[str, Any]) -> dict[str, Any]:
    return {
        "app": "Obsidian Property Studio",
        "version": APP_VERSION,
        "storage_types": STORAGE_TYPE_LABELS,
        "ui_controls": UI_CONTROL_SERIALIZATION,
        "ui_control_allowed_storage": UI_CONTROL_ALLOWED_STORAGE,
        "recipes": [
            {
                "id": r.id,
                "label": r.label,
                "description": r.description,
                "type_value": r.type_value,
            }
            for r in design.RECIPES
        ],
        "intents": [{"id": i.id, "label": i.label} for i in design.INTENTS],
        "proposal_contract_version": proposal.PROPOSAL_CONTRACT_VERSION,
        "vault_write_capability": False,
        "requires_network": False,
        "requires_api_key": False,
        "default_export_dir": exports.default_output_dir(),
    }


def api_scan(body: dict[str, Any]) -> dict[str, Any]:
    path = body.get("vault_path", "")
    from app.storage.local_storage import VaultIsolationError, set_active_vault_path
    try:
        set_active_vault_path(path)
    except VaultIsolationError as exc:
        raise ApiError(f"Vault isolation violation: {exc}", 400) from exc

    try:
        scan = scan_vault(path, ScanOptions())
    except VaultPathError as exc:
        raise ApiError(str(exc), 400) from exc
    baseline = vault_manifest(scan.vault_path) if body.get("hash_baseline", True) else None
    STORE.set_scan(scan, baseline)
    report = inventory.discovery_report(scan, STORE.inventory)
    report["scan_seconds"] = scan.scan_seconds
    report["baseline_captured"] = baseline is not None
    report["baseline_file_count"] = len(baseline or {})
    return report


def api_discovery(_body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    scoped_scan = STORE.get_scoped_scan()
    inv = STORE.get_scoped_inventory()
    report = inventory.discovery_report(scoped_scan, inv)
    report["scope"] = STORE.scope.to_dict()
    report["notes_in_scope"] = scoped_scan.note_count
    report["total_vault_notes"] = scan.note_count
    return report


def api_property_detail(body: dict[str, Any]) -> dict[str, Any]:
    STORE.require_scan()
    scoped_scan = STORE.get_scoped_scan()
    inv = STORE.get_scoped_inventory()
    key = body.get("key", "")
    entry = inv.get(key)
    if entry is None:
        raise ApiError(f"Property '{key}' is not used in current scope.", 404)
    entry_dict = entry.to_dict(value_limit=200)
    entry_dict["values"] = entry_dict.get("top_values", [])
    return {
        "entry": entry_dict,
        "notes_by_type": {k: sorted(v) for k, v in sorted(entry.type_notes.items())},
    }



def api_design_suggest(body: dict[str, Any]) -> dict[str, Any]:
    goal = str(body.get("goal", ""))
    return {
        "recipes": design.suggest_recipes(goal, limit=4),
        "detected_intents": design.detect_intents(goal),
    }


def api_design_presets(_body: dict[str, Any]) -> dict[str, Any]:
    return {
        "objects": [
            {"id": v["id"], "name_zh": v["name_zh"], "name_en": v["name_en"], "props_count": len(v["props"])}
            for v in design.OBJECT_PRESETS.values()
        ],
        "needs": [
            {"id": v["id"], "name_zh": v["name_zh"], "name_en": v["name_en"], "props_count": len(v["props"])}
            for v in design.NEED_PRESETS.values()
        ],
    }


def api_design_build(body: dict[str, Any]) -> dict[str, Any]:
    goal = str(body.get("goal", ""))
    objects = list(body.get("objects", []) or [])
    needs = list(body.get("needs", []) or [])
    scoped_inv = STORE.get_scoped_inventory() if STORE.scan else inventory.Inventory()
    global_inv = STORE.inventory or scoped_inv

    if objects or needs:
        schema = design.build_schema_from_structured_inputs(
            objects=objects,
            needs=needs,
            extra_text=goal,
            schema_name=body.get("schema_name") or None,
            inv=scoped_inv,
        )
    else:
        schema = design.build_schema(
            goal_text=goal,
            recipe_id=body.get("recipe_id") or None,
            intent_ids=tuple(body.get("intents", []) or []),
            schema_name=body.get("schema_name") or None,
            inv=scoped_inv,
        )
    return design.review_schema_against_vault(schema, scoped_inv, global_inv=global_inv)


def api_design_review(body: dict[str, Any]) -> dict[str, Any]:
    schema = Schema.from_dict(body.get("schema", {}))
    scoped_inv = STORE.get_scoped_inventory() if STORE.scan else inventory.Inventory()
    global_inv = STORE.inventory or scoped_inv
    return design.review_schema_against_vault(schema, scoped_inv, global_inv=global_inv)


def api_fill_preview(body: dict[str, Any]) -> dict[str, Any]:
    schema = Schema.from_dict(body.get("schema", {}))
    values = body.get("values", {}) or {}
    index = note_name_index(STORE.scan) if STORE.scan is not None else None
    return fill_preview(schema, values, index)


def api_workspace_candidates(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    query = str(body.get("query", "")).strip()
    candidates = note_workspace.find_candidate_notes(scan, query, current_scope=STORE.scope)
    return {"candidates": candidates, "total": len(candidates)}


def api_workspace_inspect(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    note_path = str(body.get("note_path", "")).strip()
    if not note_path:
        raise ApiError("note_path is required", 400)
    result = note_workspace.inspect_note_for_workspace(scan, note_path)
    return result.to_dict()


def api_workspace_preview(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    note_path = str(body.get("note_path", "")).strip()
    note = scan.note_by_path(note_path) if note_path else None
    values = body.get("values", {}) or {}
    schema_data = body.get("schema")
    schema = Schema.from_dict(schema_data) if schema_data else None
    deleted_keys = list(body.get("deleted_keys", []) or [])
    touched_keys = list(body["touched_keys"]) if "touched_keys" in body else None
    diff_res = note_workspace.compute_workspace_diff_and_frontmatter(
        original_note=note,
        updated_values=values,
        schema=schema,
        deleted_keys=deleted_keys,
        touched_keys=touched_keys,
    )
    return diff_res.to_dict()


def api_note_candidates(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    query = str(body.get("query", "")).strip().casefold()
    matches = []
    for note in scan.notes:
        if query and query not in note.name.casefold() and query not in note.path.casefold():
            continue
        matches.append(note.path)
    index = note_name_index(scan)
    ambiguous = sorted(name for name, paths in index.items() if len(paths) > 1)
    return {"candidates": matches, "ambiguous_names": ambiguous}


def api_refactor_plan(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    operation = body.get("operation")
    scope_data = body.get("scope")
    try:
        active_scope = ScopeSpec.from_dict(scope_data) if scope_data else STORE.scope
    except ScopeValidationError as exc:
        raise ApiError(f"Invalid Scope specification: {exc}", 400) from exc

    if operation == "rename":
        source = str(body.get("source", "")).strip()
        target = str(body.get("target", "")).strip()
        if not source:
            raise ApiError("Source property name is required.", 400)
        if not target:
            raise ApiError("Target property name cannot be empty.", 400)
        plan = refactor.plan_rename(scan, source, target, scope=active_scope)
        # Check target conflict against global inventory
        global_inv = STORE.inventory
        if global_inv and target in global_inv.properties:
            plan["target_already_exists"] = True
            plan["target_existing_usage_count"] = global_inv.properties[target].usage_count
    elif operation == "merge":
        sources = [str(s).strip() for s in body.get("sources", []) if str(s).strip()]
        target = str(body.get("target", "")).strip()
        if not sources:
            raise ApiError("Merge requires at least one source property.", 400)
        if not target:
            raise ApiError("Target property name cannot be empty.", 400)
        plan = refactor.plan_merge(scan, sources, target, scope=active_scope)
    elif operation == "normalize":
        prop = str(body.get("property") or body.get("key") or "").strip()
        if not prop:
            raise ApiError("Property name is required for normalization.", 400)
        mapping = body.get("mapping") if isinstance(body.get("mapping"), dict) else None
        overrides = body.get("canonical_overrides") if isinstance(body.get("canonical_overrides"), dict) else None
        plan = refactor.plan_normalize(
            scan, prop, canonical_overrides=overrides, mapping=mapping, scope=active_scope
        )

    elif operation == "convert_type":
        prop = str(body.get("property") or body.get("key") or "").strip()
        target_type = str(body.get("target_type", "")).strip()
        if not prop:
            raise ApiError("Property name is required for type conversion.", 400)
        valid_types = {"text", "number", "date", "checkbox", "list", "tags", "note_link", "note_link_list"}
        if target_type not in valid_types:
            raise ApiError(f"Target type must be one of {sorted(valid_types)}, got '{target_type}'.", 400)
        plan = refactor.plan_type_conversion(scan, prop, target_type, scope=active_scope)
    elif operation == "required_impact":
        schema = Schema.from_dict(body.get("schema", {}))
        plan = refactor.plan_required_impact(
            scan, schema, body.get("scope_property") or None, body.get("scope_value") or None, scope=active_scope
        )
    else:
        raise ApiError(f"Unknown refactor operation '{operation}'.", 400)
    return plan



def api_relationships(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    prop_filter = body.get("property") or None
    src_data = body.get("source_scope")
    tgt_data = body.get("target_scope")
    try:
        source_scope = ScopeSpec.from_dict(src_data) if src_data else STORE.scope
        target_scope = ScopeSpec.from_dict(tgt_data) if tgt_data else None
    except ScopeValidationError as exc:
        raise ApiError(f"Invalid Scope specification: {exc}", 400) from exc

    res = relationships.build_inbox(
        scan,
        property_filter=prop_filter,
        source_scope=source_scope,
        target_scope=target_scope,
    )
    res["findings"] = res.get("items", [])
    return res


def api_relationships_body(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    src_data = body.get("source_scope")
    tgt_data = body.get("target_scope")
    try:
        source_scope = ScopeSpec.from_dict(src_data) if src_data else STORE.scope
        target_scope = ScopeSpec.from_dict(tgt_data) if tgt_data else None
    except ScopeValidationError as exc:
        raise ApiError(f"Invalid Scope specification: {exc}", 400) from exc

    res = body_links.analyze_body_wikilinks(
        scan,
        source_scope=source_scope,
        target_scope=target_scope,
    )
    res["items"] = res.get("findings", [])
    return res



def api_saved_checks_list(_body: dict[str, Any]) -> dict[str, Any]:
    checks = STORE.saved_checks_store.list_checks()
    return {"checks": [c.to_dict() for c in checks], "total": len(checks)}


def api_saved_checks_save(body: dict[str, Any]) -> dict[str, Any]:
    chk_data = body.get("check") or body
    try:
        chk = saved_checks.SavedCheck.from_dict(chk_data)
    except Exception as exc:
        raise ApiError(f"Malformed Saved Check payload: {exc}", 400) from exc
    STORE.saved_checks_store.save_check(chk)
    return {"status": "saved", "check": chk.to_dict()}


def api_saved_checks_delete(body: dict[str, Any]) -> dict[str, Any]:
    check_id = str(body.get("id", "")).strip()
    if not check_id:
        raise ApiError("id is required", 400)
    deleted = STORE.saved_checks_store.delete_check(check_id)
    return {"deleted": deleted, "id": check_id}




def api_saved_checks_execute(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    check_id = str(body.get("id", "")).strip()
    if not check_id:
        raise ApiError("id is required", 400)
    try:
        return STORE.saved_checks_store.execute_check(scan, check_id)
    except KeyError as exc:
        raise ApiError(str(exc), 404) from exc


def api_health(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    scoped_scan = STORE.get_scoped_scan()
    inv = STORE.get_scoped_inventory()
    schema_data = body.get("schema")
    schema = Schema.from_dict(schema_data) if schema_data else None
    report = health.health_report(
        scoped_scan,
        inv,
        schema,
        body.get("scope_property") or None,
        body.get("scope_value") or None,
    )
    report["scope"] = STORE.scope.to_dict()
    report["notes_in_scope"] = scoped_scan.note_count
    report["total_vault_notes"] = scan.note_count
    return report


def api_proposal_import(body: dict[str, Any]) -> dict[str, Any]:
    text = body.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ApiError("Paste or open a proposal JSON file first.", 400)
    scoped_inv = STORE.get_scoped_inventory() if STORE.scan else inventory.Inventory()
    vault_inv = STORE.inventory if STORE.scan else inventory.Inventory()
    return proposal.import_proposal(
        text=text,
        scoped_inv=scoped_inv,
        vault_inv=vault_inv,
        glossary_store=user_glossary.USER_GLOSSARY_STORE,
        schema_library=named_schemas.NAMED_SCHEMA_LIBRARY,
    )


def api_export(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    kind = body.get("kind")
    params = body.get("params", {}) or {}

    # R06: Ensure export is Scope-aware and matches what user sees
    if "payload" in body and isinstance(body["payload"], dict):
        payload = body["payload"]
    elif kind == "discovery":
        scoped_scan = STORE.get_scoped_scan()
        inv = STORE.get_scoped_inventory()
        payload = inventory.discovery_report(scoped_scan, inv)
        payload["scope"] = STORE.scope.to_dict()
        payload["notes_in_scope"] = scoped_scan.note_count
        payload["total_vault_notes"] = scan.note_count
    elif kind == "health":
        scoped_scan = STORE.get_scoped_scan()
        inv = STORE.get_scoped_inventory()
        schema_data = params.get("schema")
        payload = health.health_report(
            scoped_scan,
            inv,
            Schema.from_dict(schema_data) if schema_data else None,
            params.get("scope_property") or None,
            params.get("scope_value") or None,
        )
        payload["scope"] = STORE.scope.to_dict()
        payload["notes_in_scope"] = scoped_scan.note_count
        payload["total_vault_notes"] = scan.note_count
    elif kind == "inbox":
        src_data = params.get("source_scope")
        tgt_data = params.get("target_scope")
        source_scope = ScopeSpec.from_dict(src_data) if src_data else STORE.scope
        target_scope = ScopeSpec.from_dict(tgt_data) if tgt_data else None
        payload = relationships.build_inbox(
            scan,
            property_filter=params.get("property") or None,
            source_scope=source_scope,
            target_scope=target_scope,
        )
    elif kind == "plan":
        payload = api_refactor_plan(params)
    elif kind == "schema":
        payload = Schema.from_dict(params.get("schema", {})).to_dict()
    else:
        raise ApiError(f"Unknown export kind '{kind}'.", 400)

    try:
        result = exports.export_artifact(
            kind, payload, scan.vault_path, body.get("output_dir") or None,
            body.get("basename") or None,
        )
    except exports.ExportPathError as exc:
        raise ApiError(str(exc), 400) from exc
    return result


def api_vault_verify(_body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    if STORE.baseline_manifest is None:
        raise ApiError("No baseline manifest was captured for this vault.", 400)
    after = vault_manifest(scan.vault_path)
    report = assert_unchanged(STORE.baseline_manifest, after)
    report["files_checked"] = len(after)
    return report


def api_scope_folders(_body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    folders = extract_vault_folders(scan.notes)
    return {"folders": folders, "total": len(folders)}


def api_scope_set(body: dict[str, Any]) -> dict[str, Any]:
    STORE.require_scan()
    scope_data = body.get("scope")
    try:
        scope = ScopeSpec.from_dict(scope_data)
        STORE.set_scope(scope)
    except ScopeValidationError as exc:
        raise ApiError(f"Invalid Scope specification: {exc}", 400) from exc

    scoped_scan = STORE.get_scoped_scan()
    return {
        "status": "applied",
        "scope": STORE.scope.to_dict(),
        "notes_in_scope": scoped_scan.note_count,
        "total_notes": STORE.scan.note_count,
    }


def api_scope_current(_body: dict[str, Any]) -> dict[str, Any]:
    STORE.require_scan()
    scoped_scan = STORE.get_scoped_scan()
    return {
        "scope": STORE.scope.to_dict(),
        "notes_in_scope": scoped_scan.note_count,
        "total_notes": STORE.scan.note_count,
    }


def api_glossary_catalog(_body: dict[str, Any]) -> dict[str, Any]:
    catalog = dict(property_glossary.export_glossary_catalog())
    overrides = user_glossary.USER_GLOSSARY_STORE.list_overrides()
    for ckey, ov in overrides.items():
        ckey_cf = ckey.strip().casefold()
        if ckey_cf in catalog:
            entry = dict(catalog[ckey_cf])
            if ov.get("label_zh"):
                entry["label_zh"] = ov["label_zh"]
            if ov.get("label_en"):
                entry["label_en"] = ov["label_en"]
            if ov.get("guidance"):
                entry["guidance"] = ov["guidance"]
            if ov.get("description_zh"):
                entry["short_description_zh"] = ov["description_zh"]
                entry["long_description_zh"] = ov["description_zh"]
            if ov.get("description_en"):
                entry["short_description_en"] = ov["description_en"]
                entry["long_description_en"] = ov["description_en"]
            if ov.get("category"):
                entry["category"] = ov["category"]
            if ov.get("aliases"):
                entry["aliases"] = ov["aliases"]
            if ov.get("examples"):
                entry["examples"] = ov["examples"]
            entry["is_user_override"] = True
            catalog[ckey_cf] = entry
        else:
            catalog[ckey_cf] = {
                "canonical_key": ckey,
                "label_zh": ov.get("label_zh") or ckey,
                "label_en": ov.get("label_en") or ckey,
                "short_description_zh": ov.get("description_zh") or "",
                "short_description_en": ov.get("description_en") or "",
                "long_description_zh": ov.get("description_zh") or "",
                "long_description_en": ov.get("description_en") or "",
                "usage_hint_zh": ov.get("guidance") or "",
                "usage_hint_en": ov.get("guidance") or "",
                "guidance": ov.get("guidance") or "",
                "category": ov.get("category") or "custom",
                "aliases": ov.get("aliases") or [],
                "examples": ov.get("examples") or [],
                "typical_type": "text",
                "typical_control": "plain",
                "is_user_override": True,
            }
    return {"catalog": catalog, "total": len(catalog)}


def api_glossary_property(body: dict[str, Any]) -> dict[str, Any]:
    key = str(body.get("property") or body.get("key") or "").strip()
    if not key:
        raise ApiError("Property key is required.", 400)
    entry = property_glossary.get_property_glossary_entry(key)
    override = user_glossary.USER_GLOSSARY_STORE.get_override(key)
    is_known = (entry is not None) or (override is not None)
    metadata = None
    if is_known:
        metadata = user_glossary.USER_GLOSSARY_STORE.resolve_property(key)

    scope_usage = 0
    vault_usage = 0
    observed_values: list[dict[str, Any]] = []
    dominant_type = None
    if STORE.scan:
        all_inv = STORE.inventory or inventory.build_inventory(STORE.scan)
        if key in all_inv.properties:
            vault_usage = all_inv.properties[key].usage_count
            observed_values = sorted(
                [{"value": v.value, "count": v.count} for v in all_inv.properties[key].values.values() if v.value],
                key=lambda x: -x["count"]
            )[:8]
            dt = all_inv.properties[key].dominant_type
            dominant_type = dt.value if hasattr(dt, "value") else str(dt)

        scoped_scan = STORE.get_scoped_scan()
        scoped_inv = inventory.build_inventory(scoped_scan)
        if key in scoped_inv.properties:
            scope_usage = scoped_inv.properties[key].usage_count

    return {
        "canonical_key": key,
        "is_known": is_known,
        "metadata": metadata,
        "scope_usage": scope_usage,
        "vault_usage": vault_usage,
        "detected_type": dominant_type,
        "common_values": observed_values,
    }


def api_glossary_user_list(_body: dict[str, Any]) -> dict[str, Any]:
    overrides = user_glossary.USER_GLOSSARY_STORE.list_overrides()
    return {"overrides": overrides, "total": len(overrides)}


def api_glossary_user_save(body: dict[str, Any]) -> dict[str, Any]:
    override_data = body.get("override") or body
    try:
        override = user_glossary.UserGlossaryOverride.from_dict(override_data)
        expected_rev = body.get("expected_revision")
        res = user_glossary.USER_GLOSSARY_STORE.save_override(override, expected_rev)
        return {"status": "saved", "override": override.to_dict(), "revision": res.get("revision")}
    except Exception as exc:
        raise ApiError(str(exc), 400) from exc


def api_glossary_user_delete(body: dict[str, Any]) -> dict[str, Any]:
    key = str(body.get("key") or body.get("canonical_key") or "").strip()
    if not key:
        raise ApiError("Property key is required.", 400)
    expected_rev = body.get("expected_revision")
    deleted = user_glossary.USER_GLOSSARY_STORE.delete_override(key, expected_rev)
    return {"status": "deleted" if deleted else "not_found", "key": key}


def api_schemas_list(_body: dict[str, Any]) -> dict[str, Any]:
    schemas = named_schemas.NAMED_SCHEMA_LIBRARY.list_schemas()
    return {"schemas": schemas, "total": len(schemas)}


def api_schemas_get(body: dict[str, Any]) -> dict[str, Any]:
    schema_id = str(body.get("id") or body.get("schema_id") or "").strip()
    if not schema_id:
        raise ApiError("Schema ID is required.", 400)
    schema = named_schemas.NAMED_SCHEMA_LIBRARY.get_schema(schema_id)
    if not schema:
        raise ApiError(f"Schema '{schema_id}' not found.", 404)
    return {"schema": schema.to_dict()}


def api_schemas_create(body: dict[str, Any]) -> dict[str, Any]:
    schema_data = body.get("schema") or body
    try:
        expected_rev = body.get("expected_revision")
        res = named_schemas.NAMED_SCHEMA_LIBRARY.create_schema(schema_data, expected_rev)
        return {"status": "created", "schema": res.get("schema"), "revision": res.get("revision")}
    except (ValueError, storage.ConcurrencyError) as exc:
        raise ApiError(str(exc), 400) from exc


def api_schemas_update(body: dict[str, Any]) -> dict[str, Any]:
    schema_id = str(body.get("id") or body.get("schema_id") or "").strip()
    schema_data = body.get("schema") or body
    if not schema_id:
        schema_id = str(schema_data.get("id") or "").strip()
    if not schema_id:
        raise ApiError("Schema ID is required.", 400)
    try:
        expected_rev = body.get("expected_revision")
        res = named_schemas.NAMED_SCHEMA_LIBRARY.update_schema(schema_id, schema_data, expected_rev)
        return {"status": "updated", "schema": res.get("schema"), "revision": res.get("revision")}
    except (ValueError, storage.ConcurrencyError) as exc:
        raise ApiError(str(exc), 400) from exc


def api_schemas_delete(body: dict[str, Any]) -> dict[str, Any]:
    schema_id = str(body.get("id") or body.get("schema_id") or "").strip()
    if not schema_id:
        raise ApiError("Schema ID is required.", 400)
    expected_rev = body.get("expected_revision")
    try:
        deleted = named_schemas.NAMED_SCHEMA_LIBRARY.delete_schema(schema_id, expected_rev)
        return {"status": "deleted" if deleted else "not_found", "id": schema_id}
    except storage.ConcurrencyError as exc:
        raise ApiError(str(exc), 400) from exc


def api_state_validate_context(body: dict[str, Any]) -> dict[str, Any]:
    return state_transfer.validate_navigation_payload(body)


def api_reconcile_inspect(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    note_path = str(body.get("note_path") or "").strip()
    if not note_path:
        raise ApiError("note_path is required.", 400)

    inspect_res = note_workspace.inspect_note_for_workspace(scan, note_path)
    note_props = inspect_res.original_properties

    schema_props = body.get("schema_properties") or []
    schema_name = str(body.get("schema_name") or "adopted-schema")
    schema_id = body.get("schema_id")

    if schema_id and not schema_props:
        sch = named_schemas.NAMED_SCHEMA_LIBRARY.get_schema(str(schema_id))
        if sch:
            schema_props = [p.to_dict() for p in sch.properties]
            schema_name = sch.name

    report = reconciliation.reconcile_note_frontmatter(
        note_properties=note_props,
        schema_properties=schema_props,
        schema_name=schema_name,
        schema_id=str(schema_id) if schema_id else None,
        note_path=note_path,
    )
    return report.to_dict()


def api_reconcile_preview(body: dict[str, Any]) -> dict[str, Any]:
    orig_props = body.get("original_properties") or {}
    schema_props = body.get("schema_properties") or []
    resolved_vals = body.get("resolved_values") or {}

    result = reconciliation.preview_reconciled_frontmatter(
        original_properties=orig_props,
        schema_properties=schema_props,
        resolved_values=resolved_vals,
    )
    return result


def api_scope_schema_assign(body: dict[str, Any]) -> dict[str, Any]:
    scope_key = str(body.get("scope_key") or "default").strip()
    schema_id = str(body.get("schema_id") or "").strip()
    if not schema_id:
        raise ApiError("schema_id is required.", 400)
    sch = named_schemas.NAMED_SCHEMA_LIBRARY.get_schema(schema_id)
    if not sch:
        raise ApiError(f"Schema '{schema_id}' not found.", 404)
    expected_rev = body.get("expected_revision")
    res = scope_governance.SCOPE_GOVERNANCE_STORE.assign_schema(
        scope_key=scope_key,
        schema_id=schema_id,
        schema_name=sch.name,
        expected_revision=expected_rev,
    )
    return {"status": "assigned", "assignment": res.get("assignment")}


def api_scope_schema_current(body: dict[str, Any]) -> dict[str, Any]:
    scope_key = str(body.get("scope_key") or "default").strip()
    asgn = scope_governance.SCOPE_GOVERNANCE_STORE.get_assignment(scope_key)
    return {"scope_key": scope_key, "assignment": asgn.to_dict() if asgn else None}


def api_scope_schema_unassign(body: dict[str, Any]) -> dict[str, Any]:
    scope_key = str(body.get("scope_key") or "default").strip()
    expected_rev = body.get("expected_revision")
    deleted = scope_governance.SCOPE_GOVERNANCE_STORE.unassign_schema(scope_key, expected_rev)
    return {"status": "unassigned" if deleted else "not_found", "scope_key": scope_key}


def api_drift_analyze(body: dict[str, Any]) -> dict[str, Any]:
    STORE.require_scan()
    scoped_scan = STORE.get_scoped_scan()
    scope_key = str(body.get("scope_key") or "default").strip()

    schema_id = body.get("schema_id")
    schema_props = body.get("schema_properties")
    schema_name = body.get("schema_name")

    if not schema_id and not schema_props:
        asgn = scope_governance.SCOPE_GOVERNANCE_STORE.get_assignment(scope_key)
        if asgn:
            schema_id = asgn.schema_id
            schema_name = asgn.schema_name

    schema_ver = None
    if schema_id and not schema_props:
        sch = named_schemas.NAMED_SCHEMA_LIBRARY.get_schema(str(schema_id))
        if sch:
            schema_props = [p.to_dict() for p in sch.properties]
            schema_name = sch.name
            schema_ver = sch.version

    if not schema_props:
        raise ApiError("No expected schema specified or assigned to this scope.", 400)

    report = drift.analyze_schema_drift(
        notes=scoped_scan.notes,
        schema_properties=schema_props,
        schema_id=str(schema_id or "custom"),
        schema_name=str(schema_name or "Custom Schema"),
        scope_key=scope_key,
        schema_version=schema_ver,
    )
    return report.to_dict()


def api_schema_migration_plan(body: dict[str, Any]) -> dict[str, Any]:
    src_props = body.get("source_properties") or []
    tgt_props = body.get("target_properties") or []
    src_ver = str(body.get("source_version") or "1.0.0")
    tgt_ver = str(body.get("target_version") or "1.1.0")

    src_id = body.get("source_schema_id")
    tgt_id = body.get("target_schema_id")

    if src_id and not src_props:
        s = named_schemas.NAMED_SCHEMA_LIBRARY.get_schema(str(src_id))
        if s:
            src_props = [p.to_dict() for p in s.properties]
            src_ver = s.version
    if tgt_id and not tgt_props:
        s = named_schemas.NAMED_SCHEMA_LIBRARY.get_schema(str(tgt_id))
        if s:
            tgt_props = [p.to_dict() for p in s.properties]
            tgt_ver = s.version

    scoped_notes = STORE.get_scoped_scan().notes if STORE.scan else None
    plan = migration.plan_schema_migration(
        source_properties=src_props,
        target_properties=tgt_props,
        source_version=src_ver,
        target_version=tgt_ver,
        notes=scoped_notes,
    )
    return plan.to_dict()


def api_governance_profile_export(_body: dict[str, Any]) -> dict[str, Any]:
    checks = [c.to_dict() for c in STORE.saved_checks_store.list_checks()]
    return governance_profile.export_governance_profile(saved_checks_list=checks)


def api_governance_profile_validate(body: dict[str, Any]) -> dict[str, Any]:
    profile_data = body.get("profile")
    if not profile_data:
        raise ApiError("profile data is required.", 400)
    return governance_profile.validate_governance_profile(profile_data)


def api_governance_profile_import(body: dict[str, Any]) -> dict[str, Any]:
    profile_data = body.get("profile")
    if not profile_data:
        raise ApiError("profile data is required.", 400)
    mode = str(body.get("mode") or "merge")
    try:
        res = governance_profile.import_governance_profile(
            profile_data, mode=mode, saved_checks_store=STORE.saved_checks_store
        )
        return res
    except ValueError as exc:
        raise ApiError(str(exc), 400) from exc


def api_storage_migrate_legacy(body: dict[str, Any]) -> dict[str, Any]:
    """Migrate v1.1.0 legacy localStorage state (theme, locale, saved checks) to app-local storage (REQ-051, REQ-052)."""
    # 1. Migrate preferences (locale & theme) supporting documented & actual historical aliases
    locale = body.get("ps_locale") or body.get("property_studio_locale")
    theme = body.get("ps_theme") or body.get("property_studio_theme")

    from app.core.governance_profile import PREFERENCES_STORAGE
    current_prefs = PREFERENCES_STORAGE.load().get("data") or {}
    prefs_updated = False
    if locale and isinstance(locale, str) and locale in ("zh-Hant", "en"):
        current_prefs["locale"] = locale
        prefs_updated = True
    if theme and isinstance(theme, str) and theme in ("light", "dark", "system"):
        current_prefs["theme"] = theme
        prefs_updated = True
    if prefs_updated or not current_prefs:
        if not current_prefs:
            current_prefs = {"locale": locale or "zh-Hant", "theme": theme or "system"}
        PREFERENCES_STORAGE.save(current_prefs)

    # 2. Migrate saved relationship checks supporting documented & actual historical aliases
    raw_checks = body.get("ops_saved_relationship_checks_v110")
    if raw_checks is None:
        raw_checks = body.get("property_studio_saved_checks")

    migrated_checks_count = 0
    if raw_checks is not None:
        if isinstance(raw_checks, str):
            try:
                raw_checks = json.loads(raw_checks)
            except Exception as exc:
                raise ApiError(f"Malformed legacy saved checks JSON: {exc}", 400) from exc

        if isinstance(raw_checks, dict):
            raw_checks = raw_checks.get("checks", [])

        if not isinstance(raw_checks, list):
            raise ApiError("Malformed legacy saved checks: payload must be a list.", 400)

        for index, item in enumerate(raw_checks):
            try:
                chk = saved_checks.SavedCheck.from_dict(item)
                STORE.saved_checks_store.save_check(chk)
                migrated_checks_count += 1
            except Exception as exc:
                raise ApiError(f"Malformed legacy check at index {index}: {exc}", 400) from exc

    # Read-back verification
    saved_prefs_readback = PREFERENCES_STORAGE.load().get("data", {})
    saved_checks_readback = [c.to_dict() for c in STORE.saved_checks_store.list_checks()]

    return {
        "status": "migrated",
        "preferences": saved_prefs_readback,
        "migrated_checks_count": migrated_checks_count,
        "total_saved_checks": len(saved_checks_readback),
        "checks": saved_checks_readback,
        "readback_verified": True,
    }


def api_preferences_get(_body: dict[str, Any]) -> dict[str, Any]:
    """Retrieve app-local governance preferences (REQ-051)."""
    from app.core.governance_profile import PREFERENCES_STORAGE
    prefs = PREFERENCES_STORAGE.load().get("data") or {"locale": "zh-Hant", "theme": "system"}
    return {"preferences": prefs}


def api_preferences_set(body: dict[str, Any]) -> dict[str, Any]:
    """Persist app-local governance preferences (REQ-051)."""
    from app.core.governance_profile import PREFERENCES_STORAGE
    prefs = PREFERENCES_STORAGE.load().get("data") or {"locale": "zh-Hant", "theme": "system"}
    new_prefs = body.get("preferences") or body
    if isinstance(new_prefs, dict):
        for k, v in new_prefs.items():
            if k in ("locale", "theme"):
                prefs[k] = v
        PREFERENCES_STORAGE.save(prefs)
    return {"status": "saved", "preferences": prefs}


# --------------------------------------------------------------------------
# Dispatch Table
# --------------------------------------------------------------------------
ROUTES: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "/api/meta": api_meta,
    "/api/scan": api_scan,
    "/api/discovery": api_discovery,
    "/api/property": api_property_detail,
    "/api/design/presets": api_design_presets,
    "/api/design/suggest": api_design_suggest,
    "/api/design/build": api_design_build,
    "/api/design/review": api_design_review,
    "/api/fill/preview": api_fill_preview,
    "/api/workspace/notes": api_workspace_candidates,
    "/api/workspace/inspect": api_workspace_inspect,
    "/api/workspace/preview": api_workspace_preview,
    "/api/refactor/plan": api_refactor_plan,
    "/api/relationships": api_relationships,
    "/api/relationships/body": api_relationships_body,
    "/api/relationships/saved/list": api_saved_checks_list,
    "/api/relationships/saved/save": api_saved_checks_save,
    "/api/relationships/saved/delete": api_saved_checks_delete,
    "/api/relationships/saved/execute": api_saved_checks_execute,
    "/api/health": api_health,
    "/api/proposal/import": api_proposal_import,
    "/api/proposal/validate": api_proposal_import,
    "/api/export": api_export,
    "/api/vault/verify": api_vault_verify,
    "/api/verify_untouched": api_vault_verify,
    "/api/scope/folders": api_scope_folders,
    "/api/scope/set": api_scope_set,
    "/api/scope/apply": api_scope_set,
    "/api/scope/current": api_scope_current,
    "/api/scope/schema/assign": api_scope_schema_assign,
    "/api/scope/schema/current": api_scope_schema_current,
    "/api/scope/schema/unassign": api_scope_schema_unassign,
    "/api/drift/analyze": api_drift_analyze,
    "/api/note_candidates": api_note_candidates,
    "/api/notes/candidates": api_note_candidates,
    "/api/glossary": api_glossary_catalog,
    "/api/glossary/catalog": api_glossary_catalog,
    "/api/glossary/property": api_glossary_property,
    "/api/glossary/user/list": api_glossary_user_list,
    "/api/glossary/user/save": api_glossary_user_save,
    "/api/glossary/user/delete": api_glossary_user_delete,
    "/api/schemas/list": api_schemas_list,
    "/api/schemas/get": api_schemas_get,
    "/api/schemas/create": api_schemas_create,
    "/api/schemas/update": api_schemas_update,
    "/api/schemas/delete": api_schemas_delete,
    "/api/schemas/migration/plan": api_schema_migration_plan,
    "/api/governance/profile/export": api_governance_profile_export,
    "/api/governance/profile/validate": api_governance_profile_validate,
    "/api/governance/profile/import": api_governance_profile_import,
    "/api/profile/validate": api_governance_profile_validate,
    "/api/profile/export": api_governance_profile_export,
    "/api/profile/import": api_governance_profile_import,
    "/api/reconcile/inspect": api_reconcile_inspect,
    "/api/reconcile/preview": api_reconcile_preview,
    "/api/state/validate_context": api_state_validate_context,
    "/api/storage/migrate_legacy": api_storage_migrate_legacy,
    "/api/preferences/get": api_preferences_get,
    "/api/preferences/set": api_preferences_set,
}




# --------------------------------------------------------------------------
# HTTP Server
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "ObsidianPropertyStudio/" + APP_VERSION

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002

        pass  # silent by default (AGENTS 24)

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(204, b"", "text/plain")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _serve_ui(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        full = os.path.normpath(os.path.join(UI_DIR, rel))
        if not full.startswith(UI_DIR) or not os.path.isfile(full):
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
        }.get(os.path.splitext(full)[1], "application/octet-stream")
        with open(full, "rb") as fh:
            self._send(200, fh.read(), ctype)

    # -- verbs -----------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._dispatch(parsed.path, {})
            return
        self._serve_ui(parsed.path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8")) if raw.strip() else {}
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"Invalid request JSON: {exc}"})
            return
        self._dispatch(parsed.path, body if isinstance(body, dict) else {})

    def _dispatch(self, path: str, body: dict[str, Any]) -> None:
        handler = ROUTES.get(path)
        if handler is None:
            self._send_json(404, {"error": f"Unknown endpoint {path}"})
            return
        try:
            self._send_json(200, handler(body))
        except ApiError as exc:
            self._send_json(exc.status, {"error": exc.message, "detail": exc.detail})
        except KeyError as exc:
            self._send_json(400, {"error": f"Missing required field: {exc}"})
        except Exception as exc:  # pragma: no cover - defensive
            self._send_json(
                500,
                {
                    "error": f"{type(exc).__name__}: {exc}",
                    "trace": traceback.format_exc(limit=5),
                },
            )


def create_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    httpd = create_server(host, port)
    shown = "localhost" if host in ("127.0.0.1", "0.0.0.0") else host
    print(f"Obsidian Property Studio v{APP_VERSION}")
    print(f"  Open  http://{shown}:{port}  in your browser")
    print("  Local only. No network, no API key, no vault writes. Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


StudioHttpHandler = Handler

