#!/usr/bin/env python3
"""Build the bounded R55 lexical-trivia/source-root trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json"
CONTRACT = "spec/contracts/lexical-trivia-source-root-attachment-r1.json"
FEATURES = sorted([
    "comment_trivia_lexical_priority_law",
    "documentation_comment_trivia",
    "line_comment_double_slash_trivia",
    "nested_block_comment_slash_dash_trivia",
    "shebang_comment_first_line_trivia",
    "word_comment_lossless_trivia",
    "word_comment_tokenization_law",
    "r51a1_machine_closed_lexical_modes",
    "source_root_full_consumption",
])


def evidence_key(feature: str, stage: str, outcome: str | None) -> str:
    suffix = outcome or "STRUCTURAL"
    return f"R55:{feature}:{stage}:{suffix}"


def evidence_entry(
    key: str,
    stage_role: str,
    path: str,
    locator_kind: str,
    locator: str,
    evidence_class: str,
) -> dict[str, str]:
    return {
        "evidence_key": key,
        "class": evidence_class,
        "path": path,
        "locator_kind": locator_kind,
        "locator": locator,
        "stage_role": stage_role,
    }


NA_STRUCTURAL: dict[tuple[str, str], tuple[str, str, str]] = {}
COMMENT_FEATURES = [
    "comment_trivia_lexical_priority_law",
    "documentation_comment_trivia",
    "line_comment_double_slash_trivia",
    "nested_block_comment_slash_dash_trivia",
    "shebang_comment_first_line_trivia",
    "word_comment_lossless_trivia",
    "word_comment_tokenization_law",
]
for feature in COMMENT_FEATURES:
    NA_STRUCTURAL[(feature, "AST_FRONTEND")] = (
        "NA_AST_LEXICAL_TRIVIA_ONLY",
        "FRONTEND_AUTHORITY",
        "Lexical trivia is lossless in CST and creates no canonical AST node.",
    )
    NA_STRUCTURAL[(feature, "STATIC_SEMANTICS")] = (
        "NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY",
        "TYPE_CHECKER_AUTHORITY",
        "The lexical or attachment rule terminates before type checking.",
    )
NA_STRUCTURAL[("comment_trivia_lexical_priority_law", "DYNAMIC_LOWERING")] = (
    "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
    "MIR_RUNTIME_AUTHORITY",
    "Scanner priority creates no admitted runtime behavior.",
)
for stage, reason, boundary, rationale in [
    ("AST_FRONTEND", "NA_AST_NO_PROGRAMMER_VISIBLE_FORM", "FRONTEND_AUTHORITY", "Closed scanner modes add no programmer-visible AST identity."),
    ("STATIC_SEMANTICS", "NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY", "TYPE_CHECKER_AUTHORITY", "Closed scanner modes terminate before type checking."),
    ("DYNAMIC_LOWERING", "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR", "MIR_RUNTIME_AUTHORITY", "Closed scanner modes add no runtime behavior."),
]:
    NA_STRUCTURAL[("r51a1_machine_closed_lexical_modes", stage)] = (reason, boundary, rationale)
NA_STRUCTURAL[("source_root_full_consumption", "STATIC_SEMANTICS")] = (
    "NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY",
    "TYPE_CHECKER_AUTHORITY",
    "Full input consumption is a parser commit predicate and adds no type rule.",
)

BLOCKED_TEST_CELLS = {
    ("comment_trivia_lexical_priority_law", outcome) for outcome in ("POSITIVE", "BOUNDARY", "REJECT")
} | {
    (feature, outcome)
    for feature in [
        "documentation_comment_trivia",
        "line_comment_double_slash_trivia",
        "nested_block_comment_slash_dash_trivia",
        "shebang_comment_first_line_trivia",
        "word_comment_lossless_trivia",
        "word_comment_tokenization_law",
        "r51a1_machine_closed_lexical_modes",
        "source_root_full_consumption",
    ]
    for outcome in ("BOUNDARY", "REJECT")
}

EXISTING_CASES = {
    ("line_comment_double_slash_trivia", "BOUNDARY"): "EX-R48L-COMMENT-007",
    ("nested_block_comment_slash_dash_trivia", "BOUNDARY"): "EX-R51a1-058",
    ("word_comment_lossless_trivia", "BOUNDARY"): "EX-R48L-COMMENT-005",
    ("word_comment_lossless_trivia", "REJECT"): "EX-R48L-COMMENT-006",
    ("word_comment_tokenization_law", "BOUNDARY"): "EX-R48L-COMMENT-005",
    ("r51a1_machine_closed_lexical_modes", "BOUNDARY"): "EX-R51a1-051",
    ("r51a1_machine_closed_lexical_modes", "REJECT"): "EX-R51a1-NG-043",
    ("source_root_full_consumption", "REJECT"): "EX-R51c-020",
}
NEW_CASE_INDEX = {
    ("comment_trivia_lexical_priority_law", "POSITIVE"): 0,
    ("comment_trivia_lexical_priority_law", "BOUNDARY"): 1,
    ("comment_trivia_lexical_priority_law", "REJECT"): 2,
    ("documentation_comment_trivia", "BOUNDARY"): 3,
    ("documentation_comment_trivia", "REJECT"): 4,
    ("nested_block_comment_slash_dash_trivia", "REJECT"): 5,
    ("shebang_comment_first_line_trivia", "BOUNDARY"): 6,
    ("shebang_comment_first_line_trivia", "REJECT"): 7,
    ("word_comment_tokenization_law", "REJECT"): 8,
    ("source_root_full_consumption", "BOUNDARY"): 9,
}


def rule_for(feature: str, stage: str) -> str:
    if feature == "comment_trivia_lexical_priority_law":
        return "CommentOpenerPriorityDeterministic"
    if feature == "documentation_comment_trivia":
        return "DocumentationCommentAttachmentAdmitted"
    if feature.startswith("word_comment"):
        return "WordCommentAttachmentAdmitted"
    if feature == "source_root_full_consumption":
        return "SourceRootFullConsumptionAdmitted"
    if feature == "r51a1_machine_closed_lexical_modes":
        return "LexicalTriviaHasNoDynamicLowering" if stage == "DYNAMIC_LOWERING" else "CstTriviaErasedBeforeNormalizedAst"
    if stage == "AST_FRONTEND":
        return "CstTriviaErasedBeforeNormalizedAst"
    return "LexicalTriviaHasNoStaticSemanticEffect"


def main() -> None:
    entries: list[dict[str, str]] = []
    bindings: list[dict[str, object]] = []
    cases: list[dict[str, object]] = []

    for (feature, stage), (reason, boundary, rationale) in sorted(NA_STRUCTURAL.items()):
        key = evidence_key(feature, stage, None)
        entries.append(evidence_entry(key, stage, CONTRACT, "REGISTRY_ID", rule_for(feature, stage), "CONTRACT_RULE_ID"))
        bindings.append({
            "feature_id": feature,
            "stage": stage,
            "outcome": None,
            "disposition": "NOT_APPLICABLE",
            "evidence_keys": [key],
            "delegate_feature_id": None,
            "not_applicable": {
                "reason_code": reason,
                "authority_boundary": boundary,
                "rationale": rationale,
                "justification_evidence_keys": [key],
            },
        })

    for feature, outcome in sorted(BLOCKED_TEST_CELLS):
        key = evidence_key(feature, "CONFORMANCE_TESTS", outcome)
        stage_role = f"CONFORMANCE_TESTS:{outcome}"
        if feature == "line_comment_double_slash_trivia" and outcome == "REJECT":
            entries.append(evidence_entry(key, stage_role, CONTRACT, "REGISTRY_ID", "LineCommentHasNoDistinctRejectClass", "CONTRACT_RULE_ID"))
            bindings.append({
                "feature_id": feature,
                "stage": "CONFORMANCE_TESTS",
                "outcome": outcome,
                "disposition": "NOT_APPLICABLE",
                "evidence_keys": [key],
                "delegate_feature_id": None,
                "not_applicable": {
                    "reason_code": "NA_TEST_NO_DISTINCT_REJECTION_CLASS",
                    "authority_boundary": "CONFORMANCE_AUTHORITY",
                    "rationale": "Ordinary line comments have no distinct rejected form beyond unrelated source-root or lexical failures.",
                    "justification_evidence_keys": [key],
                },
            })
            continue
        if (feature, outcome) in NEW_CASE_INDEX:
            index = NEW_CASE_INDEX[(feature, outcome)]
            locator = f"/new_acceptance_cases/{index}"
            path = CONTRACT
            kind = "JSON_POINTER"
            evidence_class = "ACCEPTANCE_CASE"
            subject = f"{CONTRACT}#{locator}"
            case_id = f"R55-TRACE-{index + 1:03d}"
        else:
            locator = EXISTING_CASES[(feature, outcome)]
            path = "examples/guide/review-corpus.md"
            kind = "REGISTRY_ID"
            evidence_class = "TEACHING_EXAMPLE_ID"
            subject = locator
            case_id = f"R55-TRACE-EX-{len(cases) + 1:03d}"
        entries.append(evidence_entry(key, stage_role, path, kind, locator, evidence_class))
        bindings.append({
            "feature_id": feature,
            "stage": "CONFORMANCE_TESTS",
            "outcome": outcome,
            "disposition": "BOUND_DIRECT",
            "evidence_keys": [key],
            "delegate_feature_id": None,
            "not_applicable": None,
        })
        cases.append({
            "case_id": case_id,
            "feature_id": feature,
            "outcome": outcome,
            "source_or_subject": subject,
            "expected": "STATIC_ACCEPTANCE_OR_REJECTION_BOUND_BY_REFERENCED_EVIDENCE",
            "diagnostic_or_null": "BOUND_BY_REFERENCED_EVIDENCE" if outcome == "REJECT" else None,
            "assertions": {"evidence_key": key, "source_activation": "none"},
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })

    bindings.sort(key=lambda row: (str(row["feature_id"]), str(row["stage"]), str(row["outcome"])))
    entries.sort(key=lambda row: row["evidence_key"])
    cases.sort(key=lambda row: row["case_id"])
    value = {
        "$schema": "../../../schemas/language/lexical-trivia-source-root-evidence-r1.schema.json",
        "schema": "deeplus.lexical-trivia-source-root-evidence/r1",
        "revision": "r55-local-lexical-trivia-source-root-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "89ded1ab5c9110476f7043e5f44b71ddd72d19a1",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": FEATURES,
        "evidence_entries": entries,
        "bindings": bindings,
        "acceptance_cases": cases,
        "counts": {
            "feature_count": 9,
            "evidence_entry_count": len(entries),
            "binding_count": len(bindings),
            "predecessor_blocked_cell_count": 38,
            "bound_direct_transition_count": 18,
            "bound_delegated_transition_count": 0,
            "not_applicable_transition_count": 20,
            "predecessor_total_blocked_cell_count": 1341,
            "post_overlay_total_blocked_cell_count": 1303,
            "acceptance_case_count": len(cases),
        },
        "guards": {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "feature_statuses": "UNCHANGED",
            "source_activation": "none",
            "surface_change_count": 0,
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
            "product_execution_receipt_count": 0,
            "implementation_claim": "NONE",
        },
    }
    OUT.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
