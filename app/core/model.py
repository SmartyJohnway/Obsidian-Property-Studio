"""Canonical internal representation for Obsidian Property Studio.

REQ-004: every downstream module (discovery, health, refactor, relationship,
exports) consumes these types.  There is exactly one interpretation of a Vault,
a Note, a frontmatter Property and an observed value/type in this product.

Nothing in this module touches the filesystem for writing.  The canonical model
is deliberately serialisable and deterministic (stable ordering, no wall-clock
fields) so that repeat runs are comparable (SC-12 / OPS-AC-027).
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# --------------------------------------------------------------------------
# Storage types (SC-05) — these mirror Obsidian's frontmatter property types.
# UI controls (select / multi-select / note link) are NOT storage types; they
# are recorded separately on the schema (DEC-012, AGENTS 28.4).
# --------------------------------------------------------------------------
class StorageType(str, Enum):
    TEXT = "text"
    LIST = "list"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    DATE = "date"
    DATETIME = "datetime"
    TAGS = "tags"
    #: value present but empty (``key:`` with nothing) — compatible with anything
    EMPTY = "empty"
    #: nested mapping / structure Obsidian's property editor cannot represent
    UNSUPPORTED = "unsupported"

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.value


#: Human wording used in the UI so that a beginner never needs YAML vocabulary.
STORAGE_TYPE_LABELS: dict[str, str] = {
    "text": "Text",
    "list": "List",
    "number": "Number",
    "checkbox": "Checkbox",
    "date": "Date",
    "datetime": "Date & time",
    "tags": "Tags",
    "empty": "Empty",
    "unsupported": "Unsupported structure",
}


class UIControl(str, Enum):
    """Higher level input affordances. Each maps onto a StorageType."""

    PLAIN = "plain"
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    NOTE_LINK = "note_link"
    NOTE_LINK_LIST = "note_link_list"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


#: Documented serialization contract for every UI control (OPS-AC-009).
UI_CONTROL_SERIALIZATION: dict[str, dict[str, str]] = {
    "plain": {
        "storage_types": "text, list, number, checkbox, date, datetime, tags",
        "serializes_as": "the underlying storage type, unchanged",
        "note": "No extra constraint. The control is only an input widget.",
    },
    "single_choice": {
        "storage_types": "text, number, date, datetime",
        "serializes_as": "a single scalar value of the underlying storage type",
        "note": (
            "Select is a schema/UI constraint over a scalar value. Obsidian has "
            "no native 'select' property type; the note stores a plain scalar."
        ),
    },
    "multi_choice": {
        "storage_types": "list, tags",
        "serializes_as": "a YAML list of scalars (or a tags list)",
        "note": (
            "Multi-select is a schema/UI constraint over a list. Obsidian stores "
            "an ordinary list property."
        ),
    },
    "note_link": {
        "storage_types": "text",
        "serializes_as": '"[[Note Name]]" wiki-link inside a text property',
        "note": (
            "Note-link picker is a UI convenience that writes a link-encoded "
            "text value. It is not a separate Obsidian storage type."
        ),
    },
    "note_link_list": {
        "storage_types": "list",
        "serializes_as": 'a YAML list whose items are "[[Note Name]]" text values',
        "note": "Same as note_link, applied to each list item.",
    },
}

#: Which storage types a UI control may legally be attached to.
UI_CONTROL_ALLOWED_STORAGE: dict[str, tuple[str, ...]] = {
    "plain": ("text", "list", "number", "checkbox", "date", "datetime", "tags"),
    "single_choice": ("text", "number", "date", "datetime"),
    "multi_choice": ("list", "tags"),
    "note_link": ("text",),
    "note_link_list": ("list",),
}


class ParseStatus(str, Enum):
    """Honest parse outcome for a note (REQ-003, SC-03, OPS-AC-004)."""

    #: no frontmatter block at all — legitimately "no properties"
    NO_FRONTMATTER = "no_frontmatter"
    #: frontmatter block parsed into a mapping
    OK = "ok"
    #: frontmatter block present but empty (``---\n---``)
    EMPTY_FRONTMATTER = "empty_frontmatter"
    #: opening delimiter but the block never closes
    UNTERMINATED = "unterminated_frontmatter"
    #: YAML syntax error
    INVALID_YAML = "invalid_yaml"
    #: valid YAML but not a mapping (e.g. a list or a bare string)
    NOT_A_MAPPING = "not_a_mapping"
    #: file could not be read/decoded
    UNREADABLE = "unreadable"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


#: Statuses that mean "we could not read this note's property layer".
FAILED_PARSE_STATUSES = frozenset(
    {
        ParseStatus.UNTERMINATED,
        ParseStatus.INVALID_YAML,
        ParseStatus.NOT_A_MAPPING,
        ParseStatus.UNREADABLE,
    }
)


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


#: Confidence vocabulary. Nothing below EXACT may be auto-applied or presented
#: as a confirmed fact (Constraints 8/9/10, REQ-010).
class Confidence(str, Enum):
    EXACT = "exact"
    AMBIGUOUS = "ambiguous"
    POSSIBLE = "possible"
    UNRESOLVED = "unresolved"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


# --------------------------------------------------------------------------
# Values
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class PropertyValue:
    """One property occurrence inside one note."""

    key: str
    #: raw Python object produced by the YAML parser
    raw: Any
    storage_type: StorageType
    #: scalar values flattened to strings, in document order (for lists: items)
    scalars: tuple[str, ...] = ()
    #: value rendered exactly as it will be compared/reported
    display: str = ""

    def is_empty(self) -> bool:
        return self.storage_type is StorageType.EMPTY


@dataclass(frozen=True)
class ParseIssue:
    """A machine + human readable parsing problem. Never silently dropped."""

    note_path: str
    status: ParseStatus
    message: str
    severity: Severity = Severity.HIGH
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_path": self.note_path,
            "status": self.status.value,
            "severity": self.severity.value,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass
class Note:
    """Canonical note record. ``path`` is a vault-relative POSIX path."""

    path: str
    parse_status: ParseStatus
    properties: dict[str, PropertyValue] = field(default_factory=dict)
    #: duplicate YAML keys found in this note's frontmatter (AGENTS 29.4)
    duplicate_keys: tuple[str, ...] = ()
    issues: tuple[ParseIssue, ...] = ()
    size_bytes: int = 0

    @property
    def name(self) -> str:
        """Note name as Obsidian shows it (file stem)."""
        base = self.path.rsplit("/", 1)[-1]
        return base[:-3] if base.lower().endswith(".md") else base

    @property
    def has_properties(self) -> bool:
        return bool(self.properties)

    @property
    def parse_failed(self) -> bool:
        return self.parse_status in FAILED_PARSE_STATUSES

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "name": self.name,
            "parse_status": self.parse_status.value,
            "has_properties": self.has_properties,
            "duplicate_keys": list(self.duplicate_keys),
            "properties": {
                k: {
                    "storage_type": v.storage_type.value,
                    "display": v.display,
                    "scalars": list(v.scalars),
                }
                for k, v in sorted(self.properties.items())
            },
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class SkippedPath:
    """A path deliberately not scanned, with the reason (never silent)."""

    path: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "reason": self.reason}


@dataclass
class VaultScan:
    """The single canonical scan result consumed by every other module."""

    vault_path: str
    notes: list[Note] = field(default_factory=list)
    skipped: list[SkippedPath] = field(default_factory=list)
    issues: list[ParseIssue] = field(default_factory=list)
    #: seconds; excluded from canonical/deterministic comparisons
    scan_seconds: float = 0.0

    # ---- derived, deterministic ------------------------------------------
    @property
    def note_count(self) -> int:
        return len(self.notes)

    @property
    def notes_with_properties(self) -> int:
        return sum(1 for n in self.notes if n.has_properties)

    @property
    def notes_with_parse_failure(self) -> int:
        return sum(1 for n in self.notes if n.parse_failed)

    def note_by_path(self, path: str) -> Note | None:
        for n in self.notes:
            if n.path == path:
                return n
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "vault_path": self.vault_path,
            "note_count": self.note_count,
            "notes_with_properties": self.notes_with_properties,
            "notes_without_properties": self.note_count
            - self.notes_with_properties
            - self.notes_with_parse_failure,
            "notes_with_parse_failure": self.notes_with_parse_failure,
            "skipped_path_count": len(self.skipped),
            "issue_count": len(self.issues),
        }


# --------------------------------------------------------------------------
# Schema (design output)
# --------------------------------------------------------------------------
SCHEMA_FORMAT_VERSION = "1.0"


@dataclass
class SchemaProperty:
    name: str
    storage_type: StorageType
    ui_control: UIControl = UIControl.PLAIN
    required: bool = False
    #: why this property exists / what it lets you do (OPS-AC-008)
    reason: str = ""
    allowed_values: tuple[str, ...] | None = None
    #: provenance: "recipe:<id>", "vault:existing", "user", "proposal:<name>"
    origin: str = "user"
    confidence: float | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.name or not self.name.strip():
            errors.append("Property name must not be empty.")
        allowed = UI_CONTROL_ALLOWED_STORAGE[self.ui_control.value]
        if self.storage_type.value not in allowed:
            errors.append(
                f"UI control '{self.ui_control.value}' cannot be used with storage "
                f"type '{self.storage_type.value}' (allowed: {', '.join(allowed)})."
            )
        if self.ui_control in (UIControl.SINGLE_CHOICE, UIControl.MULTI_CHOICE):
            if not self.allowed_values:
                errors.append(
                    f"'{self.name}': a choice control requires at least one allowed value."
                )
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "storage_type": self.storage_type.value,
            "storage_type_label": STORAGE_TYPE_LABELS[self.storage_type.value],
            "ui_control": self.ui_control.value,
            "serialization": UI_CONTROL_SERIALIZATION[self.ui_control.value],
            "required": self.required,
            "reason": self.reason,
            "allowed_values": list(self.allowed_values)
            if self.allowed_values
            else None,
            "origin": self.origin,
            "confidence": self.confidence,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SchemaProperty":
        allowed = data.get("allowed_values")
        return SchemaProperty(
            name=str(data.get("name", "")),
            storage_type=StorageType(data.get("storage_type", "text")),
            ui_control=UIControl(data.get("ui_control") or "plain"),
            required=bool(data.get("required", False)),
            reason=str(data.get("reason", "") or ""),
            allowed_values=tuple(str(a) for a in allowed) if allowed else None,
            origin=str(data.get("origin", "user") or "user"),
            confidence=data.get("confidence"),
        )


@dataclass
class Schema:
    name: str
    description: str = ""
    properties: list[SchemaProperty] = field(default_factory=list)
    format_version: str = SCHEMA_FORMAT_VERSION

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.name.strip():
            errors.append("Schema name must not be empty.")
        seen: dict[str, int] = {}
        for prop in self.properties:
            errors.extend(prop.validate())
            seen[prop.name] = seen.get(prop.name, 0) + 1
        for key, count in sorted(seen.items()):
            if count > 1:
                errors.append(f"Duplicate property '{key}' defined {count} times.")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": self.format_version,
            "schema_name": self.name,
            "description": self.description,
            "properties": [p.to_dict() for p in self.properties],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Schema":
        return Schema(
            name=str(data.get("schema_name") or data.get("name") or ""),
            description=str(data.get("description", "") or ""),
            properties=[
                SchemaProperty.from_dict(p) for p in data.get("properties", []) or []
            ],
            format_version=str(data.get("format_version", SCHEMA_FORMAT_VERSION)),
        )


# --------------------------------------------------------------------------
# Findings (health / relationship / refactor share this shape, REQ-011)
# --------------------------------------------------------------------------
@dataclass
class Finding:
    id: str
    category: str
    severity: Severity
    title: str
    explanation: str
    #: what the user can do; never performed automatically
    recommendation: str = ""
    property_keys: tuple[str, ...] = ()
    affected_notes: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)
    confidence: Confidence = Confidence.EXACT

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "severity": self.severity.value,
            "title": self.title,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
            "property_keys": list(self.property_keys),
            "affected_note_count": len(self.affected_notes),
            "affected_notes": list(self.affected_notes),
            "evidence": self.evidence,
            "confidence": self.confidence.value,
        }


def iso_date(value: Any) -> str:
    """Deterministic string rendering for date/datetime scalars."""
    if isinstance(value, _dt.datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, _dt.date):
        return value.isoformat()
    return str(value)
