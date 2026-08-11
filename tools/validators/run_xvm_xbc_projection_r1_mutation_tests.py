#!/usr/bin/env python3
"""Run bounded negative controls for the R92 XBC projection contract."""

from __future__ import annotations

import argparse
import copy
import json
import struct
from pathlib import Path

from validate_xvm_xbc_projection_r1 import (
    BACKEND,
    CONTRACT,
    MACHINE,
    build_sample_container,
    load,
    validate,
    validate_container_bytes,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    baseline = validate(root)
    if baseline:
        print(json.dumps({"result": "BLOCKED_BASELINE", "errors": baseline}, separators=(",", ":")))
        return 1

    contract = load(root / CONTRACT)
    machine = load(root / MACHINE)
    backend = load(root / BACKEND)
    sample = build_sample_container(contract)
    mutations: list[tuple[str, bool, list[str]]] = []

    def container_mutation(name: str, mutate) -> None:
        value = bytearray(sample)
        mutate(value)
        errors = validate_container_bytes(bytes(value))
        mutations.append((name, bool(errors), errors[:4]))

    container_mutation("BAD_MAGIC", lambda x: x.__setitem__(0, 0))
    container_mutation("UNSUPPORTED_MAJOR", lambda x: x.__setitem__(8, 2))
    container_mutation("NONZERO_FLAGS", lambda x: x.__setitem__(12, 1))
    container_mutation("DUPLICATE_SECTION_KIND", lambda x: x.__setitem__(128 + 56, 1))
    container_mutation("SECTION_OFFSET_GAP", lambda x: x.__setitem__(128 + 8, x[128 + 8] + 1))
    container_mutation("SECTION_PAYLOAD_MUTATION", lambda x: x.__setitem__(688, x[688] ^ 1))
    container_mutation("LOGICAL_DIGEST_MUTATION", lambda x: x.__setitem__(64, x[64] ^ 1))
    container_mutation("TRAILING_BYTE", lambda x: x.extend(b"\x00"))

    wrong_operation = copy.deepcopy(contract)
    wrong_operation["opcode_contract"]["operation_assignments"][1]["opcode"] = 0
    errors = validate(root, {CONTRACT: wrong_operation})
    mutations.append(("DUPLICATE_OPERATION_OPCODE", bool(errors), errors[:4]))

    wrong_terminator = copy.deepcopy(contract)
    wrong_terminator["opcode_contract"]["terminator_assignments"][0]["opcode"] = 32769
    errors = validate(root, {CONTRACT: wrong_terminator})
    mutations.append(("TERMINATOR_OPCODE_DRIFT", bool(errors), errors[:4]))

    wrong_machine = copy.deepcopy(machine)
    wrong_machine["projection_capability_fence"]["projection_contracts"].pop("PROJ-CAP-XVM-CANONICAL-XBC-R1")
    errors = validate(root, {MACHINE: wrong_machine})
    mutations.append(("DROP_CAPABILITY_BINDING", bool(errors), errors[:4]))

    wrong_backend = copy.deepcopy(backend)
    wrong_backend["xvm_xbc_projection_guard"]["backend_semantic_reselection_count"] = 1
    errors = validate(root, {BACKEND: wrong_backend})
    mutations.append(("BACKEND_RESELECTS_SEMANTICS", bool(errors), errors[:4]))

    passed = all(row[1] for row in mutations)
    print(json.dumps({
        "schema": "deeplus.xvm-xbc-projection-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "declared": len(mutations),
        "rejected": sum(row[1] for row in mutations),
        "results": [
            {"mutation_id": name, "rejected": rejected, "errors": errors}
            for name, rejected, errors in mutations
        ],
        "product_execution": "NOT_RUN",
    }, ensure_ascii=False, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
