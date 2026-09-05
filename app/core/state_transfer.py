"""State transfer and navigation context model for M016.

Ensures explicit cross-module state transfer (REQ-040, DEC-031):
- Navigating across modules carries intent, schema, finding, and proposal payloads.
- Consumable single-use semantics prevents stale state replay.
- Fail-closed validation for all serialized navigation contexts.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class NavigationIntent(str, enum.Enum):
    NAVIGATE = "navigate"
    RECONCILE = "reconcile"
    INSPECT_FINDING = "inspect_finding"
    APPLY_SCHEMA = "apply_schema"
    EDIT_CANDIDATE = "edit_candidate"
    NEW_FRONTMATTER = "new_frontmatter"
    DRIFT_VIEW = "drift_view"
    UNKNOWN = "unknown"

    @classmethod
    def from_str(cls, val: str | None) -> NavigationIntent:
        if not val:
            return cls.NAVIGATE
        try:
            return cls(str(val).lower())
        except ValueError:
            return cls.UNKNOWN


class StateTransferError(ValueError):
    pass


@dataclass
class NavigationContext:
    target_module: str
    intent: NavigationIntent = NavigationIntent.NAVIGATE
    schema_id: str | None = None
    schema_name: str | None = None
    schema_version: str | None = None
    note_path: str | None = None
    finding_id: str | None = None
    finding_type: str | None = None
    property_key: str | None = None
    expected_schema_id: str | None = None
    properties: list[dict[str, Any]] = field(default_factory=list)
    filter_scope: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_module": self.target_module,
            "intent": self.intent.value,
            "schema_id": self.schema_id,
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "note_path": self.note_path,
            "finding_id": self.finding_id,
            "finding_type": self.finding_type,
            "property_key": self.property_key,
            "expected_schema_id": self.expected_schema_id,
            "properties": self.properties,
            "filter_scope": self.filter_scope,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NavigationContext:
        if not isinstance(data, dict):
            raise StateTransferError("NavigationContext payload must be a dictionary.")
        target = data.get("target_module")
        if not target or not isinstance(target, str):
            raise StateTransferError("Missing or invalid 'target_module' in NavigationContext.")
        
        intent_raw = data.get("intent")
        intent = NavigationIntent.from_str(intent_raw)
        if intent == NavigationIntent.UNKNOWN and intent_raw:
            raise StateTransferError(f"Unknown navigation intent '{intent_raw}'.")

        return cls(
            target_module=target.strip(),
            intent=intent,
            schema_id=data.get("schema_id"),
            schema_name=data.get("schema_name"),
            schema_version=data.get("schema_version"),
            note_path=data.get("note_path"),
            finding_id=data.get("finding_id"),
            finding_type=data.get("finding_type"),
            property_key=data.get("property_key"),
            expected_schema_id=data.get("expected_schema_id"),
            properties=list(data.get("properties") or []),
            filter_scope=data.get("filter_scope"),
            extra=dict(data.get("extra") or {}),
        )


def validate_navigation_payload(payload: Any) -> dict[str, Any]:
    """Validate a navigation context payload honestly, returning a diagnostic report."""
    if not isinstance(payload, dict):
        return {"valid": False, "error": "Payload must be a JSON dictionary.", "context": None}
    try:
        ctx = NavigationContext.from_dict(payload)
        return {"valid": True, "error": None, "context": ctx.to_dict()}
    except StateTransferError as exc:
        return {"valid": False, "error": str(exc), "context": None}


class StateTransferEngine:
    """In-memory queue for cross-module state transfer."""

    def __init__(self) -> None:
        self._pending: dict[str, NavigationContext] = {}

    def set_pending(self, context: NavigationContext) -> None:
        self._pending[context.target_module] = context

    def has_pending(self, target_module: str) -> bool:
        return target_module in self._pending

    def peek_pending(self, target_module: str) -> NavigationContext | None:
        return self._pending.get(target_module)

    def consume_pending(self, target_module: str) -> NavigationContext | None:
        return self._pending.pop(target_module, None)

    def clear_all(self) -> None:
        self._pending.clear()
