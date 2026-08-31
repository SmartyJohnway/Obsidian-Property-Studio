# Obsidian Property Studio

**Understand, design, fill and govern Obsidian Properties — without learning YAML.**

Version 1.0.0 · Local-first · Windows 11 target · **Your vault is never modified**

---

## What it does

Obsidian's Properties turn a pile of Markdown files into something you can filter, group and
relate. Property Studio is a small application that runs on your own machine and helps you:

| Step | What you get |
| --- | --- |
| **1 · Vault** | Point at a vault folder. Everything is read-only; a SHA-256 manifest lets you prove it. |
| **2 · Discover** | Every property key in your vault, how often it is used, how it is stored, what values exist, and what is drifting. Click any finding to see the exact notes. |
| **3 · Design** | Say *“I want to manage my lab equipment and know where each item is”*. You get a set of properties with plain-language explanations, checked against what your vault already uses. |
| **4 · Fill & Copy** | A form built from your schema. It generates valid frontmatter, proves it parses back to what you saw, and copies it for pasting into Obsidian. |
| **5 · Refactor plan** | Rename / merge / normalize / change type / make fields required — as an **analysis**, showing affected notes, conflicts and everything needing a human decision. |
| **6 · Relationships** | Property values that name other notes: exact link candidates, ambiguous names (never auto-picked), and links pointing nowhere. |
| **7 · Health** | One explainable score with every deduction itemised, plus every finding drilled down to the notes it came from. |
| **8 · AI proposal** | Optional. Import a versioned schema proposal JSON produced by an external agent; it is validated and compared with your real vault, never applied to it. |

## Safety guarantees (v1)

* **Read-only.** No note is created, edited, renamed, moved or deleted. `.obsidian/` is never touched.
* **No “Apply to vault” button exists.** Refactoring is planning only — there is no vault-write code
  path in the product, and the test suite enforces that.
* **Nothing leaves your machine.** No network calls, no telemetry, no account, no API key.
* **No AI required.** Every feature works offline with zero configuration.
* **Nothing is guessed.** Ambiguous property names, duplicate YAML keys and ambiguous note links are
  reported as ambiguous — the app will not pick a winner for you.
* **Reports never land in your vault.** Exports go to `%USERPROFILE%\.obsidian-property-studio\exports`
  (or a folder you choose outside the vault); writing inside the vault is refused.

## Requirements

* Python **3.10 or newer** (developed and verified on 3.13)
* One dependency: **PyYAML**
* Any modern browser (the UI runs at `http://localhost:8765`)

## Install & run — Windows 11

```bat
:: 1. get the code, then from the project folder:
py -m pip install -r requirements.txt

:: 2. start it (also opens your browser)
run_windows.bat
```

`run_windows.bat` simply runs `py -m app`. Equivalent manual command:

```bat
py -m app                      :: http://localhost:8765
py -m app --port 9000          :: different port
py -m app --no-browser         :: don't open a browser
```

macOS / Linux:

```bash
python3 -m pip install -r requirements.txt
./run.sh                       # or: python3 -m app
```

The server binds to `127.0.0.1` (your machine only). `--host` exists for advanced users; changing it
exposes the app to your network and is not recommended.

Stop the app with `Ctrl+C` in the console window.

## A five-minute tour

1. **Vault** — paste the full path of your vault (in Explorer: click the address bar, `Ctrl+C`) and
   press *Scan vault*. You'll see note counts, how many notes have properties, and — separately —
   how many notes have frontmatter that **could not be read**. Those are never silently counted as
   “no properties”.
2. Press **Verify vault untouched** at any time: every file is re-hashed and compared with the
   moment you scanned.
3. **Discover** — read the inventory table. Click a row to see the value distribution and the notes.
   Findings explain drift, type conflicts and duplicate keys, each with a *what you can do* line.
4. **Design** — type a goal, tick what you want to be able to do, press *Propose properties*.
   Edit anything: name, stored type, input style, required, allowed values, explanation.
   If your vault already uses a property, the editor says so and offers to reuse it as-is.
5. **Fill & Copy** — fill in the form, read the YAML preview, press *Copy frontmatter*, then paste
   it at the very top of a note in Obsidian. The app verifies the YAML parses back to exactly the
   values you saw before it lets you trust it.
6. **Refactor plan** → **Relationships** → **Health** as needed; each screen can export a JSON +
   Markdown artifact you can keep or hand to someone else.

## Storage types vs input styles

Obsidian stores properties as: Text, List, Number, Checkbox, Date, Date & time, Tags.
Property Studio never invents a storage type. Convenience *input styles* map onto them transparently:

| Input style | Stored as | Serialised as |
| --- | --- | --- |
| `plain` | any | the underlying type, unchanged |
| `single_choice` | text / number / date / datetime | a single scalar (select is a schema constraint, not an Obsidian type) |
| `multi_choice` | list / tags | a YAML list of scalars |
| `note_link` | text | `"[[Note Name]]"` inside a text property |
| `note_link_list` | list | a list of `"[[Note Name]]"` text values |

## What it deliberately does **not** do

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md). Short version: no Obsidian plugin, no note-body or
template generation, no automatic migration, no attachment management, no note merging, no Dataview
or Bases replacement, no required LLM.

## For developers

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/build_fixtures.py     # regenerate synthetic fixture vaults + oracle
python3 -m pytest -q                  # full suite (includes the 5,000-note benchmark)
python3 -m pytest -q -m "not benchmark"
```

Layout:

```
app/core/      canonical vault/property/schema logic (one interpretation, REQ-004)
app/server.py  stdlib HTTP server + JSON API
app/ui/        single-file browser UI (no CDN, no external assets)
tests/         OPS-AC acceptance suite, HTTP end-to-end, benchmark
fixtures/      synthetic vaults + expectation oracle + proposal samples
evidence/      verification artifacts referenced by ROADMAP.md
docs/          proposal contract, limitations, architecture notes
```

Governance for this repository lives in `PROJECT.md`, `ROADMAP.md`, `HANDOFF.md`, `AGENTS.md`.

## License / status

Internal v1 release candidate. See `ROADMAP.md` for the formal release status and evidence.
