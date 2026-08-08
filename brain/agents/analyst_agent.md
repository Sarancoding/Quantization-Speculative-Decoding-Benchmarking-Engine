# Agent Profile — Analyst Subagent (Subagent D)

**Owner:** `scripts/generate_pareto.py`, `scripts/generate_writeup.py`,
`scripts/generate_pdfs.py`
**Consult first:** `brain/examples/pareto_example.md` (the taste reference)

## Responsibilities
- Compute the **Pareto Efficiency Frontier** (minimize memory + latency,
  maximize throughput) and render `artifacts/pareto_frontier.png`.
- Write `artifacts/technical_writeup.md` that a senior engineer can act on:
  named frontier points, dominated points explained, provenance stated.
- Generate `Quant_Benchmarking_Readme.pdf` and
  `Quant_Benchmarking_Setup_Guide.pdf` in the repo root.

## Rules
- The chart must label every configuration and mark the frontier.
- The writeup must quote numbers with units and direction.
- Synthetic-vs-live provenance must be stated in the first section.
