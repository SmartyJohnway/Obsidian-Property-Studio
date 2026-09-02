# Obsidian Property Studio v1.1.0 — UI/UX vNext 設計規格

> 文件用途：  
> 1. 作為 **v1.1.0 正式改版的產品／UI/UX 設計依據**。  
> 2. 作為提交給 Antigravity（AG）實作的工程契約與驗收基準。  
> 3. 作為專案擁有者未來回顧「為什麼下一代要這樣改」的設計決策紀錄。  
>
> 基準版本：**v1.0.0**  
> 目標版本：**v1.1.0**  
> 文件狀態：**PROPOSED DESIGN BASELINE — 待正式納入 PROJECT / ROADMAP**  
>
> 核心原則：**v1.1.0 是 v1.0.0 的 UX / Context Architecture 演進，不是重寫產品、不改變唯讀安全契約。**

---

# 0. Executive Summary

v1.0.0 已經證明 Obsidian Property Studio 的核心產品方向成立：

- Local-first。
- Vault read-only。
- 不需要 AI / API key / cloud。
- 能掃描整個 Vault，理解既有 Properties。
- 能設計 Schema。
- 能產生合法 Frontmatter。
- 能做 Property Refactor Planning。
- 能分析 Property Relationships。
- 能做 explainable Property Health。
- 能匯入外部 AI / Agent schema proposal。
- 所有結果以「分析／預覽／複製」為主，不直接修改 Vault。

但是 v1.0.0 的工作模型仍然偏向：

> **Whole-Vault Property Analysis Tool**

使用者實際工作時，常常不是只想問「整個 Vault 怎麼樣」，而是：

- 我現在只想看某一組資料夾。
- 我的 Vault 有多個主題，彼此 Property vocabulary 差很多。
- 我想同時把幾個資料夾視為同一個工作範圍。
- 我想處理某一篇特定 Note 的 Properties。
- 我想分析「這些資料夾裡的 Note」是否正確連到「另外幾個資料夾」。
- 我目前甚至還不知道自己最後會建立什麼分類規則，希望先分析、慢慢理解，再決定哪些關聯檢查值得儲存。
- 我希望繁體中文 / English 可以真正切換，而不是兩套文字全部塞在 HTML 裡。
- 我希望 UI 更像一個 Property Governance Workspace，而不是八個平鋪功能頁。

因此 v1.1.0 的核心不是單純「換漂亮 UI」，而是正式導入：

```text
Vault
  ↓
Scope
  ↓
Note
  ↓
Schema
```

並讓 Relationships 使用：

```text
Source Scope
  ↓
Relationship Analysis
  ↓
Target Scope
```

同時引入：

- i18n（繁體中文 / English）
- Light / Dark theme
- Multi-folder Scope
- Single-note Property Workspace
- Ad-hoc Relationship Analysis
- Optional Saved Relationship Checks
- 更成熟的 Navigation / Drawer / Next Action / Dashboard
- 明確的 loading / empty / error / fail-closed states

---

# 1. 不變的 Product Truth

v1.1.0 不得因 UI 改版而破壞下列 v1.0.0 核心安全契約。

## 1.1 Vault 仍然 Read-only

正式產品仍不得：

- create note
- rename note
- move note
- delete note
- rewrite note body
- automatically apply Property changes
- automatically apply Refactor plans
- automatically repair Wikilinks
- automatically rewrite body links

產品仍然只能：

- read
- analyze
- validate
- compare
- preview
- generate copyable output
- export reports outside the Vault

核心文案仍應維持：

> **The selected Vault is an input source, not a writable workspace.**

## 1.2 AI 仍然是 Optional

v1.1.0 不得把 AI 變成必要依賴。

正式產品：

- 不要求 LLM。
- 不要求 API key。
- 不要求 Internet。
- 不要求 cloud account。
- 不要求 telemetry。
- External AI / Agent Proposal 仍然只是 optional advisory input。

原則：

> **AI advises. Deterministic tooling validates. Human decides.**

## 1.3 v1.0.0 的 Fail-closed 行為不可倒退

例如：

- malformed frontmatter 不得被當成 ordinary no-properties。
- duplicate key ambiguity 不得被靜默消失。
- ambiguous note target 不得被自動猜測。
- Fill Preview 無效時 Copy 必須 disabled。
- Export 不得 silent omission。
- Vault byte-for-byte read-only verification不得失效。

UI 改版不能用「更漂亮」交換 safety regression。

---

# 2. v1.1.0 主要設計問題

## 2.1 問題 A — 單檔 HTML 不適合真正雙語

