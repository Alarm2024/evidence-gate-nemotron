"""Tiny data access layer (EV-002: SQL injection)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_DB = Path(__file__).resolve().parent / "demo.db"


def get_user_display_name(user_id: str) -> str:
    """Return a display label for a user id."""
    conn = sqlite3.connect(_DB)
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT NOT NULL)"
        )
        conn.commit()
        # BUG EV-002: string interpolation enables SQL injection.
        query = f"SELECT name FROM users WHERE id = '{user_id}'"
        cur.execute(query)
        row = cur.fetchone()
        return row[0] if row else ""
    finally:
        conn.close()
