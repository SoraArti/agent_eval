from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "state" / "jobs.sqlite3"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml_like(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return load_simple_yaml(path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_simple_yaml(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_multiline_key: str | None = None
    multiline: list[str] = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        if not line or line.lstrip().startswith("#"):
            continue
        if current_multiline_key is not None:
            if raw.startswith("  "):
                multiline.append(raw[2:])
                continue
            result[current_multiline_key] = "\n".join(multiline).rstrip()
            current_multiline_key = None
            multiline = []
        if ": |" in line:
            key = line.split(": |", 1)[0].strip()
            current_multiline_key = key
            multiline = []
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = parse_scalar(value.strip())

    if current_multiline_key is not None:
        result[current_multiline_key] = "\n".join(multiline).rstrip()

    return result


def parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    if value.isdigit():
        return int(value)
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def discover_jobs() -> list[Path]:
    return sorted((ROOT / "manifests" / "jobs").glob("*.yaml"))


def discover_benchmarks() -> list[Path]:
    return sorted((ROOT / "manifests" / "benchmarks").glob("*.yaml"))


def load_benchmark(benchmark_id: str) -> dict[str, Any]:
    for path in discover_benchmarks():
        data = load_yaml_like(path)
        if data.get("benchmark_id") == benchmark_id:
            data["_path"] = str(path)
            return data
    raise FileNotFoundError(f"benchmark not found: {benchmark_id}")


def build_job_payload(job_path: Path) -> dict[str, Any]:
    job = load_yaml_like(job_path)
    benchmark_id = job.get("benchmark")
    benchmark = load_benchmark(benchmark_id) if benchmark_id else {}
    return {
        **job,
        "_job_path": str(job_path),
        "_benchmark": benchmark,
    }


def ensure_jobs_registered() -> None:
    conn = connect_db()
    conn.execute(
        """
        create table if not exists jobs (
            job_id text primary key,
            job_path text not null,
            tool text not null,
            status text not null,
            retries integer not null default 0,
            last_error text,
            claimed_by text,
            updated_at text not null
        )
        """
    )
    now = utc_now()
    for path in discover_jobs():
        data = load_yaml_like(path)
        job_id = data["job_id"]
        tool = data["tool"]
        conn.execute(
            """
            insert into jobs(job_id, job_path, tool, status, updated_at)
            values (?, ?, ?, 'PENDING', ?)
            on conflict(job_id) do nothing
            """,
            (job_id, str(path), tool, now),
        )
    conn.commit()
    conn.close()


def output_dir(job_id: str) -> Path:
    outdir = ROOT / "outputs" / job_id
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def worker_name() -> str:
    return os.environ.get("EVAL_WORKER_NAME", os.uname().nodename)
