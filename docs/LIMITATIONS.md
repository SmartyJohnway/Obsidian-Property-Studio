# Known limitations — v1.0.0

These are deliberate boundaries or honest gaps. Nothing here is hidden behind a friendly default.

## Out of scope by decision (PROJECT.md §4, DEC-001…DEC-008)

1. **No Obsidian plugin.** Property Studio is a standalone local app; it does not integrate with the
   Obsidian plugin API.
2. **No vault modification of any kind.** There is no “apply migration”, no note creation, no
   rename/move/delete, no `.obsidian/` editing. Every change is something *you* paste in yourself.
3. **No note body, heading, section or writing template generation.** The product governs the
   property layer only; your prose stays yours.
4. **No note merging / note identity resolution.**
5. **No attachment or media management** (no orphan cleanup, no attachment rename/move).
6. **No body-text backlink rewriting.** The Relationship Inbox only looks at property values.
7. **Not a Dataview or Bases replacement**, and not a task manager.
8. **No cloud sync, no SaaS, no telemetry, no required LLM/API key.**

## Functional limitations you should know about

* **Property discovery is frontmatter-only.** Inline `key:: value` (Dataview-style) fields in note
  bodies are not parsed, because they are not Obsidian Properties.
* **Semantic similarity is deliberately shallow.** `project` vs `project_name` is reported as a
  *possible overlap* using name-token/edit-distance heuristics; the product never claims two
  differently-named properties mean the same thing, and never merges them.
* **Value normalization groups case/whitespace variants only.** `active`/`Active`/`ACTIVE` group;
  `active` and `in progress` never do.
* **Duplicate YAML keys fail closed.** A note that defines the same property twice is excluded from
  plans that depend on that property, and is reported as an ambiguity instead.
* **Note-link resolution uses note name and vault-relative path.** Obsidian's "shortest path when
  possible" resolution and per-vault link settings are not simulated; ambiguous names are reported
  as ambiguous rather than resolved with a guess.
* **Only the first 256 KB of a note is inspected** when locating the frontmatter block. A note whose
  frontmatter is not closed within that window is reported as unterminated.
* **Non-UTF-8 notes are reported as unreadable**, not silently skipped or re-encoded.
* **Hidden folders (names starting with `.`) are skipped**, as Obsidian itself ignores them. Each
  skipped path is listed with a reason.
* **Symlinks / junctions are never followed.** A symlinked file or folder inside the vault is listed
  as skipped; nothing outside the vault is scanned.
* **The health score is a heuristic summary**, not a verdict. The published formula and every
  weight/cap are shown next to the score; the findings, not the number, are the real output.
* **The schema you design lives in the browser session.** Export it to JSON to keep it; there is no
  hidden database, and nothing is stored inside your vault.
* **Clipboard copy needs a secure context.** On `http://localhost` browsers allow it; if the
  clipboard API is blocked, the app falls back to a manual selection copy and tells you.
* **Single-user local app.** No authentication is implemented, which is why it binds to
  `127.0.0.1` by default. Do not expose it to a network with `--host`.

## Measured performance (not a guarantee)

`evidence/integration/m009_benchmark.json` records a 5,040-note synthetic vault run with the environment, fixture
size and per-stage timings. PROJECT.md deliberately sets **no accepted seconds threshold** for v1,
so these numbers are evidence, not a pass/fail gate. Runtime scales roughly linearly with note
count; the dominant cost is reading and YAML-parsing each note's frontmatter.

## Platform verification status

* Automated test suite, performance benchmark, and end-to-end UI smoke executed natively on Windows (Windows 10 Build 19045, Python 3.13.7 AMD64) — see evidence recorded under `evidence/integration/`.
* Windows-native behavior (drive-letter paths, `run_windows.bat`, `py` / `python` launcher, loopback binding) is fully implemented and tested. Unicode filenames, Traditional Chinese values, spaces in paths, nested folders and CRLF notes are verified by fixtures and live server smoke tests.
