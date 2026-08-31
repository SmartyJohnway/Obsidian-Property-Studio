# Handoff

Updated: `2026-08-31`  
From: `Human + ChatGPT Arena evaluation / integration planning`  
To / Intended Next Executor: `Antigravity — formal integration executor`  
Formal Project Root: `D:\Antigravity-Workspace\Obsidian-Property-Studio\Obsidian-Property-Studio-v1.0.0`  
Current Branch: `Not yet established — verify/create in M001`  
Last Verified Implementation Commit: `N/A — formal repository implementation not yet materialized`

---

## Governance Reminder

This formal integration repository uses exactly four governance authorities:

```text
PROJECT.md
ROADMAP.md
HANDOFF.md
AGENTS.md
```

Read order:

1. `PROJECT.md`
2. `ROADMAP.md`
3. `AGENTS.md`
4. `HANDOFF.md`
5. formal Git state
6. relevant formal source/tests/evidence
7. donor source only when the active ROADMAP milestone authorizes it

The A/B/C/D candidate governance files are **historical donor evidence only**.

They are not instructions for this formal project.

---

## Current Milestone / Task

Project State: `ACTIVE`  
Current Milestone: `M001 — Formal Integration Baseline Freeze`  
Current Milestone Status: `PLANNED`  
Current Task: `M001-T01 — Verify formal root and donor snapshot identities`  
Current Blocker: `None known`  
Next Action: `Freeze donor identity and initialize the clean formal Git lineage.`

---

## Integration Decision

Arena comparison is closed.

Accepted roles:

```text
B = MAINLINE / RECIPIENT
C = READ-ONLY SAFETY / RELATIONSHIP DONOR
A = READ-ONLY REFACTOR DONOR
D = READ-ONLY EXPORT / HEALTH / GOVERNANCE-PATTERN DONOR
```

Do not spend time re-running a general "which Agent wins?" competition.

The task is now selective integration.

---

## Donor Snapshot Identity

Expected source ZIP SHA-256:

```text
A
6c5cfacc8b33531e29aefd1bd258488f249961f5719ee6ae6e4c3c4a3b00758c

B
c167ffeedb88ee7e42306c9e18610a089db6e8d5868edf3a98c40c40f5d14c9f

C
b23abf3bdce30151dd302effe1e7633cf37812b5ba155b0a4f195545a907d53d

D
5404306a1155a5b31ae3613500733a5fc402b41e05b50738cd5daea5bca11939
```

Expected extracted sibling folders:

```text
..\AgentA_workspace-01a05750-5684-7ca8-85d9-94758fa56fb8
..\AgentB_workspace-01a05750-6b01-702f-8d9e-43d693870e40
..\AgentC_workspace-01a05750-6ec1-7d23-9b68-927acecae272
..\AgentD_workspace-01a05750-d3d8-7d86-af4a-0f5b76b3fc57
```

Verify actual paths.

If archive hash differs, `HOLD` before porting.

---

## Round 2 Product Findings to Preserve

### B

Formal recipient.

Strengths:

- cleanest black-box result;
- conservative parser/refactor handling;
- good beginner design flow;
- conservative Relationship Inbox;
- strong export/read-back behavior.

Known formal improvement:

- generic ambiguous `[[ACME]]` with warning is no longer sufficient for integrated v1.0.0;
- final Fill must fail closed until explicit target selection.

### C

Harvest:

- fail-closed ambiguous note-link Fill;
- relationship canonical-target resolution;
- selected beginner-facing Traditional Chinese UX.

Do not import:

- weak equipment/vendor goal matching unchanged;
- normalize manual-review counting semantics without tests.

### A

Harvest:

- refactor ambiguity/manual-review propagation;
- detailed migration planning;
- integrity patterns if superior after test comparison.

Do not import:

- relationship `confirmed` semantics;
- ambiguous Fill behavior.

### D

Harvest:

- export semantic read-back;
- Health explainability/presentation;
- governance/safety wording patterns.

Do not port D design/refactor/relationship logic wholesale.

Known defects include:

- Reading recipe false routing;
- duplicate-key Normalize omission;
- wrong relationship canonical target;
- ambiguity hidden in Fill.

