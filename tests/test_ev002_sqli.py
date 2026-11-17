"""Exploit test for EV-002 SQL injection."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.exploit

DB = Path(__file__).resolve().parent.parent / "demo_app" / "db.py"


def test_db_uses_parameterized_queries():
    source = DB.read_text(encoding="utf-8")
    assert "f\"SELECT" not in source and "f'SELECT" not in source, (
        "SQL built with f-string; use parameterized execute()"
    )
    assert "execute(" in source
    assert "?" in source or "%s" in source
