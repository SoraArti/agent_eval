#!/usr/bin/env bash
set -euo pipefail

JOB_JSON="$1"
OUTDIR="$2"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

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

load_env_file() {
  local env_file="$1"
  if [[ -n "$env_file" && -f "$env_file" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
}

CODEX_CMD_DETECTED="$(detect_codex_cmd || true)"
if [[ -n "$CODEX_CMD_DETECTED" ]]; then
  PROMPT_FILE="$OUTDIR/prompt.txt"
  python3 "$ROOT_DIR/runner/render_prompt.py" --job-json "$JOB_JSON" --out "$PROMPT_FILE"
  load_env_file "${CODEX_ENV:-}"
  {
    echo "running real codex command"
    echo "command: $CODEX_CMD_DETECTED ${CODEX_ARGS:-}"
  } >>"$OUTDIR/stdout.log"
  RAW_OUTPUT="$(cat "$PROMPT_FILE" | "$CODEX_CMD_DETECTED" exec --skip-git-repo-check --json --dangerously-bypass-approvals-and-sandbox ${CODEX_ARGS:-} - 2>>"$OUTDIR/stderr.log" || true)"
  printf '%s\n' "$RAW_OUTPUT" >>"$OUTDIR/stdout.log"
  printf '%s\n' "$RAW_OUTPUT" >"$OUTDIR/codex_raw.jsonl"
  if [[ ! -f "$OUTDIR/result.json" ]]; then
    CODEX_RAW_PATH="$OUTDIR/codex_raw.jsonl" JOB_JSON="$JOB_JSON" python3 - <<'PY'
import json
import os
from pathlib import Path

raw_path = Path(os.environ["CODEX_RAW_PATH"])
job = json.loads(os.environ["JOB_JSON"])
lines = [line for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()]
items = []
for line in lines:
    try:
        items.append(json.loads(line))
    except json.JSONDecodeError:
        pass
message = ""
for item in items:
    if item.get("type") == "item.completed":
        obj = item.get("item", {})
        if obj.get("type") == "agent_message":
            message = obj.get("text", "")
result = {
    "status": "success" if message else "error",
    "tool": "codex",
    "job_id": job.get("job_id", "unknown"),
    "summary": message or "No final agent message captured",
}
(raw_path.parent / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
  fi
else
  python3 "$ROOT_DIR/runner/dry_run_tool.py" \
    --tool codex \
    --job-json "$JOB_JSON" \
    --outdir "$OUTDIR" \
    >>"$OUTDIR/stdout.log" 2>>"$OUTDIR/stderr.log"
fi
