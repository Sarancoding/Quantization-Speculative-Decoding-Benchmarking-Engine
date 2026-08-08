# SOP — Running a Benchmark

Applies to `benchmarks/quantization_runner.py` and `benchmarks/speculative_runner.py`.

## 1. Pre-flight
- [ ] Read `brain/strategy.md`.
- [ ] Confirm config exists in `benchmarks/config.py` (method, bits, model_id,
      backend, num_params).
- [ ] Decide mode: `simulate` (default, deterministic) or `live` (GPU).

## 2. Execute
- [ ] Use the config's **model id + backend**, never a bare model name.
- [ ] Fix the prompt set from `harness/data.py` and the token budget.
- [ ] Fix the seed. Record it in every row.
- [ ] Run ≥ 3 repetitions for latency statistics; report mean/median/p90.

## 3. Record
Every metric row must include:
```json
{
  "mode": "simulate|live",
  "method": "FP16|FP8|AWQ|GPTQ|speculative|...",
  "model_id": "org/name",
  "num_params": 6.74e9,
  "bits": 16,
  "backend": "none|bitsandbytes|autoawq|gptqmodel",
  "seed": 42,
  "domain": "code",
  "latency_ms_mean": 0.0,
  "tokens_per_sec": 0.0,
  "mem_gb": 0.0,
  "quality_ppl": 0.0,
  "acceptance_rate": null,
  "speedup_vs_baseline": null
}
```

## 4. Submit
- [ ] Merge rows into `results/raw_metrics.json` (and a committed snapshot in
      `artifacts/raw_metrics.json`).
- [ ] Hand off to the Eval Loop (`orchestrator/eval_loop.py`) — never skip it.
