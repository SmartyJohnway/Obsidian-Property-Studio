# Handoff

Updated: `2026-09-08`  
From: `Antigravity — v1.2.0 Autonomous Implementation Agent`  
To / Intended Next Executor: `Dr. J (Human Owner) / Verification Auditor`  
Formal Project Root: `D:\Antigravity-Workspace\Obsidian-Property-Studio\Obsidian-Property-Studio-v1.0.0`  
Published Baseline: `v1.1.0 — CLOSED (cca408c)`  
Current Target: `v1.2.0`  
Active Branch: `main`  
Active Milestone: `M022`  
Active Milestone Status: `PASS`  
Current Task: `Final documentation audit / tag / release publication`  
Last Verified Gate: `M022 — Full Workflow Closure, Human Acceptance & Release Gate PASS`  
Last Verified Implementation Commit: `7e3c03d` (docs(v1.2): correct final release closure metadata)  
GitHub PR: `PR #2 (feat(v1.2): Personal Property Governance System — MERGED c652894)`  
Authoritative Specification: `docs/specs/Obsidian_Property_Studio_v1.2.0_Spec.md`  
Completed Roadmap Archive: `docs/archive/ROADMAP_v1.2.0.md` (SHA-256: `c976c5385ece1593d6f340d0dc8c14c76fbccdc8c488a623de5d3839afbaf61f`)  
Archived v1.1 Roadmap: `docs/archive/ROADMAP_v1.1.0.md`  
Release Staging State: `PR_MERGED_PRE_TAG`  
Human Acceptance: `PASS` (M022-T04 / M022-AC04 PASS; Human Verified by Dr. J on Windows 10 Build 19045+)  
Finding Backlog: `CLEAR` (All 16 recorded Human Acceptance findings closed: HA-F01, HA-F08~HA-F19, HA-F21~HA-F23)  
Automated Verification: `PASS (253/253 tests pass in 18.29s)`  
Vault Read-Only: `PASS (100% byte-for-byte read-only, zero mutation)`  
Consistency Gate: `PASS (PROJECT.md, ROADMAP.md, HANDOFF.md, AGENTS.md aligned)`  

---

## Current Status & Checkpoint Summary

All autonomous implementation and verification milestones from M016 through M021 have been executed, tested, and marked **PASS**. The project is now at **M022 (Release Candidate)**:

- **M016: Workflow Closure Foundation & State Transfer Engine — PASS**
  - Implemented `app/core/state_transfer.py` and `app/ui/state_transfer.js`.
  - Added single-consumption navigation context with fail-closed deserialization.
  - 6 dedicated unit tests (`tests/test_v12_state_transfer.py`) PASS.

- **M017: Personal Glossary & Named Schema Library — PASS**
  - Implemented `app/storage/local_storage.py` outside Vault with OCC (`revision`/`etag`) and crash-safe backup isolation.
  - Implemented `app/core/user_glossary.py` with 3-tier precedence (`Built-in → User Override → Vault Facts`) and immutable canonical keys.
  - Implemented `app/core/named_schemas.py` with full CRUD, versioning, and naming collision protection.
  - Expanded bilingual i18n dictionaries to 299 aligned keys (`test_v11_i18n.py` PASS).
  - 6 dedicated unit tests (`tests/test_v12_glossary.py`, `tests/test_v12_named_schemas.py`) PASS.

- **M018: Existing Note Reconciliation & Health Drilldown — PASS**
  - Implemented `app/core/reconciliation.py` computing 4 distinct states (`Matches`, `Missing`, `Conflict`, `Outside-Schema Preserved`).
  - Strict preservation of non-schema properties (DEC-029).
  - Integrated Health finding drilldown into Note Workspace (`drilldownToNoteWorkspace`).
  - 3 dedicated unit tests (`tests/test_v12_reconciliation.py`, `tests/test_v12_health_drilldown.py`) PASS.

- **M019: Scope Governance & Schema Drift — PASS**
  - Implemented `app/core/scope_governance.py` persisting folder-to-schema assignments outside Vault.
  - Implemented `app/core/drift.py` analyzing Desired vs Actual schema compliance rate, missing required properties, type mismatches, and value drift.
  - Integrated Schema Drift card into Property Health UI.
  - 2 dedicated unit tests (`tests/test_v12_scope_governance.py`, `tests/test_v12_drift.py`) PASS.

- **M020: External AI Proposal Workflow & Companion Skill — PASS**
  - Updated `app/core/proposal.py` supporting Proposal Contract 1.1 additions (`target_note`, `target_scope`, `rationale`, `proposed_migration`) while retaining 100% backward compatibility with Proposal Contract 1.0.
  - Built interactive Proposal Review UI with one-click Save as Named Schema and Reconcile with Note actions.
  - Packaged companion skill `skills/obsidian-property-advisor/` (`SKILL.md`).
  - 3 dedicated unit tests (`tests/test_v12_proposal_workflow.py`) PASS.

- **M021: Schema Versioning, Migration Planning & Governance Profile (P1 Full Implementation) — PASS**
  - Implemented `app/core/migration.py` detecting breaking changes, suggesting SemVer bumps (patch/minor/major), and generating step-by-step migration plans.
  - Implemented `app/core/governance_profile.py` exporting and importing portable packages with SHA-256 integrity checksums.
  - Integrated Migration Planner drawer and Profile export/import in UI.
  - 4 dedicated unit tests (`tests/test_v12_migration.py`, `tests/test_v12_governance_profile.py`) PASS.

