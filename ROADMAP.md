# Roadmap

> Project: `Obsidian Property Studio`  
> Target Release: `v1.1.0`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Roadmap Type: `v1.1.0 Product & UI/UX vNext Execution Roadmap`  
> Baseline: `v1.0.0 Formal Mainline (95/95 tests PASS)`  
> UX/Visual Donors: `index_areaagentB.html (UX donor)`, `index_areaagentD.html (Visual donor)`

---

##### Current State

Project State: `COMPLETE`  
Current Milestone: `NONE`  
Current Milestone Status: `PASS`  
Current Task: `NONE`  
Last Verified Gate: `M013 — Release Closure In-Place Repair PASS`  
Current Blocker: `NONE`  
Next Action: `PR #1 final merge approval`  
Formal Release Verdict: `PROPERTY_STUDIO_V1_1_0_RELEASE_PASS_WITH_LIMITATIONS`  
Accepted Limitation: `Windows 11 AMD64 native verification recorded as NOT YET VERIFIED due to test host unavailability (accepted non-blocking release limitation per human approved contract).`  
Last Updated: `2026-09-01`

---

# 1. Authority & Governance Boundaries

This ROADMAP is the sole active authoritative execution plan for `Obsidian Property Studio v1.1.0`.

- `PROJECT.md` defines accepted v1.1.0 Product Truth, Scope, and Non-goals.
- `ROADMAP.md` (this file) defines milestone execution, acceptance criteria, and evidence.
- `HANDOFF.md` tracks the latest runtime recovery context.
- `AGENTS.md` governs agent operating behavior.
- `docs/archive/ROADMAP_v1.0.0.md` is an immutable historical snapshot and no longer tracks current progress.
- `docs/specs/Obsidian_Property_Studio_v1.1.0_UIUX_vNext_Design_Spec.md` is the formal product and UI/UX design specification for v1.1.0.
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
- `V11-012` Property Links and Body Wikilinks analysis results are strictly separated in models and API.
- `V11-013` Body Wikilink analysis is strictly read-only and never modifies Markdown note bodies.
- `V11-014` System starts with zero default relationship rules or ontology assumptions.
- `V11-015` Saved Relationship Checks persist correctly to external storage/JSON (outside Vault) and reload accurately.
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
- [x] `M001-T02` Archive `ROADMAP.md` (v1.0.0) to `docs/archive/ROADMAP_v1.0.0.md`.
- [x] `M001-T03` Update `PROJECT.md` with v1.1.0 Scope, Core Capabilities, Success Criteria, and Non-Goals.
- [x] `M001-T04` Update `AGENTS.md` with v1.1.0 donor isolation, supported platforms, and regression IDs.
- [x] `M001-T05` Author new v1.1.0 `ROADMAP.md` with milestones M001 ~ M012.
- [x] `M001-T06` Run baseline test suite (confirm 95/95 pass).
- [x] `M001-T07` Create initial git commit for governance transition.

### Acceptance Criteria
- [x] `M001-AC01` Clean read-order re-entry completed.
- [x] `M001-AC02` Four governance files updated and mutually consistent.
- [x] `M001-AC03` Baseline test suite passes (95/95).
- [x] `M001-AC04` Initial commit completed on `feature/v1.1.0-release`.

### Result
`PASS` (95/95 baseline tests pass, git commit verified)

---

# M002 — Lightweight Local-First Bilingual i18n Engine

Status: `PASS`

### Objective
Implement a local-first, zero-CDN, offline bilingual (Traditional Chinese zh-Hant / English en) i18n architecture.

### Tasks
- [x] `M002-T01` Define regression test `tests/test_v11_i18n.py` covering V11-001.
- [x] `M002-T02` Create structured locale dictionaries `app/ui/locales/zh-Hant.json` and `app/ui/locales/en.json`.
- [x] `M002-T03` Implement client-side translation loader `app/ui/i18n.js` with `localStorage` language preference.
- [x] `M002-T04` Implement top navigation bar language toggle (繁中 / EN) with DOM text replacement.
- [x] `M002-T05` Execute and verify i18n test suite.

