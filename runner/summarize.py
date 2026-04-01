#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def main() -> None:
    rows = []
    for result_path in sorted(OUTPUTS.glob("*/result.json")):
        data = json.loads(result_path.read_text(encoding="utf-8"))
        judge_path = result_path.parent / "judge.json"
        heartbeat_path = result_path.parent / "heartbeat.json"
        metadata_path = result_path.parent / "metadata.json"
        judge = json.loads(judge_path.read_text(encoding="utf-8")) if judge_path.exists() else {}
        heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8")) if heartbeat_path.exists() else {}
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        rows.append(
            {
                "job_id": data.get("job_id"),
                "tool": data.get("tool"),
                "benchmark_id": metadata.get("benchmark_id"),
                "runner_status": heartbeat.get("status"),
                "tool_status": data.get("status"),
                "judge_passed": judge.get("passed"),
                "summary": data.get("summary"),
            }
        )

    print(json.dumps({"jobs": rows, "count": len(rows)}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