- **M022: Full Workflow Closure, Human Acceptance & Release Gate — PASS**
  - **Human Acceptance Verified**: Formally verified by Human Owner (Dr. J) on Windows 10 (Build 19045 AMD64) on 2026-09-07 (`evidence/integration/m022_v120_windows10_native_acceptance.json`).
  - **Finding Backlog Closed (CLEAR)**: All 16 recorded human acceptance findings (HA-F01, HA-F08~HA-F19, HA-F21~HA-F23) fully resolved and verified.
  - **Closure Smoke Gates (1~6)**: Runtime F5 rehydration (Gate 1), Named Schema -> Workspace identity/version (Gate 2), Workspace untouched complex YAML preservation (Gate 3), Blank Note Scope schema authority (Gate 4), Drift exact navigation (Gate 5), and Governance Profile export/import/preview (Gate 6) all PASS.
  - **Full Automated Suite**: 253/253 tests PASS in 18.29s.
  - **Authoritative Benchmark**: Measured and recorded on 5,040 notes (5.844s total analysis / 5.667s scan, Vault 100% byte-for-byte read-only).
  - **Release Artifacts Staged**:
    - `dist/Obsidian-Property-Studio-v1.2.0-source.zip`
    - `dist/Obsidian-Property-Studio-v1.2.0.bundle`
    - `dist/RELEASE_MANIFEST.json`
    (Final artifact sizes and SHA-256 are authoritative in the externally generated `dist/RELEASE_MANIFEST.json` and final release publication evidence; packaging verification PASS).
  - **Roadmap Archived**: Authoritative v1.2.0 Roadmap copied to `docs/archive/ROADMAP_v1.2.0.md` (SHA-256: `c976c5385ece1593d6f340d0dc8c14c76fbccdc8c488a623de5d3839afbaf61f`); root `ROADMAP.md` set to active release-staging pointer.
  - **Release Notes Drafted**: `docs/releases/v1.2.0-release-notes.md`.
- **Commit 21N: HA-F18 Governance Profile Concrete Change-Set Preview Closure — COMPLETED**
  - **Backend Deterministic Per-Entity Plan Engine**: In `app/core/governance_profile.py`, implemented `compute_concrete_changeset(profile_data, mode="merge")`. Generates deterministic per-entity change records across all 5 profile categories (`schemas`, `scope_assignments`, `glossary`, `saved_checks`, and `preferences`). Each entity record defines `action` (`add`, `update`, `conflict`, `unchanged`, `remove`, `retained`), `identity`, `display_name`, `before`, `after`, and human-readable `reason`.
  - **Dual Mode Pre-calculation in Validation Report**: In `validate_governance_profile()`, pre-calculates and embeds concrete plans for both modes under `plans: {"merge": ..., "replace": ...}` without mutating storage or disk.
  - **Dynamic UI Projection with Monospace Keys & Action Pills**: In `app/ui/index.html`, added concrete per-entity change-set rendering in `renderProfilePreviewArea()`. Visualizes items with color-coded status badges (`新增`, `更新`, `衝突`, `移除`, `保留`, `無變更`), monospace identifier codes, clear before $\to$ after details, and localized rationale strings.
  - **Instant Client-Side Mode Toggle**: In `renderProfilePreviewArea()`, added dynamic `onchange` listener to `#profileImportModeSelect` that updates `S.lastProfileValidation.mode` and immediately re-renders the preview from precomputed plans with zero network request, zero re-parsing, and zero re-validation.
  - **Bilingual i18n Symmetry**: Added 11 symmetric keys (`profile.action_unchanged`, `action_add`, `action_update`, `action_conflict`, `action_remove`, `action_retained`, `label_before`, `label_after`, `concrete_changeset_title`, `cat_preferences`, `empty_category`) to both `app/ui/locales/zh-Hant.json` and `app/ui/locales/en.json` (557 symmetric keys).
  - **Automated Verification**: Added 2 automated tests in `tests/test_v12_human_acceptance_repairs.py`:
    - `test_ha_f18_concrete_changeset_tests_a_to_j`: Covers tests A through J (schema update with before/after props, schema retained in merge, schema remove in replace, scope add, glossary add, check add, unchanged preference, replace vs merge differentiation, empty category graceful display, deterministic ordering).
    - `test_ha_f18_production_javascript_rendering_in_node`: Real Node.js execution of production JS verifying title, action badges, dropdown toggle from merge to replace and back to merge, and zero raw i18n key leakage.
    - **253/253 tests PASS** in 18.91s. Vault 100% byte-for-byte read-only.
- **Commit 21M: HA-F14 Complex / Nested YAML Value Rendering Closure — COMPLETED**
  - **Canonical Display Formatter (`formatPropertyValueForDisplay`)**: In `app/ui/index.html`, added a reusable, pure-display formatter handling null, boolean, number, string, flat array, nested array, plain object / mapping, and array of objects. Produces deterministic, safely escaped string representations with zero `[object Object]` and zero `[object Array]`.
  - **Property Editor Fail-Safe Rendering**: In `renderWorkspaceFields()`, complex objects/mappings are formatted with `formatPropertyValueForDisplay()` into a read-only input, tagged with `data-is-complex="true"`, and displayed with a localized badge (`workspace.complex_val_preserved`).
  - **Zero Object-to-String Coercion on Untouched Properties**: In `updateWorkspacePreview()`, harvesting inputs checks `data-is-complex="true"`: if the key is not in `S.wsTouchedKeys`, the 100% native dict/array is drawn directly from `S.currentNote.original_properties[k]`, completely avoiding `.value` stringification.
  - **Semantic Diff Formatter**: In `updateWorkspacePreview()`, formatted `d.old_value` and `d.new_value` using `formatPropertyValueForDisplay()`, displaying `location preserved { readable structured value }` without `[object Object]`.
  - **Status Banner Formatter**: Updated `renderWorkspaceStatusBanner()` to display `it.current_value` via `formatPropertyValueForDisplay()`.
  - **Bilingual i18n Symmetry**: Added `workspace.complex_val_preserved` ("複合值 — 保留原值" / "Complex value — preserved") symmetrically to `app/ui/locales/zh-Hant.json` and `app/ui/locales/en.json` (546 symmetric keys).
  - **Automated Verification**:
    - `test_ha_f14_complex_yaml_diff_and_serialization_tests_a_to_f`: Covers flat mapping (location), nested mapping (equipment -> motor), array of objects (items), native scalar regression (string, number, boolean, date, list of strings, tags, aliases), untouched preservation, and YAML roundtrip readback.
    - `test_ha_f14_production_javascript_rendering_in_node`: Real Node.js execution of production JS verifying zero `[object Object]` in display, fields, and diff.
    - **251/251 tests PASS** in 18.38s. Vault 100% byte-for-byte read-only.
