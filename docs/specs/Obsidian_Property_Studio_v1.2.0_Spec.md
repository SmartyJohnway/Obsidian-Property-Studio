# Obsidian Property Studio v1.2.0 — Product & Workflow Specification

**Document status:** Human-approved planning specification  
**Target version:** v1.2.0  
**Product direction:** Personal Property Governance System  
**Baseline:** v1.1.0 published and closed  
**Primary safety invariant:** The selected Obsidian Vault is an input source, never a writable workspace.

---

## 0. Executive Summary

Obsidian Property Studio v1.2.0 is the next major product step after v1.1.0.

v1.1.0 established a stable, local-first, bilingual, read-only Property governance tool with:

- Vault → Scope → Note → Schema context
- Property discovery and health analysis
- Schema Designer
- Note Properties Workspace
- New Frontmatter generation
- Refactor planning
- Relationships analysis
- Property Vocabulary Layer
- Traditional Chinese / English UI
- Light / Dark themes
- strict Vault read-only guarantees

v1.2.0 moves the product from:

> **“Understand and use Properties.”**

to:

> **“Build and govern your own Property system.”**

Core model:

```text
User Property Glossary
        +
Named Schema Library
        +
Scope → Expected Schema
        +
Desired vs Actual Drift
        +
Existing Note Reconciliation
        +
Migration Planning
        +
External AI Proposal Review
        +
Optional AI Property Advisor Skill
        =
Personal Property Governance System
```

v1.2.0 must preserve:

> **Local deterministic governance + Human decision + Read-only Vault safety.**

AI may advise. Deterministic tooling validates. The human decides. The application never silently writes to the Vault.

---

# 1. Release Boundary

v1.1.0 is a published immutable historical release.

v1.2.0 development must not:

- move or rewrite the `v1.1.0` tag;
- alter v1.1.0 release assets;
- rewrite archived v1.1.0 evidence as current v1.2 evidence;
- regress the v1.1.0 read-only contract.

Before v1.2 implementation begins:

```text
current ROADMAP.md
→ docs/archive/ROADMAP_v1.1.0.md

new active ROADMAP.md
→ v1.2.0
```

---

# 2. Product Position

## 2.1 One-line definition

> **Build and govern your own Property system — without surrendering control of your Vault.**

繁中：

> **建立並治理屬於你自己的 Property 系統，同時讓 Vault 始終掌握在你手上。**

## 2.2 Product evolution

```text
v1.0
Understand / Design / Fill / Refactor

        ↓

v1.1
Scope / Relationships / Bilingual /
Property Vocabulary / Better UX

        ↓

v1.2
Personal Property Governance System

Glossary
Schema Library
Expected State
Drift
Reconciliation
Migration
AI Advisory Bridge
Governance Profile
```

---

# 3. Non-Negotiable Principles

## 3.1 Strict Vault read-only

Property Studio must never automatically:

- create a Note in the selected Vault;
- modify Frontmatter;
- modify Markdown body;
- rename / move / delete a Note;
- rewrite Body Wikilinks;
- modify `.obsidian/`;
- Apply migration plans.

Outputs remain:

- preview;
- comparison;
- advisory result;
- migration plan;
- validated YAML;
- clipboard content;
- external report;
- external governance profile.

## 3.2 Canonical keys remain stable

Display labels may change. Canonical YAML Property keys do not.

```text
UI:
狀態 (status)

Canonical key:
status
```

Do not silently emit translated YAML keys.

## 3.3 AI advisory boundary

```text
AI / Agent
    ↓
Proposal
    ↓
Deterministic validation
    ↓
Compare against real Vault / Glossary / Schema
    ↓
Human review
    ↓
Accept / Edit / Reject
```

## 3.4 No forced ontology

No mandatory PARA, taxonomy, relationship rules, or universal Property naming.

Built-in presets and glossary entries are advisory starting points.

## 3.5 No Dead-End CTA

Every primary CTA must have:

```text
User Intent
↓
Action
↓
State Transfer
↓
Deterministic Processing
↓
Visible Result
↓
Meaningful Next Action or Terminal Artifact
```

