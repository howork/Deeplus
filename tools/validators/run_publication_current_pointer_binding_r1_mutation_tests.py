#!/usr/bin/env python3
"""Run independent mutations against the R94 publication binding."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_publication_current_pointer_binding_r1 as validator


Documents = list[Any]
Mutator = Callable[[Documents], None]


def current_binding_true(docs: Documents) -> None:
    docs[3]["candidate_binding"]["current_binding"] = True


def pending_receipt(docs: Documents) -> None:
    docs[3]["candidate_binding"]["receipt_location"] = "PENDING_POST_MERGE_READBACK_RECEIPT"


def semantic_commit_drift(docs: Documents) -> None:
    docs[0]["identity_roles"]["semantic_publication"]["commit"] = "0" * 40


def closure_commit_drift(docs: Documents) -> None:
    docs[5]["publication_closure"]["merge_commit"] = "0" * 40


def closure_tree_drift(docs: Documents) -> None:
    docs[5]["publication_closure"]["tree"] = "0" * 40


def receipt_binding_true(docs: Documents) -> None:
    docs[5]["binding"]["pointer_current_binding"] = True


def ci_failure(docs: Documents) -> None:
    docs[5]["github_actions"]["closure_merge"][0]["conclusion"] = "FAILURE"


def product_pass(docs: Documents) -> None:
    docs[2]["execution"]["production_implementation"] = "PASS"


MUTATIONS: list[tuple[str, Mutator]] = [
    ("R94-M-01-CURRENT-BINDING-TRUE", current_binding_true),
    ("R94-M-02-PENDING-RECEIPT", pending_receipt),
    ("R94-M-03-SEMANTIC-COMMIT-DRIFT", semantic_commit_drift),
    ("R94-M-04-CLOSURE-COMMIT-DRIFT", closure_commit_drift),
    ("R94-M-05-CLOSURE-TREE-DRIFT", closure_tree_drift),
    ("R94-M-06-RECEIPT-BINDING-TRUE", receipt_binding_true),
    ("R94-M-07-CI-FAILURE", ci_failure),
    ("R94-M-08-PRODUCT-PASS", product_pass),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base = list(validator.load_documents(root))
    base_errors = validator.validate_documents(root, *base)
    results = []
    if not base_errors:
        for mutation_id, mutate in MUTATIONS:
            documents = copy.deepcopy(base)
            mutate(documents)
            errors = validator.validate_documents(root, *documents)
            results.append({"mutation_id": mutation_id, "rejected": bool(errors), "error_count": len(errors)})
    declared = [row.get("mutation_id") for row in base[2].get("mutations", [])]
    expected = [mutation_id for mutation_id, _ in MUTATIONS]
    passed = not base_errors and declared == expected and len(results) == 8 and all(row["rejected"] for row in results)
    receipt = {
        "schema": "deeplus.r94-publication-current-pointer-binding-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "baseline_main": validator.BASELINE_MAIN,
        "mutation_count": 8,
        "rejected_mutation_count": sum(row.get("rejected", False) for row in results),
        "mutations": results,
        "base_errors": base_errors,
        "product_execution": "NOT_RUN",
        "github_mutation": False,
    }
    print(json.dumps(receipt, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
