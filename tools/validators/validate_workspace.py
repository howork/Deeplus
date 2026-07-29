#!/usr/bin/env python3
"""Static closure validator for the Deeplus current or candidate workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
from collections import Counter
from pathlib import Path
from typing import Any


LEGACY_REVISION = "r51f3-current-publication-m1.3"
POST_PR16_REVISION = "r51f3-post-pr16-preview-design-r4-cma-r1"
LANGUAGE_COHERENCE_REVISION = "r51f3-current-trait-operator-refinement-r1"
TRAIT_OPERATOR_REFINEMENT_REVISION = "r51f3-current-trait-operator-refinement-r1"
PREVIOUS_LANGUAGE_COHERENCE_REVISION = "r51f3-current-pattern-sequence-multivalue-r1"
PATTERN_COMPONENT_REVISION = "r51f3-current-trait-operator-refinement-r1"
LANGUAGE_COHERENCE_CONTRACT_REL = (
    "spec/contracts/language-coherence-current-integrity-r1.json"
)
EXCLUDED_TREE_PARTS = {
    ".git",
    "target",
    "dist",
    "candidate",
    "tmp",
    "__pycache__",
}
EXPECTED = {
    "features": 719, "diagnostics": 1424, "predicates": 268,
    "predicate_fixtures": 819, "no_go": 155,
    "hard_keywords": 29, "contextual_words": 105,
}
REQUIRED_FEATURE_IDS = (
    "named_rest_parameter_record_msp",
    "schema_named_unfolding",
    "unicode_char_literal_single_quote_msp",
    "char_unicode_scalar_value_model",
    "strict_boolean_word_operators_msp",
    "sequential_boolean_control_words_msp",
    "standalone_bang_not_current_not_word_law",
    "rightward_flow_dollar_local_binding_msp",
    "optional_chaining_not_current_law",
    "ternary_conditional_expression",
    "ternary_short_expression_stable_profile",
    "at_control_expression_family",
    "local_value_body_msp",
    "match_exhaustiveness_phase_a",
    "match_arm_guard_msp",
    "bytes_literal_hash_bytes_msp",
    "string_interpolation_braced_expr_core",
    "string_interpolation_format_spec_core",
    "string_interpolation_shorthand_factor_msp",
    "numeric_array_postfix_transpose_caret_msp",
)
MIR_DISPOSITIONS = {
    "named_rest_parameter_record_msp": "LAW_PRESENT",
    "schema_named_unfolding": "GENERIC_LAW_PRESENT",
    "unicode_char_literal_single_quote_msp": "LAW_PRESENT",
    "char_unicode_scalar_value_model": "LAW_PRESENT",
    "strict_boolean_word_operators_msp": "LAW_PRESENT",
    "sequential_boolean_control_words_msp": "LAW_PRESENT",
    "standalone_bang_not_current_not_word_law": "NO_DISTINCT_MIR_OP",
    "rightward_flow_dollar_local_binding_msp": "LAW_PRESENT",
    "optional_chaining_not_current_law": "NOT_APPLICABLE(rejected current surface)",
    "ternary_conditional_expression": "LAW_PRESENT",
    "ternary_short_expression_stable_profile": "LAW_PRESENT",
    "at_control_expression_family": "GENERIC_LAW_PRESENT",
    "local_value_body_msp": "NO_DISTINCT_MIR_OP",
    "match_exhaustiveness_phase_a": "NOT_APPLICABLE(checker-only rejection before MIR)",
    "match_arm_guard_msp": "GENERIC_LAW_PRESENT",
    "bytes_literal_hash_bytes_msp": "LAW_PRESENT",
    "string_interpolation_braced_expr_core": "LAW_PRESENT",
    "string_interpolation_format_spec_core": "DEFERRED_PRODUCT_HANDOFF",
    "string_interpolation_shorthand_factor_msp": "LAW_PRESENT",
    "numeric_array_postfix_transpose_caret_msp": "LAW_PRESENT",
}
SUPPLEMENTAL_MIR_FEATURE_IDS = (
    "no_string_char_bytes_implicit_conversion_law",
    "text_model_char_grapheme_current_law",
)
MATCH_GUARD_FIXIT = "combine predicates into one Bool guard or remove the extra guard"
FROZEN_UNCHANGED_SEMANTIC_HASHES = {
    "spec/grammar/deeplus.ebnf": "c844f1422b17001d279e7eeb897ad320dd780513de0b93297c986cec69916c72",
    "spec/frontend/frontend-model.json": "8dc54dca8bc16b22fe07824260c193d5da43b449cc408535290dd420f1bf53bb",
    "spec/types/type-system.md": "17ac6b139b0ffc422b091ef97ba900fe9f028400034f3e73534bb5d6c1fdae4a",
    "library/prelude/prelude.md": "41d4bdefb110dd4c648b986cca2a4b3ef26760d1f0ced321d4e6d0ce05249a8f",
}
EXPECTED_POINTER_KEYS = {
    "schema", "updated_at", "language_version", "spec_revision",
    "publication_authority_source", "audited_implementation_baseline",
    "candidate_binding", "authority_digest", "source_snapshot",
    "product_lanes", "open_actions", "required_next_reviews",
    "previous_pointer",
}
EXPECTED_NEXT_REVIEWS = [
    "M13-A002: Impl_ + Spec_ + Test_",
    "M13-A003: Design_ + Legal_",
    "M13-A004: Build_",
    "M13-A005: Design_ + Spec_ + Devel_",
]
EXPECTED_ACTION_IDS = ["M13-A002", "M13-A003", "M13-A004", "M13-A005"]
FIXED_OPERATOR_IDS = [
    "UnaryPlus", "UnaryMinus",
    "BinaryAdd", "BinarySubtract", "BinaryMultiply", "BinaryDivide",
    "BinaryRemainder", "BinaryEqual", "BinaryNotEqual", "BinaryLessThan",
    "BinaryLessThanOrEqual", "BinaryGreaterThan", "BinaryGreaterThanOrEqual",
]
FIXED_OPERATOR_TRAIT_ROOTS = [
    "UnaryPlus", "UnaryMinus", "Add", "Subtract", "Multiply", "Divide",
    "Remainder", "Eq", "Ord",
]
FIXED_OPERATOR_MAPPING = [
    (
        "UnaryPlus", "+", "prefix", "UnaryPlus", "UnaryPlus.positive",
        "UnaryPlus::Output", "ASSOCIATED_OUTPUT", "UnaryPlus::Output",
    ),
    (
        "UnaryMinus", "-", "prefix", "UnaryMinus", "UnaryMinus.negate",
        "UnaryMinus::Output", "ASSOCIATED_OUTPUT", "UnaryMinus::Output",
    ),
    (
        "BinaryAdd", "+", "binary_infix", "Add<Rhs>", "Add.add",
        "Add<Rhs>::Output", "ASSOCIATED_OUTPUT", "Add<Rhs>::Output",
    ),
    (
        "BinarySubtract", "-", "binary_infix", "Subtract<Rhs>",
        "Subtract.subtract", "Subtract<Rhs>::Output", "ASSOCIATED_OUTPUT",
        "Subtract<Rhs>::Output",
    ),
    (
        "BinaryMultiply", "*", "binary_infix", "Multiply<Rhs>",
        "Multiply.multiply", "Multiply<Rhs>::Output", "ASSOCIATED_OUTPUT",
        "Multiply<Rhs>::Output",
    ),
    (
        "BinaryDivide", "/", "binary_infix", "Divide<Rhs>", "Divide.divide",
        "Divide<Rhs>::Output", "ASSOCIATED_OUTPUT", "Divide<Rhs>::Output",
    ),
    (
        "BinaryRemainder", "%", "binary_infix", "Remainder<Rhs>",
        "Remainder.remainder", "Remainder<Rhs>::Output", "ASSOCIATED_OUTPUT",
        "Remainder<Rhs>::Output",
    ),
    (
        "BinaryEqual", "==", "binary_infix", "Eq<Rhs>", "Eq.equals",
        "Bool", "IDENTITY", "Bool.identity",
    ),
    (
        "BinaryNotEqual", "!=", "binary_infix", "Eq<Rhs>", "Eq.equals",
        "Bool", "BOOL_NEGATION", "Bool.not",
    ),
    (
        "BinaryLessThan", "<", "binary_infix", "Ord<Rhs>", "Ord.compare",
        "Bool", "COMPARE_SIGN_LT_ZERO", "compare_sign_lt_zero",
    ),
    (
        "BinaryLessThanOrEqual", "<=", "binary_infix", "Ord<Rhs>",
        "Ord.compare", "Bool", "COMPARE_SIGN_LE_ZERO", "compare_sign_le_zero",
    ),
    (
        "BinaryGreaterThan", ">", "binary_infix", "Ord<Rhs>", "Ord.compare",
        "Bool", "COMPARE_SIGN_GT_ZERO", "compare_sign_gt_zero",
    ),
    (
        "BinaryGreaterThanOrEqual", ">=", "binary_infix", "Ord<Rhs>",
        "Ord.compare", "Bool", "COMPARE_SIGN_GE_ZERO", "compare_sign_ge_zero",
    ),
]
FIXED_OPERATOR_COMPARISON_IDS = {
    "BinaryEqual", "BinaryNotEqual", "BinaryLessThan",
    "BinaryLessThanOrEqual", "BinaryGreaterThan",
    "BinaryGreaterThanOrEqual",
}
FIXED_OPERATOR_ARITHMETIC_PROFILE_ID = (
    "BORROWED_PURE_SYNCHRONOUS_NONCONSUMING_"
    "ARITHMETIC_DEFECT_PRECOMMIT"
)
FIXED_OPERATOR_COMPARISON_PROFILE_ID = (
    "BORROWED_PURE_TOTAL_SYNCHRONOUS_NONCONSUMING"
)
FIXED_OPERATOR_HIR_REQUIRED_FIELDS = [
    "operator_id",
    "operand_arity",
    "normalized_left_type_id",
    "normalized_right_type_id_or_null",
    "conformance_id",
    "witness_id",
    "method_id",
    "substitution",
    "output_type_id",
    "responsibility_profile_id",
]
FIXED_OPERATOR_SCHEMA_REQUIRED_FIELDS = [
    "operator_id",
    "operand_arity",
    "normalized_left_type_id",
    "normalized_right_type_id",
    "conformance_id",
    "witness_id",
    "method_id",
    "substitution_id",
    "output_type_id",
    "responsibility_profile_id",
    "dispatch_route",
    "runtime_relookup_count",
    "fallback_count",
]
FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP = {
    "operator_id": "operator_id",
    "operand_arity": "operand_arity",
    "normalized_left_type_id": "normalized_left_type_id",
    "normalized_right_type_id_or_null": "normalized_right_type_id",
    "conformance_id": "conformance_id",
    "witness_id": "witness_id",
    "method_id": "method_id",
    "substitution": "substitution_id",
    "output_type_id": "output_type_id",
    "responsibility_profile_id": "responsibility_profile_id",
}
FIXED_OPERATOR_SCHEMA_STAGE_CONSTANT_FIELDS = {
    "dispatch_route": "DIRECT_GLOBAL",
    "runtime_relookup_count": 0,
    "fallback_count": 0,
}
TRAIT_SURFACE_CASE_PROJECTION_SHA256 = {
    "TCS-R1-POS-001": "200a65fcdb4f4048e8ca3a9c47ee9a6a3b064d0e1a4c3cb213cee813eaa93964",
    "TCS-R1-POS-002": "bcf8175f86f6beeb7a2f408fb2c6caf0b01b3d7f22a330359a28c9de9a6bc987",
    "TCS-R1-POS-003": "702e9ad35b10a6e6423b6fac2ad91ef026aff2401f7b5cc34f913f6aea0ad3fb",
    "TCS-R1-POS-004": "75e53f203bfc6f8644e443b95bd8093627a69c7bbfdab057185dd3963e7529c3",
    "TCS-R1-POS-005": "a3d5f4ac2214934e98d4c46becf91e46c5c0a5ce85a7ffb4627fe0104c8d8677",
    "TCS-R1-POS-006": "6c9343d277a11511992a25c3d57f2bc442332529ef21e739aa2da664f208becb",
    "TCS-R1-POS-007": "7efc43d30b3ed5d4914c0fc06de63c57efcdf761d705d8ac5140af1ce6b20d60",
    "TCS-R1-POS-008": "720eb7a5e2c34957aed727753021715c349265dbb2fca89e73ae35a0b8531065",
    "TCS-R1-POS-009": "a517e10df764ba6e632ed864e19da000ea1de90591e59f62fcc6d86ae1248cc9",
    "TCS-R1-POS-010": "c16cab0427163c5821fb444476cfa070043d26fb4893e42e0482ce0d03bdd056",
    "TCS-R1-POS-011": "770707cc84b0399689e885e0be7132d03ef76b404bbf17bd0ae65bd63a5f31da",
    "TCS-R1-POS-012": "4dcf319599787633d85666851aea9503495e5fba4825c20c6f8f67f4045ae8ab",
    "TCS-R1-POS-013": "02e69912455fe5f6e5f9ddbcb49efc25021e7d9bd017ea1c32e19f9b2416146d",
    "TCS-R1-POS-014": "35648e2d7db3044bed1961e172a5228c12885e767975dee72a26fdac895ffbdb",
    "TCS-R1-NEG-001": "5dcde2137f56f172fd5ba8e83108e9cbd2f5fa59805613f00bbd83457869f545",
    "TCS-R1-NEG-002": "474ece87f02a6f6221e104352ddffa1d89a6a28be22411ca52b67b4e97e4c3a2",
    "TCS-R1-NEG-003": "b957106d59114c58544985137f22e8ef6fed44fef7d5380401904d2624e3f6f7",
    "TCS-R1-NEG-004": "130ef4b13027c6ca0a53aad52a174efaf674f785f885cfc1d18ec719f2873318",
    "TCS-R1-NEG-005": "264f8aa880cc64a4fd05e4bf54f65e0ddbed455830d2d9dc4fa4ede808716cb8",
    "TCS-R1-NEG-006": "9ed178ba38c49167f145866f8a2994d753569ab10dce8ba885f62a875fe512e6",
    "TCS-R1-NEG-007": "077fcf182885bd2998e3d086c5783e237b370bb10f64c17ea20d021771b732e2",
    "TCS-R1-NEG-008": "e41d57a96744f8f40b85900fd9282392fe7eefa1248a9946ef18badb9031369a",
    "TCS-R1-NEG-009": "398a9621caf006a6f21d74388e95865ed43034101acc50ad3a6dfe769d09f9a0",
    "TCS-R1-NEG-010": "c41174f295f7ce210fb382996f3216dd54e7a678dce7467b2ebd5a066601e769",
    "TCS-R1-NEG-011": "d1bf0fe69fa1dc6a3160db99d90c0b9ce0d641a904515fd3bc54f4868ed48c91",
}
REFINEMENT_SURFACE_CASE_SHA256 = {
    "TRN-R1-POS-046": "a1847aaebbdd743d8aacc74eb99bc85fdcddf047a15cc39676e82190ae04ecca",
    "TRN-R1-POS-047": "f21cd981e0410836d60a78db86491db7b7da8efdb721005f9814d0aa4979a227",
    "TRN-R1-NEG-048": "011c969dd8b300be001e44b7c26adf6b77eb64d0c2108f533de984ad8dffe35d",
    "TRN-R1-POS-049": "ae4f7f97cf9ec046e5d5dbcce1f7c170286a9165b7c0806f97de840e56b8ac23",
    "TRN-R1-POS-050": "1aff5b88898dae43a3b5c3315361907b19da56cb36e530364db493a3b55cdf47",
    "TRN-R1-NEG-051": "93c880354cc80e692a1142119c4b74a21c85011aedbda686c1b0d145f71e4f6c",
    "TRN-R1-POS-052": "3275519eda59a109d3619cfb51ffdb5359c7659ade2a5422a33d952bc8214ed7",
    "TRN-R1-NEG-053": "107433645051536eba564afa8c31818a9bed4923829cd949e828c948d81a60b7",
    "TRN-R1-POS-054": "ca6b6410c56ce952dd6844dfe28af9df31f4a4ffecc8632dd8e479a05075c0c5",
    "TRN-R1-POS-055": "1f7d04c1a280ac95f7f1c1a19a70799b43c4ecbdb1aa155b40d67547c218d1bb",
    "TRN-R1-NEG-056": "4676503c257b8d25eb3cb937fad99e25ce3e2c92fc6237681dafe13c018ff567",
    "TRN-R1-BOUND-057": "f04f8e08f7a8ce300526f0d6ab47d71644b578ad0d457f2c24e34532ed664672",
    "TRN-R1-NEG-058": "f4167e587ce908b1ce5e05b7c085e5a8f6aca74561ef03fb392c58a0e282c7ea",
}
SUCCESSOR_ACTION_IDS = EXPECTED_ACTION_IDS + [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
POST_PR16_CANONICAL_DELTA_PATHS = {
    "spec/language.md",
    "spec/frontend/frontend-model.json",
    "spec/types/type-system.md",
    "spec/mir/semantics.md",
    "decisions/language/current-decisions.json",
    "library/prelude/prelude.md",
    "examples/guide/review-corpus.md",
    "examples/manifests/by-outcome/catalog-metadata.json",
    *(f"examples/manifests/by-outcome/chunks/part-{index:04d}.json" for index in range(5, 15)),
    "tests/conformance/surface/rejected/catalog-metadata.json",
    "tests/conformance/surface/rejected/chunks/part-0001.json",
    "tests/conformance/surface/rejected/chunks/part-0002.json",
    "library/prelude/signatures/catalog-metadata.json",
    "library/prelude/signatures/chunks/part-0001.json",
    "spec/diagnostics/catalog/catalog-metadata.json",
    "spec/diagnostics/catalog/chunks/part-0011.json",
    "spec/diagnostics/relations/catalog-metadata.json",
    "spec/diagnostics/relations/chunks/part-0001.json",
    "spec/features/catalog/chunks/part-0002.json",
    "spec/features/catalog/chunks/part-0004.json",
    "spec/features/catalog/chunks/part-0018.json",
    "spec/types/predicates/chunks/part-0004.json",
}
EXPR_AUTHORITY = "governance/policies/management-policy.yaml#EXPR-001"
EXPR_DIGEST = "42250c554d2d5f9cfb29bbd3668bed40ec1390fce658ac1804f7c6de29b1ac39"
EXPR_FIELDS = {
    "clause_id": "EXPR-001",
    "statement": "Expressiveness means translating programmer intent easily, consistently, and responsibly.",
    "restriction_rule": "A restriction must provide an expression-preserving alternative or state an explicit impossibility case.",
    "visibility_rule": "Responsibility, ownership, effects, failure, cleanup, suspension, authority, provider lookup, call domain, and public API residue remain visible.",
}
EXPR_TEXT_CONSUMERS = [
    "roles/prompts/Deeplus_Shared_Work_Role_Charter_Prompt.txt",
    "roles/prompts/Design_Deeplus_Design_and_Release_Steward_Prompt.txt",
    "roles/prompts/Spec_Deeplus_Language_and_Type_System_Architect_Prompt.txt",
    "roles/prompts/Impl_Deeplus_Compiler_and_Runtime_Lead_Prompt.txt",
    "roles/prompts/Test_Deeplus_Conformance_and_Quality_Lead_Prompt.txt",
    "roles/prompts/Devel_Deeplus_Developer_Experience_and_Ecosystem_Lead_Prompt.txt",
    "governance/templates/Design_Deeplus_RFC_Template.md",
    "governance/templates/Design_Deeplus_ADR_Template.md",
]


def canonical_sha(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_pointer(value: Any, fragment: str) -> bool:
    if not fragment or fragment == "#":
        return True
    if not fragment.startswith("#/"):
        return False
    current = value
    for raw in fragment[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            return False
    return True


def walk_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                refs.append(child)
            refs.extend(walk_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(walk_refs(child))
    return refs


def scalar_occurrences(value: Any, needle: str) -> int:
    if isinstance(value, dict):
        return sum(scalar_occurrences(child, needle) for child in value.values())
    if isinstance(value, list):
        return sum(scalar_occurrences(child, needle) for child in value)
    return int(value == needle)


def longest_exact_indent_prefix(lines: list[str]) -> str:
    prefixes: list[str] = []
    for line in lines:
        if not isinstance(line, str):
            return "\0INVALID"
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        if line[len(prefix):]:
            prefixes.append(prefix)
    if not prefixes:
        return ""
    common = prefixes[0]
    for prefix in prefixes[1:]:
        limit = min(len(common), len(prefix))
        index = 0
        while index < limit and common[index] == prefix[index]:
            index += 1
        common = common[:index]
    return common


def fixed_operator_schema_role_rows(schema_def: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for clause in schema_def.get("allOf", []):
        if not isinstance(clause, dict):
            continue
        operator_id = (
            clause.get("if", {})
            .get("properties", {})
            .get("operator_id", {})
            .get("const")
        )
        properties = clause.get("then", {}).get("properties")
        if isinstance(operator_id, str) and isinstance(properties, dict):
            rows[operator_id] = properties
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--write-receipt", action="store_true", help="write migration receipt; rebuild source-tree manifest afterward")
    parser.add_argument("--no-receipt", action="store_true", help="deprecated compatibility no-op; validation is read-only by default")
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.candidate and (root / "release/candidate-state.json").is_file() and not (root / "current/current-pointer.json").exists():
        args.candidate = True
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(condition: bool, code: str, detail: str) -> None:
        checks.append({"code": code, "pass": bool(condition), "detail": detail})
        if not condition:
            errors.append(f"{code}: {detail}")

    try:
        revision = tomllib.loads(
            (root / "current/language-version.toml").read_text(encoding="utf-8")
        )["spec_revision"]
    except Exception as exc:  # noqa: BLE001
        revision = ""
        check(False, "REVISION_PARITY", str(exc))
    check(
        revision
        in {LEGACY_REVISION, POST_PR16_REVISION, LANGUAGE_COHERENCE_REVISION},
        "REVISION_PARITY",
        revision,
    )

    language_coherence_contract: dict[str, Any] = {}
    if revision == LANGUAGE_COHERENCE_REVISION:
        try:
            language_coherence_contract = json.loads(
                (root / LANGUAGE_COHERENCE_CONTRACT_REL).read_text(
                    encoding="utf-8"
                )
            )
            fixed_counts = language_coherence_contract.get("canonical_counts", {})
            check(
                language_coherence_contract.get("schema")
                == "deeplus.language-coherence-current-integrity-contract/r1"
                and language_coherence_contract.get("revision") == revision
                and fixed_counts.get("features") == 719
                and fixed_counts.get("predicates") == 268
                and fixed_counts.get("predicate_fixtures") == 819
                and fixed_counts.get("no_go") == 155
                and fixed_counts.get("hard_keywords") == 29
                and fixed_counts.get("contextual_words") == 105,
                "LANGUAGE_COHERENCE_CONTRACT",
                str(fixed_counts),
            )
        except Exception as exc:  # noqa: BLE001
            check(False, "LANGUAGE_COHERENCE_CONTRACT", str(exc))

    required = [
        "README.md", "GOVERNANCE.md", "CONTRIBUTING.md", "Cargo.toml",
        "current/authority-map.yaml", "current/implementation-status.yaml",
        "current/language-version.toml", "current/product-lanes.json",
        "spec/language.md", "spec/grammar/deeplus.ebnf",
        "spec/frontend/frontend-model.json", "spec/types/type-system.md",
        "spec/mir/semantics.md", "library/prelude/prelude.md",
        "examples/guide/review-corpus.md", "migration/import-manifest.json",
        "migration/catalog-reassembly.json", "migration/path-aliases.json",
        "migration/m1.1-repair-manifest.json", "release/source-tree-manifest.json",
        "tools/generators/generate_example_projections.py",
        "tools/generators/example-projections.contract.json",
        "tools/validators/run_example_projection_generator_tests.py",
        "docs/grammar-reference/README.md",
        "docs/grammar-reference/coverage-manifest.json",
        "spec/contracts/grammar-reference-r1.json",
        "schemas/language/grammar-reference-coverage.schema.json",
        "tools/generators/generate_grammar_reference.py",
        "tools/validators/run_grammar_reference_generator_tests.py",
        "docs/tutorial/README.md",
        "docs/tutorial/SUMMARY.md",
        "docs/tutorial/coverage-manifest.json",
        "spec/contracts/tutorial-r1.json",
        "spec/contracts/trait-conformance-surface.json",
        "tests/fixtures/current/trait-conformance-surface-r1.json",
        "schemas/language/tutorial-coverage.schema.json",
        "tools/generators/generate_tutorial.py",
        "tools/validators/run_tutorial_generator_tests.py",
        "tools/generators/generate_current_integrity.py",
        "tools/generators/current-integrity.contract.json",
        "tools/validators/run_current_integrity_generator_tests.py",
        "migration/current-document-consistency-repair-r2.3-manifest.json",
        "governance/policies/management-policy.yaml",
        "release/evidence/current-publication-m1.3-source-snapshot-receipt.json",
        "release/evidence/current-publication-m1.3-predecessor-receipt.json",
        "release/evidence/current-publication-m1.3-git-binding-receipt.json",
        "release/evidence/current-publication-m1.3-role-review-index.json",
    ]
    if revision == POST_PR16_REVISION:
        required.extend([
            "tools/generators/generate_post_pr16_current_integrity.py",
            "tools/generators/post-pr16-current-integrity.contract.json",
            "tools/validators/run_post_pr16_current_integrity_tests.py",
        ])
    elif revision == LANGUAGE_COHERENCE_REVISION:
        required.extend([
            "tools/generators/generate_language_coherence_current_integrity.py",
            LANGUAGE_COHERENCE_CONTRACT_REL,
        ])
    required.append("release/candidate-state.json" if args.candidate else "current/current-pointer.json")
    for rel in required:
        check((root / rel).is_file(), "REQUIRED_PATH", rel)
    check(not (root / ("current/current-pointer.json" if args.candidate else "release/candidate-state.json")).exists(),
          "RELEASE_STATE_EXCLUSIVE", "candidate and published current states are mutually exclusive")

    generator = root / "tools/generators/generate_example_projections.py"
    if generator.is_file():
        process = subprocess.run(
            [sys.executable, str(generator), "--root", str(root), "--check"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        detail = process.stdout.strip() if process.returncode == 0 else process.stderr.strip()
        check(
            process.returncode == 0,
            "EXAMPLE_PROJECTION_GENERATOR_CHECK",
            detail[-2000:],
        )

    grammar_reference_generator = (
        root / "tools/generators/generate_grammar_reference.py"
    )
    if grammar_reference_generator.is_file():
        process = subprocess.run(
            [
                sys.executable,
                str(grammar_reference_generator),
                "--root",
                str(root),
                "--check",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        detail = process.stdout.strip() if process.returncode == 0 else (
            process.stderr.strip() or process.stdout.strip()
        )
        check(
            process.returncode == 0,
            "GRAMMAR_REFERENCE_GENERATOR_CHECK",
            detail[-4000:],
        )

    tutorial_generator = root / "tools/generators/generate_tutorial.py"
    if tutorial_generator.is_file():
        process = subprocess.run(
            [
                sys.executable,
                str(tutorial_generator),
                "--root",
                str(root),
                "--check",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        detail = process.stdout.strip() if process.returncode == 0 else (
            process.stderr.strip() or process.stdout.strip()
        )
        check(
            process.returncode == 0,
            "TUTORIAL_GENERATOR_CHECK",
            detail[-4000:],
        )

    if revision == LANGUAGE_COHERENCE_REVISION:
        current_integrity_generator_rel = (
            "tools/generators/generate_language_coherence_current_integrity.py"
        )
    elif revision == POST_PR16_REVISION:
        current_integrity_generator_rel = (
            "tools/generators/generate_post_pr16_current_integrity.py"
        )
    else:
        current_integrity_generator_rel = (
            "tools/generators/generate_current_integrity.py"
        )
    current_integrity_generator = root / current_integrity_generator_rel
    if current_integrity_generator.is_file():
        process = subprocess.run(
            [
                sys.executable,
                str(current_integrity_generator),
                "--root",
                str(root),
                "--check",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        detail = process.stdout.strip() if process.returncode == 0 else (
            process.stderr.strip() or process.stdout.strip()
        )
        check(
            process.returncode == 0,
            "CURRENT_INTEGRITY_GENERATOR_CHECK",
            detail[-4000:],
        )
        if revision == LANGUAGE_COHERENCE_REVISION:
            mutation_process = subprocess.run(
                [
                    sys.executable,
                    str(current_integrity_generator),
                    "--root",
                    str(root),
                    "--self-test",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            mutation_detail = (
                mutation_process.stdout.strip()
                if mutation_process.returncode == 0
                else mutation_process.stderr.strip()
                or mutation_process.stdout.strip()
            )
            check(
                mutation_process.returncode == 0,
                "CURRENT_INTEGRITY_GENERATOR_MUTATION_CHECK",
                mutation_detail[-4000:],
            )

    parsed: dict[Path, Any] = {}
    json_files = sorted(
        path
        for path in root.rglob("*.json")
        if not any(
            part in EXCLUDED_TREE_PARTS
            for part in path.relative_to(root).parts
        )
    )
    for path in json_files:
        try:
            parsed[path] = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"JSON_PARSE: {path.relative_to(root)}: {exc}")
    check(len(parsed) == len(json_files), "JSON_CLOSURE", f"{len(parsed)}/{len(json_files)}")
    try:
        tomllib.loads((root / "current/language-version.toml").read_text(encoding="utf-8"))
        tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
        check(True, "TOML_PARSE", "language version and workspace")
    except Exception as exc:  # noqa: BLE001
        check(False, "TOML_PARSE", str(exc))

    archives = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".zip", ".tar", ".gz", ".zst"}
        and not any(
            part in EXCLUDED_TREE_PARTS
            for part in path.relative_to(root).parts
        )
    ]
    check(not archives, "NO_NESTED_ARCHIVES", str(archives))

    integrity_contract = parsed.get(
        root / "tools/generators/current-integrity.contract.json", {}
    )
    current_delta = parsed.get(
        root / "migration/current-document-consistency-repair-r2.3-manifest.json", {}
    )
    contract_transitions = integrity_contract.get("historical_transitions", [])
    delta_transitions = current_delta.get("transitions", [])
    transition_keys = {
        "path",
        "historical_receipt",
        "classification",
        "frozen_sha256",
        "approved_current_sha256",
        "decision_ids",
    }
    transition_shape = (
        isinstance(contract_transitions, list)
        and isinstance(delta_transitions, list)
        and len(contract_transitions) == len(delta_transitions) == 26
        and len({row.get("path") for row in contract_transitions}) == 26
        and all(set(row) == transition_keys for row in contract_transitions)
        and delta_transitions == contract_transitions
        and current_delta.get("transition_count") == 26
        and "migration/current-document-consistency-repair-r2.3-manifest.json"
        not in {row.get("path") for row in delta_transitions}
        and "release/source-tree-manifest.json"
        not in {row.get("path") for row in delta_transitions}
    )
    check(
        transition_shape,
        "CURRENT_DELTA_TRANSITION_EXACT",
        f"contract={len(contract_transitions)} delta={len(delta_transitions)}",
    )
    transitions_by_path = {
        row["path"]: row
        for row in contract_transitions
        if isinstance(row, dict) and set(row) == transition_keys
    }

    def exact_transition(
        rel: str,
        receipt: str,
        frozen_sha256: str,
        approved_current_sha256: str,
    ) -> bool:
        row = transitions_by_path.get(rel)
        return bool(
            transition_shape
            and row
            and row["historical_receipt"] == receipt
            and row["frozen_sha256"] == frozen_sha256
            and row["approved_current_sha256"] == approved_current_sha256
            and bool(row["classification"])
            and bool(row["decision_ids"])
            and (root / rel).is_file()
            and file_sha(root / rel) == approved_current_sha256
        )

    language_identity_exemptions = {
        row.get("path"): row.get("sha256")
        for row in language_coherence_contract.get(
            "migration_identity_exemptions", []
        )
        if isinstance(row, dict)
        and set(row) == {"path", "sha256"}
        and isinstance(row.get("path"), str)
        and isinstance(row.get("sha256"), str)
    }

    def revision_identity_exempt(relative: str, current_sha256: str) -> bool:
        if revision == POST_PR16_REVISION:
            return relative in POST_PR16_CANONICAL_DELTA_PATHS
        if revision == LANGUAGE_COHERENCE_REVISION:
            return language_identity_exemptions.get(relative) == current_sha256
        return False

    repair = parsed.get(root / "migration/m1.1-repair-manifest.json", {})
    changed_paths = {repair.get("human_corpus", {}).get("path")}
    transformations = repair.get("reference_normalization", {}).get("transformations", [])
    changed_paths.update(row.get("path") for row in transformations)
    changed_paths.discard(None)
    for row in transformations:
        path = root / row["path"]
        current_hash = file_sha(path) if path.is_file() else ""
        check(
            path.is_file()
            and (
                current_hash == row["output_sha256"]
                or revision_identity_exempt(row["path"], current_hash)
                or exact_transition(
                    row["path"],
                    "migration/m1.1-repair-manifest.json",
                    row["output_sha256"],
                    current_hash,
                )
            ),
            "REPAIR_OUTPUT_IDENTITY",
            row["path"],
        )

    imported = parsed.get(root / "migration/import-manifest.json", {})
    legacy = imported.get("legacy_files", [])
    check(imported.get("legacy_file_count") == len(legacy) == 86, "IMPORT_FILE_COUNT", str(len(legacy)))
    check(imported.get("semantic_delta") == "NONE; identity/path/configuration migration only", "IMPORT_SEMANTIC_DELTA", str(imported.get("semantic_delta")))
    for entry in legacy:
        for rel in entry.get("current_paths", []):
            target = root / rel
            check(target.exists(), "MIGRATED_PATH_EXISTS", f"{entry['legacy_path']} -> {rel}")
            if target.is_file() and entry["disposition"] != "MIGRATED_SOURCE_SHARDS" and rel not in changed_paths:
                current_hash = file_sha(target)
                check(
                    current_hash == entry["sha256"]
                    or revision_identity_exempt(rel, current_hash)
                    or exact_transition(
                        rel,
                        "migration/import-manifest.json",
                        entry["sha256"],
                        current_hash,
                    ),
                    "IMPORT_BYTE_IDENTITY",
                    rel,
                )

    aliases = parsed.get(root / "migration/path-aliases.json", {}).get("aliases", [])
    by_legacy = {row["legacy_path"]: row for row in legacy}
    by_alias = {row["legacy_name"]: row for row in aliases}
    check(len(by_legacy) == len(legacy) and len(by_alias) == len(aliases), "ALIAS_UNIQUENESS", f"legacy={len(by_legacy)} alias={len(by_alias)}")
    check(set(by_legacy) == set(by_alias), "ALIAS_BIJECTION", f"legacy={len(by_legacy)} alias={len(by_alias)}")
    for name in set(by_legacy) & set(by_alias):
        entry, alias = by_legacy[name], by_alias[name]
        check(entry["sha256"] == alias.get("legacy_sha256") and entry.get("current_paths", []) == alias.get("current_paths", []), "ALIAS_IDENTITY", name)
    current_projection_files = [
        path for top in ("spec", "schemas", "tests", "examples", "library", "docs")
        for path in (root / top).rglob("*") if path.is_file()
    ]
    current_projection_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in current_projection_files)
    for alias in aliases:
        if alias.get("resolution") == "stable_path":
            check(alias["legacy_name"] not in current_projection_text, "CURRENT_LEGACY_BASENAME_CLOSURE", alias["legacy_name"])

    reassembly = parsed.get(root / "migration/catalog-reassembly.json", {})
    reconstructed: dict[str, Any] = {}
    all_shards: list[Path] = []
    for contract in reassembly.get("contracts", []):
        metadata = parsed.get(root / contract["metadata_path"])
        rows: list[Any] = []
        for rel in contract.get("ordered_shard_paths", []):
            path = root / rel
            all_shards.append(path)
            check(path.is_file(), "SHARD_PATH_CLOSURE", rel)
            check(path.is_file() and path.stat().st_size <= 61440, "SOURCE_SHARD_SIZE", rel)
            value = parsed.get(path)
            if isinstance(value, list):
                rows.extend(value)
        check(len(rows) == contract.get("row_count"), "SHARD_ROW_COUNT", contract.get("legacy_file", "?"))
        if not isinstance(metadata, dict):
            check(False, "CATALOG_METADATA", contract["metadata_path"])
            continue
        doc = dict(metadata)
        doc[contract["array_key"]] = rows
        check(canonical_sha(doc) == contract.get("canonical_object_sha256"), "CATALOG_OBJECT_IDENTITY", contract["legacy_file"])
        ids = [row.get(contract["id_key"]) for row in rows if isinstance(row, dict) and row.get(contract["id_key"])]
        check(len(ids) == len(set(ids)), "CATALOG_ID_UNIQUENESS", contract["legacy_file"])
        reconstructed[contract["legacy_file"]] = doc
    chunk_files = sorted(
        path
        for path in root.glob("**/chunks/part-*.json")
        if not any(
            part in EXCLUDED_TREE_PARTS
            for part in path.relative_to(root).parts
        )
    )
    check(set(chunk_files) == set(all_shards), "SHARD_CONTRACT_COVERAGE", f"actual={len(chunk_files)} declared={len(all_shards)}")
    check(len(reconstructed) == 12, "CATALOG_COUNT", str(len(reconstructed)))

    def rows(name: str, key: str) -> list[dict[str, Any]]:
        return reconstructed.get(name, {}).get(key, [])
    active = rows("deeplus-0.1.2-baseline-r51f3-examples-active-profile-manifest.json", "examples")
    positive = rows("deeplus-0.1.2-baseline-r51f3-surface-smoke-corpus-positive.json", "cases")
    rejected = rows("deeplus-0.1.2-baseline-r51f3-surface-smoke-corpus-rejected.json", "cases")
    gated = rows("deeplus-0.1.2-baseline-r51f3-surface-smoke-corpus-gated.json", "cases")
    counts = Counter(row.get("expected_outcome") for row in active)
    check(
        sum(counts.values()) == len(active)
        and set(counts) <= {"accept", "accept_with_gate", "reject"}
        and counts["accept"] == len(positive)
        and counts["accept_with_gate"] == len(gated)
        and counts["reject"] == len(rejected),
        "EXAMPLE_OUTCOME_COUNTS",
        str(dict(counts)),
    )
    active_ids = {row["example_id"] for row in active}
    partitions = [positive, rejected, gated]
    partition_ids = [row["example_id"] for group in partitions for row in group]
    check(len(partition_ids) == len(set(partition_ids)) and set(partition_ids) == active_ids, "EXAMPLE_PARTITION_EXACT", str([len(group) for group in partitions]))
    active_by_id = {row["example_id"]: row for row in active}
    for row in gated:
        owner = active_by_id.get(row["example_id"], {})
        check(owner.get("expected_outcome") == "accept_with_gate" and owner.get("source_activation") == "explicit_feature_gate" and bool(owner.get("feature_ids")), "GATED_EXAMPLE_LAW", row["example_id"])

    feature_rows = rows("deeplus-0.1.2-baseline-r51f3-feature-registry.json", "features")
    diagnostic_rows = rows("deeplus-0.1.2-baseline-r51f3-diagnostic-registry.json", "diagnostics")
    predicate_rows = rows("deeplus-0.1.2-baseline-r51f3-checker-predicate-catalog.json", "predicates")
    actual = {
        "features": len(feature_rows),
        "diagnostics": len(diagnostic_rows),
        "predicates": len(predicate_rows),
        "predicate_fixtures": len(rows("deeplus-0.1.2-baseline-r51f3-checker-predicate-fixtures.json", "fixtures")),
        "examples": len(active),
        "no_go": len(rows("deeplus-0.1.2-baseline-r51f3-current-no-go-registry.json", "entries")),
    }
    vocabulary = parsed.get(root / "spec/grammar/keyword-vocabulary.json", {})
    actual["hard_keywords"] = len(vocabulary.get("hard_keywords", []))
    actual["contextual_words"] = len(vocabulary.get("contextual_words", []))
    expected_counts = (
        {
            key: value
            for key, value in language_coherence_contract.get(
                "canonical_counts", {}
            ).items()
            if key != "prelude_entries"
        }
        if revision == LANGUAGE_COHERENCE_REVISION
        else EXPECTED
    )
    for key, expected in expected_counts.items():
        check(actual[key] == expected, "CANONICAL_COUNT", f"{key}={actual[key]} expected={expected}")

    feature_by_id = {row.get("feature_id"): row for row in feature_rows}
    diagnostic_by_id = {row.get("diagnostic_id"): row for row in diagnostic_rows}
    predicate_by_id = {row.get("predicate_id"): row for row in predicate_rows}
    frontend_surface = parsed.get(
        root / "spec/frontend/frontend-model.json", {}
    )
    keyword_model = frontend_surface.get("keyword_model", {})
    identifier_model = frontend_surface.get("identifier_model", {})
    ordinary_identifier_seeds = {"array", "case"}
    keyword_projection = {
        "hard_keywords": keyword_model.get("hard_reserved", []),
        "contextual_words": keyword_model.get("contextual", []),
        "sigil_role_subset": keyword_model.get("sigil_role_subset", []),
    }
    check(
        "ordinary_identifiers" not in vocabulary
        and "ordinary_identifiers" not in keyword_model
        and ordinary_identifier_seeds.isdisjoint(
            set(vocabulary.get("hard_keywords", []))
            | set(vocabulary.get("contextual_words", []))
            | set(vocabulary.get("sigil_role_subset", []))
        )
        and ordinary_identifier_seeds.isdisjoint(
            set(keyword_model.get("hard_reserved", []))
            | set(keyword_model.get("contextual", []))
            | set(keyword_model.get("sigil_role_subset", []))
        )
        and set(
            identifier_model.get("ordinary_identifier_regression_seeds", [])
        )
        == ordinary_identifier_seeds
        and identifier_model.get("regression_seed_token_kind") == "IDENTIFIER"
        and identifier_model.get("regression_seed_special_role_count") == 0
        and vocabulary.get("hard_keywords") == keyword_projection["hard_keywords"]
        and vocabulary.get("contextual_words")
        == keyword_projection["contextual_words"]
        and vocabulary.get("sigil_role_subset")
        == keyword_projection["sigil_role_subset"]
        and vocabulary.get("projection_sha256")
        == canonical_sha(keyword_projection),
        "ORDINARY_IDENTIFIER_KEYWORD_SEPARATION",
        f"vocabulary={sorted(ordinary_identifier_seeds & (set(vocabulary.get('hard_keywords', [])) | set(vocabulary.get('contextual_words', [])) | set(vocabulary.get('sigil_role_subset', []))))}",
    )
    predicate_relation_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-diagnostic-relation-registry.json",
        "relations",
    )
    for predicate_id, predicate in predicate_by_id.items():
        if not predicate.get("emission_eligible"):
            continue
        primary_relations = [
            row.get("diagnostic_id")
            for row in predicate_relation_rows
            if row.get("predicate_id") == predicate_id
            and row.get("relation") == "primary"
        ]
        secondary_relations = {
            row.get("diagnostic_id")
            for row in predicate_relation_rows
            if row.get("predicate_id") == predicate_id
            and row.get("relation") == "secondary"
        }
        declared_secondaries = set(predicate.get("secondary_diagnostics", []))
        check(
            primary_relations == [predicate.get("active_primary_diagnostic")],
            "DIAGNOSTIC_RELATION_PRIMARY_BINDING",
            f"{predicate_id}: declared={predicate.get('active_primary_diagnostic')} relations={primary_relations}",
        )
        check(
            declared_secondaries == secondary_relations,
            "DIAGNOSTIC_RELATION_SECONDARY_BINDING",
            f"{predicate_id}: missing={sorted(declared_secondaries - secondary_relations)} extra={sorted(secondary_relations - declared_secondaries)}",
        )
    empty_char = active_by_id.get("EX-R49B-CHAR-005", {})
    empty_char_surface = next(
        (row for row in rejected if row.get("example_id") == "EX-R49B-CHAR-005"),
        {},
    )
    empty_char_features = {
        "char_unicode_scalar_value_model",
        "unicode_char_literal_single_quote_msp",
    }
    empty_char_sha = "57f7a0556e0351b914052e202e272fbf8c801a26dbc3e34179cf1b886c817399"
    check(
        empty_char.get("expected_outcome") == "reject"
        and empty_char.get("primary_diagnostic") == "CHAR_LITERAL_EMPTY"
        and set(empty_char.get("feature_ids", [])) == empty_char_features
        and empty_char.get("code_sha256") == empty_char_sha
        and empty_char.get("parser_status") == "not_run"
        and empty_char.get("checker_status") == "not_run"
        and empty_char_surface.get("primary_diagnostic") == "CHAR_LITERAL_EMPTY"
        and set(empty_char_surface.get("feature_ids", [])) == empty_char_features
        and empty_char_surface.get("code_sha256") == empty_char_sha,
        "CMA_EMPTY_CHAR_EXAMPLE",
        str(empty_char.get("example_id")),
    )
    required_set = set(REQUIRED_FEATURE_IDS)
    check(
        len(REQUIRED_FEATURE_IDS) == 20
        and len(required_set) == 20
        and required_set <= set(feature_by_id),
        "REQUIRED_FEATURE_SET",
        f"count={len(required_set)} missing={sorted(required_set - set(feature_by_id))}",
    )
    for feature_id in REQUIRED_FEATURE_IDS:
        feature = feature_by_id.get(feature_id, {})
        trace = feature.get("normative_trace_refs", {})
        forward_diagnostics = set(trace.get("diagnostics", []))
        reverse_diagnostics = {
            row.get("diagnostic_id")
            for row in diagnostic_rows
            if row.get("diagnostic_status") == "active"
            and feature_id in row.get("feature_refs", [])
        }
        check(
            forward_diagnostics == reverse_diagnostics,
            "DIRECT_DIAGNOSTIC_TRACE_EQUALITY",
            f"{feature_id}: forward={sorted(forward_diagnostics)} reverse={sorted(reverse_diagnostics)}",
        )
        forward_predicates = {
            predicate_id
            for predicate_id in trace.get("predicates", [])
            if predicate_by_id.get(predicate_id, {}).get("predicate_maturity") == "active"
        }
        reverse_predicates = {
            row.get("predicate_id")
            for row in predicate_rows
            if row.get("predicate_maturity") == "active"
            and feature_id in row.get("feature_refs", [])
        }
        design_seed_predicates = {
            row.get("predicate_id")
            for row in predicate_rows
            if row.get("predicate_maturity") == "design_seed"
            and feature_id in row.get("feature_refs", [])
        }
        check(
            forward_predicates == reverse_predicates,
            "DIRECT_PREDICATE_TRACE_EQUALITY",
            f"{feature_id}: forward={sorted(forward_predicates)} reverse={sorted(reverse_predicates)} design_seed={sorted(design_seed_predicates)}",
        )
        forward_examples = set(trace.get("examples", []))
        reverse_examples = {
            row.get("example_id")
            for row in active
            if feature_id in row.get("source_feature_ids", row.get("feature_ids", []))
        }
        check(
            forward_examples == reverse_examples,
            "DIRECT_EXAMPLE_TRACE_EQUALITY",
            f"{feature_id}: forward={sorted(forward_examples)} reverse={sorted(reverse_examples)}",
        )
        check(
            feature.get("status_enum") == "STABLE_DESIGN"
            and feature.get("source_activation") == "none",
            "REQUIRED_FEATURE_STATUS_ACTIVATION",
            feature_id,
        )

    rightward_id = "rightward_flow_dollar_local_binding_msp"
    rightward_feature = feature_by_id.get(rightward_id, {})
    rightward_owned = sum(
        rightward_id in row.get("source_feature_ids", row.get("feature_ids", []))
        for row in active
        if row.get("example_id") == "EX-R51d-008"
    )
    check(
        "EX-R51d-008" not in rightward_feature.get("normative_trace_refs", {}).get("examples", [])
        and rightward_owned == 0,
        "RIGHTWARD_UNRELATED_EXAMPLE_ZERO",
        str(rightward_owned),
    )
    numeric_diagnostics = feature_by_id.get(
        "numeric_array_postfix_transpose_caret_msp", {}
    ).get("normative_trace_refs", {}).get("diagnostics", [])
    check(
        numeric_diagnostics.count("CARET_ATTACHMENT_AMBIGUOUS") == 0,
        "NUMERIC_TRANSPOSE_CARET_DIAGNOSTIC_ZERO",
        str(numeric_diagnostics),
    )
    set_feature = feature_by_id.get("set_prefixed_literal", {})
    check(
        set_feature.get("normative_trace_refs", {}).get("examples", []) == ["EX-R51f-008"],
        "SUPPLEMENTAL_SET_PREFIX_EDGE",
        str(set_feature.get("normative_trace_refs", {}).get("examples", [])),
    )
    unknown_prefixed = diagnostic_by_id.get("UNKNOWN_PREFIXED_LITERAL", {})
    check(
        unknown_prefixed.get("feature_refs") == [
            "set_prefixed_literal",
            "closed_source_surface_boundary_law",
        ]
        and unknown_prefixed.get("message") == "Unknown #prefix literal; current prefixed literal families are #map, #set, #mut, #raw, and #bytes."
        and unknown_prefixed.get("stage") == "checker"
        and unknown_prefixed.get("severity") == "error"
        and unknown_prefixed.get("diagnostic_status") == "active"
        and unknown_prefixed.get("product_support") == "NOT_RUN",
        "SUPPLEMENTAL_UNKNOWN_PREFIXED_LITERAL_ZERO_DELTA",
        str(unknown_prefixed),
    )
    raw_feature = feature_by_id.get("raw_string_prefixed_literal", {})
    raw_delimiter_diagnostic = diagnostic_by_id.get(
        "RAW_STRING_DELIMITER_INVALID", {}
    )
    raw_scanner = frontend_surface.get("scanner", {})
    raw_phase = raw_scanner.get("raw_string_stable", {})
    raw_terminal = raw_scanner.get("external_terminals", {}).get(
        "ScannerRawStringLiteral", {}
    )
    raw_hash_policy = next(
        (
            row
            for row in frontend_surface.get("boundary_policies", [])
            if row.get("id") == "HASH_LITERAL_SIGILS"
        ),
        {},
    )
    raw_no_go = next(
        (
            row
            for row in rows(
                "deeplus-0.1.2-baseline-r51f3-current-no-go-registry.json",
                "entries",
            )
            if row.get("rejection_id") == "NG-RAW-ALT-DELIMITER"
        ),
        {},
    )
    check(
        raw_feature.get("status_enum") == "STABLE_DESIGN"
        and raw_feature.get("language_status") == "Stable design"
        and raw_phase.get("surface") == '#raw"..."'
        and raw_phase.get("design_maturity") == "STABLE"
        and raw_terminal.get("surface") == '#raw"..."'
        and "#raw\"" in raw_hash_policy.get("owners", [])
        and raw_delimiter_diagnostic.get("fixit_policy") == 'use #raw"..."'
        and raw_delimiter_diagnostic.get("message")
        == 'Stable raw String uses exactly the attached `#raw"..."` delimiter family.'
        and set(raw_no_go.get("negative_fixture_ids", []))
        == {"EX-R51d-002"}
        and raw_no_go.get("replacement_or_no_fix") == 'use #raw"..."',
        "STABLE_RAW_STRING_SURFACE_CLOSURE",
        f"feature={raw_feature.get('status_enum')} surface={raw_phase.get('surface')} no_go={raw_no_go.get('negative_fixture_ids')}",
    )
    package_module = frontend_surface.get("package_module_model", {})
    package_model = package_module.get("package", {})
    module_model = package_module.get("module", {})
    source_mapping = package_module.get("source_mapping", {})
    package_module_grammar = (
        root / "spec/grammar/deeplus.ebnf"
    ).read_text(encoding="utf-8")
    check(
        package_model.get("identity_owner")
        == "build manifest and resolved dependency graph"
        and package_model.get("source_declaration") is None
        and package_model.get("may_contain_multiple_modules") is True
        and module_model.get("identity") == "ModuleId = (PackageId, ModulePath)"
        and module_model.get("path_shape")
        == "one-or-more Identifier segments joined by ::"
        and source_mapping.get("filesystem_path_equals_module_path") is False
        and source_mapping.get(
            "explicit_module_decl_must_equal_mapped_module_path"
        )
        is True
        and source_mapping.get("omitted_module_decl_uses_mapped_module_path")
        is True
        and 'QualifiedPath ::= Identifier ("::" Identifier)* ;'
        in package_module_grammar,
        "PACKAGE_MODULE_IDENTITY_SEPARATION",
        f"package={package_model.get('role')} module={module_model.get('role')}",
    )

    coverage_rows = {
        row.get("feature_id"): row.get("evidence_coverage")
        for row in feature_rows
        if row.get("evidence_coverage") is not None
    }
    expected_coverage = {
        "optional_chaining_not_current_law": ("N/A_REJECTION_ONLY_LAW", "accept"),
        "at_control_expression_family": ("N/A_DELEGATED_UMBRELLA", "reject"),
        "ternary_short_expression_stable_profile": ("N/A_WARNING_PROFILE", "reject"),
    }
    check(
        set(coverage_rows) == set(expected_coverage),
        "FEATURE_EVIDENCE_COVERAGE_SET",
        str(sorted(coverage_rows)),
    )
    for feature_id, (kind, missing_outcome) in expected_coverage.items():
        entries = coverage_rows.get(feature_id, [])
        entry = entries[0] if len(entries) == 1 and isinstance(entries[0], dict) else {}
        common_keys = {"feature_id", "coverage_kind", "missing_outcome", "reason", "owner"}
        evidence = entry.get("substitute_evidence", [])
        delegated = kind == "N/A_DELEGATED_UMBRELLA"
        check(
            entry.get("feature_id") == feature_id
            and entry.get("coverage_kind") == kind
            and entry.get("missing_outcome") == missing_outcome
            and all(entry.get(key) for key in common_keys)
            and bool(evidence)
            and all(example_id in active_by_id for example_id in evidence)
            and (
                bool(entry.get("delegated_feature_id"))
                and entry.get("delegated_feature_id") in feature_by_id
                and entry.get("delegated_rule") in diagnostic_by_id
                if delegated
                else entry.get("substitute_boundary_diagnostic") in diagnostic_by_id
            ),
            "FEATURE_EVIDENCE_COVERAGE_SCHEMA",
            f"{feature_id}: {entry}",
        )
    for feature_id in REQUIRED_FEATURE_IDS:
        direct_outcomes = {
            "accept" if row.get("expected_outcome") in {"accept", "accept_with_gate"} else "reject"
            for row in active
            if feature_id in row.get("source_feature_ids", row.get("feature_ids", []))
        }
        missing = {"accept", "reject"} - direct_outcomes
        coverage = coverage_rows.get(feature_id, [])
        declared_missing = {entry.get("missing_outcome") for entry in coverage}
        check(
            not missing or missing == declared_missing,
            "FEATURE_EVIDENCE_OUTCOME_CLOSURE",
            f"{feature_id}: direct={sorted(direct_outcomes)} missing={sorted(missing)} declared={sorted(str(item) for item in declared_missing)}",
        )

    bytes_feature = feature_by_id.get("bytes_literal_hash_bytes_msp", {})
    check(
        bytes_feature.get("notes") == '#bytes"..." raw byte sequence literal; no implicit String/Bytes conversion.'
        and '.." raw byte sequence literal' not in json.dumps(feature_rows, ensure_ascii=False),
        "BYTES_NOTE_CURRENT_SPELLING",
        str(bytes_feature.get("notes")),
    )
    match_guard = diagnostic_by_id.get("MATCH_ARM_SINGLE_GUARD_ONLY", {})
    match_fixture = active_by_id.get("EX-R51b-GRAM-NG-009", {})
    check(
        match_guard.get("message") == "A match arm admits at most one `if` or attached `!if` guard."
        and match_guard.get("severity") == "error"
        and match_guard.get("stage") == "parser"
        and match_guard.get("diagnostic_status") == "active"
        and match_guard.get("feature_refs") == ["match_arm_guard_msp"]
        and match_guard.get("fixit_hint") == MATCH_GUARD_FIXIT
        and match_guard.get("fixit_policy") == MATCH_GUARD_FIXIT
        and "annotation" not in (match_guard.get("fixit_hint", "") + match_guard.get("fixit_policy", "")).lower()
        and match_fixture.get("primary_diagnostic") == "MATCH_ARM_SINGLE_GUARD_ONLY"
        and "match_arm_guard_msp" in match_fixture.get("source_feature_ids", match_fixture.get("feature_ids", [])),
        "MATCH_GUARD_FIXIT",
        str(match_guard),
    )

    mir_text = (root / "spec/mir/semantics.md").read_text(encoding="utf-8")
    mir_section = mir_text.split(
        "## 14. Normative document-consistency product-handoff dispositions", 1
    )
    mir_rows = {}
    if len(mir_section) == 2:
        for feature_id, disposition in re.findall(
            r"^\| `([^`]+)` \| `([^`]+(?:\([^`]+\))?)` \|", mir_section[1], re.MULTILINE
        ):
            mir_rows[feature_id] = disposition
    check(
        mir_rows == MIR_DISPOSITIONS,
        "MIR_REQUIRED_DISPOSITION_CLOSURE",
        f"rows={len(mir_rows)} missing={sorted(required_set - set(mir_rows))} extra={sorted(set(mir_rows) - required_set)}",
    )
    deferred_required = {
        feature_id for feature_id, disposition in MIR_DISPOSITIONS.items()
        if disposition == "DEFERRED_PRODUCT_HANDOFF"
    }
    check(
        deferred_required == {"string_interpolation_format_spec_core"}
        and all(
            f"`{feature_id}`" in mir_section[-1]
            for feature_id in SUPPLEMENTAL_MIR_FEATURE_IDS
        )
        and mir_section[-1].count("are `LAW_PRESENT`") == 1
        and "Exactly one required row remains `DEFERRED_PRODUCT_HANDOFF`"
        in mir_section[-1]
        and "All product lanes remain `NOT_RUN`" in mir_section[-1]
        and "not a product execution receipt" in mir_section[-1],
        "MIR_PRODUCT_HANDOFF_BOUNDARY",
        f"required={len(deferred_required)} supplemental={SUPPLEMENTAL_MIR_FEATURE_IDS}",
    )

    successor_semantic_files = {
        row.get("path"): row.get("sha256")
        for row in language_coherence_contract.get(
            "semantic_authority_files", []
        )
        if isinstance(row, dict) and set(row) == {"path", "sha256"}
    }
    for rel, expected_sha in FROZEN_UNCHANGED_SEMANTIC_HASHES.items():
        if revision == LANGUAGE_COHERENCE_REVISION:
            check(
                successor_semantic_files.get(rel) == file_sha(root / rel),
                "SUCCESSOR_SEMANTIC_FILE_IDENTITY",
                rel,
            )
            continue
        if revision == POST_PR16_REVISION and rel == "spec/types/type-system.md":
            continue
        check(file_sha(root / rel) == expected_sha, "FROZEN_SEMANTIC_FILE_IDENTITY", rel)
    r42 = feature_by_id.get("type_system_rcts_v5_ts_r42_current_canonical_companion", {})
    active_navigation_text = "\n".join(
        (root / rel).read_text(encoding="utf-8", errors="replace")
        for rel in ("README.md", "GOVERNANCE.md", "CONTRIBUTING.md", "current/current-pointer.json")
        if (root / rel).is_file()
    )
    check("EP1" not in active_navigation_text, "EP1_CURRENT_NAVIGATION_ZERO", "README/GOVERNANCE/CONTRIBUTING/pointer")
    check(
        r42.get("status_enum") == "SUPERSEDED"
        and r42.get("source_activation") == "nonactivatable",
        "R42_SUPERSEDED_NONACTIVATABLE",
        str(r42.get("status_enum")),
    )

    for path, value in parsed.items():
        if not path.is_relative_to(root / "schemas"):
            continue
        for ref in walk_refs(value):
            if ref.startswith(("http://", "https://", "urn:")):
                continue
            file_part, marker, fragment = ref.partition("#")
            target = path if not file_part else (path.parent / file_part).resolve()
            ok = target.is_file() and target in parsed
            check(ok, "LOCAL_JSON_REF_FILE", f"{path.relative_to(root)} -> {ref}")
            if ok and marker:
                check(resolve_pointer(parsed[target], "#" + fragment), "LOCAL_JSON_REF_FRAGMENT", f"{path.relative_to(root)} -> {ref}")

    operational = {
        "examples/manifests/by-outcome/catalog-metadata.json": ("source_file", "examples/guide/review-corpus.md"),
        "examples/manifests/design-gallery.json": ("source_file", "docs/guide/design-gallery.md"),
        "tests/conformance/checker-predicates/catalog-metadata.json": ("fixture_schema", "schemas/language/checker-predicate-fixture-row.schema.json"),
        "tests/fixtures/imported/uml-export-fixtures.json": ("profile_schema", "schemas/language/uml-export-profile.schema.json"),
        "tests/fixtures/imported/deterministic-suite-fixtures.json": ("profile_schema", "schemas/language/deterministic-suite-profile.schema.json"),
        "tests/fixtures/current/type-flow-callable-coherence-r1.json": ("fixture_schema", "schemas/language/type-flow-callable-coherence-fixtures.schema.json"),
        "tests/fixtures/current/destructuring-pattern-matching-r1.json": ("fixture_schema", "schemas/language/destructuring-pattern-matching-static-fixtures.schema.json"),
        "tests/fixtures/current/value-operator-indexing-coherence-r1.json": ("fixture_schema", "schemas/language/value-operator-indexing-coherence-fixtures.schema.json"),
        "tests/fixtures/current/type-refinement-narrowing-coherence-r1.json": ("fixture_schema", "schemas/language/type-refinement-narrowing-coherence-fixtures.schema.json"),
        "tests/fixtures/current/enum-derived-capabilities-r1.json": ("fixture_schema", "schemas/language/enum-derived-capabilities-fixtures.schema.json"),
        "tests/fixtures/current/literal-shaped-collection-design-r1.json": ("fixture_schema", "schemas/language/literal-shaped-collection-design-fixtures.schema.json"),
        "tests/fixtures/current/companion-capability-coherence-r1.json": ("fixture_schema", "schemas/language/companion-capability-coherence-fixtures.schema.json"),
        "tests/fixtures/current/rational-complex-numeric-coherence-r1.json": ("fixture_schema", "schemas/language/rational-complex-numeric-coherence-fixtures.schema.json"),
        "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json": ("fixture_schema", "schemas/language/hir-h1-current-mir-bridge-fixtures.schema.json"),
    }
    for rel, (field, expected) in operational.items():
        value = parsed.get(root / rel, {})
        check(value.get(field) == expected and (root / expected).exists(), "OPERATIONAL_POINTER", f"{rel}:{field}")

    numeric_contract = parsed.get(
        root / "spec/contracts/rational-complex-numeric-coherence.json", {}
    )
    numeric_fixture = parsed.get(
        root / "tests/fixtures/current/rational-complex-numeric-coherence-r1.json",
        {},
    )
    numeric_machine = numeric_contract.get("machine_acceptance", {})
    numeric_counts = numeric_fixture.get("expected_counts", {})
    numeric_cases = numeric_fixture.get("cases", [])
    numeric_by_id = {
        row.get("fixture_id"): row
        for row in numeric_cases
        if isinstance(row, dict)
    }
    check(
        numeric_contract.get("revision") == revision
        and numeric_fixture.get("revision") == revision
        and numeric_contract.get("semantic_p0") == 0
        and numeric_fixture.get("semantic_p0") == 0
        and numeric_machine.get("fixture_case_count") == len(numeric_cases) == 64
        and numeric_counts.get("cases") == 64
        and numeric_machine.get("exact_open_feature_p1_count")
        == numeric_counts.get("open_feature_p1")
        == 22
        and numeric_machine.get("feature_p1_closed_by_contract")
        == numeric_counts.get("p1_closed")
        == 0
        and numeric_machine.get("feature_p1_created_by_contract")
        == numeric_counts.get("p1_created")
        == 0
        and numeric_machine.get("fixed_conformance_operator_ids")
        == numeric_counts.get("fixed_conformance_operator_ids")
        == FIXED_OPERATOR_IDS
        and numeric_machine.get("arbitrary_custom_operator_count") == 0
        and numeric_machine.get("power_conformance_witness_count") == 0
        and numeric_machine.get("Rational_power_initial_profile_count") == 0
        and numeric_machine.get("integer_imaginary_literal_count") == 0
        and numeric_machine.get("runtime_operator_lookup_count") == 0
        and numeric_machine.get("product_lane_count")
        == numeric_machine.get("product_lane_not_run_count")
        == numeric_counts.get("product_lanes")
        == numeric_counts.get("product_not_run_lanes")
        == 15
        and numeric_counts.get("product_executed") == 0,
        "EXACT_NUMERIC_CONTRACT_AND_FIXTURE_CLOSURE",
        f"cases={len(numeric_cases)} counts={numeric_counts}",
    )
    numeric_negative_dividend_remainder = numeric_by_id.get(
        "RCN-R1-POS-013", {}
    )
    numeric_negative_divisor_remainder = numeric_by_id.get(
        "RCN-R1-POS-014", {}
    )
    numeric_zero_divisor_boundary = numeric_by_id.get(
        "RCN-R1-BOUND-006", {}
    )
    check(
        numeric_negative_dividend_remainder.get("subject")
        == "(-<7/3>) % <2/3> == -<1/3>"
        and numeric_negative_dividend_remainder.get("operator_id_or_null")
        == "BinaryRemainder"
        and "q=truncTowardZero((-7/3)/(2/3))=-3, r=-1/3"
        in numeric_negative_dividend_remainder.get("token_or_owner", "")
        and "identity=a-q*b,abs_r_lt_abs_b"
        in numeric_negative_dividend_remainder.get("mir_residue_or_null", "")
        and numeric_negative_divisor_remainder.get("subject")
        == "<7/3> % (-<2/3>) == <1/3>"
        and numeric_negative_divisor_remainder.get("operator_id_or_null")
        == "BinaryRemainder"
        and "q=truncTowardZero((7/3)/(-2/3))=-3, r=1/3"
        in numeric_negative_divisor_remainder.get("token_or_owner", "")
        and "identity=a-q*b,abs_r_lt_abs_b"
        in numeric_negative_divisor_remainder.get("mir_residue_or_null", "")
        and numeric_zero_divisor_boundary.get("operator_id_or_null")
        == "BinaryRemainder"
        and "ArithmeticDefect::divisionByZero before commit"
        in numeric_zero_divisor_boundary.get("token_or_owner", "")
        and "commit_count=0,original_residue_preserved=true"
        in numeric_zero_divisor_boundary.get("mir_residue_or_null", ""),
        "RATIONAL_REMAINDER_SIGN_IDENTITY_ZERO_DIVISOR_FIXTURE_BINDING",
        (
            f"negative_dividend={numeric_negative_dividend_remainder.get('subject')} "
            f"negative_divisor={numeric_negative_divisor_remainder.get('subject')} "
            f"zero={numeric_zero_divisor_boundary.get('subject')}"
        ),
    )
    check(
        all(
            feature_by_id.get(feature_id, {}).get("status_enum")
            == "STABLE_DESIGN"
            for feature_id in (
                "rational_exact_numeric_value",
                "complex_core_numeric_value",
                "scalar_real_complex_power",
            )
        )
        and all(
            predicate_id in predicate_by_id
            for predicate_id in (
                "RationalLiteralAdmitted",
                "ComplexLiteralAndOperatorAdmitted",
                "CaretPowerAdmitted",
            )
        )
        and all(
            diagnostic_id in diagnostic_by_id
            for diagnostic_id in (
                "RATIONAL_LITERAL_DENOMINATOR_ZERO",
                "IMAGINARY_LITERAL_FORM_NOT_ADMITTED",
                "COMPLEX_MIXED_REP_REQUIRES_EXPLICIT_CONVERSION",
                "POWER_OPERAND_DOMAIN_NOT_ADMITTED",
                "POWER_EXPECTED_RESULT_SELECTION_FORBIDDEN",
            )
        ),
        "EXACT_NUMERIC_REGISTRY_BINDING",
        "Rational/Complex/power feature, predicate, or diagnostic missing",
    )

    companion_contract = parsed.get(
        root / "spec/contracts/companion-capability-coherence.json", {}
    )
    companion_fixture = parsed.get(
        root / "tests/fixtures/current/companion-capability-coherence-r1.json",
        {},
    )
    companion_machine = companion_contract.get("machine_acceptance", {})
    companion_counts = companion_fixture.get("expected_counts", {})
    check(
        companion_contract.get("revision") == revision
        and companion_fixture.get("revision") == revision
        and companion_contract.get("semantic_p0") == 0
        and companion_machine.get("rule_count") == 18
        and companion_machine.get("lookup_domain_count") == 4
        and companion_machine.get("identity_residue_field_count") == 7
        and companion_machine.get("fixture_count")
        == companion_counts.get("cases")
        == len(companion_fixture.get("cases", []))
        == 28
        and companion_machine.get("open_feature_p1")
        == companion_counts.get("open_feature_p1")
        == 22
        and companion_machine.get("runtime_lookup_count") == 0
        and companion_machine.get("activation_trigger_count") == 0
        and companion_machine.get("companion_object_count") == 0
        and companion_machine.get("class_scope_static_current_acceptance_count")
        == 0
        and companion_machine.get("new_CALL_INPUT_COMMIT_event_count") == 0
        and companion_machine.get("product_lane_count")
        == companion_counts.get("product_lanes")
        == 15
        and companion_machine.get("product_executed_count")
        == companion_counts.get("product_executed")
        == 0
        and feature_by_id.get(
            "trait_qualified_associated_static_selection", {}
        ).get("status_enum")
        == "STABLE_DESIGN"
        and feature_by_id.get("companion_capability_decomposition", {}).get(
            "status_enum"
        )
        == "STABLE_DESIGN"
        and "TraitAssociatedStaticSelectionAdmitted" in predicate_by_id,
        "COMPANION_CAPABILITY_MACHINE_CLOSURE",
        f"machine={companion_machine} counts={companion_counts}",
    )

    hir_contract = parsed.get(
        root / "spec/contracts/hir-h1-current-mir-bridge.json", {}
    )
    hir_fixture = parsed.get(
        root / "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json", {}
    )
    hir_machine = hir_contract.get("machine_acceptance", {})
    hir_counts = hir_fixture.get("expected_counts", {})
    check(
        hir_contract.get("revision") == revision
        and hir_fixture.get("revision") == revision
        and hir_contract.get("semantic_p0") == 0
        and hir_machine.get("pipeline_stage_count") == 7
        and hir_machine.get("power_operation_count") == 6
        and hir_machine.get("power_adaptation_count") == 5
        and hir_machine.get("call_mode_count") == 3
        and hir_machine.get("resolved_call_plan_count") == 6
        and hir_machine.get("message_payload_aggregate_count") == 0
        and hir_machine.get("actor_transport_implicit_suspend_count") == 0
        and hir_machine.get("actor_transport_implicit_retry_count") == 0
        and hir_machine.get("fixture_count")
        == hir_counts.get("cases")
        == len(hir_fixture.get("cases", []))
        == 48
        and hir_machine.get("generic_pow_node_count") == 0
        and hir_machine.get("invalid_or_unresolved_canonical_count") == 0
        and hir_machine.get("implementation_or_execution_count")
        == hir_counts.get("implementation_or_execution")
        == 0
        and hir_machine.get("backend_switch_count")
        == hir_counts.get("backend_switches")
        == 0
        and hir_machine.get("open_feature_p1_count")
        == hir_counts.get("open_feature_p1")
        == 22
        and hir_machine.get("product_lanes") == "15/15_NOT_RUN"
        and hir_counts.get("product_lanes") == 15
        and hir_counts.get("product_executed") == 0
        and feature_by_id.get("hir_h1_current_mir_bridge_design", {}).get(
            "status_enum"
        )
        == "STABLE_DESIGN",
        "HIR_H1_CURRENT_MIR_BRIDGE_CLOSURE",
        f"machine={hir_machine} counts={hir_counts}",
    )

    cranelift_contract = parsed.get(
        root / "spec/contracts/cranelift-backend-current.json", {}
    )
    cranelift_fixture = parsed.get(
        root / "tests/fixtures/current/cranelift-backend-current-r1.json", {}
    )
    cranelift_cases = [
        row
        for row in cranelift_fixture.get("cases", [])
        if isinstance(row, dict)
    ]
    cranelift_rule_ids = [
        row.get("rule_id")
        for row in cranelift_contract.get("rules", [])
        if isinstance(row, dict)
    ]
    expected_cranelift_rule_ids = [
        f"CLB-R{index:03d}" for index in range(1, 13)
    ]
    expected_cranelift_paths = [
        "xvm_interpreter",
        "cranelift_object_aot_backend",
        "cranelift_jit_backend",
    ]
    cranelift_counts = cranelift_fixture.get("expected_counts", {})
    check(
        cranelift_contract.get("revision") == revision
        and cranelift_fixture.get("revision") == revision
        and cranelift_contract.get("status")
        == "CURRENT_BACKEND_ARCHITECTURE"
        and cranelift_contract.get("semantic_authority") == "Deeplus MIR"
        and cranelift_contract.get("semantic_p0") == 0
        and cranelift_contract.get("open_feature_p1_count") == 22
        and cranelift_contract.get("closed_feature_p1_by_backend_change") == 0
        and cranelift_contract.get("new_feature_p1_by_backend_change") == 0
        and cranelift_contract.get("product_lanes") == "15/15_NOT_RUN"
        and [
            row.get("id")
            for row in cranelift_contract.get("execution_paths", [])
        ]
        == expected_cranelift_paths
        and all(
            row.get("status") == "NOT_RUN"
            for row in cranelift_contract.get("execution_paths", [])
        )
        and cranelift_rule_ids == expected_cranelift_rule_ids
        and {
            rule_id
            for row in cranelift_cases
            for rule_id in row.get("rule_ids", [])
        }
        == set(expected_cranelift_rule_ids)
        and len(cranelift_cases)
        == len(
            {
                row.get("fixture_id")
                for row in cranelift_cases
            }
        )
        == cranelift_counts.get("cases")
        == 12
        and sum(row.get("class") == "positive" for row in cranelift_cases)
        == cranelift_counts.get("positive")
        == 6
        and sum(row.get("class") == "negative" for row in cranelift_cases)
        == cranelift_counts.get("negative")
        == 6
        and all(
            row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in cranelift_cases
        )
        and cranelift_counts.get("semantic_p0") == 0
        and cranelift_counts.get("open_feature_p1") == 22
        and cranelift_counts.get("p1_closed") == 0
        and cranelift_counts.get("p1_created") == 0
        and cranelift_counts.get("product_lanes") == 15
        and cranelift_counts.get("product_executed") == 0,
        "CRANELIFT_BACKEND_AUTHORITY_AND_FIXTURE_CLOSURE",
        (
            f"paths={expected_cranelift_paths} rules={len(cranelift_rule_ids)} "
            f"cases={len(cranelift_cases)} counts={cranelift_counts}"
        ),
    )
    cranelift_toolchain = cranelift_contract.get("toolchain_guard", {})
    cranelift_hir = cranelift_contract.get("hir_boundary", {})
    cranelift_projection = cranelift_contract.get("mir_projection", {})
    cranelift_outcomes = cranelift_contract.get("outcome_guard", {})
    cranelift_aot = cranelift_contract.get("aot_contract", {})
    cranelift_jit = cranelift_contract.get("jit_contract", {})
    cranelift_managed = cranelift_contract.get("managed_reference_guard", {})
    cranelift_debug = cranelift_contract.get("debug_guard", {})
    check(
        cranelift_toolchain.get("rust_toolchain") == "1.85.0"
        and cranelift_toolchain.get("selected_cranelift_family") == "0.121.2"
        and cranelift_toolchain.get("cargo_dependency_connected") is False
        and cranelift_toolchain.get("dependency_or_product_receipt_count") == 0
        and cranelift_hir.get("backend_neutral") is True
        and cranelift_hir.get("backend_specific_field_count") == 0
        and cranelift_hir.get("clif_identity_count") == 0
        and cranelift_hir.get("native_layout_identity_count") == 0
        and cranelift_hir.get("calling_convention_identity_count") == 0
        and cranelift_projection.get("input") == "Verified<DeeplusMir>"
        and cranelift_projection.get("module_kinds")
        == ["ObjectAot", "InMemoryJit"]
        and cranelift_projection.get("clif_is_semantic_authority") is False
        and cranelift_projection.get("object_and_jit_share_lowering") is True
        and cranelift_projection.get("module_local_id_selects_semantics")
        is False
        and cranelift_projection.get("symbol_or_link_order_selects_semantics")
        is False
        and len(cranelift_contract.get("required_receipt_inputs", [])) == 12
        and cranelift_outcomes.get("native_exception_semantic_authority")
        is False
        and cranelift_outcomes.get("host_unwind_semantic_authority") is False
        and cranelift_outcomes.get(
            "arbitrary_backend_trap_semantic_authority"
        )
        is False
        and cranelift_outcomes.get(
            "trap_requires_preselected_defect_or_verified_unreachable"
        )
        is True
        and cranelift_aot.get("module") == "ObjectModule"
        and len(cranelift_aot.get("required_output_identity", [])) == 5
        and cranelift_jit.get("module") == "JITModule"
        and len(cranelift_jit.get("required_output_identity", [])) == 5
        and cranelift_jit.get(
            "missing_duplicate_or_signature_mismatched_import"
        )
        == "TERMINAL_LINK_FAILURE"
        and cranelift_managed.get("mir_safepoint_identity_preserved") is True
        and cranelift_managed.get("root_map_requirement_preserved") is True
        and cranelift_managed.get("raw_pointer_fallback") is False
        and cranelift_debug.get("separate_debug_digest") is True
        and cranelift_debug.get("debug_info_is_semantic_authority") is False
        and (root / "crates/deeplus-codegen-cranelift/Cargo.toml").is_file(),
        "CRANELIFT_HIR_MIR_PROJECTION_BOUNDARY",
        (
            f"toolchain={cranelift_toolchain} hir={cranelift_hir} "
            f"module={cranelift_projection.get('module_kinds')}"
        ),
    )

    tfc_rel = "tests/fixtures/current/type-flow-callable-coherence-r1.json"
    tfc = parsed.get(root / tfc_rel, {})
    tfc_top_keys = {
        "schema", "fixture_schema", "revision", "contract", "evidence_status",
        "product_support", "product_lanes", "fixture_policy", "positive",
        "negative", "boundary", "expected_counts",
    }
    check(set(tfc) == tfc_top_keys, "TFC_FIXTURE_CLOSED_SHAPE", str(sorted(set(tfc) ^ tfc_top_keys)))
    tfc_groups = {
        "positive": tfc.get("positive", []),
        "negative": tfc.get("negative", []),
        "boundary": tfc.get("boundary", []),
    }
    tfc_rows = [row for rows in tfc_groups.values() for row in rows if isinstance(row, dict)]
    tfc_ids = [row.get("fixture_id") for row in tfc_rows]
    tfc_counts = tfc.get("expected_counts", {})
    check(
        len(tfc_rows) == len(tfc_ids) == len(set(tfc_ids))
        and all(tfc_counts.get(group) == len(rows) for group, rows in tfc_groups.items())
        and tfc_counts.get("total") == len(tfc_rows)
        and tfc_counts.get("product_executed") == 0,
        "TFC_FIXTURE_COUNT_AND_ID_CLOSURE",
        f"rows={len(tfc_rows)} ids={len(set(tfc_ids))} counts={tfc_counts}",
    )
    tfc_contract = parsed.get(root / "spec/contracts/type-flow-callable-coherence.json", {})
    tfc_rule_ids = [row.get("rule_id") for row in tfc_contract.get("rules", []) if isinstance(row, dict)]
    check(
        len(tfc_rule_ids) == 22
        and len(set(tfc_rule_ids)) == 22
        and all(
            isinstance(row.get("rule_ids"), list)
            and row["rule_ids"]
            and set(row["rule_ids"]).issubset(set(tfc_rule_ids))
            for row in tfc_rows
        ),
        "TFC_RULE_BINDING_CLOSURE",
        f"rules={len(tfc_rule_ids)} rows={len(tfc_rows)}",
    )
    cleanup_skip = next(
        (row for row in tfc_groups["negative"] if row.get("fixture_id") == "TFC-N-025-CLEANUP-SKIP"),
        {},
    )
    cleanup_descriptor = cleanup_skip.get("responsibility_descriptor", {})
    check(
        cleanup_skip.get("expected_existing_diagnostic") == "DEFER_CLEANUP_RESERVED_PLACE_MOVED"
        and cleanup_descriptor.get("normalized_type") == "File"
        and cleanup_descriptor.get("ownership") == "resource"
        and cleanup_descriptor.get("cleanup") == "drop_exactly_once"
        and cleanup_descriptor.get("bound_place") == "resource",
        "TFC_CLEANUP_OBLIGATION_EXPLICIT",
        str(cleanup_descriptor),
    )
    tfc_parameter_modes = tfc_contract.get("parameter_mode_matrix", [])
    tfc_ternary = tfc_contract.get("ternary_join_contract", {})
    tfc_by_id = {row.get("fixture_id"): row for row in tfc_rows}
    tfc_rule_by_id = {
        row.get("rule_id"): row
        for row in tfc_contract.get("rules", [])
        if isinstance(row, dict)
    }
    trailing_contract = tfc_rule_by_id.get("TFC-R011", {}).get("contract", {})
    message_call_contract = tfc_rule_by_id.get("TFC-R021", {}).get("contract", {})
    responsibility_clause_contract = tfc_rule_by_id.get("TFC-R022", {}).get(
        "contract", {}
    )
    repeated_responsibility_case = tfc_by_id.get(
        "TFC-P-028-REPEATED-CALLABLE-RESPONSIBILITIES", {}
    )
    rejected_throws_bar_case = tfc_by_id.get(
        "TFC-N-030-CALLABLE-THROWS-BAR-LIST", {}
    )
    effect_clause_boundary = tfc_by_id.get(
        "TFC-B-022-CALLABLE-EFFECT-CLAUSE-LIST", {}
    )
    call_frontend = parsed.get(
        root / "spec/frontend/frontend-model.json", {}
    ).get("call_frontend_contract", {})
    call_ast = (
        call_frontend.get("normalized_ast_nodes", {})
        .get("CallExpr", {})
    )
    message_grammar = (
        root / "spec/grammar/deeplus.ebnf"
    ).read_text(encoding="utf-8")
    check(
        trailing_contract.get("trailing_closure_owner")
        == "TrailingClosureGroup shared by every CallExpr mode"
        and "every closure is labeled" in trailing_contract.get(
            "multiple_trailing_closures", ""
        )
        and message_call_contract.get("argument_cardinality") == "zero_to_many"
        and message_call_contract.get("ordinary_argument_list_owner_reused")
        is True
        and message_call_contract.get("message_payload_node_count") == 0
        and message_call_contract.get("tuple_or_record_payload_projection_count")
        == 0
        and message_call_contract.get("trailing_closure_contract")
        == "TFC-R011"
        and tfc_contract.get("machine_acceptance", {}).get(
            "message_payload_max_count"
        )
        == 0
        and tfc_contract.get("machine_acceptance", {}).get(
            "message_argument_list_reuse_count"
        )
        == 1
        and tfc_contract.get("machine_acceptance", {}).get(
            "normalized_call_node_count"
        )
        == 1
        and tfc_contract.get("machine_acceptance", {}).get("call_mode_count") == 3
        and tfc_contract.get("machine_acceptance", {}).get(
            "actor_colon_tilde_surface_count"
        )
        == 1
        and tfc_contract.get("machine_acceptance", {}).get(
            "multiple_trailing_closures_require_all_named"
        )
        is True,
        "MESSAGE_CALL_CONTRACT_MACHINE_CLOSURE",
        f"arguments={message_call_contract.get('argument_cardinality')} trailing={trailing_contract.get('multiple_trailing_closures')}",
    )
    check(
        responsibility_clause_contract.get("throws_surface")
        == "throws ErrorSetTerm"
        and responsibility_clause_contract.get("effects_surface")
        == "effects CallableEffectTerm"
        and responsibility_clause_contract.get("multiple_error_surface")
        == "repeat throws"
        and responsibility_clause_contract.get("multiple_effect_surface")
        == "repeat effects"
        and responsibility_clause_contract.get("explicit_empty_error_surface")
        == "throws Never"
        and responsibility_clause_contract.get("explicit_empty_effect_surface")
        == "effects {}"
        and responsibility_clause_contract.get("callable_error_bar_union_count")
        == 0
        and responsibility_clause_contract.get(
            "callable_nonempty_effect_set_literal_count"
        )
        == 0
        and responsibility_clause_contract.get("throws_before_effects") is True
        and responsibility_clause_contract.get(
            "duplicate_normalized_term_admitted"
        )
        is False
        and repeated_responsibility_case.get("expected_outcome") == "accept"
        and repeated_responsibility_case.get("assertions", {}).get(
            "throws_clause_count"
        )
        == 2
        and repeated_responsibility_case.get("assertions", {}).get(
            "effects_clause_count"
        )
        == 2
        and rejected_throws_bar_case.get("expected_existing_diagnostic")
        == "CALLABLE_THROWS_CLAUSE_REPETITION_REQUIRED"
        and effect_clause_boundary.get(
            "expected_existing_diagnostic_for_reject"
        )
        == "CALLABLE_EFFECTS_CLAUSE_REPETITION_REQUIRED",
        "TFC_CALLABLE_RESPONSIBILITY_CLAUSE_REPETITION",
        (
            f"throws={responsibility_clause_contract.get('multiple_error_surface')} "
            f"effects={responsibility_clause_contract.get('multiple_effect_surface')}"
        ),
    )
    check(
        'CallSuffix ::= ArgumentList TrailingClosureGroup?' in message_grammar
        and 'TildeCallLed ::= TildeCallToken MessageSelector' in message_grammar
        and 'TildeCallToken ::= "~" | ":~" ;' in message_grammar
        and 'TildeArgumentSequence ::= TildeArgument ("," TildeArgument)* ;'
        in message_grammar
        and 'TrailingClosureArgument ::= ClosureExpr | Identifier ":" ClosureExpr ;'
        in message_grammar
        and "MessagePayload" not in message_grammar
        and 'DeferredMessageCall ::= DeferredReceiver "~" MessageSelector TildeArgumentSequence? ;'
        in message_grammar
        and call_ast.get("mode") == "Ordinary | Message | ActorMessage"
        and call_frontend.get("mode_and_pratt_contract", {}).get(
            "message_payload_node_count"
        )
        == 0
        and call_frontend.get("mode_and_pratt_contract", {}).get(
            "ordinary_argument_list_reuse_count"
        )
        == 1
        and parsed.get(
            root / "spec/frontend/frontend-model.json", {}
        ).get("control_frontend_contract", {}).get(
            "parenless_call_exception"
        )
        == "one AtomicCallArgument followed by one TrailingClosureGroup",
        "MESSAGE_CALL_GRAMMAR_FRONTEND_PARITY",
        "Unified CallExpr modes and structured tilde arguments",
    )
    rcts_schema = parsed.get(
        root / "schemas/language/rcts-v5-descriptor.schema.json", {}
    )
    callable_variants = [
        row
        for row in rcts_schema.get("oneOf", [])
        if isinstance(row, dict)
        and row.get("properties", {}).get("variant", {}).get("const")
        == "callable"
    ]
    callable_call_shape = (
        callable_variants[0].get("properties", {}).get("call_shape", {})
        if len(callable_variants) == 1
        else {}
    )
    mir_schema = parsed.get(
        root / "schemas/language/mir-responsibility.schema.json", {}
    )
    residence_array_schema = mir_schema.get("properties", {}).get(
        "callable_residence_descriptors", {}
    )
    residence_descriptor_schema = (
        mir_schema.get("$defs", {}).get("callableResidenceDescriptor", {})
    )

    def callable_residence_rows_are_coherent(rows: Any) -> bool:
        if not isinstance(rows, list):
            return False
        callable_ids = [
            row.get("callable_id")
            for row in rows
            if isinstance(row, dict)
        ]
        if (
            len(callable_ids) != len(rows)
            or any(not isinstance(value, str) or not value for value in callable_ids)
            or len(callable_ids) != len(set(callable_ids))
        ):
            return False
        for row in rows:
            residence = row.get("residence", {})
            dependencies = row.get("lexical_dependencies", [])
            closed = row.get("closed_ancestor_frame_assertion")
            if not isinstance(dependencies, list) or not isinstance(closed, bool):
                return False
            if residence.get("kind") == "FrameIndependent" and dependencies:
                return False
            if closed and dependencies:
                return False
            if dependencies and (
                residence.get("kind") != "RegionBound" or closed
            ):
                return False
        return True

    coherent_residence_rows = [
        {
            "callable_id": "callable.closed",
            "residence": {"kind": "FrameIndependent", "region_id": None},
            "environment": {"kind": "Empty", "capture_plan_id": None},
            "closed_ancestor_frame_assertion": True,
            "lexical_dependencies": [],
        },
        {
            "callable_id": "callable.mixed",
            "residence": {"kind": "RegionBound", "region_id": "region.outer"},
            "environment": {
                "kind": "Explicit",
                "capture_plan_id": "capture.seed",
            },
            "closed_ancestor_frame_assertion": False,
            "lexical_dependencies": [
                {
                    "place_id": "place.offset",
                    "access": "shared_read",
                    "lifetime": "call_duration",
                }
            ],
        },
    ]
    incoherent_residence_rows = [
        coherent_residence_rows + [dict(coherent_residence_rows[0])],
        [
            {
                **coherent_residence_rows[0],
                "lexical_dependencies": [
                    {
                        "place_id": "place.bad",
                        "access": "shared_read",
                        "lifetime": "call_duration",
                    }
                ],
            }
        ],
        [
            {
                **coherent_residence_rows[1],
                "closed_ancestor_frame_assertion": True,
            }
        ],
    ]
    check(
        residence_array_schema.get("x-deeplus-unique-by") == "callable_id"
        and len(residence_descriptor_schema.get("allOf", [])) == 3
        and callable_residence_rows_are_coherent(coherent_residence_rows)
        and all(
            not callable_residence_rows_are_coherent(rows)
            for rows in incoherent_residence_rows
        ),
        "NONESCAPING_LEXICAL_ACCESS_MIR_DESCRIPTOR_INVARIANTS",
        "unique callable identity + residence/closed/dependency exclusion",
    )
    module_schema = parsed.get(
        root / "schemas/language/module-api-digest.schema.json", {}
    )
    module_channel_properties = (
        module_schema.get("$defs", {})
        .get("responsibilityChannel", {})
        .get("properties", {})
    )
    check(
        len(callable_call_shape.get("oneOf", [])) == 2
        and mir_schema.get("properties", {})
        .get("call_responsibilities", {})
        .get("items", {})
        .get("$ref")
        == "#/$defs/callResponsibilityDescriptor"
        and mir_schema.get("$defs", {})
        .get("callResponsibilityDescriptor", {})
        .get("properties", {})
        .get("payload_count", {})
        .get("maximum")
        == 1
        and "visible_label" in module_channel_properties
        and "trailing_closure"
        in module_channel_properties.get("call_channel_kind", {}).get("enum", []),
        "MESSAGE_CALL_RCTS_MIR_API_BINDING",
        "RCTS call_shape + MIR call responsibility + API channel label",
    )
    check(
        tfc_by_id.get(
            "TFC-P-025-MULTIPLE-ALL-NAMED-TRAILING-CLOSURES", {}
        )
        .get("assertions", {})
        .get("all_named")
        is True
        and tfc_by_id.get(
            "TFC-P-026-QUALIFIED-MESSAGE-TUPLE-ARGUMENT", {}
        )
        .get("assertions", {})
        .get("argument_expression_type")
        == "Tuple"
        and tfc_by_id.get(
            "TFC-P-027-MESSAGE-NAMED-ARGUMENTS-MULTIPLE-CLOSURES", {}
        )
        .get("assertions", {})
        .get("ordered_argument_count")
        == 2
        and tfc_by_id.get(
            "TFC-N-027-MIXED-NAMED-UNNAMED-TRAILING-CLOSURES", {}
        )
        .get("expected_existing_diagnostic")
        == "MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT"
        and tfc_by_id.get(
            "TFC-N-029-DUPLICATE-MESSAGE-ARGUMENT-LABEL", {}
        )
        .get("expected_existing_diagnostic")
        == "STATIC_CALL_SHAPE_NOT_ADMITTED",
        "MESSAGE_CALL_FIXTURE_MATRIX",
        "positive=tuple-argument|named-arguments|multiple-named negative=mixed-group|duplicate-label",
    )
    check(
        [row.get("mode") for row in tfc_parameter_modes]
        == ["ordinary", "mut", "borrow", "move", "inout"]
        and tfc_parameter_modes[1].get("caller_writeback") is False
        and tfc_parameter_modes[4].get("caller_writeback") is True
        and tfc_contract.get("machine_acceptance", {}).get(
            "ordinary_mut_precommit_owner_retention"
        )
        is True
        and tfc_by_id.get("TFC-P-022-ORDINARY-MUT-CALLEE-LOCAL", {})
        .get("assertions", {})
        .get("caller_writeback_count")
        == 0
        and tfc_by_id.get("TFC-B-019-MUT-PRECOMMIT-FAILURE", {})
        .get("assertions", {})
        .get("caller_owner_retained")
        is True,
        "TFC_PARAMETER_MODE_MACHINE_CLOSURE",
        f"modes={[row.get('mode') for row in tfc_parameter_modes]}",
    )
    check(
        tfc_ternary.get("condition_evaluation_count") == 1
        and tfc_ternary.get("selected_arm_evaluation_count") == 1
        and tfc_ternary.get("unselected_arm_evaluation_count") == 0
        and tfc_ternary.get("automatic_anonymous_union_count") == 0
        and set(tfc_ternary.get("joined_axes", []))
        == {
            "normalized value type",
            "place capability",
            "ownership",
            "effects",
            "recoverable errors",
            "cancellation",
            "cleanup",
        }
        and tfc_by_id.get("TFC-B-016-TERNARY-RESPONSIBILITY-JOIN", {})
        .get("descriptor", {})
        .get("discarded_obligation_count")
        == 0,
        "TFC_TERNARY_MACHINE_CLOSURE",
        str(tfc_ternary),
    )

    dpm_rel = "tests/fixtures/current/destructuring-pattern-matching-r1.json"
    dpm = parsed.get(root / dpm_rel, {})
    dpm_top_keys = {
        "schema", "fixture_schema", "revision", "authority", "evidence_level",
        "product_execution", "phase_profile", "failure_profile",
        "lifecycle_identities", "counts", "fixtures",
    }
    dpm_row_keys = {
        "fixture_id", "fixture_class", "context_id", "pattern_kind_id", "source",
        "subject_profile", "expected", "primary_diagnostic_family_or_null",
        "assertions", "execution_state",
    }
    dpm_rows = [row for row in dpm.get("fixtures", []) if isinstance(row, dict)]
    dpm_ids = [row.get("fixture_id") for row in dpm_rows]
    dpm_class_counts = Counter(row.get("fixture_class") for row in dpm_rows)
    dpm_counts = dpm.get("counts", {})
    check(
        set(dpm) == dpm_top_keys
        and all(set(row) == dpm_row_keys for row in dpm_rows),
        "DPM_FIXTURE_CLOSED_SHAPE",
        f"top_delta={sorted(set(dpm) ^ dpm_top_keys)} rows={len(dpm_rows)}",
    )
    check(
        len(dpm_rows) == len(dpm_ids) == len(set(dpm_ids)) == dpm_counts.get("fixtures")
        and all(dpm_counts.get(group) == dpm_class_counts.get(group, 0) for group in ("positive", "negative", "boundary"))
        and dpm_counts.get("product_executed") == 0
        and all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in dpm_rows),
        "DPM_FIXTURE_COUNT_AND_ID_CLOSURE",
        f"rows={len(dpm_rows)} ids={len(set(dpm_ids))} classes={dict(dpm_class_counts)}",
    )

    psm_contract_rel = "spec/contracts/pattern-sequence-multivalue-r1.json"
    psm_contract = parsed.get(root / psm_contract_rel, {})
    psm_acceptance = psm_contract.get("acceptance", {})
    psm_rest = psm_contract.get("sequence_rest", {})
    psm_rest_result = psm_rest.get("rest_result", {})
    psm_assignment = psm_contract.get("assignment", {})
    psm_lowering = psm_contract.get("lowering_invariants", {})
    psm_sources = {
        row.get("filename"): (row.get("bytes"), row.get("sha256"), row.get("precedence"))
        for row in psm_contract.get("source_packages", [])
        if isinstance(row, dict)
    }
    psm_diagnostic_families = psm_contract.get("diagnostic_families", [])
    check(
        psm_contract.get("schema") == "deeplus.pattern-sequence-multivalue-contract/r1"
        and psm_contract.get("revision") == LANGUAGE_COHERENCE_REVISION
        and psm_contract.get("status") == "CURRENT_STABLE_DESIGN_WITH_PREVIEW_GATES"
        and psm_contract.get("semantic_p0") == 0
        and psm_contract.get("product_lanes") == "15/15_NOT_RUN"
        and len(psm_contract.get("stable_design", [])) == 20
        and len(psm_contract.get("preview_gated", [])) == 14
        and len(psm_contract.get("not_admitted", [])) == 10,
        "PSM_CONTRACT_IDENTITY_AND_DECISION_COUNTS",
        f"acceptance={psm_acceptance}",
    )
    check(
        psm_sources
        == {
            "Design_Deeplus_Sequence_Rest_and_Multi_Value_Revision_R3.zip": (
                23760,
                "6e4f9f433e2b6abe631b07427b9ffa9c6a9495d08dee93fa6765dfa652c7c60b",
                "CONTROLS_SEQUENCE_REST_AND_MULTI_VALUE",
            ),
            "Design_Deeplus_Pattern_and_Destructuring_Revision_R2.zip": (
                36559,
                "93b685e088f5de2aa4eafde9ca9161178b3c34456f3028b19adf5bf48b0cea20",
                "CONTROLS_REMAINING_PATTERN_AND_DESTRUCTURING_SCOPE",
            ),
        },
        "PSM_SOURCE_PACKAGE_PROVENANCE_BINDING",
        repr(psm_sources),
    )
    check(
        len(psm_diagnostic_families)
        == len(set(psm_diagnostic_families))
        == psm_acceptance.get("diagnostic_family_count")
        == 20
        and all(
            diagnostic_id in diagnostic_by_id
            and diagnostic_by_id[diagnostic_id].get("diagnostic_status")
            == "active"
            for diagnostic_id in psm_diagnostic_families
        ),
        "PSM_DIAGNOSTIC_FAMILY_CATALOG_BINDING",
        repr(psm_diagnostic_families),
    )
    check(
        psm_rest.get("maximum_rest_per_pattern") == 1
        and psm_rest.get("descriptor") == "SequenceDecompositionDescriptorV1"
        and psm_rest.get("sequence_conformance_alone_activates_pattern") is False
        and psm_rest_result.get("borrowed_type") == "ListRestView<T>"
        and psm_rest_result.get("moved_list_type") == "List<T>"
        and psm_rest_result.get("requires_sequence_conformance") is True
        and psm_rest_result.get("coordinate_provenance_preserved") is True
        and psm_rest_result.get("hidden_copy_or_allocation") is False
        and "count=0" in psm_rest_result.get("empty_representation", "")
        and psm_rest.get("list_rest_view", {}).get(
            "ordinary_readonly_view_sequence_witness_changed"
        )
        is False,
        "PSM_SEQUENCE_REST_CARRIER_CLOSURE",
        repr(psm_rest_result),
    )
    check(
        psm_contract.get("tuple_and_multi_value", {}).get("semantic_carrier")
        == "Tuple"
        and psm_contract.get("tuple_and_multi_value", {}).get(
            "general_comma_operator"
        )
        is False
        and psm_contract.get("tuple_and_multi_value", {}).get(
            "sequence_as_fixed_return_carrier"
        )
        is False
        and psm_assignment.get("initial_targets")
        == "DISTINCT_DIRECT_MUTABLE_LOCALS"
        and psm_assignment.get("commit")
        == "ONE_FAILURE_ATOMIC_LOGICAL_GROUP_COMMIT"
        and psm_assignment.get("hardware_atomicity") is False
        and psm_assignment.get("cross_thread_atomicity") is False
        and psm_lowering.get("subject_evaluation_count") == 1
        and psm_lowering.get("precommit_irreversible_move_count") == 0
        and psm_lowering.get("failed_probe_commit_count") == 0
        and psm_lowering.get("false_guard_commit_count") == 0
        and psm_lowering.get("hidden_allocation_count") == 0
        and psm_lowering.get("product_execution_receipt_count") == 0,
        "PSM_TUPLE_ASSIGNMENT_AND_LOWERING_CLOSURE",
        f"assignment={psm_assignment} lowering={psm_lowering}",
    )

    psm_fixture_rel = "tests/fixtures/current/pattern-sequence-multivalue-r1.json"
    psm_fixture = parsed.get(root / psm_fixture_rel, {})
    psm_fixture_rows = [
        row for row in psm_fixture.get("fixtures", []) if isinstance(row, dict)
    ]
    psm_fixture_ids = [row.get("fixture_id") for row in psm_fixture_rows]
    psm_fixture_classes = Counter(
        row.get("fixture_class") for row in psm_fixture_rows
    )
    psm_fixture_row_keys = {
        "fixture_id",
        "fixture_class",
        "surface",
        "rule",
        "expected",
        "assertions",
        "execution",
    }
    check(
        psm_fixture.get("schema")
        == "deeplus.pattern-sequence-multivalue-fixtures/r1"
        and psm_fixture.get("revision") == LANGUAGE_COHERENCE_REVISION
        and psm_fixture.get("contract") == psm_contract_rel
        and psm_fixture.get("product_lanes") == "15/15_NOT_RUN"
        and len(psm_fixture_rows)
        == len(psm_fixture_ids)
        == len(set(psm_fixture_ids))
        == 40
        and psm_fixture_classes
        == Counter({"positive": 24, "negative": 12, "preview": 4})
        and all(set(row) == psm_fixture_row_keys for row in psm_fixture_rows)
        and all(
            row.get("execution") == "DESIGN_STATIC_NOT_RUN"
            for row in psm_fixture_rows
        ),
        "PSM_FIXTURE_SHAPE_COUNT_AND_ID_CLOSURE",
        f"rows={len(psm_fixture_rows)} classes={dict(psm_fixture_classes)}",
    )

    voi_rel = "tests/fixtures/current/value-operator-indexing-coherence-r1.json"
    voi = parsed.get(root / voi_rel, {})
    voi_top_keys = {
        "schema", "fixture_schema", "revision", "contract", "authority",
        "evidence_level", "semantic_p0", "current_binding", "open_feature_p1",
        "separate_open_actions", "product_lanes", "positive", "negative",
        "boundary", "expected_counts",
    }
    voi_row_keys = {
        "fixture_id", "fixture_class", "rule_ids", "domain", "source",
        "subject_profile", "expected", "diagnostic_or_null", "assertions",
        "execution_state",
    }
    voi_groups = {
        group: voi.get(group, []) for group in ("positive", "negative", "boundary")
    }
    voi_rows = [
        row for group in voi_groups.values() for row in group if isinstance(row, dict)
    ]
    voi_ids = [row.get("fixture_id") for row in voi_rows]
    voi_counts = voi.get("expected_counts", {})
    check(
        set(voi) == voi_top_keys
        and all(set(row) == voi_row_keys for row in voi_rows)
        and len(voi_rows) == len(voi_ids) == len(set(voi_ids)) == 67
        and all(voi_counts.get(group) == len(rows) for group, rows in voi_groups.items())
        and voi_counts.get("total") == 67
        and voi_counts.get("semantic_p0") == 0
        and voi_counts.get("open_feature_p1") == 22
        and voi_counts.get("closed_feature_p1") == 0
        and voi_counts.get("new_feature_p1") == 0
        and voi_counts.get("product_executed") == 0,
        "VOI_FIXTURE_SHAPE_COUNT_AND_ID_CLOSURE",
        f"rows={len(voi_rows)} ids={len(set(voi_ids))} counts={voi_counts}",
    )
    voi_contract = parsed.get(root / "spec/contracts/value-operator-indexing-coherence.json", {})
    voi_rule_ids = [
        row.get("rule_id") for row in voi_contract.get("rules", []) if isinstance(row, dict)
    ]
    expected_voi_rules = [f"VOI-R{index:03d}" for index in range(1, 13)]
    expected_feature_p1 = SUCCESSOR_ACTION_IDS[4:]
    expected_product_lanes = {row: "NOT_RUN" for row in (
        "rust_frontend_lexer", "rust_frontend_parser", "rust_hir_lowering",
        "rust_integrated_checker", "deeplus_mir_lowering", "xvm_bytecode_emitter",
        "xvm_interpreter", "cranelift_object_aot_backend", "cranelift_jit_backend",
        "formatter_lsp", "stdlib_provider_runner", "official_tooling",
        "independent_conformance", "cross_backend_conformance",
        "actual_user_team_study",
    )}
    check(
        voi_rule_ids == expected_voi_rules
        and {
            rule_id
            for row in voi_rows
            for rule_id in row.get("rule_ids", [])
        } == set(expected_voi_rules)
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(expected_voi_rules))
            and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in voi_rows
        )
        and voi.get("open_feature_p1") == expected_feature_p1
        and voi.get("separate_open_actions") == EXPECTED_ACTION_IDS
        and voi.get("product_lanes") == expected_product_lanes,
        "VOI_RULE_GUARD_AND_PRODUCT_CLOSURE",
        f"rules={voi_rule_ids} p1={len(voi.get('open_feature_p1', []))} lanes={len(voi.get('product_lanes', {}))}",
    )
    voi_by_id = {row.get("fixture_id"): row for row in voi_rows}
    voi_map_plan = voi_contract.get("map_literal_plan_contract", {})
    voi_transpose = voi_contract.get("numeric_array_transpose_contract", {})
    check(
        voi_map_plan.get("entry_kinds") == ["direct_key_value", "map_unfold"]
        and voi_map_plan.get("normalized_key_domain_count") == 1
        and voi_map_plan.get("normalized_value_domain_count") == 1
        and voi_map_plan.get("displaced_owner_cleanup_count") == 1
        and voi_map_plan.get("publication_count_on_failure") == 0
        and voi_map_plan.get("keyable_operation_contract", {}).get("errors") == []
        and voi_map_plan.get("keyable_operation_contract", {}).get("effects") == []
        and voi_map_plan.get("call_record_unfold", {}).get(
            "map_literal_plan_entry"
        )
        is False
        and voi_by_id.get("VOI-R1-BND-015", {})
        .get("assertions", {})
        .get("partial_map_escape_count")
        == 0,
        "VOI_MAP_LITERAL_PLAN_MACHINE_CLOSURE",
        str(voi_map_plan),
    )
    check(
        voi_transpose.get("implicit_element_copy_count") == 0
        and voi_transpose.get("language_observable_allocation_count") == 0
        and voi_transpose.get("owner_lifetime_escape_count") == 0
        and voi_transpose.get("isolation_crossing_count") == 0
        and voi_transpose.get("backend_representation_selected") is False
        and voi_by_id.get("VOI-R1-NEG-022", {}).get("diagnostic_or_null")
        == "NUMARR_VECTOR_TRANSPOSE_REQUIRES_ORIENTATION"
        and voi_by_id.get("VOI-R1-BND-017", {})
        .get("assertions", {})
        .get("implicit_element_copy_count")
        == 0,
        "VOI_TRANSPOSE_MACHINE_CLOSURE",
        str(voi_transpose),
    )
    voi_machine = voi_contract.get("machine_acceptance", {})
    voi_rules_by_id = {
        row.get("rule_id"): row
        for row in voi_contract.get("rules", [])
        if isinstance(row, dict)
    }
    voi_fixed_profile = (
        voi_rules_by_id.get("VOI-R005", {})
        .get("contract", {})
        .get("fixed_operator_stable_profile", {})
    )
    frontend_contract = parsed.get(
        root / "spec/frontend/frontend-model.json", {}
    ).get("fixed_operator_conformance_frontend_contract", {})
    expected_value_operator_rows = [
        {
            "operator_id": operator_id,
            "glyph": glyph,
            "fixity": fixity,
            "trait_id": trait_id,
            "method_id": method_id,
            "result": result,
            "projection": value_projection,
        }
        for (
            operator_id, glyph, fixity, trait_id, method_id, result,
            value_projection, _frontend_projection,
        ) in FIXED_OPERATOR_MAPPING
    ]
    expected_frontend_operator_rows = [
        {
            "operator_id": operator_id,
            "glyph": glyph,
            "fixity": fixity,
            "trait_id": trait_id,
            "method_id": method_id,
            "output_projection": frontend_projection,
            "responsibility_profile_id": (
                FIXED_OPERATOR_COMPARISON_PROFILE_ID
                if operator_id in FIXED_OPERATOR_COMPARISON_IDS
                else FIXED_OPERATOR_ARITHMETIC_PROFILE_ID
            ),
        }
        for (
            operator_id, glyph, fixity, trait_id, method_id, _result,
            _value_projection, frontend_projection,
        ) in FIXED_OPERATOR_MAPPING
    ]
    mir_schema = parsed.get(
        root / "schemas/language/mir-responsibility.schema.json", {}
    )
    api_schema = parsed.get(
        root / "schemas/language/module-api-digest.schema.json", {}
    )
    mir_fixed_schema = (
        mir_schema.get("$defs", {})
        .get("fixedOperatorConformanceDispatch", {})
    )
    api_fixed_schema = (
        api_schema.get("$defs", {})
        .get("fixedOperatorConformanceResidue", {})
    )
    mir_operator_ids = (
        mir_fixed_schema
        .get("properties", {})
        .get("operator_id", {})
        .get("enum")
    )
    api_operator_ids = (
        api_fixed_schema
        .get("properties", {})
        .get("operator_id", {})
        .get("enum")
    )
    check(
        [row[0] for row in FIXED_OPERATOR_MAPPING] == FIXED_OPERATOR_IDS
        and voi_fixed_profile.get("admitted_operator_ids")
        == FIXED_OPERATOR_IDS
        and voi_fixed_profile.get("trait_roots")
        == FIXED_OPERATOR_TRAIT_ROOTS
        and voi_fixed_profile.get("operator_trait_mapping")
        == expected_value_operator_rows
        and frontend_contract.get("trait_roots")
        == FIXED_OPERATOR_TRAIT_ROOTS
        and frontend_contract.get("admitted_operator_rows")
        == expected_frontend_operator_rows
        and mir_operator_ids == FIXED_OPERATOR_IDS
        and api_operator_ids == FIXED_OPERATOR_IDS,
        "FIXED_OPERATOR_VALUE_FRONTEND_MIR_API_EXACT_BINDING",
        (
            f"value_rows={len(voi_fixed_profile.get('operator_trait_mapping', []))} "
            f"frontend_rows={len(frontend_contract.get('admitted_operator_rows', []))} "
            f"mir={mir_operator_ids} api={api_operator_ids}"
        ),
    )
    mir_fixed_contract = mir_schema.get(
        "x-deeplus-fixed-operator-conformance-contract", {}
    )
    api_fixed_contract = api_schema.get(
        "x-deeplus-fixed-operator-conformance-contract", {}
    )
    check(
        frontend_contract.get("typed_hir_residue", {}).get("required_fields")
        == FIXED_OPERATOR_HIR_REQUIRED_FIELDS
        and mir_fixed_schema.get("required")
        == FIXED_OPERATOR_SCHEMA_REQUIRED_FIELDS
        and api_fixed_schema.get("required")
        == FIXED_OPERATOR_SCHEMA_REQUIRED_FIELDS
        and mir_fixed_contract.get("schema_stage") == "MIR"
        and api_fixed_contract.get("schema_stage") == "MODULE_API"
        and mir_fixed_contract.get("hir_to_schema_field_map")
        == FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP
        and api_fixed_contract.get("hir_to_schema_field_map")
        == FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP
        and mir_fixed_contract.get("schema_stage_constant_fields")
        == FIXED_OPERATOR_SCHEMA_STAGE_CONSTANT_FIELDS
        and api_fixed_contract.get("schema_stage_constant_fields")
        == FIXED_OPERATOR_SCHEMA_STAGE_CONSTANT_FIELDS
        and mir_fixed_contract.get("field_mapping")
        == api_fixed_contract.get("field_mapping")
        == "TOTAL_INJECTIVE_DETERMINISTIC"
        and len(set(FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP.values()))
        == len(FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP)
        and set(FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP)
        == set(FIXED_OPERATOR_HIR_REQUIRED_FIELDS)
        and (
            set(FIXED_OPERATOR_HIR_TO_SCHEMA_FIELD_MAP.values())
            | set(FIXED_OPERATOR_SCHEMA_STAGE_CONSTANT_FIELDS)
        )
        == set(FIXED_OPERATOR_SCHEMA_REQUIRED_FIELDS),
        "FIXED_OPERATOR_HIR_MIR_API_FIELD_MAP_EXACT_BINDING",
        (
            f"hir={frontend_contract.get('typed_hir_residue', {}).get('required_fields')} "
            f"mir={mir_fixed_schema.get('required')} "
            f"api={api_fixed_schema.get('required')}"
        ),
    )
    expected_schema_role_rows = {}
    for (
        operator_id, _glyph, fixity, _trait_id, method_id, _result,
        _value_projection, _frontend_projection,
    ) in FIXED_OPERATOR_MAPPING:
        is_comparison = operator_id in FIXED_OPERATOR_COMPARISON_IDS
        properties = {
            "operand_arity": {"const": 1 if fixity == "prefix" else 2},
            "normalized_right_type_id": (
                {"const": None}
                if fixity == "prefix"
                else {"type": "string", "minLength": 1}
            ),
            "method_id": {"const": method_id},
            "responsibility_profile_id": {
                "const": (
                    FIXED_OPERATOR_COMPARISON_PROFILE_ID
                    if is_comparison
                    else FIXED_OPERATOR_ARITHMETIC_PROFILE_ID
                )
            },
        }
        if is_comparison:
            properties["output_type_id"] = {"const": "Bool"}
        expected_schema_role_rows[operator_id] = properties
    mir_schema_role_rows = fixed_operator_schema_role_rows(mir_fixed_schema)
    api_schema_role_rows = fixed_operator_schema_role_rows(api_fixed_schema)
    check(
        list(mir_schema_role_rows) == FIXED_OPERATOR_IDS
        and list(api_schema_role_rows) == FIXED_OPERATOR_IDS
        and mir_schema_role_rows == expected_schema_role_rows
        and api_schema_role_rows == expected_schema_role_rows
        and mir_fixed_contract.get("operator_role_binding")
        == api_fixed_contract.get("operator_role_binding")
        == "EXACT_13_IF_THEN_ROWS",
        "FIXED_OPERATOR_MIR_API_SCHEMA_ROLE_IF_THEN_BINDING",
        (
            f"expected={len(expected_schema_role_rows)} "
            f"mir={len(mir_schema_role_rows)} api={len(api_schema_role_rows)}"
        ),
    )
    voi_new_diagnostics = [
        row.get("diagnostic_id")
        for row in voi_contract.get("new_rejection_diagnostic_matrix", [])
        if isinstance(row, dict)
    ]
    expected_voi_diagnostics = [
        "OPERATOR_CONFORMANCE_MISSING",
        "OPERATOR_CONFORMANCE_AMBIGUOUS",
        "OPERATOR_CONFORMANCE_INTRINSIC_DOMAIN_RESERVED",
        "OPERATOR_CONFORMANCE_LEFT_OWNER_REQUIRED",
        "OPERATOR_CONFORMANCE_EVIDENCE_ROUTE_NOT_ADMITTED",
        "OPERATOR_CONFORMANCE_RESPONSIBILITY_MISMATCH",
        "RETURN_TYPE_DIRECTED_OPERATOR_RESOLUTION_FORBIDDEN",
        "OPERATOR_CONFORMANCE_REQUIRES_EXPLICIT_CONVERSION",
        "OPERATOR_NOT_CONFORMANCE_OVERLOADABLE",
        "INDEX_SUFFIX_REQUIRES_AXIS",
        "BITWISE_OPERATOR_MIXED_DOMAIN_REQUIRES_EXPLICIT_CONVERSION",
    ]
    check(
        voi_contract.get("revision") == revision
        and voi_contract.get("semantic_p0") == 0
        and voi_contract.get("current_binding") is False
        and voi_contract.get("product_lanes") == "15/15_NOT_RUN"
        and voi_contract.get("open_feature_p1", {}).get("total") == 22
        and voi_machine.get("rule_count") == 12
        and voi_machine.get("literal_domain_row_count")
        == len(voi_contract.get("literal_domain_matrix", [])) == 12
        and voi_machine.get("expression_precedence_row_count")
        == len(voi_contract.get("expression_operator_precedence_matrix", [])) == 19
        and voi_machine.get("index_carrier_row_count")
        == len(voi_contract.get("index_carrier_matrix", [])) == 10
        and voi_machine.get("slice_form_row_count")
        == len(voi_contract.get("slice_form_matrix", [])) == 8
        and voi_machine.get("operator_dispatch_mode")
        == "INTRINSIC_RESERVED_OR_STABLE_FIXED_CONFORMANCE"
        and voi_machine.get("custom_operator_current_count") == 0
        and voi_machine.get("fixed_operator_conformance_overloading_current_count") == 1
        and voi_machine.get("fixed_operator_stable_profile_count") == 1
        and voi_machine.get("fixed_operator_stable_operator_count")
        == len(FIXED_OPERATOR_IDS) == 13
        and voi_machine.get("fixed_operator_trait_root_count")
        == len(FIXED_OPERATOR_TRAIT_ROOTS) == 9
        and voi_machine.get("fixed_operator_derived_comparison_projection_count")
        == 5
        and voi_machine.get("fixed_operator_independent_compound_assignment_hook_count")
        == 0
        and voi_machine.get("fixed_operator_range_hook_count") == 0
        and voi_by_id.get("VOI-R1-POS-022", {}).get("assertions", {}).get(
            "admitted_operator_ids"
        ) == FIXED_OPERATOR_IDS
        and voi_by_id.get("VOI-R1-POS-022", {}).get("assertions", {}).get(
            "trait_roots"
        ) == FIXED_OPERATOR_TRAIT_ROOTS
        and voi_fixed_profile.get("responsibility_profile")
        == FIXED_OPERATOR_ARITHMETIC_PROFILE_ID
        and voi_by_id.get("VOI-R1-POS-022", {}).get("assertions", {}).get(
            "responsibility_profile"
        ) == FIXED_OPERATOR_ARITHMETIC_PROFILE_ID
        and voi_by_id.get("VOI-R1-BND-004", {}).get("assertions", {}).get(
            "Ord_zero_equals_Eq"
        ) is True
        and voi_by_id.get("VOI-R1-BND-006", {}).get("assertions", {}).get(
            "independent_compound_assignment_conformance_hook_count"
        ) == 0
        and voi_machine.get(
            "trait_operator_lookup_max_per_nonintrinsic_admitted_expression"
        )
        == 1
        and voi_machine.get("structural_bracket_activation_count") == 0
        and voi_machine.get("ordinary_sequence_first_index") == 1
        and voi_machine.get("negative_from_end_rewrite_count") == 0
        and voi_machine.get("implicit_rebase_count") == 0
        and voi_machine.get("product_execution_receipt_count") == 0
        and voi_machine.get("new_rejection_diagnostic_count")
        == len(voi_new_diagnostics) == 11
        and voi_new_diagnostics == expected_voi_diagnostics
        and set(voi_new_diagnostics).issubset(set(diagnostic_by_id)),
        "VOI_CONTRACT_MACHINE_ACCEPTANCE",
        f"machine={voi_machine} diagnostics={voi_new_diagnostics}",
    )
    voi_remainder_boundary = voi_by_id.get("VOI-R1-BND-018", {})
    voi_remainder_assertions = voi_remainder_boundary.get("assertions", {})
    check(
        voi_remainder_boundary.get("subject_profile")
        == "RATIONAL_TRUNCATING_REMAINDER_SIGN_IDENTITY_AND_PRECOMMIT_ZERO_DIVISOR"
        and voi_remainder_assertions.get("operator_id") == "BinaryRemainder"
        and voi_remainder_assertions.get("method_id") == "Remainder.remainder"
        and voi_remainder_assertions.get(
            "negative_dividend_quotient_toward_zero"
        )
        == -3
        and voi_remainder_assertions.get("negative_dividend_remainder")
        == "-1/3"
        and voi_remainder_assertions.get(
            "negative_divisor_quotient_toward_zero"
        )
        == -3
        and voi_remainder_assertions.get("negative_divisor_remainder")
        == "1/3"
        and voi_remainder_assertions.get(
            "identity_a_equals_q_times_b_plus_r"
        )
        is True
        and voi_remainder_assertions.get(
            "absolute_remainder_less_than_absolute_divisor"
        )
        is True
        and voi_remainder_assertions.get("zero_divisor_terminal")
        == "ArithmeticDefect::divisionByZero"
        and voi_remainder_assertions.get("target_place_evaluation_count") == 1
        and voi_remainder_assertions.get("rhs_evaluation_count") == 1
        and voi_remainder_assertions.get("commit_count_on_zero_divisor") == 0
        and voi_remainder_assertions.get("original_value_preserved") is True,
        "VOI_RATIONAL_REMAINDER_SIGN_IDENTITY_PRECOMMIT_BINDING",
        str(voi_remainder_assertions),
    )
    voi_example_ids = {
        *(f"EX-R51VOI-{index:03d}" for index in range(1, 10)),
    }
    warning_example = active_by_id.get("EX-R51VOI-009", {})
    check(
        voi_example_ids.issubset(active_ids)
        and warning_example.get("expected_outcome") == "accept"
        and warning_example.get("expected_warnings")
        == ["SLICE_HALF_OPEN_RANGE_NONCANONICAL"],
        "VOI_EXAMPLE_AND_WARNING_BINDING",
        f"missing={sorted(voi_example_ids - active_ids)} warning={warning_example.get('expected_warnings')}",
    )

    trn_rel = "tests/fixtures/current/type-refinement-narrowing-coherence-r1.json"
    trn = parsed.get(root / trn_rel, {})
    trn_contract = parsed.get(root / "spec/contracts/type-refinement-narrowing-coherence.json", {})
    trn_rows = [row for row in trn.get("cases", []) if isinstance(row, dict)]
    trn_ids = [row.get("fixture_id") for row in trn_rows]
    trn_rule_ids = [
        row.get("rule_id") for row in trn_contract.get("rules", []) if isinstance(row, dict)
    ]
    trn_counts = trn.get("expected_counts", {})
    trn_admit = sum(row.get("expected") == "ADMIT" for row in trn_rows)
    trn_reject = sum(row.get("expected") == "REJECT" for row in trn_rows)
    check(
        trn.get("revision") == revision
        and trn_contract.get("revision") == revision
        and trn_contract.get("semantic_p0") == 0
        and trn_contract.get("current_binding") is False
        and trn_contract.get("product_lanes") == "15/15_NOT_RUN"
        and trn_contract.get("open_feature_p1", {}).get("total") == 22
        and trn_rule_ids == [f"TRN-R{index:03d}" for index in range(1, 16)]
        and len(trn_rows) == len(trn_ids) == len(set(trn_ids)) == trn_counts.get("cases") == 58
        and trn_admit == trn_counts.get("admit") == 24
        and trn_reject == trn_counts.get("reject") == 34
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(trn_rule_ids))
            and row.get("commit_count") in {0, 1}
            and (row.get("expected") == "ADMIT") == (row.get("diagnostic_or_null") is None)
            for row in trn_rows
        )
        and len(trn.get("open_feature_p1", [])) == 22
        and len(trn.get("product_lanes", {})) == 15
        and set(trn.get("product_lanes", {}).values()) == {"NOT_RUN"}
        and trn_counts.get("runtime_union_pattern_tests") == 2
        and trn_counts.get("closed_union_expression_tests") == 5
        and trn_counts.get("open_runtime_type_tests") == 0
        and trn_counts.get("def_guard_narrowing_facts") == 3
        and trn_counts.get("refinement_shorthand_cases") == 7
        and trn_counts.get("chained_binder_pattern_cases") == 6
        and trn_counts.get("mixed_strictness_cases") == 2
        and trn_counts.get("generic_close_cases") == 1
        and trn_counts.get("runtime_bound_rejections") == 2
        and trn_counts.get("overlap_exhaustiveness_boundaries") == 1
        and trn_counts.get("p1_closed") == 0
        and trn_counts.get("p1_created") == 0,
        "TRN_CONTRACT_FIXTURE_CLOSURE",
        f"rules={trn_rule_ids} rows={len(trn_rows)} admit={trn_admit} reject={trn_reject} counts={trn_counts}",
    )

    edc_rel = "tests/fixtures/current/enum-derived-capabilities-r1.json"
    edc = parsed.get(root / edc_rel, {})
    edc_contract = parsed.get(
        root / "spec/contracts/enum-derived-capabilities.json", {}
    )
    edc_rows = [row for row in edc.get("cases", []) if isinstance(row, dict)]
    edc_ids = [row.get("fixture_id") for row in edc_rows]
    edc_rule_ids = [
        row.get("rule_id")
        for row in edc_contract.get("rules", [])
        if isinstance(row, dict)
    ]
    edc_counts = edc.get("expected_counts", {})
    edc_expected_p1 = [
        *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
        *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
        *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
        "SFD-P1-009",
    ]
    edc_feature_ids = {
        "enum_declaration_order_ord_preview_design",
        "enum_case_display_mapping_preview_design",
        "enum_exact_variant_subset_alias_preview_design",
    }
    edc_features = [feature_by_id.get(feature_id, {}) for feature_id in edc_feature_ids]
    edc_frontend = parsed.get(root / "spec/frontend/frontend-model.json", {}).get(
        "stable_design_surfaces_current", {}
    )
    edc_frontend_ids = {
        "enum_declaration_order_ord",
        "enum_case_display_mapping",
        "enum_exact_variant_subset_alias",
    }
    edc_pc10_lanes = [
        "source", "resolution", "behavior", "serialization",
        "runtime_layout", "foreign_ABI", "tooling_reflection", "product",
    ]
    edc_serialized = json.dumps(edc_contract, ensure_ascii=False)
    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    check(
        edc.get("revision") == revision
        and edc_contract.get("revision") == revision
        and edc_contract.get("semantic_p0") == 0
        and edc_contract.get("current_binding") is True
        and edc_contract.get("source_activation") == "none"
        and edc_contract.get("product_lanes") == "15/15_NOT_RUN"
        and edc_contract.get("open_feature_p1", {}).get("total") == 22
        and edc_contract.get("compatibility_lanes") == edc_pc10_lanes
        and edc_contract.get("compatibility_lane_subrecords") == {
            "resolution": ["subset_membership", "variant_owner_widening"],
            "behavior": ["order_behavior", "display_behavior"],
            "serialization": ["raw_identity"],
        }
        and "overall_pass" not in edc_serialized
        and "sibling_status_propagation" not in edc_serialized
        and edc_contract.get("trait_contracts", {}).get("Eq<Rhs>", {}).get(
            "canonical_signature"
        ) == "public trait Eq<Rhs> { +def equals.(borrow rhs: Rhs) -> Bool throws Never effects {}; }"
        and edc_contract.get("trait_contracts", {}).get("Ord<Rhs>", {}).get(
            "canonical_signature"
        ) == "public trait Ord<Rhs>\nderives Eq<Rhs> {\n    +def compare.(borrow rhs: Rhs) -> Int throws Never effects {}\n}"
        and edc_contract.get("machine_acceptance", {}).get(
            "operator_glyph_activation_count"
        ) == 6
        and edc_contract.get("machine_acceptance", {}).get(
            "semantic_ascending_range_activation_count"
        ) == 1
        and edc_contract.get("machine_acceptance", {}).get(
            "range_operator_conformance_hook_count"
        ) == 0
        and edc_contract.get("trait_contracts", {}).get("Display", {}).get(
            "canonical_signature"
        ) == "public trait Display { +def display.() -> String throws Never effects {}; }"
        and edc.get("open_feature_p1") == edc_expected_p1
        and edc_rule_ids == [f"EDC-R{index:03d}" for index in range(1, 19)]
        and len(edc_rows) == len(edc_ids) == len(set(edc_ids)) == 35
        and sum(row.get("expected_design") == "ADMIT" for row in edc_rows)
        == edc_counts.get("design_admit") == 15
        and sum(row.get("expected_design") == "REJECT" for row in edc_rows)
        == edc_counts.get("design_reject") == 15
        and sum(row.get("expected_design") == "BOUNDARY" for row in edc_rows)
        == edc_counts.get("boundary") == 5
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(edc_rule_ids))
            and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in edc_rows
        )
        and set(edc_rule_ids)
        == {rule_id for row in edc_rows for rule_id in row.get("rule_ids", [])}
        and len(edc.get("product_lanes", {})) == 15
        and set(edc.get("product_lanes", {}).values()) == {"NOT_RUN"}
        and edc_counts.get("current_source_activated") == 0
        and edc_counts.get("p1_closed") == 0
        and edc_counts.get("p1_created") == 0
        and edc_counts.get("product_executed") == 0,
        "EDC_CONTRACT_FIXTURE_CLOSURE",
        f"rules={edc_rule_ids} rows={len(edc_rows)} counts={edc_counts}",
    )
    edc_by_id = {row.get("fixture_id"): row for row in edc_rows}
    check(
        edc_by_id.get("EDC-R1-POS-001", {}).get("source")
        == "enum#increasing Stage { queued, running, done }"
        and edc_by_id.get("EDC-R1-POS-001", {}).get("assertions")
        == [
            "queued<running<done",
            "queued..done=semantic_ascending",
            "one_whole_enum_eq_witness",
            "one_whole_enum_ord_witness",
        ]
        and edc_by_id.get("EDC-R1-POS-002", {}).get("source")
        == "enum#decreasing Severity { critical, warning, info }"
        and edc_by_id.get("EDC-R1-POS-002", {}).get("assertions")
        == [
            "critical>warning>info",
            "info..critical=semantic_ascending",
            "declaration_direction_reversed_for_range",
            "one_direction",
        ]
        and edc_by_id.get("EDC-R1-POS-003", {}).get("assertions")
        == ["compare(x,x)==0", "no_tooling_advice"]
        and edc_by_id.get("EDC-R1-POS-004", {}).get("assertions")
        == ["sign_matrix_total", "transitive"]
        and edc_by_id.get("EDC-R1-NEG-017", {}).get("assertions")
        == ["no_payload_ord_synthesis"]
        and edc_by_id.get("EDC-R1-NEG-018", {}).get("assertions")
        == ["no_conditional_synthesis"]
        and edc_by_id.get("EDC-R1-NEG-019", {}).get("assertions")
        == [
            "no_source_order_priority",
            "no_specialization",
            "no_partial_pair_override",
        ]
        and grammar.count(
            'EnumOrderRole ::= "#" ("increasing" | "decreasing") ;'
        ) == 1
        and edc_contract.get("authority_fence", {}).get(
            "semantic_ascending_range_activation"
        ) is True
        and edc_contract.get("authority_fence", {}).get(
            "range_operator_conformance_hook"
        ) is False,
        "EDC_EQ_ORD_SEMANTIC_RANGE_ASSERTIONS_EXACT_BINDING",
        "ordered Enum Eq/Ord/range fixtures and grammar are exact",
    )
    check(
        all(
            feature.get("status_enum") == "STABLE_DESIGN"
            and feature.get("source_activation") == "none"
            and feature.get("product_support") == "NOT_RUN"
            and feature.get("production_lexer") == "NOT_RUN"
            and feature.get("production_parser") == "NOT_RUN"
            and feature.get("integrated_checker") == "NOT_RUN"
            and feature.get("runtime_xvm") == "NOT_RUN"
            and feature.get("artifact_trace_refs")
            == ["spec/contracts/enum-derived-capabilities.json"]
            and bool(feature.get("normative_trace_refs", {}).get("productions"))
            for feature in edc_features
        )
        and all(
            edc_frontend.get(feature_id, {}).get("status") == "STABLE_DESIGN"
            and edc_frontend.get(feature_id, {}).get("product_support")
            == "NOT_RUN"
            and bool(edc_frontend.get(feature_id, {}).get("grammar_owner"))
            for feature_id in edc_frontend_ids
        )
        and '"increasing" | "decreasing"' in grammar
        and 'EnumCaseDisplayMapping ::= "~>" RestrictedEnumDisplayTemplate ;'
        in grammar
        and 'EnumVariantSubsetAliasDecl ::= "+" "type" Identifier' in grammar,
        "EDC_STABLE_DESIGN_FEATURE_FENCE",
        f"features={sorted(edc_feature_ids)} frontend={sorted(edc_frontend_ids)}",
    )

    lstc = parsed.get(
        root / "tests/fixtures/current/literal-shaped-collection-design-r1.json",
        {},
    )
    lstc_contract = parsed.get(
        root / "spec/contracts/literal-shaped-collection-design.json", {}
    )
    lstc_rows = [row for row in lstc.get("cases", []) if isinstance(row, dict)]
    lstc_ids = [row.get("fixture_id") for row in lstc_rows]
    lstc_rule_ids = [
        row.get("rule_id")
        for row in lstc_contract.get("rules", [])
        if isinstance(row, dict)
    ]
    lstc_counts = lstc.get("expected_counts", {})
    lstc_expected_p1 = [
        *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
        *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
        *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
        "SFD-P1-009",
    ]
    lstc_feature_ids = {
        "literal_shaped_collection_type_surface_preview_design",
        "literal_shaped_closed_record_type_surface_preview_design",
        "immutable_first_collection_ownership_preview_design",
        "freeze_snapshot_view_responsibility_preview_design",
    }
    lstc_features = [
        feature_by_id.get(feature_id, {}) for feature_id in lstc_feature_ids
    ]
    lstc_frontend = parsed.get(
        root / "spec/frontend/frontend-model.json", {}
    ).get("preview_design_nonactivatable", {})
    lstc_frontend_ids = {
        "literal_shaped_list_type_surface",
        "literal_shaped_set_map_type_surface",
        "literal_shaped_closed_record_type_surface",
        "immutable_first_collection_ownership",
        "freeze_snapshot_view_successor",
    }
    lstc_serialized = json.dumps(lstc_contract, ensure_ascii=False)
    check(
        lstc.get("revision") == revision
        and lstc_contract.get("revision") == revision
        and lstc_contract.get("semantic_p0") == 0
        and lstc_contract.get("current_binding") is False
        and lstc_contract.get("source_activation") == "nonactivatable"
        and lstc_contract.get("product_lanes") == "15/15_NOT_RUN"
        and lstc_contract.get("open_feature_p1", {}).get("total") == 22
        and lstc.get("open_feature_p1") == lstc_expected_p1
        and lstc_rule_ids == [f"LSTC-R{index:03d}" for index in range(1, 17)]
        and len(lstc_rows) == len(lstc_ids) == len(set(lstc_ids)) == 30
        and sum(row.get("expected_design") == "ADMIT" for row in lstc_rows)
        == lstc_counts.get("design_admit") == 12
        and sum(row.get("expected_design") == "REJECT" for row in lstc_rows)
        == lstc_counts.get("design_reject") == 12
        and sum(row.get("expected_design") == "BOUNDARY" for row in lstc_rows)
        == lstc_counts.get("boundary") == 6
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(lstc_rule_ids))
            and row.get("current_source_outcome")
            == "NONACTIVATABLE_NOT_CURRENT"
            and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in lstc_rows
        )
        and set(lstc_rule_ids)
        == {
            rule_id
            for row in lstc_rows
            for rule_id in row.get("rule_ids", [])
        }
        and len(lstc.get("product_lanes", {})) == 15
        and set(lstc.get("product_lanes", {}).values()) == {"NOT_RUN"}
        and lstc_counts.get("current_source_activated") == 0
        and lstc_counts.get("p1_closed") == 0
        and lstc_counts.get("p1_created") == 0
        and lstc_counts.get("product_executed") == 0
        and lstc_contract.get("machine_acceptance", {}).get(
            "current_identity_rewrite_count"
        )
        == 0
        and lstc_contract.get("machine_acceptance", {}).get(
            "implicit_shareability_proof_count"
        )
        == 0
        and lstc_contract.get("machine_acceptance", {}).get(
            "sequence_operation_activation_count"
        )
        == 0
        and lstc_contract.get("machine_acceptance", {}).get(
            "final_diagnostic_id_count"
        )
        == 0
        and "overall_pass" not in lstc_serialized,
        "LSTC_CONTRACT_FIXTURE_CLOSURE",
        f"rules={lstc_rule_ids} rows={len(lstc_rows)} counts={lstc_counts}",
    )
    check(
        all(
            feature.get("status_enum") == "PREVIEW_DESIGN"
            and feature.get("source_activation") == "nonactivatable"
            and feature.get("product_support") == "NOT_RUN"
            and feature.get("production_lexer") == "NOT_RUN"
            and feature.get("production_parser") == "NOT_RUN"
            and feature.get("integrated_checker") == "NOT_RUN"
            and feature.get("runtime_xvm") == "NOT_RUN"
            and feature.get("artifact_trace_refs")
            == ["spec/contracts/literal-shaped-collection-design.json"]
            and feature.get("normative_trace_refs", {}).get("productions") == []
            for feature in lstc_features
        )
        and all(
            lstc_frontend.get(feature_id, {}).get("parser_cover_grammar") is False
            and lstc_frontend.get(feature_id, {}).get("source_activation")
            == "nonactivatable"
            for feature_id in lstc_frontend_ids
        )
        and 'TypePrimary ::= "[" TypeRef "]"' not in grammar
        and '"#mut["' not in grammar
        and '"#set{"' not in grammar
        and '"#map{"' not in grammar
        and '"${" RecordType' not in grammar,
        "LSTC_NONACTIVATABLE_FEATURE_FENCE",
        f"features={sorted(lstc_feature_ids)} frontend={sorted(lstc_frontend_ids)}",
    )
    lstc_prelude_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-prelude-signature-catalog.json",
        "entries",
    )
    current_prelude = {
        row.get("symbol"): row
        for row in lstc_prelude_rows
        if isinstance(row, dict)
    }
    check(
        current_prelude.get("MutableList<T>", {}).get("signatures")
        == [
            "prelude intrinsic mutable resource type MutableList<T>",
            "prelude intrinsic def MutableList::snapshot<T>(borrow self: MutableList<T>) -> ListSnapshot<T> throws AllocationError effects allocate",
            "prelude intrinsic def#consume MutableList::freeze<T>(move self: MutableList<T>) -> FrozenList<T> throws AllocationError effects allocate",
        ]
        and "MutableMap<K,V>" not in current_prelude
        and "MutableSet<T>" not in current_prelude
        and "StringBuilder" not in current_prelude
        and "ByteBuffer" not in current_prelude,
        "LSTC_CURRENT_PRELUDE_IDENTITY_FENCE",
        f"entries={len(current_prelude)}",
    )
    trn_case_by_id = {row.get("fixture_id"): row for row in trn_rows}
    trn_required_axes = {f"TRN-R1-{kind}-{index:03d}" for kind, index in (
        [("NEG", value) for value in range(19, 30)] + [("POS", 30), ("POS", 31)]
    )}
    check(
        trn_required_axes <= set(trn_case_by_id)
        and all(trn_case_by_id[fixture_id].get("commit_count") == 0 for fixture_id in trn_required_axes)
        and all(
            trn_case_by_id[f"TRN-R1-NEG-{index:03d}"].get("diagnostic_or_null")
            == "ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH"
            for index in range(19, 24)
        )
        and all(
            trn_case_by_id[f"TRN-R1-NEG-{index:03d}"].get("diagnostic_or_null")
            == "OR_PATTERN_BINDINGS_INCONSISTENT"
            for index in range(24, 30)
        ),
        "TRN_ENUM_OR_PATTERN_AND_TRANSACTION_AXES",
        f"required={len(trn_required_axes & set(trn_case_by_id))}/13",
    )
    trn_bounded_expected = {
        "TRN-R1-POS-054": None,
        "TRN-R1-POS-055": None,
        "TRN-R1-NEG-056": "REFINEMENT_RANGE_BOUND_STATIC_INT_REQUIRED",
        "TRN-R1-BOUND-057": None,
        "TRN-R1-NEG-058": "PATTERN_PIN_VALUE_NOT_STABLE",
    }
    trn_surface = trn_contract.get("refinement_surface", {})
    trn_binder = trn_contract.get("chained_binder_pattern", {})
    trn_frontend = parsed.get(root / "spec/frontend/frontend-model.json", {}).get(
        "refinement_and_bounded_binder_frontend_contract", {}
    )
    check(
        trn_bounded_expected.keys() <= trn_case_by_id.keys()
        and all(
            trn_case_by_id[fixture_id].get("diagnostic_or_null") == diagnostic
            for fixture_id, diagnostic in trn_bounded_expected.items()
        )
        and trn_surface.get("implicit_this_rhs_parse_goal")
        == "RefinementComparisonOperand"
        and trn_surface.get("implicit_this_rhs_is_full_predicate") is False
        and trn_surface.get("bare_relational_type_suffix_admitted") is False
        and trn_binder.get("subject_evaluation_count") == 1
        and trn_binder.get("mixed_direction_admitted") is False
        and "source order" in trn_binder.get("bound_evaluation_order", "")
        and trn_frontend.get("implicit_this", {}).get("full_predicate_rhs") is False
        and trn_frontend.get("bounded_binder_pattern", {}).get(
            "scrutinee_evaluation_count"
        ) == 1
        and trn_frontend.get("bounded_binder_pattern", {}).get(
            "hidden_guard"
        ) is False,
        "TRN_REFINEMENT_BOUNDED_BINDER_EXACT_AXES",
        f"fixtures={sorted(trn_bounded_expected.keys() & trn_case_by_id.keys())} surface={trn_surface.get('implicit_this_rhs_parse_goal')}",
    )
    refinement_grammar_productions = [
        'RefinementSuffix ::= RefinementClause | IntervalRefinementClause ;',
        'RefinementClause ::= "where" (PredicateExpr | ImplicitThisPredicate) ;',
        'ImplicitThisPredicate ::= OrderedComparisonOperator RefinementComparisonOperand ;',
        'RefinementComparisonOperand ::= Literal | Identifier | QualifiedStaticExpr ;',
        'IntervalRefinementClause ::= "in" RefinementBound (".." | "..<") RefinementBound ;',
        'MatchArm ::= MatchHead GuardClause? "=>" MatchArmBodySlot ;',
        'MatchHead ::= BoundedBinderPattern | Pattern | "otherwise" ;',
        (
            "BoundedBinderPattern ::= PatternBound OrderedComparisonOperator Identifier\n"
            "                         OrderedComparisonOperator PatternBound ;"
        ),
    ]
    refinement_case_sha256 = {
        fixture_id: canonical_sha(trn_case_by_id.get(fixture_id, {}))
        for fixture_id in REFINEMENT_SURFACE_CASE_SHA256
    }
    check(
        all(grammar.count(production) == 1 for production in refinement_grammar_productions)
        and refinement_case_sha256 == REFINEMENT_SURFACE_CASE_SHA256,
        "TRN_GRAMMAR_AND_SURFACE_FIXTURE_ASSERTIONS_EXACT_BINDING",
        (
            f"grammar={sum(grammar.count(row) == 1 for row in refinement_grammar_productions)}/"
            f"{len(refinement_grammar_productions)} "
            f"fixtures={sum(refinement_case_sha256.get(key) == value for key, value in REFINEMENT_SURFACE_CASE_SHA256.items())}/"
            f"{len(REFINEMENT_SURFACE_CASE_SHA256)}"
        ),
    )
    pattern_kinds = parsed.get(root / "spec/patterns/pattern-kinds.json", {})
    pattern_lowering = parsed.get(root / "spec/patterns/pattern-lowering.json", {})
    union_kind = next(
        (row for row in pattern_kinds.get("rows", []) if row.get("pattern_kind_id") == "PK-UNION-ALTERNATIVE-BINDER"),
        {},
    )
    union_lowering = next(
        (row for row in pattern_lowering.get("rows", []) if row.get("lowering_id") == "PL-UNION-ALTERNATIVE-BINDER"),
        {},
    )
    bounded_kind = next(
        (row for row in pattern_kinds.get("rows", []) if row.get("pattern_kind_id") == "PK-BOUNDED-BINDER"),
        {},
    )
    bounded_lowering = next(
        (row for row in pattern_lowering.get("rows", []) if row.get("lowering_id") == "PL-BOUNDED-BINDER"),
        {},
    )
    pattern_policies = parsed.get(root / "spec/patterns/pattern-context-policies.json", {})
    expected_union_contexts = {
        "PCTX-ASSERTIVE-LET", "PCTX-ASSERTIVE-VAR", "PCTX-GUARDED-LET",
        "PCTX-IF-LET", "PCTX-WHILE-LET", "PCTX-PATTERN-CONDITION-CHAIN",
        "PCTX-FOR-LET", "PCTX-ASYNC-FOR-LET", "PCTX-STATEMENT-MATCH",
        "PCTX-VALUE-MATCH", "PCTX-DECLARATIVE-CLAUSE", "PCTX-CATCH",
        "PCTX-VALUE-CATCH", "PCTX-COMPREHENSION-IF-LET",
    }
    policy_union_contexts = {
        row.get("context_id")
        for row in pattern_policies.get("rows", [])
        if "PK-UNION-ALTERNATIVE-BINDER" in row.get("allowed_pattern_kind_ids", [])
    }
    policy_bounded_contexts = {
        row.get("context_id")
        for row in pattern_policies.get("rows", [])
        if "PK-BOUNDED-BINDER" in row.get("allowed_pattern_kind_ids", [])
    }
    check(
        pattern_kinds.get("counts", {}).get("rows") == len(pattern_kinds.get("rows", [])) == 40
        and pattern_lowering.get("counts", {}).get("rows") == len(pattern_lowering.get("rows", [])) == 40
        and pattern_kinds.get("revision") == PATTERN_COMPONENT_REVISION
        and pattern_lowering.get("revision") == PATTERN_COMPONENT_REVISION
        and pattern_policies.get("revision") == PATTERN_COMPONENT_REVISION
        and all(
            row.get("revision") == PATTERN_COMPONENT_REVISION
            for row in pattern_kinds.get("rows", [])
            + pattern_lowering.get("rows", [])
            + pattern_policies.get("rows", [])
        )
        and union_kind.get("normalized_variant") == "UnionAlternativeBindPattern"
        and union_kind.get("coverage_contribution") == "SUBJECT_CONSTRUCTOR_CELL"
        and set(union_kind.get("allowed_context_ids", [])) == expected_union_contexts
        and "PK-UNION-ALTERNATIVE-BINDER" in pattern_policies.get("current_pattern_kind_ids", [])
        and policy_union_contexts == expected_union_contexts
        and union_lowering.get("test_kind") == "UNION_INJECTION_TAG_TEST"
        and union_lowering.get("mir_disposition") == "TEST_PROBE_COMMIT_TRACE",
        "TRN_UNION_PATTERN_LOWERING_BINDING",
        f"kind={union_kind.get('normalized_variant')} contexts={sorted(policy_union_contexts)} lowering={union_lowering.get('test_kind')}",
    )
    check(
        bounded_kind.get("normalized_variant") == "BoundedBinderPattern"
        and bounded_kind.get("binder_contract") == "INTRODUCES_ONE"
        and bounded_kind.get("coverage_contribution") == "RANGE_INTERVAL_CELL"
        and set(bounded_kind.get("allowed_context_ids", []))
        == {"PCTX-STATEMENT-MATCH", "PCTX-VALUE-MATCH"}
        and "PK-BOUNDED-BINDER" in pattern_policies.get("current_pattern_kind_ids", [])
        and policy_bounded_contexts
        == {"PCTX-STATEMENT-MATCH", "PCTX-VALUE-MATCH"}
        and bounded_lowering.get("test_kind")
        == "MONOTONE_ORDERED_INTERVAL_BIND_TEST"
        and bounded_lowering.get("mir_disposition")
        == "TEST_PROBE_COMMIT_TRACE",
        "TRN_BOUNDED_BINDER_PATTERN_LOWERING_BINDING",
        f"kind={bounded_kind.get('normalized_variant')} contexts={sorted(policy_bounded_contexts)} lowering={bounded_lowering.get('test_kind')}",
    )
    trn_predicate_ids = {
        "NarrowUnionByPattern", "NormalizeUnion", "MatchExhaustive",
        "GuardPredicateAdmitted", "R0GuardSafe", "RefinementCheckBoundaryAdmitted",
    }
    trn_inputs = [
        row for row in trn_contract.get("predicate_inputs", [])
        if isinstance(row, dict) and row.get("predicate_id") in trn_predicate_ids
    ]
    trn_input_ids = [row.get("fixture_id") for row in trn_inputs]
    trn_input_groups = {
        predicate_id: [row for row in trn_inputs if row.get("predicate_id") == predicate_id]
        for predicate_id in trn_predicate_ids
    }
    trn_predicate_rows = {
        row.get("predicate_id"): row
        for row in predicate_rows
        if row.get("predicate_id") in trn_predicate_ids
    }
    trn_schema_rel = "schemas/language/type-refinement-narrowing-coherence-descriptor.schema.json"
    descriptor_binding_ok = (
        len(trn_inputs) == len(trn_input_ids) == len(set(trn_input_ids)) == 12
        and all(
            len(rows) == 2
            and {row.get("expected") for row in rows} == {"admitted", "rejected"}
            for rows in trn_input_groups.values()
        )
        and set(trn_predicate_rows) == trn_predicate_ids
        and all(
            row.get("input_descriptor") == "TRNCoherenceDescriptor"
            and row.get("input_descriptor_schema") == trn_schema_rel
            for row in trn_predicate_rows.values()
        )
    )
    match_descriptors = [
        row.get("descriptor", {}) for row in trn_input_groups["MatchExhaustive"]
    ]
    union_descriptors = [
        row.get("descriptor", {}) for row in trn_input_groups["NormalizeUnion"]
    ]
    match_binding_ok = all(
        descriptor.get("arms")
        and len(descriptor.get("arms", [])) == len(descriptor.get("arm_order", []))
        and all(
            {"arm_id", "kind", "coverage_cells", "guard_origin", "binder_contract", "entry_place_state", "exit_place_state"}
            <= set(arm)
            for arm in descriptor.get("arms", [])
        )
        for descriptor in match_descriptors
    )
    union_pair_binding_ok = all(
        len(descriptor.get("union_pairs", []))
        == len(descriptor.get("current_alternatives", [])) * (len(descriptor.get("current_alternatives", [])) - 1) // 2
        for descriptor in union_descriptors
    )
    check(
        descriptor_binding_ok and match_binding_ok and union_pair_binding_ok,
        "TRN_PREDICATE_DESCRIPTOR_BINDING",
        f"inputs={len(trn_inputs)} predicates={sorted(trn_predicate_rows)} match={match_binding_ok} pairs={union_pair_binding_ok}",
    )
    stored_guard = next(
        (row for row in trn_inputs if row.get("fixture_id") == "TRN-DESC-REFINE-NEG"), {}
    ).get("descriptor", {})
    as_option_case = next(
        (row for row in trn_rows if row.get("fixture_id") == "TRN-R1-POS-009"), {}
    )
    check(
        stored_guard.get("guard_origin") == "DEF_GUARD_STORED_BOOL"
        and stored_guard.get("proof_state") == "UNKNOWN"
        and stored_guard.get("commit_count") == 0
        and as_option_case.get("flow_in") == as_option_case.get("flow_join"),
        "TRN_STORED_GUARD_BOOL_AND_AS_OPTION_FLOW",
        f"guard={stored_guard.get('proof_state')} phi={as_option_case.get('flow_in')}->{as_option_case.get('flow_join')}",
    )

    module_fixtures = parsed.get(root / "tests/fixtures/imported/module-api-digest-fixtures.json", {})
    module_positive = module_fixtures.get("positive_fixtures", [])
    callable_rows = [
        symbol
        for fixture in module_positive
        for symbol in fixture.get("payload", {}).get("symbols", [])
        if symbol.get("kind") in {"function", "method"}
    ]
    callable_axis_ok = all(
        row.get("cancellation") in {"forbidden", "propagate", "observe", "shielded_cleanup"}
        and isinstance(row.get("suspends"), bool)
        and row.get("isolation") in {"local", "task", "actor", "global"}
        for row in callable_rows
    )
    callable_channel_ok = True
    for row in callable_rows:
        profile = row.get("responsibility_profile", {})
        channels = []
        if isinstance(profile.get("receiver"), dict):
            channels.append(profile["receiver"])
        channels.extend(profile.get("parameters", []))
        if isinstance(profile.get("result"), dict):
            channels.append(profile["result"])
        channels.extend(profile.get("captures", []))
        channel_ids = [channel.get("channel_id") for channel in channels]
        callable_channel_ok = callable_channel_ok and len(channel_ids) == len(set(channel_ids))
    module_negative_by_id = {
        row.get("fixture_id"): row for row in module_fixtures.get("negative_fixtures", [])
    }
    axis_negative = module_negative_by_id.get("MODULE-API-NEG-CALLABLE-AXES-001", {})
    axis_negative_function = next(
        (
            row for row in axis_negative.get("payload", {}).get("symbols", [])
            if row.get("kind") == "function"
        ),
        {},
    )
    channel_negative = module_negative_by_id.get("MODULE-API-NEG-CALLABLE-CHANNEL-ID-001", {})
    channel_negative_method = next(
        (
            row for row in channel_negative.get("payload", {}).get("symbols", [])
            if row.get("kind") == "method"
        ),
        {},
    )
    channel_negative_profile = channel_negative_method.get("responsibility_profile", {})
    channel_negative_rows = []
    if isinstance(channel_negative_profile.get("receiver"), dict):
        channel_negative_rows.append(channel_negative_profile["receiver"])
    channel_negative_rows.extend(channel_negative_profile.get("parameters", []))
    if isinstance(channel_negative_profile.get("result"), dict):
        channel_negative_rows.append(channel_negative_profile["result"])
    channel_negative_rows.extend(channel_negative_profile.get("captures", []))
    channel_negative_ids = [row.get("channel_id") for row in channel_negative_rows]
    check(callable_axis_ok, "MODULE_API_CALLABLE_AXES_CONCRETE", f"callables={len(callable_rows)}")
    check(callable_channel_ok, "MODULE_API_CALLABLE_CHANNEL_IDS_UNIQUE", f"callables={len(callable_rows)}")
    check(
        "MODULE_API_CALLABLE_RESPONSIBILITY_AXIS_NOT_APPLICABLE"
        in axis_negative.get("expected_errors", [])
        and all(
            axis_negative_function.get(axis) == "not_applicable"
            for axis in ("cancellation", "suspends", "isolation")
        )
        and "MODULE_API_CALLABLE_CHANNEL_ID_DUPLICATE"
        in channel_negative.get("expected_errors", [])
        and len(channel_negative_ids) > len(set(channel_negative_ids))
        and module_fixtures.get("negative_fixture_count")
        == len(module_fixtures.get("negative_fixtures", [])),
        "MODULE_API_CALLABLE_NEGATIVE_COVERAGE",
        f"negative={module_fixtures.get('negative_fixture_count')}",
    )

    actor_contract = parsed.get(
        root / "spec/contracts/actor-concurrency-coherence.json", {}
    )
    actor_fixtures = parsed.get(
        root / "tests/fixtures/current/actor-concurrency-coherence-r1.json", {}
    )
    actor_fixture_groups = {
        name: actor_fixtures.get(name, [])
        for name in ("positive", "negative", "boundary", "cross_module")
    }
    actor_fixture_counts = actor_fixtures.get("expected_counts", {})
    check(
        all(
            actor_fixture_counts.get(name) == len(rows)
            for name, rows in actor_fixture_groups.items()
        )
        and actor_fixture_counts.get("total")
        == sum(len(rows) for rows in actor_fixture_groups.values())
        and actor_fixture_counts.get("product_executed") == 0,
        "ACTOR_FIXTURE_COUNT_CLOSURE",
        str(actor_fixture_counts),
    )
    module_api_schema = parsed.get(
        root / "schemas/language/module-api-digest.schema.json", {}
    )
    mir_responsibility_schema = parsed.get(
        root / "schemas/language/mir-responsibility.schema.json", {}
    )
    responsibility_kinds = ["actor_request_reply", "concur_run"]
    reply_descriptor_fields = [
        "result_type",
        "normalized_handler_error_set",
        "cancellation_axis",
        "isolation_owner",
        "reply_id",
        "correlation_id",
        "terminal_transport_failure",
    ]
    reply_descriptor_field_set = set(reply_descriptor_fields)
    admission_only_errors = {
        "mailboxFull",
        "receiverClosedBeforeAdmission",
        "ActorMessageError::mailboxFull",
        "ActorMessageError::receiverClosedBeforeAdmission",
    }
    terminal_transport_failure = ["receiverClosedBeforeReply"]

    def reply_descriptor_is_normalized(
        descriptor: Any, *, module_api_marker: bool = False
    ) -> bool:
        if not isinstance(descriptor, dict):
            return False
        handler_errors = descriptor.get("normalized_handler_error_set")
        identity_fields_ok = all(
            isinstance(descriptor.get(field), str) and bool(descriptor.get(field))
            for field in (
                "result_type",
                "cancellation_axis",
                "isolation_owner",
                "reply_id",
                "correlation_id",
            )
        )
        if module_api_marker:
            identity_fields_ok = (
                identity_fields_ok
                and descriptor.get("reply_id") == "per_value_non_forgeable"
                and descriptor.get("correlation_id") == "per_value_non_forgeable"
            )
        return (
            set(descriptor) == reply_descriptor_field_set
            and identity_fields_ok
            and isinstance(handler_errors, list)
            and all(isinstance(error, str) and bool(error) for error in handler_errors)
            and handler_errors == sorted(set(handler_errors))
            and not admission_only_errors.intersection(handler_errors)
            and descriptor.get("terminal_transport_failure")
            == terminal_transport_failure
        )

    module_channel_schema = (
        module_api_schema.get("$defs", {}).get("responsibilityChannel", {})
    )
    module_reply_descriptor_schema = (
        module_api_schema.get("$defs", {}).get("replyResponsibilityDescriptor", {})
    )
    module_reply_type_rule = next(
        (
            row
            for row in module_channel_schema.get("allOf", [])
            if isinstance(row, dict)
            and "Reply<"
            in row.get("if", {})
            .get("properties", {})
            .get("type_identity", {})
            .get("pattern", "")
        ),
        {},
    )
    module_run_type_rule = next(
        (
            row
            for row in module_channel_schema.get("allOf", [])
            if isinstance(row, dict)
            and "Run<"
            in row.get("if", {})
            .get("properties", {})
            .get("type_identity", {})
            .get("pattern", "")
        ),
        {},
    )
    module_handler_schema = (
        module_reply_descriptor_schema.get("properties", {})
        .get("normalized_handler_error_set", {})
    )
    module_terminal_schema = (
        module_reply_descriptor_schema.get("properties", {})
        .get("terminal_transport_failure", {})
    )
    module_run_reply_contract = module_api_schema.get(
        "x-deeplus-run-reply-responsibility-contract", {}
    )
    actor_rule_by_id = {
        row.get("rule_id"): row
        for row in actor_contract.get("rules", [])
        if isinstance(row, dict)
    }
    actor_reply_contract = (
        actor_rule_by_id.get("ACC-R008", {})
        .get("contract", {})
        .get("reply_responsibility_descriptor", {})
    )
    actor_storage_contract = actor_reply_contract.get("storage_and_api_export", {})
    check(
        "task_origin" not in module_channel_schema.get("properties", {})
        and "task_responsibility" not in module_channel_schema.get("properties", {})
        and module_channel_schema.get("properties", {})
        .get("reply_responsibility", {})
        .get("$ref")
        == "#/$defs/replyResponsibilityDescriptor"
        and module_reply_descriptor_schema.get("additionalProperties") is False
        and module_reply_descriptor_schema.get("required") == reply_descriptor_fields
        and set(module_reply_descriptor_schema.get("properties", {}))
        == reply_descriptor_field_set
        and module_reply_descriptor_schema.get("properties", {})
        .get("reply_id", {})
        .get("const")
        == "per_value_non_forgeable"
        and module_reply_descriptor_schema.get("properties", {})
        .get("correlation_id", {})
        .get("const")
        == "per_value_non_forgeable"
        and set(
            module_handler_schema.get("items", {})
            .get("not", {})
            .get("enum", [])
        )
        == admission_only_errors
        and module_handler_schema.get("uniqueItems") is True
        and module_terminal_schema.get("items", {}).get("const")
        == terminal_transport_failure[0]
        and module_terminal_schema.get("minItems")
        == module_terminal_schema.get("maxItems")
        == 1
        and module_terminal_schema.get("uniqueItems") is True
        and module_reply_type_rule.get("then", {}).get("required")
        == ["reply_responsibility"]
        and module_reply_type_rule.get("else", {})
        .get("not", {})
        .get("required")
        == ["reply_responsibility"]
        and module_run_type_rule.get("then") is False
        and module_run_reply_contract.get("run_module_api_export")
        == "FORBIDDEN_OWNER_BOUND_VALUE"
        and module_run_reply_contract.get("reply_responsibility_required") is True
        and actor_reply_contract.get("fields") == reply_descriptor_fields
        and actor_reply_contract.get("source_type_spelling") == "Reply<T>"
        and actor_reply_contract.get("spawned_Run_actor_transport_descriptor")
        == "FORBIDDEN"
        and set(actor_reply_contract.get("admission_only_errors_forbidden", []))
        == {"mailboxFull", "receiverClosedBeforeAdmission"}
        and actor_reply_contract.get("field_contract", {}).get(
            "terminal_transport_failure"
        )
        == terminal_transport_failure
        and actor_storage_contract.get("module_api_correlation_id_field")
        == "per_value_non_forgeable"
        and actor_storage_contract.get("module_api_reply_id_field")
        == "per_value_non_forgeable"
        and actor_storage_contract.get("module_api_contains_runtime_correlation_value")
        is False,
        "MODULE_API_RUN_REPLY_RESPONSIBILITY_SEPARATION",
        "Reply<T>=descriptor-bound Run<T>=owner-bound-nonexportable",
    )

    actor_cross_module = actor_fixtures.get("cross_module", [])
    reply_cross_rows = [
        row
        for row in actor_cross_module
        if isinstance(row, dict)
        and row.get("responsibility_kind") == "actor_request_reply"
    ]
    run_cross_rows = [
        row
        for row in actor_cross_module
        if isinstance(row, dict)
        and row.get("responsibility_kind") == "concur_run"
    ]
    exact_reply_rows = [
        row
        for row in reply_cross_rows
        if isinstance(row.get("exported_descriptor"), dict)
        and row.get("exported_descriptor") == row.get("imported_descriptor")
    ]
    subsumption_reply_rows = [
        row
        for row in reply_cross_rows
        if isinstance(row.get("explicit_admitted_error_set_subsumption"), dict)
    ]
    dropped_reply_rows = [
        row
        for row in reply_cross_rows
        if row.get("expected_outcome") == "reject_design_static"
        and row.get("source_value_has_reply_responsibility") is True
        and row.get("exported_reply_responsibility") is None
    ]
    run_export_rows = [
        row
        for row in run_cross_rows
        if row.get("expected_outcome") == "reject_design_static"
        and any(
            "Run<" in str(channel.get("type_identity", ""))
            for channel in (
                row.get("exported_result_channel", {}),
                row.get("imported_result_channel", {}),
            )
            if isinstance(channel, dict)
        )
    ]
    subsumption_proof = (
        subsumption_reply_rows[0].get("explicit_admitted_error_set_subsumption", {})
        if len(subsumption_reply_rows) == 1
        else {}
    )
    check(
        len(actor_cross_module) == 4
        and len(reply_cross_rows) == 3
        and len(run_cross_rows) == 1
        and len(exact_reply_rows) == 1
        and reply_descriptor_is_normalized(
            exact_reply_rows[0].get("exported_descriptor"), module_api_marker=True
        )
        and exact_reply_rows[0].get("expected_outcome") == "accept_design_static"
        and len(subsumption_reply_rows) == 1
        and set(subsumption_proof.get("source", []))
        < set(subsumption_proof.get("target", []))
        and isinstance(subsumption_proof.get("proof_identity"), str)
        and bool(subsumption_proof.get("proof_identity"))
        and subsumption_reply_rows[0].get("other_static_fields_exact") is True
        and subsumption_reply_rows[0].get("reply_id_preserved_per_value") is True
        and subsumption_reply_rows[0].get("correlation_id_preserved_per_value") is True
        and len(dropped_reply_rows) == 1
        and dropped_reply_rows[0].get("expected_existing_diagnostic")
        == "RCTS_API_DIGEST_INCOMPLETE"
        and len(run_export_rows) == 1
        and run_export_rows[0].get("expected_existing_diagnostic")
        in {"RCTS_API_DIGEST_INCOMPLETE", "RCTS_RESPONSIBILITY_COMBINATION_INVALID"},
        "ACTOR_REPLY_RESPONSIBILITY_CROSS_MODULE_BINDING",
        "reply exact/subsumption/drop=3; owner-bound Run export reject=1",
    )

    actor_negative_rows = [
        row for row in actor_fixtures.get("negative", []) if isinstance(row, dict)
    ]
    invalid_run_reply_combinations = [
        row
        for row in actor_negative_rows
        if row.get("expected_outcome") == "reject_design_static"
        and row.get("expected_existing_diagnostic")
        == "RCTS_RESPONSIBILITY_COMBINATION_INVALID"
        and isinstance(row.get("descriptor"), dict)
        and row.get("descriptor", {}).get("responsibility_kind") == "concur_run"
        and isinstance(
            row.get("descriptor", {}).get("actor_request_reply_responsibility"),
            dict,
        )
    ]
    check(
        len(invalid_run_reply_combinations) == 1,
        "RUN_FORBIDS_ACTOR_REPLY_RESPONSIBILITY",
        f"negative_cases={len(invalid_run_reply_combinations)}",
    )

    mir_reply_descriptor_schema = (
        mir_responsibility_schema.get("$defs", {})
        .get("actorRequestReplyResponsibilityDescriptor", {})
    )
    mir_reply_array_schema = (
        mir_responsibility_schema.get("properties", {})
        .get("actor_request_reply_responsibilities", {})
    )
    mir_binding_rule = next(
        (
            row
            for row in mir_responsibility_schema.get("allOf", [])
            if isinstance(row, dict)
            and "actor_request_reply_responsibilities"
            in row.get("then", {}).get("required", [])
        ),
        {},
    )
    mir_binding_then = (
        mir_binding_rule.get("then", {})
        .get("properties", {})
        .get("actor_request_reply_responsibilities", {})
    )
    mir_binding_else = (
        mir_binding_rule.get("else", {})
        .get("properties", {})
        .get("actor_request_reply_responsibilities", {})
    )
    mir_handler_item_schema = (
        mir_reply_descriptor_schema.get("properties", {})
        .get("normalized_handler_error_set", {})
        .get("items", {})
    )
    mir_terminal_schema = (
        mir_reply_descriptor_schema.get("properties", {})
        .get("terminal_transport_failure", {})
    )
    check(
        mir_reply_array_schema.get("uniqueItems") is True
        and mir_reply_descriptor_schema.get("additionalProperties") is False
        and mir_reply_descriptor_schema.get("required") == reply_descriptor_fields
        and set(mir_reply_descriptor_schema.get("properties", {}))
        == reply_descriptor_field_set
        and set(mir_handler_item_schema.get("not", {}).get("enum", []))
        == admission_only_errors
        and mir_reply_descriptor_schema.get("properties", {})
        .get("normalized_handler_error_set", {})
        .get("uniqueItems")
        is True
        and mir_terminal_schema.get("items", {}).get("const")
        == terminal_transport_failure[0]
        and mir_terminal_schema.get("minItems")
        == mir_terminal_schema.get("maxItems")
        == 1
        and mir_terminal_schema.get("uniqueItems") is True
        and mir_binding_then.get("minItems") == 1
        and mir_binding_then.get("uniqueItems") is True
        and mir_binding_else.get("maxItems") == 0
        and "one-to-one set"
        in mir_responsibility_schema.get("x-deeplus-semantic-contract", {}).get(
            "actor_request_reply_responsibility", ""
        ),
        "MIR_ACTOR_REQUEST_REPLY_RESPONSIBILITY_SCHEMA",
        "descriptor-fields=7 admitted-request conditional=present",
    )

    def actor_request_reply_binding_state(row: Any) -> tuple[bool, bool]:
        if not isinstance(row, dict):
            return False, False
        admitted_request_events = [
            event
            for event in row.get("actor_isolation", [])
            if isinstance(event, dict)
            and event.get("kind") == "actor_lifecycle"
            and event.get("phase") == "enqueue_committed"
        ]
        request_correlation_ids = [
            event.get("correlation_id") for event in admitted_request_events
        ]
        request_reply_ids = [event.get("reply_id") for event in admitted_request_events]
        descriptors = row.get("actor_request_reply_responsibilities", [])
        if not isinstance(descriptors, list):
            return False, False
        descriptor_correlation_ids = [
            descriptor.get("correlation_id")
            if isinstance(descriptor, dict)
            else None
            for descriptor in descriptors
        ]
        descriptor_reply_ids = [
            descriptor.get("reply_id") if isinstance(descriptor, dict) else None
            for descriptor in descriptors
        ]
        bijection = (
            len(admitted_request_events) == len(request_correlation_ids)
            == len(request_reply_ids)
            == len(descriptor_correlation_ids)
            == len(descriptor_reply_ids)
            and all(
                isinstance(identity, str) and bool(identity)
                for identity in [
                    *request_correlation_ids,
                    *request_reply_ids,
                    *descriptor_correlation_ids,
                    *descriptor_reply_ids,
                ]
            )
            and len(request_correlation_ids) == len(set(request_correlation_ids))
            and len(request_reply_ids) == len(set(request_reply_ids))
            and len(descriptor_correlation_ids)
            == len(set(descriptor_correlation_ids))
            and len(descriptor_reply_ids) == len(set(descriptor_reply_ids))
            and set(request_correlation_ids) == set(descriptor_correlation_ids)
            and set(request_reply_ids) == set(descriptor_reply_ids)
        )
        normalization = all(
            reply_descriptor_is_normalized(descriptor) for descriptor in descriptors
        )
        return bijection, normalization

    mir_binding_cases = actor_fixtures.get(
        "mir_reply_responsibility_binding_cases", []
    )
    mir_binding_states = [
        (row, actor_request_reply_binding_state(row))
        for row in mir_binding_cases
        if isinstance(row, dict)
    ]
    mir_binding_descriptors = [
        descriptor
        for row in mir_binding_cases
        if isinstance(row, dict)
        for descriptor in row.get("actor_request_reply_responsibilities", [])
    ]
    guard_distribution = {
        guard: sum(row.get("expected_failed_guard") == guard for row, _ in mir_binding_states)
        for guard in (None, "bijection", "normalization")
    }
    mir_expected_guard_semantics = all(
        state[0] is (row.get("expected_failed_guard") != "bijection")
        and state[1] is (row.get("expected_failed_guard") != "normalization")
        and row.get("expected_outcome")
        == (
            "admit_design_static"
            if row.get("expected_failed_guard") is None
            else "reject_design_static"
        )
        for row, state in mir_binding_states
    )
    normalization_reject_error_sets = [
        descriptor.get("normalized_handler_error_set", [])
        for row, _ in mir_binding_states
        if row.get("expected_failed_guard") == "normalization"
        for descriptor in row.get("actor_request_reply_responsibilities", [])
        if isinstance(descriptor, dict)
    ]
    normalization_failure_causes = (
        any(errors != sorted(set(errors)) for errors in normalization_reject_error_sets)
        and any(
            bool(admission_only_errors.intersection(errors))
            for errors in normalization_reject_error_sets
        )
    )
    mir_binding_counts = actor_fixtures.get("expected_counts", {})
    mir_admit_count = sum(
        row.get("expected_outcome") == "admit_design_static"
        for row in mir_binding_cases
        if isinstance(row, dict)
    )
    mir_reject_count = sum(
        row.get("expected_outcome") == "reject_design_static"
        for row in mir_binding_cases
        if isinstance(row, dict)
    )
    check(
        len(mir_binding_cases) == 7
        and guard_distribution == {None: 3, "bijection": 2, "normalization": 2}
        and mir_binding_counts.get("mir_reply_responsibility_binding") == 7
        and mir_binding_counts.get("mir_reply_responsibility_binding_admit")
        == mir_admit_count
        == 3
        and mir_binding_counts.get("mir_reply_responsibility_binding_reject")
        == mir_reject_count
        == 4
        and all(
            reply_descriptor_is_normalized(descriptor)
            or any(
                descriptor is candidate
                for row, _ in mir_binding_states
                if row.get("expected_failed_guard") == "normalization"
                for candidate in row.get("actor_request_reply_responsibilities", [])
            )
            for descriptor in mir_binding_descriptors
        ),
        "MIR_ACTOR_REQUEST_REPLY_RESPONSIBILITY_FIXTURE_MATRIX",
        f"cases={len(mir_binding_cases)} admit={mir_admit_count} reject={mir_reject_count}",
    )
    check(
        mir_expected_guard_semantics,
        "MIR_ACTOR_REQUEST_REPLY_RESPONSIBILITY_GUARDS",
        str(guard_distribution),
    )
    check(
        normalization_failure_causes,
        "MIR_ACTOR_REQUEST_REPLY_RESPONSIBILITY_NORMALIZATION",
        f"normalization_reject_sets={len(normalization_reject_error_sets)}",
    )

    imported_mir_fixtures = parsed.get(
        root / "tests/fixtures/imported/mir-responsibility-fixtures.json", {}
    )
    imported_mir_groups = [
        *imported_mir_fixtures.get("positive_fixtures", []),
        *imported_mir_fixtures.get("negative_fixtures", []),
    ]
    concur_stack_contract = imported_mir_fixtures.get(
        "stack_kind_contracts", {}
    ).get("concur_runs")
    concur_schema_refs = [
        row.get("$ref")
        for row in mir_responsibility_schema.get("properties", {})
        .get("concur_runs", {})
        .get("items", {})
        .get("oneOf", [])
        if isinstance(row, dict)
    ]
    concur_run_rows = [
        event
        for fixture in imported_mir_groups
        if isinstance(fixture, dict)
        for event in fixture.get("record", {}).get("concur_runs", [])
        if isinstance(event, dict)
    ]
    identities_by_run: dict[str, set[str]] = {}
    for event in concur_run_rows:
        identities_by_run.setdefault(str(event.get("concur_run_id")), set()).add(
            str(event.get("execution_id"))
        )
    imported_mir_text = json.dumps(imported_mir_fixtures, ensure_ascii=False)
    schema_mir_text = json.dumps(mir_responsibility_schema, ensure_ascii=False)
    check(
        "concur_runs" in mir_responsibility_schema.get("required", [])
        and "task_scope" not in mir_responsibility_schema.get("properties", {})
        and concur_stack_contract
        == ["concur_run_spawn", "concur_run_join", "concur_run_lifecycle"]
        and concur_schema_refs
        == [
            "#/$defs/concurRunSpawnEvent",
            "#/$defs/concurRunJoinEvent",
            "#/$defs/concurRunLifecycleEvent",
        ]
        and imported_mir_fixtures.get("positive_fixture_count") == 3
        and imported_mir_fixtures.get("negative_fixture_count") == 9
        and len(concur_run_rows) > 0
        and all(
            event.get("kind")
            in {"concur_run_spawn", "concur_run_join", "concur_run_lifecycle"}
            and str(event.get("concur_run_id", "")).startswith("concur-run-")
            and str(event.get("execution_id", "")).startswith("execution-")
            and str(event.get("concur_id", "")).startswith("concur-")
            and "task_id" not in event
            and "scope_id" not in event
            for event in concur_run_rows
        )
        and all(len(execution_ids) == 1 for execution_ids in identities_by_run.values())
        and "MIR-POS-CONCUR-RUN-SPAWN-ORDER-001"
        in {
            row.get("fixture_id")
            for row in imported_mir_fixtures.get("positive_fixtures", [])
            if isinstance(row, dict)
        }
        and "MIR-NEG-CONCUR-RUN-COMPLETION-PRIMARY-001"
        in {
            row.get("fixture_id")
            for row in imported_mir_fixtures.get("negative_fixtures", [])
            if isinstance(row, dict)
        }
        and "task_scope" not in imported_mir_text
        and "task_spawn" not in imported_mir_text
        and "task_join" not in imported_mir_text
        and "task_lifecycle" not in imported_mir_text
        and "task_scope" not in schema_mir_text
        and "actor_request_task" not in schema_mir_text,
        "MIR_CONCUR_RUN_IDENTITY_AND_LEGACY_ERASURE",
        f"runs={len(concur_run_rows)} identities={len(identities_by_run)} fixtures=3+9",
    )

    authority_path = root / "current/authority-map.yaml"
    authority_text = authority_path.read_text(encoding="utf-8")
    domains = re.findall(r'^  ([a-z_]+):\n    path: (\S+)\n    owner: "([^"]+)"\n    sha256: ([0-9a-f]{64})$', authority_text, re.MULTILINE)
    digest_rows = []
    for domain, rel, owner, digest in domains:
        target = root / rel
        check(target.exists(), "AUTHORITY_PATH", rel)
        if target.is_file():
            actual_digest = file_sha(target)
        else:
            material = "\n".join(p.relative_to(root).as_posix() + "\0" + file_sha(p) for p in sorted(target.rglob("*.json"))).encode()
            actual_digest = hashlib.sha256(material).hexdigest()
        check(digest == actual_digest, "AUTHORITY_DOMAIN_IDENTITY", domain)
        digest_rows.append({"domain": domain, "path": rel, "sha256": actual_digest, "owner": owner})
    declared_match = re.search(r"^authority_digest: ([0-9a-f]{64})$", authority_text, re.MULTILINE)
    computed_authority = canonical_sha(digest_rows)
    check(len(domains) == 11 and bool(declared_match) and declared_match.group(1) == computed_authority, "AUTHORITY_AGGREGATE", computed_authority)

    lanes = parsed.get(root / "current/product-lanes.json", {}).get("lanes", [])
    lane_ids = [row.get("lane_id") for row in lanes]
    lane_status = {row.get("lane_id"): row.get("status") for row in lanes}
    check(len(lanes) == 15 and len(set(lane_ids)) == 15 and all(lane_status.get(lane_id) == "NOT_RUN" for lane_id in lane_ids), "PRODUCT_EVIDENCE_HONESTY", str(len(lanes)))
    implementation_text = (root / "current/implementation-status.yaml").read_text(encoding="utf-8")
    implementation_rows = dict(re.findall(r"^  ([a-z0-9_]+): (NOT_RUN|BLOCKED|FAILED|PASSED_FOCUSED|PASSED_INTEGRATED|PASSED_INDEPENDENT)$", implementation_text, re.MULTILINE))
    check(set(implementation_rows) == set(lane_ids) and implementation_rows == lane_status, "IMPLEMENTATION_STATUS_PARITY", f"registry={len(lane_ids)} yaml={len(implementation_rows)}")

    management_text = (root / "governance/policies/management-policy.yaml").read_text(encoding="utf-8")
    policy_values: dict[str, str] = {}
    clause_match = re.search(r"^  clause_id: (\S+)$", management_text, re.MULTILINE)
    if clause_match:
        policy_values["clause_id"] = clause_match.group(1)
    for key in ("statement", "restriction_rule", "visibility_rule"):
        match = re.search(rf'^  {key}: "([^"]+)"$', management_text, re.MULTILINE)
        if match:
            policy_values[key] = match.group(1)
    digest_match = re.search(r"^  clause_digest: ([0-9a-f]{64})$", management_text, re.MULTILINE)
    computed_expr_digest = canonical_sha(policy_values) if set(policy_values) == set(EXPR_FIELDS) else ""
    check(
        management_text.count("clause_id: EXPR-001") == 1
        and policy_values == EXPR_FIELDS
        and bool(digest_match)
        and digest_match.group(1) == computed_expr_digest == EXPR_DIGEST,
        "EXPR_NORMATIVE_AUTHORITY",
        f"count={management_text.count('clause_id: EXPR-001')} digest={computed_expr_digest}",
    )
    binding = (
        "[EXPR-001_BINDING]\n"
        "clause_id: EXPR-001\n"
        f"authority: {EXPR_AUTHORITY}\n"
        f"clause_digest: {EXPR_DIGEST}\n"
        "classification: non-authoritative projection"
    )
    review_consumers = sorted(
        path for path in (root / "governance/templates").glob("*Review*")
        if path.is_file()
    )
    text_consumers = [root / rel for rel in EXPR_TEXT_CONSUMERS] + review_consumers
    for path in text_consumers:
        text = path.read_text(encoding="utf-8")
        duplicate_normative = any(value in text for key, value in EXPR_FIELDS.items() if key != "clause_id")
        check(
            text.count(binding) == 1 and not duplicate_normative,
            "EXPR_CONSUMER_BINDING",
            path.relative_to(root).as_posix(),
        )
    check(len(review_consumers) == 7, "EXPR_REVIEW_TEMPLATE_DISCOVERY", str(len(review_consumers)))
    if args.candidate:
        state = parsed.get(root / "release/candidate-state.json", {})
        check(state.get("candidate_revision") == revision and state.get("authority_digest") == computed_authority and state.get("current_pointer_published") is False, "CANDIDATE_STATE", str(state.get("candidate_revision")))
    else:
        pointer = parsed.get(root / "current/current-pointer.json", {})
        check(set(pointer) == EXPECTED_POINTER_KEYS, "POINTER_REQUIRED_KEYS", f"missing={sorted(EXPECTED_POINTER_KEYS - set(pointer))} extra={sorted(set(pointer) - EXPECTED_POINTER_KEYS)}")
        check(pointer.get("schema") == "deeplus.current-pointer/v2", "POINTER_CLOSED_SHAPE", str(pointer.get("schema")))
        publication_source = pointer.get("publication_authority_source", {})
        audited_baseline = pointer.get("audited_implementation_baseline", {})
        candidate_binding = pointer.get("candidate_binding", {})
        check(
            publication_source == {
                "kind": "git-commit",
                "commit": "b6ff1f6e53ea8a21cfb706864478baa02545d3dd",
                "role": "publication_authority_source",
                "repository": "https://github.com/howork/Deeplus.git",
            },
            "POINTER_PUBLICATION_SOURCE",
            str(publication_source),
        )
        check(
            audited_baseline == {
                "kind": "git-commit",
                "commit": "4c85d5b923ee0a58ec6993bb0552e4d0aa7e24d9",
                "repository": "https://github.com/howork/Deeplus.git",
                "branch": "main",
                "role": "document_consistency_repair_base",
            },
            "POINTER_AUDITED_BASELINE",
            str(audited_baseline),
        )
        check(
            candidate_binding == {
                "mode": "external_post_commit_receipt_required",
                "receipt_location": "external_result_pack",
                "current_binding": False,
                "self_binding_forbidden": True,
            },
            "POINTER_EXTERNAL_BINDING",
            str(candidate_binding),
        )
        snapshot = pointer.get("source_snapshot")
        check(snapshot is None or (set(snapshot) == {"library_file_id", "sha256"} and bool(re.fullmatch(r"[0-9a-f]{64}", snapshot.get("sha256", "")))), "POINTER_SOURCE_SNAPSHOT", str(snapshot))
        git_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-git-binding-receipt.json", {})
        check(
            git_receipt.get("result") == "PASS_REVIEWED_HEAD"
            and git_receipt.get("scope") == "historical_reviewed_head"
            and git_receipt.get("current_binding") is False
            and git_receipt.get("reviewed_head") == "989bef9da472348971e56fafb2c9abc550100226"
            and git_receipt.get("pull_request") == 7
            and publication_source.get("repository") == git_receipt.get("repository")
            and publication_source.get("commit") == git_receipt.get("source_authority_commit"),
            "POINTER_SOURCE_BINDING", str(publication_source),
        )
        snapshot_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-source-snapshot-receipt.json", {})
        snapshot_object = snapshot_receipt.get("object", {})
        check(bool(snapshot and snapshot.get("library_file_id")), "POINTER_SNAPSHOT_ID", str(snapshot))
        check(
            snapshot_receipt.get("result") == "PASS_DIRECT_BYTES"
            and snapshot == {"library_file_id": snapshot_object.get("library_file_id"), "sha256": snapshot_object.get("sha256")},
            "POINTER_SNAPSHOT_BINDING", str(snapshot),
        )
        predecessor_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-predecessor-receipt.json", {})
        if revision == LANGUAGE_COHERENCE_REVISION:
            expected_predecessor = PREVIOUS_LANGUAGE_COHERENCE_REVISION
        elif revision == POST_PR16_REVISION:
            expected_predecessor = "r51f3-post-pr16-preview-design-r4"
        else:
            expected_predecessor = predecessor_receipt.get(
                "predecessor_revision"
            )
        check(
            predecessor_receipt.get("result") == "PASS_DIRECT_BYTES"
            and pointer.get("previous_pointer") == expected_predecessor
            and bool(re.fullmatch(r"[0-9a-f]{64}", predecessor_receipt.get("pointer_object", {}).get("sha256", ""))),
            "POINTER_PREDECESSOR_BINDING", str(pointer.get("previous_pointer")),
        )
        check(pointer.get("spec_revision") == revision and pointer.get("authority_digest") == computed_authority, "POINTER_AUTHORITY", str(pointer.get("spec_revision")))
        check(pointer.get("product_lanes") == lane_status, "POINTER_LANE_PARITY", f"pointer={len(pointer.get('product_lanes', {}))} registry={len(lane_status)}")
        actions = pointer.get("open_actions", [])
        action_keys = {"id", "priority", "summary", "owner", "tracking_ref", "acceptance_test", "target"}
        action_ids = [row.get("id") for row in actions]
        next_review_ids = [row.split(":", 1)[0] for row in pointer.get("required_next_reviews", [])]
        expected_action_ids = (
            SUCCESSOR_ACTION_IDS
            if revision in {POST_PR16_REVISION, LANGUAGE_COHERENCE_REVISION}
            else EXPECTED_ACTION_IDS
        )
        check(
            action_ids == expected_action_ids
            and (
                next_review_ids == action_ids
                if revision == LEGACY_REVISION
                else pointer.get("required_next_reviews") == EXPECTED_NEXT_REVIEWS
            )
            and len(action_ids) == len(set(action_ids))
            and all(set(row) == action_keys and all(bool(row.get(key)) for key in action_keys) for row in actions),
            "POINTER_ACTION_BINDING", str(action_ids),
        )
        check(
            all(row.get("tracking_ref") == f"deeplus-action:{row.get('id')}" for row in actions)
            and all("issues/6" not in row.get("tracking_ref", "") for row in actions),
            "POINTER_INTERNAL_TRACKING",
            str([row.get("tracking_ref") for row in actions]),
        )
        check(pointer.get("required_next_reviews") == EXPECTED_NEXT_REVIEWS, "POINTER_NEXT_REVIEW_BINDING", str(pointer.get("required_next_reviews")))
        review_index = parsed.get(root / "release/evidence/current-publication-m1.3-role-review-index.json", {})
        review_roles = [row.get("role") for row in review_index.get("reports", [])]
        check(
            review_roles == ["Design_", "Spec_", "Impl_", "Test_", "Devel_", "Archive_", "Build_"]
            and all(bool(re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))) for row in review_index.get("reports", []))
            and review_index.get("reviewed_head") == git_receipt.get("reviewed_head")
            and review_index.get("integrated_gate") == "HOLD",
            "ROLE_REVIEW_INDEX", str(review_roles),
        )
        check(
            review_index.get("static_corpus", {}).get("status") == "PASS_STATIC_ONLY"
            and review_index.get("executable_conformance", {}).get("status") == "NOT_RUN"
            and review_index.get("product_execution") == "NOT_RUN",
            "STATIC_EXECUTABLE_EVIDENCE_SPLIT", str(review_index.get("executable_conformance")),
        )

    language = (root / "spec/language.md").read_text(encoding="utf-8")
    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    frontend = parsed.get(root / "spec/frontend/frontend-model.json", {})
    trait_surface = parsed.get(
        root / "spec/contracts/trait-conformance-surface.json", {}
    )
    trait_surface_fixtures = parsed.get(
        root / "tests/fixtures/current/trait-conformance-surface-r1.json", {}
    )
    trait_surface_diagnostics = {
        "CONFORMANCE_OLD_DECLARATION_INTRODUCER_REMOVED",
        "CLASS_COLON_INHERITANCE_REMOVED",
        "TRAIT_REQUIRES_INHERITANCE_REMOVED",
        "CONFORMANCE_AUTO_POLICY_NOT_REGISTERED",
        "CONFORMANCE_AUTO_BODY_FORBIDDEN",
        "CONFORMANCE_LOCAL_SCOPE_FORBIDDEN",
        "CONFORMANCE_TRAIT_QUALIFICATION_REDUNDANT_IN_GROUP",
        "CONFORM_BLOCK_OWNER_CONTEXT_REQUIRED",
    }
    trait_open_p1 = [f"TCC-P1-{index:03d}" for index in range(2, 9)]
    global_open_p1 = [
        *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
        *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
        *trait_open_p1,
        "SFD-P1-009",
    ]
    trait_cases = trait_surface_fixtures.get("cases", [])
    check(
        frontend.get("revision") == TRAIT_OPERATOR_REFINEMENT_REVISION
        and trait_surface.get("revision") == TRAIT_OPERATOR_REFINEMENT_REVISION
        and trait_surface_fixtures.get("revision")
        == TRAIT_OPERATOR_REFINEMENT_REVISION
        and trait_surface.get("current_binding") is False
        and trait_surface.get("semantic_p0") == 0
        and trait_surface.get("open_feature_p1") == trait_open_p1
        and trait_surface.get("global_open_feature_p1") == global_open_p1
        and trait_surface.get("product_lanes") == "15/15_NOT_RUN"
        and trait_surface.get("tcc_evolution_lanes")
        == ["SOURCE", "RESOLUTION", "BEHAVIOR", "BINARY_ABI"]
        and frontend.get("trait_conformance_surface_contract", {}).get(
            "tcc_evolution_lanes"
        )
        == ["SOURCE", "RESOLUTION", "BEHAVIOR", "BINARY_ABI"]
        and trait_surface.get("admitted_nominal_kinds")
        == [
            "ordinary_class",
            "value_class",
            "resource_class",
            "data_class",
            "enum",
        ]
        and set(trait_surface.get("diagnostics", [])) == trait_surface_diagnostics
        and all(
            diagnostic_by_id.get(diagnostic_id, {}).get("diagnostic_status")
            == "active"
            for diagnostic_id in trait_surface_diagnostics
        )
        and trait_surface_fixtures.get("current_binding") is False
        and trait_surface_fixtures.get("semantic_p0") == 0
        and trait_surface_fixtures.get("global_open_feature_p1_count") == 22
        and trait_surface_fixtures.get("trait_open_feature_p1_count") == 7
        and trait_surface_fixtures.get("product_lanes") == "15/15_NOT_RUN"
        and len(trait_cases) == len(
            {row.get("fixture_id") for row in trait_cases if isinstance(row, dict)}
        )
        == 25
        and trait_surface_fixtures.get("counts")
        == {"positive": 14, "negative": 11, "total": 25, "executed": 0},
        "TRAIT_CONFORMANCE_SUCCESSOR_SURFACE",
        f"revision={frontend.get('revision')} p1={len(global_open_p1)} fixtures={len(trait_cases)}",
    )
    trait_case_by_id = {
        row.get("fixture_id"): row
        for row in trait_cases
        if isinstance(row, dict)
    }
    trait_case_projection_sha256 = {
        fixture_id: canonical_sha(
            {
                "source": row.get("source"),
                "expected": row.get("expected"),
                "diagnostic": row.get("diagnostic"),
                "assertions": row.get("assertions"),
            }
        )
        for fixture_id, row in trait_case_by_id.items()
    }
    trait_auto_receipt_case = trait_case_by_id.get("TCS-R1-POS-004", {})
    trait_auto_enum_case = trait_case_by_id.get("TCS-R1-POS-010", {})
    trait_auto_boundary_case = trait_case_by_id.get("TCS-R1-POS-009", {})
    check(
        list(trait_case_by_id) == list(TRAIT_SURFACE_CASE_PROJECTION_SHA256)
        and trait_case_projection_sha256
        == TRAIT_SURFACE_CASE_PROJECTION_SHA256
        and trait_auto_receipt_case.get("expected") == "ACCEPT_STATIC"
        and "public trait AutoUserIdentity\nsupports auto {"
        in trait_auto_receipt_case.get("source", "")
        and "closed_test_auto_policy"
        in trait_auto_receipt_case.get("assertions", [])
        and trait_auto_enum_case.get("expected") == "ACCEPT_STATIC"
        and "public trait AutoEnumIdentity\nsupports auto {"
        in trait_auto_enum_case.get("source", "")
        and "closed_test_auto_policy"
        in trait_auto_enum_case.get("assertions", [])
        and trait_auto_boundary_case.get("expected")
        == "ACCEPT_STATIC_IF_POLICY_REGISTERED"
        and "closed_test_auto_policy"
        not in trait_auto_boundary_case.get("assertions", []),
        "TRAIT_CONFORMANCE_CASE_SOURCE_OUTCOME_POLICY_EXACT_BINDING",
        (
            f"cases={len(trait_case_projection_sha256)} "
            f"exact={trait_case_projection_sha256 == TRAIT_SURFACE_CASE_PROJECTION_SHA256}"
        ),
    )
    check(
        scalar_occurrences(frontend, "FlowBindingArrow") == 1
        and scalar_occurrences(frontend, "FlowBinding") == 0,
        "CMA_FLOW_BINDING_PROJECTION",
        "CST FlowBindingArrow=1; semantic FlowBinding=0",
    )
    expression_operators = frontend.get("pratt", {}).get("expression", {}).get(
        "operators", []
    )
    range_operator = next(
        (row for row in expression_operators if row.get("id") == "range"), {}
    )
    assignment_operator = next(
        (row for row in expression_operators if row.get("id") == "assignment"), {}
    )
    slice_index_owner = frontend.get("pratt", {}).get("slice_index", {})
    ellipsis_stage = next(
        (row for row in frontend.get("stage_names", []) if row.get("surface") == "..."),
        {},
    )
    ellipsis_token = next(
        (
            row
            for row in frontend.get("boundary_policies", [])
            if row.get("id") == "POSITIONAL_REPEAT"
        ),
        {},
    )
    literal_rule = re.search(r"^Literal ::= (.+)$", grammar, re.MULTILINE)
    vocabulary = parsed.get(root / "spec/grammar/keyword-vocabulary.json", {})
    check(
        literal_rule is not None
        and "NullLiteral" not in literal_rule.group(1)
        and "RecoveryNullLiteral" not in grammar
        and 'UnfoldClause ::= "for" "..." Pattern "in" Expr ;' in grammar
        and 'IndexSuffix ::= "[" SliceAxisList "]" ;' in grammar
        and 'BoundedListLiteral ::= "[" StaticIntLiteral ".." StaticIntLiteral'
        in grammar
        and range_operator.get("tokens") == [[".."], ["..<"]]
        and "rejected_reserved_spellings" not in range_operator
        and assignment_operator.get("tokens")
        == [["="], ["+="], ["-="], ["*="], ["/="], ["%="]]
        and slice_index_owner.get("entry") == "SLICE_INDEX_PRATT_ENTRY"
        and slice_index_owner.get("bounds_required") is True
        and slice_index_owner.get("full_axis") == "* (NumericArray axis only)"
        and slice_index_owner.get("empty_axis") == "INDEX_SUFFIX_REQUIRES_AXIS"
        and slice_index_owner.get("anchor_outside_slice_bound_diagnostic")
        == {
            "diagnostic": "SLICE_ANCHOR_OUTSIDE_SLICE",
            "stage": "parser",
            "semantic_anchor_node_count": 0,
        }
        and ellipsis_stage.get("cst_roles")
        == ["RepeatedPositionalMarker", "UnfoldClause"]
        and ellipsis_stage.get("ast_roles")
        == ["RepeatedPositional", "ComprehensionUnfold"]
        and ellipsis_token.get("contexts")
        == ["parameter", "function_type", "comprehension_unfold_clause"]
        and "recovery_reserved_words" not in vocabulary
        and "null" not in vocabulary.get("hard_keywords", []),
        "VOI_GRAMMAR_FRONTEND_OWNER_CLOSURE",
        f"literal={literal_rule.group(1) if literal_rule else None} range={range_operator.get('tokens')} assignment={assignment_operator.get('tokens')}",
    )
    basic_index_predicate = predicate_by_id.get("BasicIndexOperatorAdmitted", {})
    index_suffix_diagnostic = diagnostic_by_id.get("INDEX_SUFFIX_REQUIRES_AXIS", {})
    check(
        index_suffix_diagnostic.get("stage") == "parser"
        and "empty_axis_recovery_production" not in slice_index_owner
        and basic_index_predicate.get("active_primary_diagnostic")
        == "LOGICAL_INDEX_DOMAIN_MISMATCH"
        and basic_index_predicate.get("diagnostic_refs")
        == ["LOGICAL_INDEX_DOMAIN_MISMATCH"]
        and basic_index_predicate.get("secondary_diagnostics") == []
        and not any(
            row.get("predicate_id") == "BasicIndexOperatorAdmitted"
            and row.get("diagnostic_id") == "INDEX_SUFFIX_REQUIRES_AXIS"
            for row in predicate_relation_rows
        ),
        "VOI_EMPTY_INDEX_SINGLE_OWNER",
        f"parser={index_suffix_diagnostic.get('stage')} primary={basic_index_predicate.get('active_primary_diagnostic')}",
    )
    prelude_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-prelude-signature-catalog.json", "entries"
    )
    forbidden_public_trees = {"RawAst", "ResolvedAst", "TypedAst<T,R>"}
    expected_prelude_entries = (
        language_coherence_contract.get("canonical_counts", {}).get(
            "prelude_entries"
        )
        if revision == LANGUAGE_COHERENCE_REVISION
        else 49
    )
    check(
        len(prelude_rows) == expected_prelude_entries
        and not forbidden_public_trees.intersection(
            {row.get("symbol") for row in prelude_rows}
        )
        and all(symbol not in (root / "library/prelude/prelude.md").read_text(encoding="utf-8") for symbol in forbidden_public_trees),
        "CMA_COMPILER_TREE_BOUNDARY",
        f"prelude_entries={len(prelude_rows)}",
    )
    prelude_by_id = {row.get("entry_id"): row for row in prelude_rows}
    arithmetic_defect = prelude_by_id.get("arithmetic_defect", {})
    index_error = prelude_by_id.get("index_error", {})
    indexable = prelude_by_id.get("indexable", {})
    display_entry = prelude_by_id.get("display", {})
    ord_entry = prelude_by_id.get("ord_t", {})
    eq_entry = prelude_by_id.get("eq_rhs", {})
    unary_plus_entry = prelude_by_id.get("unary_plus", {})
    unary_minus_entry = prelude_by_id.get("unary_minus", {})
    add_entry = prelude_by_id.get("add_rhs", {})
    subtract_entry = prelude_by_id.get("subtract_rhs", {})
    multiply_entry = prelude_by_id.get("multiply_rhs", {})
    divide_entry = prelude_by_id.get("divide_rhs", {})
    remainder_entry = prelude_by_id.get("remainder_rhs", {})
    fixed_operator_prelude_entries = [
        unary_plus_entry,
        unary_minus_entry,
        add_entry,
        subtract_entry,
        multiply_entry,
        divide_entry,
        remainder_entry,
        eq_entry,
        ord_entry,
    ]
    check(
        arithmetic_defect.get("symbol") == "ArithmeticDefect"
        and arithmetic_defect.get("kind") == "language_intrinsic_defect"
        and arithmetic_defect.get("signatures")
        == ["prelude intrinsic ArithmeticDefect { overflow; divisionByZero; }"]
        and arithmetic_defect.get("product_support") == "NOT_RUN"
        and index_error.get("symbol") == "IndexError"
        and index_error.get("status") == "stable_design"
        and index_error.get("signatures")
        == ["public enum IndexError { outOfLogicalDomain; keyNotFound; }"]
        and index_error.get("product_support") == "NOT_RUN"
        and "conformance does not activate []" in indexable.get("notes", "")
        and display_entry.get("signatures")
        == ["public trait Display { +def display.() -> String throws Never effects {}; }"]
        and eq_entry.get("signatures")
        == ["public trait Eq<Rhs> { +def equals.(borrow rhs: Rhs) -> Bool throws Never effects {}; }"]
        and ord_entry.get("signatures")
        == ["public trait Ord<Rhs>\nderives Eq<Rhs> {\n    +def compare.(borrow rhs: Rhs) -> Int throws Never effects {}\n}"]
        and unary_plus_entry.get("signatures")
        == ["public trait UnaryPlus { type Output; +def positive.() -> <Self as UnaryPlus>::Output throws Never effects {}; }"]
        and unary_minus_entry.get("signatures")
        == ["public trait UnaryMinus { type Output; +def negate.() -> <Self as UnaryMinus>::Output throws Never effects {}; }"]
        and add_entry.get("signatures")
        == ["public trait Add<Rhs> { type Output; +def add.(borrow rhs: Rhs) -> <Self as Add<Rhs>>::Output throws Never effects {}; }"]
        and subtract_entry.get("signatures")
        == ["public trait Subtract<Rhs> { type Output; +def subtract.(borrow rhs: Rhs) -> <Self as Subtract<Rhs>>::Output throws Never effects {}; }"]
        and multiply_entry.get("signatures")
        == ["public trait Multiply<Rhs> { type Output; +def multiply.(borrow rhs: Rhs) -> <Self as Multiply<Rhs>>::Output throws Never effects {}; }"]
        and divide_entry.get("signatures")
        == ["public trait Divide<Rhs> { type Output; +def divide.(borrow rhs: Rhs) -> <Self as Divide<Rhs>>::Output throws Never effects {}; }"]
        and remainder_entry.get("signatures")
        == ["public trait Remainder<Rhs> { type Output; +def remainder.(borrow rhs: Rhs) -> <Self as Remainder<Rhs>>::Output throws Never effects {}; }"]
        and all(
            entry.get("kind") == "trait"
            and entry.get("status") == "stable_design"
            and "fixed_operator_conformance_overloading"
            in entry.get("feature_refs", [])
            and entry.get("product_support") == "NOT_RUN"
            and len(entry.get("signatures", [])) == 1
            and entry.get("signature_records")
            == [
                {
                    "text": entry.get("signatures", [])[0],
                    "dialect": "deeplus_source",
                    "grammar_root": "TopLevelDecl",
                    "schema": None,
                }
            ]
            for entry in fixed_operator_prelude_entries
        )
        and all(
            diagnostic_by_id.get(diagnostic_id, {}).get("diagnostic_status")
            == "active"
            for diagnostic_id in (
                "OPERATOR_CONFORMANCE_MISSING",
                "OPERATOR_CONFORMANCE_AMBIGUOUS",
                "OPERATOR_CONFORMANCE_INTRINSIC_DOMAIN_RESERVED",
                "OPERATOR_CONFORMANCE_LEFT_OWNER_REQUIRED",
                "OPERATOR_CONFORMANCE_EVIDENCE_ROUTE_NOT_ADMITTED",
                "OPERATOR_CONFORMANCE_RESPONSIBILITY_MISMATCH",
                "RETURN_TYPE_DIRECTED_OPERATOR_RESOLUTION_FORBIDDEN",
                "OPERATOR_CONFORMANCE_REQUIRES_EXPLICIT_CONVERSION",
                "OPERATOR_NOT_CONFORMANCE_OVERLOADABLE",
                "INDEX_SUFFIX_REQUIRES_AXIS",
            )
        ),
        "VOI_PRELUDE_AND_DIAGNOSTIC_CLOSURE",
        f"arithmetic_defect={arithmetic_defect.get('entry_id')} index_error={index_error.get('entry_id')} indexable={indexable.get('entry_id')}",
    )
    retired_multiline_diagnostic = "MULTILINE_STRING_INDENT_PREFIX_MISMATCH"
    diagnostic_relation_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-diagnostic-relation-registry.json",
        "relations",
    )
    check(
        retired_multiline_diagnostic not in language
        and all(row.get("diagnostic_id") != retired_multiline_diagnostic for row in diagnostic_rows)
        and all(row.get("diagnostic_id") != retired_multiline_diagnostic for row in diagnostic_relation_rows)
        and all(retired_multiline_diagnostic not in json.dumps(row, ensure_ascii=False) for row in feature_rows)
        and all(retired_multiline_diagnostic not in json.dumps(row, ensure_ascii=False) for row in predicate_rows),
        "CMA_MULTILINE_DIAGNOSTIC_RETIRED",
        retired_multiline_diagnostic,
    )
    lcp_fixtures = parsed.get(
        root / "tests/fixtures/current/multiline-string-lcp-r1.json", {}
    )
    lcp_cases = lcp_fixtures.get("cases", [])
    lcp_ids = [row.get("fixture_id") for row in lcp_cases if isinstance(row, dict)]
    lcp_valid = (
        lcp_fixtures.get("schema") == "deeplus.multiline-string-lcp-fixtures/r1"
        and lcp_fixtures.get("authority") == "CMA-R1-A003"
        and lcp_fixtures.get("evidence_status") == "DESIGN_STATIC_NOT_RUN"
        and lcp_fixtures.get("product_support") == "NOT_RUN"
        and len(lcp_cases) == len(set(lcp_ids)) == 6
    )
    for row in lcp_cases:
        if not isinstance(row, dict):
            lcp_valid = False
            continue
        lines = row.get("content_lines", [])
        expected_prefix = longest_exact_indent_prefix(lines) if isinstance(lines, list) else "\0INVALID"
        dedented = [
            "" if not line.lstrip(" \t") else line[len(expected_prefix):]
            for line in lines
        ] if isinstance(lines, list) and expected_prefix != "\0INVALID" else []
        lcp_valid = lcp_valid and (
            row.get("line_ending") in {"LF", "CRLF"}
            and isinstance(row.get("terminal_content_line_break"), bool)
            and row.get("expected_common_prefix") == expected_prefix
            and row.get("expected_dedented_lines") == dedented
            and row.get("expected_outcome") == "accept"
            and row.get("expected_primary_diagnostic") is None
        )
    lcp_by_id = {row.get("fixture_id"): row for row in lcp_cases if isinstance(row, dict)}
    for left, right in (
        ("LCP-LF-PARITY", "LCP-CRLF-PARITY"),
        ("LCP-NO-TRAILING-CONTENT-NEWLINE", "LCP-TRAILING-CONTENT-NEWLINE"),
    ):
        a, b = lcp_by_id.get(left, {}), lcp_by_id.get(right, {})
        lcp_valid = lcp_valid and all(
            a.get(field) == b.get(field)
            for field in ("content_lines", "expected_common_prefix", "expected_dedented_lines")
        )
    check(lcp_valid, "CMA_MULTILINE_LCP_FIXTURES", f"cases={len(lcp_cases)}")
    check("| `*` | call-side positional unfold" in language and 'PositionalUnfoldArgument ::= "*" Expr ;' in grammar, "POSITIONAL_UNFOLD_OWNER", "* in spec and grammar")
    check("repeated positional parameter/type residue and positional unfold" not in language, "POSITIONAL_UNFOLD_NO_ELLIPSIS", "... is not call-side unfold")
    probes = ["options***: Record", "Record***", "**options", "let#lazy", "sealed class"]
    for probe in probes:
        check(probe in language, "CURRENT_SURFACE_PROBE", probe)
    check('Identifier "***" TypeAnnotation' in grammar, "NAMED_REST_GRAMMAR", "***")

    instruction_chars = len((root / "governance/project-instructions.txt").read_text(encoding="utf-8"))
    check(instruction_chars <= 8000, "PROJECT_INSTRUCTION_LIMIT", str(instruction_chars))
    memories = sorted((root / "roles/current-memory").glob("*.json"))
    check(len(memories) == 5, "ROLE_MEMORY_COUNT", str(len(memories)))
    for path in memories:
        capsule = parsed.get(path, {})
        check(len(capsule.get("current_facts", [])) <= 50 and len(capsule.get("open_actions", [])) <= 30 and len(capsule.get("watch_items", [])) <= 20 and path.stat().st_size <= 102400, "ROLE_MEMORY_CAP", path.name)
        check(capsule.get("source_revision") == revision and all(not row.get("id", "").startswith("MIG-M1-") for row in capsule.get("open_actions", [])), "ROLE_MEMORY_CURRENT", path.name)
        facts_by_id = {
            row.get("id"): row
            for row in capsule.get("current_facts", [])
            if isinstance(row, dict)
        }
        memory_action_ids = {
            row.get("id")
            for row in capsule.get("open_actions", [])
            if isinstance(row, dict)
        }
        check(
            set(facts_by_id) == {
                "ARCH-001", "EVID-001", "PUB-001", "P1-001",
                "CMA-001", "MIRX1-001", "EXPR-001",
            }
            and "22 total" in facts_by_id.get("P1-001", {}).get("statement", "")
            and "15 product lanes remain NOT_RUN" in facts_by_id.get("EVID-001", {}).get("statement", "")
            and facts_by_id.get("CMA-001", {}).get("introduced")
            == (
                POST_PR16_REVISION
                if revision == LANGUAGE_COHERENCE_REVISION
                else revision
            )
            and "Issue #24 remains open" in facts_by_id.get("MIRX1-001", {}).get("statement", "")
            and memory_action_ids <= {"M13-A002", "M13-A005", "M13-TEST-001"}
            and not {"M13-IMPL-A004", "M13-DEVEL-001"}.intersection(memory_action_ids),
            "CMA_ROLE_MEMORY_ROTATION",
            path.name,
        )
        expr_rows = [row for row in capsule.get("current_facts", []) if row.get("id") == "EXPR-001"]
        check(
            len(expr_rows) == 1
            and expr_rows[0].get("statement") == "Non-authoritative projection; resolve the normative clause by authority path and digest."
            and expr_rows[0].get("authority") == EXPR_AUTHORITY
            and expr_rows[0].get("source") == EXPR_AUTHORITY
            and expr_rows[0].get("clause_digest") == EXPR_DIGEST
            and "github.com/howork/Deeplus/issues/8" not in json.dumps(capsule, ensure_ascii=False),
            "EXPR_MEMORY_BINDING",
            path.name,
        )
    design_memory = parsed.get(root / "roles/current-memory/Design_Deeplus_Current_Memory.json", {})
    design_actions = design_memory.get("open_actions", [])
    design_history = design_memory.get("recent_releases", [])
    pr7_history = [row for row in design_history if row.get("release") == "github-pr-7-historical-merge"]
    check(
        all(row.get("id") != "M13-DESIGN-001" for row in design_actions)
        and all("PR #7" not in json.dumps(row, ensure_ascii=False) and "Draft" not in json.dumps(row, ensure_ascii=False) for row in design_actions)
        and len(pr7_history) == 1
        and "merged=true" in pr7_history[0].get("verdict", "")
        and "draft=false" in pr7_history[0].get("verdict", "")
        and "cec72e38d3de716344b64f049fb7a6fc9c1dd01e" in pr7_history[0].get("verdict", "")
        and all(term in pr7_history[0].get("verdict", "") for term in ("tag", "GitHub Release", "Issue closure", "public license", "product promotion", "not inferred")),
        "DESIGN_PR7_HISTORICAL",
        str(pr7_history),
    )

    crates = sorted(path for path in (root / "crates").iterdir() if path.is_dir())
    check(len(crates) == 15, "CRATE_BOUNDARY_COUNT", str(len(crates)))
    for crate in crates:
        check((crate / "Cargo.toml").is_file() and bool(list((crate / "src").glob("*.rs"))), "CRATE_SCAFFOLD", crate.name)
    manifest = parsed.get(root / "release/source-tree-manifest.json", {})
    listed = manifest.get("files", [])
    actual_files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and not any(part in EXCLUDED_TREE_PARTS for part in p.relative_to(root).parts)
        and p.relative_to(root).as_posix() != "release/source-tree-manifest.json"
    )
    listed_map = {row["path"]: row for row in listed}
    check(set(listed_map) == {p.relative_to(root).as_posix() for p in actual_files}, "SOURCE_TREE_MEMBERSHIP", f"listed={len(listed_map)} actual={len(actual_files)}")
    for path in actual_files:
        rel = path.relative_to(root).as_posix()
        row = listed_map.get(rel, {})
        check(row.get("sha256") == file_sha(path) and row.get("bytes") == path.stat().st_size, "SOURCE_TREE_FILE_IDENTITY", rel)
    tree_material = "\n".join(f"{row['path']}\0{row['sha256']}" for row in sorted(listed, key=lambda x: x["path"])).encode()
    check(manifest.get("revision") == revision and manifest.get("tree_sha256") == hashlib.sha256(tree_material).hexdigest(), "SOURCE_TREE_AGGREGATE", str(manifest.get("tree_sha256")))

    result = "PASS" if not errors else "FAIL"
    receipt = {
        "schema": "deeplus.canonical-workspace-validation-receipt/v1.1",
        "revision": revision, "mode": "candidate" if args.candidate else "published-current",
        "result": result, "evidence_level": "E2_STATIC_CLOSURE",
        "checks": len(checks), "passed": sum(row["pass"] for row in checks),
        "failed": sum(not row["pass"] for row in checks), "canonical_counts": actual,
        "json_files_parsed": len(parsed), "legacy_files_accounted": len(legacy),
        "catalogs_reassembled": len(reconstructed), "rust_scaffold_crates": len(crates),
        "product_execution": "NOT_RUN", "warnings": warnings, "errors": errors,
        "evidence_honesty": "Static closure does not establish lexer, parser, checker, MIR, xVM, Cranelift, tooling, conformance, or user-study product support.",
    }
    if args.write_receipt:
        write_json(root / "migration/migration-receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
