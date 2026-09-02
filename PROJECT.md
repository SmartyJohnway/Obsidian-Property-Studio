# Project

> Project: `Obsidian Property Studio`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Product Stage: `v1.2.0 Development Cycle`  
> Target Product Release: `v1.2.0`  
> Baseline: `v1.1.0 Formal Mainline (Published release cca408c / 176/176 tests PASS)`  
> Primary Platform: `Windows 10 (Build 19045+) / Windows 11 (64-bit AMD64)`  
> Product Principle: **Build and govern your own Property system — without surrendering control of your Vault.** (繁中：建立並治理屬於你自己的 Property 系統，同時讓 Vault 始終掌握在你手上。)

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
- 現有外掛各自解決部分問題，但使用者仍需要自己理解 schema、YAML、metadata migration；
- 整個 Vault 的主題與資料夾分類可能很多元，不同子資料夾的 Property 詞彙與慣例各不相同；
- 使用者常需要針對「特定資料夾範圍（Scope）」或「單篇 Note」進行精確的 Property 檢視、編輯、校驗與 frontmatter 產生；
- 在分析筆記間的關聯時，使用者希望在多個 Source 資料夾與 Target 資料夾之間進行 ad-hoc 分析，並可依需要將有用的分析條件儲存起來重複執行，而不是被強加預設的分類規則；
- 介面需要真正支援繁體中文與 English 的雙語切換與 Light / Dark 主題，而不是將中英文全部堆疊在單一 HTML 檔案中；
- **[v1.2.0 核心演進]**：
  - 使用者需要建立並維護自己的一套屬性詞彙庫（User Property Glossary）與可重用的具名架構庫（Named Schema Library）；
  - 使用者需要將設計好的 Named Schema 指派為特定 Scope 的預期規範（Scope → Expected Schema），並在健康分析中精確檢視「預期 vs 實際」的架構漂移（Desired vs Actual Schema Drift）；
  - 使用者在設計或選取 Schema 後，需要能直接與既有筆記進行架構調和（Reconciliation），明確辨識相符、缺漏、衝突與架構外保留屬性；
  - 健檢發現的問題需要能一鍵鑽取（Drilldown）至確切筆記工作區並攜帶問題情境；
  - 外部 AI / Agent 產生的 Schema 建議需要完整的人性化審查工作流程（可檢視、編輯、接受為具名架構或拒絕），並搭配獨立的 Obsidian Property Advisor Companion Skill；
  - 架構演進時需要支援版本化與跨版本遷移規劃（Migration Planning），以及整體治理設定檔（Governance Profile）的匯出/匯入與本機持久化。

本專案建立一個 **獨立、local-first、read-only-by-default 的 Personal Property Governance System**，讓使用者可以透過 GUI / local Web App 建立並治理屬於自己的 Property 系統，同時嚴格保持 Vault 的安全唯讀。

---

## 2. Goal

交付一個可直接在 Windows 10 (Build 19045+) 或 Windows 11 使用的 standalone local application，使不懂 YAML 的使用者能在 Vault、Scope、Note 三種尺度下完成：

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

而不需要：

- 安裝 Obsidian community plugin；
- 學習 YAML syntax；
- 使用 Dataview；
- 設定 OpenAI / Gemini / Claude API；
- 允許應用程式修改 Vault；
- 接受應用程式替自己生成 Markdown 正文或寫作模板；
- 被強加任何預設的知識本體（ontology）或強制的關聯規則。

核心安全承諾與邊界：

> **The application may analyze the Property layer, but it does not own the user's prose.**

以及：

> **The selected Vault is an input source, not a writable workspace.**

以及：

> **Local deterministic governance + Human decision + Read-only Vault safety.**

AI 可以提供建議（AI may advise），確定性工具進行校驗（Deterministic tooling validates），人類做最終決定（Human decides）。應用程式絕不靜默寫入 Vault。

---

## 2A. Historical Integration Baseline (v1.0.0 & v1.1.0 Provenance)

### v1.0.0 Provenance
v1.0.0 階段已透過嚴格的黑箱評測與四文件治理完成正式整合：

| Candidate | Formal Integration Role | Round 2 Product Result | Primary Reason |
|---|---|---|---|
| **Agent B** | **MAINLINE / RECIPIENT** | `ROUND2_BLACKBOX_PASS` | Cleanest overall hidden-test behavior and best cross-module consistency |
| **Agent C** | **READ-ONLY DONOR** | `PASS_WITH_LIMITATIONS` | Strongest fail-closed note-link ambiguity semantics and strong relationship target resolution |
| **Agent A** | **READ-ONLY DONOR** | `HOLD` | Strong refactor/manual-review propagation despite ambiguity defects elsewhere |
| **Agent D** | **READ-ONLY DONOR** | `HOLD` | Strong governance/evidence/export-readback patterns despite hidden semantic defects |

