import json
import pytest
from pathlib import Path
from app.core import property_glossary, refactor, inventory
from app.core.scanner import scan_vault
from app.core.scope import ScopeSpec
from app import server


@pytest.fixture
def sample_vault(tmp_path: Path):
    vault = tmp_path / 'glossary_test_vault'
    vault.mkdir()
    (vault / 'FolderA').mkdir()
    (vault / 'FolderB').mkdir()

    (vault / 'FolderA' / 'Task1.md').write_text(
        '---\ntype: task\nstatus: In Progress\nowner: Alice\ncustom_field: alpha\n---\n# Task 1',
        encoding='utf-8',
    )
    (vault / 'FolderA' / 'Task2.md').write_text(
        '---\ntype: task\nstatus: ongoing\nowner: Bob\ncustom_field: beta\n---\n# Task 2',
        encoding='utf-8',
    )
    (vault / 'FolderB' / 'Task3.md').write_text(
        '---\ntype: task\nstatus: active\nowner: Charlie\n---\n# Task 3',
        encoding='utf-8',
    )
    return vault


def test_prop_001_glossary_catalog_completeness():
    catalog = property_glossary.export_glossary_catalog()
    assert len(catalog) >= 35

    core_keys = ['type', 'status', 'owner', 'due_date', 'repo', 'software', 'jurisdiction', 'compliance_status', 'tags', 'priority']
    for k in core_keys:
        assert k in catalog
        entry = catalog[k]
        assert entry['canonical_key'] == k
        assert len(entry['label_zh']) > 0
        assert len(entry['label_en']) > 0
        assert len(entry['short_description_zh']) > 0
        assert len(entry['short_description_en']) > 0
        assert len(entry['usage_hint_zh']) > 0
        assert len(entry['typical_type']) > 0
        assert len(entry['typical_control']) > 0
        assert isinstance(entry['examples'], list)


def test_prop_002_canonical_keys_preserved_exact():
    for key, entry in property_glossary.BUILTIN_PROPERTY_GLOSSARY.items():
        assert key == entry.canonical_key
        assert key == key.lower()
        assert ' ' not in key


def test_prop_003_display_label_presentation_layer():
    assert property_glossary.get_property_display_label('status', locale='zh-Hant') == '狀態 (status)'
    assert property_glossary.get_property_display_label('status', locale='en') == 'Status (status)'
    assert property_glossary.get_property_display_label('due_date', locale='zh-Hant') == '截止日期 (due_date)'
    assert property_glossary.get_property_display_label('due_date', locale='en') == 'Due Date (due_date)'


def test_prop_004_unknown_custom_property_safe_fallback():
    assert property_glossary.get_property_display_label('my_custom_xyz', locale='zh-Hant') == 'my_custom_xyz'
    assert property_glossary.get_property_display_label('my_custom_xyz', locale='en') == 'my_custom_xyz'
    assert property_glossary.get_property_glossary_entry('my_custom_xyz') is None


def test_prop_005_api_glossary_catalog_endpoint():
    res = server.api_glossary_catalog({})
    assert 'catalog' in res
    assert 'total' in res
    assert res['total'] >= 35
    assert 'status' in res['catalog']


def test_prop_006_api_glossary_property_known_detail(sample_vault: Path):
    scan = scan_vault(sample_vault)
    with server.STORE.lock:
        server.STORE.scan = scan
        server.STORE.inventory = inventory.build_inventory(scan)
        server.STORE.scope = ScopeSpec.from_dict({'mode': 'entire_vault'})

    res = server.api_glossary_property({'property': 'status'})
    assert res['canonical_key'] == 'status'
    assert res['is_known'] is True
    assert res['metadata'] is not None
    assert res['vault_usage'] == 3
    assert res['scope_usage'] == 3
    assert len(res['common_values']) > 0


def test_prop_007_api_glossary_property_custom_detail(sample_vault: Path):
    scan = scan_vault(sample_vault)
    with server.STORE.lock:
        server.STORE.scan = scan
        server.STORE.inventory = inventory.build_inventory(scan)
        server.STORE.scope = ScopeSpec.from_dict({'mode': 'entire_vault'})

    res = server.api_glossary_property({'property': 'custom_field'})
    assert res['canonical_key'] == 'custom_field'
    assert res['is_known'] is False
    assert res['metadata'] is None
    assert res['vault_usage'] == 2
    assert len(res['common_values']) == 2


