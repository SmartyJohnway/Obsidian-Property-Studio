# Obsidian Property Advisor v1.2.1 Human Agent Runtime Acceptance

- **Artifact Lineage**: Companion Skill for Obsidian Property Studio
- **Skill Version**: `1.2.1`
- **Application Compatibility**: Obsidian Property Studio `v1.2.0` (Immutable / Unchanged)
- **Evaluation Date**: 2026-09-08
- **Evaluator**: Human Owner (Dr. J)

---

## 1. Finding Closure & Verification Evidence

### SK-F01 — Proposal Contract Pre-Output Compatibility Validation
- **Original Claude Failure**: Claude emitted `storage_type: "text"` combined with `ui_control: "note_link_list"`. Property Studio correctly rejected this proposal because `note_link_list` strictly requires `storage_type: "list"`.
- **Implementation Hardening**:
  - Implemented normative Pre-Output Contract Validation section in `SKILL.md` (Section 9).
  - Explicitly documented compatibility matrix and concrete forbidden examples in `SKILL.md` and `references/proposal-contract.md`.
  - Added Gate 2 (Contract Syntax & Compatibility Checklist) before final JSON emission.
  - Added deterministic regression test `test_v12_prp_005_sk_f01_proposal_compatibility_matrix`.
- **Hardened Retest Result**: Claude emitted `storage_type: "list"` with `ui_control: "note_link_list"`.
- **Property Studio Interoperability**: `PASS` (Schema validation passed with 0 errors).
- **Status**: **CLOSED / HUMAN VERIFIED**.

### SK-F02 — Clarification & Restraint Before Schema Generation
- **Original Multi-Agent Drift**: When given ambiguous prompt (*"https://blog.kyomind.tw/memos/ 這篇內容我要放進 Obsidian。請依照已安裝的 Obsidian Property Advisor Skill 幫我整理。"*):
  - Claude immediately inferred a 7-property schema without asking clarification.
  - Hermes asked clarification questions and demonstrated minimalism.
- **Implementation Hardening**:
  - Established Mandatory Management-Purpose Gate (Section 3).
  - Defined strict bifurcation: **Path A (Clarification First)** vs **Path B (Conservative No/Minimal-Metadata)**.
  - Defined normative restraint rule: *Information extractability does NOT justify Property creation*.
  - Enforced prose vs property boundary (summaries, opinions, metrics remain in body prose).
  - Formalized first-class "No Properties" option.
  - Added Gate 1 (Pre-Schema Decision Checklist) before proposal drafting.
- **Hardened Retest Results**:
  - **Claude Retest**: Initiated Path A clarification inquiring about long-term management intent rather than assuming a multi-property schema. `PASS`.
  - **Hermes Retest**: Maintained restraint and proposed minimal metadata with clear prose boundary. `PASS`.
  - **Zero/Minimal-Property Awareness**: Both agents recognized when zero custom properties are appropriate. `PASS`.
  - **Narrative / Property Boundary**: Narrative summaries and opinions preserved in body prose. `PASS`.
- **Status**: **CLOSED / HUMAN VERIFIED**.

---

## 2. Combined Runtime Acceptance Summary

| Verification Gate | Agent / Runtime | Model Used | Result |
|---|---|---|---|
| Contract Compatibility (SK-F01) | Claude | Haiku 4.5 | PASS |
| Purpose Clarification & Restraint (SK-F02) | Claude | Haiku 4.5 | PASS |
| Contract Compatibility (SK-F01) | Hermes | nous:upstage/solar-pro4:free | PASS |
| Purpose Clarification & Restraint (SK-F02) | Hermes | nous:upstage/solar-pro4:free | PASS |
| Multi-Agent Portability | Claude + Hermes | Haiku 4.5 + nous:upstage/solar-pro4:free | PASS |
| Property Studio Interoperability | Property Studio v1.2.0 | deterministic local validator | PASS |

> **Provenance Note:**  
> Model selections above were supplied by the Human Evaluator from the actual Human Agent Runtime Acceptance sessions and are recorded as tested runtime configuration rather than inferred from Agent output.

---

## 3. Non-Blocking Canonical Vocabulary Observation

Different AI models may propose different candidate property names (e.g. `source_url` vs `url`, `topics` vs `tags`). This is expected and non-blocking:
- The Companion Skill operates strictly in an **advisory capacity**.
- The Advisor does NOT claim that any proposed property name is canonical across the user's vault.
- **Obsidian Property Studio** remains the single deterministic authority for evaluating Existing keys, New keys, Type conflicts, Glossary definitions, and Schema library comparisons upon import.

