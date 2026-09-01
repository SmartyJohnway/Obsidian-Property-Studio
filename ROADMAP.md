# Roadmap

> Project: `Obsidian Property Studio`  
> Target Release: `v1.1.0`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Roadmap Type: `v1.1.0 Product & UI/UX vNext Execution Roadmap`  
> Baseline: `v1.0.0 Formal Mainline (95/95 tests PASS)`  
> UX/Visual Donors: `index_areaagentB.html (UX donor)`, `index_areaagentD.html (Visual donor)`

---

#### Current State

Project State: `ACTIVE`  
Current Milestone: `M008 — Body Wikilink Relationship Analysis (Strict Read-Only)`  
Current Milestone Status: `IN_PROGRESS`  
Current Task: `M008-T01`  
Last Verified Gate: `M007 — Scope-Aware Relationship Analysis PASS` (Baseline: `M001 PASS`)  
Current Blocker: `None`  
Next Action: `Implement Body Wikilink extractor in app/core/body_links.py, separate Property Link and Body Wikilink results, and implement V11-012..013 regression tests.`  
Last Updated: `2026-09-01`

---

# 1. Authority & Governance Boundaries

This ROADMAP is the sole active authoritative execution plan for `Obsidian Property Studio v1.1.0`.

- `PROJECT.md` defines accepted v1.1.0 Product Truth, Scope, and Non-goals.
- `ROADMAP.md` (this file) defines milestone execution, acceptance criteria, and evidence.
- `HANDOFF.md` tracks the latest runtime recovery context.
- `AGENTS.md` governs agent operating behavior.
- `docs/archive/ROADMAP_v1.0.0.md` is an immutable historical snapshot and no longer tracks current progress.
- `Obsidian_Property_Studio_v1.1.0_UIUX_vNext_Design_Spec.md` is the formal product and UI/UX design specification for v1.1.0.
- `index_areaagentB.html` and `index_areaagentD.html` are visual/UX donors only; neither has functional or architectural authority.

---

# 2. Closed Status Vocabulary

Milestone Status:
```text
PLANNED
IN_PROGRESS
HOLD
PASS
SUPERSEDED
```

Result / Verification State:
```text
NOT YET VERIFIED
PASS
HOLD
SUPERSEDED
```

Project State:
```text
ACTIVE
HOLD
COMPLETE
```

---

# 3. v1.1.0 Engineering Regression Contracts

All 95 v1.0.0 regression tests are permanently retained. v1.1.0 introduces 18 new regression contracts:

- `V11-001` i18n zh-Hant / English seamless switch with deterministic local key resolution (no CDN, localStorage preference).
- `V11-002` Multi-folder Scope correctly calculates union of selected folders and deduplicates overlapping notes.
- `V11-003` Nested folder `include_subfolders` true/false filter semantics correctly enforced.
- `V11-004` Scope filtering operates in-memory and does not trigger full Vault disk rescan.
- `V11-005` Note selector handles duplicate base names across folders without auto-guessing (requires explicit path).
- `V11-006` Existing Note Property Workspace preserves unrelated frontmatter properties across edits and diffs.
- `V11-007` Existing Note Property Workspace fails closed on notes with duplicate keys or malformed frontmatter.
- `V11-008` Note Property Workspace disables Copy action when frontmatter preview/validation is invalid.
- `V11-009` Relationship Source Scope correctly accepts multiple folder roots.
- `V11-010` Relationship Target Scope correctly accepts multiple folder roots.
- `V11-011` Relationship analysis marks resolved links outside selected Target Scope as `OUTSIDE SELECTED TARGET`.
- `V11-012` Property Links and Body Wikilinks analysis results are strictly separated in models and UI.
- `V11-013` Body Wikilink analysis is strictly read-only and never modifies Markdown note bodies.
- `V11-014` System starts with zero default relationship rules or ontology assumptions.
- `V11-015` Saved Relationship Checks persist correctly to external storage (outside Vault) and reload accurately.
- `V11-016` Scope-aware Property Health calculates scores and findings strictly from Scope notes without cross-contamination.
- `V11-017` Scope-aware Refactor Planner strictly limits migration plans to Scope notes without silent expansion.
- `V11-018` Vault remains byte-for-byte read-only across all v1.1.0 product workflows (pre/post hash equality).

---

# M001 — v1.1.0 Governance Transition & Baseline Freeze

Status: `PASS`

