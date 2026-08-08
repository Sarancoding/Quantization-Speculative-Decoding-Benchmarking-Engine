"""Benchmark configuration registry.

Central place for the quantization matrix (FP16/FP8/AWQ/GPTQ) and the
speculative-decoding draft/target pairs, plus the domains benchmarked.
"""
from __future__ import annotations

# --- Quantization matrix (Subagent B) -------------------------------------
QUANTIZATION_CONFIGS: list[dict] = [
    {
        "method": "FP16",
        "bits": 16,
        "quant_backend": "none",
        "model": "Llama-2-7B",
        "model_id": "meta-llama/Llama-2-7b-hf",
        "num_params": 6.74e9,
    },
    {
        "method": "FP8",
        "bits": 8,
        "quant_backend": "bitsandbytes",
        "model": "Llama-2-7B",
        "model_id": "meta-llama/Llama-2-7b-hf",
        "num_params": 6.74e9,
    },
    {
        "method": "AWQ",
        "bits": 4,
        "quant_backend": "autoawq",
        "model": "Llama-2-7B",
        "model_id": "TheBloke/Llama-2-7B-AWQ",
        "num_params": 6.74e9,
    },
    {
        "method": "GPTQ",
        "bits": 4,
        "quant_backend": "gptqmodel",
        "model": "Llama-2-7B",
        "model_id": "TheBloke/Llama-2-7B-GPTQ",
        "num_params": 6.74e9,
    },
]

# --- Speculative decoding pairs (Subagent C) -------------------------------
SPECULATIVE_CONFIGS: list[dict] = [
    {
        "method": "baseline",
        "draft": None,
        "target": "Llama-2-7B",
        "target_id": "meta-llama/Llama-2-7b-hf",
        "target_params": 6.74e9,
        "gamma": 1,
    },
    {
        "method": "speculative",
        "draft": "Llama-2-1B",
        "target": "Llama-2-7B",
        "draft_id": "meta-llama/Llama-2-1b-hf",
        "target_id": "meta-llama/Llama-2-7b-hf",
        "draft_params": 1.0e9,
        "target_params": 6.74e9,
        "gamma": 4,
    },
    {
        "method": "speculative",
        "draft": "Llama-2-3B",
        "target": "Llama-2-7B",
        "draft_id": "meta-llama/Llama-2-3b-hf",
        "target_id": "meta-llama/Llama-2-7b-hf",
        "draft_params": 3.2e9,
        "target_params": 6.74e9,
        "gamma": 4,
    },
    {
        "method": "medusa",
        "draft": "Medusa-1B",
        "target": "Llama-2-7B",
        "draft_id": "FasterDecoding/medusa-llama2-7b",
        "target_id": "meta-llama/Llama-2-7b-hf",
        "draft_params": 1.0e9,
        "target_params": 6.74e9,
        "gamma": 5,
    },
    {
        "method": "eagle",
        "draft": "EAGLE-3B",
        "target": "Llama-2-7B",
        "draft_id": "SafeAILab/EAGLE-llama2-7b",
        "target_id": "meta-llama/Llama-2-7b-hf",
        "draft_params": 3.2e9,
        "target_params": 6.74e9,
        "gamma": 6,
    },
]

# --- Domains ---------------------------------------------------------------
DOMAINS: list[str] = ["code", "math", "reasoning", "chat", "summarization"]
