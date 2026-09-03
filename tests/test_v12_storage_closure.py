"""Test suite for Commit 17: Frozen Storage Architecture & Safety Closure.

Covers:
1. P0 Runtime Vault Isolation (Task 1 / REQ-051)
2. P0 Legacy State Migration Contract /api/storage/migrate_legacy (Task 2 / REQ-051, REQ-052)
3. P0 App-Local Saved Checks Persistence & REQ-052 corruption protection (Task 3 & 7)
4. Storage Layout Alignment and Pre-release Migration (Task 4)
5. Real App-Local Preferences (Task 5)
6. Governance Profile Transaction Boundary & Rollback (Task 6)
7. Drift Exact Canonical StorageType (Task 8)
8. Frontend JS Dynamic String i18n Inspection (Task 9)
"""

import json
import os
import re
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from app.storage.local_storage import (
    VaultIsolationError,
    assert_outside_vault,
    set_active_vault_path,
    get_active_vault_path,
    migrate_legacy_storage_paths,
    get_storage_dir,
    EntityStorage,
)
from app.core import saved_checks, drift, governance_profile, scope_governance, named_schemas, user_glossary
from app.core.saved_checks import SavedCheck, SavedChecksStore, CorruptedSavedChecksError
from app.core.model import VaultScan, Note, PropertyValue, SchemaProperty
from app.core.scope import ScopeSpec
from app.server import (
    api_storage_migrate_legacy,
    api_preferences_get,
    api_preferences_set,
    api_scan,
    STORE,
    ApiError,
)


# ==============================================================================
# 1. P0 Runtime Vault Isolation Tests (Task 1 / REQ-051)
# ==============================================================================
def test_vault_isolation_assert():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        vault_dir = root / "MyVault"
        vault_dir.mkdir()
        storage_dir = root / "AppStorage"
        storage_dir.mkdir()

        # Legitimate outside storage: passes
        assert_outside_vault(storage_dir, vault_dir)

        # Equal paths: strictly rejected
        with pytest.raises(VaultIsolationError, match="identical"):
            assert_outside_vault(vault_dir, vault_dir)

        # Storage inside vault: strictly rejected
        nested_storage = vault_dir / "governance_storage"
        nested_storage.mkdir()
        with pytest.raises(VaultIsolationError, match="located inside"):
            assert_outside_vault(nested_storage, vault_dir)

        # Storage is parent containing vault: strictly rejected
        with pytest.raises(VaultIsolationError, match="parent directory containing"):
            assert_outside_vault(root, vault_dir)


def test_runtime_vault_isolation_enforcement():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        vault_dir = root / "SafeVault"
        vault_dir.mkdir()
        (vault_dir / "Note.md").write_text("# Note\n", encoding="utf-8")

        # Set valid active vault
        set_active_vault_path(vault_dir)
        assert get_active_vault_path() == vault_dir.resolve()

        # EntityStorage operations inside valid storage work without error
        storage = EntityStorage("test_entity", "test/test.json")
        storage.save({"foo": "bar"})
        loaded = storage.load()
        assert loaded["data"] == {"foo": "bar"}

        # Negative test: point storage directory directly inside the active vault
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": str(vault_dir / "bad_store")}):
            bad_storage = EntityStorage("bad_entity", "bad.json")
            with pytest.raises(VaultIsolationError):
                bad_storage.save({"violating": "vault"})

        # Negative test: call api_scan with vault set to current storage directory
        current_storage = get_storage_dir()
        with pytest.raises(ApiError) as exc_info:
            api_scan({"vault_path": str(current_storage)})
        assert "Vault isolation violation" in str(exc_info.value)

        # Reset active vault
        set_active_vault_path(None)
        assert get_active_vault_path() is None