### Objective
Establish the formal v1.1.0 governance baseline, archive the v1.0.0 roadmap, update PROJECT.md, AGENTS.md, ROADMAP.md, and verify existing 95-test baseline before modifying code.

### Tasks
- [x] `M001-T01` Re-enter project following mandatory order: PROJECT → ROADMAP → AGENTS → HANDOFF → git status/log → test suite.
- [x] `M001-T02` Inspect `Obsidian_Property_Studio_v1.1.0_UIUX_vNext_Design_Spec.md`, `index_areaagentB.html`, and `index_areaagentD.html`.
- [x] `M001-T03` Archive v1.0.0 ROADMAP.md to `docs/archive/ROADMAP_v1.0.0.md` and verify file hash.
- [x] `M001-T04` Update `PROJECT.md` with v1.1.0 Product Truth, Scope, Success Criteria (SC-16..22), Requirements (REQ-024..035), Non-goals, and Decisions (DEC-021..029).
- [x] `M001-T05` Author new v1.1.0 active `ROADMAP.md` with discrete milestones M001~M012.
- [x] `M001-T06` Update `AGENTS.md` Part B with v1.1.0 specific operating rules and donor boundaries.
- [x] `M001-T07` Verify baseline test suite (all 95 v1.0.0 tests PASS).
- [x] `M001-T08` Execute four-file consistency check.
- [x] `M001-T09` Update `HANDOFF.md` last with current checkpoint.

### Acceptance Criteria
- [x] `M001-AC01` `docs/archive/ROADMAP_v1.0.0.md` exists and matches historical v1.0.0 final hash.
- [x] `M001-AC02` `PROJECT.md` accurately reflects accepted v1.1.0 truth without weakening safety contracts.
- [x] `M001-AC03` `ROADMAP.md` is active for v1.1.0 with granular milestones and test contracts.
- [x] `M001-AC04` Baseline tests (95 items) executed and passing in formal repository.
- [x] `M001-AC05` Four-file consistency gate satisfied.

### Verification / Evidence
- `docs/archive/ROADMAP_v1.0.0.md` (SHA-256: `6ED8CCF707ACDAF0CBD8B7E1D91D3B41CF2E823B371D6B1EFA26CF69493FFC64`)
- Test baseline run: 95 passed in 13.43s (pytest on Python 3.13.7)

### Result
`PASS`

---

# M002 — Modern UI Shell & Design System (Visual Hierarchy & Navigation)

Status: `PASS`

### Objective
Implement the v1.1.0 modern UI shell in `app/ui/` by harvesting visual hierarchy from Donor D and navigation/workflow patterns from Donor B, without embedding mock data or compromising existing API integration.

### Tasks
- [x] `M002-T01` Design unified layout structure: Sidebar with categories (Overview, Context, Create, Govern, Advanced), Top Context Bar, Main Container, Right Drawer.
- [x] `M002-T02` Implement CSS Design Tokens for typography, spacing, elevations, card surfaces, and status badges.
- [x] `M002-T03` Implement Persistent Context Bar displaying current Vault, Scope, and Selected Note.
- [x] `M002-T04` Implement generic Right Drawer component for deep property/finding inspection with keyboard (Esc) accessibility.
- [x] `M002-T05` Implement Home / Overview screen with quick-action cards and summary metrics.
- [x] `M002-T06` Implement universal module state containers (Initial, Loading skeleton, Ready, Empty, Blocked, Error).
- [x] `M002-T07` Ensure responsive layout (1024px desktop and collapsed navigation support).
- [x] `M002-T08` Run UI integrity tests and verify no mock/demo backend contamination.

### Acceptance Criteria
- [x] `M002-AC01` UI shell renders cleanly with Sidebar categories, Persistent Context Bar, and Right Drawer.
- [x] `M002-AC02` Right Drawer opens and closes smoothly, including Esc key support.
- [x] `M002-AC03` Universal loading/empty/error states render without visual glitch.
- [x] `M002-AC04` No mock backend or fake API logic exists in production UI scripts.
- [x] `M002-AC05` All 95 existing tests continue to PASS.

### Verification / Evidence
- `tests/test_ui_integrity.py` (7/7 tests passed in 0.18s)
- Full automated test suite (95/95 passed in 12.10s)

### Result
`PASS`

---

# M003 — Lightweight Bilingual i18n & Theme Engine

Status: `PASS`

### Objective
Implement lightweight, local-first bilingual support (zh-Hant / English) and Light / Dark theme switching with localStorage persistence and no CDN dependencies.

