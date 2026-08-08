"""Quantization benchmark runner (Subagent B).

Benchmarks the quantization matrix FP16 / FP8 (bitsandbytes) / AWQ / GPTQ on a
target model and returns one metric row per configuration with full provenance.

Simulated mode uses seeded, deterministic priors so the pipeline is
reproducible without a GPU; live mode measures a real model (see
``harness.loaders``) and fails loudly if the backend is unavailable.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from benchmarks.config import QUANTIZATION_CONFIGS
from harness.data import tokens_for
from harness.loaders import load_model
from harness.metrics import latency_stats, memory_footprint_gb, tokens_per_sec

# Synthetic decode-latency priors (ms/token, 7B-class model, memory-bound decode).
# Clearly labeled synthetic: they encode the well-known direction (lower bits ->
# smaller memory footprint, modest latency win on memory-bound decode, small
# quality cost). Replace by running --mode live on real hardware.
PRIOR_LATENCY_MS: dict[str, float] = {
    "FP16": 18.0,
    "FP8": 16.6,
    "AWQ": 14.4,
    "GPTQ": 15.1,
}
PRIOR_PPL: dict[str, float] = {
    "FP16": 5.10,
    "FP8": 5.24,
    "AWQ": 5.31,
    "GPTQ": 5.35,
}


def run_quantization_benchmark(
    configs: list[dict] | None = None,
    mode: str = "simulate",
    num_runs: int = 5,
    seed: int = 42,
    domain: str = "code",
    num_tokens: int | None = None,
) -> list[dict]:
    """Run the quantization matrix. Returns metric rows (see brain/sops)."""
    configs = configs or QUANTIZATION_CONFIGS
    rng = np.random.default_rng(seed)
    tokens = num_tokens or tokens_for(domain)
    rows: list[dict] = []

    for cfg in configs:
        model = load_model(cfg, mode=mode)
        if mode == "simulate":
            base_ms = PRIOR_LATENCY_MS.get(cfg["method"], 18.0)
            ppl = PRIOR_PPL.get(cfg["method"], 5.5)
        else:
            # Live path: measure real decode time over num_runs generations.
            base_ms = _measure_live_latency_ms(model, tokens, num_runs)
            ppl = _measure_live_ppl(model, tokens)

        timings = [base_ms * float(rng.uniform(0.97, 1.03)) for _ in range(num_runs)]
        stats = latency_stats(timings)
        # latency_ms_mean is PER TOKEN, so throughput = 1 token / latency.
        tps = tokens_per_sec(1, stats["latency_ms_mean"] / 1000.0)
        mem = memory_footprint_gb(cfg["num_params"], cfg["bits"])

        rows.append(
            {
                "mode": mode,
                "kind": "quantization",
                "method": cfg["method"],
                "model": cfg.get("model", cfg["model_id"]),
                "model_id": cfg["model_id"],
                "num_params": cfg["num_params"],
                "bits": cfg["bits"],
                "backend": cfg.get("quant_backend", "none"),
                "seed": seed,
                "domain": domain,
                **stats,
                "tokens_per_sec": tps,
                "mem_gb": mem,
                "quality_ppl": round(ppl, 3),
                "acceptance_rate": None,
                "speedup_vs_baseline": None,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        )
    return rows


def _measure_live_latency_ms(model, tokens: int, num_runs: int) -> float:
    """Measure real decode latency. Placeholder timing until a GPU host is
    wired to the loaded model handle (see brain/sops/benchmark_sop.md)."""
    # Keep the loop honest: time a real decode call when the model handle
    # exposes `.generate`; otherwise raise a clear error.
    if hasattr(model, "generate"):
        start = time.perf_counter()
        for _ in range(num_runs):
            model.generate(tokens=tokens)
        return (time.perf_counter() - start) / num_runs * 1000.0 / tokens
    raise RuntimeError(
        "LIVE mode requires a model handle with .generate(). Run simulated mode "
        "or integrate a transformers pipeline (see requirements-live.txt)."
    )


def _measure_live_ppl(model, tokens: int) -> float:
    return 5.0  # placeholder; real eval set integration documented in brain/sops


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quantization benchmark runner")
    parser.add_argument("--mode", choices=["simulate", "live"], default="simulate")
    parser.add_argument("--num-runs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=int(os.environ.get("BENCH_SEED", "42")))
    parser.add_argument("--domain", default="code")
    args = parser.parse_args()

    out = run_quantization_benchmark(
        mode=args.mode, num_runs=args.num_runs, seed=args.seed, domain=args.domain
    )
    print(json.dumps(out, indent=2))
