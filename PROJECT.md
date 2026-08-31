# Project

> Project: `Obsidian Property Studio`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Product Stage: `Formal integration / v1.0.0 release candidate`  
> Target Product Release: `v1.0.0`  
> Integration Baseline: `Agent B mainline + selective A/C/D capability donors`  
> Primary Platform: `Windows 10 (Build 19045+) / Windows 11 (64-bit AMD64)`  
> Product Principle: **Property governance without requiring the user to understand YAML.**

---

## 1. Purpose

Obsidian 的 Properties 可以把 Markdown Vault 從單純的文件集合提升為可篩選、分組、關聯與治理的結構化 PKM；但一般使用者常遇到下列問題：

- 不知道應該建立哪些 Properties；
- 不知道 Property name / type / values 應如何設計；
- 不熟悉 YAML；
- 不知道既有 Vault 是否已經存在可重用的 Property；
- 長期使用後容易出現 naming drift、value drift、type conflict、missing metadata；
- plain-text metadata 與 `[[Note Links]]` 關係混雜；
- 想重構 Properties，卻缺少安全、可理解的影響分析；
- 現有外掛各自解決部分問題，但使用者仍需要自己理解 schema、YAML、metadata migration。

本專案建立一個 **獨立、local-first、read-only-by-default 的 Obsidian Property Studio**，讓使用者可以透過 GUI / local Web App：

1. 看懂目前 Vault 的 Property 結構；
2. 用「我想管理什麼」而不是 YAML 語法設計 Property schema；
3. 用表單填寫 Property values；
4. 產生可複製到 Obsidian 的合法 YAML/frontmatter；
5. 找出 Property naming/value/type/schema drift；
6. 規劃 Property rename / merge / normalization / type migration；
7. 管理 Property 中的 note relationships；
8. 匯入外部 AI/Agent 產生的 schema proposal，但核心產品不依賴任何 LLM。

---

## 2. Goal

交付一個可直接在 Windows 10 (Build 19045+) 或 Windows 11 使用的 standalone local application，使不懂 YAML 的使用者也能完成：

```text
Discover
→ Design
→ Fill
→ Refactor Plan
→ Relationship Review
→ Govern
```

而不需要：

- 安裝 Obsidian community plugin；
- 學習 YAML syntax；
- 使用 Dataview；
- 設定 OpenAI / Gemini / Claude API；
- 允許應用程式修改 Vault；
- 接受應用程式替自己生成 Markdown 正文或寫作模板。

v1 的核心承諾：

> **The application may analyze the Property layer, but it does not own the user's prose.**

以及：

> **The selected Vault is an input source, not a writable workspace.**

---

---

## 2A. Formal Integration Baseline

The Arena phase is closed as a discovery/selection exercise.

Independent Round 2 black-box validation established the integration roles below:

| Candidate | Formal Integration Role | Round 2 Product Result | Primary Reason |
|---|---|---|---|
| **Agent B** | **MAINLINE / RECIPIENT** | `ROUND2_BLACKBOX_PASS` | Cleanest overall hidden-test behavior and best cross-module consistency |
| **Agent C** | **READ-ONLY DONOR** | `PASS_WITH_LIMITATIONS` | Strongest fail-closed note-link ambiguity semantics and strong relationship target resolution |
| **Agent A** | **READ-ONLY DONOR** | `HOLD` | Strong refactor/manual-review propagation despite ambiguity defects elsewhere |
| **Agent D** | **READ-ONLY DONOR** | `HOLD` | Strong governance/evidence/export-readback patterns despite hidden semantic defects |

This table is an **accepted integration decision**, not a new Arena ranking task.

Formal integration must proceed as:

```text
Agent B
= product recipient / starting implementation

Agent C
= safety + relationship + selected beginner-UX donor

Agent A
= refactor ambiguity/manual-review donor

Agent D
= export read-back + health/evidence-presentation donor
```

### Integration principle

