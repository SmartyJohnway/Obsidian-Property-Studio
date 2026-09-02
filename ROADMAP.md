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
Current Milestone: `M015`  
Current Milestone Status: `PASS`  
Current Task: `NONE`  
Last Verified Gate: `M015 — v1.2 Governance Transition & Architecture Freeze PASS`  
Current Blocker: `NONE`  
Next Action: `Awaiting Human Owner (Dr. J) review and approval of M015 architecture freeze before starting M016 implementation.`  
Implementation: `NOT STARTED`  
Automated Verification: `PASS (176/176 baseline tests pass)`  
Human Verified Acceptance: `NOT YET VERIFIED`  
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

Status: `PLANNED`

### Objective
Implement reusable cross-module context/state transfer engine and CTA closure testing framework to ensure zero dead-end CTAs.

### Tasks
- [ ] `M016-T01` Define regression tests `tests/test_v12_state_transfer.py` covering V12-WFC-*.
- [ ] `M016-T02` Implement client-side explicit state manager `app/ui/state_transfer.js` preserving navigation intent, schema_id, finding_id, note_path, and proposal candidates.
- [ ] `M016-T03` Expose state serialization / validation endpoints where required.
- [ ] `M016-T04` Build automated CTA closure verification suite.

### Acceptance Criteria
- [ ] `M016-AC01` State transfer survives cross-module navigation without accidental loss.
- [ ] `M016-AC02` CTA closure test suite verifies all primary navigation paths.

### Required Evidence
- `tests/test_v12_state_transfer.py` execution results.
- Automated CTA navigation log.

### Result
`NOT YET VERIFIED`

---

# M017 — Personal Glossary & Named Schema Library

Status: `PLANNED`

### Objective
Implement user-editable Property Glossary with precedence hierarchy and Named Schema Library with CRUD operations persisted outside Vault.

### Tasks
- [ ] `M017-T01` Define regression tests `tests/test_v12_glossary.py` and `tests/test_v12_named_schemas.py` covering V12-GLO-* and V12-SCH-*.
- [ ] `M017-T02` Implement `app/core/user_glossary.py` with precedence `System Built-in → User Override → Observed Vault Facts` and canonical key immutability.
- [ ] `M017-T03` Implement `app/core/named_schemas.py` with Schema CRUD and metadata.
- [ ] `M017-T04` Implement app-local persistence layer in `app/core/storage.py` outside Vault.
- [ ] `M017-T05` Build UI for Glossary Manager and Named Schema Library with zh-Hant / English i18n.
- [ ] `M017-T06` Connect Schema Designer `[Adopt Schema]` to Save to Named Schema Library.

### Acceptance Criteria
- [ ] `M017-AC01` User glossary allows overriding labels/descriptions while canonical keys remain untouched.
- [ ] `M017-AC02` Named Schemas persist across app restarts outside Vault.
- [ ] `M017-AC03` Precedence hierarchy verified with zero Vault mutation.

### Required Evidence
- Automated test suite results.
- App-local storage inspection verifying outside-vault persistence.

### Result
`NOT YET VERIFIED`

---

# M018 — Existing Note Reconciliation & Health Drilldown

Status: `PLANNED`

### Objective
Implement Schema → Existing Note Reconciliation in Note Workspace (4 states: Matches, Missing, Conflict, Outside-schema) and Health Finding → Note Workspace one-click drilldown.

### Tasks
- [ ] `M018-T01` Define regression tests `tests/test_v12_reconciliation.py` and `tests/test_v12_health_drilldown.py` covering V12-REC-* and V12-HLT-*.
- [ ] `M018-T02` Implement reconciliation algorithm in `app/core/reconciliation.py` computing 4 distinct property states against target note.
- [ ] `M018-T03` Expose API endpoints `/api/reconcile/inspect`, `/api/reconcile/preview`.
- [ ] `M018-T04` Build Note Workspace Reconciliation UI with 4-state badges, non-schema property preservation, semantic diff, and validated frontmatter copy.
- [ ] `M018-T05` Wire Health Finding list items to drilldown directly into Note Workspace with finding highlight.

### Acceptance Criteria
- [ ] `M018-AC01` REQ-043 full workflow closed (Schema -> Existing Note -> 4-state reconciliation -> diff -> copy).
- [ ] `M018-AC02` REQ-048 health drilldown opens exact note with preserved finding context.
- [ ] `M018-AC03` Vault remains strictly read-only.

### Required Evidence
- Reconciliation unit & integration test results.
- Health drilldown navigation test results.

### Result
`NOT YET VERIFIED`

---

# M019 — Scope Governance & Schema Drift

Status: `PLANNED`

### Objective
Implement Scope → Expected Named Schema assignment and Property Health Desired vs Actual schema drift diagnostics.

### Tasks
- [ ] `M019-T01` Define regression tests `tests/test_v12_scope_governance.py` and `tests/test_v12_drift.py` covering V12-SCP-* and V12-DRIFT-*.
- [ ] `M019-T02` Implement Scope Expected Schema association in `app/core/scope_governance.py`.
- [ ] `M019-T03` Implement Schema Drift diagnostic engine in `app/core/drift.py` (missing expected, type mismatch, value drift, unexpected properties).
- [ ] `M019-T04` Update Property Health UI with Desired vs Actual drift summary and breakdown cards.