目前 Arena B / D 主要是繁中介面，原版主要是英文介面。

如果直接在 HTML 裡同時放：

```text
盤點現況 / Discover
設計屬性 / Design Properties
填寫並複製 / Fill & Copy
```

全站文字會快速膨脹，維護困難，而且 UI 會變擁擠。

### v1.1.0 Decision

正式導入輕量 i18n。

建議檔案：

```text
app/ui/
├─ index.html
├─ styles.css
├─ app.js
├─ i18n.js
└─ locales/
   ├─ zh-Hant.json
   └─ en.json
```

不要求 React / Vue。

不要求大型 i18n framework。

可使用簡單 deterministic local i18n layer。

必須：

- 全部 locale 資源 local。
- 不使用 CDN。
- 語言偏好記錄在 localStorage。
- 切換語言後 `<html lang>` 同步更新。
- Dynamic messages 也必須走 translation keys，不得只翻 static HTML。
- 缺少 translation key 時應 fail visibly 或 fallback English，不得空白。

### UI

右上：

```text
繁中 | EN
```

或：

```text
Language
[繁體中文 ▼]
```

### Terminology Policy

下列 Obsidian / technical domain terms可保留英文，不強制硬翻：

- Vault
- Property
- YAML
- Frontmatter
- Schema
- Wikilink
- AI / Agent

其他 UI instruction / explanation 應完整翻譯。

---

# 3. v1.1.0 核心 Context Architecture

## 3.1 四層 Context Model

正式概念：

```text
1. VAULT
   Global knowledge boundary

2. SCOPE
   Current working subset of the Vault

3. NOTE
   Current individual working item

4. SCHEMA
   Property contract
```

### Vault

Vault 是完整知識邊界。

Whole-Vault scan 仍然保留，因為它提供：

- note index
- Property inventory
- Property types
- vocabulary
- relationship candidate index
- ambiguity knowledge
- global health context

### Scope

Scope 是目前工作的知識子集合。

重要：

> Scope 不等於 single folder。

Scope 定義為：

> **A set of Notes selected from the current Vault.**

v1.1.0 至少支援：

```text
Entire Vault
One Folder
Multiple Folders
Single Note
```

Folder 預設可選：

```text
Include subfolders = Yes
```

Scope 必須可以同時選多個 folder roots。

例如：

```text
Current Scope

✓ Texas-Factory/Projects/
✓ Texas-Factory/Equipment/
✓ Texas-Factory/Meetings/

Include subfolders: Yes

187 Notes
3 Folder roots
```

Scope selection 是 union：

```text
Scope Notes
=
Folder A notes
∪ Folder B notes
∪ Folder C notes
```

重複 path 必須 deduplicate。

## 3.2 Scope 不能破壞 Global Truth

設計原則：

> **Vault provides global truth; Scope provides local relevance.**

例如：

`AI/Models/` Scope 不應因 `Texas-Factory/Equipment/` 大量出現 `serial_number` 而把它視為主要 local schema reuse signal。

但是 Whole Vault 仍可用來判斷：

- 某 Wikilink 名稱是否全域重名。
- 某 Property 是否全域存在。
- 是否存在 Scope 外同名 candidate。
- Scope 裡的 local convention 是否偏離全 Vault convention。

因此 Scope 是 filtering / relevance layer，不是另一個隔離 Vault。

---

# 4. Navigation / Information Architecture

v1.0.0 的 1 → 8 線性流程需要重新整理。

因為 AI Proposal 並不是「第 8 步」，Health / Refactor 也不是每次都必須依序操作。

## 4.1 Proposed Sidebar

```text
HOME
Overview

CONTEXT
Vault
Scope

CREATE
Design
Note Properties

GOVERN
Discover
Refactor Planner
Relationships
Property Health

ADVANCED
AI Proposal Import
```

可依實作精簡，但資訊架構至少要表達：

```text
Context
Create
Govern
Advanced
```

而不是把所有模組都當成同一種 Step。

## 4.2 Persistent Context Bar

主畫面上方永久顯示：

```text
Vault      MyVault
Scope      Texas-Factory/Projects + 2
Note       Dayton Factory.md
```

如果未選：

```text
Vault      MyVault
Scope      Entire Vault
Note       —
```

每個模組都必須讓使用者明確知道目前分析範圍。

不得讓 Scope 在背景默默改變。

---

# 5. Home / Overview

v1.1.0 新增一個輕量 Overview。

## Scan 前

```text
Obsidian Property Studio

Understand, design and govern
your Obsidian Properties.

[Select Vault]

Read-only
Local only
No AI required
```