- **Commit 21L: HA-F21 & HA-F23 Schema Context & Version Identity Closure — COMPLETED**
  - **HA-F23 Blank Note Schema Authority**: Decoupled `S.blankNoteSchema` (Blank Note authority) from `S.currentSchema` (Designer transient authority).
    - Mode 1 (Designer handoff): Clicking `designGoToFill` explicitly sets `S.blankNoteSchema = S.currentSchema` and `S.blankNoteEntrySource = "designer"`, navigating to `fill`.
    - Mode 2 (Direct Blank Note Navigation): Sidebar click or direct navigation sets `S.blankNoteEntrySource = "direct"`. In `setTab("fill")`, `resolveBlankNoteSchemaForScope()` resolves active Scope expected schema via `getCanonicalScopeKey()` -> `/api/scope/schema/current` -> `assignment.schema_id` -> `/api/schemas/get` -> sets `S.blankNoteSchema = exact Named Schema`.
    - Fail-Closed: If active scope has no schema assignment, `S.blankNoteSchema = null` and empty state card is displayed. Never falls back to `S.currentSchema`.
    - UI Projection: Blank Note header displays `Name (vVersion)` if version present, or `Name` if unversioned. All Fill inputs and `/api/fill/preview` payload consume `S.blankNoteSchema`.
  - **HA-F21 Workspace Reconciliation Exact Version Identity**:
    - Backend: Added `schema_version: str | None = None` to `ReconciliationReport` in `app/core/reconciliation.py`. In `app/server.py` (`api_reconcile_inspect`), resolved `sch.version` for Named Schema and passed to `reconciliation.reconcile_note_frontmatter()`.
    - Frontend State: Captured `reconciliationSchemaVersion` in `S.lastWorkspaceStatus`.
    - Banner Display: `renderWorkspaceStatusBanner()` renders `⚖️ 核對筆記：${recSchemaName} (v${recSchemaVersion})` / `⚖️ Reconcile Note: ${recSchemaName} (v${recSchemaVersion})`. Dynamic locale switch preserves exact version identity without downgrade. Cancel clears version.
  - **Automated Verification**: Added 3 automated tests in `tests/test_v12_human_acceptance_repairs.py` (`test_ha_f21_reconciliation_exact_version_identity`, `test_ha_f21_server_api_reconcile_inspect`, `test_ha_f23_and_f21_frontend_in_node`). **249/249 tests PASS** in 21.28s. Vault 100% byte-for-byte read-only.
- **Commit 21K: HA-F22 Scan-Dependent UI Rehydration Closure — COMPLETED**
  - **Backend Context Authority Enrichment**: In `app/server.py`, enriched `/api/runtime/context` with `summary`, `unique_property_count`, and `scan_seconds` directly from in-memory `STORE.scan` and `STORE.inventory` authority with strictly zero disk rescan.
  - **Scan-Dependent UI Projection Restoration**: In `app/ui/index.html`, updated `rehydrateRuntimeContext()` to rehydrate `S.vaultSummary`, `S.uniquePropertyCount`, and `S.lastScanSeconds`. Created `restoreActiveScanUI()` and invoked it at the end of `init()` when `S.scanned` is true:
    - Overview Module: Hides `overviewNotScanned` and displays `overviewScanned`. Rehydrates `ovNotesCount`, `ovPropsCount`, `vaultPathInput`, and all note statistics cards (`statNotesTotal`, `statNotesWithProps`, `statNotesNoProps`, `statNotesFailed`).
    - Scope Module: Automatically invokes `loadScopeFolders()` without requiring manual user re-scan. Added `renderScopeControlsFromState()` to sync `scopeModeSelect`, project active scope into folder checkboxes or single-note selector, and update scope badges.
    - Dependent Caches & Views: Rebuilds `loadDiscovery()`, `loadHealth()`, `loadSavedChecks()`, `populateRefactorSourceOptions()`, and `updateScopeSchemaAssignmentUI()`.
  - **Zero Disk Rescan Guarantee**: Verified zero disk rescan on F5 rehydration (`/api/scan` is never called, file `mtime` unchanged).
  - **Automated Verification (TESTS A-H)**: Updated `test_ha_f22_backend_runtime_context_active_and_empty` and extended `test_ha_f22_frontend_runtime_context_rehydration_in_node` with comprehensive tests (TESTS C-H) covering Overview un-hiding, note/prop counts rehydration, Folders mode selector display, and active folder counts.
  - **Automated Verification**: **246/246 tests PASS** in 15.21s. Vault 100% byte-for-byte read-only.
