#!/usr/bin/env python3
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "state" / "jobs.sqlite3"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
