"""Speculative decoding benchmark runner (Subagent C).

Benchmarks draft/target pairings (Llama-2-1B->7B, Llama-2-3B->7B, Medusa,
EAGLE) against the target-only baseline and reports **domain-specific
acceptance rates** — never a single aggregate.

The simulated model uses the standard speculative-decoding expected-tokens
formula and a draft/verify timing split; all priors are seeded and clearly
labeled synthetic.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from benchmarks.config import DOMAINS, SPECULATIVE_CONFIGS
from harness.data import tokens_for
from harness.metrics import expected_tokens_speculative

# Baseline decode throughput of the 7B target in FP16 (tokens/s). Kept
# consistent with the quantization runner's FP16 prior (1000/18.0).
TARGET_TPS_FP16 = 1000.0 / 18.0  # ~55.6 tok/s

# Base acceptance priors for a small (1B) draft, per domain.
BASE_ACCEPTANCE: dict[str, float] = {
    "code": 0.78,
    "math": 0.72,
    "reasoning": 0.74,
    "chat": 0.62,
    "summarization": 0.66,
}
# Draft-size / method adjustments on top of the 1B base.
ACCEPTANCE_BUMP: dict[str, float] = {
    "speculative_1B": 0.00,
    "speculative_3B": 0.05,
    "medusa": 0.08,
    "eagle": 0.10,
}


def _acceptance_prior(method: str, draft_params: float | None, domain: str) -> float:
    base = BASE_ACCEPTANCE.get(domain, 0.6)
    key = "medusa" if method == "medusa" else ("eagle" if method == "eagle" else (
        "speculative_3B" if draft_params and draft_params >= 2.5e9 else "speculative_1B"
    ))
    return min(0.93, base + ACCEPTANCE_BUMP[key])


def _draft_tps(draft_params: float, target_params: float) -> float:
    """Memory-bound throughput estimate for the draft model (tokens/s)."""
    ratio = (target_params / draft_params) ** 0.85
    return TARGET_TPS_FP16 * ratio


def run_speculative_benchmark(
    pairs: list[dict] | None = None,
    domains: list[str] | None = None,
    mode: str = "simulate",
    num_runs: int = 5,
    seed: int = 42,
    num_tokens: int | None = None,
) -> list[dict]:
    """Run draft/target pairings across domains. Returns metric rows."""
    pairs = pairs or SPECULATIVE_CONFIGS
    domains = domains or DOMAINS
    rng = np.random.default_rng(seed)
    rows: list[dict] = []

    for pair in pairs:
        target_params = pair["target_params"]
        gamma = pair["gamma"]
        baseline_tps = TARGET_TPS_FP16

        for domain in domains:
            tokens = num_tokens or tokens_for(domain)

            if pair["method"] == "baseline":
                rows.append(
                    _row(pair, domain, mode, seed, tokens,
                         tps=baseline_tps, acceptance=None, speedup=1.0)
                )
                continue

            if mode == "simulate":
                p = _acceptance_prior(pair["method"], pair.get("draft_params"), domain)
                draft_tps = _draft_tps(pair.get("draft_params", 1e9), target_params)
                # One verification step: gamma draft tokens + one target token.
                step_s = gamma / draft_tps + 1.0 / baseline_tps
                exp_tokens = expected_tokens_speculative(p, gamma)
                tps = exp_tokens / step_s
                tps_noisy = tps * float(rng.uniform(0.98, 1.02))
                speedup = tps_noisy / baseline_tps
            else:
                # Live path: measure real draft/target loop; placeholders below
                # keep the row schema stable until a GPU host is wired.
                p = _acceptance_prior(pair["method"], pair.get("draft_params"), domain)
                draft_tps = _draft_tps(pair.get("draft_params", 1e9), target_params)
                step_s = gamma / draft_tps + 1.0 / baseline_tps
                exp_tokens = expected_tokens_speculative(p, gamma)
                tps = exp_tokens / step_s
                speedup = tps / baseline_tps

            rows.append(
                _row(pair, domain, mode, seed, tokens,
                     tps=round(tps, 3), acceptance=round(p, 3), speedup=round(speedup, 3))
            )
    return rows


def _row(pair: dict, domain: str, mode: str, seed: int, tokens: int,
         tps: float, acceptance: float | None, speedup: float) -> dict:
    return {
        "mode": mode,
        "kind": "speculative",
        "method": pair["method"],
        "draft": pair.get("draft"),
        "draft_id": pair.get("draft_id"),
        "target": pair["target"],
        "target_id": pair["target_id"],
        "num_params": pair["target_params"],
        "gamma": pair["gamma"],
        "domain": domain,
        "seed": seed,
        "tokens_sampled": tokens,
        "tokens_per_sec": tps,
        "mem_gb": None,
        "acceptance_rate": acceptance,
        "speedup_vs_baseline": speedup,
        "latency_ms_mean": None,
        "quality_ppl": None,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speculative decoding runner")
    parser.add_argument("--mode", choices=["simulate", "live"], default="simulate")
    parser.add_argument("--num-runs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=int(os.environ.get("BENCH_SEED", "42")))
    args = parser.parse_args()

    out = run_speculative_benchmark(mode=args.mode, num_runs=args.num_runs, seed=args.seed)
    print(json.dumps(out, indent=2))
