"""File helpers (EV-003: path traversal)."""

from __future__ import annotations

from pathlib import Path

_STORAGE = Path(__file__).resolve().parent / "storage"


def read_user_file(relative_name: str) -> str:
    _STORAGE.mkdir(parents=True, exist_ok=True)
    # BUG EV-003: no normalization allows path traversal.
    target = _STORAGE / relative_name
    return target.read_text(encoding="utf-8")
