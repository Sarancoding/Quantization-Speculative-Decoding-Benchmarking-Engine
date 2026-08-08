# Lessons & Friction Log

> Append-only. Orchestrator and DevOps subagents write here whenever a step
> fails or a non-obvious decision is made, then reference the entry from the
> task board.

## 2026-08-08 — Eval Loop ordering bug (caught by the loop itself)
- **Failure:** First pipeline run failed its own gate: the taste gate ran
  before Phase 5 generated the artifacts, so `artifacts/pareto_frontier.png`
  and `artifacts/technical_writeup.md` were judged missing.
- **Fix:** Split the Eval Loop into `check_metrics` (schema/sanity, pre-
  artifact) and `check_taste` (post-artifact). Pipeline now runs metrics
  check → artifacts → taste gate. Also simplified the token-budget warning to
  cumulative-spend semantics.
- **Lesson:** The Eval Loop working as intended — it rejected a badly ordered
  run instead of shipping unverified output.

## 2026-08-08 — Repo bootstrap
- **Context:** Fresh repo contained only a LICENSE (single "Initial commit").
  No `AGENTS.md` existed to copy, so `AGENTS.md` was authored from the spec's
  constraint section.
- **Decision:** Started the project from scratch in this repo (per client
  instruction "start fresh and forget last project").
- **Decision:** Simulated benchmark mode (seeded, deterministic, CPU-only) is
  the default so the full pipeline — metrics → Pareto → writeup → PDFs — is
  verifiable in CI/sandbox without GPUs. Live mode is a first-class path.
- **Lesson:** When the sandbox has no `freebuff-preview` CLI, persist preview
  commands in `package.json` scripts (`dev` / `build` / `start`) so the
  platform's preview controls can pick them up.

## 2026-08-08 12:22:13 — Eval Loop issues
- pareto chart missing or too small: artifacts/pareto_frontier.png
- writeup missing: artifacts/technical_writeup.md
