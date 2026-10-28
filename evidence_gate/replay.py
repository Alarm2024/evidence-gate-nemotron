"""Replay records: offline verification without API access."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from evidence_gate.pytest_runner import PytestResult
from evidence_gate.verdict import GateOutcome, Verdict


@dataclass
class ReplayRecord:
    finding_id: str
    prompt_hash: str
    model: str
    fix_diff: str
    test_before: dict
    test_after: dict
    verdict: str
    reason: str
    affected_files: list[str] | None = None

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ReplayRecord:
        return cls(
            finding_id=str(data["finding_id"]),
            prompt_hash=str(data["prompt_hash"]),
            model=str(data["model"]),
            fix_diff=str(data["fix_diff"]),
            test_before=dict(data["test_before"]),
            test_after=dict(data["test_after"]),
            verdict=str(data["verdict"]),
            reason=str(data["reason"]),
            affected_files=list(data["affected_files"]) if data.get("affected_files") else None,
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_json(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> ReplayRecord:
        return cls.from_json(json.loads(path.read_text(encoding="utf-8")))


def record_from_run(
    *,
    finding_id: str,
    prompt_hash: str,
    model: str,
    fix_diff: str,
    before: PytestResult,
    after: PytestResult,
    outcome: GateOutcome,
    affected_files: tuple[str, ...],
) -> ReplayRecord:
    return ReplayRecord(
        finding_id=finding_id,
        prompt_hash=prompt_hash,
        model=model,
        fix_diff=fix_diff,
        test_before=before.to_dict(),
        test_after=after.to_dict(),
        verdict=outcome.verdict.value,
        reason=outcome.reason,
        affected_files=list(affected_files),
    )


def replay_matches_live(
    recorded: ReplayRecord,
    live_before: PytestResult,
    live_after: PytestResult,
    live_outcome: GateOutcome,
) -> bool:
    return (
        recorded.verdict == live_outcome.verdict.value
        and live_before.exit_code == recorded.test_before.get("exit_code")
        and live_after.exit_code == recorded.test_after.get("exit_code")
    )
