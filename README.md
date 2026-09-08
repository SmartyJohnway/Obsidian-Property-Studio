# Obsidian Property Studio

[English](README.md) | [繁體中文](README.zh-TW.md)

**Understand, design, fill and govern Obsidian Properties — without learning YAML.**

Version 1.2.0 · Standalone Local-first · Read-only · **Your Vault is never modified**

---

## What It Does

Obsidian's Properties turn a collection of Markdown notes into a structured knowledge base that you can filter, group, and query. **Obsidian Property Studio** is a standalone local application that runs 100% on your machine to help you understand, design, and govern your note properties with human-readable semantics and strict read-only safety guarantees:

| Module | What you get |
| --- | --- |
| **1 · Vault & Scope** | Select a vault folder and define an active Scope (**Entire Vault**, **One Folder**, **Multiple Folders**, or **Single Note**). Switching scopes requires zero disk rescans. Pre/post SHA-256 manifests prove your vault remains completely untouched. |
| **2 · Discover** | Real-time property inventory computed within your active Scope, compared against whole-vault counts. Inspect property storage types, usage counts, value variants, and malformed frontmatter in the contextual Right Drawer. |
| **3 · Schema Designer** | Design structured frontmatter using deterministic multi-select presets for **Management Objects** (e.g., Projects, Persons, Books) and **Management Needs** (e.g., Progress Tracking, Relationships), with optional free-text context. Suggestions explain why properties are recommended, allow selective retain/exclude, and offer an **Adopt Schema** action that routes directly to Note Workspace, New Frontmatter, or the Named Schema Library. |
| **4 · Note Workspace** | Deep-dive into individual notes via **Search** or the **Hierarchical Folder Tree** (with Expand/Collapse All and no arbitrary 100-note limits). Disambiguates duplicate note basenames by relative path. Reconcile existing notes against adopted schemas across 4 states (`Matches`, `Missing`, `Conflict`, `Outside-Schema Preserved`), edit properties with real-time **Semantic Diff**, complex YAML preservation, and copy-only YAML output. Fails closed on corrupt frontmatter or duplicate YAML keys. |
| **5 · New Frontmatter** | Dynamic form control generation based on the adopted schema. Configure properties with live YAML preview, validation, and copy-only output. Never creates files in your vault. |
| **6 · Refactor Planner** | Scope-bounded planning for **Rename**, **Merge**, **Normalize Values**, and **Convert Types**. Features controlled property dropdowns, target collision warnings, and a **Scope Observed Values Mapping Table** for controlled normalization. Renders a structured human-readable plan summary by default. Planning-only with **zero apply** capability. |
| **7 · Relationships** | Multi-folder Source Scope to Multi-folder Target Scope analysis. Evaluates **Property Links** and read-only **Body Wikilinks** (`[[Wikilinks]]`) across four deterministic states: `VALID`, `BROKEN`, `AMBIGUOUS`, and `OUTSIDE SELECTED TARGET`. |
| **8 · Saved Checks** | User-initiated, advisory relationship queries with custom notes and scopes. Persisted safely in app-local governance storage outside the Vault with zero pre-populated assumptions or default ontology rules. |
| **9 · Property Health** | Scope-aware health scoring and explainable findings (missing properties, type drift, ambiguous links, desired vs actual schema drift). Jump directly from findings to affected notes in the Note Workspace with preserved context. |
| **10 · Personal Glossary** | Custom bilingual labels, guidance hints, descriptions, and categories for property keys. Follows a clean 3-tier precedence hierarchy: `System Built-in → User Override → Vault Observed Facts`. Canonical YAML keys remain strictly immutable. |
| **11 · Named Schema Library** | Save, version (`v1.0`, `v1.1`, `v2.0`), and organize reusable frontmatter schemas outside your Vault with collision protection and optimistic concurrency control (OCC). |
| **12 · Scope Governance & Drift** | Associate folder scopes with expected Named Schemas. Property Health reports Desired vs Actual compliance rates, missing required properties, and unexpected properties. |
| **13 · Migration Planner** | Compare schema versions, detect breaking changes, determine recommended SemVer bump levels (major/minor/patch), and generate step-by-step migration plans (strictly planning-only). |
| **14 · Governance Profile** | Export and import complete portable governance packages (Named Schemas, Scope assignments, Glossary overrides, Saved Checks, and preferences) with SHA-256 integrity verification and concrete per-entity change-set preview. |
| **15 · AI Proposal Review** | Human-in-the-loop review workspace for external AI schema proposals (Proposal Contract 1.0 & 1.1). Inspect, validate, compare against your vault, edit, save as Named Schema, or reject. Core application requires no AI. |
| **16 · Companion AI Skill** | Independent, decoupled `obsidian-property-advisor` skill packaged for local agent environments with zero runtime dependency on the core application. |

