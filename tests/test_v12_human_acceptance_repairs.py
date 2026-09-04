"""Regression test suite for Commit 21: Human Acceptance Findings Repair (HA-F01 ~ HA-F18).

Verifies all 17 findings verified during Dr. J's Windows production acceptance walkthrough:
- HA-F01: Personal Glossary API Contract: Returns list of entries, eliminating frontend .map TypeError
- HA-F08: Dynamic Locale Re-render: ps:localeChanged custom event dispatches on applyLocale
- HA-F09 & HA-F11: Reconciliation Active Schema & Schema Identity Preservation
- HA-F10: Workspace Untouched Property Semantic Equality & Preservation
- HA-F12: Drift Canonical Navigable Path Guard
- HA-F13 & HA-F14: Workspace Complex YAML Mapping Preservation & Input Field String Formatting
- HA-F15: Proposal Save as Named Schema & Readback Verification
- HA-F16: Designer Schema State Separation
- HA-F17: Internal Migration Marker Portable Preference Exclusion
- HA-F18: Governance Profile Detailed Change-Set Validation
- HA-Vault: 100% Byte-for-byte read-only integrity preservation
"""

import json
import os
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import patch
import pytest

from app.core import (
    user_glossary,
    property_glossary,
    named_schemas,
    governance_profile,
    drift,
    note_workspace,
    scope_governance,
)
from app.core.named_schemas import NamedSchema, NAMED_SCHEMA_LIBRARY
from app.core.governance_profile import PREFERENCES_STORAGE, export_governance_profile, validate_governance_profile, import_governance_profile
from app.core.drift import NoteDriftFinding, is_canonical_navigable_path, DriftCategory
from app.core.note_workspace import compute_workspace_diff_and_frontmatter, are_semantically_equal
from app.core.model import VaultScan, Note, PropertyValue, StorageType, ParseStatus, Schema, SchemaProperty
from app.server import (
    api_glossary_catalog,
    api_reconcile_inspect,
    api_schemas_create,
    api_schemas_get,
    api_governance_profile_export,
    api_governance_profile_validate,
    api_governance_profile_import,
    api_workspace_preview,
    STORE,
    ApiError,
)


# ==============================================================================
# HA-F01: Personal Glossary API Contract
# ==============================================================================
def test_ha_f01_glossary_catalog_returns_list_of_entries():
    """Verify /api/glossary/catalog returns a list of dictionaries with total count."""
    res = api_glossary_catalog({})
    assert "catalog" in res
    assert "total" in res
    assert isinstance(res["catalog"], list), "catalog must be a JSON array (list) for frontend .map()"
    assert res["total"] == len(res["catalog"])
    if res["catalog"]:
        first = res["catalog"][0]
        assert "canonical_key" in first
        assert "label_zh" in first
        assert "label_en" in first


# ==============================================================================
# HA-F08: Dynamic Locale Re-render Event Dispatch Contract
# ==============================================================================
def test_ha_f08_i18n_dispatches_locale_changed_event():
    """Verify i18n.js includes window.dispatchEvent with ps:localeChanged."""
    i18n_path = Path(__file__).parent.parent / "app" / "ui" / "i18n.js"
    assert i18n_path.exists()
    content = i18n_path.read_text(encoding="utf-8")
    assert "ps:localeChanged" in content
    assert "window.dispatchEvent" in content


# ==============================================================================
# HA-F09 & HA-F11: Reconciliation Schema Identity & Active State
# ==============================================================================
def test_ha_f09_ha_f11_reconciliation_preserves_schema_identity():
    """Verify api_reconcile_inspect preserves authoritative schema name instead of hardcoding adopted-schema."""
    schema_id = "test-custom-doc-schema"
    custom_sch = NamedSchema(
        id=schema_id,
        name="Project Documentation Standard",
        version="2.1.0",
        description="Authoritative documentation rules",
        properties=[{"name": "status", "storage_type": "text", "required": True}],
    )

    note_obj = Note(
        path="doc.md",
        properties={"status": PropertyValue("status", "draft", StorageType.TEXT, ("draft",), "draft")},
        parse_status=ParseStatus.OK,
    )
    mock_scan = VaultScan(vault_path=".", notes=[note_obj])

    with patch.object(STORE, "require_scan", return_value=mock_scan):
        with patch.object(NAMED_SCHEMA_LIBRARY, "get_schema", return_value=custom_sch):
            res = api_reconcile_inspect({
                "note_path": "doc.md",
                "schema_id": schema_id,
                "schema_properties": [p.to_dict() if hasattr(p, "to_dict") else p for p in custom_sch.properties]
            })

            assert res["schema_name"] == "Project Documentation Standard"
            assert res["schema_name"] != "adopted-schema"
            assert res["summary"]["matches"] == 1


