"""Static integrity checks for the single-file browser UI.

No browser automation is available in the verification environment, so instead
of claiming an unverified click-through, these tests check the things that can
be verified mechanically: the script parses, every element the script touches
exists, every endpoint it calls is implemented by the server, and the page
references no external resources (local-first / offline).
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest


from app.server import ROUTES

UI_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "ui", "index.html"
)


@pytest.fixture(scope="module")
def html() -> str:
    return open(UI_PATH, encoding="utf-8").read()


@pytest.fixture(scope="module")
def script(html: str) -> str:
    match = re.search(r"<script>(.*)</script>", html, re.S)
    assert match, "UI must contain an inline script"
    return match.group(1)


def test_script_parses(script, tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to syntax-check the UI script")
    path = tmp_path / "ui.js"
    path.write_text(script, encoding="utf-8")
    result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_every_referenced_element_exists(html, script):
    ids = set(re.findall(r'\$\("([^"]+)"\)', script))
    declared = set(re.findall(r'id="([^"]+)"', html))
    # ids created dynamically by the script itself
    dynamic = {"propDetail", "healthFindings", "acceptProposalBtn", "rejectProposalBtn", "noteList"}
    missing = ids - declared - dynamic
    assert not missing, f"UI script references unknown element ids: {sorted(missing)}"


def test_every_called_endpoint_exists(script):
    called = set(re.findall(r'api\("(/api/[^"]+)"', script))
    assert called, "UI must call the local API"
    unknown = called - set(ROUTES)
    assert not unknown, f"UI calls undefined endpoints: {sorted(unknown)}"


def test_no_external_resources(html):
    for pattern in (r'src="https?://', r'href="https?://', r"@import", "cdn."):
        assert not re.search(pattern, html), f"UI must not load external resources ({pattern})"


def test_untrusted_vault_content_is_escaped(script):
    assert "function esc" in script or "const esc" in script
    # innerHTML interpolations of vault-derived values go through esc()
    raw = re.findall(r"innerHTML\s*=\s*`([^`]*)`", script, re.S)
    joined = "\n".join(raw)
    suspicious = re.findall(r"\$\{(?!esc\()(?![^}]*\bstat\()[^}]*\b(key|value|path|note|title)\b[^}]*\}", joined)
    assert not suspicious, f"unescaped vault content in UI: {suspicious[:5]}"





def test_ui_states_the_safety_contract(html):
    for phrase in ("read-only", "never changes it", "no vault"):
        assert phrase.lower() in html.lower()
    assert "Verify vault untouched" in html


def test_copy_buttons_fail_closed_on_invalid_fill(html, script):
    """UI must fail closed on invalid/ambiguous fill: buttons disabled by default,
    enabled only when valid, and click handlers refuse copying invalid state."""
    assert 'id="copyFmBtn" disabled' in html
    assert 'id="copyYamlBtn" disabled' in html
    assert "!S.fill.valid" in script
    assert "canCopy" in script or ("d.valid" in script and "disabled" in script)


def test_every_init_setup_handler_is_defined(script):
    """Bug regression from M014 walkthrough: Every setupXxx() called in init() MUST be defined."""
    # Find all setupXxx() called within function init()
    init_match = re.search(r"async\s+function\s+init\s*\(\)\s*\{(.*?)\n\}\n\nfunction updateContextBarLabels", script, re.S)
    assert init_match, "init() function body not found"
    init_body = init_match.group(1)

    setup_calls = set(re.findall(r"\b(setup[A-Za-z0-9_]+)\s*\(\)", init_body))
    assert setup_calls, "init() must call setup handlers"

    for func_name in sorted(setup_calls):
        assert f"function {func_name}" in script or f"const {func_name}" in script, (
            f"Fatal startup defect: '{func_name}()' is invoked in init() but function definition is missing!"
        )


def test_load_design_presets_is_called_in_init(script):
    assert "loadDesignPresets()" in script, "loadDesignPresets() must be invoked on initialization"


def test_headless_browser_startup_execution_no_uncaught_errors(html, script, tmp_path):
    """Execute the actual browser JavaScript in a simulated headless DOM harness using Node.js.
    
    Verifies:
    1. Zero uncaught runtime errors during init() execution.
    2. loadDesignPresets() populates designObjectsList and designNeedsList with non-empty DOM content.
    3. Primary CTA buttons (designSuggestBtn, relAnalyzeBtn, runRefactorPlanBtn) are wired to functions.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is not available for headless DOM smoke test")

    declared_ids = set(re.findall(r'id="([^"]+)"', html))
    i18n_path = Path(__file__).resolve().parent.parent / "app" / "ui" / "i18n.js"
    i18n_script = i18n_path.read_text(encoding="utf-8") if i18n_path.exists() else ""

    harness_code = f"""
const fs = require('fs');
const path = require('path');

// Mock browser DOM & Web APIs
const elements = {{}};
const declaredIds = {list(declared_ids)};
declaredIds.forEach(id => {{
  elements[id] = {{
    id: id,
    value: '',
    textContent: '',
    innerHTML: '',
    style: {{ display: 'block' }},
    classList: {{ add: () => {{}}, remove: () => {{}} }},
    onclick: null,
    onchange: null,
    oninput: null,
    focus: () => {{}},
    options: [{{ value: '' }}],
    checked: false,
    disabled: false,
    setAttribute: () => {{}},
    getAttribute: () => null,
    hasAttribute: () => false
  }};
}});

global.document = {{
  documentElement: {{
    getAttribute: (attr) => 'dark',
    setAttribute: (attr, val) => {{}}
  }},
  getElementById: (id) => elements[id] || {{
    id: id,
    value: '',
    textContent: '',
    innerHTML: '',
    style: {{ display: 'block' }},
    classList: {{ add: () => {{}}, remove: () => {{}} }},
    onclick: null,
    onchange: null,
    oninput: null,
    focus: () => {{}},
    options: [{{ value: '' }}],
    checked: false,
    disabled: false,
    setAttribute: () => {{}},
    getAttribute: () => null,
    hasAttribute: () => false
  }},
  querySelectorAll: (selector) => [],
  addEventListener: (event, handler) => {{}}
}};

global.window = {{
  addEventListener: (event, handler) => {{}}
}};

global.localStorage = {{
  getItem: (key) => null,
  setItem: (key, val) => {{}},
  removeItem: (key) => {{}}
}};

global.fetch = async (url, opts) => {{
  if (url.includes('/api/design/presets')) {{
    return {{
      ok: true,
      json: async () => ({{
        objects: [{{ id: 'equipment', name_zh: '設備', name_en: 'Equipment' }}],
        needs: [{{ id: 'location', name_zh: '存放位置', name_en: 'Location' }}]
      }})
    }};
  }}
  return {{
    ok: true,
    json: async () => ({{}})
  }};
}};

// Include i18n.js
{i18n_script}

// Execute index.html script
{script}

async function runSmoke() {{
  try {{
    // Mock I18N locales
    I18N.locales['zh-Hant'] = {{}};
    I18N.locales['en'] = {{}};
    I18N.currentLocale = 'zh-Hant';

    // Run full browser initialization
    await init();

    // Verify critical assertions
    const objList = elements['designObjectsList'];
    const needList = elements['designNeedsList'];
    if (!objList || !objList.innerHTML.includes('equipment')) {{
      throw new Error('designObjectsList was not populated after init()');
    }}
    if (!needList || !needList.innerHTML.includes('location')) {{
      throw new Error('designNeedsList was not populated after init()');
    }}

    if (typeof elements['designSuggestBtn'].onclick !== 'function') {{
      throw new Error('designSuggestBtn.onclick was not wired');
    }}
    if (typeof elements['relAnalyzeBtn'].onclick !== 'function') {{
      throw new Error('relAnalyzeBtn.onclick was not wired');
    }}
    if (typeof elements['runRefactorPlanBtn'].onclick !== 'function') {{
      throw new Error('runRefactorPlanBtn.onclick was not wired');
    }}

    console.log('HEADLESS_SMOKE_PASS');
  }} catch (err) {{
    console.error('HEADLESS_SMOKE_ERROR:', err);
    process.exit(1);
  }}
}}

runSmoke();
"""
    test_file = tmp_path / "headless_smoke.js"
    test_file.write_text(harness_code, encoding="utf-8")

    res = subprocess.run([node, str(test_file)], capture_output=True, text=True)
    assert res.returncode == 0, f"Headless startup failed with error:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    assert "HEADLESS_SMOKE_PASS" in res.stdout
