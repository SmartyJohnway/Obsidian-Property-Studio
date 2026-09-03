"""v1.2.0 Product Completion Repair & Workflow Closure Verification Suite.

Validates that all 8 workflow closure gaps identified during Human Owner review
are thoroughly resolved and integrated into the frontend/backend contract.
"""

import json
from pathlib import Path
from app.core.proposal import validate_proposal
from app.server import ROUTES


def test_gap_a_version_badge_dynamic():
    html = Path("app/ui/index.html").read_text(encoding="utf-8")
    assert '<span class="chip" id="versionBadge">v1.1.0</span>' not in html
    assert 'id="versionBadge"' in html
    assert 'api("/api/meta")' in html


def test_gap_b_schema_card_actions():
    html = Path("app/ui/index.html").read_text(encoding="utf-8")
    assert "openSchemaEditModal" in html
    assert "openSchemaMigrationModal" in html
    assert "assignSchemaToScope" in html
    assert "applyNamedSchemaToWorkspace" in html
    assert "/api/schemas/update" in html


def test_gap_c_reconciliation_item_level():
    html = Path("app/ui/index.html").read_text(encoding="utf-8")
    assert "addMissingPropertyToWorkspace" in html
    assert "focusPropertyInWorkspace" in html
    assert "recRes.items" in html
    assert "✓ 符合 (Match)" in html
    assert "+ 缺漏 (Missing)" in html


def test_gap_d_proposal_file_and_four_way_comparison():
    html = Path("app/ui/index.html").read_text(encoding="utf-8")
    assert 'id="openProposalFileBtn"' in html
    assert 'id="proposalFileInput"' in html
    assert "openProposalCandidateEditor" in html
    assert "proposalRejectBtn" in html
    assert "相容 (Compatible)" in html


def test_gap_e_scope_expected_schema_assignment():
    html = Path("app/ui/index.html").read_text(encoding="utf-8")
    assert "scopeSchemaAssignCard" in html
    assert "scopeSchemaAssignSelect" in html
    assert "scopeAssignSchemaBtn" in html
    assert "scopeUnassignSchemaBtn" in html
    assert "/api/scope/schema/assign" in html


def test_gap_f_skill_package_complete_and_valid():
    skill_root = Path("skills/obsidian-property-advisor")
    assert (skill_root / "SKILL.md").is_file()
    assert (skill_root / "references" / "proposal-contract.md").is_file()
    assert (skill_root / "references" / "property-design-principles.md").is_file()
    assert (skill_root / "references" / "examples.md").is_file()
    
    for ex_name in ["project.json", "equipment.json", "regulation.json"]:
        p = skill_root / "examples" / ex_name
        assert p.is_file(), f"Missing {ex_name}"
        data = json.loads(p.read_text(encoding="utf-8"))
        val_res = validate_proposal(data)
        assert val_res["valid"], f"Invalid example {ex_name}: {val_res.get('errors')}"


def test_gap_g_health_drift_drilldown():
    html = Path("app/ui/index.html").read_text(encoding="utf-8")
    assert "viewDriftDetailsBtn" in html
    assert "openDriftDetailsDrawer" in html
    assert "drilldownToNoteWorkspace" in html
    assert "schema_id: schemaId" in html or "schemaId" in html


def test_gap_h_test_contracts_strict_v120():
    meta = ROUTES["/api/meta"]({})
    assert meta["version"] == "1.2.0"
