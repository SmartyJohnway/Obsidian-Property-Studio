"""End-to-end tests through the real local HTTP server (M001/M010).

These exercise the same endpoints the browser UI calls, so a passing suite
means the shipped application — not just the library — behaves correctly.
"""

from __future__ import annotations

import json
import os
import threading
import urllib.request

import pytest

from app.core.manifest import assert_unchanged, vault_manifest
from app.server import create_server
from conftest import MAIN_VAULT, PROPOSALS


@pytest.fixture(scope="module")
def server():
    httpd = create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[0], httpd.server_address[1]
    yield f"http://{host}:{port}"
    httpd.shutdown()
    httpd.server_close()


def post(base: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        base + path, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read().decode("utf-8")) | {"_status": exc.code}


def test_ui_is_served(server):
    with urllib.request.urlopen(server + "/", timeout=30) as res:
        html = res.read().decode("utf-8")
    assert res.status == 200
    assert "Obsidian Property Studio" in html
    # UI must be self-contained: no external network resources (offline/local-first)
    for token in ("http://", "https://"):
        assert token not in html.replace("http://localhost", "").replace(
            "http-equiv", ""
        ), "UI must not reference external resources"


def test_meta_declares_local_only(server):
    meta = post(server, "/api/meta")
    assert meta["vault_write_capability"] is False
    assert meta["requires_network"] is False
    assert meta["requires_api_key"] is False
    assert meta["proposal_contract_version"] == "1.0"
    assert "text" in meta["storage_types"] and "note_link" in meta["ui_controls"]


def test_full_workflow_over_http_leaves_vault_untouched(server, tmp_path):
    before = vault_manifest(MAIN_VAULT)

    scan = post(server, "/api/scan", {"vault_path": MAIN_VAULT})
    assert scan["summary"]["note_count"] == 22
    assert scan["summary"]["notes_with_parse_failure"] == 3

    detail = post(server, "/api/property", {"key": "status"})
    assert detail["entry"]["usage_count"] == 9

    build = post(
        server,
        "/api/design/build",
        {"goal": "I want to manage lab equipment", "recipe_id": "equipment",
         "intents": ["track_location"], "schema_name": "equipment"},
    )
    schema = build["schema"]
    assert build["counts"]["exact_existing"] >= 1  # 'project'/'location' already exist

    preview = post(
        server,
        "/api/fill/preview",
        {"schema": schema, "values": {"type": "equipment", "status": "in use",
                                      "location": "lab", "owner": "Ada Lovelace"}},
    )
    assert preview["roundtrip"]["matches"] is True
    assert preview["frontmatter"].startswith("---\n")

    candidates = post(server, "/api/notes/candidates", {"query": "duplicate"})
    assert "duplicate name" in candidates["ambiguous_names"]

    plan = post(server, "/api/refactor/plan",
                {"operation": "merge", "sources": ["project_name"], "target": "project"})
    assert plan["apply_supported"] is False and plan["summary"]["conflicts"] == 1

    inbox = post(server, "/api/relationships", {})
    assert inbox["summary"]["auto_resolved"] == 0

    report = post(server, "/api/health", {"schema": schema, "scope_property": "type",
                                          "scope_value": "equipment"})
    assert report["health_score"]["score"] >= 0
    assert report["summary"]["finding_count"] == len(report["findings"])

    export = post(server, "/api/export",
                  {"kind": "health", "params": {"schema": schema},
                   "output_dir": str(tmp_path)})
    assert export["verification"]["no_silent_omission"] is True
    assert os.path.isfile(export["files"][0]["path"])

    verify = post(server, "/api/vault/verify", {})
    assert verify["unchanged"] is True
    assert verify["files_created"] == verify["files_modified"] == verify["files_deleted"] == 0

    assert assert_unchanged(before, vault_manifest(MAIN_VAULT))["unchanged"] is True


def test_export_into_vault_is_refused_over_http(server):
    post(server, "/api/scan", {"vault_path": MAIN_VAULT})
    result = post(server, "/api/export",
                  {"kind": "discovery", "output_dir": os.path.join(MAIN_VAULT, "out")})
    assert result.get("_status") == 400
    assert "Refusing to write inside the selected vault" in result["error"]
    assert not os.path.exists(os.path.join(MAIN_VAULT, "out"))


def test_bad_vault_path_returns_useful_error(server):
    result = post(server, "/api/scan", {"vault_path": "/definitely/not/here"})
    assert result.get("_status") == 400
    assert "does not exist" in result["error"]


def test_proposal_endpoints(server):
    post(server, "/api/scan", {"vault_path": MAIN_VAULT})
    valid = open(os.path.join(PROPOSALS, "valid_equipment.json"), encoding="utf-8").read()
    result = post(server, "/api/proposal/import", {"text": valid})
    assert result["valid"] is True and result["vault_modified"] is False
    assert len(result["comparison"]) == 3

    bad = open(os.path.join(PROPOSALS, "invalid_malformed_json.json"), encoding="utf-8").read()
    rejected = post(server, "/api/proposal/import", {"text": bad})
    assert rejected["valid"] is False and rejected["schema"] is None

    empty = post(server, "/api/proposal/import", {"text": "   "})
    assert empty.get("_status") == 400


def test_unknown_endpoint_and_bad_json(server):
    assert post(server, "/api/nope").get("_status") == 404
    req = urllib.request.Request(
        server + "/api/scan", data=b"{not json", headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=30)
        raise AssertionError("should have failed")
    except urllib.error.HTTPError as exc:
        assert exc.code == 400
