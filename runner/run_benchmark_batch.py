#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from common import load_yaml_like, utc_now, write_json


ROOT = Path(__file__).resolve().parents[1]


def run_job(job_path: Path) -> dict:
    proc = subprocess.run(
        ["python3", str(ROOT / "runner" / "run_job.py"), "--job", str(job_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "job_id": load_yaml_like(job_path).get("job_id"),
        "job_path": str(job_path),
        "rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

def load_job_artifacts(job_id: str) -> dict:
    outdir = ROOT / "outputs" / job_id
    judge_path = outdir / "judge.json"
    heartbeat_path = outdir / "heartbeat.json"
    metadata_path = outdir / "metadata.json"
    result_path = outdir / "result.json"

    judge = json.loads(judge_path.read_text(encoding="utf-8")) if judge_path.exists() else {}
    heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8")) if heartbeat_path.exists() else {}
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}

    return {
        "judge_passed": judge.get("passed"),
        "runner_status": heartbeat.get("status"),
        "benchmark_id": metadata.get("benchmark_id"),
        "tool_status": result.get("status"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark")
    parser.add_argument("--tool")
    args = parser.parse_args()

    jobs_dir = ROOT / "manifests" / "jobs"
    selected: list[Path] = []
    for job_path in sorted(jobs_dir.glob("*.yaml")):
        job = load_yaml_like(job_path)
        if args.benchmark and job.get("benchmark") != args.benchmark:
            continue
        if args.tool and job.get("tool") != args.tool:
            continue
        selected.append(job_path)

    results = []
    for job_path in selected:
        result = run_job(job_path)
        artifacts = load_job_artifacts(result["job_id"])
        result.update(artifacts)
        results.append(result)

    total = len(results)
    judge_passed = sum(1 for r in results if r.get("judge_passed") is True)
    judge_failed = sum(1 for r in results if r.get("judge_passed") is False)
    judge_missing = sum(1 for r in results if r.get("judge_passed") is None)
    tool_failed = sum(1 for r in results if r.get("rc") not in (0, None))

    payload = {
        "started_at": utc_now(),
        "benchmark": args.benchmark,
        "tool": args.tool,
        "jobs": results,
        "count": len(results),
        "batch_summary": {
            "total": total,
            "judge_passed": judge_passed,
            "judge_failed": judge_failed,
            "judge_missing": judge_missing,
            "tool_failed": tool_failed,
        },
    }

    state_dir = ROOT / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    batch_name = f"batch_{args.benchmark or 'all'}_{args.tool or 'all'}.json"
    write_json(state_dir / batch_name, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