> **Harvest proven capabilities, not whole repositories.**

The formal repository must not directly merge/cherry-pick donor Git histories.

Instead:

1. freeze donor identity;
2. establish hidden regression tests;
3. selectively port a proven capability;
4. run recipient + regression tests;
5. inspect outputs/read-back;
6. record evidence;
7. continue only if the integrated behavior remains correct.

### Formal repository lineage

`Obsidian-Property-Studio-v1.0.0` is a **new formal Git lineage**.

Do not copy any Arena candidate `.git/` directory into the formal repository.

Agent B contributes the starting product implementation, but its historical governance/evidence/Git state does not become formal project state automatically.


## 3. Success Criteria

### SC-01 — Beginner usability

一個不懂 YAML 的使用者可以透過 UI：

- 選擇 Vault；
- 看懂現有 Properties；
- 建立一組 useful schema；
- 填入 values；
- Copy 出合法 frontmatter。

不需要手寫 YAML。

### SC-02 — Vault safety

v1 對選定 Vault 必須保持 read-only：

- 不建立 note；
- 不修改 note；
- 不 rename / move / delete note；
- 不修改 `.obsidian/`；
- 不修改 attachment；
- 不自動 apply Property migration。

任何分析、schema、migration suggestion 都不能改變 Vault bytes。

### SC-03 — Accurate discovery

可掃描 Vault 中 Markdown frontmatter 並至少提供：

- note count；
- notes-with-properties count；
- property inventory；
- usage counts；
- observed storage types；
- naming variants；
- value distributions；
- malformed/unreadable frontmatter warnings。

不得把解析失敗 silent 當成「沒有 Properties」。

### SC-04 — Property design without YAML knowledge

提供 beginner-oriented Property/schema design flow，至少支援：

- goal/use-case driven design；
- existing-property reuse；
- new-property creation；
- type selection；
- required/optional schema intent；
- controlled-value suggestions；
- clear explanation of what each Property is for。

### SC-05 — Native Obsidian-aware output

輸出應對齊 Obsidian/Markdown frontmatter semantics。

v1 至少支援下列 storage concepts：

- Text
- List
- Number
- Checkbox / Boolean
- Date
- Date & time
- Tags

UI 可以提供 higher-level controls，例如：

- single-choice；
- multi-choice；
- note-link picker；

但不得假裝它們是不存在的 Obsidian storage type。Higher-level controls 必須有明確 serialization semantics。

### SC-06 — Existing-schema reuse

當使用者想新增與 Vault 既有 Property 同名或疑似近似的 Property 時，產品必須：

- 顯示 existing usage；
- 提醒可能重複；
- 允許 reuse；
- 不得 silent 建立另一個近似欄位。

### SC-07 — Safe Property refactor planning

至少能產生下列 read-only refactor analysis / migration plan：

- Rename Property；
- Merge Properties；
- Normalize Values；
- Property type conversion feasibility；
- Required / Optional schema change impact；
- conflict detection。

v1 **不得直接 apply 到 Vault**。

### SC-08 — Relationship Inbox

Property Relationship Inbox 至少能辨識：

- plain-text Property value 對應到既有 note 的候選；
- Property 中 unresolved/broken note links；
- ambiguous entity targets；
- relationship value drift；
- Property reference relink proposal。

不包含正文全文 backlink rewriting。

### SC-09 — Property Health

可提供可解釋的健康檢查，包括：

- naming drift；
- value drift；
- type conflicts；
- missing expected Properties；
- unknown/unexpected Properties；
- relationship issues。

若提供單一 Health Score，計算方式必須透明；不能用無法解釋的 magic score 取代具體問題。

### SC-10 — External AI interoperability

核心 App 不依賴 AI。

產品可匯入 external Agent / Skill 產生的 schema proposal，並在 UI 中：

- validate；
- compare with Vault；
- accept/edit/reject；
- 顯示 provenance/notes/confidence（若 proposal 提供）。

