"""Check whether a unified diff stays within allowed files."""

from __future__ import annotations

import re
from dataclasses import dataclass


_DIFF_PATH = re.compile(r"^(?:---|\+\+\+)\s+(?:a/|b/)?(?P<path>.+)$", re.MULTILINE)


@dataclass(frozen=True)
class ScopeCheck:
    ok: bool
    touched: tuple[str, ...]
    extra: tuple[str, ...]
    reason: str


def normalize_repo_path(path: str) -> str:
    p = path.strip()
    if p.startswith("a/") or p.startswith("b/"):
        p = p[2:]
    return p.replace("\\", "/")


def paths_in_diff(diff_text: str) -> set[str]:
    paths: set[str] = set()
    for line in diff_text.splitlines():
        m = _DIFF_PATH.match(line)
        if not m:
            continue
        raw = m.group("path")
        if raw == "/dev/null":
            continue
        paths.add(normalize_repo_path(raw))
    return paths


def check_scope(diff_text: str, allowed_files: tuple[str, ...]) -> ScopeCheck:
    allowed = {normalize_repo_path(f) for f in allowed_files}
    touched = tuple(sorted(paths_in_diff(diff_text)))
    extra = tuple(sorted(p for p in touched if p not in allowed))
    if extra:
        return ScopeCheck(
            ok=False,
            touched=touched,
            extra=extra,
            reason=f"Diff touches files outside finding scope: {', '.join(extra)}",
        )
    if not touched:
        return ScopeCheck(
            ok=False,
            touched=touched,
            extra=extra,
            reason="Diff contains no file paths",
        )
    return ScopeCheck(
        ok=True,
        touched=touched,
        extra=extra,
        reason="Diff only modifies files named in the finding",
    )