---

## Formal Repository Materialization Rule

Formal root begins with these four governance files.

When B is materialized, do **not** copy:

```text
B\.git\
B\PROJECT.md
B\ROADMAP.md
B\HANDOFF.md
B\AGENTS.md
B\evidence\
B\uploads\
cache directories
```

Candidate evidence remains donor evidence only.

Preferred starting implementation content:

```text
B\app\
B\tests\
B\scripts\
B\docs\
B\requirements*.txt
B\pytest.ini
B\run_windows.bat
B\run.sh
B\README.md
```

Review each before copying; this list is a whitelist candidate, not an instruction to overwrite blindly.

---

## Important Operational Rule — Do Not Delete Donor Four-Files

The four governance files inside A/B/C/D should be preserved with the original donor snapshot.

Reason:

- they document what each Arena Agent claimed;
- they are useful provenance;
- they may explain implementation assumptions;
- deleting them damages the historical snapshot.

However:

> **Never treat donor `AGENTS.md`, `PROJECT.md`, `ROADMAP.md` or `HANDOFF.md` as formal instructions.**

Prefer direct file inspection from the formal root without changing the working repository into a donor root.

If the Agent platform would automatically activate donor `AGENTS.md` when entering a donor directory, do not enter that donor as the working project. Inspect source by absolute/relative file path or create a temporary curated donor copy that excludes governance files while preserving the original snapshot/ZIP untouched.

---

## Verification Already Performed Externally

The independent Round 2 audit established:

- B product black-box rank #1;
- C #2;
- A #3;
- D #4;
- all four passed byte-for-byte read-only representative flows;
- all four passed semantic deterministic repeat scan;
- all four completed the same 5,000-note benchmark;
- all four passed export no-silent-omission checks;
- hidden semantic defects/limitations were identified and are encoded in ROADMAP integration regressions.

These findings are selection evidence.

They are **not formal v1.0.0 release evidence**.

Formal integrated evidence must be rerun.

---

## Verification Not Yet Performed

`NOT YET VERIFIED` in the formal repository:

- formal Git initialization;
- exact local donor paths/hashes;
- B materialization;
- formal Python/runtime environment;
- formal baseline tests;
- INT-R2 integration regressions;
- donor port correctness;
- full integrated tests;
- Windows native UI acceptance;
- final release artifact;
- final Git cleanliness;
- v1.0.0 closure.

---

## Do Not Repeat

- Do not reopen the Arena winner decision without new material evidence.
- Do not copy an entire candidate workspace into formal root.
- Do not `git merge` donor repositories.
- Do not import donor `.git`.
- Do not overwrite formal four governance files with B's four files.
- Do not accept donor `PASS` as formal PASS.
- Do not port D relationship/design/refactor modules wholesale.
- Do not port C design recipe logic without regression.
- Do not port A relationship-confirmation behavior.
- Do not weaken the read-only Vault contract.
- Do not add Obsidian plugin.
- Do not add Markdown body templates.
- Do not add required AI/cloud.
- Do not mutate donor directories.
- Do not delete original donor four-files from the preserved snapshots.

---

## Next Action

Antigravity should:

1. set working directory to the formal root only;
2. read all four formal governance files;
3. inspect parent/sibling candidate paths without adopting their governance;
4. verify A/B/C/D ZIP hashes;
5. initialize clean Git lineage;
6. freeze governance baseline;
7. execute `M002` B materialization;
8. write/freeze `INT-R2-001…010` regression tests;
9. integrate C → A → D capabilities in ROADMAP order;
10. rerun full evidence;
11. perform native Windows acceptance;
12. close v1.0.0 only through M011.

Update HANDOFF last.

---

## Important Notes for Next Agent

The objective is not to create a "best-of-four code collage".

The objective is:

> **one coherent formal product using B's stable recipient architecture, strengthened only by donor behaviors that independent black-box evidence showed to be better.**

Preserve one canonical model and one set of semantics.

If a donor capability conflicts with the recipient architecture, prefer the behavior contract/tests over literal donor code.

Port behavior, not identity.
