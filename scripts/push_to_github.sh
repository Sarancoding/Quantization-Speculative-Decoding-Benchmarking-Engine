#!/bin/sh
# =============================================================================
# DevOps / Git push protocol (Subagent E) - a gated task in the orchestrator.
# POSIX sh compatible so it can be invoked as `sh scripts/push_to_github.sh`.
#
# Runs the pre-push verification checklist, commits staged work, and pushes to
# the EXISTING origin remote (Freebuff injects the short-lived credential for
# git commands automatically). Fast-forward by default; --force enables
# --force-with-lease explicitly.
#
# Usage:
#   sh scripts/push_to_github.sh            # checklist + commit + push
#   sh scripts/push_to_github.sh --check    # checklist only, no git ops
# =============================================================================
set -eu
cd "$(dirname "$0")/.."

CHECK_ONLY="${1:-}"

# --- Pre-push verification checklist ---------------------------------------
echo "== pre-push checklist =="
FAILED=0
fail() { echo "  [FAIL] $1"; FAILED=1; }
pass() { echo "  [ok]   $1"; }

[ -f README.md ] && pass "README.md present" || fail "README.md missing"
[ -f GITMORE.md ] && pass "GITMORE.md present" || fail "GITMORE.md missing"
[ -f Quant_Benchmarking_Readme.pdf ] && pass "README PDF present" || fail "README PDF missing"
[ -f Quant_Benchmarking_Setup_Guide.pdf ] && pass "Setup Guide PDF present" || fail "Setup Guide PDF missing"
[ -f artifacts/pareto_frontier.png ] && pass "pareto_frontier.png present" || fail "pareto_frontier.png missing"
[ -f artifacts/technical_writeup.md ] && pass "technical_writeup.md present" || fail "technical_writeup.md missing"
[ -f requirements.txt ] && pass "requirements.txt present" || fail "requirements.txt missing"

# No hardcoded secrets / absolute local paths. (This script defines the
# regex, so it is excluded from its own scan; vendor dirs are skipped too.)
SECRET_SCAN="$(grep -rnE "(api[_-]?key|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|/home/)" \
  --include="*.py" --include="*.sh" --include="*.md" --include="*.json" . \
  | grep -vE "^\./(\.git|\.venv|node_modules)/" \
  | grep -v "^./scripts/push_to_github.sh:" || true)"
if [ -n "$SECRET_SCAN" ]; then
  echo "$SECRET_SCAN"
  fail "possible hardcoded secret or absolute path (see matches above)"
else
  pass "no hardcoded secrets / absolute local paths"
fi

# .gitignore excludes the sensitive outputs.
for pat in "results/" "__pycache__/" "*.pt" "*.bin" ".env"; do
  grep -qE "^${pat}" .gitignore && pass ".gitignore excludes ${pat}" || fail ".gitignore does not exclude ${pat}"
done

if [ "$FAILED" = "1" ]; then
  echo "== PRE-PUSH CHECKLIST FAILED — fix issues, log to tasks/lessons.md, retry =="
  exit 1
fi
echo "== pre-push checklist PASSED =="

if [ "$CHECK_ONLY" = "--check" ]; then
  exit 0
fi

# --- Git operations ---------------------------------------------------------
origin="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$origin" ]; then
  echo "ERROR: no origin remote configured. Add one first (Freebuff injects the credential)." >&2
  exit 1
fi
echo "== origin: $origin =="

git add .
if git diff --cached --quiet; then
  echo "nothing to commit — working tree already in sync"
else
  git commit -m "feat: quantization & speculative decoding benchmarking engine

- Implements FP16, FP8, AWQ, GPTQ benchmarking pipeline
- Adds speculative decoding runner with domain-specific acceptance rates
- Generates Pareto Efficiency Frontier chart and technical writeup
- Includes Company Brain, Agent Profiles, and Orchestrator harness
- Adds Setup Guide and README PDFs for GitHub landing page"
fi

if [ "${1:-}" = "--force" ]; then
  PUSH_ARGS="--force-with-lease"
else
  PUSH_ARGS=""
fi

# Freebuff injects a short-lived GitHub App token for gh; wire it into git
# as the credential helper so pushes authenticate without any persisted
# secret or remote rewrite.
if ! git push -u origin main $PUSH_ARGS; then
  echo "plain push failed; retrying via the injected gh credential helper"
  git -c credential.helper='!gh auth git-credential' push -u origin main $PUSH_ARGS
fi

echo "== post-push verification =="
git ls-remote origin HEAD | head -1
echo "== pushed successfully =="
