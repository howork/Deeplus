#!/usr/bin/env python3
"""Run exactly 16 in-memory mutations against the bounded R63 validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_trait_associated_static_stale_diagnostic_removal import (
    CONTRACT_REL,
    EXPLICIT_DIAGNOSTIC,
    FIXTURE_REL,
    META_REL,
    STALE,
    TARGET_FEATURE,
    TRACE_REL,
    WITNESS_DIAGNOSTIC,
    load,
    load_shards,
    validate,
)


ROOT = Path(__file__).resolve().parents[2]
Bundle = dict[str, Any]
Mutation = tuple[str, Callable[[Bundle], None]]


def fixture_case(bundle: Bundle, fixture_id: str) -> dict[str, Any]:
    return next(
        row for row in bundle["fixture"]["cases"] if row["fixture_id"] == fixture_id
    )


def diagnostic(bundle: Bundle, diagnostic_id: str) -> dict[str, Any]:
    return next(
        row
        for row in bundle["diagnostics"]
        if row["diagnostic_id"] == diagnostic_id
    )


def predicate(bundle: Bundle, predicate_id: str) -> dict[str, Any]:
    return next(
        row for row in bundle["predicates"] if row["predicate_id"] == predicate_id
    )


def primary_relation(bundle: Bundle, predicate_id: str) -> dict[str, Any]:
    return next(
        row
        for row in bundle["relations"]
        if row.get("predicate_id") == predicate_id and row.get("relation") == "primary"
    )


def target_stage(bundle: Bundle, stage: str) -> dict[str, Any]:
    row = next(
        item for item in bundle["trace"] if item["feature_id"] == TARGET_FEATURE
    )
    return next(item for item in row["stages"] if item["stage"] == stage)


def mutate_neg_candidate_count(bundle: Bundle) -> None:
    fixture_case(bundle, "CCC-R1-NEG-009")["source_or_scenario"] = (
        "explicit <T as Factory>::default with exactly three visible normalized "
        "T conforms Factory candidates"
    )


def mutate_neg_ordering(bundle: Bundle) -> None:
    fixture_case(bundle, "CCC-R1-NEG-009")["assertions"][1] = (
        "associated-item lookup runs before WitnessResolution rejects the candidates"
    )


def mutate_neg_runtime(bundle: Bundle) -> None:
    oracle = fixture_case(bundle, "CCC-R1-NEG-009")["oracle"]
    oracle["runtime_lookup_count"] = 1
    oracle["fallback_count"] = 1


def mutate_witness_relation(bundle: Bundle) -> None:
    predicate(bundle, "WitnessResolution")["active_primary_diagnostic"] = (
        EXPLICIT_DIAGNOSTIC
    )
    primary_relation(bundle, "WitnessResolution")["relation"] = "secondary"


def mutate_target_diagnostics(bundle: Bundle) -> None:
    stage = target_stage(bundle, "DIAGNOSTICS")
    stage["disposition"] = "APPLICABLE_BLOCKED_BY_GAP"
    stage["evidence_refs"].pop()


def mutate_other_trace_and_governance(bundle: Bundle) -> None:
    bundle["metadata"]["derived_counts"]["bound_direct_cells"] += 1
    bundle["metadata"]["governance"]["semantic_p0"] = 1
    bundle["metadata"]["governance"]["feature_p1"] = "21_OPEN"
    bundle["metadata"]["governance"]["product_lanes"] = "15_OF_15_PASS"
    bundle["contract"]["semantic_p0"] = 1
    bundle["contract"]["open_feature_p1"]["total"] = 21
    first_lane = next(iter(bundle["fixture"]["product_lanes"]))
    bundle["fixture"]["product_lanes"][first_lane] = "PASS"


def main() -> int:
    base: Bundle = {
        "contract": load(ROOT / CONTRACT_REL),
        "fixture": load(ROOT / FIXTURE_REL),
        "diagnostics": load_shards(ROOT, "spec/diagnostics/catalog"),
        "relations": load_shards(ROOT, "spec/diagnostics/relations"),
        "predicates": load_shards(ROOT, "spec/types/predicates"),
        "features": load_shards(ROOT, "spec/features/catalog"),
        "trace": load(ROOT / TRACE_REL),
        "metadata": load(ROOT / META_REL),
    }
    _, normal_errors = validate(ROOT)
    if normal_errors:
        print(
            json.dumps(
                {"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors},
                indent=2,
            )
        )
        return 1

    mutations: list[Mutation] = [
        (
            "STALE_FAMILY_RETAINED",
            lambda b: b["contract"]["diagnostic_families"].insert(1, STALE),
        ),
        (
            "UNRELATED_FAMILY_REMOVED",
            lambda b: b["contract"]["diagnostic_families"].pop(),
        ),
        (
            "DUPLICATE_FAMILY",
            lambda b: b["contract"]["diagnostic_families"].append(
                b["contract"]["diagnostic_families"][0]
            ),
        ),
        (
            "NEG_UNQUALIFIED",
            lambda b: fixture_case(b, "CCC-R1-NEG-009").__setitem__(
                "source_or_scenario", "T::default with two visible Factory witnesses"
            ),
        ),
        ("NEG_CANDIDATE_COUNT_NOT_TWO", mutate_neg_candidate_count),
        (
            "NEG_WRONG_OR_STALE_DIAGNOSTIC",
            lambda b: fixture_case(b, "CCC-R1-NEG-009").__setitem__(
                "diagnostic_family_or_null", STALE
            ),
        ),
        ("NEG_ORDERING_AFTER_ITEM_LOOKUP", mutate_neg_ordering),
        (
            "NEG_DOWNSTREAM_IDENTITY_SELECTED",
            lambda b: fixture_case(b, "CCC-R1-NEG-009")["oracle"].__setitem__(
                "selected_requirement_id_count", 1
            ),
        ),
        ("NEG_RUNTIME_OR_FALLBACK_NONZERO", mutate_neg_runtime),
        (
            "MUT_STALE_OR_NON_NULL_DIAGNOSTIC",
            lambda b: fixture_case(b, "CCC-R1-MUT-022").__setitem__(
                "diagnostic_family_or_null", STALE
            ),
        ),
        (
            "MUT_STRUCTURAL_DRIFT",
            lambda b: fixture_case(b, "CCC-R1-MUT-022")["assertions"].__setitem__(
                0, "mutant merges only three lookup domains"
            ),
        ),
        (
            "EXISTING_CATALOG_DIAGNOSTIC_INACTIVE_OR_MISSING",
            lambda b: diagnostic(b, WITNESS_DIAGNOSTIC).__setitem__(
                "diagnostic_status", "inactive"
            ),
        ),
        ("WITNESS_RESOLUTION_OR_PRIMARY_RELATION_DRIFT", mutate_witness_relation),
        (
            "FIXTURE_COUNT_OR_CLASS_DRIFT",
            lambda b: b["fixture"]["cases"].pop(),
        ),
        (
            "TARGET_DIAGNOSTICS_DISPOSITION_OR_EVIDENCE_DRIFT",
            mutate_target_diagnostics,
        ),
        (
            "OTHER_TRACE_ARTIFACT_COUNT_OR_P0_P1_PRODUCT_OVERCLAIM",
            mutate_other_trace_and_governance,
        ),
    ]
    if len(mutations) != 16:
        raise AssertionError(f"R63_MUTATION_COUNT:{len(mutations)}")

    results: list[dict[str, Any]] = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        _, errors = validate(
            ROOT,
            contract_override=candidate["contract"],
            fixture_override=candidate["fixture"],
            diagnostics_override=candidate["diagnostics"],
            relations_override=candidate["relations"],
            predicates_override=candidate["predicates"],
            features_override=candidate["features"],
            trace_override=candidate["trace"],
            metadata_override=candidate["metadata"],
        )
        results.append(
            {
                "mutation_id": mutation_id,
                "rejected": bool(errors),
                "first_error": errors[0] if errors else None,
            }
        )

    rejected = sum(row["rejected"] for row in results)
    passed = rejected == 16
    print(
        json.dumps(
            {
                "schema": "deeplus.trait-associated-static-stale-diagnostic-removal-mutation-validation/r1",
                "result": "PASS" if passed else "FAIL",
                "normal_path": "PASS",
                "mutation_count": 16,
                "rejected_count": rejected,
                "results": results,
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