- **Commit 21J: Active Vault Runtime Context Rehydration Closure (HA-F22) — SUPERSEDED BY 21K**
  - **Backend Runtime Context Endpoint (/api/runtime/context)**: In `app/server.py`, added `api_runtime_context(_body)` reporting `{ "scan_loaded": bool, "vault_path": str|None, "vault_name": str|None, "scope": dict|None, "notes_in_scope": int, "total_vault_notes": int }` directly from in-memory `STORE.scan` and `STORE.scope` authority with zero disk rescan. Added route `/api/runtime/context` to `ROUTES`.
  - **Frontend State Rehydration on Browser Load/F5**: In `app/ui/index.html`, added `vaultName: ""` to state `S` and implemented `rehydrateRuntimeContext()` called during `init()`. Rehydrates `S.scanned`, `S.vaultPath`, `S.vaultName`, `S.scope`, and `S.notesInScope` when active backend scan exists, or cleanly resets when backend has no active scan.
  - **State-Driven Context Bar Rendering**: In `updateContextBarLabels()`, updated vault label resolution to set `$("currentVaultLabel").textContent` from `S.vaultName || S.vaultPath.split(/[/\]/).pop()` whenever `S.scanned` is true, preventing the context bar from falling back to `"No vault loaded"` during dynamic view rerenders or locale switching. In `setupVaultHandlers()`, populated `S.vaultName` on scan completion and routed UI updates through `updateContextBarLabels()`.
- **Commit 21I: Observed Property Canonical Key Identity Closure (HA-F19) — SUPERSEDED BY 21J**
  - **Iterate Real Inventory Records (pdata.key)**: In `app/ui/index.html` (`loadGlossaryList`), repaired observed vault property iteration from `S.inventory.properties`. Because `inventory.properties` is canonically a JSON array of `PropertyEntry` objects, replaced `Object.entries(S.inventory.properties)` (which produced numeric array indexes `"0"`, `"1"`, `"2"` as keys) with direct array iteration extracting `pdata.key`.
  - **Fail Closed on Malformed Records**: Records missing a non-empty string `key` are skipped immediately without generating fallback index keys, "undefined", or empty rows.
  - **Deduplication Precedence**: Retained canonical 3-tier precedence (`user override > builtin catalog > observed-only property`). Observed inventory entries only add keys not already in `seenKeys`.
  - **Metadata Association Intact**: Preserved `pdata.usage_count` and `pdata.dominant_type` correctly bound to each canonical property key.
  - **Locale-Invariant Identity**: Raw YAML property keys remain strictly immutable across zh-Hant and English views, while labels/sources/guidance localize properly.
  - **Automated Node.js Test Coverage (TESTS A-F)**: In `tests/test_v12_human_acceptance_repairs.py`, added `test_ha_f19_observed_property_canonical_key_identity_in_node()` validating: (A) real array identity renders `custom_alpha` and `custom_beta`, 0 numeric index rows; (B) metadata attached without cross-wiring; (C) builtin `status` deduplication; (D) user override `shared_override_key` deduplication; (E) malformed records fail-closed; (F) locale switch identity stability.
  - **Automated Verification**: **244/244 tests PASS** in 15.36s. Vault 100% byte-for-byte read-only.
- **Commit 21H: Drift Exact-Path Click Navigation Closure (HA-F12) — SUPERSEDED BY 21I**
  - **DOM Event Binding & Zero Inline JS Injection**: In `app/ui/index.html` (`window.openDriftDetailsDrawer`), removed untrusted/canonical `note_path` strings from inline `onclick="drilldownToNoteWorkspace('${esc(f.note_path)}', ...)"`. Rendered buttons with class `.drift-reconcile-btn` and `data-finding-index="${idx}"`, and attached DOM event listeners via `drawerBody.querySelectorAll(".drift-reconcile-btn")` after drawer rendering.
  - **Exact Path Preserved**: Clicking "Reconcile Note" retrieves `findings[idx].note_path` directly from state, passing the exact canonical string (including apostrophes `'`, double quotes `"`, ampersands `&`, square brackets `[[`, and Chinese Unicode characters) to `drilldownToNoteWorkspace`. Completely eliminated browser `SyntaxError` / silent handler failures on paths like `·'![[台灣_美國通用採購流程使用手冊_v1.0.docx.md`.
  - **Automated Node.js Test Coverage (TESTS A-D)**: In `tests/test_v12_human_acceptance_repairs.py`, added `test_ha_f12_actual_js_drift_click_navigation_in_node()`:
    - TEST A: Real filename with apostrophe, bullet, wikilink syntax, and Unicode (`·'![[台灣_美國通用採購流程使用手冊_v1.0.docx.md`) renders button, click fires without error, 0 exceptions, passes exact string to `drilldownToNoteWorkspace`.
    - TEST B: Double quotes, ampersand, and Unicode (`工程 "A&B" Review.md`) clicks and passes exact string.
    - TEST C: Normal path regression (`00_Home/HOME.md`) clicks and passes exact string.
    - TEST D: Duplicate basename in different folders (`FolderA/Item.md` vs `FolderB/Item.md`), clicking FolderB row passes exact `FolderB/Item.md`.
    - Zero inline onclick injection verified (`drilldownToNoteWorkspace` not in `innerHtml`).
  - **Automated Verification**: **243/243 tests PASS** in 17.95s. Vault 100% byte-for-byte read-only.
