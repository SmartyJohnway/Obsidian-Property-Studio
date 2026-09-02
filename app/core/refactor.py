"""Property Refactor Planner (M010) — scope-aware planning only, never applies (DEC-006, REQ-034, REQ-035).

Every plan is a read-only analysis of the canonical scan. There is deliberately
no function in this package that writes to a vault; ``apply_supported`` is
always ``False`` in the machine-readable output.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from .inventory import Inventory, build_inventory, normalize_value
from .model import StorageType, VaultScan
from .scanner import note_name_index
from .fill import WIKILINK_RE
from .scope import ScopeMode, ScopeSpec, filter_scan_by_scope

PLAN_FORMAT_VERSION = "1.1.0"

PLANNING_ONLY_NOTICE = (
    "Planning only. Obsidian Property Studio v1 never modifies your vault. "
    "Use this plan to make the changes yourself in Obsidian."
)


def _base_plan(operation: str, **fields: Any) -> dict[str, Any]:
    plan = {
        "plan_format_version": PLAN_FORMAT_VERSION,
        "operation": operation,
        "apply_supported": False,
        "notice": PLANNING_ONLY_NOTICE,
    }
    plan.update(fields)
    return plan


def _resolve_scoped_scan(scan: VaultScan, scope: ScopeSpec | None) -> tuple[VaultScan, bool]:
    if scope is not None and scope.mode != ScopeMode.ENTIRE_VAULT:
        return filter_scan_by_scope(scan, scope), True
    return scan, False


def _excluded_ambiguous(scan: VaultScan, keys: tuple[str, ...]) -> list[dict[str, str]]:
    excluded = []
    for note in scan.notes:
        for key in keys:
            if key in note.duplicate_keys:
                excluded.append(
                    {
                        "note": note.path,
                        "property": key,
                        "reason": (
                            "duplicate YAML key — value is ambiguous, so this note is "
                            "excluded from the plan (fail-closed)"
                        ),
                    }
                )
    return sorted(excluded, key=lambda e: (e["note"], e["property"]))


def _parse_failures(scan: VaultScan) -> list[dict[str, str]]:
    return sorted(
        (
            {"note": n.path, "reason": n.parse_status.value}
            for n in scan.notes
            if n.parse_failed
        ),
        key=lambda e: e["note"],
    )


# --------------------------------------------------------------------------
# Rename
# --------------------------------------------------------------------------
def plan_rename(
    scan: VaultScan, source: str, target: str, scope: ScopeSpec | None = None
) -> dict[str, Any]:
    active_scan, is_scoped = _resolve_scoped_scan(scan, scope)
    inv = build_inventory(active_scan)
    all_inv = build_inventory(scan) if is_scoped else inv

    affected: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    excluded = _excluded_ambiguous(active_scan, (source, target))
    excluded_notes = {e["note"] for e in excluded}

    for note in active_scan.notes:
        if source not in note.properties:
            continue
        if note.path in excluded_notes:
            continue
        src = note.properties[source]
        if target in note.properties:
            tgt = note.properties[target]
            conflicts.append(
                {
                    "note": note.path,
                    "reason": "target_property_already_present",
                    "detail": (
                        f"'{note.path}' already has '{target}'. Renaming would collide."
                    ),
                    "source_value": src.display,
                    "target_value": tgt.display,
                    "resolution": "manual review required",
                }
            )
            continue
        affected.append(
            {
                "note": note.path,
                "before": {source: src.display},
                "after": {target: src.display},
                "storage_type": src.storage_type.value,
            }
        )

    source_entry = inv.get(source)
    target_entry = inv.get(target)
    all_source_entry = all_inv.get(source)
    all_source_count = all_source_entry.usage_count if all_source_entry else 0

    type_warning = None
    if source_entry and target_entry and (
        source_entry.dominant_type != target_entry.dominant_type
    ):
        type_warning = (
            f"'{source}' is mostly stored as {source_entry.dominant_type} but "
            f"'{target}' is mostly {target_entry.dominant_type}. Renaming will create "
            "a type conflict."
        )

    summary: dict[str, Any] = {
        "source_usage_count": source_entry.usage_count if source_entry else 0,
        "target_existing_usage_count": target_entry.usage_count if target_entry else 0,
        "notes_to_change": len(affected),
        "in_scope_notes_to_change": len(affected),
        "out_of_scope_notes_to_change": max(0, all_source_count - (source_entry.usage_count if source_entry else 0)),
        "conflicts": len(conflicts),
        "excluded_ambiguous": len(excluded),
        "notes_with_parse_failure": len(_parse_failures(active_scan)),
    }

    return _base_plan(
        "rename_property",
        source=source,
        target=target,
        scope=scope.to_dict() if scope else {"mode": "entire_vault"},
        summary=summary,
        affected_notes=sorted(affected, key=lambda a: a["note"]),
        conflicts=sorted(conflicts, key=lambda c: c["note"]),
        excluded=excluded,
        unreadable_notes=_parse_failures(active_scan),
        warnings=[w for w in [type_warning] if w],
    )


# --------------------------------------------------------------------------
# Merge
# --------------------------------------------------------------------------
def plan_merge(
    scan: VaultScan, sources: list[str], target: str, scope: ScopeSpec | None = None
) -> dict[str, Any]:
    active_scan, is_scoped = _resolve_scoped_scan(scan, scope)
    all_keys = tuple(dict.fromkeys([*sources, target]))
    excluded = _excluded_ambiguous(active_scan, all_keys)
    excluded_notes = {e["note"] for e in excluded}

    affected: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    manual_review: list[dict[str, Any]] = []

    for note in active_scan.notes:
        present = [k for k in all_keys if k in note.properties]
        if not present or (present == [target]):
            continue
        if note.path in excluded_notes:
            continue
        values = {k: note.properties[k] for k in present}
        distinct = {v.display for v in values.values()}
        if len(distinct) == 1:
            affected.append(
                {
                    "note": note.path,
                    "before": {k: v.display for k, v in values.items()},
                    "after": {target: next(iter(distinct))},
                    "resolution": "identical values — safe to merge",
                }
            )
            continue
        list_like = all(
            v.storage_type in (StorageType.LIST, StorageType.TAGS)
            for v in values.values()
        )
        if list_like:
            union: list[str] = []
            for key in present:
                for scalar in values[key].scalars:
                    if scalar not in union:
                        union.append(scalar)
            manual_review.append(
                {
                    "note": note.path,
                    "reason": "list_values_differ",
                    "before": {k: v.display for k, v in values.items()},
                    "proposed_after": {target: "[" + ", ".join(union) + "]"},
                    "detail": (
                        "Lists can be combined, but confirm the union is what you "
                        "want before changing anything."
                    ),
                }
            )
            continue
        conflicts.append(
            {
                "note": note.path,
                "reason": "conflicting_values",
                "detail": (
                    "This note holds different values for the properties being "
                    "merged. The product will not choose a winner."
                ),
                "values": {k: v.display for k, v in values.items()},
                "resolution": "manual review required",
            }
        )

    inv = build_inventory(active_scan)
    return _base_plan(
        "merge_properties",
        sources=list(sources),
        target=target,
        scope=scope.to_dict() if scope else {"mode": "entire_vault"},
        summary={
            "notes_to_change": len(affected),
            "conflicts": len(conflicts),
            "manual_review": len(manual_review),
            "excluded_ambiguous": len(excluded),
            "usage": {
                key: (inv.get(key).usage_count if inv.get(key) else 0)
                for key in all_keys
            },
        },
        affected_notes=sorted(affected, key=lambda a: a["note"]),
        conflicts=sorted(conflicts, key=lambda c: c["note"]),
        manual_review=sorted(manual_review, key=lambda m: m["note"]),
        excluded=excluded,
        unreadable_notes=_parse_failures(active_scan),
        warnings=[],
    )


# --------------------------------------------------------------------------
# Normalize values
# --------------------------------------------------------------------------
def plan_normalize(
    scan: VaultScan,
    key: str,
    canonical_overrides: dict[str, str] | None = None,
    mapping: dict[str, str] | None = None,
    scope: ScopeSpec | None = None,
) -> dict[str, Any]:
    active_scan, is_scoped = _resolve_scoped_scan(scan, scope)
    inv: Inventory = build_inventory(active_scan)
    all_inv: Inventory = build_inventory(scan)
    entry = inv.get(key)
    all_entry = all_inv.get(key)
    all_usage = all_entry.usage_count if all_entry else 0
    in_scope_usage = entry.usage_count if entry else 0

    overrides = canonical_overrides or {}
    explicit_mapping = mapping or {}

    changes: list[dict[str, Any]] = []
    untouched: list[dict[str, Any]] = []

    if explicit_mapping and entry:
        # User provided explicit controlled mapping per observed value
        # e.g. {"In Progress": "active", "ongoing": "active", "active": "active"}
        target_groups: dict[str, list[Any]] = {}
        for stat in entry.values.values():
            if not stat.value.strip():
                continue
            orig_val = stat.value
            target_val = explicit_mapping.get(orig_val, orig_val)
            if target_val != orig_val:
                target_groups.setdefault(target_val, []).append(stat)
            else:
                untouched.append({
                    "value": orig_val,
                    "count": stat.count,
                    "reason": "mapped to self (kept as-is)",
                })

        for target_val, stats in sorted(target_groups.items()):
            variant_notes = sorted({p for s in stats for p in s.notes})
            changes.append({
                "canonical_value": target_val,
                "variants": [
                    {"value": s.value, "count": s.count, "notes": sorted(s.notes)}
                    for s in stats
                ],
                "match_basis": "user controlled mapping",
                "notes_to_change": variant_notes,
                "notes_to_change_count": len(variant_notes),
            })
    else:
        # Automatic grouping based on normalize_value (case/whitespace)
        groups: dict[str, list[Any]] = {}
        if entry:
            for stat in entry.values.values():
                if not stat.value.strip():
                    continue
                groups.setdefault(normalize_value(stat.value), []).append(stat)

        for norm, stats in sorted(groups.items()):
            stats.sort(key=lambda s: (-s.count, s.value))
            canonical = overrides.get(norm, stats[0].value)
            if len(stats) < 2 and canonical == stats[0].value:
                untouched.append(
                    {
                        "value": stats[0].value,
                        "count": stats[0].count,
                        "reason": (
                            "only one spelling of this value exists; a different value is "
                            "not assumed to mean the same thing"
                        ),
                    }
                )
                continue
            variant_notes = sorted(
                {p for s in stats for p in s.notes if s.value != canonical}
            )
            changes.append(
                {
                    "canonical_value": canonical,
                    "variants": [
                        {"value": s.value, "count": s.count, "notes": sorted(s.notes)}
                        for s in stats
                    ],
                    "match_basis": "case/whitespace only",
                    "notes_to_change": variant_notes,
                    "notes_to_change_count": len(variant_notes),
                }
            )

    excluded = _excluded_ambiguous(active_scan, (key,))
    notes_to_change_count = sum(c["notes_to_change_count"] for c in changes)

    return _base_plan(
        "normalize_values",
        property=key,
        scope=scope.to_dict() if scope else {"mode": "entire_vault"},
        summary={
            "usage_count": in_scope_usage,
            "in_scope_notes_to_change": notes_to_change_count,
            "out_of_scope_notes_to_change": max(0, all_usage - in_scope_usage),
            "distinct_values": entry.distinct_value_count if entry else 0,
            "groups_to_normalize": len(changes),
            "notes_to_change": notes_to_change_count,
            "values_left_untouched": len(untouched),
            "excluded_ambiguous": len(excluded),
        },
        changes=changes,
        untouched_values=untouched,
        excluded=excluded,
        unreadable_notes=_parse_failures(active_scan),
        warnings=[],
    )



# --------------------------------------------------------------------------
# Type conversion feasibility
# --------------------------------------------------------------------------
def _convertible_to(
    value_display: str,
    scalars: tuple[str, ...],
    storage: StorageType,
    target: str,
    name_index: dict[str, list[str]],
) -> tuple[str, str, str]:
    text = value_display.strip()
    if target == storage.value:
        return "already", text, "Already stored as the target type."

    if target == "note_link":
        if storage in (StorageType.LIST, StorageType.TAGS):
            outcomes = [
                _convertible_to(s, (s,), StorageType.TEXT, "note_link", name_index)
                for s in scalars
            ]
            if any(o[0] == "ambiguous" for o in outcomes):
                return "ambiguous", "", "One or more list items match several notes."
            if any(o[0] == "unresolved" for o in outcomes):
                return "unresolved", "", "One or more list items match no note."
            return (
                "convertible",
                "[" + ", ".join(o[1] for o in outcomes) + "]",
                "Every list item matches exactly one note.",
            )
        match = WIKILINK_RE.match(text)
        target_name = match.group("target").strip() if match else text
        hits = name_index.get(target_name.casefold(), [])
        if len(hits) == 1:
            return "convertible", f"[[{target_name}]]", f"Matches note '{hits[0]}'."
        if len(hits) > 1:
            return "ambiguous", "", f"Matches {len(hits)} notes: {', '.join(hits)}."
        return "unresolved", "", f"No note named '{target_name}' exists."

    if target == "number":
        try:
            float(text)
        except ValueError:
            return "unresolved", "", f"'{text}' is not a number."
        return "convertible", text, ""

    if target == "checkbox":
        if text.casefold() in ("true", "yes", "1", "done", "y"):
            return "convertible", "true", ""
        if text.casefold() in ("false", "no", "0", "n"):
            return "convertible", "false", ""
        return "unresolved", "", f"'{text}' is not a yes/no value."

    if target in ("date", "datetime"):
        candidate = text.replace("/", "-").strip()
        try:
            if target == "date":
                _dt.date.fromisoformat(candidate[:10])
                return "convertible", candidate[:10], ""
            _dt.datetime.fromisoformat(candidate.replace(" ", "T"))
            return "convertible", candidate, ""
        except ValueError:
            return "unresolved", "", f"'{text}' is not a valid {target}."

    if target == "list":
        if storage in (StorageType.LIST, StorageType.TAGS):
            return "already", text, ""
        return "convertible", f"[{text}]", "Single value becomes a one-item list."

    if target == "text":
        if storage in (StorageType.LIST, StorageType.TAGS):
            if len(scalars) > 1:
                return (
                    "ambiguous",
                    "",
                    "A list with several items cannot become one text value without "
                    "choosing which item to keep.",
                )
            return "convertible", scalars[0] if scalars else "", ""
        return "convertible", text, ""

    return "unresolved", "", f"Unsupported target type '{target}'."


def plan_type_conversion(
    scan: VaultScan, key: str, target_type: str, scope: ScopeSpec | None = None
) -> dict[str, Any]:
    active_scan, _ = _resolve_scoped_scan(scan, scope)
    name_index = note_name_index(scan)
    buckets: dict[str, list[dict[str, Any]]] = {
        "convertible": [],
        "ambiguous": [],
        "unresolved": [],
        "already": [],
    }
    excluded = _excluded_ambiguous(active_scan, (key,))
    excluded_notes = {e["note"] for e in excluded}

    for note in active_scan.notes:
        value = note.properties.get(key)
        if value is None or note.path in excluded_notes:
            continue
        if value.storage_type is StorageType.EMPTY:
            buckets["already"].append(
                {"note": note.path, "value": "", "detail": "empty value — nothing to convert"}
            )
            continue
        outcome, proposed, detail = _convertible_to(
            value.display, value.scalars, value.storage_type, target_type, name_index
        )
        buckets[outcome].append(
            {
                "note": note.path,
                "value": value.display,
                "proposed_value": proposed,
                "detail": detail,
                "current_type": value.storage_type.value,
            }
        )

    for bucket in buckets.values():
        bucket.sort(key=lambda item: item["note"])

    total = sum(len(b) for b in buckets.values())
    return _base_plan(
        "convert_property_type",
        property=key,
        target_type=target_type,
        scope=scope.to_dict() if scope else {"mode": "entire_vault"},
        summary={
            "values_examined": total,
            "convertible": len(buckets["convertible"]),
            "ambiguous": len(buckets["ambiguous"]),
            "unresolved": len(buckets["unresolved"]),
            "already_target_type": len(buckets["already"]),
            "excluded_ambiguous": len(excluded),
            "feasible_without_manual_work": len(buckets["ambiguous"]) == 0
            and len(buckets["unresolved"]) == 0,
        },
        convertible=buckets["convertible"],
        ambiguous=buckets["ambiguous"],
        unresolved=buckets["unresolved"],
        already_target_type=buckets["already"],
        excluded=excluded,
        unreadable_notes=_parse_failures(active_scan),
        warnings=[
            "Ambiguous and unresolved values are never converted automatically or "
            "guessed."
        ],
    )


# --------------------------------------------------------------------------
# Required / optional schema impact
# --------------------------------------------------------------------------
def plan_required_impact(
    scan: VaultScan,
    schema: Any,
    scope_property: str | None = None,
    scope_value: str | None = None,
    scope: ScopeSpec | None = None,
) -> dict[str, Any]:
    """Impact of making schema fields required, scoped to matching notes."""
    active_scan, _ = _resolve_scoped_scan(scan, scope)
    schema_keys = [p.name for p in schema.properties]
    required_keys = [p.name for p in schema.properties if p.required]

    in_scope: list[Any] = []
    for note in active_scan.notes:
        if note.parse_failed:
            continue
        if scope_property:
            value = note.properties.get(scope_property)
            if value is None:
                continue
            if scope_value is not None and scope_value not in value.scalars:
                continue
        elif not any(k in note.properties for k in schema_keys):
            continue
        in_scope.append(note)

    missing: list[dict[str, Any]] = []
    for note in in_scope:
        gaps = [k for k in required_keys if k not in note.properties]
        empties = [
            k
            for k in required_keys
            if k in note.properties
            and note.properties[k].storage_type is StorageType.EMPTY
        ]
        if gaps or empties:
            missing.append(
                {
                    "note": note.path,
                    "missing_properties": gaps,
                    "empty_properties": empties,
                }
            )

    return _base_plan(
        "required_optional_impact",
        schema_name=getattr(schema, "name", ""),
        scope={"property": scope_property, "value": scope_value, "spec": scope.to_dict() if scope else None},
        summary={
            "notes_in_scope": len(in_scope),
            "required_properties": required_keys,
            "notes_missing_required": len(missing),
            "notes_compliant": len(in_scope) - len(missing),
            "notes_with_parse_failure": len(_parse_failures(active_scan)),
        },
        missing=sorted(missing, key=lambda m: m["note"]),
        unreadable_notes=_parse_failures(active_scan),
        warnings=[
            "Notes whose frontmatter could not be parsed are listed separately and "
            "are not counted as compliant."
        ],
    )