A page change alone is not workflow completion unless navigation itself is the explicit purpose.

A raw backend JSON dump is not a finished user workflow.

---

# 4. Formal v1.2 Requirements

The requirement numbering continues after v1.1.0 `REQ-039`.

## REQ-040 — Workflow Closure Contract

Every primary CTA must be represented in a maintained Workflow Closure Matrix.

Each CTA defines:

- Starting State
- User Intent
- Action
- State Transfer
- Processing
- Visible Result
- Terminal Outcome / Next Action
- Failure Path
- Automated Verification
- Human Verification

A CTA cannot PASS merely because a handler exists or an API returns HTTP 200.

## REQ-041 — User-editable Property Glossary

Users may manage personal display/advisory metadata for canonical Property keys.

At minimum:

- canonical key;
- Traditional Chinese label;
- English label;
- description;
- usage guidance;
- examples;
- optional aliases;
- optional category/domain.

The glossary must not mutate Vault keys.

Precedence:

```text
System Built-in Glossary
        ↓
User Override
        ↓
Observed Vault Facts
```

These must remain visibly distinguishable.

## REQ-042 — Named Schema Library

Users can save adopted Schemas as reusable named governance objects.

Example:

```text
My Schemas
├─ 工作專案
├─ 法規文件
├─ 設備資產
├─ 軟體工具
├─ 供應商
└─ AI Agent
```

Named Schema includes:

- stable schema ID;
- display name;
- version;
- description;
- Property definitions;
- required/recommended distinction where supported;
- creation/update metadata;
- optional parent version.

Stored outside the Vault.

## REQ-043 — Schema → Existing Note Reconciliation

Close the v1.1.0 incomplete workflow:

```text
Schema Designer
→ Adopt Schema
→ Apply to Existing Note
→ Note Workspace
→ Select Note
→ Schema context currently does not materialize into editor
```

Required v1.2 flow:

```text
Named / Current Schema
        ↓
Apply to Existing Note
        ↓
Select Note
        ↓
Schema / Note Reconciliation
```

Reconciliation states:

```text
✓ Existing & Matches
＋ Missing from Note
⚠ Existing but Conflicts with Schema
• Existing Note Property outside Schema
```

Existing unrelated Note Properties are preserved by default.

Final outcome:

```text
Reconciliation
↓
Semantic Diff
↓
Validated Frontmatter Preview
↓
Copy
```

No Vault write.

## REQ-044 — Scope → Expected Schema Assignment

A Scope may be associated with an Expected / Desired Named Schema.

```text
Projects/    → 工作專案 v2
Equipment/   → 設備資產 v1
Regulations/ → 法規文件 v3
```

This is governance metadata, not an automatic mutation rule.

No default assignments.

## REQ-045 — Desired vs Actual Schema Drift

When an Expected Schema exists, Property Health can compare Desired vs Actual.

Example:

```text
Scope: Projects/
Expected Schema: 工作專案 v2
Notes: 132

Compliant               103
Missing status           12
Missing owner             8
Unexpected Property      17
Type conflict             4
Value drift               6
```

At minimum detect:

- missing expected Property;
- type mismatch;
- governed value drift;
- unmanaged Property;
- missing required relationship;
- schema version mismatch where relevant.

Explainable only. No automatic correction.

## REQ-046 — External AI Proposal → Schema Candidate Workflow

v1.1 validates Proposal JSON but ends in raw JSON.

v1.2 must provide:

```text
Paste / Open Proposal JSON
↓
Contract Validation
↓
Compare Current Scope
↓
Compare Whole Vault
↓
Compare Property Glossary
↓
Compare Named Schema Library
↓
Human-readable Proposal Review
↓
Accept / Edit / Reject
```

Proposal result states should include:

```text
Compatible Existing Property
New Property
Potential Duplicate / Alias
Type Conflict
Value Vocabulary Conflict
Ambiguous Proposal
Invalid Contract
```

Primary actions:

```text
[Reject Proposal]
[Edit Candidate]
[Accept as Named Schema]
```

Optional:

```text
[Reconcile with Existing Note]
```

Raw JSON remains Advanced / Evidence.

## REQ-047 — Obsidian Property Advisor Skill

