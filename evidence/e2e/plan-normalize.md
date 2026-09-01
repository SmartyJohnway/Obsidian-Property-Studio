# Migration plan — normalize_values

> Planning only. Obsidian Property Studio v1 never modifies your vault. Use this plan to make the changes yourself in Obsidian.

## Summary

- usage_count: 9
- distinct_values: 6
- groups_to_normalize: 1
- notes_to_change: 2
- values_left_untouched: 3
- excluded_ambiguous: 1

## Value groups to normalize (1)

- `active` — canonical_value: active — variants: [{'value': 'active', 'count': 3, 'notes': ['People/Ada Lovelace.md', 'People/林小明.md', 'Projects/Apollo.md']}, {'value': 'ACTIVE', 'count': 1, 'notes': ['Projects/Cascade.md']}, {'value': 'Active', 'count': 1, 'notes': ['Projects/Borealis.md']}] — match_basis: case/whitespace only — notes_to_change: ['Projects/Borealis.md', 'Projects/Cascade.md'] — notes_to_change_count: 2

## Excluded (ambiguous duplicate keys) (1)

- `Notes/Duplicate Key.md` — property: status — reason: duplicate YAML key — value is ambiguous, so this note is excluded from the plan (fail-closed)

## Notes whose frontmatter could not be read (3)

- `Notes/Malformed.md` — reason: invalid_yaml
- `Notes/Not A Mapping.md` — reason: not_a_mapping
- `Notes/Unterminated.md` — reason: unterminated_frontmatter