### Tasks
- [x] `M003-T01` Create `app/ui/i18n.js` client translation engine supporting key lookup and parameter interpolation (`{count}`).
- [x] `M003-T02` Author complete `app/ui/locales/zh-Hant.json` translation dictionary.
- [x] `M003-T03` Author complete `app/ui/locales/en.json` translation dictionary.
- [x] `M003-T04` Wire i18n switcher in top navigation, updating `<html lang>` and localStorage.
- [x] `M003-T05` Implement Light / Dark theme CSS variables and theme toggle in top bar.
- [x] `M003-T06` Ensure dynamic alerts, validation toasts, and backend error codes resolve through i18n.
- [x] `M003-T07` Implement regression test `V11-001` (i18n switch & locale integrity).
- [x] `M003-T08` Verify contrast and accessibility in both Light and Dark themes.

### Acceptance Criteria
- [x] `M003-AC01` `V11-001` PASS.
- [x] `M003-AC02` UI seamlessly toggles between zh-Hant and English without page reload.
- [x] `M003-AC03` HTML does not duplicate complete bilingual DOM trees.
- [x] `M003-AC04` Light and Dark themes toggle cleanly and persist across sessions.
- [x] `M003-AC05` No external font/script/style CDN requests are made.

### Verification / Evidence
- `tests/test_v11_i18n.py` (4/4 tests passed in 0.05s)
- Full automated test suite (99/99 passed in 11.69s)

### Result
`PASS`

---

# M004 — Formal Scope Domain Model & In-Memory Engine

Status: `PASS`

### Objective
Implement the backend Scope domain model (`ScopeSpec`), supporting Entire Vault, One Folder, Multi-Folder, Single Note, and `include_subfolders` with in-memory derivation without full Vault rescans.

### Tasks
- [x] `M004-T01` Define backend `ScopeSpec` domain dataclass and validation schema in `app/core/scope.py`.
- [x] `M004-T02` Implement Scope evaluation engine: folder matching, subfolder recursion, note path union, and deduplication.
- [x] `M004-T03` Implement in-memory Scope filter over `ScanResult` indexes (notes, properties, links).
- [x] `M004-T04` Expose Scope configuration and note listing endpoints in backend server API.
- [x] `M004-T05` Implement backend tests for Multi-folder union and nested subfolder logic.
- [x] `M004-T06` Implement `V11-002` (multi-folder union/dedupe), `V11-003` (subfolder filter semantics), and `V11-004` (in-memory Scope derivation without disk rescan).
- [x] `M004-T07` Integrate Scope Selector modal/drawer in UI Context section.

### Acceptance Criteria
- [x] `M004-AC01` `V11-002` PASS.
- [x] `M004-AC02` `V11-003` PASS.
- [x] `M004-AC03` `V11-004` PASS.
- [x] `M004-AC04` Multi-folder Scope accurately unions note sets and deduplicates overlapping paths.
- [x] `M004-AC05` Scope switching does not trigger disk I/O rescan.

### Verification / Evidence
- `tests/test_v11_scope.py` (5/5 tests passed in 0.06s)
- Full automated test suite (104/104 passed in 12.34s)

### Result
`PASS`

---

# M005 — Scope-Aware Discover & Property Health

Status: `PASS`

### Objective
Update Discover and Health modules to calculate metrics, property inventories, and health scores strictly within the active Scope, with global context comparison and drawer drill-down.

### Tasks
- [x] `M005-T01` Update Discover API/engine to compute scope-filtered property inventory, usage counts, and type distributions.
- [x] `M005-T02` Include global Vault comparison counters (e.g. scope count vs total vault count) in Discover output.
- [x] `M005-T03` Update Health calculation to evaluate only Scope notes while retaining clear explainable metrics.
- [x] `M005-T04` Connect UI Discover and Health screens to Scope-aware APIs.
- [x] `M005-T05` Implement Right Drawer drill-down for property details and health findings.
- [x] `M005-T06` Implement quick navigation action from finding/property note list directly into Note Properties Workspace.
- [x] `M005-T07` Implement `V11-016` (Scope-aware Health isolation).
- [x] `M005-T08` Run full test suite and verify no cross-scope data contamination.