def test_prop_008_refactor_normalize_explicit_mapping(sample_vault: Path):
    scan = scan_vault(sample_vault)
    user_mapping = {
        'In Progress': 'active',
        'ongoing': 'active',
    }
    plan = refactor.plan_normalize(scan, 'status', mapping=user_mapping)
    assert plan['summary']['notes_to_change'] == 2
    assert plan['summary']['groups_to_normalize'] == 1
    ch = plan['changes'][0]
    assert ch['canonical_value'] == 'active'
    assert ch['match_basis'] == 'user controlled mapping'
    assert len(ch['notes_to_change']) == 2
    assert 'FolderA/Task1.md' in ch['notes_to_change']
    assert 'FolderA/Task2.md' in ch['notes_to_change']


def test_prop_009_refactor_normalize_keep_original_untouched(sample_vault: Path):
    scan = scan_vault(sample_vault)
    user_mapping = {
        'In Progress': 'active',
        'ongoing': 'ongoing',
    }
    plan = refactor.plan_normalize(scan, 'status', mapping=user_mapping)
    assert plan['summary']['notes_to_change'] == 1
    assert 'FolderA/Task1.md' in plan['changes'][0]['notes_to_change']
    untouched_vals = [u['value'] for u in plan['untouched_values']]
    assert 'ongoing' in untouched_vals or 'active' in untouched_vals


def test_prop_010_refactor_normalize_api_endpoint(sample_vault: Path):
    scan = scan_vault(sample_vault)
    with server.STORE.lock:
        server.STORE.scan = scan
        server.STORE.inventory = inventory.build_inventory(scan)
        server.STORE.scope = ScopeSpec.from_dict({'mode': 'entire_vault'})

    body = {
        'operation': 'normalize',
        'property': 'status',
        'mapping': {'In Progress': 'active', 'ongoing': 'active'}
    }
    res = server.api_refactor_plan(body)
    assert res['summary']['notes_to_change'] == 2
    assert len(res['changes']) == 1
    assert res['changes'][0]['canonical_value'] == 'active'


def test_prop_011_refactor_normalize_out_of_scope_notes_tracked(sample_vault: Path):
    scan = scan_vault(sample_vault)
    scope = ScopeSpec.from_dict({'mode': 'folders', 'folders': ['FolderA'], 'include_subfolders': True})
    user_mapping = {'In Progress': 'active', 'ongoing': 'active'}
    plan = refactor.plan_normalize(scan, 'status', mapping=user_mapping, scope=scope)
    assert plan['summary']['in_scope_notes_to_change'] == 2
    assert plan['summary']['out_of_scope_notes_to_change'] == 1


def test_prop_012_ui_index_contains_glossary_components():
    html = Path('app/ui/index.html').read_text(encoding='utf-8')
    assert 'GLOSSARY_CACHE' in html
    assert 'formatPropertyLabel' in html
    assert 'renderPropertyBadge' in html
    assert 'openPropertyHelpDrawer' in html
    assert 'prop-help-btn' in html


def test_prop_013_ui_index_contains_normalize_mapping_table():
    html = Path('app/ui/index.html').read_text(encoding='utf-8')
    assert 'refactorNormalizeSection' in html
    assert 'refactorNormalizeTableContainer' in html
    assert 'populateNormalizeTable' in html
    assert 'refactor-norm-target-select' in html


def test_prop_014_i18n_glossary_and_normalize_keys_exist():
    zh = json.loads(Path('app/ui/locales/zh-Hant.json').read_text(encoding='utf-8'))
    en = json.loads(Path('app/ui/locales/en.json').read_text(encoding='utf-8'))

    required_keys = [
        'property.help_title',
        'property.canonical_key',
        'property.display_label',
        'property.purpose',
        'property.usage_hint',
        'property.storage_type',
        'property.ui_control',
        'property.examples',
        'property.scope_usage',
        'property.vault_usage',
        'property.observed_values',
        'property.custom_notice',
        'refactor.normalize_mapping_title',
        'refactor.observed_val_col',
        'refactor.target_val_col',
        'refactor.keep_original',
        'refactor.custom_target_val',
        'refactor.no_observed_values',
        'refactor.normalize_summary',
    ]

    for k in required_keys:
        assert k in zh, f'Missing key {k} in zh-Hant.json'
        assert k in en, f'Missing key {k} in en.json'
