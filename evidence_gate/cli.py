"""Command-line interface for Evidence Gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from evidence_gate import FAST_MODEL, MAIN_MODEL
from evidence_gate.gate import make_live_model, run_gate, run_replay
from evidence_gate.model_client import list_reachable_models


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def cmd_models(_: argparse.Namespace) -> int:
    try:
        ids = list_reachable_models()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for mid in ids:
        marker = ""
        if mid == MAIN_MODEL:
            marker = "  (main)"
        elif mid == FAST_MODEL:
            marker = "  (fast)"
        print(f"{mid}{marker}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    root = _repo_root()
    finding = Path(args.finding)
    if not finding.is_file():
        print(f"Finding not found: {finding}", file=sys.stderr)
        return 1

    if args.replay:
        replay_path = Path(args.replay)
        if not replay_path.is_file():
            print(f"Replay not found: {replay_path}", file=sys.stderr)
            return 1
        result = run_replay(root, replay_path)
        print(f"Replay file: {replay_path}")
    else:
        model = make_live_model(fast=args.fast)
        result = run_gate(
            root,
            finding,
            model,
            model_name=model.model,
        )
        out = root / "replays" / f"{result.finding.finding_id}.json"
        result.write_replay(out)
        print(f"Wrote replay: {out}")

    print(f"Finding: {result.finding.finding_id}")
    print(f"Model: {result.model}")
    print(f"Prompt hash: {result.prompt_hash}")
    print(f"Verdict: {result.outcome.verdict.value}")
    print(f"Reason: {result.outcome.reason}")
    print("--- test before ---")
    print(result.before.stdout or result.before.stderr)
    print("--- test after ---")
    print(result.after.stdout or result.after.stderr)
    return 0 if result.outcome.verdict.value == "PROVEN" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evidence_gate", description="Evidence Gate CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("models", help="List reachable Nebius Token Factory models")

    run_p = sub.add_parser("run", help="Run gate on a finding or replay file")
    run_p.add_argument(
        "--finding",
        required=True,
        help="Path to finding markdown (e.g. findings/seed/EV-001.md)",
    )
    run_p.add_argument(
        "--replay",
        help="Replay JSON path; no API key or network required",
    )
    run_p.add_argument(
        "--fast",
        action="store_true",
        help=f"Use fast model ({FAST_MODEL}) instead of main",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "models":
        return cmd_models(args)
    if args.command == "run":
        return cmd_run(args)
    parser.error(f"Unknown command: {args.command}")
    return 2
