# Roadmap

> Project: `Obsidian Property Studio`  
> Target Release: `v1.2.0`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Roadmap Type: `v1.2.0 Personal Property Governance Execution Roadmap`  
> Baseline: `v1.1.0 Formal Mainline (176/176 tests PASS, published release cca408c)`  
> Active Target Specification: `docs/specs/Obsidian_Property_Studio_v1.2.0_Spec.md` (SHA-256: `8760e592381685c4a31ae5eac2b8692fd8fa80ebc6a8ad7044fcb4c037f7187b`)  
> Archived Roadmap: `docs/archive/ROADMAP_v1.1.0.md` (SHA-256: `d68f8ac57411896dd1b2b10b0716629f2d12c46b1e0bb6a2a1368c961ee7ac2a`)

---

##### Current State

Project State: `ACTIVE`  
Current Target: `v1.2.0`  
Current Milestone: `M022`  
Current Milestone Status: `IN_PROGRESS`  
Current Task: `M022-T04`  
Last Verified Gate: `M021 — Schema Versioning, Migration Planning & Governance Profile PASS`  
Current Blocker: `NONE`  
Next Action: `Package v1.2.0 RC and submit to Human Owner (Dr. J) for final Windows 10 production UI walkthrough acceptance (M022-T04 / M022-AC04).`  
Implementation: `COMPLETE (Commit 18 Storage Side-Effect, Pure Path Resolution & Migration Atomicity Closure: Pure Path Resolution before mkdir, Negative Inside-Vault 0-Mutation Proof, Atomic Validate-Before-Persist Legacy Migration with Exact Readback, One-time Idempotency Guard, Path Migration out of __init__ with Fail-Closed Protection, Governance Profile Clear-Stage Rollback & Preferences Preview, 0 residual openDrawer/toast hardcoded Chinese)`  
Automated Verification: `PASS (218/218 tests pass, 5,040-note benchmark 4.794s analysis / 4.639s scan, Vault 100% byte-for-byte read-only and 0 directory mutation on violation)`  
Human Verified Acceptance: `NOT YET VERIFIED`  
Release Readiness: `READY_FOR_HUMAN_ACCEPTANCE` (Human Owner UI Walkthrough: `NOT YET VERIFIED`)  
Accepted Limitation: `Windows 11 AMD64 native verification recorded as NOT YET VERIFIED due to test host unavailability (accepted non-blocking release limitation per human approved contract).`  
Last Updated: `2026-09-03`

---

# 1. Authority & Governance Boundaries

This ROADMAP is the sole active authoritative execution plan for `Obsidian Property Studio v1.2.0`.

- `PROJECT.md` defines accepted v1.2.0 Product Truth, Scope, and Non-goals.
- `ROADMAP.md` (this file) defines milestone execution, acceptance criteria, and evidence.
- `HANDOFF.md` tracks the latest runtime recovery context.
- `AGENTS.md` governs agent operating behavior.
- `docs/specs/Obsidian_Property_Studio_v1.2.0_Spec.md` is the formal product and workflow specification for v1.2.0 (SHA-256: `8760e592381685c4a31ae5eac2b8692fd8fa80ebc6a8ad7044fcb4c037f7187b`).
- `docs/specs/v1.2.0_App_Local_Governance_Storage.md` is the approved architecture specification for app-local persistence outside Vault (SHA-256: `d0acd3a28a3597d3aacff1119fa78628df1c450c50c9f75060fb36cbb9e5b573`).
- `docs/specs/v1.2.0_Workflow_Closure_Matrix.md` is the approved architecture specification for CTA closure and verification (SHA-256: `380f243e7b480768700611f79aaba0bfc6e60a005e1b4afc590c969968441dc9`).
- `docs/specs/v1.2.0_Proposal_Contract_Compatibility.md` is the approved architecture specification for AI proposal contracts and skill interoperability (SHA-256: `fc9cc011cf43dc2000f37bd5e700f4a743a708255d69eb05b958e2c36881c43a`).
- `docs/archive/ROADMAP_v1.1.0.md` is an immutable historical snapshot of the published v1.1.0 release (SHA-256: `d68f8ac57411896dd1b2b10b0716629f2d12c46b1e0bb6a2a1368c961ee7ac2a`).
- `docs/archive/ROADMAP_v1.0.0.md` is an immutable historical snapshot of the published v1.0.0 release.

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