## Scan 後

```text
MyVault

1,482 Notes
26 Properties
Property Health 83 / 100

Current Scope
Texas-Factory/Projects + Equipment

Quick Actions

[Open Discover]
[Edit Note Properties]
[Analyze Relationships]
[Run Health Check]
```

Home 不應塞滿所有報表。

用途是：

- 告訴使用者現在在哪個 Vault / Scope。
- 提供「下一步去哪」。
- 提供 resumability。

---

# 6. Discover vNext

Discover 必須支援 Scope。

## 6.1 Scope Aware

例如：

```text
Discover

Scope:
Texas-Factory/
```

只計算 Scope 內：

- notes
- notes with Properties
- Property keys
- values
- type conflicts
- naming drift
- findings

但可以顯示 global context：

```text
vendor
Used in current Scope: 18 notes
Used in entire Vault: 47 notes
```

這有助於理解 local vs global convention。

## 6.2 Drill-down 用 Drawer

採用 Arena D 的右側 Drawer 概念。

點：

```text
vendor
```

右側：

```text
Property Detail

Scope usage
Observed types
Distinct values
Affected notes
Findings
```

每篇 Note 可提供：

```text
[Open in Note Properties]
```

---

# 7. Design vNext

Design 必須同時使用：

```text
User goal
+
Current Scope inventory
+
Whole-Vault global inventory
```

Local Scope 權重高於整個 Vault。

必須清楚顯示：

```text
Existing in Scope
Existing elsewhere in Vault
New Property
Possible overlap
```

Design 不得偷偷把 Scope 外 vocabulary 當作 local standard。

---

# 8. Note Properties Workspace

這是 v1.1.0 最重要的新能力之一。

## 8.1 目標

讓使用者完成：

```text
Scan Vault
↓
Select a specific Note
↓
Inspect existing Properties
↓
Edit / add Property values
↓
Validate using whole-Vault context
↓
Preview Diff
↓
Generate safe Frontmatter
↓
Copy
```

仍然：

> **不直接修改原 Note。**

## 8.2 Two Modes

```text
Note Properties

[Existing Note]   [New / Blank]
```

### New / Blank

保留 v1.0.0 Fill & Copy：

```text
Schema
→ values
→ validation
→ YAML
→ Copy
```

### Existing Note

新增：

```text
Select Note
→ load parsed existing Properties
→ choose / load Schema
→ edit
→ diff
→ validate
→ Copy updated Frontmatter
```

## 8.3 Note Selector

必須使用 Whole-Vault note index。

支援：

- search by filename
- search by relative path
- show duplicate names separately
- show current Scope priority

例如：

```text
Search Notes...

Dayton Factory
  Texas-Factory/Projects/Dayton Factory.md

Dayton Factory
  Archive/Dayton Factory.md
```

不得只用 basename 在 ambiguity 時自動猜。

## 8.4 Existing Note Safety Contract

Existing Note mode 不得：

- silently remove unrelated Properties
- silently collapse duplicate keys
- silently discard unsupported structures
- silently pretend comments / formatting are preserved

如果 frontmatter：

- malformed
- duplicate keys
- unsupported nested structure
- parser cannot safely round-trip

必須 fail-closed：

```text
Cannot safely prepare updated Properties.

Reason:
Duplicate Property key: status

[View issue]
```

### Formatting

如果目前 parser 無法保留：

- comments
- quoting style
- key ordering
- custom formatting

UI 必須誠實標示：

> Generated Frontmatter is semantically equivalent but formatting may be normalized.

更好的做法是：

- preserve unrelated semantic values
- show full semantic diff
- only claim formatting preservation if actually verified

---

# 9. Relationships vNext

Relationships 從 Whole-Vault relationship inbox 演進成 Scope-aware relationship analysis。

## 9.1 Relationship Model

```text
Source Scope
  ↓
Relationship Analysis
  ↓
Target Scope
```

Source / Target 都必須支援：

```text
Entire Vault
One Folder
Multiple Folders
Single Note (Source only required)
```

## 9.2 Ad-hoc Analysis 是預設

重要產品決策：

> v1.1.0 **不預設任何 Relationship Rule。**

使用者一開始可能不知道自己的 Vault 最後應該如何分類。

所以預設畫面應是：

```text
Analyze Relationships

Source Scope
[Select folders...]

Target Scope
[Select folders...]

Relationship Source
[Property Links ▼]

Property
[vendor ▼]

[Analyze]
```

這只是一次分析。

不會自動保存。

不會變成 governance enforcement。

## 9.3 Multi-folder Source / Target