v1.2 includes an optional companion AI Skill.

The core application must not depend on the Skill.

### Trigger situations

The Skill should activate when an AI is asked to:

- turn a conversation into an Obsidian Note;
- save a report/research result to Obsidian;
- convert an attachment into Markdown for Obsidian;
- prepare a meeting/project/regulation/equipment/software/research Note;
- recommend Properties for long-term Obsidian storage.

### Skill goal

Before suggesting Properties:

```text
What is this content?
What will the user do with it later?
How does the user want to find, filter, group, relate,
review, maintain, or track it?
```

If management intent is unclear, ask concise questions about management purpose.

Good:

> 這份設備資料主要作為技術參考，還是也希望追蹤供應商、設備位置、採購與維護狀態？

Bad:

> 你想要 Text 還是 List？

### Property principle

Only propose a Property if it supports:

- filter;
- sort;
- group;
- relation;
- validation;
- workflow/status;
- lifecycle/review;
- materially reducing future ambiguity.

Otherwise leave the information in prose.

### Skill outputs

Depending on user intent:

1. Markdown Note only;
2. Property Proposal only;
3. Markdown Note + Property Proposal;
4. clarification questions first.

Proposal output must conform to the current Proposal Contract.

The Skill never directly modifies the Vault.

## REQ-048 — Health Finding → Note Drilldown

Required flow:

```text
Health Finding
↓
Affected Notes
↓
[Inspect in Note Workspace]
↓
Workspace opens exact Note
↓
Finding context survives navigation
↓
Relevant issue is highlighted
```

Context should include:

```text
finding_id
property_key(s)
finding_type
note_path
expected_schema_id if available
```

## REQ-049 — Schema Versioning & Migration Planning

Named Schemas support explicit versions:

```text
工作專案 v1
→ 工作專案 v2
```

Schema comparison identifies:

- Added Properties
- Removed Properties
- Changed Types
- Changed Value Vocabularies
- Changed Requirements
- Changed Relationship Expectations

Migration Planner evaluates selected Scope and outputs a plan only.

No Apply.

## REQ-050 — Governance Profile Import / Export

Once v1.2 stores:

- user glossary;
- Named Schemas;
- versions;
- Scope assignments;
- Saved Relationship Checks;
- governance preferences;

the user must be able to back them up and move them.

Example format:

```json
{
  "format": "property-studio-governance-profile",
  "version": "1.0",
  "glossary": {},
  "schemas": {},
  "scope_profiles": {},
  "saved_relationship_checks": []
}
```

Required actions:

```text
Export
Import
Validate
Preview Changes
Confirm
```

Malformed import fails closed.

No silent overwrite.

## REQ-051 — App-local Governance Persistence

Governance state persists across sessions outside the selected Vault.

Separate:

```text
Vault Content
Governance/App State
Temporary Session State
Export Artifacts
```

Storage must be deterministic, versioned, backup-capable, and never inside a selected Vault by default.

## REQ-052 — Backward Compatibility & Fail-Closed Upgrade

v1.2 reads v1.1-compatible state/contracts where applicable.

If safe migration is impossible:

```text
Do not silently coerce.
Do not discard.
Fail closed.
Explain.
Offer export/recovery guidance where possible.
```

---

# 5. Scope Priority

## P0 — Must Ship

1. Workflow Closure Contract
2. User-editable Property Glossary
3. Named Schema Library
4. Schema → Existing Note Reconciliation
5. Scope → Expected Schema Assignment
6. Desired vs Actual Schema Drift
7. Health → Note Drilldown
8. External AI Proposal → Schema Candidate Workflow
9. Optional Obsidian Property Advisor Skill
10. Persistent app-local governance state

## P1 — Should Ship

11. Schema Versioning
12. Schema Migration Planning
13. Governance Profile Import / Export

A v1.2.0 release cannot PASS if any P0 item is incomplete.

P1 must be explicitly implemented or human-approved deferred. No silent omission.

---

# 6. Explicit Non-Goals

Do not introduce:

