#!/usr/bin/env python3
"""Validate the R99 scanner/Pratt authority repair and its mutations."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any


class ValidationError(RuntimeError):
    pass


def require(condition: bool, code: str, detail: Any = None) -> None:
    if not condition:
        suffix = "" if detail is None else f": {detail}"
        raise ValidationError(f"{code}{suffix}")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "R99_JSON_OBJECT_REQUIRED", path)
    return value


def row_by_id(rows: list[dict[str, Any]], row_id: str) -> dict[str, Any]:
    found = [row for row in rows if row.get("id") == row_id]
    require(len(found) == 1, "R99_EXACT_ROW_ID", row_id)
    return found[0]


def validate_model(
    contract: dict[str, Any],
    scanner: dict[str, Any],
    contexts: dict[str, Any],
    pratt: dict[str, Any],
    frontend: dict[str, Any],
    fixture: dict[str, Any],
    dpg_text: str,
) -> dict[str, int]:
    require(
        contract.get("schema")
        == "deeplus.parser-scanner-pratt-authority-r99/r1",
        "R99_CONTRACT_SCHEMA",
    )
    dispositions = contract.get("gap_dispositions", [])
    require(len(dispositions) == 5, "R99_GAP_DISPOSITION_COUNT")
    require(
        all(row.get("disposition", "").startswith("CLOSED_BY_") for row in dispositions),
        "R99_GAP_DISPOSITION_STATE",
    )

    terminals = scanner.get("syntax_terminal_registry", [])
    spellings = [row.get("spelling") for row in terminals]
    require(len(terminals) == 201, "R99_SCANNER_TERMINAL_COUNT", len(terminals))
    require(len(spellings) == len(set(spellings)), "R99_SCANNER_DUPLICATE_SPELLING")
    semicolon = [row for row in terminals if row.get("spelling") == ";"]
    require(
        len(semicolon) == 1
        and semicolon[0].get("scanner_kind") == "SEMICOLON"
        and semicolon[0].get("classification") == "FIXED_GLYPH",
        "R99_SCANNER_SEMICOLON_ROW",
    )
    require("';'" in dpg_text, "R99_DPG_SEMICOLON_USE")

    adapter = scanner.get("parser_terminal_adapter_registry", {})
    aggregate_rows = adapter.get("aggregate_rows", [])
    aggregate_terminals = [row.get("parser_terminal") for row in aggregate_rows]
    expected_aggregate = [
        "NUMERIC_LITERAL",
        "DECIMAL_INTEGER",
        "HARD_KEYWORD",
        "EOF_TOKEN",
        "SHEBANG",
    ]
    require(aggregate_terminals == expected_aggregate, "R99_ADAPTER_EXACT_ORDER")
    require(
        all(row.get("emits_additional_physical_token") is False for row in aggregate_rows),
        "R99_ADAPTER_DUPLICATE_EMISSION",
    )
    require(adapter.get("aggregate_match_emits_token") is False, "R99_ADAPTER_EMITS_TOKEN")
    require(
        adapter.get("physical_token_emission_per_source_span") == 1,
        "R99_ADAPTER_PHYSICAL_TOKEN_CARDINALITY",
    )
    closed_adapter = contexts.get("closed_external_bindings", {}).get(
        "scanner_outcome_adapter", {}
    )
    require(
        closed_adapter.get("pointer") == "/parser_terminal_adapter_registry"
        and closed_adapter.get("physical_token_duplication_count") == 0,
        "R99_CONTEXT_ADAPTER_BINDING",
    )
    scanner_outcomes = set(
        contexts.get("closed_external_bindings", {}).get("scanner_outcomes", [])
    )
    resolved_outcomes = set(adapter.get("physical_token_passthrough", [])) | set(
        aggregate_terminals
    )
    require(scanner_outcomes == resolved_outcomes, "R99_ADAPTER_OUTCOME_TOTALITY", {
        "missing": sorted(scanner_outcomes - resolved_outcomes),
        "extra": sorted(resolved_outcomes - scanner_outcomes),
    })

    range_row = row_by_id(pratt.get("expression_led", []), "range")
    range_tokens = [parts[0] for parts in range_row.get("tokens", [])]
    require(range_tokens == ["..", "..<", "..."], "R99_RANGE_EXACT_TOKENS")
    require(
        "required" in range_row.get("rhs", "")
        and "absent" in range_row.get("rhs", ""),
        "R99_RANGE_RHS_PARTITION",
    )
    require(
        "Range owner" in range_row.get("step_suffix", ""),
        "R99_RANGE_STEP_OWNER",
    )
    require(
        range_row.get("one_sided_trailing_expression", "").startswith("reject"),
        "R99_RANGE_ONE_SIDED_TRAILING_REJECT",
    )
    frontend_range = row_by_id(
        frontend.get("pratt", {}).get("expression", {}).get("operators", []),
        "range",
    )
    require(
        [parts[0] for parts in frontend_range.get("tokens", [])] == range_tokens,
        "R99_RANGE_FRONTEND_PARITY",
    )
    require(
        frontend.get("range_index_frontend_contract", {})
        .get("range", {})
        .get("step_suffix_owner")
        == "Range parselet, not ternary",
        "R99_RANGE_OWNER_FRONTEND_PARITY",
    )

    primary = pratt.get("primary_dispatch", [])
    measure = row_by_id(primary, "measure_literal")
    literal_index = next(i for i, row in enumerate(primary) if row.get("id") == "literal")
    measure_index = next(
        i for i, row in enumerate(primary) if row.get("id") == "measure_literal"
    )
    require(measure_index < literal_index, "R99_MEASURE_PROBE_ORDER")
    require(measure.get("ast_target") == "MeasureLiteralExpr", "R99_MEASURE_AST")
    require(
        "zero tokens" in measure.get("probe_failure", "")
        and "zero diagnostics" in measure.get("probe_failure", ""),
        "R99_MEASURE_TRANSACTIONAL_FALLBACK",
    )
    separated_measure = measure.get("separated_measure_lookahead", {})
    require(
        separated_measure.get("trigger")
        == "one physical INTEGER_LITERAL or FLOAT_LITERAL followed by nonempty trivia and then ["
        and separated_measure.get("probe")
        == "transactionally parse one complete UnitExpr followed by ] without type information",
        "R99_MEASURE_SEPARATED_LOOKAHEAD",
    )
    require(
        "UNIT_LITERAL_BRACKET_MUST_BE_ATTACHED"
        in separated_measure.get("success", "")
        and "one recovery CST error node" in separated_measure.get("success", "")
        and "zero canonical MeasureLiteralExpr or IndexExpr AST nodes"
        in separated_measure.get("success", ""),
        "R99_MEASURE_SEPARATED_SUCCESS_RECOVERY",
    )
    require(
        "zero bracket or trivia tokens" in separated_measure.get("failure", "")
        and "zero diagnostics" in separated_measure.get("failure", "")
        and separated_measure.get("non_unit_examples") == ["13[0]", "13 [0]"],
        "R99_MEASURE_SEPARATED_TRANSACTIONAL_FALLBACK",
    )
    index_row = row_by_id(pratt.get("structured_postfix", []), "index")
    require(
        "Measure structured-primary probe" in index_row.get("measure_boundary", "")
        and "separated UnitExpr lookahead"
        in index_row.get("measure_boundary", ""),
        "R99_MEASURE_INDEX_BOUNDARY",
    )
    frontend_measure = (
        frontend.get("pratt", {})
        .get("closed_parse_goal_contract", {})
        .get("measure_literal_primary", {})
    )
    require(
        frontend_measure.get("success") == "MeasureLiteralExpr"
        and frontend_measure.get("type_information_used") is False,
        "R99_MEASURE_FRONTEND_PARITY",
    )
    frontend_separated = frontend_measure.get("separated_measure_lookahead", {})
    contract_separated = contract.get("measure_contract", {}).get(
        "separated_measure_lookahead", {}
    )
    require(
        frontend_separated.get("trigger") == separated_measure.get("trigger")
        == contract_separated.get("trigger")
        and frontend_separated.get("probe") == separated_measure.get("probe")
        == contract_separated.get("probe"),
        "R99_MEASURE_SEPARATED_TRIGGER_PARITY",
    )
    require(
        frontend_separated.get("success_diagnostic")
        == contract_separated.get("success_diagnostic")
        == "UNIT_LITERAL_BRACKET_MUST_BE_ATTACHED"
        and contract_separated.get("success_recovery_cst_error_node_count") == 1
        and contract_separated.get("success_canonical_ast_count") == 0
        and contract_separated.get("failure_bracket_or_trivia_token_consumption") == 0
        and contract_separated.get("failure_diagnostic_count") == 0
        and contract_separated.get("failure_owner") == "IndexExpr"
        and frontend_separated.get("non_unit_examples")
        == contract_separated.get("non_unit_examples")
        == ["13[0]", "13 [0]"],
        "R99_MEASURE_SEPARATED_OUTCOME_PARITY",
    )

    sign = row_by_id(pratt.get("expression_nud", []), "numeric_prefix_sign")
    boundary = sign.get("semantic_boundary", "")
    require("never conformance" not in boundary, "R99_UNARY_INTRINSIC_ONLY_STALE")
    require(
        "intrinsic-reserved" in boundary
        and "UnaryPlus" in boundary
        and "UnaryMinus" in boundary
        and "DIRECT_GLOBAL" in boundary,
        "R99_UNARY_PARSE_STATIC_SELECTION",
    )
    frontend_sign = row_by_id(
        frontend.get("pratt", {}).get("expression", {}).get("operators", []),
        "numeric_prefix_sign",
    )
    require(
        "intrinsic-reserved" in frontend_sign.get("semantic_boundary", "")
        and "UnaryPlus" in frontend_sign.get("semantic_boundary", "")
        and "UnaryMinus" in frontend_sign.get("semantic_boundary", ""),
        "R99_UNARY_FRONTEND_PARITY",
    )
    require(
        frontend.get("scanner", {})
        .get("complete_token_lexical_goal_contract", {})
        .get("syntax_terminal_count")
        == 201,
        "R99_SCANNER_FRONTEND_COUNT",
    )

    cases = fixture.get("cases", [])
    counts = Counter(row.get("kind", "").lower() for row in cases)
    expected_counts = fixture.get("counts", {})
    require(len(cases) == expected_counts.get("total") == 17, "R99_FIXTURE_TOTAL")
    require(
        counts
        == Counter(
            {
                "positive": expected_counts.get("positive"),
                "boundary": expected_counts.get("boundary"),
                "reject": expected_counts.get("reject"),
            }
        ),
        "R99_FIXTURE_COUNTS",
    )
    ids = [row.get("id") for row in cases]
    require(len(ids) == len(set(ids)), "R99_FIXTURE_DUPLICATE_ID")
    semicolon_case = row_by_id(cases, "R99-BOUND-SEMICOLON-001")
    require(
        semicolon_case.get("source", "").count(";")
        == semicolon_case.get("expected_physical_token_count")
        == 2
        and semicolon_case.get("expected") == "TWO_SEMICOLON_TOKENS"
        and semicolon_case.get("expected_cst_roles")
        == ["INTERNAL_ROW_SEPARATOR", "TRAILING_ROW_BOUNDARY"],
        "R99_SEMICOLON_FIXTURE_EXACT_ORACLE",
    )
    require(
        row_by_id(cases, "R99-REJECT-MEASURE-001").get("source") == "13 [cm]"
        and row_by_id(cases, "R99-REJECT-MEASURE-001").get("expected")
        == "UNIT_LITERAL_BRACKET_MUST_BE_ATTACHED"
        and row_by_id(cases, "R99-BOUND-MEASURE-002").get("source") == "13[0]"
        and row_by_id(cases, "R99-BOUND-MEASURE-002").get("expected")
        == "IndexExpr_AFTER_ATTACHED_UNITEXPR_PROBE_FAILURE"
        and row_by_id(cases, "R99-BOUND-MEASURE-003").get("source") == "13 [0]"
        and row_by_id(cases, "R99-BOUND-MEASURE-003").get("expected")
        == "IndexExpr_AFTER_SEPARATED_UNITEXPR_PROBE_FAILURE",
        "R99_MEASURE_FIXTURE_EXACT_ORACLE",
    )
    require(
        contract.get("authority_fence", {}).get("feature_p1")
        == "22_OPEN_UNCHANGED"
        and contract.get("authority_fence", {}).get("product_lanes")
        == "15_OF_15_NOT_RUN"
        and fixture.get("product_execution") == "NOT_RUN",
        "R99_AUTHORITY_FENCE",
    )

    return {
        "terminal_count": len(terminals),
        "adapter_count": len(aggregate_rows),
        "range_surface_count": len(range_tokens),
        "acceptance_case_count": len(cases),
        "gap_disposition_count": len(dispositions),
    }


def run_mutations(documents: dict[str, Any], dpg_text: str) -> int:
    mutations: list[tuple[str, str, Any]] = []

    scanner = copy.deepcopy(documents["scanner"])
    scanner["syntax_terminal_registry"] = [
        row for row in scanner["syntax_terminal_registry"] if row.get("spelling") != ";"
    ]
    mutations.append(("R99-MUT-SEMICOLON-MISSING", "scanner", scanner))

    scanner = copy.deepcopy(documents["scanner"])
    scanner["parser_terminal_adapter_registry"]["aggregate_match_emits_token"] = True
    mutations.append(("R99-MUT-ADAPTER-DUPLICATE-EMISSION", "scanner", scanner))

    scanner = copy.deepcopy(documents["scanner"])
    scanner["parser_terminal_adapter_registry"]["aggregate_rows"].pop()
    mutations.append(("R99-MUT-ADAPTER-OUTCOME-MISSING", "scanner", scanner))

    pratt = copy.deepcopy(documents["pratt"])
    row_by_id(pratt["expression_led"], "range")["tokens"] = [[".."], ["..<"]]
    mutations.append(("R99-MUT-RANGE-ELLIPSIS-MISSING", "pratt", pratt))

    pratt = copy.deepcopy(documents["pratt"])
    row_by_id(pratt["expression_led"], "range")["rhs"] = "required for every form"
    mutations.append(("R99-MUT-RANGE-ELLIPSIS-HAS-RHS", "pratt", pratt))

    pratt = copy.deepcopy(documents["pratt"])
    row_by_id(pratt["expression_led"], "range").pop("step_suffix")
    mutations.append(("R99-MUT-RANGE-STEP-OWNER-MISSING", "pratt", pratt))

    pratt = copy.deepcopy(documents["pratt"])
    rows = pratt["primary_dispatch"]
    measure = rows.pop(next(i for i, row in enumerate(rows) if row.get("id") == "measure_literal"))
    literal = next(i for i, row in enumerate(rows) if row.get("id") == "literal")
    rows.insert(literal + 1, measure)
    mutations.append(("R99-MUT-MEASURE-AFTER-LITERAL", "pratt", pratt))

    pratt = copy.deepcopy(documents["pratt"])
    row_by_id(pratt["primary_dispatch"], "measure_literal").pop(
        "separated_measure_lookahead"
    )
    mutations.append(("R99-MUT-MEASURE-SEPARATED-PROBE-MISSING", "pratt", pratt))

    fixture = copy.deepcopy(documents["fixture"])
    row_by_id(fixture["cases"], "R99-BOUND-SEMICOLON-001")[
        "expected_physical_token_count"
    ] = 4
    mutations.append(("R99-MUT-SEMICOLON-FIXTURE-ORACLE", "fixture", fixture))

    pratt = copy.deepcopy(documents["pratt"])
    row_by_id(pratt["expression_nud"], "numeric_prefix_sign")[
        "semantic_boundary"
    ] = "language-reserved numeric sign; never conformance lookup"
    mutations.append(("R99-MUT-UNARY-INTRINSIC-ONLY", "pratt", pratt))

    rejected = 0
    for mutation_id, key, value in mutations:
        current = {name: copy.deepcopy(doc) for name, doc in documents.items()}
        current[key] = value
        try:
            validate_model(
                current["contract"],
                current["scanner"],
                current["contexts"],
                current["pratt"],
                current["frontend"],
                current["fixture"],
                dpg_text,
            )
        except ValidationError:
            rejected += 1
        else:
            raise ValidationError(f"R99_MUTATION_NOT_REJECTED: {mutation_id}")
    require(rejected == len(mutations) == 10, "R99_MUTATION_COUNT", rejected)
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    documents = {
        "contract": read_json(root / "spec/contracts/parser-scanner-pratt-authority-r99.json"),
        "scanner": read_json(root / "spec/contracts/complete-token-lexical-goal-contract-r1.json"),
        "contexts": read_json(root / "spec/grammar/deeplus.parser-contexts.json"),
        "pratt": read_json(root / "spec/contracts/closed-pratt-parse-goal-contract-r1.json"),
        "frontend": read_json(root / "spec/frontend/frontend-model.json"),
        "fixture": read_json(root / "tests/fixtures/current/parser-scanner-pratt-authority-r99.json"),
    }
    dpg_text = (root / "spec/grammar/deeplus.dpg").read_text(encoding="utf-8")
    metrics = validate_model(
        documents["contract"],
        documents["scanner"],
        documents["contexts"],
        documents["pratt"],
        documents["frontend"],
        documents["fixture"],
        dpg_text,
    )
    mutation_count = run_mutations(documents, dpg_text) if args.mutations else 0
    print(
        json.dumps(
            {
                "schema": "deeplus.parser-scanner-pratt-authority-r99-validation/r1",
                "result": "PASS",
                "evidence_level": "E2_STATIC_MUTATION_BACKED",
                "metrics": metrics,
                "mutation_count": mutation_count,
                "product_execution": "NOT_RUN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, ValueError, KeyError, StopIteration) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, sort_keys=True))
        raise SystemExit(1)
