# eval-runner 中文说明

`eval-runner` 是一个面向 `Claude Code`、`Codex` 等编程 agent 的最小评测执行框架。

它当前的目标不是一次性做成完整平台，而是先把下面三件事跑通：

1. 自动搭建工具环境
2. 自动运行一批 benchmark job
3. 自动完成 `setup -> eval -> summary` 的整条闭环

## 当前能力

目前仓库已经包含：

- benchmark / job manifest 结构
- tool adapter 结构
- runner 主链路
- judge / summary 输出
- `setup_tool_env.py`
- `run_benchmark_batch.py`
- `orchestrate_eval.py`

这意味着它已经可以支持以下三类入口：

### 1. 自动搭建工具环境

```bash
python3 runner/setup_tool_env.py --tool codex
```

这个入口会：

- 调用对应工具的 `install.sh`
- 调用对应工具的 `healthcheck.sh`
- 自动记录 setup 结果到 `state/setup_<tool>.json`

### 2. 自动运行 benchmark batch 并评分

```bash
python3 runner/run_benchmark_batch.py --tool codex --benchmark swe_bench_lite_stub
```

这个入口会：

- 读取匹配的 job manifests
- 逐个执行 job
- 调用 judge
- 输出 batch 级统计结果

输出文件位于：

- `state/batch_<benchmark>_<tool>.json`

### 3. 自动编排 setup + eval + summary

```bash
python3 runner/orchestrate_eval.py --tool codex --benchmark swe_bench_lite_stub
```

这个入口会顺序执行：

- `bootstrap`
- `setup_tool_env.py`
- `run_benchmark_batch.py`
- `summarize.py`

输出文件位于：

- `state/orchestrate_<tool>_<benchmark>.json`

## 目录结构

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
    tasks_schema.md
  runner/
  docs/
  tests/
```

## 三层结构

仓库分成三层：

### 1. Bench Layer

位置：

- `manifests/benchmarks/*.yaml`
- `manifests/jobs/*.yaml`

作用：

- 定义 benchmark 元数据
- 定义具体 job
- 描述 task 与 profile

### 2. Tool Environment Layer

位置：

- `envs/base/*`
- `envs/claude_code/*`
- `envs/codex/*`

作用：

- 安装工具依赖
- 检查工具是否可用
- 把通用 job 转换成具体 CLI 调用

### 3. Runner Layer

位置：

- `runner/*`

作用：

- 注册 job
- claim / run / judge / summarize
- 输出 heartbeat、metadata、result、judge、batch report

## 当前已验证路径

目前已经验证过一条完整闭环：

- `tool = codex`
- `benchmark = swe_bench_lite_stub`

验证步骤：

```bash
python3 runner/setup_tool_env.py --tool codex
python3 runner/orchestrate_eval.py --tool codex --benchmark swe_bench_lite_stub
python3 runner/summarize.py
```

该闭环已经可以自动完成：

- setup
- batch 执行
- judge
- summary

## 真实 CLI 接入

当前工具层支持两种模式：

- 显式指定命令
- 自动探测本机已安装 CLI

环境变量约定：

- `CLAUDE_CODE_CMD`
- `CLAUDE_CODE_ARGS`
- `CLAUDE_CODE_ENV`
- `CODEX_CMD`
- `CODEX_ARGS`
- `CODEX_ENV`

自动探测顺序：

- `claude_code`: `claude`，然后 `claude-code`
- `codex`: `codex`

## 当前限制

这版仍然是最小可用版本，还没有覆盖：

- 容器隔离
- 多机调度
- 严格 turn 限制
- 完整 transcript 标准化
- 大规模真实 benchmark 数据接入

## 下一步

下一步更值得做的是：

1. 把 `stub benchmark` 换成真实 benchmark 样本
2. 继续收紧 `codex` / `claude` 的 real-run 接口
3. 增加更稳定的 judge 与 batch report
4. 扩展到多工具、多 benchmark 的批量比较
