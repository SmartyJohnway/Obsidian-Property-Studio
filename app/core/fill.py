"""Property Fill: schema-driven values -> inspectable, valid frontmatter (M005).

Nothing in this module writes to the vault. It produces text that the user
reviews and copies manually (DEC-004). No note body / template is generated
(DEC-005, REQ-014).
"""

from __future__ import annotations

import datetime as _dt
import re
from typing import Any

import yaml

from .model import (
    Schema,
    SchemaProperty,
    StorageType,
    UIControl,
)
from .scanner import classify_value, extract_frontmatter

WIKILINK_RE = re.compile(r"^\[\[(?P<target>[^\[\]|]+)(\|(?P<alias>[^\[\]]*))?\]\]$")


class FillError(ValueError):
    pass


def wrap_note_link(value: str) -> str:
    text = str(value).strip()
    if not text:
        return ""
    if WIKILINK_RE.match(text):
        return text
    return f"[[{text}]]"


def _as_list(raw: Any) -> list[Any]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return list(raw)
    if isinstance(raw, str):
        if raw.strip() == "":
            return []
        # UI sends comma or newline separated text for list inputs
        parts = re.split(r"[\n,]", raw)
        return [p.strip() for p in parts if p.strip()]
    return [raw]


def coerce_value(prop: SchemaProperty, raw: Any) -> tuple[Any, list[str]]:
    """Convert a UI input into the value that will be serialised.

    Returns ``(value, errors)``. ``value`` is ``None`` when the field is blank.
    """
    errors: list[str] = []
    control = prop.ui_control
    storage = prop.storage_type

    if storage in (StorageType.LIST, StorageType.TAGS) or control in (
        UIControl.MULTI_CHOICE,
        UIControl.NOTE_LINK_LIST,
    ):
        items = [str(i).strip() for i in _as_list(raw) if str(i).strip() != ""]
        if control == UIControl.NOTE_LINK_LIST:
            items = [wrap_note_link(i) for i in items]
        if control == UIControl.MULTI_CHOICE and prop.allowed_values:
            for item in items:
                if item not in prop.allowed_values:
                    errors.append(
                        f"'{prop.name}': '{item}' is not one of the allowed values "
                        f"({', '.join(prop.allowed_values)})."
                    )
        if not items:
            if prop.required:
                errors.append(f"'{prop.name}' is required but empty.")
            return None, errors
        return items, errors

    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        if prop.required:
            errors.append(f"'{prop.name}' is required but empty.")
        return None, errors

    text = str(raw).strip() if not isinstance(raw, bool) else raw

    if storage is StorageType.CHECKBOX:
        if isinstance(raw, bool):
            return raw, errors
        lowered = str(raw).strip().casefold()
        if lowered in ("true", "yes", "1", "on", "checked"):
            return True, errors
        if lowered in ("false", "no", "0", "off", "unchecked"):
            return False, errors
        errors.append(f"'{prop.name}': '{raw}' is not a yes/no value.")
        return None, errors

    if storage is StorageType.NUMBER:
        try:
            number = float(str(text))
        except ValueError:
            errors.append(f"'{prop.name}': '{raw}' is not a number.")
            return None, errors
        value: Any = int(number) if number.is_integer() and "." not in str(text) else number
        if prop.allowed_values and str(value) not in prop.allowed_values:
            errors.append(
                f"'{prop.name}': '{value}' is not one of the allowed values."
            )
        return value, errors

    if storage is StorageType.DATE:
        try:
            return _dt.date.fromisoformat(str(text)), errors
        except ValueError:
            errors.append(
                f"'{prop.name}': '{raw}' is not a date. Use the date picker "
                "(YYYY-MM-DD)."
            )
            return None, errors

    if storage is StorageType.DATETIME:
        candidate = str(text).replace(" ", "T")
        try:
            return _dt.datetime.fromisoformat(candidate), errors
        except ValueError:
            errors.append(
                f"'{prop.name}': '{raw}' is not a date & time. Use YYYY-MM-DD HH:MM."
            )
            return None, errors

    # text
    result = str(text)
    if control is UIControl.NOTE_LINK:
        result = wrap_note_link(result)
    if control is UIControl.SINGLE_CHOICE and prop.allowed_values:
        if result not in prop.allowed_values:
            errors.append(
                f"'{prop.name}': '{result}' is not one of the allowed values "
                f"({', '.join(prop.allowed_values)})."
            )
    return result, errors


