#!/usr/bin/env python3
"""Fail-closed checks for the deliberately allowlisted public workbench."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".cff", ".json", ".lean", ".md", ".ndjson", ".py", ".tex",
    ".toml", ".txt", ".yml", ".yaml",
}
TEXT_NAMES = {".gitattributes", ".gitignore", "LICENSE", "lean-toolchain"}
OPTIONAL_LIFECYCLE_FILES = {
    "packets/MC-ES-PACKET-R107-001-v1.1.0-ready.json",
    "transitions/MC-ES-TRANSITION-R107-001-v1.0.0.json",
}
REQUIRED_DRAFT_FILES = {
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/literature.yml",
    ".github/ISSUE_TEMPLATE/result.yml",
    ".github/ISSUE_TEMPLATE/review.yml",
    ".github/workflows/validate.yml",
    ".gitattributes",
    ".gitignore",
    "CITATION.cff",
    "COMMONS_BASELINE.json",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "RIGHTS.md",
    "STATUS.md",
    "certificates/verify_r107_deficit_progression.py",
    "corpus/claims.ndjson",
    "corpus/crosswalks.ndjson",
    "corpus/dependencies.ndjson",
    "corpus/morphisms.ndjson",
    "formal/lean/R107DeficitProgression.lean",
    "formal/lean/R107DeficitProgression/Definitions.lean",
    "formal/lean/R107DeficitProgression/Difference.lean",
    "formal/lean/R107DeficitProgression/FullSupport.lean",
    "formal/lean/R107DeficitProgression/Reduced.lean",
    "formal/lean/lake-manifest.json",
    "formal/lean/lakefile.toml",
    "formal/lean/lean-toolchain",
    "packets/MC-ES-PACKET-R107-001-v1.0.0-draft.json",
    "problem/statement.md",
    "problems/MC-ES-PROBLEM-001-v1.0.0.json",
    "schemas/evidence-record.schema.json",
    "schemas/packet-transition.schema.json",
    "schemas/problem-record.schema.json",
    "schemas/research-packet.schema.json",
    "schemas/review-record.schema.json",
    "schemas/run-record.schema.json",
    "schemas/source-record.schema.json",
    "sources/MC-ES-SOURCE-REDDIT-R107-001.json",
    "sources/MC-ES-SOURCE-STATEMENT-001.json",
    "sources/MC-ES-SOURCE-ZENODO-21845035.json",
    "sources/reddit-r107-public-lead-metadata.md",
    "sources/zenodo-21845035-metadata.md",
    "tools/validate_packets.py",
    "tools/verify_lean_environment.py",
    "tools/verify_lean_audit.py",
    "tools/verify_public_surface.py",
    "work/MC-ES-PACKET-R107-001/R107_DEFICIT_PROGRESSION_REPLAY.json",
    "work/MC-ES-PACKET-R107-001/r107_deficit_progression.pdf",
    "work/MC-ES-PACKET-R107-001/r107_deficit_progression.tex",
}
FORBIDDEN = {
    "absolute Windows user path": re.compile(r"C:[\\/]Users[\\/]", re.IGNORECASE),
    "Codex private root": re.compile(re.escape("." + "codex"), re.IGNORECASE),
    "ChatGPT backend locator": re.compile("backend" + "-api|est" + "uary", re.IGNORECASE),
    "stable private attachment id": re.compile(r"file_[0-9a-f]{16,}", re.IGNORECASE),
    "GitHub classic token": re.compile(r"(?:^|[^A-Za-z0-9])ghp_[A-Za-z0-9]{20,}"),
    "GitHub fine-grained token": re.compile(r"(?:^|[^A-Za-z0-9])github_pat_[A-Za-z0-9_]{20,}"),
    "private key": re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH )?" + "PRIVATE KEY-----"),
    "private archive path": re.compile("private_" + "review|rar_" + "beavershine", re.IGNORECASE),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_allowlist() -> tuple[set[str], int]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "-z"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    require(result.stderr == b"", "git ls-files wrote stderr")
    tracked = {
        item.decode("utf-8") for item in result.stdout.split(b"\0") if item
    }
    missing = REQUIRED_DRAFT_FILES - tracked
    unexpected = tracked - REQUIRED_DRAFT_FILES - OPTIONAL_LIFECYCLE_FILES
    lifecycle = tracked & OPTIONAL_LIFECYCLE_FILES
    require(not missing, f"required tracked files missing: {sorted(missing)}")
    require(not unexpected, f"unexpected tracked files: {sorted(unexpected)}")
    require(
        lifecycle in (set(), OPTIONAL_LIFECYCLE_FILES),
        f"partial lifecycle publication: {sorted(lifecycle)}",
    )
    return tracked, len(lifecycle)


def scan_public_text(tracked: set[str]) -> int:
    scanned = 0
    for relative in sorted(tracked):
        path = ROOT / relative
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        text = path.read_text(encoding="utf-8")
        scanned += 1
        for label, pattern in FORBIDDEN.items():
            require(pattern.search(text) is None, f"{relative} contains {label}")
    return scanned


def verify_replay_receipt() -> int:
    receipt_path = ROOT / "work/MC-ES-PACKET-R107-001/R107_DEFICIT_PROGRESSION_REPLAY.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(receipt.get("status") == "PASS", "replay receipt is not PASS")
    require(receipt.get("copyrighted_bulk_text_included") is False,
            "receipt does not exclude copyrighted bulk text")
    require(receipt.get("private_correspondence_included") is False,
            "receipt does not exclude private correspondence")
    artifacts = receipt.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, "receipt artifact list missing")
    seen: set[str] = set()
    root = ROOT.resolve()
    for entry in artifacts:
        relative = entry.get("path")
        require(isinstance(relative, str) and relative not in seen,
                f"invalid or duplicate receipt path: {relative!r}")
        seen.add(relative)
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(root), f"receipt path escapes repository: {relative}")
        require(path.is_file(), f"receipt artifact missing: {relative}")
        require(path.stat().st_size == entry.get("bytes"),
                f"receipt byte mismatch: {relative}")
        require(sha256(path) == entry.get("sha256"),
                f"receipt hash mismatch: {relative}")
    return len(artifacts)


def verify_pdf_surface() -> str:
    pdf = ROOT / "work/MC-ES-PACKET-R107-001/r107_deficit_progression.pdf"
    expected = "202b56085f3b78e2a80ac2a5c88a5ba3b8e0f0b44548fd09a281539848eb4f9b"
    require(sha256(pdf) == expected, "public PDF differs from the visually audited bytes")
    payload = pdf.read_bytes()
    for marker in (b"/EmbeddedFiles", b"/Filespec", b"/JavaScript", b"/JS ", b"/Launch", b"/Encrypt"):
        require(marker not in payload, f"public PDF contains active/embedded marker {marker!r}")
    require(re.search(rb"/Author\s*\(\s*[^)]", payload) is None,
            "public PDF contains nonempty Author metadata")
    latin1 = payload.decode("latin-1")
    for label, pattern in FORBIDDEN.items():
        require(pattern.search(latin1) is None, f"public PDF contains {label}")
    return expected


def verify_ndjson() -> tuple[int, int]:
    ids: set[str] = set()
    records = 0
    for path in sorted((ROOT / "corpus").glob("*.ndjson")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(bool(line.strip()), f"blank NDJSON line {path.name}:{line_number}")
            record = json.loads(line)
            id_fields = [key for key in record if key.endswith("_id")]
            require(len(id_fields) >= 1, f"missing stable id {path.name}:{line_number}")
            stable_id = str(record[id_fields[0]])
            require(stable_id not in ids, f"duplicate stable id {stable_id}")
            ids.add(stable_id)
            records += 1
    return records, len(ids)


def replay_python() -> tuple[str, str]:
    checker = ROOT / "certificates" / "verify_r107_deficit_progression.py"
    tree = ast.parse(checker.read_text(encoding="utf-8"))
    require(not any(isinstance(node, ast.Assert) for node in ast.walk(tree)),
            "finite checker contains removable assert nodes")
    ordinary = subprocess.run(
        [sys.executable, str(checker)], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    optimized = subprocess.run(
        [sys.executable, "-O", str(checker)], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    require(ordinary.stderr == b"" and optimized.stderr == b"", "finite checker wrote stderr")
    require(ordinary.stdout == optimized.stdout, "ordinary and optimized checker output differ")
    require(b"status=PASS" in ordinary.stdout, "finite checker did not report PASS")
    return sha256(checker), hashlib.sha256(ordinary.stdout).hexdigest()


def verify_required_artifacts() -> dict[str, str]:
    required = [
        "problem/statement.md",
        "work/MC-ES-PACKET-R107-001/r107_deficit_progression.tex",
        "work/MC-ES-PACKET-R107-001/r107_deficit_progression.pdf",
        "certificates/verify_r107_deficit_progression.py",
        "formal/lean/R107DeficitProgression.lean",
        "formal/lean/R107DeficitProgression/Definitions.lean",
        "formal/lean/R107DeficitProgression/Reduced.lean",
        "formal/lean/R107DeficitProgression/Difference.lean",
        "formal/lean/R107DeficitProgression/FullSupport.lean",
        "formal/lean/lean-toolchain",
        "formal/lean/lakefile.toml",
        "formal/lean/lake-manifest.json",
        "corpus/claims.ndjson",
        "corpus/dependencies.ndjson",
        "corpus/morphisms.ndjson",
        "corpus/crosswalks.ndjson",
    ]
    hashes: dict[str, str] = {}
    for relative in required:
        path = ROOT / relative
        require(path.is_file(), f"required artifact missing: {relative}")
        require(path.stat().st_size > 0, f"required artifact empty: {relative}")
        hashes[relative] = sha256(path)
    return hashes


def verify_commons_baseline() -> int:
    baseline = json.loads((ROOT / "COMMONS_BASELINE.json").read_text(encoding="utf-8"))
    require(baseline["upstream_commit"] == "6c0c7bbd368cb554d4d9ab9133881a5d4bf56a75",
            "unexpected Commons baseline commit")
    components = baseline["copied_components"]
    for component in components:
        path = ROOT / component["path"]
        require(path.is_file(), f"missing vendored contract {component['path']}")
        require(path.stat().st_size == component["bytes"],
                f"vendored contract byte mismatch {component['path']}")
        require(sha256(path) == component["sha256"],
                f"vendored contract hash mismatch {component['path']}")
    return len(components)


def main() -> None:
    tracked, lifecycle_count = tracked_allowlist()
    artifacts = verify_required_artifacts()
    receipt_artifacts = verify_replay_receipt()
    pdf_hash = verify_pdf_surface()
    contracts = verify_commons_baseline()
    scanned = scan_public_text(tracked)
    records, unique_ids = verify_ndjson()
    checker_hash, output_hash = replay_python()
    require(artifacts["certificates/verify_r107_deficit_progression.py"] == checker_hash,
            "checker hash changed during replay")
    print("verification=public-surface")
    print("status=PASS")
    print(f"text_files_scanned={scanned}")
    print(f"ndjson_records={records}")
    print(f"unique_stable_ids={unique_ids}")
    print(f"required_artifacts={len(artifacts)}")
    print(f"tracked_allowlist_files={len(tracked)}")
    print(f"lifecycle_records={lifecycle_count}")
    print(f"receipt_artifacts_verified={receipt_artifacts}")
    print(f"vendored_contracts={contracts}")
    print(f"pdf_sha256={pdf_hash}")
    print(f"checker_sha256={checker_hash}")
    print(f"checker_output_sha256={output_hash}")
    print("unexpected_tracked_files=0")
    print("forbidden_text_or_binary_matches=0")


if __name__ == "__main__":
    main()
