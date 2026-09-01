"""Property Relationship Inbox & Scope-Aware Relationship Analysis (M007).

Property layer only (DEC-007, REQ-028, REQ-029, DEC-024):
1. Never touches note bodies or mutates backlinks.
2. Accepts multi-folder Source Scope (V11-009).
3. Accepts multi-folder Target Scope (V11-010).
4. Categorizes resolved links outside Target Scope as OUTSIDE SELECTED TARGET (V11-011).
5. Zero default rules or ontology assumptions on startup (V11-014).
"""

from __future__ import annotations

import difflib
from typing import Any

from .fill import WIKILINK_RE
from .inventory import build_inventory, normalize_value
from .model import Confidence, Severity, StorageType, VaultScan
from .scanner import note_name_index, note_path_index
from .scope import ScopeMode, ScopeSpec, filter_notes_by_scope

#: property types that can carry a relationship to another note
RELATIONSHIP_TYPES = (StorageType.TEXT, StorageType.LIST)


def _link_target(value: str) -> str | None:
    match = WIKILINK_RE.match(value.strip())
    if match:
        return match.group("target").strip()
    if value.strip().startswith("[[") and value.strip().endswith("]]"):
        inner = value.strip()[2:-2]
        return inner.split("|", 1)[0].strip()
    return None


def _resolve(
    target: str, name_index: dict[str, list[str]], path_index: dict[str, str]
) -> list[str]:
    key = target.strip().casefold()
    if key in path_index:  # full path reference wins
        return [path_index[key]]
    return list(name_index.get(key, []))


def _close_candidates(
    target: str, name_index: dict[str, list[str]], limit: int = 3
) -> list[str]:
    names = list(name_index)
    matches = difflib.get_close_matches(target.casefold(), names, n=limit, cutoff=0.8)
    out: list[str] = []
    for name in matches:
        out.extend(name_index[name])
    return sorted(set(out))


def _is_in_target_scope(note_path: str, target_scope: ScopeSpec | None, all_notes: list[Any]) -> bool:
    if target_scope is None or target_scope.mode == ScopeMode.ENTIRE_VAULT:
        return True
    scoped_notes = filter_notes_by_scope(all_notes, target_scope)
    scoped_paths = {n.path for n in scoped_notes}
    return note_path in scoped_paths


