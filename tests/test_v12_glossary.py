"""Test suite for M017 User Property Glossary and 3-tier Precedence."""

from __future__ import annotations

import os
import pytest
from app.storage import get_storage_dir
from app.core.user_glossary import UserGlossaryOverride, UserGlossaryStore


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("PROPERTY_STUDIO_STORAGE_DIR", str(tmp_path / "storage"))
    yield


def test_v12_glo_001_precedence_system_vs_override():
    store = UserGlossaryStore()
    
    # 1. Builtin check
    res = store.resolve_property("status")
    assert res["source"] == "builtin"
    assert res["is_known"] is True
    assert res["label_zh"] == "狀態"

    # 2. Add user override
    override = UserGlossaryOverride(
        canonical_key="status",
        label_zh="自訂專案進度狀態",
        guidance="請統一填寫 planning / in_progress / done",
        category="custom_workflow",
    )
    store.save_override(override)

    # 3. Precedence check: override takes precedence over builtin
    res_override = store.resolve_property("status")
    assert res_override["source"] == "user_override"
    assert res_override["label_zh"] == "自訂專案進度狀態"
    assert res_override["guidance_zh"] == "請統一填寫 planning / in_progress / done"
    assert res_override["canonical_key"] == "status"  # Canonical key immutable!


def test_v12_glo_002_unknown_property_fallback():
    store = UserGlossaryStore()
    res = store.resolve_property("unregistered_random_prop")
    assert res["source"] == "vault_facts_only"
    assert res["is_known"] is False
    assert res["canonical_key"] == "unregistered_random_prop"


def test_v12_glo_003_delete_override_reverts_to_builtin():
    store = UserGlossaryStore()
    override = UserGlossaryOverride(canonical_key="owner", label_zh="負責團隊")
    store.save_override(override)
    assert store.resolve_property("owner")["label_zh"] == "負責團隊"

    # Delete override
    assert store.delete_override("owner") is True
    assert store.resolve_property("owner")["source"] == "builtin"
    assert store.resolve_property("owner")["label_zh"] == "負責人"
