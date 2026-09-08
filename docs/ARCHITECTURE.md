# Architecture Notes (Developer-Facing)

> Product truth lives in `PROJECT.md`; execution history in `docs/archive/ROADMAP_v1.2.0.md`. This file explains how the v1.2.0 implementation is structured.

---

## 1. Stack Decisions

| Choice | Why |
| --- | --- |
| Python 3.10+ (tested & verified on 3.13.7 AMD64) | Available on Windows 10/11 via the `py` launcher; zero compilation steps needed. |
| PyYAML (only external runtime dependency) | Obsidian frontmatter is YAML; a hand-rolled parser would be the single biggest correctness risk. `SafeLoader` is subclassed so unsupported tags raise instead of executing arbitrary code. |
| Standard-library `http.server` + single self-contained HTML file | Real GUI in the browser with zero frontend build steps, zero CDN dependency, and zero framework churn. Runs 100% offline; loopback-bound (`127.0.0.1`) by default. |
| Standard-library JSON storage layer outside Vault | Governed app-local persistence with atomic writes, optimistic concurrency control (OCC), and automatic snapshots. |
| pytest | Comprehensive regression suite (253 tests) validating functional invariants, storage isolation, and human acceptance findings. |

---

## 2. Three State Domains

Obsidian Property Studio strictly separates state into three distinct lifecycle domains:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Vault Domain (Markdown Notes, .obsidian/)                           │
│    - STRICTLY READ-ONLY INPUT SOURCE                                   │
│    - Byte-for-byte read-only enforcement; no write code paths exist    │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (In-Memory Scan & Inventory)
┌────────────────────────────────────────────────────────────────────────┐
│ 2. App-Local Governance State Domain (Outside Vault)                  │
│    - Windows: %APPDATA%/ObsidianPropertyStudio/                        │
│    - macOS/Linux: ~/.property_studio/                                  │
│    - Preferences, User Glossary, Named Schemas, Scope Bindings, Checks │
│    - Atomic writes (os.replace), OCC (revision/etag), automatic backup │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (REST APIs over Loopback)
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Session / UI State Domain (Browser Client Memory)                  │
│    - Transient designer draft state, unadopted schema builder forms    │
│    - Single-consumption navigation context (app/ui/state_transfer.js)   │
│    - Transient filter inputs and modal dialog contexts                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Map

```text
app/
├── core/
│   ├── model.py              Canonical domain dataclasses & enums (StorageType, UIControl, etc.)
│   ├── scanner.py            Vault walk & frontmatter parsing (duplicate-key aware, symlink-safe)
│   ├── manifest.py           SHA-256 pre/post manifest generator & assert_unchanged validator
│   ├── inventory.py          Property inventory, usage counts, and value variant distribution
│   ├── design.py             Deterministic management object/need presets & recommendations
│   ├── fill.py               Form control generator & validated YAML output builder
│   ├── refactor.py           Scope-bounded planning (rename, merge, normalize, convert)
│   ├── relationships.py      Property & body Wikilink relationship analysis (4 states)
│   ├── saved_checks.py       Persistent advisory relationship checks with custom scopes
│   ├── health.py             Health scoring & explainable diagnostics aggregation
│   ├── proposal.py           External AI proposal ingestion (Contract 1.0 & 1.1 support)
│   ├── note_workspace.py     Note deep-dive, hierarchical tree, and semantic diff engine
│   ├── user_glossary.py      Personal Glossary with 3-tier precedence hierarchy
│   ├── named_schemas.py      Named Schema Library CRUD, versioning, and collision guards
│   ├── reconciliation.py     Schema-to-note 4-state reconciliation (Matches, Missing, Conflict, Preserved)
│   ├── scope_governance.py   Folder Scope → Expected Schema association persistence
│   ├── drift.py              Desired vs Actual schema drift diagnostics & exact navigation
│   ├── migration.py          Schema version diffing, breaking change detection & SemVer bumper
│   ├── governance_profile.py Portable Profile JSON export/import with concrete change-sets
│   ├── state_transfer.py     Cross-module single-consumption state transfer engine
│   └── exports.py            JSON & Markdown report generators (written outside the Vault)
├── storage/
│   ├── __init__.py           Storage module exports
│   └── local_storage.py      App-local persistence layer (OCC, backup snapshots, Vault isolation)
├── ui/
│   ├── index.html            Full application UI (inline CSS & JS, zero external network calls)
│   ├── i18n.js               Bilingual localization manager (zh-Hant & en)
│   ├── state_transfer.js     Client-side explicit navigation state transfer manager
│   └── locales/
│       ├── zh-Hant.json      Traditional Chinese translation dictionary (557 symmetric keys)
│       └── en.json           English translation dictionary (557 symmetric keys)
└── server.py                 HTTP server, routing dispatch table, and REST API handlers
```

---

## 4. Architectural Guarantees & Invariants

