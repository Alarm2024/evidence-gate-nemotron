"""Run pytest for a single exploit test file."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PytestResult:
    exit_code: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    def to_dict(self) -> dict:
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PytestResult:
        return cls(
            exit_code=int(data["exit_code"]),
            stdout=str(data.get("stdout", "")),
            stderr=str(data.get("stderr", "")),
        )


def run_exploit_test(
    repo_root: Path,
    test_path: str,
    *,
    timeout: int = 120,
) -> PytestResult:
    test_file = repo_root / test_path
    if not test_file.is_file():
        return PytestResult(
            exit_code=2,
            stdout="",
            stderr=f"Missing exploit test: {test_path}",
        )
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-q",
            "--tb=short",
            "-m",
            "exploit",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return PytestResult(
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
