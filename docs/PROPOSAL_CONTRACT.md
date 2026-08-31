# External schema proposal contract — version 1.0

Obsidian Property Studio contains **no AI**. It can, however, import a schema *proposal* produced by
an external agent or skill (for example a future `Obsidian Property Architect Skill`).

A proposal is **advisory, untrusted input**. Property Studio validates it locally, compares it with
your real vault inventory, and shows it to you for accept / edit / reject. A proposal can never
modify a vault — the product has no vault-write capability at all.

## Format

```json
{
  "proposal_version": "1.0",
  "schema_name": "equipment",
  "description": "optional free text",
  "generated_by": "optional producer identification",
  "provenance": "optional free-form provenance",
  "notes": "optional free text",
  "properties": [
    {
      "name": "project",
      "storage_type": "text",
      "ui_control": "note_link",
      "required": false,
      "reason": "Relate this record to an existing project note",
      "allowed_values": null,
      "confidence": 0.82,
      "evidence": "optional, preserved and displayed",
      "provenance": "optional, preserved and displayed"
    }
  ]
}
```

### Top-level fields

| Field | Required | Rules |
| --- | --- | --- |
| `proposal_version` | yes | string; currently only `"1.0"` is supported. Anything else is rejected. |
| `schema_name` | yes | non-empty string |
| `properties` | yes | non-empty array of property objects |
| `description`, `generated_by`, `provenance`, `notes` | no | free text, preserved and displayed |

Unknown top-level fields are ignored with a warning (never silently dropped from the report).

### Property fields

| Field | Required | Rules |
| --- | --- | --- |
| `name` | yes | non-empty string, unique within the proposal |
| `storage_type` | yes | one of `text`, `list`, `number`, `checkbox`, `date`, `datetime`, `tags` |
| `ui_control` | no (default `plain`) | one of `plain`, `single_choice`, `multi_choice`, `note_link`, `note_link_list`; must be compatible with `storage_type` |
| `required` | no (default `false`) | boolean |
| `reason` | no | string shown to the user — say *why* the property exists |
| `allowed_values` | no | `null` or an array of scalars; required when the control is a choice control |
| `confidence` | no | `null` or a number between `0` and `1` |
| `evidence`, `provenance` | no | preserved and displayed as provenance |

### Compatibility matrix (`ui_control` → allowed `storage_type`)

| Control | Allowed storage types | Serialised as |
| --- | --- | --- |
| `plain` | text, list, number, checkbox, date, datetime, tags | the storage type, unchanged |
| `single_choice` | text, number, date, datetime | one scalar value |
| `multi_choice` | list, tags | a YAML list of scalars |
| `note_link` | text | `"[[Note Name]]"` text value |
| `note_link_list` | list | list of `"[[Note Name]]"` text values |

## Rejection behaviour

A proposal is rejected — honestly, with a specific message per problem — when:

* the file is not valid JSON, or is not a JSON object;
* `proposal_version` is missing or unsupported;
* `schema_name` is missing/empty;
* `properties` is missing, empty or not a list;
* a property has no usable `name`, or repeats a name;
* `storage_type` is not an Obsidian property type (e.g. `"select"` — that is a UI control, not a type);
* `ui_control` is unknown or incompatible with `storage_type`;
* `required` is not boolean, `allowed_values` is not a list of scalars, or `confidence` is out of range;
* a choice control has no allowed values.

Nothing is imported when validation fails, and the vault is untouched in every case.

## What happens after a valid import

1. Each proposed property is compared with the vault inventory:
   `new` · `exact_existing` · `case_variant_exists` · `possible_overlap`.
2. Where the property already exists, its current usage count, dominant storage type and top values
   are shown, plus whether the proposed type agrees with what the vault actually contains.
3. `reason`, `confidence` and provenance fields are preserved and displayed.
4. You choose: accept into the schema editor (still fully editable), edit, or reject.

Sample files: `fixtures/proposals/valid_equipment.json`,
`fixtures/proposals/invalid_bad_types.json`, `fixtures/proposals/invalid_unsupported_version.json`,
`fixtures/proposals/invalid_malformed_json.json`.
