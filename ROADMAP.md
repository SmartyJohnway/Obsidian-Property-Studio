# Obsidian Property Studio — Active Roadmap

> Project: `Obsidian Property Studio`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Current Released/Staged Line: `v1.2.0`  
> Status: `HUMAN ACCEPTANCE COMPLETE / RELEASE STAGING / READY_FOR_MERGE_AND_RELEASE_DECISION`  
> Archived Completed Roadmap: `docs/archive/ROADMAP_v1.2.0.md`  
> Archive SHA-256: `48707ccd278b5cecbd8fc19b2849daedd6c4bcd70e6efc95077336cd8c0767b3`  
> Historical v1.1.0 Roadmap: `docs/archive/ROADMAP_v1.1.0.md` (SHA-256: `d68f8ac57411896dd1b2b10b0716629f2d12c46b1e0bb6a2a1368c961ee7ac2a`)  
> GitHub PR: `#2` (`feat(v1.2): Personal Property Governance System`)  

---

##### Current State

Project State: `ACTIVE`  
Current Target: `v1.2.0`  
Current Milestone: `NONE`  
Current Milestone Status: `PASS`  
Current Task: `NONE`  
Last Verified Gate: `M022 — Full Workflow Closure, Human Acceptance & Release Gate PASS`  
Current Blocker: `NONE`  
Next Action: `Final source & release artifact audit -> Human Owner (Dr. J) merge decision -> tag/release if approved.`  
Implementation: `COMPLETE (v1.2.0 Personal Property Governance System fully implemented across M016~M022 and Commit 21A~21N human acceptance closures)`  
Automated Verification: `PASS (253/253 tests pass, 5,040-note benchmark verified, Vault 100% byte-for-byte read-only and zero mutation)`  
Human Verified Acceptance: `PASS — Human Verified (Dr. J external Windows 10 production UI walkthrough verified on 2026-09-07; HA-F01~HA-F23 findings backlog CLEAR; Gate 1~Gate 6 smoke gates PASS)`  
Release Readiness: `READY_FOR_MERGE_AND_RELEASE_DECISION`  
Accepted Limitation: `Windows 11 AMD64 native verification recorded as NOT YET VERIFIED due to test host unavailability (accepted non-blocking release limitation per human approved contract).`  
Future Version Scope: `NOT YET OPENED`  
Last Updated: `2026-09-07`

---

# 1. Authority & Governance Boundaries

This active ROADMAP reflects the current release-staging state of `Obsidian Property Studio`:

- `PROJECT.md` defines accepted v1.2.0 Product Truth, Scope, and Non-goals.
- `ROADMAP.md` (this file) defines active release staging and points to authoritative archived milestones.
- `HANDOFF.md` tracks the latest runtime recovery context and next action.
- `AGENTS.md` governs agent operating behavior.
- `docs/archive/ROADMAP_v1.2.0.md` is the authoritative, immutable historical record of the complete v1.2.0 execution roadmap (SHA-256: `48707ccd278b5cecbd8fc19b2849daedd6c4bcd70e6efc95077336cd8c0767b3`).
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

# 3. Release Staging Overview & Milestone Archive Summary

All v1.2.0 milestones have been completed, verified, and closed:

| Milestone | Description | Status | Verification State |
|---|---|---|---|
| **M015** | v1.2 Governance Transition & Architecture Freeze | `PASS` | `PASS` (176 tests) |
| **M016** | Workflow Closure Foundation & State Transfer Engine | `PASS` | `PASS` (6 tests) |
| **M017** | Personal Glossary & Named Schema Library Persistence | `PASS` | `PASS` (6 tests) |
| **M018** | Schema-to-Note Reconciliation & Health Drilldown | `PASS` | `PASS` (3 tests) |
| **M019** | Scope Expected Schema Assignment & Drift Diagnostics | `PASS` | `PASS` (2 tests) |
| **M020** | External AI Proposal Review & Companion Skill Packaging | `PASS` | `PASS` (3 tests) |
| **M021** | Schema Versioning, Migration Planner & Governance Profile [P1] | `PASS` | `PASS` (4 tests) |
| **M022** | Full Workflow Closure, Human Acceptance & Release Gate | `PASS` | `PASS` (253 tests + Human Verified) |

Full milestone details, acceptance criteria traces, and verification records are preserved in:
`docs/archive/ROADMAP_v1.2.0.md` (SHA-256: `48707ccd278b5cecbd8fc19b2849daedd6c4bcd70e6efc95077336cd8c0767b3`).

---

# 4. Future Version Scope Policy

**No v1.3.0 scope has been authorized yet.**

Development of subsequent milestones or scope expansion remains strictly blocked until:
1. Human Owner (Dr. J) reviews and merges PR #2 into `main`;
2. A formal v1.2.0 release tag is published;
3. New project goals, requirements, and specifications are explicitly authorized in `PROJECT.md`.


