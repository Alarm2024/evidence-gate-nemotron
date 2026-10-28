# Evidence Gate (Nemotron)

Evidence Gate takes one security finding, asks an **NVIDIA Nemotron** model on **Nebius Token Factory** (OpenAI-compatible API) to propose a fix, then **proves** the fix with exploit tests:

1. The exploit test **fails** on vulnerable code (finding still exploitable).
2. The **same** test **passes** after applying the model’s diff.
3. The diff touches **only** files named in the finding.

Each run yields **PROVEN**, **NOT PROVEN**, or **OUT OF SCOPE**, with a short reason. A replay JSON captures prompt hash, model id, diff, before/after test output, and verdict — **no API key** and **no auth headers**.

**Author:** Wyndham Heaven (elghaly) · **License:** MIT

> **Note:** Upstream Exploit-to-Evidence demo code was not present in this repository; this project includes a rebuilt `demo_app` with seed findings **EV-001** (hard-coded secret), **EV-002** (SQL injection), and **EV-003** (path traversal).

## Models

| Role | Model ID |
|------|----------|
| Main | `nvidia/nemotron-3-super-120b-a12b` |
| Fast | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` |

API key: environment variable **`NEBIUS_API_KEY` only** (never committed).

## Setup

```bash
python -m pip install -e ".[dev]"
```

## CLI

```bash
# List models (requires NEBIUS_API_KEY)
python -m evidence_gate models

# Run gate on a finding (requires NEBIUS_API_KEY; writes replays/EV-xxx.json)
python -m evidence_gate run --finding findings/seed/EV-001.md

# Fast model
python -m evidence_gate run --finding findings/seed/EV-002.md --fast

# Offline replay — no key, no network
python -m evidence_gate run --finding findings/seed/EV-001.md --replay replays/EV-001.json
```

## Tests

```bash
pytest -q
```

## Demo site

Open [`docs/index.html`](docs/index.html) on GitHub Pages to step through a bundled replay in the browser (no external network calls).

## Hackathon

Nebius × NVIDIA — track **Coding and Agentic Engineering**.
