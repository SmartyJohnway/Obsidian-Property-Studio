"""Scope Expected Schema Governance Layer (REQ-044, DEC-030).

Allows associating a designated scope with an Expected Schema from the
Named Schema Library, persisted in app-local storage outside the Vault.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.storage import EntityStorage


@dataclass
class ScopeAssignment:
    scope_key: str
    schema_id: str
    schema_name: str
    assigned_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_key": self.scope_key,
            "schema_id": self.schema_id,
            "schema_name": self.schema_name,
            "assigned_at": self.assigned_at,
        }


class ScopeGovernanceStore:
    def __init__(self) -> None:
        self.storage = EntityStorage("scope_assignments", "governance/scope_assignments.json")

    def list_assignments(self) -> dict[str, dict[str, Any]]:
        record = self.storage.load()
        return dict(record.get("data") or {})

    def get_assignment(self, scope_key: str) -> ScopeAssignment | None:
        data = self.list_assignments()
        raw = data.get(scope_key)
        if not raw:
            return None
        return ScopeAssignment(
            scope_key=raw["scope_key"],
            schema_id=raw["schema_id"],
            schema_name=raw.get("schema_name", ""),
            assigned_at=raw.get("assigned_at", ""),
        )

    def assign_schema(self, scope_key: str, schema_id: str, schema_name: str, expected_revision: int | None = None) -> dict[str, Any]:
        from datetime import datetime, timezone
        data = self.list_assignments()
        now = datetime.now(timezone.utc).isoformat()
        assignment = ScopeAssignment(
            scope_key=scope_key,
            schema_id=schema_id,
            schema_name=schema_name,
            assigned_at=now,
        )
        data[scope_key] = assignment.to_dict()
        res = self.storage.save(data, expected_revision)
        res["assignment"] = assignment.to_dict()
        return res

    def unassign_schema(self, scope_key: str, expected_revision: int | None = None) -> bool:
        data = self.list_assignments()
        if scope_key in data:
            del data[scope_key]
            self.storage.save(data, expected_revision)
            return True
        return False


SCOPE_GOVERNANCE_STORE = ScopeGovernanceStore()
