"""Replay mode works offline."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPLAY = REPO / "replays" / "EV-001.json"


def test_replay_cli_offline():
    assert REPLAY.is_file()
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidence_gate",
            "run",
            "--finding",
            "findings/seed/EV-001.md",
            "--replay",
            str(REPLAY),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env={
            k: v
            for k, v in __import__("os").environ.items()
            if k != "NEBIUS_API_KEY"
        },
    )
    assert "Verdict: PROVEN" in proc.stdout
    assert proc.returncode == 0


def test_replay_json_has_no_secrets():
    data = json.loads(REPLAY.read_text(encoding="utf-8"))
    blob = json.dumps(data).lower()
    assert "nebius_api_key" not in blob
    assert "authorization" not in blob
    assert "bearer" not in blob
    for key in ("prompt_hash", "model", "fix_diff", "verdict"):
        assert key in data
