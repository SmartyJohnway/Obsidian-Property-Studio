# Property Discovery Report

- Vault: `D:\Antigravity-Workspace\Obsidian-Property-Studio\Obsidian-Property-Studio-v1.0.0\fixtures\vaults\main_vault`
- Notes scanned: 22
- Notes with properties: 17
- Notes without properties: 2
- Notes whose properties could NOT be read: 3
- Unique property keys: 15

## Property inventory

| Property | Notes using it | Types observed | Distinct values |
| --- | ---: | --- | ---: |
| `type` | 16 | text (16) | 5 |
| `status` | 9 | text (9) | 6 |
| `project` | 6 | text (6) | 4 |
| `due_date` | 3 | date (2), text (1) | 3 |
| `owner` | 3 | text (3) | 3 |
| `date` | 2 | date (2) | 2 |
| `location` | 2 | text (2) | 2 |
| `project_name` | 2 | text (2) | 2 |
| `purchase_date` | 2 | date (2) | 2 |
| `serial_number` | 2 | text (2) | 2 |
| `tags` | 2 | tags (2) | 3 |
| `attendees` | 1 | list (1) | 2 |
| `contact` | 1 | unsupported (1) | 0 |
| `priority` | 1 | text (1) | 1 |
| `Project` | 1 | text (1) | 1 |

## Findings

### [HIGH] 'status' is defined more than once in the same note

- Category: `ambiguous_property` (confidence: exact)
- Properties: `status`
- Affected notes (1): `Notes/Duplicate Key.md`
- Why: Duplicate YAML keys have no single defined value. The product refuses to guess which one is correct.
- Suggested next step: Open the listed notes and keep exactly one definition of this property.

### [MEDIUM] Case drift: project, Project

- Category: `naming_drift` (confidence: exact)
- Properties: `project`, `Project`
- Affected notes (7): `Archive/Merged Candidate.md`, `Equipment/Microscope.md`, `Equipment/Oscilloscope.md`, `Inbox/Ambiguous Target.md`, `Meetings/2026-01-05 Kickoff.md`, `Meetings/CRLF Note.md`, `Projects/Cascade.md`
- Why: These property keys are the same word written differently, so Obsidian treats them as separate properties and filtering/grouping splits across them.
- Suggested next step: Consider standardising on 'project' (most used: 6 notes) via the Refactor Planner. Nothing is changed automatically.

### [HIGH] 1 note(s) with unreadable properties (invalid_yaml)

- Category: `parse_failure` (confidence: exact)
- Properties: —
- Affected notes (1): `Notes/Malformed.md`
- Why: These notes could not be parsed. They are NOT counted as notes without properties — their property layer is unknown.
- Suggested next step: Fix the frontmatter in Obsidian, then rescan.

### [HIGH] 1 note(s) with unreadable properties (not_a_mapping)

- Category: `parse_failure` (confidence: exact)
- Properties: —
- Affected notes (1): `Notes/Not A Mapping.md`
- Why: These notes could not be parsed. They are NOT counted as notes without properties — their property layer is unknown.
- Suggested next step: Fix the frontmatter in Obsidian, then rescan.

### [HIGH] 1 note(s) with unreadable properties (unterminated_frontmatter)

- Category: `parse_failure` (confidence: exact)
- Properties: —
- Affected notes (1): `Notes/Unterminated.md`
- Why: These notes could not be parsed. They are NOT counted as notes without properties — their property layer is unknown.
- Suggested next step: Fix the frontmatter in Obsidian, then rescan.

### [LOW] Possible overlap: 'Project' and 'project_name'

- Category: `possible_semantic_overlap` (confidence: possible)
- Properties: `Project`, `project_name`
- Affected notes (3): `Archive/Merged Candidate.md`, `Archive/Old Project.md`, `Projects/Cascade.md`
- Why: These two property names look related, but the product cannot prove they mean the same thing. This is a possibility for you to judge, not a confirmed duplicate.
- Suggested next step: Review both properties' values. Merge only if you decide they mean the same thing.

### [LOW] Possible overlap: 'date' and 'due_date'

