#!/usr/bin/env python3
"""Design-static validator for the R34 path-sensitive loan-close contract.

The validator checks authored contracts, a compact path projection, and exact
mutations.  It does not execute a Deeplus parser, checker, MIR lowerer,
runtime, backend, formatter, or LSP; product support therefore remains NOT_RUN.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DIAGNOSTIC = "MIR_LOAN_UNBALANCED"
REASON_PRIORITY = [
    "TOKEN_BINDING_MISMATCH",
    "BEGIN_DECLARATION_MISMATCH",
    "BEGIN_STATE_INVALID",
    "END_STATE_INVALID",
    "ACTIVE_CHILD_BLOCKS_PARENT_END",
    "OWNER_INVALIDATION_WHILE_LIVE",
    "SUSPENSION_WHILE_LIVE",
    "CFG_JOIN_LOAN_STATE_CONFLICT",
    "TERMINAL_LIVE_LOAN",
]
EXPECTED_MUTATIONS = [
    "DROP_END_NORMAL",
    "DROP_END_ERROR",
    "DROP_END_CANCELLATION",
    "DUPLICATE_END",
    "END_UNKNOWN_OR_INACTIVE",
    "END_PARENT_BEFORE_CHILD",
    "OMIT_BEGIN_ACCESS_OUTPUT",
    "OMIT_END_ACCESS_DISCHARGE",
    "WRONG_ACCESS_TOKEN_LOAN_BINDING",
    "OWNER_CLEANUP_BEFORE_END",
    "SUSPEND_WITH_LIVE_LOAN",
    "CHECK_ONLY_FIRST_TERMINAL_EDGE",
]


def load(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def rows(root: Path, rel: str) -> list[dict[str, Any]]:
    answer: list[dict[str, Any]] = []
    for path in sorted((root / rel).glob("part-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            raise ValueError(f"catalog shard is not an array: {path}")
        answer.extend(row for row in value if isinstance(row, dict))
    return answer


def local_refs_closed(schema: dict[str, Any]) -> bool:
    defs = schema.get("$defs", {})
    refs: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            ref = value.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                refs.append(ref.removeprefix("#/$defs/"))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(schema)
    return bool(refs) and all(ref in defs for ref in refs)


@dataclass(frozen=True)
class Violation:
    reason: str
    loan_id: str
    origin: str


def violation_key(value: Violation) -> tuple[int, str, str]:
    try:
        rank = REASON_PRIORITY.index(value.reason)
    except ValueError:
        rank = len(REASON_PRIORITY)
    return rank, value.origin, value.loan_id


def derive_case(value: dict[str, Any]) -> dict[str, Any]:
    loan_rows = value["loans"]
    loan_by_id = {row["loan_id"]: row for row in loan_rows}
    violations: list[Violation] = []
    join_states: dict[str, list[tuple[tuple[str, str], ...]]] = {}
    path_outcomes: list[tuple[str | None, tuple[str, ...]]] = []

    if len(loan_by_id) != len(loan_rows):
        violations.append(Violation("BEGIN_DECLARATION_MISMATCH", "<duplicate>", value["body_id"]))
    for row in loan_rows:
        ends = row["end_operation_ids"]
        if ends != sorted(set(ends)) or not ends:
            violations.append(Violation("BEGIN_DECLARATION_MISMATCH", row["loan_id"], row["begin_operation_id"]))
        parent = row["parent_loan_id_or_null"]
        if parent is not None and parent not in loan_by_id:
            violations.append(Violation("BEGIN_DECLARATION_MISMATCH", row["loan_id"], row["begin_operation_id"]))

    admitted = set(value["suspension_admitted_loan_ids"])
    if not admitted.issubset(loan_by_id):
        violations.append(Violation("BEGIN_DECLARATION_MISMATCH", "<suspension>", value["body_id"]))

    for path in value["paths"]:
        state = {loan_id: "INACTIVE" for loan_id in loan_by_id}
        token_live = {loan_id: False for loan_id in loan_by_id}
        primary: str | None = None
        suppressed: list[str] = []
        last_cleanup_ordinal: int | None = None

        for event in path["events"]:
            kind = event["kind"]
            origin = event["event_id"]
            loan_id = event.get("loan_id_or_null")
            row = loan_by_id.get(loan_id)

            if kind in {"BEGIN_SHARED", "BEGIN_EXCLUSIVE", "BEGIN_REBORROW"}:
                if row is None or origin != row["begin_operation_id"]:
                    violations.append(Violation("BEGIN_DECLARATION_MISMATCH", loan_id or "<null>", origin))
                    continue
                expected_kind = "BEGIN_REBORROW" if row["parent_loan_id_or_null"] else (
                    "BEGIN_SHARED" if row["kind"] == "SHARED" else "BEGIN_EXCLUSIVE"
                )
                if kind != expected_kind or event.get("parent_loan_id_or_null") != row["parent_loan_id_or_null"]:
                    violations.append(Violation("BEGIN_DECLARATION_MISMATCH", loan_id, origin))
                if event.get("access_token_id_or_null") != row["access_token_id"]:
                    violations.append(Violation("TOKEN_BINDING_MISMATCH", loan_id, origin))
                if state[loan_id] != "INACTIVE" or token_live[loan_id]:
                    violations.append(Violation("BEGIN_STATE_INVALID", loan_id, origin))
                parent = row["parent_loan_id_or_null"]
                if parent is not None:
                    if state.get(parent) != "ACTIVE":
                        violations.append(Violation("BEGIN_STATE_INVALID", loan_id, origin))
                    else:
                        state[parent] = "SUSPENDED_BY_CHILD"
                state[loan_id] = "ACTIVE"
                token_live[loan_id] = True
                continue

            if kind == "USE":
                if row is None or state.get(loan_id) != "ACTIVE":
                    violations.append(Violation("END_STATE_INVALID", loan_id or "<null>", origin))
                continue

            if kind == "END":
                if row is None:
                    violations.append(Violation("END_STATE_INVALID", loan_id or "<null>", origin))
                    continue
                if event.get("access_token_id_or_null") != row["access_token_id"]:
                    violations.append(Violation("TOKEN_BINDING_MISMATCH", loan_id, origin))
                if origin not in row["end_operation_ids"] or state[loan_id] == "INACTIVE":
                    violations.append(Violation("END_STATE_INVALID", loan_id, origin))
                live_children = [
                    child_id for child_id, child in loan_by_id.items()
                    if child["parent_loan_id_or_null"] == loan_id
                    and state.get(child_id) != "INACTIVE"
                ]
                if live_children:
                    violations.append(Violation("ACTIVE_CHILD_BLOCKS_PARENT_END", loan_id, origin))
                if state[loan_id] == "ACTIVE" and not live_children:
                    state[loan_id] = "INACTIVE"
                    token_live[loan_id] = False
                    parent = row["parent_loan_id_or_null"]
                    if parent is not None and state.get(parent) == "SUSPENDED_BY_CHILD":
                        state[parent] = "ACTIVE"
                continue

            if kind in {"OWNER_MOVE", "OWNER_CLEANUP"}:
                for overlap in event.get("overlapping_loan_ids", []):
                    if state.get(overlap) != "INACTIVE":
                        violations.append(Violation("OWNER_INVALIDATION_WHILE_LIVE", overlap, origin))
                continue

            if kind == "SUSPEND":
                for active_id, active_state in state.items():
                    if active_state != "INACTIVE" and active_id not in admitted:
                        violations.append(Violation("SUSPENSION_WHILE_LIVE", active_id, origin))
                continue

            if kind == "JOIN":
                join_id = event.get("join_id_or_null")
                snapshot = tuple(sorted((loan, state[loan] + (":TOKEN" if token_live[loan] else ":NO_TOKEN")) for loan in state))
                join_states.setdefault(join_id or "<null>", []).append(snapshot)
                continue

            if kind in {"PRIMARY_ERROR", "PRIMARY_DEFECT", "PRIMARY_CANCELLATION"}:
                failure = event.get("failure_id_or_null")
                if primary is None:
                    primary = failure
                elif failure is not None:
                    suppressed.append(failure)
                continue

            if kind == "CLEANUP_FAIL":
                ordinal = event.get("cleanup_acquisition_ordinal_or_null")
                if last_cleanup_ordinal is not None and ordinal is not None and ordinal >= last_cleanup_ordinal:
                    violations.append(Violation("OWNER_INVALIDATION_WHILE_LIVE", "<cleanup-order>", origin))
                last_cleanup_ordinal = ordinal
                failure = event.get("failure_id_or_null")
                if primary is None:
                    primary = failure
                elif failure is not None:
                    suppressed.append(failure)
                continue

            if kind == "TERMINAL":
                for active_id, active_state in state.items():
                    if active_state != "INACTIVE" or token_live[active_id]:
                        violations.append(Violation("TERMINAL_LIVE_LOAN", active_id, origin))

        path_outcomes.append((primary, tuple(suppressed)))

    for join_id, snapshots in join_states.items():
        if len(snapshots) > 1 and len(set(snapshots)) != 1:
            differing = next((loan for loan, _ in snapshots[0]), "<join>")
            violations.append(Violation("CFG_JOIN_LOAN_STATE_CONFLICT", differing, join_id))

    if violations:
        winner = min(violations, key=violation_key)
        return {
            "verdict": "REJECT",
            "diagnostic_or_null": DIAGNOSTIC,
            "reason_or_null": winner.reason,
            "primary_failure_or_null": "PATH_DEPENDENT" if len(set(primary for primary, _ in path_outcomes)) > 1 else (path_outcomes[0][0] if path_outcomes else None),
            "suppressed_failures": [],
            "oracle": {
                "diagnostic": DIAGNOSTIC,
                "reason": winner.reason,
                "loan_id": winner.loan_id,
                "origin": winner.origin,
                "emission_count": 1,
                "later_checks": "NOT_EVALUATED",
            },
        }

    primaries = {primary for primary, _ in path_outcomes}
    suppressed_sets = {suppressed for _, suppressed in path_outcomes}
    return {
        "verdict": "ACCEPT",
        "diagnostic_or_null": None,
        "reason_or_null": None,
        "primary_failure_or_null": next(iter(primaries)) if len(primaries) == 1 else "PATH_DEPENDENT",
        "suppressed_failures": list(next(iter(suppressed_sets))) if len(suppressed_sets) == 1 else [],
    }


def mutate(base: dict[str, Any], name: str, cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    value = copy.deepcopy(base)
    path = value["paths"][0]
    events = path["events"]
    end = next(event for event in events if event["kind"] == "END")
    terminal_index = next(i for i, event in enumerate(events) if event["kind"] == "TERMINAL")

    if name == "DROP_END_NORMAL":
        path["events"] = [event for event in events if event["kind"] != "END"]
    elif name in {"DROP_END_ERROR", "DROP_END_CANCELLATION"}:
        bad = copy.deepcopy(path)
        bad["path_id"] = "path.mutant.edge"
        bad["events"] = [event for event in bad["events"] if event["kind"] != "END"]
        terminal_index = next(i for i, event in enumerate(bad["events"]) if event["kind"] == "TERMINAL")
        outcome_kind = "PRIMARY_ERROR" if name == "DROP_END_ERROR" else "PRIMARY_CANCELLATION"
        bad["events"].insert(terminal_index, {"event_id":"outcome.mutant","kind":outcome_kind,"failure_id_or_null":"failure.mutant"})
        value["paths"].append(bad)
    elif name == "DUPLICATE_END":
        duplicate = copy.deepcopy(end)
        duplicate["event_id"] = "op.end.shared.duplicate"
        value["loans"][0]["end_operation_ids"].append(duplicate["event_id"])
        value["loans"][0]["end_operation_ids"].sort()
        events.insert(terminal_index, duplicate)
    elif name == "END_UNKNOWN_OR_INACTIVE":
        duplicate = copy.deepcopy(end)
        duplicate["event_id"] = "op.end.shared.unknown"
        duplicate["loan_id_or_null"] = "loan.unknown"
        events.insert(terminal_index, duplicate)
    elif name == "END_PARENT_BEFORE_CHILD":
        value = copy.deepcopy(cases["R34-LOAN-NEG-010"]["input"])
    elif name == "OMIT_BEGIN_ACCESS_OUTPUT":
        next(event for event in events if event["kind"].startswith("BEGIN_"))["access_token_id_or_null"] = None
    elif name == "OMIT_END_ACCESS_DISCHARGE":
        end["access_token_id_or_null"] = None
    elif name == "WRONG_ACCESS_TOKEN_LOAN_BINDING":
        end["access_token_id_or_null"] = "token.other"
    elif name == "OWNER_CLEANUP_BEFORE_END":
        cleanup = next(event for event in events if event["kind"] == "OWNER_CLEANUP")
        events.remove(cleanup)
        events.insert(events.index(end), cleanup)
    elif name == "SUSPEND_WITH_LIVE_LOAN":
        events.insert(events.index(end), {"event_id":"suspend.mutant","kind":"SUSPEND"})
    elif name == "CHECK_ONLY_FIRST_TERMINAL_EDGE":
        value = copy.deepcopy(cases["R34-LOAN-NEG-008"]["input"])
    else:
        raise ValueError(f"unknown mutation: {name}")
    return value


def validate_shape(fixtures: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_ids = [case.get("case_id") for case in fixtures.get("cases", [])]
    mutation_ids = [case.get("mutation_id") for case in fixtures.get("mutation_cases", [])]
    if len(case_ids) != len(set(case_ids)):
        errors.append("duplicate case ID")
    if len(mutation_ids) != len(set(mutation_ids)):
        errors.append("duplicate mutation ID")
    for case in fixtures.get("cases", []):
        if case.get("product_support") != "NOT_RUN":
            errors.append(f"{case.get('case_id')}: product support is not NOT_RUN")
        value = case.get("input", {})
        loan_ids = [row.get("loan_id") for row in value.get("loans", [])]
        if len(loan_ids) != len(set(loan_ids)):
            errors.append(f"{case.get('case_id')}: duplicate LoanId")
        for row in value.get("loans", []):
            ends = row.get("end_operation_ids", [])
            if ends != sorted(set(ends)):
                errors.append(f"{case.get('case_id')}: noncanonical end-operation IDs")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    try:
        contract = load(root, "spec/contracts/loan-close-operation-r1.json")
        schema = load(root, "schemas/language/loan-close-operation-fixtures-r1.schema.json")
        fixtures = load(root, "tests/fixtures/current/loan-close-operation-r1.json")
        mir_schema = load(root, "schemas/language/deeplus-mir.schema.json")
        mir_registry = load(root, "spec/contracts/mir-machine-registry.json")
        lowering = load(root, "spec/contracts/hir-mir-lowering-registry.json")
        feature_rows = rows(root, "spec/features/catalog/chunks")
        diagnostic_rows = rows(root, "spec/diagnostics/catalog/chunks")
    except Exception as exc:  # pragma: no cover - preflight reporting
        print(f"R34_LOAN_CLOSE_JSON_PARSE_FAILURE: {exc}")
        return 1

    if contract.get("schema") != "deeplus.loan-close-operation/r1":
        errors.append("contract identity differs")
    if contract.get("gap", {}).get("gap_id") != "IR-OWN-P1-022":
        errors.append("gap binding differs")
    if contract.get("verifier", {}).get("reason_priority") != REASON_PRIORITY:
        errors.append("diagnostic reason priority differs")
    if contract.get("acceptance", {}).get("case_count") != 12 or contract.get("acceptance", {}).get("mutation_count") != 12:
        errors.append("contract acceptance counts differ")
    if not local_refs_closed(schema):
        errors.append("fixture schema has an unresolved local reference")
    errors.extend(validate_shape(fixtures))

    classes = Counter(case.get("class") for case in fixtures.get("cases", []))
    expected_counts = fixtures.get("expected_counts", {})
    if classes != Counter({"POSITIVE": 3, "BOUNDARY": 3, "NEGATIVE": 6}):
        errors.append(f"case classes differ: {dict(classes)}")
    if expected_counts != {"total":12,"POSITIVE":3,"BOUNDARY":3,"NEGATIVE":6,"MUTATION":12}:
        errors.append("fixture expected counts differ")

    case_by_id = {case["case_id"]: case for case in fixtures.get("cases", [])}
    passed_cases = 0
    for case in fixtures.get("cases", []):
        actual = derive_case(case["input"])
        expected = case["expected"]
        comparable = {key: actual.get(key) for key in expected}
        if comparable != expected:
            errors.append(f"{case['case_id']}: oracle differs expected={expected} actual={comparable}")
        else:
            passed_cases += 1

    mutations = fixtures.get("mutation_cases", [])
    if [row.get("mutation") for row in mutations] != EXPECTED_MUTATIONS:
        errors.append("mutation set or order differs")
    passed_mutations = 0
    base = case_by_id.get("R34-LOAN-POS-001", {}).get("input", {})
    for row in mutations:
        try:
            mutant = mutate(base, row["mutation"], case_by_id)
            actual = derive_case(mutant)
        except Exception as exc:  # pragma: no cover - mutation report
            errors.append(f"{row.get('mutation_id')}: mutation failed to construct: {exc}")
            continue
        if actual.get("verdict") != "REJECT" or actual.get("diagnostic_or_null") != row.get("expected_diagnostic") or actual.get("reason_or_null") != row.get("expected_reason"):
            errors.append(f"{row['mutation_id']}: mutant survived or wrong oracle: {actual}")
        else:
            passed_mutations += 1

    loan_decl = mir_schema.get("$defs", {}).get("loanDecl", {})
    required_loan_fields = {
        "loan_id", "kind", "base_kind", "base_id", "projection_identity_id",
        "region_id", "parent_loan_id_or_null", "begin_operation_id", "end_operation_ids",
    }
    if set(loan_decl.get("required", [])) != required_loan_fields:
        errors.append("MIR loanDecl is not the exact enriched R34 shape")
    if not {"parent_loan_id_or_null", "begin_operation_id", "end_operation_ids"}.issubset(loan_decl.get("properties", {})):
        errors.append("MIR loanDecl close binding is missing")

    operation_by_kind = {row.get("operation_kind"): row for row in mir_registry.get("semantic_operations", [])}
    if operation_by_kind.get("LOAN_END", {}).get("semantic_operation_id") != "DM-SEMOP-LOAN-END-R1":
        errors.append("existing LOAN_END identity changed")
    token_by_kind = {row.get("token_kind"): row for row in mir_registry.get("linear_tokens", [])}
    if token_by_kind.get("ACCESS", {}).get("binding_fields") != ["loan_id"]:
        errors.append("ACCESS token binding changed")
    if mir_registry.get("loan_close_projection_contract", {}).get("contract") != "spec/contracts/loan-close-operation-r1.json":
        errors.append("MIR registry does not bind the R34 contract")
    if mir_registry.get("verifier_contract", {}).get("loan_close_path_balance") != "RECOMPUTE_FROM_LOAN_CLOSE_OPERATION_R1":
        errors.append("MIR verifier contract does not recompute loan close balance")
    if lowering.get("loan_close_projection_contract", {}).get("new_lowering_row_count") != 0:
        errors.append("lowering registry did not preserve zero new rows")

    diagnostic_matches = [row for row in diagnostic_rows if row.get("diagnostic_id") == DIAGNOSTIC]
    if len(diagnostic_matches) != 1:
        errors.append("MIR_LOAN_UNBALANCED is not exactly one catalog identity")
    elif diagnostic_matches[0].get("diagnostic_class") != "release_verifier" or diagnostic_matches[0].get("product_support") != "NOT_RUN":
        errors.append("MIR_LOAN_UNBALANCED catalog classification differs")
    feature_by_id = {row.get("feature_id"): row for row in feature_rows}
    for feature_id in ("hir_h1_current_mir_bridge_design", "region_lifetime_model_phase_a"):
        row = feature_by_id.get(feature_id, {})
        if DIAGNOSTIC not in row.get("normative_trace_refs", {}).get("diagnostics", []):
            errors.append(f"{feature_id}: diagnostic trace missing")
        if "spec/contracts/loan-close-operation-r1.json" not in row.get("artifact_trace_refs", []):
            errors.append(f"{feature_id}: artifact trace missing")
        if row.get("product_support") != "NOT_RUN":
            errors.append(f"{feature_id}: product support changed")

    fences = contract.get("global_fences", {})
    if fences != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "separate_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
        "canonical_github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION",
    }:
        errors.append("global status fence differs")

    if errors:
        for error in errors:
            print(f"R34_LOAN_CLOSE_FAILURE: {error}")
        return 1
    print(
        "R34_LOAN_CLOSE_PASS: "
        f"cases={passed_cases}/12 mutations={passed_mutations}/12 "
        "diagnostics=1 new_surface=0 new_mir_ops=0 product=NOT_RUN"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
