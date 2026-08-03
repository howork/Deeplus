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
    overlays = [(path, read_json(path)) for path in OVERLAYS]
    overlay_evidence: dict[str, dict[str, Any]] = {}
    overlay_bindings: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for path, overlay in overlays:
        for item in overlay["evidence_entries"]:
            key = item["evidence_key"]
            if key in overlay_evidence:
                raise ValueError(f"OVERLAY_EVIDENCE_KEY_DUPLICATE:{path.name}:{key}")
            overlay_evidence[key] = item
        for item in overlay["bindings"]:
            cell = (item["feature_id"], item["stage"], item["outcome"])
            if cell in overlay_bindings:
                raise ValueError(f"OVERLAY_BINDING_CELL_DUPLICATE:{path.name}:{cell}")
            overlay_bindings[cell] = item

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
        if row.get("status_enum") in BASE_STATUSES or row["feature_id"] in DEPENDENCY_ADDITIONS
    )
    excluded_ids = sorted(set(by_id) - set(target_ids), key=powershell_ordinal_key)

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
            "production": "spec/grammar/deeplus.ebnf",
            "predicate": "spec/types/predicates",
            "diagnostic": "spec/diagnostics/catalog",
            "example": "examples/guide/review-corpus.md",
        }
        classes = {
            "production": "GRAMMAR_PRODUCTION_ID",
            "predicate": "CHECKER_PREDICATE_ID",
            "diagnostic": "DIAGNOSTIC_REGISTRY_ID",
            "example": "TEACHING_EXAMPLE_ID",
        }
        return add_evidence(classes[kind], paths[kind], "REGISTRY_ID", locator, stage)

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
        production_refs = [registry_evidence("production", item, "SOURCE_GRAMMAR") for item in productions + semantic_productions]
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
        if metadata_only and not productions and not semantic_productions:
            value = not_applicable("NA_SOURCE_TOOLING_OR_PUBLICATION_METADATA_ONLY", "PUBLICATION_AUTHORITY", [feature_ref], "The target row is tooling/publication metadata and introduces no programmer source form.")
        elif library_only and not productions and not semantic_productions:
            value = not_applicable("NA_SOURCE_INTERNAL_NO_PROGRAMMER_FORM", "PRELUDE_PROVIDER_AUTHORITY", [feature_ref, primary_ref], "The library/provider profile introduces no core-language grammar production.")
        else:
            value = direct([feature_ref, primary_ref] + production_refs)
        value = apply_overlay(feature_id, "SOURCE_GRAMMAR", None, value)
        stages.append({"stage": "SOURCE_GRAMMAR", **value})

        if feature_id == "member_visibility_hierarchy_protected":
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

        if predicates:
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

        if feature_id == "member_visibility_sigil_surface_phase_a":
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

        if tooling_refs:
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
                "inclusion_basis": "DEPENDENCY_CLOSURE" if feature_id in DEPENDENCY_ADDITIONS else "BASE_STATUS",
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
        "revision": "r65-local-associated-requirement-ast-diagnostic-parity-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "f2e7353b1c44fc066eba47f6d013cbe0a20e9239",
        "external_post_commit_receipt_required": True,
        "catalog_feature_count": len(feature_rows),
        "base_statuses": sorted(BASE_STATUSES),
        "base_count": sum(row.get("status_enum") in BASE_STATUSES for row in feature_rows),
        "dependency_additions": sorted(DEPENDENCY_ADDITIONS),
        "dependency_addition_count": len(DEPENDENCY_ADDITIONS),
        "target_count": len(target_ids),
        "target_feature_id_list_sha256": digest_ids(target_ids),
        "excluded_count": len(excluded_ids),
        "excluded_feature_id_list_sha256": digest_ids(excluded_ids),
        "stage_order": STAGES,
        "test_outcome_order": OUTCOMES,
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
            "gap_status": "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE",
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
            "e4_e5_evidence_count": 0,
        },
    }
    write_json(OUT / "catalog-metadata.json", metadata)


if __name__ == "__main__":
    main()