- Category: `possible_semantic_overlap` (confidence: possible)
- Properties: `date`, `due_date`
- Affected notes (5): `Meetings/2026-01-05 Kickoff.md`, `Meetings/CRLF Note.md`, `Projects/Apollo.md`, `Projects/Borealis.md`, `Projects/Cascade.md`
- Why: These two property names look related, but the product cannot prove they mean the same thing. This is a possibility for you to judge, not a confirmed duplicate.
- Suggested next step: Review both properties' values. Merge only if you decide they mean the same thing.

### [LOW] Possible overlap: 'date' and 'purchase_date'

- Category: `possible_semantic_overlap` (confidence: possible)
- Properties: `date`, `purchase_date`
- Affected notes (4): `Equipment/Microscope.md`, `Equipment/Oscilloscope.md`, `Meetings/2026-01-05 Kickoff.md`, `Meetings/CRLF Note.md`
- Why: These two property names look related, but the product cannot prove they mean the same thing. This is a possibility for you to judge, not a confirmed duplicate.
- Suggested next step: Review both properties' values. Merge only if you decide they mean the same thing.

### [LOW] Possible overlap: 'project' and 'project_name'

- Category: `possible_semantic_overlap` (confidence: possible)
- Properties: `project`, `project_name`
- Affected notes (7): `Archive/Merged Candidate.md`, `Archive/Old Project.md`, `Equipment/Microscope.md`, `Equipment/Oscilloscope.md`, `Inbox/Ambiguous Target.md`, `Meetings/2026-01-05 Kickoff.md`, `Meetings/CRLF Note.md`
- Why: These two property names look related, but the product cannot prove they mean the same thing. This is a possibility for you to judge, not a confirmed duplicate.
- Suggested next step: Review both properties' values. Merge only if you decide they mean the same thing.

### [HIGH] 'due_date' is stored as date and text in different notes

- Category: `type_conflict` (confidence: exact)
- Properties: `due_date`
- Affected notes (3): `Projects/Apollo.md`, `Projects/Borealis.md`, `Projects/Cascade.md`
- Why: Obsidian expects one property type per property. Mixed shapes break sorting, filtering and Bases/Dataview style queries.
- Suggested next step: Decide the intended type and use the Refactor Planner's type conversion feasibility check before changing anything.

### [LOW] 'location' uses inconsistent spellings of 'Lab', 'lab'

- Category: `value_drift` (confidence: exact)
- Properties: `location`
- Affected notes (2): `Equipment/Microscope.md`, `Equipment/Oscilloscope.md`
- Why: The same value is written with different capitalisation or spacing, so it appears as several different values when you filter or group.
- Suggested next step: Normalize to 'Lab' with the Refactor Planner (planning only — the vault is not modified).

### [LOW] 'status' uses inconsistent spellings of 'active', 'ACTIVE', 'Active'

- Category: `value_drift` (confidence: exact)
- Properties: `status`
- Affected notes (5): `People/Ada Lovelace.md`, `People/林小明.md`, `Projects/Apollo.md`, `Projects/Borealis.md`, `Projects/Cascade.md`
- Why: The same value is written with different capitalisation or spacing, so it appears as several different values when you filter or group.
- Suggested next step: Normalize to 'active' with the Refactor Planner (planning only — the vault is not modified).

## Parse issues

- `Notes/Duplicate Key.md` — **ok**: Property 'status' is defined more than once in this note's frontmatter; its effective value is ambiguous. This note is excluded from automated recommendations that depend on that property (fail-closed).
- `Notes/Malformed.md` — **invalid_yaml**: Frontmatter is not valid YAML, so its properties cannot be read. while scanning a quoted scalar   in "<unicode string>", line 1, column 8:     title: "unclosed            ^ found unexpected end of stream   in "<unicode string>", line 2, column 16:     status: [broken                    ^
- `Notes/Nested Structure.md` — **ok**: Property 'contact' contains a nested structure that Obsidian's property editor cannot represent. Reported as 'unsupported structure'; value left untouched.
- `Notes/Not A Mapping.md` — **not_a_mapping**: Frontmatter is valid YAML but is not a list of properties (found list). Obsidian expects 'key: value' pairs at the top level.
- `Notes/Unterminated.md` — **unterminated_frontmatter**: Frontmatter starts with '---' but never closes. Obsidian will not read properties from this note. No closing '---' delimiter was found.

## Skipped paths

- `.obsidian` — excluded folder ('.obsidian')
- `.trash` — excluded folder ('.trash')