def build_property_mapping(
    schema: Schema, values: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    mapping: dict[str, Any] = {}
    errors: list[str] = []
    for prop in schema.properties:
        value, prop_errors = coerce_value(prop, values.get(prop.name))
        errors.extend(prop_errors)
        if value is None:
            continue
        mapping[prop.name] = value
    return mapping, errors


def render_yaml(mapping: dict[str, Any]) -> str:
    if not mapping:
        return ""
    return yaml.safe_dump(
        mapping,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=4096,
    )


def render_frontmatter(mapping: dict[str, Any]) -> str:
    body = render_yaml(mapping)
    return f"---\n{body}---\n"


def canonical_from_mapping(mapping: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "storage_type": classify_value(key, value).storage_type.value,
            "display": classify_value(key, value).display,
            "scalars": list(classify_value(key, value).scalars),
        }
        for key, value in mapping.items()
    }


def roundtrip_check(frontmatter_text: str, mapping: dict[str, Any]) -> dict[str, Any]:
    """Parse the generated frontmatter back through the canonical parser.

    OPS-AC-010 / AGENTS 32: generated YAML must parse and round-trip to the same
    value semantics that were previewed.
    """
    source, terminated = extract_frontmatter(frontmatter_text)
    result: dict[str, Any] = {
        "parses": False,
        "terminated": terminated,
        "matches": False,
        "differences": [],
    }
    if source is None or not terminated:
        result["differences"].append("Generated text is not a closed frontmatter block.")
        return result
    try:
        parsed = yaml.safe_load(source) if source.strip() else {}
    except yaml.YAMLError as exc:
        result["differences"].append(f"YAML parse error: {exc}")
        return result
    result["parses"] = True
    parsed = parsed or {}
    expected = canonical_from_mapping(mapping)
    actual = canonical_from_mapping(parsed)
    for key in sorted(set(expected) | set(actual)):
        if key not in actual:
            result["differences"].append(f"'{key}' missing after re-parsing.")
        elif key not in expected:
            result["differences"].append(f"'{key}' appeared unexpectedly.")
        elif expected[key] != actual[key]:
            result["differences"].append(
                f"'{key}' changed: previewed {expected[key]} vs re-parsed {actual[key]}."
            )
    result["matches"] = not result["differences"]
    result["reparsed"] = actual
    return result


def fill_preview(
    schema: Schema, values: dict[str, Any], note_index: dict[str, list[str]] | None = None
) -> dict[str, Any]:
    """Full fill result: preview text, validation, ambiguity, round-trip proof."""
    mapping, errors = build_property_mapping(schema, values)
    frontmatter = render_frontmatter(mapping)
    warnings: list[str] = []

    if note_index is not None:
        for prop in schema.properties:
            if prop.ui_control not in (UIControl.NOTE_LINK, UIControl.NOTE_LINK_LIST):
                continue
            value = mapping.get(prop.name)
            candidates = value if isinstance(value, list) else ([value] if value else [])
            for item in candidates:
                match = WIKILINK_RE.match(str(item))
                if not match:
                    continue
                target = match.group("target").strip()
                hits = note_index.get(target.casefold(), [])
                if len(hits) == 1:
                    pass
                elif len(hits) > 1:
                    exact = [
                        h for h in hits
                        if h.casefold() == target.casefold()
                        or h.casefold() == f"{target.casefold()}.md"
                    ]
                    if not exact:
                        errors.append(
                            f"'{prop.name}': '{target}' matches {len(hits)} notes "
                            f"({', '.join(hits)}). Pick a specific note path to make the link unambiguous."
                        )
                else:
                    all_paths = [p for path_list in note_index.values() for p in path_list]
                    path_hits = [
                        p for p in all_paths
                        if p.casefold() == target.casefold()
                        or p.casefold() == f"{target.casefold()}.md"
                        or p.casefold().endswith(f"/{target.casefold()}")
                        or p.casefold().endswith(f"/{target.casefold()}.md")
                    ]
                    if len(path_hits) == 1:
                        pass
                    elif len(path_hits) > 1:
                        errors.append(
                            f"'{prop.name}': '{target}' matches {len(path_hits)} notes "
                            f"({', '.join(path_hits)}). Pick a specific note path to make the link unambiguous."
                        )
                    else:
                        warnings.append(
                            f"'{prop.name}': no note named '{target}' exists in this vault "
                            "yet. The link will show as unresolved in Obsidian."
                        )

    roundtrip = roundtrip_check(frontmatter, mapping)
    return {
        "frontmatter": frontmatter,
        "yaml": render_yaml(mapping),
        "mapping_preview": canonical_from_mapping(mapping),
        "errors": errors,
        "warnings": warnings,
        "roundtrip": roundtrip,
        "valid": not errors and roundtrip["matches"],
        "contains_body": False,
    }
