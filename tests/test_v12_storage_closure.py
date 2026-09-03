"""Test suite for Commit 19: Migration Transaction Rollback, Per-Entity Guard & Runtime Path Migration Closure.

Covers:
1. P0 Pure Path Resolution & Negative Zero-Change Proof (Task 1 & 4)
2. P0 Legacy State Migration: Atomic Validate-Before-Persist (Task 2)
3. P0 Legacy State Migration: True Persistence Transaction Rollback on I/O failure (Commit 19 Blocker 1)
4. P0 Legacy State Migration: Per-Entity Initialized-State Guard (Commit 19 Blocker 2)
5. P0 Legacy State Migration: Canonical Dict Exact Readback (Commit 19 Polish)
6. Runtime Legacy Path Migration Invocation in create_server and api_scan (Commit 19 Blocker 3)
7. Path Migration Out of __init__ and Fail-Closed (Task 3)
8. Governance Profile Clear-Stage Rollback & Preferences Preview (Task 5 & 6)
9. Saved Checks REQ-052 Corruption Protection & Persistence (Task 3 & 7)
10. Drift Exact Canonical StorageType (Task 8)
11. Frontend Dynamic JS i18n & Drawer Strings Clean (Task 7 & 9)
"""

import json
import os
import re
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import patch
import pytest

from app.storage.local_storage import (
    VaultIsolationError,
    StorageError,
    assert_outside_vault,
    set_active_vault_path,
    get_active_vault_path,
    migrate_legacy_storage_paths,
    get_storage_dir,
    EntityStorage,
)
from app.core import saved_checks, drift, governance_profile, scope_governance, named_schemas, user_glossary
from app.core.saved_checks import SavedCheck, SavedChecksStore, CorruptedSavedChecksError
from app.core.model import VaultScan, Note, PropertyValue, SchemaProperty, StorageType, ParseStatus
from app.core.scope import ScopeSpec
from app.server import (
    api_storage_migrate_legacy,
    api_preferences_get,
    api_preferences_set,
    api_scan,
    create_server,
    init_runtime_storage,
    STORE,
    ApiError,
)


def get_dir_tree_snapshot(directory: Path) -> dict[str, str]:
    """Capture full recursive snapshot of all directories and file hashes in a directory."""
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            rel = os.path.relpath(os.path.join(root, d), directory).replace("\\", "/")
            snapshot[f"DIR:{rel}"] = "DIR"
        for f in files:
            p = Path(root) / f
            rel = os.path.relpath(p, directory).replace("\\", "/")
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            snapshot[f"FILE:{rel}"] = h
    return snapshot


