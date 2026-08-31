"""Vault scanning + honest frontmatter parsing.

Safety contract (REQ-002 / REQ-017 / AGENTS 29):
  * this module only ever *reads* the vault;
  * it never follows symlinks/junctions out of the vault;
  * it never executes vault content;
  * every skipped path and every parse failure is reported explicitly.
"""

from __future__ import annotations

import os
import time
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable

import yaml

from .model import (
    Note,
    ParseIssue,
    ParseStatus,
    PropertyValue,
    Severity,
    SkippedPath,
    StorageType,
    VaultScan,
    iso_date,
)

#: Folders that are never treated as notes (AGENTS 29.2).
DEFAULT_EXCLUDED_DIRS: tuple[str, ...] = (".obsidian", ".trash", ".git")

#: Maximum bytes inspected while looking for the closing frontmatter delimiter.
MAX_FRONTMATTER_BYTES = 256 * 1024

MARKDOWN_SUFFIXES = (".md", ".markdown")

TAG_KEYS = frozenset({"tags", "tag"})


class DuplicateKeyLoader(yaml.SafeLoader):
    """SafeLoader that records duplicate mapping keys instead of overwriting.

    AGENTS 29.4: duplicate/ambiguous keys must surface as ambiguity, never be
    silently resolved by "last one wins".
    """

    def __init__(self, stream: Any) -> None:
        super().__init__(stream)
        self.duplicate_keys: list[str] = []

    def construct_mapping(self, node, deep=False):  # type: ignore[override]
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hashable = isinstance(key, (str, int, float, bool, tuple, type(None)))
            except Exception:  # pragma: no cover - defensive
                hashable = False
            if not hashable:
                key = str(key)
            if key in mapping:
                self.duplicate_keys.append(str(key))
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


# Explicitly refuse python/object tags etc. SafeLoader already does, but be loud.
DuplicateKeyLoader.add_constructor(
    None,
    lambda loader, node: (_ for _ in ()).throw(
        yaml.constructor.ConstructorError(
            None, None, f"unsupported YAML tag {node.tag!r}", node.start_mark
        )
    ),
)


@dataclass
class ScanOptions:
    excluded_dirs: tuple[str, ...] = DEFAULT_EXCLUDED_DIRS
    #: also skip other dot-directories (Obsidian ignores them too)
    skip_dot_dirs: bool = True
    follow_symlinks: bool = False


# --------------------------------------------------------------------------
# value classification
# --------------------------------------------------------------------------
def _scalar_to_text(value: Any) -> str:
    import datetime as _dt

    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (_dt.date, _dt.datetime)):
        return iso_date(value)
    return str(value)


def classify_value(key: str, raw: Any) -> PropertyValue:
    """Map a parsed YAML value onto an Obsidian storage type (SC-05)."""
    import datetime as _dt

    key_l = key.strip().lower()

    if isinstance(raw, dict):
        return PropertyValue(
            key=key,
            raw=raw,
            storage_type=StorageType.UNSUPPORTED,
            scalars=(),
            display="<nested mapping>",
        )

    if isinstance(raw, list):
        scalars: list[str] = []
        unsupported = False
        for item in raw:
            if isinstance(item, (dict, list)):
                unsupported = True
                scalars.append("<nested structure>")
            else:
                scalars.append(_scalar_to_text(item))
        storage = StorageType.UNSUPPORTED if unsupported else (
            StorageType.TAGS if key_l in TAG_KEYS else StorageType.LIST
        )
        return PropertyValue(
            key=key,
            raw=raw,
            storage_type=storage,
            scalars=tuple(scalars),
            display="[" + ", ".join(scalars) + "]",
        )

    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return PropertyValue(
            key=key, raw=raw, storage_type=StorageType.EMPTY, scalars=(), display=""
        )

    if isinstance(raw, bool):
        text = _scalar_to_text(raw)
        return PropertyValue(
            key=key,
            raw=raw,
            storage_type=StorageType.CHECKBOX,
            scalars=(text,),
            display=text,
        )
    if isinstance(raw, (int, float)):
        text = _scalar_to_text(raw)
        return PropertyValue(
            key=key,
            raw=raw,
            storage_type=StorageType.NUMBER,
            scalars=(text,),
            display=text,
        )
    if isinstance(raw, _dt.datetime):
        text = iso_date(raw)
        return PropertyValue(
            key=key,
            raw=raw,
            storage_type=StorageType.DATETIME,
            scalars=(text,),
            display=text,
        )
    if isinstance(raw, _dt.date):
        text = iso_date(raw)
        return PropertyValue(
            key=key, raw=raw, storage_type=StorageType.DATE, scalars=(text,), display=text
        )

    text = _scalar_to_text(raw)
    storage = StorageType.TAGS if key_l in TAG_KEYS else StorageType.TEXT
    return PropertyValue(
        key=key, raw=raw, storage_type=storage, scalars=(text,), display=text
    )


