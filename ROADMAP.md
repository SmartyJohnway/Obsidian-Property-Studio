# Roadmap

> Project: `Obsidian Property Studio`  
> Target Release: `v1.0.0`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Roadmap Type: `Formal Mainline Integration Roadmap`  
> Recipient: `Agent B`  
> Read-only Donors: `Agent C`, `Agent A`, `Agent D`

---

## Current State

Project State: `ACTIVE`  
Current Milestone: `M001 — Formal Integration Baseline Freeze`  
Current Milestone Status: `PLANNED`  
Current Task: `M001-T01 — Verify formal root and donor snapshot identities`  
Last Verified Gate: `Round 2 independent black-box selection completed externally`  
Current Blocker: `None known; local donor paths and archive hashes must be verified before porting.`  
Next Action: `Initialize the clean formal repository, freeze donor identities, then materialize Agent B selectively without importing donor governance/Git/evidence.`  
Last Updated: `2026-08-31`

---

# 1. Integration Authority

This ROADMAP is the only authoritative execution plan for formal integration.

The Arena candidates are no longer parallel implementations.

```text
B = MAINLINE / RECIPIENT
C = READ-ONLY DONOR
A = READ-ONLY DONOR
D = READ-ONLY DONOR
```

Do not reopen the Arena winner decision unless new reproducible evidence demonstrates a material error in the accepted baseline.

---

# 2. Expected Local Layout

Human-selected formal root:

```text
D:\Antigravity-Workspace\Obsidian-Property-Studio\
│
├─ Obsidian-Property-Studio-v1.0.0\        ← FORMAL REPOSITORY
│  ├─ PROJECT.md
│  ├─ ROADMAP.md
│  ├─ HANDOFF.md
│  └─ AGENTS.md
│
├─ AgentA_workspace-01a05750-5684-7ca8-85d9-94758fa56fb8\
├─ AgentB_workspace-01a05750-6b01-702f-8d9e-43d693870e40\
├─ AgentC_workspace-01a05750-6ec1-7d23-9b68-927acecae272\
├─ AgentD_workspace-01a05750-d3d8-7d86-af4a-0f5b76b3fc57\
│
└─ corresponding Arena ZIP snapshots
```

The exact local names must be verified rather than assumed.

Candidate roots are external donor sources, not nested project authorities.

---

# 3. Frozen Donor Archive Identities

Expected SHA-256 from the Arena submissions supplied for independent audit:

```text
Agent A ZIP
6c5cfacc8b33531e29aefd1bd258488f249961f5719ee6ae6e4c3c4a3b00758c

Agent B ZIP
c167ffeedb88ee7e42306c9e18610a089db6e8d5868edf3a98c40c40f5d14c9f

Agent C ZIP
b23abf3bdce30151dd302effe1e7633cf37812b5ba155b0a4f195545a907d53d

Agent D ZIP
5404306a1155a5b31ae3613500733a5fc402b41e05b50738cd5daea5bca11939
```

If the local candidate ZIP differs:

```text
HOLD
```

until provenance is reconciled.

Do not silently integrate a different candidate snapshot.

---

# 4. Accepted Round 2 Integration Findings

## B — Mainline strengths

Use as recipient baseline:

- strong parsing/inventory separation;
- conservative duplicate/malformed handling;
- strong refactor conflict handling;
- conservative Relationship Inbox;
- good beginner design workflow;
- strong export/read-back behavior;
- no major hidden core defect identified.

Known integration improvement:

### R2-B-01 — Ambiguous Fill should become fully fail-closed

B currently keeps ambiguity visible via warning but can still serialize generic:

```yaml
company: '[[ACME]]'
```

when multiple same-name targets exist.

Formal v1.0.0 adopts the stronger C behavior:

> do not emit the confirmed relationship value until the user selects an explicit target.

---

## C — Donor strengths / limitations

Harvest candidates:

- `app/core/fill.py`
  - ambiguous target resolution;
  - fail-closed Fill semantics.
- `app/core/relationship.py`
  - entity-target resolution;
  - canonical target semantics.
- selected beginner-facing Traditional Chinese explanations / UX patterns.
- tests proving ambiguous note identity behavior.

Do not blindly port:

- goal matching logic that missed equipment/vendor in the common equipment/procurement prompt;
- normalize manual-review count semantics without regression review.

Round 2 limitations to guard:

### R2-C-01
Beginner design prompt missed `equipment/vendor`.

