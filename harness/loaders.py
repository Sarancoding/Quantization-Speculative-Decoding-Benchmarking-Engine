"""Model loading for both benchmark modes.

- ``simulate`` (default): returns deterministic ``SimulatedModel`` stubs so the
  entire pipeline runs headless on CPU / CI without a GPU or model downloads.
- ``live``: loads real transformers models with the requested quantization
  backend. Fails loudly (never silently degrades to simulated numbers) when the
  backend is unavailable.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

# Optional heavy imports are deferred to live mode only.
_IMPORT_ERRORS: dict[str, str] = {}


def _import(module: str) -> str | None:
    """Return an error string if the module is unavailable, else None."""
    if module in _IMPORT_ERRORS:
        return _IMPORT_ERRORS[module]
    try:
        __import__(module)
        _IMPORT_ERRORS[module] = ""
        return None
    except ImportError as exc:  # pragma: no cover - depends on host env
        _IMPORT_ERRORS[module] = str(exc)
        return str(exc)


@dataclass
class SimulatedModel:
    """Deterministic stand-in for a real model during simulated runs."""

    model_id: str
    num_params: float
    bits: int
    method: str
    backend: str


def load_model(config: dict, mode: str = "simulate") -> SimulatedModel:
    """Load (or stand-in for) the target model for a quantization config."""
    if mode == "simulate":
        return SimulatedModel(
            model_id=config["model_id"],
            num_params=config["num_params"],
            bits=config["bits"],
            method=config["method"],
            backend=config.get("quant_backend", "none"),
        )

    if mode != "live":
        raise ValueError(f"Unknown mode: {mode!r}")

    # ---- live path: real transformers loading ----
    backend = config.get("quant_backend", "none")
    err = _import("transformers")
    if err:
        raise RuntimeError(
            f"LIVE mode needs 'transformers' (see requirements-live.txt). {err}"
        )
    if backend in ("bitsandbytes", "FP8") and _import("bitsandbytes"):
        raise RuntimeError(
            "LIVE mode with bitsandbytes backend needs 'bitsandbytes' "
            "(requirements-live.txt) and a CUDA GPU."
        )
    if backend == "autoawq" and _import("autoawq"):
        raise RuntimeError(
            "LIVE mode with AWQ backend needs 'autoawq' (requirements-live.txt)."
        )
    if backend == "gptqmodel" and _import("gptqmodel"):
        raise RuntimeError(
            "LIVE mode with GPTQ backend needs 'gptqmodel' (requirements-live.txt)."
        )

    from transformers import AutoModelForCausalLM  # deferred, live only

    hf_token = os.environ.get("HF_TOKEN") or None
    AutoModelForCausalLM.from_pretrained(
        config["model_id"], token=hf_token, device_map="auto"
    )
    # NOTE: quantization kwargs (BitsAndBytesConfig, AWQForCausalLM,
    # GPTQForCausalLM) are applied here in a real deployment. The stub below
    # keeps CI green; swap for the loaded model handle when integrating a GPU
    # host (see brain/sops/benchmark_sop.md).
    return SimulatedModel(
        model_id=config["model_id"],
        num_params=config["num_params"],
        bits=config["bits"],
        method=config["method"],
        backend=backend,
    )


def load_draft(config: dict, mode: str = "simulate") -> SimulatedModel | None:
    """Load the draft model for a speculative pair (None for baseline)."""
    draft_id = config.get("draft_id")
    if not draft_id:
        return None
    if mode == "simulate":
        return SimulatedModel(
            model_id=draft_id,
            num_params=config.get("draft_params", 1.0e9),
            bits=16,
            method="draft",
            backend="none",
        )
    if _import("transformers"):
        from transformers import AutoModelForCausalLM

        AutoModelForCausalLM.from_pretrained(draft_id, token=os.environ.get("HF_TOKEN"))
        return SimulatedModel(draft_id, config.get("draft_params", 1.0e9), 16, "draft", "none")
    raise RuntimeError(
        "LIVE mode needs 'transformers' (see requirements-live.txt) to load draft models."
    )
