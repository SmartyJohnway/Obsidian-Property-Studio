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
Last Verified Gate: `M013 — Release Closure Final In-Place Repair PASS`  
Current Blocker: `NONE`  
Next Action: `PR #1 final merge approval`  
Formal Release Verdict: `PROPERTY_STUDIO_V1_1_0_RELEASE_PASS_WITH_LIMITATIONS`  
Accepted Limitations:  
1. `Windows 11 AMD64 native verification recorded as NOT YET VERIFIED due to test host unavailability (accepted non-blocking release limitation per human approved contract).`  
2. `Windows 10 Browser DOM automation recorded as NOT YET VERIFIED (Windows 10 native launcher invocation and live HTTP socket walkthrough fully verified; accepted non-blocking release limitation).`  
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

### Result
`PASS` (95/95 baseline tests pass, git commit verified)

---

# M002 — Lightweight Local-First Bilingual i18n Engine

Status: `PASS`

### Result
`PASS` (4/4 i18n tests pass, offline verified)

---

# M003 — Context-Aware Multi-Folder & Single-Note Scope Filter Engine

Status: `PASS`

### Result
`PASS` (5/5 scope tests pass)

---

# M004 — Beginner-Friendly Schema Builder with Recipe Suggestions

Status: `PASS`

### Result
`PASS` (Design test suite pass)

---

# M005 — Blank Note Property Fill & Copy Engine

Status: `PASS`

### Result
`PASS` (Fill test suite pass)

---

# M006 — Note Properties Workspace (Inspect, Edit & Semantic Diff)

Status: `PASS`

### Result
`PASS` (4/4 note workspace tests pass)

---

# M007 — Scope-Aware Property Relationship Inbox & 4-State Analysis

Status: `PASS`

### Result
`PASS` (3/3 relationship tests pass)

---

# M008 — Read-Only Body Wikilink Relationship Analysis Engine

Status: `PASS`

### Result
`PASS` (3/3 body links tests pass)

---

# M009 — User-Initiated Saved Relationship Checks

Status: `PASS`

### Result
`PASS` (2/2 saved checks tests pass)

---

# M010 — Scope-Aware Property Health & Refactor Planner Isolation

Status: `PASS`

### Result
`PASS` (Health & Refactor scope isolation tests pass)

---

# M011 — 5,000-Note Performance Benchmark & Full Suite Verification

Status: `PASS`

### Objective
Execute full regression test suite (all 140 tests) and record formal >=5,000-note benchmark evidence with byte-for-byte read-only validation.

### Tasks
- [x] `M011-T01` Run 5,000-note synthetic vault benchmark generator and recorder (`scripts/benchmark.py`).
- [x] `M011-T02` Record timing, memory, and performance observations in `evidence/benchmark.json`.
- [x] `M011-T03` Execute comprehensive Vault read-only test `tests/test_v11_vault_readonly.py` covering V11-018.
- [x] `M011-T04` Run full pytest suite across all modules.

### Acceptance Criteria
- [x] `M011-AC01` All 140 tests PASS without failures.
- [x] `M011-AC02` Benchmark on 5,040 notes recorded (5.062s scan, 5.227s full analysis).
- [x] `M011-AC03` `V11-018` Vault byte-for-byte read-only verified.

### Result
`PASS` (140/140 tests pass, benchmark recorded in `evidence/benchmark.json`: 5.062s scan / 5.227s total analysis)

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
- [x] `M012-AC01` Windows 10 (Build 19045+) native launcher and live HTTP server walkthrough verified (`evidence/integration/m012_v110_windows10_native_acceptance.json`).
- [x] `M012-AC02` Windows 11 (64-bit AMD64) and Windows 10 Browser DOM automation recorded accurately as `NOT YET VERIFIED` (accepted non-blocking release limitations).
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

### Result
`PASS` (Verified across 140 test cases in `tests/`, Windows 10 live HTTP native acceptance test, Refactor Merge operation contract, and automated release packaging verification)

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
  ├─ Refactor Planner (Rename, Merge, Normalize, Convert Type)
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