# --------------------------------------------------------------------------
# frontmatter extraction
# --------------------------------------------------------------------------
def extract_frontmatter(text: str) -> tuple[str | None, bool]:
    """Return ``(yaml_source, terminated)``.

    ``yaml_source`` is None when the document has no frontmatter block at all.
    ``terminated`` is False when an opening ``---`` was found but no closing
    delimiter — that is a malformed note, not a note without properties.
    """
    if text.startswith("\ufeff"):
        text = text[1:]
    # normalise line endings only for delimiter detection (CRLF/LF, REQ-016)
    lines = text.splitlines()
    if not lines:
        return None, True
    if lines[0].strip() != "---":
        return None, True
    body: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if stripped in ("---", "..."):
            return "\n".join(body), True
        body.append(line)
    return "\n".join(body), False


def _read_head(path: str) -> tuple[str, int, ParseIssue | None]:
    """Read enough of the file to cover the frontmatter block."""
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        data = fh.read(MAX_FRONTMATTER_BYTES)
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return "", size, ParseIssue(
            note_path="",
            status=ParseStatus.UNREADABLE,
            message="File is not valid UTF-8 and could not be decoded.",
            detail=str(exc),
        )
    return text, size, None


def parse_note(abs_path: str, rel_path: str) -> Note:
    """Parse one note honestly. Never raises for content problems."""
    try:
        text, size, decode_issue = _read_head(abs_path)
    except OSError as exc:
        issue = ParseIssue(
            note_path=rel_path,
            status=ParseStatus.UNREADABLE,
            message="File could not be opened.",
            detail=str(exc),
        )
        return Note(rel_path, ParseStatus.UNREADABLE, issues=(issue,))

    if decode_issue is not None:
        issue = ParseIssue(
            note_path=rel_path,
            status=decode_issue.status,
            message=decode_issue.message,
            detail=decode_issue.detail,
        )
        return Note(rel_path, ParseStatus.UNREADABLE, issues=(issue,), size_bytes=size)

    source, terminated = extract_frontmatter(text)

    if source is None:
        return Note(rel_path, ParseStatus.NO_FRONTMATTER, size_bytes=size)

    if not terminated:
        issue = ParseIssue(
            note_path=rel_path,
            status=ParseStatus.UNTERMINATED,
            message=(
                "Frontmatter starts with '---' but never closes. Obsidian will not "
                "read properties from this note."
            ),
            detail="No closing '---' delimiter was found.",
        )
        return Note(rel_path, ParseStatus.UNTERMINATED, issues=(issue,), size_bytes=size)

    if source.strip() == "":
        return Note(rel_path, ParseStatus.EMPTY_FRONTMATTER, size_bytes=size)

    loader = DuplicateKeyLoader(source)
    try:
        try:
            data = loader.get_single_data()
        finally:
            duplicates = tuple(sorted(set(loader.duplicate_keys)))
            loader.dispose()
    except yaml.YAMLError as exc:
        issue = ParseIssue(
            note_path=rel_path,
            status=ParseStatus.INVALID_YAML,
            message="Frontmatter is not valid YAML, so its properties cannot be read.",
            detail=str(exc).replace("\n", " ").strip(),
        )
        return Note(rel_path, ParseStatus.INVALID_YAML, issues=(issue,), size_bytes=size)

    if data is None:
        return Note(rel_path, ParseStatus.EMPTY_FRONTMATTER, size_bytes=size)

    if not isinstance(data, dict):
        issue = ParseIssue(
            note_path=rel_path,
            status=ParseStatus.NOT_A_MAPPING,
            message=(
                "Frontmatter is valid YAML but is not a list of properties "
                f"(found {type(data).__name__})."
            ),
            detail="Obsidian expects 'key: value' pairs at the top level.",
        )
        return Note(rel_path, ParseStatus.NOT_A_MAPPING, issues=(issue,), size_bytes=size)

    props: dict[str, PropertyValue] = {}
    issues: list[ParseIssue] = []
    for raw_key, raw_value in data.items():
        key = raw_key if isinstance(raw_key, str) else str(raw_key)
        key = unicodedata.normalize("NFC", key)
        props[key] = classify_value(key, raw_value)
        if props[key].storage_type is StorageType.UNSUPPORTED:
            issues.append(
                ParseIssue(
                    note_path=rel_path,
                    status=ParseStatus.OK,
                    severity=Severity.MEDIUM,
                    message=(
                        f"Property '{key}' contains a nested structure that Obsidian's "
                        "property editor cannot represent."
                    ),
                    detail="Reported as 'unsupported structure'; value left untouched.",
                )
            )
    for dup in duplicates:
        issues.append(
            ParseIssue(
                note_path=rel_path,
                status=ParseStatus.OK,
                severity=Severity.HIGH,
                message=(
                    f"Property '{dup}' is defined more than once in this note's "
                    "frontmatter; its effective value is ambiguous."
                ),
                detail=(
                    "This note is excluded from automated recommendations that depend "
                    "on that property (fail-closed)."
                ),
            )
        )

    return Note(
        path=rel_path,
        parse_status=ParseStatus.OK,
        properties=props,
        duplicate_keys=duplicates,
        issues=tuple(issues),
        size_bytes=size,
    )