- automatic Vault writes;
- Apply Migration;
- automatic Note creation in Vault;
- automatic Note rename/move/delete;
- Markdown body rewriting;
- Body Wikilink rewriting;
- AI auto-acceptance;
- mandatory LLM/API;
- cloud/SaaS account;
- multi-user sync;
- vector DB / RAG subsystem;
- graph database;
- Obsidian plugin rewrite;
- forced ontology;
- automatic Folder organization.

---

# 7. Architecture

```text
                  ┌─────────────────────┐
                  │ Built-in Glossary   │
                  └─────────┬───────────┘
                            │
                  ┌─────────▼───────────┐
                  │ User Glossary       │
                  │ Overrides           │
                  └─────────┬───────────┘
                            │
                            ▼
                   Property Vocabulary
                            │
                            ▼
                  ┌─────────────────────┐
                  │ Named Schema Library│
                  └─────────┬───────────┘
                            │
           ┌────────────────┼─────────────────┐
           │                │                 │
           ▼                ▼                 ▼
 Existing Note       Scope Assignment     AI Proposal
 Reconciliation      Expected Schema      Candidate
           │                │                 │
           │                ▼                 │
           │         Desired vs Actual        │
           │                │                 │
           │               Drift              │
           │                │                 │
           └────────────────┼─────────────────┘
                            ▼
                    Migration Planner
                            │
                            ▼
                       Human Plan

                  NEVER WRITE THE VAULT
```

---

# 8. AI Advisory Architecture

```text
Conversation / Attachment / Report
                ↓
       AI Property Advisor Skill
                ↓
      Understand Content Meaning
                ↓
     Understand Management Purpose
                ↓
      Intent sufficiently clear?
          ↙               ↘
        YES                NO
         │                  │
         │          Ask concise human
         │          management question
         │                  │
         └──────────┬───────┘
                    ↓
           Property Recommendation
                    ↓
       Markdown Note and/or Proposal
                    ↓
          Property Studio Validator
                    ↓
      Compare against real governance state
                    ↓
              Human Review
                    ↓
           Accept / Edit / Reject
```

The Skill does not require direct Vault access.

---

# 9. Proposal Contract Direction

Preserve compatibility with current v1.1 concept:

```json
{
  "proposal_version": "1.0",
  "schema_name": "equipment",
  "description": "...",
  "generated_by": "...",
  "properties": []
}
```

If new fields are required, increment the Proposal Contract explicitly.

Potential optional fields:

```text
management_purpose
source_context
target_note_kind
proposal_notes
schema_target
provenance
```

UI placeholder, docs, fixtures, tests, and Skill must use one authoritative contract.

---

# 10. v1.1.0 Workflow Closure Audit

This becomes the v1.2 baseline.

## Global / Navigation

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| zh-Hant / EN | Locale switches and persists | PASS | Regression-lock |
| Light / Dark | Theme switches and persists | PASS | Regression-lock |
| Sidebar navigation | Intended module opens | PASS | Navigation closure |
| Overview → Vault | Vault setup opens | PASS | Regression-lock |
| Overview Quick Actions | Intended module opens | PASS | Regression-lock |

## Vault / Scope

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Scan Vault | Inventory + baseline | PASS | Regression-lock |
| Verify untouched | SHA manifest comparison | PASS | Regression-lock |
| Apply Scope | Active Scope changes | PASS | Regression-lock |
| Reset Whole Vault | Entire Vault restored | PASS | Regression-lock |

## Note Workspace

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Search | Candidate Notes | PASS | Regression-lock |
| Folder Tree | Whole-Vault hierarchy | PASS | Regression-lock |
| Expand / Collapse All | Tree state changes | PASS | Regression-lock |
| Select Note | Existing Properties load | PASS | Regression-lock |
| Add Property | Editor row added | PASS | Regression-lock |
| Remove Property | Explicit removal in Diff | PASS | Regression-lock |
| Property ⓘ | Glossary drawer | PASS | User Glossary-aware |
| Copy Frontmatter | Valid clipboard artifact | PASS | Regression-lock |

## Discover

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Property Detail | Inventory drawer | PASS | Regression-lock |
| Property ⓘ | Glossary help | PASS | User Glossary-aware |
| Export Discovery | External report | PASS | Regression-lock |