例如：

```text
Source Scope

✓ Texas-Factory/Projects/
✓ Taiwan-Factory/Projects/

Target Scope

✓ Suppliers/
✓ Manufacturers/
```

分析：

```text
Property:
vendor
```

結果：

```text
VALID
BROKEN
AMBIGUOUS
OUTSIDE SELECTED TARGET
```

### OUTSIDE SELECTED TARGET

例如 link 本身存在：

```text
vendor: [[SEW]]
```

解析到：

```text
Company/Customers/SEW.md
```

但 Target Scope 是：

```text
Suppliers/
Manufacturers/
```

則：

```text
OUTSIDE SELECTED TARGET

Resolved:
Company/Customers/SEW.md

Selected target scope:
Suppliers/
Manufacturers/
```

不能把「link exists」直接判 PASS。

---

# 10. Property Links vs Body Wikilinks

這是 v1.1.0 需要新增的正式 Scope。

## 10.1 Property Links

例如：

```yaml
vendor: [[SEW]]
project: [[Dayton Factory]]
```

為既有核心功能。

## 10.2 Body Wikilinks

例如：

```markdown
今天討論 [[Dayton Factory]] 的設備採購。
相關法規請見 [[OSHA 1910.95]]。
```

v1.1.0 可新增：

```text
Body Wikilink Analysis
```

但安全契約必須明確：

> Body content may be read only for extracting relationship metadata such as Wikilinks.

> It may observe prose-level links, but it does not edit prose.

允許：

- read body
- extract `[[wikilink]]`
- analyze target
- report broken / ambiguous / outside selected target

禁止：

- modify body
- replace body link
- repair body link
- rewrite prose
- relink backlinks

Body Wikilinks 與 Property Links 在 UI / report 中必須分開標示。

不得混成一種結果。

---

# 11. Saved Relationship Checks

## 11.1 不使用預設 Rules

系統不得內建：

```text
Projects.vendor → Vendors/
Equipment.project → Projects/
```

之類的假設。

使用者還在探索自己的 Vault。

產品不能替使用者先發明 ontology。

## 11.2 定義

正式名稱建議：

```text
Saved Relationship Check
已儲存的關聯檢查
```

而不是：

```text
Enforced Relationship Rule
```

它的語意：

> **把一次 Ad-hoc Relationship Analysis 的設定保存起來，方便未來重跑。**

不是：

> 「不符合就是錯誤。」

## 11.3 Save Flow

使用者先做：

```text
Source:
Texas-Factory/Projects/

Target:
Suppliers/

Property:
vendor

[Analyze]
```

覺得有用後：

```text
[Save this check]
```

輸入：

```text
Name:
Texas Projects → Suppliers

Notes:
目前觀察 Project 裡的 vendor 通常是否來自 Suppliers。
Manufacturer 是否也應包含仍待觀察。
```

## 11.4 Saved Check Fields

至少：

```text
Name
Source Scope
Target Scope
Relationship Source
Property Name (if Property Link)
Include Subfolders
Notes
```

可選輕量狀態：

```text
Draft
Active
Archived
```

如果實作狀態會明顯增加複雜度，v1.1.0 可以只做：

```text
Saved
Archived
```

或完全不做 status。

## 11.5 Advisory Only

v1.1.0 的 Saved Check：

```text
matches selected target
outside selected target
broken
ambiguous
```

不得使用：

```text
VIOLATION
POLICY FAILURE
```

除非未來正式新增 enforced governance mode。

v1.1.0 不做 enforced mode。

---

# 12. Health vNext

Health 必須吃 Current Scope。

例如：

```text
Entire Vault
Health = 82

Texas-Factory/
Health = 87

AI/
Health = 96
```

Scope Health 必須只以 Scope notes 計算。

同時可提供：

```text
Compare with Whole Vault
```

但不要混算。

Health 的所有 finding 必須能：

```text
Open Note
```

進 Note Properties。

---

# 13. Refactor Planner vNext

Refactor 必須明確顯示 Scope。

例如：

```text
Rename
supplier → vendor

Scope:
Texas-Factory/

Affected in Scope:
23 notes

Also present outside Scope:
115 notes

Outside-Scope notes are NOT included in this plan.
```

這符合：

> No silent scope change.

不得因 global inventory 知道 138 notes 使用 supplier，就在使用者選 Scope 後偷偷把 138 全部納入。

---

# 14. i18n Architecture

## 14.1 Locale files

建議：

```text
locales/zh-Hant.json
locales/en.json
```

使用 hierarchical keys：

