#!/usr/bin/env python3
"""Run independent in-memory mutations against the R93 authority rebase."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_formatter_lsp_dpg_authority_rebase as validator


Documents = list[Any]
Mutator = Callable[[Documents], None]


def contract(documents: Documents) -> dict[str, Any]:
    return documents[0]


def fixtures(documents: Documents) -> dict[str, Any]:
    return documents[2]


def frontend(documents: Documents) -> dict[str, Any]:
    return documents[3]


def promote_ebnf(documents: Documents) -> None:
    contract(documents)["parser_authority_rebase"]["surface_census"]["semantic_authority"] = True


def drop_axis(axis: str) -> Mutator:
    def mutate(documents: Documents) -> None:
        rows = contract(documents)["parser_authority_rebase"]["authority_digest_set"]
        contract(documents)["parser_authority_rebase"]["authority_digest_set"] = [
            row for row in rows if row["axis"] != axis
        ]

    return mutate


def restore_grammar_sha(documents: Documents) -> None:
    recipe = contract(documents)["identity_domains"]["ParseSnapshotId"]["recipe"]
    recipe[recipe.index("parser_authority_digest_set")] = "grammar_sha256"


def restore_production_id(documents: Documents) -> None:
    recipe = contract(documents)["identity_domains"]["CstContentId"]["recipe"]
    recipe[recipe.index("structural_cst_owner_id")] = "production_id"


def allow_old_handle_reuse(documents: Documents) -> None:
    frontend(documents)["formatter_lsp_incremental_parsing_contract"]["parser_authority_rebase"]["old_handle_reuse_on_authority_change"] = 1


def allow_tooling_reselection(documents: Documents) -> None:
    contract(documents)["parser_authority_rebase"]["tooling_parser_semantic_reselection_count"] = 1


def claim_product_pass(documents: Documents) -> None:
    fixtures(documents)["execution"]["production_formatter"] = "PASS"


MUTATIONS: list[tuple[str, Mutator]] = [
    ("R93-M-01-PROMOTE-EBNF", promote_ebnf),
    ("R93-M-02-DROP-DPG", drop_axis("STRUCTURAL_DPG")),
    ("R93-M-03-DROP-PARSER-CONTEXT", drop_axis("PARSER_CONTEXT")),
    ("R93-M-04-DROP-PRATT", drop_axis("PRATT")),
    ("R93-M-05-DROP-SCANNER", drop_axis("SCANNER")),
    ("R93-M-06-RESTORE-GRAMMAR-SHA256", restore_grammar_sha),
    ("R93-M-07-RESTORE-PRODUCTION-ID", restore_production_id),
    ("R93-M-08-ALLOW-OLD-HANDLE-REUSE", allow_old_handle_reuse),
    ("R93-M-09-ALLOW-TOOLING-RESELECTION", allow_tooling_reselection),
    ("R93-M-10-CLAIM-PRODUCT-PASS", claim_product_pass),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()

    base = list(validator.load_documents(root))
    base_errors = validator.validate_documents(root, *base)
    results: list[dict[str, Any]] = []
    if not base_errors:
        for mutation_id, mutate in MUTATIONS:
            mutated = copy.deepcopy(base)
            mutate(mutated)
            errors = validator.validate_documents(root, *mutated)
            results.append(
                {
                    "mutation_id": mutation_id,
                    "rejected": bool(errors),
                    "error_count": len(errors),
                }
            )

    declared_ids = [
        row.get("mutation_id")
        for row in fixtures(base).get("authority_mutations", [])
    ]
    expected_ids = [mutation_id for mutation_id, _ in MUTATIONS]
    passed = (
        not base_errors
        and declared_ids == expected_ids
        and len(results) == len(MUTATIONS)
        and all(row["rejected"] for row in results)
    )
    receipt = {
        "schema": "deeplus.r93-formatter-lsp-dpg-authority-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "baseline_main": validator.BASELINE_MAIN,
        "mutation_count": len(MUTATIONS),
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
