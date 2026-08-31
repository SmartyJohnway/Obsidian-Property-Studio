"""Build the synthetic fixture vaults + an independent expectation oracle.

The oracle is computed from the *declarative fixture spec* in this file, not by
running the product. Tests compare product output against the oracle, so the
oracle can never be "whatever the code happens to produce".

Run:  python scripts/build_fixtures.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "fixtures", "vaults")

# --------------------------------------------------------------------------
# Declarative spec: path -> (frontmatter_text | None, declared properties)
# ``declared`` describes what a human reader says the note's property layer is;
# ``status`` is the expected parse status.
# --------------------------------------------------------------------------
Note = dict


def note(path, frontmatter, declared, status="ok", body="Body text stays untouched.\n",
         newline="\n", duplicate_keys=()):
    return {
        "path": path,
        "frontmatter": frontmatter,
        "declared": declared,
        "status": status,
        "body": body,
        "newline": newline,
        "duplicate_keys": list(duplicate_keys),
    }


MAIN_NOTES: list[Note] = [
    note("Projects/Apollo.md",
         'type: project\nstatus: active\nowner: "[[Ada Lovelace]]"\n'
         'due_date: 2026-09-30\ntags:\n  - work\n  - urgent\n',
         {"type": "project", "status": "active", "owner": "[[Ada Lovelace]]",
          "due_date": "2026-09-30", "tags": ["work", "urgent"]}),
    note("Projects/Borealis.md",
         'type: project\nstatus: Active\nowner: Ada Lovelace\n'
         'due_date: 2026-10-15\npriority: high\n',
         {"type": "project", "status": "Active", "owner": "Ada Lovelace",
          "due_date": "2026-10-15", "priority": "high"}),
    note("Projects/Cascade.md",
         'type: project\nstatus: ACTIVE\nProject: Cascade\ndue_date: next month\n',
         {"type": "project", "status": "ACTIVE", "Project": "Cascade",
          "due_date": "next month"}),
    note("Projects/Delta 專案.md",
         'type: project\nstatus: 進行中\nowner: "[[林小明]]"\ntags:\n  - 研究\n',
         {"type": "project", "status": "進行中", "owner": "[[林小明]]",
          "tags": ["研究"]}),
    note("People/Ada Lovelace.md", 'type: person\nstatus: active\n',
         {"type": "person", "status": "active"}),
    note("People/林小明.md", 'type: person\nstatus: active\n',
         {"type": "person", "status": "active"}),
    note("Meetings/2026-01-05 Kickoff.md",
         'type: meeting\ndate: 2026-01-05\nattendees:\n  - "[[Ada Lovelace]]"\n'
         '  - "[[Missing Person]]"\nproject: "[[Apollo]]"\n',
         {"type": "meeting", "date": "2026-01-05",
          "attendees": ["[[Ada Lovelace]]", "[[Missing Person]]"],
          "project": "[[Apollo]]"}),
    note("Meetings/CRLF Note.md",
         'type: meeting\ndate: 2026-02-01\nproject: Apollo\n',
         {"type": "meeting", "date": "2026-02-01", "project": "Apollo"},
         newline="\r\n"),
    note("Archive/Old Project.md", 'project_name: Legacy\nstatus: archived\n',
         {"project_name": "Legacy", "status": "archived"}),
    note("Archive/Merged Candidate.md",
         'type: project\nproject: Apollo Legacy\nproject_name: Legacy Apollo\n'
         'status: archived\n',
         {"type": "project", "project": "Apollo Legacy",
          "project_name": "Legacy Apollo", "status": "archived"}),
    note("Notes/No Properties.md", None, {}, status="no_frontmatter"),
    note("Notes/Empty Frontmatter.md", "", {}, status="empty_frontmatter"),
    note("Notes/Malformed.md", 'title: "unclosed\nstatus: [broken\n', {},
         status="invalid_yaml"),
    note("Notes/Unterminated.md", None, {}, status="unterminated_frontmatter",
         body="---\ntype: note\nstatus: active\nThis block never closes.\n"),
    note("Notes/Not A Mapping.md", '- just\n- a\n- list\n', {}, status="not_a_mapping"),
    note("Notes/Duplicate Key.md", 'type: note\nstatus: draft\nstatus: final\n',
         {"type": "note", "status": "<ambiguous>"}, duplicate_keys=("status",)),
    note("Notes/Nested Structure.md", 'type: note\ncontact:\n  email: a@example.com\n',
         {"type": "note", "contact": "<unsupported>"}),
    note("Inbox/Ambiguous Target.md", 'type: note\nproject: "[[Duplicate Name]]"\n',
         {"type": "note", "project": "[[Duplicate Name]]"}),
    note("A/Duplicate Name.md", 'type: note\n', {"type": "note"}),
    note("B/Duplicate Name.md", 'type: note\n', {"type": "note"}),
    note("Equipment/Microscope.md",
         'type: equipment\nlocation: Lab\nproject: Apollo\n'
         'purchase_date: 2024-05-01\nserial_number: SN-001\n',
         {"type": "equipment", "location": "Lab", "project": "Apollo",
          "purchase_date": "2024-05-01", "serial_number": "SN-001"}),
    note("Equipment/Oscilloscope.md",
         'type: equipment\nlocation: lab\nproject: "[[Apollo]]"\n'
         'purchase_date: 2023-11-20\nserial_number: SN-002\n',
         {"type": "equipment", "location": "lab", "project": "[[Apollo]]",
          "purchase_date": "2023-11-20", "serial_number": "SN-002"}),
]

EMPTY_NOTES: list[Note] = [
    note("Daily/2026-01-01.md", None, {}, status="no_frontmatter"),
    note("Daily/2026-01-02.md", None, {}, status="no_frontmatter"),
    note("Ideas/隨手筆記.md", None, {}, status="no_frontmatter",
         body="沒有屬性的筆記。\n"),
]

#: files that exist in the vault but must never be scanned as notes
NON_NOTE_FILES = {
    ".obsidian/app.json": '{"promptDelete": false}\n',
    ".obsidian/workspace.json": '{"main": {}}\n',
    ".trash/Deleted Note.md": "---\ntype: trashed\n---\nGone.\n",
    "Attachments/diagram.png": None,          # binary
    "Attachments/notes.txt": "not markdown\n",
}


def write_vault(target: str, notes: list[Note], extras: dict[str, str | None] | None = None):
    if os.path.isdir(target):
        shutil.rmtree(target)
    for spec in notes:
        full = os.path.join(target, *spec["path"].split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        text = ""
        if spec["frontmatter"] is not None:
            text += "---\n" + spec["frontmatter"] + "---\n\n"
        text += spec["body"]
        if spec["newline"] != "\n":
            text = text.replace("\n", spec["newline"])
        with open(full, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    for rel, content in (extras or {}).items():
        full = os.path.join(target, *rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if content is None:
            with open(full, "wb") as fh:
                fh.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
        else:
            with open(full, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)


def build_oracle(notes: list[Note]) -> dict:
    """Independent expectations derived from the spec (not from the product)."""
    failed = {"invalid_yaml", "unterminated_frontmatter", "not_a_mapping", "unreadable"}
    usage: dict[str, int] = {}
    notes_with_props = 0
    for spec in notes:
        declared = spec["declared"]
        if declared:
            notes_with_props += 1
        for key in declared:
            usage[key] = usage.get(key, 0) + 1
    return {
        "note_count": len(notes),
        "notes_with_properties": notes_with_props,
        "notes_with_parse_failure": sum(1 for n in notes if n["status"] in failed),
        "unique_property_keys": sorted(usage),
        "property_usage": dict(sorted(usage.items())),
        "parse_status_by_note": {n["path"]: n["status"] for n in sorted(notes, key=lambda s: s["path"])},
        "duplicate_keys_by_note": {
            n["path"]: n["duplicate_keys"] for n in notes if n["duplicate_keys"]
        },
    }


def main() -> int:
    main_vault = os.path.join(FIXTURES, "main_vault")
    empty_vault = os.path.join(FIXTURES, "empty_vault")
    write_vault(main_vault, MAIN_NOTES, NON_NOTE_FILES)
    write_vault(empty_vault, EMPTY_NOTES)

    oracles = {
        "main_vault": build_oracle(MAIN_NOTES),
        "empty_vault": build_oracle(EMPTY_NOTES),
    }
    oracle_path = os.path.join(FIXTURES, "oracle.json")
    with open(oracle_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(oracles, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    print(f"main_vault: {oracles['main_vault']['note_count']} notes")
    print(f"empty_vault: {oracles['empty_vault']['note_count']} notes")
    print(f"oracle -> {oracle_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