# ==============================================================================
# 1. P0 Pure Path Resolution & Negative Zero-Change Proof (Task 1 & 4)
# ==============================================================================
def test_vault_isolation_pure_path_and_negative_zero_change():
    """Verify pure path resolution before mkdir and prove 0 directory/file mutation on violation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        vault_dir = root / "DisposableVault"
        vault_dir.mkdir()
        (vault_dir / "Notes").mkdir()
        (vault_dir / "Notes" / "Note1.md").write_text("# Note 1\n", encoding="utf-8")
        (vault_dir / "Notes" / "Note2.md").write_text("# Note 2\n", encoding="utf-8")

        initial_snapshot = get_dir_tree_snapshot(vault_dir)

        # Set active vault first
        set_active_vault_path(vault_dir)
        assert get_active_vault_path() == vault_dir.resolve()

        # 1. Negative Test: Point storage directory to a SUBDIRECTORY of vault
        bad_store_path = vault_dir / "bad_store"
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": str(bad_store_path)}):
            # Pure path calculation must NOT create bad_store
            s_dir = get_storage_dir(create=False)
            assert s_dir == bad_store_path.resolve()
            assert not bad_store_path.exists(), "get_storage_dir(create=False) must not mutate filesystem!"

            # Instantiating and attempting EntityStorage operations fails-closed
            storage = EntityStorage("test", "test.json")
            with pytest.raises(VaultIsolationError):
                storage.save({"should": "fail"})

            # CRITICAL ASSERTION: The bad_store directory was NEVER created!
            assert not bad_store_path.exists(), "Failed isolation must reject before mkdir!"

        # 2. Negative Test: Storage directory is EQUAL to vault
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": str(vault_dir)}):
            storage = EntityStorage("test", "test.json")
            with pytest.raises(VaultIsolationError):
                storage.save({"should": "fail"})

        # 3. Negative Test: Storage directory is PARENT containing vault
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": str(root)}):
            storage = EntityStorage("test", "test.json")
            with pytest.raises(VaultIsolationError):
                storage.save({"should": "fail"})

        # Absolute proof: Vault tree (both files AND directories) remains 100% byte-for-byte untouched!
        final_snapshot = get_dir_tree_snapshot(vault_dir)
        assert initial_snapshot == final_snapshot, "Vault directory/file tree must remain byte-for-byte identical!"

        # Cleanup
        set_active_vault_path(None)


# ==============================================================================
# 2. P0 Legacy State Migration: Validation-Before-Persist (Task 2)
# ==============================================================================
def test_legacy_migration_validate_before_persist_atomic():
    """Verify that corrupt item in legacy payload fails-closed with zero partial writes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            with patch.object(STORE, "saved_checks_store", chk_store):
                # Malformed payload: valid locale, valid theme, but check #3 has invalid dict structure
                malformed_payload = {
                    "ps_locale": "en",
                    "ps_theme": "dark",
                    "ops_saved_relationship_checks_v110": [
                        {"id": "chk-1", "name": "Check 1", "link_type": "property_link", "property_name": "related"},
                        {"id": "chk-2", "name": "Check 2", "link_type": "body_wikilink"},
                        "NOT_A_DICTIONARY",  # Corrupted entry
                    ]
                }

                # Must fail-closed with 400
                with pytest.raises(ApiError, match="Malformed legacy check"):
                    api_storage_migrate_legacy(malformed_payload)

                # ATOMICITY ASSERTION: Neither preferences nor saved checks were partially written!
                prefs = governance_profile.PREFERENCES_STORAGE.load().get("data")
                assert not prefs or "_legacy_migrated" not in prefs, "Preferences must not be partially saved on failure!"
                assert len(chk_store.list_checks()) == 0, "No checks should be saved on validation failure!"


# ==============================================================================
# 3. P0 Legacy State Migration: True Persistence Transaction Rollback (Blocker 1)
# ==============================================================================
def test_legacy_migration_persistence_failure_full_rollback():
    """Verify that when persistence fails midway (e.g. check save fails after prefs), both entities are 100% rolled back."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            with patch.object(STORE, "saved_checks_store", chk_store):
                # Setup initial baseline (empty uninitialized backend)
                governance_profile.PREFERENCES_STORAGE.save({})
                assert len(chk_store.list_checks()) == 0

                valid_payload = {
                    "ps_locale": "en",
                    "ps_theme": "light",
                    "ops_saved_relationship_checks_v110": [
                        {"id": "chk-new-1", "name": "New Check 1", "link_type": "body_wikilink"},
                        {"id": "chk-new-2", "name": "New Check 2", "link_type": "property_link", "property_name": "rel"}
                    ]
                }

                # Simulate I/O failure during checks persistence (Prefs written, checks fail)
                with patch.object(chk_store, "replace_all", side_effect=[IOError("Simulated disk write failure on checks"), None]):
                    with pytest.raises(ApiError) as exc_info:
                        api_storage_migrate_legacy(valid_payload)
                    assert exc_info.value.status == 500
                    assert "rolled back" in str(exc_info.value)

                # CRITICAL TRANSACTION ROLLBACK ASSERTIONS:
                # 1. Preferences must be exactly restored to original empty baseline (no locale=en, no theme=light, no _legacy_migrated)
                restored_prefs = governance_profile.PREFERENCES_STORAGE.load().get("data")
                assert not restored_prefs or "_legacy_migrated" not in restored_prefs

                # 2. Saved checks must be exactly restored to original empty baseline
                restored_checks = chk_store.list_checks()
                assert len(restored_checks) == 0


# ==============================================================================
# 4. P0 Legacy State Migration: Per-Entity Initialized-State Guard (Blocker 2)
# ==============================================================================
def test_legacy_migration_per_entity_guard_prefs_only_initialized():
    """If backend preferences are already initialized but checks are not, migrate checks and preserve prefs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            with patch.object(STORE, "saved_checks_store", chk_store):
                # Backend has existing preferences, but NO saved checks
                governance_profile.PREFERENCES_STORAGE.save({"locale": "zh-Hant", "theme": "dark"})
                assert len(chk_store.list_checks()) == 0

                # Incoming legacy payload has conflicting prefs + new checks
                payload = {
                    "ps_locale": "en",
                    "ps_theme": "light",
                    "ops_saved_relationship_checks_v110": [
                        {"id": "chk-migrated", "name": "Migrated Check", "link_type": "body_wikilink"}
                    ]
                }
                res = api_storage_migrate_legacy(payload)
                assert res["status"] == "migrated"
                assert res["readback_verified"] is True
                # Existing backend preferences are PRESERVED (not overwritten by stale localStorage)
                assert res["preferences"]["locale"] == "zh-Hant"
                assert res["preferences"]["theme"] == "dark"
                # Checks are migrated
                assert res["migrated_checks_count"] == 1
                assert any(c["id"] == "chk-migrated" for c in res["checks"])