# 3. v1.2.0 Engineering Regression & Governance Contracts

All 176 retained regression tests (95 v1.0.0 tests + 18 v1.1.0 tests `V11-001` ~ `V11-018` + M014 human walkthrough tests + 14 glossary tests) remain permanently active and must pass.

v1.2.0 establishes the following regression and contract test families:

- `V12-WFC-*` Workflow Closure Contract & cross-module state transfer.
- `V12-GLO-*` User-editable Property Glossary CRUD, persistence & 3-level precedence hierarchy.
- `V12-SCH-*` Named Schema Library CRUD, metadata, and out-of-vault persistence.
- `V12-REC-*` Schema to Existing Note Reconciliation (4 states: Matches, Missing, Conflict, Outside-schema preserved).
- `V12-SCP-*` Scope to Expected Schema assignment association & persistence.
- `V12-DRIFT-*` Desired vs Actual Schema Drift diagnostics in Property Health.
- `V12-HLT-*` Health diagnostic finding to exact Note Workspace drilldown with preserved context.
- `V12-AIP-*` External AI Proposal Review workspace (compatibility analysis, Accept, Edit, Reject).
- `V12-SKL-*` Companion Skill contract adherence, fixtures validation & decoupled execution.
- `V12-MIG-*` Schema Versioning diffing & Scope-aware Migration Planning [P1].
- `V12-PROF-*` Governance Profile JSON import/export round-trip & fail-closed validation [P1].
- `V12-RO-*` Vault strict byte-for-byte read-only guarantee across all v1.2 workflows.
- `V12-I18N-*` 100% zh-Hant / English bilingual parity across all v1.2 UI modules.

---

# M015 — v1.2 Governance Transition & Architecture Freeze

Status: `PASS`

### Objective
Establish the formal v1.2.0 governance baseline, archive the v1.1.0 roadmap, update PROJECT.md, AGENTS.md, ROADMAP.md, freeze app-local persistence architecture (`docs/specs/v1.2.0_App_Local_Governance_Storage.md`), freeze Workflow Closure Matrix (`docs/specs/v1.2.0_Workflow_Closure_Matrix.md`), and freeze Proposal Contract compatibility strategy (`docs/specs/v1.2.0_Proposal_Contract_Compatibility.md`) before starting implementation.

### Tasks
- [x] `M015-T01` Re-enter project following mandatory order: PROJECT → ROADMAP → AGENTS → HANDOFF → git status/log → test suite.
- [x] `M015-T02` Install approved `docs/specs/Obsidian_Property_Studio_v1.2.0_Spec.md` and verify SHA-256 (`8760e592381685c4a31ae5eac2b8692fd8fa80ebc6a8ad7044fcb4c037f7187b`).
- [x] `M015-T03` Archive `ROADMAP.md` (v1.1.0) to `docs/archive/ROADMAP_v1.1.0.md` and record SHA-256 (`d68f8ac57411896dd1b2b10b0716629f2d12c46b1e0bb6a2a1368c961ee7ac2a`).
- [x] `M015-T04` Update `PROJECT.md` with v1.2.0 position, requirements REQ-040 ~ REQ-052, Success Criteria SC-23 ~ SC-34, P0/P1 scope fidelity, and Non-Goals.
- [x] `M015-T05` Update `AGENTS.md` with durable v1.2 project-specific operating rules and P0/P1 release gate logic.
- [x] `M015-T06` Author active v1.2.0 `ROADMAP.md` with milestones M015 ~ M022.
- [x] `M015-T07` Freeze App-local Governance Storage Architecture in `docs/specs/v1.2.0_App_Local_Governance_Storage.md`.
- [x] `M015-T08` Freeze Workflow Closure Matrix and baseline CTA coverage in `docs/specs/v1.2.0_Workflow_Closure_Matrix.md`.
- [x] `M015-T09` Freeze Proposal Contract Compatibility Strategy in `docs/specs/v1.2.0_Proposal_Contract_Compatibility.md`.
- [x] `M015-T10` Run final M015 baseline verification (176 tests) and complete architecture freeze governance commit.

