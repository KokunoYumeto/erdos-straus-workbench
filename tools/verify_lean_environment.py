#!/usr/bin/env python3
"""Run Lean's independent environment checker on each bounded proof module."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "formal" / "lean"
MODULES = (
    "R107DeficitProgression.Definitions",
    "R107DeficitProgression.Reduced",
    "R107DeficitProgression.Difference",
    "R107DeficitProgression.FullSupport",
)


def check_module(module: str) -> None:
    started = time.monotonic()
    process = subprocess.Popen(
        ["lake", "env", "leanchecker", module],
        cwd=LEAN_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if process.stdout is None:
        raise RuntimeError(f"leanchecker pipe was not created for {module}")
    while process.poll() is None:
        elapsed = int(time.monotonic() - started)
        print(f"leanchecker module={module} status=running elapsed_seconds={elapsed}", flush=True)
        time.sleep(15)
    output = process.stdout.read()
    try:
        decoded = output.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"non-UTF-8 leanchecker output for {module}: {exc}") from exc
    if decoded:
        print(decoded, end="" if decoded.endswith("\n") else "\n")
    if process.returncode != 0:
        raise RuntimeError(f"leanchecker failed for {module} with exit {process.returncode}")
    elapsed = int(time.monotonic() - started)
    print(f"leanchecker module={module} status=PASS elapsed_seconds={elapsed}", flush=True)


def main() -> None:
    for module in MODULES:
        check_module(module)
    print("verification=lean-independent-environment")
    print("status=PASS")
    print(f"modules={len(MODULES)}")


if __name__ == "__main__":
    main()
