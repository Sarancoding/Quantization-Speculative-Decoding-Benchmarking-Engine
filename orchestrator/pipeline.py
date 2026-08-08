"""Phase orchestrator (Hermes strategy: fan out -> cross-verify -> merge).

Runs the full automated loop:

    Phase 1  brain/ gate
    Phase 2  harness + orchestrator (implicit — modules must import)
    Phase 3  fan out quant + spec runners -> merge metrics
    Phase 4  eval loop (schema + sanity + taste gate)
    Phase 5  artifacts (pareto chart, technical writeup, PDFs)
    Phase 6  deploy is executed separately via scripts/push_to_github.sh

Usage:
    python -m orchestrator.pipeline --mode simulate --seed 42 --num-runs 5
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from benchmarks.quantization_runner import run_quantization_benchmark
from benchmarks.speculative_runner import run_speculative_benchmark
from orchestrator.eval_loop import check_metrics, check_taste
from orchestrator.token_budget import default_budget, phase_clock
from scripts.generate_pareto import generate_pareto
from scripts.generate_pdfs import generate_pdfs
from scripts.generate_writeup import generate_writeup

SCHEMA_VERSION = "1.0"
ROOT = Path(__file__).resolve().parent.parent


def _phase_gate(name: str, check: bool) -> None:
    if not check:
        print(f"[pipeline] GATE FAILED: {name}")
        sys.exit(1)
    print(f"[pipeline] gate passed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantization & speculative decoding benchmark pipeline")
    parser.add_argument("--mode", choices=["simulate", "live"], default="simulate")
    parser.add_argument("--num-runs", type=int, default=5)
    parser.add_argument("--seed", type=int, default=int(os.environ.get("BENCH_SEED", "42")))
    parser.add_argument("--no-pdfs", action="store_true", help="skip PDF generation")
    args = parser.parse_args()

    budget = default_budget()

    # ---- Phase 1: Company Brain gate -------------------------------------
    _phase_gate("brain/ present", (ROOT / "brain").is_dir())
    _phase_gate("AGENTS.md present", (ROOT / "AGENTS.md").is_file())
    budget.spend("brain", 1000)

    # ---- Phase 3: fan out runners, then merge -----------------------------
    with phase_clock("benchmarks"):
        with ThreadPoolExecutor(max_workers=2) as ex:
            fq = ex.submit(run_quantization_benchmark, mode=args.mode, num_runs=args.num_runs, seed=args.seed)
            fs = ex.submit(run_speculative_benchmark, mode=args.mode, num_runs=args.num_runs, seed=args.seed)
            quant_rows = fq.result()
            spec_rows = fs.result()
    budget.spend("benchmarks", 8000)

    merged = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": args.mode,
        "seed": args.seed,
        "num_runs": args.num_runs,
        "system": {
            "python": sys.version.split()[0],
            "cwd": "<repo_root>",  # no absolute local paths in committed provenance
        },
        "quantization": quant_rows,
        "speculative": spec_rows,
    }

    results_dir = ROOT / "results"
    artifacts_dir = ROOT / "artifacts"
    results_dir.mkdir(exist_ok=True)
    artifacts_dir.mkdir(exist_ok=True)

    (results_dir / "raw_metrics.json").write_text(json.dumps(merged, indent=2), encoding="utf-8")
    (artifacts_dir / "raw_metrics.json").write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"[pipeline] merged {len(quant_rows)} quant rows + {len(spec_rows)} spec rows")

    # ---- Phase 4: Eval Loop stage 1 — metrics check (pre-artifact) ---------
    with phase_clock("eval"):
        metric_errors = check_metrics(merged)
    budget.spend("eval", 3000)
    if metric_errors:
        print("[pipeline] metrics check FAILED — see tasks/lessons.md; fix and re-run.")
        return 1

    # ---- Phase 5: artifacts ----------------------------------------------
    with phase_clock("artifacts"):
        frontier = generate_pareto(artifacts_dir / "raw_metrics.json", artifacts_dir / "pareto_frontier.png")
        writeup = generate_writeup(artifacts_dir / "raw_metrics.json", artifacts_dir / "technical_writeup.md")
        if not args.no_pdfs:
            generate_pdfs(ROOT)
        # Eval Loop stage 2 — taste gate on the generated artifacts.
        taste_issues = check_taste(artifacts_dir, ROOT / "tasks" / "lessons.md")
    budget.spend("artifacts", 6000)
    if taste_issues:
        print("[pipeline] taste gate FAILED — see tasks/lessons.md; fix and re-run.")
        return 1

    status = {
        "status": "ok",
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": args.mode,
        "seed": args.seed,
        "frontier": frontier,
        "writeup_chars": len(writeup),
        "token_budget": budget.report(),
    }
    (results_dir / "run_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")

    print("\n[pipeline] SUMMARY")
    print(f"  mode        : {args.mode} (seed={args.seed}, runs={args.num_runs})")
    print(f"  frontier    : {', '.join(frontier['frontier'])}")
    print(f"  artifacts   : {artifacts_dir}")
    print(f"  eval loop   : PASS")
    print(f"  token spend : {budget.report()['pct']}% of budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
