"""Generate a large synthetic vault for the performance benchmark (OPS-AC-028).

Usage:
    python scripts/make_benchmark_vault.py <target_dir> [note_count]

Deterministic content (seeded), so repeat runs are comparable.
"""

from __future__ import annotations

import os
import random
import shutil
import sys

STATUSES = ["active", "Active", "ACTIVE", "on hold", "done", "archived"]
AREAS = ["research", "operations", "客戶服務", "platform", "finance"]
TAGS = ["work", "urgent", "研究", "personal", "review"]


def build(target: str, count: int = 5000, seed: int = 20260831) -> None:
    rng = random.Random(seed)
    if os.path.isdir(target):
        shutil.rmtree(target)
    os.makedirs(target, exist_ok=True)
    os.makedirs(os.path.join(target, ".obsidian"), exist_ok=True)
    with open(os.path.join(target, ".obsidian", "app.json"), "w", encoding="utf-8") as fh:
        fh.write("{}\n")

    people = [f"Person {i:03d}" for i in range(40)]
    for name in people:
        folder = os.path.join(target, "People")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"{name}.md"), "w", encoding="utf-8") as fh:
            fh.write(f"---\ntype: person\nstatus: active\n---\n\n{name}\n")

    for i in range(count):
        folder = os.path.join(target, f"Notes/{i // 250:03d}")
        os.makedirs(folder, exist_ok=True)
        name = f"Note {i:05d}" if i % 7 else f"筆記 {i:05d}"
        lines = ["---", "type: record", f"status: {rng.choice(STATUSES)}"]
        if i % 3 == 0:
            lines.append(f"owner: \"[[{rng.choice(people)}]]\"")
        if i % 4 == 0:
            lines.append(f"owner_name: {rng.choice(people)}")
        if i % 5 == 0:
            lines.append(f"due_date: 2026-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}")
        if i % 11 == 0:
            lines.append("due_date: not scheduled")  # duplicate + type conflict source
        lines.append(f"area: {rng.choice(AREAS)}")
        lines.append("tags:")
        for tag in rng.sample(TAGS, k=2):
            lines.append(f"  - {tag}")
        if i % 97 == 0:
            lines.append("broken: [unclosed")  # malformed frontmatter
        lines.append("---")
        lines.append("")
        lines.append(f"Body of note {i}. The product never rewrites this text.")
        with open(os.path.join(folder, f"{name}.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    target = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    build(target, count)
    total = sum(len(files) for _, _, files in os.walk(target))
    print(f"Created {total} files in {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