### Acceptance Criteria
- [x] `M005-AC01` `V11-016` PASS.
- [x] `M005-AC02` Discover inventory accurately reflects active Scope.
- [x] `M005-AC03` Health score and issues calculate exclusively from Scope notes.
- [x] `M005-AC04` Drawer drill-down allows clicking a note to open in Note Properties Workspace.

### Verification / Evidence
- `tests/test_v11_discover_health.py` (1/1 test passed in 0.07s)
- Full automated test suite (105/105 passed in 11.45s)

### Result
`PASS`

---

# M006 — Note Properties Workspace (Existing Note & Blank Modes)

Status: `PASS`

### Objective
Implement the single-note Property Workspace supporting Existing Note inspection/editing with semantic diff and fail-closed corrupt-frontmatter protection, as well as New/Blank fill.

### Tasks
- [x] `M006-T01` Implement note search and retrieval backend supporting filename and relative path lookup.
- [x] `M006-T02` Implement note selection消歧義 logic (distinguishing duplicate basenames across different folders).
- [x] `M006-T03` Implement Existing Note frontmatter parser and semantic editor in `app/core/note_workspace.py`.
- [x] `M006-T04` Implement semantic frontmatter diff generator (comparing original vs updated properties).
- [x] `M006-T05` Implement fail-closed protection: reject editing if note has duplicate keys, unreadable YAML, or parse errors.
- [x] `M006-T06` Implement New/Blank Fill mode preserving v1.0.0 schema-based creation flow.
- [x] `M006-T07` Connect Note Properties Workspace UI with Existing/Blank mode switcher, property form, diff view, and Copy button.
- [x] `M006-T08` Implement `V11-005` (note selector ambiguity), `V11-006` (unrelated property preservation), `V11-007` (duplicate-key fail-closed), and `V11-008` (invalid fill copy disabled).
- [x] `M006-T09` Verify Vault remains 100% untouched during note inspection, editing, and preview.

### Acceptance Criteria
- [x] `M006-AC01` `V11-005` PASS.
- [x] `M006-AC02` `V11-006` PASS.
- [x] `M006-AC03` `V11-007` PASS.
- [x] `M006-AC04` `V11-008` PASS.
- [x] `M006-AC05` Existing note properties edit cleanly with visual semantic diff and copyable frontmatter.
- [x] `M006-AC06` Corrupted/duplicate-key frontmatter is rejected fail-closed with clear error explanation.
- [x] `M006-AC07` Note body is never modified.

### Verification / Evidence
- `tests/test_v11_note_workspace.py` (4/4 tests passed in 0.08s)
- Full automated test suite (109/109 passed in 12.78s)

### Result
`PASS`

---

# M007 — Scope-Aware Relationship Analysis (Property Links)

Status: `PASS`

### Objective
Upgrade Relationship Analysis to support custom Multi-folder Source Scope and Multi-folder Target Scope, categorizing Property Link findings into VALID, BROKEN, AMBIGUOUS, and OUTSIDE SELECTED TARGET without default rules.

### Tasks
- [x] `M007-T01` Update Relationship engine in `app/core/relationships.py` to accept `source_scope` and `target_scope`.
- [x] `M007-T02` Implement target location evaluation: check whether resolved note falls within selected `target_scope`.
- [x] `M007-T03` Implement four-way status classifier: `VALID`, `BROKEN`, `AMBIGUOUS`, and `OUTSIDE_SELECTED_TARGET`.
- [x] `M007-T04` Implement Relationship UI with Source Scope selector, Target Scope selector, Property selector, and Analyze button.
- [x] `M007-T05` Confirm zero default rules or assumptions are loaded on fresh startup.
- [x] `M007-T06` Implement `V11-009` (multi-folder Source Scope), `V11-010` (multi-folder Target Scope), and `V11-011` (target outside scope classification).
- [x] `M007-T07` Run full suite and verify existing relationship tests PASS.

### Acceptance Criteria
- [x] `M007-AC01` `V11-009` PASS.
- [x] `M007-AC02` `V11-010` PASS.
- [x] `M007-AC03` `V11-011` PASS.
- [x] `M007-AC04` Multi-folder Source and Target Scopes analyze accurately.
- [x] `M007-AC05` Links resolving outside Target Scope are explicitly categorized as `OUTSIDE SELECTED TARGET`.
- [x] `M007-AC06` No default relationship rules exist.

### Verification / Evidence
- `tests/test_v11_relationships.py` (3/3 tests passed in 0.09s)
- Full automated test suite (112/112 passed in 13.29s)

### Result
`PASS`

---

