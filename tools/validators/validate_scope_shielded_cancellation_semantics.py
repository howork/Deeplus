#!/usr/bin/env python3
"""Validate the bounded R81 @scope shielded design/static closure."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/scope-shielded-cancellation-semantics-r1.json"
SCHEMA_REL = "schemas/language/scope-shielded-cancellation-semantics-r1.schema.json"
FIXTURE_REL = "tests/fixtures/current/scope-shielded-cancellation-semantics-r1.json"
ACTOR_REL = "spec/contracts/actor-concurrency-coherence.json"
ACTOR_FIXTURE_REL = "tests/fixtures/current/actor-concurrency-coherence-r1.json"
HIR_REL = "schemas/language/canonical-hir-h1.schema.json"
MIR_RESP_REL = "schemas/language/mir-responsibility.schema.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
LOWERING_REL = "spec/contracts/hir-mir-lowering-registry.json"
FEATURE_REL = "spec/features/catalog/chunks/part-0001.json"
DIAGNOSTIC_REL = "spec/diagnostics/catalog/chunks/part-0033.json"
PREDICATE_REL = "spec/types/predicates/chunks/part-0026.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
LANGUAGE_REL = "spec/language.md"
TYPE_REL = "spec/types/type-system.md"
MIR_REL = "spec/mir/semantics.md"
DOC_REL = "docs/grammar-reference/13-async-tasks-actors-and-concurrency.md"
DECISION_REL = "decisions/language/Design_Deeplus_Scope_Shielded_Cancellation_Semantics_R1.md"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(case: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    modifiers = case.get("modifiers", [])
    if len(modifiers) != len(set(modifiers)):
        return None, "DUPLICATE_MODIFIER"
    if "cancellable" in modifiers and "shielded" in modifiers:
        return None, "CONFLICTING_CANCELLATION_MODE"
    if "cancellable" in modifiers and case.get("inside_active_shield"):
        return None, "CANCELLABLE_INSIDE_SHIELD"
    if ({"cancellable", "shielded"} & set(modifiers)) and not case.get(
        "context_has_cancellation_axis"
    ):
        return None, "CANCELLATION_CONTEXT_REQUIRED"

    normalized = [item for item in ("isolated", "cancellable", "shielded") if item in modifiers]
    depth = case.get("nested_depth", 1)
    request = case.get("request_site") != "NONE"
    phases = ["shield_enter"] * depth
    if request:
        phases.append("observation_deferred")
    for _ in range(depth):
        phases.extend(["scope_cleanup_complete", "shield_exit"])

    body_outcome = case.get("body_outcome")
    cleanup_outcome = case.get("cleanup_outcome")
    selected_failure = cleanup_outcome if cleanup_outcome != "NORMAL" else body_outcome
    observe = 0
    acknowledge = 0
    pending = False
    if selected_failure in {"ERROR", "DEFECT"}:
        terminal = selected_failure
        pending = request and selected_failure == "ERROR"
    elif request:
        phases.extend(["cancel_observe", "cancel_acknowledge"])
        observe = acknowledge = 1
        terminal = "CANCELLATION"
    else:
        terminal = "NORMAL"
    return {
        "normalized_modifiers": normalized,
        "phases": phases,
        "cleanup_execution_count": depth,
        "observe_count": observe,
        "acknowledge_count": acknowledge,
        "terminal_outcome": terminal,
        "pending_after_exit": pending,
    }, None


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = copy.deepcopy(contract_override) if contract_override is not None else load(root / CONTRACT_REL)
    fixture = copy.deepcopy(fixture_override) if fixture_override is not None else load(root / FIXTURE_REL)
    schema = load(root / SCHEMA_REL)
    actor = load(root / ACTOR_REL)
    actor_fixture = load(root / ACTOR_FIXTURE_REL)
    hir = load(root / HIR_REL)
    mir_resp = load(root / MIR_RESP_REL)
    frontend = load(root / FRONTEND_REL)
    lowering = load(root / LOWERING_REL)
    features = load(root / FEATURE_REL)
    diagnostics = load(root / DIAGNOSTIC_REL)
    predicates = load(root / PREDICATE_REL)
    trace_rows = load(root / TRACE_REL)
    language = (root / LANGUAGE_REL).read_text(encoding="utf-8")
    types = (root / TYPE_REL).read_text(encoding="utf-8")
    mir = (root / MIR_REL).read_text(encoding="utf-8")
    docs = (root / DOC_REL).read_text(encoding="utf-8")
    decision = (root / DECISION_REL).read_text(encoding="utf-8")

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(contract)
        except Exception as exc:  # noqa: BLE001
            errors.append("G01:SCHEMA_BINDING:" + type(exc).__name__)

    surface = contract.get("surface_contract", {})
    require(
        surface.get("current_modifiers") == ["isolated", "cancellable", "shielded"]
        and surface.get("cancellation_modes")
        == {
            "omitted": "INHERIT",
            "cancellable": "OBSERVE",
            "shielded": "DEFER_TO_OUTERMOST_SHIELD_EXIT",
        }
        and surface.get("duplicate_modifier_allowed") is False
        and surface.get("cancellable_with_shielded_allowed") is False
        and surface.get("isolated_with_cancellation_mode_allowed") is True
        and surface.get("formatter_order") == ["isolated", "cancellable_or_shielded"],
        "G02",
        "SURFACE_AND_COMBINATION_EXACT",
    )

    admission = contract.get("static_admission", {})
    require(
        admission.get("predicate_id") == "ScopeCancellationPlanAdmitted"
        and admission.get("requires_cancellation_axis_for") == ["cancellable", "shielded"]
        and admission.get("reason_precedence")
        == ["DUPLICATE_MODIFIER", "CONFLICTING_CANCELLATION_MODE", "CANCELLABLE_INSIDE_SHIELD", "CANCELLATION_CONTEXT_REQUIRED"]
        and admission.get("diagnostics")
        == {
            "DUPLICATE_MODIFIER": "SCOPE_MODIFIER_DUPLICATE",
            "CONFLICTING_CANCELLATION_MODE": "SCOPE_CANCELLATION_MODE_CONFLICT",
            "CANCELLABLE_INSIDE_SHIELD": "SCOPE_CANCELLABLE_INSIDE_SHIELD_FORBIDDEN",
            "CANCELLATION_CONTEXT_REQUIRED": "SCOPE_CANCELLATION_CONTEXT_REQUIRED",
        }
        and admission.get("rejected_hir_residue_count") == 0
        and admission.get("rejected_mir_residue_count") == 0,
        "G03",
        "STATIC_ADMISSION_EXACT",
    )

    observed = {"positive": 0, "boundary": 0, "reject": 0}
    for case in fixture.get("cases", []):
        kind = case.get("class")
        if kind in observed:
            observed[kind] += 1
        result, reason = evaluate_case(case)
        if kind in {"positive", "boundary"}:
            require(reason is None and result == case.get("expected"), "G04", f"ADMITTED_CASE:{case.get('id')}")
        elif kind == "reject":
            expected_reason = case.get("expected_reason")
            require(
                result is None
                and reason == expected_reason
                and case.get("diagnostic") == admission.get("diagnostics", {}).get(expected_reason),
                "G04",
                f"REJECT_CASE:{case.get('id')}",
            )
    counts = fixture.get("expected_counts", {})
    require(
        len(fixture.get("cases", [])) == counts.get("cases") == 11
        and observed == {"positive": 3, "boundary": 4, "reject": 4}
        and counts.get("semantic_p0") == 0
        and counts.get("feature_p1") == 22
        and counts.get("product_lanes") == 15
        and counts.get("product_executed") == 0,
        "G04",
        "FIXTURE_COUNTS_AND_GOVERNANCE",
    )

    dynamic = contract.get("dynamic_semantics", {})
    require(
        dynamic.get("inside_observed_count") == 0
        and dynamic.get("inside_acknowledged_count") == 0
        and dynamic.get("scope_cleanup") == "RUN_EXACTLY_ONCE_WHILE_CURRENT_SCOPE_REMAINS_SHIELDED"
        and dynamic.get("nested_exit") == "INNER_EXIT_NEVER_OBSERVES_WHILE_PARENT_SHIELD_REMAINS_ACTIVE"
        and dynamic.get("cancellation_state_order")
        == ["requested", "observed", "acknowledged", "cancellation_cleanup_complete", "terminal_cancelled"]
        and dynamic.get("cancellation_to_error_conversion_count") == 0
        and dynamic.get("cleanup_bypass_count") == 0
        and dynamic.get("terminal_cancelled_fabrication_after_defect_count") == 0,
        "G05",
        "DYNAMIC_STATE_AND_PRECEDENCE_EXACT",
    )

    rules = {row.get("rule_id"): row.get("contract", {}) for row in actor.get("rules", [])}
    actor_states = next(
        (
            row.get("descriptor", {}).get("states")
            for row in actor_fixture.get("positive", [])
            if row.get("fixture_id") == "ACC-P-010-COOPERATIVE-CANCELLATION-CLEANUP"
        ),
        None,
    )
    r13 = rules.get("ACC-R013", {})
    require(
        rules.get("ACC-R012", {}).get("minimum_state_order")
        == ["requested", "observed", "acknowledged", "cleanup_complete", "terminal_cancelled"]
        and actor_states == ["requested", "observed", "acknowledged", "cleanup_complete", "terminal_cancelled"]
        and r13.get("shielded", {}).get("observation") == "defer until the outermost shield exits after scope-local cleanup"
        and r13.get("combination_admission", {}).get("cancellable_with_shielded") == "reject",
        "G06",
        "ACTOR_CANCELLATION_AND_SCOPE_RULES_BOUND",
    )

    defs = hir.get("$defs", {})
    cleanup = defs.get("CleanupScopePlan", {})
    cleanup_text = json.dumps(cleanup, sort_keys=True)
    scope_plan = defs.get("ScopeCancellationPlan", {})
    frontend_scope = frontend.get("scope_modifier_contract", {})
    require(
        "scope_cancellation_plan" in cleanup_text
        and "scope_cancellation_plan" in cleanup.get("allOf", [{}, {}])[1].get("required", [])
        and scope_plan.get("additionalProperties") is False
        and scope_plan.get("required")
        == [
            "normalized_modifiers",
            "cancellation_mode",
            "execution_context_id_or_null",
            "parent_shield_scope_id_or_null",
            "exit_observation_policy",
            "cleanup_fence",
            "failure_precedence",
        ]
        and frontend_scope.get("ast_cancellation_modes")
        == ["INHERIT", "OBSERVE", "DEFER_TO_OUTERMOST_SHIELD_EXIT"]
        and frontend_scope.get("source_order_selects_semantics") is False,
        "G07",
        "CST_AST_HIR_PLAN_BOUND",
    )

    control_refs = json.dumps(mir_resp.get("properties", {}).get("control_events", {}), sort_keys=True)
    mir_event = mir_resp.get("$defs", {}).get("scopeCancellationEvent", {})
    row = next((item for item in lowering.get("rows", []) if item.get("row_id") == "HM-LR-TOP-021"), {})
    require(
        "scopeCancellationEvent" in control_refs
        and mir_event.get("properties", {}).get("phase", {}).get("enum")
        == ["shield_enter", "observation_deferred", "scope_cleanup_complete", "shield_exit", "cancel_observe", "cancel_acknowledge"]
        and row.get("operation_plan", [{}])[0].get("input_roles")
        == ["cleanup_scope_plan", "scope_cancellation_plan", "cancellation_state"]
        and row.get("operation_plan", [{}])[0].get("output_roles")
        == ["cleanup_region", "scope_cancellation_state"]
        and row.get("token_inputs") == [{"token_kind": "CANCELLATION", "token_role": "cancellation_state", "cardinality": 1}]
        and row.get("token_outputs") == [{"token_kind": "CANCELLATION", "token_role": "cancellation_state", "cardinality": 1}],
        "G08",
        "MIR_EVENT_AND_LOWERING_TOKEN_BOUND",
    )

    feature = next((item for item in features if item.get("feature_id") == "async_concur_control"), {})
    diag_ids = {item.get("diagnostic_id") for item in diagnostics}
    predicate = next((item for item in predicates if item.get("predicate_id") == "ScopeCancellationPlanAdmitted"), {})
    trace = next((item for item in trace_rows if item.get("feature_id") == "async_concur_control"), {})
    dynamic_trace = next((item for item in trace.get("stages", []) if item.get("stage") == "DYNAMIC_LOWERING"), {})
    require(
        feature.get("status_enum") == "STABLE_DESIGN"
        and "ScopeCancellationPlanAdmitted" in feature.get("normative_trace_refs", {}).get("predicates", [])
        and {"SCOPE_MODIFIER_DUPLICATE", "SCOPE_CANCELLATION_MODE_CONFLICT", "SCOPE_CANCELLABLE_INSIDE_SHIELD_FORBIDDEN", "SCOPE_CANCELLATION_CONTEXT_REQUIRED"} <= diag_ids
        and predicate.get("predicate_maturity") == "design_algorithm"
        and predicate.get("emission_eligible") is True
        and dynamic_trace.get("disposition") == "BOUND_DIRECT"
        and CONTRACT_REL in feature.get("artifact_trace_refs", []),
        "G09",
        "REGISTRY_AND_TRACE_BINDING",
    )
    require(
        "A Stable `shielded` scope is a lexical cancellation-observation fence" in language
        and "Scope cancellation plans" in mir
        and "ScopeCancellationPlanAdmitted" in types
        and "가장 바깥쪽 `shielded` 범위" in docs
        and "LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED" in decision,
        "G09",
        "NORMATIVE_TEXT_CLOSURE",
    )

    require(
        contract.get("governance")
        == {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "github_publication": "NOT_PERFORMED_FOR_R81",
        },
        "G10",
        "GOVERNANCE_FENCE",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    print(
        json.dumps(
            {
                "schema": "deeplus.r81-scope-shielded-cancellation-validation-receipt/r1",
                "result": "PASS" if not errors else "FAIL",
                "checks": 10,
                "failed": errors,
                "semantic_p0": 0,
                "feature_p1": "22_OPEN_UNCHANGED",
                "product_lanes": "15_OF_15_NOT_RUN",
                "product_execution": "NOT_RUN",
            },
            separators=(",", ":"),
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
