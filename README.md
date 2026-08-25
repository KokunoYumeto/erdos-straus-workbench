# Erdős–Straus Workbench

This is a focused, public [Mathematics Commons](https://github.com/KokunoYumeto/mathematics-commons-pilot) workbench for literature-first, reproducible work on the Erdős–Straus conjecture

\[
\frac{4}{n}=\frac1x+\frac1y+\frac1z,
\qquad n\ge 2,
\qquad x,y,z\in\mathbb Z_{>0}.
\]

The repository starts with one bounded community lead: a ten-point arithmetic progression in the mod-107 signed-divisor deficit and a short difference-set proof that two translates saturate the quadratic-nonresidue sheet. The calculation has an executable Python certificate and a Lean certificate. It is useful local structure, not a proof of the conjecture and not a priority claim.

## Start here

- [Canonical problem statement](problem/statement.md)
- [Current status](STATUS.md)
- [Mod-107 note](work/MC-ES-PACKET-R107-001/r107_deficit_progression.tex)
- [Python certificate](certificates/verify_r107_deficit_progression.py)
- [Lean certificate](formal/lean/R107DeficitProgression.lean)
- [Typed claim ledger](corpus/claims.ndjson)
- [Contribution and review rules](CONTRIBUTING.md)
- [Rights and publication boundary](RIGHTS.md)

The larger historical project remains available as the immutable [Erdős–Straus Project Archive on Zenodo](https://zenodo.org/records/21845035). A live reader is being reconstructed separately from that archive. These resources are references, not proof that every inherited claim is correct.

## Reproduce the first packet

Python 3.11 or newer is sufficient for the finite checker:

```console
python certificates/verify_r107_deficit_progression.py
python -O certificates/verify_r107_deficit_progression.py
```

The two outputs must be byte-identical. The checker uses explicit runtime guards and contains no Python `assert` statements.

The Lean project is pinned to Lean 4.32.0 and mathlib v4.32.0:

```console
cd formal/lean
lake exe cache get
lake build
lake env lean R107DeficitProgression.lean
```

Validate the preserved Commons contracts and live packet graph with:

```console
python tools/validate_packets.py --schema-only
python tools/validate_packets.py --require-live
```

## Public boundary

This repository is built from an explicit allowlist. Raw transcripts, prompt histories, private correspondence, personal context, credentials, private workspace paths, copyrighted paper or book PDFs, and unlicensed source payloads are not part of the workbench. Please open a literature lead, bounded result, computation, or review issue instead of uploading private source dumps.
