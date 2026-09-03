"""App-local governance storage layer (REQ-051, DEC-032).

Safety & Concurrency Contracts:
- Resolved outside selected Vault (%APPDATA%/ObsidianPropertyStudio/ or ~/.property_studio/).
- Path containment assertion guarantees Vault bytes are 100% read-only.
- Atomic file replacement (os.replace) prevents partial writes.
- Optimistic Concurrency Control (OCC) with integer revisions and ETags prevents lost updates.
- Collision-safe backups before destructive mutations.
- Fail-closed quarantine on corrupted files without silent overwrite.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STORAGE_SCHEMA_VERSION = "1.0"
STORAGE_FORMAT_IDENTIFIER = "property-studio-storage"


class StorageError(Exception):
    pass


class ConcurrencyError(StorageError):
    def __init__(self, message: str, current_revision: int, current_etag: str) -> None:
        super().__init__(message)
        self.current_revision = current_revision
        self.current_etag = current_etag


class VaultIsolationError(StorageError):
    pass


def get_storage_dir() -> Path:
    """Resolve base directory for app-local storage."""
    env_dir = os.environ.get("PROPERTY_STUDIO_STORAGE_DIR")
    if env_dir:
        p = Path(env_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    app_data = os.environ.get("APPDATA")
    if app_data:
        p = (Path(app_data) / "ObsidianPropertyStudio").resolve()
    else:
        p = (Path.home() / ".property_studio").resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


_ACTIVE_VAULT_PATH: Path | None = None


def set_active_vault_path(vault_path: str | Path | None) -> None:
    """Set and enforce runtime isolation invariant against the active vault (REQ-051)."""
    global _ACTIVE_VAULT_PATH
    if not vault_path:
        _ACTIVE_VAULT_PATH = None
        return
    v_real = Path(vault_path).resolve()
    s_real = get_storage_dir().resolve()
    assert_outside_vault(s_real, v_real)
    _ACTIVE_VAULT_PATH = v_real


def get_active_vault_path() -> Path | None:
    """Return currently active vault path, if any."""
    return _ACTIVE_VAULT_PATH


def assert_outside_vault(storage_path: Path, vault_path: str | Path | None) -> None:
    """Assert that storage directory is strictly not within the selected vault (REQ-051)."""
    if not vault_path:
        return
    v_real = Path(vault_path).resolve()
    s_real = Path(storage_path).resolve()

    # Reject equal paths
    if s_real == v_real:
        raise VaultIsolationError(
            f"Storage path '{s_real}' is identical to selected Vault path '{v_real}'. Storage must reside outside the Vault."
        )

    # Reject storage root being an ancestor of the Vault (storage parent containing Vault)
    if s_real in v_real.parents:
        raise VaultIsolationError(
            f"Storage path '{s_real}' is a parent directory containing selected Vault '{v_real}'. Storage must reside outside the Vault."
        )

    # Reject storage being inside the Vault or a Vault subdirectory
    if v_real in s_real.parents:
        raise VaultIsolationError(
            f"Storage path '{s_real}' is located inside selected Vault '{v_real}'. Storage must reside outside the Vault."
        )


def migrate_legacy_storage_paths() -> None:
    """Idempotently migrate pre-release entity paths to frozen M015 layout without data loss."""
    base = get_storage_dir()
    migrations = [
        ("preferences.json", "config/preferences.json"),
        ("governance/scope_assignments.json", "scope_profiles/scope_expected_schemas.json"),
        ("user_glossary.json", "glossary/user_glossary.json"),
        ("named_schemas.json", "schemas/named_schemas.json"),
        ("saved_relationship_checks.json", "saved_checks/saved_relationship_checks.json"),
    ]
    for old_rel, new_rel in migrations:
        old_path = base / old_rel
        new_path = base / new_rel
        if old_path.exists() and not new_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(old_path, new_path)
            except Exception:
                pass


class EntityStorage:
    """Thread-safe, OCC-protected file storage for a single entity type."""

    def __init__(self, entity_type: str, relative_file: str) -> None:
        self.entity_type = entity_type
        self.relative_file = relative_file
        self.lock = threading.RLock()
        # Automatically run idempotent path migration on first use
        migrate_legacy_storage_paths()

    def verify_isolation(self) -> None:
        """Enforce that this entity's file and root storage directory are strictly outside the active vault."""
        if _ACTIVE_VAULT_PATH is not None:
            assert_outside_vault(self._file_path(), _ACTIVE_VAULT_PATH)
            assert_outside_vault(get_storage_dir(), _ACTIVE_VAULT_PATH)

    def _file_path(self) -> Path:
        base = get_storage_dir()
        p = base / self.relative_file
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _compute_etag(self, raw_data: Any) -> str:
        serialized = json.dumps(raw_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    def load(self) -> dict[str, Any]:
        """Load entity data with OCC metadata."""
        self.verify_isolation()
        with self.lock:
            path = self._file_path()
            if not path.exists():
                empty_data: dict[str, Any] = {}
                return {
                    "format": STORAGE_FORMAT_IDENTIFIER,
                    "storage_schema_version": STORAGE_SCHEMA_VERSION,
                    "entity_type": self.entity_type,
                    "revision": 0,
                    "etag": self._compute_etag(empty_data),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "data": empty_data,
                }
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                if not isinstance(content, dict):
                    raise ValueError("Root payload is not a dictionary.")
                if "data" not in content:
                    # Upgrade legacy wrapper
                    data = content
                    rev = 1
                    etag = self._compute_etag(data)
                    return {
                        "format": STORAGE_FORMAT_IDENTIFIER,
                        "storage_schema_version": STORAGE_SCHEMA_VERSION,
                        "entity_type": self.entity_type,
                        "revision": rev,
                        "etag": etag,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "data": data,
                    }
                return content
            except Exception as exc:
                # Quarantine corrupt file
                ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                corrupt_path = path.with_suffix(f".corrupted_{ts}.json")
                try:
                    shutil.copy2(path, corrupt_path)
                except Exception:
                    pass
                raise StorageError(
                    f"Corrupted storage file for '{self.entity_type}'. Quarantined to '{corrupt_path.name}'. Error: {exc}"
                ) from exc

    def create_backup(self) -> Path | None:
        """Create collision-safe snapshot before mutation."""
        self.verify_isolation()
        path = self._file_path()
        if not path.exists():
            return None
        backups_dir = get_storage_dir() / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        uid = uuid.uuid4().hex[:8]
        backup_name = f"backup_{self.entity_type}_{ts}_{uid}.json"
        backup_path = backups_dir / backup_name
        shutil.copy2(path, backup_path)
        return backup_path

    def save(self, data: Any, expected_revision: int | None = None) -> dict[str, Any]:
        """Save entity data atomically with OCC check and backup."""
        self.verify_isolation()
        with self.lock:
            current = self.load()
            current_rev = current.get("revision", 0)
            current_etag = current.get("etag", "")

            if expected_revision is not None and expected_revision != current_rev:
                raise ConcurrencyError(
                    f"Conflict updating '{self.entity_type}': expected revision {expected_revision} != current {current_rev}.",
                    current_revision=current_rev,
                    current_etag=current_etag,
                )

            self.create_backup()

            new_rev = current_rev + 1
            new_etag = self._compute_etag(data)
            now_iso = datetime.now(timezone.utc).isoformat()

            payload = {
                "format": STORAGE_FORMAT_IDENTIFIER,
                "storage_schema_version": STORAGE_SCHEMA_VERSION,
                "entity_type": self.entity_type,
                "revision": new_rev,
                "etag": new_etag,
                "updated_at": now_iso,
                "data": data,
            }

            path = self._file_path()
            tmp_path = path.with_suffix(f".tmp.{os.getpid()}_{uuid.uuid4().hex[:6]}")
            try:
                with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, path)
            finally:
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass

            return payload
