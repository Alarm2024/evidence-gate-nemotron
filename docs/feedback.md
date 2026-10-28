# Nebius / NVIDIA feedback (draft)

1. **OpenAI-compatible surface** — Using the official Python client with a single `base_url` swap made Evidence Gate integration straightforward; model listing and chat completions behaved as documented.
2. **Model IDs** — Nemotron main vs nano naming is clear once listed; a short “recommended for code repair” tag in the models API would help agents pick defaults faster.
3. **Diff-shaped outputs** — Security fix workflows want unified diffs; response_format or a documented “unified diff only” prompt pattern in Token Factory examples would reduce parse failures.
4. **Rate and latency** — Larger Nemotron models are strong but slow for tight CI loops; the nano model as a `--fast` path is useful; exposing typical tokens/sec in the dashboard would set expectations.
5. **Offline replay story** — Hackathon judges appreciate reproducibility; pairing Token Factory runs with hashed prompts (no secrets in artifacts) matches how we ship `replays/*.json` for demo and CI.