# M008 — Body Wikilink Relationship Analysis (Strict Read-Only)

Status: `PLANNED`

### Objective
Implement Body Wikilink Analysis allowing users to analyze `[[Wikilinks]]` inside Markdown note bodies across Source and Target Scopes, keeping analysis strictly read-only and strictly separated from Property Links.

### Tasks
- [ ] `M008-T01` Implement lightweight Markdown body Wikilink extractor in `app/core/body_links.py`.
- [ ] `M008-T02` Connect extracted body links to Scope-aware relationship analyzer.
- [ ] `M008-T03` Separate Property Link findings and Body Wikilink findings in domain models and API responses.
- [ ] `M008-T04` Update UI Relationships view to offer Relationship Source toggle (Property Links / Body Wikilinks) or separated tabs.
- [ ] `M008-T05` Implement `V11-012` (Property Link / Body Wikilink result separation).
- [ ] `M008-T06` Implement `V11-013` (strict read-only body analysis; zero byte changes to note bodies).
- [ ] `M008-T07` Verify that no feature, API, or button exists to rewrite prose or auto-repair body links.

### Acceptance Criteria
- [ ] `M008-AC01` `V11-012` PASS.
- [ ] `M008-AC02` `V11-013` PASS.
- [ ] `M008-AC03` Body Wikilinks are correctly extracted and analyzed across Scopes.
- [ ] `M008-AC04` Property Links and Body Wikilinks are displayed with separate metrics and labels.
- [ ] `M008-AC05` Note bodies are strictly read-only and never modified.

### Result
`NOT YET VERIFIED`

---

# M009 — Saved Relationship Checks Management

Status: `PLANNED`

### Objective
Implement user-initiated Saved Relationship Checks allowing users to name, annotate, save, reload, and re-execute ad-hoc relationship queries, stored entirely outside the Vault.

### Tasks
- [ ] `M009-T01` Define versioned schema for Saved Relationship Checks (name, notes, source_scope, target_scope, link_type, property_name, created_at).
- [ ] `M009-T02` Implement client/backend persistence layer for Saved Checks (localStorage / application app-data outside Vault).
- [ ] `M009-T03` Implement UI "Save this check" action in Relationship analysis view.
- [ ] `M009-T04` Implement Saved Checks management panel (list, execute, edit notes, delete/archive, export/import).
- [ ] `M009-T05` Implement `V11-014` (no default saved checks on clean initialization).
- [ ] `M009-T06` Implement `V11-015` (round-trip persistence and execution of saved checks).
- [ ] `M009-T07` Confirm results remain advisory with no enforced violation semantics.

### Acceptance Criteria
- [ ] `M009-AC01` `V11-014` PASS.
- [ ] `M009-AC02` `V11-015` PASS.
- [ ] `M009-AC03` User can save, re-run, annotate, and delete relationship checks.
- [ ] `M009-AC04` Saved checks are never written into the Vault directory.
- [ ] `M009-AC05` Saved checks are purely advisory.

### Result
`NOT YET VERIFIED`

---

# M010 — Scope-Aware Property Refactor Planner

Status: `PLANNED`

### Objective
Update the Property Refactor Planner to operate strictly within the selected Scope, disclosing in-scope vs out-of-scope counts and preventing silent scope expansion.

### Tasks
- [ ] `M010-T01` Update Refactor Planner in `app/core/refactor.py` to accept Scope boundaries.
- [ ] `M010-T02` Compute affected note count in Scope alongside informative out-of-scope usage count.
- [ ] `M010-T03` Ensure generated migration plan files list only Scope notes.
- [ ] `M010-T04` Update Refactor UI to display active Scope and prevent silent whole-vault expansion.
- [ ] `M010-T05` Implement `V11-017` (Scope-aware Refactor does not expand scope).
- [ ] `M010-T06` Verify duplicate-key and malformed note manual-review propagation remains fail-closed.

### Acceptance Criteria
- [ ] `M010-AC01` `V11-017` PASS.
- [ ] `M010-AC02` Refactor plans list strictly in-Scope notes.
- [ ] `M010-AC03` Out-of-scope note counts are clearly indicated as not included in the plan.
- [ ] `M010-AC04` All v1.0.0 refactor conflict and manual-review contracts are preserved.

### Result
`NOT YET VERIFIED`

---

# M011 — Full Regression Suite, Large-Vault Benchmark & Read-Only Verification

Status: `PLANNED`

