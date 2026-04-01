# eval-runner

Minimal evaluation runner for agentic coding tools such as Claude Code and Codex.

This repository is intended to evaluate coding agents through three automated steps:

- setup a tool environment
- run one benchmark batch
- orchestrate setup plus evaluation plus summary in a single entrypoint

This first version is designed to be:

- runnable on a single machine
- expandable to multiple workers later
- usable in dry-run mode before real CLIs are wired in
- explicit about job state, logs, and outputs

## Layout

```text
eval-runner/
  envs/
    base/
    claude_code/
    codex/
  manifests/
    benchmarks/
    jobs/
    models.yaml
    profiles.yaml
  outputs/
  runner/
  state/
```

## Quick start

1. Bootstrap the local runner:

```bash
bash runner/bootstrap.sh
```

2. Run a health check:

```bash
bash envs/base/healthcheck.sh
```

3. Run one job directly:

```bash
python3 runner/run_job.py --job manifests/jobs/demo_claude_code.yaml
```

4. Run the worker loop:

```bash
bash runner/worker_loop.sh --once
```

5. Summarize outputs:

```bash
python3 runner/summarize.py
```

6. Setup one tool environment:

```bash
python3 runner/setup_tool_env.py --tool claude_code
```

7. Run a benchmark batch for one tool:

```bash
python3 runner/run_benchmark_batch.py --tool codex --benchmark swe_bench_lite_stub
```

The batch output includes `batch_summary` with totals and judge pass/fail counts.

8. Orchestrate bootstrap + tool setup + batch eval:

```bash
python3 runner/orchestrate_eval.py --tool claude_code --benchmark repobench_stub
```

## Current validated path

The current repository has already validated a full local closure for:

- `tool = codex`
- `benchmark = swe_bench_lite_stub`

The validated flow is:

```bash
python3 runner/setup_tool_env.py --tool codex
python3 runner/orchestrate_eval.py --tool codex --benchmark swe_bench_lite_stub
python3 runner/summarize.py
```

Artifacts are written to:

- `state/setup_<tool>.json`
- `state/batch_<benchmark>_<tool>.json`
- `state/orchestrate_<tool>_<benchmark>.json`

## Real CLI wiring

The default `claude_code` and `codex` integrations are safe placeholders:

- if `CLAUDE_CODE_CMD` or `CODEX_CMD` is provided, the runner will execute it
- otherwise it will try to auto-detect installed CLIs
- otherwise the tool integration falls back to a deterministic dry-run stub

Expected pattern:

```bash
export CLAUDE_CODE_CMD="/path/to/real/claude-cli"
export CODEX_CMD="/path/to/real/codex-cli"
```

Auto-detect search order:

- `claude_code`: `claude`, then `claude-code`
- `codex`: `codex`

Optional environment variables:

- `CLAUDE_CODE_ARGS` / `CODEX_ARGS` for extra CLI flags
- `CLAUDE_CODE_ENV` / `CODEX_ENV` for env files with `KEY=VALUE` lines

The current implementation passes a prompt file and output directory to the tool wrapper script.
You can replace the placeholder command construction in:

- `envs/claude_code/run.sh`
- `envs/codex/run.sh`

without changing the runner core.

## Current scope

This version includes:

- SQLite-backed job state
- claim/run/complete job lifecycle
- per-job output directory
- structured metadata, heartbeat, result, logs
- demo benchmark plus stub benchmarks and job templates for SWE-bench Lite and RepoBench

Task schema reference:

- `manifests/tasks_schema.md`
- `manifests/profiles.yaml`

This version does not yet include:

- containerized isolation
- internet policy enforcement
- strict turn limits
- transcript capture from real vendor CLIs
- multi-host coordination
