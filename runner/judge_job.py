#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from common import build_job_payload, output_dir, write_json


ROOT = Path(__file__).resolve().parents[1]


def judge_file_exists(required_file: str, outdir: Path) -> dict:
    target = outdir / required_file
    passed = target.exists()
    return {
        "passed": passed,
        "reason": f"required file {'found' if passed else 'missing'}: {required_file}",
    }


def judge_command_stub(command: str, success_regex: str, outdir: Path) -> dict:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        capture_output=True,
        text=True,
    )
    haystack = "\n".join(part for part in (proc.stdout, proc.stderr) if part)
    regex_matched = re.search(success_regex, haystack) is not None if success_regex else True
    passed = proc.returncode == 0 and regex_matched

    return {
        "passed": passed,
        "reason": "verification matched" if passed else "verification did not match",
        "command": command,
        "success_regex": success_regex,
        "exit_code": proc.returncode,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    args = parser.parse_args()

    job_path = (ROOT / args.job).resolve() if not args.job.startswith("/") else Path(args.job)
    payload = build_job_payload(job_path)
    benchmark = payload.get("_benchmark", {})
    verification = benchmark.get("verification", {})
    outdir = output_dir(payload["job_id"])

    verification_type = verification.get("type", "")
    if verification_type == "file_exists":
        result = judge_file_exists(verification.get("required_file", ""), outdir)
    else:
        result = judge_command_stub(
            verification.get("command", ""),
            verification.get("success_regex", ""),
            outdir,
        )

    judge_payload = {
        "job_id": payload["job_id"],
        "benchmark": payload.get("benchmark"),
        "verification_type": verification_type or "command",
        "passed": result["passed"],
        "details": result,
    }
    write_json(outdir / "judge.json", judge_payload)
    print(json.dumps(judge_payload, indent=2))


if __name__ == "__main__":
    main()