### R2-C-02
Duplicate-key normalize manual-review count was per duplicate occurrence rather than per affected note.

---

## A — Donor strengths / limitations

Harvest candidates:

- `app/core/refactor.py`
  - `_ambiguity_warnings`;
  - duplicate/malformed propagation into manual review;
  - detailed migration planning.
- `app/core/integrity.py`
  - useful manifest/read-only verification patterns if better than recipient.
- related refactor tests.

Do not port A relationship confirmation semantics wholesale.

Round 2 defects to guard:

### R2-A-01
Malformed note contributed to ordinary `notes_without_properties` count.

### R2-A-02
Ambiguous `ACME` Fill emitted `[[ACME]]` with no ambiguity warning.

### R2-A-03
Relationship drift could be marked `confirmed: true` while multiple targets existed.

---

## D — Donor strengths / limitations

Harvest candidates:

- `ops/core/export.py`
  - `verify_migration_readback`;
  - `verify_health_readback`;
  - explicit output completeness checks.
- selected Health presentation/explainability patterns.
- user-facing safety/governance wording where useful.

Do **not** port D design/refactor/relationship logic wholesale.

Round 2 defects to guard:

### R2-D-01
Equipment/procurement design prompt incorrectly routed to a Reading recipe.

### R2-D-02
Normalize plan omitted a known duplicate-key note from manual review.

### R2-D-03
Relationship drift `canonical_target` could point to the source equipment note instead of entity note.

### R2-D-04
Ambiguous `ACME` Fill did not surface the actual multi-target ambiguity.

---

# 5. Integration Strategy

Use:

```text
test-first selective port
```

Never:

```text
wholesale repository copy
direct git merge
direct cherry-pick
donor governance inheritance
donor PASS inheritance
```

For each donor capability:

```text
1. write/freeze regression test
2. reproduce recipient baseline behavior
3. inspect donor implementation
4. port minimum necessary code
5. run focused tests
6. run full suite
7. inspect/read-back outputs
8. update evidence
9. continue
```

---

# 6. Formal Status Vocabulary

Milestone:

```text
PLANNED
IN_PROGRESS
HOLD
PASS
SUPERSEDED
```

Result:

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

`DONE`, `COMPLETED`, `READY`, `GREEN`, etc. do not replace `PASS`.

---

# M001 — Formal Integration Baseline Freeze

Status: `PLANNED`

### Objective

Establish a clean formal repository and freeze the exact Arena donor snapshots before touching product code.

### Tasks

- [ ] `M001-T01` Verify formal root path.
- [ ] `M001-T02` Inspect parent directory and resolve exact A/B/C/D donor paths.
- [ ] `M001-T03` Verify all four donor ZIP SHA-256 identities.
- [ ] `M001-T04` Confirm donor extracted directories are treated read-only.
- [ ] `M001-T05` Confirm only formal root four governance files are authoritative.
- [ ] `M001-T06` Initialize new Git repository in formal root if absent.
- [ ] `M001-T07` Record initial Git branch/HEAD/status.
- [ ] `M001-T08` Commit or otherwise freeze four-file governance baseline.
- [ ] `M001-T09` Establish integration evidence directory.
- [ ] `M001-T10` Update AGENTS Part B with verified runtime/Git facts only.
- [ ] `M001-T11` Update ROADMAP truthfully.
- [ ] `M001-T12` Update HANDOFF last.

### Acceptance Criteria

- [ ] `M001-AC01` Formal repository is a distinct Git lineage.
- [ ] `M001-AC02` No candidate `.git` has been copied into formal root.
- [ ] `M001-AC03` A/B/C/D archive identities match expected hashes or discrepancy is HOLD.
- [ ] `M001-AC04` Donor directories are unchanged.
- [ ] `M001-AC05` Formal root four files are the only governance authorities.
- [ ] `M001-AC06` Initial Git/evidence state is recorded.

### Verification / Evidence

Expected:

- donor hash record;
- formal Git state;
- donor immutability manifest/check;
- authority-boundary check.

### Result

`NOT YET VERIFIED`

---

# M002 — Materialize Agent B as Formal Recipient

Status: `PLANNED`

### Objective

Create the starting formal implementation from Agent B without importing B's historical governance/Git/evidence state.

### Allowed initial materialization candidates

From B, selectively evaluate/copy:

