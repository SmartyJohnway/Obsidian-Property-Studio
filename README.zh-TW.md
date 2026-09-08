# Obsidian Property Studio

[English](README.md) | **繁體中文**

**無需學習 YAML，輕鬆理解、設計、填寫與治理你的 Obsidian 屬性（Properties）。**

版本 1.2.0 · 獨立本機優先 · 唯讀安全 · **絕不修改你的 Vault 知識庫**

---

## 它可以做什麼

Obsidian 的 Properties（屬性）能將零散的 Markdown 筆記轉變為可篩選、分組與查詢的結構化知識庫。**Obsidian Property Studio** 是一套 100% 在您本機運行的獨立應用程式，協助您在嚴格的唯讀安全保護下，以人類易讀的語意理解、設計與治理筆記屬性：

| 模組 | 提供功能 |
| --- | --- |
| **1 · 知識庫與範圍 (Vault & Scope)** | 選擇知識庫資料夾並定義分析範圍（**整個知識庫**、**單一資料夾**、**多資料夾**或**單篇筆記**）。切換範圍無需重新掃描硬碟。提供掃描前後 SHA-256 雜湊比對，證明知識庫完全未被變動。 |
| **2 · 屬性探索 (Discover)** | 即時計算當前 Scope 範圍內的屬性庫存清單，並與全庫總數對照。可在右側抽屜（Drawer）深入檢視屬性儲存型態、使用次數、值變體以及格式損毀的 Frontmatter。 |
| **3 · 屬性架構設計 (Schema Designer)** | 提供結構化的**「管理對象」**（如專案、人物、書籍）與**「管理需求」**（如進度追蹤、關聯對象）確定性預設複選清單，搭配選填之自由文字說明。系統產生具備解釋理由的建議屬性清單，支援個別勾選/排除，並提供**「採用此屬性架構 (Adopt Schema)」**動作直接引導至筆記工作區、新增 Frontmatter 或儲存至具名架構庫。 |
| **4 · 單篇筆記屬性工作區 (Note Workspace)** | 支援**即時路徑搜尋**與**全庫階層式資料夾樹目錄**（支援展開/收合全部，無 100 筆上限）。依完整相對路徑消歧義同名筆記。支援針對採用架構進行四態核對（`相符`、`缺漏`、`衝突`、`保留非架構屬性`），具備即時**語意差異比對 (Semantic Diff)**、複合 YAML 原樣保留與唯複製 YAML 輸出。遇損毀或重複 YAML 鍵名嚴格安全中斷 (Fail-Closed)。 |
| **5 · 新增 Frontmatter (New Frontmatter)** | 依據已採用的架構動態生成輸入表單。即時預覽 YAML 內容、完成格式驗證與複製。絕不在知識庫中自動建立檔案。 |
| **6 · 安全重構規劃 (Refactor Planner)** | 嚴格受限於 Scope 範圍的**重新命名 (Rename)**、**合併屬性 (Merge)**、**數值正規化 (Normalize Values)** 與**型態轉換 (Convert Types)** 規劃。提供受控屬性下拉選單、目標名稱衝突警告，以及**「Scope 觀察值受控對照表」**。預設呈現結構化易讀摘要，純規劃性質，**絕無寫入功能**。 |
| **7 · 筆記關聯分析 (Relationships)** | 多資料夾來源範圍（Source Scope）至多資料夾目標範圍（Target Scope）關聯分析。精確區分**屬性連結 (Property Links)** 與唯讀**正文雙向連結 (Body `[[Wikilinks]]`)**，分類為四種確定性狀態：`VALID`（有效）、`BROKEN`（失效）、`AMBIGUOUS`（歧義）與 `OUTSIDE SELECTED TARGET`（目標範圍外）。 |
| **8 · 常用關聯檢查 (Saved Checks)** | 使用者主動儲存的自訂關聯分析條件（自訂名稱、備註、範圍與屬性）。安全持久化於 Vault 外部的應用程式本機儲存空間，系統不預設任何強加的知識本體規則。 |
| **9 · 屬性健康檢查 (Property Health)** | 基於當前 Scope 範圍計算可解釋的健康指標與問題清單（缺失必要屬性、型態漂移、無效或歧義連結、預期 vs 實際架構漂移），並可一鍵攜帶情境鑽取至單篇筆記工作區。 |
| **10 · 個人詞彙庫 (Personal Glossary)** | 自訂屬性顯示標籤、指引提示、描述與分類。遵循「`系統內建 → 使用者覆寫 → 知識庫觀察事實`」三層清晰優先權，底層 YAML 鍵名嚴格維持不可變。 |
| **11 · 具名架構庫 (Named Schema Library)** | 儲存、管理與版本化（`v1.0`, `v1.1`, `v2.0`）自訂 Frontmatter 架構規範，持久化於 Vault 外部並具備衝突防護與 OCC 並發控制。 |
| **12 · 範圍治理與架構漂移 (Scope Drift)** | 將資料夾範圍綁定至預期具名架構，健康診斷即時呈現期望 vs 實際符合率、缺漏屬性與非預期屬性。 |
| **13 · 架構遷移規劃 (Migration Planner)** | 比對架構版本差異，自動識別破壞性變更，建議語意化版號（Major/Minor/Patch）並提供逐步遷移指引（純規劃、絕不自動套用）。 |
| **14 · 治理設定檔匯出匯入 (Governance Profile)** | 一鍵打包匯出具名架構、範圍指派、個人詞彙庫、常用檢查與喜好設定，具備 SHA-256 數位簽章校驗與實體變更清單預覽。 |
| **15 · AI 提案審查 (AI Proposal Review)** | 支援外部 AI 架構提案（Proposal Contract 1.0 & 1.1）之完整審查工作區。可檢驗、與庫存比對、編輯、儲存為具名架構或拒絕。核心應用程式無需任何 AI。 |
| **16 · 獨立 AI 伴隨技能 (Companion Skill)** | 於 `skills/obsidian-property-advisor/` 打包專屬 Companion Skill，供本機 Agent 環境使用，與核心應用程式零執行期耦合。 |