# ==============================================================================
# 2. P0 Legacy State Migration Contract Tests (Task 2 / REQ-051, REQ-052)
# ==============================================================================
def test_legacy_state_migration_aliases_and_idempotency():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            # Test documented and historical aliases:
            # 1. ps_locale, ps_theme, ops_saved_relationship_checks_v110
            payload1 = {
                "ps_locale": "en",
                "ps_theme": "dark",
                "ops_saved_relationship_checks_v110": [
                    {
                        "id": "chk-1",
                        "name": "Check Alpha",
                        "link_type": "property_link",
                        "property_name": "related",
                    }
                ]
            }
            res1 = api_storage_migrate_legacy(payload1)
            assert res1["status"] == "migrated"
            assert res1["readback_verified"] is True
            assert res1["preferences"]["locale"] == "en"
            assert res1["preferences"]["theme"] == "dark"
            assert res1["migrated_checks_count"] == 1
            assert any(c["id"] == "chk-1" for c in res1["checks"])

            # 2. property_studio_* aliases (idempotent rerun)
            payload2 = {
                "property_studio_locale": "zh-Hant",
                "property_studio_theme": "light",
                "property_studio_saved_checks": [
                    {
                        "id": "chk-1",
                        "name": "Check Alpha (Updated)",
                        "link_type": "property_link",
                        "property_name": "related",
                    },
                    {
                        "id": "chk-2",
                        "name": "Check Beta",
                        "link_type": "body_wikilink",
                    }
                ]
            }
            res2 = api_storage_migrate_legacy(payload2)
            assert res2["status"] == "migrated"
            assert res2["readback_verified"] is True
            assert res2["preferences"]["locale"] == "zh-Hant"
            assert res2["preferences"]["theme"] == "light"
            assert len(res2["checks"]) == 2

            # Malformed checks fail-closed without corrupting storage
            with pytest.raises(ApiError) as exc_info:
                api_storage_migrate_legacy({"ops_saved_relationship_checks_v110": "invalid json {["})
            assert "Malformed legacy saved checks" in str(exc_info.value)


# ==============================================================================
# 3. P0 App-Local Saved Checks Persistence & REQ-052 Tests (Task 3 & 7)
# ==============================================================================
def test_saved_checks_storage_persistence():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            store1 = SavedChecksStore(persistent=True)
            store1.clear()
            chk = SavedCheck(id="chk-p1", name="Persistent Check", property_name="author")
            store1.save_check(chk)

            # Assert file exists on disk
            saved_file = Path(temp_dir) / "saved_checks" / "saved_relationship_checks.json"
            assert saved_file.exists()

            # Second instance loads directly from app-local storage
            store2 = SavedChecksStore(persistent=True)
            loaded = store2.get_check("chk-p1")
            assert loaded is not None
            assert loaded.name == "Persistent Check"
            assert loaded.property_name == "author"

            # Delete syncs to storage
            store2.delete_check("chk-p1")
            store3 = SavedChecksStore(persistent=True)
            assert store3.get_check("chk-p1") is None


def test_saved_checks_req052_corruption_fail_closed():
    # from_json must not silently return an empty store on corruption
    with pytest.raises(CorruptedSavedChecksError):
        SavedChecksStore.from_json("invalid json {[[")

    with pytest.raises(CorruptedSavedChecksError):
        SavedChecksStore.from_json(json.dumps({"format_version": "1.1.0", "checks": "not a list"}))

    with pytest.raises(CorruptedSavedChecksError):
        SavedChecksStore.from_json(json.dumps({"format_version": "1.1.0", "checks": ["not an object"]}))

    # Persistent storage corruption also raises CorruptedSavedChecksError
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            saved_file = Path(temp_dir) / "saved_checks" / "saved_relationship_checks.json"
            saved_file.parent.mkdir(parents=True, exist_ok=True)
            storage = EntityStorage("saved_checks", "saved_checks/saved_relationship_checks.json")
            storage.save({"checks": "corrupted"})

            with pytest.raises(CorruptedSavedChecksError):
                SavedChecksStore(persistent=True)