```text
app/
tests/
scripts/
requirements.txt
requirements-dev.txt
pytest.ini
run_windows.bat
run.sh
README.md
docs/
```

### Explicit exclusions

Do not import as formal state:

```text
.git/
PROJECT.md
ROADMAP.md
HANDOFF.md
AGENTS.md
evidence/
uploads/
__pycache__/
.pytest_cache/
developer-local caches
```

B docs/README may be copied only as implementation content and must later be reconciled with formal behavior.

### Tasks

- [ ] `M002-T01` Record B source tree baseline.
- [ ] `M002-T02` Materialize allowed recipient files.
- [ ] `M002-T03` Re-establish project-local Python environment.
- [ ] `M002-T04` Verify install command.
- [ ] `M002-T05` Verify run command.
- [ ] `M002-T06` Run B baseline automated suite in formal repo.
- [ ] `M002-T07` Verify local UI launch.
- [ ] `M002-T08` Verify selected Vault remains read-only.
- [ ] `M002-T09` Record baseline formal evidence.
- [ ] `M002-T10` Remove/ignore stale candidate-specific path assumptions.

### Acceptance Criteria

- [ ] `M002-AC01` Formal app launches.
- [ ] `M002-AC02` Formal baseline tests execute with actual results recorded.
- [ ] `M002-AC03` Core requires no network/AI.
- [ ] `M002-AC04` Formal root governance remains unchanged except truthful state updates.
- [ ] `M002-AC05` Donor B directory remains unchanged.
- [ ] `M002-AC06` No B evidence is misrepresented as formal evidence.

### Result

`NOT YET VERIFIED`

---

# M003 — Freeze Integration Regression Oracle

Status: `PLANNED`

### Objective

Convert Round 2 findings into formal tests before donor implementation is ported.

### Required hidden-regression contracts

#### `INT-R2-001` — Malformed is not ordinary no-properties

Malformed YAML must be separately counted/reported and must not inflate ordinary property-free note counts.

#### `INT-R2-002` — Duplicate-key ambiguity survives Refactor

A note with duplicate `status` keys must appear in manual review/excluded ambiguity for Normalize.

#### `INT-R2-003` — Ambiguous Fill fails closed

Given:

```text
Companies/ACME.md
Vendors/ACME.md
company = ACME
```

final serialization must not emit a confirmed generic `[[ACME]]`.

User must select explicit target/path.

#### `INT-R2-004` — Relationship canonical target is entity

For:

```text
vendor: SEW
```

with:

```text
Companies/SEW.md
```

canonical target must be `Companies/SEW.md`, not the source note containing the value.

#### `INT-R2-005` — No false confirmed ambiguity

A relationship finding with multiple possible targets cannot be `confirmed: true`.

#### `INT-R2-006` — Equipment goal does not route to Reading

Prompt:

```text
I want to manage equipment by project, vendor, procurement status, and review date.
```

must not choose a reading/book schema as the primary result.

#### `INT-R2-007` — Normalize counts affected notes coherently

Manual-review summary must distinguish:

- affected notes;
- duplicated occurrences/values;

and must not conflate them.

#### `INT-R2-008` — Output completeness

Multiple findings must survive JSON/Markdown/read-back export.

#### `INT-R2-009` — Vault read-only

Representative integrated workflows cause:

```text
0 created
0 modified
0 renamed
0 deleted
```

#### `INT-R2-010` — Deterministic scan

Unchanged Vault + unchanged config yields semantically identical canonical output.

### Tasks

- [ ] `M003-T01` Implement fixtures for INT-R2-001…010.
- [ ] `M003-T02` Run tests against B baseline before donor port.
- [ ] `M003-T03` Record which tests already PASS and which expose accepted integration gap.
- [ ] `M003-T04` Freeze test intent before modifying production behavior.

### Acceptance Criteria

- [ ] `M003-AC01` All ten regression contracts exist as executable tests.
- [ ] `M003-AC02` Expected B baseline gap(s) are recorded honestly.
- [ ] `M003-AC03` Tests do not encode donor implementation details.
- [ ] `M003-AC04` No production fix is smuggled in before baseline evidence.

### Result

`NOT YET VERIFIED`

---

# M004 — Harvest C Safety & Relationship Semantics

Status: `PLANNED`

### Objective

Port only the proven C behaviors that strengthen B's ambiguity and relationship safety.

### Primary donor inspection targets

