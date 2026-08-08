# AGENTS.md — Quantization & Speculative Decoding Benchmarking Engine

> Rule of law for every agent, script, and reviewer working in this repository.
> Reference the Company Brain (`brain/`) before acting. Taste is the gate.

## Mission

Build an **end-to-end automated benchmarking engine** that produces the
**Pareto Efficiency Frontier** and technical insights for LLM **quantization**
(FP16 / FP8 / AWQ / GPTQ) and **speculative decoding** (draft/target pairing,
domain-specific acceptance rates) — and publishes those results as artifacts.

## Non-Negotiable Rules

1. **Company Brain first.** Every agent consults `brain/` (strategy, SOPs,
   examples, agent profiles) before writing code or claiming a task is done.
2. **Long-term architecture decisions.** No backward-compatibility hacks.
   Simplest correct implementation, modular layout, established libraries only.
3. **Hermes Subagent Strategy.** Fan out → Cross-verify → Merge. Never merge
   work that has not been verified by the Eval Loop.
4. **Eval Loop mandatory.** Every artifact (metrics, chart, writeup, PDF) is
   judged against the good examples in `brain/examples/` before it ships.
5. **GitHub push is a task.** A verified, gated step in the orchestrator loop —
   not an afterthought. Pre-push checklist must pass first.
6. **No secrets in source.** API keys / tokens come from the environment
   (`.env`, CI secrets). `.env`, model weights, and raw outputs are gitignored.
7. **Reproducibility.** Simulated benchmarks are seeded and deterministic;
   live benchmarks record full provenance (model ids, backend, seed, dates).

## Repository Map

| Path               | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| `brain/`           | Company Brain: strategy, SOPs, examples, agent profiles      |
| `orchestrator/`    | Pipeline orchestration, token budget, eval loop              |
| `harness/`         | Model loading, metric computation, prompt data               |
| `benchmarks/`      | Quantization + speculative decoding runners and configs      |
| `infra/`           | Environment bootstrap                                        |
| `scripts/`         | Pareto, writeup, PDF generation; push protocol; build shim   |
| `tasks/`           | `todo.md` (gated checklist) and `lessons.md` (error log)     |
| `results/`         | Raw benchmark outputs (gitignored)                           |
| `artifacts/`       | Curated deliverables: Pareto chart, writeup, raw metrics     |
| `web/` + `server.js` | Docs/landing server for the Freebuff preview                 |

## Workflow Mode

Strictly adhere to **Workflow Orchestration**, **System Architecture**, and this
file. Phases:

1. **Company Brain (knowledge layer)** — populate `brain/`.
2. **Harness & Orchestrator (system design)** — `orchestrator/`, `harness/`.
3. **Execution & Skills (the build)** — fan out runners, merge metrics.
4. **Eval Loop (verification)** — automated checks + taste gate.
5. **Artifacts & Landing Page** — Pareto chart, writeup, PDFs.
6. **GitHub Deployment** — gated pre-push checklist, push, post-push verify.