### Acceptance Criteria
- [x] `M002-AC01` `V11-001` test passes.
- [x] `M002-AC02` Zero external network calls or CDN dependencies.
- [x] `M002-AC03` Full coverage of UI navigation and labels in both locales without side-by-side hardcoded strings.

### Result
`PASS` (4/4 i18n tests pass, offline verified)

---

# M003 — Context-Aware Multi-Folder & Single-Note Scope Filter Engine

Status: `PASS`

### Objective
Implement the multi-folder union, single-note, and subfolder inclusion scope engine with in-memory filtering.

### Tasks
- [x] `M003-T01` Define regression tests `tests/test_v11_scope.py` covering V11-002, V11-003, V11-004.
- [x] `M003-T02` Implement `app/core/scope.py` (`ScopeMode`, `ScopeSpec`, `filter_scan_by_scope`, `extract_vault_folders`, `ScopeValidationError`).
- [x] `M003-T03` Expose API endpoints `/api/scope/folders`, `/api/scope/apply`, `/api/scope/current`.
- [x] `M003-T04` Build UI Scope Selection view in `app/ui/index.html` with folder multi-select and subfolder checkboxes.
- [x] `M003-T05` Wire Scope context chip into topbar header with live note counts.
- [x] `M003-T06` Execute and verify scope test suite.

### Acceptance Criteria
- [x] `M003-AC01` `V11-002`, `V11-003`, `V11-004` tests pass.
- [x] `M003-AC02` Scope filtering executes in-memory without disk rescanning.
- [x] `M003-AC03` UI correctly updates active scope and note count.

### Result
`PASS` (5/5 scope tests pass)

---

# M004 — Beginner-Friendly Schema Builder with Recipe Suggestions

Status: `PASS`

### Objective
Enhance schema design with goal-driven suggestion recipes, natural language query matching, and property reuse reviews.

### Tasks
- [x] `M004-T01` Define regression tests `tests/test_v11_design.py`.
- [x] `M004-T02` Implement recipes (Reading, Lab Equipment, Projects, Journal, Courses) in `app/core/design.py`.
- [x] `M004-T03` Expose API endpoints `/api/design/suggest`, `/api/design/build`, `/api/design/review`.
- [x] `M004-T04` Build UI Schema Designer with goal input, suggestion cards, and reuse badges.
- [x] `M004-T05` Execute and verify design test suite.

### Acceptance Criteria
- [x] `M004-AC01` Design tests pass.
- [x] `M004-AC02` Natural language goals route to appropriate recipes.
- [x] `M004-AC03` Storage types and UI controls remain cleanly separated.

### Result
`PASS` (Design test suite pass)

---

# M005 — Blank Note Property Fill & Copy Engine

Status: `PASS`

### Objective
Implement schema-based form filling and real-time YAML frontmatter generation with copy functionality for blank notes.

### Tasks
- [x] `M005-T01` Define regression tests `tests/test_v11_fill.py`.
- [x] `M005-T02` Implement `fill_preview`, `render_frontmatter`, and `roundtrip_check` in `app/core/fill.py`.
- [x] `M005-T03` Expose API endpoint `/api/fill/preview`.
- [x] `M005-T04` Build UI Blank Note Form in `app/ui/index.html` with preview and copy buttons.
- [x] `M005-T05` Execute and verify fill test suite.

### Acceptance Criteria
- [x] `M005-AC01` Fill tests pass.
- [x] `M005-AC02` Copy button disables fail-closed when frontmatter is invalid.
- [x] `M005-AC03` Form values serialize to valid Obsidian YAML.

### Result
`PASS` (Fill test suite pass)

---

# M006 — Note Properties Workspace (Inspect, Edit & Semantic Diff)

Status: `PASS`

### Objective
Implement the single-note workspace for inspecting existing frontmatter, editing properties with live semantic diffs, and preserving unrelated properties without mutating files.