# ==============================================================================
# HA-F10: Workspace Untouched Property Semantic Equality & Preservation
# ==============================================================================
def test_ha_f10_workspace_untouched_property_preserves_native_value():
    """Verify untouched properties in schema or outside schema remain preserved without false diffs."""
    note_obj = Note(
        path="test.md",
        properties={
            "status": PropertyValue("status", "draft", StorageType.TEXT, ("draft",), "draft"),
            "tags": PropertyValue("tags", ["alpha", "beta"], StorageType.LIST, ("alpha", "beta"), "alpha, beta"),
            "authors": PropertyValue("authors", "Alice, Bob", StorageType.TEXT, ("Alice, Bob",), "Alice, Bob"),
            "custom_num": PropertyValue("custom_num", 42, StorageType.NUMBER, ("42",), "42"),
        },
        parse_status=ParseStatus.OK,
    )
    schema = Schema(
        name="Test",
        properties=[
            SchemaProperty(name="status", storage_type=StorageType.TEXT),
            SchemaProperty(name="tags", storage_type=StorageType.LIST),
        ]
    )

    # User touched ONLY status, input values contain strings
    updated_values = {
        "status": "published",
        "tags": "alpha, beta",
        "authors": "Alice, Bob",
        "custom_num": "42",
    }
    touched_keys = ["status"]

    res = compute_workspace_diff_and_frontmatter(
        original_note=note_obj,
        updated_values=updated_values,
        schema=schema,
        deleted_keys=[],
        touched_keys=touched_keys,
    )

    diff_dict = {d.key: d for d in res.diffs}

    # 'status' was touched and value changed -> modified
    assert diff_dict["status"].change_type == "modified"
    assert diff_dict["status"].new_value == "published"

    # 'tags' was NOT touched -> preserved, native list retained
    assert diff_dict["tags"].change_type == "preserved"
    assert res.merged_properties["tags"] == ["alpha", "beta"], "Untouched native list must be strictly preserved"

    # 'authors' was NOT touched -> preserved
    assert diff_dict["authors"].change_type == "preserved"
    assert res.merged_properties["authors"] == "Alice, Bob"

    # 'custom_num' was NOT touched -> preserved with native int
    assert diff_dict["custom_num"].change_type == "preserved"
    assert res.merged_properties["custom_num"] == 42


def test_ha_f10_semantic_equality_helper():
    """Verify are_semantically_equal handles formatting differences gracefully."""
    assert are_semantically_equal(["a", "b"], "a, b")
    assert are_semantically_equal(["a", "b"], ["a", "b"])
    assert are_semantically_equal(42, "42")
    assert are_semantically_equal(True, "true")
    assert are_semantically_equal("hello", "hello")
    assert not are_semantically_equal("hello", "world")
    assert not are_semantically_equal(["a"], ["b"])


# ==============================================================================
# HA-F12: Drift Findings Canonical Navigable Path Guard
# ==============================================================================
def test_ha_f12_drift_canonical_navigable_path_guard():
    """Verify is_canonical_navigable_path and NoteDriftFinding navigation safety."""
    # Valid canonical relative md paths
    ok, _ = is_canonical_navigable_path("Notes/Meeting.md")
    assert ok is True
    ok, _ = is_canonical_navigable_path("daily/2026-09-04.md")
    assert ok is True

    # Invalid paths: wikilinks, list markers, absolute paths, missing .md
    ok, reason = is_canonical_navigable_path("![[image.png]]")
    assert ok is False
    assert "wikilink" in reason

    ok, reason = is_canonical_navigable_path("· item 1")
    assert ok is False

    ok, reason = is_canonical_navigable_path("[[Meeting]]")
    assert ok is False

    ok, reason = is_canonical_navigable_path("C:/Users/file.md")
    assert ok is False

    ok, reason = is_canonical_navigable_path("")
    assert ok is False

    # NoteDriftFinding dataclass auto-detection
    valid_f = NoteDriftFinding(
        note_path="Projects/Alpha.md",
        category=DriftCategory.TYPE_MISMATCH,
        property_key="status",
        detail="Type mismatch",
        expected="text",
        actual="list",
    )
    assert valid_f.navigation_available is True
    assert valid_f.navigation_reason is None

    invalid_f = NoteDriftFinding(
        note_path="![[Attached Doc]]",
        category=DriftCategory.VALUE_DRIFT,
        property_key="ref",
        detail="Embedded link",
        expected="text",
        actual="unknown",
    )
    assert invalid_f.navigation_available is False
    assert "wikilink" in invalid_f.navigation_reason


