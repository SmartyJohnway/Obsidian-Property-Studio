# Project

> Project: `Obsidian Property Studio`  
> Governance Standard: `Project Four-File Governance v2.1`  
> Product Stage: `v1.1.0 Development Cycle`  
> Target Product Release: `v1.1.0`  
> Baseline: `v1.0.0 Formal Mainline (Agent B recipient + harvested A/C/D capabilities)`  
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
- 現有外掛各自解決部分問題，但使用者仍需要自己理解 schema、YAML、metadata migration；
- 整個 Vault 的主題與資料夾分類可能很多元，不同子資料夾的 Property 詞彙與慣例各不相同；
- 使用者常需要針對「特定資料夾範圍（Scope）」或「單篇 Note」進行精確的 Property 檢視、編輯、校驗與 frontmatter 產生；
- 在分析筆記間的關聯時，使用者希望在多個 Source 資料夾與 Target 資料夾之間進行 ad-hoc 分析，並可依需要將有用的分析條件儲存起來重複執行，而不是被強加預設的分類規則；
- 介面需要真正支援繁體中文與 English 的雙語切換與 Light / Dark 主題，而不是將中英文全部堆疊在單一 HTML 檔案中。

本專案建立一個 **獨立、local-first、read-only-by-default 的 Obsidian Property Studio**，讓使用者可以透過 GUI / local Web App：

1. 看懂目前 Vault / Scope 的 Property 結構；
2. 用「我想管理什麼」而不是 YAML 語法設計 Property schema；
3. 在單篇筆記工作區（Note Properties Workspace）或全新填表模式下填寫、校驗 Property values，並產生合法 Frontmatter / YAML；
4. 找出 Property naming/value/type/schema drift；
5. 在選定 Scope 下規劃 Property rename / merge / normalization / type migration；
6. 在自訂 Source Scope 與 Target Scope 之間分析 Property Links 與 Body Wikilinks 關聯，並可將分析條件儲存為 Reusable Relationship Checks；
7. 匯入外部 AI/Agent 產生的 schema proposal，但核心產品不依賴任何 LLM。

---

## 2. Goal

交付一個可直接在 Windows 10 (Build 19045+) 或 Windows 11 使用的 standalone local application，使不懂 YAML 的使用者能在 Vault、Scope、Note 三種尺度下完成：

```text
Discover
→ Design
→ Note Properties Workspace (Fill & Diff)
→ Refactor Plan
→ Relationship Analysis (Source Scope → Target Scope)
→ Govern & Health
```

而不需要：

- 安裝 Obsidian community plugin；
- 學習 YAML syntax；
- 使用 Dataview；
- 設定 OpenAI / Gemini / Claude API；
- 允許應用程式修改 Vault；
- 接受應用程式替自己生成 Markdown 正文或寫作模板；
- 被強加任何預設的知識本體（ontology）或強制的關聯規則。

v1.0.0 / v1.1.0 的核心安全承諾：

> **The application may analyze the Property layer, but it does not own the user's prose.**

以及：

> **The selected Vault is an input source, not a writable workspace.**

---

## 2A. Historical Integration Baseline (v1.0.0 Provenance)

v1.0.0 階段已透過嚴格的黑箱評測與四文件治理完成正式整合：

| Candidate | Formal Integration Role | Round 2 Product Result | Primary Reason |
|---|---|---|---|
| **Agent B** | **MAINLINE / RECIPIENT** | `ROUND2_BLACKBOX_PASS` | Cleanest overall hidden-test behavior and best cross-module consistency |
| **Agent C** | **READ-ONLY DONOR** | `PASS_WITH_LIMITATIONS` | Strongest fail-closed note-link ambiguity semantics and strong relationship target resolution |
| **Agent A** | **READ-ONLY DONOR** | `HOLD` | Strong refactor/manual-review propagation despite ambiguity defects elsewhere |
| **Agent D** | **READ-ONLY DONOR** | `HOLD` | Strong governance/evidence/export-readback patterns despite hidden semantic defects |

此歷史事實與決策在 v1.1.0 週期中保持有效。

### v1.1.0 UI/UX Donor Roles

在 v1.1.0 開發週期中，上層目錄保留的兩個 Arena 前端檔案的角色被嚴格限定為：

