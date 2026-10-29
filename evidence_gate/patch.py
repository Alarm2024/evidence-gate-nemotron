"""Apply unified diffs to a working tree."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def apply_unified_diff(repo_root: Path, diff_text: str) -> tuple[bool, str]:
    if not diff_text.strip():
        return False, "Empty diff"
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".patch",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(diff_text)
        if not diff_text.endswith("\n"):
            tmp.write("\n")
        patch_path = tmp.name

    try:
        proc = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", patch_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return True, ""
        proc2 = subprocess.run(
            ["patch", "-p1", "--forward", "-i", patch_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        if proc2.returncode in (0, 1):
            return True, proc2.stderr
        return False, (proc.stderr or proc2.stderr or "patch failed").strip()
    finally:
        Path(patch_path).unlink(missing_ok=True)