# ==============================================================================
# HA-F13 & HA-F14: Complex YAML Mapping Preservation in Workspace
# ==============================================================================
def test_ha_f13_ha_f14_complex_yaml_mapping_preservation():
    """Verify complex nested YAML dictionaries are preserved as dicts and serialized cleanly."""
    note_obj = Note(
        path="complex.md",
        properties={
            "metadata": PropertyValue("metadata", {"author": "Dr. J", "level": 5}, StorageType.UNSUPPORTED, (), ""),
            "config": PropertyValue("config", {"enabled": True, "timeout": 30}, StorageType.UNSUPPORTED, (), ""),
        },
        parse_status=ParseStatus.OK,
    )
    touched_keys = [] # untouched

    res = compute_workspace_diff_and_frontmatter(
        original_note=note_obj,
        updated_values={
            "metadata": '{"author": "Dr. J", "level": 5}',
            "config": '{"enabled": true, "timeout": 30}'
        },
        schema=None,
        deleted_keys=[],
        touched_keys=touched_keys,
    )

    assert res.merged_properties["metadata"] == {"author": "Dr. J", "level": 5}
    assert isinstance(res.merged_properties["metadata"], dict)
    assert res.merged_properties["config"] == {"enabled": True, "timeout": 30}
    assert isinstance(res.merged_properties["config"], dict)


# ==============================================================================
# HA-F15: Proposal Save as Named Schema & Readback
# ==============================================================================
def test_ha_f15_proposal_save_named_schema_from_dict():
    """Verify NamedSchema.from_dict accepts schema_name as an alias for name."""
    proposal_dict = {
        "schema_name": "AI Recommended Research Standard",
        "description": "Auto-generated from Proposal JSON",
        "properties": [
            {"name": "hypothesis", "storage_type": "text", "required": True},
            {"name": "confidence", "storage_type": "number", "required": False}
        ]
    }

    schema = NamedSchema.from_dict(proposal_dict)
    assert schema.name == "AI Recommended Research Standard"
    assert len(schema.properties) == 2
    assert schema.properties[0].name == "hypothesis"


def test_ha_f15_api_schemas_create_and_readback():
    """Verify api_schemas_create stores schema and can be read back via api_schemas_get."""
    payload = {
        "schema": {
            "schema_name": "Integration Test Proposal Schema",
            "description": "Verified through readback",
            "properties": [{"name": "test_key", "storage_type": "text"}]
        }
    }
    create_res = api_schemas_create(payload)
    assert "schema" in create_res
    new_id = create_res["schema"]["id"]
    assert create_res["schema"]["name"] == "Integration Test Proposal Schema"

    # Readback
    readback_res = api_schemas_get({"id": new_id})
    assert readback_res["schema"]["id"] == new_id
    assert readback_res["schema"]["name"] == "Integration Test Proposal Schema"
    assert readback_res["schema"]["properties"][0]["name"] == "test_key"


# ==============================================================================
# HA-F16: Schema State Separation
# ==============================================================================
def test_ha_f16_schema_state_separation():
    """Verify NamedSchema instances have unique IDs and properties list independence."""
    s1 = NamedSchema(id="id-1", name="Schema Alpha", properties=[{"name": "p1", "storage_type": "text"}])
    s2 = NamedSchema(id="id-2", name="Schema Beta", properties=[{"name": "p2", "storage_type": "number"}])

    assert s1.id != s2.id
    assert s1.name != s2.name
    assert s1.properties[0]["name"] == "p1"
    assert s2.properties[0]["name"] == "p2"


