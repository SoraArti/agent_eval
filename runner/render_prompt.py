#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-json", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    job = json.loads(args.job_json)
    benchmark = job.get("_benchmark", {})
    benchmark_data = benchmark.get("data", {})
    verification = benchmark.get("verification", {})
    text = f"""You are an engineering agent working in a local evaluation sandbox.

Job ID: {job['job_id']}
Tool: {job['tool']}
Model: {job.get('model', 'unknown')}
Profile: {job.get('profile', 'unknown')}
Benchmark: {job.get('benchmark', 'unknown')}

Task:
{job['task_spec']}

Benchmark context:
{benchmark.get('description', 'No benchmark description provided.')}

Repository / dataset hints:
- repo_url: {benchmark_data.get('repo_url', '')}
- repo_commit: {benchmark_data.get('repo_commit', '')}
- dataset_path: {benchmark_data.get('dataset_path', '')}
- notes: {benchmark_data.get('notes', '')}

Verification hints:
- type: {verification.get('type', '')}
- command: {verification.get('command', '')}
- success_regex: {verification.get('success_regex', '')}

Requirements:
- Write outputs into the provided output directory.
- Produce a short summary.
- Prefer minimal, verifiable work.
"""
    Path(args.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
