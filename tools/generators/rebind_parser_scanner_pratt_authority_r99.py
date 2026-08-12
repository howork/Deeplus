#!/usr/bin/env python3
"""Rebind byte identities owned by the R99 parser-authority repair."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


AXES = {
    "STRUCTURAL_DPG": "spec/grammar/deeplus.dpg",
    "PARSER_CONTEXT": "spec/grammar/deeplus.parser-contexts.json",
    "PRATT": "spec/contracts/closed-pratt-parse-goal-contract-r1.json",
    "SCANNER": "spec/contracts/complete-token-lexical-goal-contract-r1.json",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def encode_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(root: Path) -> dict[Path, bytes]:
    formatter_path = root / "spec/contracts/formatter-lsp-incremental-parsing-contract-r1.json"
    formatter = read_json(formatter_path)
    rows = formatter["parser_authority_rebase"]["authority_digest_set"]
    for row in rows:
        axis = row["axis"]
        expected_path = AXES[axis]
        if row["path"] != expected_path:
            raise ValueError(f"formatter authority path drift: {axis}")
        row["sha256"] = digest(root / expected_path)

    fixture_path = root / "tests/fixtures/current/formatter-lsp-incremental-parsing-r1.json"
    fixture = read_json(fixture_path)
    fixture_rows = fixture["parser_authority_domain"]["authority_digest_set"]
    for row in fixture_rows:
        axis = row["axis"]
        expected_path = AXES[axis]
        if row["path"] != expected_path:
            raise ValueError(f"fixture authority path drift: {axis}")
        row["sha256"] = digest(root / expected_path)

    differential_path = root / "spec/contracts/parser-grammar-differential-r1.json"
    differential = read_json(differential_path)
    context_path = root / AXES["PARSER_CONTEXT"]
    context_row = differential["artifacts"]["contexts"]
    if context_row["path"] != AXES["PARSER_CONTEXT"]:
        raise ValueError("parser differential context path drift")
    context_row["bytes"] = len(context_path.read_bytes())
    context_row["sha256"] = digest(context_path)

    return {
        formatter_path: encode_json(formatter),
        fixture_path: encode_json(fixture),
        differential_path: encode_json(differential),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    outputs = render(root)
    drift = [str(path.relative_to(root)) for path, data in outputs.items() if path.read_bytes() != data]
    if args.check:
        if drift:
            print(json.dumps({"result": "FAIL", "drift": drift}, sort_keys=True))
            return 1
        print(json.dumps({"result": "PASS", "output_count": len(outputs)}, sort_keys=True))
        return 0
    for path, data in outputs.items():
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(data.decode("utf-8"))
    print(json.dumps({"result": "UPDATED", "outputs": sorted(str(p.relative_to(root)) for p in outputs)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
