#!/usr/bin/env bash
# Record a live Nemotron run for EV-002 into replays/model/ (not committed by default).
# Requires NEBIUS_API_KEY in the environment only — never embed or pass the key on the CLI.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -z "${NEBIUS_API_KEY:-}" ]]; then
  echo "NEBIUS_API_KEY must be set in the environment." >&2
  exit 1
fi

SEED_REPLAY="$ROOT/replays/EV-002.json"
if [[ ! -f "$SEED_REPLAY" ]]; then
  echo "Missing bundled seed replay: $SEED_REPLAY" >&2
  exit 1
fi

mkdir -p "$ROOT/replays/model"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/replays/model/EV-002-${STAMP}.json"
BACKUP="$(mktemp)"

cp "$SEED_REPLAY" "$BACKUP"
python3 -m evidence_gate run --finding findings/seed/EV-002.md
mv "$ROOT/replays/EV-002.json" "$OUT"
mv "$BACKUP" "$SEED_REPLAY"

echo "Saved model replay to $OUT (seed replay restored at replays/EV-002.json)"