- **Commit 21G: Drift Canonical Path Authority Closure (HA-F12) — SUPERSEDED BY 21H**
  - **Bound Drift Path Authority to Active VaultScan**: Repaired `is_canonical_navigable_path` in `app/core/drift.py` by removing ad-hoc filename string heuristics (which previously rejected filenames starting with `·`, `![[`, `*`, `-`, `+`). Canonical note identity is bound to membership in active `VaultScan` (scanned filesystem notes) while enforcing `.md` extension and blocking path traversal / non-relative paths fail-closed.
  - **CASE A Verified**: Scanned notes with unusual but legitimate filenames (such as `· ![[台灣_美國通用採購流程使用手冊_v1.0.docx.md`) now evaluate to `navigation_available: True` and enable direct one-click Reconcile Note navigation.
  - **CASE B Preserved**: Truly unresolvable or unscanned paths (or malformed non-markdown inputs) fail closed (`navigation_available: False`) while preserving the raw string in findings for transparent diagnosis.
  - **Regression Coverage (TESTS A-D)**: Updated `test_ha_f12_drift_canonical_navigable_path_guard` in `tests/test_v12_human_acceptance_repairs.py` to assert: (A) unusual real filename is recognized and navigable; (B) phantom/traversal path fails closed; (C) ordinary `.md` file is navigable; (D) duplicate file names in different folders maintain distinct identities without collision.
  - **Automated Verification**: **242/242 tests PASS** in 16.72s. Vault 100% byte-for-byte read-only.
- **Commit 21F: Workspace Dynamic i18n & Immutable Evidence Closure — SUPERSEDED BY 21G**
  - **window.renderWorkspaceStatusBanner state-driven renderer (HA-F08)**: Extracted workspace reconciliation banner rendering (note loaded card, diagnostic focus, four-state reconciliation table with Fill/Focus buttons, cancel button) from inline `inspectNoteInWorkspace()` into a dedicated `window.renderWorkspaceStatusBanner(statusData)` function. First API call caches result in `S.lastWorkspaceStatus = { noteResponse, pendingContext, reconciliationResult, reconciliationSchemaName }`. Locale switch calls `renderAllDynamicViews()` → `renderWorkspaceStatusBanner(S.lastWorkspaceStatus)`, re-rendering all i18n labels from cached data without re-calling the API or losing workspace edit state (`wsTouchedKeys`, input values, search selection, active reconciliation schema).
  - **cancelWorkspaceReconciliation upgraded**: Clears `S.lastWorkspaceStatus.reconciliationResult` and calls `renderWorkspaceStatusBanner()` to show only the note loaded card (without reconciliation table). Previously cleared the entire banner innerHTML.
  - **test_ha_f08_workspace_reconciliation_banner_locale_rerender_in_js**: New Node.js test verifying: (a) first render contains note loaded card, reconciliation table with 4 states, Fill/Focus buttons, column headers, cancel button; (b) locale switch re-renders same content from cache; (c) cache integrity preserved; (d) cancel clears reconciliation but preserves note loaded card.
  - **Historical evidence immutability**: Restored `evidence/integration/m009_benchmark.json` and `evidence/integration/m012_v110_windows10_native_acceptance.json` to their `main` branch baseline. `test_benchmark.py` now writes to `evidence/integration/m022_v120_benchmark.json` (not m009). `test_windows10_acceptance.py` now writes to `evidence/integration/m022_v120_windows10_native_acceptance.json` (not m012).
  - **ROADMAP evidence authority clarified**: `evidence/integration/m022_v120_benchmark.json` is the authoritative M022 benchmark (5.844s analysis / 5.667s scan). `evidence/benchmark.json` is explicitly marked as non-authoritative latest local benchmark.
  - **Automated Verification**: **242/242 tests PASS** in 17.43s. 5,040-note benchmark: 5.844s analysis / 5.667s scan. Vault 100% byte-for-byte read-only.
- **Commit 21E: Refactor Runtime, Profile State & Evidence Closure — SUPERSEDED BY 21F**
- **Commit 21D: Final Browser Runtime & State Closure — SUPERSEDED BY 21E**
- **Commit 21C: Final Human Acceptance State & i18n Closure — SUPERSEDED BY 21D**
  - **Workspace & Schema State Complete Decoupling (HA-F09 / HA-F11 Frontend State Isolation)**:
    - Implemented `window.cancelWorkspaceReconciliation()`: clearing `S.activeReconciliationSchema` and triggering `updateWorkspacePreview()` with `schema: null` to remove all schema-imposed constraints in-place.
    - Isolated `S.currentSchema` (used exclusively by Designer and Fill) from `S.activeReconciliationSchema` (used exclusively by Note Workspace reconciliation).
    - Hardened `drilldownToNoteWorkspace()`: if no `schema_id` is supplied, active reconciliation schema is cleared and not inherited.
  - **HA-F08 Dynamic Locale Re-render & Bilingual Glossary Support**:
    - Fixed `renderAllDynamicViews()` to call `loadGlossaryList()` correctly (resolved `populateGlossaryTable` typo).
    - `loadGlossaryList()` renders primary and secondary labels and guidance according to active locale (`label_en` / `desc_en` in English; `label_zh` / `desc_zh` in zh-Hant).
    - Switching locales strictly retains active uncommitted input values and `wsTouchedKeys` in Note Workspace.
  - **HA-F16 Named Schema Lifecycle Hardening & Collision Prevention**:
    - Added `<select id="saveSchemaTargetSelect">` dropdown in Save Modal when multiple versions of the same schema exist, enabling the user to explicitly target which version to update.
    - Implemented robust `bumpSemVer(v)` handling standard SemVer (`1.0.0` -> `1.1.0`, `1.10.0` -> `1.11.0`) and non-standard tokens without float rounding bugs.
    - Backend `NamedSchemaLibrary.update_schema` enforces unique `(name, version)` pair across library, raising `ValueError` (HTTP 400) on collision.
    - Frontend Save As Different Name validates that the target name differs from existing schema name.
  - **Static HTML i18n & Mismatch Banner Fallback**:
    - Internationalized remaining static HTML placeholders, badges, titles, and buttons (including `openProposalFileBtn` -> `proposal.open_file_btn`, `vaultPathInput`, `scopeSingleNoteInput`, `healthDriftComplianceBadge`).
    - Added safe fallback strings in `renderMismatchBanner()` preventing raw key exposure during early initialization.
    - Synchronized all 537 translation keys symmetrically between `zh-Hant.json` and `en.json`.
  - **Automated Verification**: **240/240 tests PASS** across full suite in 15.05s. 5,040-note benchmark verified at 9.90s, 0 Vault mutations.
