# Property Health Report

- Vault: `D:\Antigravity-Workspace\Obsidian-Property-Studio\Obsidian-Property-Studio-v1.0.0\fixtures\vaults\main_vault`
- Health score: **49.5 / 100**
- Findings: 19

## How the score is calculated

`score = max(0, 100 - sum over categories of min(category_cap, weight_per_finding * finding_count)). Weights and caps are listed in 'score_breakdown'. Informational categories have weight 0.`

| Category | Findings | Weight each | Raw | Cap | Applied |
| --- | ---: | ---: | ---: | ---: | ---: |
| ambiguous_property | 1 | 6.0 | 6.0 | 15.0 | 6.0 |
| ambiguous_relationship | 1 | 1.5 | 1.5 | 8.0 | 1.5 |
| broken_relationship | 1 | 2.0 | 2.0 | 10.0 | 2.0 |
| link_upgrade_opportunity | 3 | 0.0 | 0.0 | 0.0 | 0.0 |
| naming_drift | 1 | 4.0 | 4.0 | 15.0 | 4.0 |
| parse_failure | 3 | 8.0 | 24.0 | 25.0 | 24.0 |
| possible_semantic_overlap | 4 | 0.0 | 0.0 | 0.0 | 0.0 |
| type_conflict | 1 | 5.0 | 5.0 | 20.0 | 5.0 |
| value_drift | 4 | 2.0 | 8.0 | 10.0 | 8.0 |

## Findings

### [HIGH] 'status' is defined more than once in the same note

- Category: `ambiguous_property` (confidence: exact)
- Properties: `status`
- Affected notes (1): `Notes/Duplicate Key.md`
- Why: Duplicate YAML keys have no single defined value. The product refuses to guess which one is correct.
- Suggested next step: Open the listed notes and keep exactly one definition of this property.

### [MEDIUM] 'Duplicate Name' could mean 2 different notes

- Category: `ambiguous_relationship` (confidence: ambiguous)
- Properties: `project`
- Affected notes (1): `Inbox/Ambiguous Target.md`
- Why: Several notes share this name. Property Studio will not choose one for you.
- Suggested next step: Pick the intended note, or use a full path link.

### [HIGH] Link 'Missing Person' points to no existing note

- Category: `broken_relationship` (confidence: unresolved)
- Properties: `attendees`
- Affected notes (1): `Meetings/2026-01-05 Kickoff.md`
- Why: This property links to a note that does not exist in this vault.
- Suggested next step: Create the note, fix the spelling, or clear the value.

### [INFO] 'Apollo' exactly matches the note Projects/Apollo.md

- Category: `link_upgrade_opportunity` (confidence: exact)
- Properties: `project`
- Affected notes (1): `Equipment/Microscope.md`
- Why: This plain text value names an existing note. Turning it into a link makes the relationship visible in Obsidian's graph and backlinks.
- Suggested next step: Review and, if correct, copy the proposed link value.

### [INFO] 'Apollo' exactly matches the note Projects/Apollo.md

- Category: `link_upgrade_opportunity` (confidence: exact)
- Properties: `project`
- Affected notes (1): `Meetings/CRLF Note.md`
- Why: This plain text value names an existing note. Turning it into a link makes the relationship visible in Obsidian's graph and backlinks.
- Suggested next step: Review and, if correct, copy the proposed link value.

### [INFO] 'Ada Lovelace' exactly matches the note People/Ada Lovelace.md

- Category: `link_upgrade_opportunity` (confidence: exact)
- Properties: `owner`
- Affected notes (1): `Projects/Borealis.md`
- Why: This plain text value names an existing note. Turning it into a link makes the relationship visible in Obsidian's graph and backlinks.
- Suggested next step: Review and, if correct, copy the proposed link value.

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

### [LOW] 'owner' refers to the same target in 2 different ways

- Category: `value_drift` (confidence: exact)
- Properties: `owner`
- Affected notes (2): `Projects/Apollo.md`, `Projects/Borealis.md`
- Why: Mixing plain text and links (or different spellings) for the same target splits the relationship.
- Suggested next step: Standardise on one form using the Refactor Planner.

### [LOW] 'project' refers to the same target in 2 different ways

- Category: `value_drift` (confidence: exact)
- Properties: `project`
- Affected notes (4): `Equipment/Microscope.md`, `Equipment/Oscilloscope.md`, `Meetings/2026-01-05 Kickoff.md`, `Meetings/CRLF Note.md`
- Why: Mixing plain text and links (or different spellings) for the same target splits the relationship.
- Suggested next step: Standardise on one form using the Refactor Planner.

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

