# SOP — Orchestration Loop

Applies to `orchestrator/pipeline.py` and every gated hand-off.

## Phases

```
Phase 1  Brain        : brain/ present and indexed -> GATE
Phase 2  Design       : orchestrator/, harness/ coherent -> GATE
Phase 3  Build        : fan out runners -> merge metrics -> GATE
Phase 4  Eval Loop    : schema + sanity + taste gate -> GATE
Phase 5  Artifacts    : pareto.png, writeup.md, PDFs -> GATE
Phase 6  Deploy       : pre-push checklist -> push -> post-push verify -> DONE
```

## Gate rules
- A phase is DONE only when its outputs pass the **Eval Loop**.
- Any failure: **STOP, log to `tasks/lessons.md`, fix, retry.** No hand-holding,
  no silent skip.
- The orchestrator tracks its own token spend via `orchestrator/token_budget.py`
  and warns when a phase approaches its budget.
- Judgment is explicit: artifacts are compared against
  `brain/examples/pareto_example.md` (the taste reference).

## Subagent strategy (Hermes)
1. **Fan out** — one subagent per workstream (Infra, Quant, Spec, Analyst, DevOps).
2. **Cross-verify** — Eval Loop checks every deliverable independently.
3. **Merge** — only verified work lands in `results/` / `artifacts/`.
