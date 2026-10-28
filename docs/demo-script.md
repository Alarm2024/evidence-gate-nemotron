# Demo script (under 2:50)

1. **0:00–0:20** — Show `findings/seed/EV-001.md`: hard-coded secret in `demo_app/config.py`.
2. **0:20–0:45** — Run `pytest tests/test_ev001_secret.py` → fails on vulnerable tree.
3. **0:45–1:15** — Run offline replay:  
   `python -m evidence_gate run --finding findings/seed/EV-001.md --replay replays/EV-001.json`  
   → **PROVEN**, before fail / after pass, diff scoped to one file.
4. **1:15–1:45** — Open `docs/index.html`: walk through the same replay (verdict, diff, test output).
5. **1:45–2:20** — With `NEBIUS_API_KEY` set, `python -m evidence_gate models` and one live `run` on EV-002 or EV-003; show new `replays/EV-00x.json`.
6. **2:20–2:45** — Mention pytest gate tests (mocked model): NOT PROVEN and OUT OF SCOPE paths.
