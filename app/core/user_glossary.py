"""User-editable Property Glossary with 3-tier Precedence (REQ-041, DEC-033).

Precedence hierarchy:
1. System Built-in Glossary (app/core/property_glossary.py)
2. User Override (glossary/user_glossary.json)
3. Observed Vault Facts (inventory scan)

Core Safety Invariant:
Canonical YAML Property Keys are IMMUTABLE. Labels/guidance may be customized,
but the underlying key is never translated or rewritten.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .property_glossary import PropertyGlossaryEntry, get_property_glossary_entry
from ..storage import EntityStorage


@dataclass
class UserGlossaryOverride:
    canonical_key: str
    label_zh: str | None = None
    label_en: str | None = None
    description_zh: str | None = None
    description_en: str | None = None
    guidance: str | None = None
    examples: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    category: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_key": self.canonical_key,
            "label_zh": self.label_zh,
            "label_en": self.label_en,
            "description_zh": self.description_zh,
            "description_en": self.description_en,
            "guidance": self.guidance,
            "examples": self.examples,
            "aliases": self.aliases,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserGlossaryOverride:
        key = str(data.get("canonical_key") or "").strip()
        if not key:
            raise ValueError("canonical_key is required for UserGlossaryOverride.")
        return cls(
            canonical_key=key,
            label_zh=data.get("label_zh"),
            label_en=data.get("label_en"),
            description_zh=data.get("description_zh"),
            description_en=data.get("description_en"),
            guidance=data.get("guidance"),
            examples=list(data.get("examples") or []),
            aliases=list(data.get("aliases") or []),
            category=data.get("category"),
        )


class UserGlossaryStore:
    """Manages user glossary overrides persisted in app-local storage."""

    def __init__(self) -> None:
        self.storage = EntityStorage("user_glossary", "glossary/user_glossary.json")

    def list_overrides(self) -> dict[str, dict[str, Any]]:
        record = self.storage.load()
        return dict(record.get("data") or {})

    def get_override(self, key: str) -> UserGlossaryOverride | None:
        overrides = self.list_overrides()
        raw = overrides.get(key)
        return UserGlossaryOverride.from_dict(raw) if raw else None

    def save_override(self, override: UserGlossaryOverride, expected_revision: int | None = None) -> dict[str, Any]:
        overrides = self.list_overrides()
        overrides[override.canonical_key] = override.to_dict()
        return self.storage.save(overrides, expected_revision)

    def delete_override(self, key: str, expected_revision: int | None = None) -> bool:
        overrides = self.list_overrides()
        if key in overrides:
            del overrides[key]
            self.storage.save(overrides, expected_revision)
            return True
        return False

    def resolve_property(self, key: str) -> dict[str, Any]:
        """Resolve property guidance honoring the 3-tier precedence."""
        builtin = get_property_glossary_entry(key)
        override = self.get_override(key)

        if not builtin and not override:
            return {
                "canonical_key": key,
                "source": "vault_facts_only",
                "is_known": False,
                "label_zh": key,
                "label_en": key,
                "description_zh": "",
                "description_en": "",
                "guidance": "",
                "examples": [],
                "aliases": [],
                "category": "custom",
            }

        # Base from builtin if exists
        base_dict = builtin.to_dict() if builtin else {
            "canonical_key": key,
            "label_zh": key,
            "label_en": key,
            "description_zh": "",
            "description_en": "",
            "typical_storage_type": "text",
            "typical_control": "plain",
            "allowed_values": [],
            "examples": [],
            "aliases": [],
            "guidance_zh": "",
            "guidance_en": "",
            "category": "custom",
        }

        if override:
            if override.label_zh:
                base_dict["label_zh"] = override.label_zh
            if override.label_en:
                base_dict["label_en"] = override.label_en
            if override.description_zh:
                base_dict["description_zh"] = override.description_zh
            if override.description_en:
                base_dict["description_en"] = override.description_en
            if override.guidance:
                base_dict["guidance_zh"] = override.guidance
                base_dict["guidance_en"] = override.guidance
            if override.examples:
                base_dict["examples"] = override.examples
            if override.aliases:
                base_dict["aliases"] = override.aliases
            if override.category:
                base_dict["category"] = override.category

            base_dict["source"] = "user_override"
            base_dict["is_known"] = True
        else:
            base_dict["source"] = "builtin"
            base_dict["is_known"] = True

        return base_dict


USER_GLOSSARY_STORE = UserGlossaryStore()