### Acceptance Criteria
- [x] `M015-AC01` Clean read-order re-entry completed.
- [x] `M015-AC02` Four governance files updated, consistent, and active target set to v1.2.0 with P0/P1 scope fidelity.
- [x] `M015-AC03` v1.1.0 Roadmap archived with recorded SHA-256.
- [x] `M015-AC04` Storage architecture frozen in `docs/specs/v1.2.0_App_Local_Governance_Storage.md`.
- [x] `M015-AC05` Workflow Closure Matrix frozen in `docs/specs/v1.2.0_Workflow_Closure_Matrix.md`.
- [x] `M015-AC06` Proposal Contract compatibility frozen in `docs/specs/v1.2.0_Proposal_Contract_Compatibility.md`.
- [x] `M015-AC07` 176 retained tests PASS.
- [x] `M015-AC08` M015 governance transition & architecture freeze commit completed.

### Required Evidence
- `git status` clean on `feature/v1.2.0`.
- Pytest baseline run output: `176/176 tests PASS`.
- Frozen architecture specifications in `docs/specs/`.
- Governance transition commit hash recorded in HANDOFF.md.

### Result
`PASS` (All 10 tasks completed, 176/176 baseline tests pass, 3 architecture freeze specifications authored and frozen)

---

# M016 — Workflow Closure Foundation & State Transfer

Status: `PASS`

### Objective
Implement reusable cross-module context/state transfer engine and CTA closure testing framework to ensure zero dead-end CTAs.

### Tasks
- [x] `M016-T01` Define regression tests `tests/test_v12_state_transfer.py` covering V12-WFC-*.
- [x] `M016-T02` Implement client-side explicit state manager `app/ui/state_transfer.js` preserving navigation intent, schema_id, finding_id, note_path, and proposal candidates.
- [x] `M016-T03` Expose state serialization / validation endpoints where required (`/api/state/validate_context`).
- [x] `M016-T04` Build automated CTA closure verification suite and wire into index.html navigation.

### Acceptance Criteria
- [x] `M016-AC01` State transfer survives cross-module navigation without accidental loss.
- [x] `M016-AC02` CTA closure test suite verifies all primary navigation paths.

### Required Evidence
- `tests/test_v12_state_transfer.py` execution results (6 tests PASS).

### Result
`PASS`

---

# M017 — Personal Glossary & Named Schema Library

Status: `PASS`

### Objective
Implement user-editable Property Glossary with precedence hierarchy and Named Schema Library with CRUD operations persisted outside Vault.

### Tasks
- [x] `M017-T01` Define regression tests `tests/test_v12_glossary.py` and `tests/test_v12_named_schemas.py` covering V12-GLO-* and V12-SCH-*.
- [x] `M017-T02` Implement `app/core/user_glossary.py` with precedence `System Built-in → User Override → Observed Vault Facts` and canonical key immutability.
- [x] `M017-T03` Implement `app/core/named_schemas.py` with Schema CRUD and metadata.
- [x] `M017-T04` Implement app-local persistence layer in `app/storage/local_storage.py` outside Vault.
- [x] `M017-T05` Build UI for Glossary Manager and Named Schema Library with zh-Hant / English i18n.
- [x] `M017-T06` Connect Schema Designer `[Adopt Schema]` to Save to Named Schema Library.

### Acceptance Criteria
- [x] `M017-AC01` User glossary allows overriding labels/descriptions while canonical keys remain untouched.
- [x] `M017-AC02` Named Schemas persist across app restarts outside Vault.
- [x] `M017-AC03` Precedence hierarchy verified with zero Vault mutation.

### Required Evidence
- Automated test suite results (`tests/test_v12_glossary.py`, `tests/test_v12_named_schemas.py` PASS).
- Storage persistence and bilingual alignment (299/299 keys aligned PASS).

### Result
`PASS`

---

# M018 — Existing Note Reconciliation & Health Drilldown

Status: `PASS`

### Objective
Implement Schema → Existing Note Reconciliation in Note Workspace (4 states: Matches, Missing, Conflict, Outside-schema) and Health Finding → Note Workspace one-click drilldown.