- **Commit 21B: Human Acceptance Repair Completion (HA-F01 ~ HA-F18) — SUPERSEDED BY 21C**
  - **Named Schema Full Lifecycle & Collision Protection (HA-F16)**: Implemented `openSaveNamedSchemaModal` drawer handling existing schema detection, offering Update Existing Schema (`/api/schemas/update`), Create New Version (`/api/schemas/create` with bumped SemVer), or Save As Different Name (`/api/schemas/create`). Readback verification via `/api/schemas/get` before updating UI state.
  - **Dynamic Locale Re-render & Workspace Edit State Retention (HA-F08)**: Triggered `renderAllDynamicViews()` upon `ps:localeChanged` event. In `renderWorkspaceFields(propsMap, preserveTouched = true)`, active user inputs and `S.wsTouchedKeys` are strictly retained without wiping dirty state. Cleaned all hardcoded Chinese in JS script (517 synchronized keys in `zh-Hant.json` / `en.json`).
  - **Canonical Schema ID Authority in Reconciliation (HA-F09, HA-F11)**: Backend `/api/reconcile/inspect` enforces canonical schema properties and metadata from `NAMED_SCHEMA_LIBRARY` whenever `schema_id` is supplied, overriding stale payload arguments.
  - **Drift Canonical Navigable Path Guard & Link Defense (HA-F12)**: Reject wikilinks (`[[...]]`, `![[...]]`), list markers (`*`, `-`, `+`, `·`), and drive letters/traversal fail-closed. Drift drawer disables navigation buttons and surfaces explanation tooltip when `navigation_available` is false.
  - **Governance Profile Detailed 4-Category Changeset (HA-F18)**: `validate_governance_profile` generates comprehensive changesets for `schemas`, `scope_assignments`, `glossary_overrides`, and `saved_checks`, with safe object serialization preventing `[object Object]`.
  - **StorageType-Aware Semantic Equality (HA-F10)**: Upgraded `are_semantically_equal()` with type-aware precision for `NUMBER`, `CHECKBOX`, `LIST`, `TAGS`, and `TEXT` (strictly preserving text leading zeros).
  - **Automated Verification**: **235/235 tests PASS** across full suite in 15.51s (`tests/test_v12_human_acceptance_repairs.py` 13/13 PASS). 5,040-note benchmark verified, 0 Vault mutations.
- **Commit 21: Human Acceptance Findings Repair (HA-F01 ~ HA-F18 Baseline) — SUPERSEDED BY 21B**
- **Commit 20: Production Lifecycle Safety Timing, Rehydration & Real Storage Persistence Failure Closure — PASS**
  - **Zero Pre-Vault Destructive Migration (Task A / P0 REQ-051)**: Removed `init_runtime_storage()` from `app/__main__.py::main()` and `server.py::create_server()`. Prohibits any copying, filesystem mutation, or directory creation before the active Vault path is known. Migration is strictly guarded and executed inside `api_scan()` immediately after `assert_outside_vault` succeeds.
  - **Immediate In-Process Saved Checks Rehydration (Task B / REQ-051, REQ-052)**: Added `SavedChecksStore.reload()` method. After `migrate_legacy_storage_paths()` moves legacy files to their canonical location during `api_scan()`, `STORE.saved_checks_store.reload()` is invoked immediately, rehydrating checks in the current running process with zero restart required. Verified via `api_saved_checks_list()`.
  - **Real Storage-Layer Persistence Failure Mock & Rollback (Task C)**: Upgraded persistence rollback test to mock `chk_store.storage.save` (simulating real disk write failure after in-memory state has transitioned). Verified that on failure, memory and underlying storage for both preferences and saved checks are 100% restored to pre-migration baseline with zero mutation.
  - **Per-Entity Validation Isolation (Task C)**: Refactored Phase 1 validation so that already-initialized entities completely ignore and bypass stale/corrupted legacy payloads (e.g. invalid `ps_locale` does not abort checks migration if preferences are already initialized).
  - **Automated Verification**: **222/222 tests PASS** across full suite in 16.3s. 5,040-note benchmark verified at **4.919s** (scan: 4.755s, 0 Vault mutations).
