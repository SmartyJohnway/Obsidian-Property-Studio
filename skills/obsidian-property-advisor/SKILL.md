---
name: obsidian-property-advisor
description: Companion AI advisor skill for Obsidian Property Studio. Generates valid Proposal Contract JSON schemas to model, standardize, and govern note frontmatter properties.
---

# Obsidian Property Advisor Skill

This skill guides external AI assistants, agents, and LLMs in designing valid property schemas for Obsidian PKM vaults, compatible with **Obsidian Property Studio v1.2.0**.

## Core Safety Constraints
1. **Advisory Role Only**: You never write directly to the Obsidian vault. All recommendations are output as structured JSON proposals that the human user reviews and adopts within Obsidian Property Studio.
2. **Strict Schema Contract**: All generated schema proposals must strictly follow Proposal Contract 1.0 or 1.1.

## Supported Storage Types
- `text`: Plain text string.
- `list`: Array / sequence of items.
- `number`: Numeric values (integers or floats).
- `checkbox`: Boolean true / false.
- `date`: ISO date `YYYY-MM-DD`.
- `datetime`: ISO datetime `YYYY-MM-DDTHH:MM:SS`.
- `tags`: Tag list.

## Supported UI Controls
- `plain`: Standard Obsidian input widget (default).
- `single_choice`: Dropdown selection from fixed `allowed_values`.
- `multi_choice`: Multi-select dropdown from fixed `allowed_values`.
- `note_link`: Wikilink `[[Note Name]]` picker.
- `note_link_list`: List of wikilinks `[[Note Name]]`.

## Proposal Contract Specification (v1.1)

```json
{
  "proposal_version": "1.1",
  "schema_name": "book_summary",
  "description": "Schema for reading notes and book summaries",
  "target_scope": "Reading",
  "rationale": "Ensure all reading notes track author, rating, and publication year consistently.",
  "properties": [
    {
      "name": "author",
      "storage_type": "text",
      "ui_control": "plain",
      "required": true,
      "reason": "Author of the book"
    },
    {
      "name": "rating",
      "storage_type": "number",
      "ui_control": "plain",
      "required": false,
      "reason": "1-5 star review score"
    },
    {
      "name": "status",
      "storage_type": "text",
      "ui_control": "single_choice",
      "allowed_values": ["reading", "completed", "abandoned"],
      "required": true,
      "reason": "Current reading progress"
    }
  ]
}
```

## How to Import into Obsidian Property Studio
1. Copy the generated JSON block.
2. Open Obsidian Property Studio.
3. Navigate to **AI 提案匯入 (AI Proposal Import)**.
4. Paste the JSON into the input area and click **匯入與比對 (Validate & Compare)**.
5. Review the schema diff and click **儲存至具名架構庫 (Save as Named Schema)**.
