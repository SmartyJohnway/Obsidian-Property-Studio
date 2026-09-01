"""
v1.1.0 Regression Contracts V11-012, V11-013:
Body Wikilink Relationship Analysis (Strict Read-Only) Verification.
"""

from __future__ import annotations

import os
from app.core.body_links import analyze_body_wikilinks, extract_body_wikilinks_from_text
from app.core.manifest import vault_manifest, assert_unchanged
from app.core.model import Note, ParseStatus, PropertyValue, StorageType, VaultScan
from app.core.relationships import build_inbox
from app.core.scope import ScopeMode, ScopeSpec


def test_extract_body_wikilinks_skips_code_and_frontmatter() -> None:
    content = """---
property_link: "[[FrontmatterTarget]]"
---
# Main Content

Here is a link to [[ValidNote]] and an aliased link [[AliasNote|Display Name]].

```python
# Code block should be ignored
print("[[IgnoredInsideCode]]")
```

Inline `[[IgnoredInlineCode]]` should also be ignored.
And finally [[AnotherValidTarget]].
"""
    links = extract_body_wikilinks_from_text(content)
    targets = [t[0] for t in links]

    assert "ValidNote" in targets
    assert "AliasNote" in targets
    assert "AnotherValidTarget" in targets
    # Frontmatter link, code block link, and inline code link must NOT be extracted as body links
    assert "FrontmatterTarget" not in targets
    assert "IgnoredInsideCode" not in targets
    assert "IgnoredInlineCode" not in targets


def test_v11_012_property_and_body_links_strictly_separated(tmp_path: any) -> None:
    """V11-012: Property Links and Body Wikilinks analysis results are strictly separated in models."""
    # Setup a small real vault directory on disk
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    (vault_dir / "Source.md").write_text(
        "---\nrel_prop: \"[[PropTarget]]\"\n---\nBody link to [[BodyTarget]].\n",
        encoding="utf-8",
    )
    (vault_dir / "PropTarget.md").write_text("# Prop Target\n", encoding="utf-8")
    (vault_dir / "BodyTarget.md").write_text("# Body Target\n", encoding="utf-8")

    scan = VaultScan(
        vault_path=str(vault_dir),
        notes=[
            Note(
                path="Source.md",
                parse_status=ParseStatus.OK,
                properties={
                    "rel_prop": PropertyValue("rel_prop", "[[PropTarget]]", StorageType.TEXT, ("[[PropTarget]]",), "[[PropTarget]]")
                },
            ),
            Note(path="PropTarget.md", parse_status=ParseStatus.OK, properties={}),
            Note(path="BodyTarget.md", parse_status=ParseStatus.OK, properties={}),
        ],
    )

    # 1. Property links analysis
    prop_inbox = build_inbox(scan)
    # 2. Body links analysis
    body_res = analyze_body_wikilinks(scan)

    # Model and structure separation:
    assert body_res["analysis_type"] == "body_wikilinks"
    assert "total_links_found" in body_res["summary"]
    # Body links contains BodyTarget, NOT PropTarget
    body_targets = [f["target_raw"] for f in body_res["findings"]]
    assert "BodyTarget" in body_targets
    assert "PropTarget" not in body_targets


def test_v11_013_body_wikilink_analysis_strictly_read_only(tmp_path: any) -> None:
    """V11-013: Body Wikilink analysis is strictly read-only and never modifies Markdown note bodies."""
    vault_dir = tmp_path / "vault_ro"
    vault_dir.mkdir()
    source_file = vault_dir / "Article.md"
    original_text = "# Title\n\nLink to [[MissingNote]] and [[ExistingNote]].\n"
    source_file.write_text(original_text, encoding="utf-8")

    existing_file = vault_dir / "ExistingNote.md"
    existing_file.write_text("# Existing\n", encoding="utf-8")

    manifest_before = vault_manifest(str(vault_dir))

    scan = VaultScan(
        vault_path=str(vault_dir),
        notes=[
            Note(path="Article.md", parse_status=ParseStatus.OK, properties={}),
            Note(path="ExistingNote.md", parse_status=ParseStatus.OK, properties={}),
        ],
    )

    # Run analysis
    res = analyze_body_wikilinks(scan)
    assert res["summary"]["read_only_contract"] == "strict_read_only"
    assert res["summary"]["by_status"]["broken"] == 1
    assert res["summary"]["by_status"]["valid"] == 1

    manifest_after = vault_manifest(str(vault_dir))
    diff = assert_unchanged(manifest_before, manifest_after)
    assert diff["unchanged"] is True
    assert source_file.read_text(encoding="utf-8") == original_text