def build_inbox(
    scan: VaultScan,
    property_filter: str | None = None,
    source_scope: ScopeSpec | None = None,
    target_scope: ScopeSpec | None = None,
) -> dict[str, Any]:
    """Analyze property relationships with optional Source and Target scopes (REQ-028, REQ-029)."""
    name_index = note_name_index(scan)
    path_index = note_path_index(scan)

    # Filter source notes by source_scope (V11-009)
    source_notes = (
        filter_notes_by_scope(scan.notes, source_scope)
        if source_scope is not None and source_scope.mode != ScopeMode.ENTIRE_VAULT
        else scan.notes
    )

    items: list[dict[str, Any]] = []

    def add(**kwargs: Any) -> None:
        items.append(kwargs)

    for note in source_notes:
        for key in sorted(note.properties):
            if property_filter and key != property_filter:
                continue
            value = note.properties[key]
            if value.storage_type not in RELATIONSHIP_TYPES:
                continue
            ambiguous_note = key in note.duplicate_keys
            for scalar in value.scalars:
                if not scalar.strip():
                    continue
                target = _link_target(scalar)
                if target is not None:
                    hits = _resolve(target, name_index, path_index)
                    if len(hits) == 1:
                        resolved_path = hits[0]
                        # Check target scope boundary (V11-010, V11-011)
                        if not _is_in_target_scope(resolved_path, target_scope, scan.notes):
                            add(
                                id=f"outside-target:{note.path}:{key}:{scalar}",
                                kind="outside_target_scope",
                                confidence=Confidence.EXACT.value,
                                severity=Severity.LOW.value,
                                note=note.path,
                                property=key,
                                value=scalar,
                                candidates=hits,
                                canonical_target=resolved_path,
                                proposed_value=None,
                                title=f"Link '{target}' resolves outside selected Target Scope",
                                explanation=(
                                    f"Target note '{resolved_path}' exists in the vault but is outside "
                                    "the currently selected Target Scope."
                                ),
                                action="Verify whether this cross-folder relationship is intended.",
                                auto_resolved=False,
                            )
                        continue  # healthy resolved link within target scope
                    if len(hits) > 1:
                        add(
                            id=f"ambiguous-link:{note.path}:{key}:{scalar}",
                            kind="ambiguous_link",
                            confidence=Confidence.AMBIGUOUS.value,
                            severity=Severity.MEDIUM.value,
                            note=note.path,
                            property=key,
                            value=scalar,
                            candidates=hits,
                            canonical_target=None,
                            proposed_value=None,
                            title=f"'{target}' could mean {len(hits)} different notes",
                            explanation=(
                                "Several notes share this name. Property Studio will "
                                "not choose one for you."
                            ),
                            action="Pick the intended note, or use a full path link.",
                            auto_resolved=False,
                        )
                    else:
                        suggestions = _close_candidates(target, name_index)
                        add(
                            id=f"broken-link:{note.path}:{key}:{scalar}",
                            kind="broken_link",
                            confidence=Confidence.UNRESOLVED.value,
                            severity=Severity.HIGH.value,
                            note=note.path,
                            property=key,
                            value=scalar,
                            candidates=suggestions,
                            canonical_target=None,
                            proposed_value=None,
                            title=f"Link '{target}' points to no existing note",
                            explanation=(
                                "This property links to a note that does not exist in "
                                "this vault."
                            ),
                            action=(
                                "Create the note, fix the spelling, or clear the value."
                                + (
                                    f" Similar existing notes: {', '.join(suggestions)}"
                                    " (suggestions only)."
                                    if suggestions
                                    else ""
                                )
                            ),
                            auto_resolved=False,
                        )
                    continue

                # plain text value -> possible relationship
                hits = [
                    p
                    for p in _resolve(scalar, name_index, path_index)
                    if p != note.path  # a note naming itself is not a relationship
                ]
                if len(hits) == 1 and not ambiguous_note:
                    resolved_path = hits[0]
                    # If target scope specified, check if resolved is in target scope
                    is_in_target = _is_in_target_scope(resolved_path, target_scope, scan.notes)
                    if is_in_target:
                        add(
                            id=f"link-upgrade:{note.path}:{key}:{scalar}",
                            kind="link_upgrade_candidate",
                            confidence=Confidence.EXACT.value,
                            severity=Severity.LOW.value,
                            note=note.path,
                            property=key,
                            value=scalar,
                            candidates=hits,
                            canonical_target=resolved_path,
                            proposed_value=f"[[{scalar}]]",
                            title=f"'{scalar}' exactly matches the note {hits[0]}",
                            explanation=(
                                "This plain text value names an existing note. Turning it "
                                "into a link makes the relationship visible in Obsidian's "
                                "graph and backlinks."
                            ),
                            action="Review and, if correct, copy the proposed link value.",
                            auto_resolved=False,
                        )
                    else:
                        add(
                            id=f"outside-target-candidate:{note.path}:{key}:{scalar}",
                            kind="outside_target_scope",
                            confidence=Confidence.EXACT.value,
                            severity=Severity.LOW.value,
                            note=note.path,
                            property=key,
                            value=scalar,
                            candidates=hits,
                            canonical_target=resolved_path,
                            proposed_value=None,
                            title=f"'{scalar}' matches note outside target scope ({resolved_path})",
                            explanation="The target note exists in the vault but is outside the selected Target Scope.",
                            action="Verify whether this cross-folder relationship is intended.",
                            auto_resolved=False,
                        )
                elif len(hits) > 1:
                    add(
                        id=f"ambiguous-candidate:{note.path}:{key}:{scalar}",
                        kind="ambiguous_candidate",
                        confidence=Confidence.AMBIGUOUS.value,
                        severity=Severity.MEDIUM.value,
                        note=note.path,
                        property=key,
                        value=scalar,
                        candidates=hits,
                        canonical_target=None,
                        proposed_value=None,
                        title=f"'{scalar}' matches {len(hits)} notes",
                        explanation="More than one note could be meant, so no link is proposed.",
                        action="Choose the intended note yourself.",
                        auto_resolved=False,
                    )

    # relationship value drift within analyzed source notes
    inv = build_inventory(VaultScan(vault_path=scan.vault_path, notes=source_notes))
    link_keys = {
        key
        for key, entry in inv.properties.items()
        if any(_link_target(v) is not None for v in entry.values)
    }
    for key in sorted(link_keys):
        if property_filter and key != property_filter:
            continue
        entry = inv.properties[key]
        groups: dict[str, list[str]] = {}
        for stat in entry.values.values():
            target = _link_target(stat.value) or stat.value
            if not target.strip():
                continue
            groups.setdefault(normalize_value(target), []).append(stat.value)
        for norm, variants in sorted(groups.items()):
            if len(set(variants)) < 2:
                continue
            notes = sorted({n for v in variants for n in entry.values[v].notes})
            items.append(
                {
                    "id": f"relationship-drift:{key}:{norm}",
                    "kind": "relationship_drift",
                    "confidence": Confidence.EXACT.value,
                    "severity": Severity.LOW.value,
                    "note": notes[0] if notes else "",
                    "property": key,
                    "value": ", ".join(sorted(set(variants))),
                    "candidates": notes,
                    "canonical_target": None,
                    "proposed_value": None,
                    "title": (
                        f"'{key}' refers to the same target in {len(set(variants))} "
                        "different ways"
                    ),
                    "explanation": (
                        "Mixing plain text and links (or different spellings) for the "
                        "same target splits the relationship."
                    ),
                    "action": "Standardise on one form using the Refactor Planner.",
                    "auto_resolved": False,
                    "affected_notes": notes,
                }
            )

    items.sort(key=lambda i: (i["kind"], i["id"]))
    counts: dict[str, int] = {}
    for item in items:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1

    return {
        "summary": {
            "total_items": len(items),
            "by_kind": dict(sorted(counts.items())),
            "auto_resolved": 0,
            "scope": "property values only (no note body links are analysed or changed)",
        },
        "items": items,
    }