### v1.1.0 Release Baseline
v1.1.0 開發週期已於 2026-09-02 完成正式發布與封存（Release tag: `v1.1.0`, Commit: `cca408c0456e1fe94e8224bd6550cf30c7274926`），所有 176 項自動化測試通過，並在 Windows 10 生產環境完成真人驗收。其歷史事實、發布資產與封存路線圖（`docs/archive/ROADMAP_v1.1.0.md`）保持不可變。

---

## 3. Success Criteria

### [v1.0.0 Retained Success Criteria]
- **SC-01 — Beginner usability**: 不懂 YAML 的使用者可透過 UI 選擇 Vault、理解 Properties、設計 Schema、填值並複製合法 frontmatter。
- **SC-02 — Vault safety**: 對選定 Vault 保持嚴格 read-only：不建立、修改、重命名、移動或刪除任何筆記與附件，不修改 `.obsidian/`，不自動套用遷移。任何分析與建議皆不改變 Vault bytes。
- **SC-03 — Accurate discovery**: 掃描 Vault Frontmatter，提供 note count、notes-with-properties count、property inventory、usage counts、storage types、naming variants、value distributions 與 malformed frontmatter warnings。解析失敗不得靜默當作「無 Property」。
- **SC-04 — Property design without YAML knowledge**: 提供以目標/用途為導向的 Property/Schema 設計流程，支援既有屬性重用、新型態設定、必填/選填意圖與受控值建議。
- **SC-05 — Native Obsidian-aware output**: 輸出對齊 Obsidian/Markdown frontmatter 語意，支援 Text, List, Number, Checkbox/Boolean, Date, Date & time, Tags 等 storage concepts，高階控制項（如 note-link picker）具備明確序列化語意。
- **SC-06 — Existing-schema reuse**: 新增或編輯屬性時，主動比對現有 Vault 庫存並警示重複或相近名稱，允許直接重用。
- **SC-07 — Safe Property refactor planning**: 提供 Rename, Merge, Normalize Values, Type Conversion feasibility, Required/Optional 變更衝擊與衝突偵測之唯讀規劃分析，不直接套用至 Vault。
- **SC-08 — Relationship Inbox & Analysis**: 能辨識 plain-text 屬性值對應既有筆記的候選、unresolved/broken 連結、ambiguous 實體目標與關係漂移。
- **SC-09 — Property Health**: 提供透明、可解釋的健康檢查，涵蓋 naming drift、value drift、type conflicts、missing properties、unexpected properties 與 relationship issues。
- **SC-10 — External AI interoperability**: 核心 App 完全不依賴 AI；可匯入外部 Agent/Skill 產生的版本化 schema proposal JSON 並進行本機校驗與比對。
- **SC-11 — Local-first**: 核心工作流程無須連網、無須雲端帳號、無須 API key，不傳輸 Vault 內容，無預設遙測。
- **SC-12 — Deterministic and auditable**: 相同 Vault 快照與設定產生一致且可由測試/read-back 驗證的分析結果。
- **SC-13 — Integrated ambiguity propagation**: 當 note-link 解析至多個同名候選時，行為必須 fail-closed，不自動猜測，必須要求使用者明確選擇。
- **SC-14 — Cross-module ambiguity consistency**: 解析層發現的歧義與問題必須貫穿 Fill, Refactor, Relationships, Health 與 Export，不得在中途靜默消失。
- **SC-15 — Formal evidence regeneration**: 正式發布時必須在整合庫中重新執行並生成全部自動化測試、唯讀性驗證、確定性與讀回測試證據。

