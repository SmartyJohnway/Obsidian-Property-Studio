"""Vault integrity manifest helpers (REQ-002 / OPS-AC-005).

Used by tests and by the in-app "verify vault untouched" action to prove the
selected vault is byte-for-byte unchanged before and after product flows.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 256), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vault_manifest(vault_path: str) -> dict[str, dict[str, Any]]:
    """Hash **every** file in the vault, including .obsidian and attachments."""
    root = os.path.abspath(vault_path)
    manifest: dict[str, dict[str, Any]] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                stat = os.stat(full, follow_symlinks=False)
                manifest[rel] = {
                    "sha256": file_sha256(full) if not os.path.islink(full) else "<symlink>",
                    "size": stat.st_size,
                }
            except OSError as exc:  # pragma: no cover - defensive
                manifest[rel] = {"sha256": f"<unreadable: {exc}>", "size": -1}
    return manifest


def manifest_digest(manifest: dict[str, dict[str, Any]]) -> str:
    """Single stable digest for a whole manifest."""
    hasher = hashlib.sha256()
    for rel in sorted(manifest):
        entry = manifest[rel]
        hasher.update(rel.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(str(entry["sha256"]).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(str(entry["size"]).encode("utf-8"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def diff_manifests(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> dict[str, list[str]]:
    created = sorted(set(after) - set(before))
    deleted = sorted(set(before) - set(after))
    modified = sorted(
        rel
        for rel in set(before) & set(after)
        if before[rel]["sha256"] != after[rel]["sha256"]
        or before[rel]["size"] != after[rel]["size"]
    )
    return {"created": created, "modified": modified, "deleted": deleted}


def assert_unchanged(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Return a report dict; ``unchanged`` is the machine-checkable claim."""
    diff = diff_manifests(before, after)
    return {
        "unchanged": not (diff["created"] or diff["modified"] or diff["deleted"]),
        "files_created": len(diff["created"]),
        "files_modified": len(diff["modified"]),
        "files_deleted": len(diff["deleted"]),
        "files_renamed": 0 if not (diff["created"] or diff["deleted"]) else "see created/deleted",
        "detail": diff,
        "before_digest": manifest_digest(before),
        "after_digest": manifest_digest(after),
    }
