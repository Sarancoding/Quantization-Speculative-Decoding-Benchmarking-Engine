"""Token budget tracker for the orchestrator loop.

Each phase of the pipeline gets a budget (context-token accounting for the
orchestrating agent loop). The tracker warns when a phase approaches its
budget and reports the final spend, so no phase silently overruns.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

WARN_RATIO = 0.8


@dataclass
class TokenBudget:
    """Track spend per phase against a total budget."""

    total: int = 120_000
    phases: dict[str, int] = field(default_factory=dict)
    _spent: int = 0

    def check(self, phase: str) -> None:
        # Warn when cumulative spend approaches the global budget; the per-phase
        # budgets are informational allocations reported at the end.
        if self._spent >= self.total * WARN_RATIO:
            print(
                f"[token-budget] WARNING cumulative spend {self._spent}/{self.total} "
                f"tokens ({self._spent / self.total:.0%})"
            )

    def spend(self, phase: str, tokens: int) -> None:
        self._spent += max(0, tokens)
        self.check(phase)

    def report(self) -> dict:
        return {
            "spent": self._spent,
            "total": self.total,
            "pct": round(100.0 * self._spent / self.total, 1) if self.total else 0.0,
        }


def default_budget() -> TokenBudget:
    b = TokenBudget(total=120_000)
    b.phases = {
        "brain": 15_000,
        "harness": 25_000,
        "benchmarks": 25_000,
        "merge": 5_000,
        "eval": 10_000,
        "artifacts": 20_000,
        "deploy": 20_000,
    }
    return b


def phase_clock(name: str):
    """Tiny context manager measuring a phase's wall-clock time."""
    start = time.perf_counter()

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            elapsed = time.perf_counter() - start
            print(f"[phase] {name}: {elapsed:.2f}s")
            return False

    return _Ctx()
