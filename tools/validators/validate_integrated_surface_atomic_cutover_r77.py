#!/usr/bin/env python3
"""Validate the bounded R77 integrated-surface atomic cutover.

This validator checks design-static contracts and projections only.  A PASS is
not parser, checker, HIR/MIR, runtime, backend, tooling, or product execution
evidence; all product lanes remain NOT_RUN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


DECISION_ID = "DSGN-CURRENT-INTEGRATED-SURFACE-ATOMIC-CUTOVER-R77-R1"
DECISION_REL = (
    "decisions/language/"
    "Design_Deeplus_Integrated_Surface_Atomic_Cutover_R77_R1.md"
)
CONTRACT_REL = "spec/contracts/integrated-surface-atomic-cutover-r77-r1.json"
FIXTURE_REL = "tests/fixtures/current/integrated-surface-atomic-cutover-r77-r1.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
GRAMMAR_REL = "spec/grammar/deeplus.ebnf"
POINTER_REL = "current/current-pointer.json"
RECEIPT_REL = (
    "release/evidence/"
    "r77-integrated-surface-publication-closure-readback.json"
)
HIR_SCHEMA_REL = "schemas/language/canonical-hir-h1.schema.json"
API_SCHEMA_REL = "schemas/language/module-api-digest.schema.json"

REMOVED_SUFFIXES = [
    "i8", "i16", "i32", "i64", "i128", "isize",
    "u8", "u16", "u32", "u64", "u128", "usize", "f32", "f64",
]

TRAIT_ROLE_IDS = {
    "TRAIT_LANGUAGE_ROLE_OPERATOR_R1",
    "TRAIT_LANGUAGE_ROLE_ITERATION_R1",
    "TRAIT_LANGUAGE_ROLE_INTERPOLATION_R1",
    "TRAIT_LANGUAGE_ROLE_BINDING_R1",
}

TRAIT_ROLE_MEMBERS = {
    "operator": [
        "UnaryPlus", "UnaryMinus", "Add", "Subtract", "Multiply",
        "Divide", "Remainder", "Eq", "Ord",
    ],
    "iteration": ["Sequence", "Iterator"],
    "interpolation": ["Display"],
    "binding": ["Failable"],
}

MUTABLE_LIST_OPERATIONS = [
    "MutableList::insertBefore",
    "MutableList::insertAfter",
    "MutableList::prepend",
    "MutableList::append",
    "MutableList::insertAllBefore",
    "MutableList::insertAllAfter",
    "MutableList::prependAll",
    "MutableList::appendAll",
    "MutableList::removeAt",
    "MutableList::removeRange",
    "MutableList::removeSelected",
    "MutableList::popFirst",
    "MutableList::popLast",
]

OPEN_FEATURE_P1 = (
    ["CE-C-P1-%03d" % value for value in range(1, 7)]
    + ["CE-E-P1-%03d" % value for value in range(1, 9)]
    + ["TCC-P1-%03d" % value for value in range(2, 9)]
    + ["SFD-P1-009"]
)
OPEN_M13 = ["M13-A002", "M13-A003", "M13-A004", "M13-A005"]

EXPECTED_FIXTURE_IDS = {
    "positive": {
        "R77-POS-COLLECT-001", "R77-POS-PATTERN-001",
        "R77-POS-COMPREHENSION-001", "R77-POS-RANGE-001",
        "R77-POS-SLICE-001", "R77-POS-MUTABLE-LIST-001",
        "R77-POS-FAILABLE-001", "R77-POS-NUMERIC-001",
    },
    "boundary": {
        "R77-BOUNDARY-SLICE-001", "R77-BOUNDARY-RANGE-001",
        "R77-BOUNDARY-MUTABLE-LIST-001", "R77-BOUNDARY-NUMERIC-001",
    },
    "rejected": {
        "R77-NEG-LEGACY-001", "R77-NEG-COMPREHENSION-001",
        "R77-NEG-NAMED-001", "R77-NEG-RANGE-001",
        "R77-NEG-RANGE-002", "R77-NEG-SLICE-001",
        "R77-NEG-AXIS-001", "R77-NEG-MUTABLE-LIST-001",
        "R77-NEG-FAILABLE-001", "R77-NEG-NUMERIC-001",
        "R77-NEG-OVERLOAD-001",
    },
}

R77_EXAMPLES = {
    "EX-R77-CALL-P-001": (
        "accept",
        ["call_shape_rest_type_residue_law", "named_rest_parameter_record_msp",
         "call_side_positional_unfold_star_msp"],
        None,
    ),
    "EX-R77-COMP-P-001": (
        "accept", ["comprehension_unfold", "call_side_positional_unfold_star_msp"], None,
    ),
    "EX-R77-PAT-P-001": (
        "accept", ["sequence_positional_rest_pattern", "structured_record_map_pattern"], None,
    ),
    "EX-R77-RANGE-P-001": (
        "accept", ["runtime_range_step_expression", "range_step_expression_surface_clarification"], None,
    ),
    "EX-R77-RANGE-NG-001": (
        "reject", ["runtime_range_step_expression"], "RANGE_STEP_ZERO",
    ),
    "EX-R77-INDEX-P-001": (
        "accept",
        ["numeric_array_multiaxis_slice_readonly_view_msp",
         "inclusive_slice_range_canonical_msp", "slice_logical_domain_preservation"],
        None,
    ),
    "EX-R77-INDEX-NG-001": (
        "reject", ["basic_index_operator", "numeric_array_multiaxis_slice_readonly_view_msp"],
        "INDEX_AXIS_COUNT_MISMATCH",
    ),
    "EX-R77-MUTLIST-P-001": ("accept", ["basic_index_operator"], None),
    "EX-R77-MUTLIST-NG-001": (
        "reject", ["basic_index_operator"], "MUTABLE_LIST_ORDINARY_BRACKET_REPLACE_NOT_CURRENT",
    ),
    "EX-R77-TRAIT-P-001": (
        "accept", ["fixed_operator_conformance_overloading", "iterator_protocol_core",
                   "trait_binding_failable_v1"], None,
    ),
    "EX-R77-TRAIT-NG-001": (
        "reject", ["fixed_operator_conformance_overloading"],
        "TRAIT_LANGUAGE_ROLE_OWNER_NOT_CORE",
    ),
    "EX-R77-NUM-P-001": (
        "accept", ["numeric_literal_lexical_contract", "numeric_literal_suffix",
                   "complex_core_numeric_value"], None,
    ),
    "EX-R77-NUM-NG-001": (
        "reject", ["numeric_literal_lexical_contract", "numeric_literal_suffix"],
        "NUMERIC_TYPE_SUFFIX_REMOVED",
    ),
}

FEATURE_PROFILES = {
    "basic_index_operator": "STABLE_DESIGN",
    "call_side_positional_unfold_star_msp": "STABLE_DESIGN",
    "comprehension_unfold": "STABLE_DESIGN",
    "fixed_operator_conformance_overloading": "STABLE_DESIGN",
    "inclusive_slice_range_canonical_msp": "STABLE_DESIGN",
    "iterator_protocol_core": "STABLE_DESIGN",
    "map_unfold_double_star_current": "STABLE_DESIGN",
    "named_rest_parameter_record_msp": "STABLE_DESIGN",
    "numeric_array_multiaxis_slice_readonly_view_msp": "STABLE_DESIGN",
    "numeric_literal_suffix": "NOT_CURRENT",
    "one_based_sequence_logical_indexing": "STABLE_DESIGN",
    "range_step_expression_surface_clarification": "STABLE_DESIGN",
    "runtime_range_step_expression": "STABLE_DESIGN",
    "sequence_positional_rest_pattern": "STABLE_DESIGN",
    "slice_logical_domain_preservation": "STABLE_DESIGN",
    "structured_record_map_pattern": "STABLE_DESIGN",
    "trait_binding_failable_v1": "STABLE_GROUP",
}

REQUIRED_DIAGNOSTICS = {
    "LEGACY_REST_UNFOLD_SPELLING_REMOVED",
    "NAMED_REST_REQUIRES_RECORD_LABEL_SOURCE",
    "RANGE_STEP_ZERO",
    "RANGE_STEP_DIRECTION_MISMATCH",
    "RANGE_ONE_SIDED_FINITE_DOMAIN",
    "RANGE_OPERATOR_SPELLING_NOT_CURRENT",
    "SLICE_OPEN_BOUND_FORM_INVALID",
    "SLICE_AXIS_COUNT_MISMATCH",
    "PLACE_REPLACE_NOT_ADMITTED",
    "OPTIONAL_BINDING_SOURCE_NOT_CURRENT",
    "NUMERIC_TYPE_SUFFIX_REMOVED",
    "RETURN_TYPE_DIRECTED_OPERATOR_RESOLUTION_FORBIDDEN",
    "UINT_NEGATIVE_CONTEXT_ADAPTER_FORBIDDEN",
    "LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE",
}

REQUIRED_GRAMMAR_RHS = {
    "RequiresClause": '"requires" PredicateExpr',
    "RepeatedParameter": 'Identifier ".." TypeAnnotation',
    "NamedRestParameter": 'Identifier "**" NamedRestRequirementClause?',
    "NamedRestRequirementClause": '"requires" "{" NamedRestRequirementEntries "}"',
    "NamedRestRequirementEntry": 'Identifier ":" TypeRef',
    "ParenTypeItem": 'FunctionTypeModeItem | TypeRef | TypeRef ".." | TypeRef "**"',
    "RecordRestPattern": 'RestBinder "**"',
    "MapPatternEntry": 'MapDestination ":" MapKeyPattern | MapRestPattern',
    "MapRestPattern": '".." RestBinder',
    "ListRestPattern": 'RestBinder ".."',
    "AssigneeRestPattern": '("_" | Identifier) ".."',
    "AssigneeRecordRestPattern": '("_" | Identifier) "**"',
    "GuardedBindingStmt": '"let" "?" BindingPattern "=" Expr "else" Pattern "=>" GuardedBindingExit StatementBoundary?',
    "MutableListStructuralEditStmt": 'MutableListInsertStmt | MutableListRemoveStmt',
    "MutableListInsertPayload": 'Expr | "*" Expr',
    "PositionalUnfoldArgument": '"*" Expr',
    "NamedUnfoldArgument": '"**" Expr',
    "IndexSuffix": '"[" SliceAxisList "]"',
    "SliceAxisList": 'SliceAxis ("," SliceAxis)*',
    "SliceAxis": 'SliceRange | SliceIndexExpr | AxisWildcard',
    "SliceRange": 'SliceBound? ".." SliceBound? | SliceBound? "..<" SliceBound',
    "AxisWildcard": '"*"',
    "UnfoldClause": '"for" Pattern "in" "*" Expr',
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_chunk_rows(root: Path, relative_pattern: str, parsed: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    paths = sorted(root.glob(relative_pattern))
    if not paths:
        raise ValueError("no JSON chunks matched: %s" % relative_pattern)
    for path in paths:
        value = load_json(path)
        parsed.append(path.relative_to(root).as_posix())
        if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
            raise ValueError("chunk must be an array of objects: %s" % path)
        rows.extend(value)
    return rows


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def grammar_productions(grammar_text: str) -> Tuple[Dict[str, str], str]:
    stripped = re.sub(r"\(\*.*?\*\)", "", grammar_text, flags=re.DOTALL)
    productions: Dict[str, str] = {}
    for match in re.finditer(
        r"(?m)^([A-Za-z][A-Za-z0-9_]*)\s*::=\s*(.*?);", stripped, flags=re.DOTALL
    ):
        productions[match.group(1)] = normalize_space(match.group(2))
    return productions, stripped


def collect_prefixed_enum_strings(value: Any, prefix: str) -> Set[str]:
    """Collect only closed JSON-Schema enum members in the requested domain."""
    found: Set[str] = set()
    if isinstance(value, dict):
        enum = value.get("enum")
        if isinstance(enum, list):
            found.update(
                item for item in enum
                if isinstance(item, str) and item.startswith(prefix)
            )
        for child in value.values():
            found.update(collect_prefixed_enum_strings(child, prefix))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_prefixed_enum_strings(child, prefix))
    return found


def extract_example_code(root: Path, row: Dict[str, Any]) -> str:
    source = root / row["source_file"]
    lines = source.read_text(encoding="utf-8").splitlines()
    start = row["card_line_start"]
    end = row["card_line_end"]
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        raise ValueError("invalid one-based card range for %s" % row.get("example_id"))
    card = lines[start - 1:end]
    opening = next(index for index, line in enumerate(card) if line.startswith("```deeplus"))
    closing = next(index for index in range(opening + 1, len(card)) if card[index].startswith("```"))
    return "\n".join(card[opening + 1:closing])


def evaluate(root: Path, docs: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, int]]:
    failures: Dict[str, List[str]] = {}

    def require(check_id: str, condition: bool, message: str) -> None:
        if not condition:
            failures.setdefault(check_id, []).append(message)

    contract = docs["contract"]
    fixture = docs["fixture"]
    frontend = docs["frontend"]
    pointer = docs["pointer"]
    receipt = docs["receipt"]
    decision = docs["decision"]
    grammar = docs["grammar"]
    productions, grammar_without_comments = grammar_productions(grammar)
    diagnostics = docs["diagnostics"]
    relations = docs["relations"]
    features = docs["features"]
    examples = docs["examples"]
    prelude = docs["prelude"]

    check = "R77-AT-001-IDENTITY-CURRENT-FENCE"
    require(check, contract.get("decision_id") == DECISION_ID, "contract decision ID differs")
    require(check, fixture.get("decision_id") == DECISION_ID, "fixture decision ID differs")
    for fragment in (
        "decision_id: %s" % DECISION_ID,
        "status: VERIFIED_CLOSED_BY_POST_MERGE_READBACK",
        "current_authority_active: true",
        "artifact_self_binding: false",
        "github_mutation: semantic surface integrated at da734c608c0d583a671c0da9e14da00bff42affd",
        "publication_closure: PR #77 / 10e64f492f0529610673846139afcf0d95175663 / tree 8e08d498795c1054e392f82802f54d92cf2c215a",
    ):
        require(check, fragment in decision, "decision fence missing: %s" % fragment)
    require(check, contract.get("status") == "VERIFIED_CLOSED_BY_POST_MERGE_READBACK", "contract status differs")
    transition = contract.get("source_transition", {})
    require(check, transition.get("mode") == "ATOMIC_FORCED_CUTOVER", "cutover mode differs")
    require(check, transition.get("legacy_alias_count") == 0, "legacy alias count is not zero")
    require(check, transition.get("github_mutation") is True, "contract does not record the semantic main integration")
    require(check, transition.get("current_authority_active") is True, "current authority is absent")
    require(check, transition.get("artifact_self_binding") is False, "artifact self-binding fence differs")
    require(check, transition.get("semantic_publication_commit") == "da734c608c0d583a671c0da9e14da00bff42affd", "semantic publication commit differs")
    require(check, transition.get("publication_closure_commit") == "10e64f492f0529610673846139afcf0d95175663", "publication closure commit differs")
    require(check, transition.get("publication_closure_receipt") == RECEIPT_REL, "publication receipt path differs")
    require(check, pointer.get("candidate_binding") == {
        "mode": "semantic_publication_target_bound_by_external_post_merge_receipt",
        "receipt_location": RECEIPT_REL,
        "current_binding": False,
        "self_binding_forbidden": True,
    }, "current pointer receipt/self-binding fence differs")
    semantic_receipt = receipt.get("semantic_publication", {})
    closure_receipt = receipt.get("publication_closure", {})
    binding_receipt = receipt.get("binding", {})
    require(check, receipt.get("result") == "VERIFIED_CLOSED", "receipt result differs")
    require(check, semantic_receipt.get("merge_commit") == "da734c608c0d583a671c0da9e14da00bff42affd", "receipt semantic commit differs")
    require(check, closure_receipt.get("merge_commit") == "10e64f492f0529610673846139afcf0d95175663", "receipt closure commit differs")
    require(check, closure_receipt.get("tree") == "8e08d498795c1054e392f82802f54d92cf2c215a", "receipt closure tree differs")
    require(check, closure_receipt.get("live_main_exact_match_at_audit_start") is True, "receipt live-main readback differs")
    require(check, binding_receipt.get("semantic_authority_active") is True
            and binding_receipt.get("artifact_self_binding") is False
            and binding_receipt.get("pointer_current_binding") is False,
            "receipt authority/self-binding semantics differ")

    check = "R77-AT-002-GOVERNANCE-FENCE"
    evidence = contract.get("evidence", {})
    invariants = fixture.get("invariants", {})
    require(check, evidence.get("semantic_p0") == invariants.get("semantic_p0") == 0,
            "semantic P0 is not exact zero")
    require(check, evidence.get("open_feature_p1") == invariants.get("open_feature_p1") == 22,
            "feature P1 count is not exact 22")
    require(check, evidence.get("separate_open_m13_actions") == invariants.get("separate_open_m13_actions") == 4,
            "M13 action count is not exact four")
    require(check, evidence.get("product_lanes") == invariants.get("product_lanes") == "15/15_NOT_RUN",
            "product-lane fence differs")
    require(check, evidence.get("production_execution") == fixture.get("product_execution") == "NOT_RUN",
            "product execution is overclaimed")
    require(check, invariants.get("github_mutation") == 0, "fixture claims GitHub mutation")
    lanes = pointer.get("product_lanes", {})
    require(check, isinstance(lanes, dict) and len(lanes) == 15
            and set(lanes.values()) == {"NOT_RUN"}, "pointer product lanes are not 15/15 NOT_RUN")
    action_ids = [row.get("id") for row in pointer.get("open_actions", []) if isinstance(row, dict)]
    require(check, len(action_ids) == len(set(action_ids)), "pointer open-action IDs are duplicated")
    require(check, sorted(value for value in action_ids if value.startswith("M13-")) == sorted(OPEN_M13),
            "pointer M13 action set differs")
    require(check, sorted(value for value in action_ids if value.startswith(("CE-", "TCC-", "SFD-"))) == sorted(OPEN_FEATURE_P1),
            "pointer feature P1 set differs from exact 22")
    require(check, "R77-A006" in action_ids, "Failable target-bound closure action is absent")

    check = "R77-AT-003-COLLECT-UNFOLD-REQUIRES"
    collect = contract.get("surface", {}).get("collect_unfold", {})
    require(check, collect.get("positional_formal") == "name..: T", "positional formal differs")
    require(check, collect.get("positional_function_residue") == "T..", "positional type residue differs")
    require(check, collect.get("named_formal") == "name**", "named formal differs")
    require(check, collect.get("named_function_residue") == "NamedPack**", "named type residue differs")
    require(check, collect.get("positional_pattern") == ["name..", "_.."], "positional pattern rest differs")
    require(check, collect.get("static_named_pattern") == ["name**", "_**"], "named pattern rest differs")
    require(check, collect.get("positional_outward_unfold") == "*Expr", "positional unfold differs")
    require(check, collect.get("static_named_outward_unfold") == "**Expr", "named unfold differs")
    require(check, collect.get("outward_unfold_is_general_pratt_prefix") is False,
            "unfold became a general Pratt prefix")
    require(check, collect.get("outward_unfold_owners") == {
        "positional": ["call_argument", "list_entry", "mutable_list_insertion_payload", "comprehension_source"],
        "static_named": ["call_argument", "record_materialization_entry", "map_entry"],
    }, "closed unfold-owner sets differ")
    requirement = contract.get("surface", {}).get("named_rest_requirements", {})
    require(check, requirement == {
        "owner": "NamedRestParameter",
        "grammar_node": "NamedRestRequirementClause",
        "shape": "requires { label: TypeRef ... }",
        "callable_requires_preserved": "RequiresClause ::= requires PredicateExpr",
    }, "named-rest/callable requires partition differs")
    front_collect = frontend.get("integrated_collect_unfold_frontend_contract", {})
    for key, value in {
        "decision": DECISION_ID,
        "positional_parameter": "name..: T",
        "positional_function_type_residue": "T..",
        "named_parameter": "name**",
        "named_function_type_residue": "NamedPack**",
        "positional_unfold_surface": "*Expr",
        "named_unfold_surface": "**Expr",
        "structural_unfold_general_prefix": False,
        "runtime_shape_selection": False,
        "expected_type_or_overload_selects_shape": False,
        "product_support": "NOT_RUN",
    }.items():
        require(check, front_collect.get(key) == value, "frontend collect/unfold differs: %s" % key)

    check = "R77-AT-004-PATTERN-OWNER-PARTITION"
    patterns = contract.get("surface", {}).get("patterns", {})
    require(check, patterns == {
        "record_family_field": "label: Pattern",
        "record_family_remainder": ["name**", "_**"],
        "map_orientation": "Pattern: key",
        "map_remainder": ["..name", ".._"],
        "tuple_rest": "PREVIEW_NOT_PROMOTED",
    }, "Record/Map/rest owner partition differs")

    check = "R77-AT-005-RANGE-CONTRACT"
    range_contract = contract.get("surface", {}).get("range", {})
    expected_range = {
        "bounded_inclusive": "start..end",
        "bounded_exclusive": "start..<end",
        "one_sided": "start...",
        "step_suffix": ":step",
        "evaluation": "start_then_end_if_present_then_step_exactly_once",
        "zero_step": "REJECT",
        "direction_mismatch": "REJECT",
        "overflow": "TERMINATE_BEFORE_OVERFLOW",
        "one_sided_finite_enum": "REJECT",
    }
    for key, value in expected_range.items():
        require(check, range_contract.get(key) == value, "range law differs: %s" % key)
    require(check, range_contract.get("removed") == ["terminal start..", "..>"], "removed range forms differ")
    front_range = frontend.get("range_index_frontend_contract", {}).get("range", {})
    require(check, front_range.get("bounded_inclusive") == "start..end"
            and front_range.get("bounded_exclusive") == "start..<end"
            and front_range.get("one_sided") == "start..."
            and front_range.get("step_suffix") == ":step"
            and front_range.get("one_sided_finite_enum") == "REJECT",
            "frontend range projection differs")

    check = "R77-AT-006-INDEX-SLICE-ONE-BASED"
    indexing = contract.get("surface", {}).get("indexing", {})
    require(check, indexing.get("axis_separator") == ","
            and indexing.get("axis_separator_owner") == "IndexSuffix_only", "axis ownership differs")
    require(check, indexing.get("open_slices") == ["[..<end]", "[..end]", "[start..]", "[..]"],
            "open-slice set differs")
    require(check, indexing.get("rejected") == ["[start..<]", "tuple_as_gather", "implicit_linear_indexing"],
            "rejected index set differs")
    require(check, indexing.get("coordinate_origin") == 1, "coordinate origin is not one")
    require(check, indexing.get("numeric_array_axis_count") == "exact_source_rank"
            and indexing.get("scalar_axis_rule") == "drop"
            and indexing.get("result_rank") == "count_non_scalar_axes"
            and indexing.get("multi_axis_composition") == "cartesian",
            "comma-axis rank/composition law differs")
    front_index = frontend.get("range_index_frontend_contract", {}).get("index", {})
    require(check, front_index.get("coordinates") == "one-based", "frontend indexing is not one-based")
    require(check, front_index.get("open_slice_surfaces") == ["[..<end]", "[..end]", "[start..]", "[..]"],
            "frontend open-slice set differs")

    check = "R77-AT-007-MUTABLE-LIST-CLOSED-13"
    mutable = contract.get("surface", {}).get("mutable_list_edit", {})
    require(check, contract.get("closed_prelude_operations") == MUTABLE_LIST_OPERATIONS,
            "closed MutableList operation set/order differs")
    require(check, len(set(MUTABLE_LIST_OPERATIONS)) == 13, "expected operation constant is not exact 13")
    require(check, mutable.get("statement_only") is True
            and mutable.get("ordinary_bracket_replace_activated") is False
            and mutable.get("dedicated_hir_mir_opcode") is False
            and mutable.get("mutation_commits") == 1
            and mutable.get("failure_preserves_target") is True
            and mutable.get("hidden_clone_snapshot_move") is False,
            "MutableList statement/lowering/atomicity fence differs")
    mutable_rows = [row for row in prelude if row.get("entry_id") == "mutable_list_t"]
    require(check, len(mutable_rows) == 1, "Prelude MutableList<T> row is not unique")
    if len(mutable_rows) == 1:
        signatures = mutable_rows[0].get("signatures", [])
        found = [operation for operation in MUTABLE_LIST_OPERATIONS
                 if sum(operation + "<" in signature for signature in signatures) == 1]
        require(check, found == MUTABLE_LIST_OPERATIONS, "Prelude does not bind every closed operation exactly once")
        require(check, mutable_rows[0].get("product_support") == "NOT_RUN", "Prelude claims product support")
    front_mutable = frontend.get("mutable_list_structural_edit_frontend_contract", {})
    require(check, front_mutable.get("statement_only") is True
            and front_mutable.get("dedicated_hir_or_mir") is False
            and front_mutable.get("mutation_commit_count") == 1
            and front_mutable.get("product_support") == "NOT_RUN",
            "frontend MutableList projection differs")

    check = "R77-AT-008-TRAIT-LANGUAGE-ROLE-4"
    roles = contract.get("trait_roles", {})
    require(check, roles.get("identity") == "TraitLanguageRoleId"
            and roles.get("core_owned") is True, "Trait role identity/owner differs")
    require(check, roles.get("roles") == TRAIT_ROLE_MEMBERS, "Trait role membership differs")
    require(check, roles.get("operator_glyph_count") == 13
            and roles.get("operator_role_selects_glyph") is False
            and roles.get("user_role_declaration") == "REJECT"
            and roles.get("proof_role") == "INTERNAL_DEFERRED",
            "Trait role closure fence differs")
    schema_role_ids = (
        collect_prefixed_enum_strings(docs["hir_schema"], "TRAIT_LANGUAGE_ROLE_")
        | collect_prefixed_enum_strings(docs["api_schema"], "TRAIT_LANGUAGE_ROLE_")
    )
    require(check, schema_role_ids == TRAIT_ROLE_IDS, "schema TraitLanguageRoleId universe differs")
    front_roles = frontend.get("trait_conformance_surface_contract", {}).get("language_role_registry", {})
    require(check, front_roles.get("roles") == TRAIT_ROLE_MEMBERS
            and front_roles.get("core_owned") is True
            and front_roles.get("user_role_declaration") == "REJECT",
            "frontend Trait role registry differs")

    check = "R77-AT-009-FAILABLE-BINDING"
    failable = contract.get("failable_binding", {})
    expected_failable = {
        "surface": "let? Pattern = Expr else Pattern => ExitStatement",
        "branch": "def ::branch(move source: Self) -> BindingBranch<Success, Failure> throws Never effects {}",
        "source_mode": "consume_once",
        "else_required": True,
        "success_pattern": "IRREFUTABLE",
        "failure_pattern": "IRREFUTABLE",
        "failure_continuation": "STRUCTURALLY_UNCONDITIONAL_EXIT",
        "var_form": "REJECT",
        "bare_form": "REJECT",
        "if_while_generalization": "REJECT",
        "option_failure": "Unit",
        "result_failure": "E",
    }
    require(check, failable == expected_failable, "Failable guarded-binding contract differs")
    front_failable = frontend.get("trait_conformance_surface_contract", {}).get("failable_binding", {})
    require(check, front_failable.get("trait") == "trait#binding Failable"
            and front_failable.get("source_evaluation_count") == 1
            and front_failable.get("source_transfer") == "CONSUME"
            and front_failable.get("else_required") is True
            and front_failable.get("failure_continuation") == "STRUCTURALLY_UNCONDITIONAL_EXIT"
            and front_failable.get("product_support") == "NOT_RUN",
            "frontend Failable projection differs")

    check = "R77-AT-010-NUMERIC-SUFFIX-CUTOVER"
    numeric = contract.get("numeric_suffix_cutover", {})
    require(check, numeric.get("removed_suffixes") == REMOVED_SUFFIXES, "removed suffix set/order differs")
    require(check, numeric.get("preserved_suffix_domains") == [
        "floating_look_imaginary_i", "measure_unit", "rational_literal"
    ], "preserved suffix-domain set differs")
    require(check, numeric.get("unconstrained_defaults") == {
        "integer": "Int", "real": "Float64", "imaginary_or_complex": "Complex<Float64>"
    }, "unconstrained numeric defaults differ")
    for key in ("smallest_fit", "width_fit_overload_ranking",
                "expected_result_selects_operator", "generic_Type_bang_cast"):
        require(check, numeric.get(key) is False, "numeric selection fence differs: %s" % key)
    require(check, numeric.get("diagnostic") == "NUMERIC_TYPE_SUFFIX_REMOVED",
            "removed-suffix diagnostic differs")

    check = "R77-AT-011-GRAMMAR-CURRENT-ONLY"
    for production, expected_rhs in REQUIRED_GRAMMAR_RHS.items():
        require(check, productions.get(production) == expected_rhs,
                "grammar production differs: %s" % production)
    for removed_token in ("TRIPLE_STAR", "DOT_DOT_GT"):
        require(check, removed_token not in grammar_without_comments,
                "removed admitted token remains: %s" % removed_token)
    for removed_spelling in ('"***"', '"..>"'):
        require(check, removed_spelling not in grammar_without_comments,
                "removed admitted spelling remains: %s" % removed_spelling)
    for suffix in REMOVED_SUFFIXES:
        require(check, '"%s"' % suffix not in grammar_without_comments,
                "removed numeric suffix remains admitted: %s" % suffix)

    check = "R77-AT-012-DIAGNOSTIC-RELATION-BINDING"
    diagnostic_ids = [row.get("diagnostic_id") for row in diagnostics]
    require(check, all(count == 1 for count in Counter(diagnostic_ids).values()),
            "diagnostic IDs are not unique")
    registry = {row.get("diagnostic_id"): row for row in diagnostics}
    require(check, REQUIRED_DIAGNOSTICS.issubset(registry), "required R77 diagnostic is absent")
    for diagnostic_id in REQUIRED_DIAGNOSTICS & set(registry):
        row = registry[diagnostic_id]
        require(check, row.get("diagnostic_maturity") == "active"
                and row.get("diagnostic_status") == "active"
                and row.get("diagnostic_class") == "current_source"
                and row.get("product_support") == "NOT_RUN",
                "diagnostic profile differs: %s" % diagnostic_id)
    relation_rows = [row for row in relations if row.get("predicate_id") == "ListLiteralElementJoinAdmitted"]
    primary = [row for row in relation_rows if row.get("relation") == "primary"]
    secondary = [row for row in relation_rows if row.get("relation") == "secondary"]
    require(check, primary == [{
        "violation_id": "ListLiteralElementJoinAdmitted:default",
        "predicate_id": "ListLiteralElementJoinAdmitted",
        "diagnostic_id": "LIST_LITERAL_ELEMENT_JOIN_FAILED",
        "relation": "primary",
    }], "ListLiteralElementJoinAdmitted primary relation differs")
    require(check, {row.get("diagnostic_id") for row in secondary} == {
        "LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE",
        "UINT_NEGATIVE_CONTEXT_ADAPTER_FORBIDDEN",
        "NUMERIC_TYPE_SUFFIX_REMOVED",
    } and len(secondary) == 3 and all(row.get("violation_id") is None for row in secondary),
            "ListLiteralElementJoinAdmitted secondary relation set differs")

    check = "R77-AT-013-FEATURE-PROFILES"
    feature_ids = [row.get("feature_id") for row in features]
    require(check, all(count == 1 for count in Counter(feature_ids).values()), "feature IDs are not unique")
    feature_map = {row.get("feature_id"): row for row in features}
    for feature_id, status in FEATURE_PROFILES.items():
        row = feature_map.get(feature_id)
        require(check, row is not None, "feature row absent: %s" % feature_id)
        if row is not None:
            require(check, row.get("status_enum") == status, "feature status differs: %s" % feature_id)
            require(check, row.get("product_support") == "NOT_RUN", "feature claims product support: %s" % feature_id)
    one_based_index = feature_map.get("one_based_sequence_logical_indexing", {})
    require(check, "1..length" in one_based_index.get("notes", ""), "one-based List index law is absent")
    named_rest = feature_map.get("named_rest_parameter_record_msp", {})
    require(check, "EX-R77-CALL-P-001" in named_rest.get("normative_trace_refs", {}).get("examples", []),
            "named-rest feature lacks R77 example trace")

    check = "R77-AT-014-EXAMPLE-PROJECTIONS"
    r77_rows = [row for row in examples if row.get("example_id", "").startswith("EX-R77-")]
    example_counts = Counter(row.get("example_id") for row in r77_rows)
    require(check, set(example_counts) == set(R77_EXAMPLES)
            and all(count == 1 for count in example_counts.values()), "R77 example ID universe differs")
    r77_map = {row.get("example_id"): row for row in r77_rows}
    extracted_code: Dict[str, str] = {}
    for example_id, expected in R77_EXAMPLES.items():
        row = r77_map.get(example_id)
        if row is None:
            continue
        outcome, feature_refs, diagnostic = expected
        require(check, row.get("expected_outcome") == outcome
                and row.get("feature_ids") == feature_refs
                and row.get("source_feature_ids") == feature_refs
                and row.get("primary_diagnostic") == diagnostic,
                "example projection differs: %s" % example_id)
        require(check, row.get("certification_status") == "design_static_product_not_run"
                and row.get("parser_status") == "not_run"
                and row.get("checker_status") == "not_run",
                "example overclaims execution: %s" % example_id)
        require(check, row.get("line_range_scope") == "one_based_inclusive_within_source_file",
                "example range convention differs: %s" % example_id)
        try:
            code = extract_example_code(root, row)
            extracted_code[example_id] = code
            digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
            require(check, digest == row.get("code_sha256"), "example code hash differs: %s" % example_id)
        except (OSError, ValueError, KeyError, StopIteration) as exc:
            require(check, False, "example extraction failed %s: %s" % (example_id, exc))
    index_code = extracted_code.get("EX-R77-INDEX-P-001", "")
    require(check, "matrix[1, 2]" in index_code and "matrix[1, ..]" in index_code
            and "matrix[0" not in index_code, "R77 indexing example does not demonstrate one-based axes")

    check = "R77-AT-015-FIXTURE-EXACT"
    for group, expected_ids in EXPECTED_FIXTURE_IDS.items():
        rows = fixture.get(group, [])
        ids = [row.get("id") for row in rows if isinstance(row, dict)]
        require(check, set(ids) == expected_ids and len(ids) == len(set(ids)),
                "fixture ID set differs: %s" % group)
    rejected_rows = fixture.get("rejected", [])
    require(check, all(row.get("canonical_residue") is False for row in rejected_rows),
            "rejected fixture commits canonical residue")
    positive_sources = "\n".join(row.get("source", "") for row in fixture.get("positive", []))
    require(check, "args..: String" in positive_sources and "options**" in positive_sources
            and "*args" in positive_sources and "**options" in positive_sources,
            "collect/unfold fixture does not bind both channels")
    require(check, "matrix[1, ..]" in positive_sources and "values[..<5]" in positive_sources,
            "one-based/open-slice fixture is absent")

    checks: List[Dict[str, Any]] = []
    check_ids = [
        "R77-AT-001-IDENTITY-CURRENT-FENCE",
        "R77-AT-002-GOVERNANCE-FENCE",
        "R77-AT-003-COLLECT-UNFOLD-REQUIRES",
        "R77-AT-004-PATTERN-OWNER-PARTITION",
        "R77-AT-005-RANGE-CONTRACT",
        "R77-AT-006-INDEX-SLICE-ONE-BASED",
        "R77-AT-007-MUTABLE-LIST-CLOSED-13",
        "R77-AT-008-TRAIT-LANGUAGE-ROLE-4",
        "R77-AT-009-FAILABLE-BINDING",
        "R77-AT-010-NUMERIC-SUFFIX-CUTOVER",
        "R77-AT-011-GRAMMAR-CURRENT-ONLY",
        "R77-AT-012-DIAGNOSTIC-RELATION-BINDING",
        "R77-AT-013-FEATURE-PROFILES",
        "R77-AT-014-EXAMPLE-PROJECTIONS",
        "R77-AT-015-FIXTURE-EXACT",
    ]
    for check_id in check_ids:
        checks.append({
            "check_id": check_id,
            "result": "FAIL" if failures.get(check_id) else "PASS",
        })
    errors = ["%s:%s" % (check_id, message)
              for check_id in check_ids for message in failures.get(check_id, [])]
    counts = {
        "open_feature_p1": len(OPEN_FEATURE_P1),
        "separate_open_m13_actions": len(OPEN_M13),
        "product_lanes_not_run": len(lanes) if set(lanes.values()) == {"NOT_RUN"} else 0,
        "closed_mutable_list_operations": len(MUTABLE_LIST_OPERATIONS),
        "trait_language_role_ids": len(TRAIT_ROLE_IDS),
        "removed_numeric_suffixes": len(REMOVED_SUFFIXES),
        "r77_examples": len(r77_rows),
    }
    return checks, errors, counts


def load_documents(root: Path) -> Tuple[Dict[str, Any], List[str]]:
    parsed: List[str] = []

    def one(relative: str) -> Any:
        path = root / relative
        value = load_json(path)
        parsed.append(relative)
        return value

    documents: Dict[str, Any] = {
        "decision": (root / DECISION_REL).read_text(encoding="utf-8"),
        "grammar": (root / GRAMMAR_REL).read_text(encoding="utf-8"),
        "contract": one(CONTRACT_REL),
        "fixture": one(FIXTURE_REL),
        "frontend": one(FRONTEND_REL),
        "pointer": one(POINTER_REL),
        "receipt": one(RECEIPT_REL),
        "hir_schema": one(HIR_SCHEMA_REL),
        "api_schema": one(API_SCHEMA_REL),
        "diagnostics": load_chunk_rows(root, "spec/diagnostics/catalog/chunks/*.json", parsed),
        "relations": load_chunk_rows(root, "spec/diagnostics/relations/chunks/*.json", parsed),
        "features": load_chunk_rows(root, "spec/features/catalog/chunks/*.json", parsed),
        "examples": load_chunk_rows(root, "examples/manifests/by-outcome/chunks/*.json", parsed),
        "prelude": load_chunk_rows(root, "library/prelude/signatures/chunks/*.json", parsed),
    }
    return documents, parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    parsed: List[str] = []
    try:
        documents, parsed = load_documents(root)
        checks, errors, counts = evaluate(root, documents)
        checks.insert(0, {"check_id": "R77-AT-000-JSON-PARSE", "result": "PASS"})
    except Exception as exc:  # noqa: BLE001 - receipt must preserve exact static failure.
        checks = [{"check_id": "R77-AT-000-JSON-PARSE", "result": "FAIL"}]
        errors = ["R77-AT-000-JSON-PARSE:%s:%s" % (type(exc).__name__, exc)]
        counts = {}

    result = "PASS" if not errors and all(row["result"] == "PASS" for row in checks) else "FAIL"
    receipt = {
        "schema": "deeplus.integrated-surface-atomic-cutover-r77-validation-receipt/r1",
        "result": result,
        "decision_id": DECISION_ID,
        "evidence_level": "E2_DESIGN_STATIC",
        "scope": "R77_CURRENT_SEMANTIC_SURFACE_VERIFIED_CLOSED_BY_POST_MERGE_READBACK",
        "check_count": len(checks),
        "passed_check_count": sum(row["result"] == "PASS" for row in checks),
        "checks": checks,
        "parsed_json_file_count": len(parsed),
        "counts": counts,
        "semantic_p0": 0,
        "product_execution": "NOT_RUN",
        "github_mutation": True,
        "implementation_claim": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