### Acceptance Criteria
- [ ] `M019-AC01` Scope can be assigned an Expected Schema without writing to Vault.
- [ ] `M019-AC02` Health diagnostics accurately report Desired vs Actual drift.

### Required Evidence
- Automated test results and drift calculation reports.

### Result
`NOT YET VERIFIED`

---

# M020 — External AI Proposal Workflow & Companion Skill

Status: `PLANNED`

### Objective
Implement External AI Proposal Review Workspace (replacing raw JSON endpoint) and deliver the independent `obsidian-property-advisor` Companion Skill.

### Tasks
- [ ] `M020-T01` Define regression tests `tests/test_v12_ai_proposal.py` and `tests/test_v12_skill_contract.py` covering V12-AIP-* and V12-SKL-*.
- [ ] `M020-T02` Implement Proposal comparison engine against Scope, Whole Vault, Glossary, and Schema Library in `app/core/ai_proposal.py`.
- [ ] `M020-T03` Build UI Proposal Review Workspace with Accept as Named Schema, Edit Candidate, and Reject actions.
- [ ] `M020-T04` Implement and package `skills/obsidian-property-advisor/` (SKILL.md, references, example fixtures).
- [ ] `M020-T05` Author test fixtures validating Skill proposal outputs against Property Studio contract validator.

### Acceptance Criteria
- [ ] `M020-AC01` REQ-046 full proposal review workflow closed (paste/open -> validate -> compare -> review -> accept/edit/reject).
- [ ] `M020-AC02` Companion Skill outputs validate seamlessly against Proposal Contract without Core App runtime dependency.

### Required Evidence
- Proposal review test suite and Skill fixture validation artifacts.

### Result
`NOT YET VERIFIED`

---

# M021 — Schema Versioning, Migration Planning & Governance Profile [P1 — Should Ship]

Status: `PLANNED`

> **P1 Scope Notice:** This milestone encompasses P1 features. Target is full implementation during v1.2.0. If deferred, it requires explicit, recorded Human Owner (Dr. J) approval prior to release; silent omission is prohibited.

### Objective
Implement Schema versioning (v1 -> v2), read-only Migration Planner, and complete Governance Profile JSON export/import with change preview and fail-closed safety.

### Tasks
- [ ] `M021-T01` Define regression tests `tests/test_v12_migration.py` and `tests/test_v12_profile_io.py` covering V12-MIG-* and V12-PROF-*.
- [ ] `M021-T02` Implement schema version diffing and migration impact evaluator in `app/core/schema_migration.py`.
- [ ] `M021-T03` Build Migration Planner UI displaying affected notes and impact summary (strictly planning-only).
- [ ] `M021-T04` Implement Governance Profile export and import engine with schema validation in `app/core/governance_profile.py`.
- [ ] `M021-T05` Build Profile Import/Export UI with change preview and fail-closed error reporting.

### Acceptance Criteria
- [ ] `M021-AC01` Schema migration planner outputs human-readable impact plan without writing to Vault.
- [ ] `M021-AC02` Governance Profile exports and imports round-trip cleanly with full validation.

### Required Evidence
- Migration planner test output and Profile round-trip validation evidence.

### Result
`NOT YET VERIFIED`

---

# M022 — Full Workflow Closure, Human Acceptance & Release Gate

Status: `PLANNED`

### Objective
Execute complete Workflow Closure Matrix validation, run full regression suite and 5,000-note benchmark, verify Vault byte-for-byte read-only integrity, conduct human walkthrough on Windows 10 production UI, verify P0 completion and P1 implementation (or recorded deferral), and package v1.2.0 release artifacts.

### Tasks
- [ ] `M022-T01` Execute complete Workflow Closure Matrix automated test suite covering all primary CTAs.
- [ ] `M022-T02` Run 5,000-note performance benchmark and record in `evidence/benchmark.json`.
- [ ] `M022-T03` Verify Vault byte-for-byte read-only integrity across all v1.2 workflows.
- [ ] `M022-T04` Conduct Windows 10 production UI walkthrough acceptance with Human Owner (Dr. J).
- [ ] `M022-T05` Verify P0 requirements complete and P1 status (PASS or recorded Human-approved deferral).
- [ ] `M022-T06` Run four-file consistency check (PROJECT, ROADMAP, HANDOFF, AGENTS).
- [ ] `M022-T07` Generate release packaging and record formal release verdict.

### Acceptance Criteria
- [ ] `M022-AC01` All automated regression and closure tests PASS.
- [ ] `M022-AC02` 5,000-note benchmark recorded.
- [ ] `M022-AC03` Vault remains byte-for-byte untouched.
- [ ] `M022-AC04` Human Owner walkthrough PASS.
- [ ] `M022-AC05` Four-file consistency gate PASS.

### Required Evidence
- Release manifest, benchmark JSON, and Windows 10 native walkthrough log.

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
