"""Regenerate the verification artifacts under ``evidence/``.

Run:  python scripts/collect_evidence.py

Produces (all outside any vault):
  evidence/readonly-verification.json   pre/post vault manifest proof for a full workflow
  evidence/determinism.json             two independent runs compared
  evidence/e2e/                         exported discovery/health/plan/inbox/schema artifacts
  evidence/e2e-summary.json             read-back verification of every exported artifact
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.core import design, exports, health, inventory, proposal, refactor, relationships  # noqa: E402
from app.core.fill import fill_preview  # noqa: E402
from app.core.manifest import assert_unchanged, vault_manifest  # noqa: E402
from app.core.scanner import note_name_index, scan_vault  # noqa: E402
from app.server import APP_VERSION  # noqa: E402

VAULT = os.path.join(ROOT, "fixtures", "vaults", "main_vault")
EVIDENCE = os.path.join(ROOT, "evidence")
E2E = os.path.join(EVIDENCE, "e2e")


def digest(payload) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def full_workflow(vault: str) -> dict:
    scan = scan_vault(vault)
    inv = inventory.build_inventory(scan)
    schema = design.build_schema(
        "I want to manage my lab equipment and know where each item is",
        "equipment",
        ["track_location"],
        inv=inv,
    )
    payload = {
        "discovery": inventory.discovery_report(scan, inv),
        "schema": schema.to_dict(),
        "schema_review": design.review_schema_against_vault(schema, inv),
        "fill": fill_preview(
            schema,
            {
                "type": "equipment",
                "status": "in use",
                "location": "lab",
                "owner": "Ada Lovelace",
                "serial_number": "SN-003",
                "purchase_date": "2026-01-15",
            },
            note_name_index(scan),
        ),
        "plan_rename": refactor.plan_rename(scan, "Project", "project"),
        "plan_merge": refactor.plan_merge(scan, ["project_name"], "project"),
        "plan_normalize": refactor.plan_normalize(scan, "status"),
        "plan_convert": refactor.plan_type_conversion(scan, "project", "note_link"),
        "plan_required": refactor.plan_required_impact(scan, schema, "type", "equipment"),
        "inbox": relationships.build_inbox(scan),
        "health": health.health_report(scan, inv, schema, "type", "equipment"),
        "proposal_valid": proposal.import_proposal(
            open(os.path.join(ROOT, "fixtures", "proposals", "valid_equipment.json"),
                 encoding="utf-8").read(), inv),
        "proposal_invalid": proposal.import_proposal(
            open(os.path.join(ROOT, "fixtures", "proposals", "invalid_bad_types.json"),
                 encoding="utf-8").read(), inv),
    }
    payload["discovery"].pop("scan_seconds", None)
    return payload


def main() -> int:
    os.makedirs(EVIDENCE, exist_ok=True)
    os.makedirs(E2E, exist_ok=True)

    before = vault_manifest(VAULT)
    run_a = full_workflow(VAULT)
    mid = vault_manifest(VAULT)
    run_b = full_workflow(VAULT)
    after = vault_manifest(VAULT)

    integrity = assert_unchanged(before, after)
    readonly = {
        "case": "OPS-AC-005 / REQ-002",
        "app_version": APP_VERSION,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "vault": VAULT,
        "files_hashed": len(before),
        "workflow_executed": sorted(run_a),
        "files_created": integrity["files_created"],
        "files_modified": integrity["files_modified"],
        "files_deleted": integrity["files_deleted"],
        "files_renamed": 0,
        "unchanged": integrity["unchanged"],
        "manifest_digest_before": integrity["before_digest"],
        "manifest_digest_after": integrity["after_digest"],
        "manifest_digest_mid_run": assert_unchanged(before, mid)["after_digest"],
        "detail": integrity["detail"],
    }
    with open(os.path.join(EVIDENCE, "readonly-verification.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(readonly, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    determinism = {
        "case": "OPS-AC-027 / SC-12",
        "runs": 2,
        "compared_sections": sorted(run_a),
        "per_section": {
            key: {
                "digest_run_1": digest(run_a[key]),
                "digest_run_2": digest(run_b[key]),
                "identical": digest(run_a[key]) == digest(run_b[key]),
            }
            for key in sorted(run_a)
        },
        "all_identical": all(digest(run_a[k]) == digest(run_b[k]) for k in run_a),
        "note": "scan_seconds (wall clock) is excluded; it is not a semantic field.",
    }
    with open(os.path.join(EVIDENCE, "determinism.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(determinism, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    exported = []
    for kind, payload, basename in (
        ("discovery", run_a["discovery"], "discovery"),
        ("health", run_a["health"], "health"),
        ("inbox", run_a["inbox"], "relationship-inbox"),
        ("plan", run_a["plan_rename"], "plan-rename"),
        ("plan", run_a["plan_merge"], "plan-merge"),
        ("plan", run_a["plan_normalize"], "plan-normalize"),
        ("plan", run_a["plan_convert"], "plan-convert-type"),
        ("plan", run_a["plan_required"], "plan-required-impact"),
        ("schema", run_a["schema"], "schema-equipment"),
    ):
        result = exports.export_artifact(kind, payload, VAULT, E2E, basename)
        source_items = len(payload.get("findings", [])) or len(payload.get("items", []))
        exported.append(
            {
                "kind": kind,
                "basename": basename,
                "files": [
                    {
                        "path": os.path.relpath(f["path"], ROOT),
                        "bytes": f["bytes"],
                        "read_back_matches": f["read_back_matches"],
                    }
                    for f in result["files"]
                ],
                "items_in_memory": source_items,
                "items_in_file": result["verification"]["finding_count_in_file"],
                "no_silent_omission": result["verification"]["no_silent_omission"],
            }
        )

    summary = {
        "case": "OPS-AC-026 / REQ-015 output read-back",
        "app_version": APP_VERSION,
        "vault": VAULT,
        "artifacts": exported,
        "all_read_back_ok": all(
            f["read_back_matches"] for a in exported for f in a["files"]
        ),
        "all_complete": all(a["no_silent_omission"] for a in exported),
        "export_destination_inside_vault": False,
        "counts": {
            "notes": run_a["discovery"]["summary"]["note_count"],
            "unique_properties": run_a["discovery"]["inventory"]["unique_property_count"],
            "discovery_findings": len(run_a["discovery"]["findings"]),
            "health_findings": len(run_a["health"]["findings"]),
            "health_score": run_a["health"]["health_score"]["score"],
            "inbox_items": run_a["inbox"]["summary"]["total_items"],
            "fill_roundtrip_matches": run_a["fill"]["roundtrip"]["matches"],
            "proposal_valid_accepted": run_a["proposal_valid"]["valid"],
            "proposal_invalid_rejected": not run_a["proposal_invalid"]["valid"],
        },
    }
    with open(os.path.join(EVIDENCE, "e2e-summary.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("read-only unchanged:", readonly["unchanged"])
    print("deterministic:", determinism["all_identical"])
    print("artifacts complete:", summary["all_complete"])
    return 0 if (readonly["unchanged"] and determinism["all_identical"]
                 and summary["all_complete"]) else 1


if __name__ == "__main__":
    sys.exit(main())
