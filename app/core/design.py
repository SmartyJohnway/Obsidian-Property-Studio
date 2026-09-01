"""Beginner-oriented property/schema design (M004).

Deterministic recipes only — no LLM, no network (REQ-005 / REQ-013).
A user describes *what they want to manage* and *what they want to filter or
group by*; the product proposes properties with plain-language reasons.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .inventory import Inventory, key_tokens, normalize_key
from .model import (
    Schema,
    SchemaProperty,
    StorageType,
    UIControl,
)

import difflib


@dataclass(frozen=True)
class PropTemplate:
    name: str
    storage_type: StorageType
    ui_control: UIControl
    reason: str
    required: bool = False
    allowed_values: tuple[str, ...] | None = None

    def to_schema_property(self, origin: str) -> SchemaProperty:
        return SchemaProperty(
            name=self.name,
            storage_type=self.storage_type,
            ui_control=self.ui_control,
            required=self.required,
            reason=self.reason,
            allowed_values=self.allowed_values,
            origin=origin,
        )


T = StorageType
C = UIControl

#: Properties proposed for every schema — they are what make a vault filterable.
BASE_TEMPLATES: tuple[PropTemplate, ...] = (
    PropTemplate(
        "type", T.TEXT, C.SINGLE_CHOICE,
        "Marks what kind of note this is, so you can filter one kind of note out "
        "of the whole vault.",
        required=True,
    ),
    PropTemplate(
        "status", T.TEXT, C.SINGLE_CHOICE,
        "Tracks where this item currently is, so you can see only what is active.",
        required=False,
        allowed_values=("active", "on hold", "done", "archived"),
    ),
    PropTemplate(
        "tags", T.TAGS, C.MULTI_CHOICE,
        "Free-form labels for cross-cutting themes. Obsidian indexes tags "
        "natively for search.",
    ),
)


@dataclass(frozen=True)
class Recipe:
    id: str
    label: str
    description: str
    keywords: tuple[str, ...]
    type_value: str
    properties: tuple[PropTemplate, ...]
    status_values: tuple[str, ...] = ("active", "on hold", "done", "archived")


RECIPES: tuple[Recipe, ...] = (
    Recipe(
        "project", "Projects", "Track projects, their owner, deadline and state.",
        ("project", "projects", "專案", "計畫", "計劃", "專桉"),
        "project",
        (
            PropTemplate("owner", T.TEXT, C.NOTE_LINK,
                         "Who is responsible. Linking to a person note lets you open "
                         "that person and see every project they own."),
            PropTemplate("start_date", T.DATE, C.PLAIN,
                         "When work started, so you can sort projects by age."),
            PropTemplate("due_date", T.DATE, C.PLAIN,
                         "Deadline, so you can find what is due this week."),
            PropTemplate("priority", T.TEXT, C.SINGLE_CHOICE,
                         "Lets you sort the list when everything feels urgent.",
                         allowed_values=("high", "medium", "low")),
            PropTemplate("area", T.TEXT, C.SINGLE_CHOICE,
                         "Which part of your life/work this belongs to."),
        ),
        ("planning", "active", "on hold", "done", "archived"),
    ),
    Recipe(
        "task", "Tasks / action items", "Track individual actions and their state.",
        ("task", "tasks", "todo", "to-do", "action", "任務", "待辦", "工作項目"),
        "task",
        (
            PropTemplate("due_date", T.DATE, C.PLAIN, "A real date property lets you list everything due this week."),
            PropTemplate("project", T.TEXT, C.NOTE_LINK,
                         "Connects the task to its project note, so a project shows its tasks."),
            PropTemplate("priority", T.TEXT, C.SINGLE_CHOICE,
                         "Lets you sort a long list when everything feels urgent.", allowed_values=("high", "medium", "low")),
            PropTemplate("done", T.CHECKBOX, C.PLAIN,
                         "A simple yes/no flag you can filter on to hide finished work."),
        ),
        ("todo", "doing", "blocked", "done"),
    ),
    Recipe(
        "reading", "Reading list / books",
        "Track books and articles, what you read and what you thought.",
        ("book", "books", "reading", "read", "article", "閱讀", "書", "書籍", "讀書"),
        "book",
        (
            PropTemplate("author", T.TEXT, C.NOTE_LINK,
                         "Links to an author note so you can see everything by them."),
            PropTemplate("rating", T.NUMBER, C.PLAIN,
                         "A number lets you sort your best reads to the top."),
            PropTemplate("finished_date", T.DATE, C.PLAIN,
                         "When you finished, for yearly reading reviews."),
            PropTemplate("topics", T.LIST, C.MULTI_CHOICE,
                         "Subjects covered, so you can group by topic."),
        ),
        ("to read", "reading", "finished", "abandoned"),
    ),
    Recipe(
        "meeting", "Meetings", "Track meetings, attendees and follow-ups.",
        ("meeting", "meetings", "1:1", "standup", "會議", "會談", "訪談"),
        "meeting",
        (
            PropTemplate("date", T.DATE, C.PLAIN, "A real date lets you find meetings by week, month or quarter."),
            PropTemplate("attendees", T.LIST, C.NOTE_LINK_LIST,
                         "Links to the people who attended, so each person note can "
                         "show their meetings."),
            PropTemplate("project", T.TEXT, C.NOTE_LINK,
                         "Links the meeting to its project, so the project shows its meetings."),
            PropTemplate("follow_up_required", T.CHECKBOX, C.PLAIN,
                         "Flags meetings that still need action, so nothing is forgotten."),
        ),
        ("scheduled", "held", "cancelled"),
    ),
    Recipe(
        "person", "People / contacts", "Keep a people directory you can query.",
        ("person", "people", "contact", "contacts", "人", "人物", "聯絡人", "客戶"),
        "person",
        (
            PropTemplate("organisation", T.TEXT, C.NOTE_LINK,
                         "Links the person to a company/organisation note."),
            PropTemplate("role", T.TEXT, C.PLAIN, "Their role, so you can group people by what they do."),
            PropTemplate("email", T.TEXT, C.PLAIN, "Plain contact detail kept as structured data instead of loose text."),
            PropTemplate("last_contacted", T.DATE, C.PLAIN,
                         "Lets you find people you have not spoken to in a while."),
        ),
        ("active", "inactive"),
    ),
    Recipe(
        "equipment", "Equipment / assets",
        "Track hardware, tools or gear, where it is and when it was serviced.",
        ("equipment", "asset", "assets", "device", "gear", "hardware", "machine",
         "設備", "器材", "資產", "機台", "工具"),
        "equipment",
        (
            PropTemplate("serial_number", T.TEXT, C.PLAIN,
                         "Identifies the exact physical unit, not just the model name."),
            PropTemplate("location", T.TEXT, C.SINGLE_CHOICE,
                         "Where it physically is, so you can find it."),
            PropTemplate("owner", T.TEXT, C.NOTE_LINK,
                         "Who is responsible for it, linked to that person's note."),
            PropTemplate("purchase_date", T.DATE, C.PLAIN,
                         "Age of the asset, for warranty and replacement planning."),
            PropTemplate("last_service_date", T.DATE, C.PLAIN,
                         "Lets you find equipment overdue for maintenance."),
            PropTemplate("project", T.TEXT, C.NOTE_LINK,
                         "Relates this record to an existing project note."),
        ),
        ("in use", "in storage", "in repair", "retired"),
    ),
    Recipe(
        "research", "Research / papers", "Track sources and what you concluded.",
        ("research", "paper", "papers", "study", "literature", "研究", "論文", "文獻"),
        "paper",
        (
            PropTemplate("authors", T.LIST, C.NOTE_LINK_LIST,
                         "Links to author notes, so an author shows all of their papers."),
            PropTemplate("year", T.NUMBER, C.PLAIN, "Publication year as a number, so you can sort and filter by age."),
            PropTemplate("source_url", T.TEXT, C.PLAIN, "Where to find the original source again without searching."),
            PropTemplate("topics", T.LIST, C.MULTI_CHOICE,
                         "Subject grouping across your literature."),
        ),
        ("to read", "reading", "summarised", "cited"),
    ),
    Recipe(
        "journal", "Journal / daily notes", "Make daily notes queryable.",
        ("journal", "diary", "daily", "log", "日誌", "日記", "每日"),
        "journal",
        (
            PropTemplate("date", T.DATE, C.PLAIN, "The day this entry is about, so entries sort chronologically."),
            PropTemplate("mood", T.TEXT, C.SINGLE_CHOICE,
                         "Lets you look back at patterns over time.",
                         allowed_values=("great", "good", "ok", "low")),
            PropTemplate("people", T.LIST, C.NOTE_LINK_LIST,
                         "Who you saw that day, linked to person notes."),
        ),
        ("draft", "final"),
    ),
    Recipe(
        "course", "Courses / study", "Track learning material and progress.",
        ("course", "class", "study", "learning", "課程", "學習", "上課"),
        "course",
        (
            PropTemplate("instructor", T.TEXT, C.NOTE_LINK, "Links to the teacher note, so a teacher shows all their courses."),
            PropTemplate("start_date", T.DATE, C.PLAIN, "Start date, so you can see what is running right now."),
            PropTemplate("progress", T.NUMBER, C.PLAIN,
                         "Percentage completed, so you can sort by what is unfinished."),
        ),
        ("enrolled", "in progress", "completed", "dropped"),
    ),
    Recipe(
        "recipe", "Recipes / cooking", "Make a cookbook you can filter.",
        ("recipe", "cooking", "food", "食譜", "料理", "烹飪"),
        "recipe",
        (
            PropTemplate("cuisine", T.TEXT, C.SINGLE_CHOICE, "Groups recipes by style of food when you cannot decide what to cook."),
            PropTemplate("prep_minutes", T.NUMBER, C.PLAIN,
                         "Find something you can cook in the time you have."),
            PropTemplate("ingredients", T.LIST, C.MULTI_CHOICE,
                         "Lets you search recipes by what is already in the fridge."),
            PropTemplate("rating", T.NUMBER, C.PLAIN, "A number score, so your favourites sort to the top."),
        ),
        ("to try", "tested", "favourite"),
    ),
    Recipe(
        "travel", "Trips / travel", "Plan and review trips.",
        ("trip", "travel", "holiday", "vacation", "旅行", "旅遊", "行程"),
        "trip",
        (
            PropTemplate("destination", T.TEXT, C.SINGLE_CHOICE, "Groups trips by place, so you can revisit what you did there."),
            PropTemplate("start_date", T.DATE, C.PLAIN, "Departure date, so trips sort correctly on a timeline."),
            PropTemplate("end_date", T.DATE, C.PLAIN, "Return date, used with the start date to work out trip length."),
            PropTemplate("budget", T.NUMBER, C.PLAIN, "A number, so you can compare and total what trips cost."),
            PropTemplate("companions", T.LIST, C.NOTE_LINK_LIST, "Links to the people you travelled with, from their own notes."),
        ),
        ("idea", "booked", "completed"),
    ),
    Recipe(
        "media", "Films / series / media", "Track what you watched.",
        ("movie", "film", "series", "tv", "watch", "media", "電影", "影集", "觀影"),
        "media",
        (
            PropTemplate("director", T.TEXT, C.NOTE_LINK, "Links to the creator note, so a director shows all their films."),
            PropTemplate("year", T.NUMBER, C.PLAIN, "Release year as a number, so you can sort and filter by decade."),
            PropTemplate("rating", T.NUMBER, C.PLAIN, "Your own score as a number, so you can rank what you watched."),
            PropTemplate("watched_date", T.DATE, C.PLAIN, "When you watched it, for yearly review lists."),
        ),
        ("to watch", "watching", "watched"),
    ),
)


#: Additional intents the user can tick. Each maps to concrete properties.
@dataclass(frozen=True)
class Intent:
    id: str
    label: str
    keywords: tuple[str, ...]
    properties: tuple[PropTemplate, ...]


INTENTS: tuple[Intent, ...] = (
    Intent(
        "filter_by_status", "See only what is still open / active",
        ("status", "open", "active", "progress", "狀態", "進度"),
        (BASE_TEMPLATES[1],),
    ),
    Intent(
        "group_by_category", "Group things into categories or areas",
        ("category", "categor", "area", "group", "分類", "類別", "領域"),
        (PropTemplate("category", T.TEXT, C.SINGLE_CHOICE,
                      "A controlled category value so grouping stays consistent."),),
    ),
    Intent(
        "find_by_date", "Find things by date (recent, overdue, this month)",
        ("date", "when", "deadline", "due", "recent", "日期", "時間", "期限"),
        (PropTemplate("date", T.DATE, C.PLAIN,
                      "A real date property sorts correctly; a text date does not."),),
    ),
    Intent(
        "link_to_people", "Connect notes to people",
        ("people", "person", "who", "owner", "人", "誰", "負責"),
        (PropTemplate("people", T.LIST, C.NOTE_LINK_LIST,
                      "Links to person notes, so each person shows their related notes."),),
    ),
    Intent(
        "link_to_projects", "Connect notes to projects",
        ("project", "initiative", "專案", "計畫"),
        (PropTemplate("project", T.TEXT, C.NOTE_LINK,
                      "Relates this note to an existing project note."),),
    ),
    Intent(
        "track_location", "Know where something is",
        ("location", "where", "place", "shelf", "位置", "地點", "存放"),
        (PropTemplate("location", T.TEXT, C.SINGLE_CHOICE,
                      "A controlled location value so the same place is spelled once."),),
    ),
    Intent(
        "track_priority", "Decide what to do first",
        ("priority", "important", "urgent", "優先", "重要"),
        (PropTemplate("priority", T.TEXT, C.SINGLE_CHOICE,
                      "Lets you sort a long list by importance instead of guessing.",
                      allowed_values=("high", "medium", "low")),),
    ),
    Intent(
        "rate_things", "Rate or score things",
        ("rating", "score", "rate", "評分", "分數"),
        (PropTemplate("rating", T.NUMBER, C.PLAIN,
                      "A number property can be sorted and averaged."),),
    ),
    Intent(
        "track_cost", "Track cost or amount",
        ("cost", "price", "budget", "amount", "money", "費用", "價格", "預算"),
        (PropTemplate("cost", T.NUMBER, C.PLAIN,
                      "A number property lets you sum and compare amounts."),),
    ),
    Intent(
        "track_vendor", "Track vendor or supplier",
        ("vendor", "supplier", "廠商", "供應商", "賣家"),
        (PropTemplate("vendor", T.TEXT, C.NOTE_LINK,
                      "Links to a vendor note so you can see all equipment and purchases from them."),),
    ),
    Intent(
        "track_procurement", "Track procurement or purchasing status",
        ("procurement", "procurement status", "purchasing", "採購", "採購狀態", "進貨"),
        (PropTemplate("procurement_status", T.TEXT, C.SINGLE_CHOICE,
                      "Tracks procurement progress (requested, approved, ordered, delivered).",
                      allowed_values=("requested", "approved", "ordered", "delivered")),),
    ),
    Intent(
        "track_review_date", "Track review or audit date",
        ("review date", "review_date", "next review", "audit date", "審查日期", "複查日期", "檢視日期"),
        (PropTemplate("review_date", T.DATE, C.PLAIN,
                      "Date scheduled for next review or audit."),),
    ),
)


_WORD = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]+")


def _match_score(text: str, keywords: tuple[str, ...]) -> int:
    lowered = text.casefold()
    score = 0
    for kw in keywords:
        if kw.casefold() in lowered:
            score += 2 if len(kw) > 3 else 1
    return score


def suggest_recipes(goal_text: str, limit: int = 3) -> list[dict[str, Any]]:
    """Rank recipes against a free-text goal (deterministic)."""
    scored = [
        (
            _match_score(goal_text, r.keywords),
            r,
        )
        for r in RECIPES
    ]
    scored = [(s, r) for s, r in scored if s > 0]
    scored.sort(key=lambda item: (-item[0], item[1].id))
    return [
        {
            "id": r.id,
            "label": r.label,
            "description": r.description,
            "score": s,
            "type_value": r.type_value,
        }
        for s, r in scored[:limit]
    ]


def detect_intents(goal_text: str) -> list[str]:
    hits = []
    for intent in INTENTS:
        if _match_score(goal_text, intent.keywords) > 0:
            hits.append(intent.id)
    return hits


def _slug(text: str) -> str:
    words = _WORD.findall(text.casefold())
    if not words:
        return "notes"
    return "_".join(words[:3])


def _settle_choice_controls(props: list[SchemaProperty], inv: "Inventory | None") -> None:
    """A choice control needs values. Take them from the vault when the vault
    already uses that property; otherwise keep the property as a plain input and
    tell the user how to turn it into a controlled choice."""
    for prop in props:
        if prop.ui_control not in (UIControl.SINGLE_CHOICE, UIControl.MULTI_CHOICE):
            continue
        if prop.allowed_values:
            continue
        entry = inv.get(prop.name) if inv is not None else None
        if entry is not None and entry.values:
            top = [stat.value for stat in entry.top_values(8) if stat.value.strip()]
            if top:
                prop.allowed_values = tuple(top)
                prop.reason = (
                    prop.reason
                    + f" Suggested values come from the {entry.usage_count} notes in "
                    "your vault that already use this property."
                ).strip()
                continue
        prop.ui_control = UIControl.PLAIN
        prop.reason = (
            prop.reason
            + " Add a list of allowed values in the editor to turn this into a "
            "controlled choice."
        ).strip()


OBJECT_PRESETS: dict[str, dict[str, Any]] = {
    "project": {
        "id": "project",
        "name_zh": "專案／計畫",
        "name_en": "Projects / Plans",
        "type_val": "project",
        "props": [
            PropTemplate("owner", T.TEXT, C.NOTE_LINK, "Responsible person note link"),
            PropTemplate("start_date", T.DATE, C.PLAIN, "Project start date"),
            PropTemplate("due_date", T.DATE, C.PLAIN, "Project deadline"),
            PropTemplate("priority", T.TEXT, C.SINGLE_CHOICE, "Urgency priority", allowed_values=("high", "medium", "low")),
            PropTemplate("area", T.TEXT, C.SINGLE_CHOICE, "Life or work domain"),
        ]
    },
    "task": {
        "id": "task",
        "name_zh": "任務／行動事項",
        "name_en": "Tasks / Actions",
        "type_val": "task",
        "props": [
            PropTemplate("due_date", T.DATE, C.PLAIN, "Due date for task"),
            PropTemplate("project", T.TEXT, C.NOTE_LINK, "Related project note"),
            PropTemplate("priority", T.TEXT, C.SINGLE_CHOICE, "Priority level", allowed_values=("high", "medium", "low")),
            PropTemplate("done", T.CHECKBOX, C.PLAIN, "Completion status flag"),
        ]
    },
    "concept": {
        "id": "concept",
        "name_zh": "知識／概念",
        "name_en": "Knowledge / Concepts",
        "type_val": "concept",
        "props": [
            PropTemplate("topics", T.LIST, C.MULTI_CHOICE, "Cross-cutting subject topics"),
            PropTemplate("summary", T.TEXT, C.PLAIN, "Short summary of the concept"),
            PropTemplate("parent_topic", T.TEXT, C.NOTE_LINK, "Parent concept hierarchy"),
            PropTemplate("aliases", T.LIST, C.MULTI_CHOICE, "Alternative names or acronyms"),
        ]
    },
    "reference": {
        "id": "reference",
        "name_zh": "參考資料／來源",
        "name_en": "References / Sources",
        "type_val": "reference",
        "props": [
            PropTemplate("author", T.TEXT, C.NOTE_LINK, "Author note or attribution"),
            PropTemplate("source_url", T.TEXT, C.PLAIN, "Original source URL"),
            PropTemplate("year", T.NUMBER, C.PLAIN, "Publication year"),
            PropTemplate("topics", T.LIST, C.MULTI_CHOICE, "Related subject topics"),
        ]
    },
    "standard": {
        "id": "standard",
        "name_zh": "法規／標準",
        "name_en": "Regulations / Standards",
        "type_val": "standard",
        "props": [
            PropTemplate("code", T.TEXT, C.PLAIN, "Official standard code or identifier"),
            PropTemplate("effective_date", T.DATE, C.PLAIN, "Date effective or enacted"),
            PropTemplate("authority", T.TEXT, C.NOTE_LINK, "Regulatory authority organization"),
            PropTemplate("scope_domain", T.TEXT, C.SINGLE_CHOICE, "Applicable business domain"),
        ]
    },
    "sop": {
        "id": "sop",
        "name_zh": "廠內規範／SOP",
        "name_en": "Internal SOPs / Specs",
        "type_val": "sop",
        "props": [
            PropTemplate("doc_number", T.TEXT, C.PLAIN, "Document number"),
            PropTemplate("department", T.TEXT, C.SINGLE_CHOICE, "Responsible department"),
            PropTemplate("version", T.TEXT, C.PLAIN, "Current SOP version string"),
            PropTemplate("review_date", T.DATE, C.PLAIN, "Next scheduled review date"),
        ]
    },
    "equipment": {
        "id": "equipment",
        "name_zh": "物品／設備／資產",
        "name_en": "Equipment / Assets",
        "type_val": "equipment",
        "props": [
            PropTemplate("serial_number", T.TEXT, C.PLAIN, "Serial number or asset tag"),
            PropTemplate("location", T.TEXT, C.SINGLE_CHOICE, "Physical storage location"),
            PropTemplate("owner", T.TEXT, C.NOTE_LINK, "Custodian person note"),
            PropTemplate("purchase_date", T.DATE, C.PLAIN, "Acquisition date"),
            PropTemplate("last_service_date", T.DATE, C.PLAIN, "Last maintenance date"),
        ]
    },
    "software": {
        "id": "software",
        "name_zh": "軟體／工具／服務",
        "name_en": "Software / Tools / Services",
        "type_val": "software",
        "props": [
            PropTemplate("vendor", T.TEXT, C.NOTE_LINK, "Vendor or developer organization"),
            PropTemplate("license_type", T.TEXT, C.SINGLE_CHOICE, "License classification"),
            PropTemplate("version", T.TEXT, C.PLAIN, "Deployed software version"),
            PropTemplate("doc_url", T.TEXT, C.PLAIN, "Documentation link"),
        ]
    },
    "workflow": {
        "id": "workflow",
        "name_zh": "應用場景／工作流",
        "name_en": "Workflows / Scenarios",
        "type_val": "workflow",
        "props": [
            PropTemplate("trigger", T.TEXT, C.PLAIN, "Workflow trigger event"),
            PropTemplate("inputs", T.LIST, C.MULTI_CHOICE, "Input artifacts or prerequisites"),
            PropTemplate("outputs", T.LIST, C.MULTI_CHOICE, "Expected deliverables or outputs"),
            PropTemplate("owner", T.TEXT, C.NOTE_LINK, "Workflow owner note"),
        ]
    },
    "organization": {
        "id": "organization",
        "name_zh": "組織／供應商／客戶",
        "name_en": "Organizations / Vendors",
        "type_val": "organization",
        "props": [
            PropTemplate("org_type", T.TEXT, C.SINGLE_CHOICE, "Organization category", allowed_values=("vendor", "client", "partner", "internal")),
            PropTemplate("contact_person", T.TEXT, C.NOTE_LINK, "Primary point of contact"),
            PropTemplate("website", T.TEXT, C.PLAIN, "Official website URL"),
        ]
    },
    "person": {
        "id": "person",
        "name_zh": "人員／聯絡人",
        "name_en": "People / Contacts",
        "type_val": "person",
        "props": [
            PropTemplate("organisation", T.TEXT, C.NOTE_LINK, "Company or organization link"),
            PropTemplate("role", T.TEXT, C.PLAIN, "Job title or function"),
            PropTemplate("email", T.TEXT, C.PLAIN, "Email address"),
            PropTemplate("last_contacted", T.DATE, C.PLAIN, "Last interaction date"),
        ]
    },
    "meeting": {
        "id": "meeting",
        "name_zh": "會議／事件",
        "name_en": "Meetings / Events",
        "type_val": "meeting",
        "props": [
            PropTemplate("date", T.DATE, C.PLAIN, "Meeting date"),
            PropTemplate("attendees", T.LIST, C.NOTE_LINK_LIST, "Attending people links"),
            PropTemplate("project", T.TEXT, C.NOTE_LINK, "Associated project link"),
            PropTemplate("follow_up_required", T.CHECKBOX, C.PLAIN, "Action item flag"),
        ]
    },
    "dataset": {
        "id": "dataset",
        "name_zh": "資料集／報表",
        "name_en": "Datasets / Reports",
        "type_val": "dataset",
        "props": [
            PropTemplate("source", T.TEXT, C.PLAIN, "Data origin system"),
            PropTemplate("update_frequency", T.TEXT, C.SINGLE_CHOICE, "Refresh cadence", allowed_values=("daily", "weekly", "monthly", "quarterly", "ad-hoc")),
            PropTemplate("format", T.TEXT, C.SINGLE_CHOICE, "Data storage format", allowed_values=("csv", "parquet", "json", "sql", "excel")),
            PropTemplate("owner", T.TEXT, C.NOTE_LINK, "Data steward note"),
        ]
    },
}

NEED_PRESETS: dict[str, dict[str, Any]] = {
    "progress": {
        "id": "progress",
        "name_zh": "進度追蹤",
        "name_en": "Progress Tracking",
        "props": [
            PropTemplate("progress", T.NUMBER, C.PLAIN, "Progress percentage (0-100)"),
            PropTemplate("status", T.TEXT, C.SINGLE_CHOICE, "Execution state", allowed_values=("planning", "in progress", "blocked", "completed", "cancelled")),
        ]
    },
    "priority": {
        "id": "priority",
        "name_zh": "優先順序",
        "name_en": "Priority Order",
        "props": [
            PropTemplate("priority", T.TEXT, C.SINGLE_CHOICE, "Urgency ranking", allowed_values=("critical", "high", "medium", "low")),
        ]
    },
    "owner": {
        "id": "owner",
        "name_zh": "責任人／負責單位",
        "name_en": "Assignee / Department",
        "props": [
            PropTemplate("owner", T.TEXT, C.NOTE_LINK, "Primary responsible person note"),
            PropTemplate("department", T.TEXT, C.SINGLE_CHOICE, "Owning department or team"),
        ]
    },
    "dates": {
        "id": "dates",
        "name_zh": "開始／截止日期",
        "name_en": "Start / Due Dates",
        "props": [
            PropTemplate("start_date", T.DATE, C.PLAIN, "Initiation date"),
            PropTemplate("due_date", T.DATE, C.PLAIN, "Target completion deadline"),
        ]
    },
    "review": {
        "id": "review",
        "name_zh": "定期檢視",
        "name_en": "Periodic Review",
        "props": [
            PropTemplate("review_date", T.DATE, C.PLAIN, "Next scheduled review date"),
            PropTemplate("review_cycle", T.TEXT, C.SINGLE_CHOICE, "Review cycle interval", allowed_values=("monthly", "quarterly", "semi-annual", "annual")),
        ]
    },
    "expiration": {
        "id": "expiration",
        "name_zh": "有效期限",
        "name_en": "Expiration / Validity",
        "props": [
            PropTemplate("expiration_date", T.DATE, C.PLAIN, "Validity expiration date"),
        ]
    },
    "version": {
        "id": "version",
        "name_zh": "版本／修訂",
        "name_en": "Version / Revision",
        "props": [
            PropTemplate("version", T.TEXT, C.PLAIN, "Semantic version or revision ID"),
            PropTemplate("revision_date", T.DATE, C.PLAIN, "Date of latest revision"),
        ]
    },
    "related": {
        "id": "related",
        "name_zh": "關聯其他筆記",
        "name_en": "Related Notes / Links",
        "props": [
            PropTemplate("related", T.LIST, C.NOTE_LINK_LIST, "Linked related entity notes"),
        ]
    },
    "citation": {
        "id": "citation",
        "name_zh": "來源／引用",
        "name_en": "Source / Citations",
        "props": [
            PropTemplate("source_url", T.TEXT, C.PLAIN, "External reference link"),
            PropTemplate("author", T.TEXT, C.NOTE_LINK, "Originating author or creator"),
        ]
    },
    "compliance": {
        "id": "compliance",
        "name_zh": "適用性／合規",
        "name_en": "Compliance / Standards",
        "props": [
            PropTemplate("compliance_status", T.TEXT, C.SINGLE_CHOICE, "Compliance evaluation status", allowed_values=("compliant", "non-compliant", "exempt", "under-review")),
            PropTemplate("standard_ref", T.TEXT, C.NOTE_LINK, "Referenced compliance standard"),
        ]
    },
    "cost": {
        "id": "cost",
        "name_zh": "採購／成本",
        "name_en": "Procurement / Cost",
        "props": [
            PropTemplate("cost", T.NUMBER, C.PLAIN, "Financial cost or procurement amount"),
            PropTemplate("currency", T.TEXT, C.SINGLE_CHOICE, "Currency code", allowed_values=("TWD", "USD", "EUR", "JPY")),
        ]
    },
    "location": {
        "id": "location",
        "name_zh": "位置／保管",
        "name_en": "Location / Custody",
        "props": [
            PropTemplate("location", T.TEXT, C.SINGLE_CHOICE, "Physical place, room, or building"),
            PropTemplate("custodian", T.TEXT, C.NOTE_LINK, "Person or team currently holding custody"),
        ]
    },
    "maintenance": {
        "id": "maintenance",
        "name_zh": "維護／保養",
        "name_en": "Maintenance / Service",
        "props": [
            PropTemplate("last_service_date", T.DATE, C.PLAIN, "Most recent service or inspection date"),
            PropTemplate("next_service_date", T.DATE, C.PLAIN, "Upcoming maintenance schedule"),
        ]
    },
}


def build_schema_from_structured_inputs(
    objects: list[str] | tuple[str, ...],
    needs: list[str] | tuple[str, ...],
    extra_text: str = "",
    schema_name: str | None = None,
    inv: "Inventory | None" = None,
) -> Schema:
    """Deterministic schema proposal synthesis from structured management objects and needs (M014 / REQ-037)."""
    props: list[SchemaProperty] = []
    seen: set[str] = set()

    def add(template: PropTemplate, origin: str, override: dict[str, Any] | None = None):
        if template.name in seen:
            return
        seen.add(template.name)
        prop = template.to_schema_property(origin)
        if override:
            for key, value in override.items():
                setattr(prop, key, value)
        props.append(prop)

    # 1. Base 'type' property
    type_candidates = [OBJECT_PRESETS[obj_id]["type_val"] for obj_id in objects if obj_id in OBJECT_PRESETS]
    if not type_candidates and extra_text.strip():
        type_candidates = [_slug(extra_text)]
    if not type_candidates:
        type_candidates = ["item"]

    add(
        BASE_TEMPLATES[0],
        "recipe:base",
        {"allowed_values": tuple(type_candidates), "required": True},
    )

    # 2. Base 'status' property if not overridden
    add(BASE_TEMPLATES[1], "recipe:base")

    # 3. Add properties from selected Management Objects
    for obj_id in objects:
        preset = OBJECT_PRESETS.get(obj_id)
        if not preset:
            continue
        for template in preset["props"]:
            add(template, f"object:{obj_id}")

    # 4. Add properties from selected Management Needs
    for need_id in needs:
        preset = NEED_PRESETS.get(need_id)
        if not preset:
            continue
        for template in preset["props"]:
            add(template, f"need:{need_id}")

    # 5. Optional extra text intent detection
    if extra_text.strip():
        for detected_id in detect_intents(extra_text):
            intent = next((i for i in INTENTS if i.id == detected_id), None)
            if intent is not None:
                for template in intent.properties:
                    add(template, f"intent:{intent.id}")

    # 6. Base 'tags' property
    add(BASE_TEMPLATES[2], "recipe:base")

    _settle_choice_controls(props, inv)

    derived_name = schema_name
    if not derived_name:
        if objects:
            derived_name = "-".join(objects)
        elif extra_text.strip():
            derived_name = _slug(extra_text)
        else:
            derived_name = "custom-schema"

    description = f"Designed from {len(objects)} object preset(s) and {len(needs)} management need(s)."
    return Schema(name=derived_name, description=description, properties=props)


def build_schema(
    goal_text: str,
    recipe_id: str | None = None,
    intent_ids: tuple[str, ...] | list[str] = (),
    schema_name: str | None = None,
    inv: "Inventory | None" = None,
) -> Schema:
    """Turn 'I want to manage X' + intents into a concrete schema proposal."""
    recipe = None
    if recipe_id:
        recipe = next((r for r in RECIPES if r.id == recipe_id), None)
    if recipe is None:
        ranked = suggest_recipes(goal_text, limit=1)
        if ranked:
            recipe = next(r for r in RECIPES if r.id == ranked[0]["id"])

    props: list[SchemaProperty] = []
    seen: set[str] = set()

    def add(template: PropTemplate, origin: str, override: dict[str, Any] | None = None):
        if template.name in seen:
            return
        seen.add(template.name)
        prop = template.to_schema_property(origin)
        if override:
            for key, value in override.items():
                setattr(prop, key, value)
        props.append(prop)

    origin = f"recipe:{recipe.id}" if recipe else "recipe:generic"

    type_values = (recipe.type_value,) if recipe else (_slug(goal_text),)
    add(
        BASE_TEMPLATES[0],
        origin,
        {"allowed_values": type_values, "required": True},
    )
    status_values = recipe.status_values if recipe else BASE_TEMPLATES[1].allowed_values
    add(BASE_TEMPLATES[1], origin, {"allowed_values": tuple(status_values)})

    if recipe:
        for template in recipe.properties:
            add(template, origin)

    active_intent_ids = list(intent_ids)
    if goal_text.strip():
        for detected_id in detect_intents(goal_text):
            if detected_id not in active_intent_ids:
                active_intent_ids.append(detected_id)

    for intent_id in active_intent_ids:
        intent = next((i for i in INTENTS if i.id == intent_id), None)
        if intent is None:
            continue
        for template in intent.properties:
            add(template, f"intent:{intent.id}")

    add(BASE_TEMPLATES[2], origin)

    _settle_choice_controls(props, inv)

    name = schema_name or (recipe.id if recipe else _slug(goal_text))
    description = (
        f"Designed from the goal: “{goal_text.strip()}”."
        if goal_text.strip()
        else "Designed in Property Studio."
    )
    return Schema(name=name, description=description, properties=props)



# --------------------------------------------------------------------------
# Existing-property awareness (REQ-006 / OPS-AC-007 / R07)
# --------------------------------------------------------------------------
def check_property_reuse(
    name: str, inv: Inventory, global_inv: Inventory | None = None
) -> dict[str, Any]:
    """Compare a proposed property name with current Scope and Whole Vault inventories (R07)."""
    effective_global = global_inv or inv
    result: dict[str, Any] = {
        "proposed_name": name,
        "status": "new",
        "in_scope": False,
        "in_vault_only": False,
        "exact_match": None,
        "case_variants": [],
        "possible_overlaps": [],
        "auto_merged": False,
    }

    # 1. Check current scope inventory
    if name in inv.properties:
        entry = inv.properties[name]
        result["status"] = "exact_existing"
        result["in_scope"] = True
        result["exact_match"] = {
            "key": entry.key,
            "usage_count": entry.usage_count,
            "dominant_type": entry.dominant_type,
            "top_values": [v.to_dict() for v in entry.top_values(8)],
            "notes": sorted(entry.notes)[:50],
            "scope_location": "in_scope",
        }
    # 2. Check whole-vault inventory if not found in scope
    elif global_inv is not None and name in global_inv.properties:
        entry = global_inv.properties[name]
        result["status"] = "exact_existing_in_vault_only"
        result["in_vault_only"] = True
        result["exact_match"] = {
            "key": entry.key,
            "usage_count": entry.usage_count,
            "dominant_type": entry.dominant_type,
            "top_values": [v.to_dict() for v in entry.top_values(8)],
            "notes": sorted(entry.notes)[:50],
            "scope_location": "outside_scope",
        }

    # Check case variants and overlaps across global inventory
    norm = normalize_key(name)
    tokens = set(key_tokens(name))
    for key, entry in sorted(effective_global.properties.items()):
        if key == name:
            continue
        if normalize_key(key) == norm:
            result["case_variants"].append(
                {
                    "key": key,
                    "usage_count": entry.usage_count,
                    "dominant_type": entry.dominant_type,
                    "in_scope": key in inv.properties,
                }
            )
            continue
        other = set(key_tokens(key))
        ratio = difflib.SequenceMatcher(None, norm, normalize_key(key)).ratio()
        if (tokens and other and (tokens < other or other < tokens)) or ratio >= 0.82:
            result["possible_overlaps"].append(
                {
                    "key": key,
                    "usage_count": entry.usage_count,
                    "dominant_type": entry.dominant_type,
                    "similarity_ratio": round(ratio, 3),
                    "confidence": "possible",
                    "in_scope": key in inv.properties,
                }
            )

    if result["status"] == "new":
        if result["case_variants"]:
            result["status"] = "case_variant_exists"
        elif result["possible_overlaps"]:
            result["status"] = "possible_overlap"

    status_keys = {
        "exact_existing": "schema.status_in_scope",
        "exact_existing_in_vault_only": "schema.status_elsewhere",
        "case_variant_exists": "schema.status_case_variant",
        "possible_overlap": "schema.status_overlap",
        "new": "schema.status_new",
    }
    message_keys = {
        "exact_existing": "schema.msg_in_scope",
        "exact_existing_in_vault_only": "schema.msg_elsewhere",
        "case_variant_exists": "schema.msg_case_variant",
        "possible_overlap": "schema.msg_overlap",
        "new": "schema.msg_new",
    }
    messages = {
        "exact_existing": (
            f"'{name}' already exists in current Scope. Reuse it to keep your schema consistent."
        ),
        "exact_existing_in_vault_only": (
            f"'{name}' exists elsewhere in this vault (outside current Scope). You can adopt this existing convention."
        ),
        "case_variant_exists": (
            f"This vault already uses a differently-written version of '{name}'. "
            "Reusing the existing spelling keeps filtering consistent."
        ),
        "possible_overlap": (
            f"'{name}' looks similar to an existing property. This is a possibility "
            "for you to judge — nothing is merged automatically."
        ),
        "new": f"'{name}' is not used anywhere in this vault yet.",
    }
    result["status_key"] = status_keys.get(result["status"], "schema.status_new")
    result["message_key"] = message_keys.get(result["status"], "schema.msg_new")
    result["message"] = messages.get(result["status"], "")
    return result



def review_schema_against_vault(
    schema: Schema, inv: Inventory, global_inv: Inventory | None = None
) -> dict[str, Any]:
    """Full reuse/type comparison for every property in a schema across Scope and Vault (R07)."""
    reviews = []
    effective_global = global_inv or inv
    for prop in schema.properties:
        review = check_property_reuse(prop.name, inv, global_inv=global_inv)
        entry = inv.get(prop.name) or effective_global.get(prop.name)
        if entry is not None:
            review["type_agreement"] = (
                "matches"
                if entry.dominant_type == prop.storage_type.value
                else "differs"
            )
            review["vault_dominant_type"] = entry.dominant_type
            review["schema_storage_type"] = prop.storage_type.value
        reviews.append(review)
    return {
        "schema": schema.to_dict(),
        "validation_errors": schema.validate(),
        "reuse_reviews": reviews,
        "counts": {
            "new": sum(1 for r in reviews if r["status"] == "new"),
            "exact_existing": sum(1 for r in reviews if r["status"] in ("exact_existing", "exact_existing_in_vault_only")),
            "exact_existing_in_scope": sum(1 for r in reviews if r["status"] == "exact_existing"),
            "exact_existing_in_vault_only": sum(1 for r in reviews if r["status"] == "exact_existing_in_vault_only"),
            "case_variant_exists": sum(
                1 for r in reviews if r["status"] == "case_variant_exists"
            ),
            "possible_overlap": sum(
                1 for r in reviews if r["status"] == "possible_overlap"
            ),
        },
    }