```text
C/app/core/fill.py
  resolve_link_targets
  build_property_values
  preview

C/app/core/relationship.py
  resolve_note_target
  relationship_inbox
  relink_proposals

C/tests/
  fill / relationship ambiguity cases
```

### Tasks

- [ ] `M004-T01` Inspect C implementation without changing donor.
- [ ] `M004-T02` Port minimal fail-closed ambiguous Fill behavior.
- [ ] `M004-T03` Ensure explicit path choice serializes correctly.
- [ ] `M004-T04` Verify relationship canonical target semantics.
- [ ] `M004-T05` Prevent ambiguous target from becoming confirmed relationship.
- [ ] `M004-T06` Port/select Traditional Chinese beginner wording only where it improves clarity without changing scope.
- [ ] `M004-T07` Run INT-R2-003/004/005.
- [ ] `M004-T08` Run full suite.
- [ ] `M004-T09` Verify no regression in B's conservative relationship behavior.

### Acceptance Criteria

- [ ] `M004-AC01` INT-R2-003 PASS.
- [ ] `M004-AC02` INT-R2-004 PASS.
- [ ] `M004-AC03` INT-R2-005 PASS.
- [ ] `M004-AC04` No C goal-routing weakness is imported.
- [ ] `M004-AC05` Donor C remains unchanged.
- [ ] `M004-AC06` No body/template/plugin scope creep.

### Result

`NOT YET VERIFIED`

---

# M005 — Harvest A Refactor Ambiguity Propagation

Status: `PLANNED`

### Objective

Strengthen recipient Refactor Planner so known malformed/duplicate ambiguity remains visible.

### Primary donor inspection targets

```text
A/app/core/refactor.py
  _ambiguity_warnings
  plan_merge
  plan_normalize_values
  plan_type_conversion

A/app/core/integrity.py

A/tests/test_refactor.py
```

### Tasks

- [ ] `M005-T01` Compare B and A refactor semantics.
- [ ] `M005-T02` Preserve B strengths in excluded/unreadable separation.
- [ ] `M005-T03` Port minimum A ambiguity/manual-review behavior that adds value.
- [ ] `M005-T04` Keep affected-note counts distinct from duplicate occurrence counts.
- [ ] `M005-T05` Verify malformed note does not become ordinary no-property note.
- [ ] `M005-T06` Run INT-R2-001/002/007.
- [ ] `M005-T07` Run full suite.
- [ ] `M005-T08` Read back migration plan outputs.

### Acceptance Criteria

- [ ] `M005-AC01` INT-R2-001 PASS.
- [ ] `M005-AC02` INT-R2-002 PASS.
- [ ] `M005-AC03` INT-R2-007 PASS.
- [ ] `M005-AC04` No A relationship-confirmation defect imported.
- [ ] `M005-AC05` Merge conflicts remain fail-closed.
- [ ] `M005-AC06` Donor A remains unchanged.

### Result

`NOT YET VERIFIED`

---

# M006 — Harvest D Export Read-back & Health Presentation

Status: `PLANNED`

### Objective

Adopt D's proven output-verification/presentation patterns without importing D's faulty design/refactor/relationship semantics.

### Primary donor inspection targets

```text
D/ops/core/export.py
  verify_migration_readback
  verify_health_readback

D/ops/core/health.py
  presentation / explainability patterns only

D/docs/user-guide.md
  selected safety wording only
```

### Explicit do-not-port list

Do not copy wholesale:

```text
D/ops/core/design.py
D/ops/core/refactor.py
D/ops/core/relationships.py
```

unless a later focused test proves a specific isolated helper is safe and useful.

### Tasks

- [ ] `M006-T01` Compare B export logic with D read-back verification.
- [ ] `M006-T02` Integrate explicit semantic read-back for migration output.
- [ ] `M006-T03` Integrate explicit semantic read-back for Health output.
- [ ] `M006-T04` Preserve all findings/warnings/ambiguity across export.
- [ ] `M006-T05` Improve Health explainability without changing underlying truth semantics.
- [ ] `M006-T06` Run INT-R2-008.
- [ ] `M006-T07` Run full suite.
- [ ] `M006-T08` Verify D known defects are absent.

### Acceptance Criteria

- [ ] `M006-AC01` INT-R2-008 PASS.
- [ ] `M006-AC02` Important exports have real read-back evidence.
- [ ] `M006-AC03` No D relationship canonical-target defect imported.
- [ ] `M006-AC04` No D duplicate-key Normalize omission imported.
- [ ] `M006-AC05` No D Reading-recipe misrouting imported.
- [ ] `M006-AC06` Donor D remains unchanged.

