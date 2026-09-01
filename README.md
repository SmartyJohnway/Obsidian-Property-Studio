# Obsidian Property Studio

**Understand, design, fill and govern Obsidian Properties — without learning YAML.**

Version 1.1.0 · Local-first · Windows 10 & 11 supported · **Your vault is never modified**

---

## What it does

Obsidian's Properties turn a pile of Markdown files into something you can filter, group and
relate. Property Studio is a local application that runs on your own machine and helps you:

| Module | What you get |
| --- | --- |
| **1 · Vault & Scope** | Point at a vault folder and choose your Scope (Entire Vault, One Folder, Multi-Folder, Single Note). Everything is strictly read-only; a SHA-256 manifest lets you prove it. |
| **2 · Discover** | Property inventory computed strictly within your active Scope, compared against global counts. Click any finding to inspect exact notes and values in the Right Drawer. |
| **3 · Design** | Describe a goal in natural language. Get suggested properties with plain-language explanations, checked against existing vault properties. |
| **4 · Note Workspace** | Inspect and edit properties of existing notes with real-time semantic diff and fail-closed corrupt/duplicate-key frontmatter protection, or generate new blank frontmatter. |
| **5 · Scope Refactor** | Rename / merge / normalize / change type / make fields required — as an **analysis bounded by Scope**, disclosing in-scope vs out-of-scope counts with no silent expansion. |
| **6 · Relationships** | Multi-folder Source Scope and Target Scope analysis. Categorizes Property Links and Body Wikilinks (`[[Links]]`) into Valid, Broken, Ambiguous, and `OUTSIDE SELECTED TARGET`. |
| **7 · Saved Checks** | User-initiated, advisory relationship checks with custom notes and Scopes, stored entirely outside the Vault with zero pre-populated assumptions. |
| **8 · Health** | Explainable property health score and actionable findings calculated exclusively from Scope notes without cross-contamination. |
| **9 · AI proposal** | Optional. Import a versioned schema proposal JSON produced by an external agent; validated and compared with your real vault, never applied to it. |

## Safety guarantees (v1.1.0)

* **Strictly Read-only.** No note is created, edited, renamed, moved or deleted. Note bodies and `.obsidian/` are never touched.
* **No “Apply to vault” button exists.** Refactoring is planning only — there is no vault-write code path in the product, enforced by automated tests.
* **Nothing leaves your machine.** No outbound network calls, no telemetry, no cloud dependency, no account, no API keys.
* **No AI required.** Every feature operates 100% offline with deterministic algorithms.
* **Fail-Closed Ambiguity.** Ambiguous property names, duplicate YAML keys, and ambiguous note links fail closed with clear warnings and never auto-guess.
* **Reports and Checks never touch your vault.** Exports go to `%USERPROFILE%\.obsidian-property-studio\exports` (or a chosen external folder). Saved Checks persist outside the Vault.

## Requirements

* Python **3.10 or newer** (tested and verified on Python 3.13.7)
* One dependency: **PyYAML**
* Any modern browser (runs locally at `http://127.0.0.1:8765`)

## Install & run — Windows 10 & 11

```bat
:: 1. Install dependencies from the project folder:
py -m pip install -r requirements.txt

:: 2. Launch the application (starts local server and opens your browser):
run_windows.bat
```

Equivalent manual command:

```bat
py -m app                      :: http://127.0.0.1:8765
py -m app --port 9000          :: custom port
py -m app --no-browser         :: headless / manual browser open
```

macOS / Linux:

```bash
python3 -m pip install -r requirements.txt
./run.sh                       # or: python3 -m app
```

The server binds strictly to `127.0.0.1` (loopback only).

Stop the app with `Ctrl+C` in the terminal window.

## New in v1.1.0

1. **Lightweight Bilingual Engine (zh-Hant / English):** Seamless live UI translation toggle with local storage persistence and no CDN scripts.
2. **Light / Dark Theme Engine:** Modern high-contrast dark and light themes with token-based CSS variables.
3. **Formal Scope Domain Model:** Focus analysis on specific folders, nested subfolders, or single notes without disk rescans.
4. **Note Properties Workspace:** Deep-dive into existing notes, edit properties with instant semantic diffs, copy verified YAML, and fail-closed on corrupt frontmatter.
5. **Body Wikilink Analysis:** Strict read-only discovery of Markdown body `[[Wikilinks]]`, strictly separated from Property Links.
6. **User Saved Relationship Checks:** Name, annotate, save, reload, and execute relationship queries stored safely outside the Vault.
7. **Scope-Aware Refactor Planner:** Migration planning strictly respects Scope boundaries, preventing silent whole-vault changes while disclosing out-of-scope counts.
