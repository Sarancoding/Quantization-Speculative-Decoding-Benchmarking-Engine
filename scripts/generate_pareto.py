"""Analyst (Subagent D): Pareto Efficiency Frontier chart.

Reads the merged metrics and plots throughput (tokens/s) vs memory footprint
(GB) with latency as the marker color, marking the Pareto-optimal set.
Headless: forces the Agg backend so it runs anywhere.

Usage:
    python scripts/generate_pareto.py [--input artifacts/raw_metrics.json] \\
        [--output artifacts/pareto_frontier.png]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from harness.metrics import pareto_optimal


def load_metrics(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def generate_pareto(metrics_path: Path, out_path: Path) -> dict:
    metrics = load_metrics(metrics_path)
    rows = [r for r in metrics.get("quantization", []) if r.get("mem_gb") is not None]
    if not rows:
        raise SystemExit("no quantization rows with mem_gb found — cannot plot Pareto")

    # Frontier axes: max throughput, min memory, min latency, min quality cost.
    # Including the quality axis keeps the frontier meaningful (a fast, tiny,
    # low-quality config does not dominate a slower, higher-quality one).
    idx = pareto_optimal(
        rows,
        maximize=("tokens_per_sec",),
        minimize=("mem_gb", "latency_ms_mean", "quality_ppl"),
    )
    frontier = [rows[i] for i in idx]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    colors = {"FP16": "#58a6ff", "FP8": "#3fb950", "AWQ": "#f0883e", "GPTQ": "#bc8cff"}
    for row in rows:
        color = colors.get(row["method"], "#8b949e")
        ax.scatter(
            row["mem_gb"], row["tokens_per_sec"],
            s=140, color=color, edgecolors="white", linewidths=1.2, zorder=3,
        )
        ax.annotate(
            f"{row['method']} ({row['bits']}bit)",
            (row["mem_gb"], row["tokens_per_sec"]),
            textcoords="offset points", xytext=(8, 6), fontsize=9,
            color="#c9d1d9", zorder=4,
        )

    # Pareto frontier step line (ascending memory order).
    order = sorted(frontier, key=lambda r: r["mem_gb"])
    xs = [r["mem_gb"] for r in order]
    ys = [r["tokens_per_sec"] for r in order]
    ax.step(xs, ys, where="post", color="#f0f6fc", linewidth=2, linestyle="--", alpha=0.9, label="Pareto frontier")

    ax.set_xlabel("Memory footprint (GB) — lower is better", color="#c9d1d9")
    ax.set_ylabel("Throughput (tokens/s) — higher is better", color="#c9d1d9")
    ax.set_title(
        f"Quantization Pareto Efficiency Frontier\nmode={metrics.get('mode')} seed={metrics.get('seed')} "
        f"({metrics.get('generated_at', '')[:10]})",
        color="#f0f6fc", fontsize=13,
    )
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.tick_params(colors="#c9d1d9")
    ax.grid(color="#21262d", linestyle=":", linewidth=0.6)
    ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", loc="lower right")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    frontier_names = [r["method"] for r in order]
    print(f"[pareto] chart saved: {out_path}")
    print(f"[pareto] frontier set: {', '.join(frontier_names)}")
    return {"frontier": frontier_names, "n": len(rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render the Pareto efficiency frontier")
    parser.add_argument("--input", default="artifacts/raw_metrics.json")
    parser.add_argument("--output", default="artifacts/pareto_frontier.png")
    args = parser.parse_args()
    generate_pareto(Path(args.input), Path(args.output))
