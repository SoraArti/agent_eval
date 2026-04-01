#!/usr/bin/env bash
set -euo pipefail

JOB_JSON="$1"
OUTDIR="$2"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

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

load_env_file() {
  local env_file="$1"
  if [[ -n "$env_file" && -f "$env_file" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
}

CLAUDE_CODE_CMD_DETECTED="$(detect_claude_cmd || true)"
if [[ -n "$CLAUDE_CODE_CMD_DETECTED" ]]; then
  PROMPT_FILE="$OUTDIR/prompt.txt"
  python3 "$ROOT_DIR/runner/render_prompt.py" --job-json "$JOB_JSON" --out "$PROMPT_FILE"
  load_env_file "${CLAUDE_CODE_ENV:-}"
  {
    echo "running real claude_code command"
    echo "command: $CLAUDE_CODE_CMD_DETECTED ${CLAUDE_CODE_ARGS:-}"
  } >>"$OUTDIR/stdout.log"
  PROMPT_TEXT="$(cat "$PROMPT_FILE")"
  RAW_OUTPUT="$("$CLAUDE_CODE_CMD_DETECTED" -p --output-format json ${CLAUDE_CODE_ARGS:-} "$PROMPT_TEXT" 2>>"$OUTDIR/stderr.log" || true)"
  printf '%s\n' "$RAW_OUTPUT" >>"$OUTDIR/stdout.log"
  printf '%s\n' "$RAW_OUTPUT" >"$OUTDIR/claude_raw.json"
  if [[ ! -f "$OUTDIR/result.json" ]]; then
    CLAUDE_RAW_PATH="$OUTDIR/claude_raw.json" JOB_JSON="$JOB_JSON" python3 - <<'PY'
import json
import os
from pathlib import Path

raw_path = Path(os.environ["CLAUDE_RAW_PATH"])
job = json.loads(os.environ["JOB_JSON"])
text = raw_path.read_text(encoding="utf-8").strip()
payload = json.loads(text) if text else {}
result = {
    "status": "success" if not payload.get("is_error", False) else "error",
    "tool": "claude_code",
    "job_id": job.get("job_id", "unknown"),
    "summary": payload.get("result", text),
    "raw_session_id": payload.get("session_id"),
}
(raw_path.parent / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
  fi
else
  python3 "$ROOT_DIR/runner/dry_run_tool.py" \
    --tool claude_code \
    --job-json "$JOB_JSON" \
    --outdir "$OUTDIR" \
    >>"$OUTDIR/stdout.log" 2>>"$OUTDIR/stderr.log"
fi
