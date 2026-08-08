# Company Brain — Knowledge Layer

> The single source of truth every agent consults before acting.
> **Company Brain first: no task starts without referencing this layer.**

## Contents

| Path | What it is |
| --- | --- |
| `strategy.md` | Why we benchmark, what we measure, how we decide what wins |
| `sops/benchmark_sop.md` | Standard operating procedure for running a benchmark |
| `sops/orchestration_sop.md` | SOP for the orchestrator loop (phases + gates) |
| `examples/pareto_example.md` | Annotated good example — the taste gate's reference |
| `agents/` | Agent profiles: Quant, Spec, Analyst, DevOps |
| `client_learnings.md` | Friction log shared with the client org |

## How to use

1. Read `strategy.md` to understand the measurement philosophy.
2. Follow `sops/` for anything that executes or reviews a benchmark.
3. Judge artifacts against `examples/` before merging.
4. Log every failure/friction in `../tasks/lessons.md` and (client-facing
   lessons only) `client_learnings.md`.
