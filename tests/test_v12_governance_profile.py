"""Test suite for M021 Governance Profile Import/Export Engine."""

from __future__ import annotations

import pytest
from app.core.governance_profile import (
    compute_profile_checksum,
    export_governance_profile,
    import_governance_profile,
)
from app.core.named_schemas import NAMED_SCHEMA_LIBRARY
from app.core.scope_governance import SCOPE_GOVERNANCE_STORE
from app.core.user_glossary import USER_GLOSSARY_STORE, UserGlossaryOverride


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("PROPERTY_STUDIO_STORAGE_DIR", str(tmp_path / "storage"))
    yield


def test_v12_gov_001_export_and_import_roundtrip():
    # Setup state
    NAMED_SCHEMA_LIBRARY.create_schema({
        "id": "sch_profile_test",
        "name": "測試架構",
        "properties": [{"name": "topic", "storage_type": "text"}],
    })
    SCOPE_GOVERNANCE_STORE.assign_schema("DefaultScope", "sch_profile_test", "測試架構")
    USER_GLOSSARY_STORE.save_override(
        UserGlossaryOverride(canonical_key="status", label_zh="自訂狀態", guidance="測試指引")
    )

    # Export
    exported = export_governance_profile()
    assert exported["profile_metadata"]["format_version"] == "1.0"
    assert exported["profile_metadata"]["sha256_checksum"] is not None
    assert exported["profile_metadata"]["schema_count"] >= 1

    # Clear and Import
    import_res = import_governance_profile(exported)
    assert import_res["status"] == "imported"
    assert import_res["imported"]["schemas"] >= 1
    assert import_res["imported"]["scope_assignments"] >= 1
    assert import_res["imported"]["glossary_overrides"] >= 1


def test_v12_gov_002_corrupted_checksum_fails_closed():
    exported = export_governance_profile()
    # Corrupt data
    exported["data"]["named_schemas"].append({"id": "tampered", "name": "惡意篡改"})

    with pytest.raises(ValueError, match="Profile checksum mismatch"):
        import_governance_profile(exported)