- `index_areaagentB.html`: **UX donor only**（參考其 beginner-friendly 導引、Light/Dark 主題、Next Action 導航、載入狀態）
- `index_areaagentD.html`: **Visual / interaction donor only**（參考其視覺層次、卡片樣式、右側 Drawer 抽屜、詳細指標呈現、麵包屑）

**Donor 檔案絕對不得作為功能 Source of Truth，不得覆蓋正式前端，亦不得將 mock/demo API 搬入正式產品。**

---

## 3. Success Criteria

### SC-01 — Beginner usability
不懂 YAML 的使用者可透過 UI 選擇 Vault、理解 Properties、設計 Schema、填值並複製合法 frontmatter。

### SC-02 — Vault safety
對選定 Vault 保持嚴格 read-only：不建立、修改、重命名、移動或刪除任何筆記與附件，不修改 `.obsidian/`，不自動套用遷移。任何分析與建議皆不改變 Vault bytes。

### SC-03 — Accurate discovery
掃描 Vault Frontmatter，提供 note count、notes-with-properties count、property inventory、usage counts、storage types、naming variants、value distributions 與 malformed frontmatter warnings。解析失敗不得靜默當作「無 Property」。

### SC-04 — Property design without YAML knowledge
提供以目標/用途為導向的 Property/Schema 設計流程，支援既有屬性重用、新型態設定、必填/選填意圖與受控值建議。

### SC-05 — Native Obsidian-aware output
輸出對齊 Obsidian/Markdown frontmatter 語意，支援 Text, List, Number, Checkbox/Boolean, Date, Date & time, Tags 等 storage concepts，高階控制項（如 note-link picker）具備明確序列化語意。

### SC-06 — Existing-schema reuse
新增或編輯屬性時，主動比對現有 Vault 庫存並警示重複或相近名稱，允許直接重用。

### SC-07 — Safe Property refactor planning
提供 Rename, Merge, Normalize Values, Type Conversion feasibility, Required/Optional 變更衝擊與衝突偵測之唯讀規劃分析，不直接套用至 Vault。

### SC-08 — Relationship Inbox & Analysis
能辨識 plain-text 屬性值對應既有筆記的候選、unresolved/broken 連結、ambiguous 實體目標與關係漂移。

### SC-09 — Property Health
提供透明、可解釋的健康檢查，涵蓋 naming drift、value drift、type conflicts、missing properties、unexpected properties 與 relationship issues。

### SC-10 — External AI interoperability
核心 App 完全不依賴 AI；可匯入外部 Agent/Skill 產生的版本化 schema proposal JSON 並進行本機校驗與比對。

### SC-11 — Local-first
核心工作流程無須連網、無須雲端帳號、無須 API key，不傳輸 Vault 內容，無預設遙測。

### SC-12 — Deterministic and auditable
相同 Vault 快照與設定產生一致且可由測試/read-back 驗證的分析結果。

### SC-13 — Integrated ambiguity propagation
當 note-link 解析至多個同名候選時，行為必須 fail-closed，不自動猜測，必須要求使用者明確選擇。

### SC-14 — Cross-module ambiguity consistency
解析層發現的歧義與問題必須貫穿 Fill, Refactor, Relationships, Health 與 Export，不得在中途靜默消失。

### SC-15 — Formal evidence regeneration
正式發布時必須在整合庫中重新執行並生成全部自動化測試、唯讀性驗證、確定性與讀回測試證據。

---

### v1.1.0 Success Criteria (New)

### SC-16 — True Lightweight Bilingual i18n
UI 支援繁體中文（zh-Hant）與 English 即時無縫切換，偏好記錄於本機儲存（localStorage）。所有語系檔（JSON）皆為 local 資源，無 CDN 依賴，靜態文字、動態訊息與錯誤代碼均走 i18n 鍵值，UI 不得在同一畫面堆疊兩套中英文 DOM。

### SC-17 — Clean Theme System (Light / Dark)
支援 Light 與 Dark 主題，偏好記錄於本機儲存，顏色採用 design tokens 管理，在兩種主題下皆滿足可讀性與對比度要求。

