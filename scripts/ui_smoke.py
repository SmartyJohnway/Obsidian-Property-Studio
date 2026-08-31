"""Live-server smoke evidence (M001-T08 / M010-T01…T04 / M011-T03).

Starts the real application server on a free loopback port, drives the same
endpoints the browser UI uses, and writes ``evidence/ui-smoke.json``.

Run:  python scripts/ui_smoke.py
"""

from __future__ import annotations

import json
import os
import platform
import socket
import sys
import threading
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.server import APP_VERSION, create_server  # noqa: E402

VAULT = os.path.join(ROOT, "fixtures", "vaults", "main_vault")
EVIDENCE = os.path.join(ROOT, "evidence")


def post(base: str, path: str, payload: dict | None = None):
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(base + path, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def main() -> int:
    httpd = create_server("127.0.0.1", 0)
    host, port = httpd.server_address[0], httpd.server_address[1]
    base = f"http://{host}:{port}"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    steps = []
    try:
        with urllib.request.urlopen(base + "/", timeout=30) as res:
            html = res.read().decode("utf-8")
        steps.append({
            "step": "GET / (UI)",
            "http_status": res.status,
            "bytes": len(html),
            "title_present": "Obsidian Property Studio" in html,
            "external_resource_references": sum(
                html.count(token) for token in ("src=\"http", "href=\"http")
            ),
        })

        status, meta = post(base, "/api/meta")
        steps.append({"step": "POST /api/meta", "http_status": status,
                      "version": meta["version"],
                      "vault_write_capability": meta["vault_write_capability"],
                      "requires_network": meta["requires_network"],
                      "requires_api_key": meta["requires_api_key"]})

        status, scan = post(base, "/api/scan", {"vault_path": VAULT})
        steps.append({"step": "POST /api/scan", "http_status": status,
                      "summary": scan["summary"], "scan_seconds": scan["scan_seconds"]})

        status, build = post(base, "/api/design/build",
                             {"goal": "I want to manage my lab equipment",
                              "recipe_id": "equipment", "intents": ["track_location"],
                              "schema_name": "equipment"})
        schema = build["schema"]
        steps.append({"step": "POST /api/design/build", "http_status": status,
                      "properties": [p["name"] for p in schema["properties"]],
                      "reuse_counts": build["counts"]})

        status, preview = post(base, "/api/fill/preview",
                               {"schema": schema,
                                "values": {"type": "equipment", "status": "in use",
                                           "location": "lab", "owner": "Ada Lovelace"}})
        steps.append({"step": "POST /api/fill/preview", "http_status": status,
                      "frontmatter": preview["frontmatter"],
                      "roundtrip_matches": preview["roundtrip"]["matches"],
                      "errors": preview["errors"], "warnings": preview["warnings"]})

        for params in (
            {"operation": "rename", "source": "Project", "target": "project"},
            {"operation": "merge", "sources": ["project_name"], "target": "project"},
            {"operation": "normalize", "property": "status"},
            {"operation": "convert_type", "property": "project", "target_type": "note_link"},
        ):
            status, plan = post(base, "/api/refactor/plan", params)
            steps.append({"step": f"POST /api/refactor/plan ({params['operation']})",
                          "http_status": status, "apply_supported": plan["apply_supported"],
                          "summary": plan["summary"]})

        status, inbox = post(base, "/api/relationships", {})
        steps.append({"step": "POST /api/relationships", "http_status": status,
                      "summary": inbox["summary"]})

        status, report = post(base, "/api/health", {"schema": schema})
        steps.append({"step": "POST /api/health", "http_status": status,
                      "score": report["health_score"]["score"],
                      "finding_count": report["summary"]["finding_count"]})

        proposal_text = open(os.path.join(ROOT, "fixtures", "proposals",
                                          "valid_equipment.json"), encoding="utf-8").read()
        status, imported = post(base, "/api/proposal/import", {"text": proposal_text})
        steps.append({"step": "POST /api/proposal/import (valid)", "http_status": status,
                      "valid": imported["valid"], "vault_modified": imported["vault_modified"],
                      "comparison_statuses": [c["status"] for c in imported["comparison"]]})

        bad_text = open(os.path.join(ROOT, "fixtures", "proposals",
                                     "invalid_unsupported_version.json"), encoding="utf-8").read()
        status, rejected = post(base, "/api/proposal/import", {"text": bad_text})
        steps.append({"step": "POST /api/proposal/import (unsupported version)",
                      "http_status": status, "valid": rejected["valid"],
                      "errors": rejected["errors"]})

        status, refused = post(base, "/api/export",
                               {"kind": "discovery",
                                "output_dir": os.path.join(VAULT, "should-not-exist")})
        steps.append({"step": "POST /api/export into the vault (must be refused)",
                      "http_status": status, "error": refused.get("error"),
                      "folder_created": os.path.exists(
                          os.path.join(VAULT, "should-not-exist"))})

        status, verify = post(base, "/api/vault/verify", {})
        steps.append({"step": "POST /api/vault/verify", "http_status": status,
                      "unchanged": verify["unchanged"],
                      "files_checked": verify["files_checked"],
                      "files_created": verify["files_created"],
                      "files_modified": verify["files_modified"],
                      "files_deleted": verify["files_deleted"]})
    finally:
        httpd.shutdown()
        httpd.server_close()

    record = {
        "case": "local application launch + end-to-end UI API smoke",
        "app_version": APP_VERSION,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "bind_default": "127.0.0.1 (loopback only)",
            "bound_for_this_run": f"{host}:{port}",
            "hostname": socket.gethostname(),
        },
        "vault": VAULT,
        "steps": steps,
        "all_http_ok": all(
            s.get("http_status") in (200, 400) for s in steps
        ),
        "vault_unchanged_after_smoke": steps[-1]["unchanged"],
    }
    os.makedirs(EVIDENCE, exist_ok=True)
    with open(os.path.join(EVIDENCE, "ui-smoke.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("steps:", len(steps), "| vault unchanged:", record["vault_unchanged_after_smoke"])
    return 0 if record["vault_unchanged_after_smoke"] else 1


if __name__ == "__main__":
    sys.exit(main())
