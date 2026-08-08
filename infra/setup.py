#!/usr/bin/env python3
"""One-command environment bootstrap.

Creates ``.venv`` and installs the pinned requirements so the pipeline can
run headless on CPU (metrics + Pareto chart + PDFs). No GPU needed.

Usage:
    python3 infra/setup.py
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def venv_python(venv: str) -> str:
    if os.name == "nt":
        return os.path.join(venv, "Scripts", "python.exe")
    return os.path.join(venv, "bin", "python")


def main() -> None:
    venv = os.path.join(ROOT, ".venv")
    py = venv_python(venv)

    if not os.path.exists(py):
        print(f"[setup] Creating virtualenv at {venv}")
        run([sys.executable, "-m", "venv", venv])

    print("[setup] Upgrading pip")
    run([py, "-m", "pip", "install", "--quiet", "--upgrade", "pip"])

    print("[setup] Installing pinned requirements.txt")
    run([py, "-m", "pip", "install", "--quiet", "-r", os.path.join(ROOT, "requirements.txt")])

    print("[setup] Done. Next:")
    print("  source .venv/bin/activate")
    print('  python -m orchestrator.pipeline --mode simulate   # full run')


if __name__ == "__main__":
    main()
