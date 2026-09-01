"""
v1.1.0 Regression Contracts V11-014, V11-015:
Saved Relationship Checks Management Verification (M009 / R03).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import pytest

from app.core.manifest import assert_unchanged, vault_manifest
from app.core.model import Note, ParseStatus, PropertyValue, StorageType, VaultScan
from app.core.saved_checks import SavedCheck, SavedChecksStore
from app.core.scope import ScopeMode, ScopeSpec


def _make_vault(vault_dir: any) -> VaultScan:
    (vault_dir / "Projects").mkdir(exist_ok=True)
    (vault_dir / "Clients").mkdir(exist_ok=True)

    (vault_dir / "Projects" / "ProjA.md").write_text(
        "---\nclient: \"[[Client1]]\"\n---\nBody mentions [[Client1]].\n", encoding="utf-8"
    )
    (vault_dir / "Clients" / "Client1.md").write_text("# Client 1\n", encoding="utf-8")

    return VaultScan(
        vault_path=str(vault_dir),
        notes=[
            Note(
                path="Projects/ProjA.md",
                parse_status=ParseStatus.OK,
                properties={
                    "client": PropertyValue(
                        "client", "[[Client1]]", StorageType.TEXT, ("[[Client1]]",), "[[Client1]]"
                    )
                },
            ),
            Note(path="Clients/Client1.md", parse_status=ParseStatus.OK, properties={}),
        ],
    )


def test_v11_014_starts_with_zero_default_checks() -> None:
    """V11-014: System starts with zero default relationship rules or saved checks."""
    store = SavedChecksStore()
    assert store.list_checks() == []


def test_v11_015_saved_checks_round_trip_persistence_outside_vault(tmp_path: Path) -> None:
    """V11-015: Saved checks persist to external storage/JSON, reload accurately across restarts, and leave Vault untouched."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    store_file = tmp_path / "app_data" / "saved_checks.json"
    os.makedirs(store_file.parent, exist_ok=True)

    scan = _make_vault(vault_dir)
    manifest_before = vault_manifest(str(vault_dir))

    # 1. Create a Property SavedCheck & Body Wikilink SavedCheck
    chk_prop = SavedCheck(
        id="chk-001",
        name="Project to Client Scope Check",
        notes="Verify that projects only point to clients in the Clients folder.",
        link_type="property_link",
        property_name="client",
        source_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Projects"], include_subfolders=True),
        target_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Clients"], include_subfolders=True),
    )

    chk_body = SavedCheck(
        id="chk-002",
        name="Body Wikilink Check",
        notes="Analyze body links from Projects to Clients.",
        link_type="body_wikilink",
        source_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Projects"], include_subfolders=True),
        target_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Clients"], include_subfolders=True),
    )

    # Save to store and serialize to disk outside Vault
    store = SavedChecksStore()
    store.save_check(chk_prop)
    store.save_check(chk_body)

    with open(store_file, "w", encoding="utf-8") as f:
        f.write(store.to_json())

    assert os.path.exists(store_file)

    # 2. Simulate application restart by loading serialized JSON
    with open(store_file, "r", encoding="utf-8") as f:
        store_restarted = SavedChecksStore.from_json(f.read())
    loaded_checks = store_restarted.list_checks()
    assert len(loaded_checks) == 2

    # 3. Execute Property check
    res_prop = store_restarted.execute_check(scan, "chk-001")
    assert "summary" in res_prop
    assert "four_state_counts" in res_prop["summary"]
    assert res_prop["check_id"] == "chk-001"

    # 4. Execute Body Wikilink check (verify it dispatches to body analyzer)
    res_body = store_restarted.execute_check(scan, "chk-002")
    assert res_body.get("analysis_type") == "body_wikilinks"
    assert res_body["check_id"] == "chk-002"

    # 5. Verify Vault remains byte-for-byte untouched
    manifest_after = vault_manifest(str(vault_dir))
    diff = assert_unchanged(manifest_before, manifest_after)
    assert diff["unchanged"] is True