### [v1.1.0 Retained Success Criteria]
- **SC-16 — True Lightweight Bilingual i18n**: UI 支援繁體中文（zh-Hant）與 English 即時無縫切換，偏好記錄於本機儲存（localStorage）。所有語系檔（JSON）皆為 local 資源，無 CDN 依賴，靜態文字、動態訊息與錯誤代碼均走 i18n 鍵值，UI 不得在同一畫面堆疊兩套中英文 DOM。
- **SC-17 — Clean Theme System (Light / Dark)**: 支援 Light 與 Dark 主題，偏好記錄於本機儲存，顏色採用 design tokens 管理，在兩種主題下皆滿足可讀性與對比度要求。
- **SC-18 — Multi-level Context Model & Multi-folder Scope**: 正式建立 `Vault → Scope → Note → Schema` 四層工作模型。Scope 支援「整個 Vault（Entire Vault）」、「單一資料夾（One Folder）」、「多資料夾組合（Multiple Folders）」與「單篇筆記（Single Note）」，支援包含子資料夾（include_subfolders）選項。資料夾重疊時自動去重。切換 Scope 時優先基於記憶體索引過濾，不重複掃描整個硬碟 Vault。
- **SC-19 — Note Properties Workspace (Existing Note & Blank Modes)**: 提供單篇筆記屬性工作區。支援全 Vault 筆記搜尋與樹狀目錄瀏覽（清楚標示同名路徑歧義），能讀入既有屬性、進行表單編輯、對比語意 Diff、依全域/區域 Schema 進行校驗，並產生 Frontmatter 預覽與複製。遇 duplicate keys / malformed 時 fail-closed。
- **SC-20 — Scope-Aware Relationship Analysis & Separation**: 關聯分析支援自訂 `Source Scope` 與 `Target Scope`。清楚區分並分開呈現「Property Links」與「Body Wikilinks」分析結果（`VALID`、`BROKEN`、`AMBIGUOUS`、`OUTSIDE SELECTED TARGET`）。
- **SC-21 — Body Wikilink Analysis (Strict Read-Only)**: 可分析 Markdown 正文中的 Wikilinks 關聯，但正文內容僅供讀取解析，嚴禁修改、替換、修復正文或重寫反向連結。
- **SC-22 — User-Initiated Saved Relationship Checks**: 系統不內建任何預設的關聯規則或知識本體假設。Ad-hoc 關聯分析為預設流程；使用者可主動將分析條件儲存為「已儲存的關聯檢查」，設定檔儲存於 Vault 外部。

---

### [v1.2.0 New Success Criteria]

### SC-23 — Workflow Closure & Zero Dead-End CTA
所有主要 CTA 必須具備完整的工作流程閉環（Starting State → User Intent → Action → State Transfer → Deterministic Processing → Visible Result → Terminal Artifact / Meaningful Next Action），並納入受治理的 Workflow Closure Matrix，不接受僅更換畫面或僅回傳 HTTP 200 作為完成。

### SC-24 — User-Editable Property Glossary
使用者可自訂與管理個人屬性詞彙庫（Canonical Key, 繁中標籤, 英文標籤, 說明, 使用指引, 範例值, 別名, 分類），遵循 `內建詞彙 → 使用者覆寫 → 觀察到的事實` 優先序，且保證 Canonical YAML Key 永遠不被翻譯或修改。

### SC-25 — Named Schema Library
使用者可將採用的屬性架構儲存為具名架構（Named Schema），包含版本、屬性清單、必填/選填標示與中繼資料，支援 CRUD 操作並持久化於 Vault 外部。

### SC-26 — Schema to Existing Note Reconciliation
支援將 Named Schema 或 Current Schema 套用至既有筆記，呈現「相符 Matches」、「缺漏 Missing」、「衝突 Conflict」與「架構外保留 Outside Schema」四種調和狀態，保留無關屬性，輸出語意 Diff 與驗證通過的 Frontmatter。

### SC-27 — Scope to Expected Schema Assignment & Drift Analysis
支援將特定 Scope 指派預期 Named Schema，Property Health 能精確對比 Desired vs Actual，檢視缺少預期屬性、型態不符、數值漂移、非預期屬性等架構漂移情況。

### SC-28 — External AI Proposal Review & Schema Candidate Workflow
外部 AI Proposal JSON 匯入後，提供完整的人性化審查工作介面（呈現與當前 Scope、全庫、詞彙庫及架構庫的比對結果），支援接受為具名架構、線上編輯候選架構或明確拒絕。

### SC-29 — Obsidian Property Advisor Companion Skill
提供獨立、解耦的 AI Companion Skill，遵循明確的觸發情境、意圖釐清原則與屬性建議規範，產出符合 Proposal Contract 的建議，核心 App 完全不依賴 Skill。

### SC-30 — Health Finding to Exact Note Drilldown
Health 診斷問題可一鍵鑽取至確切筆記工作區，並跨視圖完整傳遞問題情境（finding_id, property_key, finding_type, expected_schema_id），在工作區高亮標示相關問題。

### SC-31 — Schema Versioning & Migration Planning
Named Schema 支援跨版本對比（新增、刪除、型態變更、數值詞彙變更、必填變更），Migration Planner 能針對選定 Scope 產出結構化遷移計畫（純唯讀規劃，不自動套用至 Vault）。

### SC-32 — App-Local Governance Persistence & Profile Import/Export
所有治理狀態（詞彙庫、架構庫、Scope 指派、Saved Checks、偏好設定）持久化於 Vault 外部的應用程式目錄中，並支援整份 Governance Profile 的匯出與匯入（含版本檢查、預覽與 fail-closed 驗證）。

