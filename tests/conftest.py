"""Shared pytest fixtures."""

from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FIXTURE_ROOT = os.path.join(ROOT, "fixtures")
MAIN_VAULT = os.path.join(FIXTURE_ROOT, "vaults", "main_vault")
EMPTY_VAULT = os.path.join(FIXTURE_ROOT, "vaults", "empty_vault")
PROPOSALS = os.path.join(FIXTURE_ROOT, "proposals")


@pytest.fixture(scope="session")
def oracle() -> dict:
    with open(os.path.join(FIXTURE_ROOT, "vaults", "oracle.json"), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def main_vault() -> str:
    return MAIN_VAULT


@pytest.fixture(scope="session")
def empty_vault() -> str:
    return EMPTY_VAULT


@pytest.fixture(scope="session")
def scan(main_vault):
    from app.core.scanner import scan_vault

    return scan_vault(main_vault)


@pytest.fixture(scope="session")
def inv(scan):
    from app.core.inventory import build_inventory

    return build_inventory(scan)


@pytest.fixture()
def out_dir(tmp_path) -> str:
    return str(tmp_path / "exports")