### 4.1 Strict Vault Read-Only Enforcement (REQ-002, REQ-051)
* **Zero Write Paths to Vault:** The selected Obsidian Vault has no writable code path in any backend handler.
* **Storage Path Isolation Assertion:** In `app/storage/local_storage.py`, `assert_outside_vault(storage_path, vault_path)` actively asserts that the storage directory is strictly not identical to, not an ancestor of, and not inside the selected Vault directory. Violations fail closed with `VaultIsolationError`.
* **Manifest Proof:** `manifest.py` computes SHA-256 manifests across all Markdown notes before and after operations to mathematically prove zero byte mutation.

### 4.2 App-Local Persistence & Concurrency Control (REQ-051)
* **Atomic File Writes:** Writes use `tempfile.NamedTemporaryFile` in the same filesystem directory followed by `os.replace` to prevent partial or corrupted file writes.
* **Optimistic Concurrency Control (OCC):** Stored entities include integer `revision` and SHA-256 `etag` fields. Updates verify incoming revisions against storage state, raising `ConcurrencyError` on version drift.
* **Automatic Backups:** Destructive mutations automatically create timestamped snapshots under `backups/` before applying modifications.

### 4.3 Legacy State Migration Boundary (v1.1.0 → v1.2.0)
* Prior to v1.2.0, preferences and saved relationship checks were saved in browser `localStorage`.
* In v1.2.0, `/api/storage/migrate_legacy` migrates legacy items to app-local files outside the Vault.
* Migration is idempotent, validates data before writing, returns read-back proof, and retains `localStorage` as fallback if payload validation fails.

### 4.4 Untrusted Input & Fail-Closed Behavior (REQ-017)
* **YAML Safety:** `DuplicateKeyLoader` extends `yaml.SafeLoader` and rejects custom Python execution tags. Duplicate keys in note frontmatter fail closed and are categorized as ambiguity.
* **Path Traversal Guards:** All note and scope paths are resolved and validated to prevent path traversal outside the active Vault.
* **HTML Sanitization:** User-derived and note-derived strings are escaped in the UI (`esc()`) to prevent XSS injection.

---

## 5. Complete REST API Surface

The backend exposes the following `POST` endpoints on loopback (`127.0.0.1`):

| Endpoint | Handler | Purpose |
|---|---|---|
| `/api/meta` | `api_meta` | App metadata, supported types, UI controls, and preset recipes |
| `/api/runtime/context` | `api_runtime_context` | In-memory scan and active scope authority report (HA-F22) |
| `/api/scan` | `api_scan` | Scan Obsidian Vault and build property inventory |
| `/api/discovery` | `api_discovery` | Discovery report with usage counts and malformed note listings |
| `/api/property` | `api_property_detail` | Detailed property usage, types, and top observed values |
| `/api/design/presets` | `api_design_presets` | Retrieve management object and management need preset options |
| `/api/design/suggest` | `api_design_suggest` | Generate suggested property schema with rationale |
| `/api/design/build` | `api_design_build` | Build custom schema definition from designer selections |
| `/api/design/review` | `api_design_review` | Review schema against current vault property inventory |
| `/api/fill/preview` | `api_fill_preview` | Generate validated YAML frontmatter from schema form values |
| `/api/workspace/notes` | `api_workspace_candidates` | Search and filter notes for Note Workspace |
| `/api/workspace/inspect` | `api_workspace_inspect` | Inspect single note frontmatter, semantic diff, and reconciliation |
| `/api/workspace/preview` | `api_workspace_preview` | Compute live semantic diff and updated frontmatter preview |
| `/api/refactor/plan` | `api_refactor_plan` | Generate planning-only refactor impact analysis (rename/merge/normalize) |
| `/api/relationships` | `api_relationships` | Property-layer link analysis between source and target scopes |
| `/api/relationships/body` | `api_relationships_body` | Read-only Markdown body Wikilink analysis (4 states) |
| `/api/relationships/saved/list` | `api_saved_checks_list` | List persistent Saved Relationship Checks from app-local storage |
| `/api/relationships/saved/save` | `api_saved_checks_save` | Create or update a Saved Relationship Check in app-local storage |
| `/api/relationships/saved/delete`| `api_saved_checks_delete` | Delete a Saved Relationship Check from app-local storage |
| `/api/relationships/saved/execute`| `api_saved_checks_execute`| Execute a Saved Relationship Check with its saved scope parameters |
| `/api/health` | `api_health` | Calculate scope-aware health metrics and explainable findings |
| `/api/proposal/import` | `api_proposal_import` | Ingest and validate external AI schema proposal (Contract 1.0 & 1.1) |
| `/api/proposal/validate` | `api_proposal_import` | Alias for proposal validation |
| `/api/export` | `api_export` | Export reports (JSON/Markdown) to user-specified external directory |
| `/api/vault/verify` | `api_vault_verify` | Re-verify that Vault files remain byte-for-byte untouched |
| `/api/verify_untouched` | `api_vault_verify` | Alias for vault verification |
| `/api/scope/folders` | `api_scope_folders` | List subfolders in vault for scope configuration |
| `/api/scope/set` | `api_scope_set` | Update active analysis Scope without disk rescan |
| `/api/scope/apply` | `api_scope_set` | Alias for scope update |
| `/api/scope/current` | `api_scope_current` | Query current active Scope settings |
| `/api/scope/schema/assign` | `api_scope_schema_assign` | Assign expected Named Schema to a folder scope |
| `/api/scope/schema/current` | `api_scope_schema_current`| Query expected Named Schema for active Scope |
| `/api/scope/schema/unassign` | `api_scope_schema_unassign` | Remove schema assignment from a folder scope |
| `/api/drift/analyze` | `api_drift_analyze` | Analyze Desired vs Actual schema drift in active scope |
| `/api/note_candidates` | `api_note_candidates` | Retrieve candidate note paths for note-link autocompletion |
| `/api/notes/candidates` | `api_note_candidates` | Alias for note candidates |
| `/api/glossary` | `api_glossary_catalog` | Retrieve merged Personal Property Glossary catalog |
| `/api/glossary/catalog` | `api_glossary_catalog` | Authoritative catalog endpoint |
| `/api/glossary/property` | `api_glossary_property` | Query single property glossary metadata and observed facts |
| `/api/glossary/user/list` | `api_glossary_user_list` | List user-customized glossary overrides |
| `/api/glossary/user/save` | `api_glossary_user_save` | Save custom glossary override to app-local storage |
| `/api/glossary/user/delete` | `api_glossary_user_delete` | Remove custom glossary override |
| `/api/schemas/list` | `api_schemas_list` | List all schemas from Named Schema Library |
| `/api/schemas/get` | `api_schemas_get` | Retrieve specific Named Schema by ID |
| `/api/schemas/create` | `api_schemas_create` | Create new Named Schema with SemVer tracking |
| `/api/schemas/update` | `api_schemas_update` | Update existing Named Schema or create new version |
| `/api/schemas/delete` | `api_schemas_delete` | Delete Named Schema from library |
| `/api/schemas/migration/plan` | `api_schema_migration_plan` | Generate step-by-step schema migration impact plan |
| `/api/governance/profile/export` | `api_governance_profile_export` | Export portable Governance Profile JSON with checksum |
| `/api/governance/profile/validate`| `api_governance_profile_validate` | Validate Governance Profile JSON and precompute change-sets |
| `/api/governance/profile/import` | `api_governance_profile_import` | Confirm import of Governance Profile in merge or replace mode |
| `/api/profile/validate` | `api_governance_profile_validate` | Alias for profile validation |
| `/api/profile/export` | `api_governance_profile_export` | Alias for profile export |
| `/api/profile/import` | `api_governance_profile_import` | Alias for profile import |
| `/api/reconcile/inspect` | `api_reconcile_inspect` | Calculate 4-state property reconciliation against a note |
| `/api/reconcile/preview` | `api_reconcile_preview` | Generate updated frontmatter preview from reconciliation |
| `/api/state/validate_context` | `api_state_validate_context` | Validate cross-module state transfer payload |
| `/api/storage/migrate_legacy` | `api_storage_migrate_legacy` | Migrate v1.1 localStorage items to app-local JSON storage |
| `/api/preferences/get` | `api_preferences_get` | Retrieve app-local preferences (locale, theme) |
| `/api/preferences/set` | `api_preferences_set` | Save app-local preferences (locale, theme) |