### SC-33 — Fail-Closed Backward Compatibility
完整相容 v1.1 資料結構與測試基準，遇到毀損或不相容的設定時 fail-closed 拒絕載入並提示修復，絕不靜默丟棄或強制覆寫使用者資料。

---

## 4. Scope

### In Scope (v1.2.0)

#### A. User Property Glossary Management
- 使用者自訂屬性展示層詞彙與中繼資料（繁中標籤、英文標籤、說明、指引、範例值、別名、分類）。
- 詞彙優先層次：`System Built-in → User Override → Observed Vault Facts`。
- 全站通用 Help Drawer 即時讀取使用者詞彙庫。
- 保證 Canonical YAML Property Key 原始不變。

#### B. Named Schema Library & CRUD
- 具名架構庫（Named Schema Library）管理介面與後端引擎。
- 支援建立、讀取、編輯、刪除、版本設定、中繼資料儲存。
- 從 Schema Designer 採用時支援「儲存為具名架構」。
- 資料儲存於 Vault 外部。

#### C. Schema → Existing Note Reconciliation Workspace
- 將 Named / Current Schema 與選定既有筆記進行調和（Reconciliation）。
- 四種狀態：`✓ Existing & Matches`, `＋ Missing from Note`, `⚠ Conflict with Schema`, `• Outside Schema (Preserved)`。
- 保留既有無關屬性。
- 整合語意 Diff、驗證後 Frontmatter 預覽與複製功能。

#### D. Scope → Expected Schema Assignment & Drift Detection
- 為特定 Scope 設定預期 Named Schema（手動指派，無強制預設）。
- Property Health 模組支援「Desired vs Actual」架構漂移分析。
- 檢測：缺少屬性、型態衝突、受控值漂移、非預期額外屬性。

#### E. External AI Proposal Review Workspace
- 取代 raw JSON 終點，提供結構化 Proposal 審查 UI。
- 對比 Current Scope、Whole Vault、Property Glossary、Named Schema Library。
- 顯示相容狀態、型態衝突、數值衝突、別名警告。
- 主要操作：`[Accept as Named Schema]`, `[Edit Candidate]`, `[Reject Proposal]`, `[Reconcile with Existing Note]`。

#### F. Obsidian Property Advisor Skill (Decoupled Companion Skill)
- 獨立的 AI Companion Skill 規格、提示詞與範例（`skills/obsidian-property-advisor/`）。
- 意圖釐清指引（詢問知識管理用途而非 YAML 語法）。
- 產生符合 Proposal Contract 的輸出。
- 核心 App 不依賴 Skill，不要求 API Key。

#### G. Health Finding → Exact Note Drilldown
- Health 面板的受影響筆記清單支援一鍵跳轉至 Note Properties Workspace。
- 跨模組明確傳遞情境（finding_id, property, type, note_path）。
- 工作區顯示導航來源與待處理問題提示。

#### H. Schema Versioning & Migration Planning
- 具名架構版本管理（v1 → v2）。
- 架構差異比對（新增、移除、型態變更、受控值變更、必填變更）。
- 產生 Scope 範圍內的唯讀遷移影響計畫（嚴格 Planning-only，絕不修改 Vault）。

#### I. App-Local Governance Persistence & Governance Profile I/O
- 本機儲存目錄架構（獨立於 Vault）。
- Governance Profile JSON 匯出與匯入（含架構校驗、變更預覽、fail-closed 防護）。

#### J. Testing & Governance
- 保留全套 176 項 v1.1.0 回歸測試。
- 新增 v1.2.0 各模組回歸測試（`V12-WFC-*`, `V12-GLO-*`, `V12-SCH-*`, `V12-REC-*`, `V12-SCP-*`, `V12-DRIFT-*`, `V12-HLT-*`, `V12-AIP-*`, `V12-SKL-*`, `V12-MIG-*`, `V12-PROF-*`, `V12-RO-*`, `V12-I18N-*`）。
- 維護權威 Workflow Closure Matrix。
- ≥5,000 篇筆記基準測試與 Vault 唯讀雜湊驗證。

---

### Out of Scope (Non-goals)

以下在 v1.2.0 明確不做：

1. 自動寫入或修改 Vault 筆記（No automatic Vault mutation）。
2. 自動執行架構遷移（No Apply Migration to Vault）。
3. 自動在 Vault 建立、重命名、移動或刪除檔案。
4. Markdown 正文寫作、改寫或正文模板（No body/prose ownership）。
5. 自動修復正文 Wikilinks（No body link rewriting）。
6. AI 自動採用或自動套用建議（No AI auto-acceptance）。
7. 核心 App 依賴強制 LLM、API Key 或雲端服務。
8. 雲端同步、多使用者協作或 SaaS 帳號。
9. Vector Database / RAG 子系統。
10. Graph Database。
11. Obsidian Community Plugin 改寫。
12. 強制預設的關聯規則、分類法或知識本體（No forced ontology）。
13. 自動重組或分類使用者的資料夾結構。

