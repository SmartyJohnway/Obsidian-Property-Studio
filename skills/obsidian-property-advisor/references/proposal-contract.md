# Proposal Contract Specification (v1.0 & v1.1)

All proposals produced by the Obsidian Property Advisor Skill must strictly adhere to the Proposal Contract specification.

## Core Schema Structure
- `proposal_version`: String, '1.0' or '1.1'.
- `schema_name`: String, required. Identifies the schema.
- `description`: String, optional. Brief human-readable purpose.
- `properties`: Array of Property objects, required.
- `target_scope`: String (v1.1+), optional target folder/scope name.
- `rationale`: String (v1.1+), optional explanation of the overall design.
- `target_note`: String (v1.1+), optional path of the note this proposal applies to.

## Property Object Fields
- `name`: String, required. Valid non-empty property identifier.
- `storage_type`: String, required. One of: 'text', 'number', 'date', 'datetime', 'checkbox', 'list', 'tags'.
- `ui_control`: String, optional. Defaults to 'plain'. One of: 'plain', 'single_choice', 'multi_choice', 'note_link', 'note_link_list'.
- `required`: Boolean, optional. Defaults to false.
- `allowed_values`: Array of strings, optional. Required when ui_control is single_choice or multi_choice.
- `reason`: String, optional human-understandable justification.
- `description`: String, optional.
