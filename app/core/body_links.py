"""Body Wikilink Relationship Analysis Engine (M008).

REQ-030 / REQ-031 / DEC-025:
1. Extracts [[Wikilinks]] from note bodies (outside YAML frontmatter and code blocks).
2. Analyzes links across Source and Target scopes.
3. Categorizes links into: valid, broken, ambiguous, outside_target_scope.
4. Strictly read-only: never modifies, rewrites, or auto-repairs note bodies (V11-013).
5. Strictly separates Property Links and Body Wikilinks in data model and API (V11-012).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from .model import Confidence, Severity, VaultScan
from .scanner import note_name_index, note_path_index
from .scope import ScopeMode, ScopeSpec, filter_notes_by_scope

WIKILINK_BODY_RE = re.compile(r"\[\[(?P<target>[^\]\|\n]+)(?:\|(?P<display>[^\]\n]+))?\]\]")
CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```|`[^`\n]*`")


@dataclass
class BodyWikilinkFinding:
    id: str
    source_note: str
    target_raw: str
    canonical_target: str | None
    status: str  # "valid" | "broken" | "ambiguous" | "outside_target_scope"
    line_number: int
    context_snippet: str
    title: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_note": self.source_note,
            "target_raw": self.target_raw,
            "canonical_target": self.canonical_target,
            "status": self.status,
            "line_number": self.line_number,
            "context_snippet": self.context_snippet,
            "title": self.title,
            "explanation": self.explanation,
        }


def extract_body_wikilinks_from_text(content: str) -> list[tuple[str, int, str]]:
    """Extract (target, line_no, snippet) from Markdown content, skipping frontmatter and code blocks."""
    lines = content.splitlines()
    # Strip frontmatter if present
    start_line = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start_line = i + 1
                break

    extracted: list[tuple[str, int, str]] = []
    in_fence = False

    for idx in range(start_line, len(lines)):
        line = lines[idx]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Strip inline code from line before searching
        line_clean = re.sub(r"`[^`]*`", "", line)
        for match in WIKILINK_BODY_RE.finditer(line_clean):
            target = match.group("target").strip()
            if target:
                extracted.append((target, idx + 1, line.strip()))

    return extracted


def analyze_body_wikilinks(
    scan: VaultScan,
    source_scope: ScopeSpec | None = None,
    target_scope: ScopeSpec | None = None,
) -> dict[str, Any]:
    """Analyze Body Wikilinks across Source and Target Scopes (Strict Read-Only)."""
    name_index = note_name_index(scan)
    path_index = note_path_index(scan)

    # Resolve source notes
    source_notes = (
        filter_notes_by_scope(scan.notes, source_scope)
        if source_scope is not None and source_scope.mode != ScopeMode.ENTIRE_VAULT
        else scan.notes
    )

    # Target scope paths lookup
    target_scoped_paths: set[str] | None = None
    if target_scope is not None and target_scope.mode != ScopeMode.ENTIRE_VAULT:
        target_scoped_paths = {n.path for n in filter_notes_by_scope(scan.notes, target_scope)}

    findings: list[BodyWikilinkFinding] = []
    status_counts = {
        "valid": 0,
        "broken": 0,
        "ambiguous": 0,
        "outside_target_scope": 0,
    }

    for note in source_notes:
        full_file_path = os.path.join(scan.vault_path, note.path.replace("/", os.sep))
        if not os.path.exists(full_file_path):
            continue

        try:
            with open(full_file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError:
            continue

        links = extract_body_wikilinks_from_text(content)
        for target, line_no, snippet in links:
            t_key = target.casefold()
            hits: list[str] = []
            if t_key in path_index:
                hits = [path_index[t_key]]
            elif t_key in name_index:
                hits = list(name_index[t_key])

            fid = f"body-link:{note.path}:{line_no}:{target}"

            if len(hits) == 0:
                status_counts["broken"] += 1
                findings.append(
                    BodyWikilinkFinding(
                        id=fid,
                        source_note=note.path,
                        target_raw=target,
                        canonical_target=None,
                        status="broken",
                        line_number=line_no,
                        context_snippet=snippet,
                        title=f"Broken body link [[{target}]]",
                        explanation=f"Target '{target}' does not match any existing note in vault.",
                    )
                )
            elif len(hits) > 1:
                status_counts["ambiguous"] += 1
                findings.append(
                    BodyWikilinkFinding(
                        id=fid,
                        source_note=note.path,
                        target_raw=target,
                        canonical_target=None,
                        status="ambiguous",
                        line_number=line_no,
                        context_snippet=snippet,
                        title=f"Ambiguous body link [[{target}]]",
                        explanation=f"Target '{target}' matches {len(hits)} different notes in vault.",
                    )
                )
            else:
                canonical = hits[0]
                if target_scoped_paths is not None and canonical not in target_scoped_paths:
                    status_counts["outside_target_scope"] += 1
                    findings.append(
                        BodyWikilinkFinding(
                            id=fid,
                            source_note=note.path,
                            target_raw=target,
                            canonical_target=canonical,
                            status="outside_target_scope",
                            line_number=line_no,
                            context_snippet=snippet,
                            title=f"Body link [[{target}]] resolves outside Target Scope",
                            explanation=f"Target note '{canonical}' is outside the active Target Scope.",
                        )
                    )
                else:
                    status_counts["valid"] += 1
                    findings.append(
                        BodyWikilinkFinding(
                            id=fid,
                            source_note=note.path,
                            target_raw=target,
                            canonical_target=canonical,
                            status="valid",
                            line_number=line_no,
                            context_snippet=snippet,
                            title=f"Valid body link [[{target}]]",
                            explanation=f"Resolved to '{canonical}'.",
                        )
                    )

    return {
        "analysis_type": "body_wikilinks",
        "summary": {
            "total_links_found": len(findings),
            "by_status": dict(status_counts),
            "source_notes_checked": len(source_notes),
            "read_only_contract": "strict_read_only",
        },
        "findings": [f.to_dict() for f in findings],
    }