### Result

`NOT YET VERIFIED`

---

# M007 — Beginner Design & Unified UX Integration

Status: `PLANNED`

### Objective

Make the integrated product coherent for a user who does not know YAML.

### Tasks

- [ ] `M007-T01` Preserve B's goal/use-case-oriented design flow.
- [ ] `M007-T02` Verify equipment/project/vendor/procurement/review-date design prompt.
- [ ] `M007-T03` Reuse existing properties before new near-duplicates.
- [ ] `M007-T04` Ensure Property purpose explanations remain understandable.
- [ ] `M007-T05` Ensure storage type vs UI-control distinction is visible.
- [ ] `M007-T06` Ensure ambiguous link picker requires explicit target.
- [ ] `M007-T07` Improve Traditional Chinese labels/explanations where useful.
- [ ] `M007-T08` Confirm no正文/template authoring was introduced.
- [ ] `M007-T09` Run beginner workflow from empty/new schema through Copy YAML.

### Acceptance Criteria

- [ ] `M007-AC01` INT-R2-006 PASS.
- [ ] `M007-AC02` User can complete core flow without authoring YAML.
- [ ] `M007-AC03` Existing Property reuse remains visible.
- [ ] `M007-AC04` Ambiguous link UI does not serialize prematurely.
- [ ] `M007-AC05` No Reading false-positive for equipment scenario.
- [ ] `M007-AC06` No body/template scope creep.

### Result

`NOT YET VERIFIED`

---

# M008 — Cross-Module Canonical Consistency Gate

Status: `PLANNED`

### Objective

Prove parsing/ambiguity/provenance semantics remain consistent through all product surfaces.

### Required path

```text
Scan
→ Inventory
→ Design
→ Fill
→ Refactor
→ Relationship
→ Health
→ Export
```

### Tasks

- [ ] `M008-T01` Trace malformed note across modules.
- [ ] `M008-T02` Trace duplicate-key note across modules.
- [ ] `M008-T03` Trace ambiguous ACME identity across modules.
- [ ] `M008-T04` Trace broken relationship across modules.
- [ ] `M008-T05` Verify canonical target provenance.
- [ ] `M008-T06` Verify no module silently upgrades uncertainty.
- [ ] `M008-T07` Verify report/export preserves ambiguity.
- [ ] `M008-T08` Verify direct API vs exported artifact semantic parity.

### Acceptance Criteria

- [ ] `M008-AC01` Known ambiguity never disappears silently.
- [ ] `M008-AC02` No `confirmed` state has multiple unresolved targets.
- [ ] `M008-AC03` Counts have documented semantics.
- [ ] `M008-AC04` Export parity PASS.
- [ ] `M008-AC05` Health drill-down agrees with canonical findings.

### Result

`NOT YET VERIFIED`

---

# M009 — Full Formal Regression, Read-only, Determinism & Performance

Status: `PLANNED`

### Objective

Rerun formal evidence in the integrated repository.

### Tasks

- [ ] `M009-T01` Run full automated test suite.
- [ ] `M009-T02` Run all original OPS acceptance cases retained by formal PROJECT.
- [ ] `M009-T03` Run INT-R2-001…010.
- [ ] `M009-T04` Run pre/post Vault SHA-256/manifest verification.
- [ ] `M009-T05` Run deterministic repeat-scan.
- [ ] `M009-T06` Run output read-back verification.
- [ ] `M009-T07` Run common ≥5,000-note benchmark.
- [ ] `M009-T08` Verify offline/no-key operation.
- [ ] `M009-T09` Run security/adversarial frontmatter cases.
- [ ] `M009-T10` Record environment and measured results.

### Acceptance Criteria

- [ ] `M009-AC01` Required tests PASS.
- [ ] `M009-AC02` INT-R2-001…010 PASS.
- [ ] `M009-AC03` Vault mutation count = 0 for representative workflows.
- [ ] `M009-AC04` Determinism PASS.
- [ ] `M009-AC05` Output read-back PASS.
- [ ] `M009-AC06` ≥5,000-note benchmark completes and is recorded.
- [ ] `M009-AC07` No invented hard performance threshold.
- [ ] `M009-AC08` No required network/AI.

### Result

`NOT YET VERIFIED`

---