AI proposal 永遠只是 proposal，不是 Project/Vault Truth。

### SC-11 — Local-first

正常核心 workflow：

- 不要求 Internet；
- 不要求 cloud account；
- 不要求 API key；
- 不傳送 Vault 內容到外部服務；
- 不含 telemetry by default。

### SC-12 — Deterministic and auditable

相同 Vault snapshot + 相同設定應產生 deterministic discovery/refactor outputs（允許 UI timestamps 等非語意欄位排除）。

Formal claims 必須可由 tests / fixtures / read-back evidence 驗證。

---


### SC-13 — Integrated ambiguity propagation

When a note-link-oriented Property value resolves to multiple candidate notes, the integrated v1.0.0 behavior must fail closed:

- do not silently choose a target;
- do not emit a generic `[[Name]]` as if it were unambiguous;
- surface all relevant candidates;
- require an explicit user choice / path before serializing a confirmed relationship.

This adopts the strongest proven behavior from the Arena comparison.

### SC-14 — Cross-module ambiguity consistency

A parse/identity ambiguity known by Discovery must not disappear in:

- Fill;
- Refactor Planner;
- Relationship Inbox;
- Property Health;
- exported migration/report artifacts.

Known ambiguity must remain visible until explicitly resolved.

### SC-15 — Formal evidence must be regenerated

Arena candidate evidence is historical donor evidence only.

The formal v1.0.0 release must rerun and regenerate:

- automated tests;
- read-only verification;
- determinism;
- output read-back;
- common hidden regressions;
- performance measurement;
- Windows/local launch verification.

No donor `PASS` automatically transfers into the formal project.


## 4. Scope

### In Scope

#### A. Vault Discovery

- 選擇本機 Obsidian Vault / Markdown Vault folder。
- 遞迴掃描 Markdown notes。
- 解析 YAML/frontmatter Property layer。
- Property inventory / usage frequency。
- observed types / value distributions。
- naming drift / case drift / likely alias candidates。
- malformed frontmatter / unsupported structure warnings。
- default exclude Obsidian internal metadata folders such as `.obsidian/` and `.trash/` from note analysis。

#### B. Property Design

- Beginner Property Builder。
- 「What do you want to manage?」goal/use-case flow。
- schema editor。
- existing-property reuse。
- new-property design。
- Property purpose explanation。
- required / optional schema intent。
- controlled single/multi-value UI concepts。
- schema-level validation rules where justified。

#### C. Property Fill

- 選 schema。
- 表單輸入 values。
- text / number / boolean / date / datetime / list / tag。
- note-link picker against existing note names/paths。
- generated YAML/frontmatter preview。
- Copy YAML / Copy frontmatter。

**不建立正文、不建立 Note Template。**

#### D. Property Refactor Planner

- Rename Property。
- Merge Properties。
- Normalize Values。
- type conversion feasibility。
- required / optional impact。
- conflict detection。
- affected-file preview。
- machine-readable + human-readable migration plan。

**只 planning，不直接改 Vault。**

#### E. Property Relationship Inbox

- plain text → existing note-link suggestion。
- unresolved Property links。
- ambiguous entity target。
- relationship value drift。
- relink Property references proposal。

只治理 **Property values 的 relationships**。

#### F. Property Health

- naming drift。
- value drift。
- observed type conflicts。
- expected-property gaps。
- unexpected/unknown property keys。
- relationship issues。
- explainable health summary。

#### G. Outputs / Interchange

至少支援：

- Copy generated YAML/frontmatter。
- Export schema definition。
- Export Property health report。
- Export refactor/migration plan。
- Import external AI/Agent schema proposal JSON。

Agent 可選擇 JSON / Markdown 等 additional outputs，但至少一個 machine-readable schema format 必須存在。

#### H. Testing / Evidence