### SC-18 — Multi-level Context Model & Multi-folder Scope
正式建立 `Vault → Scope → Note → Schema` 四層工作模型。Scope 支援「整個 Vault（Entire Vault）」、「單一資料夾（One Folder）」、「多資料夾組合（Multiple Folders）」與「單篇筆記（Single Note）」，支援包含子資料夾（include_subfolders）選項。資料夾重疊時自動去重（deduplicate）。切換 Scope 時優先基於記憶體索引過濾，不重複掃描整個硬碟 Vault。主畫面上方持續顯示當前 Context（Vault / Scope / Note）。

### SC-19 — Note Properties Workspace (Existing Note & Blank Modes)
提供單篇筆記屬性工作區。支援全 Vault 筆記搜尋與選擇（清楚標示同名路徑歧義），能讀入既有屬性、進行表單編輯、對比語意 Diff、依全域/區域 Schema 進行校驗，並產生 Frontmatter 預覽與複製。若筆記 frontmatter 存在 malformed 或 duplicate keys，必須 fail-closed 拒絕編輯並揭露原因。絕不修改或覆寫硬碟上的筆記。

### SC-20 — Scope-Aware Relationship Analysis & Separation
關聯分析支援自訂 `Source Scope`（支援多資料夾）與 `Target Scope`（支援多資料夾）。清楚區分並分開呈現「Property Links」與「Body Wikilinks」分析結果。分析結果清楚分類為：`VALID`、`BROKEN`、`AMBIGUOUS` 與 `OUTSIDE SELECTED TARGET`（連結存在但目標落在所選 Target Scope 之外）。

### SC-21 — Body Wikilink Analysis (Strict Read-Only)
可分析 Markdown 正文中的 Wikilinks 關聯，但正文內容僅供讀取解析，**嚴禁修改、替換、修復正文或重寫反向連結**。

### SC-22 — User-Initiated Saved Relationship Checks
系統**不內建任何預設的關聯規則或知識本體假設**。Ad-hoc 關聯分析為預設流程；使用者可主動將有價值的分析條件命名、添加備註並儲存為「已儲存的關聯檢查（Saved Relationship Check）」，供未來重新執行。檢查結果僅具建議性質（advisory），且設定檔儲存於 Vault 外部（如本機應用程式儲存/localStorage），絕不寫入 Vault。

---

## 4. Scope

### In Scope

#### A. Vault Discovery vNext
- 選擇本機 Obsidian Vault 資料夾。
- 遞迴掃描 Markdown notes，解析 frontmatter Property layer。
- **Scope-aware Inventory**：依當前 Scope 計算筆記數、屬性統計、型態分布與問題清單，同時提供全 Vault 全域背景比對。
- **Property Drawer**：點擊屬性開啟右側抽屜查看詳細資訊、受影響筆記清單，並可點擊跳轉至 Note Properties Workspace。
- 預設排除 `.obsidian/` 與 `.trash/`。

#### B. Property Design vNext
- Beginner Property Builder，支援「我想管理什麼」意圖引導。
- 同時結合 User Goal + 當前 Scope 庫存 + 全域 Vault 庫存推薦屬性。
- 清楚區分「Scope 內既有」、「Vault 其他位置既有」、「全新屬性」與「可能重複」。

#### C. Note Properties Workspace
- **Existing Note Mode**：搜尋/選擇特定筆記（支援同名路徑消歧義），讀入解析後屬性，支援編輯、刪除、新增屬性值，顯示前後語意 Diff，支援複製更新後的 Frontmatter。遇 duplicate keys / malformed 時 fail-closed。
- **New / Blank Mode**：保留既有基於 Schema 填寫全新 frontmatter 並複製的流程。
- 預覽無效時 Copy 動作 disabled。

#### D. Property Refactor Planner vNext
- Rename, Merge, Normalize, Type Conversion feasibility 分析。
- **Scope-aware Refactor**：明確標示當前 Scope 內受影響筆記數量，以及 Scope 外存在該屬性的筆記數量；規劃遷移計劃時嚴格限制於所選 Scope，**絕不隱性擴大範圍**。

#### E. Relationships vNext (Scope-Aware)
- 支援多資料夾 `Source Scope` 與多資料夾 `Target Scope`。
- 預設 Ad-hoc 分析模式，無預設強加規則。
- 判定結果：`VALID`, `BROKEN`, `AMBIGUOUS`, `OUTSIDE SELECTED TARGET`。
- 支援 Property Links 分析。

