#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

output="$(cd "$repo_root" && bash ./run_tests.sh 2>&1)"

if [[ "$output" != *"PASS"* ]]; then
  echo "expected PASS in output"
  echo "$output"
  exit 1
fi

echo "ok"
