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

from app.storage.local_storage import EntityStorage

SAVED_CHECKS_FORMAT_VERSION = "1.1.0"


class CorruptedSavedChecksError(ValueError):
    """Raised when persisted or legacy saved relationship checks are corrupt (REQ-052)."""

    def __init__(self, message: str, raw_payload: Any = None) -> None:
        super().__init__(message)
        self.raw_payload = raw_payload


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
        if not isinstance(data, dict):
            raise ValueError("SavedCheck data must be a dictionary.")
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
    """Manager for saved checks with app-local persistence (REQ-033, REQ-051, REQ-052)."""

    def __init__(
        self,
        initial_checks: list[SavedCheck] | None = None,
        storage: EntityStorage | None = None,
        persistent: bool = False,
    ):
        self._checks: dict[str, SavedCheck] = {}
        self.storage = storage or (
            EntityStorage("saved_checks", "saved_checks/saved_relationship_checks.json")
            if persistent
            else None
        )

        if initial_checks is not None:
            for c in initial_checks:
                self._checks[c.id] = c
        elif self.storage is not None:
            self._load_from_storage()

    def _load_from_storage(self) -> None:
        if self.storage is None:
            return
        payload = self.storage.load()
        raw_checks = payload.get("data")
        if raw_checks is None or raw_checks == {}:
            return
        if isinstance(raw_checks, dict):
            raw_checks = raw_checks.get("checks", [])
        if not isinstance(raw_checks, list):
            raise CorruptedSavedChecksError(
                "Saved checks storage payload is not a valid list.",
                raw_payload=raw_checks,
            )
        for index, item in enumerate(raw_checks):
            try:
                chk = SavedCheck.from_dict(item)
                self._checks[chk.id] = chk
            except Exception as exc:
                raise CorruptedSavedChecksError(
                    f"Corrupted item in saved checks storage at index {index}: {exc}",
                    raw_payload=item,
                ) from exc

    def _sync_to_storage(self) -> None:
        if self.storage is not None:
            data = [c.to_dict() for c in self.list_checks()]
            self.storage.save(data)

    def list_checks(self) -> list[SavedCheck]:
        return sorted(self._checks.values(), key=lambda c: c.created_at)

    def get_check(self, check_id: str) -> SavedCheck | None:
        return self._checks.get(check_id)

    def save_check(self, check: SavedCheck) -> None:
        self._checks[check.id] = check
        self._sync_to_storage()

    def delete_check(self, check_id: str) -> bool:
        if check_id in self._checks:
            del self._checks[check_id]
            self._sync_to_storage()
            return True
        return False

    def clear(self) -> None:
        self._checks.clear()
        self._sync_to_storage()

    def replace_all(self, checks: list[SavedCheck]) -> None:
        """Atomically replace in-memory checks and persist in a single operation."""
        self._checks = {c.id: c for c in checks}
        self._sync_to_storage()

    def reload(self) -> None:
        """Reload saved checks from underlying storage into memory (rehydration)."""
        self._checks.clear()
        self._load_from_storage()

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
        except Exception as exc:
            raise CorruptedSavedChecksError(
                f"Malformed JSON in saved checks payload: {exc}",
                raw_payload=json_str,
            ) from exc

        if not isinstance(data, dict):
            raise CorruptedSavedChecksError(
                "Saved checks JSON root must be an object.",
                raw_payload=data,
            )

        raw_list = data.get("checks")
        if not isinstance(raw_list, list):
            raise CorruptedSavedChecksError(
                "Saved checks payload missing 'checks' list.",
                raw_payload=data,
            )

        checks = []
        for index, item in enumerate(raw_list):
            try:
                checks.append(SavedCheck.from_dict(item))
            except Exception as exc:
                raise CorruptedSavedChecksError(
                    f"Malformed check at index {index}: {exc}",
                    raw_payload=item,
                ) from exc

        return SavedChecksStore(initial_checks=checks, persistent=False)

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