```json
{
  "nav.home": "總覽",
  "nav.discover": "盤點現況",
  "scan.complete": "已掃描 {count} 篇筆記，耗時 {seconds} 秒。",
  "relationship.outside_target": "連結存在，但位於目前選定的 Target Scope 外。"
}
```

English：

```json
{
  "nav.home": "Overview",
  "nav.discover": "Discover",
  "scan.complete": "Scanned {count} notes in {seconds} seconds.",
  "relationship.outside_target": "The link resolves, but the target is outside the selected Target Scope."
}
```

## 14.2 Backend Error Contract

長期建議：

```json
{
  "code": "NOTE_LINK_AMBIGUOUS",
  "params": {
    "name": "ACME",
    "candidate_count": 2
  }
}
```

Front-end：

```text
t(error.code, error.params)
```

而不是依賴比對 backend 英文句子再翻譯。

若 v1.1.0 不適合一次重構所有 backend messages，至少：

- 新增的 API 一律使用 machine-readable error code。
- 舊 API 保留 fallback。
- 不得因翻譯導致 error detail 消失。

---

# 15. Light / Dark Theme

採用 Arena B 已驗證的概念。

支援：

```text
System
Light
Dark
```

至少：

```text
Light
Dark
```

偏好保存：

```text
localStorage
```

Theme 必須使用 design tokens。

不可在大量 component 中 hard-code color。

---

# 16. UI Visual Direction

## 16.1 Arena D Donor

主要吸收：

- visual hierarchy
- sidebar density
- typography
- cards
- status box
- breadcrumbs
- right-side drawer
- finding presentation
- operation cards
- detail drill-down
- progress state concept

不得直接吸收：

- automatic demo fallback
- embedded mock backend as production logic
- any fake API response
- any behavior that conflicts with formal repo

## 16.2 Arena B Donor

主要吸收：

- beginner-friendly wording
- sidebar secondary descriptions
- Light / Dark
- next-action navigation
- responsive behavior
- loading skeleton
- explicit locked-state explanation
- workflow guidance

## 16.3 Formal v1.0.0 Repo

唯一功能 Source of Truth：

- API behavior
- safety contract
- deterministic logic
- fail-closed behavior
- tests
- Product Truth

### Priority

```text
Formal v1.0.0 repo
    >
v1.1.0 Design Spec
    >
Arena B / D visual donors
```

更精確：

```text
Functional truth:
Formal repo + accepted v1.1.0 requirements

Visual / interaction inspiration:
B + D
```

若 B / D 與正式 repo 衝突：

> **正式 repo / accepted v1.1.0 contract 優先。**

---

# 17. 是否需要把 Arena B / D 給 AG？

**建議：要。**

原因不是它們的 code 比規格重要，而是：

> 規格描述 interaction architecture；HTML donor 提供 visual target，降低 AG 自行重新發明第三套 UI 的機率。

目前建議 AG 可直接參考：

```text
D:\Antigravity-Workspace\Obsidian-Property-Studio\
├─ Obsidian-Property-Studio-v1.0.0\
├─ index_areaagentB.html
└─ index_areaagentD.html
```

但 AG 必須先接受：

```text
index_areaagentB.html
= UX donor only

index_areaagentD.html
= Visual / interaction donor only

Neither file is a functional authority.
```

不得直接：

```text
copy whole HTML
replace production index
```

不得把 D 的 demo/mock API 併入 production behavior。

不得把 B / D 的翻譯文字視為 backend contract。

---

# 18. Demo Mode

Arena D 的 Demo Mode 概念可保留，但 v1.1.0 不要求實作。

若實作：

不得：

```text
backend connection failed
→ automatically pretend app is working
```

必須：

```text
Local backend unavailable.

[Retry]
[Enter Demo Mode]
```

Demo 必須是 explicit user action。

UI 要永久顯示：

```text
DEMO MODE
Sample data only
```

v1.1.0 若時間有限：

> Demo Mode 可延期，不是 release blocker。

---

# 19. Loading / Empty / Error States

每個主要 module 都必須定義：

```text
Initial
Loading
Ready
Empty
Error
Blocked
```

例如 Relationship：

### Initial

```text
Select Source and Target Scope to begin.
```

### Loading

```text
Analyzing 187 source notes...
```

### Empty

```text
No relationship issues found in this Scope.
```

### Blocked

```text
Cannot analyze:
Source Scope is empty.
```

### Error

顯示：

- error code / human readable message
- retry action
- no silent failure

---

# 20. Accessibility

至少：