### Tasks
- [x] `M006-T01` Define regression tests `tests/test_v11_note_workspace.py` covering V11-005 ~ V11-008.
- [x] `M006-T02` Implement `app/core/note_workspace.py` (`inspect_note_for_workspace`, `compute_workspace_diff_and_frontmatter`, `find_candidate_notes`).
- [x] `M006-T03` Expose API endpoints `/api/workspace/notes`, `/api/workspace/inspect`, `/api/workspace/preview`.
- [x] `M006-T04` Build UI Note Workspace view with candidate search, property table, diff view, and YAML preview.
- [x] `M006-T05` Execute and verify note workspace test suite.

### Acceptance Criteria
- [x] `M006-AC01` `V11-005`, `V11-006`, `V11-007`, `V11-008` tests pass.
- [x] `M006-AC02` Unrelated frontmatter properties are preserved across edits.
- [x] `M006-AC03` Notes with duplicate keys or corrupt YAML fail closed.
- [x] `M006-AC04` Copy button is disabled on invalid states.

### Result
`PASS` (4/4 note workspace tests pass)

---

# M007 — Scope-Aware Property Relationship Inbox & 4-State Analysis

Status: `PASS`

### Objective
Implement multi-folder Source Scope and Target Scope analysis for property links with 4-state classification (`VALID`, `BROKEN`, `AMBIGUOUS`, `OUTSIDE SELECTED TARGET`).

### Tasks
- [x] `M007-T01` Define regression tests `tests/test_v11_relationships.py` covering V11-009 ~ V11-011.
- [x] `M007-T02` Update `app/core/relationships.py` with multi-folder source and target scope filtering.
- [x] `M007-T03` Expose API endpoint `/api/relationships` with source/target scopes and 4-state reporting.
- [x] `M007-T04` Build UI Relationship view with multi-folder Source/Target selectors, 4-state metric cards, and item breakdown.
- [x] `M007-T05` Execute and verify relationship test suite.

### Acceptance Criteria
- [x] `M007-AC01` `V11-009`, `V11-010`, `V11-011` tests pass.
- [x] `M007-AC02` Links to notes outside target scope are classified as `OUTSIDE SELECTED TARGET`.
- [x] `M007-AC03` Source and Target scopes support multi-folder selections.

### Result
`PASS` (3/3 relationship tests pass)

---

# M008 — Read-Only Body Wikilink Relationship Analysis Engine

Status: `PASS`

### Objective
Implement note body `[[Wikilink]]` extraction and analysis across source and target scopes with strict read-only safety guarantees.

### Tasks
- [x] `M008-T01` Define regression tests `tests/test_v11_body_links.py` covering V11-012, V11-013.
- [x] `M008-T02` Implement `app/core/body_links.py` (`extract_body_wikilinks_from_text`, `analyze_body_wikilinks`).
- [x] `M008-T03` Expose API endpoint `/api/relationships/body`.
- [x] `M008-T04` Build UI Body Wikilinks tab in Relationships view.
- [x] `M008-T05` Execute and verify body links test suite.

### Acceptance Criteria
- [x] `M008-AC01` `V11-012`, `V11-013` tests pass.
- [x] `M008-AC02` Property links and body wikilinks data models and UI remain strictly separated.
- [x] `M008-AC03` Body wikilink engine is strictly read-only and never modifies note files.

### Result
`PASS` (3/3 body links tests pass)

---

# M009 — User-Initiated Saved Relationship Checks

Status: `PASS`

### Objective
Implement user-initiated saved relationship checks persisted to external storage outside the vault, with zero default assumptions.

### Tasks
- [x] `M009-T01` Define regression tests `tests/test_v11_saved_checks.py` covering V11-014, V11-015.
- [x] `M009-T02` Implement `app/core/saved_checks.py` (`SavedCheck`, `SavedChecksStore`).
- [x] `M009-T03` Expose API endpoints `/api/relationships/saved/list`, `save`, `delete`, `execute`.
- [x] `M009-T04` Build Saved Checks management UI with body_wikilink support and localStorage persistence.
- [x] `M009-T05` Execute and verify saved checks test suite.

### Acceptance Criteria
- [x] `M009-AC01` `V11-014`, `V11-015` tests pass.
- [x] `M009-AC02` System starts with zero default relationship rules.
- [x] `M009-AC03` Saved checks persist outside vault directory.

