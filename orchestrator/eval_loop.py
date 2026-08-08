"""Eval Loop (Phase 4): automated checks + Judge/Taste gate.

Runs in two stages so the pipeline gates correctly:

1. **Metrics check** (`check_metrics`) — schema validation + sanity checks on
   the merged rows. Runs *before* artifacts are generated.
2. **Taste gate** (`check_taste`) — judges the generated artifacts (Pareto
   chart, technical writeup) against `brain/examples/pareto_example.md`.
   Runs *after* artifacts are generated.

Failures are appended to `tasks/lessons.md` and the phase must be re-run.
"""
from __future__ import annotations

import time
from pathlib import Path

REQUIRED_FIELDS = {
    "mode", "kind", "method", "seed", "generated_at", "tokens_per_sec",
}
REQUIRED_FLOAT_FIELDS = {"tokens_per_sec"}

WRITEUP_REQUIRED_SECTIONS = [
    "Key findings",
    "Pareto",
    "Provenance",
]


def check_metrics(metrics: dict) -> list[str]:
    """Return a list of schema/sanity errors (empty == pass)."""
    errors: list[str] = []
    rows = metrics.get("quantization", []) + metrics.get("speculative", [])

    if metrics.get("schema_version") != "1.0":
        errors.append("missing schema_version == '1.0'")
    if not rows:
        errors.append("no metric rows found")

    for i, row in enumerate(rows):
        missing = REQUIRED_FIELDS - set(row)
        if missing:
            errors.append(f"row {i}: missing fields {sorted(missing)}")
            continue
        for f in REQUIRED_FLOAT_FIELDS:
            if not isinstance(row.get(f), (int, float)):
                errors.append(f"row {i}: {f} not numeric")
        if "acceptance_rate" in row and row["acceptance_rate"] is not None:
            if not 0.0 <= row["acceptance_rate"] <= 1.0:
                errors.append(f"row {i}: acceptance_rate out of range")
        if row.get("tokens_per_sec", 0) <= 0:
            errors.append(f"row {i}: tokens_per_sec <= 0")
        if row.get("mem_gb") is not None and row["mem_gb"] <= 0:
            errors.append(f"row {i}: mem_gb <= 0")

    # At least one quantization config per supported method must be present.
    present = {r["method"] for r in metrics.get("quantization", [])}
    for method in ("FP16", "FP8", "AWQ", "GPTQ"):
        if method not in present:
            errors.append(f"quantization matrix missing method {method}")
    return errors


def check_taste(artifact_dir: Path, lessons_path: Path) -> list[str]:
    """Judge artifacts against the reference in brain/examples."""
    pareto_path = artifact_dir / "pareto_frontier.png"
    writeup_path = artifact_dir / "technical_writeup.md"
    issues: list[str] = []

    if not pareto_path.exists() or pareto_path.stat().st_size < 20_000:
        issues.append(f"pareto chart missing or too small: {_rel(pareto_path)}")
    if not writeup_path.exists():
        issues.append(f"writeup missing: {_rel(writeup_path)}")
    else:
        text = writeup_path.read_text(encoding="utf-8")
        words = len(text.split())
        if words < 300:
            issues.append(f"writeup too short ({words} words)")
        for section in WRITEUP_REQUIRED_SECTIONS:
            if section.lower() not in text.lower():
                issues.append(f"writeup missing section: {section}")

    if issues:
        _log(lessons_path, issues)
    return issues


def _rel(p: Path) -> str:
    """Relative path (no absolute local paths in committed logs)."""
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:
        return str(p)


def _log(lessons_path: Path, issues: list[str]) -> None:
    lessons_path.parent.mkdir(parents=True, exist_ok=True)
    with lessons_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## {time.strftime('%Y-%m-%d %H:%M:%S')} — Eval Loop issues\n")
        for issue in issues:
            fh.write(f"- {issue}\n")


def run_eval_loop(metrics: dict, artifact_dir: Path, lessons_path: Path) -> dict:
    """Execute the full eval loop (both stages). Returns a report dict."""
    metric_errors = check_metrics(metrics)
    taste_issues = check_taste(artifact_dir, lessons_path)
    passed = not metric_errors and not taste_issues

    report = {
        "passed": passed,
        "schema_errors": metric_errors,
        "taste_issues": taste_issues,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    print("[eval-loop] " + ("PASS" if passed else "FAIL"))
    if metric_errors:
        print("  schema errors:", metric_errors)
    if taste_issues:
        print("  taste issues:", taste_issues)
    return report


if __name__ == "__main__":
    import json
    import sys

    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts/raw_metrics.json")
    data = json.loads(src.read_text(encoding="utf-8"))
    print(json.dumps(run_eval_loop(data, Path("artifacts"), Path("tasks/lessons.md")), indent=2))