## Schema Designer

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Generate Schema | Deterministic recommendation | PASS | Save to library |
| Retain / Exclude | Controls adopted Schema | PASS | Regression-lock |
| Property ⓘ | Help | PASS | User Glossary-aware |
| Adopt Schema | Session `currentSchema` | PASS, session-only | Named Schema |
| Apply to Existing Note | Navigates but does not reconcile Schema into selected Note | **HOLD** | **REQ-043** |
| New Frontmatter | Adopted Schema drives form | PASS | Named Schema support |

## New Frontmatter

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Go to Schema Design | Useful next action | PASS | Regression-lock |
| Copy Full Frontmatter | Clipboard artifact | PASS | Named Schema support |
| Copy Properties YAML | Clipboard artifact | PASS | Named Schema support |

## Relationships

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Property Links | Property mode | PASS | Regression-lock |
| Body Wikilinks | Body read-only mode | PASS | Regression-lock |
| Analyze | Four-state result | PASS | Regression-lock |
| Save Check | User check saved | PASS | Governance persistence |
| Run Check | Executes saved contract | PASS | Governance persistence |
| Delete Check | Removes check | PASS | Governance persistence |

## Property Health

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Export Health | External report | PASS | Regression-lock |
| Property ⓘ | Help | PASS | User Glossary-aware |
| Finding → affected Note | Text only; no real one-click drilldown | **HOLD** | **REQ-048** |

## Refactor

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Rename | Human-readable plan | PASS | Migration integration |
| Merge | Human-readable plan | PASS | Migration integration |
| Normalize | Controlled mapping plan | PASS | Migration integration |
| Convert Type | Human-readable plan | PASS | Migration integration |
| Raw JSON | Evidence view | PASS | Keep secondary |

Refactor is planning-only; no Apply button is required for closure.

## AI Proposal

| CTA | v1.1 Result | Status | v1.2 |
|---|---|---|---|
| Validate & Compare | Backend works, UI ends in raw JSON | **HOLD** | **REQ-046** |
| Open Proposal File | Wording implies file flow; workflow incomplete | **HOLD** | Implement or remove claim |
| Accept Proposal | Not implemented | **HOLD** | Accept to Named Schema |
| Edit Candidate | Not implemented | **HOLD** | Candidate editor |
| Reject Proposal | Not implemented | **HOLD** | Explicit terminal action |
| Proposal Contract example | Must match actual authoritative contract | **HOLD** | Single contract source |

---

# 11. Workflow Closure Matrix Format

Maintain a governed matrix with columns:

```text
CTA ID
Module
Starting State
User Intent
Action
State Transferred
Backend/Core Operation
Visible Result
Next Action or Terminal Artifact
Failure Path
Automated Test
Human Verification
Formal Status
```

Example:

```text
CTA-DESIGN-APPLY-EXISTING

Start:
Named Schema "Project v2" selected

Intent:
Apply the Schema to an existing Note without modifying the Vault.

Action:
Apply to Existing Note

State Transfer:
schema_id survives navigation

Selection:
Projects/Dayton.md

Result:
✓ matching Properties
＋ missing Schema Properties
⚠ conflicts
• unrelated existing Properties preserved

Terminal:
Validated YAML Preview + Copy
```

---

# 12. Detailed Workflow — Schema → Existing Note

```text
Schema Library / Designer
↓
Select Schema
↓
Apply to Existing Note
↓
Search / Folder Tree
↓
Select Note
↓
Reconciliation Workspace
```

Required sections:

### A. Governed Schema Properties

```text
✓ Exists and matches
＋ Missing
⚠ Conflict
```

### B. Existing Note Properties outside Schema

Preserved by default.

### C. Semantic Diff

```text
Added
Changed
Explicitly Removed
Unchanged
```

### D. Preview

Validated Frontmatter + Copy.

---

# 13. Detailed Workflow — Health → Note

```text
Property Health
↓
Finding
↓
Affected Notes
↓
Inspect Note
↓
Workspace
```

Workspace must show why the user arrived:

```text
Opened from Property Health

Finding:
Missing required Property

Expected Schema:
工作專案 v2

Property:
owner
```

