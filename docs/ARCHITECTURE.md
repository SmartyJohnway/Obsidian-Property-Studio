# Architecture notes (developer-facing)

> Product truth lives in `PROJECT.md`; progress/status in `ROADMAP.md`. This file only explains how
> the implementation is put together.

## Stack decision

| Choice | Why |
| --- | --- |
| Python 3.10+ (verified 3.13.14) | Available on Windows 11 via the `py` launcher; no compiler needed. |
| PyYAML (only runtime dependency) | Obsidian frontmatter is YAML; a hand-rolled parser would be the single biggest correctness risk. `SafeLoader` is subclassed so unsupported tags raise instead of executing anything. |
| Standard-library `http.server` + a single self-contained HTML file | Real GUI in the browser with zero frontend build step, zero CDN, zero framework churn. Runs offline; loopback-bound by default. |
| pytest | Acceptance suite mirrors the ROADMAP OPS-AC cases 1:1. |

Rejected: Electron/Tauri (heavy install, native toolchain), Flask/FastAPI (extra dependencies for a
handful of JSON endpoints), a CLI-only tool (violates REQ-001).

## Module map

```
app/core/model.py         canonical types: StorageType, UIControl, ParseStatus, Note, VaultScan,
                          PropertyValue, Schema/SchemaProperty, Finding, Severity, Confidence
app/core/scanner.py       vault walk + honest frontmatter parsing (duplicate-key aware,
                          symlink-safe, CRLF/BOM/Unicode aware)
app/core/manifest.py      SHA-256 vault manifest + diff (read-only proof)
app/core/inventory.py     inventory, usage counts, value distributions, drift/conflict findings
app/core/design.py        deterministic beginner recipes/intents + existing-property reuse checks
app/core/fill.py          schema -> values -> YAML + round-trip verification
app/core/refactor.py      rename / merge / normalize / type-conversion / required-impact PLANS
app/core/relationships.py property-layer relationship inbox
app/core/health.py        findings aggregation + transparent score
app/core/proposal.py      external proposal validation + vault comparison
app/core/exports.py       JSON + Markdown artifacts, written outside the vault, read back
app/server.py             JSON API + static UI serving
app/ui/index.html         the entire UI (inline CSS/JS, no external requests)
```

### One canonical interpretation (REQ-004)

`scanner.scan_vault()` produces a `VaultScan`. **Every** other module takes that object (or the
`Inventory` derived from it) as input. No module opens a note or parses YAML on its own, so the
Discover screen, a migration plan, the health report and an export can never disagree about what a
property means.

### Determinism (SC-12)

* Notes are sorted by relative POSIX path; skipped paths, findings, plan rows and value groups all
  sort by stable keys.
* Filesystem enumeration order never leaks into output (`os.walk` results are sorted).
* Canonical payloads contain no timestamps; `scan_seconds` is the only wall-clock value and is
  excluded from determinism comparisons.
* Tie-breaks (e.g. the canonical value of a normalization group) are `(-count, value)` — frequency
  first, then lexicographic.

### Read-only enforcement (REQ-002)

* No module except `exports.py` opens a file for writing; a test asserts this by scanning the source.
* `exports.ensure_output_dir()` refuses any path inside the selected vault.
* `manifest.py` provides pre/post hashing used by tests *and* by the in-app
  “Verify vault untouched” button.

### Untrusted input (REQ-017)

* `DuplicateKeyLoader` extends `yaml.SafeLoader`; the catch-all constructor raises on any unknown
  tag, so `!!python/...` payloads fail as invalid YAML instead of executing.
* Symlinks/junctions are not followed, and every note path is verified to resolve inside the vault.
* All vault-derived strings are HTML-escaped in the UI (`esc()` is applied to every interpolation).
* Imported proposals are schema-validated before anything is displayed or used.

## API surface

`POST` JSON endpoints: `/api/meta`, `/api/scan`, `/api/discovery`, `/api/property`,
`/api/design/suggest`, `/api/design/build`, `/api/design/review`, `/api/fill/preview`,
`/api/notes/candidates`, `/api/refactor/plan`, `/api/relationships`, `/api/health`,
`/api/proposal/import`, `/api/export`, `/api/vault/verify`.

There is intentionally **no** endpoint that accepts vault-write instructions.

## Testing strategy

* `tests/test_ops_acceptance.py` — one test (or a small group) per ROADMAP acceptance case,
  named `test_ops_ac_0NN_*`, checked against `fixtures/vaults/oracle.json`, which is generated from
  a declarative fixture spec rather than from product output.
* `tests/test_server_api.py` — the same workflows over real HTTP, plus vault-integrity verification.
* `tests/test_benchmark.py` — 5,000+ note synthetic vault; asserts functional correctness and records
  timings as evidence without inventing a threshold.
* `scripts/collect_evidence.py` — regenerates the artifacts under `evidence/`.
