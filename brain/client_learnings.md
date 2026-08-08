# Client Learnings

> Client-facing friction log. Add entries whenever deployment or integration
> friction is encountered. Keep entries short and actionable.

## 2026-08-08 — Repo bootstrap
- The connected repository was empty (single commit, LICENSE only); the
  engine was built from scratch per client direction ("start fresh").
- Freebuff sandbox has no `freebuff-preview` CLI; preview commands are
  persisted in `package.json` scripts (`dev` / `build` / `start`) instead,
  which the platform preview controls read.
- Analysis stack (numpy/matplotlib/fpdf2) installed into `.venv` via uv;
  live GPU dependencies remain optional (`requirements-live.txt`).

## 2026-08-08 — Push friction (pre-push checklist caught all of it)
- Committed provenance must never carry absolute local paths (stored as
  `"<repo_root>"` now); lessons logs must use relative paths.
- Secret scans must exclude vendor dirs (`.venv/`, `node_modules/`) and the
  scanning script itself.
- Scripts invoked as `sh ...` must be POSIX-compatible (no `pipefail`).
- **Lesson:** the gated checklist worked — every issue was caught before the
  push, not after.
- Push auth: `git push` needs a credential helper; on Freebuff workspaces use
  `gh auth git-credential` (the injected repo-scoped token authenticates).