#### F. Body Wikilink Analysis (Analysis-Only)
- 讀取 Markdown 正文中的 `[[Wikilink]]` 並分析其連結有效性與目標範圍。
- **嚴格唯讀，絕不修改或覆寫正文內容**。
- 與 Property Links 結果分開呈現。

#### G. Saved Relationship Checks
- 使用者主動儲存關聯分析條件（名稱、備註、Source Scope、Target Scope、關聯來源、屬性名稱）。
- 支援重新執行、編輯備註與刪除/封存。
- 儲存於 Vault 外部，結果僅為諮詢建議（advisory）。

#### H. Property Health vNext
- **Scope-aware Health**：僅以當前 Scope 內的筆記計算健康指標與問題清單，可選全 Vault 對比。
- 所有 issue 均可 drill-down 至具體筆記並支援跳轉至 Note Properties Workspace。

#### I. UI / UX Overhaul & i18n
- 繁體中文（zh-Hant）與 English 雙語系，架構式 i18n，無 CDN。
- Light / Dark 雙主題支援，design tokens 管理。
- 整合式工作區版面（Sidebar 分組：Overview, Context, Create, Govern, Advanced；頂部 Persistent Context Bar；右側 Drawer；清晰的 Initial / Loading / Ready / Empty / Blocked / Error 狀態）。

#### J. Outputs / Interchange
- 複製 Frontmatter / YAML。
- 匯出 Schema 定義、Health 報告、Refactor 計劃。
- 匯出 / 匯入 Saved Relationship Checks。
- 匯入外部 AI / Agent Schema Proposal JSON。

#### K. Testing & Evidence
- 保留全部 v1.0.0 回歸測試（95 項）。
- 新增 v1.1.0 專屬回歸測試套件（V11-001 ~ V11-018）。
- 5,000 篇筆記基準測試、Vault 唯讀雜湊驗證與 Windows 10/11 本機測試。

---

### Out of Scope (Non-goals)

以下在 v1.1.0 明確不做：

1. Obsidian community plugin。
2. 自動修改任何 Vault note。
3. 自動建立、重命名、移動或刪除檔案。
4. 自動 apply Property migration / Refactor。
5. Markdown 正文寫作與編輯。
6. Markdown 正文改寫（Body rewriting）。
7. 自動修復正文 Wikilinks（Body link repair）。
8. 正文/寫作/標題模板（Writing / Heading templates）。
9. AI 生成筆記正文。
10. 合併筆記實體或合併筆記內文。
11. 全 Vault 正文反向連結改寫。
12. 附件/媒體檔案重構與清理。
13. Dataview / Bases 替代品。
14. 雲端同步、多使用者協作或 SaaS。
15. 核心 App 內嵌必要 AI / LLM / API key。
16. 強制預設的關聯規則或知識本體（Enforced Ontology）。
17. 使用者自訂屬性詞彙編輯器（User-editable Property Glossary，正式延期至 v1.1.1）。
18. 自動將使用者資料夾進行分類或自動重組 Vault 結構。
19. Graph database 或向量嵌入 / RAG。


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

### [v1.1.0 New Requirements]

### REQ-024 — True Lightweight Bilingual i18n Layer
前端必須具備獨立的 i18n 模組與本地 JSON 語系檔（`locales/zh-Hant.json`, `locales/en.json`）。不得在 HTML 內重複中英文 DOM；語言偏好儲存於 localStorage；切換語言無需重新整理頁面，`<html lang>` 屬性同步更新；離線環境下完整可用。

### REQ-025 — Design Token Based Theme Support
提供 Light 與 Dark 主題，樣式統一以 CSS Custom Properties (Design Tokens) 管理，支援系統偏好與使用者手動切換（儲存於 localStorage），符合無障礙對比標準。

### REQ-026 — Formal Scope Domain Model
後端與領域層必須正式支援 Scope 定義（支援 Entire Vault、One Folder、Multiple Folders、Single Note 與 include_subfolders）。多資料夾選取時以聯集（Union）計算並自動去重。

### REQ-027 — In-Memory Scope Derivation
切換 Scope 時必須基於記憶體中的筆記與屬性索引進行過濾與衍生計算，不得在切換 Scope 時重新掃描整個磁碟 Vault。重新掃描 Vault 時自動使 Scope 衍生快取失效。

