# Property Relationship Inbox

- Items: 7
- Scope: property values only (no note body links are analysed or changed)
- Automatically resolved by the app: 0

- ambiguous_link: 1
- broken_link: 1
- link_upgrade_candidate: 3
- relationship_drift: 2

## Items

### [MEDIUM] 'Duplicate Name' could mean 2 different notes

- Kind: `ambiguous_link` (confidence: ambiguous)
- Note: `Inbox/Ambiguous Target.md` — property `project`
- Current value: `[[Duplicate Name]]`
- Candidates: `A/Duplicate Name.md`, `B/Duplicate Name.md`
- Proposed value: — (none proposed)
- Why: Several notes share this name. Property Studio will not choose one for you.
- What to do: Pick the intended note, or use a full path link.

### [HIGH] Link 'Missing Person' points to no existing note

- Kind: `broken_link` (confidence: unresolved)
- Note: `Meetings/2026-01-05 Kickoff.md` — property `attendees`
- Current value: `[[Missing Person]]`
- Candidates: —
- Proposed value: — (none proposed)
- Why: This property links to a note that does not exist in this vault.
- What to do: Create the note, fix the spelling, or clear the value.

### [LOW] 'Apollo' exactly matches the note Projects/Apollo.md

- Kind: `link_upgrade_candidate` (confidence: exact)
- Note: `Equipment/Microscope.md` — property `project`
- Current value: `Apollo`
- Candidates: `Projects/Apollo.md`
- Proposed value: `[[Apollo]]`
- Why: This plain text value names an existing note. Turning it into a link makes the relationship visible in Obsidian's graph and backlinks.
- What to do: Review and, if correct, copy the proposed link value.

### [LOW] 'Apollo' exactly matches the note Projects/Apollo.md

- Kind: `link_upgrade_candidate` (confidence: exact)
- Note: `Meetings/CRLF Note.md` — property `project`
- Current value: `Apollo`
- Candidates: `Projects/Apollo.md`
- Proposed value: `[[Apollo]]`
- Why: This plain text value names an existing note. Turning it into a link makes the relationship visible in Obsidian's graph and backlinks.
- What to do: Review and, if correct, copy the proposed link value.

### [LOW] 'Ada Lovelace' exactly matches the note People/Ada Lovelace.md

- Kind: `link_upgrade_candidate` (confidence: exact)
- Note: `Projects/Borealis.md` — property `owner`
- Current value: `Ada Lovelace`
- Candidates: `People/Ada Lovelace.md`
- Proposed value: `[[Ada Lovelace]]`
- Why: This plain text value names an existing note. Turning it into a link makes the relationship visible in Obsidian's graph and backlinks.
- What to do: Review and, if correct, copy the proposed link value.

### [LOW] 'owner' refers to the same target in 2 different ways

- Kind: `relationship_drift` (confidence: exact)
- Note: `Projects/Apollo.md` — property `owner`
- Current value: `Ada Lovelace, [[Ada Lovelace]]`
- Candidates: `Projects/Apollo.md`, `Projects/Borealis.md`
- Proposed value: — (none proposed)
- Why: Mixing plain text and links (or different spellings) for the same target splits the relationship.
- What to do: Standardise on one form using the Refactor Planner.

### [LOW] 'project' refers to the same target in 2 different ways

- Kind: `relationship_drift` (confidence: exact)
- Note: `Equipment/Microscope.md` — property `project`
- Current value: `Apollo, [[Apollo]]`
- Candidates: `Equipment/Microscope.md`, `Equipment/Oscilloscope.md`, `Meetings/2026-01-05 Kickoff.md`, `Meetings/CRLF Note.md`
- Proposed value: — (none proposed)
- Why: Mixing plain text and links (or different spellings) for the same target splits the relationship.
- What to do: Standardise on one form using the Refactor Planner.

