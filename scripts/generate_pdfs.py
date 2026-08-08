"""Analyst (Subagent D): PDF generation for the GitHub landing page.

Produces `Quant_Benchmarking_Readme.pdf` and `Quant_Benchmarking_Setup_Guide.pdf`
in the repo root using fpdf2 (pure-Python, headless-friendly). Markdown is
rendered as clean wrapped text (core fonts are Latin-1 only; non-ASCII is
transliterated).

Usage:
    python scripts/generate_pdfs.py [--root .]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from fpdf import FPDF

SETUP_GUIDE = """\
Quantization & Speculative Decoding Benchmarking Engine
Setup Guide

1. Prerequisites
   - Python 3.10+ and pip (or uv).
   - For LIVE benchmark runs: a CUDA GPU and the optional
     requirements-live.txt stack (torch, transformers, bitsandbytes,
     autoawq, gptqmodel). Simulated runs need no GPU.

2. One-command setup
   python3 infra/setup.py
   Creates .venv and installs the pinned requirements.txt.

3. Run the full pipeline (simulated, deterministic)
   python -m orchestrator.pipeline --mode simulate --seed 42
   Outputs:
     - artifacts/raw_metrics.json     merged metrics with provenance
     - artifacts/pareto_frontier.png  Pareto efficiency frontier chart
     - artifacts/technical_writeup.md technical writeup
     - results/run_status.json        pipeline status report

4. Run individual modules
   python -m benchmarks.quantization_runner --mode simulate --seed 42
   python -m benchmarks.speculative_runner --mode simulate --seed 42
   python scripts/generate_pareto.py
   python scripts/generate_writeup.py

5. Run on real hardware (LIVE mode)
   pip install -r requirements-live.txt   # GPU host only
   python -m orchestrator.pipeline --mode live

6. View the docs / landing page locally
   bun server.js          (or: npm run dev)
   Serves ./web and ./artifacts at http://0.0.0.0:4173

7. Push to GitHub (gated DevOps task)
   sh scripts/push_to_github.sh
   Runs the pre-push checklist, commits, and fast-forward pushes to origin.
"""


def _safe(text: str) -> str:
    return "".join(ch if ord(ch) < 256 else "?" for ch in text)


def md_to_lines(md: str, max_len: int = 92) -> list[str]:
    lines: list[str] = []
    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        if re.match(r"^\s*\|?[\s\-:|]+\|?\s*$", line) and "|" in line and "---" in line:
            continue  # drop table separators
        line = re.sub(r"^#{1,6}\s*", "", line)          # headings
        line = re.sub(r"[`*_>]", "", line)               # inline md tokens
        line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)  # links -> text
        line = line.replace("|", " | ").strip(" |")
        while len(line) > max_len:
            cut = line.rfind(" ", 0, max_len)
            if cut < 1:
                cut = max_len
            lines.append(_safe(line[:cut].rstrip()))
            line = line[cut:].lstrip()
        lines.append(_safe(line))
    return lines


def render_pdf(title: str, lines: list[str], out_path: Path) -> None:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(usable, 8, _safe(title))
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    for line in lines:
        if line == "":
            pdf.ln(3)
            continue
        pdf.set_x(pdf.l_margin)  # fpdf2 leaves x at end-of-text; reset per cell
        pdf.multi_cell(usable, 5, line)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    print(f"[pdfs] saved: {out_path} ({out_path.stat().st_size} bytes)")


def generate_pdfs(root: Path) -> dict:
    readme_path = root / "README.md"
    if readme_path.exists():
        render_pdf(
            "Quantization & Speculative Decoding Benchmarking Engine — README",
            md_to_lines(readme_path.read_text(encoding="utf-8")),
            root / "Quant_Benchmarking_Readme.pdf",
        )
    render_pdf(
        "Setup Guide",
        md_to_lines(SETUP_GUIDE),
        root / "Quant_Benchmarking_Setup_Guide.pdf",
    )
    return {
        "readme_pdf": str(root / "Quant_Benchmarking_Readme.pdf"),
        "setup_pdf": str(root / "Quant_Benchmarking_Setup_Guide.pdf"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate landing-page PDFs")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    generate_pdfs(Path(args.root))
