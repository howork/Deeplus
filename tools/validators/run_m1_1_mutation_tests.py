#!/usr/bin/env python3
"""Verify that M1.1 validator rejects representative closure mutations."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools/validators/validate_workspace.py"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def alias_duplicate(root: Path) -> None:
    path = root / "migration/path-aliases.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["aliases"][1]["legacy_name"] = value["aliases"][0]["legacy_name"]
    write_json(path, value)


def oversize_shard(root: Path) -> None:
    path = root / "library/prelude/signatures/chunks/part-0001.json"
    path.write_text(path.read_text(encoding="utf-8") + (" " * 70000), encoding="utf-8")


def broken_schema_ref(root: Path) -> None:
    path = root / "schemas/language/checker-predicate-fixture-row.schema.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.setdefault("$defs", {})["mutation_descriptor"] = {"$ref": "./missing-descriptor.schema.json"}
    write_json(path, value)


def authority_drift(root: Path) -> None:
    path = root / "spec/language.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nmutation\n", encoding="utf-8")


def invalid_gate(root: Path) -> None:
    reassembly = json.loads((root / "migration/catalog-reassembly.json").read_text(encoding="utf-8"))
    contract = next(row for row in reassembly["contracts"] if row["shard_root"] == "examples/manifests/by-outcome")
    for rel in contract["ordered_shard_paths"]:
        path = root / rel
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            if row.get("expected_outcome") == "accept_with_gate":
                row["source_activation"] = "stdlib"
                write_json(path, rows)
                return


def missing_candidate_state(root: Path) -> None:
    (root / "release/candidate-state.json").unlink()


def legacy_current_pointer(root: Path) -> None:
    path = root / "spec/frontend/frontend-model.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["authority_bundle"]["exact_syntax"] = "Deeplus_Grammar_0_1_2_R51f3_Current_Canonical.ebnf"
    write_json(path, value)


def run() -> int:
    mutations: list[tuple[str, Callable[[Path], None]]] = [
        ("same_count_alias_duplicate", alias_duplicate),
        ("unlisted_root_oversize_shard", oversize_shard),
        ("broken_local_schema_ref", broken_schema_ref),
        ("authority_file_drift", authority_drift),
        ("invalid_gate_activation", invalid_gate),
        ("missing_candidate_state", missing_candidate_state),
        ("legacy_basename_in_current_owner", legacy_current_pointer),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="deeplus-m1-1-mutations-") as temp:
        base = Path(temp)
        for name, mutate in mutations:
            target = base / name
            shutil.copytree(ROOT, target)
            mutate(target)
            result = subprocess.run(
                ["python3", str(VALIDATOR), "--root", str(target), "--candidate", "--no-receipt"],
                text=True, capture_output=True, check=False,
            )
            rejected = result.returncode != 0
            results.append({"mutation": name, "rejected": rejected, "returncode": result.returncode})
    passed = sum(row["rejected"] for row in results)
    receipt = {
        "schema": "deeplus.validator-mutation-receipt/v1",
        "revision": "r51f3-migration-m1.1",
        "result": "PASS" if passed == len(results) else "FAIL",
        "mutations": len(results), "rejected": passed,
        "product_execution": "NOT_RUN", "cases": results,
    }
    receipt_path = ROOT / "release/evidence/m1.1-validator-mutation-receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(receipt_path, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