There is intentionally **no** endpoint that accepts instructions to write, edit, or delete files inside the Vault.

---

## 6. Testing Strategy

The test suite consists of **253 automated tests** organized across focused test families:

* `tests/test_v11_vault_readonly.py`: Vault byte-for-byte read-only proof across all analysis workflows.
* `tests/test_consistency_gate.py`: Cross-module consistency gate (Scan → Inventory → Design → Health → Export).
* `tests/test_benchmark.py`: Authoritative 5,000-note performance benchmark.
* `tests/test_windows10_acceptance.py`: Windows 10 native launcher, live server socket, and HTTP walkthrough.
* `tests/test_v12_human_acceptance_repairs.py`: 31 regression tests verifying all 16 recorded human findings (HA-F01 ~ HA-F23 closures).
* `tests/test_v12_storage_closure.py`: OCC concurrency, atomic rollback, path containment, and legacy migration invariants.
* `tests/test_v12_state_transfer.py`: Cross-module navigation context transfer and fail-closed validation.
* `tests/test_v12_glossary.py`: User glossary precedence (`Built-in → Override → Vault Facts`) and immutable keys.
* `tests/test_v12_named_schemas.py`: Named schema CRUD, version collision protection, and version sorting.
* `tests/test_v12_reconciliation.py`: 4-state property reconciliation and non-schema property preservation.
* `tests/test_v12_scope_governance.py`: Scope expected schema association and persistence.
* `tests/test_v12_drift.py`: Desired vs Actual schema drift diagnostics.
* `tests/test_v12_proposal_workflow.py`: Proposal Contract 1.0 & 1.1 validation and review workspace actions.
* `tests/test_v12_migration.py`: Breaking change detection and SemVer recommendation engine.
* `tests/test_v12_governance_profile.py`: Governance profile round-trip export/import, validation, and rollback.
* `tests/test_v12_health_drilldown.py`: Health finding to Note Workspace drilldown with preserved context.
* `tests/test_v12_ui_workflow.py`: Production UI workflow coverage.
