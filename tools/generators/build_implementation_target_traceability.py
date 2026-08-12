#!/usr/bin/env python3
"""Build the exact implementation-target traceability registry.

The generator is intentionally conservative: it binds only structured evidence
already present in the feature catalog and reports unresolved applicable cells
as APPLICABLE_BLOCKED_BY_GAP. Empty catalog arrays are never promoted to PASS.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1"
CHUNKS = OUT / "chunks"
PARSER_AUTHORITY_CONTRACT = ROOT / "spec/contracts/parser-authority-traceability-r1.json"
R101_FEATURE_P1_CONTRACT = ROOT / "spec/contracts/implementation-target-feature-p1-disposition-r101.json"
OVERLAYS = [
    OUT / "scalar-numeric-fixed-operator-evidence-r1.json",
    OUT / "lexical-trivia-source-root-evidence-r1.json",
    OUT / "numeric-array-shape-inferred-evidence-r1.json",
    OUT / "unified-call-tilde-evidence-r1.json",
    OUT / "member-visibility-evidence-r1.json",
    OUT / "pattern-dynamic-lowering-evidence-r1.json",
    OUT / "pattern-match-ownership-split-evidence-r1.json",
    OUT / "pattern-clause-exhaustiveness-evidence-r1.json",
    OUT / "trait-qualified-associated-static-selection-evidence-r1.json",
    OUT / "associated-requirement-phase-a-evidence-r1.json",
    OUT / "associated-requirement-ast-diagnostic-parity-evidence-r1.json",
    OUT / "responsibility-identity-dynamic-trace-evidence-r1.json",
    OUT / "closure-capture-dynamic-trace-evidence-r1.json",
    OUT / "region-lifetime-dynamic-trace-evidence-r1.json",
    OUT / "managed-reference-dynamic-trace-evidence-r1.json",
    OUT / "static-runtime-member-boundary-evidence-r1.json",
    OUT / "method-extension-resolution-dynamic-evidence-r1.json",
    OUT / "member-extension-collision-dynamic-evidence-r1.json",
    OUT / "member-extension-collision-conformance-evidence-r1.json",
    OUT / "actor-cranelift-projection-dynamic-evidence-r1.json",
    OUT / "global-trace-closure-evidence-r1.json",
    OUT / "accessor-property-forwarding-evidence-r100.json",
]
BASE_STATUSES = {"STABLE_DESIGN", "STDLIB_PROFILE"}
DEPENDENCY_ADDITIONS = {
    "callable_responsibility_profile_core",
    "data_shaping_callshape_model",
    "nominal_prototype_derivation",
    "numeric_literal_lexical_contract",
    "source_role_contract",
    "typed_labeled_materialization_family",
}
# A removed spelling can still be an implementation-target obligation when the
# lexer must reject it before any canonical residue is admitted.  It therefore
# stays in the profile by an explicit negative-compatibility rule, not by a
# stale Stable status in the feature catalog.
NEGATIVE_COMPATIBILITY_ADDITIONS = {
    "numeric_literal_suffix",
    # The duplicate conversion identity is not an independently implementable
    # feature.  Keep one target row as a negative identity obligation so an
    # implementation must reject a second conversion algorithm/registry owner.
    "static_exact_unit_conversion_msp",
}
# `trait_binding_failable_v1` is a reachable Stable-group surface, but its
# checker predicate and complete P/B/R corpus are intentionally deferred to
# R77-A006.  Keep that exclusion explicit so the first implementation target
# cannot silently claim its vertical slice is closed.
EXCLUDED_CURRENT_FEATURE_REASONS = {
    "affine_unit_profile_msp": {
        "status": "EXPLICITLY_DEFERRED_TARGET_EXCLUDED",
        "action_id": "IR-MEASURE-P1-069",
        "reason": "The current UnitCatalog source surface has no point/delta or affine-offset declaration. Current source remains rejected until a separate surface and law are approved.",
    },
    "arbitrary_generator_stdlib_profile": {
        "status": "EXPLICITLY_DEFERRED_TARGET_EXCLUDED_OPTIONAL_PROVIDER",
        "action_id": "IR-COLL-P1-070",
        "reason": "This optional provider profile is not a normative dependency of shaped-generator admission and has no bootstrap carrier/API contract.",
    },
    "trait_binding_failable_v1": {
        "status": "EXCLUDED_PENDING_BOUNDARY_CLOSURE",
        "action_id": "R77-A006",
        "reason": "The static Failable contract is current, but its target-bound checker and full positive/boundary/reject corpus remain a separately tracked P1 before the Failable vertical slice.",
    },
    "enum_declaration_order_ord_preview_design": {
        "status": "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION",
        "action_id": "CE-E-P1-007",
        "action_ids": ["CE-E-P1-007", "CE-E-P1-008"],
        "reason": "The Stable design remains referenced by the Enum actions, but execution evidence is open and the derived-Ord vertical slice is excluded from the first implementation target.",
    },
    "enum_case_display_mapping_preview_design": {
        "status": "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION",
        "action_id": "CE-E-P1-007",
        "action_ids": ["CE-E-P1-007", "CE-E-P1-008"],
        "reason": "The Stable design remains referenced by the Enum actions, but execution evidence is open and the derived-Display vertical slice is excluded from the first implementation target.",
    },
    "enum_exact_variant_subset_alias_preview_design": {
        "status": "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION",
        "action_id": "CE-E-P1-004",
        "action_ids": ["CE-E-P1-004", "CE-E-P1-008"],
        "reason": "The Stable design remains referenced by the Enum actions, but execution evidence is open and the exact-subset alias vertical slice is excluded from the first implementation target.",
    },
}
TARGET_ADDITIONS = DEPENDENCY_ADDITIONS | NEGATIVE_COMPATIBILITY_ADDITIONS
ABSORBED_ALIAS_TARGETS = {"static_exact_unit_conversion_msp"}
# These rows own parser/checker boundaries only. Their R89 contract artifacts
# make the static trace explicit but intentionally add no distinct MIR/runtime
# behavior; preserve the predecessor dynamic-stage non-applicability instead of
# treating the mere presence of a contract path as a runtime gap.
STATIC_ONLY_DYNAMIC_NA_FEATURES = {
    "source_role_contract",
    "member_visibility_sigil_surface_phase_a",
    "enum_bare_case_declaration_canonical",
    "match_otherwise_default_arm",
    "match_exhaustiveness_phase_a",
}
STAGES = [
    "SOURCE_GRAMMAR",
    "AST_FRONTEND",
    "STATIC_SEMANTICS",
    "DYNAMIC_LOWERING",
    "DIAGNOSTICS",
    "TOOLING_OBLIGATIONS",
    "CONFORMANCE_TESTS",
]
OUTCOMES = ["POSITIVE", "BOUNDARY", "REJECT"]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def r101_feature_p1_projection(
    contract: dict[str, Any], catalog_ids: set[str], target_ids: list[str]
) -> dict[str, Any]:
    expected_action_ids = [
        *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
        *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
        *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
        "SFD-P1-009",
    ]
    actions = contract.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("R101_ACTIONS_NOT_ARRAY")
    by_id = {row.get("id"): row for row in actions if isinstance(row, dict)}
    if len(actions) != 22 or sorted(by_id) != sorted(expected_action_ids):
        raise ValueError("R101_ACTION_IDENTITY_NOT_EXACT_22")
    if any(str(row.get("design_handoff_gate", "")).startswith("OPEN") for row in actions):
        raise ValueError("R101_DESIGN_GATE_STILL_OPEN_IN_TARGET")
    if sum(str(row.get("execution_receipt_gate", "")).startswith("OPEN") for row in actions) != 22:
        raise ValueError("R101_EXECUTION_OPEN_NOT_EXACT_22")
    if any(row.get("product_execution") != "NOT_RUN" for row in actions):
        raise ValueError("R101_PRODUCT_EXECUTION_NOT_NOT_RUN")
    for row in actions:
        action_id = row.get("id", "")
        if action_id.startswith("CE-C-"):
            expected_domain = "CLASS"
        elif action_id.startswith("CE-E-"):
            expected_domain = "ENUMERATION"
        elif action_id.startswith("TCC-"):
            expected_domain = "TRAIT_CONFORMANCE"
        else:
            expected_domain = "STATIC_FIRST_DYNAMIC"
        excluded_scope = action_id.startswith("CE-")
        if (
            row.get("domain") != expected_domain
            or row.get("action_status") != "OPEN"
            or row.get("design_handoff_gate")
            != (
                "EXPLICITLY_DEFERRED_OUTSIDE_FIRST_TARGET"
                if excluded_scope
                else "CLOSED_DESIGN_STATIC"
            )
            or row.get("disposition")
            != (
                "EXCLUDED_SUCCESSOR_SCOPE_RETAIN_CLOSED_BASE"
                if excluded_scope
                else "INCLUDED_IMPLEMENTATION_ACCEPTANCE"
            )
        ):
            raise ValueError(f"R101_ACTION_PARTITION_MISMATCH:{action_id}")

    excluded_mapping: dict[str, list[str]] = {}
    retained_ids: set[str] = set()
    tcc_sfd_retained_ids: set[str] = set()
    for row in actions:
        action_id = row["id"]
        retained = row.get("retained_feature_ids", [])
        excluded = row.get("excluded_target_feature_ids", [])
        if not isinstance(retained, list) or not isinstance(excluded, list):
            raise ValueError(f"R101_FEATURE_MAPPING_NOT_ARRAY:{action_id}")
        if not retained:
            raise ValueError(f"R101_RETAINED_FEATURE_EMPTY:{action_id}")
        retained_ids.update(retained)
        if action_id.startswith("TCC-") or action_id == "SFD-P1-009":
            tcc_sfd_retained_ids.update(retained)
        for feature_id in excluded:
            excluded_mapping.setdefault(feature_id, []).append(action_id)
    excluded_mapping = {
        feature_id: sorted(action_ids)
        for feature_id, action_ids in sorted(excluded_mapping.items())
    }
    expected_mapping = {
        feature_id: sorted(reason["action_ids"])
        for feature_id, reason in EXCLUDED_CURRENT_FEATURE_REASONS.items()
        if reason.get("status") == "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION"
    }
    if excluded_mapping != expected_mapping:
        raise ValueError("R101_EXCLUDED_FEATURE_MAPPING_MISMATCH")
    missing_retained = sorted(retained_ids - catalog_ids)
    if missing_retained:
        raise ValueError(f"R101_RETAINED_FEATURE_NOT_IN_CATALOG:{missing_retained}")
    missing_tcc_sfd = sorted(tcc_sfd_retained_ids - set(target_ids))
    if missing_tcc_sfd:
        raise ValueError(f"R101_TCC_SFD_FEATURE_NOT_IN_TARGET:{missing_tcc_sfd}")
    return {
        "contract_path": R101_FEATURE_P1_CONTRACT.relative_to(ROOT).as_posix(),
        "contract_sha256": file_sha256(R101_FEATURE_P1_CONTRACT),
        "exact_action_ids": expected_action_ids,
        "action_count": 22,
        "design_open_in_target_count": 0,
        "execution_open_action_count": 22,
        "excluded_target_feature_mapping": excluded_mapping,
        "retained_feature_ids": sorted(retained_ids),
        "retained_feature_id_list_sha256": digest_ids(sorted(retained_ids)),
        "tcc_sfd_retained_feature_ids": sorted(tcc_sfd_retained_ids),
        "tcc_sfd_retained_feature_id_list_sha256": digest_ids(
            sorted(tcc_sfd_retained_ids)
        ),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        # These generated registries are large and machine-owned. Compact JSON
        # keeps review and manifest costs bounded; the validator supplies the
        # human-readable derived summary.
        stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def digest_ids(ids: list[str]) -> str:
    return hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()


def powershell_ordinal_key(value: str) -> str:
    """Match the established Sort-Object ordering used by the R52 authority."""
    return value.replace("_", "\0")


def evidence_id(evidence_class: str, path: str, locator_kind: str, locator: str, stage_role: str) -> str:
    material = "\0".join([evidence_class, path, locator_kind, locator, stage_role])
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def main() -> None:
    parser_authority = read_json(PARSER_AUTHORITY_CONTRACT)
    if (
        parser_authority.get("schema")
        != "deeplus.parser-authority-traceability/r1"
        or parser_authority.get("revision")
        != "r78-dpg-implementation-target-traceability-closure-r1"
    ):
        raise ValueError("PARSER_AUTHORITY_CONTRACT_IDENTITY")
    overlays = [(path, read_json(path)) for path in OVERLAYS]
    overlay_evidence: dict[str, dict[str, Any]] = {}
    overlay_bindings: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    overlay_binding_sources: dict[tuple[str, str, str | None], str] = {}
    for path, overlay in overlays:
        rel = path.relative_to(ROOT).as_posix()
        supersession = overlay.get("supersedes_binding_cells")
        declared_superseded: set[tuple[str, str, str | None]] = set()
        predecessor_overlay_path: str | None = None
        if supersession is not None:
            predecessor_overlay_path = supersession["predecessor_overlay_path"]
            declared_superseded = {
                (item["feature_id"], item["stage"], item.get("outcome"))
                for item in supersession["cells"]
            }
        observed_superseded: set[tuple[str, str, str | None]] = set()
        for item in overlay["evidence_entries"]:
            key = item["evidence_key"]
            if key in overlay_evidence:
                raise ValueError(f"OVERLAY_EVIDENCE_KEY_DUPLICATE:{path.name}:{key}")
            overlay_evidence[key] = item
        for item in overlay["bindings"]:
            cell = (item["feature_id"], item["stage"], item["outcome"])
            if cell in overlay_bindings:
                if (
                    cell not in declared_superseded
                    or overlay_binding_sources[cell] != predecessor_overlay_path
                ):
                    raise ValueError(f"OVERLAY_BINDING_CELL_DUPLICATE:{path.name}:{cell}")
                observed_superseded.add(cell)
            overlay_bindings[cell] = item
            overlay_binding_sources[cell] = rel
        if observed_superseded != declared_superseded:
            raise ValueError(
                f"OVERLAY_SUPERSESSION_CELL_SET:{path.name}:"
                f"declared={len(declared_superseded)}:observed={len(observed_superseded)}"
            )

    feature_rows: list[dict[str, Any]] = []
    source_locations: dict[str, tuple[str, int]] = {}
    for path in sorted((ROOT / "spec/features/catalog/chunks").glob("part-*.json")):
        rows = read_json(path)
        rel = path.relative_to(ROOT).as_posix()
        for index, row in enumerate(rows):
            feature_rows.append(row)
            source_locations[row["feature_id"]] = (rel, index)
    by_id = {row["feature_id"]: row for row in feature_rows}
    target_ids = sorted(
        row["feature_id"]
        for row in feature_rows
        if (
            row.get("status_enum") in BASE_STATUSES
            or row["feature_id"] in TARGET_ADDITIONS
        )
        and row["feature_id"] not in EXCLUDED_CURRENT_FEATURE_REASONS
    )
    excluded_ids = sorted(set(by_id) - set(target_ids), key=powershell_ordinal_key)
    if not R101_FEATURE_P1_CONTRACT.is_file():
        raise FileNotFoundError(
            f"R101_FEATURE_P1_CONTRACT_MISSING:{R101_FEATURE_P1_CONTRACT}"
        )
    r101_projection = r101_feature_p1_projection(
        read_json(R101_FEATURE_P1_CONTRACT), set(by_id), target_ids
    )

    evidence: dict[str, dict[str, Any]] = {}

    def add_evidence(evidence_class: str, path: str, locator_kind: str, locator: str, stage_role: str) -> str:
        ev_id = evidence_id(evidence_class, path, locator_kind, locator, stage_role)
        evidence[ev_id] = {
            "evidence_id": ev_id,
            "class": evidence_class,
            "path": path,
            "locator_kind": locator_kind,
            "locator": locator,
            "stage_role": stage_role,
            "evidence_level": "E2_STRUCTURED_STATIC",
        }
        return ev_id

    def row_evidence(feature_id: str, stage: str) -> str:
        path, index = source_locations[feature_id]
        return add_evidence("FEATURE_REGISTRY_ROW", path, "JSON_POINTER", f"/{index}", stage)

    def path_evidence(path: str, stage: str) -> str:
        file_path, separator, fragment = path.partition("#")
        if not separator:
            locator_kind = "FILE"
            locator = file_path
        elif fragment.startswith("/"):
            locator_kind = "JSON_POINTER"
            locator = fragment
        else:
            locator_kind = "REGISTRY_ID"
            locator = fragment
        return add_evidence("ARTIFACT_POINTER", file_path, locator_kind, locator, stage)

    def registry_evidence(kind: str, locator: str, stage: str) -> str:
        paths = {
            "production": parser_authority["surface_census"]["path"],
            "predicate": "spec/types/predicates",
            "diagnostic": "spec/diagnostics/catalog",
            "example": "examples/guide/review-corpus.md",
        }
        classes = {
            "production": "GRAMMAR_SURFACE_CENSUS_ID",
            "predicate": "CHECKER_PREDICATE_ID",
            "diagnostic": "DIAGNOSTIC_REGISTRY_ID",
            "example": "TEACHING_EXAMPLE_ID",
        }
        return add_evidence(classes[kind], paths[kind], "REGISTRY_ID", locator, stage)

    def parser_authority_refs() -> list[str]:
        refs = []
        for axis in ("structural_grammar", "parser_context", "pratt", "scanner"):
            item = parser_authority["authority_ensemble"][axis]
            refs.append(
                add_evidence(
                    item["class"],
                    item["path"],
                    item["locator_kind"],
                    item["locator"],
                    item["stage_role"],
                )
            )
        return refs

    def direct(refs: list[str]) -> dict[str, Any]:
        return {"disposition": "BOUND_DIRECT", "evidence_refs": sorted(set(refs)), "delegate_feature_id": None, "not_applicable": None, "blocked_gap_ids": []}

    def not_applicable(reason: str, boundary: str, refs: list[str], rationale: str) -> dict[str, Any]:
        return {
            "disposition": "NOT_APPLICABLE",
            "evidence_refs": [],
            "delegate_feature_id": None,
            "not_applicable": {"reason_code": reason, "authority_boundary": boundary, "justification_evidence_refs": sorted(set(refs)), "rationale": rationale},
            "blocked_gap_ids": [],
        }

    def blocked(refs: list[str]) -> dict[str, Any]:
        return {"disposition": "APPLICABLE_BLOCKED_BY_GAP", "evidence_refs": sorted(set(refs)), "delegate_feature_id": None, "not_applicable": None, "blocked_gap_ids": ["IR-XCUT-P1-054"]}

    def delegated(delegate_feature_id: str, refs: list[str]) -> dict[str, Any]:
        return {
            "disposition": "BOUND_DELEGATED",
            "evidence_refs": sorted(set(refs)),
            "delegate_feature_id": delegate_feature_id,
            "not_applicable": None,
            "blocked_gap_ids": [],
        }

    def apply_overlay(
        feature_id: str,
        stage: str,
        outcome: str | None,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        binding = overlay_bindings.get((feature_id, stage, outcome))
        if binding is None:
            return value
        expected_predecessor = binding.get(
            "predecessor_disposition", "APPLICABLE_BLOCKED_BY_GAP"
        )
        observed_disposition = value.get("disposition")
        final_disposition = binding["disposition"]
        if observed_disposition not in {
            expected_predecessor,
            final_disposition,
        }:
            raise ValueError(
                f"OVERLAY_PREDECESSOR_DISPOSITION:{feature_id}:{stage}:{outcome}:"
                f"expected={expected_predecessor}|{final_disposition}:"
                f"observed={observed_disposition}"
            )
        refs = []
        for key in binding["evidence_keys"]:
            item = overlay_evidence[key]
            refs.append(add_evidence(
                item["class"],
                item["path"],
                item["locator_kind"],
                item["locator"],
                item["stage_role"],
            ))
        if binding["disposition"] == "BOUND_DIRECT":
            return direct(refs)
        if binding["disposition"] == "BOUND_DELEGATED":
            return delegated(binding["delegate_feature_id"], refs)
        detail = binding["not_applicable"]
        return not_applicable(
            detail["reason_code"],
            detail["authority_boundary"],
            refs,
            detail["rationale"],
        )

    rows_out: list[dict[str, Any]] = []
    for feature_id in target_ids:
        row = by_id[feature_id]
        trace = row.get("normative_trace_refs", {})
        productions = list(trace.get("productions", []))
        semantic_productions = list(trace.get("semantic_reference_productions", []))
        predicates = list(trace.get("predicates", []))
        diagnostics = list(trace.get("diagnostics", []))
        examples = list(trace.get("examples", []))
        artifacts = [value for value in row.get("artifact_trace_refs", []) if isinstance(value, str)]
        trace_class = row.get("trace_class", "unclassified")
        feature_kind = row.get("feature_kind", "canonical_feature")
        source_activation = row.get("source_activation", "none")
        feature_ref = row_evidence(feature_id, "CATALOG_BINDING")
        primary = row.get("primary_source", "spec/language.md")
        primary_ref = path_evidence(primary, "NORMATIVE_SOURCE")
        production_refs = [
            registry_evidence(
                "production",
                item,
                parser_authority["surface_census"]["stage_role"],
            )
            for item in productions + semantic_productions
        ]
        source_authority_refs = parser_authority_refs()
        predicate_refs = [registry_evidence("predicate", item, "STATIC_SEMANTICS") for item in predicates]
        diagnostic_refs = [registry_evidence("diagnostic", item, "DIAGNOSTICS") for item in diagnostics]
        example_refs = [registry_evidence("example", item, "CONFORMANCE_TESTS") for item in examples]
        artifact_refs = [path_evidence(item, "ARTIFACT_TRACE") for item in artifacts]
        fixture_refs = [ref for ref, path in [(path_evidence(item, "CONFORMANCE_TESTS"), item) for item in artifacts] if path.startswith("tests/")]
        runtime_refs = [ref for ref, path in [(path_evidence(item, "DYNAMIC_LOWERING"), item) for item in artifacts] if any(token in path for token in ("/mir/", "runtime", "xvm", "backend"))]
        tooling_refs = [ref for ref, path in [(path_evidence(item, "TOOLING_OBLIGATIONS"), item) for item in artifacts] if any(token in path for token in ("formatter", "lsp", "tooling"))]

        metadata_only = feature_kind in {"publication_closure", "tooling_feature", "internal_design"} or trace_class == "tooling"
        library_only = trace_class == "library" or row.get("status_enum") == "STDLIB_PROFILE"

        stages: list[dict[str, Any]] = []
        if feature_id in ABSORBED_ALIAS_TARGETS:
            value = not_applicable(
                "NA_SOURCE_INTERNAL_NO_PROGRAMMER_FORM",
                "GRAMMAR_AUTHORITY",
                [feature_ref, primary_ref],
                "The absorbed identity has no source spelling; the canonical conversion owner supplies the only active surface and semantics.",
            )
        elif metadata_only and not productions and not semantic_productions:
            value = not_applicable("NA_SOURCE_TOOLING_OR_PUBLICATION_METADATA_ONLY", "PUBLICATION_AUTHORITY", [feature_ref], "The target row is tooling/publication metadata and introduces no programmer source form.")
        elif library_only and not productions and not semantic_productions:
            value = not_applicable("NA_SOURCE_INTERNAL_NO_PROGRAMMER_FORM", "PRELUDE_PROVIDER_AUTHORITY", [feature_ref, primary_ref], "The library/provider profile introduces no core-language grammar production.")
        else:
            value = direct(
                [feature_ref, primary_ref]
                + source_authority_refs
                + production_refs
            )
        value = apply_overlay(feature_id, "SOURCE_GRAMMAR", None, value)
        stages.append({"stage": "SOURCE_GRAMMAR", **value})

        if feature_id in ABSORBED_ALIAS_TARGETS:
            value = not_applicable(
                "NA_AST_NO_PROGRAMMER_VISIBLE_FORM",
                "FRONTEND_AUTHORITY",
                [feature_ref, primary_ref],
                "The absorbed identity may not create an AST or HIR identity distinct from its canonical replacement.",
            )
        elif feature_id == "member_visibility_hierarchy_protected":
            value = not_applicable(
                "NA_AST_NO_PROGRAMMER_VISIBLE_FORM",
                "FRONTEND_AUTHORITY",
                [feature_ref, primary_ref],
                "The rule reuses an existing surface or provider API and adds no AST identity.",
            )
        elif productions or semantic_productions:
            value = direct([feature_ref, path_evidence("spec/frontend/frontend-model.json", "AST_FRONTEND")] + production_refs)
        elif trace_class == "lexical":
            value = not_applicable("NA_AST_LEXICAL_TRIVIA_ONLY", "FRONTEND_AUTHORITY", [feature_ref], "The lexical rule has no distinct canonical AST node.")
        elif metadata_only:
            value = not_applicable("NA_AST_TOOLING_OR_PUBLICATION_METADATA_ONLY", "PUBLICATION_AUTHORITY", [feature_ref], "Tooling/publication metadata has no programmer-visible AST node.")
        elif library_only or (trace_class == "semantic" and source_activation in {"none", "stdlib", "governance"}):
            value = not_applicable("NA_AST_NO_PROGRAMMER_VISIBLE_FORM", "FRONTEND_AUTHORITY", [feature_ref, primary_ref], "The rule reuses an existing surface or provider API and adds no AST identity.")
        else:
            value = blocked([feature_ref, primary_ref])
        value = apply_overlay(feature_id, "AST_FRONTEND", None, value)
        stages.append({"stage": "AST_FRONTEND", **value})

        if feature_id in ABSORBED_ALIAS_TARGETS:
            value = not_applicable(
                "NA_STATIC_TOOLING_OR_PUBLICATION_METADATA_ONLY",
                "TYPE_CHECKER_AUTHORITY",
                [feature_ref, primary_ref],
                "This row records absorbed provenance; the canonical replacement owns the only static conversion judgment.",
            )
        elif predicates:
            value = direct([feature_ref, primary_ref] + predicate_refs)
        elif library_only:
            value = direct([feature_ref, primary_ref])
        elif metadata_only:
            value = not_applicable("NA_STATIC_TOOLING_OR_PUBLICATION_METADATA_ONLY", "PUBLICATION_AUTHORITY", [feature_ref], "The row is publication/tooling metadata rather than a language static rule.")
        elif trace_class == "lexical":
            value = not_applicable("NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY", "TYPE_CHECKER_AUTHORITY", [feature_ref, primary_ref], "The lexical rule terminates before type checking.")
        elif trace_class == "semantic":
            value = direct([feature_ref, primary_ref])
        else:
            value = blocked([feature_ref, primary_ref])
        value = apply_overlay(feature_id, "STATIC_SEMANTICS", None, value)
        stages.append({"stage": "STATIC_SEMANTICS", **value})

        if feature_id in ABSORBED_ALIAS_TARGETS:
            value = not_applicable(
                "NA_DYNAMIC_ALIAS_NORMALIZES_NO_DISTINCT_RUNTIME_IDENTITY",
                "MIR_RUNTIME_AUTHORITY",
                [feature_ref, primary_ref],
                "The absorbed identity normalizes to the canonical exact-ratio conversion plan before lowering.",
            )
        elif feature_id in STATIC_ONLY_DYNAMIC_NA_FEATURES:
            value = not_applicable(
                "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
                "MIR_RUNTIME_AUTHORITY",
                [feature_ref, primary_ref],
                "The catalog class is lexical/syntactic and binds no runtime artifact.",
            )
        elif runtime_refs:
            value = direct([feature_ref, primary_ref] + runtime_refs)
        elif trace_class == "rejection":
            value = not_applicable("NA_DYNAMIC_REJECTED_BEFORE_LOWERING", "MIR_RUNTIME_AUTHORITY", [feature_ref] + diagnostic_refs, "The rejected form creates no admitted dynamic residue.")
        elif metadata_only:
            value = not_applicable("NA_DYNAMIC_TOOLING_OR_PUBLICATION_METADATA_ONLY", "PUBLICATION_AUTHORITY", [feature_ref], "The row has no runtime behavior.")
        elif trace_class in {"lexical", "syntax"} and not artifacts:
            value = not_applicable("NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR", "MIR_RUNTIME_AUTHORITY", [feature_ref, primary_ref], "The catalog class is lexical/syntactic and binds no runtime artifact.")
        elif library_only:
            value = direct([feature_ref, primary_ref] + artifact_refs)
        else:
            value = blocked([feature_ref, primary_ref] + artifact_refs)
        value = apply_overlay(feature_id, "DYNAMIC_LOWERING", None, value)
        stages.append({"stage": "DYNAMIC_LOWERING", **value})

        if diagnostics:
            value = direct([feature_ref] + diagnostic_refs)
        elif trace_class == "rejection":
            value = blocked([feature_ref, primary_ref])
        else:
            value = not_applicable("NA_DIAGNOSTIC_NO_REJECTION_WARNING_OR_INFO_CONDITION", "DIAGNOSTIC_AUTHORITY", [feature_ref, primary_ref], "The catalog row declares no distinct public rejection, warning, or information condition.")
        value = apply_overlay(feature_id, "DIAGNOSTICS", None, value)
        stages.append({"stage": "DIAGNOSTICS", **value})

        if feature_id in ABSORBED_ALIAS_TARGETS:
            value = not_applicable(
                "NA_TOOLING_NO_NEW_SOURCE_OR_OBSERVATION_OBLIGATION",
                "TOOLING_AUTHORITY",
                [feature_ref, primary_ref],
                "The absorbed identity introduces no source spelling, formatting rule, completion item, or observation surface.",
            )
        elif tooling_refs:
            value = direct([feature_ref] + tooling_refs)
        elif metadata_only:
            value = direct([feature_ref, primary_ref] + artifact_refs)
        elif library_only and not productions:
            value = not_applicable("NA_TOOLING_NO_NEW_SOURCE_OR_OBSERVATION_OBLIGATION", "TOOLING_AUTHORITY", [feature_ref, primary_ref], "The provider profile adds no separate source-formatting or LSP observation contract.")
        else:
            value = direct([feature_ref, path_evidence("spec/contracts/formatter-lsp-incremental-parsing-contract-r1.json", "TOOLING_OBLIGATIONS")])
        value = apply_overlay(feature_id, "TOOLING_OBLIGATIONS", None, value)
        stages.append({"stage": "TOOLING_OBLIGATIONS", **value})

        outcomes = []
        for outcome in OUTCOMES:
            if fixture_refs:
                outcome_value = direct([feature_ref] + fixture_refs)
            elif outcome == "POSITIVE" and example_refs:
                outcome_value = direct([feature_ref] + example_refs)
            else:
                outcome_value = blocked([feature_ref] + example_refs + artifact_refs)
            outcome_value = apply_overlay(
                feature_id, "CONFORMANCE_TESTS", outcome, outcome_value
            )
            outcomes.append({"outcome": outcome, **outcome_value})
        stages.append({"stage": "CONFORMANCE_TESTS", "outcomes": outcomes, "product_execution": "NOT_RUN"})

        rows_out.append({
            "feature_id": feature_id,
            "catalog_binding": {
                "status_enum": row.get("status_enum"),
                "feature_kind": feature_kind,
                "trace_class": trace_class,
                "source_activation": source_activation,
                "inclusion_basis": (
                    "DEPENDENCY_CLOSURE" if feature_id in DEPENDENCY_ADDITIONS
                    else "NEGATIVE_COMPATIBILITY" if feature_id in NEGATIVE_COMPATIBILITY_ADDITIONS
                    else "BASE_STATUS"
                ),
                "feature_row_evidence_ref": feature_ref,
            },
            "stages": stages,
            "product_execution": "NOT_RUN",
        })

    CHUNKS.mkdir(parents=True, exist_ok=True)
    for old in CHUNKS.glob("part-*.json"):
        old.unlink()
    rows_path = OUT / "rows.json"
    write_json(rows_path, rows_out)
    chunks = [{
        "path": "spec/traceability/implementation-target-profile-r1/rows.json",
        "row_count": len(rows_out),
    }]

    blocked_cells = 0
    direct_cells = 0
    delegated_cells = 0
    na_cells = 0
    for row in rows_out:
        for stage in row["stages"]:
            cells = stage.get("outcomes", [stage])
            for cell in cells:
                blocked_cells += cell.get("disposition") == "APPLICABLE_BLOCKED_BY_GAP"
                direct_cells += cell.get("disposition") == "BOUND_DIRECT"
                delegated_cells += cell.get("disposition") == "BOUND_DELEGATED"
                na_cells += cell.get("disposition") == "NOT_APPLICABLE"

    metadata = {
        "$schema": "../../../schemas/language/implementation-target-traceability-r1.schema.json",
        "schema": "deeplus.implementation-target-traceability/r1",
        "revision": "r78-dpg-implementation-target-traceability-closure-r1",
        "canonical_baseline_commit": "10e64f492f0529610673846139afcf0d95175663",
        "local_predecessor_commit": "7d4e6c48b9374bec34a60b970530174dd9b4e145",
        "external_post_commit_receipt_required": True,
        "catalog_feature_count": len(feature_rows),
        "base_statuses": sorted(BASE_STATUSES),
        "base_count": sum(row.get("status_enum") in BASE_STATUSES for row in feature_rows),
        "dependency_additions": sorted(DEPENDENCY_ADDITIONS),
        "dependency_addition_count": len(DEPENDENCY_ADDITIONS),
        "negative_compatibility_additions": sorted(NEGATIVE_COMPATIBILITY_ADDITIONS),
        "negative_compatibility_addition_count": len(NEGATIVE_COMPATIBILITY_ADDITIONS),
        "excluded_current_feature_reasons": EXCLUDED_CURRENT_FEATURE_REASONS,
        "target_count": len(target_ids),
        "target_feature_id_list_sha256": digest_ids(target_ids),
        "excluded_count": len(excluded_ids),
        "excluded_feature_id_list_sha256": digest_ids(excluded_ids),
        "stage_order": STAGES,
        "test_outcome_order": OUTCOMES,
        "source_grammar_authority": {
            "contract": PARSER_AUTHORITY_CONTRACT.relative_to(ROOT).as_posix(),
            "authority_axes": list(parser_authority["authority_ensemble"]),
            "surface_census_path": parser_authority["surface_census"]["path"],
            "surface_census_semantic_authority": False,
            "direct_cell_requires_all_authority_axes": True,
            "ebnf_only_binding_rejected": True,
        },
        "chunks": chunks,
        "applied_evidence_overlays": [{
            "path": path.relative_to(ROOT).as_posix(),
            "feature_count": len(overlay["feature_ids"]),
            "binding_count": len(overlay["bindings"]),
        } for path, overlay in overlays],
        "evidence_registry": [evidence[key] for key in sorted(evidence)],
        "derived_counts": {
            "feature_rows": len(rows_out),
            "stage_cells": len(rows_out) * len(STAGES),
            "test_outcome_cells": len(rows_out) * len(OUTCOMES),
            "bound_direct_cells": direct_cells,
            "bound_delegated_cells": delegated_cells,
            "not_applicable_cells": na_cells,
            "applicable_blocked_cells": blocked_cells,
            "missing_cells": 0,
            "conflict_cells": 0,
            "product_not_run_rows": len(rows_out),
        },
        "governance": {
            "gap_id": "IR-XCUT-P1-054",
            "gap_status": "LOCAL_VERIFIED_CANDIDATE_NOT_INTEGRATED",
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "NOT_PERFORMED_FOR_DPG_TRACE_REPAIR",
            "e4_e5_evidence_count": 0,
            "r101_feature_p1_disposition": r101_projection,
        },
    }
    write_json(OUT / "catalog-metadata.json", metadata)


if __name__ == "__main__":
    main()
