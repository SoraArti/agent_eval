#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import build_job_payload, connect_db, ensure_jobs_registered, output_dir, utc_now, worker_name, write_json


ROOT = Path(__file__).resolve().parents[1]


def run_shell(script: Path, job_json: str, outdir: Path) -> int:
    command = ["bash", str(script), job_json, str(outdir)]
    proc = subprocess.run(command, cwd=ROOT)
    return proc.returncode


def run_judge(job_path: Path) -> int:
    command = ["python3", str(ROOT / "runner" / "judge_job.py"), "--job", str(job_path)]
    proc = subprocess.run(command, cwd=ROOT)
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    args = parser.parse_args()

    ensure_jobs_registered()
    job_path = (ROOT / args.job).resolve() if not args.job.startswith("/") else Path(args.job)
    job = build_job_payload(job_path)
    job_id = job["job_id"]
    tool = job["tool"]
    outdir = output_dir(job_id)

    conn = connect_db()
    conn.execute(
        """
        insert into jobs(job_id, job_path, tool, status, claimed_by, updated_at)
        values (?, ?, ?, 'RUNNING', ?, ?)
        on conflict(job_id) do update set
            job_path = excluded.job_path,
            tool = excluded.tool,
            status = 'RUNNING',
            claimed_by = excluded.claimed_by,
            updated_at = excluded.updated_at,
            last_error = null
        """,
        (job_id, str(job_path), tool, worker_name(), utc_now()),
    )
    conn.commit()
    conn.close()

    metadata = {
        "job_id": job_id,
        "tool": tool,
        "model": job.get("model"),
        "profile": job.get("profile"),
        "job_path": str(job_path),
        "benchmark_id": job.get("benchmark"),
        "benchmark_path": job.get("_benchmark", {}).get("_path"),
        "worker": worker_name(),
        "started_at": utc_now(),
    }
    write_json(outdir / "metadata.json", metadata)
    write_json(outdir / "heartbeat.json", {"status": "RUNNING", "updated_at": utc_now()})

    script = ROOT / "envs" / tool / "run.sh"
    rc = run_shell(script, json.dumps(job), outdir)
    judge_rc = 1
    if rc == 0 and (outdir / "result.json").exists():
        judge_rc = run_judge(job_path)

    status = "DONE" if rc == 0 and judge_rc == 0 and (outdir / "result.json").exists() else "FAILED"
    write_json(
        outdir / "heartbeat.json",
        {"status": status, "updated_at": utc_now()},
    )
    (outdir / "exit_status.txt").write_text(str(rc) + "\n", encoding="utf-8")

    conn = connect_db()
    conn.execute(
        """
        update jobs
        set status = ?, claimed_by = ?, updated_at = ?, last_error = ?
        where job_id = ?
        """,
        (
            status,
            worker_name(),
            utc_now(),
            None if status == "DONE" else f"tool_rc={rc}, judge_rc={judge_rc}",
            job_id,
        ),
    )
    conn.commit()
    conn.close()

    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
