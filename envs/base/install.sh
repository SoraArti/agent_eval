#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$ROOT_DIR/outputs"
mkdir -p "$ROOT_DIR/state"
mkdir -p "$ROOT_DIR/manifests/jobs"
mkdir -p "$ROOT_DIR/manifests/benchmarks"

ROOT_DIR="$ROOT_DIR" python3 - <<'PY'
import os
import pathlib
root = pathlib.Path(os.environ["ROOT_DIR"])
db = root / "state" / "jobs.sqlite3"
db.touch(exist_ok=True)
print(f"prepared {db}")
PY