# ==============================================================================
# 4. Storage Layout Alignment and Pre-release Migration Tests (Task 4)
# ==============================================================================
def test_storage_layout_automatic_migration():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            base = Path(temp_dir)
            # Simulate pre-release files
            (base / "preferences.json").write_text(json.dumps({"data": {"locale": "en", "theme": "dark"}}), encoding="utf-8")
            (base / "governance").mkdir()
            (base / "governance" / "scope_assignments.json").write_text(json.dumps({"data": {"default": {"schema_id": "sch-1"}}}), encoding="utf-8")

            # Run migration
            migrate_legacy_storage_paths()

            # Assert new paths exist with intact data
            new_pref = base / "config" / "preferences.json"
            new_scope = base / "scope_profiles" / "scope_expected_schemas.json"
            assert new_pref.exists()
            assert new_scope.exists()

            pref_data = json.loads(new_pref.read_text(encoding="utf-8"))
            assert pref_data["data"]["locale"] == "en"
            scope_data = json.loads(new_scope.read_text(encoding="utf-8"))
            assert scope_data["data"]["default"]["schema_id"] == "sch-1"


# ==============================================================================
# 5. Governance Preferences UI Preferences Tests (Task 5)
# ==============================================================================
def test_preferences_api_round_trip():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            # Set preferences
            set_res = api_preferences_set({"preferences": {"locale": "en", "theme": "light"}})
            assert set_res["status"] == "saved"
            assert set_res["preferences"]["locale"] == "en"
            assert set_res["preferences"]["theme"] == "light"

            # Get preferences
            get_res = api_preferences_get({})
            assert get_res["preferences"]["locale"] == "en"
            assert get_res["preferences"]["theme"] == "light"

            # Export governance profile includes real preferences
            export_res = governance_profile.export_governance_profile()
            assert export_res["data"]["governance_preferences"]["locale"] == "en"
            assert export_res["data"]["governance_preferences"]["theme"] == "light"


# ==============================================================================
# 6. Governance Profile Transaction Boundary & Rollback Tests (Task 6)
# ==============================================================================
def test_governance_profile_transaction_boundaries():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"PROPERTY_STUDIO_STORAGE_DIR": temp_dir}):
            chk_store = SavedChecksStore(persistent=True)
            chk_store.save_check(SavedCheck(id="init-chk", name="Initial Check"))
            named_schemas.NAMED_SCHEMA_LIBRARY.save_schema({"id": "s1", "name": "Initial Schema", "properties": []})
            scope_governance.SCOPE_GOVERNANCE_STORE.assign_schema("default", "s1", "Initial Schema")
            user_glossary.USER_GLOSSARY_STORE.save_override(user_glossary.UserGlossaryOverride(canonical_key="author", label_zh="作者"))
            governance_profile.PREFERENCES_STORAGE.save({"locale": "zh-Hant", "theme": "dark"})

            # Reject unknown mode
            valid_profile = {
                "version": "1.0",
                "exported_at": "2026-09-03T00:00:00Z",
                "checksum": "",
                "data": {"format_version": "1.0"}
            }
            with pytest.raises(ValueError, match="Invalid import mode"):
                governance_profile.import_governance_profile(
                    valid_profile, mode="unknown_mode", saved_checks_store=chk_store
                )

            # Test A: Failure midway through import stage in 'replace' mode -> full rollback
            bad_profile = {
                "version": "1.0",
                "exported_at": "2026-09-03T00:00:00Z",
                "checksum": "",
                "data": {
                    "format_version": "1.0",
                    "named_schemas": [{"id": "s2", "name": "New Schema", "properties": []}],
                    "scope_assignments": {"default": {"schema_id": "s2"}},
                    "user_glossary": {"status": {"canonical_key": "status", "label_zh": "狀態"}},
                    "saved_checks": [{"id": "c2", "name": "New Check"}],
                    "governance_preferences": {"locale": "en", "theme": "light"}
                }
            }
            # Inject a failure during schema saving
            with patch.object(named_schemas.NAMED_SCHEMA_LIBRARY, "save_schema", side_effect=RuntimeError("Disk write failure")):
                with pytest.raises(ValueError, match="Import aborted and rolled back"):
                    governance_profile.import_governance_profile(
                        bad_profile, mode="replace", saved_checks_store=chk_store
                    )

            # Assert exact rollback: schemas, assignments, glossary, checks, preferences
            assert named_schemas.NAMED_SCHEMA_LIBRARY.get_schema("s1") is not None
            assert scope_governance.SCOPE_GOVERNANCE_STORE.get_assignment("default") is not None
            assert user_glossary.USER_GLOSSARY_STORE.get_override("author") is not None
            assert chk_store.get_check("init-chk") is not None
            assert governance_profile.PREFERENCES_STORAGE.load()["data"]["theme"] == "dark"


