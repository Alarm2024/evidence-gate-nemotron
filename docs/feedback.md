# Nebius Token Factory / Nemotron feedback — Draft

**Status: Draft.** Not yet confirmed by a keyed run from this repo. Points marked *to confirm* need the owner's first real run before sending.

1. **OpenAI-compatible base URL keeps the client small.** Evidence Gate talks to Token Factory with the standard `openai` Python client and only a `base_url` change, so the model client is about 100 lines and easy to mock in tests. *(Integration shape confirmed in code; response behavior to confirm.)*
2. **Diff-only output is the hard part.** The gate needs exactly one unified diff. A documented prompt pattern or structured-output option for "return only a patch" would cut the regex parsing we do in `extract_diff`. *(To confirm how often Nemotron adds text around the diff.)*
3. **Picking a model for code repair.** We hard-code a main and a fast Nemotron ID. A short "good for code edits" hint in the model list would help tools choose without trial and error.
4. **Reproducibility needs a stable model version.** We store the model ID and a prompt hash in each replay. If an ID can point to updated weights over time, a version or snapshot field in the response would make replays easier to compare. *(Unknown whether IDs are pinned; to confirm in docs.)*
5. **Latency for the fast path.** *(To fill in after a keyed run: measured time per EV run for main vs `--fast`. No numbers yet.)*