---

## 5. Requirements

### [v1.0.0 Retained Core Requirements]
- `REQ-001` Standalone local application (GUI / local Web UI, no cloud-only).
- `REQ-002` Read-only Vault contract (Vault maintains byte-for-byte identical hash).
- `REQ-003` Honest parsing (malformed/duplicate keys surfaced as warnings/errors, never silent dropped).
- `REQ-004` Canonical internal representation across all modules.
- `REQ-005` Beginner design flow without YAML knowledge.
- `REQ-006` Existing-property awareness & reuse suggestions.
- `REQ-007` Fill and copy frontmatter with inspectable preview.
- `REQ-008` Note-link semantics with fail-closed ambiguity handling.
- `REQ-009` Refactor impact analysis with explicit conflict & ambiguity disclosure.
- `REQ-010` Relationship Inbox safety (distinguish exact, ambiguous, unresolved, drift).
- `REQ-011` Health explainability and drill-down capability.
- `REQ-012` Versioned AI proposal import without AI dependency.
- `REQ-013` No hidden AI/cloud dependency in core workflows.
- `REQ-014` No writing-workflow/prose ownership.
- `REQ-015` No silent omission in reports and exports.
- `REQ-016` Unicode Traditional Chinese & Windows path compatibility.
- `REQ-017` Security & trust boundary (treat Vault contents as untrusted input).
- `REQ-018` Performance measurement on synthetic benchmark (≥5,000 notes).
- `REQ-019` Mainline/donor isolation.
- `REQ-020` No wholesale donor merge or candidate `.git` inheritance.
- `REQ-021` Fail-closed note-link ambiguity serialization contract.
- `REQ-022` Historical donor provenance preservation.
- `REQ-023` Integration regression oracle maintenance.

---

### [v1.1.0 Retained Requirements]
- `REQ-024` True Lightweight Bilingual i18n Layer (`locales/zh-Hant.json`, `locales/en.json`, no CDN, localStorage).
- `REQ-025` Design Token Based Theme Support (Light / Dark).
- `REQ-026` Formal Scope Domain Model (Entire Vault, One Folder, Multi-Folder, Single Note, include_subfolders).
- `REQ-027` In-Memory Scope Derivation (no full disk rescan on scope switch).
- `REQ-028` Persistent Context Navigation (Topbar context chip, grouped sidebar).
- `REQ-029` Note Properties Workspace (Existing Note & Blank modes, semantic diff, fail-closed corrupted YAML).
- `REQ-030` Scope-Aware Relationship Analysis (Multi-folder Source & Target, 4-state classification).
- `REQ-031` Body Wikilink Read-Only Analysis (strictly analysis-only, never mutate prose).
- `REQ-032` No Default Relationship Rules (ad-hoc discovery by default).
- `REQ-033` User-Initiated Saved Relationship Checks (stored outside Vault, advisory only).
- `REQ-034` Scope-Aware Refactor & Health (strictly scoped calculations).
- `REQ-035` Universal Module States & Drawer Drill-Down.
- `REQ-036` Note Properties Search & Hierarchical Folder Tree (no note truncation limits, path disambiguation).
- `REQ-037` Structured Multi-Select Schema Inputs & Adopt Next Actions.
- `REQ-038` Controlled Vocabulary Refactor Planner & Human-Readable Primary View.
- `REQ-039` Human-Readable Property Vocabulary Layer (Presentation layer bilingual labels, canonical key immutability).

---

### [v1.2.0 New Formal Requirements]

### REQ-040 — Workflow Closure Contract
Every primary CTA must be represented in a maintained Workflow Closure Matrix defining Starting State, User Intent, Action, State Transfer, Processing, Visible Result, Terminal Outcome / Next Action, Failure Path, Automated Verification, and Human Verification. A CTA cannot PASS merely because a handler exists or an API returns HTTP 200.

### REQ-041 — User-editable Property Glossary
Users may manage personal display and advisory metadata for canonical Property keys (Traditional Chinese label, English label, description, usage guidance, examples, aliases, category). Precedence is strictly enforced: `System Built-in Glossary → User Override → Observed Vault Facts`. Canonical YAML Property keys must never be mutated or translated.

