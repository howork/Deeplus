#!/usr/bin/env python3
"""Validate R27 closed RHS binding and six-root grammar reachability."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable


CONTRACT_REL = "spec/contracts/grammar-topology-closure-r1.json"
FIXTURE_REL = "tests/fixtures/current/grammar-topology-closure-r1.json"
GRAMMAR_REL = "spec/grammar/deeplus.ebnf"
FRONTEND_REL = "spec/frontend/frontend-model.json"
DISPOSITION_REL = "spec/contracts/grammar-production-disposition-registry-r1.json"
REFERENCE_CONTRACT_REL = "spec/contracts/grammar-reference-r1.json"

CHECK_IDS = [
    "R27_CONTRACT_EXACT",
    "R27_RHS_REFERENCE_BINDING_643",
    "R27_EXTERNAL_SYMBOL_REGISTRY_EXACT_40",
    "R27_SIX_ROOT_REACHABILITY_EXACT",
    "R27_UNOWNED_ORPHAN_COUNT_ZERO",
    "R27_PROFILE_EDGE_FENCE",
    "R27_AGGREGATE_ENTRY_FENCE",
    "R27_ACCEPTANCE_CASES_EXACT_3",
    "R27_MUTATIONS_EXACT_6",
    "R27_GOVERNANCE_FENCE",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_generator(root: Path):
    path = root / "tools/generators/generate_grammar_reference.py"
    spec = importlib.util.spec_from_file_location("deeplus_grammar_reference", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load grammar-reference generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_documents(root: Path) -> dict[str, Any]:
    return {
        "contract": load_json(root / CONTRACT_REL),
        "fixtures": load_json(root / FIXTURE_REL),
        "grammar_text": (root / GRAMMAR_REL).read_text(encoding="utf-8"),
        "grammar_bytes": (root / GRAMMAR_REL).read_bytes(),
        "frontend": load_json(root / FRONTEND_REL),
        "disposition": load_json(root / DISPOSITION_REL),
        "disposition_bytes": (root / DISPOSITION_REL).read_bytes(),
        "reference_contract": load_json(root / REFERENCE_CONTRACT_REL),
    }


def evaluate(documents: dict[str, Any], generator: Any) -> list[str]:
    errors: list[str] = []
    contract = documents["contract"]
    fixtures = documents["fixtures"]

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(
        contract.get("schema") == "deeplus.grammar-topology-closure/r1",
        "CONTRACT_SCHEMA",
    )
    require(
        contract.get("status") == "CURRENT_STABLE_DESIGN_MACHINE_CONTRACT",
        "CONTRACT_STATUS",
    )
    require(
        contract.get("production_set", {}).get("count") == 643,
        "CONTRACT_PRODUCTION_COUNT",
    )
    require(
        contract.get("external_symbol_set", {}).get("count") == 40,
        "CONTRACT_EXTERNAL_COUNT",
    )
    require(
        len(contract.get("source_roots", [])) == 6,
        "ROOT_SET_CONTRACT_COUNT",
    )
    require(
        contract.get("unowned_orphan_count") == 0,
        "ORPHAN_CONTRACT_COUNT",
    )
    require(
        contract.get("illegal_cross_profile_edge_count") == 0,
        "PROFILE_EDGE_CONTRACT_COUNT",
    )
    require(
        documents["frontend"].get("grammar_topology_closure")
        == {
            "contract": CONTRACT_REL,
            "disposition_registry": DISPOSITION_REL,
            "source_root_count": 6,
            "production_count": 643,
            "closed_external_symbol_count": 40,
            "unowned_orphan_count": 0,
            "illegal_cross_profile_edge_count": 0,
            "product_support": "NOT_RUN",
        },
        "CONTRACT_FRONTEND_BINDING",
    )

    inputs = contract.get("inputs", {})
    require(
        inputs.get("grammar", {}).get("sha256")
        == hashlib.sha256(documents["grammar_bytes"]).hexdigest(),
        "CONTRACT_GRAMMAR_HASH",
    )
    require(
        inputs.get("disposition_registry", {}).get("sha256")
        == hashlib.sha256(documents["disposition_bytes"]).hexdigest(),
        "CONTRACT_DISPOSITION_HASH",
    )

    try:
        productions, _counts = generator.parse_grammar(
            documents["grammar_text"],
            documents["frontend"],
            documents["reference_contract"],
        )
        generator.validate_grammar_topology(
            productions,
            documents["frontend"],
            contract,
            documents["disposition"],
        )
    except generator.GeneratorError as exc:
        errors.append(exc.code)

    expected_cases = [
        ("IR-R3-GAP-12-P", "positive", "ACCEPT_CLOSED_TOPOLOGY"),
        ("IR-R3-GAP-12-B", "boundary", "ACCEPT_SHARED_REACHABILITY"),
        (
            "IR-R3-GAP-12-N",
            "negative",
            "REJECT_UNDEFINED_OR_ORPHAN_WITH_LOCATOR",
        ),
    ]
    observed_cases = [
        (row.get("test_id"), row.get("kind"), row.get("expected_outcome"))
        for row in fixtures.get("acceptance_cases", [])
        if isinstance(row, dict)
    ]
    require(observed_cases == expected_cases, "FIXTURE_CASES")
    mutation_specs = fixtures.get("mutation_specs", [])
    require(
        isinstance(mutation_specs, list)
        and [row.get("mutation_id") for row in mutation_specs]
        == [f"R27-MUT-{index:03d}" for index in range(1, 7)],
        "FIXTURE_MUTATION_SPECS",
    )
    acceptance = fixtures.get("acceptance", {})
    require(
        acceptance
        == {
            "case_count": 3,
            "mutation_count": 6,
            "production_count": 643,
            "external_symbol_count": 40,
            "source_root_count": 6,
            "unowned_orphan_count": 0,
            "illegal_cross_profile_edge_count": 0,
            "semantic_change_count": 0,
            "product_execution": "NOT_RUN",
        },
        "FIXTURE_ACCEPTANCE",
    )
    governance = contract.get("governance", {})
    require(governance.get("gap_id") == "IR-FE-P1-039", "GOVERNANCE_GAP")
    require(governance.get("semantic_change_count") == 0, "GOVERNANCE_SEMANTIC")
    require(
        governance.get("grammar_production_change_count") == 0,
        "GOVERNANCE_GRAMMAR",
    )
    require(governance.get("new_source_spelling_count") == 0, "GOVERNANCE_SURFACE")
    require(governance.get("feature_p1") == "22_OPEN_UNCHANGED", "GOVERNANCE_P1")
    require(governance.get("m13_actions") == "4_OPEN_UNCHANGED", "GOVERNANCE_M13")
    require(governance.get("product_lanes") == "15/15_NOT_RUN", "GOVERNANCE_PRODUCT")
    require(contract.get("product_support") == "NOT_RUN", "GOVERNANCE_SUPPORT")
    return errors


def mutation_receipts(documents: dict[str, Any], generator: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def disposition_row(docs: dict[str, Any], production_id: str) -> dict[str, Any]:
        return next(
            row
            for row in docs["disposition"]["production_rows"]
            if row.get("production_id") == production_id
        )

    def detach_library_items(docs: dict[str, Any]) -> None:
        docs["grammar_text"] = docs["grammar_text"].replace(
            "LibrarySourceFile ::= ModuleDecl? LibrarySourceItem* ;",
            "LibrarySourceFile ::= ModuleDecl? ;",
            1,
        )
        disposition_row(docs, "LibrarySourceFile")["referenced_productions"] = [
            "ModuleDecl"
        ]

    def add_stable_to_preview_edge(docs: dict[str, Any]) -> None:
        docs["grammar_text"] = docs["grammar_text"].replace(
            'ExpressionPrefixParselet ::= "+" | "-" | "not" | "~~"',
            'ExpressionPrefixParselet ::= PreviewGate | "+" | "-" | "not" | "~~"',
            1,
        )
        disposition_row(docs, "ExpressionPrefixParselet")[
            "referenced_productions"
        ] = ["PreviewGate"]

    def run(
        mutation_id: str,
        mutate: Callable[[dict[str, Any]], None],
        expected_prefix: str,
    ) -> None:
        mutated = copy.deepcopy(documents)
        mutate(mutated)
        observed = evaluate(mutated, generator)
        rejected = any(error.startswith(expected_prefix) for error in observed)
        rows.append(
            {
                "mutation_id": mutation_id,
                "result": "REJECTED" if rejected else "SURVIVED",
                "expected_error_prefix": expected_prefix,
                "observed_errors": observed,
            }
        )

    run(
        "R27-MUT-001",
        lambda docs: docs.update(
            {
                "grammar_text": docs["grammar_text"].replace(
                    "SourceCharacter ::= UnicodeScalar ;",
                    "SourceCharacter ::= UnicodeScalarr ;",
                    1,
                )
            }
        ),
        "GRAMMAR_TOPOLOGY_EXTERNAL_REGISTRY",
    )
    run(
        "R27-MUT-002",
        lambda docs: docs["disposition"]["external_symbol_contracts"].pop(0),
        "GRAMMAR_TOPOLOGY_EXTERNAL_REGISTRY",
    )
    run(
        "R27-MUT-003",
        detach_library_items,
        "GRAMMAR_TOPOLOGY_ROOT_REACHABILITY",
    )
    run(
        "R27-MUT-004",
        add_stable_to_preview_edge,
        "GRAMMAR_TOPOLOGY_PROFILE_EDGE",
    )
    run(
        "R27-MUT-005",
        lambda docs: disposition_row(docs, "ExpressionPrefixParselet").update(
            {"reachability_owner": "CURRENT_SOURCE_GRAPH"}
        ),
        "GRAMMAR_TOPOLOGY_ORPHAN",
    )
    run(
        "R27-MUT-006",
        lambda docs: docs["contract"]["source_roots"].pop(),
        "GRAMMAR_TOPOLOGY_ROOT_SET",
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        generator = load_generator(root)
        documents = load_documents(root)
        errors = evaluate(documents, generator)
        mutations = mutation_receipts(documents, generator)
    except Exception as exc:  # noqa: BLE001
        errors = [f"VALIDATOR_EXCEPTION:{type(exc).__name__}:{exc}"]
        mutations = []

    mutation_pass = (
        len(mutations) == 6
        and all(row["result"] == "REJECTED" for row in mutations)
    )
    prefix_groups = {
        "R27_CONTRACT_EXACT": ("CONTRACT_",),
        "R27_RHS_REFERENCE_BINDING_643": (
            "GRAMMAR_TOPOLOGY_PRODUCTION_SET",
            "GRAMMAR_TOPOLOGY_DISPOSITION",
            "GRAMMAR_TOPOLOGY_REFERENCE_BINDING",
        ),
        "R27_EXTERNAL_SYMBOL_REGISTRY_EXACT_40": (
            "GRAMMAR_TOPOLOGY_EXTERNAL_",
        ),
        "R27_SIX_ROOT_REACHABILITY_EXACT": (
            "GRAMMAR_TOPOLOGY_ROOT_",
            "GRAMMAR_TOPOLOGY_UNREACHABLE_SET",
        ),
        "R27_UNOWNED_ORPHAN_COUNT_ZERO": (
            "GRAMMAR_TOPOLOGY_ORPHAN",
            "ORPHAN_",
        ),
        "R27_PROFILE_EDGE_FENCE": (
            "GRAMMAR_TOPOLOGY_PROFILE_EDGE",
            "PROFILE_EDGE_",
        ),
        "R27_AGGREGATE_ENTRY_FENCE": (
            "GRAMMAR_TOPOLOGY_AGGREGATE_ROOT",
        ),
        "R27_ACCEPTANCE_CASES_EXACT_3": ("FIXTURE_",),
        "R27_GOVERNANCE_FENCE": ("GOVERNANCE_",),
    }
    checks = []
    for check_id in CHECK_IDS:
        if check_id == "R27_MUTATIONS_EXACT_6":
            passed = mutation_pass
        else:
            prefixes = prefix_groups[check_id]
            passed = not any(
                any(error.startswith(prefix) for prefix in prefixes)
                for error in errors
            )
        checks.append({"check_id": check_id, "pass": passed})

    result = "PASS" if not errors and all(row["pass"] for row in checks) else "FAIL"
    receipt = {
        "schema": "deeplus.r27-grammar-topology-validation-receipt/r1",
        "result": result,
        "evidence_level": "E2_STATIC_CLOSURE",
        "check_scope": "R27_GRAMMAR_TOPOLOGY_CLOSURE_EXACT",
        "check_count": len(checks),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "production_count": 643,
        "declared_reference_binding_count": 643,
        "external_symbol_count": 40,
        "source_root_count": 6,
        "six_root_union_count": 492,
        "six_root_shared_count": 465,
        "six_root_unreachable_count": 151,
        "aggregate_entry_root_count": 2,
        "unowned_orphan_count": 0,
        "illegal_cross_profile_edge_count": 0,
        "acceptance_case_count": 3,
        "mutation_count": len(mutations),
        "rejected_mutation_count": sum(
            row["result"] == "REJECTED" for row in mutations
        ),
        "mutations": mutations,
        "grammar_production_change_count": 0,
        "new_source_spelling_count": 0,
        "semantic_change_count": 0,
        "product_execution": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