- keyboard reachable
- visible focus
- semantic button / form labels
- drawer keyboard close
- Esc closes Drawer
- reduced-motion support
- color 不是唯一 status signal
- aria-live for validation / toast
- current language reflected in `html lang`
- contrast 在 Light / Dark 都足夠

---

# 21. Responsive

主要目標仍是 Windows Desktop。

但是：

- 1024px 寬度不得崩版。
- narrow window 時 sidebar 可 collapse / horizontal nav。
- Drawer 在小寬度可變 full-screen panel。
- tables 可 horizontal scroll。
- primary actions 不得被截掉。

不要求 mobile-native UX。

---

# 22. Performance / Scan Model

## 22.1 不因 Scope 每次重新掃整個 Vault

理想流程：

```text
Full Vault Scan
↓
build ScanResult / indexes
↓
Scope = filtered views over current ScanResult
```

切換 Scope 不應重讀整個 Vault。

Scope 分析應優先從：

- parsed note index
- Property inventory
- note-name index
- path index
- relationship index

取得資料。

## 22.2 Scope Cache

可以做 in-memory deterministic cache。

但：

- 不寫回 Vault。
- cache invalidation 要明確。
- Re-scan Vault 後所有 Scope derived state 必須重建。

---

# 23. Backend / Domain Changes

v1.1.0 的功能不應只靠前端假裝 Scope。

後端 / domain layer 必須正式理解 Scope。

建議 domain：

```text
ScopeSpec
- mode
- roots[]
- include_subfolders
- note_paths[]
```

Relationship：

```text
RelationshipQuery
- source_scope
- target_scope
- source_type
    property_link
    body_wikilink
- property_key?
```

Note Workspace：

```text
SelectedNote
- relative_path
- parse_status
- properties
- issues
```

具體 endpoint 名稱由 AG 設計，但契約不可缺失。

可能需要的 API 概念：

```text
scope-aware discovery
scope-aware health
scope-aware refactor
scope-aware relationships
note detail
existing-note frontmatter preview
saved relationship checks
```

不得把全部 Scope filtering 只寫在 JavaScript。

---

# 24. Saved Checks Storage

Saved Relationship Checks 是 Property Studio 自己的使用者設定。

它們不得存入 Vault。

建議存放：

```text
Property Studio local app data
```

或 browser local storage / application-local config。

必須：

- 不修改 Vault。
- 可以 export / import。
- 有明確刪除。
- 不把使用者 Notes body 存進設定檔。

v1.1.0 若先採 localStorage，可接受，但資料結構必須 versioned。

---

# 25. v1.1.0 Non-goals

本版不要順便擴張成大型 Obsidian replacement。

明確不做：

- Obsidian plugin
- automatic Vault mutation
- Apply Refactor
- note creation
- note rename / move / delete
- body rewriting
- body link repair
- backlinks rewrite
- attachment management
- graph database
- semantic embeddings / RAG
- required AI
- cloud sync
- multi-user collaboration
- enforced ontology
- automatic Relationship Rules
- automatic classification of user folders
- automatic restructuring of Vault

---

# 26. v1.1.0 UX Acceptance Criteria

## I18N

- [ ] zh-Hant / English 可即時切換。
- [ ] 不需要 reload。
- [ ] locale preference 可保存。
- [ ] `<html lang>` 同步。
- [ ] Static / dynamic / error UI 均可翻譯。
- [ ] UI 不同時堆兩套完整語言。
- [ ] Offline 正常。

## Theme

- [ ] Light / Dark。
- [ ] preference 保存。
- [ ] 兩種 theme 都通過基本 contrast / readability。

## Scope

- [ ] Entire Vault。
- [ ] One Folder。
- [ ] Multiple Folders。
- [ ] Include subfolders。
- [ ] Single Note。
- [ ] Scope note count 正確。
- [ ] Folder overlap 不重複計算。
- [ ] Scope 切換不重新掃整個 Vault。
- [ ] Persistent Context Bar 永遠顯示當前 Scope。

## Discover

- [ ] Scope-aware inventory。
- [ ] Scope stats 與 Whole Vault stats 不混淆。
- [ ] Property drawer。
- [ ] Note drill-down 可 Open in Note Properties。

## Note Properties

- [ ] Existing Note 可搜尋 / 選擇。
- [ ] duplicate basename 不自動猜。
- [ ] 既有 Properties 可讀入。
- [ ] 可編輯 / 新增 value。
- [ ] semantic diff。
- [ ] unrelated Property 不可 silent loss。
- [ ] malformed / duplicate key fail-closed。
- [ ] preview invalid 時 Copy disabled。
- [ ] 不寫 Vault。

## Relationships