### REQ-042 — Named Schema Library
Users can save adopted Schemas as reusable named governance objects (stable schema ID, display name, version, description, Property definitions, required/recommended flags, creation/update metadata) stored outside the selected Vault, with full CRUD support.

### REQ-043 — Schema → Existing Note Reconciliation
Provide a dedicated reconciliation flow when applying a Named or Current Schema to an existing Note. The UI must explicitly present four distinct reconciliation states: `✓ Existing & Matches`, `＋ Missing from Note`, `⚠ Existing but Conflicts with Schema`, and `• Existing Note Property outside Schema (Preserved)`. The flow must generate a semantic diff, a validated frontmatter preview, and clipboard copy without writing to the Vault.

### REQ-044 — Scope → Expected Schema Assignment
A Scope may be associated with an Expected/Desired Named Schema as user-defined governance metadata (no default assignments, strictly advisory).

### REQ-045 — Desired vs Actual Schema Drift
When an Expected Schema is assigned to a Scope, Property Health must compare Desired vs Actual state, detecting missing expected properties, type mismatches, governed value drift, unmanaged properties, and missing required relationships in an explainable, read-only diagnostic view.

### REQ-046 — External AI Proposal → Schema Candidate Workflow
Replace the raw JSON validation endpoint with a complete Proposal Review workspace. The UI compares proposed properties against Current Scope, Whole Vault, Property Glossary, and Named Schema Library, surfacing compatibility status, type conflicts, value vocabulary conflicts, and alias warnings. Users can choose to `[Accept as Named Schema]`, `[Edit Candidate]`, `[Reject Proposal]`, or `[Reconcile with Existing Note]`.

### REQ-047 — Obsidian Property Advisor Skill
Provide an independent, decoupled AI companion skill (`obsidian-property-advisor`) with clear trigger guidelines, management purpose clarification rules, property design principles, and validated Proposal JSON outputs conforming strictly to the authoritative Proposal Contract. Core application workflows must not depend on this Skill.

### REQ-048 — Health Finding → Note Drilldown
Health diagnostic findings for affected notes must provide one-click drilldown into Note Properties Workspace, carrying full finding context across navigation (`finding_id`, `property_key`, `finding_type`, `note_path`, `expected_schema_id`) and highlighting the relevant issue in the workspace.

### REQ-049 — Schema Versioning & Migration Planning
Named Schemas support explicit versioning. Schema comparison identifies added, removed, type-changed, value-changed, and requirement-changed properties. The Migration Planner evaluates selected Scope and produces a human-readable migration plan without automatically executing any writes to Vault notes.

### REQ-050 — Governance Profile Import / Export
Users can export and import complete governance state (User Glossary, Named Schemas, Scope assignments, Saved Checks, preferences) as a structured Governance Profile JSON. Import must support schema validation, change preview, and fail-closed handling of malformed profiles without silent overwrites.

### REQ-051 — App-local Governance Persistence
All governance state must persist across sessions in application-local storage outside the selected Vault. Vault content, governance/app state, temporary session state, and export artifacts must remain strictly separated.

### REQ-052 — Backward Compatibility & Fail-Closed Upgrade
v1.2 must transparently read v1.1-compatible state and contracts. If safe migration or parsing of corrupted state is impossible, the application must fail closed, display an explanatory error, and offer recovery guidance without silently coercing or discarding data.

---

## 6. Constraints / Non-negotiables

1. **Vault is strictly read-only across v1.0.0, v1.1.0, and v1.2.0.**
2. **No automatic Vault mutation under any workflow.**
3. **No Markdown body/prose ownership or writing template enforcement.**
4. **No Obsidian plugin requirement in v1.2.0.**
5. **No mandatory AI/LLM/API key in core application workflows.**
6. **No telemetry by default.**
7. **No silent parse failure or silent property drops.**
8. **No silent Property merge or ambiguous resolution.**
9. **Ambiguity must remain visible and fail closed.**
10. **Property refactor and migration planning are strictly read-only.**
11. **Relationship analysis clearly distinguishes Property Links and Body Wikilinks.**
12. **Body Wikilink analysis is strictly read-only; never mutates prose.**
13. **No default relationship rules or enforced ontology.**
14. **Saved Relationship Checks and governance state are stored outside Vault.**
15. **Note Properties Workspace fails closed on malformed frontmatter or duplicate keys.**
16. **Scope switching operates in-memory without full Vault disk rescans.**
17. **i18n is architecture-driven without duplicating HTML DOM trees.**
18. **Arena candidate files are historical read-only donors without functional authority.**
19. **No developer-specific absolute paths in shipped code or artifacts.**
20. **No evidence, no PASS; no contradictory evidence, no PASS.**
21. **Known ambiguity must propagate across modules until resolved.**
22. **Formal evidence must be regenerated in the formal repository.**
23. **No Dead-End CTA: every primary CTA must reach a meaningful result or explicit next action.**
24. **Cross-module workflows must transfer context explicitly rather than relying on accidental global state.**
25. **Canonical Property keys remain strictly immutable; display labels must never overwrite YAML keys.**
26. **AI proposals are advisory only; deterministic validation and human decision are mandatory before adopting.**
27. **Schema migration planning is planning-only; never automatically executes writes to Vault notes.**

