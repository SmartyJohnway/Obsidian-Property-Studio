"""Test suite for M017 Named Schema Library & Storage OCC."""

from __future__ import annotations

import os
import pytest
from app.core.named_schemas import NamedSchema, NamedSchemaLibrary, NamedSchemaProperty
from app.storage import ConcurrencyError, assert_outside_vault, VaultIsolationError


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("PROPERTY_STUDIO_STORAGE_DIR", str(tmp_path / "storage"))
    yield


def test_v12_sch_001_named_schema_crud_and_persistence():
    library = NamedSchemaLibrary()
    
    schema_data = {
        "name": "設備資產",
        "version": "1.0",
        "description": "標準設備資產管理架構",
        "properties": [
            {"name": "serial_no", "storage_type": "text", "ui_control": "plain", "required": True},
            {"name": "status", "storage_type": "text", "ui_control": "plain", "required": True, "allowed_values": ["active", "maintenance"]},
        ]
    }
    
    res = library.create_schema(schema_data)
    schema_id = res["schema"]["id"]
    assert schema_id.startswith("schema_")
    assert res["revision"] == 1

    # Read back
    retrieved = library.get_schema(schema_id)
    assert retrieved is not None
    assert retrieved.name == "設備資產"
    assert len(retrieved.properties) == 2

    # Update
    update_data = retrieved.to_dict()
    update_data["description"] = "更新之設備資產管理"
    up_res = library.update_schema(schema_id, update_data, expected_revision=1)
    assert up_res["revision"] == 2
    assert library.get_schema(schema_id).description == "更新之設備資產管理"

    # Delete
    assert library.delete_schema(schema_id, expected_revision=2) is True
    assert library.get_schema(schema_id) is None


def test_v12_sch_002_occ_concurrency_conflict_rejection():
    library = NamedSchemaLibrary()
    res = library.create_schema({"name": "專案", "version": "1.0"})
    schema_id = res["schema"]["id"]
    
    # Stale update with wrong revision fails with ConcurrencyError
    with pytest.raises(ConcurrencyError) as exc_info:
        library.update_schema(schema_id, {"name": "專案更新"}, expected_revision=999)
    assert exc_info.value.current_revision == 1


def test_v12_sch_003_vault_isolation_assertion(tmp_path):
    vault_dir = tmp_path / "my_vault"
    vault_dir.mkdir()
    inside_vault_storage = vault_dir / ".storage"
    
    with pytest.raises(VaultIsolationError):
        assert_outside_vault(inside_vault_storage, vault_dir)
