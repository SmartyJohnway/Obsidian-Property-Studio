"""Exports and interchange (PROJECT §4G, AGENTS 32).

Rules enforced here:
  * artifacts are NEVER written inside the selected vault (REQ-002);
  * exports contain every canonical finding — no truncation (REQ-015);
  * every write is read back and verified by the caller-visible report.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIRNAME = ".obsidian-property-studio"


class ExportPathError(ValueError):
    pass


def default_output_dir() -> str:
    return str(Path.home() / DEFAULT_OUTPUT_DIRNAME / "exports")


def ensure_output_dir(vault_path: str | None, output_dir: str | None = None) -> str:
    target = os.path.abspath(os.path.expanduser(output_dir or default_output_dir()))
    if vault_path:
        vault = os.path.abspath(vault_path)
        try:
            common = os.path.commonpath([vault, target])
        except ValueError:  # different drives on Windows
            common = ""
        if common == vault:
            raise ExportPathError(
                "Refusing to write inside the selected vault. Choose a folder outside "
                f"the vault ({vault})."
            )
    os.makedirs(target, exist_ok=True)
    return target


def _write_text(path: str, text: str) -> dict[str, Any]:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    with open(path, "r", encoding="utf-8") as fh:
        read_back = fh.read()
    return {
        "path": path,
        "bytes": len(read_back.encode("utf-8")),
        "read_back_matches": read_back == text,
    }


# --------------------------------------------------------------------------
# Markdown renderers (human readable twin of the JSON artifacts)
# --------------------------------------------------------------------------
def _md_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def discovery_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Property Discovery Report",
        "",
        f"- Vault: `{summary['vault_path']}`",
        f"- Notes scanned: {summary['note_count']}",
        f"- Notes with properties: {summary['notes_with_properties']}",
        f"- Notes without properties: {summary['notes_without_properties']}",
        f"- Notes whose properties could NOT be read: {summary['notes_with_parse_failure']}",
        f"- Unique property keys: {report['inventory']['unique_property_count']}",
        "",
        "## Property inventory",
        "",
        "| Property | Notes using it | Types observed | Distinct values |",
        "| --- | ---: | --- | ---: |",
    ]
    for entry in report["inventory"]["properties"]:
        types = ", ".join(f"{k} ({v})" for k, v in entry["observed_types"].items())
        lines.append(
            f"| `{_md_escape(entry['key'])}` | {entry['usage_count']} | {types} | "
            f"{entry['distinct_value_count']} |"
        )
    lines += ["", "## Findings", ""]
    if not report["findings"]:
        lines.append("_No findings._")
    for finding in report["findings"]:
        lines += [
            f"### [{finding['severity'].upper()}] {finding['title']}",
            "",
            f"- Category: `{finding['category']}` (confidence: {finding['confidence']})",
            f"- Properties: {', '.join('`' + k + '`' for k in finding['property_keys']) or '—'}",
            f"- Affected notes ({finding['affected_note_count']}): "
            + (", ".join(f"`{n}`" for n in finding["affected_notes"][:50]) or "—")
            + (" …" if finding["affected_note_count"] > 50 else ""),
            f"- Why: {finding['explanation']}",
            f"- Suggested next step: {finding['recommendation']}",
            "",
        ]
    if report.get("issues"):
        lines += ["## Parse issues", ""]
        for issue in report["issues"]:
            lines.append(
                f"- `{issue['note_path']}` — **{issue['status']}**: {issue['message']} "
                f"{issue['detail']}"
            )
        lines.append("")
    if report.get("skipped"):
        lines += ["## Skipped paths", ""]
        for skipped in report["skipped"]:
            lines.append(f"- `{skipped['path']}` — {skipped['reason']}")
    return "\n".join(lines) + "\n"


def health_markdown(report: dict[str, Any]) -> str:
    score = report["health_score"]
    lines = [
        "# Property Health Report",
        "",
        f"- Vault: `{report['vault_path']}`",
        f"- Health score: **{score['score']} / 100**",
        f"- Findings: {report['summary']['finding_count']}",
        "",
        "## How the score is calculated",
        "",
        f"`{score['formula']}`",
        "",
        "| Category | Findings | Weight each | Raw | Cap | Applied |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in score["score_breakdown"]:
        lines.append(
            f"| {row['category']} | {row['finding_count']} | {row['weight_per_finding']} "
            f"| {row['raw_deduction']} | {row['category_cap']} | {row['applied_deduction']} |"
        )
    lines += ["", "## Findings", ""]
    if not report["findings"]:
        lines.append("_No findings._")
    for finding in report["findings"]:
        lines += [
            f"### [{finding['severity'].upper()}] {finding['title']}",
            "",
            f"- Category: `{finding['category']}` (confidence: {finding['confidence']})",
            f"- Properties: {', '.join('`' + k + '`' for k in finding['property_keys']) or '—'}",
            f"- Affected notes ({finding['affected_note_count']}): "
            + (", ".join(f"`{n}`" for n in finding["affected_notes"]) or "—"),
            f"- Why: {finding['explanation']}",
            f"- Suggested next step: {finding['recommendation']}",
            "",
        ]
    return "\n".join(lines) + "\n"


def plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# Migration plan — {plan['operation']}",
        "",
        f"> {plan['notice']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in plan["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    def section(title: str, rows: list[dict[str, Any]]) -> None:
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append("_None._")
            lines.append("")
            return
        for row in rows:
            parts = [f"`{row.get('note', row.get('canonical_value', ''))}`"]
            for key, value in row.items():
                if key == "note":
                    continue
                parts.append(f"{key}: {_md_escape(value)}")
            lines.append("- " + " — ".join(parts))
        lines.append("")

    for key, title in (
        ("affected_notes", "Notes that would change"),
        ("changes", "Value groups to normalize"),
        ("convertible", "Convertible values"),
        ("ambiguous", "Ambiguous — manual decision required"),
        ("unresolved", "Unresolved — cannot be converted"),
        ("conflicts", "Conflicts — manual review required"),
        ("manual_review", "Manual review"),
        ("missing", "Notes missing required properties"),
        ("excluded", "Excluded (ambiguous duplicate keys)"),
        ("unreadable_notes", "Notes whose frontmatter could not be read"),
    ):
        if key in plan:
            section(title, plan[key])

    if plan.get("warnings"):
        lines += ["## Warnings", ""] + [f"- {w}" for w in plan["warnings"]] + [""]
    return "\n".join(lines) + "\n"


def inbox_markdown(inbox: dict[str, Any]) -> str:
    lines = [
        "# Property Relationship Inbox",
        "",
        f"- Items: {inbox['summary']['total_items']}",
        f"- Scope: {inbox['summary']['scope']}",
        f"- Automatically resolved by the app: {inbox['summary']['auto_resolved']}",
        "",
    ]
    for kind, count in inbox["summary"]["by_kind"].items():
        lines.append(f"- {kind}: {count}")
    lines += ["", "## Items", ""]
    if not inbox["items"]:
        lines.append("_Nothing to review._")
    for item in inbox["items"]:
        lines += [
            f"### [{item['severity'].upper()}] {item['title']}",
            "",
            f"- Kind: `{item['kind']}` (confidence: {item['confidence']})",
            f"- Note: `{item['note']}` — property `{item['property']}`",
            f"- Current value: `{_md_escape(item['value'])}`",
            f"- Candidates: "
            + (", ".join(f"`{c}`" for c in item["candidates"]) or "—"),
            f"- Proposed value: "
            + (f"`{item['proposed_value']}`" if item["proposed_value"] else "— (none proposed)"),
            f"- Why: {item['explanation']}",
            f"- What to do: {item['action']}",
            "",
        ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Export entry point
# --------------------------------------------------------------------------
EXPORT_KINDS = ("discovery", "health", "plan", "inbox", "schema")


def export_artifact(
    kind: str,
    payload: dict[str, Any],
    vault_path: str | None,
    output_dir: str | None = None,
    basename: str | None = None,
) -> dict[str, Any]:
    """Write JSON (+ Markdown twin) and read it back for verification."""
    if kind not in EXPORT_KINDS:
        raise ExportPathError(f"Unknown export kind '{kind}'.")
    target_dir = ensure_output_dir(vault_path, output_dir)
    stem = basename or f"property-studio-{kind}"
    json_path = os.path.join(target_dir, f"{stem}.json")
    json_text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False)
    written = [_write_text(json_path, json_text)]

    markdown = {
        "discovery": discovery_markdown,
        "health": health_markdown,
        "plan": plan_markdown,
        "inbox": inbox_markdown,
    }.get(kind)
    if markdown is not None:
        md_path = os.path.join(target_dir, f"{stem}.md")
        written.append(_write_text(md_path, markdown(payload)))

    # read-back verification of the JSON artifact (REQ-015)
    with open(json_path, "r", encoding="utf-8") as fh:
        reloaded = json.load(fh)
    verification = {
        "json_reload_ok": reloaded == json.loads(json_text),
        "finding_count_in_payload": len(payload.get("findings", []))
        or len(payload.get("items", [])),
        "finding_count_in_file": len(reloaded.get("findings", []))
        or len(reloaded.get("items", [])),
    }
    verification["no_silent_omission"] = (
        verification["finding_count_in_payload"] == verification["finding_count_in_file"]
        and verification["json_reload_ok"]
    )
    return {
        "kind": kind,
        "output_dir": target_dir,
        "files": written,
        "verification": verification,
    }