- **Commit 19: Migration Transaction Rollback, Per-Entity Guard & Runtime Path Migration Closure — PASS**
  - **Migration Persistence Transaction + Rollback (Blocker 1 / REQ-051, REQ-052)**: Refactored `/api/storage/migrate_legacy` with full pre-persistence snapshots of `old_prefs` and `old_checks`. Added bulk atomic `replace_all()` to `SavedChecksStore`. If persistence fails midway (e.g. disk failure on checks after preferences are written), a comprehensive `try...except` block rolls back both entities to their exact pre-migration state, raising HTTP 500 fail-closed.
  - **Per-Entity Initialized-State Guard (Blocker 2 / REQ-051)**: Separated migration initialization checks for Preferences and Saved Checks. If backend preferences already exist, incoming legacy preferences cannot overwrite them, but uninitialized checks can still be migrated. If backend checks already exist, incoming legacy checks cannot overwrite them, but uninitialized preferences can still be migrated. Rerun when both are initialized is safely skipped.
  - **Runtime Legacy Storage Path Migration Invocation (Blocker 3 / REQ-051)**: Wired `migrate_legacy_storage_paths()` into the production execution lifecycle: invoked in `create_server()` upon application startup, in `app/__main__.py::main()`, and inside `api_scan()` immediately after active Vault isolation verification succeeds. Added integration tests verifying unnested legacy paths are automatically migrated without user data loss.
  - **Canonical Dict Exact Readback (Polish)**: Upgraded readback verification to compare full canonical `SavedCheck` dictionaries (including `source_scope`, `target_scope`, `link_type`, and `property_name`) rather than IDs alone.
  - **Automated Verification**: **222/222 tests PASS** across full suite in 15.4s. 5,040-note benchmark analysis verified at **5.125s** (scan: 4.928s, 0 Vault mutations).
- **Commit 18: Storage Side-Effect, Pure Path Resolution & Migration Atomicity Closure — PASS**
  - **Pure Path Resolution before mkdir (P0 Blocker 1 / REQ-051)**: `get_storage_dir(create=False)` and `EntityStorage._file_path(create=False)` refactored to perform zero filesystem mutations during resolution and containment verification. Directories are strictly created only on actual mutation (`save` / `create_backup`) after `assert_outside_vault` succeeds.
  - **Negative Inside-Vault 0-Mutation Proof (P0 Blocker 2 / REQ-051)**: Added automated test `test_vault_isolation_pure_path_and_negative_zero_change` verifying against a disposable vault directory tree and SHA-256 manifest. When pointing storage to `<vault>/bad_store`, `bad_store/` is never created and vault remains 100% byte-for-byte identical.
  - **Atomic Validate-Before-Persist Legacy Migration (P0 Blocker 3 / REQ-051, REQ-052)**: `/api/storage/migrate_legacy` validates all locale, theme, and saved check entries before saving anything. If any item is corrupted, it fails closed (HTTP 400) with 0 partial writes.
  - **One-Time Idempotency & Exact Readback Compare (P0 Blocker 4 / REQ-051)**: Migration checks if backend storage is initialized (`_legacy_migrated: True` or existing state) and skips subsequent runs. Readback proof explicitly compares requested vs persisted canonical states. Frontend cleans all legacy localStorage keys (`ps_locale`, `property_studio_locale`, `ps_theme`, `property_studio_theme`, `ops_saved_relationship_checks_v110`, `property_studio_saved_checks`) and sets `ps_v12_legacy_migrated: true`.
  - **Automatic Path Migration Decoupled & Fail-Closed (Task 3)**: Removed `migrate_legacy_storage_paths()` from `EntityStorage.__init__()` to eliminate startup side effects. Copy errors raise `StorageError` fail-closed and retain source files.
  - **Governance Profile Clear-Stage Rollback & Preferences Preview (Task 5 & 6)**: Added rollback test verifying full restoration when clear stage fails midway. `validate_governance_profile` returns `preferences_preview` and UI renders detailed locale/theme diff.
  - **Full Dynamic JS i18n & Drawer Clean (Task 7 & 9)**: Internationalized all dynamic modal drawer titles and button labels; static script scan asserts 0 hardcoded Chinese in `toast()` and `openDrawer()`.
  - **Evidence Consistency**: Standardized 5,040-note benchmark analysis to **4.794s** (scan: 4.639s; total test run: 10.29s) and full test suite to **218/218 PASS**.
- **Commit 17: Frozen Storage Architecture & Safety Closure — PASS**
  - **Runtime Vault Isolation (P0 / REQ-051)**: Wired `local_storage.py::assert_outside_vault()` directly into runtime execution (`api_scan`, `EntityStorage.load/save/backup`). Prohibits equal path, storage inside vault, storage parent containing vault, and traversal. Fails closed with 0 vault modification.
  - **Legacy State Migration Contract (P0 / REQ-051, REQ-052)**: Implemented `/api/storage/migrate_legacy` supporting documented & historical aliases (`ps_locale`/`property_studio_locale`, `ps_theme`/`property_studio_theme`, `ops_saved_relationship_checks_v110`/`property_studio_saved_checks`). Validated before write, idempotent rerun safe, returns read-back proof, keeps legacy localStorage until backend returns success and readback proof, fails closed on corrupt payload.
  - **App-Local Saved Checks Persistence (P0 / REQ-051, REQ-052)**: Persisted `saved_checks/saved_relationship_checks.json` outside Vault using `EntityStorage`. Server API uses this as authoritative state. Eliminated silent discard in `from_json` and storage loader; raises explicit `CorruptedSavedChecksError` preserving original payload.
  - **M015 Storage Layout Alignment & Path Migration (Task 4)**: Aligned storage paths strictly to frozen contract (`config/preferences.json`, `glossary/user_glossary.json`, `schemas/named_schemas.json`, `scope_profiles/scope_expected_schemas.json`, `saved_checks/saved_relationship_checks.json`). Implemented `migrate_legacy_storage_paths()` for seamless, idempotent pre-release file migration without data loss.
  - **Real Governance UI Preferences (Task 5 / REQ-051)**: UI locale & theme authoritative state backed by app-local preferences. Loaded on startup via `/api/preferences/get`, synchronized on toggle via `/api/preferences/set`, exported in Governance Profile, previewed in profile validation, and applied on profile confirm.
  - **Governance Profile Transaction Boundary (Task 6 / REQ-047)**: Enclosed destructive clear and import writes within a single protected `try...except` block with pre-snapshot. Tested both clear stage failure and midway import failure ensuring 100% atomic rollback of all 5 entities. Rejects unknown import modes fail-closed.
  - **Drift Exact Canonical StorageType (Task 8 / REQ-045)**: Strictly distinguishes `list` vs `tags` and `date` vs `datetime` without interchangeable fallback.
  - **Dynamic JS i18n Strings Cleaned (Task 9 / REQ-049)**: Replaced all dynamic JS toasts and banners with `I18N.t(...)`. Static script scan verified 0 residual hardcoded Chinese in scripts.
  - **Automated Verification**: **219/219 tests PASS** across full regression and integration suite in 16.5s. Authoritative 5,000-note release benchmark passed in 10.28s. Vault verified 100% byte-for-byte read-only.
