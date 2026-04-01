#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import utc_now, write_json


ROOT = Path(__file__).resolve().parents[1]


def run_script(script: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["bash", str(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True)
    args = parser.parse_args()

    tool = args.tool
    env_dir = ROOT / "envs" / tool
    install_script = env_dir / "install.sh"
    healthcheck_script = env_dir / "healthcheck.sh"

    if not env_dir.exists():
        raise SystemExit(f"unknown tool env: {tool}")

    install_rc, install_stdout, install_stderr = run_script(install_script)
    health_rc, health_stdout, health_stderr = run_script(healthcheck_script)

    payload = {
        "tool": tool,
        "started_at": utc_now(),
        "install": {
            "rc": install_rc,
            "stdout": install_stdout,
            "stderr": install_stderr,
        },
        "healthcheck": {
            "rc": health_rc,
            "stdout": health_stdout,
            "stderr": health_stderr,
        },
        "success": install_rc == 0 and health_rc == 0,
    }

    state_dir = ROOT / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    write_json(state_dir / f"setup_{tool}.json", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=True))

    if not payload["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
