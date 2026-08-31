"""Property Health & Governance (M008).

Every finding drills down to property + notes + reason + severity (REQ-011).
The health score is a published arithmetic formula, never a magic number
(SC-09): it is derived from the same findings shown in the UI.
"""

from __future__ import annotations

from typing import Any

from .inventory import (
    Inventory,
    ambiguity_findings,
    build_inventory,
    naming_drift_findings,
    parse_findings,
    type_conflict_findings,
    value_drift_findings,
)
from .model import Confidence, Finding, Schema, Severity, StorageType, VaultScan
from .relationships import build_inbox

#: Published deduction weights, per finding, per category (SC-09 transparency).
CATEGORY_WEIGHTS: dict[str, float] = {
    "parse_failure": 8.0,
    "ambiguous_property": 6.0,
    "type_conflict": 5.0,
    "naming_drift": 4.0,
    "missing_required_property": 3.0,
    "value_drift": 2.0,
    "broken_relationship": 2.0,
    "ambiguous_relationship": 1.5,
    "unexpected_property": 1.0,
    "possible_semantic_overlap": 0.0,   # informational only — never penalised
    "link_upgrade_opportunity": 0.0,
}

#: Maximum total deduction a single category may contribute.
CATEGORY_CAPS: dict[str, float] = {
    "parse_failure": 25.0,
    "ambiguous_property": 15.0,
    "type_conflict": 20.0,
    "naming_drift": 15.0,
    "missing_required_property": 15.0,
    "value_drift": 10.0,
    "broken_relationship": 10.0,
    "ambiguous_relationship": 8.0,
    "unexpected_property": 5.0,
    "possible_semantic_overlap": 0.0,
    "link_upgrade_opportunity": 0.0,
}

SCORE_FORMULA = (
    "score = max(0, 100 - sum over categories of min(category_cap, "
    "weight_per_finding * finding_count)). Weights and caps are listed in "
    "'score_breakdown'. Informational categories have weight 0."
)


def schema_findings(
    scan: VaultScan,
    inv: Inventory,
    schema: Schema,
    scope_property: str | None = None,
    scope_value: str | None = None,
) -> list[Finding]:
    """Missing expected properties + unexpected keys for notes in schema scope."""
    findings: list[Finding] = []
    schema_keys = {p.name for p in schema.properties}
    required_keys = [p.name for p in schema.properties if p.required]

    in_scope = []
    for note in scan.notes:
        if note.parse_failed:
            continue
        if scope_property:
            value = note.properties.get(scope_property)
            if value is None:
                continue
            if scope_value is not None and scope_value not in value.scalars:
                continue
        elif not (schema_keys & set(note.properties)):
            continue
        in_scope.append(note)

    for key in required_keys:
        missing = [
            n.path
            for n in in_scope
            if key not in n.properties
            or n.properties[key].storage_type is StorageType.EMPTY
        ]
        if not missing:
            continue
        findings.append(
            Finding(
                id=f"missing-required:{schema.name}:{key}",
                category="missing_required_property",
                severity=Severity.MEDIUM,
                title=f"{len(missing)} note(s) in scope are missing '{key}'",
                explanation=(
                    f"Schema '{schema.name}' marks '{key}' as required, but these "
                    "notes do not have a usable value for it."
                ),
                recommendation=(
                    f"Fill '{key}' on those notes (Property Fill can generate the "
                    "frontmatter to paste)."
                ),
                property_keys=(key,),
                affected_notes=tuple(sorted(missing)),
                evidence={
                    "schema": schema.name,
                    "scope": {"property": scope_property, "value": scope_value},
                    "notes_in_scope": len(in_scope),
                },
            )
        )

    unexpected: dict[str, list[str]] = {}
    for note in in_scope:
        for key in note.properties:
            if key not in schema_keys:
                unexpected.setdefault(key, []).append(note.path)
    for key, notes in sorted(unexpected.items()):
        entry = inv.get(key)
        findings.append(
            Finding(
                id=f"unexpected-property:{schema.name}:{key}",
                category="unexpected_property",
                severity=Severity.LOW,
                title=f"'{key}' is used by in-scope notes but is not in the schema",
                explanation=(
                    "This property is not part of the selected schema. It is reported "
                    "for review only — nothing is deleted or rewritten."
                ),
                recommendation=(
                    f"Either add '{key}' to the schema or decide it is intentional."
                ),
                property_keys=(key,),
                affected_notes=tuple(sorted(notes)),
                evidence={
                    "usage_count": entry.usage_count if entry else len(notes),
                    "dominant_type": entry.dominant_type if entry else "unknown",
                    "destructive_action_taken": False,
                },
                confidence=Confidence.EXACT,
            )
        )
    return findings