---

## 你的資料存放在哪裡 (Where Your Data Lives)

Obsidian Property Studio 在知識庫筆記與治理中繼資料之間建立了嚴格的架構隔離邊界：

```text
1. 選擇的 Obsidian Vault (Markdown 筆記文件, .obsidian/)
   └── 嚴格唯讀輸入來源 (STRICTLY READ-ONLY)。絕不建立、修改、重命名或刪除。

2. 應用程式本機治理儲存空間 (位於 Vault 外部)
   ├── Windows: %APPDATA%\ObsidianPropertyStudio\
   └── macOS / Linux: ~/.property_studio/
       ├── config/preferences.json                   (介面語言、主題)
       ├── glossary/user_glossary.json               (個人詞彙庫自訂覆寫)
       ├── schemas/named_schemas.json                 (具名架構庫定義)
       ├── scope_profiles/scope_expected_schemas.json (範圍預期架構指派)
       ├── saved_checks/saved_relationship_checks.json (常用關聯檢查條件)
       └── backups/                                  (OCC 自動備份快照)

3. 工作階段與暫存狀態 (瀏覽器記憶體)
   └── 設計工具中的暫時狀態、即時過濾輸入以及尚未儲存的草稿架構。

4. 匯出與剪貼簿產物
   └── 由使用者主動點擊複製的剪貼簿內容、手動匯出至指定目錄的報告，
       以及可攜式的治理設定檔 JSON。絕不會在未經同意下寫入 Vault。
```

詳細並發控制與儲存實作規範請參閱 [架構規範文件：應用程式本機治理儲存 (App-Local Governance Storage)](docs/specs/v1.2.0_App_Local_Governance_Storage.md)。

---

