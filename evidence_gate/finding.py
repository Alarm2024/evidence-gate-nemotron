"""Parse security finding markdown files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    finding_id: str
    title: str
    body: str
    affected_files: tuple[str, ...]
    test_path: str


_FILE_LINE = re.compile(
    r"^(?:-\s+|`\s*)?(?P<path>demo_app/[a-zA-Z0-9_./-]+\.(?:py|md|txt|json))(?:\s*`|(?:\s|$))",
    re.MULTILINE,
)
_TEST_LINE = re.compile(
    r"^##\s+Exploit test\s*\n\s*(?P<path>tests/test_[^\s]+\.py)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_ID_FROM_NAME = re.compile(r"(EV-\d{3})", re.IGNORECASE)


def parse_finding(path: Path) -> Finding:
    text = path.read_text(encoding="utf-8")
    stem = path.stem.upper()
    match = _ID_FROM_NAME.search(stem)
    if not match:
        raise ValueError(f"Cannot infer finding id from {path.name}")
    finding_id = match.group(1).upper()

    title = finding_id
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    files_section = re.search(
        r"##\s+Affected files\s*\n(?P<body>(?:.*\n)*?)(?:\n##|\Z)",
        text,
        re.IGNORECASE,
    )
    affected: list[str] = []
    if files_section:
        for m in _FILE_LINE.finditer(files_section.group("body")):
            p = m.group("path").strip()
            if p not in affected:
                affected.append(p)

    if not affected:
        for m in _FILE_LINE.finditer(text):
            p = m.group("path").strip()
            if p not in affected:
                affected.append(p)

    test_match = _TEST_LINE.search(text)
    if test_match:
        test_path = test_match.group("path").strip()
    else:
        test_path = f"tests/test_{finding_id.lower().replace('-', '_')}.py"

    if not affected:
        raise ValueError(f"No affected files listed in {path}")

    return Finding(
        finding_id=finding_id,
        title=title,
        body=text,
        affected_files=tuple(affected),
        test_path=test_path,
    )