# --------------------------------------------------------------------------
# vault walk
# --------------------------------------------------------------------------
class VaultPathError(ValueError):
    """Raised when the selected folder cannot be used as a vault."""


def validate_vault_path(path: str) -> str:
    if not path or not str(path).strip():
        raise VaultPathError("Please choose a vault folder.")
    expanded = os.path.abspath(os.path.expanduser(str(path).strip()))
    if not os.path.exists(expanded):
        raise VaultPathError(f"Folder does not exist: {expanded}")
    if not os.path.isdir(expanded):
        raise VaultPathError(f"Not a folder: {expanded}")
    if not os.access(expanded, os.R_OK):
        raise VaultPathError(f"Folder is not readable: {expanded}")
    return expanded


def _rel(root: str, abs_path: str) -> str:
    return os.path.relpath(abs_path, root).replace(os.sep, "/")


def scan_vault(vault_path: str, options: ScanOptions | None = None) -> VaultScan:
    """Walk the vault and produce the canonical scan (deterministic ordering)."""
    opts = options or ScanOptions()
    root = validate_vault_path(vault_path)
    root_real = os.path.realpath(root)
    started = time.perf_counter()

    notes: list[Note] = []
    skipped: list[SkippedPath] = []

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        keep: list[str] = []
        for name in sorted(dirnames):
            full = os.path.join(dirpath, name)
            if name in opts.excluded_dirs:
                skipped.append(
                    SkippedPath(_rel(root, full), f"excluded folder ('{name}')")
                )
                continue
            if opts.skip_dot_dirs and name.startswith("."):
                skipped.append(
                    SkippedPath(_rel(root, full), "hidden folder (ignored by Obsidian)")
                )
                continue
            if os.path.islink(full) and not opts.follow_symlinks:
                skipped.append(
                    SkippedPath(
                        _rel(root, full),
                        "symlink/junction not followed (may point outside the vault)",
                    )
                )
                continue
            keep.append(name)
        dirnames[:] = keep

        for name in sorted(filenames):
            if not name.lower().endswith(MARKDOWN_SUFFIXES):
                continue
            full = os.path.join(dirpath, name)
            rel = _rel(root, full)
            if os.path.islink(full) and not opts.follow_symlinks:
                skipped.append(
                    SkippedPath(rel, "symlink not followed (may point outside the vault)")
                )
                continue
            try:
                real = os.path.realpath(full)
            except OSError:  # pragma: no cover - defensive
                real = full
            if os.path.commonpath([root_real, real]) != root_real:
                skipped.append(SkippedPath(rel, "resolves outside the selected vault"))
                continue
            notes.append(parse_note(full, unicodedata.normalize("NFC", rel)))

    notes.sort(key=lambda n: n.path)
    skipped.sort(key=lambda s: s.path)

    issues: list[ParseIssue] = []
    for note in notes:
        issues.extend(note.issues)
    issues.sort(key=lambda i: (i.note_path, i.status.value, i.message))

    return VaultScan(
        vault_path=root,
        notes=notes,
        skipped=skipped,
        issues=issues,
        scan_seconds=round(time.perf_counter() - started, 4),
    )


def note_name_index(scan: VaultScan) -> dict[str, list[str]]:
    """Map lower-cased note name -> sorted note paths (for link resolution)."""
    index: dict[str, list[str]] = {}
    for note in scan.notes:
        index.setdefault(note.name.strip().lower(), []).append(note.path)
    for paths in index.values():
        paths.sort()
    return index


def note_path_index(scan: VaultScan) -> dict[str, str]:
    """Map lower-cased extension-less relative path -> note path."""
    index: dict[str, str] = {}
    for note in scan.notes:
        stem = note.path
        for suffix in MARKDOWN_SUFFIXES:
            if stem.lower().endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        index[stem.strip().lower()] = note.path
    return index


def iter_property_occurrences(
    scan: VaultScan, key: str
) -> Iterable[tuple[Note, PropertyValue]]:
    for note in scan.notes:
        value = note.properties.get(key)
        if value is not None:
            yield note, value