- synthetic Vault fixtures；
- malformed frontmatter fixtures；
- Unicode Traditional Chinese filenames/values；
- CRLF/LF cases where relevant；
- duplicate/ambiguous Property cases；
- relationship cases；
- deterministic repeat-run evidence；
- Vault hash/read-only verification；
- larger synthetic Vault benchmark。

---

### Out of Scope

以下 v1 明確不做：

1. Obsidian community plugin。
2. Obsidian plugin API integration。
3. 自動修改任何 Vault note。
4. 自動 rename/move/delete files。
5. 自動 apply Property migration。
6. Markdown body editing。
7. Markdown body rewriting。
8. Note正文 Template / Heading Template / Writing Template。
9. AI-generated正文。
10. Merge Note Identity。
11. Merge note bodies。
12. Vault-wide backlink/body relinking。
13. Attachment/media refactor。
14. orphan attachment cleanup。
15. attachment rename/move/delete。
16. Dataview replacement。
17. Bases replacement。
18. full PKM task manager。
19. cloud sync。
20. SaaS。
21. required external LLM/API。
22. 在核心 App 內實作 AI provider orchestration。
23. `Obsidian Property Architect Skill` 本身的實作。

`Obsidian Property Architect Skill` 是未來/平行 companion project；本專案只需保留清楚的 proposal import contract。

---

## 5. Requirements

### REQ-001 — Standalone local application

必須交付 GUI 或 local Web App experience，而不是只有 CLI/library。

可接受：

- local desktop GUI；
- localhost-only Web App；
- 其他真正 standalone local UI。

不接受 cloud-hosted-only solution。

### REQ-002 — Read-only Vault contract

在 v1 正常流程中，selected Vault 必須維持 byte-for-byte 不變。

Acceptance intent:

- 測試前後 Vault file manifest/hash 一致；
- 不寫入 hidden sidecar；
- 不偷偷建立 cache/report 在 Vault 內；
- application cache/output 放 Vault 外。

### REQ-003 — Honest parsing

解析失敗、unsupported frontmatter、duplicate-key ambiguity、invalid YAML 等情況：

- 顯示 warning/error；
- 不得 silent drop；
- 不得將失敗誤報成「note has no properties」。

### REQ-004 — Canonical internal representation

應有一個清楚的 internal Property/Vault/Schema representation，使 discovery、health、refactor、relationship、exports 從同一 canonical interpretation 產生。

不得讓不同 UI/report 各自重新猜 Property semantics 而造成 drift。

### REQ-005 — Beginner design flow

使用者不需要先知道 Property name 或 YAML syntax。

至少能從：

```text
I want to manage X
I want to filter/group/find by Y
```

這類 intention 建立 Property proposal。

可以使用 deterministic recipes/rules；核心不可依賴 LLM。

### REQ-006 — Existing-property awareness

建立 schema/property 前必須能查現有 Vault inventory，並警告：

- exact duplicate；
- case/spacing variants；
- probable near-duplicates。

若語意無法 deterministic 判定，應標示「possible overlap」，而不是自動合併。

### REQ-007 — Fill and copy

使用者可依 schema 填值並產生：

- readable preview；
- valid frontmatter/YAML；
- clipboard-copy action。

正文不在輸出範圍。

### REQ-008 — Note-link semantics

對 relationship-oriented Property，UI 應能從 existing note candidates 建立可理解的 note-link value。

Ambiguous note names/path collisions 不得自行選一個。

### REQ-009 — Refactor impact analysis

每一個 refactor proposal 必須提供：

- canonical target；
- affected notes count/list；
- conflicts；
- ambiguous/manual-review cases；
- proposed before/after semantics。

不得只顯示「121 files will change」而不揭露衝突。

### REQ-010 — Relationship Inbox safety

Relationship suggestion 必須區分：

- exact candidate；
- ambiguous candidate；
- unresolved/broken；
- likely drift。

低確定性不得自動提升為 confirmed relationship。

### REQ-011 — Health explainability

任何 issue/score 都應能 drill down 到：

- affected property；
- affected values/notes；
- reason；
- severity/category。

