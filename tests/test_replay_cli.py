"""Replay mode works with no API key and no network, for every seed replay."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NETBLOCK = REPO / "tests" / "netblock"
IDS = ("EV-001", "EV-002", "EV-003")


def _offline_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "NEBIUS_API_KEY"}
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (str(NETBLOCK), env.get("PYTHONPATH", "")) if p
    )
    for proxy in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        env.pop(proxy, None)
    return env


def test_netblock_really_blocks():
    proc = subprocess.run(
        [sys.executable, "-c", "import socket; socket.create_connection(('example.com', 443), 1)"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=_offline_env(),
    )
    assert proc.returncode != 0
    assert "network access blocked" in proc.stderr


@pytest.mark.parametrize("fid", IDS)
def test_replay_cli_offline_no_key(fid):
    replay = REPO / "replays" / f"{fid}.json"
    assert replay.is_file()
    proc = subprocess.run(
        [sys.executable, "-m", "evidence_gate", "run", "--replay", str(replay)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=_offline_env(),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"Finding: {fid}" in proc.stdout
    assert "Verdict: PROVEN" in proc.stdout
    assert "network access blocked" not in proc.stdout + proc.stderr


def test_replay_mode_does_not_import_openai():
    code = (
        "import sys; from evidence_gate.cli import main; "
        "rc = main(['run', '--replay', 'replays/EV-001.json']); "
        "assert 'openai' not in sys.modules, 'openai imported in replay mode'; "
        "raise SystemExit(rc)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=_offline_env(),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_run_without_key_fails_cleanly():
    proc = subprocess.run(
        [sys.executable, "-m", "evidence_gate", "run", "--finding", "findings/seed/EV-001.md"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=_offline_env(),
    )
    assert proc.returncode == 1
    assert "NEBIUS_API_KEY is not set" in proc.stderr


def test_replay_mismatch_is_reported(tmp_path):
    data = json.loads((REPO / "replays" / "EV-001.json").read_text(encoding="utf-8"))
    data["verdict"] = "NOT PROVEN"
    bad = tmp_path / "EV-001.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "evidence_gate", "run", "--replay", str(bad)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=_offline_env(),
    )
    assert proc.returncode == 3
    assert "Replay mismatch" in proc.stderr


@pytest.mark.parametrize("fid", IDS)
def test_replay_json_has_no_secrets(fid):
    data = json.loads((REPO / "replays" / f"{fid}.json").read_text(encoding="utf-8"))
    blob = json.dumps(data).lower()
    for needle in ("nebius_api_key", "authorization", "bearer", "api_key", "x-api-key"):
        assert needle not in blob, needle
    assert not re.search(r"sk-[a-z0-9]{8,}", blob)
    for key in ("prompt_hash", "model", "fix_diff", "verdict"):
        assert key in data


def test_seed_replays_reproduce():
    proc = subprocess.run(
        [sys.executable, "scripts/make_seed_replays.py", "--check"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=_offline_env(),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
