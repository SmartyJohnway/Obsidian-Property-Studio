"""Scope domain model and in-memory evaluation engine for v1.1.0.

REQ-024 / REQ-025 / DEC-021:
Supports Entire Vault, Multiple Selected Folders (with union & deduplication),
and Single Note scopes with include_subfolders toggles.
All scope filtering executes in-memory over VaultScan without triggering disk rescans.
Invalid Scope specifications FAIL CLOSED with ScopeValidationError and never fallback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence

from app.core.model import Note, ParseIssue, VaultScan


class ScopeValidationError(ValueError):
    """Raised when a ScopeSpec configuration is malformed or invalid."""
    pass


class ScopeMode(str, Enum):
    ENTIRE_VAULT = "entire_vault"
    FOLDERS = "folders"
    SINGLE_NOTE = "single_note"

    def __str__(self) -> str:
        return self.value


@dataclass
class ScopeSpec:
    """Formal Scope specification."""

    mode: ScopeMode = ScopeMode.ENTIRE_VAULT
    folders: list[str] = field(default_factory=list)
    include_subfolders: bool = True
    note_path: str | None = None

    def validate(self) -> None:
        """Validate Scope configuration, failing closed on invalid states (R04)."""
        if not isinstance(self.mode, ScopeMode):
            raise ScopeValidationError(f"Invalid ScopeMode: {self.mode}")

        if self.mode == ScopeMode.FOLDERS:
            if not self.folders or not any(str(f).strip() for f in self.folders):
                raise ScopeValidationError("ScopeMode.FOLDERS requires at least one folder path.")
        elif self.mode == ScopeMode.SINGLE_NOTE:
            if not self.note_path or not str(self.note_path).strip():
                raise ScopeValidationError("ScopeMode.SINGLE_NOTE requires a non-empty note_path.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "folders": list(self.folders),
            "include_subfolders": self.include_subfolders,
            "note_path": self.note_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ScopeSpec:
        if data is None:
            return cls()
        if not isinstance(data, dict):
            raise ScopeValidationError("Scope data must be a dictionary.")

        mode_raw = data.get("mode", ScopeMode.ENTIRE_VAULT.value)
        mode_str = str(mode_raw).strip()
        try:
            mode = ScopeMode(mode_str)
        except ValueError:
            raise ScopeValidationError(f"Unknown ScopeMode '{mode_str}'. Fail-closed without fallback.")

        folders_raw = data.get("folders", [])
        if isinstance(folders_raw, (list, tuple)):
            folders = [str(f).strip().replace("\\", "/").strip("/") for f in folders_raw if str(f).strip()]
        else:
            folders = []

        include_sub = bool(data.get("include_subfolders", True))
        note_p = data.get("note_path")
        note_path = str(note_p).strip().replace("\\", "/").strip("/") if note_p else None

        spec = cls(
            mode=mode,
            folders=folders,
            include_subfolders=include_sub,
            note_path=note_path,
        )
        spec.validate()
        return spec


def normalize_posix_path(p: str) -> str:
    """Normalize a vault relative path to POSIX style without leading/trailing slashes."""
    return p.replace("\\", "/").strip("/")


def is_note_in_scope(note_path: str, scope: ScopeSpec) -> bool:
    """Evaluate whether a note path belongs to the given ScopeSpec."""
    scope.validate()
    norm_path = normalize_posix_path(note_path)
    if not norm_path:
        return False

    if scope.mode == ScopeMode.ENTIRE_VAULT:
        return True

    if scope.mode == ScopeMode.SINGLE_NOTE:
        if not scope.note_path:
            return False
        return norm_path == normalize_posix_path(scope.note_path)

    if scope.mode == ScopeMode.FOLDERS:
        if not scope.folders:
            return False

        # Check if note matches ANY of the specified folders (Union)
        for folder in scope.folders:
            norm_f = normalize_posix_path(folder)
            if norm_f == "":
                # Root folder
                if scope.include_subfolders:
                    return True
                else:
                    return "/" not in norm_path
            else:
                if scope.include_subfolders:
                    if norm_path == norm_f or norm_path.startswith(norm_f + "/"):
                        return True
                else:
                    parts = norm_path.rsplit("/", 1)
                    if len(parts) == 2 and parts[0] == norm_f:
                        return True

        return False

    return True


def filter_notes_by_scope(notes: Sequence[Note], scope: ScopeSpec) -> list[Note]:
    """Filter notes by ScopeSpec with union evaluation and deduplication (V11-002..004)."""
    scope.validate()
    seen: set[str] = set()
    result: list[Note] = []

    for note in notes:
        norm_p = normalize_posix_path(note.path)
        if norm_p in seen:
            continue
        if is_note_in_scope(norm_p, scope):
            seen.add(norm_p)
            result.append(note)

    return result


def filter_scan_by_scope(scan: VaultScan, scope: ScopeSpec) -> VaultScan:
    """Produce an in-memory scoped VaultScan without rescanning the disk (V11-004)."""
    scope.validate()
    scoped_notes = filter_notes_by_scope(scan.notes, scope)
    scoped_paths = {n.path for n in scoped_notes}

    # Retain issues that belong to the in-scope notes
    scoped_issues: list[ParseIssue] = [
        issue for issue in scan.issues if issue.note_path in scoped_paths
    ]

    return VaultScan(
        vault_path=scan.vault_path,
        notes=scoped_notes,
        skipped=list(scan.skipped),
        issues=scoped_issues,
        scan_seconds=0.0,
    )


def extract_vault_folders(notes: Sequence[Note]) -> list[str]:
    """Extract and sort all unique folder paths present in the scanned notes."""
    folders: set[str] = set()
    for note in notes:
        norm = normalize_posix_path(note.path)
        if "/" in norm:
            parts = norm.split("/")
            # Add all ancestor folder paths
            for i in range(1, len(parts)):
                folders.add("/".join(parts[:i]))

    return sorted(folders)
