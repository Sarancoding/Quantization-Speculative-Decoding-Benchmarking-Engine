# Orchestrator Task Board

> Every phase is gated: a phase is DONE only after its outputs pass the Eval Loop.

## Phase 1 — Company Brain (Knowledge Layer)
- [x] `brain/` initialized with strategy, SOPs, examples, agent profiles
- [x] `AGENTS.md` authored with constraints (repo had none to copy)
- [x] `tasks/` tracking created

## Phase 2 — Harness & Orchestrator (System Design)
- [x] `orchestrator/` (pipeline, token budget, eval loop)
- [x] `harness/` (loaders, metrics, data)
- [x] `benchmarks/` configs (FP16 / FP8 / AWQ / GPTQ + draft/target pairs)

## Phase 3 — Execution & Skills (The Build)
- [x] Subagent A (Infra): `infra/setup.py`, `requirements.txt`, `.gitignore`
- [x] Subagent B (Quant): `benchmarks/quantization_runner.py`
- [x] Subagent C (Spec): `benchmarks/speculative_runner.py`
- [x] Subagent D (Analyst): `scripts/generate_pareto.py`, `scripts/generate_writeup.py`
- [x] Subagent E (DevOps): `scripts/push_to_github.sh` + repo readiness
- [x] Merge → `results/raw_metrics.json` + `artifacts/raw_metrics.json`

## Phase 4 — Eval Loop (Verification)
- [x] Schema validation of merged metrics
- [x] Taste gate: Pareto chart + writeup judged vs `brain/examples/`

## Phase 5 — Artifacts & Landing Page
- [x] `artifacts/pareto_frontier.png`
- [x] `artifacts/technical_writeup.md`
- [x] `Quant_Benchmarking_Readme.pdf`, `Quant_Benchmarking_Setup_Guide.pdf`
- [x] `README.md`, `GITMORE.md`, `web/` landing page

## Phase 6 — GitHub Deployment (Gated)
- [x] Pre-push verification checklist passed
- [x] Code pushed to `origin/main`
- [x] Post-push verification (repo URL accessible, landing files present)
- [x] Updates logged in `tasks/lessons.md` + `brain/client_learnings.md`

> ✅ **Push to GitHub: DONE** — see `GITMORE.md` Phase 6 entry.