### REQ-028 — Persistent Context Navigation
UI 必須包含永久顯示的 Context Bar（呈現當前 Vault, Scope, Note），以及分組結構清晰的導航欄（Overview, Context, Create, Govern, Advanced）。

### REQ-029 — Note Properties Workspace
提供 Existing Note 與 New/Blank 兩種模式。在 Existing Note 模式下：
- 能依檔名或相對路徑搜尋筆記，並清楚區分同名筆記；
- 載入並解析現有屬性，允許編輯值與對照 Schema；
- 提供語意 Diff 預覽；
- 若筆記存在 malformed frontmatter 或 duplicate keys，必須 fail-closed 拒絕編輯並顯示明確原因；
- 預覽無效時 Copy 動作 disabled；
- 絕不直接修改磁碟上的筆記。

### REQ-030 — Scope-Aware Relationship Analysis
關係分析必須支援使用者指定的 Source Scope（多資料夾）與 Target Scope（多資料夾）。狀態分類必須涵蓋 `VALID`、`BROKEN`、`AMBIGUOUS` 與 `OUTSIDE SELECTED TARGET`。

### REQ-031 — Body Wikilink Read-Only Analysis
可分析 Markdown 正文中的 Wikilinks，但嚴格限制為唯讀分析。絕不得修改正文內容、修復連結或重寫反向連結。分析結果必須與 Property Links 明確分開標示。

### REQ-032 — No Default Relationship Rules
系統不得內建任何預設的資料夾關聯規則或知識本體假設。所有關聯分析以 Ad-hoc 探索為預設起點。

### REQ-033 — User-Initiated Saved Relationship Checks
使用者可將滿意的關聯分析條件主動儲存為 Saved Relationship Check（包含名稱、備註、Source/Target Scope、屬性）。設定必須儲存於 Vault 外部，結果僅具諮詢性質（advisory），不作強制規則。

### REQ-034 — Scope-Aware Refactor & Health
Refactor Planner 與 Property Health 必須嚴格根據當前選定的 Scope 進行影響計算與呈現。Refactor 規劃絕不得隱性擴大到 Scope 外部的筆記；Health 指標不得將 Scope 內外數據混算。

### REQ-035 — Universal Module States & Drawer Drill-Down
主要模組皆需定義明確的 Initial, Loading, Ready, Empty, Blocked, Error 狀態。Discover 與 Health 提供右側 Drawer 抽屜供深入檢視，並提供開啟至 Note Properties Workspace 的快捷操作。

### REQ-036 — Note Properties Search & Hierarchical Folder Tree
Note Properties Workspace 必須同時支援即時路徑搜尋（Search）與全知識庫層級資料夾樹狀目錄瀏覽（Hierarchical Folder Tree with Expand/Collapse-All），移除人為筆記筆數上限限制。呈現筆記時標示 Scope 關聯性與資料夾路徑；同名筆記必須呈現完整相對路徑以消歧義，絕不自動猜測同名 Note。

### REQ-037 — Structured Multi-Select Schema Inputs & Adopt Next Actions
Schema Designer 必須提供結構化的「管理對象（Management Objects）」與「管理需求（Management Needs）」確定性預設複選清單，自由文字降為選填輔助；產生的建議屬性清單支援個別勾選/剔除，並提供明確的「採用此屬性架構 (Adopt Schema)」CTA。採用後建立 Current Schema，並導引至「套用到既有筆記」或「建立新筆記 Frontmatter」；Blank Note 模式在未選擇 Schema 時提供清晰的 Empty State 與前往設計器導引，採用後動態渲染可用表單控制項。所有建議標籤與原因透過 i18n 完全在地化。

### REQ-038 — Controlled Vocabulary Refactor Planner & Human-Readable Primary View
Refactor Planner 的操作輸入（來源屬性、目標型態、屬性值正規化受控對照）必須最大程度使用 Scope 既有屬性/值之下拉選單、多選方塊或受控對照表，避免要求手動輸入已知資料；Rename 目標衝突需即時警告；空目標嚴格 fail-closed。計畫產出以直觀的統計摘要、Scope 範圍與受影響筆記清單為第一主視圖，原始 JSON 計畫作為進階/證據視圖折疊提供。維持 Planning-only，絕不執行寫入。

