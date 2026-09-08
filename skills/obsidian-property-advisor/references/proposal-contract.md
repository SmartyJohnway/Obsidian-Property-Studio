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
- `name`: String, required. Valid non-empty property identifier, unique within the proposal.
- `storage_type`: String, required. Frontmatter storage data type. One of: 'text', 'list', 'number', 'checkbox', 'date', 'datetime', 'tags'.
- `ui_control`: String, optional. Defaults to 'plain'. Higher-level input affordance. One of: 'plain', 'single_choice', 'multi_choice', 'note_link', 'note_link_list'.
- `required`: Boolean, optional. Defaults to false.
- `allowed_values`: Array of scalars (string or number), optional. Required when ui_control is single_choice or multi_choice.
- `confidence`: Number, optional. Float between 0.0 and 1.0.
- `reason`: String, optional human-understandable justification for PKM management.
- `evidence`: Any, optional provenance or context evidence.
- `provenance`: Any, optional producer tracking data.

---

## Storage Type vs UI Control Distinction

It is critical to distinguish between **Storage Type** (`storage_type`) and **UI Control** (`ui_control`):
- `storage_type` defines how Obsidian serializes the property in the note's YAML frontmatter.
- `ui_control` defines the user interface editing widget displayed in Obsidian Property Studio.

A UI control is NOT a storage type. For instance:
- `select` is NOT a storage type; it is a `single_choice` UI control over a scalar `text`, `number`, `date`, or `datetime` storage type.
- `multiselect` is NOT a storage type; it is a `multi_choice` UI control over a `list` or `tags` storage type.
- `note_link` is NOT a storage type; it is a wikilink UI widget over a `text` storage type (e.g. `"[[Note Name]]"`).
- `note_link_list` is NOT a storage type; it is a wikilink list UI widget over a `list` storage type (e.g. `["[[Note A]]", "[[Note B]]"]`).

---

## Authoritative Compatibility Matrix

Every property in a proposal MUST have a compatible `storage_type` and `ui_control` pair. Any incompatible pair will be rejected by Property Studio.

| UI Control (`ui_control`) | Allowed Storage Types (`storage_type`) | Obsidian Frontmatter Serialization | Notes |
|---|---|---|---|
| `plain` | `text`, `list`, `number`, `checkbox`, `date`, `datetime`, `tags` | Raw value matching storage type | Supported across all standard storage types without extra constraints. |
| `single_choice` | `text`, `number`, `date`, `datetime` | Single scalar value | Dropdown / select widget. Requires `allowed_values`. |
| `multi_choice` | `list`, `tags` | YAML list of scalars | Multi-select widget. Requires `allowed_values`. |
| `note_link` | `text` | `"[[Note Name]]"` | Single wikilink picker. Must serialize as scalar text. |
| `note_link_list` | `list` | `["[[Note A]]", "[[Note B]]"]` | Multi-wikilink picker. Must serialize as YAML list. |

### Concrete Incompatibility Examples

#### INVALID (Rejected by Property Studio):
```json
{
  "name": "related_tools",
  "storage_type": "text",
  "ui_control": "note_link_list"
}
```
*Why it fails:* `note_link_list` represents a list of wikilinks and requires `storage_type: "list"`. It cannot be paired with `text`.

#### VALID (Accepted):
```json
{
  "name": "related_tools",
  "storage_type": "list",
  "ui_control": "note_link_list"
}
```

#### INVALID:
```json
{
  "name": "status",
  "storage_type": "list",
  "ui_control": "single_choice",
  "allowed_values": ["active", "completed"]
}
```
*Why it fails:* `single_choice` selects a single scalar value (`text`, `number`, `date`, `datetime`), not a `list`. For a list of multiple selections, use `multi_choice`.
