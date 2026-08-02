#!/usr/bin/env python3
"""Focused static validator for the R31 closure-capture-plan candidate.

This validator checks design artifacts and deterministic machine projections.
It does not execute a compiler/runtime or make a product-support claim.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

PREDICATE_IDS = {
    "ClosureCaptureDescriptorAdmitted",
    "ClosureCaptureDescriptorAdmittedCurrentGate",
}
CAPTURE_MODES = {
    "BORROW",
    "INOUT",
    "MOVE",
    "COPY",
    "CLONE",
    "DEEP",
    "ONCE",
    "INIT_LET",
    "INIT_VAR",
}
REQUIRED_MIR_OPERATIONS = {
    "BUILDER_BEGIN",
    "BUILDER_STAGE",
    "BUILDER_COMMIT",
    "MOVE_RESERVE",
    "MOVE_CANCEL",
    "PLACE_MOVE",
    "LOAN_BEGIN_SHARED",
    "LOAN_BEGIN_EXCLUSIVE",
    "LOAN_END",
    "CLEANUP_REGISTER",
    "CLEANUP_DISARM",
    "CLOSURE_MAKE",
}
EXPECTED_FIXTURE_COUNTS = {
    "positive": 9,
    "boundary": 3,
    "negative": 12,
    "mutation": 11,
    "total": 35,
}
EXPECTED_DIAGNOSTICS = {
    "FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE",
    "CONCUR_LOCAL_ASYNC_CAPTURE_NOT_ADMITTED",
    "RESOLVER_SCOPE_TREE_INVALID",
    "OWNERSHIP_MODE_ADMISSION_FAILED",
    "BORROW_ESCAPE_OWNER_REGION",
    "CLOSURE_INOUT_CAPTURE_REQUIRES_SCOPED_MUT",
    "INOUT_ALIAS_CONFLICT",
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def rows_from_chunks(root: Path, rel: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / rel).glob("part-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            rows.extend(payload)
            continue
        candidates = [value for value in payload.values() if isinstance(value, list)]
        if len(candidates) != 1:
            raise ValueError(f"cannot identify row array in {path}")
        rows.extend(candidates[0])
    return rows


def decide_capture_input(value: dict[str, Any]) -> tuple[str, str | None]:
    """Reference decision function for the four typed catalog fixtures."""

    if value.get("product_support") != "NOT_RUN":
        return "REJECT", "PRODUCT_SUPPORT_OVERCLAIM"
    items = value.get("capture_items", [])
    state = value.get("capture_list_state")
    if state == "PRESENT_NONEMPTY" and not items:
        return "REJECT", "RESOLVER_SCOPE_TREE_INVALID"
    if state in {"ABSENT", "PRESENT_EMPTY"} and items:
        return "REJECT", "RESOLVER_SCOPE_TREE_INVALID"
    if [item.get("source_ordinal") for item in items] != list(range(len(items))):
        return "REJECT", "RESOLVER_SCOPE_TREE_INVALID"
    binders = [item.get("binder_name") for item in items]
    fields = [item.get("capture_field_id") for item in items]
    places = [
        item.get("source_place_id_or_null")
        for item in items
        if item.get("source_place_id_or_null") is not None
    ]
    if (
        len(binders) != len(set(binders))
        or len(fields) != len(set(fields))
        or len(places) != len(set(places))
    ):
        return "REJECT", "RESOLVER_SCOPE_TREE_INVALID"
    if any(item.get("evaluation_count") != 1 for item in items):
        return "REJECT", "OWNERSHIP_MODE_ADMISSION_FAILED"

    profile = value.get("callable_profile", {})
    owner_kind = value.get("owner_kind")
    for item in items:
        mode = item.get("normalized_mode")
        if mode not in CAPTURE_MODES:
            return "REJECT", "OWNERSHIP_MODE_ADMISSION_FAILED"
        if mode == "DEEP":
            return "REJECT", "FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE"
        if owner_kind == "CONCUR_LOCAL_ASYNC" and mode != "COPY":
            return "REJECT", "CONCUR_LOCAL_ASYNC_CAPTURE_NOT_ADMITTED"
        if mode == "BORROW" and value.get("escaping"):
            return "REJECT", "BORROW_ESCAPE_OWNER_REGION"
        if mode == "INOUT" and (
            profile.get("lifetime") != "SCOPED"
            or profile.get("environment_receiver") != "MUT"
            or profile.get("suspension") != "NONSUSPENDING"
            or value.get("escaping")
        ):
            return "REJECT", "CLOSURE_INOUT_CAPTURE_REQUIRES_SCOPED_MUT"
        if mode == "INIT_VAR" and profile.get("environment_receiver") != "MUT":
            return "REJECT", "PURE_CALLABLE_MUTABLE_CAPTURE_FORBIDDEN"
        if mode == "ONCE" and profile.get("call_right") != "ONCE":
            return "REJECT", "OWNERSHIP_MODE_ADMISSION_FAILED"
        if mode == "COPY" and (
            item.get("responsibility_rule_id_or_null") != "CopyValue"
            or item.get("responsibility_evidence_id_or_null") is None
            or item.get("trait_witness_id_or_null") is not None
        ):
            return "REJECT", "OWNERSHIP_MODE_ADMISSION_FAILED"
        if mode == "CLONE" and item.get("trait_witness_id_or_null") is None:
            return "REJECT", "OWNERSHIP_MODE_ADMISSION_FAILED"
    return "ADMIT", None


def projection_errors(model: dict[str, Any]) -> set[str]:
    """Return the violated transactional projection invariants."""

    errors: set[str] = set()
    items = model["capture_items"]
    ordinals = [item["source_ordinal"] for item in items]
    if ordinals != list(range(len(items))):
        errors.add("SOURCE_ORDINAL")
    if model["evaluation_order"] != ordinals:
        errors.add("CAPTURE_REORDER")
    if any(item["evaluation_count"] != 1 for item in items):
        errors.add("EVALUATION_COUNT")
    fields = [item["capture_field_id"] for item in items]
    places = [item["source_place_id"] for item in items]
    if len(fields) != len(set(fields)) or len(places) != len(set(places)):
        errors.add("STABLE_PLACE_BINDING")
    copy_item = next(item for item in items if item["mode"] == "COPY")
    clone_item = next(item for item in items if item["mode"] == "CLONE")
    if copy_item["rule"] != "CopyValue" or copy_item["evidence_domain"] != "COPY_VALUE":
        errors.add("RESPONSIBILITY_DOMAIN")
    if clone_item["trait_witness_id_or_null"] is None:
        errors.add("CLONE_WITNESS")
    if model["rollback_order"] != list(reversed(ordinals)):
        errors.add("ROLLBACK_ORDER")
    if not model["move_reservation_cancelled"]:
        errors.add("MOVE_RESERVATION")
    if model["partial_publication_count"] != 0:
        errors.add("PARTIAL_PUBLICATION")
    if any(count != 1 for count in model["cleanup_counts"].values()):
        errors.add("CLEANUP_EXACTLY_ONCE")
    if model["product_support"] != "NOT_RUN":
        errors.add("PRODUCT_SUPPORT")
    return errors


def base_projection_model() -> dict[str, Any]:
    return {
        "capture_items": [
            {
                "source_ordinal": 0,
                "capture_field_id": "field:0:owned",
                "source_place_id": "place:owned",
                "mode": "MOVE",
                "evaluation_count": 1,
                "rule": "Move",
                "evidence_domain": "MOVE",
                "trait_witness_id_or_null": None,
            },
            {
                "source_ordinal": 1,
                "capture_field_id": "field:1:copied",
                "source_place_id": "place:copied",
                "mode": "COPY",
                "evaluation_count": 1,
                "rule": "CopyValue",
                "evidence_domain": "COPY_VALUE",
                "trait_witness_id_or_null": None,
            },
            {
                "source_ordinal": 2,
                "capture_field_id": "field:2:cloned",
                "source_place_id": "place:cloned",
                "mode": "CLONE",
                "evaluation_count": 1,
                "rule": "Clone",
                "evidence_domain": "TRAIT_WITNESS",
                "trait_witness_id_or_null": "witness:clone",
            },
        ],
        "evaluation_order": [0, 1, 2],
        "rollback_order": [2, 1, 0],
        "move_reservation_cancelled": True,
        "partial_publication_count": 0,
        "cleanup_counts": {"field:0:owned": 1, "field:2:cloned": 1},
        "product_support": "NOT_RUN",
    }


def mutation_matrix() -> dict[str, tuple[str, Any]]:
    """Return mutation id -> expected error and mutator."""

    return {
        "CAPTURE_REORDER": (
            "CAPTURE_REORDER",
            lambda m: m.__setitem__("evaluation_order", [1, 0, 2]),
        ),
        "EVALUATE_TWICE": (
            "EVALUATION_COUNT",
            lambda m: m["capture_items"][0].__setitem__("evaluation_count", 2),
        ),
        "ORDINAL_GAP": (
            "SOURCE_ORDINAL",
            lambda m: m["capture_items"][2].__setitem__("source_ordinal", 3),
        ),
        "SOURCE_PLACE_SWAP": (
            "STABLE_PLACE_BINDING",
            lambda m: m["capture_items"][1].__setitem__(
                "source_place_id", m["capture_items"][0]["source_place_id"]
            ),
        ),
        "RESPONSIBILITY_DOMAIN_SWAP": (
            "RESPONSIBILITY_DOMAIN",
            lambda m: m["capture_items"][1].__setitem__(
                "evidence_domain", "TRAIT_WITNESS"
            ),
        ),
        "CLONE_WITNESS_NULL": (
            "CLONE_WITNESS",
            lambda m: m["capture_items"][2].__setitem__(
                "trait_witness_id_or_null", None
            ),
        ),
        "ROLLBACK_NOT_REVERSE": (
            "ROLLBACK_ORDER",
            lambda m: m.__setitem__("rollback_order", [0, 1, 2]),
        ),
        "MOVE_RESERVATION_NOT_CANCELLED": (
            "MOVE_RESERVATION",
            lambda m: m.__setitem__("move_reservation_cancelled", False),
        ),
        "PARTIAL_PUBLICATION": (
            "PARTIAL_PUBLICATION",
            lambda m: m.__setitem__("partial_publication_count", 1),
        ),
        "CLEANUP_MISSING_OR_DOUBLE": (
            "CLEANUP_EXACTLY_ONCE",
            lambda m: m["cleanup_counts"].__setitem__("field:2:cloned", 2),
        ),
        "PRODUCT_LANE_FLIP": (
            "PRODUCT_SUPPORT",
            lambda m: m.__setitem__("product_support", "PASS"),
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[dict[str, Any]] = []

    def check(ok: bool, check_id: str, detail: str) -> None:
        checks.append(
            {"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail}
        )

    paths = {
        "input_schema": "schemas/language/closure-capture-plan-input-r1.schema.json",
        "contract": "spec/contracts/closure-capture-plan-r1.json",
        "fixtures": "tests/fixtures/current/closure-capture-plan-r1.json",
        "hir": "schemas/language/canonical-hir-h1.schema.json",
        "mir": "schemas/language/deeplus-mir.schema.json",
        "bridge": "spec/contracts/hir-h1-current-mir-bridge.json",
        "lowering": "spec/contracts/hir-mir-lowering-registry.json",
        "mir_registry": "spec/contracts/mir-machine-registry.json",
        "api": "schemas/language/module-api-digest.schema.json",
        "predicate_metadata": "spec/types/predicates/catalog-metadata.json",
        "fixture_metadata": "tests/conformance/checker-predicates/catalog-metadata.json",
        "feature_chunk": "spec/features/catalog/chunks/part-0003.json",
    }
    loaded = {key: load_json(root, rel) for key, rel in paths.items()}
    contract = loaded["contract"]
    fixtures = loaded["fixtures"]
    hir_defs = loaded["hir"]["$defs"]
    mir_defs = loaded["mir"]["$defs"]
    lowering = loaded["lowering"]["closure_capture_plan_lowering_contract"]
    mir_registry = loaded["mir_registry"]["closure_environment_plan_contract"]
    feature_rows = loaded["feature_chunk"]
    capture_features = [
        row for row in feature_rows
        if isinstance(row, dict)
        and row.get("feature_id") == "closure_capture_descriptor_msp"
    ] if isinstance(feature_rows, list) else []

    check(
        len(capture_features) == 1
        and capture_features[0].get("depends_on")
        == ["function_signature_exactness", "responsibility_identity_registry_r1"],
        "CCP-V00_FEATURE_DEPENDENCY",
        "closure capture explicitly depends on exact signature and responsibility identity",
    )

    check(
        loaded["input_schema"].get("additionalProperties") is False
        and loaded["input_schema"].get("x-product-compiler") == "NOT_RUN"
        and contract.get("schema") == "deeplus.closure-capture-plan/r1",
        "CCP-V01_SCHEMA_CLOSED",
        "closed input schema and exact R31 contract",
    )
    check(
        contract["identity_model"]["source_order"] == "contiguous zero-based"
        and hir_defs["ReferenceCapture"]["properties"]["source_ordinal"]["minimum"] == 0
        and mir_registry["ordering"]["source_ordinal"]
        == "ZERO_BASED_CONTIGUOUS_EXACT_SOURCE_ORDER",
        "CCP-V02_SOURCE_ORDINAL_EXACT",
        "zero-based contiguous source order is bound in contract/HIR/MIR",
    )
    check(
        contract["algorithm"]["preparation_order"]
        == "strict source ordinal, left to right, exactly once"
        and lowering["source_order_expansion"]["evaluation"]
        == "LEFT_TO_RIGHT_EXACTLY_ONCE",
        "CCP-V03_EVALUATED_ONCE",
        "left-to-right exactly-once preparation",
    )
    check(
        "CaptureFieldId" in hir_defs
        and "closureCaptureField" in mir_defs
        and contract["identity_model"]["duplicate_normalized_source_place_count"] == 0,
        "CCP-V04_STABLE_PLACE_BINDING",
        "stable field identity and duplicate-place preflight",
    )
    check(
        contract["profile_gates"]["COPY"]
        == "one exact CopyValue ResponsibilityEvidenceId"
        and contract["profile_gates"]["CLONE"]
        == "one exact Clone TraitWitnessId and visible normalized error/effect rows",
        "CCP-V05_MODE_RESPONSIBILITY_BINDING",
        "CopyValue evidence and exact Clone witness remain distinct",
    )
    check(
        contract["profile_gates"]["DEEP"].startswith("reject ")
        and contract["surface"]["capture_once_requires_explicit_callable_once"] is True
        and contract["profile_gates"]["INOUT"].startswith("#scoped#mut")
        and contract["profile_gates"]["CONCUR_LOCAL_ASYNC"].endswith("COPY-only capture plan"),
        "CCP-V06_PROFILE_GATE",
        "Deep, once, inout and concur-local async gates",
    )
    check(
        contract["algorithm"]["failure_atomicity"]["move_reservation_cancelled"] is True
        and contract["algorithm"]["failure_atomicity"]["loans_ended"] is True
        and contract["algorithm"]["failure_atomicity"]["staged_owned_values_cleaned"] is True,
        "CCP-V07_OWNER_LOAN_DISPOSITION",
        "move, loan and staged-value disposition",
    )
    check(
        contract["algorithm"]["failure_atomicity"]["rollback_order"]
        == "strict reverse acquisition order"
        and lowering["source_order_expansion"]["rollback_order"]
        == "REVERSE_ACQUISITION_ORDER",
        "CCP-V08_REVERSE_ROLLBACK",
        "reverse prepared-prefix rollback",
    )
    check(
        contract["algorithm"]["failure_atomicity"]["partial_environment_publication_count"] == 0
        and lowering["commit_and_publish"]["publication"]
        == "NO_PARTIAL_ENVIRONMENT_OR_CLOSURE_PUBLICATION"
        and lowering["commit_and_publish"]["closure_make"]
        == "INFALLIBLE_CLOSURE_MAKE_AFTER_BUILDER_COMMIT",
        "CCP-V09_ZERO_PARTIAL_PUBLICATION",
        "single environment commit before infallible closure creation",
    )
    check(
        contract["lexical_separation"]["same_place_lexical_residue_count"] == 0
        and contract["lexical_separation"]["different_place_lexical_dependency_may_coexist"] is True
        and contract["lexical_separation"]["lexical_dependency_creates_capture_event_count"] == 0,
        "CCP-V10_EXPLICIT_LEXICAL_SEPARATION",
        "explicit capture and lexical access remain orthogonal",
    )
    check(
        "ClosurePlan" in hir_defs
        and "closureEnvironmentPlan" in mir_defs
        and "closureMakePayload" in mir_defs
        and lowering["new_mir_operation_kind_count"] == 0
        and REQUIRED_MIR_OPERATIONS <= set(lowering["reused_operation_kinds"])
        and loaded["bridge"]["closure_capture_plan_contract"]["product_support"] == "NOT_RUN",
        "CCP-V11_HIR_MIR_BINDING",
        "tagged HIR capture sum and existing-op MIR transaction are bound",
    )
    api_fence = loaded["api"]["x-deeplus-closure-capture-plan-api-fence"]
    check(
        contract["global_fences"]["product_lanes"] == "15_OF_15_NOT_RUN"
        and contract["global_fences"]["github_publication"].startswith("SUSPENDED")
        and fixtures["product_support"] == "NOT_RUN"
        and api_fence["value_level_identity_export_count"] == 0
        and api_fence["product_support"] == "NOT_RUN",
        "CCP-V12_PRODUCT_NOT_RUN_FENCE",
        "15/15 product lanes and GitHub publication remain fenced",
    )

    case_counts = Counter(row["class"] for row in fixtures["cases"])
    observed_counts = dict(case_counts)
    observed_counts["total"] = len(fixtures["cases"])
    check(
        observed_counts == EXPECTED_FIXTURE_COUNTS
        and fixtures["expected_counts"] == EXPECTED_FIXTURE_COUNTS,
        "CCP-FIXTURE-COUNT",
        json.dumps(observed_counts, sort_keys=True),
    )
    check(
        len({row["case_id"] for row in fixtures["cases"]}) == 35,
        "CCP-FIXTURE-IDENTITY",
        "35 unique case identities",
    )
    fixture_diagnostics = {
        row["expected_diagnostic_or_null"]
        for row in fixtures["cases"]
        if row["expected_diagnostic_or_null"] is not None
    }
    check(
        fixture_diagnostics <= EXPECTED_DIAGNOSTICS,
        "CCP-DIAGNOSTIC-REUSE",
        f"new diagnostic count=0; used={sorted(fixture_diagnostics)}",
    )

    predicate_meta = loaded["predicate_metadata"]
    overrides = predicate_meta["input_descriptor_overrides"]
    predicate_rows = rows_from_chunks(root, "spec/types/predicates/chunks")
    check(
        predicate_meta["predicate_count"] == len(predicate_rows)
        and predicate_meta["override_count"] == len(overrides)
        and all(
            overrides[predicate_id]["input_descriptor"] == "ClosureCapturePlanInputR1"
            for predicate_id in PREDICATE_IDS
        ),
        "CCP-PREDICATE-OVERRIDE",
        "catalog count and override count are exact; two R31 predicates are typed",
    )
    catalog_rows = rows_from_chunks(root, "tests/conformance/checker-predicates/chunks")
    fixture_meta = loaded["fixture_metadata"]
    check(
        fixture_meta["fixture_count"] == len(catalog_rows)
        and fixture_meta["typed_input_fixture_count"] >= 4
        and paths["input_schema"] in fixture_meta["typed_input_schemas"],
        "CCP-TYPED-FIXTURE-METADATA",
        "catalog fixture count is exact and the R31 input schema is bound",
    )

    typed_rows = [row for row in catalog_rows if row.get("predicate_id") in PREDICATE_IDS]
    typed_results: list[str] = []
    typed_ok = len(typed_rows) == 4
    for row in typed_rows:
        outcome, diagnostic = decide_capture_input(row["decision_input"])
        expected = row["expected_decision"]
        if outcome != expected["outcome"] or diagnostic != expected["diagnostic_id_or_null"]:
            typed_ok = False
        typed_results.append(f"{row['fixture_id']}={outcome}:{diagnostic}")
    check(
        typed_ok,
        "CCP-TYPED-FIXTURE-DECISION",
        "; ".join(typed_results),
    )

    base = base_projection_model()
    check(not projection_errors(base), "CCP-PROJECTION-BASELINE", "baseline projection accepted")
    mutation_results: list[dict[str, Any]] = []
    for mutation_id, (expected_error, mutate) in mutation_matrix().items():
        candidate = copy.deepcopy(base)
        mutate(candidate)
        errors = projection_errors(candidate)
        passed = expected_error in errors
        mutation_results.append(
            {
                "mutation_id": mutation_id,
                "expected_error": expected_error,
                "observed_errors": sorted(errors),
                "result": "PASS" if passed else "FAIL",
            }
        )
    check(
        all(row["result"] == "PASS" for row in mutation_results),
        "CCP-MUTATION-MATRIX",
        f"{sum(row['result'] == 'PASS' for row in mutation_results)}/11 rejected",
    )

    failed = [row for row in checks if row["result"] == "FAIL"]
    receipt = {
        "schema": "deeplus.closure-capture-plan-static-validation-receipt/r1",
        "revision": "R31-CLOSURE-CAPTURE-PLAN-R1",
        "result": "PASS" if not failed else "FAIL",
        "evidence_level": "E2_DESIGN_STATIC",
        "check_count": len(checks),
        "passed_check_count": len(checks) - len(failed),
        "failed_check_count": len(failed),
        "mutation_count": len(mutation_results),
        "mutation_rejection_count": sum(
            row["result"] == "PASS" for row in mutation_results
        ),
        "new_mir_operation_kind_count": 0,
        "new_diagnostic_id_count": 0,
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "checks": checks,
        "mutations": mutation_results,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
