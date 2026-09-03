"""Saved Relationship Checks Management Engine (M009 / R03).

REQ-032 / REQ-033 / DEC-026:
1. Versioned schema for user-saved relationship checks.
2. Core engine operates in-memory; serialization to/from JSON for external storage.
3. Zero default checks or built-in ontology on startup (V11-014).
4. Round-trip serialization and execution without Vault mutations (V11-015).
5. Supports property_link and body_wikilink analysis types accurately.
6. Strictly adheres to Constraint 2 (app/core/ contains zero file-writing APIs).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .body_links import analyze_body_wikilinks
from .model import VaultScan
from .relationships import build_inbox
from .scope import ScopeSpec

SAVED_CHECKS_FORMAT_VERSION = "1.1.0"


@dataclass
class SavedCheck:
    id: str
    name: str
    notes: str = ""
    link_type: str = "property_link"  # "property_link" | "body_wikilink"
    property_name: str | None = None
    source_scope: ScopeSpec = field(default_factory=ScopeSpec)
    target_scope: ScopeSpec | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    format_version: str = SAVED_CHECKS_FORMAT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "notes": self.notes,
            "link_type": self.link_type,
            "property_name": self.property_name,
            "source_scope": self.source_scope.to_dict(),
            "target_scope": self.target_scope.to_dict() if self.target_scope else None,
            "created_at": self.created_at,
            "format_version": self.format_version,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SavedCheck":
        link_type = str(data.get("link_type", "property_link"))
        if link_type == "body":
            link_type = "body_wikilink"
        elif link_type == "property":
            link_type = "property_link"

        return SavedCheck(
            id=data.get("id") or str(uuid.uuid4()),
            name=str(data.get("name", "Untitled Check")),
            notes=str(data.get("notes", "")),
            link_type=link_type,
            property_name=data.get("property_name"),
            source_scope=ScopeSpec.from_dict(data.get("source_scope") or {}),
            target_scope=ScopeSpec.from_dict(data["target_scope"])
            if data.get("target_scope")
            else None,
            created_at=str(
                data.get("created_at") or datetime.now(timezone.utc).isoformat()
            ),
            format_version=str(
                data.get("format_version", SAVED_CHECKS_FORMAT_VERSION)
            ),
        )


class SavedChecksStore:
    """In-memory manager for saved checks (Constraint 2: pure in-memory core)."""

    def __init__(self, initial_checks: list[SavedCheck] | None = None):
        self._checks: dict[str, SavedCheck] = {}
        if initial_checks is not None:
            for c in initial_checks:
                self._checks[c.id] = c

    def list_checks(self) -> list[SavedCheck]:
        return sorted(self._checks.values(), key=lambda c: c.created_at)

    def get_check(self, check_id: str) -> SavedCheck | None:
        return self._checks.get(check_id)

    def save_check(self, check: SavedCheck) -> None:
        self._checks[check.id] = check

    def delete_check(self, check_id: str) -> bool:
        if check_id in self._checks:
            del self._checks[check_id]
            return True
        return False

    def clear(self) -> None:
        self._checks.clear()

    def to_json(self) -> str:
        data = {
            "format_version": SAVED_CHECKS_FORMAT_VERSION,
            "checks": [c.to_dict() for c in self.list_checks()],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def from_json(json_str: str) -> "SavedChecksStore":
        try:
            data = json.loads(json_str)
            checks = [SavedCheck.from_dict(item) for item in data.get("checks", [])]
            return SavedChecksStore(initial_checks=checks)
        except Exception:
            return SavedChecksStore(initial_checks=[])

    def execute_check(self, scan: VaultScan, check_id: str) -> dict[str, Any]:
        chk = self.get_check(check_id)
        if chk is None:
            raise KeyError(f"Saved check '{check_id}' not found.")

        # Accurately dispatch body_wikilink vs property_link
        if chk.link_type in ("body_wikilink", "body"):
            res = analyze_body_wikilinks(
                scan,
                source_scope=chk.source_scope,
                target_scope=chk.target_scope,
            )
        else:
            res = build_inbox(
                scan,
                property_filter=chk.property_name,
                source_scope=chk.source_scope,
                target_scope=chk.target_scope,
            )
        res["check_id"] = check_id
        res["check_name"] = chk.name
        res["executed_check"] = chk.to_dict()
        res["results"] = dict(res)
        return res