### Objective
Execute the complete regression test suite (95 v1.0.0 tests + 18 v1.1.0 tests), run the ≥5,000-note performance benchmark, and verify byte-for-byte Vault read-only integrity.

### Tasks
- [ ] `M011-T01` Run full automated test suite (all 95 v1.0.0 tests + `V11-001`..`V11-018`).
- [ ] `M011-T02` Execute pre/post SHA-256 Vault manifest verification across all v1.1.0 workflows (`V11-018`).
- [ ] `M011-T03` Run deterministic repeat-scan test across varied Scope configurations.
- [ ] `M011-T04` Run output read-back verification on Scope-aware reports, Health exports, and Refactor plans.
- [ ] `M011-T05` Run ≥5,000-note synthetic benchmark and record scan and Scope-filtering timings.
- [ ] `M011-T06` Verify complete offline execution without network or API keys.
- [ ] `M011-T07` Generate formal integration evidence file `evidence/integration/m011_v110_formal_verification.json`.

### Acceptance Criteria
- [ ] `M011-AC01` All 113+ automated tests PASS with zero failures.
- [ ] `M011-AC02` `V11-018` PASS (Vault modified count = 0).
- [ ] `M011-AC03` Determinism and export read-back PASS.
- [ ] `M011-AC04` 5,000-note benchmark completes and is documented.
- [ ] `M011-AC05` Zero network/AI requirements verified.

### Result
`NOT YET VERIFIED`

---

# M012 — Windows 10 / 11 Native Acceptance & v1.1.0 Release Closure

Status: `PLANNED`

### Objective
Validate v1.1.0 native execution on Windows 10 (Build 19045+) / Windows 11, execute UI acceptance, update documentation, conduct four-file consistency check, package release artifacts, and record formal release verdict.

### Tasks
- [ ] `M012-T01` Test `run_windows.bat` launcher natively on Windows environment.
- [ ] `M012-T02` Execute full end-to-end UI acceptance walkthrough (Scope selection, Note Workspace editing, Relationship analysis, Saved Checks, i18n toggle, Light/Dark toggle).
- [ ] `M012-T03` Verify Traditional Chinese paths, spaces in folder names, and Unicode property values.
- [ ] `M012-T04` Update `README.md` and user documentation for v1.1.0 features.
- [ ] `M012-T05` Freeze version string `1.1.0` in `app/__init__.py` and UI metadata.
- [ ] `M012-T06` Run four-file consistency check (PROJECT, ROADMAP, HANDOFF, AGENTS).
- [ ] `M012-T07` Generate release manifest and packaging bundles (`Obsidian-Property-Studio-v1.1.0-source.zip`, git bundle).
- [ ] `M012-T08` Update ROADMAP final state to COMPLETE and record release verdict.
- [ ] `M012-T09` Update HANDOFF.md last.

### Acceptance Criteria
- [ ] `M012-AC01` Windows 10 (Build 19045+) native launcher and UI acceptance freshly verified.
- [ ] `M012-AC02` Windows 11 (64-bit AMD64) recorded accurately as `NOT YET VERIFIED` (accepted non-blocking release limitation if test machine unavailable).
- [ ] `M012-AC03` Traditional Chinese and English UI verified end-to-end.
- [ ] `M012-AC04` Documentation matches implementation.
- [ ] `M012-AC05` Four-file consistency gate PASS.
- [ ] `M012-AC06` Release manifest and bundles verified.
- [ ] `M012-AC07` Formal release verdict recorded (`PROPERTY_STUDIO_V1_1_0_RELEASE_PASS_WITH_LIMITATIONS` or `PASS`).

### Result
`NOT YET VERIFIED`

---

# 4. Final v1.1.0 Integration Summary

The v1.1.0 release evolves Obsidian Property Studio from a Whole-Vault Property Tool into a **Context-Aware Bilingual Property Governance Workspace**:

```text
Vault
  │
  ├─ Scope (Entire Vault, One Folder, Multi-Folder, Single Note)
  │
  ├─ Note Properties Workspace (Existing Note Inspect/Edit/Diff + Blank Fill)
  │
  └─ Relationships
       │
       ├─ Property Links (Source Scope → Target Scope)
       ├─ Body Wikilinks (Analysis-only, Strict Read-only)
       │
       └─ Saved Relationship Checks (User-initiated, Reusable, Outside Vault)
```

No evidence, no PASS.  
No contradictory evidence, no PASS.
