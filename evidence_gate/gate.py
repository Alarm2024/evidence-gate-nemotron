"""Core Evidence Gate pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from evidence_gate.finding import Finding, parse_finding
from evidence_gate.model_client import (
    FixModel,
    NemotronFixModel,
    build_fix_prompt,
    prompt_hash,
)
from evidence_gate.patch import apply_unified_diff
from evidence_gate.pytest_runner import PytestResult, run_exploit_test
from evidence_gate.replay import ReplayRecord, record_from_run
from evidence_gate.scope import check_scope
from evidence_gate.verdict import GateOutcome, evaluate_gate
from evidence_gate.workspace import ephemeral_repo


@dataclass
class RunResult:
    finding: Finding
    outcome: GateOutcome
    before: PytestResult
    after: PytestResult
    fix_diff: str
    prompt_hash: str
    model: str
    replay: ReplayRecord

    def write_replay(self, path: Path) -> None:
        self.replay.save(path)


def _read_file_contents(repo_root: Path, paths: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in paths:
        p = repo_root / rel
        out[rel] = p.read_text(encoding="utf-8")
    return out


def run_gate(
    repo_root: Path,
    finding_path: Path,
    model: FixModel,
    *,
    model_name: str,
) -> RunResult:
    finding = parse_finding(finding_path)
    before = run_exploit_test(repo_root, finding.test_path)

    system, user = build_fix_prompt(
        finding.body,
        _read_file_contents(repo_root, finding.affected_files),
    )
    phash = prompt_hash(system, user, model_name)
    fix_diff = model.complete_fix(system, user)

    scope = check_scope(fix_diff, finding.affected_files)

    with ephemeral_repo(repo_root) as sandbox:
        if scope.ok:
            ok, err = apply_unified_diff(sandbox, fix_diff)
            if not ok:
                after = PytestResult(
                    exit_code=2,
                    stdout="",
                    stderr=f"Failed to apply fix diff: {err}",
                )
            else:
                after = run_exploit_test(sandbox, finding.test_path)
        else:
            after = PytestResult(
                exit_code=2,
                stdout="",
                stderr="Skipped post-fix test because diff is out of scope",
            )

    outcome = evaluate_gate(before, after, scope)
    replay = record_from_run(
        finding_id=finding.finding_id,
        prompt_hash=phash,
        model=model_name,
        fix_diff=fix_diff,
        before=before,
        after=after,
        outcome=outcome,
        affected_files=finding.affected_files,
    )
    return RunResult(
        finding=finding,
        outcome=outcome,
        before=before,
        after=after,
        fix_diff=fix_diff,
        prompt_hash=phash,
        model=model_name,
        replay=replay,
    )


def run_replay(repo_root: Path, replay_path: Path) -> RunResult:
    record = ReplayRecord.load(replay_path)
    finding_path = repo_root / "findings" / "seed" / f"{record.finding_id}.md"
    finding = parse_finding(finding_path) if finding_path.is_file() else Finding(
        finding_id=record.finding_id,
        title=record.finding_id,
        body="",
        affected_files=tuple(record.affected_files or []),
        test_path=f"tests/test_{record.finding_id.lower().replace('-', '_')}.py",
    )
    if record.affected_files:
        allowed = tuple(record.affected_files)
    else:
        allowed = finding.affected_files

    before = run_exploit_test(repo_root, finding.test_path)
    scope = check_scope(record.fix_diff, allowed)

    with ephemeral_repo(repo_root) as sandbox:
        if scope.ok:
            ok, err = apply_unified_diff(sandbox, record.fix_diff)
            if not ok:
                after = PytestResult(
                    exit_code=2,
                    stdout="",
                    stderr=f"Failed to apply replay diff: {err}",
                )
            else:
                after = run_exploit_test(sandbox, finding.test_path)
        else:
            after = PytestResult(
                exit_code=2,
                stdout="",
                stderr="Skipped post-fix test because replay diff is out of scope",
            )

    outcome = evaluate_gate(before, after, scope)
    return RunResult(
        finding=finding,
        outcome=outcome,
        before=before,
        after=after,
        fix_diff=record.fix_diff,
        prompt_hash=record.prompt_hash,
        model=record.model,
        replay=record,
    )


def default_model_name(fast: bool = False) -> str:
    from evidence_gate import FAST_MODEL, MAIN_MODEL

    return FAST_MODEL if fast else MAIN_MODEL


def make_live_model(fast: bool = False) -> NemotronFixModel:
    return NemotronFixModel(model=default_model_name(fast=fast))