### Result
`PASS` (2/2 saved checks tests pass)

---

# M010 — Scope-Aware Property Health & Refactor Planner Isolation

Status: `PASS`

### Objective
Ensure Property Health diagnostics, scoring, and Refactor migration planning operate strictly within active Scope.

### Tasks
- [x] `M010-T01` Define regression tests `tests/test_v11_discover_health.py` and `tests/test_v11_refactor.py` covering V11-016, V11-017.
- [x] `M010-T02` Update `app/core/refactor.py` to accept and enforce `ScopeSpec`.
- [x] `M010-T03` Update `app/server.py` `/api/health` and `/api/refactor/plan` to bind to active `STORE.scope`.
- [x] `M010-T04` Update Health and Refactor UI views to display active scope indicator and out-of-scope counts.
- [x] `M010-T05` Execute and verify health and refactor test suites.

### Acceptance Criteria
- [x] `M010-AC01` `V11-016`, `V11-017` tests pass.
- [x] `M010-AC02` Health score and findings reflect only scoped notes.
- [x] `M010-AC03` Refactor plans never include out-of-scope notes.

### Result
`PASS` (Health & Refactor scope isolation tests pass)

---

# M011 — 5,000-Note Performance Benchmark & Full Suite Verification

Status: `PASS`

### Objective
Execute full regression test suite (all 139 tests) and record formal >=5,000-note benchmark evidence with byte-for-byte read-only validation.

### Tasks
- [x] `M011-T01` Run 5,000-note synthetic vault benchmark generator and recorder (`scripts/benchmark.py`).
- [x] `M011-T02` Record timing, memory, and performance observations in `evidence/benchmark.json`.
- [x] `M011-T03` Execute comprehensive Vault read-only test `tests/test_v11_vault_readonly.py` covering V11-018.
- [x] `M011-T04` Run full pytest suite across all modules.

### Acceptance Criteria
- [x] `M011-AC01` All 139 tests PASS without failures.
- [x] `M011-AC02` Benchmark on 5,040 notes recorded (5.062s scan, 5.227s full analysis).
- [x] `M011-AC03` `V11-018` Vault byte-for-byte read-only verified.

### Result
`PASS` (139/139 tests pass, benchmark recorded in `evidence/benchmark.json`: 5.062s scan / 5.227s total analysis)

---

# M012 — Windows 10 / 11 Native Acceptance & v1.1.0 Release Packaging

Status: `PASS`

### Objective
Validate v1.1.0 native execution on Windows 10 (Build 19045+), execute full live HTTP walkthrough acceptance, update documentation, conduct four-file consistency check, package release artifacts, and record formal release verdict.

### Tasks
- [x] `M012-T01` Test `run_windows.bat` launcher natively on Windows environment.
- [x] `M012-T02` Execute live local HTTP server walkthrough acceptance (Scope selection, Note Workspace editing, Multi-Folder Relationships, Saved Checks, i18n toggle, Light/Dark toggle).
- [x] `M012-T03` Verify Traditional Chinese paths, spaces in folder names, and Unicode property values.
- [x] `M012-T04` Update `README.md` and user documentation for v1.1.0 features.
- [x] `M012-T05` Freeze version string `1.1.0` in `app/__init__.py`, `server.py`, and UI metadata.
- [x] `M012-T06` Run four-file consistency check (PROJECT, ROADMAP, HANDOFF, AGENTS).
- [x] `M012-T07` Generate release manifest and packaging bundles (`Obsidian-Property-Studio-v1.1.0-source.zip`, git bundle).
- [x] `M012-T08` Update ROADMAP final state to COMPLETE and record release verdict.
- [x] `M012-T09` Update HANDOFF.md last.

