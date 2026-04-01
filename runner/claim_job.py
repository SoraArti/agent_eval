#!/usr/bin/env python3
from __future__ import annotations

from common import connect_db, ensure_jobs_registered, utc_now, worker_name


def main() -> None:
    ensure_jobs_registered()
    conn = connect_db()
    row = conn.execute(
        """
        select job_id
        from jobs
        where status = 'PENDING'
        order by job_id asc
        limit 1
        """
    ).fetchone()
    if row is None:
        print("", end="")
        conn.close()
        return

    job_id = row["job_id"]
    conn.execute(
        """
        update jobs
        set status = 'RUNNING', claimed_by = ?, updated_at = ?
        where job_id = ? and status = 'PENDING'
        """,
        (worker_name(), utc_now(), job_id),
    )
    conn.commit()
    conn.close()
    print(job_id)


if __name__ == "__main__":
    main()