# M010 — Windows Native Product Acceptance

Status: `PLANNED`

### Objective

Close the limitation that Arena candidates were not all natively verified on the user's Windows 11 environment.

### Tasks

- [ ] `M010-T01` Verify clean install on Windows 11.
- [ ] `M010-T02` Verify `run_windows.bat` or accepted launcher.
- [ ] `M010-T03` Open actual GUI/local Web UI.
- [ ] `M010-T04` Select a test Vault with spaces + Traditional Chinese path/value.
- [ ] `M010-T05` Execute Discover.
- [ ] `M010-T06` Execute Design.
- [ ] `M010-T07` Execute Fill + Copy YAML.
- [ ] `M010-T08` Execute ambiguous-note selection flow.
- [ ] `M010-T09` Execute Refactor Planner.
- [ ] `M010-T10` Execute Relationship Inbox.
- [ ] `M010-T11` Execute Health + export/read-back.
- [ ] `M010-T12` Confirm real Vault/test Vault remains unchanged.
- [ ] `M010-T13` Record screenshots/manual inspection where useful.
- [ ] `M010-T14` Record known limitations.

### Acceptance Criteria

- [ ] `M010-AC01` Windows native launch PASS.
- [ ] `M010-AC02` Beginner flow usable without YAML knowledge.
- [ ] `M010-AC03` Traditional Chinese path/value PASS.
- [ ] `M010-AC04` Ambiguous Fill requires explicit choice.
- [ ] `M010-AC05` Vault remains unchanged.
- [ ] `M010-AC06` No P0/P1 UX/safety blocker.

### Result

`NOT YET VERIFIED`

---

# M011 — v1.0.0 Release Closure

Status: `PLANNED`

### Objective

Produce a truthful formal v1.0.0 release from the integrated lineage.

### Tasks

- [ ] `M011-T01` Freeze version `1.0.0`.
- [ ] `M011-T02` Run full tests from clean formal worktree.
- [ ] `M011-T03` Run evidence contradiction gate.
- [ ] `M011-T04` Run four-file consistency gate.
- [ ] `M011-T05` Verify README/docs match actual integrated behavior.
- [ ] `M011-T06` Verify no donor governance/evidence is represented as current authority.
- [ ] `M011-T07` Verify donor directories/snapshots remain unchanged.
- [ ] `M011-T08` Verify final Git status.
- [ ] `M011-T09` Verify release artifact identity.
- [ ] `M011-T10` Distinguish Source Snapshot vs Full Git Backup.
- [ ] `M011-T11` Update ROADMAP final state.
- [ ] `M011-T12` Update HANDOFF last.
- [ ] `M011-T13` Record final release verdict.

### Acceptance Criteria

- [ ] `M011-AC01` PROJECT Global DoD satisfied.
- [ ] `M011-AC02` M009 PASS.
- [ ] `M011-AC03` M010 PASS.
- [ ] `M011-AC04` No unresolved contradictory evidence.
- [ ] `M011-AC05` Formal repository Git state is verified.
- [ ] `M011-AC06` Release artifact read-back/integrity PASS.
- [ ] `M011-AC07` Four-file state mutually consistent.
- [ ] `M011-AC08` No stale initialization residue.
- [ ] `M011-AC09` No candidate `.git`/governance leakage into formal root.

### Verification / Evidence

Final Audit must inspect underlying evidence. It cannot self-certify.

### Result

`NOT YET VERIFIED`

---

# 7. Final Integration Contract

Target architecture of responsibility:

```text
Formal v1.0.0
│
├─ B recipient architecture / stable core
│
├─ C fail-closed ambiguity + relationship semantics
│
├─ A refactor ambiguity/manual-review strength
│
└─ D export read-back + Health presentation strength
```

But implementation must remain coherent.

Do not create obvious "A module / B module / C module / D module" seams in the product.

The final product is one integrated system, with one canonical data model and one set of semantics.

---

# 8. Release Verdict Vocabulary

Formal release result must be one of:

```text
PROPERTY_STUDIO_V1_RELEASE_PASS
PROPERTY_STUDIO_V1_RELEASE_PASS_WITH_LIMITATIONS
PROPERTY_STUDIO_V1_RELEASE_BLOCKED
```

A `PASS_WITH_LIMITATIONS` must state every limitation explicitly and must not conceal a failed required safety contract.

No evidence, no PASS.  
No contradictory evidence, no PASS.
