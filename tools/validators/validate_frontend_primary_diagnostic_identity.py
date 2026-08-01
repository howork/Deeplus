#!/usr/bin/env python3
"""Validate the R26 frontend/no-go primary diagnostic identity closure."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/frontend-primary-diagnostic-identity-r1.json"
FIXTURE_REL = "tests/fixtures/current/frontend-primary-diagnostic-identity-r1.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"

EXPECTED_FAMILIES = [
    {
        "family_id": "NAMED_REST_TRIPLE_STAR_CONTEXT",
        "primary_diagnostic":
            "TRIPLE_STAR_ONLY_FOR_NAMED_REST_PARAMETER_OR_TYPE_RESIDUE",
        "stage": "PARSER",
        "frontend_fix": "***",
        "frontend_action": "BIND_EXISTING_ACTIVE_ID",
        "no_go_rejection_ids": ["NG-NAMED-REST-DOUBLE-STAR"],
        "current_ast_created": False,
    },
    {
        "family_id": "OPTION_BARE_NONE_CONTEXT",
        "primary_diagnostic": "OPTION_BARE_NONE_REMOVED",
        "stage": "CHECKER",
        "frontend_fix": "::none",
        "frontend_action": "BIND_EXISTING_ACTIVE_ID",
        "no_go_rejection_ids": [],
        "current_ast_created": True,
    },
    {
        "family_id": "NONADMITTED_OPERATOR_CONTEXT",
        "primary_diagnostic": "OPERATOR_NOT_CONFORMANCE_OVERLOADABLE",
        "stage": "CHECKER",
        "frontend_fix": (
            "use one of the exact 13 admitted roles or a named Trait method/API; "
            "assignment, range, power, bitwise, logical, membership, type "
            "identity, and arbitrary custom glyph hooks remain closed"
        ),
        "frontend_action":
            "REMOVE_REDUNDANT_UNBOUND_PLACEHOLDER_USE_EXISTING_ROW",
        "no_go_rejection_ids": [],
        "current_ast_created": True,
    },
    {
        "family_id": "EMPTY_SLICE_RANGE_CONTEXT",
        "primary_diagnostic": "SLICE_EMPTY_RANGE_FORBIDDEN_USE_STAR",
        "stage": "PARSER",
        "frontend_fix": (
            "write both bounds with .. or ..<; use * only for a NumericArray "
            "full axis"
        ),
        "frontend_action": "BIND_EXISTING_ACTIVE_ID",
        "no_go_rejection_ids": [],
        "current_ast_created": False,
    },
    {
        "family_id": "NONCURRENT_LAZY_INTRODUCER_CONTEXT",
        "primary_diagnostic": "LAZY_BINDING_AT_MARKER_REMOVED_USE_HASH",
        "stage": "PARSER",
        "frontend_fix": "let#lazy",
        "frontend_action": "BIND_EXISTING_ACTIVE_ID",
        "no_go_rejection_ids": ["NG-R51B-LAZY-AT"],
        "current_ast_created": False,
    },
    {
        "family_id": "UNIT_MIDDLE_DOT_CONTEXT",
        "primary_diagnostic": "UNIT_MIDDLE_DOT_REMOVED_USE_STAR",
        "stage": "PARSER",
        "frontend_fix": "*",
        "frontend_action": "BIND_EXISTING_ACTIVE_ID",
        "no_go_rejection_ids": ["NG-R51B-UNIT-MIDDLE-DOT"],
        "current_ast_created": False,
    },
]

EXPECTED_PRECEDENCE_IDS = [f"R26-PREC-{index:03d}" for index in range(1, 7)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_chunk_rows(root: Path, pattern: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob(pattern)):
        value = load_json(path)
        if not isinstance(value, list):
            raise ValueError(f"chunk is not an array: {path}")
        rows.extend(value)
    return rows


def load_documents(root: Path) -> dict[str, Any]:
    return {
        "contract": load_json(root / CONTRACT_REL),
        "fixtures": load_json(root / FIXTURE_REL),
        "frontend": load_json(root / FRONTEND_REL),
        "diagnostics": load_chunk_rows(
            root, "spec/diagnostics/catalog/chunks/*.json"
        ),
        "no_go": load_chunk_rows(
            root, "spec/compatibility/no-go/chunks/*.json"
        ),
    }


def evaluate(documents: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = documents["contract"]
    fixtures = documents["fixtures"]
    frontend = documents["frontend"]
    diagnostics = documents["diagnostics"]
    no_go = documents["no_go"]

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(
        contract.get("schema")
        == "deeplus.frontend-primary-diagnostic-identity-contract/r1",
        "CONTRACT_SCHEMA",
    )
    require(
        contract.get("baseline", {}).get("commit")
        == "3f0077dd8f021718dc87b3b239f417e5d3f770a6",
        "CONTRACT_BASELINE",
    )
    policy = contract.get("identity_policy", {})
    require(policy.get("frontend_binding_count") == 6, "CONTRACT_FRONTEND_COUNT")
    require(policy.get("frontend_id_insert_count") == 5, "CONTRACT_FRONTEND_INSERT_COUNT")
    require(
        policy.get("frontend_redundant_placeholder_removal_count") == 1,
        "CONTRACT_FRONTEND_REMOVAL_COUNT",
    )
    require(policy.get("frontend_diagnostic_row_count") == 39, "CONTRACT_FRONTEND_ROW_COUNT")
    require(policy.get("no_go_binding_count") == 3, "CONTRACT_NO_GO_COUNT")
    require(policy.get("binding_family_count") == 6, "CONTRACT_FAMILY_COUNT")
    require(policy.get("new_diagnostic_id_count") == 0, "CONTRACT_NEW_ID_COUNT")
    require(policy.get("new_source_spelling_count") == 0, "CONTRACT_NEW_SURFACE")
    require(policy.get("semantic_change_count") == 0, "CONTRACT_SEMANTIC_CHANGE")
    families = contract.get("binding_families")
    require(isinstance(families, list), "CONTRACT_FAMILIES_ARRAY")
    if not isinstance(families, list):
        families = []
    family_ids = [row.get("family_id") for row in families if isinstance(row, dict)]
    require(len(family_ids) == len(set(family_ids)) == 6, "CONTRACT_FAMILY_UNIQUE")
    require(families == EXPECTED_FAMILIES, "CONTRACT_FAMILY_EXACT")

    diagnostic_ids = [
        row.get("diagnostic_id") for row in diagnostics if isinstance(row, dict)
    ]
    diagnostic_counts = Counter(diagnostic_ids)
    registry = {
        row["diagnostic_id"]: row
        for row in diagnostics
        if isinstance(row, dict) and isinstance(row.get("diagnostic_id"), str)
    }
    require(
        all(count == 1 for count in diagnostic_counts.values()),
        "REGISTRY_DIAGNOSTIC_UNIQUE",
    )

    frontend_rows = frontend.get("diagnostics")
    require(isinstance(frontend_rows, list), "FRONTEND_DIAGNOSTICS_ARRAY")
    if not isinstance(frontend_rows, list):
        frontend_rows = []
    require(len(frontend_rows) == 39, "FRONTEND_DIAGNOSTIC_COUNT")
    require(
        all(isinstance(row.get("id"), str) and row["id"] for row in frontend_rows),
        "FRONTEND_MISSING_ID",
    )
    frontend_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in frontend_rows:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            frontend_by_id.setdefault(row["id"], []).append(row)

    no_go_by_id = {
        row.get("rejection_id"): row for row in no_go if isinstance(row, dict)
    }
    require(
        all(
            isinstance(row.get("primary_diagnostic"), str)
            and row["primary_diagnostic"]
            for row in no_go
            if isinstance(row, dict)
        ),
        "NO_GO_MISSING_PRIMARY",
    )

    for family in EXPECTED_FAMILIES:
        diagnostic_id = family["primary_diagnostic"]
        target = registry.get(diagnostic_id)
        require(target is not None, f"REGISTRY_TARGET:{diagnostic_id}")
        if target is not None:
            require(
                target.get("diagnostic_maturity") == "active"
                and target.get("diagnostic_status") == "active"
                and target.get("diagnostic_class") == "current_source"
                and target.get("emission_domain") == "source"
                and target.get("product_support") == "NOT_RUN",
                f"REGISTRY_ACTIVE_PROFILE:{diagnostic_id}",
            )
            require(
                str(target.get("stage", "")).upper() == family["stage"],
                f"REGISTRY_STAGE:{diagnostic_id}",
            )
        bound_rows = frontend_by_id.get(diagnostic_id, [])
        require(len(bound_rows) == 1, f"FRONTEND_BINDING:{diagnostic_id}")
        if len(bound_rows) == 1:
            require(
                bound_rows[0].get("stage") == family["stage"],
                f"FRONTEND_STAGE:{diagnostic_id}",
            )
            require(
                bound_rows[0].get("fix") == family["frontend_fix"],
                f"FRONTEND_FIX:{diagnostic_id}",
            )
        for rejection_id in family["no_go_rejection_ids"]:
            row = no_go_by_id.get(rejection_id)
            require(row is not None, f"NO_GO_ROW:{rejection_id}")
            if row is not None:
                require(
                    row.get("primary_diagnostic") == diagnostic_id,
                    f"NO_GO_BINDING:{rejection_id}",
                )
                require(
                    str(row.get("recognition_stage", "")).upper()
                    == family["stage"],
                    f"NO_GO_STAGE:{rejection_id}",
                )
                require(
                    row.get("current_ast_created")
                    is family["current_ast_created"],
                    f"NO_GO_AST:{rejection_id}",
                )

    precedence = contract.get("diagnostic_precedence")
    require(isinstance(precedence, list), "PRECEDENCE_ARRAY")
    if not isinstance(precedence, list):
        precedence = []
    require(
        [row.get("rule_id") for row in precedence if isinstance(row, dict)]
        == EXPECTED_PRECEDENCE_IDS,
        "PRECEDENCE_EXACT_ORDER",
    )
    require(
        all(
            isinstance(row.get("winner"), str)
            and isinstance(row.get("loser"), str)
            and isinstance(row.get("condition"), str)
            for row in precedence
            if isinstance(row, dict)
        ),
        "PRECEDENCE_COMPLETE",
    )

    require(
        fixtures.get("schema")
        == "deeplus.frontend-primary-diagnostic-identity-fixtures/r1",
        "FIXTURE_SCHEMA",
    )
    require(fixtures.get("contract") == CONTRACT_REL, "FIXTURE_CONTRACT_BINDING")
    cases = fixtures.get("cases")
    require(isinstance(cases, list), "FIXTURE_CASES_ARRAY")
    if not isinstance(cases, list):
        cases = []
    case_ids = [row.get("case_id") for row in cases if isinstance(row, dict)]
    require(len(case_ids) == len(set(case_ids)) == 18, "FIXTURE_CASE_COUNT")
    require(
        Counter(row.get("class") for row in cases if isinstance(row, dict))
        == {"positive": 6, "boundary": 6, "negative": 6},
        "FIXTURE_CLASS_COUNTS",
    )
    for row in cases:
        if not isinstance(row, dict):
            errors.append("FIXTURE_CASE_OBJECT")
            continue
        diagnostic_id = row.get("expected_primary_diagnostic_or_null")
        stage = row.get("expected_stage_or_null")
        require(
            (diagnostic_id is None and stage is None)
            or (
                isinstance(diagnostic_id, str)
                and diagnostic_id in registry
                and isinstance(stage, str)
                and str(registry[diagnostic_id].get("stage", "")).upper() == stage
            ),
            f"FIXTURE_ORACLE:{row.get('case_id')}",
        )
    mutations = fixtures.get("mutations")
    require(isinstance(mutations, list), "MUTATION_ARRAY")
    if not isinstance(mutations, list):
        mutations = []
    require(
        [row.get("mutation_id") for row in mutations if isinstance(row, dict)]
        == [f"R26-MUT-{index:03d}" for index in range(1, 7)]
        and all(row.get("expected_validator_result") == "REJECT" for row in mutations),
        "MUTATION_SPEC_EXACT",
    )

    governance = contract.get("governance", {})
    require(governance.get("gap_id") == "IR-FE-P1-035", "GOVERNANCE_GAP")
    require(governance.get("semantic_p0") == 0, "GOVERNANCE_P0")
    require(governance.get("feature_p1") == "22_OPEN_UNCHANGED", "GOVERNANCE_P1")
    require(governance.get("m13_actions") == "4_OPEN_UNCHANGED", "GOVERNANCE_M13")
    require(governance.get("product_lanes") == "15/15_NOT_RUN", "GOVERNANCE_PRODUCT")
    require(governance.get("github_mutation") == 0, "GOVERNANCE_GITHUB")
    require(fixtures.get("product_execution") == "NOT_RUN", "GOVERNANCE_FIXTURE_PRODUCT")
    return errors


def mutation_receipts(documents: dict[str, Any]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []

    def run(mutation_id: str, mutate, expected_prefix: str) -> None:
        candidate = copy.deepcopy(documents)
        mutate(candidate)
        errors = evaluate(candidate)
        rejected = any(error.startswith(expected_prefix) for error in errors)
        receipts.append(
            {
                "mutation_id": mutation_id,
                "result": "REJECTED" if rejected else "SURVIVED",
                "expected_error_prefix": expected_prefix,
                "observed_errors": errors,
            }
        )

    run(
        "R26-MUT-001",
        lambda docs: docs["frontend"]["diagnostics"][11].pop("id"),
        "FRONTEND_MISSING_ID",
    )
    run(
        "R26-MUT-002",
        lambda docs: docs["frontend"]["diagnostics"][11].update(
            {"stage": "CHECKER"}
        ),
        "FRONTEND_STAGE",
    )
    run(
        "R26-MUT-003",
        lambda docs: docs["diagnostics"].__setitem__(
            slice(None),
            [
                row
                for row in docs["diagnostics"]
                if row.get("diagnostic_id")
                != "SLICE_EMPTY_RANGE_FORBIDDEN_USE_STAR"
            ],
        ),
        "REGISTRY_TARGET",
    )
    run(
        "R26-MUT-004",
        lambda docs: next(
            row
            for row in docs["no_go"]
            if row.get("rejection_id") == "NG-R51B-LAZY-AT"
        ).update({"primary_diagnostic": "SOURCE_TRAILING_TOKENS"}),
        "NO_GO_BINDING",
    )
    run(
        "R26-MUT-005",
        lambda docs: docs["contract"]["binding_families"].append(
            copy.deepcopy(docs["contract"]["binding_families"][0])
        ),
        "CONTRACT_FAMILY",
    )
    run(
        "R26-MUT-006",
        lambda docs: docs["contract"]["governance"].update(
            {"product_lanes": "15/15_PASS"}
        ),
        "GOVERNANCE_PRODUCT",
    )
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        documents = load_documents(root)
        errors = evaluate(documents)
        mutations = mutation_receipts(documents)
    except Exception as exc:  # noqa: BLE001
        errors = [f"VALIDATOR_EXCEPTION:{type(exc).__name__}:{exc}"]
        mutations = []

    mutation_pass = (
        len(mutations) == 6
        and all(row["result"] == "REJECTED" for row in mutations)
    )
    checks = [
        {
            "check_id": "R26_CONTRACT_EXACT",
            "pass": not any(error.startswith("CONTRACT_") for error in errors),
        },
        {
            "check_id": "R26_FRONTEND_BINDINGS_EXACT_6",
            "pass": not any(error.startswith("FRONTEND_") for error in errors),
        },
        {
            "check_id": "R26_NO_GO_BINDINGS_EXACT_3",
            "pass": not any(error.startswith("NO_GO_") for error in errors),
        },
        {
            "check_id": "R26_ACTIVE_REGISTRY_STAGE_BINDING",
            "pass": not any(error.startswith("REGISTRY_") for error in errors),
        },
        {
            "check_id": "R26_PRECEDENCE_EXACT_6",
            "pass": not any(error.startswith("PRECEDENCE_") for error in errors),
        },
        {
            "check_id": "R26_ACCEPTANCE_CASES_EXACT_18",
            "pass": not any(error.startswith("FIXTURE_") for error in errors),
        },
        {
            "check_id": "R26_MUTATIONS_EXACT_6",
            "pass": mutation_pass,
        },
        {
            "check_id": "R26_GOVERNANCE_FENCE",
            "pass": not any(error.startswith("GOVERNANCE_") for error in errors),
        },
    ]
    result = "PASS" if not errors and all(row["pass"] for row in checks) else "FAIL"
    receipt = {
        "schema": "deeplus.r26-frontend-primary-diagnostic-validation-receipt/r1",
        "result": result,
        "evidence_level": "E2_STATIC_CLOSURE",
        "check_scope": "R26_PRIMARY_DIAGNOSTIC_IDENTITY_EXACT",
        "check_count": len(checks),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "frontend_binding_count": 6,
        "no_go_binding_count": 3,
        "binding_family_count": 6,
        "acceptance_case_count": 18,
        "mutation_count": len(mutations),
        "rejected_mutation_count": sum(
            row["result"] == "REJECTED" for row in mutations
        ),
        "mutations": mutations,
        "new_diagnostic_id_count": 0,
        "semantic_change_count": 0,
        "product_execution": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
