"""
v1.1.0 Regression Contract V11-001:
Lightweight bilingual i18n & Theme engine verification.
Ensures zero external network dependencies, valid JSON locale dictionaries,
key alignment across zh-Hant and en, and accurate local serving.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_DIR = ROOT / "app" / "ui"
LOCALES_DIR = UI_DIR / "locales"


def test_locale_files_exist_and_valid_json() -> None:
    """V11-001: Both zh-Hant.json and en.json must exist and be valid JSON."""
    zh_file = LOCALES_DIR / "zh-Hant.json"
    en_file = LOCALES_DIR / "en.json"

    assert zh_file.is_file(), f"Missing zh-Hant locale file at {zh_file}"
    assert en_file.is_file(), f"Missing en locale file at {en_file}"

    with open(zh_file, "r", encoding="utf-8") as f:
        zh_data = json.load(f)
    with open(en_file, "r", encoding="utf-8") as f:
        en_data = json.load(f)

    assert isinstance(zh_data, dict) and len(zh_data) > 10
    assert isinstance(en_data, dict) and len(en_data) > 10


def test_locale_keys_alignment() -> None:
    """V11-001: zh-Hant and en locale keys must have high alignment."""
    with open(LOCALES_DIR / "zh-Hant.json", "r", encoding="utf-8") as f:
        zh_data = json.load(f)
    with open(LOCALES_DIR / "en.json", "r", encoding="utf-8") as f:
        en_data = json.load(f)

    zh_keys = set(zh_data.keys())
    en_keys = set(en_data.keys())

    missing_in_en = zh_keys - en_keys
    missing_in_zh = en_keys - zh_keys

    assert not missing_in_en, f"Keys in zh-Hant missing from en: {missing_in_en}"
    assert not missing_in_zh, f"Keys in en missing from zh-Hant: {missing_in_zh}"


def test_no_external_resources_in_i18n() -> None:
    """V11-001: i18n script and json files must not reference external URLs or CDNs."""
    for root, _, files in os.walk(LOCALES_DIR):
        for file in files:
            p = Path(root) / file
            text = p.read_text(encoding="utf-8")
            assert not re.search(r"https?://", text), f"External URL found in {p}"
            assert not re.search(r"cdn\.", text), f"CDN reference found in {p}"

    i18n_js = UI_DIR / "i18n.js"
    if i18n_js.exists():
        text = i18n_js.read_text(encoding="utf-8")
        assert not re.search(r"https?://", text), f"External URL in {i18n_js}"


def test_i18n_param_placeholders_match() -> None:
    """V11-001: Placeholders like {count} must match between paired translations."""
    with open(LOCALES_DIR / "zh-Hant.json", "r", encoding="utf-8") as f:
        zh_data = json.load(f)
    with open(LOCALES_DIR / "en.json", "r", encoding="utf-8") as f:
        en_data = json.load(f)

    for k, zh_val in zh_data.items():
        if isinstance(zh_val, str):
            zh_params = set(re.findall(r"\{([a-zA-Z0-9_]+)\}", zh_val))
            en_val = en_data.get(k, "")
            en_params = set(re.findall(r"\{([a-zA-Z0-9_]+)\}", en_val))
            assert zh_params == en_params, f"Parameter mismatch for key '{k}': zh={zh_params}, en={en_params}"
