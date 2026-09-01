"""Local HTTP server for Obsidian Property Studio.

Standard-library only (plus PyYAML in the core) so that the app runs on a plain
Windows 11 Python install with one dependency.

Safety:
  * binds to 127.0.0.1 by default (AGENTS 24);
  * exposes **no** endpoint that writes into a vault (AGENTS 30);
  * all exports go to a folder outside the vault;
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

from .core import design, exports, health, inventory, proposal, refactor, relationships
from .core.manifest import assert_unchanged, vault_manifest
from .core.fill import fill_preview
from .core.model import (
    STORAGE_TYPE_LABELS,
    UI_CONTROL_ALLOWED_STORAGE,
    UI_CONTROL_SERIALIZATION,
    Schema,
)
from .core.scanner import ScanOptions, VaultPathError, note_name_index, scan_vault

APP_VERSION = "1.0.0"
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")


class Store:
    """In-memory state for the current session (never persisted in the vault)."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.scan = None
        self.inventory = None
        self.baseline_manifest: dict[str, Any] | None = None
        self.vault_path: str | None = None

    def set_scan(self, scan, baseline: dict[str, Any] | None) -> None:
        with self.lock:
            self.scan = scan
            self.inventory = inventory.build_inventory(scan)
            self.vault_path = scan.vault_path
            if baseline is not None:
                self.baseline_manifest = baseline

    def require_scan(self):
        if self.scan is None:
            raise ApiError("Select and scan a vault first.", 400)
        return self.scan


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400, detail: Any = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.detail = detail


STORE = Store()


# --------------------------------------------------------------------------
# API handlers
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
    return inventory.discovery_report(scan, STORE.inventory)


def api_property_detail(body: dict[str, Any]) -> dict[str, Any]:
    STORE.require_scan()
    key = body.get("key", "")
    entry = STORE.inventory.get(key) if STORE.inventory else None
    if entry is None:
        raise ApiError(f"Property '{key}' is not used in this vault.", 404)
    return {
        "entry": entry.to_dict(value_limit=200),
        "notes_by_type": {k: sorted(v) for k, v in sorted(entry.type_notes.items())},
    }


def api_design_suggest(body: dict[str, Any]) -> dict[str, Any]:
    goal = str(body.get("goal", ""))
    return {
        "recipes": design.suggest_recipes(goal, limit=4),
        "detected_intents": design.detect_intents(goal),
    }


def api_design_build(body: dict[str, Any]) -> dict[str, Any]:
    goal = str(body.get("goal", ""))
    schema = design.build_schema(
        goal_text=goal,
        recipe_id=body.get("recipe_id") or None,
        intent_ids=tuple(body.get("intents", []) or []),
        schema_name=body.get("schema_name") or None,
        inv=STORE.inventory,
    )
    inv = STORE.inventory or inventory.Inventory()
    return design.review_schema_against_vault(schema, inv)


def api_design_review(body: dict[str, Any]) -> dict[str, Any]:
    schema = Schema.from_dict(body.get("schema", {}))
    inv = STORE.inventory or inventory.Inventory()
    return design.review_schema_against_vault(schema, inv)


def api_fill_preview(body: dict[str, Any]) -> dict[str, Any]:
    schema = Schema.from_dict(body.get("schema", {}))
    values = body.get("values", {}) or {}
    index = note_name_index(STORE.scan) if STORE.scan is not None else None
    return fill_preview(schema, values, index)


def api_note_candidates(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    query = str(body.get("query", "")).strip().casefold()
    matches = []
    for note in scan.notes:
        if query and query not in note.name.casefold() and query not in note.path.casefold():
            continue
        matches.append({"name": note.name, "path": note.path})
        if len(matches) >= 50:
            break
    index = note_name_index(scan)
    ambiguous = sorted(name for name, paths in index.items() if len(paths) > 1)
    return {"candidates": matches, "ambiguous_names": ambiguous}


def api_refactor_plan(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    operation = body.get("operation")
    if operation == "rename":
        plan = refactor.plan_rename(scan, body["source"], body["target"])
    elif operation == "merge":
        plan = refactor.plan_merge(scan, list(body.get("sources", [])), body["target"])
    elif operation == "normalize":
        plan = refactor.plan_normalize(
            scan, body["property"], body.get("canonical_overrides") or None
        )
    elif operation == "convert_type":
        plan = refactor.plan_type_conversion(scan, body["property"], body["target_type"])
    elif operation == "required_impact":
        schema = Schema.from_dict(body.get("schema", {}))
        plan = refactor.plan_required_impact(
            scan, schema, body.get("scope_property") or None, body.get("scope_value") or None
        )
    else:
        raise ApiError(f"Unknown refactor operation '{operation}'.", 400)
    return plan


def api_relationships(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    return relationships.build_inbox(scan, body.get("property") or None)


def api_health(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    schema_data = body.get("schema")
    schema = Schema.from_dict(schema_data) if schema_data else None
    return health.health_report(
        scan,
        STORE.inventory,
        schema,
        body.get("scope_property") or None,
        body.get("scope_value") or None,
    )


def api_proposal_import(body: dict[str, Any]) -> dict[str, Any]:
    text = body.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ApiError("Paste or open a proposal JSON file first.", 400)
    return proposal.import_proposal(text, STORE.inventory)


def api_export(body: dict[str, Any]) -> dict[str, Any]:
    scan = STORE.require_scan()
    kind = body.get("kind")
    params = body.get("params", {}) or {}
    if kind == "discovery":
        payload = inventory.discovery_report(scan, STORE.inventory)
    elif kind == "health":
        schema_data = params.get("schema")
        payload = health.health_report(
            scan,
            STORE.inventory,
            Schema.from_dict(schema_data) if schema_data else None,
            params.get("scope_property") or None,
            params.get("scope_value") or None,
        )
    elif kind == "inbox":
        payload = relationships.build_inbox(scan, params.get("property") or None)
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


ROUTES: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "/api/meta": api_meta,
    "/api/scan": api_scan,
    "/api/discovery": api_discovery,
    "/api/property": api_property_detail,
    "/api/design/suggest": api_design_suggest,
    "/api/design/build": api_design_build,
    "/api/design/review": api_design_review,
    "/api/fill/preview": api_fill_preview,
    "/api/notes/candidates": api_note_candidates,
    "/api/refactor/plan": api_refactor_plan,
    "/api/relationships": api_relationships,
    "/api/health": api_health,
    "/api/proposal/import": api_proposal_import,
    "/api/export": api_export,
    "/api/vault/verify": api_vault_verify,
}


class Handler(BaseHTTPRequestHandler):
    server_version = f"PropertyStudio/{APP_VERSION}"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter console
        if os.environ.get("PROPERTY_STUDIO_VERBOSE"):
            super().log_message(fmt, *args)

    # -- helpers ---------------------------------------------------------
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

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