### Acceptance Criteria
- [x] `M012-AC01` Windows 10 (Build 19045+) native launcher, live HTTP server, and UI walkthrough verified (`evidence/integration/m012_v110_windows10_native_acceptance.json`).
- [x] `M012-AC02` Windows 11 (64-bit AMD64) recorded accurately as `NOT YET VERIFIED` (accepted non-blocking release limitation).
- [x] `M012-AC03` Traditional Chinese and English UI verified end-to-end with 100% key parity and zero hardcoded labels.
- [x] `M012-AC04` Documentation matches implementation.
- [x] `M012-AC05` Four-file consistency gate PASS.
- [x] `M012-AC06` Release manifest and bundles verified via clean clone, extraction, git fsck, and pytest.
- [x] `M012-AC07` Formal release verdict recorded (`PROPERTY_STUDIO_V1_1_0_RELEASE_PASS_WITH_LIMITATIONS`).

### Result
`PASS` (Evidence: `evidence/integration/m012_v110_windows10_native_acceptance.json`, `dist/RELEASE_MANIFEST.json`)

---

# M013 — Release Closure In-Place Repair (R01~R12)

Status: `PASS`

### Objective
Systematically address and verify all 12 repair contracts (R01~R12) from the PR #1 independent closure audit: UI-backend API contract parity, true zh-Hant/en bilingual rendering, 4-state Relationships with Multi-Folder selectors, Body Wikilinks & Saved Checks persistence, fail-closed Scope validation, Single Note Scope & whole-Vault Note Workspace search, Scope-aware export consistency, Design dual context, YAML round-trip semantic gate, fresh Windows 10 live HTTP acceptance evidence, non-hardcoded release packaging gate with bundle verification, 4-file governance coherence, and self-contained Design Spec.

### Tasks
- [x] `M013-T01` [R01] Reconcile UI JavaScript API calls with backend server response shapes (`/api/scan`, `/api/discovery`, `/api/property`, `/api/design/*`, `/api/workspace/*`, `/api/refactor/plan`, `/api/relationships/*`, `/api/health`, `/api/export`, `/api/scope/*`).
- [x] `M013-T02` [R02] Refactor UI to eliminate bilingual side-by-side labels; route 100% of user-visible strings through `app/ui/i18n.js` and `locales/{zh-Hant,en}.json`.
- [x] `M013-T03` [R03] Expose 4-state classification (`VALID`, `BROKEN`, `AMBIGUOUS`, `OUTSIDE SELECTED TARGET`), multi-folder Source/Target selectors, Body Wikilinks, and Saved Checks UI management in Relationships view.
- [x] `M013-T04` [R04] Enforce fail-closed Scope validation (unknown mode, empty folders, missing note fail closed with explicit errors; never fallback to Entire Vault).
- [x] `M013-T05` [R05] Add Single Note Scope UI selector and ensure Note Workspace searches whole Vault with relative paths and duplicate-basename ambiguity warnings.
- [x] `M013-T06` [R06] Align Scope-aware export payload with active UI view context.
- [x] `M013-T07` [R07] Support dual context (Scope inventory vs Whole-Vault inventory) in Design suggestion and review.
- [x] `M013-T08` [R08] Implement strict YAML serialization round-trip verification gate in Note Workspace.
- [x] `M013-T09` [R09] Generate fresh Windows 10 Build 19045+ live HTTP native acceptance evidence artifact.
- [x] `M013-T10` [R10] Upgrade `scripts/package_v110_release.py` to verify git clean status, test execution, fresh zip extraction, bundle verification, and git fsck.
- [x] `M013-T11` [R11] Reconcile HANDOFF.md and eliminate stale residue across all 4 governance files.
- [x] `M013-T12` [R12] Ensure `docs/specs/Obsidian_Property_Studio_v1.1.0_UIUX_vNext_Design_Spec.md` is committed and self-contained.
- [x] `M013-T13` Author comprehensive `tests/test_ui_api_contracts.py` and `tests/test_v11_repairs.py`.

### Result
`PASS` (Verified across 139 test cases in `tests/`, Windows 10 live HTTP native acceptance test, and automated release packaging verification)

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
       ├─ Property Links (Source Scope Multi-Folder → Target Scope Multi-Folder)
       ├─ Body Wikilinks (Analysis-only, Strict Read-only)
       │
       └─ Saved Relationship Checks (User-initiated, Reusable, Outside Vault)
```

No evidence, no PASS.  
No contradictory evidence, no PASS.
