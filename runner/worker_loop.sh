#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ONCE=0
POLL_SECONDS="${POLL_SECONDS:-5}"

if [[ "${1:-}" == "--once" ]]; then
  ONCE=1
fi

cd "$ROOT_DIR"

while true; do
  CLAIMED_JOB="$(python3 runner/claim_job.py || true)"
  if [[ -n "$CLAIMED_JOB" ]]; then
    echo "claimed job: $CLAIMED_JOB"
    python3 runner/run_job.py --job "manifests/jobs/${CLAIMED_JOB}.yaml"
  else
    echo "no pending jobs"
  fi

  if [[ "$ONCE" -eq 1 ]]; then
    break
  fi

  sleep "$POLL_SECONDS"
done