---

## Where Your Data Lives

Obsidian Property Studio enforces a strict architectural boundary between your notes and governance metadata:

```text
1. Selected Obsidian Vault (Markdown files, .obsidian/)
   └── STRICTLY READ-ONLY INPUT. Never modified, created, renamed, or deleted.

2. App-Local Governance Storage (Outside the Vault)
   ├── Windows: %APPDATA%\ObsidianPropertyStudio\
   └── macOS / Linux: ~/.property_studio/
       ├── config/preferences.json                   (UI locale, theme)
       ├── glossary/user_glossary.json               (Personal Glossary overrides)
       ├── schemas/named_schemas.json                 (Named Schema Library)
       ├── scope_profiles/scope_expected_schemas.json (Scope assignments)
       ├── saved_checks/saved_relationship_checks.json (Saved relationship queries)
       └── backups/                                  (Automatic OCC snapshots)

3. Session & Transient State (Browser Memory)
   └── Transient Designer state, active filter inputs, and unadopted draft schemas.

4. Export & Clipboard Artifacts
   └── User-controlled clipboard copies, reports exported to user-chosen directories,
       and portable Governance Profile JSON. Never silently written into your Vault.
```

See [Architecture Specification: App-Local Governance Storage](docs/specs/v1.2.0_App_Local_Governance_Storage.md) for full concurrency and storage details.

---

## Practical First-Run Workflow

Obsidian Property Studio is designed for real-world, routine PKM governance:

1. **Launch App:** Run `run_windows.bat` or `python -m app`.
2. **Select & Scan Vault:** Point to your local Obsidian Vault folder. The initial scan builds an in-memory inventory without altering any files.
3. **Review Property Inventory (Discover):** Inspect your active properties, observed values, types, and malformed frontmatter.
4. **Set Active Scope:** Focus on an active project folder (e.g. `Projects/` or `Literature/`) to scope your analysis.
5. **Customize Personal Glossary:** Define human-friendly labels, categories, and descriptions for properties you care about.
6. **Create or Save Named Schema:** Design a schema in the Designer or adopt one into the **Named Schema Library** with version tracking.
7. **Assign Expected Schema to Scope:** Bind the Named Schema to your active folder scope.
8. **Inspect Health & Schema Drift:** Review the Health tab to see compliance rates and drift diagnostics.
9. **Reconcile Notes in Workspace:** Drill down into specific notes to compare actual frontmatter against expected schemas, inspect semantic diffs, and copy validated YAML frontmatter.
10. **Export Governance Profile:** Periodically export your Governance Profile JSON as a portable backup of your schemas, scopes, glossary, and saved checks.

---

## Human-Readable Property Vocabulary Layer

Obsidian Property Studio v1.2.0 features a dedicated **Property Vocabulary Layer** designed for human-centric Personal Knowledge Management (PKM):

* **Bilingual Presentation Badges:** Front-end presentation displays human-friendly labels alongside canonical keys:
  * Traditional Chinese UI: `狀態 (status)`, `負責人 (owner)`, `截止日期 (due_date)`
  * English UI: `Status (status)`, `Owner (owner)`, `Due Date (due_date)`
