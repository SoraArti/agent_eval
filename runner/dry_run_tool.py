#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True)
    parser.add_argument("--job-json", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    job = json.loads(args.job_json)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    artifact = outdir / "generated_artifact.txt"
    artifact.write_text(
        f"tool={args.tool}\njob_id={job['job_id']}\nutc={now}\n",
        encoding="utf-8",
    )

    result = {
        "status": "success",
        "tool": args.tool,
        "job_id": job["job_id"],
        "artifact": str(artifact),
        "summary": f"Dry-run completed for {args.tool}",
    }
    (outdir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
