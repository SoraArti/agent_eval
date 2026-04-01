#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

command -v python3 >/dev/null 2>&1 || { echo "missing: python3"; exit 1; }

test -d "$ROOT_DIR/manifests/jobs" || { echo "missing manifests/jobs"; exit 1; }
test -d "$ROOT_DIR/runner" || { echo "missing runner"; exit 1; }

python3 - <<'PY'
import sqlite3
from pathlib import Path

root = Path.cwd()
db_path = root / "state" / "jobs.sqlite3"
conn = sqlite3.connect(db_path)
conn.execute("select 1")
conn.close()
print("healthcheck: ok")
PY