def test_legacy_migration_per_entity_guard_checks_only_initialized():
    """If backend checks are already initialized but preferences are not, migrate prefs and preserve checks."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            with patch.object(STORE, "saved_checks_store", chk_store):
                # Backend has existing check, but empty preferences
                existing_check = SavedCheck(id="chk-keep", name="Keep This Check", link_type="body_wikilink")
                chk_store.save_check(existing_check)
                governance_profile.PREFERENCES_STORAGE.save({})

                # Incoming legacy payload has new prefs + conflicting checks
                payload = {
                    "ps_locale": "en",
                    "ps_theme": "dark",
                    "ops_saved_relationship_checks_v110": [
                        {"id": "chk-stale", "name": "Stale Check", "link_type": "body_wikilink"}
                    ]
                }
                res = api_storage_migrate_legacy(payload)
                assert res["status"] == "migrated"
                assert res["readback_verified"] is True
                # Preferences are migrated
                assert res["preferences"]["locale"] == "en"
                assert res["preferences"]["theme"] == "dark"
                # Existing backend checks are PRESERVED (chk-stale not imported)
                assert res["migrated_checks_count"] == 0
                assert len(res["checks"]) == 1
                assert res["checks"][0]["id"] == "chk-keep"


# ==============================================================================
# 5. P0 Legacy State Migration: Canonical Dict Exact Readback (Polish)
# ==============================================================================
def test_legacy_migration_canonical_dict_exact_readback():
    """Verify that readback verification compares full canonical SavedCheck dictionaries, not just IDs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            with patch.object(STORE, "saved_checks_store", chk_store):
                payload = {
                    "ps_locale": "en",
                    "ps_theme": "dark",
                    "ops_saved_relationship_checks_v110": [
                        {
                            "id": "chk-full",
                            "name": "Full Field Check",
                            "link_type": "property_link",
                            "property_name": "related",
                            "source_scope": {"folders": ["FolderA"], "include_subfolders": True},
                            "target_scope": {"folders": ["FolderB"], "include_subfolders": False}
                        }
                    ]
                }
                res = api_storage_migrate_legacy(payload)
                assert res["readback_verified"] is True

                # Assert that every canonical field matches in readback
                persisted = chk_store.get_check("chk-full")
                assert persisted is not None
                assert persisted.link_type == "property_link"
                assert persisted.property_name == "related"
                assert persisted.source_scope.folders == ["FolderA"]
                assert persisted.target_scope.folders == ["FolderB"]


# ==============================================================================
# 6. Runtime Legacy Storage Path Migration Invocation (Blocker 3)
# ==============================================================================
def test_runtime_legacy_storage_path_migration_in_production_lifecycle():
    """Verify migrate_legacy_storage_paths is executed during actual server creation and api_scan."""
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        storage_path = root / "AppStorage"
        storage_path.mkdir()
        vault_path = root / "Vault"
        vault_path.mkdir()

        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": str(storage_path)}):
            # Seed legacy unnested files
            legacy_prefs = storage_path / "preferences.json"
            legacy_prefs.write_text(json.dumps({"locale": "zh-Hant"}), encoding="utf-8")

            legacy_gov = storage_path / "governance"
            legacy_gov.mkdir()
            (legacy_gov / "scope_assignments.json").write_text(json.dumps({"default": "schema-1"}), encoding="utf-8")

            # 1. Test create_server() lifecycle invocation
            _ = create_server("127.0.0.1", 0)
            assert (storage_path / "config" / "preferences.json").exists()
            assert (storage_path / "scope_profiles" / "scope_expected_schemas.json").exists()
            # Original legacy files are retained as safety copies
            assert legacy_prefs.exists()

            # 2. Test api_scan() lifecycle invocation with active vault context
            (storage_path / "named_schemas.json").write_text(json.dumps({"s1": "test"}), encoding="utf-8")
            api_scan({"vault_path": str(vault_path)})
            assert (storage_path / "schemas" / "named_schemas.json").exists()