### REQ-012 — AI proposal import

至少定義並支援 versioned machine-readable proposal。

建議最低欄位：

```json
{
  "proposal_version": "1.0",
  "schema_name": "equipment",
  "properties": [
    {
      "name": "project",
      "storage_type": "text",
      "ui_control": "note_link",
      "required": false,
      "reason": "Relate this record to an existing project note",
      "allowed_values": null,
      "confidence": null
    }
  ]
}
```

實際 schema 可合理擴充，但必須：

- versioned；
- validated；
- reject malformed input honestly；
- 不直接修改 Vault。

### REQ-013 — No hidden AI dependency

沒有 AI key、沒有 Internet、沒有 Agent Skill 時，核心 App 仍完整可用。

### REQ-014 — No writing-workflow ownership

產品不得要求或假設使用者正文採用特定：

- heading；
- section；
- template；
- writing style；
- note structure。

### REQ-015 — No silent omission in reports

Inventory、health、refactor、relationship、export 等重要 output：

- 不能只驗「file generated」；
- 必須驗 canonical findings 沒有被輸出層 silent truncate。

### REQ-016 — Unicode / Windows usability

Windows 10 (Build 19045+) 與 Windows 11 上至少驗證：

- Traditional Chinese filename；
- Traditional Chinese Property value；
- spaces in path；
- nested directories；
- ordinary CRLF/LF Markdown。

### REQ-017 — Security and trust boundary

Vault contents are untrusted input.

產品不得：

- 執行 Markdown/YAML 內嵌程式；
- 執行 Obsidian plugin code；
- 執行 Templater/Dataview JS；
- follow unsafe path traversal；
- 默認 follow symlink/junction 到 Vault 外並把外部檔案當 Vault content。

### REQ-018 — Performance measurement

建立至少一組 large synthetic Vault benchmark（建議 ≥ 5,000 Markdown notes）。

v1 必須記錄：

- environment；
- fixture size；
- scan time；
- memory/major observation where practical。

**沒有預先接受的硬秒數 PASS threshold。**  
Performance 是 formal measured evidence；是否需要硬 threshold 由後續 accepted Project Truth 決定。

---


### REQ-019 — Mainline/donor isolation

The formal project must treat:

- Agent B as the implementation recipient;
- Agents A/C/D as read-only donors.

Donor source may be inspected and selectively ported only when a ROADMAP milestone names the capability.

Donor governance documents are not current-project instructions.

### REQ-020 — No wholesale donor merge

Do not:

- copy an entire donor repository over the formal root;
- import donor `.git`;
- import donor governance files as current governance;
- import donor evidence as formal release evidence;
- perform direct Git merge/cherry-pick merely for convenience.

Every donor capability must be integrated through explicit tests and review.

### REQ-021 — Formal ambiguity contract

For Property note-link creation, multiple valid candidates are a blocking ambiguity for serialization of a confirmed relationship.

The user must choose an explicit target before the product emits the final linked Property value.

### REQ-022 — Historical donor provenance

The original Arena ZIPs and/or untouched extracted workspaces are historical evidence.

The integration process must preserve their identity and must not mutate them while harvesting capabilities.

### REQ-023 — Integration regression oracle

Before substantial donor code porting, the formal repository must encode the Round 2 hidden findings as regression tests, including at least:

- malformed frontmatter is not ordinary property-free content;
- duplicate-key ambiguity survives into refactor planning;
- ambiguous note-link Fill fails closed;
- relationship canonical target resolves to the entity note, not the source note;
- design routing does not confuse equipment/procurement goals with reading workflows;
- output/read-back does not silently omit findings.


## 6. Constraints / Non-negotiables

