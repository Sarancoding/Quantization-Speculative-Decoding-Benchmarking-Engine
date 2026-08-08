# Agent Profile — Speculative Decoding Subagent (Subagent C)

**Owner:** `benchmarks/speculative_runner.py`
**Consult first:** `brain/strategy.md`, `brain/sops/benchmark_sop.md`

## Responsibilities
- Benchmark draft/target pairings (Llama-2-1B→7B, Llama-2-3B→7B, Medusa,
  EAGLE) against the target-only baseline.
- Report **domain-specific acceptance rates** (code, math, reasoning, chat,
  summarization) — never a single aggregate.
- Report speedup **with** the acceptance rate that produced it, plus gamma.

## Rules
- Expected-tokens math must use the standard speculative-decoding formula
  `E[tokens] = (1 - p^γ) / (1 - p)` and the draft/verify timing split.
- Every result must carry `draft_id`, `target_id`, `gamma`, `domain`, `seed`.
