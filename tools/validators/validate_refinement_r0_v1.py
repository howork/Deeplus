#!/usr/bin/env python3
"""Validate the bounded RefinementR0V1 design and reference proof profile."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/refinement-r0-calculus-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/refinement-r0-calculus-v1.schema.json"
FORMULA_SCHEMA_REL = "schemas/language/refinement-r0-formula-v1.schema.json"
QUERY_SCHEMA_REL = "schemas/language/refinement-r0-query-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/refinement-r0-calculus-v1.json"
GUARD_SCHEMA_REL = "schemas/language/guard-summary-v1.schema.json"
GUARD_DESCRIPTOR_SCHEMA_REL = "schemas/language/guard-refinement-predicate-descriptor.schema.json"
GUARD_CONTRACT_REL = "spec/contracts/guard-refinement-summary.json"
CHECKER_FIXTURE_REL = "tests/conformance/checker-predicates/chunks/part-0026.json"
DECISION_REL = "decisions/language/Design_Deeplus_Refinement_R0_Calculus_Closure_R1.md"
LANGUAGE_REL = "spec/language.md"
TYPE_REL = "spec/types/type-system.md"
FRONTEND_REL = "spec/frontend/frontend-model.json"
MIR_REL = "spec/mir/semantics.md"
REFERENCE_REL = "docs/grammar-reference/04-types-generics-and-refinement.md"
TRN_CONTRACT_REL = "spec/contracts/type-refinement-narrowing-coherence.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def formula_digest(formula: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(formula)).hexdigest()


def invert_operator(operator: str) -> str:
    return {"EQ": "NE", "NE": "EQ", "LT": "GE", "LE": "GT", "GT": "LE", "GE": "LT"}[operator]


def reverse_operator(operator: str) -> str:
    return {"EQ": "EQ", "NE": "NE", "LT": "GT", "LE": "GE", "GT": "LT", "GE": "LE"}[operator]


def complement(formula: dict[str, Any]) -> dict[str, Any]:
    kind = formula["kind"]
    if kind == "TRUE":
        return {"kind": "FALSE"}
    if kind == "FALSE":
        return {"kind": "TRUE"}
    if kind == "ATOM":
        return {"kind": "NOT", "atom": copy.deepcopy(formula["atom"])}
    if kind == "NOT":
        return {"kind": "ATOM", "atom": copy.deepcopy(formula["atom"])}
    swapped = "ANY" if kind == "ALL" else "ALL"
    return {"kind": swapped, "terms": [complement(term) for term in formula["terms"]]}


def dnf(formula: dict[str, Any], maximum_cells: int) -> list[list[tuple[dict[str, Any], bool]]]:
    kind = formula["kind"]
    if kind == "TRUE":
        return [[]]
    if kind == "FALSE":
        return []
    if kind == "ATOM":
        return [[(formula["atom"], True)]]
    if kind == "NOT":
        return [[(formula["atom"], False)]]
    if kind == "ANY":
        result: list[list[tuple[dict[str, Any], bool]]] = []
        for term in formula["terms"]:
            result.extend(dnf(term, maximum_cells))
            if len(result) > maximum_cells:
                raise OverflowError("DNF_CELL_LIMIT")
        return result
    result = [[]]
    for term in formula["terms"]:
        child = dnf(term, maximum_cells)
        result = [left + right for left in result for right in child]
        if len(result) > maximum_cells:
            raise OverflowError("DNF_CELL_LIMIT")
    return result


def static_value(term: dict[str, Any]) -> tuple[str, Any] | None:
    if term.get("kind") != "STATIC_VALUE":
        return None
    value = term["value"]
    kind = value["kind"]
    if kind in {"SIGNED_INTEGER", "UNSIGNED_INTEGER", "STATIC_INT"}:
        return kind, int(value["decimal"])
    if kind == "RATIONAL":
        return kind, Fraction(int(value["numerator"]), int(value["denominator"]))
    if kind == "BOOL":
        return kind, bool(value["value"])
    if kind == "CHAR_SCALAR":
        return kind, int(value["scalar"][2:], 16)
    if kind == "ORDERED_ENUM":
        return kind, int(value["ordinal"])
    if kind == "FLOAT32":
        return kind, struct.unpack(">f", bytes.fromhex(value["bits"]))[0]
    if kind == "FLOAT64":
        return kind, struct.unpack(">d", bytes.fromhex(value["bits"]))[0]
    return None


def variable_key(term: dict[str, Any]) -> tuple[str, str] | None:
    kind = term.get("kind")
    if kind == "PARAMETER":
        return f"p{term['parameter_index']}", term["type_id"]
    if kind == "PLACE":
        return f"place:{term['place_id']}", term["type_id"]
    if kind == "INTRINSIC" and len(term.get("arguments", [])) == 1:
        argument = variable_key(term["arguments"][0])
        if argument is not None:
            return f"{term['intrinsic_id']}({argument[0]})", term["type_id"]
    return None


def type_domain(type_id: str) -> str:
    if type_id in {"Float32", "Float64"}:
        return "FLOAT"
    if type_id == "Bool":
        return "BOOL"
    if type_id == "Rational":
        return "RATIONAL"
    if type_id.startswith("UInt") or type_id in {"UInt", "USize"}:
        return "UNSIGNED"
    if type_id.startswith("Int") or type_id in {"Int", "ISize", "StaticInt"}:
        return "INTEGER"
    if type_id == "Char":
        return "INTEGER"
    return "ORDERED_ENUM"


def comparison_shape(atom: dict[str, Any]) -> tuple[str, str, str, Any] | tuple[str, str, int, int] | None:
    operator = atom["operator"]
    left = atom["left"]
    right = atom["right"]
    left_var = variable_key(left)
    right_static = static_value(right)
    if left_var is not None and right_static is not None:
        return left_var[0], left_var[1], operator, right_static[1]
    right_var = variable_key(right)
    left_static = static_value(left)
    if right_var is not None and left_static is not None:
        return right_var[0], right_var[1], reverse_operator(operator), left_static[1]
    if (
        operator in {"EQ", "NE"}
        and left.get("kind") == "BINARY"
        and left.get("operator") == "REMAINDER"
        and variable_key(left["left"]) is not None
        and static_value(left["right"]) is not None
        and static_value(right) is not None
    ):
        var = variable_key(left["left"])
        divisor = static_value(left["right"])[1]
        residue = static_value(right)[1]
        if isinstance(divisor, int) and isinstance(residue, int) and divisor > 0:
            return var[0], operator, divisor, residue
    return None


def cell_satisfiability(literals: list[tuple[dict[str, Any], bool]]) -> str:
    polarities: dict[bytes, set[bool]] = {}
    constraints: dict[str, dict[str, Any]] = {}
    opaque = False
    for atom, positive in literals:
        identity = canonical_bytes(atom)
        polarities.setdefault(identity, set()).add(positive)
        if len(polarities[identity]) == 2:
            return "UNSAT"
        shape = comparison_shape(atom)
        if shape is None:
            opaque = True
            continue
        if len(shape) == 4 and isinstance(shape[2], int):
            key, operator, modulus, residue = shape
            if not positive:
                operator = invert_operator(operator)
            state = constraints.setdefault(key, {"lower": None, "upper": None, "excluded": set(), "congruence": None, "nan": False, "domain": "INTEGER"})
            normalized_residue = residue % modulus
            if operator == "EQ":
                previous = state["congruence"]
                if previous is not None and previous != (modulus, normalized_residue):
                    return "UNSAT"
                state["congruence"] = (modulus, normalized_residue)
            else:
                opaque = True
            continue
        key, type_id, operator, value = shape
        domain = type_domain(type_id)
        state = constraints.setdefault(key, {"lower": None, "upper": None, "excluded": set(), "congruence": None, "nan": domain == "FLOAT", "domain": domain})
        if domain == "FLOAT":
            if math.isnan(value):
                truth = operator == "NE"
                if truth != positive:
                    return "UNSAT"
                continue
            if positive:
                if operator in {"EQ", "LT", "LE", "GT", "GE"}:
                    state["nan"] = False
            else:
                operator = invert_operator(operator)
                if operator == "EQ":
                    state["nan"] = False
        else:
            if not positive:
                operator = invert_operator(operator)
        if operator == "EQ":
            state["lower"] = (value, True)
            state["upper"] = (value, True)
        elif operator == "NE":
            state["excluded"].add(value)
        elif operator in {"GT", "GE"}:
            candidate = (value, operator == "GE")
            current = state["lower"]
            if current is None or candidate[0] > current[0] or (candidate[0] == current[0] and not candidate[1] and current[1]):
                state["lower"] = candidate
        elif operator in {"LT", "LE"}:
            candidate = (value, operator == "LE")
            current = state["upper"]
            if current is None or candidate[0] < current[0] or (candidate[0] == current[0] and not candidate[1] and current[1]):
                state["upper"] = candidate

    for state in constraints.values():
        lower = state["lower"]
        upper = state["upper"]
        numeric_empty = False
        if lower is not None and upper is not None:
            if lower[0] > upper[0] or (lower[0] == upper[0] and (not lower[1] or not upper[1])):
                numeric_empty = True
            elif lower[0] == upper[0] and lower[0] in state["excluded"]:
                numeric_empty = True
        if not numeric_empty and state["congruence"] is not None and state["domain"] != "FLOAT":
            modulus, residue = state["congruence"]
            if lower is not None:
                start = math.floor(lower[0])
                if start < lower[0] or (start == lower[0] and not lower[1]):
                    start += 1
            else:
                start = residue
            witness = start + ((residue - start) % modulus)
            while witness in state["excluded"]:
                witness += modulus
            if upper is not None and (witness > upper[0] or (witness == upper[0] and not upper[1])):
                numeric_empty = True
        if numeric_empty and not state["nan"]:
            return "UNSAT"
    return "UNKNOWN" if opaque else "SAT"


def satisfiability(formula: dict[str, Any], maximum_cells: int) -> str:
    try:
        cells = dnf(formula, maximum_cells)
    except OverflowError:
        return "UNKNOWN"
    if not cells:
        return "UNSAT"
    saw_unknown = False
    for cell in cells:
        result = cell_satisfiability(cell)
        if result == "SAT":
            return "SAT"
        if result == "UNKNOWN":
            saw_unknown = True
    return "UNKNOWN" if saw_unknown else "UNSAT"


def relation(left: dict[str, Any], right: dict[str, Any], maximum_cells: int) -> str:
    left_not_right = satisfiability({"kind": "ALL", "terms": [left, complement(right)]}, maximum_cells)
    right_not_left = satisfiability({"kind": "ALL", "terms": [right, complement(left)]}, maximum_cells)
    if left_not_right == "UNSAT" and right_not_left == "UNSAT":
        return "EQUIVALENT"
    together = satisfiability({"kind": "ALL", "terms": [left, right]}, maximum_cells)
    if together == "UNSAT":
        return "DISJOINT"
    if left_not_right == "UNSAT":
        return "LEFT_IMPLIES_RIGHT"
    if right_not_left == "UNSAT":
        return "RIGHT_IMPLIES_LEFT"
    if together == "SAT" and left_not_right != "UNKNOWN" and right_not_left != "UNKNOWN":
        return "OVERLAPS"
    return "UNKNOWN"


def count_nodes(value: Any) -> tuple[int, int]:
    if not isinstance(value, dict):
        return 0, 0
    child_results: list[tuple[int, int]] = []
    for key in ("terms", "arguments"):
        for child in value.get(key, []):
            child_results.append(count_nodes(child))
    for key in ("atom", "left", "right", "operand"):
        child = value.get(key)
        if isinstance(child, dict):
            child_results.append(count_nodes(child))
    return 1 + sum(item[0] for item in child_results), 1 + max((item[1] for item in child_results), default=0)


def term_total(term: dict[str, Any]) -> bool:
    kind = term.get("kind")
    if kind in {"PARAMETER", "PLACE", "STATIC_VALUE"}:
        return True
    if kind == "INTRINSIC":
        return term.get("intrinsic_id") in {"STRING_SCALAR_LENGTH", "BYTES_LENGTH", "LIST_LENGTH", "READONLY_VIEW_LENGTH"} and all(term_total(arg) for arg in term.get("arguments", []))
    if kind == "UNARY":
        if not term_total(term.get("operand", {})):
            return False
        return type_domain(term.get("type_id", "")) == "FLOAT" or term.get("operand", {}).get("kind") == "STATIC_VALUE"
    if kind != "BINARY" or not term_total(term.get("left", {})) or not term_total(term.get("right", {})):
        return False
    domain = type_domain(term.get("type_id", ""))
    if domain == "FLOAT":
        return True
    if term.get("operator") in {"DIVIDE", "REMAINDER"}:
        right = static_value(term.get("right", {}))
        return right is not None and right[1] != 0 and not (right[1] == -1 and term.get("left", {}).get("kind") != "STATIC_VALUE")
    return term.get("left", {}).get("kind") == "STATIC_VALUE" and term.get("right", {}).get("kind") == "STATIC_VALUE"


def formula_terms(formula: dict[str, Any]) -> list[dict[str, Any]]:
    kind = formula.get("kind")
    if kind in {"ATOM", "NOT"}:
        atom = formula.get("atom", {})
        return [atom.get("left", {}), atom.get("right", {})]
    result: list[dict[str, Any]] = []
    for child in formula.get("terms", []):
        result.extend(formula_terms(child))
    return result


def canonical_formula(formula: dict[str, Any]) -> bool:
    kind = formula.get("kind")
    if kind in {"TRUE", "FALSE", "ATOM", "NOT"}:
        return True
    terms = formula.get("terms", [])
    identities = [canonical_bytes(term) for term in terms]
    if identities != sorted(identities) or len(set(identities)) != len(identities):
        return False
    if any(term.get("kind") == kind for term in terms):
        return False
    return all(canonical_formula(term) for term in terms)


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = copy.deepcopy(contract_override) if contract_override is not None else load(root / CONTRACT_REL)
    fixture = copy.deepcopy(fixture_override) if fixture_override is not None else load(root / FIXTURE_REL)
    contract_schema = load(root / CONTRACT_SCHEMA_REL)
    formula_schema = load(root / FORMULA_SCHEMA_REL)
    query_schema = load(root / QUERY_SCHEMA_REL)
    guard_schema = load(root / GUARD_SCHEMA_REL)
    guard_descriptor_schema = load(root / GUARD_DESCRIPTOR_SCHEMA_REL)
    guard_contract = load(root / GUARD_CONTRACT_REL)
    checker_fixtures = load(root / CHECKER_FIXTURE_REL)
    trn_contract = load(root / TRN_CONTRACT_REL)

    def chunk_rows(pattern: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for path in sorted(root.glob(pattern)):
            value = load(path)
            if isinstance(value, list):
                rows.extend(item for item in value if isinstance(item, dict))
        return rows

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    for path in (CONTRACT_REL, CONTRACT_SCHEMA_REL, FORMULA_SCHEMA_REL, QUERY_SCHEMA_REL, FIXTURE_REL, GUARD_SCHEMA_REL, GUARD_DESCRIPTOR_SCHEMA_REL, DECISION_REL, TRN_CONTRACT_REL):
        require((root / path).is_file(), "G01", f"MISSING:{path}")
    require(contract.get("gap_id") == "IR-REF-P1-056", "G01", "GAP_ID")
    require(contract.get("formula_schema") == FORMULA_SCHEMA_REL, "G01", "FORMULA_SCHEMA_BINDING")
    require(contract.get("query_schema") == QUERY_SCHEMA_REL, "G01", "QUERY_SCHEMA_BINDING")
    require(formula_schema.get("$defs", {}).get("formula") is not None, "G01", "TYPED_FORMULA_DEF")
    require(query_schema.get("properties", {}).get("query_kind", {}).get("enum") == ["FORMULA_ADMISSION", "BOUNDARY_PROOF", "RELATION"], "G01", "QUERY_KIND_SET")
    require(contract_schema.get("properties", {}).get("gap_id", {}).get("const") == "IR-REF-P1-056", "G01", "CONTRACT_SCHEMA_GAP")

    require(contract.get("value_domains") == ["BOOL", "SIGNED_INTEGER", "UNSIGNED_INTEGER", "STATIC_INT", "FLOAT32", "FLOAT64", "RATIONAL", "CHAR_SCALAR", "ORDERED_ENUM"], "G02", "DOMAIN_SET")
    vocabulary = contract.get("closed_term_vocabulary", {})
    require(vocabulary.get("term_kinds") == ["PARAMETER", "PLACE", "STATIC_VALUE", "INTRINSIC", "UNARY", "BINARY"], "G02", "TERM_KINDS")
    require(vocabulary.get("user_operator_or_method_dispatch_count") == 0, "G02", "NO_USER_DISPATCH")
    normal = contract.get("formula_normal_form", {})
    require(normal.get("node_kinds") == ["TRUE", "FALSE", "ATOM", "NOT", "ALL", "ANY"], "G02", "FORMULA_KINDS")
    require(normal.get("float_comparison_complement_rewrite_count") == 0, "G02", "FLOAT_COMPLEMENT")
    require(normal.get("arithmetic_operand_reassociation_count") == 0, "G02", "NO_REASSOCIATION")

    totality = contract.get("totality", {})
    require(totality.get("required_before_formula_admission") is True, "G03", "TOTALITY_REQUIRED")
    require(totality.get("proof_input") == "DECLARED_NORMALIZED_PARAMETER_DOMAIN_ONLY", "G03", "TOTALITY_INPUT")
    require(totality.get("conjunct_or_short_circuit_fact_may_justify_failing_term") is False, "G03", "NO_SHORT_CIRCUIT_ESCAPE")
    require(totality.get("user_operator_or_method_dispatch_count", 0) == 0, "G03", "TOTALITY_USER_DISPATCH")
    require(totality.get("effects_errors_suspension_authority_mutation_consumption_count") == 0, "G03", "RESPONSIBILITY_FREE")

    limits = contract.get("resource_limits", {})
    require(limits.get("formula_node_count_max") == 256 and limits.get("formula_depth_max") == 32, "G04", "FORMULA_LIMITS")
    require(limits.get("dnf_cell_count_max") == 256 and limits.get("proof_step_count_max") == 100000, "G04", "PROOF_LIMITS")
    require(limits.get("proof_step_count_max", 0) > limits.get("formula_node_count_max", 0), "G04", "FINITE_PROOF_BUDGET")
    procedure = contract.get("relation_procedure", {})
    require(procedure.get("proof_budget_exhaustion") == "UNKNOWN_NOT_PASS", "G04", "BUDGET_UNKNOWN")
    require(procedure.get("formula_satisfiability") == ["SAT", "UNSAT", "UNKNOWN"], "G04", "THREE_VALUED")

    formula_cases = fixture.get("formula_cases", [])
    ids = [case.get("id") for case in formula_cases]
    require(len(ids) == len(set(ids)) == 8, "G05", "FORMULA_CASE_IDS")
    classes = {kind: sum(case.get("class") == kind for case in formula_cases) for kind in ("positive", "boundary")}
    require(classes == {"positive": 4, "boundary": 4}, "G05", "FORMULA_CLASS_COUNTS")
    case_map = {case["id"]: case for case in formula_cases}
    for case in formula_cases:
        document = case.get("document", {})
        formula = document.get("formula", {})
        require(document.get("schema") == "deeplus.refinement-r0-formula/v1", "G05", f"FORMULA_SCHEMA:{case.get('id')}")
        require(document.get("formula_digest") == formula_digest(formula), "G05", f"FORMULA_DIGEST:{case.get('id')}")
        node_count, depth = count_nodes(formula)
        require(node_count <= limits.get("formula_node_count_max", 0) and depth <= limits.get("formula_depth_max", 0), "G05", f"FORMULA_LIMIT:{case.get('id')}")
        require(canonical_formula(formula), "G05", f"FORMULA_CANONICAL:{case.get('id')}")
        require(all(term_total(term) for term in formula_terms(formula)), "G05", f"TERM_TOTAL:{case.get('id')}")
        if case.get("expected") != "ADMIT_SUBSTITUTED_PHI_FACT_ONLY":
            require("PLACE" not in canonical_bytes(formula).decode("utf-8"), "G05", f"SUMMARY_PLACE:{case.get('id')}")

    query_cases = fixture.get("query_cases", [])
    require(len(query_cases) == 3 and len({row.get("id") for row in query_cases}) == 3, "G05", "QUERY_CASE_IDS")
    for row in query_cases:
        descriptor = row.get("descriptor", {})
        query_kind = descriptor.get("query_kind")
        left = descriptor.get("left_formula", {})
        right = descriptor.get("right_formula_or_null")
        require(descriptor.get("schema") == "deeplus.refinement-r0-query/v1", "G05", f"QUERY_SCHEMA:{row.get('id')}")
        require(query_kind in {"FORMULA_ADMISSION", "BOUNDARY_PROOF", "RELATION"}, "G05", f"QUERY_KIND:{row.get('id')}")
        require((query_kind == "FORMULA_ADMISSION") == (right is None), "G05", f"QUERY_RIGHT:{row.get('id')}")
        require(len(descriptor.get("selected_r0_row_ids", [])) == len(set(descriptor.get("selected_r0_row_ids", []))), "G05", f"QUERY_ROWS:{row.get('id')}")
        require(not any(descriptor.get("responsibility", {}).values()), "G05", f"QUERY_RESPONSIBILITY:{row.get('id')}")
        require(descriptor.get("totality") == "PROVED", "G05", f"QUERY_TOTALITY:{row.get('id')}")
        require(canonical_formula(left) and (right is None or canonical_formula(right)), "G05", f"QUERY_CANONICAL:{row.get('id')}")
        require(all(term_total(term) for term in formula_terms(left)) and (right is None or all(term_total(term) for term in formula_terms(right))), "G05", f"QUERY_TERM_TOTAL:{row.get('id')}")
        usage = descriptor.get("resource_usage", {})
        require(usage.get("formula_nodes", 257) <= limits.get("formula_node_count_max", 0), "G05", f"QUERY_NODE_LIMIT:{row.get('id')}")
        require(usage.get("proof_steps", 100001) <= limits.get("proof_step_count_max", 0), "G05", f"QUERY_PROOF_LIMIT:{row.get('id')}")
        if query_kind == "FORMULA_ADMISSION":
            observed_query = "ADMIT_FORMULA"
        elif query_kind == "RELATION":
            observed_query = relation(left, right, limits.get("dnf_cell_count_max", 0))
        else:
            phi_not_target = satisfiability({"kind": "ALL", "terms": [left, complement(right)]}, limits.get("dnf_cell_count_max", 0))
            phi_target = satisfiability({"kind": "ALL", "terms": [left, right]}, limits.get("dnf_cell_count_max", 0))
            observed_query = "PROVED" if phi_not_target == "UNSAT" else "DISPROVED" if phi_target == "UNSAT" else "UNKNOWN"
        require(observed_query == row.get("expected"), "G05", f"QUERY_RESULT:{row.get('id')}:{observed_query}")

    relation_cases = fixture.get("relation_cases", [])
    require(len(relation_cases) == 5 and len({row.get("id") for row in relation_cases}) == 5, "G06", "RELATION_CASES")
    for row in relation_cases:
        if row.get("left_formula_case"):
            left = case_map[row["left_formula_case"]]["document"]["formula"]
            right = case_map[row["right_formula_case"]]["document"]["formula"]
        else:
            left = row["left_formula"]
            right = row["right_formula"]
        observed = relation(left, right, limits.get("dnf_cell_count_max", 0))
        require(observed == row.get("expected_relation"), "G06", f"RELATION:{row.get('id')}:{observed}")

    rejection_cases = fixture.get("rejection_cases", [])
    require(len(rejection_cases) == 5 and len({row.get("id") for row in rejection_cases}) == 5, "G07", "REJECTION_CASES")
    diagnostics: set[str] = set()
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("*.json")):
        diagnostics.update(row.get("diagnostic_id") for row in load(path) if isinstance(row, dict))
    require(all(row.get("diagnostic") in diagnostics for row in rejection_cases), "G07", "REJECTION_DIAGNOSTICS")
    diagnostic_order = contract.get("diagnostic_precedence", [])
    require([row.get("rank") for row in diagnostic_order] == list(range(1, 8)), "G07", "DIAGNOSTIC_RANK")
    require(all(row.get("diagnostic") in diagnostics for row in diagnostic_order), "G07", "DIAGNOSTIC_BINDING")

    normalized_formula_schema = guard_schema.get("properties", {}).get("normalized_formula", {})
    require(normalized_formula_schema.get("$ref") == "./refinement-r0-formula-v1.schema.json#/$defs/formula", "G08", "GUARD_TYPED_FORMULA")
    require("formula_digest" in guard_schema.get("required", []), "G08", "GUARD_FORMULA_DIGEST")
    substituted = guard_descriptor_schema.get("properties", {}).get("substituted_formula_or_null", {})
    require(any(row.get("$ref") == "./refinement-r0-formula-v1.schema.json#/$defs/formula" for row in substituted.get("oneOf", [])), "G08", "SUBSTITUTED_TYPED_FORMULA")
    require(guard_contract.get("summary", {}).get("formula_contract") == CONTRACT_REL, "G08", "GUARD_CONTRACT_BINDING")
    guard_rows = [row for row in checker_fixtures if row.get("predicate_id") in {"GuardRefinementSummaryAdmitted", "GuardCallRefinementApplied"}]
    require(len(guard_rows) >= 4, "G08", "GUARD_FIXTURE_ROWS")
    for row in guard_rows:
        summary = row.get("descriptor", {}).get("summary")
        if summary is not None:
            require(isinstance(summary.get("normalized_formula"), dict), "G08", f"GUARD_FORMULA_OBJECT:{row.get('fixture_id')}")
            require(summary.get("formula_digest") == formula_digest(summary["normalized_formula"]), "G08", f"GUARD_DIGEST:{row.get('fixture_id')}")
        substituted_formula = row.get("descriptor", {}).get("substituted_formula_or_null")
        require(substituted_formula is None or isinstance(substituted_formula, dict), "G08", f"SUBSTITUTED_OBJECT:{row.get('fixture_id')}")

    required_anchor = "spec/contracts/refinement-r0-calculus-v1.json"
    texts = {
        "LANGUAGE": (root / LANGUAGE_REL).read_text(encoding="utf-8"),
        "TYPE": (root / TYPE_REL).read_text(encoding="utf-8"),
        "FRONTEND": (root / FRONTEND_REL).read_text(encoding="utf-8"),
        "MIR": (root / MIR_REL).read_text(encoding="utf-8"),
        "REFERENCE": (root / REFERENCE_REL).read_text(encoding="utf-8"),
        "DECISION": (root / DECISION_REL).read_text(encoding="utf-8"),
    }
    for name, text in texts.items():
        require("RefinementR0V1" in text or required_anchor in text, "G09", f"ANCHOR:{name}")
    require("not(x > c)" in texts["DECISION"] and "x <= c" in texts["DECISION"], "G09", "NAN_TEACHING_BOUNDARY")

    features = {row.get("feature_id"): row for row in chunk_rows("spec/features/catalog/chunks/*.json")}
    for feature_id in ("proof_profile_r0", "r0_guard_predicate_calculus", "refinement_type_phase_a", "guard_function_for_clause_predicates"):
        feature = features.get(feature_id, {})
        require(CONTRACT_REL in feature.get("artifact_trace_refs", []), "G09", f"FEATURE_CONTRACT:{feature_id}")
        require(feature.get("product_support") == "NOT_RUN", "G09", f"FEATURE_PRODUCT:{feature_id}")
    predicates = {row.get("predicate_id"): row for row in chunk_rows("spec/types/predicates/chunks/*.json")}
    for predicate_id in ("R0GuardSafe", "RefinementR0PredicateAdmitted", "RefinementCheckBoundaryAdmitted"):
        predicate = predicates.get(predicate_id, {})
        require(predicate.get("input_descriptor") == "RefinementR0QueryV1", "G09", f"PREDICATE_DESCRIPTOR:{predicate_id}")
        require(predicate.get("input_descriptor_schema") == QUERY_SCHEMA_REL, "G09", f"PREDICATE_SCHEMA:{predicate_id}")
        require("RefinementR0V1" in canonical_bytes(predicate).decode("utf-8"), "G09", f"PREDICATE_CONTRACT:{predicate_id}")
    require("RefinementR0V1" in canonical_bytes(predicates.get("NormalizeUnion", {})).decode("utf-8"), "G09", "NORMALIZE_UNION_CONTRACT")
    trn_schema_map = trn_contract.get("predicate_input_schema_by_predicate", {})
    require(
        trn_contract.get("predicate_inputs_role")
        == "CROSS_PREDICATE_INTEGRATION_ENVELOPE_NOT_CHECKER_INPUT",
        "G09",
        "TRN_INTEGRATION_ROLE",
    )
    for predicate_id in ("R0GuardSafe", "RefinementCheckBoundaryAdmitted"):
        require(
            trn_schema_map.get(predicate_id) == QUERY_SCHEMA_REL,
            "G09",
            f"TRN_R0_QUERY_SCHEMA:{predicate_id}",
        )
    for predicate_id in ("GuardRefinementSummaryAdmitted", "GuardCallRefinementApplied"):
        require("RefinementR0V1" in canonical_bytes(predicates.get(predicate_id, {})).decode("utf-8"), "G09", f"GUARD_PREDICATE_CONTRACT:{predicate_id}")

    governance = contract.get("governance", {})
    require(governance == {"semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "production_implementation": "NOT_RUN", "github_publication": "NOT_PERFORMED"}, "G10", "GOVERNANCE")
    expected = fixture.get("expected_counts", {})
    require(expected.get("semantic_p0") == 0 and expected.get("feature_p1") == 22, "G10", "FIXTURE_P0_P1")
    require(expected.get("product_lanes") == 15 and expected.get("product_executed") == 0, "G10", "FIXTURE_PRODUCT")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2], type=Path)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(error)
        return 1
    print("REFINEMENT_R0_V1: PASS")
    print("FORMULAS: 8/8; RELATIONS: 5/5; REJECTIONS: 5/5")
    print("PRODUCT_EXECUTION: NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