---

## 7. Deliverables

v1.2.0 發布必須包含至少：

1. 獨立本機應用程式原始碼（Python + 本機 Web UI）；
2. 現代化 UI Shell（整合 Context Bar、Sidebar 分組、右側 Drawer、完整狀態處理）；
3. 輕量雙語 i18n 模組（`locales/zh-Hant.json`, `locales/en.json`）；
4. Light / Dark 主題支援；
5. Scope 領域模型與引擎（Entire Vault, One Folder, Multi-Folder, Single Note, include_subfolders）；
6. 使用者屬性詞彙庫管理模組（User Property Glossary CRUD & Persistence）；
7. 具名架構庫管理模組（Named Schema Library CRUD, Versioning & Persistence）；
8. 架構調和工作區（Schema → Existing Note Reconciliation Workspace）；
9. 範圍預期架構與漂移分析引擎（Scope Expected Schema & Drift Diagnostics）；
10. 外部 AI Proposal 審查工作區（Proposal Review, Compatibility Check, Accept/Edit/Reject）；
11. 獨立 Companion Skill 規格與測試用例（`skills/obsidian-property-advisor/`）；
12. 健檢問題一鍵鑽取至筆記工作區（Health Finding → Note Drilldown）；
13. 架構版本比對與遷移規劃引擎（Schema Versioning & Migration Planner）；
14. 治理設定檔匯入/匯出模組（Governance Profile Import/Export with Change Preview）；
15. 本機外部持久化儲存層（App-local storage outside Vault）；
16. 全套 176 項 v1.1.0 回歸測試通過；
17. 全套 v1.2.0 新增回歸測試套件通過；
18. 受治理之 Workflow Closure Matrix 驗證報告；
19. ≥5,000 篇筆記基準測試數據；
20. Vault 唯讀雜湊驗證與 Windows 10/11 本機測試證據；
21. 更新後之使用者手冊與 README；
22. 唯四根目錄治理權威檔案：
    - `PROJECT.md`
    - `ROADMAP.md`
    - `HANDOFF.md`
    - `AGENTS.md`
    以及歷史封存檔 `docs/archive/ROADMAP_v1.0.0.md` 與 `docs/archive/ROADMAP_v1.1.0.md`（唯讀快照）。

---

## 8. Key Decisions / Decision Log

### [v1.0.0 Accepted Key Decisions]
- `DEC-001` Product scope centers on Properties (ACCEPTED)
- `DEC-002` Standalone before plugin (ACCEPTED)
- `DEC-003` Vault read-only (ACCEPTED)
- `DEC-004` Copy/paste is acceptable workflow (ACCEPTED)
- `DEC-005` No note body template ownership (ACCEPTED)
- `DEC-006` Refactor features retained as read-only planning (ACCEPTED)
- `DEC-007` Relationship Inbox retained and narrowed to property values (ACCEPTED)
- `DEC-008` Note identity and attachments deferred (ACCEPTED)
- `DEC-009` AI is external/advisory only (ACCEPTED)
- `DEC-010` Proposal interchange format support (ACCEPTED)
- `DEC-011` Agent implementation autonomy within constraints (ACCEPTED)
- `DEC-012` Property storage vs UI control distinction (ACCEPTED)
- `DEC-013` Agent B selected as formal mainline recipient (ACCEPTED)
- `DEC-014` A/C/D become read-only capability donors (ACCEPTED)
- `DEC-015` Fail-closed ambiguous Fill contract (ACCEPTED)
- `DEC-016` New clean formal Git lineage (ACCEPTED)
- `DEC-017` Candidate governance is historical evidence only (ACCEPTED)
- `DEC-018` Regression tests before donor code (ACCEPTED)
- `DEC-019` Donor evidence does not transfer PASS (ACCEPTED)
- `DEC-020` Target platform encompasses Windows 10 & 11 (ACCEPTED)

---