## 實用的首次上手流程 (Practical First-Run Workflow)

Obsidian Property Studio 專為日常與定期的個人知識治理流程設計：

1. **啟動應用程式：** 執行 `run_windows.bat` 或 `python -m app`。
2. **選擇並掃描知識庫：** 指向您的本機 Obsidian 知識庫目錄。初次掃描會在記憶體中建置屬性庫存，完全不變更任何硬碟檔案。
3. **檢視屬性庫存 (Discover)：** 探索既有屬性鍵名、觀察數值、型態以及損毀的 Frontmatter。
4. **設定分析範圍 (Scope)：** 聚焦於特定進行中的專案資料夾（如 `Projects/` 或 `Literature/`）。
5. **自訂個人詞彙庫 (Personal Glossary)：** 為您在乎的屬性鍵名設定親切的繁中標籤、分類與說明指引。
6. **建立或儲存具名架構 (Named Schema)：** 於 Schema Designer 設計架構，或採用並儲存至**具名架構庫**，賦予版本號。
7. **指派預期架構至範圍：** 將具名架構綁定為該專案資料夾的預期標準。
8. **檢視健康指標與架構漂移 (Health & Drift)：** 檢視健康分頁，掌握筆記與預期架構的相符率與漂移項目。
9. **於筆記工作區調和屬性 (Reconcile)：** 鑽取進入特定筆記，對照實際 Frontmatter 與預期架構的四態差異，檢視語意 Diff，並一鍵複製校驗後的 YAML。
10. **定期匯出治理設定檔 (Governance Profile)：** 定期將包含架構、範圍、詞彙庫與檢查條件的 Governance Profile 匯出為可攜式 JSON 備份。

---

## 屬性易讀詞彙層 (Property Vocabulary Layer)

Obsidian Property Studio v1.2.0 提供專為個人知識管理（PKM）設計的**「屬性易讀詞彙層」**：

* **雙語展示標籤：** 前端展示層以對人類友善的標籤搭配原始鍵名呈現：
  * 繁體中文介面：`狀態 (status)`、`負責人 (owner)`、`截止日期 (due_date)`
  * 英文介面：`Status (status)`、`Owner (owner)`、`Due Date (due_date)`
* **Canonical YAML 鍵名安全性：** 底層原始屬性鍵名（`status`、`owner` 等）維持不可變，輸出的 YAML 絕不進行翻譯。
* **自訂屬性安全降級：** 面對未預先收錄的自訂屬性，系統絕不臆測語意，僅忠實呈現觀察到的鍵名與庫存數據事實。
* **通用 ⓘ 引導抽屜 (Help Drawer)：** 點擊任何屬性標籤旁的 `ⓘ` 按鈕即可開啟情境抽屜，查看：
  * 屬性用途說明與使用建議
  * 典型儲存型態與建議輸入元件
  * 標準範例值
  * 當前 Scope 使用次數與全庫出現頻率
  * 知識庫中觀察到的前幾名常見實際數值

---

## 安全保證 (v1.2.0)

* **嚴格唯讀 (Strictly Read-Only)：** 絕不建立、修改、重命名、移動或刪除任何筆記。筆記 Markdown 正文與 `.obsidian/` 設定資料夾永遠不受侵擾。
* **絕無「套用至知識庫」按鈕：** 所有重構與調和均為規劃與預覽性質。後端核心完全無任何修改硬碟筆記的程式碼路徑，並經自動化測試嚴格守護。
* **100% 本機離線運作：** 無任何對外網路連線、無遙測追蹤 (Telemetry)、無雲端依賴、無需註冊帳號，亦無需 API 金鑰。
* **無需任何 AI 即可完整運作：** 所有分析、架構建議與健康檢查皆由本機 Python 演算法以確定性方式執行。
* **歧義安全中斷 (Fail-Closed on Ambiguity)：** 遇歧義屬性名稱、重複 YAML 鍵名或歧義同名筆記連結時，系統一律安全中斷並給予清晰警告，絕不自行猜測意圖。
* **外部成果儲存：** 報告匯出皆儲存至使用者指定的外部目錄或 Vault 外部的應用程式本機儲存空間，絕不寫入 Vault。

