# Good Example — Pareto Frontier Writeup (Taste Reference)

> This is the reference the Eval Loop judges artifacts against. A good writeup:
> tells a story, reports provenance, and makes a decision actionable.

## Annotated example

### Key findings (3 bullets max)
- **Throughput winner:** AWQ (4-bit) sustains ~1.24× the FP16 decode
  throughput at ~25% of the memory footprint — the clear frontier point for
  latency-critical serving. _(Claims carry numbers and direction.)_
- **Memory winner:** GPTQ (4-bit) and AWQ (4-bit) both land on the frontier;
  AWQ wins on quality (ΔPPL +0.21 vs +0.25). _(Ties are broken by a second axis.)_
- **Speculative decoding:** draft/target pairing lifts tokens/s by 1.9–2.4× on
  code and math; gains shrink to ~1.3× on chat. _(Domain variance is stated,
  never hidden in an aggregate.)_

### Pareto table (frontier set only)

| Config | tokens/s | mem (GB) | ΔPPL | On frontier? |
| --- | --- | --- | --- | --- |
| FP16 baseline | 55.1 | 13.5 | — | yes |
| AWQ 4-bit | 68.4 | 3.4 | +0.21 | yes |
| GPTQ 4-bit | 65.8 | 3.4 | +0.25 | no (dominated) |

### Provenance
All rows in this report are `mode=simulate, seed=42` (see
`artifacts/raw_metrics.json`). Live runs on real GPUs are required before
production decisions.

## What the taste gate checks
1. Numbers have units and direction.
2. Every claim is traceable to a row in the raw metrics.
3. The frontier set is small and named; dominated points are explained.
4. Synthetic vs live provenance is stated up front.
