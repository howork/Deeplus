#!/usr/bin/env python3
"""Validate the bounded R80 interpolation format design/static closure."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/string-interpolation-format-spec-core-r1.json"
SCHEMA_REL = "schemas/language/string-interpolation-format-spec-core-r1.schema.json"
FIXTURE_REL = "tests/fixtures/current/string-interpolation-format-spec-core-r1.json"
HIR_REL = "schemas/language/canonical-hir-h1.schema.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
LOWERING_REL = "spec/contracts/hir-mir-lowering-registry.json"
FEATURE_REL = "spec/features/catalog/chunks/part-0016.json"
DIAGNOSTIC_REL = "spec/diagnostics/catalog/chunks/part-0009.json"
PREDICATE_REL = "spec/types/predicates/chunks/part-0026.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
LANGUAGE_REL = "spec/language.md"
MIR_REL = "spec/mir/semantics.md"
CURRENT_DECISIONS_REL = "decisions/language/current-decisions.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_format(text: str) -> tuple[dict[str, Any] | None, str | None]:
    if text == "":
        return None, "EMPTY_FORMAT"
    match = re.fullmatch(r"([<>^]?)([0-9]+)", text)
    if match is None:
        return None, "INVALID_GRAMMAR"
    align, digits = match.groups()
    if len(digits) > 1 and digits.startswith("0"):
        return None, "WIDTH_LEADING_ZERO"
    width = int(digits)
    if not 1 <= width <= 1_000_000:
        return None, "WIDTH_OUT_OF_RANGE"
    alignment = {"": "LEFT", "<": "LEFT", ">": "RIGHT", "^": "CENTER"}[align]
    return {"alignment": alignment, "minimum_width": width}, None


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
    decisions_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = copy.deepcopy(contract_override) if contract_override is not None else load(root / CONTRACT_REL)
    fixture = copy.deepcopy(fixture_override) if fixture_override is not None else load(root / FIXTURE_REL)
    schema = load(root / SCHEMA_REL)
    hir = load(root / HIR_REL)
    frontend = load(root / FRONTEND_REL)
    lowering = load(root / LOWERING_REL)
    features = load(root / FEATURE_REL)
    diagnostics = load(root / DIAGNOSTIC_REL)
    predicates = load(root / PREDICATE_REL)
    trace_rows = load(root / TRACE_REL)
    decisions = copy.deepcopy(decisions_override) if decisions_override is not None else load(root / CURRENT_DECISIONS_REL)
    language = (root / LANGUAGE_REL).read_text(encoding="utf-8")
    mir = (root / MIR_REL).read_text(encoding="utf-8")

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
        surface.get("inner_grammar") == "Align? Width"
        and surface.get("align_tokens") == ["<", ">", "^"]
        and surface.get("default_alignment") == "LEFT"
        and surface.get("width_decimal_min") == 1
        and surface.get("width_decimal_max") == 1_000_000
        and all(surface.get(key) is False for key in ("width_leading_zero_allowed", "sign_allowed", "underscore_allowed", "whitespace_allowed", "arbitrary_fill_allowed")),
        "G02",
        "SURFACE_CORE_EXACT",
    )
    static = contract.get("static_admission", {})
    require(
        static.get("predicate_id") == "StringInterpolationFormatSpecAdmitted"
        and static.get("unbraced_diagnostic") == "INTERPOLATION_FORMAT_REQUIRES_BRACED_FORM"
        and static.get("invalid_spec_diagnostic") == "INTERPOLATION_FORMAT_SPEC_INVALID"
        and static.get("reason_precedence") == ["EMPTY_FORMAT", "INVALID_GRAMMAR", "WIDTH_LEADING_ZERO", "WIDTH_OUT_OF_RANGE"]
        and static.get("invalid_spec_hir_residue_count") == 0
        and static.get("invalid_spec_mir_residue_count") == 0,
        "G03",
        "STATIC_ADMISSION_EXACT",
    )

    cases = fixture.get("cases", [])
    observed = {"positive": 0, "boundary": 0, "reject": 0}
    for case in cases:
        kind = case.get("class")
        if kind in observed:
            observed[kind] += 1
        plan, reason = parse_format(case.get("format_text", ""))
        if kind in {"positive", "boundary"}:
            expected = case.get("expected", {})
            require(plan is not None and reason is None and plan.items() <= expected.items(), "G04", f"ADMITTED_CASE:{case.get('id')}")
        elif kind == "reject":
            require(plan is None and reason == case.get("reason") and case.get("diagnostic") == "INTERPOLATION_FORMAT_SPEC_INVALID", "G04", f"REJECT_CASE:{case.get('id')}")
    counts = fixture.get("expected_counts", {})
    require(
        len(cases) == counts.get("cases") == 11
        and observed == {"positive": 4, "boundary": 3, "reject": 4}
        and all(counts.get(key) == value for key, value in {"semantic_p0": 0, "feature_p1": 22, "product_lanes": 15, "product_executed": 0}.items()),
        "G04",
        "FIXTURE_COUNTS_AND_GOVERNANCE",
    )

    dynamic = contract.get("dynamic_semantics", {})
    require(
        dynamic.get("evaluation_order") == [
            "EVALUATE_HOLE_VALUE_ONCE",
            "USE_STRING_DIRECTLY_OR_INVOKE_PRESELECTED_DISPLAY_ONCE",
            "COUNT_DISPLAY_RESULT_UNICODE_SCALARS",
            "APPLY_INTERPOLATION_OWNED_PADDING",
            "STAGE_PADDED_SEGMENT_ONCE",
        ]
        and dynamic.get("width_unit") == "UNICODE_SCALAR_VALUE"
        and dynamic.get("fill_scalar") == "U+0020"
        and dynamic.get("width_is_minimum") is True
        and dynamic.get("truncation") == "NEVER"
        and dynamic.get("center_alignment_padding") == "LEFT_FLOOR_RIGHT_REMAINDER"
        and dynamic.get("display_receives_format_argument") is False
        and dynamic.get("string_hole_display_invocation_count") == 0
        and dynamic.get("non_string_hole_display_invocation_count") == 1
        and dynamic.get("new_locale_provider_serialization_authority_count") == 0,
        "G05",
        "DYNAMIC_SEMANTICS_EXACT",
    )

    defs = hir.get("$defs", {})
    fmt = defs.get("InterpolationFormatPlan", {})
    segment = defs.get("InterpolationSegment", {})
    segment_text = json.dumps(segment, sort_keys=True)
    render_text = json.dumps(defs.get("InterpolationRenderRoute", {}), sort_keys=True)
    require(
        fmt.get("properties", {}).get("minimum_width", {}).get("maximum") == 1_000_000
        and "format_plan_or_null" in segment_text
        and "render_route" in segment_text
        and "DIRECT_STRING" in render_text
        and "DISPLAY" in render_text,
        "G06",
        "HIR_PLAN_AND_RENDER_ROUTE",
    )
    scanner = frontend.get("scanner_contract", {}).get("mode_tokens", {}).get("ScannerInterpolationFormatText")
    if scanner is None:
        scanner = frontend.get("scanner", {}).get("tokens", {}).get("ScannerInterpolationFormatText")
    frontend_text = json.dumps(frontend, ensure_ascii=False)
    require("StringInterpolationFormatSpecAdmitted checker" in frontend_text and "opaque token" in frontend_text, "G06", "FRONTEND_OWNER")

    row = next((item for item in lowering.get("rows", []) if item.get("row_id") == "HM-LR-TOP-019"), {})
    require(
        row.get("lowering_rule_id") == "DM-LR-TOP-INTERPOLATION-R1"
        and row.get("operation_plan", [{}, {}])[1].get("input_roles") == ["string_builder", "ordered_text_display_holes_and_format_plans"],
        "G07",
        "LOWERING_PLAN_BOUND",
    )
    feature = next((item for item in features if item.get("feature_id") == "string_interpolation_format_spec_core"), {})
    diagnostic = next((item for item in diagnostics if item.get("diagnostic_id") == "INTERPOLATION_FORMAT_SPEC_INVALID"), {})
    predicate = next((item for item in predicates if item.get("predicate_id") == "StringInterpolationFormatSpecAdmitted"), {})
    require(
        feature.get("status_enum") == "STABLE_DESIGN"
        and "StringInterpolationFormatSpecAdmitted" in feature.get("normative_trace_refs", {}).get("predicates", [])
        and "INTERPOLATION_FORMAT_SPEC_INVALID" in feature.get("normative_trace_refs", {}).get("diagnostics", [])
        and MIR_REL + "#stable-interpolation-format-plan" in feature.get("artifact_trace_refs", [])
        and diagnostic.get("stage") == "checker"
        and diagnostic.get("diagnostic_status") == "active"
        and predicate.get("predicate_maturity") == "design_algorithm"
        and predicate.get("emission_eligible") is True,
        "G08",
        "REGISTRY_BINDING",
    )
    trace = next((item for item in trace_rows if item.get("feature_id") == "string_interpolation_format_spec_core"), {})
    dynamic_trace = next((item for item in trace.get("stages", []) if item.get("stage") == "DYNAMIC_LOWERING"), {})
    require(dynamic_trace.get("disposition") == "BOUND_DIRECT", "G08", "TRACE_DYNAMIC_NOT_FALSE_NA")

    require(
        "The Stable format core after the colon is `Align? Width`" in language
        and "### 4.1 Stable interpolation format plan" in mir
        and "`string_interpolation_format_spec_core` | `LAW_PRESENT`" in mir
        and "Exactly one required row remains `DEFERRED_PRODUCT_HANDOFF`" not in mir,
        "G09",
        "NORMATIVE_TEXT_CLOSURE",
    )
    decision = next(
        (
            item
            for item in decisions.get("laws", [])
            if item.get("id") == "DSGN-CURRENT-VALUE-OPERATOR-INDEX-COHERENCE"
        ),
        {},
    )
    decision_law = decision.get("law", "")
    require(
        decision.get("status") == "CURRENT"
        and "colon format-spec uses the closed Stable `Align? Width` plan" in decision_law
        and "DEFERRED_PRODUCT_HANDOFF" not in decision_law,
        "G09",
        "CURRENT_DECISION_PROJECTION_CLOSED",
    )
    governance = contract.get("governance", {})
    require(
        governance == {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "github_publication": "NOT_PERFORMED_FOR_R80",
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
    print(json.dumps({"schema": "deeplus.r80-string-interpolation-format-validation-receipt/r1", "result": "PASS" if not errors else "FAIL", "checks": 10, "failed": errors, "semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "product_execution": "NOT_RUN"}, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
