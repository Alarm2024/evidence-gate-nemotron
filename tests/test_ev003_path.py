"""Exploit test for EV-003 path traversal."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.exploit

FILES = Path(__file__).resolve().parent.parent / "demo_app" / "files.py"


def test_path_traversal_blocked():
    source = FILES.read_text(encoding="utf-8")
    lowered = source.lower()
    assert "resolve(" in source, "Paths must be resolved"
    assert "relative_to" in lowered or "is_relative_to" in lowered or "commonpath" in lowered, (
        "Storage root must be enforced after resolve()"
    )