### REQ-039 — Human-Readable Property Vocabulary Layer
v1.1.0 必須提供純展示層（Presentation Layer）的雙語屬性標籤、用途說明、典型儲存型態/輸入元件與範例值，並在全站各模組提供情境式 Help Drawer 引導，同時維持 Canonical YAML Property Keys 原始不可變與不翻譯。對於未預先定義的未知/自訂屬性，系統絕不得臆測語意，僅呈現知識庫中觀察到的客觀數據事實。



---

## 6. Constraints / Non-negotiables

1. **Vault is read-only in v1.0.0 and v1.1.0.**
2. **No automatic Vault mutation.**
3. **No Markdown body/template ownership.**
4. **No Obsidian plugin in v1.1.0.**
5. **No required AI/LLM/API.**
6. **No telemetry by default.**
7. **No silent parse failure.**
8. **No silent Property merge.**
9. **No silent entity/link resolution.**
10. **Ambiguity must remain visible.**
11. **Property refactor is planning-only in v1.1.0.**
12. **Relationship analysis distinguishes Property Links and Body Wikilinks.**
13. **Body Wikilink analysis is strictly read-only; never mutates prose.**
14. **No default relationship rules or enforced ontology.**
15. **Saved Relationship Checks are user-defined and stored outside Vault.**
16. **Note Properties Workspace fails closed on malformed frontmatter or duplicate keys.**
17. **Scope switching must not trigger full Vault rescan.**
18. **i18n must be architecture-driven without duplicating complete HTML files.**
19. **Arena B / D are donors only (UX / Visual) without functional authority.**
20. **No developer-specific absolute path in shipped product.**
21. **No evidence, no PASS.**
22. **No contradictory evidence, no PASS.**
23. **Known ambiguity must propagate across modules until resolved.**
24. **Formal evidence must be regenerated in the formal repository.**

---

## 7. Deliverables

v1.1.0 發布必須包含至少：

1. 獨立本機應用程式原始碼（Python + 本機 Web UI）；
2. 現代化 UI Shell（整合 Context Bar、Sidebar 分組、右側 Drawer、完整狀態處理）；
3. 輕量雙語 i18n 模組（`app/ui/i18n.js`, `locales/zh-Hant.json`, `locales/en.json`）；
4. Light / Dark 主題支援；
5. Scope 領域模型與引擎（支援 Entire Vault, One Folder, Multi-Folder, Single Note, include_subfolders）；
6. Scope-aware Discover、Property Health 與 Refactor Planner；
7. Note Properties Workspace（Existing Note 模式 + New/Blank 模式，含語意 Diff 與 fail-closed 保護）；
8. Scope-aware Relationship Analysis（Source Scope → Target Scope, Property Links 分析）；
9. Body Wikilink Analysis 模組（純唯讀正文分析）；
10. Saved Relationship Checks 管理模組（外部儲存、重跑、備註）；
11. 保留並通過全套 v1.0.0 回歸測試（95 項）；
12. 全套 v1.1.0 回歸測試套件（V11-001 ~ V11-018 全部通過）；
13. ≥5,000 篇筆記基準測試數據；
14. Vault 唯讀雜湊驗證與 Windows 10/11 本機測試證據；
15. 更新後之使用者手冊與 README；
16. 唯四根目錄治理權威檔案：
    - `PROJECT.md`
    - `ROADMAP.md`
    - `HANDOFF.md`
    - `AGENTS.md`
    以及歷史封存檔 `docs/archive/ROADMAP_v1.0.0.md`（唯讀快照）。

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

### DEC-021 — Four-Level Context Architecture
**Decision:** 產品由 Whole-Vault Analysis 工具演進為 `Vault → Scope → Note → Schema` 四層 Context 模型。  
**Reason:** 滿足使用者在不同子資料夾群與單篇筆記尺度下的細緻治理需求。  
**Status:** ACCEPTED

### DEC-022 — Multi-Folder Scope Support
**Decision:** Scope 支援選取多個資料夾 root，以聯集與路徑去重計算筆記集合。  
**Reason:** 真實 PKM Vault 常有多個資料夾屬於同一專案或業務範疇。  
**Status:** ACCEPTED

