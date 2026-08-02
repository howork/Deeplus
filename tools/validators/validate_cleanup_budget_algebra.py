#!/usr/bin/env python3
"""Design-static validator for the R33 cleanup-budget algebra candidate.

This checks canonical design artifacts and typed fixtures only.  It does not
execute a Deeplus parser, checker, MIR lowerer, runtime, backend, formatter or
LSP and therefore cannot establish product support.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_CASE_COUNTS = {"normal": 4, "boundary": 2, "reject": 6, "mutation": 12}
EXPECTED_DIAGNOSTICS = {
    "CLEANUP_BUDGET_DUPLICATE",
    "CLEANUP_BUDGET_ERRORS_REQUIRES_ERROR_SET",
    "CLEANUP_BUDGET_EXCEEDED",
    "CLEANUP_BUDGET_BODY_POSITION_REMOVED",
    "CLEANUP_BUDGET_CAMELCASE_REMOVED",
    "RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT",
}
EXPECTED_SOURCE_KINDS = {"BASE_OWNER", "FIELD_OWNER", "OWNER_DEF_CLEANUP"}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def rows_from_chunks(root: Path, rel: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / rel).glob("part-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))
            continue
        candidates = [item for item in value.values() if isinstance(item, list)]
        if len(candidates) != 1:
            raise ValueError(f"cannot identify row array in {path}")
        rows.extend(row for row in candidates[0] if isinstance(row, dict))
    return rows


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


def sorted_unique(values: list[str]) -> bool:
    return values == sorted(set(values))


def normalize_raw(values: list[str]) -> tuple[list[str], bool]:
    return sorted(set(values)), len(values) != len(set(values))


def envelope_union(contributions: list[dict[str, Any]]) -> dict[str, list[str]]:
    errors: set[str] = set()
    effects: set[str] = set()
    for row in contributions:
        envelope = row["normalized_envelope"]
        errors.update(envelope["recoverable_error_ids"])
        effects.update(envelope["effect_ids"])
    return {
        "recoverable_error_ids": sorted(errors),
        "effect_ids": sorted(effects),
    }


def subset(left: dict[str, list[str]], right: dict[str, list[str]]) -> bool:
    return set(left["recoverable_error_ids"]).issubset(right["recoverable_error_ids"]) and set(
        left["effect_ids"]
    ).issubset(right["effect_ids"])


def trace_order_valid(contributions: list[dict[str, Any]]) -> bool:
    if [row["source_ordinal"] for row in contributions] != list(range(len(contributions))):
        return False
    kinds = [row["source_kind"] for row in contributions]
    if not set(kinds).issubset(EXPECTED_SOURCE_KINDS):
        return False
    if kinds.count("BASE_OWNER") > 1 or kinds.count("OWNER_DEF_CLEANUP") > 1:
        return False
    phase = 0
    for kind in kinds:
        next_phase = {"BASE_OWNER": 0, "FIELD_OWNER": 1, "OWNER_DEF_CLEANUP": 2}[kind]
        if next_phase < phase:
            return False
        phase = next_phase
    return all(
        sorted_unique(row["normalized_envelope"][axis])
        for row in contributions
        for axis in ("recoverable_error_ids", "effect_ids")
    )


def input_shape_errors(fixtures: dict[str, Any]) -> list[str]:
    """Check the closed fixture shape without depending on an installed JSON Schema package."""
    errors: list[str] = []
    required_input = {
        "schema", "predicate_id", "owner_type_id", "resource_hierarchy_role",
        "base_owner_type_id_or_null", "same_module_sealed_root_proven", "header",
        "family_root_envelope_or_null", "contributions_in_trace_order",
        "claimed_projection", "product_support",
    }
    required_projection = {
        "cleanup_budget_id", "declaration_mode", "family_root_type_id",
        "declared_envelope", "computed_envelope", "effective_envelope",
        "local_subset_proven", "family_subset_proven", "compatibility",
        "envelope_digest",
    }
    for row in fixtures.get("cases", []):
        case_id = row.get("case_id", "<missing>")
        value = row.get("input", {})
        if set(value) != required_input:
            errors.append(f"{case_id}:input-keys")
            continue
        if set(value.get("claimed_projection", {})) != required_projection:
            errors.append(f"{case_id}:projection-keys")
        for envelope in value.get("contributions_in_trace_order", []):
            normalized = envelope.get("normalized_envelope", {})
            for axis in ("recoverable_error_ids", "effect_ids"):
                if not sorted_unique(normalized.get(axis, [])):
                    errors.append(f"{case_id}:unsorted-contribution-{axis}")
        family = value.get("family_root_envelope_or_null")
        if family is not None:
            for axis in ("recoverable_error_ids", "effect_ids"):
                if not sorted_unique(family.get(axis, [])):
                    errors.append(f"{case_id}:unsorted-family-{axis}")
        if value.get("product_support") != "NOT_RUN":
            errors.append(f"{case_id}:product-support")
    return errors


def reject_oracle(
    diagnostic: str,
    reason: str,
    origin: str,
    axis: str,
    missing_identity: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "primary_diagnostic": diagnostic,
        "primary_reason": reason,
        "primary_origin": origin,
        "axis": axis,
        "emission_count": 1,
        "later_checks": "NOT_EVALUATED",
    }
    if missing_identity is not None:
        result["missing_identity"] = missing_identity
    return result


def derive(
    value: dict[str, Any],
) -> tuple[str, str | None, dict[str, Any] | None, dict[str, Any] | None]:
    header = value["header"]
    if header["effects_item_count"] > 1 or header["errors_item_count"] > 1:
        origin = "header.effects[1]" if header["effects_item_count"] > 1 else "header.errors[1]"
        oracle = reject_oracle("CLEANUP_BUDGET_DUPLICATE", "DUPLICATE_AXIS_ITEM", origin, "SURFACE_SHAPE")
        return "REJECT", oracle["primary_diagnostic"], None, oracle
    if header["errors_item_count"] == 1 and header["errors_type_kind"] != "ERROR_SET":
        oracle = reject_oracle(
            "CLEANUP_BUDGET_ERRORS_REQUIRES_ERROR_SET",
            "ERRORS_TYPE_NOT_ERROR_SET",
            "header.errors",
            "ERROR_SET_KIND",
        )
        return "REJECT", oracle["primary_diagnostic"], None, oracle
    _, duplicate_effect = normalize_raw(header["raw_effect_ids"])
    _, duplicate_error = normalize_raw(header["raw_recoverable_error_ids"])
    if duplicate_effect or duplicate_error:
        axis = "EFFECT" if duplicate_effect else "RECOVERABLE_ERROR"
        origin = "header.effects.identities[1]" if duplicate_effect else "header.errors.identities[1]"
        oracle = reject_oracle("CLEANUP_BUDGET_DUPLICATE", "DUPLICATE_NORMALIZED_IDENTITY", origin, axis)
        return "REJECT", oracle["primary_diagnostic"], None, oracle
    if value["resource_hierarchy_role"] == "SEALED_ROOT" and (
        not value["same_module_sealed_root_proven"] or not header["present"]
    ):
        oracle = reject_oracle(
            "RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT",
            "RESOURCE_ROOT_OR_CHILD_INVALID",
            value["owner_type_id"],
            "INHERITANCE",
        )
        return "REJECT", oracle["primary_diagnostic"], None, oracle
    if value["resource_hierarchy_role"] == "CHILD" and (
        not value["same_module_sealed_root_proven"]
        or value["family_root_envelope_or_null"] is None
    ):
        oracle = reject_oracle(
            "RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT",
            "RESOURCE_ROOT_OR_CHILD_INVALID",
            value["owner_type_id"],
            "INHERITANCE",
        )
        return "REJECT", oracle["primary_diagnostic"], None, oracle
    if not trace_order_valid(value["contributions_in_trace_order"]):
        return "REJECT", None, None, None

    declared = None
    if header["present"]:
        declared = {
            "recoverable_error_ids": sorted(set(header["raw_recoverable_error_ids"])),
            "effect_ids": sorted(set(header["raw_effect_ids"])),
        }
    computed = envelope_union(value["contributions_in_trace_order"])
    role = value["resource_hierarchy_role"]
    family = value["family_root_envelope_or_null"]
    if role == "CHILD" and not header["present"]:
        mode = "INHERITED_SEALED_ROOT"
        effective = {
            "recoverable_error_ids": list(family["recoverable_error_ids"]),
            "effect_ids": list(family["effect_ids"]),
        }
        family_root_type_id = family["family_root_type_id"]
    elif header["present"]:
        mode = "EXPLICIT_HEADER"
        effective = copy.deepcopy(declared)
        family_root_type_id = (
            family["family_root_type_id"] if role == "CHILD" else value["owner_type_id"]
        )
    else:
        mode = "IMPLICIT_EXACT_ROOT"
        effective = copy.deepcopy(computed)
        family_root_type_id = value["owner_type_id"]

    local_subset = subset(computed, effective)
    family_subset = True
    if role == "CHILD":
        family_subset = subset(
            effective,
            {
                "recoverable_error_ids": family["recoverable_error_ids"],
                "effect_ids": family["effect_ids"],
            },
        )
    if not local_subset:
        for contribution in value["contributions_in_trace_order"]:
            envelope = contribution["normalized_envelope"]
            for identity in envelope["recoverable_error_ids"]:
                if identity not in effective["recoverable_error_ids"]:
                    oracle = reject_oracle(
                        "CLEANUP_BUDGET_EXCEEDED",
                        "LOCAL_RECOVERABLE_ERROR_EXCEEDED",
                        contribution["source_id"],
                        "RECOVERABLE_ERROR",
                        identity,
                    )
                    return "REJECT", oracle["primary_diagnostic"], None, oracle
            for identity in envelope["effect_ids"]:
                if identity not in effective["effect_ids"]:
                    oracle = reject_oracle(
                        "CLEANUP_BUDGET_EXCEEDED",
                        "LOCAL_EFFECT_EXCEEDED",
                        contribution["source_id"],
                        "EFFECT",
                        identity,
                    )
                    return "REJECT", oracle["primary_diagnostic"], None, oracle
    if not family_subset:
        for axis, reason, public_axis in (
            ("recoverable_error_ids", "CHILD_RECOVERABLE_ERROR_WIDENED", "RECOVERABLE_ERROR"),
            ("effect_ids", "CHILD_EFFECT_WIDENED", "EFFECT"),
        ):
            missing = sorted(set(effective[axis]) - set(family[axis]))
            if missing:
                oracle = reject_oracle(
                    "CLEANUP_BUDGET_EXCEEDED",
                    reason,
                    value["owner_type_id"],
                    public_axis,
                    missing[0],
                )
                return "REJECT", oracle["primary_diagnostic"], None, oracle
    return (
        "ADMIT",
        None,
        {
            "declaration_mode": mode,
            "family_root_type_id": family_root_type_id,
            "declared_envelope": declared,
            "computed_envelope": computed,
            "effective_envelope": effective,
            "local_subset_proven": True,
            "family_subset_proven": True,
            "compatibility": "COMPATIBLE",
        },
        None,
    )


def positive_projection_matches(value: dict[str, Any], derived: dict[str, Any] | None) -> bool:
    if derived is None:
        return False
    claimed = value["claimed_projection"]
    return all(claimed[key] == expected for key, expected in derived.items())


def mutation_base() -> dict[str, Any]:
    return {
        "absence_mode": "IMPLICIT_EXACT_ROOT",
        "effects_item_count": 1,
        "raw_effect_ids": ["effect:audit", "effect:io"],
        "errors_type_kind": "ERROR_SET",
        "required_contribution_ids": ["type:Base", "field:handle", "decl:cleanup"],
        "actual_contribution_ids": ["type:Base", "field:handle", "decl:cleanup"],
        "recomputed": {"recoverable_error_ids": ["error:CloseError"], "effect_ids": ["effect:audit", "effect:io"]},
        "effective": {"recoverable_error_ids": ["error:CloseError", "error:FlushError"], "effect_ids": ["effect:audit", "effect:io"]},
        "family": {"recoverable_error_ids": ["error:CloseError", "error:FlushError"], "effect_ids": ["effect:audit", "effect:io"]},
        "role": "CHILD",
        "admission_relation": "SUBSET",
        "expected_failure_origin_order": ["type:Base", "field:handle", "decl:cleanup"],
        "actual_failure_origin_order": ["type:Base", "field:handle", "decl:cleanup"],
        "failure_axis_order": ["RECOVERABLE_ERROR", "EFFECT"],
        "diagnostic_emission_count": 1,
    }


def mutation_errors(model: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    if model["absence_mode"] != "IMPLICIT_EXACT_ROOT":
        errors.add("ABSENCE_MODE")
    if model["effects_item_count"] > 1:
        errors.add("ITEM_DUPLICATE")
    if len(model["raw_effect_ids"]) != len(set(model["raw_effect_ids"])):
        errors.add("IDENTITY_DUPLICATE")
    if model["errors_type_kind"] != "ERROR_SET":
        errors.add("ERROR_SET_KIND")
    if model["actual_contribution_ids"] != model["required_contribution_ids"]:
        errors.add("CONTRIBUTION_SET")
    if model["admission_relation"] != "SUBSET":
        errors.add("SUBSET_NOT_EQUALITY")
    if model["role"] == "CHILD" and not subset(model["effective"], model["family"]):
        errors.add("FAMILY_SUBSET")
    if model["actual_failure_origin_order"] != model["expected_failure_origin_order"]:
        errors.add("FAILURE_ORIGIN_ORDER")
    if model["failure_axis_order"] != ["RECOVERABLE_ERROR", "EFFECT"] or model["diagnostic_emission_count"] != 1:
        errors.add("DIAGNOSTIC_EMISSION")
    return errors


Mutator = Callable[[dict[str, Any]], None]


def mutations() -> dict[str, tuple[str, Mutator]]:
    return {
        "M01_ABSENCE_FORGED_NOT_EXACT": ("ABSENCE_MODE", lambda m: m.__setitem__("absence_mode", "EXPLICIT_HEADER")),
        "M02_DUPLICATE_AXIS_ADMITTED": ("ITEM_DUPLICATE", lambda m: m.__setitem__("effects_item_count", 2)),
        "M03_DUPLICATE_NORMALIZED_ID_ADMITTED": ("IDENTITY_DUPLICATE", lambda m: m.__setitem__("raw_effect_ids", ["effect:io", "effect:io"])),
        "M04_NON_ERROR_SET_ADMITTED": ("ERROR_SET_KIND", lambda m: m.__setitem__("errors_type_kind", "NON_ERROR_SET")),
        "M05_DROP_BASE_CONTRIBUTION": ("CONTRIBUTION_SET", lambda m: m.__setitem__("actual_contribution_ids", ["field:handle", "decl:cleanup"])),
        "M06_DROP_FIELD_CONTRIBUTION": ("CONTRIBUTION_SET", lambda m: m.__setitem__("actual_contribution_ids", ["type:Base", "decl:cleanup"])),
        "M07_DROP_HOOK_CONTRIBUTION": ("CONTRIBUTION_SET", lambda m: m.__setitem__("actual_contribution_ids", ["type:Base", "field:handle"])),
        "M08_REQUIRE_EQUALITY_INSTEAD_OF_SUBSET": ("SUBSET_NOT_EQUALITY", lambda m: m.__setitem__("admission_relation", "EQUALITY")),
        "M09_ALLOW_CHILD_EFFECT_WIDEN": ("FAMILY_SUBSET", lambda m: m.__setitem__("effective", {"recoverable_error_ids": ["error:CloseError"], "effect_ids": ["effect:audit", "effect:io", "effect:net"]})),
        "M10_ALLOW_CHILD_ERROR_WIDEN": ("FAMILY_SUBSET", lambda m: m.__setitem__("effective", {"recoverable_error_ids": ["error:CloseError", "error:FlushError", "error:NetError"], "effect_ids": ["effect:audit", "effect:io"]})),
        "M11_WRONG_FIRST_FAILURE_ORIGIN_ORDER": ("FAILURE_ORIGIN_ORDER", lambda m: m.__setitem__("actual_failure_origin_order", ["decl:cleanup", "field:handle", "type:Base"])),
        "M12_BATCH_EMIT_OR_WRONG_WITHIN_ORIGIN_AXIS": ("DIAGNOSTIC_EMISSION", lambda m: (m.__setitem__("failure_axis_order", ["EFFECT", "RECOVERABLE_ERROR"]), m.__setitem__("diagnostic_emission_count", 2))),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[dict[str, Any]] = []

    def emit(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})

    schema = load_json(root, "schemas/language/cleanup-budget-envelope-input-r1.schema.json")
    contract = load_json(root, "spec/contracts/cleanup-budget-algebra-r1.json")
    fixtures = load_json(root, "tests/fixtures/current/cleanup-budget-algebra-r1.json")
    shape_errors = input_shape_errors(fixtures)
    emit(
        "CBA-V01_SCHEMA_AND_CONTRACT_CLOSED",
        local_refs_closed(schema)
        and contract["gap"]["gap_id"] == "IR-OWN-P1-021"
        and not shape_errors,
        {"defs": len(schema.get("$defs", {})), "fixture_shape_errors": shape_errors},
    )

    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    corpus = (root / "examples/guide/review-corpus.md").read_text(encoding="utf-8")
    cleanup_example = corpus.split("## EX-R51a1-043", 1)[1].split("\n## ", 1)[0]
    emit(
        "CBA-V02_SURFACE_AND_CANONICAL_EXAMPLE",
        'CleanupBudgetClause ::= "cleanup" "budget" "{" CleanupBudgetItem* "}" ;' in grammar
        and 'EffectsBudget ::= "effects" "{" IdentifierList? "}" ;' in grammar
        and "effects { io }" in cleanup_example
        and "effects io\n}" not in cleanup_example,
        {"grammar_change_count": contract["scope_fence"]["grammar_change_count"]},
    )

    derived_rows: list[dict[str, Any]] = []
    oracle_by_case = {
        row["case_id"]: {key: value for key, value in row.items() if key != "case_id"}
        for row in fixtures["diagnostic_oracles"]
    }
    for row in fixtures["cases"]:
        outcome, diagnostic, projection, oracle = derive(row["input"])
        oracle_match = outcome != "REJECT" or oracle == oracle_by_case.get(row["case_id"])
        derived_rows.append({"case_id": row["case_id"], "outcome": outcome, "diagnostic": diagnostic, "projection_match": outcome != "ADMIT" or positive_projection_matches(row["input"], projection), "oracle_match": oracle_match, "expected_outcome": row["expected_outcome"], "expected_diagnostic": row["expected_diagnostic_or_null"]})
    emit("CBA-V03_TYPED_DECISION_MATRIX", all(row["outcome"] == row["expected_outcome"] and row["diagnostic"] == row["expected_diagnostic"] and row["projection_match"] and row["oracle_match"] for row in derived_rows), derived_rows)

    emit("CBA-V04_NORMALIZATION_ALGEBRA", contract["normalization"]["union"] == "finite commutative associative idempotent set union" and contract["normalization"]["never_error_set_members"] == [] and contract["normalization"]["empty_effect_row_members"] == [] and not contract["normalization"]["defects_are_error_members"] and not contract["normalization"]["cancellation_is_error_member"], contract["normalization"])
    emit("CBA-V05_ABSENCE_AND_EXPLICIT_DEFAULTS", contract["declaration_modes"]["IMPLICIT_EXACT_ROOT"].startswith("a non-inheritance class") and contract["surface"]["missing_effects_item"] == "EMPTY_EFFECT_ROW" and contract["surface"]["missing_errors_item"] == "NEVER_EMPTY_ERROR_SET" and contract["surface"]["empty_explicit_block"] == "EXPLICIT_EMPTY_ENVELOPE", contract["declaration_modes"])
    emit("CBA-V06_TRANSITIVE_COMPOSITION", contract["composition"]["source_kinds"] == ["BASE_OWNER", "FIELD_OWNER", "OWNER_DEF_CLEANUP"] and contract["composition"]["semantic_combination"].startswith("set union") and contract["composition"]["conditional_reachability"].startswith("include every statically reachable"), contract["composition"])
    emit("CBA-V07_INHERITANCE_SUBSTITUTABILITY", contract["inheritance"]["resource_root"].startswith("same-module sealed root") and contract["inheritance"]["implicit_child"].startswith("inherits the exact") and contract["inheritance"]["explicit_child"].startswith("may equal or narrow") and contract["inheritance"]["child_widening"] == "FORBIDDEN", contract["inheritance"])

    lifecycle = load_json(root, "spec/contracts/construction-cleanup-state-r1.json")
    expected_abort = [
        "CONSUME_CONSTRUCTION_TOKEN",
        "PRESERVE_TRIGGERING_OUTCOME_AS_PRIMARY",
        "CURRENT_CLASS_LIVE_FIELDS_REVERSE_ACQUISITION",
        "COMMITTED_BASE_SEGMENTS_RECURSIVE",
        "APPEND_CLEANUP_FAILURES_AS_SUPPRESSED",
        "RETIRE_SESSION_OWNERS_AND_TOKENS",
        "ENTER_FAILED_UNPUBLISHED",
    ]
    expected_live = [
        "CONSUME_WHOLE_OBJECT_CLEANUP_ONCE_GUARD",
        "MOST_DERIVED_DEF_HASH_CLEANUP_IF_PRESENT",
        "MOST_DERIVED_FIELDS_REVERSE_ACQUISITION",
        "DIRECT_BASE_SEGMENT_RECURSIVE",
        "ROOT_BASE_SEGMENT_TERMINAL",
    ]
    emit(
        "CBA-V08_RUNTIME_ORDER_UNCHANGED",
        lifecycle["construction_abort"]["ordered_steps"] == expected_abort
        and lifecycle["construction_abort"]["most_derived_whole_cleanup_hook_count"] == 0
        and lifecycle["live_object_cleanup"]["ordered_steps"] == expected_live
        and lifecycle["live_object_cleanup"]["continue_after_cleanup_failure"] is True
        and lifecycle["live_object_cleanup"]["automatic_cleanup_suppressed_by_user_hook"] is False
        and contract["dynamic_semantics"]["budget_changes_failure_order"] is False
        and contract["dynamic_semantics"]["budget_evaluation_count"] == 0,
        {"abort": lifecycle["construction_abort"], "live": lifecycle["live_object_cleanup"]},
    )

    diagnostics = rows_from_chunks(root, "spec/diagnostics/catalog/chunks")
    predicates = rows_from_chunks(root, "spec/types/predicates/chunks")
    relations = rows_from_chunks(root, "spec/diagnostics/relations/chunks")
    diagnostic_by_id = {row.get("diagnostic_id"): row for row in diagnostics}
    predicate = next((row for row in predicates if row.get("predicate_id") == "CleanupBudgetEnvelopeAdmitted"), None)
    predicate_relations = [row for row in relations if row.get("predicate_id") == "CleanupBudgetEnvelopeAdmitted"]
    expected_predicate_diagnostics = EXPECTED_DIAGNOSTICS - {"CLEANUP_BUDGET_BODY_POSITION_REMOVED", "CLEANUP_BUDGET_CAMELCASE_REMOVED"}
    expected_relations = {
        ("CLEANUP_BUDGET_EXCEEDED", "primary"),
        ("CLEANUP_BUDGET_DUPLICATE", "secondary"),
        ("CLEANUP_BUDGET_ERRORS_REQUIRES_ERROR_SET", "secondary"),
        ("RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT", "secondary"),
    }
    observed_relations = {(row.get("diagnostic_id"), row.get("relation")) for row in predicate_relations}
    emit("CBA-V09_DIAGNOSTIC_AND_PREDICATE_BINDING", EXPECTED_DIAGNOSTICS.issubset(diagnostic_by_id) and all(diagnostic_by_id[diag]["diagnostic_status"] == "active" for diag in EXPECTED_DIAGNOSTICS) and predicate is not None and set(predicate.get("diagnostic_refs", [])) == expected_predicate_diagnostics and observed_relations == expected_relations, {"predicate": predicate is not None, "relations": sorted(observed_relations)})

    hir = load_json(root, "schemas/language/canonical-hir-h1.schema.json")
    hir_text = json.dumps(hir, sort_keys=True)
    identity_catalog = load_json(root, "spec/contracts/hir-h1-identity-catalog.json")
    identity_contract = identity_catalog["type_header_cleanup_budget_contract"]
    emit("CBA-V10_HIR_TYPED_ENVELOPE", "TypeHeaderCleanupBudgetRecord" in hir_text and "cleanup_budget_envelopes" in hir_text and "cleanup_budget_id" in hir_text and identity_contract["new_catalog_identity_row_count"] == 0 and identity_contract["structural_id_domain_binding_count"] == 1, {"hir_schema_revision": hir["properties"]["schema_revision"]["const"], "identity_contract": identity_contract})

    mir = load_json(root, "schemas/language/deeplus-mir.schema.json")
    mir_text = json.dumps(mir, sort_keys=True)
    lowering = load_json(root, "spec/contracts/hir-mir-lowering-registry.json")
    operation_kinds = mir.get("$defs", {}).get("operationKind", {}).get("enum", [])
    op_count = len(operation_kinds)
    lowering_contract = lowering["type_header_cleanup_budget_projection_contract"]
    emit("CBA-V11_MIR_AND_LOWERING_REUSE", "cleanup_budget_envelope_table" in mir_text and "cleanup_budget_id" in mir.get("$defs", {}).get("constructionLifecyclePayload", {}).get("required", []) and lowering_contract["new_operation_kind_count"] == 0 and lowering_contract["p1_022_decided"] is False and set(lowering_contract["reused_operation_kinds"]) <= set(operation_kinds), {"op_count": op_count, "lowering_contract": lowering_contract})

    api = load_json(root, "schemas/language/module-api-digest.schema.json")
    api_text = json.dumps(api, sort_keys=True)
    api_fence = api["x-deeplus-type-header-cleanup-budget-contract"]
    emit("CBA-V12_MODULE_API_RESIDUE", "typeHeaderCleanupBudgetResidue" in api_text and "cleanup_budget_envelope" in api_text and set(api_fence["compiler_local_fields_forbidden"]) == set(contract["module_api"]["compiler_local_fields_forbidden"]) and api_fence["product_support"] == "NOT_RUN", api_fence)

    mutation_results = []
    for mutation_id, (expected_error, mutator) in mutations().items():
        model = mutation_base()
        mutator(model)
        observed = mutation_errors(model)
        mutation_results.append({"mutation_id": mutation_id, "expected_error": expected_error, "observed": sorted(observed)})
    case_counts = Counter(row["class"] for row in fixtures["cases"])
    case_counts["mutation"] = len(fixtures["mutations"])
    emit("CBA-V13_FIXTURE_AND_MUTATION_MATRIX", dict(case_counts) == EXPECTED_CASE_COUNTS and set(mutations()) == {row["mutation_id"] for row in fixtures["mutations"]} and all(row["expected_error"] in row["observed"] for row in mutation_results), {"counts": dict(case_counts), "mutations": mutation_results})

    coherence = load_json(root, "spec/contracts/language-coherence-current-integrity-r1.json")
    fences = fixtures["global_fences"]
    emit("CBA-V14_GLOBAL_EVIDENCE_FENCES", fences == {"semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "separate_actions": "4_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION"} and coherence["semantic_p0"] == 0 and len(coherence["feature_p1_ids"]) == 22 and len(coherence["separate_action_ids"]) == 4 and len(coherence["product_lanes"]) == 15 and coherence["product_execution"] == "NOT_RUN", fences)

    failed = [row for row in checks if row["result"] != "PASS"]
    receipt = {
        "schema": "deeplus.cleanup-budget-algebra-validation-receipt/r1",
        "revision": "R33-CLEANUP-BUDGET-ALGEBRA-R1",
        "result": "PASS" if not failed else "FAIL",
        "checks": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "mutation_count": len(mutations()),
        "mutation_rejections": sum(row["expected_error"] in row["observed"] for row in mutation_results),
        "new_mir_operation_kind_count": contract["scope_fence"]["new_mir_operation_kind_count"],
        "new_active_diagnostic_id_count": len(contract["diagnostic_policy"]["new_active_ids"]),
        "feature_p1": "22_OPEN_UNCHANGED",
        "separate_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_mutation": "NOT_PERFORMED",
        "check_results": checks,
    }
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