- [ ] Source Scope 支援 multi-folder。
- [ ] Target Scope 支援 multi-folder。
- [ ] Property Links。
- [ ] Body Wikilinks analysis-only。
- [ ] VALID。
- [ ] BROKEN。
- [ ] AMBIGUOUS。
- [ ] OUTSIDE SELECTED TARGET。
- [ ] 不自動 repair。
- [ ] 不預設任何 Relationship Rule。

## Saved Relationship Checks

- [ ] 只有使用者主動 Save 才建立。
- [ ] 可命名。
- [ ] 可寫 Notes。
- [ ] 保存 Source / Target / Link type / Property。
- [ ] 可重新執行。
- [ ] 可刪除 / archive。
- [ ] advisory only。
- [ ] 不存入 Vault。

## Health

- [ ] Scope-aware。
- [ ] drill-down to Note。
- [ ] Whole Vault / Scope 不混算。

## Refactor

- [ ] Scope 明確。
- [ ] affected in Scope。
- [ ] outside Scope count 可見。
- [ ] plan 不包含 Scope 外內容。
- [ ] no silent scope expansion。

---

# 27. Engineering Regression Gates

v1.1.0 必須保留 v1.0.0 全部既有測試。

新的 regression suite 至少加入：

```text
V11-001 i18n zh-Hant / en switch deterministic
V11-002 multi-folder Scope union / dedupe
V11-003 nested-folder include_subfolders semantics
V11-004 Scope does not rescan Vault
V11-005 Note selector duplicate-name ambiguity
V11-006 Existing Note unrelated properties preserved
V11-007 Existing Note duplicate-key fail-closed
V11-008 invalid Fill cannot Copy
V11-009 Relationship Source multi-folder
V11-010 Relationship Target multi-folder
V11-011 link exists but target outside selected Scope
V11-012 Property Link / Body Wikilink results separated
V11-013 Body Wikilink analysis never mutates body
V11-014 no default Saved Relationship Checks
V11-015 Saved Check round-trip persistence
V11-016 Scope-aware Health
V11-017 Scope-aware Refactor does not expand scope
V11-018 Vault byte-for-byte read-only after all v1.1 flows
```

---

# 28. Recommended Implementation Sequence for AG

不要一次同時大改全部功能。

建議：

```text
Phase 1
Re-entry / governance / baseline
Freeze v1.0.0 tests

Phase 2
UI shell refactor
D visual donor + B workflow donor
No new functionality yet

Phase 3
i18n + Light/Dark

Phase 4
Scope domain model
Entire Vault / multi-folder / single Note

Phase 5
Scope-aware Discover / Health / Refactor

Phase 6
Note Properties Workspace

Phase 7
Relationship Source / Target Scope
Property Links

Phase 8
Body Wikilink analysis-only

Phase 9
Saved Relationship Checks

Phase 10
Cross-module UX / Drawer / Home / Next Actions

Phase 11
Full regression / Windows native acceptance / packaging
```

每 Phase 必須可單獨驗證。

---

# 29. AG Implementation Contract

給 AG 的正式要求：

1. 先依治理順序重新進入正式 repo：
   - PROJECT.md
   - ROADMAP.md
   - AGENTS.md
   - HANDOFF.md
   - git status / log
   - existing tests

2. 不得從 Arena B / D 直接建立新的功能真相。

3. Arena B / D 僅是 donor：
   - B：workflow / Light-Dark / next actions / beginner UX
   - D：visual hierarchy / drawer / detail UI

4. v1.0.0 repo 是既有功能 Source of Truth。

5. v1.1.0 本文件是新功能 / 新 UX contract。

6. 不得破壞 read-only safety。

7. 不得把 Body Wikilink Analysis 實作成 body mutation。

8. 不得建立任何 default Saved Relationship Checks。

9. Scope 必須從 domain layer 支援，不得只做前端 filter。

10. Multi-folder Scope 是正式 requirement，不是 optional stretch goal。

11. Existing Note mode 必須 fail-closed。

12. UI Translation 必須用 i18n，不得複製整套 zh/en DOM。

13. HANDOFF 最後更新。

---

# 30. Release Semantics

建議版本：

```text
Obsidian Property Studio v1.1.0
```

定位：

> **Context-aware bilingual Property Governance Workspace**

與 v1.0.0 最大差異：

```text
v1.0.0
Whole-Vault Property Tool

v1.1.0
Vault / Scope / Note-aware Property Workspace
```

---

# 31. Human Design Rationale — 為什麼做 v1.1.0

這一版不是因為 v1.0.0 「不好用」才重做。

