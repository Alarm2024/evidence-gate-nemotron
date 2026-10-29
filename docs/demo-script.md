# Demo script (target under 2:50)

Spoken text only is timed. Estimated at about 150 words per minute.

## 0:00 – 0:20 · The problem

> AI tools are quick to suggest security fixes, but a suggested fix is not the same as a proven one. Evidence Gate asks one question: can we show that this fix closes the hole, and touches nothing else?

*Screen: README title.*

## 0:20 – 0:50 · The finding and the exploit test

> Here is finding EV-001: a secret written straight into the source of a small demo app. Each finding names the files it may touch and one exploit test. On the vulnerable code, that test fails. That failure is our evidence the problem is real.

*Screen: `findings/seed/EV-001.md`, then `pytest -m exploit tests/test_ev001_secret.py` failing.*

## 0:50 – 1:30 · The gate

> Evidence Gate sends the finding and the affected file to Nemotron on Nebius Token Factory and asks for one unified diff. It then copies the repo to a temporary folder, applies the diff there, and runs the same exploit test again. Three rules decide the verdict. The test must fail before, pass after, and the diff may only touch files named in the finding. That gives PROVEN, NOT PROVEN, or OUT OF SCOPE.

*Screen: `python -m evidence_gate run --replay replays/EV-001.json` → `Verdict: PROVEN`.*

## 1:30 – 2:00 · Replays

> Every run writes a replay file: the prompt hash, the model name, the diff, and both test results. No key and no headers are stored. Anyone can rerun a replay offline, and the gate recomputes the verdict instead of trusting the file.

*Screen: `replays/EV-002.json`, then the replay viewer in `docs/index.html`.*

## 2:00 – 2:30 · The other verdicts

> The tests cover all three outcomes with a mocked model. A diff that leaves the secret in place is NOT PROVEN. A diff that also edits an unrelated file is OUT OF SCOPE, even if the exploit test passes.

*Screen: `pytest -q` passing.*

## 2:30 – 2:45 · Close

> Evidence Gate: fixes you can check, not just trust. Built by Wyndham Heaven, elghaly.

*Screen: repo page.*

---

**Spoken word count:** 250 words ≈ 1:40 at 150 wpm, leaving about 1:05 for screen actions inside 2:45.

**Before recording:** the bundled replays are seed replays (hand-written fix diffs, mocked model). Record at least one keyed Nemotron run first (`python -m evidence_gate run --finding findings/seed/EV-002.md`) and show that replay, so the screen matches the narration.
