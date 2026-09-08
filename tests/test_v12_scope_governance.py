"""Test suite for M019 Scope Expected Schema assignment."""

from __future__ import annotations

import pytest
from app.core.scope_governance import ScopeGovernanceStore


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("PROPERTY_STUDIO_STORAGE_DIR", str(tmp_path / "storage"))
    yield


def test_v12_scp_001_assign_and_retrieve_scope_schema():
    store = ScopeGovernanceStore()
    
    # 1. Assign schema to scope
    res = store.assign_schema("Projects", "schema_proj_101", "專案架構規範")
    assert res["assignment"]["schema_id"] == "schema_proj_101"

    # 2. Get assignment
    asgn = store.get_assignment("Projects")
    assert asgn is not None
    assert asgn.schema_id == "schema_proj_101"
    assert asgn.schema_name == "專案架構規範"

    # 3. Unassign
    assert store.unassign_schema("Projects") is True
    assert store.get_assignment("Projects") is None