### Tasks
- [x] `M018-T01` Define regression tests `tests/test_v12_reconciliation.py` and `tests/test_v12_health_drilldown.py` covering V12-REC-* and V12-HLT-*.
- [x] `M018-T02` Implement reconciliation algorithm in `app/core/reconciliation.py` computing 4 distinct property states against target note.
- [x] `M018-T03` Expose API endpoints `/api/reconcile/inspect`, `/api/reconcile/preview`.
- [x] `M018-T04` Build Note Workspace Reconciliation UI with 4-state badges, non-schema property preservation, semantic diff, and validated frontmatter copy.
- [x] `M018-T05` Wire Health Finding list items to drilldown directly into Note Workspace with finding highlight.

### Acceptance Criteria
- [x] `M018-AC01` REQ-043 full workflow closed (Schema -> Existing Note -> 4-state reconciliation -> diff -> copy).
- [x] `M018-AC02` REQ-048 health drilldown opens exact note with preserved finding context.
- [x] `M018-AC03` Vault remains strictly read-only.

### Required Evidence
- Reconciliation unit & integration test results (`tests/test_v12_reconciliation.py` PASS).
- Health drilldown navigation test results (`tests/test_v12_health_drilldown.py` PASS).

### Result
`PASS`

---

# M019 — Scope Governance & Schema Drift

Status: `PASS`

### Objective
Implement Scope → Expected Named Schema assignment and Property Health Desired vs Actual schema drift diagnostics.

### Tasks
- [x] `M019-T01` Define regression tests `tests/test_v12_scope_governance.py` and `tests/test_v12_drift.py` covering V12-SCP-* and V12-DRIFT-*.
- [x] `M019-T02` Implement Scope Expected Schema association in `app/core/scope_governance.py`.
- [x] `M019-T03` Implement Schema Drift diagnostic engine in `app/core/drift.py` (missing expected, type mismatch, value drift, unexpected properties).
- [x] `M019-T04` Update Property Health UI with Desired vs Actual drift summary and breakdown cards.

### Acceptance Criteria
- [x] `M019-AC01` Scope can be assigned an Expected Schema without writing to Vault.
- [x] `M019-AC02` Health diagnostics accurately report Desired vs Actual drift.

### Required Evidence
- Automated test results (`tests/test_v12_scope_governance.py`, `tests/test_v12_drift.py` PASS).

### Result
`PASS`

---

# M020 — External AI Proposal Workflow & Companion Skill

Status: `PASS`

### Objective
Implement External AI Proposal Review Workspace (replacing raw JSON endpoint) and deliver the independent `obsidian-property-advisor` Companion Skill.

### Tasks
- [x] `M020-T01` Define regression tests `tests/test_v12_proposal_workflow.py` covering V12-PRP-* and Contract 1.0/1.1 compatibility.
- [x] `M020-T02` Update Proposal import engine in `app/core/proposal.py` to support Proposal Contract 1.1 additions while retaining 100% backward compatibility with Proposal Contract 1.0.
- [x] `M020-T03` Build UI Proposal Review Workspace with Accept as Named Schema and Reconcile with Note actions.
- [x] `M020-T04` Implement and package `skills/obsidian-property-advisor/` (SKILL.md, storage types, UI controls, example fixtures).
- [x] `M020-T05` Author test fixtures validating Skill proposal outputs against Property Studio contract validator.

### Acceptance Criteria
- [x] `M020-AC01` REQ-046 full proposal review workflow closed (paste/open -> validate -> compare -> review -> accept/reconcile).
- [x] `M020-AC02` Companion Skill outputs validate seamlessly against Proposal Contract without Core App runtime dependency.

### Required Evidence
- Proposal review test suite (`tests/test_v12_proposal_workflow.py` PASS) and companion skill artifact `skills/obsidian-property-advisor/SKILL.md`.

### Result
`PASS`

---

# M021 — Schema Versioning, Migration Planning & Governance Profile [P1 — Should Ship]

Status: `PASS`

> **P1 Scope Notice:** Full implementation delivered for v1.2.0.

### Objective
Implement Schema versioning (v1 -> v2), read-only Migration Planner, and complete Governance Profile JSON export/import with change preview and fail-closed safety.

