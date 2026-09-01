# Migration plan — merge_properties

> Planning only. Obsidian Property Studio v1 never modifies your vault. Use this plan to make the changes yourself in Obsidian.

## Summary

- notes_to_change: 1
- conflicts: 1
- manual_review: 0
- excluded_ambiguous: 0
- usage: {'project_name': 2, 'project': 6}

## Notes that would change (1)

- `Archive/Old Project.md` — before: {'project_name': 'Legacy'} — after: {'project': 'Legacy'} — resolution: identical values — safe to merge

## Conflicts — manual review required (1)

- `Archive/Merged Candidate.md` — reason: conflicting_values — detail: This note holds different values for the properties being merged. The product will not choose a winner. — values: {'project_name': 'Legacy Apollo', 'project': 'Apollo Legacy'} — resolution: manual review required

## Manual review (0)

_None._

## Excluded (ambiguous duplicate keys) (0)

_None._

## Notes whose frontmatter could not be read (3)

- `Notes/Malformed.md` — reason: invalid_yaml
- `Notes/Not A Mapping.md` — reason: not_a_mapping
- `Notes/Unterminated.md` — reason: unterminated_frontmatter

