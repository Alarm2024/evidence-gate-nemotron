"""Verdict types and evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from evidence_gate.pytest_runner import PytestResult
from evidence_gate.scope import ScopeCheck


class Verdict(str, Enum):
    PROVEN = "PROVEN"
    NOT_PROVEN = "NOT PROVEN"
    OUT_OF_SCOPE = "OUT OF SCOPE"


@dataclass(frozen=True)
class GateOutcome:
    verdict: Verdict
    reason: str

    def to_dict(self) -> dict:
        return {"verdict": self.verdict.value, "reason": self.reason}


def evaluate_gate(
    before: PytestResult,
    after: PytestResult,
    scope: ScopeCheck,
) -> GateOutcome:
    if not scope.ok:
        return GateOutcome(Verdict.OUT_OF_SCOPE, scope.reason)
    if before.passed:
        return GateOutcome(
            Verdict.NOT_PROVEN,
            "Exploit test passed before fix; expected failure while vulnerability exists",
        )
    if not after.passed:
        return GateOutcome(
            Verdict.NOT_PROVEN,
            "Exploit test still fails after fix; vulnerability may remain",
        )
    return GateOutcome(
        Verdict.PROVEN,
        "Exploit test failed before and passed after; diff stayed in scope",
    )