### Tasks
- [x] `M021-T01` Define regression tests `tests/test_v12_migration.py` and `tests/test_v12_governance_profile.py` covering V12-MIG-* and V12-GOV-*.
- [x] `M021-T02` Implement schema version diffing and migration impact evaluator in `app/core/migration.py`.
- [x] `M021-T03` Build Migration Planner UI displaying affected notes and impact summary (strictly planning-only).
- [x] `M021-T04` Implement Governance Profile export and import engine with SHA-256 validation in `app/core/governance_profile.py`.
- [x] `M021-T05` Build Profile Import/Export UI with change preview and fail-closed error reporting.

### Acceptance Criteria
- [x] `M021-AC01` Schema migration planner outputs human-readable impact plan without writing to Vault.
- [x] `M021-AC02` Governance Profile exports and imports round-trip cleanly with full validation.

### Required Evidence
- Migration planner test output (`tests/test_v12_migration.py` PASS) and Profile round-trip validation evidence (`tests/test_v12_governance_profile.py` PASS).

### Result
`PASS`

---

# M022 — Full Workflow Closure, Human Acceptance & Release Gate

Status: `IN_PROGRESS`

### Objective
Execute complete Workflow Closure Matrix validation, run full regression suite and 5,000-note benchmark, verify Vault byte-for-byte read-only integrity, conduct human walkthrough on Windows 10 production UI, verify P0 completion and P1 implementation, and package v1.2.0 release artifacts.

### Tasks
- [x] `M022-T01` Execute complete Workflow Closure Matrix automated test suite (218/218 tests PASS, includes `tests/test_v12_storage_closure.py` validating 9 pure path resolution, negative zero-mutation, and atomic migration invariants).
- [x] `M022-T02` Run 5,000-note performance benchmark and record in `evidence/benchmark.json` (4.794s analysis / 4.639s scan over 5,040 notes).
- [x] `M022-T03` Verify Vault byte-for-byte read-only integrity across all v1.2 workflows (`evidence/integration/m022_v120_vault_readonly.json`).
- [ ] `M022-T04` Conduct Windows 10 production UI walkthrough acceptance with Human Owner (Dr. J).
- [x] `M022-T05` Verify P0 requirements complete and P1 status (P1 M021 fully implemented).
- [x] `M022-T06` Run four-file consistency check (PROJECT, ROADMAP, HANDOFF, AGENTS).
- [x] `M022-T07` Generate release packaging and record formal release verdict (`scripts/package_v120_release.py`).

### Acceptance Criteria
- [x] `M022-AC01` All automated regression and closure tests PASS (218/218).
- [x] `M022-AC02` 5,000-note benchmark recorded (4.794s analysis / 4.639s scan over 5,040 notes).
- [x] `M022-AC03` Vault remains byte-for-byte untouched and zero directory created on violation.
- [ ] `M022-AC04` Human Owner walkthrough PASS (Reserved for Human Owner Dr. J).
- [x] `M022-AC05` Four-file consistency gate PASS.

### Required Evidence
- Release manifest, benchmark JSON (`evidence/benchmark.json`, `evidence/integration/m022_v120_benchmark.json`), and Vault readonly record (`evidence/integration/m022_v120_vault_readonly.json`).

### Result
`NOT YET VERIFIED`

---

# 4. Final v1.2.0 Integration Summary

The v1.2.0 release evolves Obsidian Property Studio into a **Personal Property Governance System**:

```text
Vault (Strict Read-Only Input)
  │
  ├─ User Property Glossary (Built-in → User Override → Vault Facts) [P0]
  │
  ├─ Named Schema Library (Reusable, Versioned, Outside Vault) [P0]
  │    │
  │    ├─ Schema → Existing Note Reconciliation (Matches, Missing, Conflict, Preserved) [P0]
  │    │
  │    ├─ Scope Expected Schema Assignment & Drift Diagnostics (Health Desired vs Actual) [P0]
  │    │
  │    └─ Schema Versioning & Migration Planning (Scope Impact, Planning-only) [P1]
  │
  ├─ External AI Proposal Review Workspace (Contract Validation, Compare, Accept/Edit/Reject) [P0]
  │
  ├─ Companion AI Skill (obsidian-property-advisor, Independent, Decoupled) [P0]
  │
  └─ App-Local Persistence & Governance Profile I/O (Export/Import, Backup, Outside Vault) [P0 / P1]
```

No evidence, no PASS.  
No contradictory evidence, no PASS.