---

## 備份與可攜性指引 (Backup Guidance)

* **Vault 筆記備份：** 由於 Obsidian Property Studio 嚴格唯讀，絕不會更動您的筆記。但您仍應保有原有的知識庫備份習慣（如 Git、Obsidian Sync 或外接硬碟）。
* **治理設定檔備份：** 透過**治理設定檔匯出**（`Export Governance Profile`），可將具名架構、範圍綁定、個人詞彙庫覆寫、常用檢查與介面設定完整導出為單一 JSON 檔案，附帶 SHA-256 雜湊驗證。
* **筆記內容邊界：** 治理設定檔僅備份您的*屬性規範與治理規則*，**絕不**備份也不包含您的 Markdown 筆記正文內容。

---

## 系統需求與平台驗證狀態

* Python **3.10 或更新版本**（已於 Python 3.13.7 AMD64 測試驗證）
* 核心執行期相依套件：**PyYAML**
* 任何現代網頁瀏覽器（Google Chrome、Microsoft Edge、Firefox 等）

### 平台驗證狀態
* **Windows 10 (Build 19045+, 64 位元 AMD64)：** `PASS — Human Verified`（完成完整本機瀏覽器操作、本機 Socket 通訊與全部 16 項記錄之人工驗收回報項目的正式驗收）。
* **Windows 11 (64 位元 AMD64)：** 正式支援之目標平台。實機驗證因缺乏測試主機目前標記為尚未執行（依合約核准之非阻礙發布限制）。
* **macOS / Linux：** 預期可直接透過 Python 進入點執行（`run.sh` / `python3 -m app`）；本 v1.2.0 發布之原生驗收主要於 Windows 10 執行。

---

## 安裝與啟動說明

Obsidian Property Studio 是一套獨立的 Python 本機 Web 應用程式。它不是 Obsidian 外掛，無需前端建置，亦無需安裝檔。

### Windows 10 & 11

```bat
:: 1. 於專案根目錄安裝相依套件：
py -m pip install -r requirements.txt

:: 2. 啟動應用程式（啟動本機伺服器並自動開啟瀏覽器）：
run_windows.bat
```

手動命令：

```bat
py -m app                      :: 於 http://127.0.0.1:8765 啟動
py -m app --port 9000          :: 自訂通訊埠
py -m app --no-browser         :: 無介面模式（手動開啟瀏覽器）
```

### macOS / Linux

```bash
python3 -m pip install -r requirements.txt
./run.sh                       # 或: python3 -m app
```

伺服器嚴格僅綁定本機環回介面 `127.0.0.1` (loopback only)。若要停止程式，請於終端機按下 `Ctrl+C`。

---

## 從 v1.1.0 升級

首次啟動 v1.2.0 時，系統會自動將 v1.1.0 中儲存在瀏覽器 `localStorage` 的介面喜好設定與常用關聯檢查條件，以等冪（Idempotent）方式安全遷移至 Vault 外部的應用程式本機 JSON 儲存空間。所有資料在寫入前皆經過格式驗證，並在後端確認讀回前完整保留於 `localStorage` 中。

---

## 相關說明文件

* [架構說明 (Architecture Notes)](docs/ARCHITECTURE.md)
* [已知限制 (Known Limitations)](docs/LIMITATIONS.md)
* [外部 AI 提案合約 (AI Proposal Contract)](docs/PROPOSAL_CONTRACT.md)
* [v1.2.0 發行說明 (Release Notes)](docs/releases/v1.2.0-release-notes.md)
* [Obsidian Property Advisor 伴隨技能](skills/obsidian-property-advisor/SKILL.md)

---

## 授權條款

MIT License.
