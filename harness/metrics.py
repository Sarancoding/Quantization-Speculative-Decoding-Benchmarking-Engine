"""Metric computation utilities shared by all runners.

All functions are pure and dependency-light (numpy only) so the pipeline can
run headless on CPU.
"""
from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


def mean(xs: Sequence[float]) -> float:
    return float(np.mean(xs)) if xs else 0.0


def median(xs: Sequence[float]) -> float:
    return float(np.median(xs)) if xs else 0.0


def p90(xs: Sequence[float]) -> float:
    return float(np.percentile(xs, 90)) if xs else 0.0


def latency_stats(timings_ms: Sequence[float]) -> dict:
    """Return mean/median/p90 latency in ms."""
    return {
        "latency_ms_mean": round(mean(timings_ms), 3),
        "latency_ms_median": round(median(timings_ms), 3),
        "latency_ms_p90": round(p90(timings_ms), 3),
    }


def tokens_per_sec(tokens: int, elapsed_s: float) -> float:
    return round(tokens / elapsed_s, 3) if elapsed_s > 0 else 0.0


def memory_footprint_gb(num_params: float, bits: int, overhead_gb: float = 0.6) -> float:
    """Model weights in memory: params * bits / 8 bytes, plus a small overhead."""
    return round((num_params * bits / 8.0) / 1e9 + overhead_gb, 3)


def expected_tokens_speculative(acceptance: float, gamma: int) -> float:
    """E[tokens] per verification step under speculative decoding.

    Standard result: E = (1 - p^gamma) / (1 - p) for p < 1, else gamma + 1.
    """
    if acceptance >= 1.0:
        return float(gamma + 1)
    return float((1.0 - acceptance**gamma) / (1.0 - acceptance))


def pareto_optimal(
    rows: Sequence[dict],
    maximize: Sequence[str] = ("tokens_per_sec",),
    minimize: Sequence[str] = ("mem_gb", "latency_ms_mean"),
) -> list[int]:
    """Return indices of rows that are Pareto-optimal.

    A row is dominated if another row is >= on every maximize axis, <= on every
    minimize axis, and strictly better on at least one.
    """
    n = len(rows)
    if n == 0:
        return []
    keys_max = [m for m in maximize if m in rows[0]]
    keys_min = [m for m in minimize if m in rows[0]]

    def dominates(i: int, j: int) -> bool:
        better = False
        for k in keys_max:
            if rows[i][k] < rows[j][k] - 1e-12:
                return False
            if rows[i][k] > rows[j][k] + 1e-12:
                better = True
        for k in keys_min:
            if rows[i][k] > rows[j][k] + 1e-12:
                return False
            if rows[i][k] < rows[j][k] - 1e-12:
                better = True
        return better

    return [j for j in range(n) if not any(dominates(i, j) for i in range(n) if i != j)]
