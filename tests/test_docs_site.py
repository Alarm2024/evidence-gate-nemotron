"""docs/index.html plays bundled replays with zero network calls."""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "docs" / "index.html"
IDS = ("EV-001", "EV-002", "EV-003")


def _html() -> str:
    return INDEX.read_text(encoding="utf-8")


def _inline_records() -> list[dict]:
    m = re.search(
        r'<script id="replay-data" type="application/json">\s*(.*?)\s*</script>',
        _html(),
        re.DOTALL,
    )
    assert m, "inline replay data missing"
    return json.loads(m.group(1))


def test_no_remote_resources():
    html = _html()
    assert not re.search(r"""(?:src|href)\s*=\s*["']?\s*(?:https?:)?//""", html, re.I)
    assert not re.search(r"@import|url\(\s*['\"]?(?:https?:)?//", html, re.I)
    for api in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "import("):
        assert api not in html, api
    assert "<script src" not in html.lower()
    assert "<link" not in html.lower()


def test_inline_data_matches_replays():
    inline = {r["finding_id"]: r for r in _inline_records()}
    assert set(inline) == set(IDS)
    for fid in IDS:
        rec = json.loads((REPO / "replays" / f"{fid}.json").read_text(encoding="utf-8"))
        for key in ("verdict", "fix_diff", "model", "prompt_hash", "affected_files"):
            assert inline[fid][key] == rec[key], (fid, key)


def test_pages_ready():
    assert (REPO / "docs" / ".nojekyll").is_file()
    assert _html().lstrip().lower().startswith("<!doctype html>")
