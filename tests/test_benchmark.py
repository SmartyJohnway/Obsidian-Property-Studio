"""OPS-AC-028 — larger synthetic vault benchmark.

Performance here is *measured evidence*, not a pass/fail threshold: PROJECT.md
REQ-018 and AGENTS 35 explicitly forbid inventing an unapproved seconds gate.
The only assertions are functional (it completes, results are correct and the
vault is untouched); timings are recorded to ``evidence/benchmark.json``.
"""

from __future__ import annotations

import json
import os
import platform
import sys
import time

import pytest

from app.core import health, inventory, refactor, relationships
from app.core.manifest import assert_unchanged, vault_manifest
from app.core.scanner import scan_vault

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from make_benchmark_vault import build  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "evidence")
NOTE_COUNT = int(os.environ.get("PROPERTY_STUDIO_BENCH_NOTES", "5000"))


def _rss_mb() -> float | None:
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1]) / 1024, 1)
    except OSError:
        return None
    return None


@pytest.mark.benchmark
def test_ops_ac_028_large_vault_benchmark(tmp_path):
    vault = str(tmp_path / "benchmark_vault")
    t0 = time.perf_counter()
    build(vault, NOTE_COUNT)
    generate_seconds = time.perf_counter() - t0

    before = vault_manifest(vault)

    t0 = time.perf_counter()
    scan = scan_vault(vault)
    scan_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    inv = inventory.build_inventory(scan)
    inventory_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    discovery = inventory.discovery_report(scan, inv)
    discovery_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    inbox = relationships.build_inbox(scan)
    relationship_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    report = health.health_report(scan, inv)
    health_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    plan = refactor.plan_type_conversion(scan, "owner_name", "note_link")
    plan_seconds = time.perf_counter() - t0

    integrity = assert_unchanged(before, vault_manifest(vault))

    # functional expectations (no invented time threshold)
    assert scan.note_count == NOTE_COUNT + 40  # notes + person notes
    assert scan.notes_with_parse_failure > 0   # malformed notes are still reported
    assert inv.get("status") is not None
    assert integrity["unchanged"] is True

    record = {
        "case": "OPS-AC-028",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "cpu_count": os.cpu_count(),
        },
        "fixture": {
            "markdown_notes": scan.note_count,
            "files_hashed": len(before),
            "vault_bytes": sum(e["size"] for e in before.values()),
            "generator": "scripts/make_benchmark_vault.py (seeded, deterministic)",
            "generate_seconds": round(generate_seconds, 3),
        },
        "measurements_seconds": {
            "scan": round(scan_seconds, 3),
            "inventory": round(inventory_seconds, 3),
            "discovery_report": round(discovery_seconds, 3),
            "relationship_inbox": round(relationship_seconds, 3),
            "health_report": round(health_seconds, 3),
            "type_conversion_plan": round(plan_seconds, 3),
            "total_analysis": round(
                scan_seconds + inventory_seconds + discovery_seconds
                + relationship_seconds + health_seconds + plan_seconds, 3
            ),
        },
        "observations": {
            "peak_rss_mb_after_run": _rss_mb(),
            "unique_properties": len(inv.properties),
            "findings": len(discovery["findings"]),
            "health_findings": report["summary"]["finding_count"],
            "inbox_items": inbox["summary"]["total_items"],
            "notes_with_parse_failure": scan.notes_with_parse_failure,
            "crash": False,
        },
        "vault_integrity": {
            "files_created": integrity["files_created"],
            "files_modified": integrity["files_modified"],
            "files_deleted": integrity["files_deleted"],
            "unchanged": integrity["unchanged"],
        },
        "threshold_policy": (
            "No pre-approved hard seconds threshold exists in PROJECT.md/ROADMAP.md. "
            "These numbers are measured evidence only."
        ),
    }
    if os.environ.get("PROPERTY_STUDIO_WRITE_BENCHMARK_EVIDENCE") == "1":
        os.makedirs(EVIDENCE, exist_ok=True)
        os.makedirs(os.path.join(EVIDENCE, "integration"), exist_ok=True)
        with open(os.path.join(EVIDENCE, "benchmark.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(EVIDENCE, "integration", "m009_benchmark.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    else:
        with open(tmp_path / "benchmark_run.json", "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
    print(json.dumps(record["measurements_seconds"], indent=2))

