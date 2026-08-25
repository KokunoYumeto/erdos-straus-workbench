#!/usr/bin/env python3
"""Replay the root Lean module and fail on any unapproved axiom report."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "formal" / "lean"
MODULE = "R107DeficitProgression.lean"
EXPECTED = {
    "reducedSupport_card": {"propext", "Classical.choice", "Quot.sound"},
    "deficit_eq_progression": {"propext", "Classical.choice", "Quot.sound"},
    "deficit_card": {"propext", "Classical.choice", "Quot.sound"},
    "differenceSet_card": {"propext", "Classical.choice", "Quot.sound"},
    "six_not_mem_differenceSet": {"propext", "Classical.choice", "Quot.sound"},
    "translatedDeficits_disjoint": {"propext", "Classical.choice", "Quot.sound"},
    "oddSheet_saturated": {"propext", "Classical.choice", "Quot.sound"},
    "factorLogarithms": {"propext", "Quot.sound"},
    "fullSupport_card": {"propext", "Classical.choice", "Quot.sound"},
    "middleTarget_mem": {"propext", "Classical.choice", "Quot.sound"},
    "exteriorTarget_not_mem": {"propext", "Classical.choice", "Quot.sound"},
}
REPORT = re.compile(
    r"^(?:info: R107DeficitProgression\.lean:\d+:\d+: )?"
    r"'R107DeficitProgression\.([A-Za-z0-9_]+)' depends on axioms: \[(.*)\]$"
)
PLACEHOLDER = re.compile(r"(?m)^\s*(?:sorry|admit|native_decide)\b")


def main() -> None:
    project_sources = [LEAN_ROOT / MODULE]
    project_sources.extend(sorted((LEAN_ROOT / "R107DeficitProgression").glob("*.lean")))
    for source in project_sources:
        text = source.read_text(encoding="utf-8")
        if PLACEHOLDER.search(text):
            raise RuntimeError(f"placeholder or native_decide token in {source.relative_to(ROOT)}")

    replay = subprocess.run(
        ["lake", "env", "lean", MODULE], cwd=LEAN_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    output = replay.stdout.decode("utf-8", errors="strict").replace("\r\n", "\n")
    if replay.returncode != 0:
        raise RuntimeError(f"Lean replay failed with exit {replay.returncode}\n{output}")

    observed: dict[str, set[str]] = {}
    for line in output.splitlines():
        match = REPORT.fullmatch(line)
        if not match:
            continue
        theorem, raw_axioms = match.groups()
        axioms = {item.strip() for item in raw_axioms.split(",") if item.strip()}
        if theorem in observed:
            raise RuntimeError(f"duplicate axiom report for {theorem}")
        observed[theorem] = axioms

    if observed != EXPECTED:
        missing = sorted(EXPECTED.keys() - observed.keys())
        extra = sorted(observed.keys() - EXPECTED.keys())
        changed = {
            name: {"expected": sorted(EXPECTED[name]), "observed": sorted(observed[name])}
            for name in EXPECTED.keys() & observed.keys()
            if EXPECTED[name] != observed[name]
        }
        raise RuntimeError(
            f"Lean axiom audit mismatch: missing={missing}, extra={extra}, changed={changed}\n{output}"
        )

    print("verification=lean-root-axiom-audit")
    print("status=PASS")
    print(f"theorems={len(observed)}")
    print("allowed_axioms=Classical.choice,Quot.sound,propext")
    print("sorry_or_native_decide=false")


if __name__ == "__main__":
    main()
