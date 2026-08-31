"""Static integrity checks for the single-file browser UI.

No browser automation is available in the verification environment, so instead
of claiming an unverified click-through, these tests check the things that can
be verified mechanically: the script parses, every element the script touches
exists, every endpoint it calls is implemented by the server, and the page
references no external resources (local-first / offline).
"""

from __future__ import annotations

import os
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
