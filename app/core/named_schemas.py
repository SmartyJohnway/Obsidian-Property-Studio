"""Named Schema Library and Governance CRUD (REQ-042, DEC-030).

Allows saving, versioning, updating, and referencing reusable named schemas
outside the Vault.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .model import StorageType, UIControl
from ..storage import EntityStorage


@dataclass
class NamedSchemaProperty:
    name: str
    storage_type: str = "text"
    ui_control: str = "plain"
    required: bool = False
    description: str = ""
    allowed_values: list[str] | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "storage_type": self.storage_type,
            "ui_control": self.ui_control,
            "required": self.required,
            "description": self.description,
            "allowed_values": self.allowed_values,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NamedSchemaProperty:
        name = str(data.get("name") or "").strip()
        if not name:
            raise ValueError("Property name must be non-empty.")
        return cls(
            name=name,
            storage_type=str(data.get("storage_type") or "text"),
            ui_control=str(data.get("ui_control") or "plain"),
            required=bool(data.get("required", False)),
            description=str(data.get("description") or ""),
            allowed_values=list(data.get("allowed_values")) if data.get("allowed_values") is not None else None,
            reason=str(data.get("reason") or ""),
        )


@dataclass
class NamedSchema:
    id: str
    name: str
    version: str = "1.0"
    description: str = ""
    properties: list[NamedSchemaProperty] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    target_scope: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "properties": [p.to_dict() if hasattr(p, "to_dict") else p for p in self.properties],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "target_scope": self.target_scope,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NamedSchema:
        schema_id = str(data.get("id") or "").strip()
        name = str(data.get("name") or data.get("schema_name") or "").strip()
        if not schema_id:
            schema_id = "schema_" + uuid.uuid4().hex[:8]
        if not name:
            raise ValueError("Schema name is required.")

        props = [NamedSchemaProperty.from_dict(p) for p in (data.get("properties") or [])]
        return cls(
            id=schema_id,
            name=name,
            version=str(data.get("version") or "1.0"),
            description=str(data.get("description") or ""),
            properties=props,
            created_at=str(data.get("created_at") or datetime.now(timezone.utc).isoformat()),
            updated_at=str(data.get("updated_at") or datetime.now(timezone.utc).isoformat()),
            target_scope=data.get("target_scope"),
        )


class NamedSchemaLibrary:
    """Manages Named Schemas persisted in app-local storage."""

    def __init__(self) -> None:
        self.storage = EntityStorage("named_schemas", "schemas/named_schemas.json")

    def list_schemas(self) -> list[dict[str, Any]]:
        record = self.storage.load()
        data = record.get("data") or {}
        schemas = [NamedSchema.from_dict(s).to_dict() for s in data.values()]
        return sorted(schemas, key=lambda s: s["name"].lower())

    def get_schema(self, schema_id: str) -> NamedSchema | None:
        record = self.storage.load()
        data = record.get("data") or {}
        raw = data.get(schema_id)
        return NamedSchema.from_dict(raw) if raw else None

    def create_schema(self, schema_data: dict[str, Any], expected_revision: int | None = None) -> dict[str, Any]:
        schema = NamedSchema.from_dict(schema_data)
        record = self.storage.load()
        data = dict(record.get("data") or {})
        
        # Check duplicate name with same version
        for existing in data.values():
            if existing.get("name") == schema.name and existing.get("version") == schema.version and existing.get("id") != schema.id:
                raise ValueError(f"A schema named '{schema.name}' (v{schema.version}) already exists.")

        data[schema.id] = schema.to_dict()
        res = self.storage.save(data, expected_revision)
        res["schema"] = schema.to_dict()
        return res

    def save_schema(self, schema_data: dict[str, Any], expected_revision: int | None = None) -> dict[str, Any]:
        schema = NamedSchema.from_dict(schema_data)
        record = self.storage.load()
        data = dict(record.get("data") or {})
        data[schema.id] = schema.to_dict()
        res = self.storage.save(data, expected_revision)
        res["schema"] = schema.to_dict()
        return res

    def update_schema(self, schema_id: str, schema_data: dict[str, Any], expected_revision: int | None = None) -> dict[str, Any]:
        schema_data["id"] = schema_id
        schema_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        schema = NamedSchema.from_dict(schema_data)
        record = self.storage.load()
        data = dict(record.get("data") or {})

        if schema_id not in data:
            raise ValueError(f"Schema '{schema_id}' not found.")

        data[schema_id] = schema.to_dict()
        res = self.storage.save(data, expected_revision)
        res["schema"] = schema.to_dict()
        return res

    def delete_schema(self, schema_id: str, expected_revision: int | None = None) -> bool:
        record = self.storage.load()
        data = dict(record.get("data") or {})
        if schema_id in data:
            del data[schema_id]
            self.storage.save(data, expected_revision)
            return True
        return False


NAMED_SCHEMA_LIBRARY = NamedSchemaLibrary()
