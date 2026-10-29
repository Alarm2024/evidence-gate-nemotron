# Evidence Gate (Nemotron)

Evidence Gate takes one security finding, asks an **NVIDIA Nemotron** model on **Nebius Token Factory** (OpenAI-compatible API) to propose a fix, then **proves** the fix with exploit tests:

1. The exploit test **fails** on vulnerable code (finding still exploitable).
2. The **same** test **passes** after applying the model’s diff.
3. The diff touches **only** files named in the finding.

Each run yields **PROVEN**, **NOT PROVEN**, or **OUT OF SCOPE**, with a short reason. A replay JSON captures prompt hash, model id, diff, before/after test output, and verdict — **no API key** and **no auth headers**.

**Author:** Wyndham Heaven (elghaly) · **License:** MIT

> **Note:** Upstream Exploit-to-Evidence demo code was not present in this repository; this project includes a rebuilt `demo_app` with seed findings **EV-001** (hard-coded secret), **EV-002** (SQL injection), and **EV-003** (path traversal).
>
> **The EV-001 secret is planted, not real.** `demo_app/config.py:4` holds the string `hardcoded-demo-secret-do-not-ship` on purpose: it is the bug EV-001 exists to find. It is not a credential for any service. The file is left as is because the seed fix (`tests/fixtures/seed_fixes/EV-001.diff`) and the replay `replays/EV-001.json` are recorded against it byte for byte.

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

# Offline replay — no key, no network (EV-001, EV-002, EV-003)
python -m evidence_gate run --replay replays/EV-001.json
```

Replay mode re-applies the stored diff in a temporary copy, reruns the exploit test, and recomputes the verdict. If it differs from the recorded verdict the CLI exits with code 3. Replay mode never imports the `openai` client.

The bundled `replays/EV-00*.json` are **seed replays**: hand-written fix diffs (`tests/fixtures/seed_fixes/`) run through the real gate with a mocked model. They are not model output. A keyed run overwrites `replays/EV-xxx.json` with a Nemotron run. Rebuild seeds and the inlined site data with `python scripts/make_seed_replays.py`.

## Tests

```bash
pytest -q
```

Tests use a mocked model and cover all three verdicts. Replay tests run the CLI with `NEBIUS_API_KEY` removed and with `tests/netblock/` on `PYTHONPATH`, which makes any socket connect or DNS lookup raise (also in pytest child processes). Exploit tests (`-m exploit`) are deselected from the default run because they fail on the vulnerable demo by design; the gate runs them, and `test_exploit_tests_fail_on_vulnerable_seed` checks they fail.

## Demo site

Open [`docs/index.html`](docs/index.html) on GitHub Pages to step through the bundled replays in the browser. Data is inlined; the page makes no network calls. Pages source: `main` branch, `/docs` folder.

## Hackathon

Nebius × NVIDIA — track **Coding and Agentic Engineering**.
