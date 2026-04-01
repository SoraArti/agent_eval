#!/usr/bin/env bash
set -euo pipefail

detect_codex_cmd() {
  if [[ -n "${CODEX_CMD:-}" ]]; then
    echo "$CODEX_CMD"
    return 0
  fi
  if command -v codex >/dev/null 2>&1; then
    echo "codex"
    return 0
  fi
  return 1
}

CODEX_CMD_DETECTED="$(detect_codex_cmd || true)"
if [[ -n "$CODEX_CMD_DETECTED" ]]; then
  if command -v "$CODEX_CMD_DETECTED" >/dev/null 2>&1 || [[ -x "$CODEX_CMD_DETECTED" ]]; then
    echo "codex healthcheck: using CODEX_CMD=$CODEX_CMD_DETECTED"
  else
    echo "codex healthcheck: CODEX_CMD not found or not executable"
    exit 1
  fi
else
  echo "codex healthcheck: dry-run mode (no CLI detected)"
fi

if [[ -n "${CODEX_ENV:-}" ]]; then
  if [[ -f "$CODEX_ENV" ]]; then
    echo "codex healthcheck: env file ok ($CODEX_ENV)"
  else
    echo "codex healthcheck: CODEX_ENV not found ($CODEX_ENV)"
    exit 1
  fi
fi

if [[ -n "$CODEX_CMD_DETECTED" ]]; then
  SMOKE_OUTPUT="$(printf 'reply with the single word READY\n' | "$CODEX_CMD_DETECTED" exec --skip-git-repo-check --json --dangerously-bypass-approvals-and-sandbox - 2>&1 || true)"
  echo "$SMOKE_OUTPUT" | sed -n '1,20p'
  if ! echo "$SMOKE_OUTPUT" | grep -q 'READY'; then
    echo "codex healthcheck: smoke test did not produce expected output"
    exit 1
  fi
  echo "codex healthcheck: smoke test ok"
fi