1. **Vault is read-only in v1.**
2. **No automatic Vault mutation.**
3. **No Markdown body/template ownership.**
4. **No Obsidian plugin in v1.**
5. **No required AI/LLM/API.**
6. **No telemetry by default.**
7. **No silent parse failure.**
8. **No silent Property merge.**
9. **No silent entity/link resolution.**
10. **Ambiguity must remain visible.**
11. **Property refactor is planning-only in v1.**
12. **Relationship Inbox is Property-layer only.**
13. **Do not re-scope into attachment/media management.**
14. **Do not re-scope into note-content merge/refactor.**
15. **Do not re-scope into Dataview/Bases replacement.**
16. **Generated YAML must be inspectable before copy.**
17. **Core feature correctness must not depend on model intelligence.**
18. **AI proposal is advisory input; deterministic App validates it.**
19. **No developer-specific absolute path in shipped product.**
20. **No evidence, no PASS.**
21. **No contradictory evidence, no PASS.**
22. **Agent B is the formal recipient; A/C/D are read-only donors.**
23. **Candidate governance files are historical evidence, never current authority.**
24. **Do not import donor `.git` into the formal repository.**
25. **Do not wholesale merge donor repositories.**
26. **Known ambiguity must propagate across modules until resolved.**
27. **Formal v1.0.0 evidence must be regenerated in the integrated repository.**

---

## 7. Deliverables

Final v1 repository must include at least:

1. standalone local application source；
2. usable GUI/local Web UI；
3. Windows launch instructions / launcher as appropriate；
4. dependency/environment definition；
5. Vault discovery；
6. beginner schema design；
7. schema editor；
8. Property fill form；
9. YAML/frontmatter preview + copy；
10. Property Refactor Planner；
11. Relationship Inbox；
12. Property Health；
13. external AI proposal JSON import；
14. schema/report/migration-plan exports；
15. automated tests；
16. synthetic Vault fixtures；
17. read-only hash/integrity tests；
18. malformed YAML/frontmatter tests；
19. Unicode/Windows tests；
20. deterministic repeat-run tests；
21. larger Vault benchmark evidence；
22. user-facing README/manual；
23. known limitations；
24. release/version information；
25. final audit evidence；
26. exactly four root governance authorities:
    - PROJECT.md
    - ROADMAP.md
    - HANDOFF.md
    - AGENTS.md

Technical evidence files may be created when required by ROADMAP; they are not additional governance authorities.

---

## 8. Key Decisions / Decision Log

### DEC-001 — Product scope centers on Properties

**Decision:** Product v1 is an Obsidian Property design/governance tool, not a general Vault refactoring suite.  
**Status:** ACCEPTED

### DEC-002 — Standalone before plugin

**Decision:** v1 is standalone GUI/local Web App. Do not build an Obsidian plugin.  
**Reason:** Validate product usefulness before investing in plugin integration.  
**Status:** ACCEPTED

### DEC-003 — Vault read-only

**Decision:** v1 may read Vault but cannot mutate it.  
**Reason:** Safety, trust, and easier black-box verification.  
**Status:** ACCEPTED

### DEC-004 — Copy/paste is acceptable

**Decision:** Manual Copy YAML → Paste into Obsidian is an accepted v1 workflow.  
**Status:** ACCEPTED

### DEC-005 — No正文 Template ownership

**Decision:** Do not design or generate note body templates/headings.  
**Reason:** Writing structure is a user habit, not Property Studio authority.  
**Status:** ACCEPTED

### DEC-006 — Refactor features retained but narrowed

**Decision:** Rename/Merge/Normalize/Type migration remain in scope as read-only planning tools.  
**Status:** ACCEPTED

### DEC-007 — Relationship Inbox retained and narrowed

**Decision:** Relationship Inbox remains in v1 but only for Property values/relationships.  
**Status:** ACCEPTED

### DEC-008 — Note identity and attachments deferred

**Decision:** Merge Note Identity and Attachment Refactor are out of scope for v1.  
**Status:** ACCEPTED

### DEC-009 — AI is external/advisory

**Decision:** Core App has no required AI. An external `Obsidian Property Architect Skill` may later read a Vault and generate a proposal.  
**Status:** ACCEPTED

