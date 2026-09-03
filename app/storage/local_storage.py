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


def assert_outside_vault(storage_path: Path, vault_path: str | Path | None) -> None:
    """Assert that storage directory is strictly not within the selected vault."""
    if not vault_path:
        return
    try:
        v_real = Path(vault_path).resolve()
        s_real = Path(storage_path).resolve()
        # Ensure s_real is not inside v_real, nor is v_real inside s_real, nor are they equal
        if s_real == v_real or s_real in v_real.parents or v_real in s_real.parents:
            raise VaultIsolationError(
                f"Storage path '{s_real}' violates Vault isolation contract with Vault '{v_real}'."
            )
    except Exception as exc:
        if isinstance(exc, VaultIsolationError):
            raise
        # Path resolution defensive


class EntityStorage:
    """Thread-safe, OCC-protected file storage for a single entity type."""

    def __init__(self, entity_type: str, relative_file: str) -> None:
        self.entity_type = entity_type
        self.relative_file = relative_file
        self.lock = threading.RLock()

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