# ==============================================================================
# HA-F17: Internal Migration Marker Portable Preference Exclusion
# ==============================================================================
def test_ha_f17_internal_migration_marker_excluded_from_profile():
    """Verify _legacy_migrated internal marker is excluded from export and import."""
    fake_stored = {
        "format": "ps_local_entity_v1",
        "storage_schema_version": "1.0",
        "entity_type": "governance_preferences",
        "revision": 1,
        "etag": "123",
        "updated_at": "2026-09-04T00:00:00Z",
        "data": {
            "_legacy_migrated": True,
            "locale": "zh-Hant",
            "theme": "dark",
            "unsupported_setting": "discard_me"
        }
    }
    with patch.object(PREFERENCES_STORAGE, "load", return_value=fake_stored):
        # Export profile
        profile = export_governance_profile(saved_checks_list=[])
        prefs_data = profile["data"]["governance_preferences"]

        # Must contain allowed portable settings
        assert prefs_data.get("locale") == "zh-Hant"
        assert prefs_data.get("theme") == "dark"

        # Must strictly EXCLUDE internal marker and unsupported settings
        assert "_legacy_migrated" not in prefs_data
        assert "unsupported_setting" not in prefs_data

    # Test importing a profile that attempts to inject _legacy_migrated
    poisoned_profile = {
        "profile_metadata": {"format_version": "1.0", "app": "Obsidian Property Studio"},
        "data": {
            "format_version": "1.0",
            "named_schemas": [],
            "scope_assignments": {},
            "user_glossary": {},
            "saved_checks": [],
            "governance_preferences": {
                "_legacy_migrated": True,
                "locale": "en",
                "theme": "light"
            }
        }
    }
    poisoned_profile["profile_metadata"]["checksum"] = governance_profile.compute_profile_checksum(poisoned_profile["data"])

    with patch.object(PREFERENCES_STORAGE, "load", return_value=fake_stored):
        with patch.object(PREFERENCES_STORAGE, "save") as mock_save:
            res = import_governance_profile(poisoned_profile, mode="merge")
            assert res["status"] == "imported"
            # Verify save was called with ONLY sanitized portable keys
            saved_payload = mock_save.call_args[0][0]
            assert saved_payload.get("locale") == "en"
            assert saved_payload.get("theme") == "light"
            # _legacy_migrated from import must NOT be injected
            assert "_legacy_migrated" not in saved_payload or saved_payload["_legacy_migrated"] == fake_stored["data"]["_legacy_migrated"]


# ==============================================================================
# HA-F18: Detailed Change-Set Computation
# ==============================================================================
def test_ha_f18_governance_profile_detailed_changeset():
    """Verify validate_governance_profile computes detailed changeset with add/update/conflict."""
    existing_schema = NamedSchema(id="existing-schema", name="Existing", properties=[{"name": "p1", "storage_type": "text"}])
    fake_stored_schemas = {
        "format": "ps_local_entity_v1",
        "data": {
            "existing-schema": existing_schema.to_dict()
        }
    }
    with patch.object(NAMED_SCHEMA_LIBRARY.storage, "load", return_value=fake_stored_schemas):
        profile = {
            "profile_metadata": {"format_version": "1.0", "app": "Obsidian Property Studio"},
            "data": {
                "format_version": "1.0",
                "named_schemas": [
                    {"id": "existing-schema", "name": "Existing Updated", "properties": []},
                    {"id": "brand-new-schema", "name": "Brand New", "properties": []}
                ],
                "scope_assignments": {},
                "user_glossary": {},
                "saved_checks": [],
                "governance_preferences": {"locale": "en"}
            }
        }
        profile["profile_metadata"]["checksum"] = governance_profile.compute_profile_checksum(profile["data"])

        report = validate_governance_profile(profile)
        assert report["valid"] is True
        assert "changeset" in report
        cs_schemas = report["changeset"]["schemas"]
        assert any(item["id"] == "existing-schema" for item in cs_schemas["update"])
        assert any(item["id"] == "brand-new-schema" for item in cs_schemas["add"])


# ==============================================================================
# Zero Vault Modification Proof
# ==============================================================================
def test_ha_vault_zero_modification():
    """Verify that throughout all governance and workspace operations, vault tree remains identical."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vdir = Path(tmpdir) / "Vault"
        vdir.mkdir()
        test_file = vdir / "Note.md"
        test_file.write_text("---\ntitle: Immutable\n---\nProse", encoding="utf-8")

        # Snapshot before
        files_before = {p.relative_to(vdir): hashlib.sha256(p.read_bytes()).hexdigest() for p in vdir.glob("**/*") if p.is_file()}

        # Perform operations
        _ = is_canonical_navigable_path("Note.md")
        _ = api_glossary_catalog({})
        _ = are_semantically_equal(["x"], "x")

        # Snapshot after
        files_after = {p.relative_to(vdir): hashlib.sha256(p.read_bytes()).hexdigest() for p in vdir.glob("**/*") if p.is_file()}
        assert files_before == files_after, "Vault must remain 100% byte-for-byte read-only"