### DEC-010 — Proposal interchange

**Decision:** App should accept versioned machine-readable schema proposals from external Agent/Skill workflows.  
**Status:** ACCEPTED

### DEC-011 — Agent implementation autonomy

**Decision:** Arena implementation agents may choose the concrete technology stack/architecture if it satisfies this Project Truth and ROADMAP acceptance criteria.  
**Reason:** Preserve fair evaluation of autonomous product/engineering choices.  
**Status:** ACCEPTED

### DEC-012 — Property storage vs UI control distinction

**Decision:** UI conveniences such as Select or Note-Link Picker must map transparently to valid underlying Obsidian/Markdown Property storage semantics.  
**Status:** ACCEPTED

---


### DEC-013 — Agent B selected as formal mainline recipient

**Decision:** Agent B is the starting implementation for formal v1.0.0 integration.  
**Reason:** Independent Round 2 black-box validation found the cleanest overall product behavior and no major hidden core defect.  
**Status:** ACCEPTED

### DEC-014 — A/C/D become read-only capability donors

**Decision:** A, C and D are not competing mainlines after integration begins. They are selective donors only.  
**Status:** ACCEPTED

### DEC-015 — Adopt C-style fail-closed ambiguous Fill

**Decision:** If a note-link value has multiple valid target notes, integrated v1.0.0 must require explicit target selection before emitting the final relationship value.  
**Reason:** This is safer than serializing generic `[[Name]]` with unresolved identity.  
**Status:** ACCEPTED

### DEC-016 — New formal Git lineage

**Decision:** `Obsidian-Property-Studio-v1.0.0` starts a new clean Git history. Candidate `.git` directories are not imported.  
**Status:** ACCEPTED

### DEC-017 — Candidate governance is historical evidence

**Decision:** The four governance files inside Agent A/B/C/D workspaces are not authoritative for formal integration.  
**Status:** ACCEPTED

### DEC-018 — Regression tests before donor code

**Decision:** Hidden Round 2 defects/limitations must be encoded as formal regression tests before the corresponding donor capability is ported.  
**Status:** ACCEPTED

### DEC-019 — Donor evidence does not transfer PASS

**Decision:** Candidate tests/evidence support donor selection only. Formal v1.0.0 must regenerate its own evidence after integration.  
**Status:** ACCEPTED

### DEC-020 — Target platform formal scope encompasses Windows 10 and Windows 11

**Decision:** The formal target platform is defined as Windows 10 (Build 19045+) and Windows 11 (64-bit AMD64).  
**Reason:** Human project owner decision accepting native Windows 10 (Build 19045+) validation alongside Windows 11 compatibility for v1.0.0 desktop release.  
**Status:** ACCEPTED


## 9. Global Definition of Done

The project is done when:

- all in-scope modules are implemented；
- the selected Vault remains read-only under all normal v1 product flows；
- beginner Property creation works without YAML knowledge；
- discovery is accurate and parse failures are explicit；
- Property Fill generates valid inspectable frontmatter；
- refactor planning exposes conflicts and ambiguity；
- Relationship Inbox does not silently resolve ambiguous entities；
- Property Health findings are explainable；
- AI proposal import is optional, versioned, and validated；
- no body/template/plugin/attachment/note-merge scope creep exists；
- Windows-targeted usage is verified；
- required automated/black-box tests pass；
- large-Vault performance is measured；
- outputs are read back where applicable to prove no silent omission；
- docs match implementation；
- governance and evidence are mutually consistent；
- no unresolved P0/P1 defect remains；
- final ROADMAP release gate is `PASS` with evidence；
- formal repository contains no inherited donor `.git`；
- formal tests prove Round 2 hidden regressions remain fixed；
- candidate governance/evidence has not been mistaken for formal authority；
- integrated ambiguity behavior is fail-closed end-to-end.

Completion state is tracked only in `ROADMAP.md`.
