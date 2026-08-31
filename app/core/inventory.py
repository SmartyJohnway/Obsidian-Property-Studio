"""Discovery / inventory analysis (M003).

Everything here is derived from the canonical :class:`VaultScan` — no module
re-parses YAML on its own (REQ-004).
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from typing import Any

from .model import Confidence, Finding, Severity, StorageType, VaultScan

_SEPARATORS = re.compile(r"[\s_\-./]+")
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def normalize_key(key: str) -> str:
    """Case/separator-insensitive normal form used for *deterministic* drift."""
    spaced = _CAMEL.sub(" ", key.strip())
    return _SEPARATORS.sub("", spaced).casefold()


def key_tokens(key: str) -> tuple[str, ...]:
    spaced = _CAMEL.sub(" ", key.strip())
    return tuple(t for t in _SEPARATORS.split(spaced.casefold()) if t)


def normalize_value(value: str) -> str:
    return " ".join(value.strip().casefold().split())


@dataclass
class ValueStat:
    value: str
    count: int
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value, "count": self.count, "notes": sorted(self.notes)}


@dataclass
class PropertyEntry:
    """Everything known about one property key across the vault."""

    key: str
    usage_count: int = 0                      # notes containing the key
    notes: list[str] = field(default_factory=list)
    empty_count: int = 0
    observed_types: dict[str, int] = field(default_factory=dict)
    type_notes: dict[str, list[str]] = field(default_factory=dict)
    values: dict[str, ValueStat] = field(default_factory=dict)
    ambiguous_notes: list[str] = field(default_factory=list)  # duplicate YAML key

    @property
    def dominant_type(self) -> str:
        candidates = [
            (count, name)
            for name, count in self.observed_types.items()
            if name != StorageType.EMPTY.value
        ]
        if not candidates:
            return StorageType.EMPTY.value
        candidates.sort(key=lambda item: (-item[0], item[1]))
        return candidates[0][1]

    @property
    def distinct_value_count(self) -> int:
        return len(self.values)

    def top_values(self, limit: int = 20) -> list[ValueStat]:
        ordered = sorted(self.values.values(), key=lambda v: (-v.count, v.value))
        return ordered[:limit]

    def to_dict(self, value_limit: int = 20) -> dict[str, Any]:
        return {
            "key": self.key,
            "usage_count": self.usage_count,
            "empty_count": self.empty_count,
            "observed_types": dict(sorted(self.observed_types.items())),
            "dominant_type": self.dominant_type,
            "distinct_value_count": self.distinct_value_count,
            "top_values": [v.to_dict() for v in self.top_values(value_limit)],
            "notes": sorted(self.notes),
            "ambiguous_notes": sorted(self.ambiguous_notes),
        }


@dataclass
class Inventory:
    properties: dict[str, PropertyEntry] = field(default_factory=dict)
    note_count: int = 0
    notes_with_properties: int = 0

    def sorted_entries(self) -> list[PropertyEntry]:
        return sorted(
            self.properties.values(), key=lambda e: (-e.usage_count, e.key.casefold())
        )

    def get(self, key: str) -> PropertyEntry | None:
        return self.properties.get(key)

    def to_dict(self, value_limit: int = 20) -> dict[str, Any]:
        return {
            "note_count": self.note_count,
            "notes_with_properties": self.notes_with_properties,
            "unique_property_count": len(self.properties),
            "properties": [e.to_dict(value_limit) for e in self.sorted_entries()],
        }


def build_inventory(scan: VaultScan) -> Inventory:
    inv = Inventory(
        note_count=scan.note_count, notes_with_properties=scan.notes_with_properties
    )
    for note in scan.notes:
        for key, value in note.properties.items():
            entry = inv.properties.get(key)
            if entry is None:
                entry = PropertyEntry(key=key)
                inv.properties[key] = entry
            entry.usage_count += 1
            entry.notes.append(note.path)
            if key in note.duplicate_keys:
                entry.ambiguous_notes.append(note.path)
            type_name = value.storage_type.value
            entry.observed_types[type_name] = entry.observed_types.get(type_name, 0) + 1
            entry.type_notes.setdefault(type_name, []).append(note.path)
            if value.storage_type is StorageType.EMPTY:
                entry.empty_count += 1
                continue
            for scalar in value.scalars:
                stat = entry.values.get(scalar)
                if stat is None:
                    stat = ValueStat(value=scalar, count=0)
                    entry.values[scalar] = stat
                stat.count += 1
                stat.notes.append(note.path)
    return inv


# --------------------------------------------------------------------------
# drift / conflict analysis
# --------------------------------------------------------------------------
def naming_drift_findings(inv: Inventory) -> list[Finding]:
    """Case/format drift (deterministic) + possible semantic overlap (labelled)."""
    findings: list[Finding] = []

    groups: dict[str, list[PropertyEntry]] = {}
    for entry in inv.properties.values():
        groups.setdefault(normalize_key(entry.key), []).append(entry)

    for norm, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        entries.sort(key=lambda e: (-e.usage_count, e.key))
        keys = [e.key for e in entries]
        case_only = len({k.casefold() for k in keys}) == 1
        affected: list[str] = sorted({p for e in entries for p in e.notes})
        findings.append(
            Finding(
                id=f"naming-drift:{norm}",
                category="naming_drift",
                severity=Severity.MEDIUM,
                title=("Case drift" if case_only else "Naming/format drift")
                + f": {', '.join(keys)}",
                explanation=(
                    "These property keys are the same word written differently, so "
                    "Obsidian treats them as separate properties and filtering/"
                    "grouping splits across them."
                ),
                recommendation=(
                    f"Consider standardising on '{keys[0]}' "
                    f"(most used: {entries[0].usage_count} notes) via the Refactor "
                    "Planner. Nothing is changed automatically."
                ),
                property_keys=tuple(keys),
                affected_notes=tuple(affected),
                evidence={
                    "normalized_key": norm,
                    "variants": [
                        {"key": e.key, "usage_count": e.usage_count} for e in entries
                    ],
                    "match_basis": "case only" if case_only else "case/separator",
                },
                confidence=Confidence.EXACT,
            )
        )

    # possible semantic overlap — never auto-merged, always labelled "possible"
    keys_sorted = sorted(inv.properties)
    for i, key_a in enumerate(keys_sorted):
        for key_b in keys_sorted[i + 1 :]:
            if normalize_key(key_a) == normalize_key(key_b):
                continue  # already reported as drift
            tokens_a, tokens_b = set(key_tokens(key_a)), set(key_tokens(key_b))
            if not tokens_a or not tokens_b:
                continue
            subset = tokens_a < tokens_b or tokens_b < tokens_a
            ratio = difflib.SequenceMatcher(
                None, normalize_key(key_a), normalize_key(key_b)
            ).ratio()
            if not subset and ratio < 0.82:
                continue
            entry_a = inv.properties[key_a]
            entry_b = inv.properties[key_b]
            findings.append(
                Finding(
                    id=f"possible-overlap:{key_a}|{key_b}",
                    category="possible_semantic_overlap",
                    severity=Severity.LOW,
                    title=f"Possible overlap: '{key_a}' and '{key_b}'",
                    explanation=(
                        "These two property names look related, but the product "
                        "cannot prove they mean the same thing. This is a "
                        "possibility for you to judge, not a confirmed duplicate."
                    ),
                    recommendation=(
                        "Review both properties' values. Merge only if you decide "
                        "they mean the same thing."
                    ),
                    property_keys=(key_a, key_b),
                    affected_notes=tuple(sorted(set(entry_a.notes) | set(entry_b.notes))),
                    evidence={
                        "similarity_ratio": round(ratio, 3),
                        "token_subset": subset,
                        "usage": {
                            key_a: entry_a.usage_count,
                            key_b: entry_b.usage_count,
                        },
                        "auto_merge": False,
                    },
                    confidence=Confidence.POSSIBLE,
                )
            )
    return findings


def value_drift_findings(inv: Inventory) -> list[Finding]:
    findings: list[Finding] = []
    for entry in sorted(inv.properties.values(), key=lambda e: e.key):
        groups: dict[str, list[ValueStat]] = {}
        for stat in entry.values.values():
            if not stat.value.strip():
                continue
            groups.setdefault(normalize_value(stat.value), []).append(stat)
        for norm, stats in sorted(groups.items()):
            if len(stats) < 2:
                continue
            stats.sort(key=lambda s: (-s.count, s.value))
            affected = sorted({p for s in stats for p in s.notes})
            findings.append(
                Finding(
                    id=f"value-drift:{entry.key}:{norm}",
                    category="value_drift",
                    severity=Severity.LOW,
                    title=(
                        f"'{entry.key}' uses inconsistent spellings of "
                        f"{', '.join(repr(s.value) for s in stats)}"
                    ),
                    explanation=(
                        "The same value is written with different capitalisation or "
                        "spacing, so it appears as several different values when you "
                        "filter or group."
                    ),
                    recommendation=(
                        f"Normalize to '{stats[0].value}' with the Refactor Planner "
                        "(planning only — the vault is not modified)."
                    ),
                    property_keys=(entry.key,),
                    affected_notes=tuple(affected),
                    evidence={
                        "normalized_value": norm,
                        "variants": [
                            {"value": s.value, "count": s.count} for s in stats
                        ],
                    },
                    confidence=Confidence.EXACT,
                )
            )
    return findings


#: date/datetime are related shapes — a mix is a low-severity conflict.
_LOW_SEVERITY_PAIRS = frozenset({frozenset({"date", "datetime"})})


def type_conflict_findings(inv: Inventory) -> list[Finding]:
    findings: list[Finding] = []
    for entry in sorted(inv.properties.values(), key=lambda e: e.key):
        observed = {
            name: count
            for name, count in entry.observed_types.items()
            if name != StorageType.EMPTY.value
        }
        if len(observed) < 2:
            continue
        names = frozenset(observed)
        severity = (
            Severity.LOW if names in _LOW_SEVERITY_PAIRS else Severity.HIGH
        )
        affected = sorted({p for name in observed for p in entry.type_notes[name]})
        findings.append(
            Finding(
                id=f"type-conflict:{entry.key}",
                category="type_conflict",
                severity=severity,
                title=(
                    f"'{entry.key}' is stored as "
                    + " and ".join(sorted(observed))
                    + " in different notes"
                ),
                explanation=(
                    "Obsidian expects one property type per property. Mixed shapes "
                    "break sorting, filtering and Bases/Dataview style queries."
                ),
                recommendation=(
                    "Decide the intended type and use the Refactor Planner's type "
                    "conversion feasibility check before changing anything."
                ),
                property_keys=(entry.key,),
                affected_notes=tuple(affected),
                evidence={
                    "observed_types": dict(sorted(observed.items())),
                    "notes_by_type": {
                        name: sorted(entry.type_notes[name]) for name in sorted(observed)
                    },
                },
                confidence=Confidence.EXACT,
            )
        )
    return findings


def ambiguity_findings(inv: Inventory) -> list[Finding]:
    """Duplicate YAML keys — fail-closed, never resolved automatically."""
    findings: list[Finding] = []
    for entry in sorted(inv.properties.values(), key=lambda e: e.key):
        if not entry.ambiguous_notes:
            continue
        findings.append(
            Finding(
                id=f"duplicate-key:{entry.key}",
                category="ambiguous_property",
                severity=Severity.HIGH,
                title=f"'{entry.key}' is defined more than once in the same note",
                explanation=(
                    "Duplicate YAML keys have no single defined value. The product "
                    "refuses to guess which one is correct."
                ),
                recommendation=(
                    "Open the listed notes and keep exactly one definition of this "
                    "property."
                ),
                property_keys=(entry.key,),
                affected_notes=tuple(sorted(entry.ambiguous_notes)),
                evidence={"policy": "fail-closed: excluded from dependent plans"},
                confidence=Confidence.EXACT,
            )
        )
    return findings


def parse_findings(scan: VaultScan) -> list[Finding]:
    """Parse failures surfaced as first-class findings (REQ-003)."""
    findings: list[Finding] = []
    by_status: dict[str, list[str]] = {}
    detail: dict[str, list[dict[str, str]]] = {}
    for note in scan.notes:
        if note.parse_failed:
            by_status.setdefault(note.parse_status.value, []).append(note.path)
            detail.setdefault(note.parse_status.value, []).append(
                {
                    "note": note.path,
                    "message": note.issues[0].message if note.issues else "",
                    "detail": note.issues[0].detail if note.issues else "",
                }
            )
    for status, paths in sorted(by_status.items()):
        findings.append(
            Finding(
                id=f"parse-failure:{status}",
                category="parse_failure",
                severity=Severity.HIGH,
                title=f"{len(paths)} note(s) with unreadable properties ({status})",
                explanation=(
                    "These notes could not be parsed. They are NOT counted as notes "
                    "without properties — their property layer is unknown."
                ),
                recommendation="Fix the frontmatter in Obsidian, then rescan.",
                affected_notes=tuple(sorted(paths)),
                evidence={"notes": sorted(detail[status], key=lambda d: d["note"])},
                confidence=Confidence.EXACT,
            )
        )
    return findings


def discovery_report(scan: VaultScan, inv: Inventory | None = None) -> dict[str, Any]:
    """The Discover tab payload — one canonical answer for UI and exports."""
    inventory = inv if inv is not None else build_inventory(scan)
    findings = (
        parse_findings(scan)
        + naming_drift_findings(inventory)
        + value_drift_findings(inventory)
        + type_conflict_findings(inventory)
        + ambiguity_findings(inventory)
    )
    findings.sort(key=lambda f: (f.category, f.id))
    return {
        "summary": scan.summary(),
        "inventory": inventory.to_dict(),
        "findings": [f.to_dict() for f in findings],
        "issues": [i.to_dict() for i in scan.issues],
        "skipped": [s.to_dict() for s in scan.skipped],
    }
