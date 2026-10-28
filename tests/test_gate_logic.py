"""Gate logic with mocked Nemotron responses (no API key)."""

from pathlib import Path

import pytest

from evidence_gate.finding import parse_finding
from evidence_gate.gate import run_gate
from evidence_gate.model_client import MockFixModel
from evidence_gate.pytest_runner import run_exploit_test
from evidence_gate.replay import ReplayRecord, record_from_run
from evidence_gate.scope import check_scope
from evidence_gate.verdict import Verdict, evaluate_gate

REPO = Path(__file__).resolve().parent.parent


GOOD_EV001_DIFF = """\
--- a/demo_app/config.py
+++ b/demo_app/config.py
@@ -1,8 +1,10 @@
 \"\"\"Application configuration (EV-001: hard-coded secret).\"\"\"
 
+import os
+
 # BUG EV-001: secret must come from environment, not source control.
-API_SECRET = "hardcoded-demo-secret-do-not-ship"
+API_SECRET = os.environ.get("API_SECRET", "")
 
 
 def get_api_secret() -> str:
     return API_SECRET
"""

STILL_VULNERABLE_DIFF = """\
--- a/demo_app/config.py
+++ b/demo_app/config.py
@@ -1,6 +1,7 @@
 \"\"\"Application configuration (EV-001: hard-coded secret).\"\"\"
 
 # BUG EV-001: secret must come from environment, not source control.
 API_SECRET = "hardcoded-demo-secret-do-not-ship"
+# comment only — exploit remains
 
 
 def get_api_secret() -> str:
"""

OUT_OF_SCOPE_DIFF = """\
--- a/demo_app/config.py
+++ b/demo_app/config.py
@@ -1,8 +1,10 @@
 \"\"\"Application configuration (EV-001: hard-coded secret).\"\"\"
 
+import os
+
-API_SECRET = "hardcoded-demo-secret-do-not-ship"
+API_SECRET = os.environ.get("API_SECRET", "")
 
 def get_api_secret() -> str:
     return API_SECRET
--- a/demo_app/app.py
+++ b/demo_app/app.py
@@ -1,5 +1,6 @@
 \"\"\"Minimal demo entrypoints wiring vulnerable modules.\"\"\"
 
+# touched extra file
 from demo_app.config import get_api_secret
"""


def test_exploit_tests_fail_on_vulnerable_seed():
    for test_path in (
        "tests/test_ev001_secret.py",
        "tests/test_ev002_sqli.py",
        "tests/test_ev003_path.py",
    ):
        result = run_exploit_test(REPO, test_path)
        assert not result.passed, test_path


def test_gate_proven_with_mock_fix():
    finding = REPO / "findings/seed/EV-001.md"
    model = MockFixModel(GOOD_EV001_DIFF)
    result = run_gate(REPO, finding, model, model_name="mock/proven")
    assert result.outcome.verdict == Verdict.PROVEN
    assert result.before.passed is False
    assert result.after.passed is True


def test_gate_not_proven_when_exploit_remains():
    finding = REPO / "findings/seed/EV-001.md"
    model = MockFixModel(STILL_VULNERABLE_DIFF)
    result = run_gate(REPO, finding, model, model_name="mock/not-proven")
    assert result.outcome.verdict == Verdict.NOT_PROVEN


def test_gate_out_of_scope_extra_file():
    finding = REPO / "findings/seed/EV-001.md"
    model = MockFixModel(OUT_OF_SCOPE_DIFF)
    result = run_gate(REPO, finding, model, model_name="mock/out-of-scope")
    assert result.outcome.verdict == Verdict.OUT_OF_SCOPE


def test_scope_check_unit():
    scope = check_scope(OUT_OF_SCOPE_DIFF, ("demo_app/config.py",))
    assert not scope.ok
    assert "demo_app/app.py" in scope.extra


def test_replay_record_roundtrip():
    finding = parse_finding(REPO / "findings/seed/EV-001.md")
    before = run_exploit_test(REPO, finding.test_path)
    after = run_exploit_test(REPO, finding.test_path)
    from evidence_gate.verdict import GateOutcome

    outcome = GateOutcome(Verdict.NOT_PROVEN, "example")
    record = record_from_run(
        finding_id=finding.finding_id,
        prompt_hash="abc",
        model="mock",
        fix_diff="",
        before=before,
        after=after,
        outcome=outcome,
        affected_files=finding.affected_files,
    )
    path = REPO / "replays" / "_test_roundtrip.json"
    record.save(path)
    loaded = ReplayRecord.load(path)
    assert loaded.finding_id == "EV-001"
    path.unlink()


def test_evaluate_gate_matrix():
    from evidence_gate.pytest_runner import PytestResult
    from evidence_gate.scope import ScopeCheck

    fail = PytestResult(1, "fail", "")
    ok = PytestResult(0, "ok", "")
    in_scope = ScopeCheck(True, ("demo_app/config.py",), (), "ok")
    out_scope = ScopeCheck(False, (), ("demo_app/app.py",), "extra")

    assert evaluate_gate(fail, ok, in_scope).verdict == Verdict.PROVEN
    assert evaluate_gate(ok, ok, in_scope).verdict == Verdict.NOT_PROVEN
    assert evaluate_gate(fail, fail, in_scope).verdict == Verdict.NOT_PROVEN
    assert evaluate_gate(fail, ok, out_scope).verdict == Verdict.OUT_OF_SCOPE
