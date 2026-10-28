"""Ephemeral copies of the repo for safe patch application."""

from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

_SKIP = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "node_modules"}


def _copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name in _SKIP:
            continue
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(item, target)


@contextmanager
def ephemeral_repo(source_root: Path):
    tmp = Path(tempfile.mkdtemp(prefix="evidence-gate-"))
    try:
        _copy_tree(source_root, tmp)
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
