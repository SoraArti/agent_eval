#!/usr/bin/env bash
set -euo pipefail

detect_claude_cmd() {
  if [[ -n "${CLAUDE_CODE_CMD:-}" ]]; then
    echo "$CLAUDE_CODE_CMD"
    return 0
  fi
  if command -v claude >/dev/null 2>&1; then
    echo "claude"
    return 0
  fi
  if command -v claude-code >/dev/null 2>&1; then
    echo "claude-code"
    return 0
  fi
  return 1
}

CLAUDE_CODE_CMD_DETECTED="$(detect_claude_cmd || true)"
if [[ -n "$CLAUDE_CODE_CMD_DETECTED" ]]; then
  if command -v "$CLAUDE_CODE_CMD_DETECTED" >/dev/null 2>&1 || [[ -x "$CLAUDE_CODE_CMD_DETECTED" ]]; then
    echo "claude_code healthcheck: using CLAUDE_CODE_CMD=$CLAUDE_CODE_CMD_DETECTED"
  else
    echo "claude_code healthcheck: CLAUDE_CODE_CMD not found or not executable"
    exit 1
  fi
else
  echo "claude_code healthcheck: dry-run mode (no CLI detected)"
fi

if [[ -n "${CLAUDE_CODE_ENV:-}" ]]; then
  if [[ -f "$CLAUDE_CODE_ENV" ]]; then
    echo "claude_code healthcheck: env file ok ($CLAUDE_CODE_ENV)"
  else
    echo "claude_code healthcheck: CLAUDE_CODE_ENV not found ($CLAUDE_CODE_ENV)"
    exit 1
  fi
fi

if [[ -n "$CLAUDE_CODE_CMD_DETECTED" ]]; then
  SMOKE_OUTPUT="$("$CLAUDE_CODE_CMD_DETECTED" -p --output-format json "reply with the single word READY" 2>&1 || true)"
  echo "$SMOKE_OUTPUT" | sed -n '1,20p'
  if echo "$SMOKE_OUTPUT" | grep -q '"is_error":true'; then
    echo "claude_code healthcheck: smoke test failed"
    exit 1
  fi
  if ! echo "$SMOKE_OUTPUT" | grep -q 'READY'; then
    echo "claude_code healthcheck: smoke test did not produce expected output"
    exit 1
  fi
  echo "claude_code healthcheck: smoke test ok"
fi
