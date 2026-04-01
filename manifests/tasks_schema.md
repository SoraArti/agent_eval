# Task Schema (Job Manifest)

Each job file in `manifests/jobs/` is a self-contained task definition.

Minimal required keys:

- `job_id`: unique id (string)
- `benchmark`: benchmark_id defined in `manifests/benchmarks/`
- `tool`: tool integration name (e.g. `claude_code`, `codex`)
- `model`: model id or placeholder
- `profile`: policy profile name (e.g. `locked_down`, `practical`)
- `task_spec`: human-readable task instructions

Optional keys:

- `timeout_min`: wall clock time budget
- `retries`: retry count for infra errors
- `params`: tool-specific parameters (dict-like)

Example:

```yaml
job_id: swe_lite_0001_claude_code
benchmark: swe_bench_lite_stub
tool: claude_code
model: placeholder-default
profile: practical
timeout_min: 90
retries: 0
params:
  mode: dry_run
task_spec: |
  Fix the failing test described in ISSUE-1234.
  Run ./run_tests.sh and ensure it passes.
```
