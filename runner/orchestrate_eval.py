#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import utc_now, write_json


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True)
    parser.add_argument("--benchmark")
    args = parser.parse_args()

    bootstrap_rc, bootstrap_stdout, bootstrap_stderr = run_cmd(["bash", str(ROOT / "runner" / "bootstrap.sh")])
    setup_rc, setup_stdout, setup_stderr = run_cmd(
        ["python3", str(ROOT / "runner" / "setup_tool_env.py"), "--tool", args.tool]
    )
    batch_cmd = ["python3", str(ROOT / "runner" / "run_benchmark_batch.py"), "--tool", args.tool]
    if args.benchmark:
        batch_cmd.extend(["--benchmark", args.benchmark])
    batch_rc, batch_stdout, batch_stderr = run_cmd(batch_cmd)
    summary_rc, summary_stdout, summary_stderr = run_cmd(["python3", str(ROOT / "runner" / "summarize.py")])

    payload = {
        "started_at": utc_now(),
        "tool": args.tool,
        "benchmark": args.benchmark,
        "bootstrap": {"rc": bootstrap_rc, "stdout": bootstrap_stdout, "stderr": bootstrap_stderr},
        "setup": {"rc": setup_rc, "stdout": setup_stdout, "stderr": setup_stderr},
        "batch": {"rc": batch_rc, "stdout": batch_stdout, "stderr": batch_stderr},
        "summary": {"rc": summary_rc, "stdout": summary_stdout, "stderr": summary_stderr},
        "success": bootstrap_rc == 0 and setup_rc == 0 and batch_rc == 0 and summary_rc == 0,
    }

    state_dir = ROOT / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    output_name = f"orchestrate_{args.tool}_{args.benchmark or 'all'}.json"
    write_json(state_dir / output_name, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=True))

    if not payload["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
