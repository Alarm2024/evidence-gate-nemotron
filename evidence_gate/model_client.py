"""Nebius Token Factory (OpenAI-compatible) client."""

from __future__ import annotations

import hashlib
import os
import re
from typing import Protocol

from evidence_gate import FAST_MODEL, MAIN_MODEL, NEBIUS_BASE_URL


class FixModel(Protocol):
    def complete_fix(self, system: str, user: str) -> str: ...


def require_api_key() -> str:
    key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "NEBIUS_API_KEY is not set. Export it to call Nemotron on Nebius Token Factory."
        )
    return key


def make_client():
    """Build the Nebius client. The key is read only from NEBIUS_API_KEY."""
    from openai import OpenAI  # imported lazily: replay mode never loads it

    return OpenAI(
        base_url=NEBIUS_BASE_URL,
        api_key=require_api_key(),
    )


def list_reachable_models() -> list[str]:
    client = make_client()
    models = client.models.list()
    return sorted(m.id for m in models.data)


def prompt_hash(system: str, user: str, model: str) -> str:
    payload = f"{model}\n---\n{system}\n---\n{user}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


_DIFF_FENCE = re.compile(
    r"```(?:diff)?\s*\n(?P<body>.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)


def extract_diff(text: str) -> str:
    m = _DIFF_FENCE.search(text)
    if m:
        return m.group("body").strip() + "\n"
    if text.lstrip().startswith("--- "):
        return text.strip() + "\n"
    raise ValueError("Model response did not contain a unified diff")


def build_fix_prompt(finding_body: str, file_contents: dict[str, str]) -> tuple[str, str]:
    system = (
        "You are a security engineer. Output ONLY a single unified diff (git format) "
        "that fixes the vulnerability described in the finding. "
        "Modify ONLY the files listed under Affected files. "
        "Do not add commentary outside the diff."
    )
    parts = [finding_body, "", "## Current file contents", ""]
    for path, content in sorted(file_contents.items()):
        parts.append(f"### {path}")
        parts.append("```")
        parts.append(content.rstrip())
        parts.append("```")
        parts.append("")
    user = "\n".join(parts)
    return system, user


class NemotronFixModel:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or MAIN_MODEL
        self._client = make_client()

    def complete_fix(self, system: str, user: str) -> str:
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        content = completion.choices[0].message.content or ""
        return extract_diff(content)


class MockFixModel:
    """Deterministic model for unit tests."""

    def __init__(self, diff: str) -> None:
        self.diff = diff
        self.calls: list[tuple[str, str]] = []

    def complete_fix(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self.diff
