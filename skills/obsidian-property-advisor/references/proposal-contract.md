# Proposal Contract Specification (v1.0 & v1.1)

All proposals produced by the Obsidian Property Advisor Skill must strictly adhere to the Proposal Contract specification.

## Core Schema Structure
- `proposal_version`: String, exactly '1.0' or '1.1'.
- `schema_name`: String, required. Identifies the schema.
- `description`: String, optional. Brief human-readable purpose.
- `properties`: Array of Property objects, required.
- `management_purpose`: String (v1.1+), optional PKM management intent.
- `source_context`: String (v1.1+), optional context of source conversation/topic.
- `target_note_kind`: String (v1.1+), optional classification (e.g. project, equipment, regulation).
- `proposal_notes`: String (v1.1+), optional advisory caveats or trade-offs.
- `schema_target`: String (v1.1+), optional target Scope path or Named Schema ID.
- `target_note`: String (optional legacy compatibility alias).
- `rationale`: String (optional legacy compatibility alias).

## Property Object Fields
- `name`: String, required. Valid non-empty property identifier.
- `storage_type`: String, required. One of: 'text', 'number', 'date', 'datetime', 'checkbox', 'list', 'tags'.
- `ui_control`: String, optional. Defaults to 'plain'. One of: 'plain', 'single_choice', 'multi_choice', 'note_link', 'note_link_list'.
- `required`: Boolean, optional. Defaults to false.
- `allowed_values`: Array of strings, optional. Required when ui_control is single_choice or multi_choice.
- `reason`: String, optional human-understandable justification.
- `description`: String, optional.
