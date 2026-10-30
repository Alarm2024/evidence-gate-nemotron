"""Rebuild the seed replays and the inlined data in docs/index.html.

Seed replays use hand-written fix diffs (tests/fixtures/seed_fixes/*.diff)
through the real gate pipeline with a mocked model. They are NOT model output.
Run with a key (python -m evidence_gate run --finding ...) to record a model run.

Usage: python scripts/make_seed_replays.py [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from evidence_gate.gate import run_gate  # noqa: E402
from evidence_gate.model_client import MockFixModel  # noqa: E402

SEED_MODEL = "seed (hand-written, mocked model)"
IDS = ("EV-001", "EV-002", "EV-003")
DOCS = REPO / "docs" / "index.html"
START = '<script id="replay-data" type="application/json">\n'
END = "\n  </script>"


def build_records() -> list[dict]:
    records = []
    for fid in IDS:
        diff = (REPO / "tests" / "fixtures" / "seed_fixes" / f"{fid}.diff").read_text(
            encoding="utf-8"
        )
        result = run_gate(
            REPO,
            REPO / "findings" / "seed" / f"{fid}.md",
            MockFixModel(diff),
            model_name=SEED_MODEL,
        )
        records.append(result.replay.to_json())
    return records


def inline_block(records: list[dict]) -> str:
    return json.dumps(records, indent=2)


def replace_inline(html: str, block: str) -> str:
    i = html.index(START) + len(START)
    j = html.index(END, i)
    return html[:i] + block + html[j:]


def main(argv: list[str]) -> int:
    check = "--check" in argv
    records = build_records()
    bad = [r["finding_id"] for r in records if r["verdict"] != "PROVEN"]
    if bad:
        print(f"Seed fix not PROVEN: {bad}", file=sys.stderr)
        return 1
    if check:
        return 0
    for rec in records:
        out = REPO / "replays" / f"{rec['finding_id']}.json"
        out.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out.relative_to(REPO)}")
    DOCS.write_text(replace_inline(DOCS.read_text(encoding="utf-8"), inline_block(records)), encoding="utf-8")
    print(f"Updated {DOCS.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
