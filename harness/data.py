"""Prompt sets per domain + token budget helpers.

Prompt sets are intentionally small and fixed so simulated and live runs are
comparable. In live mode these are the seeds of the evaluation prompts; in
simulate mode they only inform the number of tokens generated.
"""
from __future__ import annotations

PROMPTS_BY_DOMAIN: dict[str, list[str]] = {
    "code": [
        "Write a Python function that validates balanced parentheses.",
        "Implement a binary search in Rust with generics.",
        "Explain how to optimize a SQL query with a self-join.",
        "Write a debounce utility in TypeScript.",
        "Describe a lock-free queue design in Go.",
    ],
    "math": [
        "Solve the quadratic equation x^2 - 5x + 6 = 0.",
        "Prove that sqrt(2) is irrational.",
        "What is the derivative of sin(x) * ln(x)?",
        "Compute the 12th Fibonacci number and justify the recurrence.",
        "Explain Bayes' theorem with a concrete example.",
    ],
    "reasoning": [
        "If all A are B, and some B are C, what follows about A and C?",
        "Three boxes are labeled incorrectly. How do you fix them in one draw?",
        "A clock shows 3:15; what is the angle between the hands?",
        "Two trains leave stations 100 km apart at 60 km/h toward each other; when do they meet?",
        "Which statement is logically consistent: all cats are animals; some animals are pets.",
    ],
    "chat": [
        "How do you ask for a refund politely in an email?",
        "Give me three conversation starters for a networking event.",
        "Rewrite this sentence in a friendlier tone.",
        "Summarize the plot of a heist movie in three sentences.",
        "What should I say when declining a meeting invite?",
    ],
    "summarization": [
        "Summarize the key differences between HTTP/2 and HTTP/3.",
        "Give a two-sentence summary of how transformers work.",
        "Summarize the benefits of vector databases.",
        "Condense this release note into one paragraph.",
        "Summarize what speculative decoding does in one sentence.",
    ],
}

DOMAINS: list[str] = list(PROMPTS_BY_DOMAIN.keys())

# Typical generated-token counts per prompt for a 256-token budget.
AVG_TOKENS_BY_DOMAIN: dict[str, int] = {
    "code": 64,
    "math": 48,
    "reasoning": 72,
    "chat": 40,
    "summarization": 52,
}


def get_prompts(domain: str, count: int | None = None) -> list[str]:
    prompts = PROMPTS_BY_DOMAIN.get(domain, PROMPTS_BY_DOMAIN["chat"])
    return prompts if count is None else prompts[:count]


def tokens_for(domain: str, per_prompt: int | None = None) -> int:
    if per_prompt is not None:
        return per_prompt
    return AVG_TOKENS_BY_DOMAIN.get(domain, 64)