### DEC-023 — Architecture-Driven Lightweight i18n
**Decision:** 採用輕量原生 JavaScript i18n 模組與獨立 JSON 語系檔，不使用大型框架或 CDN，不重複 HTML DOM。  
**Reason:** 保持 local-first、高效能與易維護性。  
**Status:** ACCEPTED

### DEC-024 — Ad-Hoc Relationship Analysis with Optional Saved Checks
**Decision:** 關聯分析預設為 Ad-hoc 模式，不預設任何關聯規則；使用者可主動將分析條件保存為 Saved Relationship Checks。  
**Reason:** 尊重使用者的知識結構探索過程，不強加假想的 ontology。  
**Status:** ACCEPTED

### DEC-025 — Body Wikilink Analysis is Strictly Read-Only
**Decision:** 允許讀取正文解析 Wikilinks 並分析關聯，但嚴格禁止任何修改正文或自動修復連結的操作。  
**Reason:** 嚴格遵守「不擁有使用者正文」與「Vault 唯讀」的核心安全契約。  
**Status:** ACCEPTED

### DEC-026 — Arena B/D as UI/UX Donors Without Functional Authority
**Decision:** Arena B 作為 UX donor、Arena D 作為視覺/互動 donor，正式功能與安全真理完全以正式 repo 與 v1.1.0 規格為準。  
**Status:** ACCEPTED

### DEC-027 — Saved Checks Stored Outside Vault
**Decision:** Saved Relationship Checks 儲存於 Vault 外部（如應用程式設定或 localStorage），嚴禁寫入 Vault。  
**Status:** ACCEPTED

### DEC-028 — Note Properties Workspace Fails Closed on Corrupted Frontmatter
**Decision:** Existing Note 模式遇到 duplicate keys 或 malformed YAML 時必須 fail-closed 拒絕編輯並揭示原因。  
**Reason:** 避免因不完整解析導致使用者既有屬性被無意損壞。  
**Status:** ACCEPTED

### DEC-029 — In-Memory Scope Indexing
**Decision:** 切換 Scope 僅在記憶體索引中進行過濾，不觸發硬碟全 Vault 重新掃描。  
**Reason:** 保證大庫（≥5,000 筆記）切換 Scope 時的即時響應。  
**Status:** ACCEPTED

---

## 9. Global Definition of Done

The project (v1.1.0) is done when:

- all in-scope v1.1.0 modules are implemented；
- the selected Vault remains byte-for-byte read-only under all product flows；
- true zh-Hant / English i18n works seamlessly without DOM duplication or CDN；
- Light / Dark theme works seamlessly with verified contrast；
- Multi-level Context Model (Vault / Scope / Note / Schema) is functional end-to-end；
- Multi-folder Scope correctly unions and deduplicates notes without full Vault rescan；
- Discover, Health, and Refactor Planner correctly respect Scope boundaries without silent scope leakage；
- Note Properties Workspace supports Existing Note (with semantic diff & fail-closed protection) and New/Blank Fill without touching note bodies；
- Scope-aware Relationship Analysis supports Multi-folder Source/Target with correct status categorization (`VALID`, `BROKEN`, `AMBIGUOUS`, `OUTSIDE_SELECTED_TARGET`)；
- Body Wikilink analysis functions as strict read-only without modifying note prose；
- No default relationship rules exist; user-initiated Saved Relationship Checks persist outside Vault；
- all 95 retained v1.0.0 regression tests pass；
- all 18 new v1.1.0 regression tests (`V11-001` ~ `V11-018`) pass；
- large-Vault (≥5,000 notes) performance benchmark is measured and recorded；
- Windows 10 (Build 19045+) native launcher and UI acceptance freshly verified; Windows 11 (64-bit AMD64) is a supported target with native verification allowed to remain NOT YET VERIFIED as an accepted non-blocking limitation if no test machine is available (Windows 10 evidence must never be represented as Windows 11 evidence)；
- documentation (README, User Guide) reflects v1.1.0 capabilities；
- all four root governance files are mutually consistent；
- final ROADMAP v1.1.0 release gate is `PASS` with non-contradictory evidence.

Completion state is tracked only in `ROADMAP.md`.
