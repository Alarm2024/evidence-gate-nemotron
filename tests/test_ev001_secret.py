"""Exploit test for EV-001 hard-coded secret."""

import ast

import pytest

pytestmark = pytest.mark.exploit
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "demo_app" / "config.py"


def test_no_hardcoded_secret_in_config():
    source = CONFIG.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "API_SECRET":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if node.value.value:
                            raise AssertionError(
                                "API_SECRET is hard-coded; use os.environ instead"
                            )
    assert "os.environ" in source or "getenv" in source
