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


def canonical_scope_key(scope_data: dict[str, Any] | str | None) -> str:
    """Canonicalize scope keys to eliminate ambiguity between folder order and single-note paths (REQ-044)."""
    if not scope_data or scope_data == "default":
        return "default"
    if isinstance(scope_data, str):
        s = scope_data.strip()
        if s.startswith("note:") or s == "entire_vault":
            return s
        if s.startswith("folders:"):
            inner = s[len("folders:"):]
            folders = sorted(p.strip().replace("\\", "/").strip("/") for p in inner.split(",") if p.strip())
            return "folders:" + ",".join(folders)
        if "," in s:
            folders = sorted(p.strip().replace("\\", "/").strip("/") for p in s.split(",") if p.strip())
            return "folders:" + ",".join(folders)
        return s
    mode = str(scope_data.get("mode") or "").strip()
    if mode == "entire_vault":
        return "entire_vault"
    if mode == "single_note":
        np = str(scope_data.get("note_path") or "").strip().replace("\\", "/").strip("/")
        return f"note:{np}" if np else "default"
    if mode == "folders":
        folders = sorted(str(f).strip().replace("\\", "/").strip("/") for f in scope_data.get("folders", []) if f)
        return "folders:" + ",".join(folders) if folders else "default"
    return "default"


class ScopeGovernanceStore:
    def __init__(self) -> None:
        self.storage = EntityStorage("scope_assignments", "scope_profiles/scope_expected_schemas.json")

    def list_assignments(self) -> dict[str, dict[str, Any]]:
        record = self.storage.load()
        return dict(record.get("data") or {})

    def get_assignment(self, scope_key: str | dict[str, Any]) -> ScopeAssignment | None:
        ckey = canonical_scope_key(scope_key)
        data = self.list_assignments()
        raw = data.get(ckey)
        if not raw:
            return None
        return ScopeAssignment(
            scope_key=raw["scope_key"],
            schema_id=raw["schema_id"],
            schema_name=raw.get("schema_name", ""),
            assigned_at=raw.get("assigned_at", ""),
        )

    def assign_schema(self, scope_key: str | dict[str, Any], schema_id: str, schema_name: str, expected_revision: int | None = None) -> dict[str, Any]:
        from datetime import datetime, timezone
        ckey = canonical_scope_key(scope_key)
        data = self.list_assignments()
        now = datetime.now(timezone.utc).isoformat()
        assignment = ScopeAssignment(
            scope_key=ckey,
            schema_id=schema_id,
            schema_name=schema_name,
            assigned_at=now,
        )
        data[ckey] = assignment.to_dict()
        res = self.storage.save(data, expected_revision)
        res["assignment"] = assignment.to_dict()
        return res

    def unassign_schema(self, scope_key: str | dict[str, Any], expected_revision: int | None = None) -> bool:
        ckey = canonical_scope_key(scope_key)
        data = self.list_assignments()
        if ckey in data:
            del data[ckey]
            self.storage.save(data, expected_revision)
            return True
        return False



SCOPE_GOVERNANCE_STORE = ScopeGovernanceStore()