* **Canonical YAML Key Safety:** Canonical property keys (`status`, `owner`, etc.) remain strictly immutable and are never translated in output YAML.
* **Safe Custom Property Fallback:** Unrecognized or user-created custom properties safely display their observed keys without semantic guessing.
* **Universal ⓘ Guidance Drawer:** Clicking the `ⓘ` button beside any property badge opens a contextual Help Drawer showing:
  * Purpose & Usage Hints
  * Typical Storage Types & Input Controls
  * Standard Example Values
  * Current Scope Usage & Whole-Vault Frequency
  * Top Observed Values in your vault

---

## Safety Guarantees (v1.2.0)

* **Strictly Read-Only:** No note is created, edited, renamed, moved, or deleted. Markdown note bodies and the `.obsidian/` configuration folder are never touched.
* **No "Apply to Vault" Mechanism:** Refactor and reconciliation operations are strictly preview and copy-only. There is no vault-mutation code path in the backend, enforced by automated regression suites.
* **100% Local & Offline:** No external network requests, no telemetry, no cloud dependency, no account registration, and no API keys required.
* **No Required AI:** Every analysis, schema recommendation, and health check executes deterministically via local Python algorithms.
* **Fail-Closed on Ambiguity:** Ambiguous property names, duplicate frontmatter keys, and ambiguous note links fail closed with clear warnings and never guess intent.
* **External Artifact Storage:** Reports and exports are saved to user-designated external directories or app-local storage outside the Vault.

---

## Backup & Portability Guidance

* **Vault Backups:** Because Obsidian Property Studio is strictly read-only, it will never modify your Vault. However, you should always maintain your independent Vault backup strategy (e.g. Git, Obsidian Sync, external drive).
* **Governance Profile Backup:** The **Governance Profile** (`Export Governance Profile`) exports your Named Schemas, Scope assignments, Glossary overrides, Saved Checks, and preferences into a single portable JSON file with SHA-256 integrity verification.
* **Note Content Distinction:** A Governance Profile backs up your *governance rules and configurations*, not your Markdown note contents.

---

## System Requirements & Platform Verification

* Python **3.10 or newer** (tested and verified on Python 3.13.7 AMD64)
* Core runtime dependency: **PyYAML**
* Any modern web browser (Google Chrome, Microsoft Edge, Firefox)

### Platform Verification Status
* **Windows 10 (Build 19045+, 64-bit AMD64):** `PASS — Human Verified` (Full native browser walkthrough, server socket acceptance, and all 16 recorded human findings verified).
* **Windows 11 (64-bit AMD64):** Supported target platform. Native execution verification has not yet been executed due to test host availability (accepted non-blocking release limitation).
* **macOS / Linux:** Expected to run through the Python entry point (`run.sh` / `python3 -m app`). Native release acceptance for v1.2.0 was performed on Windows 10.

---

## Installation & Launch

Obsidian Property Studio is a standalone Python local web application. It is not an Obsidian plugin, requires no build steps, and does not require an installer.

### Windows 10 & 11

```bat
:: 1. Install dependencies from the project root:
py -m pip install -r requirements.txt

:: 2. Launch the application (starts local server and opens your browser):
run_windows.bat
```

Manual commands:

```bat
py -m app                      :: Launches at http://127.0.0.1:8765
py -m app --port 9000          :: Use a custom port
py -m app --no-browser         :: Headless mode (manual browser open)
```

### macOS / Linux

```bash
python3 -m pip install -r requirements.txt
./run.sh                       # or: python3 -m app
```

The server binds strictly to `127.0.0.1` (loopback only). To stop the app, press `Ctrl+C` in the terminal.

---

## Upgrading from v1.1.0

When launching v1.2.0 for the first time, any legacy preferences and Saved Relationship Checks stored in browser `localStorage` from v1.1.0 are automatically and idempotently migrated to app-local JSON storage outside your Vault. Legacy data is verified before saving and retained in `localStorage` until the backend confirms validated readback.

---

## Documentation Links

* [Architecture Notes](docs/ARCHITECTURE.md)
* [Known Limitations](docs/LIMITATIONS.md)
* [External AI Proposal Contract](docs/PROPOSAL_CONTRACT.md)
* [v1.2.0 Release Notes](docs/releases/v1.2.0-release-notes.md)
* [Obsidian Property Advisor Skill](skills/obsidian-property-advisor/SKILL.md)

---

## License

MIT License.