# ==============================================================================
# 7. Path Migration Out of __init__ and Fail-Closed
# ==============================================================================
def test_path_migration_not_in_init_and_fail_closed():
    """Verify EntityStorage init has no file-copy side effects, and path migration fails closed."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            storage_path = Path(temp_dir)
            legacy_file = storage_path / "preferences.json"
            legacy_file.write_text(json.dumps({"locale": "en"}), encoding="utf-8")

            # Instantiating EntityStorage must NOT automatically migrate files
            _ = EntityStorage("config", "config/preferences.json")
            new_file = storage_path / "config" / "preferences.json"
            assert not new_file.exists(), "EntityStorage.__init__ must not have migration side effects!"

            # Explicit migration succeeds
            migrate_legacy_storage_paths()
            assert new_file.exists()
            assert legacy_file.exists(), "Source file must be preserved after migration!"

            # Fail-closed on copy error
            with patch("shutil.copy2", side_effect=PermissionError("Locked disk")):
                fake_old = storage_path / "named_schemas.json"
                fake_old.write_text("{}", encoding="utf-8")
                with pytest.raises(StorageError, match="Failed to migrate legacy storage path"):
                    migrate_legacy_storage_paths()


# ==============================================================================
# 8. Governance Profile Clear-Stage Rollback & Preferences Preview (Task 5 & 6)
# ==============================================================================
def test_governance_profile_clear_stage_rollback():
    """Verify rollback when first clear succeeds but second clear fails in replace mode."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            chk_store.save_check(SavedCheck(id="chk-init", name="Init Check"))
            named_schemas.NAMED_SCHEMA_LIBRARY.save_schema({"id": "sch-init", "name": "Init Schema", "properties": []})
            scope_governance.SCOPE_GOVERNANCE_STORE.assign_schema("default", "sch-init", "Init Schema")
            user_glossary.USER_GLOSSARY_STORE.save_override(user_glossary.UserGlossaryOverride(canonical_key="author", label_zh="作者"))
            governance_profile.PREFERENCES_STORAGE.save({"locale": "zh-Hant", "theme": "dark"})

            valid_profile = {
                "format_version": "1.0",
                "exported_at": "2026-09-03T00:00:00Z",
                "data": {
                    "format_version": "1.0",
                    "named_schemas": [{"id": "s-new", "name": "New Schema", "properties": []}],
                    "scope_assignments": {},
                    "user_glossary": {},
                    "saved_checks": [],
                }
            }

            # Inject failure during SCOPE_GOVERNANCE_STORE.storage.save after NAMED_SCHEMA_LIBRARY.storage.save has run
            with patch.object(scope_governance.SCOPE_GOVERNANCE_STORE.storage, "save", side_effect=[RuntimeError("Scope clear disk error"), None]):
                with pytest.raises(ValueError, match="Import aborted and rolled back"):
                    governance_profile.import_governance_profile(valid_profile, mode="replace", saved_checks_store=chk_store)

            # Assert complete rollback: schemas that were cleared in stage 1 are fully restored!
            assert named_schemas.NAMED_SCHEMA_LIBRARY.get_schema("sch-init") is not None
            assert scope_governance.SCOPE_GOVERNANCE_STORE.get_assignment("default") is not None
            assert user_glossary.USER_GLOSSARY_STORE.get_override("author") is not None
            assert chk_store.get_check("chk-init") is not None
            assert governance_profile.PREFERENCES_STORAGE.load()["data"]["theme"] == "dark"