def relationship_findings(inbox: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    mapping = {
        "broken_link": ("broken_relationship", Severity.HIGH),
        "ambiguous_link": ("ambiguous_relationship", Severity.MEDIUM),
        "ambiguous_candidate": ("ambiguous_relationship", Severity.MEDIUM),
        "link_upgrade_candidate": ("link_upgrade_opportunity", Severity.INFO),
        "relationship_drift": ("value_drift", Severity.LOW),
    }
    for item in inbox["items"]:
        category, severity = mapping.get(item["kind"], ("relationship_issue", Severity.LOW))
        findings.append(
            Finding(
                id=f"health:{item['id']}",
                category=category,
                severity=severity,
                title=item["title"],
                explanation=item["explanation"],
                recommendation=item["action"],
                property_keys=(item["property"],),
                affected_notes=tuple(item.get("affected_notes") or [item["note"]]),
                evidence={
                    "value": item["value"],
                    "candidates": item["candidates"],
                    "auto_resolved": False,
                },
                confidence=Confidence(item["confidence"]),
            )
        )
    return findings


def compute_score(findings: list[Finding]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1
    breakdown = []
    total_deduction = 0.0
    for category in sorted(counts):
        weight = CATEGORY_WEIGHTS.get(category, 1.0)
        cap = CATEGORY_CAPS.get(category, 10.0)
        raw = weight * counts[category]
        applied = min(cap, raw)
        total_deduction += applied
        breakdown.append(
            {
                "category": category,
                "finding_count": counts[category],
                "weight_per_finding": weight,
                "raw_deduction": round(raw, 2),
                "category_cap": cap,
                "applied_deduction": round(applied, 2),
            }
        )
    score = max(0.0, round(100.0 - total_deduction, 2))
    return {
        "score": score,
        "total_deduction": round(total_deduction, 2),
        "formula": SCORE_FORMULA,
        "score_breakdown": breakdown,
    }


def health_report(
    scan: VaultScan,
    inv: Inventory | None = None,
    schema: Schema | None = None,
    scope_property: str | None = None,
    scope_value: str | None = None,
) -> dict[str, Any]:
    inventory = inv if inv is not None else build_inventory(scan)
    inbox = build_inbox(scan)

    findings: list[Finding] = []
    findings += parse_findings(scan)
    findings += ambiguity_findings(inventory)
    findings += type_conflict_findings(inventory)
    findings += naming_drift_findings(inventory)
    findings += value_drift_findings(inventory)
    findings += relationship_findings(inbox)
    if schema is not None:
        findings += schema_findings(
            scan, inventory, schema, scope_property, scope_value
        )

    findings.sort(key=lambda f: (f.category, f.id))
    score = compute_score(findings)

    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for finding in findings:
        by_severity[finding.severity.value] = by_severity.get(finding.severity.value, 0) + 1
        by_category[finding.category] = by_category.get(finding.category, 0) + 1

    return {
        "report_format_version": "1.0",
        "vault_path": scan.vault_path,
        "summary": {
            **scan.summary(),
            "unique_property_count": len(inventory.properties),
            "finding_count": len(findings),
            "by_severity": dict(sorted(by_severity.items())),
            "by_category": dict(sorted(by_category.items())),
            "schema_applied": schema.name if schema else None,
        },
        "health_score": score,
        "findings": [f.to_dict() for f in findings],
    }
