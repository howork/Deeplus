#!/usr/bin/env python3
"""Validate R27 closed RHS binding and six-root grammar reachability."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
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

REFRESHABLE_NEW_PRODUCTIONS = {
    "FunctionTypeModeItem": {
        "reachability_owner": "HANDWRITTEN_PARSER_REGISTRY",
        "disposition": "cst_only",
        "cst_shape": "INLINE_IN_PARENT_PRODUCTION_NODE",
        "cst_kind": None,
        "cst_owner_rule": (
            "nearest enclosing production node retains the exact child tokens and order"
        ),
        "ast_target": None,
        "ast_output_cardinality": "ZERO",
        "invalid_or_recovery_ast_count": 0,
    }
}


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


def grammar_bindings(
    productions: list[dict[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    names = {row["name"] for row in productions}
    quoted = re.compile(r'"(?:\\.|[^"\\])*"')
    references: dict[str, list[str]] = {}
    external_uses: dict[str, set[str]] = {}
    for row in productions:
        identifiers = set(
            re.findall(
                r"\b[A-Za-z][A-Za-z0-9_]*\b",
                quoted.sub(" ", row["definition"]),
            )
        )
        references[row["name"]] = sorted(identifiers & names)
        for symbol in identifiers - names:
            external_uses.setdefault(symbol, set()).add(row["name"])
    return references, {
        symbol: sorted(used_by) for symbol, used_by in external_uses.items()
    }


def ordered_counts(
    existing: dict[str, Any], values: list[str], label: str
) -> dict[str, int]:
    counts = Counter(values)
    if set(existing) != set(counts):
        raise RuntimeError(
            f"REFRESH_{label}_DOMAIN: expected={sorted(existing)} "
            f"observed={sorted(counts)}"
        )
    return {key: counts[key] for key in existing}


def render_refreshed_documents(
    root: Path, generator: Any
) -> dict[str, bytes]:
    """Render the bounded R29 grammar-derived contract refresh."""

    documents = load_documents(root)
    productions, _counts = generator.parse_grammar(
        documents["grammar_text"],
        documents["frontend"],
        documents["reference_contract"],
    )
    names = [row["name"] for row in productions]
    name_set = set(names)
    references, external_uses = grammar_bindings(productions)

    registry = copy.deepcopy(documents["disposition"])
    old_rows = registry.get("production_rows")
    if not isinstance(old_rows, list):
        raise RuntimeError("REFRESH_DISPOSITION_ROWS: not an array")
    old_by_name = {
        row.get("production_id"): row
        for row in old_rows
        if isinstance(row, dict) and isinstance(row.get("production_id"), str)
    }
    if len(old_by_name) != len(old_rows):
        raise RuntimeError(
            "REFRESH_DISPOSITION_ROWS: duplicate or invalid production_id"
        )
    missing = name_set - set(old_by_name)
    stale = set(old_by_name) - name_set
    if stale or not missing.issubset(REFRESHABLE_NEW_PRODUCTIONS):
        raise RuntimeError(
            "REFRESH_PRODUCTION_DELTA: "
            f"missing={sorted(missing)} stale={sorted(stale)}"
        )

    refreshed_rows: list[dict[str, Any]] = []
    for ordinal, production in enumerate(productions, 1):
        production_id = production["name"]
        if production_id in old_by_name:
            refreshed = copy.deepcopy(old_by_name[production_id])
        else:
            refreshed = copy.deepcopy(REFRESHABLE_NEW_PRODUCTIONS[production_id])
        derived = {
            "ordinal": ordinal,
            "production_id": production_id,
            "profile": production["profile"],
            "source_line": production["line"],
            "normalized_rhs": production["definition"],
            "rhs_sha256": hashlib.sha256(
                production["definition"].encode("utf-8")
            ).hexdigest(),
            "referenced_productions": references[production_id],
        }
        preserved = {
            key: value for key, value in refreshed.items() if key not in derived
        }
        refreshed = {**derived, **preserved}
        refreshed_rows.append(refreshed)

    external_rows = registry.get("external_symbol_contracts")
    if not isinstance(external_rows, list):
        raise RuntimeError("REFRESH_EXTERNAL_ROWS: not an array")
    external_by_symbol = {
        row.get("symbol"): row
        for row in external_rows
        if isinstance(row, dict) and isinstance(row.get("symbol"), str)
    }
    if (
        len(external_by_symbol) != len(external_rows)
        or set(external_by_symbol) != set(external_uses)
    ):
        raise RuntimeError(
            "REFRESH_EXTERNAL_DELTA: "
            f"registered={sorted(external_by_symbol)} "
            f"observed={sorted(external_uses)}"
        )
    registry["external_symbol_contracts"] = [
        {
            **copy.deepcopy(row),
            "used_by_productions": external_uses[row["symbol"]],
        }
        for row in external_rows
    ]
    grammar_bytes = documents["grammar_bytes"]
    registry["grammar"].update(
        {
            "path": GRAMMAR_REL,
            "bytes": len(grammar_bytes),
            "sha256": hashlib.sha256(grammar_bytes).hexdigest(),
            "production_count": len(productions),
            "external_symbol_count": len(external_uses),
        }
    )
    registry["production_rows"] = refreshed_rows
    registry["disposition_counts"] = ordered_counts(
        registry["disposition_counts"],
        [row["disposition"] for row in refreshed_rows],
        "DISPOSITION",
    )
    registry["profile_counts"] = ordered_counts(
        registry["profile_counts"],
        [row["profile"] for row in refreshed_rows],
        "PROFILE",
    )
    registry["reachability_owner_counts"] = ordered_counts(
        registry["reachability_owner_counts"],
        [row["reachability_owner"] for row in refreshed_rows],
        "REACHABILITY_OWNER",
    )
    registry_bytes = generator.json_bytes(registry)

    topology = copy.deepcopy(documents["contract"])
    topology["inputs"]["grammar"] = {
        "path": GRAMMAR_REL,
        "bytes": len(grammar_bytes),
        "sha256": hashlib.sha256(grammar_bytes).hexdigest(),
    }
    topology["inputs"]["disposition_registry"] = {
        "path": DISPOSITION_REL,
        "bytes": len(registry_bytes),
        "sha256": hashlib.sha256(registry_bytes).hexdigest(),
    }
    topology["production_set"] = {
        "count": len(name_set),
        "sha256": generator.grammar_name_digest(name_set),
    }
    external_names = set(external_uses)
    topology["external_symbol_set"].update(
        {
            "count": len(external_names),
            "sha256": generator.grammar_name_digest(external_names),
        }
    )

    by_name = {row["name"]: row for row in productions}

    def reachable(start: str) -> set[str]:
        seen: set[str] = set()
        pending = [start]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            pending.extend(set(references[current]) - seen)
        return seen

    root_sets: list[set[str]] = []
    for root_row in topology["source_roots"]:
        root_id = root_row["production_id"]
        reached = reachable(root_id)
        root_sets.append(reached)
        root_row.update(
            {
                "profile": by_name[root_id]["profile"],
                "reachable_count": len(reached),
                "reachable_sha256": generator.grammar_name_digest(reached),
            }
        )
    union = set().union(*root_sets)
    shared = set.intersection(*root_sets)
    topology["six_root_reachability"] = {
        "union": {
            "count": len(union),
            "sha256": generator.grammar_name_digest(union),
        },
        "shared": {
            "count": len(shared),
            "sha256": generator.grammar_name_digest(shared),
        },
    }
    aggregate_ids = {
        row["production_id"] for row in topology["aggregate_entry_roots"]
    }
    disposition_by_name = {
        row["production_id"]: row for row in refreshed_rows
    }
    unreachable = name_set - union
    owner_counts = Counter(
        disposition_by_name[production_id]["reachability_owner"]
        for production_id in unreachable
    )
    allowed_non_source = set(topology["non_source_reachability_owners"])
    unowned = {
        production_id
        for production_id in unreachable
        if production_id not in aggregate_ids
        and disposition_by_name[production_id]["reachability_owner"]
        not in allowed_non_source
    }
    topology["six_root_unreachable"].update(
        {
            "count": len(unreachable),
            "sha256": generator.grammar_name_digest(unreachable),
            "owner_counts": dict(sorted(owner_counts.items())),
        }
    )
    topology["unowned_orphan_count"] = len(unowned)
    allowed_edges = {
        profile: set(targets)
        for profile, targets in topology["profile_edge_policy"].items()
    }
    topology["illegal_cross_profile_edge_count"] = sum(
        by_name[target]["profile"] not in allowed_edges[by_name[source]["profile"]]
        for source, targets in references.items()
        for target in targets
    )
    generator.validate_grammar_topology(
        productions, documents["frontend"], topology, registry
    )
    topology_bytes = generator.json_bytes(topology)

    fixtures = copy.deepcopy(documents["fixtures"])
    fixtures["acceptance"]["production_count"] = len(productions)
    fixture_bytes = generator.json_bytes(fixtures)
    return {
        DISPOSITION_REL: registry_bytes,
        CONTRACT_REL: topology_bytes,
        FIXTURE_REL: fixture_bytes,
    }


def refresh_documents(root: Path, generator: Any) -> None:
    outputs = render_refreshed_documents(root, generator)
    for relative, data in outputs.items():
        generator.atomic_write(generator.safe_path(root, relative), data)


def evaluate(documents: dict[str, Any], generator: Any) -> list[str]:
    errors: list[str] = []
    contract = documents["contract"]
    fixtures = documents["fixtures"]
    expected_production_count = documents["reference_contract"]["grammar"][
        "expected_total"
    ]

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
        contract.get("production_set", {}).get("count") == expected_production_count,
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
            "production_count": expected_production_count,
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
        references, external_uses = grammar_bindings(productions)
        production_rows = documents["disposition"].get("production_rows", [])
        require(
            documents["disposition"].get("grammar")
            == {
                "path": GRAMMAR_REL,
                "bytes": len(documents["grammar_bytes"]),
                "sha256": hashlib.sha256(documents["grammar_bytes"]).hexdigest(),
                "production_count": len(productions),
                "external_symbol_count": len(external_uses),
            },
            "DISPOSITION_GRAMMAR_BINDING",
        )
        require(
            isinstance(production_rows, list)
            and len(production_rows) == len(productions)
            and all(
                row.get("ordinal") == ordinal
                and row.get("production_id") == production["name"]
                and row.get("profile") == production["profile"]
                and row.get("source_line") == production["line"]
                and row.get("normalized_rhs") == production["definition"]
                and row.get("rhs_sha256")
                == hashlib.sha256(
                    production["definition"].encode("utf-8")
                ).hexdigest()
                and row.get("referenced_productions")
                == references[production["name"]]
                for ordinal, (row, production) in enumerate(
                    zip(production_rows, productions), 1
                )
            ),
            "DISPOSITION_PRODUCTION_PROJECTION",
        )
        require(
            documents["disposition"].get("disposition_counts")
            == dict(
                Counter(row.get("disposition") for row in production_rows)
            ),
            "DISPOSITION_COUNTS",
        )
        require(
            documents["disposition"].get("profile_counts")
            == dict(Counter(row.get("profile") for row in production_rows)),
            "DISPOSITION_PROFILE_COUNTS",
        )
        require(
            documents["disposition"].get("reachability_owner_counts")
            == dict(
                Counter(
                    row.get("reachability_owner") for row in production_rows
                )
            ),
            "DISPOSITION_REACHABILITY_OWNER_COUNTS",
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
            "production_count": expected_production_count,
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
    require(
        governance.get("post_closure_projection_addition_count") == 1
        and governance.get("post_closure_projection_gap_id")
        == "IR-OWN-P1-018",
        "GOVERNANCE_POST_CLOSURE_PROJECTION",
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
            "LibrarySourceFile ::= ModuleDecl? LibrarySourceItem* EOF_TOKEN ;",
            "LibrarySourceFile ::= ModuleDecl? EOF_TOKEN ;",
            1,
        )
        disposition_row(docs, "LibrarySourceFile")["referenced_productions"] = [
            "EOF_TOKEN",
            "ModuleDecl",
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
    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "refresh only the bounded grammar disposition, topology, and fixture "
            "projections before validating them"
        ),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    documents: dict[str, Any] = {}
    try:
        generator = load_generator(root)
        if args.refresh:
            refresh_documents(root, generator)
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
    topology = documents.get("contract", {})
    production_count = topology.get("production_set", {}).get("count", 0)
    reachability = topology.get("six_root_reachability", {})
    unreachable = topology.get("six_root_unreachable", {})
    receipt = {
        "schema": "deeplus.r27-grammar-topology-validation-receipt/r1",
        "result": result,
        "evidence_level": "E2_STATIC_CLOSURE",
        "check_scope": "R27_GRAMMAR_TOPOLOGY_CLOSURE_EXACT",
        "check_count": len(checks),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "production_count": documents.get("contract", {}).get("production_set", {}).get("count", 0),
        "declared_reference_binding_count": len(documents.get("disposition", {}).get("production_rows", [])),
        "external_symbol_count": 40,
        "source_root_count": 6,
        "six_root_union_count": documents.get("contract", {}).get("six_root_reachability", {}).get("union", {}).get("count", 0),
        "six_root_shared_count": documents.get("contract", {}).get("six_root_reachability", {}).get("shared", {}).get("count", 0),
        "six_root_unreachable_count": documents.get("contract", {}).get("six_root_unreachable", {}).get("count", 0),
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
        "post_closure_projection_addition_count": 1,
        "post_closure_projection_gap_id": "IR-OWN-P1-018",
        "new_source_spelling_count": 0,
        "semantic_change_count": 0,
        "product_execution": "NOT_RUN",
        "errors": errors,
    }
    if args.refresh:
        receipt["mode"] = "refresh"
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
