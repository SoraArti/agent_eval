# Next Steps

This repository is now usable as a local dry-run evaluation scaffold.

To turn it into a real benchmark harness, the next work should be split into parallel tracks.

## Track A: Bench Integration

- replace demo jobs with real tasks from a selected benchmark
- add benchmark-specific verification metadata
- add profiles such as `locked_down` and `practical`
- add a small first batch of jobs for smoke testing

## Track B: Tool Integration

- wire real `Claude Code` invocation into `envs/claude_code/run.sh`
- wire real `Codex` invocation into `envs/codex/run.sh`
- add environment variable validation in `healthcheck.sh`
- capture richer transcripts if the real CLIs expose them

## Track C: Orchestration Hardening

- add retry policy for infra failures
- add timeout enforcement in `runner/run_job.py`
- add per-profile policy metadata
- add stale `RUNNING` recovery
- add structured judge output separate from tool output

## First Real Milestone

The first meaningful milestone is:

- 1 benchmark family
- 2 tools
- 5 to 20 jobs
- all runnable through `worker_loop.sh`

That is enough to start comparing behavior without overbuilding the infrastructure.
