#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

bash envs/base/install.sh
bash envs/claude_code/install.sh
bash envs/codex/install.sh

python3 runner/init_db.py

echo "bootstrap complete"
