# Architecture

`eval-runner` is split into three layers so benchmark work and tool-environment work can proceed independently.

## 1. Bench Layer

Owned by benchmark integration work.

Files:

- `manifests/benchmarks/*.yaml`
- `manifests/jobs/*.yaml`
- `manifests/models.yaml`

Responsibility:

- define benchmark/task metadata
- define concrete jobs to run
- choose tool/model/profile combinations

This layer should not depend on specific CLI invocation details.

## 2. Tool Environment Layer

Owned by tool integration work.

Files:

- `envs/base/*`
- `envs/claude_code/*`
- `envs/codex/*`

Responsibility:

- install tool-specific dependencies
- validate tool availability
- translate a generic job into a concrete CLI invocation

This layer should not define benchmark semantics.

## 3. Runner Layer

Owned by orchestration work.

Files:

- `runner/*`

Responsibility:

- register and claim jobs
- run one job in a standard lifecycle
- write heartbeat, metadata, logs, and results
- summarize outcomes

The runner only assumes:

- there is a job manifest
- there is a tool adapter under `envs/<tool>/run.sh`

## Integration Contract

The contract between the bench layer and the tool layer is the job payload.

The runner loads a job manifest and passes its JSON payload to `envs/<tool>/run.sh`.

Tool adapters must:

1. accept two arguments:
   - serialized job JSON
   - output directory
2. write:
   - `stdout.log`
   - `stderr.log`
   - `result.json`
3. exit non-zero on failure

Benchmark authors should assume only these stable outputs exist.

## Recommended Workflow

1. Add or refine benchmark/job manifests.
2. Wire or improve the tool adapter for `claude_code`, `codex`, or another tool.
3. Run:

```bash
bash runner/bootstrap.sh
bash runner/worker_loop.sh --once
python3 runner/summarize.py
```

4. Replace dry-run jobs with real benchmark jobs once the integration is stable.
