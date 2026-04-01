#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

import judge_job  # noqa: E402


class JudgeCommandStubTests(unittest.TestCase):
    def test_runs_verification_command_and_matches_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = judge_job.judge_command_stub(
                "bash -lc 'echo PASS'",
                "PASS",
                Path(tmpdir),
            )

        self.assertTrue(result["passed"])
        self.assertEqual(result["reason"], "verification matched")


if __name__ == "__main__":
    unittest.main()
