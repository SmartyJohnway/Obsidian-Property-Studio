"""
v1.1.0 Regression Contracts V11-014, V11-015:
Saved Relationship Checks Management Verification.
"""

from __future__ import annotations

from app.core.manifest import assert_unchanged, vault_manifest
from app.core.model import Note, ParseStatus, PropertyValue, StorageType, VaultScan
from app.core.saved_checks import SavedCheck, SavedChecksStore
from app.core.scope import ScopeMode, ScopeSpec


def _make_vault(vault_dir: any) -> VaultScan:
    (vault_dir / "Projects").mkdir(exist_ok=True)
    (vault_dir / "Clients").mkdir(exist_ok=True)

    (vault_dir / "Projects" / "ProjA.md").write_text(
        "---\nclient: \"[[Client1]]\"\n---\n", encoding="utf-8"
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


def test_v11_015_saved_checks_round_trip_persistence_outside_vault(tmp_path: any) -> None:
    """V11-015: Saved checks persist to external storage/JSON, reload accurately, and leave Vault untouched."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    scan = _make_vault(vault_dir)
    manifest_before = vault_manifest(str(vault_dir))

    # 1. Create a SavedCheck
    chk = SavedCheck(
        id="chk-001",
        name="Project to Client Scope Check",
        notes="Verify that projects only point to clients in the Clients folder.",
        link_type="property",
        property_name="client",
        source_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Projects"], include_subfolders=True),
        target_scope=ScopeSpec(mode=ScopeMode.FOLDERS, folders=["Clients"], include_subfolders=True),
    )

    store = SavedChecksStore()
    store.save_check(chk)

    # Serialize to JSON (for localStorage / external export)
    serialized_json = store.to_json()
    assert "chk-001" in serialized_json
    assert "Project to Client Scope Check" in serialized_json

    # 2. Reload from another store instance (round-trip test)
    store2 = SavedChecksStore.from_json(serialized_json)
    loaded_checks = store2.list_checks()
    assert len(loaded_checks) == 1
    loaded = loaded_checks[0]
    assert loaded.id == "chk-001"
    assert loaded.name == "Project to Client Scope Check"
    assert loaded.source_scope.folders == ["Projects"]
    assert loaded.target_scope.folders == ["Clients"]

    # 3. Execute saved check
    res = store2.execute_check(scan, "chk-001")
    assert "summary" in res
    assert res["executed_check"]["id"] == "chk-001"

    # 4. Verify Vault remains byte-for-byte untouched
    manifest_after = vault_manifest(str(vault_dir))
    diff = assert_unchanged(manifest_before, manifest_after)
    assert diff["unchanged"] is True
