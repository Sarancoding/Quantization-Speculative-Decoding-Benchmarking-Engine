# Agent Profile — Quant Subagent (Subagent B)

**Owner:** `benchmarks/quantization_runner.py`, `benchmarks/config.py`
**Consult first:** `brain/strategy.md`, `brain/sops/benchmark_sop.md`

## Responsibilities
- Benchmark the quantization matrix: **FP16, FP8 (bitsandbytes), AWQ, GPTQ**.
- Return one metric row per (model, method) with full provenance.
- Keep the quality proxy (PPL) and memory footprint honest and labeled.

## Rules
- Never report a latency number without repetition stats (mean/median/p90).
- Simulate mode must be deterministic for a given seed.
- Live mode must fail loudly with a helpful message if the backend
  (bitsandbytes / autoawq / gptqmodel / CUDA) is unavailable — never silently
  fall back to simulated numbers.