v1.0.0 已經完成核心安全性與 deterministic behavior。

真正原因是實際使用情境開始暴露：

### 第一層

整個 Vault 是必要 context，但不是每個工作都應該以整個 Vault 當 scope。

### 第二層

Vault 裡不同主題可能具有完全不同的 Property vocabulary。

因此需要：

```text
Scope
```

而且 Scope 必須支援 multi-folder。

### 第三層

使用者常常不是要治理整個 Vault，而只是：

> 今天我要處理這一篇 Note。

因此需要：

```text
Note Property Workspace
```

### 第四層

Relationship 不只是：

> Link 存不存在？

而是：

> 這組 Source 裡面的 link，在目前想看的 Target Scope 裡是否合理？

因此需要：

```text
Source Scope → Target Scope
```

### 第五層

使用者未必一開始就知道自己的 Vault ontology。

因此不能預設 Rules。

應先：

```text
Ad-hoc Analysis
```

用久後：

```text
Save this check
```

讓使用者自己慢慢形成可重用的分類觀察。

### 第六層

正式雙語必須從 architecture 做，而不是在 HTML 裡把中英文各寫一份。

因此：

```text
i18n
```

是 v1.1.0 正式設計要求。

---

# 32. Final Product Direction

v1.1.0 最終想達成的不是：

> 「把 Arena B / D 的 UI 搬進正式產品。」

而是：

> **在 v1.0.0 已驗證的安全核心上，建立一個更容易理解、可以真正切換語言、能在 Vault / 多資料夾 Scope / 單篇 Note 三種尺度工作，並能逐步探索與保存 Relationship 分析方式的 Property Governance Workspace。**

正式概念：

```text
Vault
  │
  ├─ Scope
  │   ├─ Entire Vault
  │   ├─ One Folder
  │   ├─ Multiple Folders
  │   └─ Single Note
  │
  ├─ Note
  │
  └─ Schema

Relationships:

Source Scope
    │
    ├─ Property Links
    └─ Body Wikilinks (analysis-only)
    │
Target Scope

Optional:
Save this analysis as a reusable Relationship Check
```

---

# 33. Final Decision on the Two Arena HTML Files

## `index_areaagentB.html`

**KEEP AND PROVIDE TO AG**

Role:

```text
UX donor
```

Use for:

- Light / Dark
- workflow guidance
- sidebar descriptions
- Next Action
- responsive states
- loading states

Do not use as functional authority.

## `index_areaagentD.html`

**KEEP AND PROVIDE TO AG**

Role:

```text
Visual / interaction donor
```

Use for:

- design system
- visual hierarchy
- right Drawer
- detailed findings UI
- breadcrumbs
- advanced information presentation

Do not copy:

- embedded mock data
- automatic demo fallback
- fake API behavior

Do not use as functional authority.

---

# 34. Recommended Folder State Before AG Starts

目前可維持：

```text
D:\Antigravity-Workspace\Obsidian-Property-Studio\
│
├─ Obsidian-Property-Studio-v1.0.0\
│   └─ formal repo
│
├─ index_areaagentB.html
│   └─ UX donor
│
└─ index_areaagentD.html
    └─ Visual / interaction donor
```

建議把本文件也放在正式 repo 或上層工作目錄，例如：

```text
UIUX_v1.1.0_DESIGN_SPEC.md
```

正式開始 v1.1.0 後，由 AG 依四文件治理決定：

- PROJECT.md：納入已接受的 v1.1.0 Product Truth / Scope。
- ROADMAP.md：建立 v1.1.0 milestones。
- HANDOFF.md：記錄當前實作狀態。
- AGENTS.md：保留固定治理規則並加入 v1.1.0 特有規則。

---

# 35. v1.1.0 Definition of Done — UI/UX Layer

只有當下列全部成立，才可宣稱 v1.1.0 UI/UX 改版完成：

```text
Existing v1.0.0 safety contract preserved
+
all existing regression tests pass
+
true zh-Hant / English i18n
+
Light / Dark
+
Vault / Scope / Note / Schema context model
+
Multi-folder Scope
+
Scope-aware Discover / Health / Refactor
+
Existing Note Property Workspace
+
Source / Target Relationship Scope
+
Property Link analysis
+
Body Wikilink analysis-only
+
no default Relationship Rules
+
user-created Saved Relationship Checks
+
cross-module navigation / Drawer / Next Action coherent
+
Vault remains byte-for-byte unchanged
+
Windows native acceptance
=
v1.1.0 UI/UX PASS
```

---

**End of v1.1.0 UI/UX vNext Design Specification**