### [v1.1.0 Accepted Key Decisions]
- `DEC-021` Four-Level Context Architecture (`Vault → Scope → Note → Schema`) (ACCEPTED)
- `DEC-022` Multi-Folder Scope Support (ACCEPTED)
- `DEC-023` Architecture-Driven Lightweight i18n (ACCEPTED)
- `DEC-024` Ad-Hoc Relationship Analysis with Optional Saved Checks (ACCEPTED)
- `DEC-025` Body Wikilink Analysis is Strictly Read-Only (ACCEPTED)
- `DEC-026` Arena B/D as UI/UX Donors Without Functional Authority (ACCEPTED)
- `DEC-027` Saved Checks Stored Outside Vault (ACCEPTED)
- `DEC-028` Note Properties Workspace Fails Closed on Corrupted Frontmatter (ACCEPTED)
- `DEC-029` In-Memory Scope Indexing (ACCEPTED)

---

### [v1.2.0 Accepted Key Decisions]

### DEC-030 — Personal Property Governance Architecture
**Decision:** 產品定位由「Property 輔助分析工具」升級為「個人屬性治理系統（Personal Property Governance System）」，核心由「詞彙庫 + 具名架構庫 + 預期架構指派 + 漂移診斷 + 既有筆記調和 + 遷移規劃 + AI 建議審查」構成。  
**Status:** ACCEPTED

### DEC-031 — Zero Dead-End CTA & Workflow Closure Contract
**Decision:** 所有主要 CTA 必須具備從使用者意圖到終端產物/明確下一步的完整工作流程閉環，嚴禁畫面跳轉後無操作承接或輸出 raw JSON 的斷頭操作。  
**Status:** ACCEPTED

### DEC-032 — Governance State Persisted Outside Vault
**Decision:** 使用者自訂詞彙庫、具名架構庫、Scope 預期架構關聯、已存檢查與偏好設定均儲存於 Vault 外部本機應用程式目錄，嚴禁在 Vault 內產生中繼資料檔案。  
**Status:** ACCEPTED

### DEC-033 — Canonical Key Immutability across Presentation & AI Layers
**Decision:** 人性化或雙語標籤僅存在於展示層與審查層，底層 Canonical YAML Property Key 永遠保持原始字串不可變，不進行語意翻譯或替換。  
**Status:** ACCEPTED

### DEC-034 — Deterministic AI Proposal Review & Validation Gate
**Decision:** 外部 AI 建議必須經過確定性契約校驗，並在人性化 UI 中與真實 Vault 庫存/詞彙庫進行對比，由人類進行採納、編輯或拒絕，不允許 AI 自動套用。  
**Status:** ACCEPTED

### DEC-035 — Independent Companion Skill Decoupling
**Decision:** Obsidian Property Advisor Skill 作為外部伴隨 Skill 獨立發布，核心 App 完全不依賴 Skill，維持 100% 離線可用。  
**Status:** ACCEPTED

### DEC-036 — Planning-Only Migration Guarantee
**Decision:** 架構版本遷移規劃（Migration Planner）維持純分析與規劃產出，絕不提供一鍵批次修改 Vault 筆記之寫入操作。  
**Status:** ACCEPTED

---

## 9. Global Definition of Done

The project (v1.2.0) is done when:

- all in-scope v1.2.0 P0 requirements (REQ-040 ~ REQ-052) are implemented；
- all primary workflows achieve full closure without dead-end CTAs as verified in the Workflow Closure Matrix；
- the selected Vault remains byte-for-byte read-only across all workflows；
- User Property Glossary is editable, respects precedence, and preserves canonical key immutability；
- Named Schema Library supports full CRUD, versioning, and persistence outside Vault；
- Schema → Existing Note Reconciliation cleanly presents matches, missing, conflicts, and outside-schema properties with valid Frontmatter preview & copy；
- Scope → Expected Schema assignment correctly diagnoses Desired vs Actual schema drift in Property Health；
- Health findings drill down cleanly into exact Note Workspace preserving diagnostic context；
- External AI Proposal workflow provides human-readable review, Vault/Glossary comparisons, and Accept/Edit/Reject actions；
- Obsidian Property Advisor Skill is fully specified and validated against fixtures without core App dependency；
- Schema Migration Planner generates structured, read-only migration plans for Scope notes；
- Governance Profile import/export works round-trip with schema validation and fail-closed safety；
- all 176 retained v1.1.0 regression tests pass；
- all new v1.2.0 regression tests (`V12-*`) pass；
- large-Vault (≥5,000 notes) performance benchmark is measured and recorded；
- Windows 10 (Build 19045+) native launcher and UI acceptance freshly verified; Windows 11 (64-bit AMD64) status accurately recorded；
- documentation (README, User Guide, Specs) reflects v1.2.0 capabilities；
- all four root governance files are mutually consistent；
- final ROADMAP v1.2.0 release gate is `PASS` with non-contradictory evidence.

Completion state is tracked only in `ROADMAP.md`.
