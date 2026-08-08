# Benchmarking Strategy

## Objective

Produce the **Pareto Efficiency Frontier** over the design space
`{quantization method} x {speculative decoding strategy}` for a target model,
so engineering can pick configurations that are not dominated on any axis
(latency, throughput, memory, quality).

## What we measure

| Metric | Unit | Direction |
| --- | --- | --- |
| Decode latency (mean / median / p90) | ms/token | minimize |
| Throughput | tokens/s | maximize |
| Memory footprint | GB | minimize |
| Quality proxy (perplexity on held-out set) | PPL | minimize |
| Speculative acceptance rate (per domain) | 0..1 | maximize |
| Speculative speedup vs baseline | ratio | maximize |

## Design principles

1. **Provenance or GTFO.** Every metric row carries model id, backend, bits,
   seed, mode, and timestamp. A number without provenance is not a number.
2. **Simulate first, live second.** `--mode simulate` (seeded, deterministic,
   CPU-only) validates the entire pipeline; `--mode live` measures real
   hardware. Never gate CI on GPUs.
3. **Fair comparison.** Same prompts, same token counts, same domains across
   configurations. Latency is measured per token, not per generation.
4. **Pareto, not leaderboard.** A configuration "wins" only if it is not
   dominated. Frontier axes: maximize throughput, minimize memory, latency,
   and quality cost (PPL) — a fast-but-low-quality config does not dominate a
   slower, higher-quality one. Speedups are reported with acceptance rates so
   they are auditable, not hand-waved.
5. **Domain matters.** Speculative decoding acceptance rates differ by domain
   (code > math > reasoning > summarization > chat for most draft pairs);
   report per domain, never only an aggregate.

## Decision flow

```
benchmark matrix -> metrics with provenance -> eval loop (schema + sanity)
-> Pareto frontier -> technical writeup -> taste gate -> publish artifacts
```