---

# 14. Detailed Workflow — AI Proposal

```text
Paste JSON / Open JSON File
↓
Contract Validate
↓
Proposal Review
```

Per Property show:

- proposed key / display label;
- reason;
- confidence;
- proposed storage type;
- UI control;
- allowed values;
- Current Scope usage;
- Whole Vault usage;
- Glossary entry;
- existing Schema usage;
- compatibility state;
- warnings.

Actions:

```text
Reject
Edit Candidate
Accept as Named Schema
```

Optional:

```text
Reconcile with Existing Note
```

Raw JSON under Advanced / Evidence.

---

# 15. Detailed Workflow — AI Property Advisor Skill

## Purpose

Help an AI produce Obsidian-ready long-term knowledge artifacts with sensible Properties.

Not merely a Schema generator.

## Example triggers

> 把剛才討論整理成一篇 Obsidian 筆記。

> 這份 PDF 幫我轉成 Markdown，我要放 Obsidian 留存。

> 把這份設備報告整理成知識庫筆記。

> 幫我整理這次 AI Agent 測試結果，準備存到 Obsidian。

## Clarification

Ask only when missing information materially affects governance.

Equipment example:

> 這份資料主要作為技術參考，還是也希望追蹤供應商、設備位置、採購與維護狀態？

Regulation example:

> 這份法規主要作為參考保存，還是需要追蹤適用地區、版本、有效日期與合規狀態？

Software example:

> 這篇筆記主要是軟體工具資料庫，還是也希望追蹤測試狀態、安裝裝置與是否持續使用？

Avoid YAML-centric questions unless genuinely necessary.

---

# 16. Persistence Boundary

```text
Selected Vault
READ ONLY
│
├─ Markdown Notes
└─ .obsidian/
        ▲
        │ NEVER WRITE
        │

Property Studio App State
OUTSIDE VAULT
│
├─ User Glossary
├─ Named Schemas
├─ Schema Versions
├─ Scope Assignments
├─ Saved Relationship Checks
└─ Preferences

Governance Profile Export
OUTSIDE VAULT

Reports / Plans
OUTSIDE VAULT
```

---

# 17. Suggested Milestones

Continue after v1.1 M014.

## M015 — v1.2 Governance Transition & Architecture Freeze

- adopt this Spec;
- archive v1.1 Roadmap;
- update four governance files;
- freeze persistence architecture;
- freeze Workflow Closure Matrix;
- freeze Proposal Contract compatibility strategy.

## M016 — Workflow Closure Foundation & State Transfer

- reusable cross-module state transfer;
- CTA closure test framework;
- Schema context survives navigation;
- Health finding context survives navigation;
- Proposal candidate state model.

## M017 — Personal Glossary & Named Schema Library

- user glossary;
- Named Schema CRUD;
- persistence;
- bilingual integration.

## M018 — Existing Note Reconciliation & Health Drilldown

- REQ-043;
- REQ-048.

## M019 — Scope Governance & Schema Drift

- Scope → Expected Schema;
- Desired vs Actual;
- explainable drift.

## M020 — External AI Proposal Workflow & Companion Skill

- Proposal Review;
- Accept/Edit/Reject;
- JSON file flow;
- contract alignment;
- Obsidian Property Advisor Skill.

## M021 — Schema Versioning, Migration Planning & Governance Profile

- schema versions;
- migration planning;
- profile export/import;
- fail-closed migration/import.

## M022 — Full Workflow Closure, Human Acceptance & Release Gate

- complete CTA matrix;
- regressions;
- human walkthrough;
- Vault read-only;
- release closure.

---

# 18. Testing Strategy

Preserve the complete v1.1 regression suite.

Recommended new families:

```text
V12-WFC-*    Workflow Closure
V12-GLO-*    User Glossary
V12-SCH-*    Named Schema
V12-REC-*    Reconciliation
V12-SCP-*    Scope Assignment
V12-DRIFT-*  Desired vs Actual
V12-HLT-*    Health Drilldown
V12-AIP-*    AI Proposal
V12-SKL-*    Skill fixtures/contracts
V12-MIG-*    Schema Migration
V12-PROF-*   Governance Profile
V12-RO-*     Read-only
V12-I18N-*   zh-Hant / English
```

