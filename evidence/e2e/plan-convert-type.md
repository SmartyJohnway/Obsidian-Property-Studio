# Migration plan — convert_property_type

> Planning only. Obsidian Property Studio v1 never modifies your vault. Use this plan to make the changes yourself in Obsidian.

## Summary

- values_examined: 6
- convertible: 4
- ambiguous: 1
- unresolved: 1
- already_target_type: 0
- excluded_ambiguous: 0
- feasible_without_manual_work: False

## Convertible values (4)

- `Equipment/Microscope.md` — value: Apollo — proposed_value: [[Apollo]] — detail: Matches note 'Projects/Apollo.md'. — current_type: text
- `Equipment/Oscilloscope.md` — value: [[Apollo]] — proposed_value: [[Apollo]] — detail: Matches note 'Projects/Apollo.md'. — current_type: text
- `Meetings/2026-01-05 Kickoff.md` — value: [[Apollo]] — proposed_value: [[Apollo]] — detail: Matches note 'Projects/Apollo.md'. — current_type: text
- `Meetings/CRLF Note.md` — value: Apollo — proposed_value: [[Apollo]] — detail: Matches note 'Projects/Apollo.md'. — current_type: text

## Ambiguous — manual decision required (1)

- `Inbox/Ambiguous Target.md` — value: [[Duplicate Name]] — proposed_value:  — detail: Matches 2 notes: A/Duplicate Name.md, B/Duplicate Name.md. — current_type: text

## Unresolved — cannot be converted (1)

- `Archive/Merged Candidate.md` — value: Apollo Legacy — proposed_value:  — detail: No note named 'Apollo Legacy' exists. — current_type: text

## Excluded (ambiguous duplicate keys) (0)

_None._

## Notes whose frontmatter could not be read (3)

- `Notes/Malformed.md` — reason: invalid_yaml
- `Notes/Not A Mapping.md` — reason: not_a_mapping
- `Notes/Unterminated.md` — reason: unterminated_frontmatter

## Warnings

- Ambiguous and unresolved values are never converted automatically or guessed.

