# Known Limitations — v1.2.0

These are deliberate architectural boundaries and honest functional limitations of **Obsidian Property Studio v1.2.0**. Nothing here is hidden behind misleading defaults.

---

## 1. Out of Scope by Decision (PROJECT.md §4, DEC-001…DEC-032)

1. **Standalone Application (Not an Obsidian Plugin):** Property Studio is a standalone local application running via Python and your web browser; it does not integrate with the Obsidian Community Plugin API.
2. **No Automatic Vault Writes:** There is no "Apply Migration" button, no automatic note creation, no file rename/move/delete, and no `.obsidian/` configuration tampering. All frontmatter updates are previewed, diffed, and copied by the user manually.
3. **No Prose or Note Body Generation:** The application governs the frontmatter property layer only; note body text, headings, sections, and writing templates are strictly out of scope.
4. **No Note Merging or Entity Unification:** The system does not merge notes together or resolve physical entity identities across files.
5. **No Attachment or Media Management:** The tool does not manage binary files, image attachments, or orphaned media.
6. **No Body Wikilink Rewriting:** Body Wikilink analysis (`[[Wikilinks]]`) is strictly read-only diagnostics; the application never rewrites Markdown note bodies.
7. **Not a Dataview or Bases Replacement:** Property Studio focuses on property schema design, health, and governance, not real-time query rendering or database table views.
8. **No Cloud Sync, SaaS, Telemetry, or Required LLM:** Property Studio runs 100% offline and local-first with zero telemetry and zero required external API keys.
9. **No Installer Executable:** Packaged as clean source ZIP and Git bundle archives, executed via standard Python runtime (`run_windows.bat` or `python -m app`).

---

## 2. Functional Limitations You Should Know About

* **Frontmatter-Only Property Discovery:** Inline Dataview-style `key:: value` annotations in note bodies are deliberately not parsed, as they are not native Obsidian frontmatter properties.
* **Semantic Similarity is Advisory and Heuristic:** Detecting potential property overlap (e.g. `project` vs `project_name`) relies on tokenized edit-distance heuristics; the application never merges properties or asserts they mean the same thing.
* **Value Normalization Groups Exact Case/Whitespace Variants:** Normalization groups variants like `active`, `Active`, and `ACTIVE`; it will never infer that `active` and `in progress` are the same value.
* **Duplicate YAML Keys Fail Closed:** Notes defining duplicate YAML keys fail closed: they are excluded from refactor plans and reported as ambiguity findings rather than parsed with an arbitrary winner.
* **Note-Link Resolution Uses Vault-Relative Paths:** Obsidian's "shortest path when possible" heuristic and custom per-vault link settings are not simulated; ambiguous note basenames fail closed as ambiguous.
* **Frontmatter Scan Window:** Only the first 256 KB of a note is inspected when locating the frontmatter block. A note whose frontmatter is not closed within that window is reported as unterminated.
* **Non-UTF-8 Notes Reported as Unreadable:** Files with character encoding failures are reported as unreadable parse failures rather than silently re-encoded or corrupted.
* **Hidden Folders Skipped:** Dot-prefixed folders (e.g. `.obsidian/`, `.trash/`) are ignored by default, mirroring Obsidian's core behavior.
* **Symlinks and Junctions Not Followed:** Symlinked files or directories inside the vault are skipped to prevent directory loops and unexpected mutations.
* **Health Score is an Explainable Heuristic:** The 0–100 health score is a transparent weighted indicator; individual diagnostic findings, not the composite number, are the real actionable output.
* **Governance Storage Lives Outside the Vault:** 
  - Unsaved Designer schemas live only in transient browser session memory.
  - Saved Named Schemas, Scope assignments, Glossary overrides, and Saved Checks persist safely in application-local storage outside the Vault (`%APPDATA%\ObsidianPropertyStudio\` on Windows or `~/.property_studio/` on macOS/Linux).
* **Governance Profile UX Workflow:**
  - Exporting a Governance Profile copies or downloads the validated whole-system JSON package rather than opening a native operating system Save-As file dialog.
  - Governance Profiles are full-governance snapshots (encompassing schemas, scopes, glossary overrides, saved checks, and preferences); selective partial-entity exporting is not supported.
* **Single-User Local Application:** No authentication is implemented, which is why the server binds strictly to `127.0.0.1` (loopback) by default. It should not be exposed to a public network.

---

## 3. Measured Performance (Evidence, Not a Hard Gate)

Authoritative performance benchmarks are recorded in [m022_v120_benchmark.json](../evidence/integration/m022_v120_benchmark.json):
* **Fixture Size:** 5,040 synthetic notes.
* **Total Analysis Time:** ~5.844 seconds (Scan time: ~5.667 seconds).
* **Vault Integrity:** 100% byte-for-byte read-only (0 files created, 0 modified, 0 deleted).
* **Policy Reminder:** `PROJECT.md` sets no arbitrary seconds threshold; runtime scales roughly linearly with note count and frontmatter complexity.

---

## 4. Platform Verification Status

* **Windows 10 (Build 19045+, 64-bit AMD64):** `PASS — Human Verified` (253 automated tests, 5,040-note benchmark, and all 16 recorded human acceptance findings verified by Human Owner Dr. J).
* **Windows 11 (64-bit AMD64):** Supported target platform. Native execution verification has not yet been executed due to test host machine availability (accepted non-blocking release limitation).
* **macOS / Linux:** Expected to run cleanly via standard Python (`python3 -m app` / `run.sh`); native human acceptance for v1.2.0 was performed on Windows 10.