Required end-to-end contracts:

1. Design → Adopt → Existing Note → Reconciliation → Copy.
2. Design → Adopt → New Frontmatter → Copy.
3. Health Finding → Exact Note Workspace + finding context.
4. Proposal → Validate → Review → Accept as Named Schema.
5. Proposal → Edit.
6. Proposal → Reject.
7. Proposal File → same deterministic result as pasted JSON.
8. Named Schema → Scope Assignment → Drift.
9. Schema v1 → v2 → Migration Plan.
10. Governance Profile export → import → semantic round-trip.
11. No workflow writes selected Vault.
12. Ambiguous/malformed state fails closed.

A test that only verifies `onclick != null` is insufficient for primary workflow closure.

---

# 19. Human Acceptance

Minimum human walkthrough:

```text
1. Create/edit user Glossary entry.
2. Save Named Schema.
3. Apply Schema to Existing Note.
4. Verify reconciliation states.
5. Copy valid Frontmatter.
6. Assign Schema to Scope.
7. View Drift.
8. Drill Health finding to exact Note.
9. Import AI Proposal.
10. Review Proposal in human-readable UI.
11. Accept Proposal into Schema Library.
12. Export Governance Profile.
13. Import Profile into clean app state.
14. Confirm Vault byte-for-byte unchanged.
```

---

# 20. Definition of Done

v1.2.0 may PASS only when:

```text
All P0 requirements implemented
+
All P0 workflows closed
+
No primary CTA dead end
+
Required automated verification PASS
+
Human workflow acceptance PASS
+
Vault byte-for-byte unchanged
+
Governance Profile round-trip PASS
+
AI Proposal contract / UI / Skill consistent
+
Four-file consistency PASS
+
Evidence non-contradictory
+
Release artifacts verified
=
v1.2.0 PASS
```

---

# 21. Governance Transition

Before implementation:

1. Preserve v1.1.0 release and tag.
2. Copy current root `ROADMAP.md` exactly to:

```text
docs/archive/ROADMAP_v1.1.0.md
```

3. Record SHA-256.
4. Replace root `ROADMAP.md` with active v1.2 Roadmap.
5. Update `PROJECT.md` with REQ-040 through REQ-052.
6. Update `AGENTS.md` only with durable v1.2 rules:
   - No Dead-End CTA;
   - explicit cross-module state transfer;
   - governance state outside Vault;
   - AI advisory boundary;
   - canonical key stability;
   - Workflow Closure evidence.
7. Update `HANDOFF.md` last:
   - v1.1.0 release closed;
   - v1.2 active;
   - M015 current;
   - Spec path/hash;
   - archived Roadmap path/hash;
   - branch and exact commit;
   - next action.

---

# 22. Recommended Repository Additions

```text
docs/specs/
└─ Obsidian_Property_Studio_v1.2.0_Spec.md

docs/archive/
└─ ROADMAP_v1.1.0.md

skills/
└─ obsidian-property-advisor/
   ├─ SKILL.md
   ├─ references/
   │  ├─ proposal-contract.md
   │  ├─ property-design-principles.md
   │  └─ examples.md
   └─ examples/
      ├─ project.json
      ├─ equipment.json
      └─ regulation.json
```

`skills/` is implemented during M020, not during governance transition.

---

# 23. Skill Acceptance

The Skill is complete only when:

```text
Trigger guidance exists
+
Clarification rules exist
+
Property recommendation principles exist
+
Valid Proposal output exists
+
Fixtures validate against Property Studio
+
No claim of Vault write capability
+
Note-only / Proposal-only / Note+Proposal supported
+
Human can understand why each Property was suggested
=
Skill PASS
```

---

# 24. Final Product Boundary

v1.2.0 is not an “AI Obsidian writer”.

It is:

> **A deterministic, read-only governance environment where users can define their own Property vocabulary, define desired Schemas, compare desired and actual Vault structure, plan migrations, reconcile existing Notes, and optionally receive AI-generated advisory proposals subject to deterministic validation and human approval.**
