# GITMORE — Dev Log & Lessons Learned

> The project's engineering diary. Every significant decision and friction
> point is logged here (short-form) and mirrored in `tasks/lessons.md`.

## 2026-08-08 — Initial build (Phase 1–5)

### Done
- **Company Brain** populated (`brain/`): strategy, SOPs, agent profiles,
  taste reference, client learnings.
- **Harness & orchestrator**: `orchestrator/pipeline.py` runs the gated loop
  (brain gate → fan-out runners → merge → eval loop → artifacts → PDFs) with a
  token budget tracker.
- **Quant runner** (`benchmarks/quantization_runner.py`): FP16/FP8/AWQ/GPTQ
  matrix with provenance, latency stats (mean/median/p90), memory, quality.
- **Spec runner** (`benchmarks/speculative_runner.py`): draft/target pairings
  (1B, 3B, Medusa, EAGLE) with per-domain acceptance rates and the standard
  expected-tokens formula.
- **Analyst scripts**: Pareto chart (matplotlib, headless Agg), technical
  writeup (markdown), PDFs (fpdf2 — no pandoc/wkhtmltopdf needed).
- **Eval Loop** (`orchestrator/eval_loop.py`): schema + sanity checks + taste
  gate vs `brain/examples/pareto_example.md`; failures logged to
  `tasks/lessons.md`.

### Decisions
- **Simulate-first architecture.** The pipeline must be verifiable on CPU/CI,
  so `--mode simulate` uses seeded, deterministic priors with real formulas;
  `--mode live` is the first-class GPU path. Rationale: don't gate CI on GPUs,
  but never let synthetic numbers masquerade as measurements (provenance is
  stamped on every row and stated in the writeup).
- **Repo was empty** (LICENSE only) — per client direction we started fresh and
  authored `AGENTS.md` from the spec's constraint section.
- **Pinned analysis stack** in `requirements.txt` (numpy/matplotlib/fpdf2);
  GPU deps stay optional in `requirements-live.txt` because the right build
  depends on the CUDA/Python toolchain.

### Lessons
- fpdf2 (pure-Python) is the right tool here: no pandoc/libreoffice on the
  build host. Core Helvetica fonts are Latin-1 only — non-ASCII gets
  transliterated.
- The Freebuff sandbox has no `freebuff-preview` CLI, so the durable preview
  config lives in `package.json` scripts (`dev` / `build` / `start`) read by
  the platform's preview controls.

## 2026-08-08 — Phase 6: GitHub deployment

### Done
- **Pre-push checklist passed** (via `sh scripts/push_to_github.sh --check`):
  docs, PDFs, artifacts, requirements present; no hardcoded secrets or
  absolute local paths; `.gitignore` excludes `results/`, `__pycache__/`,
  `*.pt`, `*.bin`, `.env`.
- **Pushed to `origin/main`** (existing remote, fast-forward; Freebuff
  injected the credential).
- **Post-push verified** — landing files present on the default branch.

### Friction & fixes (logged in `tasks/lessons.md`)
- Push auth: git had no credential helper, so the first push prompted for a
  username. Fixed by retrying with `gh auth git-credential` as a one-shot
  helper (uses the injected Freebuff token; nothing persisted).
- Committed provenance recorded absolute `cwd` → now stored as `"<repo_root>"`.
- Lessons log contained absolute paths → eval loop now logs relative paths.
- Pre-push secret scan tripped on `.venv/` deps and on the script's own
  regex → vendor dirs and the script itself are excluded from the scan.
- `push_to_github.sh` was bash-only (`pipefail`) → made POSIX-sh compatible so
  it can be invoked as `sh scripts/push_to_github.sh`.

## Next
- Live-mode integration on a GPU host: wire the loaded model handle into the
  timing loops and a real perplexity eval set.