# ==============================================================================
# 7. Drift Exact Canonical StorageType Tests (Task 8)
# ==============================================================================
def test_drift_exact_canonical_storage_types():
    from app.core.model import StorageType, ParseStatus
    schema_props = [
        {"name": "due_date", "storage_type": "date"},
        {"name": "published_at", "storage_type": "datetime"},
        {"name": "categories", "storage_type": "list"},
        {"name": "labels", "storage_type": "tags"},
        {"name": "score", "storage_type": "number"},
    ]

    # Note 1: date vs datetime mismatch
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

    # Note 2: list vs tags mismatch
    note2 = Note(
        path="Note2.md",
        parse_status=ParseStatus.OK,
        properties={
            "due_date": PropertyValue(key="due_date", raw="2026-09-03", storage_type=StorageType.DATE),
            "published_at": PropertyValue(key="published_at", raw="2026-09-03T14:30:00Z", storage_type=StorageType.DATETIME),
            "categories": PropertyValue(key="categories", raw=["tagA"], storage_type=StorageType.TAGS),  # actual tags vs exp list
            "labels": PropertyValue(key="labels", raw=["catB"], storage_type=StorageType.LIST),      # actual list vs exp tags
            "score": PropertyValue(key="score", raw=100, storage_type=StorageType.NUMBER),
        }
    )
    rep2 = drift.analyze_schema_drift([note2], schema_props, "sch-exact", "Exact Type Schema")
    mismatches2 = [f for f in rep2.findings if f.category == drift.DriftCategory.TYPE_MISMATCH]
    assert any(f.property_key == "categories" and f.actual == "tags" for f in mismatches2)
    assert any(f.property_key == "labels" and f.actual == "list" for f in mismatches2)

    # Note 3: text string "95" vs number
    note3 = Note(
        path="Note3.md",
        parse_status=ParseStatus.OK,
        properties={
            "due_date": PropertyValue(key="due_date", raw="2026-09-03", storage_type=StorageType.DATE),
            "published_at": PropertyValue(key="published_at", raw="2026-09-03T14:30:00Z", storage_type=StorageType.DATETIME),
            "categories": PropertyValue(key="categories", raw=["A"], storage_type=StorageType.LIST),
            "labels": PropertyValue(key="labels", raw=["tag1"], storage_type=StorageType.TAGS),
            "score": PropertyValue(key="score", raw="95", storage_type=StorageType.TEXT),
        }
    )
    rep3 = drift.analyze_schema_drift([note3], schema_props, "sch-exact", "Exact Type Schema")
    mismatches3 = [f for f in rep3.findings if f.category == drift.DriftCategory.TYPE_MISMATCH]
    assert any(f.property_key == "score" and f.actual == "text" for f in mismatches3)


# ==============================================================================
# 8. Frontend JS Dynamic String i18n Inspection (Task 9)
# ==============================================================================
def test_frontend_dynamic_js_strings_clean():
    """Verify that dynamic notifications (toast, banner) in index.html scripts use I18N.t."""
    index_html_path = Path(__file__).resolve().parent.parent / "app" / "ui" / "index.html"
    content = index_html_path.read_text(encoding="utf-8")

    # Extract all <script> contents
    scripts = re.findall(r"<script(?:\s+[^>]*)?>(.*?)</script>", content, re.DOTALL)
    js_content = "\n".join(scripts)

    # Prohibit hardcoded Chinese strings in toast(...) calls
    hardcoded_toast = re.findall(r'toast\(\s*["\'][\u4e00-\u9fa5]+', js_content)
    assert not hardcoded_toast, f"Found hardcoded Chinese in toast() calls: {hardcoded_toast}"

    # Prohibit hardcoded Chinese strings in backtick toast calls
    hardcoded_toast_template = re.findall(r'toast\(\s*`[^`]*[\u4e00-\u9fa5]+', js_content)
    assert not hardcoded_toast_template, f"Found hardcoded Chinese in toast(``) calls: {hardcoded_toast_template}"