- **Commit 16: Final Semantic Closure Repair (2 P0 Blockers + 4 P1 Blind Spots Resolved) — PASS**
  - **Outside-Schema Untouched Property Byte-Fidelity (P0 Blocker 1)**: Integrated frontend `wsTouchedKeys` set tracking and backend `touched_keys` validation in `compute_workspace_diff_and_frontmatter`. Outside-schema properties that are not modified by the user (or omitted from updates) are strictly preserved as their original native Python objects (`int`, `bool`, `list`) without silent string stringification; modified outside-schema properties are safely coerced using their original `storage_type`.
  - **Canonical StorageType Drift Detection (P0 Blocker 2)**: Replaced regex/content guessing in `analyze_schema_drift` with direct canonical `PropertyValue.storage_type` comparison against schema expected storage types (`"95"` TEXT vs NUMBER and `"true"` TEXT vs CHECKBOX trigger `TYPE_MISMATCH`). Added `note_link_list` non-empty wikilink list validation. Removed generic `version` fallback to ensure only dedicated `schema_version` triggers version drift.
  - **Governance Profile Preferences Round-Trip & True Replace/Rollback (P1)**: Connected `PREFERENCES_STORAGE` (`preferences.json`) to profile export and import. Implemented `SavedChecksStore.clear()` to guarantee `replace` mode purges stale checks. Added true Phase-2 monkeypatch crash rollback testing verifying schemas, scopes, glossary, saved checks, and preferences are 100% restored.
  - **Proposal Contract 1.0 Strict Field Ignored Semantics (P1)**: Enforced that when `proposal_version == "1.0"`, Contract 1.1 extension fields (`management_purpose`, `source_context`, `target_note_kind`, `proposal_notes`, `schema_target`) return `None` in addition to emitting validation warnings.
  - **Comprehensive i18n Hardcoding Cleanup (P1)**: Eliminated all hardcoded strings in Glossary table badges, buttons, editor modal labels, Profile import drawer, and Proposal validation failure notices across `zh-Hant.json` and `en.json`.
  - **Automated Verification**: **209/209 tests PASS** across full regression and integration suite in 18.2s.
- **Commit 15: Precision Closure Repair (7 Targeted Areas Resolved) — PASS**
  - **Reconciliation Native YAML Types Coercion (P0)**: Integrated canonical `coerce_value` into `compute_workspace_diff_and_frontmatter`; validated via `yaml.safe_load` that exported frontmatter preserves native Python `int`, `float`, `list[str]`, and `bool` types.
  - **Drift Comprehensive Coverage**: Added `MISSING_REQUIRED_RELATIONSHIP`, complete storage type checks (`date`, `datetime`, `list`, `tags`), and actual `SCHEMA_VERSION_MISMATCH` detection.
  - **Drift → Note Context Dual-Display**: Decoupled intent routing in `inspectNoteInWorkspace` so finding diagnosis banner (with auto-highlighting) and 4-state Reconciliation review card render in parallel.
  - **Glossary Global Resolved Overrides & Observed Vault Facts**: Merged user overrides into `/api/glossary/catalog` for authoritative caching; integrated observed vault properties into Glossary Manager table with descriptions and examples editing.
  - **Proposal Alias Resolution & Version Gating**: Fixed dictionary iteration in `reverse_alias_map`; added `alias_target` propagation; enforced strict Contract 1.0 vs 1.1 version-specific warning gating.
  - **Governance Profile Saved Checks & Transactional Rollback**: Included `saved_checks` and UI preferences in profile export/import; implemented Phase 1 semantic pre-validation and transactional rollback snapshot on replace mode.
  - **i18n & Fail-Closed Compatibility**: Added fail-closed `return` on server version mismatch; eliminated hardcoded strings across Proposal, Reconciliation, Profile, and Glossary UI; isolated pytest test runs from `%APPDATA%` via temporary directory fixture (`isolate_test_storage`).
  - **Automated Verification**: **209/209 tests PASS** across full regression and integration suite in 15.2s.

---

## Governance Reminder & Read Order

Read order:
1. `PROJECT.md`
2. `ROADMAP.md`
3. `AGENTS.md`
4. `HANDOFF.md`
5. `git status` / `git diff`
6. `docs/specs/`

---

## Immediate Next Action

1. Verify all test suites and vault read-only integrity on main.
2. Commit documentation updates to `main`.
3. Create local annotated tag `v1.2.0`.
4. Generate final packaging (`dist/Obsidian-Property-Studio-v1.2.0-source.zip`, `dist/Obsidian-Property-Studio-v1.2.0.bundle`, `dist/RELEASE_MANIFEST.json`).
5. Push annotated tag `v1.2.0` to `origin`.
6. Publish GitHub Release `v1.2.0` with assets.
7. Record publication evidence in `evidence/release/v1.2.0_github_release_publication.json` and enter extended operational observation mode.