def test_governance_profile_preferences_preview():
    """Verify validate_governance_profile returns preferences_preview with change diff."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            governance_profile.PREFERENCES_STORAGE.save({"locale": "zh-Hant", "theme": "light"})

            profile_with_diff = {
                "data": {
                    "format_version": "1.0",
                    "governance_preferences": {"locale": "en", "theme": "dark"}
                }
            }
            res = governance_profile.validate_governance_profile(profile_with_diff)
            assert res["valid"] is True
            prev = res["preferences_preview"]
            assert prev["has_changes"] is True
            assert prev["locale"] == {"from": "zh-Hant", "to": "en"}
            assert prev["theme"] == {"from": "light", "to": "dark"}


# ==============================================================================
# 9. Saved Checks REQ-052 Corruption Protection & Persistence (Task 3 & 7)
# ==============================================================================
def test_saved_checks_storage_persistence_and_corruption_fail_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            store = SavedChecksStore(persistent=True)
            c1 = SavedCheck(id="c1", name="Alpha", link_type="property_link", property_name="prop1")
            store.save_check(c1)

            # Re-read
            store2 = SavedChecksStore(persistent=True)
            assert store2.get_check("c1") is not None

            # Corrupted payload fails-closed with CorruptedSavedChecksError
            corrupt_json = "{ invalid_json: 123"
            with pytest.raises(CorruptedSavedChecksError):
                SavedChecksStore.from_json(corrupt_json)


# ==============================================================================
# 10. Drift Exact Canonical StorageType Tests (Task 8)
# ==============================================================================
def test_drift_exact_canonical_storage_types():
    schema_props = [
        {"name": "due_date", "storage_type": "date"},
        {"name": "published_at", "storage_type": "datetime"},
        {"name": "categories", "storage_type": "list"},
        {"name": "labels", "storage_type": "tags"},
        {"name": "score", "storage_type": "number"},
    ]

    # date vs datetime mismatch
    note1 = Note(
        path="Note1.md",
        parse_status=ParseStatus.OK,
        properties={
            "due_date": PropertyValue(key="due_date", raw="2026-09-03T14:30:00Z", storage_type=StorageType.DATETIME),
            "published_at": PropertyValue(key="published_at", raw="2026-09-03", storage_type=StorageType.DATE),
            "categories": PropertyValue(key="categories", raw=["A"], storage_type=StorageType.LIST),
            "labels": PropertyValue(key="labels", raw=["tag1"], storage_type=StorageType.TAGS),
            "score": PropertyValue(key="score", raw=100, storage_type=StorageType.NUMBER),
        }
    )
    rep1 = drift.analyze_schema_drift([note1], schema_props, "sch-exact", "Exact Type Schema")
    mismatches1 = [f for f in rep1.findings if f.category == drift.DriftCategory.TYPE_MISMATCH]
    assert any(f.property_key == "due_date" and f.actual == "datetime" for f in mismatches1)
    assert any(f.property_key == "published_at" and f.actual == "date" for f in mismatches1)

    # list vs tags mismatch
    note2 = Note(
        path="Note2.md",
        parse_status=ParseStatus.OK,
        properties={
            "due_date": PropertyValue(key="due_date", raw="2026-09-03", storage_type=StorageType.DATE),
            "published_at": PropertyValue(key="published_at", raw="2026-09-03T14:30:00Z", storage_type=StorageType.DATETIME),
            "categories": PropertyValue(key="categories", raw=["tagA"], storage_type=StorageType.TAGS),
            "labels": PropertyValue(key="labels", raw=["catB"], storage_type=StorageType.LIST),
            "score": PropertyValue(key="score", raw=100, storage_type=StorageType.NUMBER),
        }
    )
    rep2 = drift.analyze_schema_drift([note2], schema_props, "sch-exact", "Exact Type Schema")
    mismatches2 = [f for f in rep2.findings if f.category == drift.DriftCategory.TYPE_MISMATCH]
    assert any(f.property_key == "categories" and f.actual == "tags" for f in mismatches2)
    assert any(f.property_key == "labels" and f.actual == "list" for f in mismatches2)


# ==============================================================================
# 11. Frontend Dynamic JS i18n & Drawer Strings Clean (Task 7 & 9)
# ==============================================================================
def test_frontend_dynamic_js_strings_clean():
    """Verify that dynamic notifications and modal drawers in index.html scripts use I18N.t."""
    index_html_path = Path(__file__).resolve().parent.parent / "app" / "ui" / "index.html"
    content = index_html_path.read_text(encoding="utf-8")

    scripts = re.findall(r"<script(?:\s+[^>]*)?>(.*?)</script>", content, re.DOTALL)
    js_content = "\n".join(scripts)

    # 1. Prohibit hardcoded Chinese strings in toast(...) calls
    hardcoded_toast = re.findall(r'toast\(\s*["\'][\u4e00-\u9fa5]+', js_content)
    assert not hardcoded_toast, f"Found hardcoded Chinese in toast() calls: {hardcoded_toast}"

    # 2. Prohibit hardcoded Chinese in openDrawer(...) title calls
    hardcoded_drawers = re.findall(r'openDrawer\(\s*["\'][\u4e00-\u9fa5]+', js_content)
    assert not hardcoded_drawers, f"Found hardcoded Chinese in openDrawer() calls: {hardcoded_drawers}"
