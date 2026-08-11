#!/usr/bin/env python3
"""Static closure validator for the Deeplus current or candidate workspace."""

# Keep canonical validator bytes LF-normalized so bound-root hashes agree in CI.
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
R10_HIR_MIR_REVISION = "r51f3-current-hir-mir-machine-contract-r1"
R11_R19_FRONTEND_REVISION = "r51f3-current-frontend-readiness-r11-r19-r1"
R41_ACTOR_PROTOCOL_REVISION = (
    "r51f3-current-actor-protocol-direct-conformance-r1"
)
R23_ACTOR_PROTOCOL_BINDING_REVISION = (
    "r51f3-current-actor-protocol-binding-descriptor-r1"
)
R46_MANAGED_ROOT_RUNTIME_REVISION = (
    "r51f3-current-managed-root-runtime-fusion-r1"
)
R47_OWNERSHIP_CONTRACT_FUSION_REVISION = (
    "r51f3-current-ownership-contract-fusion-r1"
)
R74_IMPLEMENTATION_READINESS_REVISION = (
    "r51f3-current-implementation-readiness-r74-r1"
)
R75_ACTOR_CRANELIFT_PROJECTION_REVISION = (
    "r51f3-current-actor-cranelift-projection-r75-r1"
)
R76_GLOBAL_TRACE_CLOSURE_REVISION = (
    "r51f3-current-global-implementation-target-trace-closure-r76-r1"
)
G4_INDEPENDENT_READINESS_REVISION = (
    "r51f3-current-implementation-readiness-g4-audit-r1"
)
R77_PUBLICATION_POLICY_CLOSURE_REVISION = (
    "r51f3-current-r77-publication-policy-closure-r1"
)
FRONTEND_SUCCESSOR_REVISIONS = {
    R11_R19_FRONTEND_REVISION,
    R41_ACTOR_PROTOCOL_REVISION,
    R23_ACTOR_PROTOCOL_BINDING_REVISION,
    R46_MANAGED_ROOT_RUNTIME_REVISION,
    R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
    R74_IMPLEMENTATION_READINESS_REVISION,
    R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
    R76_GLOBAL_TRACE_CLOSURE_REVISION,
    G4_INDEPENDENT_READINESS_REVISION,
    R77_PUBLICATION_POLICY_CLOSURE_REVISION,
}
CURRENT_MACHINE_REVISIONS = {
    R10_HIR_MIR_REVISION,
    *FRONTEND_SUCCESSOR_REVISIONS,
}
TRAIT_OPERATOR_REFINEMENT_REVISION = "r51f3-current-trait-operator-refinement-r1"
R77_INTEGRATED_SURFACE_REVISION = "r51f3-current-integrated-surface-r77-r1"
PREVIOUS_LANGUAGE_COHERENCE_REVISION = "r51f3-current-pattern-sequence-multivalue-r1"
PATTERN_COMPONENT_REVISION = "r51f3-current-trait-operator-refinement-r1"
AUTHORITY_TRANSITION_BASE_COMMIT = "cfd5946c52571119564b9c8beb430f8dd0356750"
R4_SEMANTIC_PUBLICATION_COMMIT = "8d81d6747488055cb76da8bda1350b96e576b7b1"
R8_SEMANTIC_PUBLICATION_COMMIT = "9bc2e8694bc44cea28efe34541ce465a9bf2c109"
R9_SEMANTIC_SOURCE_COMMIT = "94b4d369213ec3ce829c70b66f15301cf3c7039c"
R9_SEMANTIC_PUBLICATION_COMMIT = "fd752f560d30a9cbe61f04b24b0e58abdbc150a3"
R9_SEMANTIC_PUBLICATION_TREE = "3afc92cae7f8cf7232e30944d6516aec811e6981"
R10_SEMANTIC_SOURCE_COMMIT = "6460e8127620d495e055cd0b800198fb6f7e1a06"
R10_SEMANTIC_PUBLICATION_COMMIT = "7d609678bdb8c94f2a365e89be578e595bb394b6"
R10_SEMANTIC_PUBLICATION_TREE = "76189fb47e75d4faeb3f2f975f51df265dc42146"
R11_R19_SEMANTIC_PUBLICATION_COMMIT = "0f3fa1e145d38725ad22f929d5100fda9584ac10"
R25_R27_SEMANTIC_SOURCE_COMMIT = "75474ed4a03cd5cb3a424509694c70831b512b59"
R25_R27_SEMANTIC_PUBLICATION_COMMIT = "2feba9e077ffdf35403c3b8467c17ddcfcf142f6"
R25_R27_SEMANTIC_PUBLICATION_TREE = "7118be15102e259d916874612423fa208e8e2c5b"
R41_SEMANTIC_SOURCE_COMMIT = "f9530ba7672172253a7ebe1bfdfcbe3dd4403a0a"
R41_SEMANTIC_PUBLICATION_COMMIT = "fae105020a7b1ebc32a8fe85e80412d8ea10a803"
R41_SEMANTIC_PUBLICATION_TREE = "d949864bf9500ac6c7d40b81e5b56848517bad15"
R23_SEMANTIC_SOURCE_COMMIT = "212dd8c0b8ac1541d89ec0f8d4f555fc04fe00c6"
R23_SEMANTIC_PUBLICATION_COMMIT = "b4a4ff8fa183c65577b18e6b7001c4ccab52befa"
R23_SEMANTIC_PUBLICATION_TREE = "bf273631afecdbe68e86a264d0e1a01e27229fe7"
R46_SEMANTIC_SOURCE_COMMIT = "2ad1e1967dd67d928f06aabb3c98cf44081ec4da"
R46_SEMANTIC_PUBLICATION_COMMIT = "82cdf6aa6b1527af3b5b06157a3fd745ee33e5b0"
R46_SEMANTIC_PUBLICATION_TREE = "d13a15af71c717c2145ce28a39e7dd1f6501c99f"
R47_SEMANTIC_SOURCE_COMMIT = "6cff69d6e655e399baf82f66cf62a225cbb05640"
R47_SEMANTIC_PUBLICATION_COMMIT = "ee7d1833dcc9156070c1071f96fc55b3e19ae967"
R47_SEMANTIC_PUBLICATION_TREE = "dd631edaf0be77a13664ba83c57bf12512302627"
R74_SEMANTIC_SOURCE_COMMIT = "ee2ec2e4df5d8a9eb36d938602506b11fc66d52b"
R74_SEMANTIC_PUBLICATION_COMMIT = "17d90a43908d45b03938006f9dfb5d1cd609e655"
R74_SEMANTIC_PUBLICATION_TREE = "a9291ef158fa21a473789d5c685dfcf0cb3050d2"
R75_SEMANTIC_SOURCE_COMMIT = "d0e3f459b55f4eeb9bf884ccf982d90602f0d2b7"
R75_SEMANTIC_PUBLICATION_COMMIT = "420ccdcbe9dae1b267d9fa0277239195f0d72d1b"
R75_SEMANTIC_PUBLICATION_TREE = "2c3b690cee13a28f89130728c5a8d0d9d39cccc9"
R76_SEMANTIC_SOURCE_COMMIT = "adfff280c015640ccb2a6c87812c984162b4b008"
R76_SEMANTIC_PUBLICATION_COMMIT = "f550338a9daf9cae64f4dc8933dfb4219ee76dcd"
R76_SEMANTIC_PUBLICATION_TREE = "7c663efaaadf8733a65d73a9540bcdb5700147fb"
G4_SEMANTIC_SOURCE_COMMIT = "df5d22f7db267519ebb16685b68fb6c8cb6b9d61"
G4_SEMANTIC_PUBLICATION_COMMIT = "f07424425929b1bf1abe0fff3ad39dfe09c0f52f"
G4_SEMANTIC_PUBLICATION_TREE = "611a303363d71f4b27daddf02b56752ac6e8e75d"
CURRENT_PUBLICATION_TARGET_COMMIT = G4_SEMANTIC_PUBLICATION_COMMIT
HISTORICAL_PUBLICATION_SOURCE_COMMIT = "b6ff1f6e53ea8a21cfb706864478baa02545d3dd"
HISTORICAL_DOCUMENT_CONSISTENCY_BASE_COMMIT = (
    "4c85d5b923ee0a58ec6993bb0552e4d0aa7e24d9"
)
HISTORICAL_RECEIPT_SHA256 = {
    "release/evidence/current-publication-m1.3-git-binding-receipt.json":
        "eb9761ced47f8c09906d04da4203eb0fba8697c2f08b26e14ba181cb4a2f2bfe",
    "release/evidence/current-publication-m1.3-source-snapshot-receipt.json":
        "33657a85c46c110f61dba2d55fa7eff193aaeaded68b5d46daca492d14255c2b",
    "release/evidence/current-publication-m1.3-predecessor-receipt.json":
        "4494cba2073e45dd70f06e20938d900c076574b965f2d0e85c109805e21584b8",
}
LANGUAGE_COHERENCE_CONTRACT_REL = (
    "spec/contracts/language-coherence-current-integrity-r1.json"
)
EXCLUDED_TREE_PARTS = {
    ".git",
    ".codex-worktrees",
    "audit",
    "target",
    "dist",
    "candidate",
    "tmp",
    "__pycache__",
}
EXPECTED = {
    "features": 723, "diagnostics": 1486, "predicates": 283,
    "predicate_fixtures": 877, "no_go": 154,
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
R77_EXPECTED_NEXT_REVIEWS = EXPECTED_NEXT_REVIEWS + [
    "R77-A006: Spec_ + Impl_ + Test_",
]
CURRENT_DECISION_INDEX_PATHS = [
    "decisions/language/current-decisions.json",
    "decisions/language/Design_Deeplus_Integrated_Surface_Atomic_Cutover_R77_R1.md",
    "decisions/language/Design_Deeplus_Parser_Oriented_DPG_Cutover_R1.md",
    "decisions/language/Design_Deeplus_Pattern_Sequence_MultiValue_Adoption_R1.md",
    "decisions/language/Design_Deeplus_Trait_Operator_Refinement_Adoption_R1.md",
    "decisions/language/Design_Deeplus_Callable_Responsibility_Static_Lexical_Adoption_R1.md",
    "decisions/language/Design_Deeplus_Cranelift_Backend_Adoption_R1.md",
    "decisions/language/Design_Deeplus_Nominal_Conform_And_Callable_Responsibility_Clauses_R1.md",
    "decisions/language/Design_Deeplus_Owner_Roles_Concur_Run_And_Shared_State_Adoption_R1.md",
]
R10_DECISION_PATH = "decisions/language/Design_Deeplus_HIR_MIR_Machine_Contract_R1.md"
R11_R19_DECISION_PATHS = [
    "decisions/language/Design_Deeplus_Construction_Cleanup_State_R1.md",
    "decisions/language/Design_Deeplus_Frontend_CST_Parser_Recovery_Readiness_R1.md",
    "decisions/language/Design_Deeplus_Closed_Pratt_Parse_Goal_R1.md",
    "decisions/language/Design_Deeplus_Complete_Token_Lexical_Goal_R1.md",
    "decisions/language/Design_Deeplus_Shorthand_Interpolation_State_Machine_R1.md",
    "decisions/language/Design_Deeplus_Multiline_Interpolation_Atomic_Payload_R1.md",
    "decisions/language/Design_Deeplus_R19_Source_Role_Profile_Gate_R1.md",
]
R47_DECISION_PATHS = [
    "decisions/language/Design_Deeplus_Ownership_Type_Qualifier_Normalization_R1.md",
    "decisions/language/Design_Deeplus_Responsibility_Identity_Registry_R1.md",
    "decisions/language/Design_Deeplus_Closure_Capture_Plan_R1.md",
    "decisions/language/Design_Deeplus_Deferred_Call_Plan_R1.md",
    "decisions/language/Design_Deeplus_Cleanup_Budget_Algebra_R1.md",
    "decisions/language/Design_Deeplus_Loan_Close_Operation_R1.md",
    "decisions/language/Design_Deeplus_SharedMutex_Payload_Bound_R1.md",
]
R48_R74_DECISION_PATHS = [
    "decisions/language/Design_Deeplus_Formatter_LSP_Incremental_Parsing_Contract_R1.md",
    "decisions/language/Design_Deeplus_Ownership_Tooling_Projection_R1.md",
    "decisions/language/Design_Deeplus_Actor_Minimum_Lifecycle_Implementation_Handoff_R1.md",
    "decisions/language/Design_Deeplus_Contract_Authority_Status_Reconciliation_R1.md",
    "decisions/language/Design_Deeplus_R54_Scalar_Numeric_Fixed_Operator_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R55_Lexical_Trivia_Source_Root_Closure_R1.md",
    "decisions/language/Design_Deeplus_R56_NumericArray_Shape_Inferred_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R57_Unified_Call_Tilde_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R58_Member_Visibility_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R59_Pattern_Dynamic_Lowering_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R60_Pattern_Match_Ownership_Split_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R61_Pattern_Clause_Exhaustiveness_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R62_Trait_Qualified_Associated_Static_Selection_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R63_Trait_Associated_Static_Stale_Diagnostic_Removal_R1.md",
    "decisions/language/Design_Deeplus_R64_Associated_Requirement_Phase_A_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R65_Associated_Requirement_AST_Diagnostic_Parity_R1.md",
    "decisions/language/Design_Deeplus_R66_Responsibility_Identity_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R67_Closure_Capture_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R68_Region_Lifetime_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_Managed_Reference_Memory_Profile_R1.md",
    "decisions/language/Design_Deeplus_R69_Managed_Reference_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R70_Static_Runtime_Member_Boundary_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R71_Method_Extension_Resolution_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R72_Member_Extension_Collision_Dynamic_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R73_Member_Extension_Collision_Conformance_Trace_Closure_R1.md",
    "decisions/language/Design_Deeplus_R74_Member_Extension_Collision_Diagnostic_Trace_Closure_R1.md",
]
R76_DECISION_PATH = (
    "decisions/language/"
    "Design_Deeplus_R76_Global_Implementation_Target_Trace_Closure_R1.md"
)
G4_DECISION_PATH = (
    "decisions/language/"
    "Design_Deeplus_G4_Independent_Implementation_Readiness_Audit_R1.md"
)
R77_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R77_Integrated_Surface_Publication_Closure_R1.md"
)
R10_DECISION_ID = "DSGN-CURRENT-HIR-MIR-MACHINE-CONTRACT"
AUTHORITY_TRANSITION_REPORT = (
    "governance/reports/Design_Deeplus_Codex_Design_Authority_Transition_R1.md"
)
R4_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R4_Name_Resolution_Module_Publication_Closure_R1.md"
)
R4_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r4-name-resolution-modules-publication-closure-receipt.json"
)
R4_INDEPENDENT_TEST_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r4-name-resolution-modules-independent-test-verification.json"
)
R4_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R4-NAME-RESOLUTION-MODULES-PUBLICATION-CLOSURE"
)
R8_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R8_Ownership_Canonical_Promotion_"
    "Publication_Closure_R1.md"
)
R8_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r8-ownership-canonical-promotion-publication-closure-receipt.json"
)
R8_INDEPENDENT_TEST_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r8-ownership-canonical-promotion-independent-verification.json"
)
R8_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R8-OWNERSHIP-CANONICAL-PROMOTION-PUBLICATION-CLOSURE"
)
R8_PUBLICATION_CLOSURE_GAP_IDS = [
    "IR-OWN-P0-012",
    "IR-OWN-P0-013",
    "IR-OWN-P0-014",
]
R9_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R9_Diagnostic_Dispatch_Publication_Closure_R1.md"
)
R9_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r9-diagnostic-dispatch-publication-closure-receipt.json"
)
R9_INDEPENDENT_TEST_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r9-diagnostic-dispatch-independent-verification.json"
)
R9_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R9-DIAGNOSTIC-DISPATCH-PUBLICATION-CLOSURE"
)
R9_PUBLICATION_CLOSURE_GAP_IDS = ["IR-DIAG-P0-052"]
R9_PUBLICATION_CLOSURE_REPORT_BYTES = 3844
R9_PUBLICATION_CLOSURE_REPORT_SHA256 = (
    "8df6e949ee1f3ad84e6d96770adecd37ff8d795895760aae6b0d1692f63e9016"
)
R9_PUBLICATION_CLOSURE_RECEIPT_BYTES = 5760
R9_PUBLICATION_CLOSURE_RECEIPT_SHA256 = (
    "c2fa4aed68aa271ad91159515503143a316766590239bd01e62652db5bf142b3"
)
R9_INDEPENDENT_TEST_VERIFICATION_BYTES = 4251
R9_INDEPENDENT_TEST_VERIFICATION_SHA256 = (
    "531fccf149c618ba19bbaaaecca23dfaff19449b32ac2955889f6d0743042e08"
)
R10_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R10_HIR_MIR_Machine_Contract_Publication_Closure_R1.md"
)
R10_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r10-hir-mir-machine-contract-publication-closure-receipt.json"
)
R10_INDEPENDENT_TEST_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r10-hir-mir-machine-contract-independent-verification.json"
)
R10_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R10-HIR-MIR-MACHINE-CONTRACT-PUBLICATION-CLOSURE"
)
R10_PUBLICATION_CLOSURE_GAP_IDS = ["IR-OWN-P0-015"]
R10_PUBLICATION_CLOSURE_REPORT_BYTES = 3768
R10_PUBLICATION_CLOSURE_REPORT_SHA256 = (
    "96e8940c851834c82ab5f85cb29b0052e89e38988e2f86aa3965fb6cfeaef5e2"
)
R10_PUBLICATION_CLOSURE_RECEIPT_BYTES = 6503
R10_PUBLICATION_CLOSURE_RECEIPT_SHA256 = (
    "09dd8c1bb031c9cf2e93374ddc1c2b3754a6f138cd2b5c29ec71aabddd18d689"
)
R10_INDEPENDENT_TEST_VERIFICATION_BYTES = 4324
R10_INDEPENDENT_TEST_VERIFICATION_SHA256 = (
    "0a5bec964f1cc622292b2d14645a17d747074238dfd779e1ed38d355395eb7d8"
)
R25_R27_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R25_R27_Frontend_Trace_Diagnostic_Grammar_Topology_"
    "Publication_Closure_R1.md"
)
R25_R27_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r25-r27-frontend-trace-diagnostic-grammar-topology-publication-"
    "closure-receipt.json"
)
R25_R27_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R25-R27-FRONTEND-TRACE-DIAGNOSTIC-GRAMMAR-TOPOLOGY-"
    "PUBLICATION-CLOSURE"
)
R25_R27_PUBLICATION_CLOSURE_GAP_IDS = [
    "IR-TRACE-P1-009",
    "IR-TRACE-P1-010",
    "IR-TRACE-P2-011",
    "IR-FE-P1-035",
    "IR-FE-P1-039",
]
R41_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R41_Actor_Protocol_Direct_Conformance_"
    "Publication_Closure_R1.md"
)
R41_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r41-actor-protocol-direct-conformance-publication-closure-receipt.json"
)
R41_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r41-actor-protocol-direct-conformance-independent-verification.json"
)
R41_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R41-ACTOR-PROTOCOL-DIRECT-CONFORMANCE-PUBLICATION-CLOSURE"
)
R41_PUBLICATION_CLOSURE_GAP_IDS = [
    "IR-ACTOR-P0-001",
    "IR-ACTOR-P0-002",
    "IR-ACTOR-P0-004",
    "IR-ACTOR-P1-003",
]
R23_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R43_R23_Actor_Protocol_Binding_Descriptor_"
    "Publication_Closure_R1.md"
)
R23_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r23-actor-protocol-binding-publication-closure-receipt.json"
)
R23_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r23-actor-protocol-binding-independent-verification.json"
)
R23_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R43-R23-ACTOR-PROTOCOL-BINDING-PUBLICATION-CLOSURE"
)
R23_PUBLICATION_CLOSURE_GAP_IDS = ["IR-ACTOR-P1-006"]
R46_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R46_Managed_Root_Runtime_Fusion_"
    "Publication_Closure_R1.md"
)
R46_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r46-managed-root-runtime-fusion-publication-closure-receipt.json"
)
R46_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r46-managed-root-runtime-fusion-independent-verification.json"
)
R46_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R46-MANAGED-ROOT-RUNTIME-FUSION-PUBLICATION-CLOSURE"
)
R46_PUBLICATION_CLOSURE_GAP_IDS = [
    "IR-OWN-P0-017",
    "IR-OWN-P1-025",
    "IR-OWN-P1-026",
]
R47_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R47_Ownership_Contract_Fusion_"
    "Publication_Closure_R1.md"
)
R47_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r47-ownership-contract-fusion-publication-closure-receipt.json"
)
R47_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r47-ownership-contract-fusion-independent-verification.json"
)
R47_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R47-OWNERSHIP-CONTRACT-FUSION-PUBLICATION-CLOSURE"
)
R47_PUBLICATION_CLOSURE_GAP_IDS = [
    *(f"IR-OWN-P1-{index:03d}" for index in range(18, 25)),
]
R74_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R48_R74_Implementation_Readiness_Trace_"
    "Publication_Closure_R1.md"
)
R74_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r48-r74-implementation-readiness-trace-publication-closure-receipt.json"
)
R74_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r48-r74-implementation-readiness-trace-independent-verification.json"
)
R74_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R48-R74-IMPLEMENTATION-READINESS-TRACE-PUBLICATION-CLOSURE"
)
R75_SEMANTIC_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R75_Actor_Cranelift_Projection_Rebase_R1.md"
)
R75_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R75_Actor_Cranelift_Projection_Rebase_"
    "Publication_Closure_R1.md"
)
R76_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_R76_Global_Implementation_Target_Trace_"
    "Publication_Closure_R1.md"
)
R76_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "r76-global-implementation-target-trace-publication-closure-receipt.json"
)
R76_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "r76-global-implementation-target-trace-independent-verification.json"
)
R76_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-R76-GLOBAL-IMPLEMENTATION-TARGET-TRACE-PUBLICATION-CLOSURE"
)
G4_PUBLICATION_CLOSURE_REPORT = (
    "governance/reports/"
    "Design_Deeplus_G4_Independent_Implementation_Readiness_"
    "Publication_Closure_R1.md"
)
G4_PUBLICATION_CLOSURE_RECEIPT = (
    "release/evidence/"
    "g4-independent-implementation-readiness-publication-closure-receipt.json"
)
G4_INDEPENDENT_VERIFICATION_RECEIPT = (
    "release/evidence/"
    "g4-independent-implementation-readiness-independent-verification.json"
)
G4_PUBLICATION_CLOSURE_DECISION_ID = (
    "DSGN-CURRENT-G4-INDEPENDENT-IMPLEMENTATION-READINESS-PUBLICATION-CLOSURE"
)
R4_PUBLICATION_CLOSURE_GAP_IDS = [
    "IR-RES-P0-040",
    "IR-RES-P0-041",
    *(f"IR-MOD-P1-{index:03d}" for index in range(42, 48)),
    "IR-RES-P1-048",
    "IR-RES-P1-049",
    "IR-TRACE-P1-050",
    "IR-TRACE-P2-051",
]
R4_PUBLICATION_CLOSURE_GAP_SEVERITIES = {
    "IR-RES-P0-040": "P0",
    "IR-RES-P0-041": "P0",
    **{f"IR-MOD-P1-{index:03d}": "P1" for index in range(42, 48)},
    "IR-RES-P1-048": "P1",
    "IR-RES-P1-049": "P1",
    "IR-TRACE-P1-050": "P1",
    "IR-TRACE-P2-051": "P2",
}
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
    "TCS-R1-POS-003": "9c590a40ab916786032584ffa2fd94b900a9d97194293710f15c8a63fb892635",
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
    "TCS-R1-NEG-010": "a2c6c0761757bb0d2fc74330ddb9af587798a29f5c5d3f15b96df8e4d69f8dde",
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
    "TRN-R1-NEG-058": "aa427e0788a031f819d374dde5ac03eaa0f0ace759edd5319f3c44e70c80f0f5",
}
SUCCESSOR_ACTION_IDS = EXPECTED_ACTION_IDS + [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
R77_ACTION_IDS = [
    *EXPECTED_ACTION_IDS,
    "R77-A006",
    *SUCCESSOR_ACTION_IDS[len(EXPECTED_ACTION_IDS):],
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
R10_SEMANTIC_DELTA_PATHS = {
    "current/authority-map.yaml",
    "current/current-pointer.json",
    "current/decision-index.yaml",
    "current/language-version.toml",
    "decisions/language/Design_Deeplus_HIR_MIR_Machine_Contract_R1.md",
    "decisions/language/current-decisions.json",
    "docs/grammar-reference/18-evaluation-ownership-mir-and-backends.md",
    "docs/grammar-reference/SUMMARY.md",
    "docs/grammar-reference/appendices/a-production-index.md",
    "docs/grammar-reference/appendices/b-token-keyword-operator-index.md",
    "docs/grammar-reference/appendices/c-feature-status-index.md",
    "docs/grammar-reference/appendices/d-diagnostic-predicate-index.md",
    "docs/grammar-reference/appendices/e-prelude-example-index.md",
    "docs/grammar-reference/appendices/f-coverage-report.md",
    "docs/grammar-reference/coverage-manifest.json",
    "docs/tutorial/part-11-modules-system/11-05-hir-mir-backends-tooling.md",
    "docs/tutorial/coverage-manifest.json",
    "docs/tutorial/coverage-report.md",
    "migration/catalog-reassembly.json",
    "release/source-tree-manifest.json",
    "rfcs/DP-RFC-0002-current-hir-h1.md",
    "schemas/language/canonical-hir-h1.schema.json",
    "schemas/language/deeplus-mir.schema.json",
    "schemas/language/grammar-reference-coverage.schema.json",
    "schemas/language/grammar-reference-coverage.schema.json",
    "schemas/language/hir-h1-current-mir-bridge-fixtures.schema.json",
    "schemas/language/hir-mir-lowering-row.schema.json",
    "schemas/language/hir-mir-machine-contract-fixtures.schema.json",
    "schemas/language/mir-capability-receipt.schema.json",
    "schemas/language/tutorial-coverage.schema.json",
    "spec/contracts/grammar-reference-r1.json",
    "spec/contracts/hir-h1-current-mir-bridge.json",
    "spec/contracts/hir-h1-identity-catalog.json",
    "spec/contracts/hir-mir-lowering-registry.json",
    "spec/contracts/hir-mir-machine-diagnostic-contract.json",
    "spec/contracts/language-coherence-current-integrity-r1.json",
    "spec/contracts/mir-machine-registry.json",
    "spec/contracts/tutorial-r1.json",
    "spec/contracts/unified-call-actor-transport.json",
    "spec/diagnostics/catalog/catalog-metadata.json",
    "spec/diagnostics/catalog/chunks/part-0028.json",
    "spec/features/catalog/chunks/part-0021.json",
    "spec/frontend/frontend-model.json",
    "spec/language.md",
    "spec/mir/semantics.md",
    "spec/patterns/pattern-lowering.json",
    "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json",
    "tests/fixtures/current/hir-mir-machine-contract-r1.json",
    "tools/generators/generate_grammar_reference.py",
    "tools/generators/generate_language_coherence_current_integrity.py",
    "tools/generators/generate_tutorial.py",
    "tools/generators/refresh_source_tree_manifest.py",
    "tools/validators/run_r5_ownership_decision_mutation_tests.py",
    "tools/validators/validate_hir_mir_machine_contract.py",
    "tools/validators/validate_workspace.py",
}
R38_SEMANTIC_DELTA_PATHS = {
    "schemas/language/canonical-hir-h1.schema.json",
    "schemas/language/continuation-interface-fixtures-r1.schema.json",
    "schemas/language/continuation-interface-r1.schema.json",
    "schemas/language/continuation-receipt-r1.schema.json",
    "schemas/language/deeplus-mir.schema.json",
    "schemas/language/hir-mir-lowering-row.schema.json",
    "schemas/language/hir-mir-machine-contract-fixtures.schema.json",
    "schemas/language/suspension-frame-responsibility.schema.json",
    "spec/contracts/continuation-interface-r1.json",
    "spec/contracts/diagnostic-dispatch-closure-r1.json",
    "spec/contracts/grammar-reference-r1.json",
    "spec/contracts/hir-h1-current-mir-bridge.json",
    "spec/contracts/hir-h1-identity-catalog.json",
    "spec/contracts/hir-mir-lowering-registry.json",
    "spec/contracts/hir-mir-machine-diagnostic-contract.json",
    "spec/contracts/mir-machine-registry.json",
    "spec/contracts/language-coherence-current-integrity-r1.json",
    "spec/contracts/suspension-frame-responsibility-r1.json",
    "spec/contracts/tutorial-r1.json",
    "spec/diagnostics/catalog/catalog-metadata.json",
    "spec/diagnostics/catalog/chunks/part-0030.json",
    "spec/diagnostics/relations/catalog-metadata.json",
    "spec/diagnostics/relations/chunks/part-0010.json",
    "spec/features/catalog/chunks/part-0021.json",
    "spec/language.md",
    "spec/mir/semantics.md",
    "spec/types/predicates/catalog-metadata.json",
    "spec/types/predicates/chunks/part-0022.json",
    "spec/types/type-system.md",
    "tests/conformance/checker-predicates/catalog-metadata.json",
    "tests/conformance/checker-predicates/chunks/part-0033.json",
    "tests/fixtures/current/continuation-interface-r1.json",
    "tests/fixtures/current/hir-mir-machine-contract-r1.json",
    "tests/fixtures/current/suspension-frame-responsibility-r1.json",
    "tools/generators/generate_language_coherence_current_integrity.py",
    "tools/generators/generate_grammar_reference.py",
    "tools/generators/generate_tutorial.py",
    "tools/generators/rebind_continuation_interface.py",
    "tools/generators/rebind_r20_suspension_frame_machine_contract.py",
    "tools/validators/validate_construction_cleanup_state.py",
    "tools/validators/run_diagnostic_dispatch_closure_tests.py",
    "tools/validators/run_r5_ownership_decision_mutation_tests.py",
    "tools/validators/validate_continuation_interface.py",
    "tools/validators/validate_hir_mir_machine_contract.py",
    "tools/validators/validate_suspension_frame_responsibility.py",
    "tools/validators/validate_workspace.py",
}
EXPR_AUTHORITY = "governance/policies/management-policy.yaml#EXPR-001"
EXPR_DIGEST = "42250c554d2d5f9cfb29bbd3668bed40ec1390fce658ac1804f7c6de29b1ac39"
EXPR_FIELDS = {
    "clause_id": "EXPR-001",
    "statement": "Expressiveness means translating programmer intent easily, consistently, and responsibly.",
    "restriction_rule": "A restriction must provide an expression-preserving alternative or state an explicit impossibility case.",
    "visibility_rule": "Responsibility, ownership, effects, failure, cleanup, suspension, authority, provider lookup, call domain, and public API residue remain visible.",
}
R4_NRM_PRECEDENCE = [
    (
        "PackageModuleSourceGraphAdmitted",
        "PACKAGE_MODULE_SOURCE_GRAPH_INVALID",
        (
            "PACKAGE_TARGET_MISSING",
            "PACKAGE_BINDING_AMBIGUOUS",
            "PACKAGE_CYCLE",
            "MODULE_MAPPING_MISMATCH",
        ),
    ),
    (
        "ModuleItemSkeletonSetAdmitted",
        "MODULE_ITEM_SKELETON_CONFLICT",
        (
            "DUPLICATE_DECLARATION",
            "OVERLOAD_SLOT_KEY_COLLISION",
            "MODULE_CONTRIBUTION_CONFLICT",
        ),
    ),
    (
        "DependencyInterfaceBindingClosed",
        "DEPENDENCY_INTERFACE_BINDING_INVALID",
        (
            "IMPORT_TARGET_NOT_FOUND",
            "IMPORT_TARGET_AMBIGUOUS",
            "IMPORT_ALIAS_COLLISION",
            "EXPORT_TARGET_NOT_FOUND",
            "EXPORT_IDENTITY_MISMATCH",
            "REEXPORT_CYCLE",
            "EXPORT_VISIBILITY_LEAK",
            "MODULE_SIGNATURE_MISMATCH",
            "FACADE_WIDENING",
            "STATIC_DEPENDENCY_CYCLE",
            "STALE_DEPENDENCY_RECEIPT",
        ),
    ),
    (
        "ResolverScopeTreeAdmitted",
        "RESOLVER_SCOPE_TREE_INVALID",
        (
            "SAME_FRAME_DUPLICATE",
            "PARAMETER_BODY_LOCAL_COLLISION",
            "IMPORT_LOCAL_COLLISION",
            "ILLEGAL_CROSS_FRAME_OVERLOAD_MERGE",
            "NAME_ACTIVATION_ENV_CONFLATION",
            "SCOPE_ESCAPE",
            "FAILED_PATTERN_PROBE_BINDING_LEAK",
        ),
    ),
    (
        "ReferenceCandidateSetResolved",
        "REFERENCE_CANDIDATE_SET_INVALID",
        (
            "ZERO_CANDIDATES",
            "MULTIPLE_SAME_TIER",
            "WRONG_NAMESPACE",
            "STATIC_PATH_UNRESOLVED",
            "STATIC_PATH_AMBIGUOUS",
        ),
    ),
    (
        "ReferenceVisibilityActivationAdmitted",
        "REFERENCE_VISIBILITY_OR_ACTIVATION_VIOLATION",
        (
            "CANDIDATE_NOT_VISIBLE",
            "ACTIVATION_SCOPE_ESCAPE",
            "ACTIVATION_IDENTITY_MISMATCH",
            "MEMBER_VISIBILITY_DOMAIN",
            "API_VISIBILITY_LEAK",
            "WITNESS_ORIGIN_INVALID",
        ),
    ),
    (
        "ResolvedNoncallReferenceSelected",
        "NONCALL_REFERENCE_SELECTION_FAILED",
        (
            "ZERO_AFTER_FILTER",
            "MULTIPLE_AFTER_FILTER",
            "ORDER_TIEBREAKER_REQUIRED",
        ),
    ),
    (
        "ResolverHirSealAdmitted",
        "RESOLVER_HIR_SEAL_INCOMPLETE",
        (
            "UNBOUND_PRIMARY",
            "UNRESOLVED_COUNT_NONZERO",
            "CANDIDATE_SET_COUNT_NONZERO",
            "MISSING_TYPED_ID",
            "MISSING_VISIBILITY_PROOF",
            "RUNTIME_RELOOKUP_RESIDUE",
        ),
    ),
    (
        "ModuleInterfaceDigestVerified",
        "MODULE_INTERFACE_DIGEST_MISMATCH",
        (
            "MISSING_EXPORT_EDGE",
            "INTERFACE_DIGEST_MISMATCH",
        ),
    ),
]
R4_NRM_TARGET_FILES = (
    "spec/diagnostics/catalog/chunks/part-0007.json",
    "spec/diagnostics/catalog/chunks/part-0011.json",
    "spec/diagnostics/catalog/chunks/part-0018.json",
    "spec/diagnostics/catalog/chunks/part-0027.json",
    "spec/diagnostics/relations/chunks/part-0001.json",
    "spec/diagnostics/relations/chunks/part-0002.json",
    "spec/diagnostics/relations/chunks/part-0007.json",
    "spec/types/predicates/chunks/part-0008.json",
    "spec/types/predicates/chunks/part-0015.json",
    "spec/types/predicates/chunks/part-0018.json",
    "tests/conformance/checker-predicates/chunks/part-0015.json",
    "tests/conformance/checker-predicates/chunks/part-0026.json",
    "tests/conformance/checker-predicates/chunks/part-0028.json",
)
R4_NRM_GAP_IDS = (
    "IR-RES-P0-040",
    "IR-RES-P0-041",
    "IR-MOD-P1-042",
    "IR-MOD-P1-043",
    "IR-MOD-P1-044",
    "IR-MOD-P1-045",
    "IR-MOD-P1-046",
    "IR-MOD-P1-047",
    "IR-RES-P1-048",
    "IR-RES-P1-049",
    "IR-TRACE-P1-050",
    "IR-TRACE-P2-051",
)
R4_NRM_ACCEPTANCE_TEST_IDS = tuple(
    f"IR-R4-GAP-{index:02d}-{suffix}"
    for index in range(1, 13)
    for suffix in ("P", "B", "N")
)
R4_NRM_ACCEPTANCE_ORACLE_SHA256 = (
    "454cbbdfaa62cd8892c93c7eb812e9ad1b21dd4eceb3fb3711bee48728b32be3"
)
R4_NRM_PREDICATE_FIXTURE_TUPLE_SHA256 = (
    "508990469db894889f6952f84836c11744e13a44f0d7cb0a624c4766b9258d19"
)
R4_NRM_ACCEPTANCE_ARTIFACT_REFS = {
    ("IR-RES-P0-040", "positive"): (
        "schemas/language/resolver-graph.schema.json",
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-RES-P0-040", "boundary"): (
        "spec/contracts/name-resolution-modules-current.json",
        "spec/contracts/hir-h1-current-mir-bridge.json",
    ),
    ("IR-RES-P0-040", "negative"): (
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-RES-P0-041", "positive"): (
        "schemas/language/method-extension-resolution-trace-schema.json",
    ),
    ("IR-RES-P0-041", "boundary"): (
        "schemas/language/method-extension-resolution-trace-schema.json",
    ),
    ("IR-RES-P0-041", "negative"): (
        "schemas/language/method-extension-resolution-trace-schema.json",
    ),
    ("IR-MOD-P1-042", "positive"): (
        "schemas/language/package-module-source-graph.schema.json",
        "schemas/language/source-role-carrier.schema.json",
    ),
    ("IR-MOD-P1-042", "boundary"): (
        "schemas/language/package-module-source-graph.schema.json",
        (
            "schemas/language/"
            "module-compilation-dependency-receipt.schema.json"
        ),
    ),
    ("IR-MOD-P1-042", "negative"): (
        "schemas/language/package-module-source-graph.schema.json",
    ),
    ("IR-MOD-P1-043", "positive"): (
        "schemas/language/resolver-graph.schema.json",
        (
            "schemas/language/"
            "module-compilation-dependency-receipt.schema.json"
        ),
    ),
    ("IR-MOD-P1-043", "boundary"): (
        "spec/contracts/name-resolution-modules-current.json",
    ),
    ("IR-MOD-P1-043", "negative"): (
        "schemas/language/resolver-graph.schema.json",
    ),
    ("IR-MOD-P1-044", "positive"): (
        "schemas/language/package-module-source-graph.schema.json",
    ),
    ("IR-MOD-P1-044", "boundary"): (
        "schemas/language/package-module-source-graph.schema.json",
    ),
    ("IR-MOD-P1-044", "negative"): (
        "schemas/language/package-module-source-graph.schema.json",
    ),
    ("IR-MOD-P1-045", "positive"): (
        "schemas/language/module-visibility-closure.schema.json",
        (
            "schemas/language/"
            "top-level-type-visibility-descriptor.schema.json"
        ),
    ),
    ("IR-MOD-P1-045", "boundary"): (
        "schemas/language/module-visibility-closure.schema.json",
    ),
    ("IR-MOD-P1-045", "negative"): (
        "schemas/language/module-visibility-closure.schema.json",
    ),
    ("IR-MOD-P1-046", "positive"): (
        "schemas/language/module-api-digest.schema.json",
        (
            "schemas/language/"
            "module-compilation-dependency-receipt.schema.json"
        ),
        (
            "schemas/language/"
            "module-source-contribution-projection.schema.json"
        ),
        "schemas/language/module-compilation-receipt.schema.json",
        (
            "tests/fixtures/current/"
            "module-compilation-artifact-relations-r1.json"
        ),
    ),
    ("IR-MOD-P1-046", "boundary"): (
        "schemas/language/module-api-digest.schema.json",
        "schemas/language/module-implementation-digest.schema.json",
        (
            "schemas/language/"
            "module-source-contribution-projection.schema.json"
        ),
        "schemas/language/module-compilation-receipt.schema.json",
        (
            "tests/fixtures/current/"
            "module-compilation-artifact-relations-r1.json"
        ),
    ),
    ("IR-MOD-P1-046", "negative"): (
        "schemas/language/module-api-digest.schema.json",
        (
            "schemas/language/"
            "module-source-contribution-projection.schema.json"
        ),
        "schemas/language/module-compilation-receipt.schema.json",
        (
            "tests/fixtures/current/"
            "module-compilation-artifact-relations-r1.json"
        ),
    ),
    ("IR-MOD-P1-047", "positive"): (
        "schemas/language/module-initialization-plan.schema.json",
    ),
    ("IR-MOD-P1-047", "boundary"): (
        "schemas/language/package-module-source-graph.schema.json",
    ),
    ("IR-MOD-P1-047", "negative"): (
        "schemas/language/module-initialization-plan.schema.json",
        "schemas/language/package-module-source-graph.schema.json",
    ),
    ("IR-RES-P1-048", "positive"): (
        "schemas/language/resolver-graph.schema.json",
    ),
    ("IR-RES-P1-048", "boundary"): (
        "schemas/language/resolver-graph.schema.json",
    ),
    ("IR-RES-P1-048", "negative"): (
        "schemas/language/resolver-graph.schema.json",
    ),
    ("IR-RES-P1-049", "positive"): (
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-RES-P1-049", "boundary"): (
        "spec/contracts/name-resolution-modules-current.json",
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-RES-P1-049", "negative"): (
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-TRACE-P1-050", "positive"): (
        "schemas/language/resolver-trace.schema.json",
        "spec/contracts/name-resolution-modules-current.json",
    ),
    ("IR-TRACE-P1-050", "boundary"): (
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-TRACE-P1-050", "negative"): (
        "schemas/language/resolver-trace.schema.json",
    ),
    ("IR-TRACE-P2-051", "positive"): (
        "spec/contracts/name-resolution-modules-current.json",
    ),
    ("IR-TRACE-P2-051", "boundary"): (
        "spec/contracts/name-resolution-modules-current.json",
    ),
    ("IR-TRACE-P2-051", "negative"): (
        "spec/contracts/name-resolution-modules-current.json",
    ),
}
R4_NRM_STAGE_SEQUENCE = tuple(
    row[0] for row in R4_NRM_PRECEDENCE
)
R4_NRM_INTEGRATED_PATHS = (
    "spec/contracts/name-resolution-modules-current.json",
    "schemas/language/name-resolution-modules-current-fixtures.schema.json",
    "tests/fixtures/current/name-resolution-modules-current-r1.json",
    "schemas/language/package-module-source-graph.schema.json",
    "schemas/language/source-role-carrier.schema.json",
    "schemas/language/module-compilation-dependency-receipt.schema.json",
    "schemas/language/module-compilation-receipt.schema.json",
    "schemas/language/module-implementation-digest.schema.json",
    "schemas/language/module-initialization-plan.schema.json",
    "schemas/language/module-source-contribution-projection.schema.json",
    "tests/fixtures/current/module-compilation-artifact-relations-r1.json",
    "schemas/language/module-visibility-closure.schema.json",
    "schemas/language/top-level-type-visibility-descriptor.schema.json",
    "schemas/language/resolver-graph.schema.json",
    "schemas/language/resolver-trace.schema.json",
    "schemas/language/method-extension-resolution-trace-schema.json",
    "schemas/language/module-api-digest.schema.json",
    "tests/fixtures/imported/module-api-digest-fixtures.json",
    "spec/contracts/hir-h1-current-mir-bridge.json",
    "schemas/language/hir-h1-current-mir-bridge-fixtures.schema.json",
    "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json",
    "spec/frontend/frontend-model.json",
)
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


def has_non_unicode_scalar(value: Any) -> bool:
    """Return whether a JSON value contains an unpaired UTF-16 surrogate."""

    if isinstance(value, str):
        return any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    if isinstance(value, dict):
        return any(
            has_non_unicode_scalar(key)
            or has_non_unicode_scalar(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(has_non_unicode_scalar(child) for child in value)
    return False


def is_canonical_json_value(value: Any) -> bool:
    """Return whether a value is in the closed R4 canonical JSON domain."""

    if value is None or type(value) in {bool, int}:
        return True
    if isinstance(value, str):
        return not has_non_unicode_scalar(value)
    if isinstance(value, list):
        return all(is_canonical_json_value(child) for child in value)
    if isinstance(value, dict):
        return all(
            type(key) is str
            and not has_non_unicode_scalar(key)
            and is_canonical_json_value(child)
            for key, child in value.items()
        )
    return False


def canonical_sha(value: Any) -> str | None:
    """Hash the closed R4 canonical JSON domain without coercion or crashes."""

    if not is_canonical_json_value(value):
        return None
    try:
        data = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError):
        return None
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


def r4_nrm_contract_results(
    root: Path,
) -> list[tuple[bool, str, str]]:
    """Validate the bounded R4 name-resolution/module diagnostic contract."""

    results: list[tuple[bool, str, str]] = []
    documents: dict[str, list[dict[str, Any]]] = {}

    def record(condition: bool, code: str, detail: str) -> None:
        results.append((bool(condition), code, detail))

    for relative in R4_NRM_TARGET_FILES:
        path = root / relative
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, list) or not all(
                isinstance(row, dict) for row in value
            ):
                raise ValueError("expected an array of objects")
            documents[relative] = value
            record(
                path.stat().st_size <= 61440,
                "R4_NRM_SHARD_SIZE",
                f"{relative} bytes={path.stat().st_size}",
            )
        except Exception as exc:  # noqa: BLE001
            documents[relative] = []
            record(False, "R4_NRM_JSON_CLOSURE", f"{relative}: {exc}")

    try:
        promotion_contract = json.loads(
            (
                root
                / "spec/contracts/name-resolution-modules-current.json"
            ).read_text(encoding="utf-8")
        )
        integrated_cases = json.loads(
            (
                root
                / "tests/fixtures/current/"
                "name-resolution-modules-current-r1.json"
            ).read_text(encoding="utf-8")
        ).get("cases", [])
    except Exception as exc:  # noqa: BLE001
        promotion_contract = {}
        integrated_cases = []
        record(
            False,
            "R4_NRM_PROMOTION_METADATA",
            f"integrated promotion metadata: {exc}",
        )

    precedence_ids = [row[0] for row in R4_NRM_PRECEDENCE]
    primary_by_predicate = {row[0]: row[1] for row in R4_NRM_PRECEDENCE}
    reasons_by_predicate = {
        row[0]: set(row[2]) for row in R4_NRM_PRECEDENCE
    }
    negative_reason_by_predicate = {
        "PackageModuleSourceGraphAdmitted": "PACKAGE_TARGET_MISSING",
        "ModuleItemSkeletonSetAdmitted": "MODULE_CONTRIBUTION_CONFLICT",
        "DependencyInterfaceBindingClosed": "IMPORT_TARGET_NOT_FOUND",
        "ResolverScopeTreeAdmitted": "IMPORT_LOCAL_COLLISION",
        "ReferenceCandidateSetResolved": "ZERO_CANDIDATES",
        "ReferenceVisibilityActivationAdmitted": "API_VISIBILITY_LEAK",
        "ResolvedNoncallReferenceSelected": "MULTIPLE_AFTER_FILTER",
        "ResolverHirSealAdmitted": "UNRESOLVED_COUNT_NONZERO",
        "ModuleInterfaceDigestVerified": "MISSING_EXPORT_EDGE",
    }

    new_diagnostics = documents[
        "spec/diagnostics/catalog/chunks/part-0027.json"
    ]
    observed_diagnostic_ids = [
        row.get("diagnostic_id") for row in new_diagnostics
    ]
    expected_diagnostic_ids = [
        primary_by_predicate[predicate_id]
        for predicate_id in precedence_ids
    ]
    record(
        observed_diagnostic_ids
        == expected_diagnostic_ids
        + [
            "PLACE_STATE_JOIN_MISMATCH",
            "EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED",
            "EFFECT_ROW_SUBSUMPTION_NOT_ADMITTED",
        ],
        "R4_NRM_DIAGNOSTIC_SET",
        f"observed={observed_diagnostic_ids}",
    )
    record(
        all(
            row.get("diagnostic_status") == "active"
            and row.get("diagnostic_maturity") == "active"
            and row.get("diagnostic_class") == "current_source"
            and row.get("emission_domain") == "source"
            and row.get("stage") == "checker"
            and row.get("severity") == "error"
            and row.get("primary_source") == "spec/language.md"
            and row.get("product_support") == "NOT_RUN"
            for row in new_diagnostics
        ),
        "R4_NRM_DIAGNOSTIC_CONTRACT",
        f"rows={len(new_diagnostics)}",
    )

    new_relations = documents[
        "spec/diagnostics/relations/chunks/part-0007.json"
    ]
    expected_primary_relations = [
        {
            "violation_id": f"{predicate_id}:default",
            "predicate_id": predicate_id,
            "diagnostic_id": primary_by_predicate[predicate_id],
            "relation": "primary",
        }
        for predicate_id in precedence_ids
    ]
    record(
        new_relations[:9] == expected_primary_relations
        and len(new_relations) == 12,
        "R4_NRM_PRIMARY_RELATIONS",
        f"rows={len(new_relations)} primary={len(new_relations[:9])}",
    )
    expected_compat_relation = {
        "violation_id": None,
        "predicate_id": "MethodExtensionResolutionAdmitted",
        "diagnostic_id": "EXTENSION_SHADOWED_BY_MEMBER_COMPAT",
        "relation": "historical",
        "replacement": "MEMBER_EXTENSION_COLLISION",
    }
    expected_r8_ownership_secondary_relations = [
        {
            "violation_id": None,
            "predicate_id": "OwnershipModeAdmitted",
            "diagnostic_id": "INOUT_ALIAS_CONFLICT",
            "relation": "secondary",
        },
        {
            "violation_id": None,
            "predicate_id": "OwnershipModeAdmitted",
            "diagnostic_id": "PLACE_STATE_JOIN_MISMATCH",
            "relation": "secondary",
        },
    ]
    record(
        len(new_relations) == 12
        and new_relations[9] == expected_compat_relation
        and new_relations[10:]
        == expected_r8_ownership_secondary_relations,
        "R4_NRM_COLLISION_RELATIONS",
        (
            f"historical={new_relations[9:10] or []} "
            f"ownership_secondary={new_relations[10:]}"
        ),
    )

    new_predicates = documents[
        "spec/types/predicates/chunks/part-0018.json"
    ]
    observed_predicate_ids = [
        row.get("predicate_id") for row in new_predicates
    ]
    expected_dependency_predicates = {
        predicate_id: precedence_ids[:index]
        + (
            ["MemberVisibilityAdmitted"]
            if predicate_id == "ReferenceVisibilityActivationAdmitted"
            else []
        )
        for index, predicate_id in enumerate(precedence_ids)
    }
    record(
        observed_predicate_ids == precedence_ids
        and all(
            row.get("dependency_predicates")
            == expected_dependency_predicates[row.get("predicate_id")]
            for row in new_predicates
        ),
        "R4_NRM_PRECEDENCE",
        f"observed={observed_predicate_ids}",
    )
    reason_contract = True
    predicate_contract = True
    for predicate_id, row in zip(precedence_ids, new_predicates):
        diagnostic_id = primary_by_predicate[predicate_id]
        dispatch = row.get("diagnostic_dispatch", {})
        reason_contract = reason_contract and (
            isinstance(dispatch, dict)
            and set(dispatch) == reasons_by_predicate[predicate_id]
            and set(dispatch.values()) == {diagnostic_id}
        )
        predicate_contract = predicate_contract and (
            row.get("active_primary_diagnostic") == diagnostic_id
            and row.get("diagnostic_refs") == [diagnostic_id]
            and row.get("design_seed_diagnostic_refs") == []
            and row.get("secondary_diagnostics") == []
            and row.get("predicate_maturity") == "design_algorithm"
            and row.get("emission_eligible") is True
            and row.get("execution_receipt") is None
            and row.get("evidence_status")
            == "DESIGN_ALGORITHM_STATIC_NOT_RUN"
            and row.get("positive_fixture_ids")
            == (
                [
                    f"PF-{predicate_id}-POS",
                    f"PF-{predicate_id}-BOUNDARY",
                    "PF-ReferenceVisibilityActivationAdmitted-MEMBER-HASH-POS",
                    "PF-ReferenceVisibilityActivationAdmitted-MEMBER-HASH-BOUNDARY",
                ]
                if predicate_id == "ReferenceVisibilityActivationAdmitted"
                else [
                    f"PF-{predicate_id}-POS",
                    f"PF-{predicate_id}-BOUNDARY",
                ]
            )
            and row.get("negative_fixture_ids")
            == (
                [
                    f"PF-{predicate_id}-NEG",
                    "PF-ReferenceVisibilityActivationAdmitted-MEMBER-HASH-NEG",
                ]
                if predicate_id == "ReferenceVisibilityActivationAdmitted"
                else [f"PF-{predicate_id}-NEG"]
            )
        )
    record(
        reason_contract,
        "R4_NRM_REASON_BINDING",
        f"predicates={len(new_predicates)}",
    )
    record(
        predicate_contract,
        "R4_NRM_PREDICATE_CONTRACT",
        f"predicates={len(new_predicates)}",
    )

    fixtures = documents[
        "tests/conformance/checker-predicates/chunks/part-0028.json"
    ]
    expected_fixture_ids = [
        f"PF-{predicate_id}-{suffix}"
        for predicate_id in precedence_ids
        for suffix in ("POS", "BOUNDARY", "NEG")
    ]
    observed_fixture_ids = [row.get("fixture_id") for row in fixtures]
    record(
        observed_fixture_ids == expected_fixture_ids,
        "R4_NRM_FIXTURE_SET",
        f"rows={len(fixtures)}",
    )
    fixture_binding = True
    fixture_tuple_projection: list[list[Any]] = []
    for row in fixtures:
        predicate_id = row.get("predicate_id")
        fixture_id = row.get("fixture_id", "")
        if predicate_id not in primary_by_predicate:
            fixture_binding = False
            continue
        negative = fixture_id.endswith("-NEG")
        descriptor = row.get("descriptor", {})
        fixture_tuple_projection.append(
            [
                fixture_id,
                descriptor.get("test_class"),
                descriptor.get("scenario"),
                descriptor.get("expected_outcome"),
                row.get("rule_seed"),
                row.get("execution_status"),
            ]
        )
        fixture_binding = fixture_binding and (
            row.get("execution_status") == "DESIGN_STATIC_NOT_RUN"
            and row.get("baseline") == "0.1.2-baseline.r51f3"
            and row.get("row_schema_version")
            == "deeplus.checker-predicate-fixture/r51f3"
            and row.get("descriptor_v5", {}).get("schema")
            == "deeplus.rcts-v5/descriptor"
            and (
                (
                    row.get("fixture_kind") == "concrete_negative"
                    and row.get("expected") == "rejected"
                    and row.get("expected_primary_diagnostic")
                    == primary_by_predicate[predicate_id]
                    and row.get("violated_condition")
                    == negative_reason_by_predicate[predicate_id]
                    and descriptor.get("primary_reason")
                    == negative_reason_by_predicate[predicate_id]
                )
                if negative
                else (
                    row.get("fixture_kind") == "concrete_positive"
                    and row.get("expected") == "admitted"
                    and row.get("expected_primary_diagnostic") is None
                    and descriptor.get("primary_reason") is None
                )
            )
        )
    fixture_tuple_sha256 = canonical_sha(fixture_tuple_projection)
    fixture_binding = (
        fixture_binding
        and fixture_tuple_sha256
        == R4_NRM_PREDICATE_FIXTURE_TUPLE_SHA256
    )
    record(
        fixture_binding,
        "R4_NRM_FIXTURE_BINDING",
        (
            f"statically_bound={len(fixtures)}/27 executed=0/27 "
            f"tuple_sha256={fixture_tuple_sha256}"
        ),
    )

    catalog_rows = [
        row
        for relative in (
            "spec/diagnostics/catalog/chunks/part-0007.json",
            "spec/diagnostics/catalog/chunks/part-0011.json",
            "spec/diagnostics/catalog/chunks/part-0018.json",
        )
        for row in documents[relative]
    ]
    collision_ids = {
        "MEMBER_EXTENSION_COLLISION",
        "EXTENSION_SHADOWED_BY_MEMBER_COMPAT",
        "STABLE_MEMBER_EXTENSION_COLLISION",
    }
    collision_catalog = {
        row.get("diagnostic_id"): row
        for row in catalog_rows
        if row.get("diagnostic_id") in collision_ids
    }
    member_collision = collision_catalog.get(
        "MEMBER_EXTENSION_COLLISION", {}
    )
    compatibility_collision = collision_catalog.get(
        "EXTENSION_SHADOWED_BY_MEMBER_COMPAT", {}
    )
    stable_collision = collision_catalog.get(
        "STABLE_MEMBER_EXTENSION_COLLISION", {}
    )
    record(
        set(collision_catalog) == collision_ids
        and member_collision.get("diagnostic_status") == "active"
        and member_collision.get("diagnostic_maturity") == "active"
        and member_collision.get("emission_domain") == "source"
        and "replaced_by" not in member_collision
        and all(
            row.get("diagnostic_status") == "retired"
            and row.get("diagnostic_maturity") == "retired"
            and row.get("emission_domain") == "historical"
            and row.get("replaced_by") == "MEMBER_EXTENSION_COLLISION"
            for row in (compatibility_collision, stable_collision)
        ),
        "R4_NRM_COLLISION_CATALOG",
        f"ids={sorted(collision_catalog)}",
    )

    all_relations = [
        row
        for relative in (
            "spec/diagnostics/relations/chunks/part-0001.json",
            "spec/diagnostics/relations/chunks/part-0002.json",
            "spec/diagnostics/relations/chunks/part-0007.json",
        )
        for row in documents[relative]
    ]
    member_primary_relations = {
        (row.get("violation_id"), row.get("predicate_id"))
        for row in all_relations
        if row.get("diagnostic_id") == "MEMBER_EXTENSION_COLLISION"
        and row.get("relation") == "primary"
    }
    expected_member_primary_relations = {
        (
            "MemberExtensionCollisionPolicyAdmitted:default",
            "MemberExtensionCollisionPolicyAdmitted",
        ),
        (
            "MemberExtensionCollisionRejected:default",
            "MemberExtensionCollisionRejected",
        ),
        (
            "QualifiedExtensionSelectorAdmitted:default",
            "QualifiedExtensionSelectorAdmitted",
        ),
    }
    stable_aliases = [
        row
        for row in all_relations
        if row.get("diagnostic_id") == "STABLE_MEMBER_EXTENSION_COLLISION"
    ]
    compatibility_relations = [
        row
        for row in all_relations
        if row.get("diagnostic_id") == "EXTENSION_SHADOWED_BY_MEMBER_COMPAT"
    ]
    record(
        member_primary_relations == expected_member_primary_relations
        and len(stable_aliases) == 1
        and stable_aliases[0].get("relation") == "alias"
        and stable_aliases[0].get("replacement")
        == "MEMBER_EXTENSION_COLLISION"
        and compatibility_relations == [expected_compat_relation],
        "R4_NRM_COLLISION_RELATIONS",
        (
            f"primary={sorted(member_primary_relations)} "
            f"aliases={len(stable_aliases)} "
            f"historical={len(compatibility_relations)}"
        ),
    )

    existing_predicates = documents[
        "spec/types/predicates/chunks/part-0008.json"
    ]
    existing_predicate_by_id = {
        row.get("predicate_id"): row for row in existing_predicates
    }
    collision_predicate = existing_predicate_by_id.get(
        "MemberExtensionCollisionRejected", {}
    )
    method_predicate = existing_predicate_by_id.get(
        "MethodExtensionResolutionAdmitted", {}
    )
    record(
        collision_predicate.get("active_primary_diagnostic")
        == "MEMBER_EXTENSION_COLLISION"
        and collision_predicate.get("diagnostic_refs")
        == ["MEMBER_EXTENSION_COLLISION"]
        and collision_predicate.get("secondary_diagnostics") == []
        and collision_predicate.get("predicate_maturity")
        == "design_algorithm"
        and collision_predicate.get("emission_eligible") is True
        and method_predicate.get("dependency_predicates")
        == ["MemberExtensionCollisionRejected"]
        and method_predicate.get("predicate_maturity") == "design_seed"
        and method_predicate.get("emission_eligible") is False
        and method_predicate.get("evidence_status")
        == "DESIGN_STATIC_NOT_RUN"
        and method_predicate.get("execution_receipt") is None,
        "R4_NRM_COLLISION_PREDICATES",
        (
            f"collision={collision_predicate.get('predicate_maturity')} "
            f"method={method_predicate.get('predicate_maturity')}"
        ),
    )
    method_decision_text = "\n".join(
        str(step)
        for step in method_predicate.get("decision_procedure", [])
    )
    method_fence_text = "\n".join(
        (
            str(method_predicate.get("output", "")),
            method_decision_text,
            str(method_predicate.get("termination_metric", "")),
            str(method_predicate.get("success_result", "")),
            str(method_predicate.get("evaluation_order", "")),
        )
    )
    forbidden_method_fence_phrases = (
        "commit one statically selected method or extension identity",
        "within an extension-only domain, reject multiple same-tier",
        "OVERLOAD_WINNER_FUNCTION_ID",
        "COMPLETE_GENERIC_SUBSTITUTION",
        "EXPECTED_TYPE_DIRECTED_WINNER",
        "APPLICABILITY_RANK",
        "SPECIFICITY_WINNER",
        "ROW_INFERENCE_RESULT",
        "RETURN_TYPE_ONLY_WINNER",
    )
    deferred_collision_cases = {
        case.get("id"): case.get("expected", {}).get(
            "selected_count_or_null"
        )
        for case in integrated_cases
        if case.get("id")
        in {"IR-R4-RES041-POS", "IR-R4-RES041-BOUND"}
    }
    record(
        "ResolvedOverloadSetRef" in method_fence_text
        and "next cluster" in method_fence_text
        and "selection_deferred" in method_fence_text
        and "selected_count = unspecified_in_R4" in method_fence_text
        and all(
            phrase not in method_fence_text
            for phrase in forbidden_method_fence_phrases
        )
        and deferred_collision_cases
        == {
            "IR-R4-RES041-POS": None,
            "IR-R4-RES041-BOUND": None,
        },
        "R4_NRM_COLLISION_SELECTION_DEFERRED",
        (
            f"method={method_predicate.get('predicate_maturity')} "
            f"selected={deferred_collision_cases}"
        ),
    )

    collision_fixture_rows = documents[
        "tests/conformance/checker-predicates/chunks/part-0015.json"
    ]
    collision_fixtures = {
        row.get("fixture_id"): row
        for row in collision_fixture_rows
        if row.get("predicate_id") == "MemberExtensionCollisionRejected"
    }
    collision_positive = collision_fixtures.get(
        "PF-MemberExtensionCollisionRejected-POS", {}
    )
    collision_negative = collision_fixtures.get(
        "PF-MemberExtensionCollisionRejected-NEG", {}
    )
    collision_positive_descriptor = collision_positive.get("descriptor", {})
    collision_negative_descriptor = collision_negative.get("descriptor", {})
    record(
        set(collision_fixtures)
        == {
            "PF-MemberExtensionCollisionRejected-POS",
            "PF-MemberExtensionCollisionRejected-NEG",
        }
        and collision_positive.get("fixture_kind") == "concrete_positive"
        and collision_positive.get("expected") == "admitted"
        and collision_positive.get("diagnostic_disposition")
        == "no diagnostic"
        and collision_positive.get("execution_status")
        == "DESIGN_STATIC_NOT_RUN"
        and collision_positive_descriptor.get("schema")
        == "deeplus.member-extension-collision-descriptor/r1"
        and collision_positive_descriptor.get("selector_kind") == "ORDINARY"
        and len(
            collision_positive_descriptor.get(
                "applicable_nominal_candidate_ids", []
            )
        )
        == 1
        and all(
            is_typed_id(candidate_id, "MemberId")
            for candidate_id in collision_positive_descriptor.get(
                "applicable_nominal_candidate_ids", []
            )
        )
        and collision_positive_descriptor.get(
            "applicable_active_extension_candidate_ids"
        )
        == []
        and collision_positive_descriptor.get(
            "qualified_extension_id_or_null"
        )
        is None
        and collision_negative.get("fixture_kind") == "concrete_negative"
        and collision_negative.get("expected") == "rejected"
        and collision_negative.get("expected_primary_diagnostic")
        == "MEMBER_EXTENSION_COLLISION"
        and collision_negative.get("diagnostic_disposition")
        == "active primary design algorithm; product NOT_RUN"
        and collision_negative.get("execution_status")
        == "DESIGN_STATIC_NOT_RUN"
        and collision_negative_descriptor.get("schema")
        == "deeplus.member-extension-collision-descriptor/r1"
        and collision_negative_descriptor.get("selector_kind") == "ORDINARY"
        and len(
            collision_negative_descriptor.get(
                "applicable_nominal_candidate_ids", []
            )
        )
        == 1
        and len(
            collision_negative_descriptor.get(
                "applicable_active_extension_candidate_ids", []
            )
        )
        == 1
        and all(
            is_typed_id(candidate_id, "MemberId")
            for candidate_id in collision_negative_descriptor.get(
                "applicable_nominal_candidate_ids", []
            )
        )
        and all(
            is_typed_id(candidate_id, "ExtensionMemberId")
            for candidate_id in collision_negative_descriptor.get(
                "applicable_active_extension_candidate_ids", []
            )
        )
        and collision_negative_descriptor.get(
            "qualified_extension_id_or_null"
        )
        is None
        and collision_predicate.get("input_descriptor")
        == "MemberExtensionCollisionDescriptorR1"
        and collision_predicate.get("input_descriptor_schema")
        == (
            "schemas/language/"
            "method-extension-resolution-trace-schema.json"
            "#/$defs/memberExtensionCollisionDescriptor"
        )
        and collision_predicate.get("descriptor_axes")
        == [
            "selector_kind",
            "applicable_nominal_candidate_ids",
            "applicable_active_extension_candidate_ids",
            "qualified_extension_id_or_null",
        ],
        "R4_NRM_COLLISION_FIXTURES",
        (
            f"rows={sorted(collision_fixtures)} "
            "positive_selection=deferred negative_selection=0"
        ),
    )

    new_diagnostic_id_set = set(observed_diagnostic_ids)
    new_primary_oracles = [
        row
        for row in promotion_contract.get("acceptance_oracles", [])
        if row.get("primary_diagnostic_or_null") in new_diagnostic_id_set
    ]
    record(
        len(new_primary_oracles) == 10
        and all(
            row.get("diagnostic_identity_status")
            == "NEW_PRIMARY_INTEGRATED_UNVERIFIED"
            for row in new_primary_oracles
        )
        and not any(
            row.get("diagnostic_identity_status")
            == "NEW_PRIMARY_APPROVED_NOT_INTEGRATED_SEED"
            for row in promotion_contract.get("acceptance_oracles", [])
        ),
        "R4_NRM_PROMOTION_METADATA",
        (
            f"new_primary_oracles={len(new_primary_oracles)} "
            f"status={promotion_contract.get('status')}"
        ),
    )

    noncall_predicate = next(
        (
            row
            for row in new_predicates
            if row.get("predicate_id") == "ResolvedNoncallReferenceSelected"
        ),
        {},
    )
    hir_boundary_fixture = next(
        (
            row
            for row in fixtures
            if row.get("fixture_id")
            == "PF-ResolverHirSealAdmitted-BOUNDARY"
        ),
        {},
    )
    noncall_text = json.dumps(noncall_predicate, ensure_ascii=False)
    record(
        "ResolvedOverloadSetRef" in noncall_text
        and "next cluster" in noncall_text
        and "generic substitution" in noncall_text
        and hir_boundary_fixture.get("descriptor", {}).get(
            "expected_outcome"
        )
        == "BYPASS_CALLABLE_OVERLOAD_SET_TO_NEXT_CLUSTER",
        "R4_NRM_NEXT_CLUSTER_FENCE",
        "callable overload winner remains outside R4",
    )
    record(
        all(
            row.get("product_support") == "NOT_RUN"
            for row in new_diagnostics + new_predicates
        )
        and all(
            row.get("execution_status") == "DESIGN_STATIC_NOT_RUN"
            for row in fixtures
        )
        and member_collision.get("product_support") == "NOT_RUN",
        "R4_NRM_PRODUCT_NOT_RUN",
        "diagnostics, predicates and fixtures remain design-static",
    )
    return results


def nested_property_consts(value: Any, property_name: str) -> list[Any]:
    """Collect JSON-Schema ``properties.<name>.const`` values recursively."""

    values: list[Any] = []
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            property_schema = properties.get(property_name)
            if (
                isinstance(property_schema, dict)
                and "const" in property_schema
            ):
                values.append(property_schema["const"])
        for child in value.values():
            values.extend(nested_property_consts(child, property_name))
    elif isinstance(value, list):
        for child in value:
            values.extend(nested_property_consts(child, property_name))
    return values


def is_typed_id(value: Any, prefix: str | None = None) -> bool:
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[A-Za-z][A-Za-z0-9]*:[^\s]+", value) is None
    ):
        return False
    domain = value.split(":", 1)[0]
    return prefix is None or domain == prefix


def is_typed_id_in(value: Any, domains: set[str]) -> bool:
    return is_typed_id(value) and value.split(":", 1)[0] in domains


def directed_strongly_connected_components(
    nodes: set[str], edges: list[tuple[str, str]]
) -> list[set[str]]:
    """Return directed SCCs iteratively, including edge-only endpoints."""

    all_nodes = set(nodes)
    for source, target in edges:
        all_nodes.add(source)
        all_nodes.add(target)
    adjacency = {node: [] for node in all_nodes}
    reverse = {node: [] for node in all_nodes}
    for source, target in edges:
        adjacency[source].append(target)
        reverse[target].append(source)

    visited: set[str] = set()
    finish_order: list[str] = []
    for start in sorted(all_nodes):
        if start in visited:
            continue
        stack: list[tuple[str, bool]] = [(start, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                finish_order.append(node)
                continue
            if node in visited:
                continue
            visited.add(node)
            stack.append((node, True))
            for child in reversed(sorted(adjacency[node])):
                if child not in visited:
                    stack.append((child, False))

    components: list[set[str]] = []
    assigned: set[str] = set()
    for start in reversed(finish_order):
        if start in assigned:
            continue
        component: set[str] = set()
        stack = [(start, False)]
        assigned.add(start)
        while stack:
            node, _expanded = stack.pop()
            component.add(node)
            for parent in reverse[node]:
                if parent not in assigned:
                    assigned.add(parent)
                    stack.append((parent, False))
        components.append(component)
    return components


def has_directed_cycle(nodes: set[str], edges: list[tuple[str, str]]) -> bool:
    self_loops = {(source, target) for source, target in edges if source == target}
    return bool(self_loops) or any(
        len(component) > 1
        for component in directed_strongly_connected_components(nodes, edges)
    )


def canonical_project_relative_path(value: Any) -> str | None:
    """Return one canonical slash-separated project-relative path."""

    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or value.startswith("/")
        or re.match(r"^[A-Za-z]:", value)
    ):
        return None
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return "/".join(parts)


def r4_source_role_carrier_failure_codes(
    carrier: dict[str, Any],
) -> set[str]:
    """Validate target ownership and normalized paths in a source carrier."""

    failures: set[str] = set()
    if (
        carrier.get("schema") != "deeplus.source-role-carrier/r2"
        or carrier.get("profile") != "R4_NAME_RESOLUTION_MODULES"
        or not is_typed_id(carrier.get("package_id"), "PackageId")
        or re.fullmatch(
            r"[0-9a-f]{64}",
            str(carrier.get("package_module_source_graph_sha256", "")),
        )
        is None
    ):
        failures.add("CARRIER_PROFILE")
    targets = carrier.get("targets", [])
    sources = carrier.get("source_files", [])
    target_ids = [row.get("target_id") for row in targets]
    if (
        not isinstance(targets, list)
        or not targets
        or len(target_ids) != len(set(target_ids))
        or any(not is_typed_id(target_id, "TargetId") for target_id in target_ids)
    ):
        failures.add("TARGET_SET")
    target_by_id = {row.get("target_id"): row for row in targets}
    target_identity_by_key: dict[tuple[Any, Any, Any], Any] = {}
    target_key_by_id: dict[Any, tuple[Any, Any, Any]] = {}
    package_id = carrier.get("package_id")
    for target in targets:
        key = (
            package_id,
            target.get("canonical_manifest_target_name"),
            target.get("target_kind"),
        )
        previous_target_id = target_identity_by_key.setdefault(
            key, target.get("target_id")
        )
        previous_key = target_key_by_id.setdefault(
            target.get("target_id"), key
        )
        if (
            None in key
            or previous_target_id != target.get("target_id")
            or previous_key != key
        ):
            failures.add("TARGET_IDENTITY_RECIPE")
        if target.get("target_kind") != target.get(
            "source_role_policy"
        ):
            failures.add("TARGET_SOURCE_ROLE_POLICY")
    source_ids: set[Any] = set()
    path_keys: set[tuple[Any, str]] = set()
    observed_source_target_ids: set[Any] = set()
    module_identity_by_key: dict[tuple[Any, tuple[Any, ...]], Any] = {}
    module_key_by_id: dict[Any, tuple[Any, tuple[Any, ...]]] = {}
    for source in sources:
        source_id = source.get("source_file_id")
        if (
            source_id in source_ids
            or not is_typed_id(source_id, "SourceFileId")
        ):
            failures.add("SOURCE_FILE_ID")
        source_ids.add(source_id)
        target_id = source.get("target_id")
        observed_source_target_ids.add(target_id)
        target = target_by_id.get(target_id)
        if target is None:
            failures.add("SOURCE_TARGET_REFERENCE")
        else:
            if (
                source.get("source_role") != target.get("source_role_policy")
                or source.get("activation_profile")
                != target.get("activation_profile")
            ):
                failures.add("SOURCE_TARGET_PROFILE")
        path = source.get("path")
        normalized_path = canonical_project_relative_path(path)
        if normalized_path is None or normalized_path != path:
            failures.add("SOURCE_PATH_NORMALIZATION")
            continue
        path_key = (target_id, normalized_path)
        if path_key in path_keys:
            failures.add("SOURCE_PATH_IDENTITY")
        path_keys.add(path_key)
        module_path = source.get("module_path")
        module_key = (
            package_id,
            tuple(module_path) if isinstance(module_path, list) else (),
        )
        module_id = source.get("module_id")
        previous_module_id = module_identity_by_key.setdefault(
            module_key, module_id
        )
        previous_module_key = module_key_by_id.setdefault(
            module_id, module_key
        )
        if (
            not is_typed_id(module_id, "ModuleId")
            or not module_key[1]
            or previous_module_id != module_id
            or previous_module_key != module_key
        ):
            failures.add("MODULE_IDENTITY_RECIPE")
    if set(target_ids) != observed_source_target_ids:
        failures.add("TARGET_SOURCE_REFERENCE")
    return failures


def canonical_self_digest(
    value: dict[str, Any], field: str
) -> str | None:
    """Hash canonical JSON after excluding one declared self-hash field."""

    if not isinstance(value, dict):
        return None
    payload = dict(value)
    payload.pop(field, None)
    return canonical_sha(payload)


def r4_module_initialization_failure_codes(
    plan: dict[str, Any],
) -> set[str]:
    """Validate the closed compile-time static-binding initialization plan."""

    failures: set[str] = set()
    if not isinstance(plan, dict):
        return {"INITIALIZATION_PROFILE"}
    expected_plan_fields = {
        "schema",
        "module_id",
        "graph_profile",
        "bindings",
        "topological_evaluation_order",
        "evaluation_order",
        "receipt_order",
        "commit",
        "runtime_initializer_count",
        "semantic_order_winner",
        "plan_sha256",
    }
    if (
        set(plan) != expected_plan_fields
        or plan.get("schema")
        != "deeplus.module-initialization-plan/r1"
        or not is_typed_id(plan.get("module_id"), "ModuleId")
        or plan.get("graph_profile")
        != "ACYCLIC_COMPILE_TIME_EVALUATION_ZERO_RUNTIME_INIT"
        or plan.get("evaluation_order")
        != "TOPOLOGICAL_THEN_CANONICAL_DECL_ID"
        or plan.get("receipt_order") != "CANONICAL_DECL_ID_ORDER"
        or plan.get("commit")
        != "ONE_ATOMIC_COMMIT_AFTER_ALL_VALUES_SUCCEED"
        or plan.get("runtime_initializer_count") != 0
        or plan.get("semantic_order_winner") is not False
    ):
        failures.add("INITIALIZATION_PROFILE")
    bindings = plan.get("bindings", [])
    if (
        not isinstance(bindings, list)
        or any(not isinstance(row, dict) for row in bindings)
    ):
        return failures | {"STATIC_BINDING_SET"}
    expected_binding_fields = {
        "binding_decl_id",
        "dependency_decl_ids",
        "value_sha256",
        "evaluation_status",
    }
    binding_ids = [row.get("binding_decl_id") for row in bindings]
    if (
        any(
            not is_typed_id(binding_id, "DeclId")
            for binding_id in binding_ids
        )
        or len(binding_ids) != len(set(binding_ids))
    ):
        failures.add("STATIC_BINDING_SET")
    binding_set = set(binding_ids)
    dependency_edges: list[tuple[str, str]] = []
    for row in bindings:
        dependencies = row.get("dependency_decl_ids", [])
        if (
            set(row) != expected_binding_fields
        ):
            failures.add("STATIC_BINDING_SET")
        if (
            not isinstance(dependencies, list)
            or any(
                not is_typed_id(dependency, "DeclId")
                for dependency in dependencies
            )
            or len(dependencies) != len(set(dependencies))
            or dependencies != sorted(dependencies)
        ):
            failures.add("STATIC_DEPENDENCY_SET")
            continue
        if row.get("binding_decl_id") in dependencies:
            failures.add("STATIC_DEPENDENCY_CYCLE")
        if any(dependency not in binding_set for dependency in dependencies):
            failures.add("STATIC_DEPENDENCY_REFERENCE")
        dependency_edges.extend(
            (row.get("binding_decl_id"), dependency)
            for dependency in dependencies
            if dependency in binding_set
        )
        if (
            re.fullmatch(
                r"[0-9a-f]{64}", str(row.get("value_sha256", ""))
            )
            is None
            or row.get("evaluation_status")
            != "COMPILE_TIME_SUCCEEDED"
        ):
            failures.add("STATIC_BINDING_RESULT")
    if has_directed_cycle(binding_set, dependency_edges):
        failures.add("STATIC_DEPENDENCY_CYCLE")

    dependencies_by_binding = {
        row.get("binding_decl_id"): set(row.get("dependency_decl_ids", []))
        for row in bindings
    }
    remaining = set(binding_set)
    emitted: list[str] = []
    while remaining:
        ready = sorted(
            binding_id
            for binding_id in remaining
            if not (dependencies_by_binding.get(binding_id, set()) & remaining)
        )
        if not ready:
            break
        emitted.extend(ready)
        remaining.difference_update(ready)
    declared_order = plan.get("topological_evaluation_order", [])
    if declared_order != emitted or len(emitted) != len(binding_set):
        failures.add("STATIC_EVALUATION_ORDER")
    if binding_ids != sorted(binding_ids):
        failures.add("STATIC_RECEIPT_ORDER")
    plan_sha256 = plan.get("plan_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(plan_sha256 or "")) is None
        or plan_sha256 != canonical_self_digest(plan, "plan_sha256")
    ):
        failures.add("INITIALIZATION_DIGEST")
    return failures


def r4_dependency_receipt_failure_codes(
    receipt: dict[str, Any],
    resolver_graph: dict[str, Any] | None = None,
    provider_interfaces: dict[str, dict[str, Any]] | None = None,
    package_graph: dict[str, Any] | None = None,
) -> set[str]:
    """Validate dependency rows and optional graph/provider pairings."""

    failures: set[str] = set()
    if not isinstance(receipt, dict):
        return {"DEPENDENCY_RECEIPT_PROFILE"}
    if (
        set(receipt)
        != {
            "schema",
            "consumer_target_id",
            "consumer_module_id",
            "package_graph_sha256",
            "resolver_graph_sha256",
            "import_bindings",
            "activation_bindings",
            "required_interfaces",
            "canonical_order",
            "dependency_receipt_sha256",
        }
        or
        receipt.get("schema")
        != "deeplus.module-compilation-dependency-receipt/r1"
        or not is_typed_id(
            receipt.get("consumer_target_id"), "TargetId"
        )
        or not is_typed_id(
            receipt.get("consumer_module_id"), "ModuleId"
        )
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(receipt.get(field, "")))
            is None
            for field in ("package_graph_sha256", "resolver_graph_sha256")
        )
        or receipt.get("canonical_order")
        != "TYPED_ID_CANONICAL_BYTE_ORDER"
    ):
        failures.add("DEPENDENCY_RECEIPT_PROFILE")

    imports = receipt.get("import_bindings", [])
    activations = receipt.get("activation_bindings", [])
    interfaces = receipt.get("required_interfaces", [])
    if not all(
        isinstance(rows, list) for rows in (imports, activations, interfaces)
    ):
        return failures | {"DEPENDENCY_RECEIPT_SHAPE"}
    if any(
        not isinstance(row, dict)
        for rows in (imports, activations, interfaces)
        for row in rows
    ):
        return failures | {"DEPENDENCY_RECEIPT_SHAPE"}

    import_ids: set[Any] = set()
    import_keys: set[tuple[Any, Any, Any]] = set()
    used_provider_pairs: set[tuple[Any, Any]] = set()
    import_fields = {
        "import_binding_id",
        "resolver_scope_id",
        "namespace",
        "local_binding_name",
        "resolved_target_identity",
        "source_origin_id",
        "provider_binding_id_or_self",
        "provider_module_id",
    }
    for row in imports:
        import_id = row.get("import_binding_id")
        key = (
            row.get("resolver_scope_id"),
            row.get("namespace"),
            row.get("local_binding_name"),
        )
        expected_domain = {
            "MODULE": "ModuleId",
            "TYPE": "DeclId",
            "VALUE": "DeclId",
            "CALLABLE_OVERLOAD_SET": "DeclId",
        }.get(row.get("namespace"))
        if (
            import_id in import_ids
            or key in import_keys
            or not is_typed_id(import_id, "ImportBindingId")
        ):
            failures.add("DEPENDENCY_IMPORT_IDENTITY")
        import_ids.add(import_id)
        import_keys.add(key)
        if (
            set(row) != import_fields
            or
            not is_typed_id(
                row.get("resolver_scope_id"), "ResolverScopeId"
            )
            or expected_domain is None
            or re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                str(row.get("local_binding_name", "")),
            )
            is None
            or not is_typed_id(
                row.get("resolved_target_identity"), expected_domain
            )
            or not is_typed_id(
                row.get("source_origin_id"), "SourceOriginId"
            )
        ):
            failures.add("DEPENDENCY_IMPORT_DOMAIN")
        provider_binding = row.get("provider_binding_id_or_self")
        provider_module = row.get("provider_module_id")
        if (
            (
                provider_binding != "self"
                and not is_typed_id(
                    provider_binding, "DependencyBindingId"
                )
            )
            or not is_typed_id(provider_module, "ModuleId")
        ):
            failures.add("DEPENDENCY_IMPORT_PROVIDER")
        else:
            used_provider_pairs.add((provider_binding, provider_module))

    activation_origins: set[Any] = set()
    activation_keys: set[tuple[Any, Any, Any, Any]] = set()
    activation_fields = {
        "activation_origin_id",
        "resolver_scope_id",
        "activated_identity",
        "activation_kind",
        "semantic_site_key",
        "provider_binding_id_or_self",
        "provider_module_id",
    }
    for row in activations:
        origin = row.get("activation_origin_id")
        key = (
            row.get("activated_identity"),
            row.get("resolver_scope_id"),
            row.get("activation_kind"),
            row.get("semantic_site_key"),
        )
        if origin in activation_origins or key in activation_keys:
            failures.add("DEPENDENCY_ACTIVATION_IDENTITY")
        activation_origins.add(origin)
        activation_keys.add(key)
        if (
            set(row) != activation_fields
            or
            not is_typed_id(origin, "ActivationOriginId")
            or not is_typed_id(
                row.get("resolver_scope_id"), "ResolverScopeId"
            )
            or not is_typed_id(
                row.get("activated_identity"), "ExtensionSetId"
            )
            or row.get("activation_kind") != "use"
            or not isinstance(row.get("semantic_site_key"), str)
            or not row.get("semantic_site_key")
        ):
            failures.add("DEPENDENCY_ACTIVATION_DOMAIN")
        provider_binding = row.get("provider_binding_id_or_self")
        provider_module = row.get("provider_module_id")
        if (
            (
                provider_binding != "self"
                and not is_typed_id(
                    provider_binding, "DependencyBindingId"
                )
            )
            or not is_typed_id(provider_module, "ModuleId")
        ):
            failures.add("DEPENDENCY_ACTIVATION_PROVIDER")
        else:
            used_provider_pairs.add((provider_binding, provider_module))

    required_interface_keys: set[tuple[Any, Any]] = set()
    interface_fields = {
        "provider_binding_id_or_self",
        "provider_module_id",
        "interface_profile",
        "interface_sha256",
    }
    for row in interfaces:
        provider_binding = row.get("provider_binding_id_or_self")
        provider_module_id = row.get("provider_module_id")
        key = (provider_binding, provider_module_id)
        if (
            key in required_interface_keys
            or (
                provider_binding != "self"
                and not is_typed_id(
                    provider_binding, "DependencyBindingId"
                )
            )
            or not is_typed_id(provider_module_id, "ModuleId")
        ):
            failures.add("DEPENDENCY_INTERFACE_IDENTITY")
        required_interface_keys.add(key)
        if (
            set(row) != interface_fields
            or row.get("interface_profile")
            != "R4_NAME_RESOLUTION_MODULES"
            or re.fullmatch(
                r"[0-9a-f]{64}", str(row.get("interface_sha256", ""))
            )
            is None
        ):
            failures.add("DEPENDENCY_INTERFACE_DOMAIN")
        if provider_interfaces is not None:
            provider = (
                provider_interfaces.get(provider_module_id)
                if isinstance(provider_interfaces, dict)
                else None
            )
            if (
                not isinstance(provider, dict)
                or r4_module_api_failure_codes(provider)
                or provider.get("module_id") != provider_module_id
                or provider.get("interface_profile")
                != "R4_NAME_RESOLUTION_MODULES"
                or provider.get("canonical_sha256")
                != row.get("interface_sha256")
            ):
                failures.add("STALE_PROVIDER_INTERFACE")

    expected_required_interface_keys = {
        pair
        for pair in used_provider_pairs
        if pair[1] != receipt.get("consumer_module_id")
    }
    if required_interface_keys != expected_required_interface_keys:
        failures.add("DEPENDENCY_INTERFACE_CLOSURE")

    if package_graph is not None:
        if (
            receipt.get("package_graph_sha256")
            != package_graph.get("canonical_graph_sha256")
        ):
            failures.add("RECEIPT_PACKAGE_GRAPH_DIGEST")
        visible_provider_pairs = {
            (
                row.get("dependency_binding_id_or_self"),
                row.get("resolved_module_id"),
            )
            for row in package_graph.get("visible_module_bindings", [])
            if row.get("consumer_target_id")
            == receipt.get("consumer_target_id")
        }
        if not used_provider_pairs.issubset(visible_provider_pairs):
            failures.add("DEPENDENCY_PROVIDER_GRAPH_BINDING")

    if [row.get("import_binding_id") for row in imports] != sorted(
        row.get("import_binding_id") for row in imports
    ):
        failures.add("DEPENDENCY_RECEIPT_ORDER")
    if [row.get("activation_origin_id") for row in activations] != sorted(
        row.get("activation_origin_id") for row in activations
    ):
        failures.add("DEPENDENCY_RECEIPT_ORDER")
    if [
        (
            row.get("provider_binding_id_or_self"),
            row.get("provider_module_id"),
        )
        for row in interfaces
    ] != sorted(
        (
            row.get("provider_binding_id_or_self"),
            row.get("provider_module_id"),
        )
        for row in interfaces
    ):
        failures.add("DEPENDENCY_RECEIPT_ORDER")

    if resolver_graph is not None:
        if receipt.get("resolver_graph_sha256") != resolver_graph.get(
            "resolver_graph_sha256"
        ):
            failures.add("RECEIPT_RESOLVER_GRAPH_DIGEST")
        graph_imports = resolver_graph.get("import_bindings", [])
        graph_activations = resolver_graph.get("activation_entries", [])
        if imports != graph_imports:
            failures.add("RECEIPT_RESOLVER_IMPORT_BINDING")
        if activations != graph_activations:
            failures.add("RECEIPT_RESOLVER_ACTIVATION_BINDING")

    receipt_sha256 = receipt.get("dependency_receipt_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(receipt_sha256 or "")) is None
        or receipt_sha256
        != canonical_self_digest(receipt, "dependency_receipt_sha256")
    ):
        failures.add("DEPENDENCY_RECEIPT_DIGEST")
    return failures


def r4_visibility_closure_failure_codes(
    closure: dict[str, Any],
) -> set[str]:
    """Validate export, proof and opaque-facade relational closure."""

    failures: set[str] = set()
    if not isinstance(closure, dict):
        return {"VISIBILITY_CLOSURE_PROFILE"}
    expected_closure_fields = {
        "schema",
        "module_id",
        "default_external_export_set",
        "export_edges",
        "reexport_edges",
        "visibility_proofs",
        "signature_relation",
        "opaque_facade_relation",
        "opaque_facades",
        "closure_sha256",
    }
    if (
        set(closure) != expected_closure_fields
        or closure.get("schema")
        != "deeplus.module-visibility-closure/r1"
        or not is_typed_id(closure.get("module_id"), "ModuleId")
        or closure.get("default_external_export_set") != "EMPTY"
        or closure.get("signature_relation")
        != "EXACT_NORMALIZED_PUBLIC_RESIDUE_MATCH"
        or closure.get("opaque_facade_relation") != "NARROWING_ONLY"
    ):
        failures.add("VISIBILITY_CLOSURE_PROFILE")
    exports = closure.get("export_edges", [])
    reexports = closure.get("reexport_edges", [])
    proofs = closure.get("visibility_proofs", [])
    facades = closure.get("opaque_facades", [])
    if not all(
        isinstance(rows, list)
        for rows in (exports, reexports, proofs, facades)
    ):
        return failures | {"VISIBILITY_CLOSURE_SHAPE"}
    if any(
        not isinstance(row, dict)
        for rows in (exports, reexports, proofs, facades)
        for row in rows
    ):
        return failures | {"VISIBILITY_CLOSURE_SHAPE"}

    export_keys: set[tuple[Any, Any, Any]] = set()
    export_identity_pairs: set[tuple[Any, Any]] = set()
    export_owners: set[Any] = {closure.get("module_id")}
    expected_export_fields = {
        "export_owner_id",
        "namespace",
        "exported_name",
        "referenced_identity_id",
        "source_origin_id",
    }
    for row in exports:
        key = (
            row.get("export_owner_id"),
            row.get("namespace"),
            row.get("exported_name"),
        )
        expected_domain = {
            "MODULE": "ModuleId",
            "TYPE": "DeclId",
            "VALUE": "DeclId",
            "CALLABLE_OVERLOAD_SET": "DeclId",
        }.get(row.get("namespace"))
        if key in export_keys:
            failures.add("EXPORT_EDGE_IDENTITY")
        export_keys.add(key)
        export_owners.add(row.get("export_owner_id"))
        export_identity_pairs.add(
            (
                row.get("export_owner_id"),
                row.get("referenced_identity_id"),
            )
        )
        if (
            set(row) != expected_export_fields
            or not is_typed_id_in(
                row.get("export_owner_id"),
                {"ModuleId", "DeclId", "TypeId", "MemberId"},
            )
            or expected_domain is None
            or re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                str(row.get("exported_name", "")),
            )
            is None
            or not is_typed_id(
                row.get("referenced_identity_id"), expected_domain
            )
            or not is_typed_id(
                row.get("source_origin_id"), "SourceOriginId"
            )
        ):
            failures.add("EXPORT_EDGE_DOMAIN")

    reexport_origins: set[Any] = set()
    expected_reexport_fields = {
        "activation_origin_id",
        "export_owner_id",
        "referenced_activation_identity_id",
        "source_origin_id",
    }
    for row in reexports:
        origin = row.get("activation_origin_id")
        if origin in reexport_origins:
            failures.add("REEXPORT_EDGE_IDENTITY")
        reexport_origins.add(origin)
        if (
            set(row) != expected_reexport_fields
            or not is_typed_id(origin, "ActivationOriginId")
            or not is_typed_id(
                row.get("referenced_activation_identity_id"),
                "ExtensionSetId",
            )
            or row.get("export_owner_id") not in export_owners
            or not is_typed_id(
                row.get("source_origin_id"), "SourceOriginId"
            )
        ):
            failures.add("REEXPORT_EDGE_DOMAIN")

    allowed_dependencies = {
        "private": {"private", "common", "public"},
        "common": {"common", "public"},
        "public": {"public"},
    }
    proof_ids: set[Any] = set()
    proof_id_by_key: dict[tuple[Any, ...], Any] = {}
    proof_key_by_id: dict[Any, tuple[Any, ...]] = {}
    expected_proof_fields = {
        "proof_id",
        "export_owner_id",
        "referenced_identity_id",
        "api_position_kind",
        "api_position_path",
        "owner_visibility",
        "referenced_visibility",
        "package_relation",
        "module_relation",
        "admission",
    }
    api_position_kinds = {
        "parameter",
        "result",
        "field",
        "generic_constraint",
        "associated_item",
        "error_set",
        "effect_capability",
        "context_capability",
        "witness_requirement",
        "nested_export",
    }
    for row in proofs:
        proof_id = row.get("proof_id")
        api_position_path = row.get("api_position_path")
        key = (
            closure.get("module_id"),
            row.get("export_owner_id"),
            row.get("referenced_identity_id"),
            row.get("api_position_kind"),
            (
                tuple(api_position_path)
                if isinstance(api_position_path, list)
                and all(
                    isinstance(component, str)
                    for component in api_position_path
                )
                else ()
            ),
            row.get("owner_visibility"),
            row.get("referenced_visibility"),
            row.get("package_relation"),
            row.get("module_relation"),
        )
        if proof_id in proof_ids:
            failures.add("VISIBILITY_PROOF_IDENTITY")
        proof_ids.add(proof_id)
        previous_proof_id = proof_id_by_key.setdefault(key, proof_id)
        previous_key = proof_key_by_id.setdefault(proof_id, key)
        if previous_proof_id != proof_id or previous_key != key:
            failures.add("VISIBILITY_PROOF_IDENTITY")
        relation_pair = (
            row.get("module_relation"),
            row.get("package_relation"),
        )
        if relation_pair not in {
            ("same_module", "same_package"),
            ("same_package_other_module", "same_package"),
            ("dependency_module", "dependency_package"),
        }:
            failures.add("VISIBILITY_RELATION")
        owner_visibility = row.get("owner_visibility")
        if row.get("referenced_visibility") not in (
            allowed_dependencies.get(owner_visibility, set())
        ):
            failures.add("VISIBILITY_WIDENING")
        if (
            set(row) != expected_proof_fields
            or not is_typed_id(proof_id, "VisibilityProofId")
            or row.get("export_owner_id") not in export_owners
            or not is_typed_id_in(
                row.get("referenced_identity_id"),
                {
                    "ModuleId",
                    "DeclId",
                    "TypeId",
                    "MemberId",
                    "AssociatedItemId",
                    "ExtensionSetId",
                    "ExtensionMemberId",
                    "TraitWitnessId",
                },
            )
            or row.get("api_position_kind") not in api_position_kinds
            or row.get("admission") != "VISIBLE_NO_WIDENING"
            or not isinstance(api_position_path, list)
            or not api_position_path
            or any(
                not isinstance(component, str) or not component
                for component in (
                    api_position_path
                    if isinstance(api_position_path, list)
                    else []
                )
            )
        ):
            failures.add("VISIBILITY_PROOF_DOMAIN")
    if any(
        pair not in {
            (row.get("export_owner_id"), row.get("referenced_identity_id"))
            for row in proofs
        }
        for pair in export_identity_pairs
    ):
        failures.add("EXPORT_PROOF_LINKAGE")

    facade_owners: set[Any] = set()
    expected_facade_fields = {
        "export_owner_id",
        "owner_public_residue_identity_ids",
        "facade_public_residue_identity_ids",
    }
    residue_domains = {
        "ModuleId",
        "DeclId",
        "TypeId",
        "MemberId",
        "AssociatedItemId",
        "ExtensionSetId",
        "ExtensionMemberId",
        "TraitWitnessId",
    }
    for row in facades:
        owner = row.get("export_owner_id")
        owner_residue = row.get("owner_public_residue_identity_ids", [])
        facade_residue = row.get(
            "facade_public_residue_identity_ids", []
        )
        if owner in facade_owners:
            failures.add("OPAQUE_FACADE_IDENTITY")
        facade_owners.add(owner)
        if (
            set(row) != expected_facade_fields
            or owner not in export_owners
            or not isinstance(owner_residue, list)
            or not isinstance(facade_residue, list)
            or any(
                not is_typed_id_in(identity, residue_domains)
                for identity in owner_residue
            )
            or any(
                not is_typed_id_in(identity, residue_domains)
                for identity in facade_residue
            )
            or len(owner_residue) != len(set(owner_residue))
            or len(facade_residue) != len(set(facade_residue))
        ):
            failures.add("OPAQUE_FACADE_DOMAIN")
        if (
            isinstance(owner_residue, list)
            and isinstance(facade_residue, list)
            and all(
                isinstance(identity, str)
                for identity in [*owner_residue, *facade_residue]
            )
            and (
                owner_residue != sorted(owner_residue)
                or facade_residue != sorted(facade_residue)
            )
        ):
            failures.add("OPAQUE_FACADE_ORDER")
        facade_subset_valid = (
            isinstance(owner_residue, list)
            and isinstance(facade_residue, list)
            and all(
                isinstance(identity, str)
                for identity in [*owner_residue, *facade_residue]
            )
            and set(facade_residue).issubset(set(owner_residue))
        )
        if not facade_subset_valid:
            failures.add("OPAQUE_FACADE_WIDENING")

    export_order = [
        (
            row.get("export_owner_id"),
            row.get("namespace"),
            row.get("exported_name"),
        )
        for row in exports
    ]
    reexport_order = [
        row.get("activation_origin_id") for row in reexports
    ]
    proof_order = [row.get("proof_id") for row in proofs]
    facade_order = [row.get("export_owner_id") for row in facades]
    if (
        not all(
            all(isinstance(component, str) for component in key)
            for key in export_order
        )
        or export_order != sorted(export_order)
        or not all(isinstance(value, str) for value in reexport_order)
        or reexport_order != sorted(reexport_order)
        or not all(isinstance(value, str) for value in proof_order)
        or proof_order != sorted(proof_order)
        or not all(isinstance(value, str) for value in facade_order)
        or facade_order != sorted(facade_order)
    ):
        failures.add("VISIBILITY_CLOSURE_ORDER")

    closure_sha256 = closure.get("closure_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(closure_sha256 or "")) is None
        or closure_sha256
        != canonical_self_digest(closure, "closure_sha256")
    ):
        failures.add("VISIBILITY_CLOSURE_DIGEST")
    return failures


def r4_module_api_failure_codes(
    api: dict[str, Any],
    visibility_closure: dict[str, Any] | None = None,
    api_hir_exported_symbols: list[dict[str, Any]] | None = None,
) -> set[str]:
    """Validate the provenance-free R4 public semantic interface identity."""

    failures: set[str] = set()
    if (
        set(api)
        != {
            "schema",
            "baseline",
            "module_id",
            "source_role",
            "interface_profile",
            "r4_interface_envelope",
            "symbols",
            "canonical_sha256",
        }
        or
        api.get("schema") != "deeplus.module-api-digest/r51f3"
        or api.get("baseline") != "0.1.2-baseline.r51f3"
        or api.get("interface_profile") != "R4_NAME_RESOLUTION_MODULES"
        or not is_typed_id(api.get("module_id"), "ModuleId")
        or api.get("source_role") not in {"library", "executable"}
    ):
        failures.add("MODULE_INTERFACE_PROFILE")
    envelope = api.get("r4_interface_envelope")
    if not isinstance(envelope, dict):
        return failures | {"MODULE_INTERFACE_ENVELOPE"}
    expected_envelope_fields = {
        "activation_profile",
        "public_export_rows",
        "public_activation_reexport_rows",
        "opaque_facade_rows",
        "signature_relation",
        "opaque_facade_relation",
        "symbols_are_exact_effective_public_residue",
        "private_body_bytes_in_interface_hash",
    }
    if (
        set(envelope) != expected_envelope_fields
        or not isinstance(envelope.get("activation_profile"), str)
        or not envelope.get("activation_profile")
        or envelope.get("signature_relation")
        != "EXACT_NORMALIZED_PUBLIC_RESIDUE_MATCH"
        or envelope.get("opaque_facade_relation") != "NARROWING_ONLY"
        or envelope.get("symbols_are_exact_effective_public_residue")
        is not True
        or envelope.get("private_body_bytes_in_interface_hash") is not False
    ):
        failures.add("MODULE_INTERFACE_ENVELOPE")

    export_rows = envelope.get("public_export_rows", [])
    activation_rows = envelope.get(
        "public_activation_reexport_rows", []
    )
    facade_rows = envelope.get("opaque_facade_rows", [])
    if not all(
        isinstance(rows, list)
        for rows in (export_rows, activation_rows, facade_rows)
    ):
        return failures | {"MODULE_INTERFACE_PUBLIC_PROJECTION"}

    export_keys: list[tuple[Any, Any, Any, Any]] = []
    export_name_keys: set[tuple[Any, Any, Any]] = set()
    for row in export_rows:
        namespace = row.get("namespace")
        target_domain = (
            "ModuleId" if namespace == "MODULE" else "DeclId"
        )
        key = (
            row.get("export_owner_id"),
            namespace,
            row.get("exported_name"),
            row.get("referenced_identity_id"),
        )
        export_keys.append(key)
        name_key = key[:3]
        if name_key in export_name_keys:
            failures.add("MODULE_INTERFACE_EXPORT_IDENTITY")
        export_name_keys.add(name_key)
        if (
            set(row)
            != {
                "export_owner_id",
                "namespace",
                "exported_name",
                "referenced_identity_id",
            }
            or namespace
            not in {"MODULE", "TYPE", "VALUE", "CALLABLE_OVERLOAD_SET"}
            or not is_typed_id_in(
                row.get("export_owner_id"),
                {"ModuleId", "DeclId", "TypeId", "MemberId"},
            )
            or not is_typed_id(
                row.get("referenced_identity_id"), target_domain
            )
            or re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                str(row.get("exported_name", "")),
            )
            is None
        ):
            failures.add("MODULE_INTERFACE_EXPORT_DOMAIN")
    if export_keys != sorted(export_keys) or len(export_keys) != len(
        set(export_keys)
    ):
        failures.add("MODULE_INTERFACE_EXPORT_ORDER")

    activation_keys: list[tuple[Any, Any]] = []
    for row in activation_rows:
        key = (
            row.get("export_owner_id"),
            row.get("referenced_activation_identity_id"),
        )
        activation_keys.append(key)
        if (
            set(row)
            != {
                "export_owner_id",
                "referenced_activation_identity_id",
            }
            or not is_typed_id_in(
                row.get("export_owner_id"),
                {"ModuleId", "DeclId", "TypeId", "MemberId"},
            )
            or not is_typed_id(
                row.get("referenced_activation_identity_id"),
                "ExtensionSetId",
            )
        ):
            failures.add("MODULE_INTERFACE_ACTIVATION_DOMAIN")
    if activation_keys != sorted(activation_keys) or len(
        activation_keys
    ) != len(set(activation_keys)):
        failures.add("MODULE_INTERFACE_ACTIVATION_ORDER")

    facade_keys: list[Any] = []
    for row in facade_rows:
        owner = row.get("export_owner_id")
        residue = row.get("facade_public_residue_identity_ids", [])
        facade_keys.append(owner)
        if (
            set(row)
            != {
                "export_owner_id",
                "facade_public_residue_identity_ids",
            }
            or not is_typed_id_in(
                owner, {"ModuleId", "DeclId", "TypeId", "MemberId"}
            )
            or not isinstance(residue, list)
            or residue != sorted(residue)
            or len(residue) != len(set(residue))
            or any(
                not is_typed_id_in(
                    identity,
                    {
                        "ModuleId",
                        "DeclId",
                        "TypeId",
                        "MemberId",
                        "AssociatedItemId",
                        "ExtensionSetId",
                        "ExtensionMemberId",
                        "TraitWitnessId",
                    },
                )
                for identity in residue
            )
        ):
            failures.add("MODULE_INTERFACE_FACADE_DOMAIN")
    if facade_keys != sorted(facade_keys) or len(facade_keys) != len(
        set(facade_keys)
    ):
        failures.add("MODULE_INTERFACE_FACADE_ORDER")

    if visibility_closure is not None:
        expected_export_rows = sorted(
            [
                {
                    "export_owner_id": row.get("export_owner_id"),
                    "namespace": row.get("namespace"),
                    "exported_name": row.get("exported_name"),
                    "referenced_identity_id": row.get(
                        "referenced_identity_id"
                    ),
                }
                for row in visibility_closure.get("export_edges", [])
            ],
            key=lambda row: (
                row["export_owner_id"],
                row["namespace"],
                row["exported_name"],
                row["referenced_identity_id"],
            ),
        )
        expected_activation_rows = sorted(
            [
                {
                    "export_owner_id": row.get("export_owner_id"),
                    "referenced_activation_identity_id": row.get(
                        "referenced_activation_identity_id"
                    ),
                }
                for row in visibility_closure.get("reexport_edges", [])
            ],
            key=lambda row: (
                row["export_owner_id"],
                row["referenced_activation_identity_id"],
            ),
        )
        expected_facade_rows = sorted(
            [
                {
                    "export_owner_id": row.get("export_owner_id"),
                    "facade_public_residue_identity_ids": sorted(
                        row.get(
                            "facade_public_residue_identity_ids", []
                        )
                    ),
                }
                for row in visibility_closure.get("opaque_facades", [])
            ],
            key=lambda row: row["export_owner_id"],
        )
        if (
            api.get("module_id") != visibility_closure.get("module_id")
            or export_rows != expected_export_rows
            or activation_rows != expected_activation_rows
            or facade_rows != expected_facade_rows
        ):
            failures.add("MODULE_INTERFACE_VISIBILITY_PROJECTION")

    symbols = api.get("symbols")
    if not isinstance(symbols, list):
        failures.add("MODULE_INTERFACE_SYMBOL_PROJECTION")
    else:
        symbol_ids = [row.get("symbol_id") for row in symbols]
        if (
            any(not isinstance(row, dict) for row in symbols)
            or any(
                not isinstance(symbol_id, str) or not symbol_id
                for symbol_id in symbol_ids
            )
            or symbol_ids != sorted(symbol_ids)
            or len(symbol_ids) != len(set(symbol_ids))
        ):
            failures.add("MODULE_INTERFACE_SYMBOL_ORDER")
        for symbol in symbols:
            for field in (
                "authority",
                "effect_row",
                "error_set",
                "evidence_ids",
            ):
                values = symbol.get(field)
                if (
                    not isinstance(values, list)
                    or values != sorted(values)
                    or len(values) != len(set(values))
                ):
                    failures.add("MODULE_INTERFACE_SYMBOL_SET_ORDER")
        if (
            api_hir_exported_symbols is not None
            and symbols != api_hir_exported_symbols
        ):
            failures.add("MODULE_INTERFACE_SYMBOL_PROJECTION")
    canonical_sha256 = api.get("canonical_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(canonical_sha256 or "")) is None
        or canonical_sha256
        != canonical_self_digest(api, "canonical_sha256")
    ):
        failures.add("MODULE_INTERFACE_DIGEST")
    return failures


def r4_module_source_projection_failure_codes(
    projection: dict[str, Any],
    package_graph: dict[str, Any] | None = None,
) -> set[str]:
    """Validate the provenance-only module/source contribution projection."""

    failures: set[str] = set()
    if (
        set(projection)
        != {
            "schema",
            "target_id",
            "module_id",
            "source_contributions",
            "projection_sha256",
        }
        or
        projection.get("schema")
        != "deeplus.module-source-contribution-projection/r1"
        or not is_typed_id(projection.get("target_id"), "TargetId")
        or not is_typed_id(projection.get("module_id"), "ModuleId")
    ):
        failures.add("MODULE_SOURCE_PROJECTION_PROFILE")
    rows = projection.get("source_contributions")
    if not isinstance(rows, list) or not rows:
        return failures | {"MODULE_SOURCE_PROJECTION_SET"}
    source_ids: list[Any] = []
    source_paths: set[Any] = set()
    expected_fields = {
        "source_file_id",
        "normalized_project_relative_path",
        "source_role",
        "activation_profile",
        "source_bytes_sha256",
    }
    for row in rows:
        source_ids.append(row.get("source_file_id"))
        path = row.get("normalized_project_relative_path")
        if path in source_paths:
            failures.add("MODULE_SOURCE_PROJECTION_PATH_IDENTITY")
        source_paths.add(path)
        if (
            set(row) != expected_fields
            or not is_typed_id(row.get("source_file_id"), "SourceFileId")
            or canonical_project_relative_path(path) != path
            or row.get("source_role")
            not in {"library", "executable", "script"}
            or not isinstance(row.get("activation_profile"), str)
            or not row.get("activation_profile")
            or re.fullmatch(
                r"[0-9a-f]{64}", str(row.get("source_bytes_sha256", ""))
            )
            is None
        ):
            failures.add("MODULE_SOURCE_PROJECTION_DOMAIN")
    if source_ids != sorted(source_ids) or len(source_ids) != len(
        set(source_ids)
    ):
        failures.add("MODULE_SOURCE_PROJECTION_ORDER")

    if package_graph is not None:
        expected_rows = sorted(
            [
                {
                    "source_file_id": row.get("source_file_id"),
                    "normalized_project_relative_path": row.get(
                        "normalized_project_relative_path"
                    ),
                    "source_role": row.get("source_role"),
                    "activation_profile": row.get("activation_profile"),
                    "source_bytes_sha256": row.get("source_bytes_sha256"),
                }
                for row in package_graph.get("source_contributions", [])
                if row.get("target_id") == projection.get("target_id")
                and row.get("module_id") == projection.get("module_id")
            ],
            key=lambda row: row["source_file_id"],
        )
        if rows != expected_rows:
            failures.add("MODULE_SOURCE_GRAPH_PROJECTION")
    digest = projection.get("projection_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(digest or "")) is None
        or digest != canonical_self_digest(projection, "projection_sha256")
    ):
        failures.add("MODULE_SOURCE_PROJECTION_DIGEST")
    return failures


def r4_module_implementation_failure_codes(
    implementation: dict[str, Any],
    module_api: dict[str, Any] | None = None,
) -> set[str]:
    """Validate the private semantic implementation hash domain."""

    failures: set[str] = set()
    target_kind = implementation.get("target_kind")
    interface_sha256 = implementation.get("interface_sha256")
    if (
        set(implementation)
        != {
            "schema",
            "interface_profile",
            "target_id",
            "target_kind",
            "module_id",
            "interface_sha256",
            "hir_semantic_sha256",
            "external_compatibility_identity",
            "implementation_sha256",
        }
        or
        implementation.get("schema")
        != "deeplus.module-implementation-digest/r1"
        or implementation.get("interface_profile")
        != "R4_NAME_RESOLUTION_MODULES"
        or not is_typed_id(implementation.get("target_id"), "TargetId")
        or not is_typed_id(implementation.get("module_id"), "ModuleId")
        or target_kind not in {"library", "executable", "script"}
        or (
            target_kind == "script"
            and interface_sha256 is not None
        )
        or (
            target_kind != "script"
            and re.fullmatch(
                r"[0-9a-f]{64}", str(interface_sha256 or "")
            )
            is None
        )
        or re.fullmatch(
            r"[0-9a-f]{64}",
            str(implementation.get("hir_semantic_sha256", "")),
        )
        is None
        or implementation.get("external_compatibility_identity") is not False
    ):
        failures.add("MODULE_IMPLEMENTATION_PROFILE")
    if module_api is not None:
        expected_source_role = {
            "library": "library",
            "executable": "executable",
        }.get(target_kind)
        if (
            r4_module_api_failure_codes(module_api)
            or target_kind == "script"
            or implementation.get("module_id")
            != module_api.get("module_id")
            or interface_sha256 != module_api.get("canonical_sha256")
            or module_api.get("source_role") != expected_source_role
        ):
            failures.add("MODULE_IMPLEMENTATION_INTERFACE_BINDING")
    digest = implementation.get("implementation_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(digest or "")) is None
        or digest
        != canonical_self_digest(
            implementation, "implementation_sha256"
        )
    ):
        failures.add("MODULE_IMPLEMENTATION_DIGEST")
    return failures


def r4_compilation_receipt_failure_codes(
    receipt: dict[str, Any],
    *,
    package_graph: dict[str, Any] | None = None,
    source_projection: dict[str, Any] | None = None,
    dependency_receipt: dict[str, Any] | None = None,
    resolver_trace: dict[str, Any] | None = None,
    visibility_closure: dict[str, Any] | None = None,
    initialization_plan: dict[str, Any] | None = None,
    module_api: dict[str, Any] | None = None,
    implementation: dict[str, Any] | None = None,
) -> set[str]:
    """Validate the full provenance/build closure and all digest relations."""

    failures: set[str] = set()
    target_kind = receipt.get("target_kind")
    if (
        set(receipt)
        != {
            "schema",
            "profile",
            "target_id",
            "target_kind",
            "module_id",
            "package_graph_sha256",
            "module_source_contribution_sha256",
            "dependency_receipt_sha256",
            "resolver_trace_sha256",
            "visibility_closure_sha256",
            "initialization_plan_sha256",
            "interface_sha256",
            "implementation_sha256",
            "compilation_receipt_sha256",
        }
        or
        receipt.get("schema")
        != "deeplus.module-compilation-receipt/r1"
        or receipt.get("profile") != "R4_NAME_RESOLUTION_MODULES"
        or not is_typed_id(receipt.get("target_id"), "TargetId")
        or not is_typed_id(receipt.get("module_id"), "ModuleId")
        or target_kind not in {"library", "executable", "script"}
        or (
            target_kind == "script"
            and receipt.get("interface_sha256") is not None
        )
        or (
            target_kind != "script"
            and re.fullmatch(
                r"[0-9a-f]{64}",
                str(receipt.get("interface_sha256") or ""),
            )
            is None
        )
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(receipt.get(field, "")))
            is None
            for field in (
                "package_graph_sha256",
                "module_source_contribution_sha256",
                "dependency_receipt_sha256",
                "resolver_trace_sha256",
                "visibility_closure_sha256",
                "initialization_plan_sha256",
                "implementation_sha256",
            )
        )
    ):
        failures.add("MODULE_COMPILATION_RECEIPT_PROFILE")

    expected_bindings: list[tuple[str, Any]] = []
    if package_graph is not None:
        expected_bindings.append(
            (
                "package_graph_sha256",
                package_graph.get("canonical_graph_sha256"),
            )
        )
        target_rows = [
            row
            for row in package_graph.get("targets", [])
            if row.get("target_id") == receipt.get("target_id")
        ]
        source_rows = [
            row
            for row in package_graph.get("source_contributions", [])
            if row.get("target_id") == receipt.get("target_id")
            and row.get("module_id") == receipt.get("module_id")
        ]
        if (
            len(target_rows) != 1
            or target_rows[0].get("target_kind") != target_kind
            or not source_rows
        ):
            failures.add("MODULE_COMPILATION_GRAPH_OWNER_BINDING")
    if source_projection is not None:
        expected_bindings.append(
            (
                "module_source_contribution_sha256",
                source_projection.get("projection_sha256"),
            )
        )
        if (
            receipt.get("target_id") != source_projection.get("target_id")
            or receipt.get("module_id")
            != source_projection.get("module_id")
        ):
            failures.add("MODULE_COMPILATION_OWNER_BINDING")
    if dependency_receipt is not None:
        expected_bindings.append(
            (
                "dependency_receipt_sha256",
                dependency_receipt.get("dependency_receipt_sha256"),
            )
        )
        if (
            receipt.get("target_id")
            != dependency_receipt.get("consumer_target_id")
            or receipt.get("module_id")
            != dependency_receipt.get("consumer_module_id")
        ):
            failures.add("MODULE_COMPILATION_OWNER_BINDING")
        if package_graph is not None and dependency_receipt.get(
            "package_graph_sha256"
        ) != package_graph.get("canonical_graph_sha256"):
            failures.add("MODULE_COMPILATION_GRAPH_BINDING")
    if resolver_trace is not None:
        expected_bindings.append(
            ("resolver_trace_sha256", resolver_trace.get("trace_sha256"))
        )
        if dependency_receipt is not None and resolver_trace.get(
            "resolver_graph_sha256"
        ) != dependency_receipt.get("resolver_graph_sha256"):
            failures.add("MODULE_COMPILATION_RESOLVER_BINDING")
    if visibility_closure is not None:
        expected_bindings.append(
            (
                "visibility_closure_sha256",
                visibility_closure.get("closure_sha256"),
            )
        )
        if receipt.get("module_id") != visibility_closure.get("module_id"):
            failures.add("MODULE_COMPILATION_OWNER_BINDING")
    if initialization_plan is not None:
        expected_bindings.append(
            (
                "initialization_plan_sha256",
                initialization_plan.get("plan_sha256"),
            )
        )
        if receipt.get("module_id") != initialization_plan.get("module_id"):
            failures.add("MODULE_COMPILATION_OWNER_BINDING")
    if module_api is not None:
        expected_bindings.append(
            ("interface_sha256", module_api.get("canonical_sha256"))
        )
        if (
            target_kind == "script"
            or receipt.get("module_id") != module_api.get("module_id")
        ):
            failures.add("MODULE_COMPILATION_INTERFACE_BINDING")
    if implementation is not None:
        expected_bindings.append(
            (
                "implementation_sha256",
                implementation.get("implementation_sha256"),
            )
        )
        if (
            receipt.get("target_id") != implementation.get("target_id")
            or receipt.get("module_id") != implementation.get("module_id")
            or target_kind != implementation.get("target_kind")
            or receipt.get("interface_sha256")
            != implementation.get("interface_sha256")
        ):
            failures.add("MODULE_COMPILATION_IMPLEMENTATION_BINDING")
    for field, expected in expected_bindings:
        if receipt.get(field) != expected:
            failures.add("MODULE_COMPILATION_ARTIFACT_BINDING")

    digest = receipt.get("compilation_receipt_sha256")
    if (
        re.fullmatch(r"[0-9a-f]{64}", str(digest or "")) is None
        or digest
        != canonical_self_digest(receipt, "compilation_receipt_sha256")
    ):
        failures.add("MODULE_COMPILATION_RECEIPT_DIGEST")
    return failures


def r4_module_artifact_relation_fixture_failure_codes(
    registry: dict[str, Any],
    module_api_fixtures: dict[str, Any],
) -> set[str]:
    """Validate the executable static relation fixture for all three domains."""

    failures: set[str] = set()
    expected_registry_fields = {
        "schema",
        "profile",
        "canonicalization",
        "interface_fixture_binding",
        "provider_interfaces",
        "shared_inputs",
        "case_count",
        "cases",
        "expected_relations",
        "evidence_level",
        "product_compiler_execution",
    }
    if (
        set(registry) != expected_registry_fields
        or has_non_unicode_scalar(registry)
        or
        registry.get("schema")
        != "deeplus.module-compilation-artifact-relations-fixtures/r1"
        or registry.get("profile") != "R4_NAME_RESOLUTION_MODULES"
        or registry.get("case_count") != 2
        or registry.get("evidence_level")
        != "E2_STATIC_HASH_RELATION_FIXTURE"
        or registry.get("product_compiler_execution") != "NOT_RUN"
    ):
        failures.add("MODULE_ARTIFACT_FIXTURE_PROFILE")
    if has_non_unicode_scalar(registry):
        return failures | {"CANONICAL_JSON_NON_UNICODE_SCALAR"}
    if not is_canonical_json_value(registry):
        return failures | {"CANONICAL_JSON_INVALID_VALUE_DOMAIN"}

    canonicalization = registry.get("canonicalization", {})
    conformance_vector = canonicalization.get("conformance_vector", {})
    vector_input = conformance_vector.get("input")
    expected_canonicalization = {
        "json_algorithm": "DEEPLUS_CANONICAL_JSON_UTF8_SHA256_V1",
        "json_algorithm_contract": {
            "object_member_order": (
                "ASCENDING_UNICODE_SCALAR_KEY_ORDER_RECURSIVE"
            ),
            "string_encoding": (
                "JSON_MANDATORY_ESCAPES_OTHER_SCALARS_DIRECT_UTF8_"
                "NO_NORMALIZATION"
            ),
            "number_domain": (
                "SCHEMA_VALIDATED_INTEGER_ONLY_FOR_CURRENT_R4_"
                "DIGEST_ARTIFACTS"
            ),
            "whitespace": "NONE_OUTSIDE_STRING_VALUES",
            "terminal_newline": False,
        },
        "conformance_vector": {
            "input": {
                "z": "한😀",
                "a": "quote:\" slash:\\ newline:\n",
            },
            "canonical_utf8_hex": (
                "7b2261223a2271756f74653a5c2220736c6173683a5c5c206e6577"
                "6c696e653a5c6e222c227a223a22ed959cf09f9880227d"
            ),
            "sha256": (
                "333657884e20443a6ee4c742f2e894b34939238558c85e2a9cd720"
                "818169ba3c"
            ),
        },
        "json_self_hash_exclusion": {
            "package_graph": "canonical_graph_sha256",
            "resolver_graph": "resolver_graph_sha256",
            "resolver_trace": "trace_sha256",
            "visibility_closure": "closure_sha256",
            "initialization_plan": "plan_sha256",
            "module_api": "canonical_sha256",
            "module_source_contribution_projection": (
                "projection_sha256"
            ),
            "dependency_receipt": "dependency_receipt_sha256",
            "implementation_digest": "implementation_sha256",
            "compilation_receipt": "compilation_receipt_sha256",
        },
        "hir_semantic_algorithm": (
            "SHA256(domain_utf8 || u64be(byte_length) || semantic_bytes)"
        ),
        "hir_semantic_domain_utf8": "deeplus.hir.semantic/h1\0",
    }
    vector_digest = canonical_sha(vector_input)
    vector_bytes = b""
    if isinstance(vector_input, dict) and vector_digest is not None:
        vector_bytes = json.dumps(
            vector_input,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    if (
        canonicalization != expected_canonicalization
        or set(canonicalization)
        != {
            "json_algorithm",
            "json_algorithm_contract",
            "conformance_vector",
            "json_self_hash_exclusion",
            "hir_semantic_algorithm",
            "hir_semantic_domain_utf8",
        }
        or set(conformance_vector)
        != {"input", "canonical_utf8_hex", "sha256"}
        or
        canonicalization.get("json_algorithm")
        != "DEEPLUS_CANONICAL_JSON_UTF8_SHA256_V1"
        or conformance_vector.get("canonical_utf8_hex")
        != vector_bytes.hex()
        or conformance_vector.get("sha256")
        != vector_digest
        or b"\xed\x95\x9c\xf0\x9f\x98\x80" not in vector_bytes
    ):
        failures.add("MODULE_ARTIFACT_CANONICALIZATION_CONTRACT")

    binding = registry.get("interface_fixture_binding", {})
    api_fixture = next(
        (
            row
            for row in module_api_fixtures.get(
                "r4_interface_envelope_fixtures", []
            )
            if row.get("fixture_id") == binding.get("fixture_id")
        ),
        None,
    )
    module_api = (
        api_fixture.get("payload", {})
        if isinstance(api_fixture, dict)
        else {}
    )
    if (
        set(binding) != {"path", "fixture_id", "interface_sha256"}
        or
        binding.get("path")
        != "tests/fixtures/imported/module-api-digest-fixtures.json"
        or not module_api
        or binding.get("interface_sha256")
        != module_api.get("canonical_sha256")
        or r4_module_api_failure_codes(module_api)
    ):
        failures.add("MODULE_ARTIFACT_INTERFACE_BINDING")

    provider_interfaces = registry.get("provider_interfaces", {})
    if (
        not isinstance(provider_interfaces, dict)
        or not provider_interfaces
        or any(
            not isinstance(provider, dict)
            or module_id != provider.get("module_id")
            or r4_module_api_failure_codes(provider)
            for module_id, provider in provider_interfaces.items()
        )
    ):
        failures.add("MODULE_ARTIFACT_PROVIDER_INTERFACE_BINDING")

    shared = registry.get("shared_inputs", {})
    manifest_bytes = shared.get("manifest_bytes_utf8")
    provider_source_module_id = shared.get(
        "provider_source_module_id"
    )
    provider_source_file_id = shared.get("provider_source_file_id")
    provider_source_bytes = shared.get("provider_source_bytes_utf8")
    visibility_closure = shared.get("visibility_closure")
    initialization_plan = shared.get("initialization_plan")
    if (
        set(shared)
        != {
            "manifest_bytes_utf8",
            "manifest_sha256",
            "provider_source_module_id",
            "provider_source_file_id",
            "provider_source_bytes_utf8",
            "provider_source_bytes_sha256",
            "visibility_closure",
            "initialization_plan",
        }
        or
        not isinstance(manifest_bytes, str)
        or hashlib.sha256(manifest_bytes.encode("utf-8")).hexdigest()
        != shared.get("manifest_sha256")
        or not is_typed_id(
            provider_source_module_id, "ModuleId"
        )
        or not is_typed_id(
            provider_source_file_id, "SourceFileId"
        )
        or provider_source_module_id not in provider_interfaces
        or provider_source_bytes
        != "public extension Int as display {\n}\n"
        or not isinstance(provider_source_bytes, str)
        or hashlib.sha256(
            provider_source_bytes.encode("utf-8")
        ).hexdigest()
        != shared.get("provider_source_bytes_sha256")
        or not isinstance(visibility_closure, dict)
        or r4_visibility_closure_failure_codes(visibility_closure)
        or not isinstance(initialization_plan, dict)
        or r4_module_initialization_failure_codes(initialization_plan)
        or (
            isinstance(module_api, dict)
            and r4_module_api_failure_codes(
                module_api, visibility_closure
            )
        )
    ):
        failures.add("MODULE_ARTIFACT_SHARED_INPUT_DIGEST")

    cases = registry.get("cases", [])
    if (
        not isinstance(cases, list)
        or [row.get("case_id") for row in cases]
        != [
            "R4-MODULE-ARTIFACT-BASELINE",
            "R4-MODULE-ARTIFACT-PRIVATE-HIR-CHANGE",
        ]
        or [row.get("mutation_class") for row in cases]
        != [
            "BASELINE",
            "PRIVATE_SEMANTIC_BODY_CHANGE_PUBLIC_RESIDUE_UNCHANGED",
        ]
    ):
        return failures | {"MODULE_ARTIFACT_FIXTURE_CASE_SET"}

    expected_case_fields = {
        "case_id",
        "mutation_class",
        "source_file_id",
        "source_bytes_utf8",
        "source_bytes_sha256",
        "package_graph",
        "resolver_graph",
        "resolver_trace",
        "hir_semantic_digest_preimage",
        "hir_semantic_bytes_utf8",
        "hir_semantic_sha256",
        "module_source_contribution_projection",
        "dependency_receipt",
        "implementation_digest",
        "compilation_receipt",
    }
    expected_source_bytes_by_case = {
        "R4-MODULE-ARTIFACT-BASELINE": (
            "use export Int::display\n"
            "public let answer: Int = 42\n"
            "private def helper() -> Int = {\n"
            "    let _ = answer\n"
            "    return 1\n"
            "}\n"
        ),
        "R4-MODULE-ARTIFACT-PRIVATE-HIR-CHANGE": (
            "use export Int::display\n"
            "public let answer: Int = 42\n"
            "private def helper() -> Int = {\n"
            "    let _ = answer\n"
            "    return 2\n"
            "}\n"
        ),
    }
    expected_hir_preimage_by_case = {
        "R4-MODULE-ARTIFACT-BASELINE": {
            "schema": "deeplus.fixture-hir-semantic/r1",
            "module_id": "ModuleId:acme.api",
            "public_items": ["DeclId:acme.api.answer"],
            "private_bodies": [
                {
                    "decl_id": "DeclId:acme.api.helper",
                    "reference_decl_ids": [
                        "DeclId:acme.api.answer"
                    ],
                    "return_int": 1,
                }
            ],
        },
        "R4-MODULE-ARTIFACT-PRIVATE-HIR-CHANGE": {
            "schema": "deeplus.fixture-hir-semantic/r1",
            "module_id": "ModuleId:acme.api",
            "public_items": ["DeclId:acme.api.answer"],
            "private_bodies": [
                {
                    "decl_id": "DeclId:acme.api.helper",
                    "reference_decl_ids": [
                        "DeclId:acme.api.answer"
                    ],
                    "return_int": 2,
                }
            ],
        },
    }
    expected_provider_modules: set[Any] = set()
    for case in cases:
        case_id = case.get("case_id")
        source_file_id = case.get("source_file_id")
        source_bytes = case.get("source_bytes_utf8")
        package_graph = case.get("package_graph")
        resolver_graph = case.get("resolver_graph")
        resolver_trace = case.get("resolver_trace")
        hir_preimage = case.get("hir_semantic_digest_preimage")
        hir_bytes = case.get("hir_semantic_bytes_utf8")
        source_projection = case.get(
            "module_source_contribution_projection"
        )
        dependency_receipt = case.get("dependency_receipt")
        implementation = case.get("implementation_digest")
        compilation = case.get("compilation_receipt")
        if not all(
            isinstance(value, dict)
            for value in (
                package_graph,
                resolver_graph,
                resolver_trace,
                hir_preimage,
                source_projection,
                dependency_receipt,
                implementation,
                compilation,
            )
        ) or set(case) != expected_case_fields:
            failures.add("MODULE_ARTIFACT_FIXTURE_SHAPE")
            continue
        if (
            not is_typed_id(source_file_id, "SourceFileId")
            or source_bytes
            != expected_source_bytes_by_case.get(case_id)
        ):
            failures.add("MODULE_ARTIFACT_SOURCE_SURFACE")
        if hir_preimage != expected_hir_preimage_by_case.get(case_id):
            failures.add("MODULE_ARTIFACT_HIR_SOURCE_RELATION")
        package_sha = package_graph.get("canonical_graph_sha256")
        resolver_sha = resolver_graph.get("resolver_graph_sha256")
        trace_sha = resolver_trace.get("trace_sha256")
        expected_hir_bytes = json.dumps(
            hir_preimage,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        hir_domain = registry.get("canonicalization", {}).get(
            "hir_semantic_domain_utf8"
        )
        hir_payload = (
            str(hir_domain).encode("utf-8")
            + len(expected_hir_bytes.encode("utf-8")).to_bytes(8, "big")
            + expected_hir_bytes.encode("utf-8")
        )
        if (
            not isinstance(source_bytes, str)
            or hashlib.sha256(source_bytes.encode("utf-8")).hexdigest()
            != case.get("source_bytes_sha256")
            or r4_package_graph_failure_codes(package_graph)
            or r4_resolver_graph_failure_codes(resolver_graph)
            or r4_resolver_trace_failure_codes(resolver_trace)
            or resolver_graph.get("package_graph_sha256") != package_sha
            or resolver_trace.get("resolver_graph_sha256") != resolver_sha
            or hir_bytes != expected_hir_bytes
            or hashlib.sha256(hir_payload).hexdigest()
            != case.get("hir_semantic_sha256")
        ):
            failures.add("MODULE_ARTIFACT_CASE_PREIMAGE_DIGEST")

        package_rows = (
            package_graph.get("packages", [])
            if isinstance(package_graph.get("packages"), list)
            else []
        )
        target_rows = (
            package_graph.get("targets", [])
            if isinstance(package_graph.get("targets"), list)
            else []
        )
        source_rows = (
            package_graph.get("source_contributions", [])
            if isinstance(
                package_graph.get("source_contributions"), list
            )
            else []
        )
        visible_module_rows = (
            package_graph.get("visible_module_bindings", [])
            if isinstance(
                package_graph.get("visible_module_bindings"), list
            )
            else []
        )
        root_package_rows = [
            row
            for row in package_rows
            if isinstance(row, dict)
            and row.get("package_id")
            == package_graph.get("root_package_id")
        ]
        if (
            len(root_package_rows) != 1
            or root_package_rows[0].get(
                "resolved_artifact_provenance_digest"
            )
            != shared.get("manifest_sha256")
        ):
            failures.add("MODULE_ARTIFACT_MANIFEST_GRAPH_BINDING")

        projection_rows = (
            source_projection.get("source_contributions", [])
            if isinstance(
                source_projection.get("source_contributions"), list
            )
            else []
        )
        consumer_source_rows = [
            row
            for row in source_rows
            if isinstance(row, dict)
            and row.get("source_file_id") == source_file_id
        ]
        consumer_projection_rows = [
            row
            for row in projection_rows
            if isinstance(row, dict)
            and row.get("source_file_id") == source_file_id
        ]
        if (
            len(consumer_source_rows) != 1
            or len(consumer_projection_rows) != 1
            or consumer_source_rows[0].get("target_id")
            != source_projection.get("target_id")
            or consumer_source_rows[0].get("module_id")
            != source_projection.get("module_id")
            or consumer_source_rows[0].get("source_bytes_sha256")
            != case.get("source_bytes_sha256")
            or consumer_projection_rows[0].get(
                "source_bytes_sha256"
            )
            != case.get("source_bytes_sha256")
        ):
            failures.add("MODULE_ARTIFACT_CONSUMER_SOURCE_BINDING")

        provider_source_rows = [
            row
            for row in source_rows
            if isinstance(row, dict)
            and row.get("source_file_id") == provider_source_file_id
            and row.get("module_id") == provider_source_module_id
        ]
        if (
            len(provider_source_rows) != 1
            or provider_source_rows[0].get("source_bytes_sha256")
            != shared.get("provider_source_bytes_sha256")
        ):
            failures.add("MODULE_ARTIFACT_PROVIDER_SOURCE_BINDING")

        package_by_id = {
            row.get("package_id"): row
            for row in package_rows
            if isinstance(row, dict)
            and isinstance(row.get("package_id"), str)
        }
        target_by_id = {
            row.get("target_id"): row
            for row in target_rows
            if isinstance(row, dict)
            and isinstance(row.get("target_id"), str)
        }
        source_by_id = {
            row.get("source_file_id"): row
            for row in source_rows
            if isinstance(row, dict)
            and isinstance(row.get("source_file_id"), str)
        }
        resolver_scopes = (
            resolver_graph.get("scopes", [])
            if isinstance(resolver_graph.get("scopes"), list)
            else []
        )
        scope_by_id = {
            row.get("resolver_scope_id"): row
            for row in resolver_scopes
            if isinstance(row, dict)
            and isinstance(row.get("resolver_scope_id"), str)
        }
        resolver_package_relation_valid = True
        for scope in resolver_scopes:
            if not isinstance(scope, dict):
                resolver_package_relation_valid = False
                continue
            kind = scope.get("kind")
            parent = scope_by_id.get(scope.get("parent_scope_id_or_null"))
            if kind == "PackageRootScope":
                resolver_package_relation_valid &= (
                    scope.get("package_id") in package_by_id
                )
            elif kind == "TargetScope":
                target = target_by_id.get(scope.get("target_id"))
                resolver_package_relation_valid &= (
                    isinstance(target, dict)
                    and isinstance(parent, dict)
                    and parent.get("kind") == "PackageRootScope"
                    and parent.get("package_id")
                    == target.get("package_id")
                )
            elif kind == "ModuleScope":
                target = (
                    target_by_id.get(parent.get("target_id"))
                    if isinstance(parent, dict)
                    else None
                )
                resolver_package_relation_valid &= (
                    isinstance(parent, dict)
                    and parent.get("kind") == "TargetScope"
                    and isinstance(target, dict)
                    and any(
                        row.get("target_id") == target.get("target_id")
                        and row.get("module_id") == scope.get("module_id")
                        for row in source_rows
                        if isinstance(row, dict)
                    )
                )
            elif kind == "SourceContributionScope":
                source = source_by_id.get(scope.get("source_file_id"))
                module_scope = parent
                target_scope = (
                    scope_by_id.get(
                        module_scope.get("parent_scope_id_or_null")
                    )
                    if isinstance(module_scope, dict)
                    else None
                )
                resolver_package_relation_valid &= (
                    isinstance(source, dict)
                    and isinstance(module_scope, dict)
                    and module_scope.get("kind") == "ModuleScope"
                    and source.get("module_id")
                    == module_scope.get("module_id")
                    and isinstance(target_scope, dict)
                    and target_scope.get("kind") == "TargetScope"
                    and source.get("target_id")
                    == target_scope.get("target_id")
                )
        if not resolver_package_relation_valid:
            failures.add("MODULE_ARTIFACT_RESOLVER_PACKAGE_BINDING")

        resolver_imports = (
            resolver_graph.get("import_bindings", [])
            if isinstance(
                resolver_graph.get("import_bindings"), list
            )
            else []
        )
        resolver_activations = (
            resolver_graph.get("activation_entries", [])
            if isinstance(
                resolver_graph.get("activation_entries"), list
            )
            else []
        )
        resolver_witnesses = (
            resolver_graph.get("witness_visibility_entries", [])
            if isinstance(
                resolver_graph.get("witness_visibility_entries"), list
            )
            else []
        )
        consumer_module_id = dependency_receipt.get(
            "consumer_module_id"
        )
        provider_api_residue_valid = True
        for row in [*resolver_imports, *resolver_activations]:
            if not isinstance(row, dict):
                provider_api_residue_valid = False
                continue
            provider_module_id = row.get("provider_module_id")
            if provider_module_id == consumer_module_id:
                continue
            expected_provider_modules.add(provider_module_id)
            provider_api = provider_interfaces.get(provider_module_id)
            envelope = (
                provider_api.get("r4_interface_envelope", {})
                if isinstance(provider_api, dict)
                else {}
            )
            if "activated_identity" in row:
                provider_api_residue_valid &= any(
                    candidate.get("export_owner_id")
                    == provider_module_id
                    and candidate.get(
                        "referenced_activation_identity_id"
                    )
                    == row.get("activated_identity")
                    for candidate in envelope.get(
                        "public_activation_reexport_rows", []
                    )
                    if isinstance(candidate, dict)
                )
            else:
                resolved_identity = row.get(
                    "resolved_target_identity"
                )
                provider_api_residue_valid &= (
                    (
                        row.get("namespace") == "MODULE"
                        and resolved_identity == provider_module_id
                    )
                    or any(
                        candidate.get("namespace")
                        == row.get("namespace")
                        and candidate.get(
                            "referenced_identity_id"
                        )
                        == resolved_identity
                        for candidate in envelope.get(
                            "public_export_rows", []
                        )
                        if isinstance(candidate, dict)
                    )
                )
        if not provider_api_residue_valid:
            failures.add("MODULE_ARTIFACT_PROVIDER_API_RESIDUE")

        resolver_name_bindings = (
            resolver_graph.get("name_bindings", [])
            if isinstance(
                resolver_graph.get("name_bindings"), list
            )
            else []
        )
        resolver_binding_ids = {
            row.get("typed_identity")
            for row in resolver_name_bindings
            if isinstance(row, dict)
        } | {
            row.get("resolved_target_identity")
            for row in resolver_imports
            if isinstance(row, dict)
        }
        resolver_binding_ids.discard(None)
        export_identity_ids = {
            row.get("referenced_identity_id")
            for row in visibility_closure.get("export_edges", [])
            if isinstance(row, dict)
        }
        resolver_activation_pairs = {
            (
                row.get("activation_origin_id"),
                row.get("activated_identity"),
            )
            for row in resolver_activations
            if isinstance(row, dict)
        }
        reexport_activation_pairs = {
            (
                row.get("activation_origin_id"),
                row.get("referenced_activation_identity_id"),
            )
            for row in visibility_closure.get("reexport_edges", [])
            if isinstance(row, dict)
        }
        if (
            not export_identity_ids.issubset(resolver_binding_ids)
            or not reexport_activation_pairs.issubset(
                resolver_activation_pairs
            )
        ):
            failures.add("MODULE_ARTIFACT_PUBLIC_RESIDUE_RELATION")

        initialization_binding_ids = {
            row.get("binding_decl_id")
            for row in initialization_plan.get("bindings", [])
            if isinstance(row, dict)
        }
        if not initialization_binding_ids.issubset(
            resolver_binding_ids
        ):
            failures.add("MODULE_ARTIFACT_INITIALIZATION_RELATION")

        graph_candidate_ids = set(resolver_binding_ids)
        for row in resolver_name_bindings:
            if isinstance(row, dict):
                graph_candidate_ids.update(
                    value
                    for value in (
                        row.get("hir_body_id_or_null"),
                        row.get("owner_local_binding_id_or_null"),
                    )
                    if value is not None
                )
        graph_candidate_ids.update(
            row.get("import_binding_id")
            for row in resolver_imports
            if isinstance(row, dict)
        )
        graph_candidate_ids.update(
            value
            for row in resolver_activations
            if isinstance(row, dict)
            for value in (
                row.get("activation_origin_id"),
                row.get("activated_identity"),
            )
        )
        graph_candidate_ids.update(
            value
            for row in resolver_witnesses
            if isinstance(row, dict)
            for value in (
                row.get("evidence_origin_id"),
                row.get("visible_witness_identity"),
            )
        )
        graph_candidate_ids.update(
            row.get("resolved_module_id")
            for row in visible_module_rows
            if isinstance(row, dict)
        )
        graph_candidate_ids.discard(None)
        import_ids = {
            row.get("import_binding_id")
            for row in resolver_imports
            if isinstance(row, dict)
        }
        activation_ids = {
            row.get("activation_origin_id")
            for row in resolver_activations
            if isinstance(row, dict)
        }
        evidence_ids = {
            row.get("evidence_origin_id")
            for row in resolver_witnesses
            if isinstance(row, dict)
        }
        proof_by_id = {
            row.get("proof_id"): row
            for row in visibility_closure.get(
                "visibility_proofs", []
            )
            if isinstance(row, dict)
        }
        source_bytes_by_file_id = {
            source_file_id: source_bytes,
            provider_source_file_id: provider_source_bytes,
        }
        trace_graph_valid = True
        trace_visibility_valid = True
        trace_source_valid = True
        for reference in resolver_trace.get("references", []):
            if not isinstance(reference, dict):
                trace_graph_valid = False
                continue
            trace_graph_valid &= (
                reference.get("resolver_scope_id") in scope_by_id
            )
            candidate_ids = set(
                reference.get("candidate_origin_ids", [])
            )
            trace_graph_valid &= candidate_ids.issubset(
                graph_candidate_ids
            )
            result = reference.get("result", {})
            resolved_identity = (
                result.get("resolved_identity")
                if isinstance(result, dict)
                else None
            )
            if resolved_identity is not None:
                trace_graph_valid &= (
                    resolved_identity in candidate_ids
                    and resolved_identity in graph_candidate_ids
                )
            optional_origin_sets = (
                ("import_binding_id_or_null", import_ids),
                ("activation_origin_id_or_null", activation_ids),
                ("evidence_origin_id_or_null", evidence_ids),
            )
            for field, admitted_ids in optional_origin_sets:
                value = reference.get(field)
                if value is not None:
                    trace_graph_valid &= value in admitted_ids
            proof_ids = set(reference.get("visibility_proof_ids", []))
            trace_visibility_valid &= proof_ids.issubset(
                set(proof_by_id)
            )
            if resolved_identity is not None and proof_ids:
                trace_visibility_valid &= any(
                    proof_by_id[proof_id].get(
                        "referenced_identity_id"
                    )
                    == resolved_identity
                    for proof_id in proof_ids
                    if proof_id in proof_by_id
                )

            source_scope = scope_by_id.get(
                reference.get("resolver_scope_id")
            )
            trace_source_bytes = (
                source_bytes_by_file_id.get(
                    source_scope.get("source_file_id")
                )
                if isinstance(source_scope, dict)
                and source_scope.get("kind")
                == "SourceContributionScope"
                else None
            )
            span = reference.get("source_span", {})
            start = span.get("start") if isinstance(span, dict) else None
            end = span.get("end") if isinstance(span, dict) else None
            if (
                not isinstance(trace_source_bytes, str)
                or type(start) is not int
                or type(end) is not int
            ):
                trace_source_valid = False
            else:
                source_utf8 = trace_source_bytes.encode("utf-8")
                try:
                    observed_spelling = source_utf8[start:end].decode(
                        "utf-8"
                    )
                except UnicodeDecodeError:
                    observed_spelling = None
                trace_source_valid &= (
                    0 <= start <= end <= len(source_utf8)
                    and observed_spelling
                    == reference.get("source_spelling")
                )
        if not trace_graph_valid:
            failures.add("MODULE_ARTIFACT_TRACE_GRAPH_RELATION")
        if not trace_visibility_valid:
            failures.add("MODULE_ARTIFACT_TRACE_VISIBILITY_RELATION")
        if not trace_source_valid:
            failures.add("MODULE_ARTIFACT_TRACE_SOURCE_BINDING")

        if (
            r4_module_source_projection_failure_codes(
                source_projection, package_graph
            )
            or source_projection.get("projection_sha256")
            != compilation.get(
                "module_source_contribution_sha256"
            )
        ):
            failures.add("MODULE_ARTIFACT_SOURCE_PROJECTION")
        if (
            r4_dependency_receipt_failure_codes(
                dependency_receipt,
                resolver_graph=resolver_graph,
                provider_interfaces=provider_interfaces,
                package_graph=package_graph,
            )
            or dependency_receipt.get("package_graph_sha256")
            != package_sha
            or dependency_receipt.get("resolver_graph_sha256")
            != resolver_sha
        ):
            failures.add("MODULE_ARTIFACT_DEPENDENCY_RECEIPT")
        if r4_module_implementation_failure_codes(
            implementation, module_api
        ) or implementation.get("hir_semantic_sha256") != case.get(
            "hir_semantic_sha256"
        ):
            failures.add("MODULE_ARTIFACT_IMPLEMENTATION")

        relation_failures = r4_compilation_receipt_failure_codes(
            compilation,
            package_graph=package_graph,
            source_projection=source_projection,
            dependency_receipt=dependency_receipt,
            resolver_trace=resolver_trace,
            visibility_closure=visibility_closure,
            initialization_plan=initialization_plan,
            module_api=module_api,
            implementation=implementation,
        )
        if relation_failures:
            failures.add("MODULE_ARTIFACT_COMPILATION_RELATION")

    if (
        set(provider_interfaces) != expected_provider_modules
        or expected_provider_modules
        != {provider_source_module_id}
    ):
        failures.add("MODULE_ARTIFACT_PROVIDER_SET_CLOSURE")

    if len(cases) == 2:
        baseline, changed = cases
        expected_relations = registry.get("expected_relations", {})
        observed_relations = {
            "interface_sha256_equal_across_cases": (
                baseline.get("implementation_digest", {}).get(
                    "interface_sha256"
                )
                == changed.get("implementation_digest", {}).get(
                    "interface_sha256"
                )
            ),
            "visibility_closure_sha256_equal_across_cases": (
                baseline.get("compilation_receipt", {}).get(
                    "visibility_closure_sha256"
                )
                == changed.get("compilation_receipt", {}).get(
                    "visibility_closure_sha256"
                )
            ),
            "initialization_plan_sha256_equal_across_cases": (
                baseline.get("compilation_receipt", {}).get(
                    "initialization_plan_sha256"
                )
                == changed.get("compilation_receipt", {}).get(
                    "initialization_plan_sha256"
                )
            ),
            "source_bytes_sha256_different_across_cases": (
                baseline.get("source_bytes_sha256")
                != changed.get("source_bytes_sha256")
            ),
            "module_source_contribution_sha256_different_across_cases": (
                baseline.get(
                    "module_source_contribution_projection", {}
                ).get("projection_sha256")
                != changed.get(
                    "module_source_contribution_projection", {}
                ).get("projection_sha256")
            ),
            "package_graph_sha256_different_across_cases": (
                baseline.get("package_graph", {}).get(
                    "canonical_graph_sha256"
                )
                != changed.get("package_graph", {}).get(
                    "canonical_graph_sha256"
                )
            ),
            "resolver_graph_sha256_different_across_cases": (
                baseline.get("resolver_graph", {}).get(
                    "resolver_graph_sha256"
                )
                != changed.get("resolver_graph", {}).get(
                    "resolver_graph_sha256"
                )
            ),
            "resolver_trace_sha256_different_across_cases": (
                baseline.get("resolver_trace", {}).get("trace_sha256")
                != changed.get("resolver_trace", {}).get(
                    "trace_sha256"
                )
            ),
            "dependency_receipt_sha256_different_across_cases": (
                baseline.get("dependency_receipt", {}).get(
                    "dependency_receipt_sha256"
                )
                != changed.get("dependency_receipt", {}).get(
                    "dependency_receipt_sha256"
                )
            ),
            "hir_semantic_sha256_different_across_cases": (
                baseline.get("hir_semantic_sha256")
                != changed.get("hir_semantic_sha256")
            ),
            "implementation_sha256_different_across_cases": (
                baseline.get("implementation_digest", {}).get(
                    "implementation_sha256"
                )
                != changed.get("implementation_digest", {}).get(
                    "implementation_sha256"
                )
            ),
            "compilation_receipt_sha256_different_across_cases": (
                baseline.get("compilation_receipt", {}).get(
                    "compilation_receipt_sha256"
                )
                != changed.get("compilation_receipt", {}).get(
                    "compilation_receipt_sha256"
                )
            ),
            "private_body_bytes_in_interface_hash": (
                module_api.get("r4_interface_envelope", {}).get(
                    "private_body_bytes_in_interface_hash"
                )
            ),
        }
        if expected_relations != observed_relations or not all(
            value is True
            for key, value in observed_relations.items()
            if key != "private_body_bytes_in_interface_hash"
        ) or observed_relations.get(
            "private_body_bytes_in_interface_hash"
        ) is not False:
            failures.add("MODULE_ARTIFACT_CHANGE_MATRIX")
    return failures


def r4_module_artifact_relation_fixture_mutation_results(
    registry: dict[str, Any],
    module_api_fixtures: dict[str, Any],
) -> list[tuple[bool, str, str]]:
    """Reseal adversarial actual-fixture mutations and require relations."""

    def clone(value: Any) -> Any:
        return json.loads(json.dumps(value))

    def reseal(value: dict[str, Any], field: str) -> None:
        value[field] = canonical_self_digest(value, field)

    def reseal_registry(mutant: dict[str, Any]) -> None:
        shared = mutant["shared_inputs"]
        shared["manifest_sha256"] = hashlib.sha256(
            shared["manifest_bytes_utf8"].encode("utf-8")
        ).hexdigest()
        shared["provider_source_bytes_sha256"] = hashlib.sha256(
            shared["provider_source_bytes_utf8"].encode("utf-8")
        ).hexdigest()
        reseal(shared["visibility_closure"], "closure_sha256")
        reseal(shared["initialization_plan"], "plan_sha256")
        for provider in mutant["provider_interfaces"].values():
            reseal(provider, "canonical_sha256")
        api_fixture = next(
            row
            for row in module_api_fixtures.get(
                "r4_interface_envelope_fixtures", []
            )
            if row.get("fixture_id")
            == mutant["interface_fixture_binding"]["fixture_id"]
        )
        module_api = api_fixture["payload"]
        hir_domain = mutant["canonicalization"][
            "hir_semantic_domain_utf8"
        ].encode("utf-8")
        for case in mutant["cases"]:
            case["source_bytes_sha256"] = hashlib.sha256(
                case["source_bytes_utf8"].encode("utf-8")
            ).hexdigest()
            package_graph = case["package_graph"]
            reseal(package_graph, "canonical_graph_sha256")
            resolver_graph = case["resolver_graph"]
            resolver_graph["package_graph_sha256"] = package_graph[
                "canonical_graph_sha256"
            ]
            reseal(resolver_graph, "resolver_graph_sha256")
            resolver_trace = case["resolver_trace"]
            resolver_trace["resolver_graph_sha256"] = resolver_graph[
                "resolver_graph_sha256"
            ]
            reseal(resolver_trace, "trace_sha256")
            hir_bytes = json.dumps(
                case["hir_semantic_digest_preimage"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            case["hir_semantic_bytes_utf8"] = hir_bytes
            encoded_hir = hir_bytes.encode("utf-8")
            case["hir_semantic_sha256"] = hashlib.sha256(
                hir_domain
                + len(encoded_hir).to_bytes(8, "big")
                + encoded_hir
            ).hexdigest()
            source_projection = case[
                "module_source_contribution_projection"
            ]
            reseal(source_projection, "projection_sha256")
            dependency_receipt = case["dependency_receipt"]
            dependency_receipt[
                "package_graph_sha256"
            ] = package_graph["canonical_graph_sha256"]
            dependency_receipt[
                "resolver_graph_sha256"
            ] = resolver_graph["resolver_graph_sha256"]
            for row in dependency_receipt["required_interfaces"]:
                provider = mutant["provider_interfaces"].get(
                    row["provider_module_id"]
                )
                if provider is not None:
                    row["interface_sha256"] = provider[
                        "canonical_sha256"
                    ]
            reseal(
                dependency_receipt, "dependency_receipt_sha256"
            )
            implementation = case["implementation_digest"]
            implementation["interface_sha256"] = module_api[
                "canonical_sha256"
            ]
            implementation["hir_semantic_sha256"] = case[
                "hir_semantic_sha256"
            ]
            reseal(implementation, "implementation_sha256")
            compilation = case["compilation_receipt"]
            compilation.update(
                package_graph_sha256=package_graph[
                    "canonical_graph_sha256"
                ],
                module_source_contribution_sha256=source_projection[
                    "projection_sha256"
                ],
                dependency_receipt_sha256=dependency_receipt[
                    "dependency_receipt_sha256"
                ],
                resolver_trace_sha256=resolver_trace["trace_sha256"],
                visibility_closure_sha256=shared[
                    "visibility_closure"
                ]["closure_sha256"],
                initialization_plan_sha256=shared[
                    "initialization_plan"
                ]["plan_sha256"],
                interface_sha256=module_api["canonical_sha256"],
                implementation_sha256=implementation[
                    "implementation_sha256"
                ],
            )
            reseal(compilation, "compilation_receipt_sha256")

    def extra_provider(mutant: dict[str, Any]) -> None:
        provider = clone(
            mutant["provider_interfaces"]["ModuleId:acme.display"]
        )
        provider["module_id"] = "ModuleId:unused"
        provider["r4_interface_envelope"][
            "public_activation_reexport_rows"
        ][0]["export_owner_id"] = "ModuleId:unused"
        mutant["provider_interfaces"]["ModuleId:unused"] = provider

    def ghost_trace_candidate(mutant: dict[str, Any]) -> None:
        reference = mutant["cases"][0]["resolver_trace"][
            "references"
        ][0]
        reference["candidate_origin_ids"] = ["DeclId:ghost"]
        reference["result"]["resolved_identity"] = "DeclId:ghost"

    def public_residue_divergence(mutant: dict[str, Any]) -> None:
        case = mutant["cases"][0]
        binding = case["resolver_graph"]["name_bindings"][0]
        binding["local_name"] = "ghost"
        binding["typed_identity"] = "DeclId:ghost"
        binding["source_origin_id"] = "SourceOriginId:ghost"
        reference = case["resolver_trace"]["references"][0]
        reference["candidate_origin_ids"] = ["DeclId:ghost"]
        reference["result"]["resolved_identity"] = "DeclId:ghost"

    def ghost_initialization(mutant: dict[str, Any]) -> None:
        plan = mutant["shared_inputs"]["initialization_plan"]
        plan["bindings"][0]["binding_decl_id"] = "DeclId:ghost"
        plan["topological_evaluation_order"] = ["DeclId:ghost"]

    def graph_unbound_provider(mutant: dict[str, Any]) -> None:
        graph = mutant["cases"][0]["package_graph"]
        graph["visible_module_bindings"] = [
            row
            for row in graph["visible_module_bindings"]
            if row["resolved_module_id"] != "ModuleId:acme.display"
        ]

    mutations: list[
        tuple[str, str, Any, bool]
    ] = [
        (
            "canonical-contract",
            "MODULE_ARTIFACT_CANONICALIZATION_CONTRACT",
            lambda value: value["canonicalization"][
                "json_algorithm_contract"
            ].__setitem__("whitespace", "DRIFT"),
            True,
        ),
        (
            "self-hash-exclusion-contract",
            "MODULE_ARTIFACT_CANONICALIZATION_CONTRACT",
            lambda value: value["canonicalization"][
                "json_self_hash_exclusion"
            ].__setitem__("package_graph", "wrong"),
            True,
        ),
        (
            "hir-algorithm-contract",
            "MODULE_ARTIFACT_CANONICALIZATION_CONTRACT",
            lambda value: value["canonicalization"].__setitem__(
                "hir_semantic_algorithm", "wrong"
            ),
            True,
        ),
        (
            "hir-domain-rebound",
            "MODULE_ARTIFACT_CANONICALIZATION_CONTRACT",
            lambda value: value["canonicalization"].__setitem__(
                "hir_semantic_domain_utf8", "evil\0"
            ),
            True,
        ),
        (
            "consumer-source-drift",
            "MODULE_ARTIFACT_SOURCE_SURFACE",
            lambda value: value["cases"][0].__setitem__(
                "source_bytes_utf8",
                value["cases"][0]["source_bytes_utf8"] + "// drift\n",
            ),
            True,
        ),
        (
            "provider-source-drift",
            "MODULE_ARTIFACT_PROVIDER_SOURCE_BINDING",
            lambda value: value["shared_inputs"].__setitem__(
                "provider_source_bytes_utf8",
                value["shared_inputs"]["provider_source_bytes_utf8"]
                + "// drift\n",
            ),
            True,
        ),
        (
            "manifest-source-drift",
            "MODULE_ARTIFACT_MANIFEST_GRAPH_BINDING",
            lambda value: value["shared_inputs"].__setitem__(
                "manifest_bytes_utf8",
                value["shared_inputs"]["manifest_bytes_utf8"]
                + "feature drift\n",
            ),
            True,
        ),
        (
            "consumer-graph-source-drift",
            "MODULE_ARTIFACT_CONSUMER_SOURCE_BINDING",
            lambda value: next(
                row
                for row in value["cases"][0]["package_graph"][
                    "source_contributions"
                ]
                if row["module_id"] == "ModuleId:acme.api"
            ).__setitem__("source_bytes_sha256", "1" * 64),
            True,
        ),
        (
            "provider-graph-source-drift",
            "MODULE_ARTIFACT_PROVIDER_SOURCE_BINDING",
            lambda value: next(
                row
                for row in value["cases"][0]["package_graph"][
                    "source_contributions"
                ]
                if row["module_id"] == "ModuleId:acme.display"
            ).__setitem__("source_bytes_sha256", "2" * 64),
            True,
        ),
        (
            "manifest-graph-drift",
            "MODULE_ARTIFACT_MANIFEST_GRAPH_BINDING",
            lambda value: value["cases"][0]["package_graph"][
                "packages"
            ][0].__setitem__(
                "resolved_artifact_provenance_digest", "3" * 64
            ),
            True,
        ),
        (
            "pseudo-provider-residue",
            "MODULE_ARTIFACT_PROVIDER_API_RESIDUE",
            lambda value: value["provider_interfaces"][
                "ModuleId:acme.display"
            ]["r4_interface_envelope"][
                "public_activation_reexport_rows"
            ][0].__setitem__(
                "referenced_activation_identity_id",
                "ExtensionSetId:pseudo",
            ),
            True,
        ),
        (
            "extra-provider",
            "MODULE_ARTIFACT_PROVIDER_SET_CLOSURE",
            extra_provider,
            True,
        ),
        (
            "ghost-target-scope",
            "MODULE_ARTIFACT_RESOLVER_PACKAGE_BINDING",
            lambda value: next(
                row
                for row in value["cases"][0]["resolver_graph"]["scopes"]
                if row["kind"] == "TargetScope"
            ).__setitem__("target_id", "TargetId:ghost"),
            True,
        ),
        (
            "ghost-source-scope",
            "MODULE_ARTIFACT_RESOLVER_PACKAGE_BINDING",
            lambda value: next(
                row
                for row in value["cases"][0]["resolver_graph"]["scopes"]
                if row["kind"] == "SourceContributionScope"
            ).__setitem__("source_file_id", "SourceFileId:ghost"),
            True,
        ),
        (
            "ghost-module-scope",
            "MODULE_ARTIFACT_RESOLVER_PACKAGE_BINDING",
            lambda value: next(
                row
                for row in value["cases"][0]["resolver_graph"]["scopes"]
                if row["kind"] == "ModuleScope"
            ).__setitem__("module_id", "ModuleId:ghost"),
            True,
        ),
        (
            "ghost-trace-scope",
            "MODULE_ARTIFACT_TRACE_GRAPH_RELATION",
            lambda value: value["cases"][0]["resolver_trace"][
                "references"
            ][0].__setitem__(
                "resolver_scope_id", "ResolverScopeId:ghost"
            ),
            True,
        ),
        (
            "ghost-trace-candidate",
            "MODULE_ARTIFACT_TRACE_GRAPH_RELATION",
            ghost_trace_candidate,
            True,
        ),
        (
            "ghost-trace-proof",
            "MODULE_ARTIFACT_TRACE_VISIBILITY_RELATION",
            lambda value: value["cases"][0]["resolver_trace"][
                "references"
            ][0].__setitem__(
                "visibility_proof_ids",
                ["VisibilityProofId:ghost"],
            ),
            True,
        ),
        (
            "trace-source-span-drift",
            "MODULE_ARTIFACT_TRACE_SOURCE_BINDING",
            lambda value: value["cases"][0]["resolver_trace"][
                "references"
            ][0]["source_span"].__setitem__("start", 95),
            True,
        ),
        (
            "resolver-public-residue-divergence",
            "MODULE_ARTIFACT_PUBLIC_RESIDUE_RELATION",
            public_residue_divergence,
            True,
        ),
        (
            "ghost-initialization-binding",
            "MODULE_ARTIFACT_INITIALIZATION_RELATION",
            ghost_initialization,
            True,
        ),
        (
            "hir-source-divergence",
            "MODULE_ARTIFACT_HIR_SOURCE_RELATION",
            lambda value: value["cases"][0][
                "hir_semantic_digest_preimage"
            ]["private_bodies"][0].__setitem__("return_int", 99),
            True,
        ),
        (
            "graph-unbound-provider",
            "MODULE_ARTIFACT_DEPENDENCY_RECEIPT",
            graph_unbound_provider,
            True,
        ),
        (
            "missing-provider",
            "MODULE_ARTIFACT_PROVIDER_SET_CLOSURE",
            lambda value: value["provider_interfaces"].pop(
                "ModuleId:acme.display"
            ),
            True,
        ),
        (
            "stale-dependency-digest",
            "MODULE_ARTIFACT_DEPENDENCY_RECEIPT",
            lambda value: value["cases"][0][
                "dependency_receipt"
            ].__setitem__("dependency_receipt_sha256", "0" * 64),
            False,
        ),
        (
            "unknown-provider-field",
            "MODULE_ARTIFACT_PROVIDER_INTERFACE_BINDING",
            lambda value: value["provider_interfaces"][
                "ModuleId:acme.display"
            ].__setitem__("unknown", True),
            True,
        ),
        (
            "change-matrix-tamper",
            "MODULE_ARTIFACT_CHANGE_MATRIX",
            lambda value: value["expected_relations"].__setitem__(
                "interface_sha256_equal_across_cases", False
            ),
            False,
        ),
    ]
    results: list[tuple[bool, str, str]] = []
    for mutation_id, expected_failure, mutate, should_reseal in mutations:
        mutant = clone(registry)
        mutate(mutant)
        if should_reseal:
            reseal_registry(mutant)
        observed = r4_module_artifact_relation_fixture_failure_codes(
            mutant, module_api_fixtures
        )
        results.append(
            (
                expected_failure in observed,
                mutation_id,
                (
                    f"expected={expected_failure} "
                    f"observed={sorted(observed)}"
                ),
            )
        )
    return results


def has_exact_object_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def is_canonically_sorted(
    values: Any, key: Any = lambda value: value
) -> bool:
    if not isinstance(values, list):
        return False
    try:
        return values == sorted(values, key=key)
    except (TypeError, ValueError):
        return False


def r4_package_graph_shape_and_order_failure_codes(
    graph: dict[str, Any],
) -> set[str]:
    """Bind the executable graph helper to its closed schema and ordering."""

    failures: set[str] = set()
    top_fields = {
        "schema",
        "root_package_id",
        "packages",
        "targets",
        "source_contributions",
        "dependency_bindings",
        "visible_module_bindings",
        "module_header_import_edges",
        "graph_policy",
        "canonical_order",
        "canonical_graph_sha256",
    }
    package_fields = {
        "package_id",
        "canonical_package_key",
        "resolved_artifact_provenance_digest",
        "dependency_binding_ids",
        "target_ids",
    }
    package_key_fields = {
        "registry_namespace",
        "package_name",
        "package_version_identity",
    }
    target_fields = {
        "target_id",
        "package_id",
        "canonical_manifest_target_name",
        "target_kind",
        "source_role_policy",
        "activation_profile",
        "source_file_ids",
    }
    source_fields = {
        "source_file_id",
        "target_id",
        "normalized_project_relative_path",
        "source_role",
        "activation_profile",
        "module_id",
        "module_path",
        "explicit_module_path_or_null",
        "source_bytes_sha256",
    }
    dependency_fields = {
        "dependency_binding_id",
        "consumer_package_id",
        "source_visible_binding",
        "provider_package_id",
        "provider_interface_sha256",
    }
    visible_fields = {
        "consumer_target_id",
        "visible_qualified_path",
        "resolved_module_id",
        "dependency_binding_id_or_self",
    }
    header_edge_fields = {
        "from_module_id",
        "to_module_id",
        "edge_kind",
        "source_origin_id",
        "scc_admission",
    }
    graph_policy_fields = {
        "package_dependency",
        "module_header_import",
        "reexport",
        "static_binding_value_dependency",
    }
    arrays_and_fields = (
        ("packages", package_fields),
        ("targets", target_fields),
        ("source_contributions", source_fields),
        ("dependency_bindings", dependency_fields),
        ("visible_module_bindings", visible_fields),
        ("module_header_import_edges", header_edge_fields),
    )
    if (
        not has_exact_object_keys(graph, top_fields)
        or graph.get("schema")
        != "deeplus.package-module-source-graph/r1"
        or graph.get("canonical_order")
        != "TYPED_ID_CANONICAL_BYTE_ORDER"
        or not has_exact_object_keys(
            graph.get("graph_policy"), graph_policy_fields
        )
        or graph.get("graph_policy")
        != {
            "package_dependency": "ACYCLIC",
            "module_header_import": (
                "HEADER_ONLY_SCC_ALLOWED_AFTER_COMPLETE_HEADER_COLLECTION"
            ),
            "reexport": "ACYCLIC",
            "static_binding_value_dependency": (
                "ACYCLIC_COMPILE_TIME_EVALUATION_ZERO_RUNTIME_INIT"
            ),
        }
        or any(
            not isinstance(graph.get(field), list)
            or any(
                not has_exact_object_keys(row, row_fields)
                for row in graph.get(field, [])
            )
            for field, row_fields in arrays_and_fields
        )
        or any(
            not has_exact_object_keys(
                row.get("canonical_package_key"), package_key_fields
            )
            for row in graph.get("packages", [])
            if isinstance(row, dict)
        )
    ):
        failures.add("PACKAGE_GRAPH_SCHEMA_SHAPE")

    packages = graph.get("packages", [])
    targets = graph.get("targets", [])
    sources = graph.get("source_contributions", [])
    bindings = graph.get("dependency_bindings", [])
    visible = graph.get("visible_module_bindings", [])
    edges = graph.get("module_header_import_edges", [])
    if (
        not is_canonically_sorted(
            packages, lambda row: row.get("package_id", "")
        )
        or not is_canonically_sorted(
            targets, lambda row: row.get("target_id", "")
        )
        or not is_canonically_sorted(
            sources, lambda row: row.get("source_file_id", "")
        )
        or not is_canonically_sorted(
            bindings,
            lambda row: row.get("dependency_binding_id", ""),
        )
        or not is_canonically_sorted(
            visible,
            lambda row: (
                row.get("consumer_target_id", ""),
                tuple(row.get("visible_qualified_path", [])),
                row.get("resolved_module_id", ""),
                row.get("dependency_binding_id_or_self", ""),
            ),
        )
        or not is_canonically_sorted(
            edges,
            lambda row: (
                row.get("from_module_id", ""),
                row.get("to_module_id", ""),
                row.get("edge_kind", ""),
                row.get("source_origin_id", ""),
            ),
        )
        or any(
            not is_canonically_sorted(
                row.get("dependency_binding_ids", [])
            )
            or not is_canonically_sorted(row.get("target_ids", []))
            for row in packages
            if isinstance(row, dict)
        )
        or any(
            not is_canonically_sorted(row.get("source_file_ids", []))
            for row in targets
            if isinstance(row, dict)
        )
    ):
        failures.add("PACKAGE_GRAPH_CANONICAL_ORDER")
    return failures


def r4_package_graph_failure_codes(graph: dict[str, Any]) -> set[str]:
    """Bounded feasibility validator for the frozen package/module graph."""

    failures = r4_package_graph_shape_and_order_failure_codes(graph)
    unicode_scalar_failure = has_non_unicode_scalar(graph)
    canonical_domain_failure = not is_canonical_json_value(graph)
    if unicode_scalar_failure:
        failures.add("CANONICAL_JSON_NON_UNICODE_SCALAR")
    elif canonical_domain_failure:
        failures.add("CANONICAL_JSON_INVALID_VALUE_DOMAIN")
    packages = graph.get("packages", [])
    targets = graph.get("targets", [])
    sources = graph.get("source_contributions", [])
    bindings = graph.get("dependency_bindings", [])
    visible = graph.get("visible_module_bindings", [])
    header_edges = graph.get("module_header_import_edges", [])

    package_ids = [row.get("package_id") for row in packages]
    target_ids = [row.get("target_id") for row in targets]
    source_ids = [row.get("source_file_id") for row in sources]
    module_ids = [row.get("module_id") for row in sources]
    dependency_ids = [
        row.get("dependency_binding_id") for row in bindings
    ]
    if (
        not packages
        or not targets
        or not sources
        or any(not row.get("target_ids") for row in packages)
        or any(not row.get("source_file_ids") for row in targets)
        or len(package_ids) != len(set(package_ids))
        or len(target_ids) != len(set(target_ids))
        or len(source_ids) != len(set(source_ids))
        or len(dependency_ids) != len(set(dependency_ids))
    ):
        failures.add("OWNER_SET")
    domain_rows = (
        ([graph.get("root_package_id"), *package_ids], "PackageId:"),
        (target_ids, "TargetId:"),
        (source_ids, "SourceFileId:"),
        (module_ids, "ModuleId:"),
        (dependency_ids, "DependencyBindingId:"),
    )
    if any(
        not isinstance(value, str) or not value.startswith(prefix)
        for values, prefix in domain_rows
        for value in values
    ):
        failures.add("IDENTITY_DOMAIN")

    package_set = set(package_ids)
    target_set = set(target_ids)
    module_set = set(module_ids)
    dependency_set = set(dependency_ids)
    package_identity_keys: dict[tuple[Any, Any, Any], Any] = {}
    for package in packages:
        canonical_key = package.get("canonical_package_key", {})
        key = (
            canonical_key.get("registry_namespace"),
            canonical_key.get("package_name"),
            canonical_key.get("package_version_identity"),
        )
        previous_id = package_identity_keys.setdefault(
            key, package.get("package_id")
        )
        if None in key or previous_id != package.get("package_id"):
            failures.add("PACKAGE_IDENTITY_RECIPE")
    target_identity_keys: dict[tuple[Any, Any, Any], Any] = {}
    for target in targets:
        key = (
            target.get("package_id"),
            target.get("canonical_manifest_target_name"),
            target.get("target_kind"),
        )
        previous_id = target_identity_keys.setdefault(
            key, target.get("target_id")
        )
        if None in key or previous_id != target.get("target_id"):
            failures.add("TARGET_IDENTITY_RECIPE")
    if graph.get("root_package_id") not in package_set:
        failures.add("ROOT_PACKAGE")
    target_by_id = {
        row.get("target_id"): row for row in targets
    }
    dependency_by_id = {
        row.get("dependency_binding_id"): row for row in bindings
    }
    for package in packages:
        package_id = package.get("package_id")
        target_id_rows = package.get("target_ids", [])
        expected_targets = set(target_id_rows)
        observed_targets = {
            target.get("target_id")
            for target in targets
            if target.get("package_id") == package_id
        }
        if (
            len(target_id_rows) != len(expected_targets)
            or expected_targets != observed_targets
            or any(
                target_id not in target_set
                or target_by_id[target_id].get("package_id")
                != package_id
                for target_id in expected_targets
            )
        ):
            failures.add("PACKAGE_TARGET_REFERENCE")
        dependency_id_rows = package.get("dependency_binding_ids", [])
        expected_dependencies = set(dependency_id_rows)
        observed_dependencies = {
            binding.get("dependency_binding_id")
            for binding in bindings
            if binding.get("consumer_package_id") == package_id
        }
        if (
            len(dependency_id_rows) != len(expected_dependencies)
            or expected_dependencies != observed_dependencies
            or any(
                dependency_id not in dependency_set
                or dependency_by_id[dependency_id].get(
                    "consumer_package_id"
                )
                != package_id
                for dependency_id in expected_dependencies
            )
        ):
            failures.add("PACKAGE_DEPENDENCY_REFERENCE")
    for target in targets:
        if target.get("target_kind") != target.get(
            "source_role_policy"
        ):
            failures.add("TARGET_SOURCE_ROLE_POLICY")
        if target.get("package_id") not in package_set:
            failures.add("TARGET_PACKAGE_REFERENCE")
        source_id_rows = target.get("source_file_ids", [])
        expected_sources = set(source_id_rows)
        observed_sources = {
            row.get("source_file_id")
            for row in sources
            if row.get("target_id") == target.get("target_id")
        }
        if (
            len(source_id_rows) != len(expected_sources)
            or expected_sources != observed_sources
        ):
            failures.add("TARGET_SOURCE_REFERENCE")
    module_identity_keys: dict[tuple[Any, tuple[Any, ...]], Any] = {}
    module_key_by_id: dict[Any, tuple[Any, tuple[Any, ...]]] = {}
    module_owner_packages: dict[Any, set[Any]] = {}
    module_owner_target_kinds: dict[Any, set[Any]] = {}
    module_paths: dict[Any, tuple[Any, ...]] = {}
    source_path_keys: set[tuple[Any, str]] = set()
    for source in sources:
        target = target_by_id.get(source.get("target_id"))
        if target is None:
            failures.add("SOURCE_TARGET_REFERENCE")
            continue
        module_key = (
            target.get("package_id"),
            tuple(source.get("module_path", [])),
        )
        previous_module_id = module_identity_keys.setdefault(
            module_key, source.get("module_id")
        )
        previous_module_key = module_key_by_id.setdefault(
            source.get("module_id"), module_key
        )
        if (
            previous_module_id != source.get("module_id")
            or previous_module_key != module_key
        ):
            failures.add("MODULE_IDENTITY_RECIPE")
        module_owner_packages.setdefault(
            source.get("module_id"), set()
        ).add(target.get("package_id"))
        module_owner_target_kinds.setdefault(
            source.get("module_id"), set()
        ).add(target.get("target_kind"))
        module_paths.setdefault(
            source.get("module_id"),
            tuple(source.get("module_path", [])),
        )
        if (
            source.get("source_role") != target.get("source_role_policy")
            or source.get("activation_profile")
            != target.get("activation_profile")
        ):
            failures.add("SOURCE_TARGET_PROFILE")
        explicit = source.get("explicit_module_path_or_null")
        if explicit is not None and explicit != source.get("module_path"):
            failures.add("MODULE_MAPPING")
        normalized_path = canonical_project_relative_path(
            source.get("normalized_project_relative_path")
        )
        if (
            normalized_path is None
            or normalized_path
            != source.get("normalized_project_relative_path")
        ):
            failures.add("SOURCE_PATH_NORMALIZATION")
        else:
            path_key = (source.get("target_id"), normalized_path)
            if path_key in source_path_keys:
                failures.add("SOURCE_PATH_IDENTITY")
            source_path_keys.add(path_key)

    dependency_keys: set[tuple[Any, Any]] = set()
    package_edges: list[tuple[str, str]] = []
    for binding in bindings:
        key = (
            binding.get("consumer_package_id"),
            binding.get("source_visible_binding"),
        )
        if key in dependency_keys:
            failures.add("DEPENDENCY_BINDING_KEY")
        dependency_keys.add(key)
        consumer = binding.get("consumer_package_id")
        provider = binding.get("provider_package_id")
        if consumer not in package_set or provider not in package_set:
            failures.add("DEPENDENCY_PACKAGE_REFERENCE")
        else:
            package_edges.append((consumer, provider))
    if has_directed_cycle(package_set, package_edges):
        failures.add("PACKAGE_CYCLE")

    visible_keys: set[tuple[Any, tuple[Any, ...]]] = set()
    for row in visible:
        key = (
            row.get("consumer_target_id"),
            tuple(row.get("visible_qualified_path", [])),
        )
        if key in visible_keys:
            failures.add("VISIBLE_MODULE_KEY")
        visible_keys.add(key)
        if row.get("consumer_target_id") not in target_set:
            failures.add("VISIBLE_TARGET_REFERENCE")
        if row.get("resolved_module_id") not in module_set:
            failures.add("VISIBLE_MODULE_REFERENCE")
        if "script" in module_owner_target_kinds.get(
            row.get("resolved_module_id"), set()
        ):
            failures.add("SCRIPT_MODULE_IMPORT")
        dependency = row.get("dependency_binding_id_or_self")
        consumer_target = target_by_id.get(row.get("consumer_target_id"))
        consumer_package = (
            consumer_target.get("package_id")
            if consumer_target is not None
            else None
        )
        module_owners = module_owner_packages.get(
            row.get("resolved_module_id"), set()
        )
        if dependency == "self":
            if module_owners != {consumer_package}:
                failures.add("VISIBLE_DEPENDENCY_REFERENCE")
            expected_visible_path = module_paths.get(
                row.get("resolved_module_id")
            )
        elif dependency not in dependency_set:
            failures.add("VISIBLE_DEPENDENCY_REFERENCE")
            expected_visible_path = None
        else:
            binding = dependency_by_id[dependency]
            if (
                binding.get("consumer_package_id") != consumer_package
                or module_owners
                != {binding.get("provider_package_id")}
            ):
                failures.add("VISIBLE_DEPENDENCY_REFERENCE")
            provider_path = module_paths.get(
                row.get("resolved_module_id"), ()
            )
            expected_visible_path = (
                binding.get("source_visible_binding"),
                *provider_path[1:],
            )
        if tuple(row.get("visible_qualified_path", [])) != (
            expected_visible_path
        ):
            failures.add("VISIBLE_PATH_PROJECTION")

    admitted_edge_kinds = {
        "module_header_reference",
        "type_declaration_reference",
        "signature_reference",
    }
    forbidden_edge_kinds = {
        "static_value_dependency",
        "runtime_initializer_dependency",
        "reexport_dependency",
    }
    all_module_edges: list[tuple[str, str]] = []
    forbidden_edges: set[tuple[str, str]] = set()
    for row in header_edges:
        source = row.get("from_module_id")
        target = row.get("to_module_id")
        kind = row.get("edge_kind")
        if source not in module_set or target not in module_set:
            failures.add("MODULE_EDGE_REFERENCE")
            continue
        all_module_edges.append((source, target))
        if kind in forbidden_edge_kinds:
            forbidden_edges.add((source, target))
            if row.get("scc_admission") != "SCC_FORBIDDEN":
                failures.add("MODULE_EDGE_ADMISSION")
        elif kind in admitted_edge_kinds and row.get("scc_admission") != (
            "HEADER_ONLY_ALLOWED_AFTER_COMPLETE_HEADER_COLLECTION"
        ):
            failures.add("MODULE_EDGE_ADMISSION")
        elif kind not in admitted_edge_kinds:
            failures.add("MODULE_EDGE_ADMISSION")
    components = directed_strongly_connected_components(
        module_set, all_module_edges
    )
    component_by_module = {
        module_id: component
        for component in components
        for module_id in component
    }
    if any(
        source == target
        or (
            target in component_by_module.get(source, set())
            and len(component_by_module.get(source, set())) > 1
        )
        for source, target in forbidden_edges
    ):
        failures.add("FORBIDDEN_MODULE_CYCLE")
    graph_sha256 = graph.get("canonical_graph_sha256")
    if (
        not canonical_domain_failure
        and (
        re.fullmatch(r"[0-9a-f]{64}", str(graph_sha256 or "")) is None
        or graph_sha256
        != canonical_self_digest(graph, "canonical_graph_sha256")
        )
    ):
        failures.add("PACKAGE_GRAPH_DIGEST")
    return failures


def r4_top_level_visibility_failure_codes(
    descriptor: dict[str, Any],
) -> set[str]:
    """Validate R4 top-level visibility relations beyond JSON shape."""

    failures: set[str] = set()
    type_producing_owners = {
        "ClassDecl",
        "TraitDecl",
        "EnumDecl",
        "TypeAliasDecl",
        "SchemaDecl",
        "ActorDecl",
        "ActorProtocolDecl",
        "TypestateResourceDecl",
        "BitfieldDecl",
    }
    computed_type_owner = (
        descriptor.get("declaration_kind") in type_producing_owners
    )
    if descriptor.get("type_producing_owner") is not computed_type_owner:
        failures.add("TYPE_OWNER_CLASSIFICATION")

    explicit_visibility = descriptor.get("explicit_visibility")
    if computed_type_owner and explicit_visibility is None:
        failures.add("TYPE_DECL_VISIBILITY_REQUIRED")
    normalized_visibility = (
        explicit_visibility
        if explicit_visibility is not None
        else "private"
    )
    if (
        normalized_visibility in {"private", "common"}
        and descriptor.get(
            "external_export_or_module_interface_admitted"
        )
        is not False
    ):
        failures.add("EXTERNAL_EXPORT_INELIGIBLE")

    allowed_dependencies = {
        "private": {"private", "common", "public"},
        "common": {"common", "public"},
        "public": {"public"},
    }
    dependency_visibilities = descriptor.get(
        "api_dependency_visibilities", []
    )
    if (
        normalized_visibility not in allowed_dependencies
        or not isinstance(dependency_visibilities, list)
        or any(
            visibility
            not in allowed_dependencies.get(normalized_visibility, set())
            for visibility in dependency_visibilities
        )
    ):
        failures.add("API_VISIBILITY_LEAK")

    if (
        normalized_visibility == "public"
        and descriptor.get(
            "external_export_or_module_interface_admitted"
        )
        is True
        and not descriptor.get("visibility_proof_ids")
    ):
        failures.add("PUBLIC_EXPORT_PROOF_MISSING")
    return failures


def r4_resolver_graph_shape_and_order_failure_codes(
    graph: dict[str, Any],
) -> set[str]:
    """Bind the resolver helper to its closed schema and array order."""

    failures: set[str] = set()
    top_fields = {
        "schema",
        "package_graph_sha256",
        "root_scope_ids",
        "scopes",
        "name_bindings",
        "import_bindings",
        "activation_entries",
        "witness_visibility_entries",
        "invariants",
        "resolver_graph_sha256",
    }
    scope_fields = {
        "PackageRootScope": {
            "resolver_scope_id",
            "parent_scope_id_or_null",
            "kind",
            "package_id",
        },
        "TargetScope": {
            "resolver_scope_id",
            "parent_scope_id_or_null",
            "kind",
            "target_id",
        },
        "ModuleScope": {
            "resolver_scope_id",
            "parent_scope_id_or_null",
            "kind",
            "module_id",
        },
        "SourceContributionScope": {
            "resolver_scope_id",
            "parent_scope_id_or_null",
            "kind",
            "source_file_id",
        },
        "ItemOwnerScope": {
            "resolver_scope_id",
            "parent_scope_id_or_null",
            "kind",
            "decl_id",
        },
        "BodyLocalScope": {
            "resolver_scope_id",
            "parent_scope_id_or_null",
            "kind",
            "hir_body_id",
            "hir_scope_id",
            "owner_local_scope_id",
            "scope_preorder_ordinal",
            "scope_role",
        },
    }
    name_fields = {
        "resolver_scope_id",
        "namespace",
        "local_name",
        "binding_kind",
        "binding_origin_kind",
        "source_admission",
        "typed_identity",
        "hir_body_id_or_null",
        "owner_local_binding_id_or_null",
        "binding_commit_ordinal_or_null",
        "source_origin_id",
        "visibility_start",
        "overload_slot_key_or_null",
    }
    import_fields = {
        "import_binding_id",
        "resolver_scope_id",
        "namespace",
        "local_binding_name",
        "resolved_target_identity",
        "provider_binding_id_or_self",
        "provider_module_id",
        "source_origin_id",
    }
    activation_fields = {
        "resolver_scope_id",
        "activation_origin_id",
        "activated_identity",
        "activation_kind",
        "provider_binding_id_or_self",
        "provider_module_id",
        "semantic_site_key",
    }
    witness_fields = {
        "resolver_scope_id",
        "evidence_origin_id",
        "visible_witness_identity",
    }
    invariant_fields = {
        "lookup",
        "same_frame_order_priority",
        "cross_frame_overload_merge",
        "provisional_bindings_in_name_env",
        "environment_cross_creation_count",
        "runtime_relookup_count",
    }
    scopes = graph.get("scopes", [])
    row_arrays = (
        ("name_bindings", name_fields),
        ("import_bindings", import_fields),
        ("activation_entries", activation_fields),
        ("witness_visibility_entries", witness_fields),
    )
    if (
        not has_exact_object_keys(graph, top_fields)
        or graph.get("schema") != "deeplus.resolver-graph/r1"
        or re.fullmatch(
            r"[0-9a-f]{64}",
            str(graph.get("package_graph_sha256") or ""),
        )
        is None
        or not isinstance(graph.get("root_scope_ids"), list)
        or not isinstance(scopes, list)
        or any(
            not isinstance(row, dict)
            or not has_exact_object_keys(
                row, scope_fields.get(row.get("kind"), set())
            )
            for row in scopes
        )
        or any(
            not isinstance(graph.get(field), list)
            or any(
                not has_exact_object_keys(row, row_fields)
                for row in graph.get(field, [])
            )
            for field, row_fields in row_arrays
        )
        or not has_exact_object_keys(
            graph.get("invariants"), invariant_fields
        )
    ):
        failures.add("RESOLVER_GRAPH_SCHEMA_SHAPE")

    if (
        not is_canonically_sorted(graph.get("root_scope_ids"))
        or not is_canonically_sorted(
            scopes, lambda row: row.get("resolver_scope_id", "")
        )
        or not is_canonically_sorted(
            graph.get("name_bindings"),
            lambda row: (
                row.get("resolver_scope_id", ""),
                row.get("namespace", ""),
                row.get("local_name", ""),
                row.get("overload_slot_key_or_null") or "",
                row.get("source_origin_id", ""),
            ),
        )
        or not is_canonically_sorted(
            graph.get("import_bindings"),
            lambda row: row.get("import_binding_id", ""),
        )
        or not is_canonically_sorted(
            graph.get("activation_entries"),
            lambda row: row.get("activation_origin_id", ""),
        )
        or not is_canonically_sorted(
            graph.get("witness_visibility_entries"),
            lambda row: row.get("evidence_origin_id", ""),
        )
    ):
        failures.add("RESOLVER_GRAPH_CANONICAL_ORDER")
    return failures


def r4_resolver_graph_failure_codes(graph: dict[str, Any]) -> set[str]:
    """Bounded feasibility validator for resolver ownership and key laws."""

    failures = r4_resolver_graph_shape_and_order_failure_codes(graph)
    unicode_scalar_failure = has_non_unicode_scalar(graph)
    canonical_domain_failure = not is_canonical_json_value(graph)
    if unicode_scalar_failure:
        failures.add("CANONICAL_JSON_NON_UNICODE_SCALAR")
    elif canonical_domain_failure:
        failures.add("CANONICAL_JSON_INVALID_VALUE_DOMAIN")
    scopes = graph.get("scopes", [])
    scope_ids = [row.get("resolver_scope_id") for row in scopes]
    if not scopes or len(scope_ids) != len(set(scope_ids)):
        failures.add("SCOPE_SET")
    if any(
        not isinstance(scope_id, str)
        or not scope_id.startswith("ResolverScopeId:")
        for scope_id in scope_ids
    ):
        failures.add("SCOPE_ID_DOMAIN")
    scope_set = set(scope_ids)
    scope_by_id = {
        row.get("resolver_scope_id"): row for row in scopes
    }
    root_scope_ids = graph.get("root_scope_ids", [])
    package_root_ids = {
        scope.get("resolver_scope_id")
        for scope in scopes
        if scope.get("kind") == "PackageRootScope"
    }
    if (
        not root_scope_ids
        or len(root_scope_ids) != len(set(root_scope_ids))
        or set(root_scope_ids) != package_root_ids
        or any(
            not is_typed_id(root_scope_id, "ResolverScopeId")
            for root_scope_id in root_scope_ids
        )
    ):
        failures.add("ROOT_SCOPE_REFERENCE")
    parent_edges: list[tuple[str, str]] = []
    owner_domains = {
        "PackageRootScope": (("package_id", "PackageId"),),
        "TargetScope": (("target_id", "TargetId"),),
        "ModuleScope": (("module_id", "ModuleId"),),
        "SourceContributionScope": (
            ("source_file_id", "SourceFileId"),
        ),
        "ItemOwnerScope": (("decl_id", "DeclId"),),
        "BodyLocalScope": (
            ("hir_body_id", "HirBodyId"),
            ("hir_scope_id", "HirScopeId"),
        ),
    }
    scope_identity_keys: dict[tuple[Any, tuple[Any, ...]], Any] = {}
    scope_key_by_id: dict[Any, tuple[Any, tuple[Any, ...]]] = {}
    root_body_scope_by_body: dict[Any, Any] = {}
    hir_scope_by_owner_key: dict[tuple[Any, Any], Any] = {}
    hir_scope_key_by_id: dict[Any, tuple[Any, Any]] = {}
    scope_ordinals_by_body: dict[Any, set[int]] = {}
    for scope in scopes:
        parent = scope.get("parent_scope_id_or_null")
        if scope.get("kind") == "PackageRootScope":
            if parent is not None:
                failures.add("ROOT_SCOPE_PARENT")
        elif parent not in scope_set:
            failures.add("SCOPE_PARENT_REFERENCE")
        else:
            parent_edges.append((scope.get("resolver_scope_id"), parent))
            expected_parent_kind = {
                "TargetScope": "PackageRootScope",
                "ModuleScope": "TargetScope",
                "SourceContributionScope": "ModuleScope",
                "ItemOwnerScope": "SourceContributionScope",
            }.get(scope.get("kind"))
            if (
                expected_parent_kind is not None
                and scope_by_id.get(parent, {}).get("kind")
                != expected_parent_kind
            ):
                failures.add("SCOPE_PARENT_KIND")
        expected_owner_domains = owner_domains.get(scope.get("kind"))
        if expected_owner_domains is None or any(
            not is_typed_id(scope.get(field), domain)
            for field, domain in expected_owner_domains
        ):
            failures.add("SCOPE_OWNER_DOMAIN")
        elif expected_owner_domains is not None:
            owner_key = (
                scope.get("kind"),
                tuple(scope.get(field) for field, _domain in expected_owner_domains),
            )
            previous_scope_id = scope_identity_keys.setdefault(
                owner_key, scope.get("resolver_scope_id")
            )
            previous_owner_key = scope_key_by_id.setdefault(
                scope.get("resolver_scope_id"), owner_key
            )
            if (
                previous_scope_id != scope.get("resolver_scope_id")
                or previous_owner_key != owner_key
            ):
                failures.add("SCOPE_IDENTITY_RECIPE")
        if scope.get("kind") == "BodyLocalScope":
            scope_role = scope.get("scope_role")
            if scope_role not in {"ROOT_BODY", "NESTED_BODY"}:
                failures.add("BODY_SCOPE_ROLE")
            if scope_role == "ROOT_BODY":
                previous_root = root_body_scope_by_body.setdefault(
                    scope.get("hir_body_id"),
                    scope.get("resolver_scope_id"),
                )
                if previous_root != scope.get("resolver_scope_id"):
                    failures.add("ROOT_BODY_SCOPE_IDENTITY")
                if scope_by_id.get(parent, {}).get("kind") != (
                    "ItemOwnerScope"
                ):
                    failures.add("SCOPE_PARENT_KIND")
            hir_scope_key = (
                scope.get("hir_body_id"),
                scope.get("owner_local_scope_id"),
            )
            previous_hir_scope = hir_scope_by_owner_key.setdefault(
                hir_scope_key, scope.get("hir_scope_id")
            )
            previous_hir_scope_key = hir_scope_key_by_id.setdefault(
                scope.get("hir_scope_id"), hir_scope_key
            )
            scope_body_id = scope.get("hir_body_id")
            scope_ordinal = scope.get("scope_preorder_ordinal")
            body_scope_ordinals = scope_ordinals_by_body.setdefault(
                scope_body_id, set()
            )
            if (
                None in hir_scope_key
                or previous_hir_scope != scope.get("hir_scope_id")
                or previous_hir_scope_key != hir_scope_key
                or scope_ordinal in body_scope_ordinals
                or type(scope_ordinal) is not int
                or scope_ordinal < 0
                or (
                    scope_role == "ROOT_BODY"
                    and (
                        scope.get("owner_local_scope_id") != "root"
                        or scope.get("scope_preorder_ordinal") != 0
                    )
                )
            ):
                failures.add("HIR_SCOPE_IDENTITY_RECIPE")
            if type(scope_ordinal) is int:
                body_scope_ordinals.add(scope_ordinal)
    if any(
        ordinals != set(range(len(ordinals)))
        for ordinals in scope_ordinals_by_body.values()
    ):
        failures.add("HIR_SCOPE_PREORDER")
    for scope in scopes:
        if (
            scope.get("kind") == "BodyLocalScope"
            and scope.get("scope_role") == "NESTED_BODY"
        ):
            parent_scope = scope_by_id.get(
                scope.get("parent_scope_id_or_null"), {}
            )
            if (
                parent_scope.get("kind") != "BodyLocalScope"
                or parent_scope.get("hir_body_id")
                != scope.get("hir_body_id")
                or type(parent_scope.get("scope_preorder_ordinal")) is not int
                or type(scope.get("scope_preorder_ordinal")) is not int
                or parent_scope.get("scope_preorder_ordinal")
                >= scope.get("scope_preorder_ordinal")
            ):
                failures.add("BODY_SCOPE_PARENT")
    if has_directed_cycle(scope_set, parent_edges):
        failures.add("SCOPE_CYCLE")
    name_binding_domains = {
        ("MODULE", "SINGLE"): "ModuleId",
        ("TYPE", "SINGLE"): "DeclId",
        ("VALUE", "SINGLE"): "DeclId",
        ("VALUE", "HIR_LOCAL"): "HirLocalId",
        ("CALLABLE_OVERLOAD_SET", "CALLABLE_OVERLOAD_SLOT"): "DeclId",
    }
    name_key_kinds: dict[tuple[Any, Any, Any], str] = {}
    overload_keys: set[tuple[Any, Any, Any, Any]] = set()
    hir_local_ids: set[Any] = set()
    hir_local_by_owner_key: dict[tuple[Any, Any], Any] = {}
    hir_local_key_by_id: dict[Any, tuple[Any, Any]] = {}
    binding_ordinals_by_body: dict[Any, set[int]] = {}
    for row in graph.get("name_bindings", []):
        key = (
            row.get("resolver_scope_id"),
            row.get("namespace"),
            row.get("local_name"),
        )
        if row.get("resolver_scope_id") not in scope_set:
            failures.add("NAME_SCOPE_REFERENCE")
        binding_kind = row.get("binding_kind")
        binding_origin_kind = row.get("binding_origin_kind")
        owner_scope = scope_by_id.get(row.get("resolver_scope_id"), {})
        if row.get("source_admission") != "CURRENT_GRAMMAR_ADMITTED":
            failures.add("BINDING_SOURCE_ADMISSION")
        expected_identity_domain = name_binding_domains.get(
            (row.get("namespace"), binding_kind)
        )
        expected_visibility_start = {
            "DECLARATION": "SCOPE_ENTRY",
            "PARAMETER": "SCOPE_ENTRY",
            "ROOT_BODY_LOCAL": "AFTER_DECLARATION",
            "NESTED_LOCAL": "AFTER_DECLARATION",
            "COMMITTED_PATTERN_BINDING": (
                "AFTER_TRANSACTION_COMMIT"
            ),
            "LOCAL_FUNCTION": "AFTER_DECLARATION",
        }.get(binding_origin_kind)
        if (
            expected_identity_domain is None
            or not is_typed_id(
                row.get("typed_identity"), expected_identity_domain
            )
            or (
                expected_visibility_start is not None
                and row.get("visibility_start")
                != expected_visibility_start
            )
        ):
            failures.add("NAME_ENVIRONMENT_SEPARATION")
        if binding_kind == "HIR_LOCAL":
            hir_local_id = row.get("typed_identity")
            if hir_local_id in hir_local_ids:
                failures.add("HIR_LOCAL_ID_REUSE")
            hir_local_ids.add(hir_local_id)
            local_owner_key = (
                row.get("hir_body_id_or_null"),
                row.get("owner_local_binding_id_or_null"),
            )
            previous_local_id = hir_local_by_owner_key.setdefault(
                local_owner_key, hir_local_id
            )
            previous_local_key = hir_local_key_by_id.setdefault(
                hir_local_id, local_owner_key
            )
            local_body_id = row.get("hir_body_id_or_null")
            binding_ordinal = row.get("binding_commit_ordinal_or_null")
            body_binding_ordinals = binding_ordinals_by_body.setdefault(
                local_body_id, set()
            )
            if (
                None in local_owner_key
                or previous_local_id != hir_local_id
                or previous_local_key != local_owner_key
                or binding_ordinal in body_binding_ordinals
                or type(binding_ordinal) is not int
                or binding_ordinal < 0
                or row.get("hir_body_id_or_null")
                != owner_scope.get("hir_body_id")
            ):
                failures.add("HIR_LOCAL_IDENTITY_RECIPE")
            if type(binding_ordinal) is int:
                body_binding_ordinals.add(binding_ordinal)
            if (
                owner_scope.get("kind") != "BodyLocalScope"
                or binding_origin_kind
                not in {
                    "PARAMETER",
                    "ROOT_BODY_LOCAL",
                    "NESTED_LOCAL",
                    "COMMITTED_PATTERN_BINDING",
                }
            ):
                failures.add("HIR_LOCAL_SCOPE_DOMAIN")
            if (
                binding_origin_kind
                in {"PARAMETER", "ROOT_BODY_LOCAL"}
                and owner_scope.get("scope_role") != "ROOT_BODY"
            ):
                failures.add("ROOT_BODY_BINDING_FRAME")
            if (
                binding_origin_kind == "NESTED_LOCAL"
                and owner_scope.get("scope_role") != "NESTED_BODY"
            ):
                failures.add("NESTED_BINDING_FRAME")
        elif binding_origin_kind == "LOCAL_FUNCTION":
            if (
                owner_scope.get("kind") != "BodyLocalScope"
                or binding_kind != "CALLABLE_OVERLOAD_SLOT"
                or row.get("visibility_start") != "AFTER_DECLARATION"
            ):
                failures.add("LOCAL_FUNCTION_VISIBILITY")
        elif binding_origin_kind != "DECLARATION":
            failures.add("BINDING_ORIGIN_KIND")
        if binding_kind != "HIR_LOCAL" and any(
            row.get(field) is not None
            for field in (
                "hir_body_id_or_null",
                "owner_local_binding_id_or_null",
                "binding_commit_ordinal_or_null",
            )
        ):
            failures.add("HIR_LOCAL_IDENTITY_RECIPE")
        if binding_origin_kind == "DECLARATION":
            allowed_declaration_scopes = {
                "MODULE": {
                    "PackageRootScope",
                    "TargetScope",
                    "ModuleScope",
                },
                "TYPE": {"ModuleScope", "ItemOwnerScope"},
                "VALUE": {"ModuleScope", "ItemOwnerScope"},
                "CALLABLE_OVERLOAD_SET": {
                    "ModuleScope",
                    "ItemOwnerScope",
                },
            }
            if owner_scope.get("kind") not in allowed_declaration_scopes.get(
                row.get("namespace"), set()
            ):
                failures.add("BINDING_SCOPE_DOMAIN")
        key_kind = (
            "CALLABLE"
            if binding_kind == "CALLABLE_OVERLOAD_SLOT"
            else "SINGLE"
        )
        previous_kind = name_key_kinds.get(key)
        if previous_kind is not None and (
            previous_kind != "CALLABLE" or key_kind != "CALLABLE"
        ):
            failures.add("SAME_FRAME_NAME_KEY")
        name_key_kinds.setdefault(key, key_kind)
        if binding_kind == "CALLABLE_OVERLOAD_SLOT":
            slot = (*key, row.get("overload_slot_key_or_null"))
            if (
                row.get("namespace") != "CALLABLE_OVERLOAD_SET"
                or slot in overload_keys
                or not isinstance(slot[-1], str)
                or not slot[-1]
            ):
                failures.add("OVERLOAD_SLOT_KEY")
            overload_keys.add(slot)
        elif row.get("overload_slot_key_or_null") is not None:
            failures.add("OVERLOAD_SLOT_KEY")
        if "overload_slot_key_or_null" not in row:
            failures.add("OVERLOAD_SLOT_KEY")
        if (
            not is_typed_id(row.get("typed_identity"))
            or not is_typed_id(row.get("source_origin_id"), "SourceOriginId")
        ):
            failures.add("NAME_IDENTITY_DOMAIN")
    if any(
        ordinals != set(range(len(ordinals)))
        for ordinals in binding_ordinals_by_body.values()
    ):
        failures.add("HIR_LOCAL_COMMIT_ORDER")

    import_keys: set[tuple[Any, Any, Any]] = set()
    import_ids: set[Any] = set()
    for row in graph.get("import_bindings", []):
        key = (
            row.get("resolver_scope_id"),
            row.get("namespace"),
            row.get("local_binding_name"),
        )
        if row.get("resolver_scope_id") not in scope_set:
            failures.add("IMPORT_SCOPE_REFERENCE")
        elif scope_by_id.get(
            row.get("resolver_scope_id"), {}
        ).get("kind") not in {
            "ModuleScope",
            "SourceContributionScope",
            "ItemOwnerScope",
            "BodyLocalScope",
        }:
            failures.add("IMPORT_SCOPE_DOMAIN")
        if row.get("namespace") not in {
            "MODULE",
            "TYPE",
            "VALUE",
            "CALLABLE_OVERLOAD_SET",
        }:
            failures.add("IMPORT_ENVIRONMENT_SEPARATION")
        if key in import_keys or key in name_key_kinds:
            failures.add("IMPORT_BINDING_KEY")
        import_keys.add(key)
        import_id = row.get("import_binding_id")
        if (
            import_id in import_ids
            or not is_typed_id(import_id, "ImportBindingId")
        ):
            failures.add("IMPORT_BINDING_ID")
        import_ids.add(import_id)
        expected_import_domain = {
            "MODULE": "ModuleId",
            "TYPE": "DeclId",
            "VALUE": "DeclId",
            "CALLABLE_OVERLOAD_SET": "DeclId",
        }.get(row.get("namespace"))
        if (
            expected_import_domain is None
            or not is_typed_id(
                row.get("resolved_target_identity"),
                expected_import_domain,
            )
            or not is_typed_id(row.get("source_origin_id"), "SourceOriginId")
        ):
            failures.add("IMPORT_IDENTITY_DOMAIN")
        provider_binding = row.get("provider_binding_id_or_self")
        if (
            (
                provider_binding != "self"
                and not is_typed_id(
                    provider_binding, "DependencyBindingId"
                )
            )
            or not is_typed_id(
                row.get("provider_module_id"), "ModuleId"
            )
        ):
            failures.add("IMPORT_PROVIDER_DOMAIN")

    activation_keys: set[tuple[Any, Any]] = set()
    activation_by_origin: dict[Any, tuple[Any, Any]] = {}
    for row in graph.get("activation_entries", []):
        key = (
            row.get("resolver_scope_id"),
            row.get("activated_identity"),
        )
        if row.get("resolver_scope_id") not in scope_set:
            failures.add("ACTIVATION_SCOPE_REFERENCE")
        elif scope_by_id.get(
            row.get("resolver_scope_id"), {}
        ).get("kind") not in {
            "ModuleScope",
            "SourceContributionScope",
            "ItemOwnerScope",
            "BodyLocalScope",
        }:
            failures.add("ACTIVATION_SCOPE_DOMAIN")
        if key in activation_keys:
            failures.add("ACTIVATION_ENTRY_KEY")
        activation_keys.add(key)
        origin_key = (
            row.get("activated_identity"),
            row.get("resolver_scope_id"),
            row.get("activation_kind"),
            row.get("semantic_site_key"),
        )
        previous_origin_key = activation_by_origin.setdefault(
            row.get("activation_origin_id"), origin_key
        )
        if previous_origin_key != origin_key:
            failures.add("ACTIVATION_ORIGIN_IDENTITY")
        if (
            not is_typed_id(
                row.get("activation_origin_id"), "ActivationOriginId"
            )
            or not is_typed_id_in(
                row.get("activated_identity"),
                {"ExtensionSetId"},
            )
            or row.get("activation_kind") != "use"
            or not isinstance(row.get("semantic_site_key"), str)
            or not row.get("semantic_site_key")
        ):
            failures.add("ACTIVATION_IDENTITY_DOMAIN")
        provider_binding = row.get("provider_binding_id_or_self")
        if (
            (
                provider_binding != "self"
                and not is_typed_id(
                    provider_binding, "DependencyBindingId"
                )
            )
            or not is_typed_id(
                row.get("provider_module_id"), "ModuleId"
            )
        ):
            failures.add("ACTIVATION_PROVIDER_DOMAIN")

    witness_keys: set[tuple[Any, Any]] = set()
    witness_by_evidence: dict[Any, Any] = {}
    for row in graph.get("witness_visibility_entries", []):
        key = (
            row.get("resolver_scope_id"),
            row.get("evidence_origin_id"),
        )
        if row.get("resolver_scope_id") not in scope_set:
            failures.add("WITNESS_SCOPE_REFERENCE")
        elif scope_by_id.get(
            row.get("resolver_scope_id"), {}
        ).get("kind") not in {
            "ModuleScope",
            "ItemOwnerScope",
            "BodyLocalScope",
        }:
            failures.add("WITNESS_SCOPE_DOMAIN")
        if key in witness_keys:
            failures.add("WITNESS_ENTRY_KEY")
        witness_keys.add(key)
        previous_witness = witness_by_evidence.setdefault(
            row.get("evidence_origin_id"),
            row.get("visible_witness_identity"),
        )
        if previous_witness != row.get("visible_witness_identity"):
            failures.add("WITNESS_EVIDENCE_IDENTITY")
        if (
            not is_typed_id(
                row.get("evidence_origin_id"), "EvidenceOriginId"
            )
            or not is_typed_id(
                row.get("visible_witness_identity"), "TraitWitnessId"
            )
        ):
            failures.add("WITNESS_IDENTITY_DOMAIN")

    invariants = graph.get("invariants", {})
    if (
        invariants.get("lookup")
        != "INNERMOST_TO_OUTERMOST_STOP_AT_FIRST_NONEMPTY_EXACT_NAMESPACE_AND_SPELLING"
        or invariants.get("same_frame_order_priority") is not False
        or invariants.get("cross_frame_overload_merge") is not False
        or invariants.get("provisional_bindings_in_name_env") is not False
        or type(invariants.get("environment_cross_creation_count")) is not int
        or invariants.get("environment_cross_creation_count") != 0
        or type(invariants.get("runtime_relookup_count")) is not int
        or invariants.get("runtime_relookup_count") != 0
    ):
        failures.add("RESOLVER_INVARIANTS")
    resolver_graph_sha256 = graph.get("resolver_graph_sha256")
    if (
        not canonical_domain_failure
        and (
            re.fullmatch(
                r"[0-9a-f]{64}", str(resolver_graph_sha256 or "")
            )
            is None
            or resolver_graph_sha256
            != canonical_self_digest(graph, "resolver_graph_sha256")
        )
    ):
        failures.add("RESOLVER_GRAPH_DIGEST")
    return failures


def r4_resolver_trace_shape_and_order_failure_codes(
    trace: dict[str, Any],
) -> set[str]:
    """Bind resolver traces to their closed schema and canonical order."""

    failures: set[str] = set()
    top_fields = {
        "schema",
        "resolver_graph_sha256",
        "references",
        "diagnostic_order",
        "diagnostic_selection",
        "seal",
        "trace_sha256",
    }
    reference_fields = {
        "source_origin_id",
        "resolver_scope_id",
        "namespace",
        "source_spelling",
        "candidate_origin_ids",
        "visibility_proof_ids",
        "activation_origin_id_or_null",
        "evidence_origin_id_or_null",
        "import_binding_id_or_null",
        "stages",
        "result",
        "source_span",
    }
    diagnostic_fields = {
        "winner_source_origin_id_or_null",
        "winner_rejection_reason_or_null",
        "suppressed_source_origin_ids",
    }
    seal_fields = {"seal_status", "counters"}
    counter_fields = {
        "unbound_primary_count",
        "unresolved_count",
        "candidate_set_count",
        "missing_typed_id_count",
        "missing_visibility_proof_count",
        "recovery_binding_count",
        "runtime_relookup_count",
        "overload_winner_count",
        "canonical_hir_overload_set_ref_count",
    }
    references = trace.get("references", [])
    if (
        not has_exact_object_keys(trace, top_fields)
        or trace.get("schema") != "deeplus.resolver-trace/r1"
        or re.fullmatch(
            r"[0-9a-f]{64}",
            str(trace.get("resolver_graph_sha256") or ""),
        )
        is None
        or not isinstance(references, list)
        or any(
            not has_exact_object_keys(row, reference_fields)
            or not isinstance(row.get("stages"), list)
            or any(
                not has_exact_object_keys(
                    stage, {"ordinal", "predicate", "status"}
                )
                for stage in row.get("stages", [])
            )
            or not has_exact_object_keys(
                row.get("source_span"), {"start", "end"}
            )
            for row in references
            if isinstance(row, dict)
        )
        or any(not isinstance(row, dict) for row in references)
        or not has_exact_object_keys(
            trace.get("diagnostic_selection"), diagnostic_fields
        )
        or not has_exact_object_keys(trace.get("seal"), seal_fields)
        or not has_exact_object_keys(
            trace.get("seal", {}).get("counters"), counter_fields
        )
    ):
        failures.add("RESOLVER_TRACE_SCHEMA_SHAPE")

    if (
        not is_canonically_sorted(
            references, lambda row: row.get("source_origin_id", "")
        )
        or any(
            not is_canonically_sorted(row.get("candidate_origin_ids"))
            or not is_canonically_sorted(
                row.get("visibility_proof_ids")
            )
            or [
                stage.get("ordinal")
                for stage in row.get("stages", [])
                if isinstance(stage, dict)
            ]
            != list(range(1, 10))
            for row in references
            if isinstance(row, dict)
        )
        or not is_canonically_sorted(
            trace.get("diagnostic_selection", {}).get(
                "suppressed_source_origin_ids"
            )
        )
    ):
        failures.add("RESOLVER_TRACE_CANONICAL_ORDER")
    return failures


def r4_resolver_trace_failure_codes(trace: dict[str, Any]) -> set[str]:
    """Bounded feasibility validator for the nine-stage resolver trace."""

    failures = r4_resolver_trace_shape_and_order_failure_codes(trace)
    unicode_scalar_failure = has_non_unicode_scalar(trace)
    canonical_domain_failure = not is_canonical_json_value(trace)
    if unicode_scalar_failure:
        failures.add("CANONICAL_JSON_NON_UNICODE_SCALAR")
    elif canonical_domain_failure:
        failures.add("CANONICAL_JSON_INVALID_VALUE_DOMAIN")
    references = trace.get("references", [])
    if not isinstance(references, list) or not references:
        return failures | {"REFERENCE_SHAPE"}
    reference_required = {
        "source_origin_id",
        "resolver_scope_id",
        "namespace",
        "source_spelling",
        "candidate_origin_ids",
        "visibility_proof_ids",
        "activation_origin_id_or_null",
        "evidence_origin_id_or_null",
        "import_binding_id_or_null",
        "stages",
        "result",
        "source_span",
    }
    namespaces = {
        "MODULE",
        "TYPE",
        "VALUE",
        "CALLABLE_OVERLOAD_SET",
    }
    observed_reference_ids: set[Any] = set()
    failed_reference_rows: list[tuple[int, str, str]] = []
    hir_seal_reasons: list[str] = []
    observed_reference_order = [
        row.get("source_origin_id")
        for row in references
        if isinstance(row, dict)
    ]
    if (
        any(not isinstance(value, str) for value in observed_reference_order)
        or observed_reference_order != sorted(observed_reference_order)
    ):
        failures.add("REFERENCE_ORDER")
    for reference in references:
        if not isinstance(reference, dict):
            failures.add("REFERENCE_SHAPE")
            continue
        if set(reference) != reference_required:
            failures.add("REFERENCE_SHAPE")
        source_origin_id = reference.get("source_origin_id")
        if (
            source_origin_id in observed_reference_ids
            or not is_typed_id(source_origin_id, "SourceOriginId")
        ):
            failures.add("REFERENCE_IDENTITY")
        observed_reference_ids.add(source_origin_id)
        if (
            not is_typed_id(
                reference.get("resolver_scope_id"), "ResolverScopeId"
            )
            or reference.get("namespace") not in namespaces
            or not isinstance(reference.get("source_spelling"), str)
            or not reference.get("source_spelling")
        ):
            failures.add("REFERENCE_DOMAIN")
        candidate_origins = reference.get("candidate_origin_ids")
        if (
            not isinstance(candidate_origins, list)
            or any(
                not is_typed_id_in(
                    value,
                    {
                        "DeclId",
                        "HirLocalId",
                        "ModuleId",
                        "ImportBindingId",
                        "ActivationOriginId",
                        "EvidenceOriginId",
                        "ExtensionSetId",
                        "TraitWitnessId",
                    },
                )
                for value in candidate_origins
            )
            or len(candidate_origins) != len(set(candidate_origins))
            or candidate_origins != sorted(candidate_origins)
        ):
            failures.add("REFERENCE_DOMAIN")
        visibility_proofs = reference.get("visibility_proof_ids")
        if (
            not isinstance(visibility_proofs, list)
            or any(
                not is_typed_id(value, "VisibilityProofId")
                for value in visibility_proofs
            )
            or len(visibility_proofs) != len(set(visibility_proofs))
            or visibility_proofs != sorted(visibility_proofs)
        ):
            failures.add("REFERENCE_DOMAIN")
        for field, domain in (
            ("activation_origin_id_or_null", "ActivationOriginId"),
            ("evidence_origin_id_or_null", "EvidenceOriginId"),
            ("import_binding_id_or_null", "ImportBindingId"),
        ):
            value = reference.get(field)
            if value is not None and not is_typed_id(value, domain):
                failures.add("REFERENCE_DOMAIN")
            if (
                value is not None
                and isinstance(candidate_origins, list)
                and value not in candidate_origins
            ):
                failures.add("REFERENCE_ORIGIN_LINKAGE")
        candidate_origin_kinds = {
            str(value).split(":", 1)[0]
            for value in candidate_origins
            if isinstance(value, str) and ":" in value
        }
        for kind, field in (
            ("ActivationOriginId", "activation_origin_id_or_null"),
            ("EvidenceOriginId", "evidence_origin_id_or_null"),
            ("ImportBindingId", "import_binding_id_or_null"),
        ):
            if (
                kind in candidate_origin_kinds
                and reference.get(field) is None
            ):
                failures.add("REFERENCE_ORIGIN_LINKAGE")
        source_span = reference.get("source_span", {})
        if not isinstance(source_span, dict):
            failures.add("SOURCE_SPAN")
            source_span = {}
        span_start = source_span.get("start")
        span_end = source_span.get("end")
        if (
            set(source_span) != {"start", "end"}
            or type(span_start) is not int
            or type(span_end) is not int
            or span_start < 0
            or span_end < span_start
        ):
            failures.add("SOURCE_SPAN")

        stages = reference.get("stages", [])
        stage_sequence_invalid = (
            not isinstance(stages, list)
            or not all(isinstance(row, dict) for row in stages)
            or len(stages) != 9
            or [row.get("ordinal") for row in stages]
            != list(range(1, 10))
            or [row.get("predicate") for row in stages]
            != list(R4_NRM_STAGE_SEQUENCE)
            or any(
                set(row) != {"ordinal", "predicate", "status"}
                or type(row.get("ordinal")) is not int
                for row in stages
            )
        )
        if stage_sequence_invalid:
            failures.add("STAGE_SEQUENCE")
            continue
        statuses = [row.get("status") for row in stages]
        failed_indices = [
            index for index, status in enumerate(statuses)
            if status == "FAIL"
        ]
        if failed_indices:
            failed_index = failed_indices[0]
            if (
                statuses[:failed_index] != ["PASS"] * failed_index
                or statuses[failed_index] != "FAIL"
                or statuses[failed_index + 1:]
                != ["NOT_EVALUATED"] * (8 - failed_index)
                or len(failed_indices) != 1
            ):
                failures.add("FAILURE_ORDER")
            result = reference.get("result", {})
            if not isinstance(result, dict):
                result = {}
            if result.get("kind") != "REJECTED":
                failures.add("REJECTED_RESULT")
            if (
                set(result)
                != {
                    "kind",
                    "resolved_ref_or_null",
                    "selected_count",
                    "rejection_reason",
                }
                or result.get("resolved_ref_or_null") is not None
                or type(result.get("selected_count")) is not int
                or result.get("selected_count") != 0
            ):
                failures.add("REJECTED_RESULT")
            reason = result.get("rejection_reason")
            if reason not in set(R4_NRM_PRECEDENCE[failed_index][2]):
                failures.add("REJECTION_REASON_STAGE")
            if isinstance(source_origin_id, str) and isinstance(reason, str):
                failed_reference_rows.append(
                    (failed_index, source_origin_id, reason)
                )
            if failed_index == 7 and isinstance(reason, str):
                hir_seal_reasons.append(reason)
        else:
            if statuses != ["PASS"] * 9:
                failures.add("PASS_SEQUENCE")
            result = reference.get("result", {})
            if not isinstance(result, dict):
                result = {}
            result_kind = result.get("kind")
            if not candidate_origins:
                failures.add("ACCEPTED_CANDIDATE_EVIDENCE")
            import_binding_id = reference.get("import_binding_id_or_null")
            if (
                import_binding_id is not None
                and import_binding_id not in candidate_origins
            ):
                failures.add("ACCEPTED_CANDIDATE_EVIDENCE")
            if result_kind == "RESOLVED_NONCALL_REFERENCE":
                namespace = reference.get("namespace")
                resolved_identity = result.get("resolved_identity")
                resolved_identity_domain_ok = (
                    (
                        namespace == "MODULE"
                        and is_typed_id(resolved_identity, "ModuleId")
                    )
                    or (
                        namespace == "TYPE"
                        and is_typed_id(resolved_identity, "DeclId")
                    )
                    or (
                        namespace == "VALUE"
                        and is_typed_id_in(
                            resolved_identity,
                            {"HirLocalId", "DeclId"},
                        )
                    )
                )
                if (
                    set(result)
                    != {
                        "kind",
                        "resolved_identity",
                        "selected_count",
                        "rejection_reason_or_null",
                    }
                    or not resolved_identity_domain_ok
                    or type(result.get("selected_count")) is not int
                    or result.get("selected_count") != 1
                    or result.get("rejection_reason_or_null") is not None
                    or namespace == "CALLABLE_OVERLOAD_SET"
                ):
                    failures.add("ACCEPTED_RESULT")
                if (
                    not visibility_proofs
                    or len(candidate_origins) != 1
                    or (
                        import_binding_id is None
                        and resolved_identity not in candidate_origins
                    )
                ):
                    failures.add("ACCEPTED_CANDIDATE_EVIDENCE")
            elif (
                result_kind
                == "RESOLVED_OVERLOAD_SET_REF_IN_ANALYSIS_HIR"
            ):
                if (
                    set(result)
                    != {
                        "kind",
                        "analysis_hir_overload_set_ref",
                        "canonical_hir_projection",
                        "winner_selected",
                    }
                    or not is_typed_id(
                        result.get("analysis_hir_overload_set_ref"),
                        "ResolvedOverloadSetRef",
                    )
                    or result.get("canonical_hir_projection") is not False
                    or result.get("winner_selected") is not False
                    or reference.get("namespace")
                    != "CALLABLE_OVERLOAD_SET"
                ):
                    failures.add("ACCEPTED_RESULT")
            else:
                failures.add("ACCEPTED_RESULT")
        if statuses[4] == "PASS" and not candidate_origins:
            failures.add("STAGE_EVIDENCE_BINDING")
        if (
            statuses[5] == "PASS"
            and reference.get("namespace") != "CALLABLE_OVERLOAD_SET"
            and not visibility_proofs
        ):
            failures.add("STAGE_EVIDENCE_BINDING")
    if trace.get("diagnostic_order") != (
        "LOWEST_FAILED_STAGE_THEN_EXACT_OWNER_PRIMARY_THEN_"
        "LOWEST_SOURCE_ORIGIN_ID"
    ):
        failures.add("DIAGNOSTIC_ORDER")
    diagnostic_selection = trace.get("diagnostic_selection", {})
    if not isinstance(diagnostic_selection, dict):
        diagnostic_selection = {}
    expected_diagnostic_fields = {
        "winner_source_origin_id_or_null",
        "winner_rejection_reason_or_null",
        "suppressed_source_origin_ids",
    }
    ordered_failures = sorted(failed_reference_rows)
    if ordered_failures:
        expected_winner = ordered_failures[0]
        expected_suppressed = sorted(
            source_origin_id
            for _, source_origin_id, _ in ordered_failures[1:]
        )
        diagnostic_selection_valid = (
            set(diagnostic_selection) == expected_diagnostic_fields
            and diagnostic_selection.get(
                "winner_source_origin_id_or_null"
            )
            == expected_winner[1]
            and diagnostic_selection.get(
                "winner_rejection_reason_or_null"
            )
            == expected_winner[2]
            and diagnostic_selection.get(
                "suppressed_source_origin_ids"
            )
            == expected_suppressed
        )
    else:
        diagnostic_selection_valid = (
            set(diagnostic_selection) == expected_diagnostic_fields
            and diagnostic_selection.get(
                "winner_source_origin_id_or_null"
            )
            is None
            and diagnostic_selection.get(
                "winner_rejection_reason_or_null"
            )
            is None
            and diagnostic_selection.get(
                "suppressed_source_origin_ids"
            )
            == []
        )
    if not diagnostic_selection_valid:
        failures.add("DIAGNOSTIC_SELECTION")

    seal = trace.get("seal", {})
    if not isinstance(seal, dict):
        return failures | {"HIR_SEAL"}
    seal_counter_fields = {
        "unbound_primary_count",
        "unresolved_count",
        "candidate_set_count",
        "missing_typed_id_count",
        "missing_visibility_proof_count",
        "recovery_binding_count",
        "runtime_relookup_count",
        "overload_winner_count",
        "canonical_hir_overload_set_ref_count",
    }
    counters = seal.get("counters", {})
    seal_shape_valid = (
        set(seal) == {"seal_status", "counters"}
        and isinstance(counters, dict)
        and set(counters) == seal_counter_fields
    )
    if not seal_shape_valid:
        failures.add("HIR_SEAL")
        return failures

    failure_indices = [row[0] for row in failed_reference_rows]
    if any(index < 7 for index in failure_indices):
        expected_seal_status = "NOT_EVALUATED"
    elif any(index == 7 for index in failure_indices):
        expected_seal_status = "REJECTED_AT_HIR_SEAL"
    else:
        expected_seal_status = "SEALED"
    if seal.get("seal_status") != expected_seal_status:
        failures.add("HIR_SEAL")

    if expected_seal_status == "NOT_EVALUATED":
        if any(counters.get(key) is not None for key in seal_counter_fields):
            failures.add("HIR_SEAL")
    elif expected_seal_status == "SEALED":
        if any(
            type(counters.get(key)) is not int
            or counters.get(key) != 0
            for key in seal_counter_fields
        ):
            failures.add("HIR_SEAL")
    else:
        reason_to_counter = {
            "UNBOUND_PRIMARY": "unbound_primary_count",
            "UNRESOLVED_COUNT_NONZERO": "unresolved_count",
            "CANDIDATE_SET_COUNT_NONZERO": "candidate_set_count",
            "MISSING_TYPED_ID": "missing_typed_id_count",
            "MISSING_VISIBILITY_PROOF": (
                "missing_visibility_proof_count"
            ),
            "RUNTIME_RELOOKUP_RESIDUE": "runtime_relookup_count",
        }
        expected_counts = {
            key: 0 for key in seal_counter_fields
        }
        for reason in hir_seal_reasons:
            counter = reason_to_counter.get(reason)
            if counter is not None:
                expected_counts[counter] += 1
        if any(
            type(counters.get(key)) is not int
            or counters.get(key) != expected_counts[key]
            for key in seal_counter_fields
        ):
            failures.add("HIR_SEAL_COUNTER_BINDING")
    trace_sha256 = trace.get("trace_sha256")
    if (
        not canonical_domain_failure
        and (
            re.fullmatch(r"[0-9a-f]{64}", str(trace_sha256 or ""))
            is None
            or trace_sha256
            != canonical_self_digest(trace, "trace_sha256")
        )
    ):
        failures.add("RESOLVER_TRACE_DIGEST")
    return failures


def r4_nrm_mechanical_self_test_results() -> list[tuple[bool, str, str]]:
    """Run E2 design-static probes; product lanes remain 15/15 NOT_RUN."""

    zero = "0" * 64
    canonical_unicode_vector = {
        "z": "한😀",
        "a": "quote:\" slash:\\ newline:\n",
    }
    canonical_unicode_vector_bytes = json.dumps(
        canonical_unicode_vector,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    canonical_unicode_vector_pass = (
        canonical_unicode_vector_bytes.hex()
        == (
            "7b2261223a2271756f74653a5c2220736c6173683a5c5c206e6577"
            "6c696e653a5c6e222c227a223a22ed959cf09f9880227d"
        )
        and canonical_sha(canonical_unicode_vector)
        == "333657884e20443a6ee4c742f2e894b34939238558c85e2a9cd720818169ba3c"
        and canonical_sha({"invalid": "\ud800"}) is None
    )
    invalid_canonical_values: list[Any] = [
        {1: "coerced-key"},
        {"mixed": "key", 1: "value"},
        {"finite_float": 1.25},
        {"nan": float("nan")},
        {"positive_infinity": float("inf")},
        {"negative_infinity": float("-inf")},
        ("tuple",),
        b"bytes",
        bytearray(b"bytes"),
        {"set"},
        object(),
    ]
    canonical_invalid_domain_pass = (
        all(canonical_sha(value) is None for value in invalid_canonical_values)
        and canonical_self_digest(
            {1: "coerced-key", "sha256": "0" * 64}, "sha256"
        )
        is None
        and canonical_sha({"1": "string-key"}) is not None
    )
    source_role_carrier: dict[str, Any] = {
        "schema": "deeplus.source-role-carrier/r2",
        "profile": "R4_NAME_RESOLUTION_MODULES",
        "package_id": "PackageId:root",
        "targets": [
            {
                "target_id": "TargetId:root.lib",
                "canonical_manifest_target_name": "lib",
                "target_kind": "library",
                "source_role_policy": "library",
                "activation_profile": "stable",
            }
        ],
        "package_module_source_graph_sha256": zero,
        "source_files": [
            {
                "path": "src/lib.dp",
                "source_role": "library",
                "source_file_id": "SourceFileId:root.lib/src/lib.dp",
                "target_id": "TargetId:root.lib",
                "activation_profile": "stable",
                "module_id": "ModuleId:root.lib",
                "module_path": ["root", "lib"],
            }
        ],
    }
    source_role_dangling_target = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_dangling_target["source_files"][0][
        "target_id"
    ] = "TargetId:missing"
    source_role_profile_mismatch = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_profile_mismatch["source_files"][0][
        "activation_profile"
    ] = "preview"
    source_role_noncanonical_path = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_noncanonical_path["source_files"][0][
        "path"
    ] = "src/../src/lib.dp"
    source_role_duplicate_path = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_duplicate_path["source_files"].append(
        {
            **source_role_duplicate_path["source_files"][0],
            "source_file_id": "SourceFileId:root.lib/src/lib-copy.dp",
        }
    )
    source_role_target_policy_mismatch = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_target_policy_mismatch["targets"][0][
        "source_role_policy"
    ] = "script"
    source_role_target_key_collision = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_target_key_collision["targets"].append(
        {
            **source_role_target_key_collision["targets"][0],
            "target_id": "TargetId:root.lib-alias",
        }
    )
    source_role_empty_sources = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_empty_sources["source_files"] = []
    source_role_module_identity_collision = json.loads(
        json.dumps(source_role_carrier)
    )
    source_role_module_identity_collision["source_files"].append(
        {
            **source_role_module_identity_collision["source_files"][0],
            "path": "src/other.dp",
            "source_file_id": "SourceFileId:root.lib/src/other.dp",
            "module_id": "ModuleId:root.alias",
        }
    )
    source_role_mutants = [
        ("SOURCE_TARGET_REFERENCE", source_role_dangling_target),
        ("SOURCE_TARGET_PROFILE", source_role_profile_mismatch),
        ("SOURCE_PATH_NORMALIZATION", source_role_noncanonical_path),
        ("SOURCE_PATH_IDENTITY", source_role_duplicate_path),
        (
            "TARGET_SOURCE_ROLE_POLICY",
            source_role_target_policy_mismatch,
        ),
        ("TARGET_IDENTITY_RECIPE", source_role_target_key_collision),
        ("TARGET_SOURCE_REFERENCE", source_role_empty_sources),
        (
            "MODULE_IDENTITY_RECIPE",
            source_role_module_identity_collision,
        ),
    ]
    source_role_pass = not r4_source_role_carrier_failure_codes(
        source_role_carrier
    )
    source_role_mutants_pass = all(
        expected in r4_source_role_carrier_failure_codes(mutant)
        for expected, mutant in source_role_mutants
    )

    package_graph: dict[str, Any] = {
        "schema": "deeplus.package-module-source-graph/r1",
        "root_package_id": "PackageId:root",
        "packages": [
            {
                "package_id": "PackageId:root",
                "canonical_package_key": {
                    "registry_namespace": "local",
                    "package_name": "root",
                    "package_version_identity": "0",
                },
                "resolved_artifact_provenance_digest": zero,
                "dependency_binding_ids": [],
                "target_ids": ["TargetId:root.lib"],
            }
        ],
        "targets": [
            {
                "target_id": "TargetId:root.lib",
                "package_id": "PackageId:root",
                "canonical_manifest_target_name": "lib",
                "target_kind": "library",
                "source_role_policy": "library",
                "activation_profile": "stable",
                "source_file_ids": [
                    "SourceFileId:root.lib/src/lib.dp"
                ],
            }
        ],
        "source_contributions": [
            {
                "source_file_id": "SourceFileId:root.lib/src/lib.dp",
                "target_id": "TargetId:root.lib",
                "normalized_project_relative_path": "src/lib.dp",
                "source_role": "library",
                "activation_profile": "stable",
                "module_id": "ModuleId:root.lib",
                "module_path": ["root", "lib"],
                "explicit_module_path_or_null": ["root", "lib"],
                "source_bytes_sha256": zero,
            }
        ],
        "dependency_bindings": [],
        "visible_module_bindings": [
            {
                "consumer_target_id": "TargetId:root.lib",
                "visible_qualified_path": ["root", "lib"],
                "resolved_module_id": "ModuleId:root.lib",
                "dependency_binding_id_or_self": "self",
            }
        ],
        "module_header_import_edges": [],
        "graph_policy": {
            "package_dependency": "ACYCLIC",
            "module_header_import": (
                "HEADER_ONLY_SCC_ALLOWED_AFTER_COMPLETE_HEADER_COLLECTION"
            ),
            "reexport": "ACYCLIC",
            "static_binding_value_dependency": (
                "ACYCLIC_COMPILE_TIME_EVALUATION_ZERO_RUNTIME_INIT"
            ),
        },
        "canonical_order": "TYPED_ID_CANONICAL_BYTE_ORDER",
        "canonical_graph_sha256": zero,
    }
    package_graph["canonical_graph_sha256"] = canonical_self_digest(
        package_graph, "canonical_graph_sha256"
    )
    package_mutants = []
    wrong_domain = json.loads(json.dumps(package_graph))
    wrong_domain["root_package_id"] = "HirLocalId:root"
    package_mutants.append(("IDENTITY_DOMAIN", wrong_domain))
    unknown_graph_field = json.loads(json.dumps(package_graph))
    unknown_graph_field["not_in_schema"] = True
    unknown_graph_field["canonical_graph_sha256"] = canonical_self_digest(
        unknown_graph_field, "canonical_graph_sha256"
    )
    package_mutants.append(
        ("PACKAGE_GRAPH_SCHEMA_SHAPE", unknown_graph_field)
    )
    unknown_package_field = json.loads(json.dumps(package_graph))
    unknown_package_field["packages"][0]["not_in_schema"] = True
    unknown_package_field["canonical_graph_sha256"] = (
        canonical_self_digest(
            unknown_package_field, "canonical_graph_sha256"
        )
    )
    package_mutants.append(
        ("PACKAGE_GRAPH_SCHEMA_SHAPE", unknown_package_field)
    )
    unsorted_package_rows = json.loads(json.dumps(package_graph))
    unsorted_package_rows["packages"] = [
        {
            **unsorted_package_rows["packages"][0],
            "package_id": "PackageId:z",
            "canonical_package_key": {
                "registry_namespace": "local",
                "package_name": "z",
                "package_version_identity": "0",
            },
            "target_ids": ["TargetId:root.lib"],
        },
        unsorted_package_rows["packages"][0],
    ]
    unsorted_package_rows["canonical_graph_sha256"] = (
        canonical_self_digest(
            unsorted_package_rows, "canonical_graph_sha256"
        )
    )
    package_mutants.append(
        ("PACKAGE_GRAPH_CANONICAL_ORDER", unsorted_package_rows)
    )
    package_digest_flip = json.loads(json.dumps(package_graph))
    package_digest_flip["canonical_graph_sha256"] = "f" * 64
    package_mutants.append(("PACKAGE_GRAPH_DIGEST", package_digest_flip))
    package_lone_surrogate = json.loads(json.dumps(package_graph))
    package_lone_surrogate["packages"][0]["canonical_package_key"][
        "registry_namespace"
    ] = "\ud800"
    package_mutants.append(
        ("CANONICAL_JSON_NON_UNICODE_SCALAR", package_lone_surrogate)
    )
    package_invalid_json_domain = json.loads(json.dumps(package_graph))
    package_invalid_json_domain["packages"][0]["canonical_package_key"][
        "registry_namespace"
    ] = 1.25
    package_mutants.append(
        (
            "CANONICAL_JSON_INVALID_VALUE_DOMAIN",
            package_invalid_json_domain,
        )
    )
    dangling_target = json.loads(json.dumps(package_graph))
    dangling_target["packages"][0]["target_ids"] = ["TargetId:missing"]
    package_mutants.append(("PACKAGE_TARGET_REFERENCE", dangling_target))
    cycle = json.loads(json.dumps(package_graph))
    cycle["dependency_bindings"] = [
        {
            "dependency_binding_id": "DependencyBindingId:self",
            "consumer_package_id": "PackageId:root",
            "source_visible_binding": "self",
            "provider_package_id": "PackageId:root",
        }
    ]
    cycle["packages"][0]["dependency_binding_ids"] = [
        "DependencyBindingId:self"
    ]
    package_mutants.append(("PACKAGE_CYCLE", cycle))
    static_cycle = json.loads(json.dumps(package_graph))
    static_cycle["module_header_import_edges"] = [
        {
            "from_module_id": "ModuleId:root.lib",
            "to_module_id": "ModuleId:root.lib",
            "edge_kind": "static_value_dependency",
            "scc_admission": "SCC_FORBIDDEN",
        }
    ]
    package_mutants.append(("FORBIDDEN_MODULE_CYCLE", static_cycle))
    omitted_reverse_target = json.loads(json.dumps(package_graph))
    omitted_reverse_target["targets"].append(
        {
            "target_id": "TargetId:root.extra",
            "package_id": "PackageId:root",
            "source_role_policy": "library",
            "activation_profile": "stable",
            "source_file_ids": [
                "SourceFileId:root.extra/src/lib.dp"
            ],
        }
    )
    omitted_reverse_target["source_contributions"].append(
        {
            "source_file_id": "SourceFileId:root.extra/src/lib.dp",
            "target_id": "TargetId:root.extra",
            "source_role": "library",
            "activation_profile": "stable",
            "module_id": "ModuleId:root.extra",
            "module_path": ["root", "extra"],
            "explicit_module_path_or_null": ["root", "extra"],
        }
    )
    package_mutants.append(
        ("PACKAGE_TARGET_REFERENCE", omitted_reverse_target)
    )
    mixed_module_cycle = json.loads(json.dumps(package_graph))
    mixed_module_cycle["targets"][0]["source_file_ids"].append(
        "SourceFileId:root.lib/src/other.dp"
    )
    mixed_module_cycle["source_contributions"].append(
        {
            "source_file_id": "SourceFileId:root.lib/src/other.dp",
            "target_id": "TargetId:root.lib",
            "source_role": "library",
            "activation_profile": "stable",
            "module_id": "ModuleId:root.other",
            "module_path": ["root", "other"],
            "explicit_module_path_or_null": ["root", "other"],
        }
    )
    mixed_module_cycle["module_header_import_edges"] = [
        {
            "from_module_id": "ModuleId:root.lib",
            "to_module_id": "ModuleId:root.other",
            "edge_kind": "static_value_dependency",
            "scc_admission": "SCC_FORBIDDEN",
        },
        {
            "from_module_id": "ModuleId:root.other",
            "to_module_id": "ModuleId:root.lib",
            "edge_kind": "module_header_reference",
            "scc_admission": (
                "HEADER_ONLY_ALLOWED_AFTER_COMPLETE_HEADER_COLLECTION"
            ),
        },
    ]
    package_mutants.append(
        ("FORBIDDEN_MODULE_CYCLE", mixed_module_cycle)
    )
    two_package_graph = json.loads(json.dumps(package_graph))
    two_package_graph["packages"].append(
        {
            "package_id": "PackageId:dep",
            "dependency_binding_ids": [],
            "target_ids": ["TargetId:dep.lib"],
        }
    )
    two_package_graph["targets"].append(
        {
            "target_id": "TargetId:dep.lib",
            "package_id": "PackageId:dep",
            "source_role_policy": "library",
            "activation_profile": "stable",
            "source_file_ids": ["SourceFileId:dep.lib/src/lib.dp"],
        }
    )
    two_package_graph["source_contributions"].append(
        {
            "source_file_id": "SourceFileId:dep.lib/src/lib.dp",
            "target_id": "TargetId:dep.lib",
            "source_role": "library",
            "activation_profile": "stable",
            "module_id": "ModuleId:dep.lib",
            "module_path": ["dep", "lib"],
            "explicit_module_path_or_null": ["dep", "lib"],
        }
    )
    orphan_dependency = json.loads(json.dumps(two_package_graph))
    orphan_dependency["dependency_bindings"].append(
        {
            "dependency_binding_id": "DependencyBindingId:dep",
            "consumer_package_id": "PackageId:root",
            "source_visible_binding": "dep",
            "provider_package_id": "PackageId:dep",
        }
    )
    package_mutants.append(
        ("PACKAGE_DEPENDENCY_REFERENCE", orphan_dependency)
    )
    foreign_self_binding = json.loads(json.dumps(two_package_graph))
    foreign_self_binding["visible_module_bindings"].append(
        {
            "consumer_target_id": "TargetId:root.lib",
            "visible_qualified_path": ["dep", "lib"],
            "resolved_module_id": "ModuleId:dep.lib",
            "dependency_binding_id_or_self": "self",
        }
    )
    package_mutants.append(
        ("VISIBLE_DEPENDENCY_REFERENCE", foreign_self_binding)
    )
    wrong_visible_path = json.loads(json.dumps(package_graph))
    wrong_visible_path["visible_module_bindings"][0][
        "visible_qualified_path"
    ] = ["wrong", "path"]
    package_mutants.append(
        ("VISIBLE_PATH_PROJECTION", wrong_visible_path)
    )
    target_policy_mismatch = json.loads(json.dumps(package_graph))
    target_policy_mismatch["targets"][0][
        "source_role_policy"
    ] = "script"
    package_mutants.append(
        ("TARGET_SOURCE_ROLE_POLICY", target_policy_mismatch)
    )
    script_import = json.loads(json.dumps(package_graph))
    script_import["targets"][0]["target_kind"] = "script"
    script_import["targets"][0]["source_role_policy"] = "script"
    script_import["source_contributions"][0][
        "source_role"
    ] = "script"
    package_mutants.append(("SCRIPT_MODULE_IMPORT", script_import))
    deep_nodes = {f"Node:{index}" for index in range(1500)}
    deep_edges = [
        (f"Node:{index}", f"Node:{index + 1}")
        for index in range(1499)
    ]
    iterative_graph_pass = not has_directed_cycle(
        deep_nodes, deep_edges
    )
    package_pass = not r4_package_graph_failure_codes(package_graph)
    package_mutants_pass = all(
        expected in r4_package_graph_failure_codes(mutant)
        for expected, mutant in package_mutants
    )

    initialization_plan: dict[str, Any] = {
        "schema": "deeplus.module-initialization-plan/r1",
        "module_id": "ModuleId:root.lib",
        "graph_profile": (
            "ACYCLIC_COMPILE_TIME_EVALUATION_ZERO_RUNTIME_INIT"
        ),
        "bindings": [
            {
                "binding_decl_id": "DeclId:a",
                "dependency_decl_ids": [],
                "value_sha256": zero,
                "evaluation_status": "COMPILE_TIME_SUCCEEDED",
            },
            {
                "binding_decl_id": "DeclId:b",
                "dependency_decl_ids": [],
                "value_sha256": "1" * 64,
                "evaluation_status": "COMPILE_TIME_SUCCEEDED",
            },
            {
                "binding_decl_id": "DeclId:c",
                "dependency_decl_ids": ["DeclId:a", "DeclId:b"],
                "value_sha256": "2" * 64,
                "evaluation_status": "COMPILE_TIME_SUCCEEDED",
            },
        ],
        "topological_evaluation_order": [
            "DeclId:a",
            "DeclId:b",
            "DeclId:c",
        ],
        "evaluation_order": "TOPOLOGICAL_THEN_CANONICAL_DECL_ID",
        "receipt_order": "CANONICAL_DECL_ID_ORDER",
        "commit": "ONE_ATOMIC_COMMIT_AFTER_ALL_VALUES_SUCCEED",
        "runtime_initializer_count": 0,
        "semantic_order_winner": False,
        "plan_sha256": zero,
    }
    initialization_plan["plan_sha256"] = canonical_self_digest(
        initialization_plan, "plan_sha256"
    )

    def reseal(value: dict[str, Any], field: str) -> dict[str, Any]:
        value[field] = canonical_self_digest(value, field)
        return value

    initialization_cycle = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_cycle["bindings"][0]["dependency_decl_ids"] = [
        "DeclId:c"
    ]
    reseal(initialization_cycle, "plan_sha256")
    initialization_dangling = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_dangling["bindings"][2][
        "dependency_decl_ids"
    ] = ["DeclId:missing"]
    reseal(initialization_dangling, "plan_sha256")
    initialization_wrong_order = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_wrong_order[
        "topological_evaluation_order"
    ] = ["DeclId:b", "DeclId:a", "DeclId:c"]
    reseal(initialization_wrong_order, "plan_sha256")
    initialization_wrong_domain = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_wrong_domain["bindings"][0][
        "binding_decl_id"
    ] = "DependencyBindingId:a"
    reseal(initialization_wrong_domain, "plan_sha256")
    initialization_bad_digest = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_bad_digest["plan_sha256"] = zero
    initialization_unknown_top = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_unknown_top["not_in_schema"] = True
    reseal(initialization_unknown_top, "plan_sha256")
    initialization_unknown_binding = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_unknown_binding["bindings"][0][
        "not_in_schema"
    ] = True
    reseal(initialization_unknown_binding, "plan_sha256")
    initialization_dependency_permutation = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_dependency_permutation["bindings"][2][
        "dependency_decl_ids"
    ].reverse()
    reseal(initialization_dependency_permutation, "plan_sha256")
    initialization_binding_permutation = json.loads(
        json.dumps(initialization_plan)
    )
    initialization_binding_permutation["bindings"][0:2] = reversed(
        initialization_binding_permutation["bindings"][0:2]
    )
    reseal(initialization_binding_permutation, "plan_sha256")
    initialization_mutants = [
        ("STATIC_DEPENDENCY_CYCLE", initialization_cycle),
        ("STATIC_DEPENDENCY_REFERENCE", initialization_dangling),
        ("STATIC_EVALUATION_ORDER", initialization_wrong_order),
        ("STATIC_BINDING_SET", initialization_wrong_domain),
        ("INITIALIZATION_PROFILE", initialization_unknown_top),
        ("STATIC_BINDING_SET", initialization_unknown_binding),
        (
            "STATIC_DEPENDENCY_SET",
            initialization_dependency_permutation,
        ),
        ("STATIC_RECEIPT_ORDER", initialization_binding_permutation),
        ("INITIALIZATION_DIGEST", initialization_bad_digest),
    ]
    initialization_pass = (
        not r4_module_initialization_failure_codes(initialization_plan)
    )
    initialization_mutants_pass = all(
        expected in r4_module_initialization_failure_codes(mutant)
        for expected, mutant in initialization_mutants
    )

    receipt_imports = [
        {
            "import_binding_id": "ImportBindingId:Widget",
            "resolver_scope_id": "ResolverScopeId:source",
            "namespace": "TYPE",
            "local_binding_name": "Widget",
            "resolved_target_identity": "DeclId:Widget",
            "source_origin_id": "SourceOriginId:import-Widget",
            "provider_binding_id_or_self": "DependencyBindingId:dep",
            "provider_module_id": "ModuleId:dep.lib",
        }
    ]
    receipt_activations = [
        {
            "activation_origin_id": "ActivationOriginId:extension",
            "resolver_scope_id": "ResolverScopeId:source",
            "activated_identity": "ExtensionSetId:extension",
            "activation_kind": "use",
            "semantic_site_key": "source:use-extension",
            "provider_binding_id_or_self": "DependencyBindingId:dep",
            "provider_module_id": "ModuleId:dep.extra",
        }
    ]
    provider_interface: dict[str, Any] = {
        "schema": "deeplus.module-api-digest/r51f3",
        "baseline": "0.1.2-baseline.r51f3",
        "module_id": "ModuleId:dep.lib",
        "source_role": "library",
        "interface_profile": "R4_NAME_RESOLUTION_MODULES",
        "r4_interface_envelope": {
            "activation_profile": "stable",
            "public_export_rows": [],
            "public_activation_reexport_rows": [],
            "opaque_facade_rows": [],
            "signature_relation": (
                "EXACT_NORMALIZED_PUBLIC_RESIDUE_MATCH"
            ),
            "opaque_facade_relation": "NARROWING_ONLY",
            "symbols_are_exact_effective_public_residue": True,
            "private_body_bytes_in_interface_hash": False,
        },
        "symbols": [],
        "canonical_sha256": zero,
    }
    reseal(provider_interface, "canonical_sha256")
    provider_interface_extra = json.loads(json.dumps(provider_interface))
    provider_interface_extra["module_id"] = "ModuleId:dep.extra"
    reseal(provider_interface_extra, "canonical_sha256")
    receipt_package_graph = json.loads(json.dumps(package_graph))
    receipt_package_graph["packages"][0]["dependency_binding_ids"] = [
        "DependencyBindingId:dep"
    ]
    receipt_package_graph["packages"].append(
        {
            "package_id": "PackageId:dep",
            "canonical_package_key": {
                "registry_namespace": "local",
                "package_name": "dep",
                "package_version_identity": "1",
            },
            "resolved_artifact_provenance_digest": "9" * 64,
            "dependency_binding_ids": [],
            "target_ids": ["TargetId:dep.lib"],
        }
    )
    receipt_package_graph["targets"].append(
        {
            "target_id": "TargetId:dep.lib",
            "package_id": "PackageId:dep",
            "canonical_manifest_target_name": "lib",
            "target_kind": "library",
            "source_role_policy": "library",
            "activation_profile": "stable",
            "source_file_ids": [
                "SourceFileId:dep.lib/src/lib.dp",
                "SourceFileId:dep.lib/src/extra.dp",
            ],
        }
    )
    receipt_package_graph["source_contributions"].extend(
        [
            {
                "source_file_id": "SourceFileId:dep.lib/src/lib.dp",
                "target_id": "TargetId:dep.lib",
                "normalized_project_relative_path": "src/lib.dp",
                "source_role": "library",
                "activation_profile": "stable",
                "module_id": "ModuleId:dep.lib",
                "module_path": ["dep", "lib"],
                "explicit_module_path_or_null": ["dep", "lib"],
                "source_bytes_sha256": "7" * 64,
            },
            {
                "source_file_id": "SourceFileId:dep.lib/src/extra.dp",
                "target_id": "TargetId:dep.lib",
                "normalized_project_relative_path": "src/extra.dp",
                "source_role": "library",
                "activation_profile": "stable",
                "module_id": "ModuleId:dep.extra",
                "module_path": ["dep", "extra"],
                "explicit_module_path_or_null": ["dep", "extra"],
                "source_bytes_sha256": "8" * 64,
            },
        ]
    )
    receipt_package_graph["dependency_bindings"] = [
        {
            "dependency_binding_id": "DependencyBindingId:dep",
            "consumer_package_id": "PackageId:root",
            "source_visible_binding": "dep",
            "provider_package_id": "PackageId:dep",
            "provider_interface_sha256": provider_interface[
                "canonical_sha256"
            ],
        }
    ]
    receipt_package_graph["visible_module_bindings"].extend(
        [
            {
                "consumer_target_id": "TargetId:root.lib",
                "visible_qualified_path": ["dep", "lib"],
                "resolved_module_id": "ModuleId:dep.lib",
                "dependency_binding_id_or_self": (
                    "DependencyBindingId:dep"
                ),
            },
            {
                "consumer_target_id": "TargetId:root.lib",
                "visible_qualified_path": ["dep", "extra"],
                "resolved_module_id": "ModuleId:dep.extra",
                "dependency_binding_id_or_self": (
                    "DependencyBindingId:dep"
                ),
            },
        ]
    )
    reseal(receipt_package_graph, "canonical_graph_sha256")
    dependency_receipt: dict[str, Any] = {
        "schema": "deeplus.module-compilation-dependency-receipt/r1",
        "consumer_target_id": "TargetId:root.lib",
        "consumer_module_id": "ModuleId:root.lib",
        "package_graph_sha256": receipt_package_graph[
            "canonical_graph_sha256"
        ],
        "resolver_graph_sha256": "5" * 64,
        "import_bindings": receipt_imports,
        "activation_bindings": receipt_activations,
        "required_interfaces": [
            {
                "provider_binding_id_or_self": "DependencyBindingId:dep",
                "provider_module_id": "ModuleId:dep.extra",
                "interface_profile": "R4_NAME_RESOLUTION_MODULES",
                "interface_sha256": provider_interface_extra[
                    "canonical_sha256"
                ],
            },
            {
                "provider_binding_id_or_self": "DependencyBindingId:dep",
                "provider_module_id": "ModuleId:dep.lib",
                "interface_profile": "R4_NAME_RESOLUTION_MODULES",
                "interface_sha256": provider_interface[
                    "canonical_sha256"
                ],
            }
        ],
        "canonical_order": "TYPED_ID_CANONICAL_BYTE_ORDER",
        "dependency_receipt_sha256": zero,
    }
    reseal(dependency_receipt, "dependency_receipt_sha256")
    receipt_graph = {
        "resolver_graph_sha256": "5" * 64,
        "import_bindings": receipt_imports,
        "activation_entries": receipt_activations,
    }
    provider_interfaces = {
        "ModuleId:dep.lib": provider_interface,
        "ModuleId:dep.extra": provider_interface_extra,
    }
    receipt_wrong_import_domain = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_wrong_import_domain["import_bindings"][0][
        "resolved_target_identity"
    ] = "ModuleId:not-a-type"
    reseal(receipt_wrong_import_domain, "dependency_receipt_sha256")
    receipt_wrong_activation = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_wrong_activation["activation_bindings"][0][
        "activation_kind"
    ] = "teleport"
    reseal(receipt_wrong_activation, "dependency_receipt_sha256")
    receipt_stale_provider = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_stale_provider["required_interfaces"][0][
        "interface_sha256"
    ] = "6" * 64
    reseal(receipt_stale_provider, "dependency_receipt_sha256")
    receipt_graph_mismatch = json.loads(json.dumps(dependency_receipt))
    receipt_graph_mismatch["resolver_graph_sha256"] = "7" * 64
    reseal(receipt_graph_mismatch, "dependency_receipt_sha256")
    receipt_missing_interface = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_missing_interface["required_interfaces"].pop()
    reseal(receipt_missing_interface, "dependency_receipt_sha256")
    receipt_unbound_provider = json.loads(json.dumps(dependency_receipt))
    receipt_unbound_provider["import_bindings"][0][
        "provider_module_id"
    ] = "ModuleId:dep.missing"
    reseal(receipt_unbound_provider, "dependency_receipt_sha256")
    receipt_bad_digest = json.loads(json.dumps(dependency_receipt))
    receipt_bad_digest["dependency_receipt_sha256"] = zero
    receipt_duplicate_interface_pair = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_duplicate_interface_pair["required_interfaces"].append(
        json.loads(
            json.dumps(
                receipt_duplicate_interface_pair[
                    "required_interfaces"
                ][0]
            )
        )
    )
    reseal(
        receipt_duplicate_interface_pair,
        "dependency_receipt_sha256",
    )
    receipt_unknown_top = json.loads(json.dumps(dependency_receipt))
    receipt_unknown_top["not_in_schema"] = True
    reseal(receipt_unknown_top, "dependency_receipt_sha256")
    receipt_unknown_import = json.loads(json.dumps(dependency_receipt))
    receipt_unknown_import["import_bindings"][0][
        "not_in_schema"
    ] = True
    reseal(receipt_unknown_import, "dependency_receipt_sha256")
    receipt_unknown_activation = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_unknown_activation["activation_bindings"][0][
        "not_in_schema"
    ] = True
    reseal(receipt_unknown_activation, "dependency_receipt_sha256")
    receipt_unknown_interface = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_unknown_interface["required_interfaces"][0][
        "not_in_schema"
    ] = True
    reseal(receipt_unknown_interface, "dependency_receipt_sha256")
    receipt_bad_local_name = json.loads(json.dumps(dependency_receipt))
    receipt_bad_local_name["import_bindings"][0][
        "local_binding_name"
    ] = "not-an-identifier"
    reseal(receipt_bad_local_name, "dependency_receipt_sha256")
    receipt_interface_permutation = json.loads(
        json.dumps(dependency_receipt)
    )
    receipt_interface_permutation["required_interfaces"].reverse()
    reseal(
        receipt_interface_permutation,
        "dependency_receipt_sha256",
    )
    pseudo_provider_interface = {
        "module_id": "ModuleId:dep.lib",
        "interface_profile": "R4_NAME_RESOLUTION_MODULES",
        "canonical_sha256": zero,
    }
    reseal(pseudo_provider_interface, "canonical_sha256")
    receipt_pseudo_provider = json.loads(json.dumps(dependency_receipt))
    next(
        row
        for row in receipt_pseudo_provider["required_interfaces"]
        if row["provider_module_id"] == "ModuleId:dep.lib"
    )["interface_sha256"] = pseudo_provider_interface[
        "canonical_sha256"
    ]
    reseal(receipt_pseudo_provider, "dependency_receipt_sha256")
    pseudo_provider_interfaces = dict(provider_interfaces)
    pseudo_provider_interfaces[
        "ModuleId:dep.lib"
    ] = pseudo_provider_interface
    receipt_mutants = [
        (
            "DEPENDENCY_IMPORT_DOMAIN",
            receipt_wrong_import_domain,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_ACTIVATION_DOMAIN",
            receipt_wrong_activation,
            provider_interfaces,
        ),
        (
            "STALE_PROVIDER_INTERFACE",
            receipt_stale_provider,
            provider_interfaces,
        ),
        (
            "RECEIPT_RESOLVER_GRAPH_DIGEST",
            receipt_graph_mismatch,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_INTERFACE_CLOSURE",
            receipt_missing_interface,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_PROVIDER_GRAPH_BINDING",
            receipt_unbound_provider,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_INTERFACE_IDENTITY",
            receipt_duplicate_interface_pair,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_RECEIPT_PROFILE",
            receipt_unknown_top,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_IMPORT_DOMAIN",
            receipt_unknown_import,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_ACTIVATION_DOMAIN",
            receipt_unknown_activation,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_INTERFACE_DOMAIN",
            receipt_unknown_interface,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_IMPORT_DOMAIN",
            receipt_bad_local_name,
            provider_interfaces,
        ),
        (
            "DEPENDENCY_RECEIPT_ORDER",
            receipt_interface_permutation,
            provider_interfaces,
        ),
        (
            "STALE_PROVIDER_INTERFACE",
            receipt_pseudo_provider,
            pseudo_provider_interfaces,
        ),
        (
            "DEPENDENCY_RECEIPT_DIGEST",
            receipt_bad_digest,
            provider_interfaces,
        ),
    ]
    receipt_pass = not r4_dependency_receipt_failure_codes(
        dependency_receipt,
        receipt_graph,
        provider_interfaces,
        receipt_package_graph,
    )
    receipt_mutants_pass = all(
        expected
        in r4_dependency_receipt_failure_codes(
            mutant,
            receipt_graph,
            mutant_provider_interfaces,
            receipt_package_graph,
        )
        for expected, mutant, mutant_provider_interfaces
        in receipt_mutants
    )

    visibility_closure: dict[str, Any] = {
        "schema": "deeplus.module-visibility-closure/r1",
        "module_id": "ModuleId:root.lib",
        "default_external_export_set": "EMPTY",
        "export_edges": [
            {
                "export_owner_id": "ModuleId:root.lib",
                "namespace": "TYPE",
                "exported_name": "Widget",
                "referenced_identity_id": "DeclId:Widget",
                "source_origin_id": "SourceOriginId:export-Widget",
            }
        ],
        "reexport_edges": [],
        "visibility_proofs": [
            {
                "proof_id": "VisibilityProofId:Widget",
                "export_owner_id": "ModuleId:root.lib",
                "referenced_identity_id": "DeclId:Widget",
                "api_position_kind": "nested_export",
                "api_position_path": ["Widget"],
                "owner_visibility": "public",
                "referenced_visibility": "public",
                "package_relation": "same_package",
                "module_relation": "same_module",
                "admission": "VISIBLE_NO_WIDENING",
            }
        ],
        "signature_relation": "EXACT_NORMALIZED_PUBLIC_RESIDUE_MATCH",
        "opaque_facade_relation": "NARROWING_ONLY",
        "opaque_facades": [
            {
                "export_owner_id": "ModuleId:root.lib",
                "owner_public_residue_identity_ids": ["DeclId:Widget"],
                "facade_public_residue_identity_ids": ["DeclId:Widget"],
            }
        ],
        "closure_sha256": zero,
    }
    reseal(visibility_closure, "closure_sha256")
    visibility_missing_proof = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_missing_proof["visibility_proofs"] = []
    reseal(visibility_missing_proof, "closure_sha256")
    visibility_widening = json.loads(json.dumps(visibility_closure))
    visibility_widening["visibility_proofs"][0][
        "referenced_visibility"
    ] = "private"
    reseal(visibility_widening, "closure_sha256")
    visibility_facade_widening = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_facade_widening["opaque_facades"][0][
        "facade_public_residue_identity_ids"
    ].append("DeclId:Hidden")
    reseal(visibility_facade_widening, "closure_sha256")
    visibility_wrong_export_domain = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_wrong_export_domain["export_edges"][0][
        "referenced_identity_id"
    ] = "ModuleId:not-a-type"
    reseal(visibility_wrong_export_domain, "closure_sha256")
    visibility_bad_digest = json.loads(json.dumps(visibility_closure))
    visibility_bad_digest["closure_sha256"] = zero
    visibility_unknown_top = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_unknown_top["not_in_schema"] = True
    reseal(visibility_unknown_top, "closure_sha256")
    visibility_unknown_export = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_unknown_export["export_edges"][0][
        "not_in_schema"
    ] = True
    reseal(visibility_unknown_export, "closure_sha256")
    visibility_unknown_reexport = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_unknown_reexport["reexport_edges"] = [
        {
            "activation_origin_id": "ActivationOriginId:extra",
            "export_owner_id": "ModuleId:root.lib",
            "referenced_activation_identity_id": (
                "ExtensionSetId:extra"
            ),
            "source_origin_id": "SourceOriginId:extra",
            "not_in_schema": True,
        }
    ]
    reseal(visibility_unknown_reexport, "closure_sha256")
    visibility_unknown_proof = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_unknown_proof["visibility_proofs"][0][
        "not_in_schema"
    ] = True
    reseal(visibility_unknown_proof, "closure_sha256")
    visibility_unknown_facade = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_unknown_facade["opaque_facades"][0][
        "not_in_schema"
    ] = True
    reseal(visibility_unknown_facade, "closure_sha256")
    visibility_row_permutation = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_row_permutation["export_edges"].append(
        {
            "export_owner_id": "ModuleId:root.lib",
            "namespace": "TYPE",
            "exported_name": "Alpha",
            "referenced_identity_id": "DeclId:Alpha",
            "source_origin_id": "SourceOriginId:export-Alpha",
        }
    )
    visibility_row_permutation["visibility_proofs"].append(
        {
            "proof_id": "VisibilityProofId:Alpha",
            "export_owner_id": "ModuleId:root.lib",
            "referenced_identity_id": "DeclId:Alpha",
            "api_position_kind": "nested_export",
            "api_position_path": ["Alpha"],
            "owner_visibility": "public",
            "referenced_visibility": "public",
            "package_relation": "same_package",
            "module_relation": "same_module",
            "admission": "VISIBLE_NO_WIDENING",
        }
    )
    reseal(visibility_row_permutation, "closure_sha256")
    visibility_facade_permutation = json.loads(
        json.dumps(visibility_closure)
    )
    visibility_facade_permutation["opaque_facades"][0][
        "owner_public_residue_identity_ids"
    ] = ["DeclId:Alpha", "DeclId:Widget"]
    visibility_facade_permutation["opaque_facades"][0][
        "facade_public_residue_identity_ids"
    ] = ["DeclId:Widget", "DeclId:Alpha"]
    reseal(visibility_facade_permutation, "closure_sha256")
    visibility_mutants = [
        ("EXPORT_PROOF_LINKAGE", visibility_missing_proof),
        ("VISIBILITY_WIDENING", visibility_widening),
        ("OPAQUE_FACADE_WIDENING", visibility_facade_widening),
        ("EXPORT_EDGE_DOMAIN", visibility_wrong_export_domain),
        ("VISIBILITY_CLOSURE_PROFILE", visibility_unknown_top),
        ("EXPORT_EDGE_DOMAIN", visibility_unknown_export),
        ("REEXPORT_EDGE_DOMAIN", visibility_unknown_reexport),
        ("VISIBILITY_PROOF_DOMAIN", visibility_unknown_proof),
        ("OPAQUE_FACADE_DOMAIN", visibility_unknown_facade),
        ("VISIBILITY_CLOSURE_ORDER", visibility_row_permutation),
        ("OPAQUE_FACADE_ORDER", visibility_facade_permutation),
        ("VISIBILITY_CLOSURE_DIGEST", visibility_bad_digest),
    ]
    visibility_pass = not r4_visibility_closure_failure_codes(
        visibility_closure
    )
    visibility_mutants_pass = all(
        expected in r4_visibility_closure_failure_codes(mutant)
        for expected, mutant in visibility_mutants
    )

    api_hir_symbols = [
        {
            "symbol_id": "DeclId:Widget",
            "kind": "type",
            "normalized_signature": "public class Widget",
            "responsibility_profile": {
                "profile_kind": "type",
                "declaration_ownership": "not_applicable",
            },
            "ownership": "not_applicable",
            "cleanup": "not_applicable",
            "error_set": [],
            "effect_row": [],
            "cancellation": "not_applicable",
            "suspends": "not_applicable",
            "authority": [],
            "isolation": "not_applicable",
            "evidence_ids": [],
            "construction_row_sha256": zero,
            "projection_row_sha256": None,
        }
    ]
    module_api: dict[str, Any] = {
        "schema": "deeplus.module-api-digest/r51f3",
        "baseline": "0.1.2-baseline.r51f3",
        "module_id": "ModuleId:root.lib",
        "source_role": "library",
        "interface_profile": "R4_NAME_RESOLUTION_MODULES",
        "r4_interface_envelope": {
            "activation_profile": "stable",
            "public_export_rows": [
                {
                    "export_owner_id": "ModuleId:root.lib",
                    "namespace": "TYPE",
                    "exported_name": "Widget",
                    "referenced_identity_id": "DeclId:Widget",
                }
            ],
            "public_activation_reexport_rows": [],
            "opaque_facade_rows": [
                {
                    "export_owner_id": "ModuleId:root.lib",
                    "facade_public_residue_identity_ids": [
                        "DeclId:Widget"
                    ],
                }
            ],
            "signature_relation": (
                "EXACT_NORMALIZED_PUBLIC_RESIDUE_MATCH"
            ),
            "opaque_facade_relation": "NARROWING_ONLY",
            "symbols_are_exact_effective_public_residue": True,
            "private_body_bytes_in_interface_hash": False,
        },
        "symbols": api_hir_symbols,
        "canonical_sha256": zero,
    }
    reseal(module_api, "canonical_sha256")
    source_projection: dict[str, Any] = {
        "schema": (
            "deeplus.module-source-contribution-projection/r1"
        ),
        "target_id": "TargetId:root.lib",
        "module_id": "ModuleId:root.lib",
        "source_contributions": [
            {
                "source_file_id": (
                    "SourceFileId:root.lib/src/lib.dp"
                ),
                "normalized_project_relative_path": "src/lib.dp",
                "source_role": "library",
                "activation_profile": "stable",
                "source_bytes_sha256": zero,
            }
        ],
        "projection_sha256": zero,
    }
    reseal(source_projection, "projection_sha256")
    module_implementation: dict[str, Any] = {
        "schema": "deeplus.module-implementation-digest/r1",
        "interface_profile": "R4_NAME_RESOLUTION_MODULES",
        "target_id": "TargetId:root.lib",
        "target_kind": "library",
        "module_id": "ModuleId:root.lib",
        "interface_sha256": module_api["canonical_sha256"],
        "hir_semantic_sha256": "7" * 64,
        "external_compatibility_identity": False,
        "implementation_sha256": zero,
    }
    reseal(module_implementation, "implementation_sha256")
    artifact_trace = {
        "resolver_graph_sha256": dependency_receipt[
            "resolver_graph_sha256"
        ],
        "trace_sha256": "8" * 64,
    }
    compilation_receipt: dict[str, Any] = {
        "schema": "deeplus.module-compilation-receipt/r1",
        "profile": "R4_NAME_RESOLUTION_MODULES",
        "target_id": "TargetId:root.lib",
        "target_kind": "library",
        "module_id": "ModuleId:root.lib",
        "package_graph_sha256": receipt_package_graph[
            "canonical_graph_sha256"
        ],
        "module_source_contribution_sha256": source_projection[
            "projection_sha256"
        ],
        "dependency_receipt_sha256": dependency_receipt[
            "dependency_receipt_sha256"
        ],
        "resolver_trace_sha256": artifact_trace["trace_sha256"],
        "visibility_closure_sha256": visibility_closure[
            "closure_sha256"
        ],
        "initialization_plan_sha256": initialization_plan[
            "plan_sha256"
        ],
        "interface_sha256": module_api["canonical_sha256"],
        "implementation_sha256": module_implementation[
            "implementation_sha256"
        ],
        "compilation_receipt_sha256": zero,
    }
    reseal(compilation_receipt, "compilation_receipt_sha256")
    artifact_relations = {
        "package_graph": receipt_package_graph,
        "source_projection": source_projection,
        "dependency_receipt": dependency_receipt,
        "resolver_trace": artifact_trace,
        "visibility_closure": visibility_closure,
        "initialization_plan": initialization_plan,
        "module_api": module_api,
        "implementation": module_implementation,
    }
    module_artifact_pass = (
        not r4_module_api_failure_codes(
            module_api, visibility_closure, api_hir_symbols
        )
        and not r4_module_source_projection_failure_codes(
            source_projection, receipt_package_graph
        )
        and not r4_module_implementation_failure_codes(
            module_implementation, module_api
        )
        and not r4_compilation_receipt_failure_codes(
            compilation_receipt, **artifact_relations
        )
    )

    api_provenance_leak = json.loads(json.dumps(module_api))
    api_provenance_leak["r4_interface_envelope"][
        "visibility_closure_sha256"
    ] = visibility_closure["closure_sha256"]
    reseal(api_provenance_leak, "canonical_sha256")
    api_projection_drift = json.loads(json.dumps(module_api))
    api_projection_drift["r4_interface_envelope"][
        "public_export_rows"
    ][0]["exported_name"] = "Renamed"
    reseal(api_projection_drift, "canonical_sha256")
    source_projection_drift = json.loads(json.dumps(source_projection))
    source_projection_drift["source_contributions"][0][
        "normalized_project_relative_path"
    ] = "src/renamed.dp"
    reseal(source_projection_drift, "projection_sha256")
    implementation_interface_drift = json.loads(
        json.dumps(module_implementation)
    )
    implementation_interface_drift["interface_sha256"] = "9" * 64
    reseal(
        implementation_interface_drift, "implementation_sha256"
    )
    compilation_artifact_drift = json.loads(
        json.dumps(compilation_receipt)
    )
    compilation_artifact_drift[
        "module_source_contribution_sha256"
    ] = "a" * 64
    reseal(
        compilation_artifact_drift, "compilation_receipt_sha256"
    )
    compilation_bad_digest = json.loads(
        json.dumps(compilation_receipt)
    )
    compilation_bad_digest["compilation_receipt_sha256"] = zero
    module_artifact_mutants_pass = (
        "MODULE_INTERFACE_ENVELOPE"
        in r4_module_api_failure_codes(
            api_provenance_leak, visibility_closure, api_hir_symbols
        )
        and "MODULE_INTERFACE_VISIBILITY_PROJECTION"
        in r4_module_api_failure_codes(
            api_projection_drift, visibility_closure, api_hir_symbols
        )
        and "MODULE_SOURCE_GRAPH_PROJECTION"
        in r4_module_source_projection_failure_codes(
            source_projection_drift, receipt_package_graph
        )
        and "MODULE_IMPLEMENTATION_INTERFACE_BINDING"
        in r4_module_implementation_failure_codes(
            implementation_interface_drift, module_api
        )
        and "MODULE_COMPILATION_ARTIFACT_BINDING"
        in r4_compilation_receipt_failure_codes(
            compilation_artifact_drift, **artifact_relations
        )
        and "MODULE_COMPILATION_RECEIPT_DIGEST"
        in r4_compilation_receipt_failure_codes(
            compilation_bad_digest, **artifact_relations
        )
    )

    private_change_implementation = json.loads(
        json.dumps(module_implementation)
    )
    private_change_implementation["hir_semantic_sha256"] = "b" * 64
    reseal(
        private_change_implementation, "implementation_sha256"
    )
    private_change_receipt = json.loads(
        json.dumps(compilation_receipt)
    )
    private_change_receipt[
        "implementation_sha256"
    ] = private_change_implementation["implementation_sha256"]
    reseal(private_change_receipt, "compilation_receipt_sha256")
    module_artifact_private_change_pass = (
        module_api["canonical_sha256"]
        == module_implementation["interface_sha256"]
        == private_change_implementation["interface_sha256"]
        and module_implementation["implementation_sha256"]
        != private_change_implementation["implementation_sha256"]
        and compilation_receipt["compilation_receipt_sha256"]
        != private_change_receipt["compilation_receipt_sha256"]
    )

    resolver_graph: dict[str, Any] = {
        "schema": "deeplus.resolver-graph/r1",
        "package_graph_sha256": package_graph[
            "canonical_graph_sha256"
        ],
        "root_scope_ids": ["ResolverScopeId:package-root"],
        "scopes": [
            {
                "resolver_scope_id": "ResolverScopeId:package-root",
                "parent_scope_id_or_null": None,
                "kind": "PackageRootScope",
                "package_id": "PackageId:root",
            }
        ],
        "name_bindings": [],
        "import_bindings": [],
        "activation_entries": [],
        "witness_visibility_entries": [],
        "invariants": {
            "lookup": (
                "INNERMOST_TO_OUTERMOST_STOP_AT_FIRST_NONEMPTY_"
                "EXACT_NAMESPACE_AND_SPELLING"
            ),
            "same_frame_order_priority": False,
            "cross_frame_overload_merge": False,
            "provisional_bindings_in_name_env": False,
            "environment_cross_creation_count": 0,
            "runtime_relookup_count": 0,
        },
        "resolver_graph_sha256": zero,
    }
    resolver_graph["resolver_graph_sha256"] = canonical_self_digest(
        resolver_graph, "resolver_graph_sha256"
    )
    resolver_graph_full = json.loads(json.dumps(resolver_graph))
    resolver_graph_full["scopes"].extend(
        [
            {
                "resolver_scope_id": "ResolverScopeId:target",
                "parent_scope_id_or_null": (
                    "ResolverScopeId:package-root"
                ),
                "kind": "TargetScope",
                "target_id": "TargetId:root.lib",
            },
            {
                "resolver_scope_id": "ResolverScopeId:module",
                "parent_scope_id_or_null": "ResolverScopeId:target",
                "kind": "ModuleScope",
                "module_id": "ModuleId:root.lib",
            },
            {
                "resolver_scope_id": "ResolverScopeId:source",
                "parent_scope_id_or_null": "ResolverScopeId:module",
                "kind": "SourceContributionScope",
                "source_file_id": "SourceFileId:root.lib/src/lib.dp",
            },
            {
                "resolver_scope_id": "ResolverScopeId:item",
                "parent_scope_id_or_null": "ResolverScopeId:source",
                "kind": "ItemOwnerScope",
                "decl_id": "DeclId:function",
            },
            {
                "resolver_scope_id": "ResolverScopeId:body-root",
                "parent_scope_id_or_null": "ResolverScopeId:item",
                "kind": "BodyLocalScope",
                "hir_body_id": "HirBodyId:function",
                "hir_scope_id": "HirScopeId:function.root",
                "owner_local_scope_id": "root",
                "scope_preorder_ordinal": 0,
                "scope_role": "ROOT_BODY",
            },
            {
                "resolver_scope_id": "ResolverScopeId:body-nested",
                "parent_scope_id_or_null": (
                    "ResolverScopeId:body-root"
                ),
                "kind": "BodyLocalScope",
                "hir_body_id": "HirBodyId:function",
                "hir_scope_id": "HirScopeId:function.nested",
                "owner_local_scope_id": "nested:block-1",
                "scope_preorder_ordinal": 1,
                "scope_role": "NESTED_BODY",
            },
        ]
    )
    resolver_graph_full["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:target",
            "namespace": "MODULE",
            "local_name": "lib",
            "binding_kind": "SINGLE",
            "binding_origin_kind": "DECLARATION",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "ModuleId:root.lib",
            "hir_body_id_or_null": None,
            "owner_local_binding_id_or_null": None,
            "binding_commit_ordinal_or_null": None,
            "source_origin_id": "SourceOriginId:module",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": None,
        },
        {
            "resolver_scope_id": "ResolverScopeId:module",
            "namespace": "TYPE",
            "local_name": "Widget",
            "binding_kind": "SINGLE",
            "binding_origin_kind": "DECLARATION",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "DeclId:Widget",
            "hir_body_id_or_null": None,
            "owner_local_binding_id_or_null": None,
            "binding_commit_ordinal_or_null": None,
            "source_origin_id": "SourceOriginId:Widget",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": None,
        },
        {
            "resolver_scope_id": "ResolverScopeId:body-root",
            "namespace": "VALUE",
            "local_name": "input",
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "PARAMETER",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:function.input",
            "hir_body_id_or_null": "HirBodyId:function",
            "owner_local_binding_id_or_null": "parameter:0",
            "binding_commit_ordinal_or_null": 0,
            "source_origin_id": "SourceOriginId:input",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": None,
        },
        {
            "resolver_scope_id": "ResolverScopeId:body-root",
            "namespace": "VALUE",
            "local_name": "rootValue",
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "ROOT_BODY_LOCAL",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:function.root-value",
            "hir_body_id_or_null": "HirBodyId:function",
            "owner_local_binding_id_or_null": "binding:root-value",
            "binding_commit_ordinal_or_null": 1,
            "source_origin_id": "SourceOriginId:root-value",
            "visibility_start": "AFTER_DECLARATION",
            "overload_slot_key_or_null": None,
        },
        {
            "resolver_scope_id": "ResolverScopeId:body-nested",
            "namespace": "VALUE",
            "local_name": "nestedValue",
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "NESTED_LOCAL",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:function.nested-value",
            "hir_body_id_or_null": "HirBodyId:function",
            "owner_local_binding_id_or_null": "binding:nested-value",
            "binding_commit_ordinal_or_null": 2,
            "source_origin_id": "SourceOriginId:nested-value",
            "visibility_start": "AFTER_DECLARATION",
            "overload_slot_key_or_null": None,
        },
        {
            "resolver_scope_id": "ResolverScopeId:body-nested",
            "namespace": "VALUE",
            "local_name": "patternValue",
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "COMMITTED_PATTERN_BINDING",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:function.pattern-value",
            "hir_body_id_or_null": "HirBodyId:function",
            "owner_local_binding_id_or_null": "binding:pattern-value",
            "binding_commit_ordinal_or_null": 3,
            "source_origin_id": "SourceOriginId:pattern-value",
            "visibility_start": "AFTER_TRANSACTION_COMMIT",
            "overload_slot_key_or_null": None,
        },
        {
            "resolver_scope_id": "ResolverScopeId:body-nested",
            "namespace": "CALLABLE_OVERLOAD_SET",
            "local_name": "helper",
            "binding_kind": "CALLABLE_OVERLOAD_SLOT",
            "binding_origin_kind": "LOCAL_FUNCTION",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "DeclId:helper",
            "hir_body_id_or_null": None,
            "owner_local_binding_id_or_null": None,
            "binding_commit_ordinal_or_null": None,
            "source_origin_id": "SourceOriginId:helper",
            "visibility_start": "AFTER_DECLARATION",
            "overload_slot_key_or_null": "()",
        },
    ]
    resolver_graph_full["import_bindings"] = [
        {
            "import_binding_id": "ImportBindingId:Widget",
            "resolver_scope_id": "ResolverScopeId:source",
            "namespace": "TYPE",
            "local_binding_name": "ImportedWidget",
            "resolved_target_identity": "DeclId:ImportedWidget",
            "source_origin_id": "SourceOriginId:import-widget",
            "provider_binding_id_or_self": "self",
            "provider_module_id": "ModuleId:root.lib",
        }
    ]
    resolver_graph_full["activation_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:source",
            "activation_origin_id": "ActivationOriginId:extension",
            "activated_identity": "ExtensionSetId:extension",
            "activation_kind": "use",
            "semantic_site_key": "source:use-extension",
            "provider_binding_id_or_self": "self",
            "provider_module_id": "ModuleId:root.lib",
        }
    ]
    resolver_graph_full["witness_visibility_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:item",
            "evidence_origin_id": "EvidenceOriginId:witness",
            "visible_witness_identity": "TraitWitnessId:witness",
        }
    ]
    resolver_graph_full["scopes"].sort(
        key=lambda row: row["resolver_scope_id"]
    )
    resolver_graph_full["name_bindings"].sort(
        key=lambda row: (
            row["resolver_scope_id"],
            row["namespace"],
            row["local_name"],
            row["overload_slot_key_or_null"] or "",
            row["source_origin_id"],
        )
    )
    resolver_graph_full["import_bindings"].sort(
        key=lambda row: row["import_binding_id"]
    )
    resolver_graph_full["activation_entries"].sort(
        key=lambda row: row["activation_origin_id"]
    )
    resolver_graph_full["witness_visibility_entries"].sort(
        key=lambda row: row["evidence_origin_id"]
    )
    resolver_graph_full["resolver_graph_sha256"] = (
        canonical_self_digest(
            resolver_graph_full, "resolver_graph_sha256"
        )
    )
    resolver_wrong_domain = json.loads(json.dumps(resolver_graph))
    resolver_wrong_domain["scopes"][0][
        "resolver_scope_id"
    ] = "ModuleId:package-root"
    resolver_dangling_parent = json.loads(json.dumps(resolver_graph))
    resolver_dangling_parent["scopes"].append(
        {
            "resolver_scope_id": "ResolverScopeId:child",
            "parent_scope_id_or_null": "ResolverScopeId:missing",
            "kind": "ModuleScope",
            "module_id": "ModuleId:root.lib",
        }
    )
    resolver_empty_roots = json.loads(json.dumps(resolver_graph))
    resolver_empty_roots["root_scope_ids"] = []
    duplicate_scope_owner = json.loads(json.dumps(resolver_graph))
    duplicate_scope_owner["root_scope_ids"].append(
        "ResolverScopeId:package-root-alias"
    )
    duplicate_scope_owner["scopes"].append(
        {
            "resolver_scope_id": "ResolverScopeId:package-root-alias",
            "parent_scope_id_or_null": None,
            "kind": "PackageRootScope",
            "package_id": "PackageId:root",
        }
    )
    wrong_scope_parent_kind = json.loads(json.dumps(resolver_graph))
    wrong_scope_parent_kind["scopes"].append(
        {
            "resolver_scope_id": "ResolverScopeId:module-wrong-parent",
            "parent_scope_id_or_null": "ResolverScopeId:package-root",
            "kind": "ModuleScope",
            "module_id": "ModuleId:wrong-parent",
        }
    )
    single_binding = {
        "resolver_scope_id": "ResolverScopeId:package-root",
        "namespace": "VALUE",
        "local_name": "same",
        "binding_kind": "SINGLE",
        "binding_origin_kind": "DECLARATION",
        "source_admission": "CURRENT_GRAMMAR_ADMITTED",
        "typed_identity": "DeclId:single",
        "hir_body_id_or_null": None,
        "owner_local_binding_id_or_null": None,
        "binding_commit_ordinal_or_null": None,
        "source_origin_id": "SourceOriginId:single",
        "visibility_start": "SCOPE_ENTRY",
        "overload_slot_key_or_null": None,
    }
    callable_binding = {
        "resolver_scope_id": "ResolverScopeId:package-root",
        "namespace": "VALUE",
        "local_name": "same",
        "binding_kind": "CALLABLE_OVERLOAD_SLOT",
        "binding_origin_kind": "DECLARATION",
        "source_admission": "CURRENT_GRAMMAR_ADMITTED",
        "typed_identity": "DeclId:callable",
        "hir_body_id_or_null": None,
        "owner_local_binding_id_or_null": None,
        "binding_commit_ordinal_or_null": None,
        "source_origin_id": "SourceOriginId:callable",
        "visibility_start": "SCOPE_ENTRY",
        "overload_slot_key_or_null": "()",
    }
    resolver_single_then_callable = json.loads(
        json.dumps(resolver_graph)
    )
    resolver_single_then_callable["name_bindings"] = [
        single_binding,
        callable_binding,
    ]
    resolver_callable_then_single = json.loads(
        json.dumps(resolver_graph)
    )
    resolver_callable_then_single["name_bindings"] = [
        callable_binding,
        single_binding,
    ]
    duplicate_import_identity = json.loads(json.dumps(resolver_graph))
    duplicate_import_identity["import_bindings"] = [
        {
            "import_binding_id": "ImportBindingId:duplicate",
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "TYPE",
            "local_binding_name": "First",
            "resolved_target_identity": "DeclId:first",
            "source_origin_id": "SourceOriginId:first",
        },
        {
            "import_binding_id": "ImportBindingId:duplicate",
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "VALUE",
            "local_binding_name": "second",
            "resolved_target_identity": "DeclId:second",
            "source_origin_id": "SourceOriginId:second",
        },
    ]
    wrong_import_target_domain = json.loads(json.dumps(resolver_graph))
    wrong_import_target_domain["import_bindings"] = [
        {
            "import_binding_id": "ImportBindingId:wrong-domain",
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "TYPE",
            "local_binding_name": "Wrong",
            "resolved_target_identity": "ModuleId:not-a-declaration",
            "source_origin_id": "SourceOriginId:wrong-domain",
        }
    ]
    wrong_module_import_target_domain = json.loads(
        json.dumps(resolver_graph)
    )
    wrong_module_import_target_domain["import_bindings"] = [
        {
            "import_binding_id": "ImportBindingId:wrong-module-domain",
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "MODULE",
            "local_binding_name": "WrongModule",
            "resolved_target_identity": "DeclId:not-a-module",
            "source_origin_id": "SourceOriginId:wrong-module-domain",
        }
    ]
    dangling_activation = json.loads(json.dumps(resolver_graph))
    dangling_activation["activation_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:missing",
            "activation_origin_id": "ActivationOriginId:test",
            "activated_identity": "ExtensionId:test",
            "activation_kind": "use",
            "semantic_site_key": "site:test",
        }
    ]
    dangling_witness = json.loads(json.dumps(resolver_graph))
    dangling_witness["witness_visibility_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:missing",
            "evidence_origin_id": "EvidenceOriginId:test",
            "visible_witness_identity": "TraitWitnessId:test",
        }
    ]
    wrong_activation_domain = json.loads(json.dumps(resolver_graph))
    wrong_activation_domain["activation_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "activation_origin_id": "ModuleId:not-an-activation-origin",
            "activated_identity": "ExtensionSetId:test",
            "activation_kind": "use",
            "semantic_site_key": "site:test",
        }
    ]
    reused_activation_origin = json.loads(json.dumps(resolver_graph))
    reused_activation_origin["activation_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "activation_origin_id": "ActivationOriginId:reused",
            "activated_identity": "ExtensionSetId:first",
            "activation_kind": "use",
            "semantic_site_key": "site:first",
        },
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "activation_origin_id": "ActivationOriginId:reused",
            "activated_identity": "ExtensionSetId:second",
            "activation_kind": "use",
            "semantic_site_key": "site:second",
        },
    ]
    wrong_witness_domain = json.loads(json.dumps(resolver_graph))
    wrong_witness_domain["witness_visibility_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "evidence_origin_id": "EvidenceOriginId:test",
            "visible_witness_identity": "DeclId:not-a-witness",
        }
    ]
    duplicate_witness_evidence = json.loads(json.dumps(resolver_graph))
    duplicate_witness_evidence["witness_visibility_entries"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "evidence_origin_id": "EvidenceOriginId:same",
            "visible_witness_identity": "TraitWitnessId:first",
        },
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "evidence_origin_id": "EvidenceOriginId:same",
            "visible_witness_identity": "TraitWitnessId:second",
        },
    ]
    extension_in_name_env = json.loads(json.dumps(resolver_graph))
    extension_in_name_env["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "EXTENSION_SET",
            "local_name": "ext",
            "binding_kind": "SINGLE",
            "binding_origin_kind": "DECLARATION",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "ExtensionSetId:test",
            "hir_body_id_or_null": None,
            "owner_local_binding_id_or_null": None,
            "binding_commit_ordinal_or_null": None,
            "source_origin_id": "SourceOriginId:extension-name",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": None,
        }
    ]
    witness_in_name_env = json.loads(json.dumps(resolver_graph))
    witness_in_name_env["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "TRAIT_WITNESS",
            "local_name": "witness",
            "binding_kind": "SINGLE",
            "binding_origin_kind": "DECLARATION",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "TraitWitnessId:test",
            "hir_body_id_or_null": None,
            "owner_local_binding_id_or_null": None,
            "binding_commit_ordinal_or_null": None,
            "source_origin_id": "SourceOriginId:witness-name",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": None,
        }
    ]
    extension_import_namespace = json.loads(json.dumps(resolver_graph))
    extension_import_namespace["import_bindings"] = [
        {
            "import_binding_id": "ImportBindingId:extension",
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "EXTENSION_SET",
            "local_binding_name": "ext",
            "resolved_target_identity": "DeclId:extension",
            "source_origin_id": "SourceOriginId:extension-import",
        }
    ]
    early_hir_local = json.loads(json.dumps(resolver_graph))
    early_hir_local["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "VALUE",
            "local_name": "local",
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "NESTED_LOCAL",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:test",
            "hir_body_id_or_null": "HirBodyId:missing-owner",
            "owner_local_binding_id_or_null": "local",
            "binding_commit_ordinal_or_null": 0,
            "source_origin_id": "SourceOriginId:local",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": None,
        }
    ]
    reused_hir_local = json.loads(json.dumps(resolver_graph))
    reused_hir_local["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "VALUE",
            "local_name": local_name,
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "NESTED_LOCAL",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:reused",
            "hir_body_id_or_null": "HirBodyId:reused",
            "owner_local_binding_id_or_null": local_name,
            "binding_commit_ordinal_or_null": (
                0 if local_name == "first" else 1
            ),
            "source_origin_id": f"SourceOriginId:{local_name}",
            "visibility_start": "AFTER_TRANSACTION_COMMIT",
            "overload_slot_key_or_null": None,
        }
        for local_name in ("first", "second")
    ]
    hir_local_outside_body = json.loads(json.dumps(resolver_graph))
    hir_local_outside_body["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "VALUE",
            "local_name": "outside",
            "binding_kind": "HIR_LOCAL",
            "binding_origin_kind": "ROOT_BODY_LOCAL",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "HirLocalId:outside",
            "hir_body_id_or_null": "HirBodyId:outside",
            "owner_local_binding_id_or_null": "outside",
            "binding_commit_ordinal_or_null": 0,
            "source_origin_id": "SourceOriginId:outside",
            "visibility_start": "AFTER_TRANSACTION_COMMIT",
            "overload_slot_key_or_null": None,
        }
    ]
    local_function_hoist = json.loads(json.dumps(resolver_graph))
    local_function_hoist["scopes"].append(
        {
            "resolver_scope_id": "ResolverScopeId:body-local-function",
            "parent_scope_id_or_null": "ResolverScopeId:package-root",
            "kind": "BodyLocalScope",
            "hir_body_id": "HirBodyId:local-function",
            "hir_scope_id": "HirScopeId:local-function",
            "owner_local_scope_id": "root",
            "scope_preorder_ordinal": 0,
            "scope_role": "ROOT_BODY",
        }
    )
    local_function_hoist["name_bindings"] = [
        {
            "resolver_scope_id": "ResolverScopeId:body-local-function",
            "namespace": "CALLABLE_OVERLOAD_SET",
            "local_name": "later",
            "binding_kind": "CALLABLE_OVERLOAD_SLOT",
            "binding_origin_kind": "LOCAL_FUNCTION",
            "source_admission": "CURRENT_GRAMMAR_ADMITTED",
            "typed_identity": "DeclId:later",
            "hir_body_id_or_null": None,
            "owner_local_binding_id_or_null": None,
            "binding_commit_ordinal_or_null": None,
            "source_origin_id": "SourceOriginId:later",
            "visibility_start": "SCOPE_ENTRY",
            "overload_slot_key_or_null": "()",
        }
    ]
    duplicate_root_body = json.loads(json.dumps(resolver_graph))
    duplicate_root_body["scopes"].extend(
        [
            {
                "resolver_scope_id": f"ResolverScopeId:root-body-{index}",
                "parent_scope_id_or_null": "ResolverScopeId:package-root",
                "kind": "BodyLocalScope",
                "hir_body_id": "HirBodyId:shared",
                "hir_scope_id": f"HirScopeId:root-{index}",
                "owner_local_scope_id": "root",
                "scope_preorder_ordinal": 0,
                "scope_role": "ROOT_BODY",
            }
            for index in (1, 2)
        ]
    )
    wrong_lookup = json.loads(json.dumps(resolver_graph))
    wrong_lookup["invariants"]["lookup"] = "WRONG"
    boolean_counter = json.loads(json.dumps(resolver_graph))
    boolean_counter["invariants"]["environment_cross_creation_count"] = (
        False
    )
    invalid_source_admission = json.loads(
        json.dumps(resolver_graph_full)
    )
    invalid_source_admission["name_bindings"][0][
        "source_admission"
    ] = "UNPROVEN"
    declaration_wrong_visibility = json.loads(
        json.dumps(resolver_graph_full)
    )
    next(
        row
        for row in declaration_wrong_visibility["name_bindings"]
        if row["local_name"] == "Widget"
    )[
        "visibility_start"
    ] = "AFTER_DECLARATION"
    declaration_wrong_scope = json.loads(
        json.dumps(resolver_graph_full)
    )
    next(
        row
        for row in declaration_wrong_scope["name_bindings"]
        if row["local_name"] == "Widget"
    )[
        "resolver_scope_id"
    ] = "ResolverScopeId:body-root"
    cross_body_hir_local = json.loads(json.dumps(resolver_graph_full))
    next(
        row
        for row in cross_body_hir_local["name_bindings"]
        if row["local_name"] == "input"
    )[
        "hir_body_id_or_null"
    ] = "HirBodyId:other"
    sparse_scope_preorder = json.loads(json.dumps(resolver_graph_full))
    next(
        row
        for row in sparse_scope_preorder["scopes"]
        if row.get("kind") == "BodyLocalScope"
        and row.get("scope_preorder_ordinal") == 1
    )[
        "scope_preorder_ordinal"
    ] = 7
    sparse_binding_order = json.loads(json.dumps(resolver_graph_full))
    next(
        row
        for row in sparse_binding_order["name_bindings"]
        if row["local_name"] == "patternValue"
    )[
        "binding_commit_ordinal_or_null"
    ] = 9
    import_wrong_scope_domain = json.loads(
        json.dumps(resolver_graph_full)
    )
    import_wrong_scope_domain["import_bindings"][0][
        "resolver_scope_id"
    ] = "ResolverScopeId:package-root"
    activation_wrong_scope_domain = json.loads(
        json.dumps(resolver_graph_full)
    )
    activation_wrong_scope_domain["activation_entries"][0][
        "resolver_scope_id"
    ] = "ResolverScopeId:package-root"
    witness_wrong_scope_domain = json.loads(
        json.dumps(resolver_graph_full)
    )
    witness_wrong_scope_domain["witness_visibility_entries"][0][
        "resolver_scope_id"
    ] = "ResolverScopeId:source"
    resolver_unknown_field = json.loads(json.dumps(resolver_graph))
    resolver_unknown_field["not_in_schema"] = True
    resolver_unknown_field["resolver_graph_sha256"] = (
        canonical_self_digest(
            resolver_unknown_field, "resolver_graph_sha256"
        )
    )
    resolver_unknown_nested = json.loads(json.dumps(resolver_graph))
    resolver_unknown_nested["scopes"][0]["not_in_schema"] = True
    resolver_unknown_nested["resolver_graph_sha256"] = (
        canonical_self_digest(
            resolver_unknown_nested, "resolver_graph_sha256"
        )
    )
    resolver_unsorted_rows = json.loads(json.dumps(resolver_graph_full))
    resolver_unsorted_rows["scopes"][0], resolver_unsorted_rows[
        "scopes"
    ][1] = (
        resolver_unsorted_rows["scopes"][1],
        resolver_unsorted_rows["scopes"][0],
    )
    resolver_unsorted_rows["resolver_graph_sha256"] = (
        canonical_self_digest(
            resolver_unsorted_rows, "resolver_graph_sha256"
        )
    )
    resolver_digest_flip = json.loads(json.dumps(resolver_graph))
    resolver_digest_flip["resolver_graph_sha256"] = "f" * 64
    resolver_lone_surrogate = json.loads(json.dumps(resolver_graph))
    resolver_lone_surrogate["invariants"]["lookup"] = "\ud800"
    resolver_mutants = [
        ("RESOLVER_GRAPH_SCHEMA_SHAPE", resolver_unknown_field),
        ("RESOLVER_GRAPH_SCHEMA_SHAPE", resolver_unknown_nested),
        ("RESOLVER_GRAPH_CANONICAL_ORDER", resolver_unsorted_rows),
        ("RESOLVER_GRAPH_DIGEST", resolver_digest_flip),
        (
            "CANONICAL_JSON_NON_UNICODE_SCALAR",
            resolver_lone_surrogate,
        ),
        ("SCOPE_ID_DOMAIN", resolver_wrong_domain),
        ("SCOPE_PARENT_REFERENCE", resolver_dangling_parent),
        ("ROOT_SCOPE_REFERENCE", resolver_empty_roots),
        ("SCOPE_IDENTITY_RECIPE", duplicate_scope_owner),
        ("SCOPE_PARENT_KIND", wrong_scope_parent_kind),
        ("SAME_FRAME_NAME_KEY", resolver_single_then_callable),
        ("SAME_FRAME_NAME_KEY", resolver_callable_then_single),
        ("IMPORT_BINDING_ID", duplicate_import_identity),
        ("IMPORT_IDENTITY_DOMAIN", wrong_import_target_domain),
        ("IMPORT_IDENTITY_DOMAIN", wrong_module_import_target_domain),
        ("ACTIVATION_SCOPE_REFERENCE", dangling_activation),
        ("WITNESS_SCOPE_REFERENCE", dangling_witness),
        ("ACTIVATION_IDENTITY_DOMAIN", wrong_activation_domain),
        ("ACTIVATION_ORIGIN_IDENTITY", reused_activation_origin),
        ("WITNESS_IDENTITY_DOMAIN", wrong_witness_domain),
        ("WITNESS_ENTRY_KEY", duplicate_witness_evidence),
        ("NAME_ENVIRONMENT_SEPARATION", extension_in_name_env),
        ("NAME_ENVIRONMENT_SEPARATION", witness_in_name_env),
        ("IMPORT_ENVIRONMENT_SEPARATION", extension_import_namespace),
        ("NAME_ENVIRONMENT_SEPARATION", early_hir_local),
        ("HIR_LOCAL_ID_REUSE", reused_hir_local),
        ("HIR_LOCAL_SCOPE_DOMAIN", hir_local_outside_body),
        ("LOCAL_FUNCTION_VISIBILITY", local_function_hoist),
        ("ROOT_BODY_SCOPE_IDENTITY", duplicate_root_body),
        ("RESOLVER_INVARIANTS", wrong_lookup),
        ("RESOLVER_INVARIANTS", boolean_counter),
        ("BINDING_SOURCE_ADMISSION", invalid_source_admission),
        ("NAME_ENVIRONMENT_SEPARATION", declaration_wrong_visibility),
        ("BINDING_SCOPE_DOMAIN", declaration_wrong_scope),
        ("HIR_LOCAL_IDENTITY_RECIPE", cross_body_hir_local),
        ("HIR_SCOPE_PREORDER", sparse_scope_preorder),
        ("HIR_LOCAL_COMMIT_ORDER", sparse_binding_order),
        ("IMPORT_SCOPE_DOMAIN", import_wrong_scope_domain),
        ("ACTIVATION_SCOPE_DOMAIN", activation_wrong_scope_domain),
        ("WITNESS_SCOPE_DOMAIN", witness_wrong_scope_domain),
    ]
    resolver_pass = all(
        not r4_resolver_graph_failure_codes(value)
        for value in (resolver_graph, resolver_graph_full)
    )
    resolver_mutants_pass = all(
        expected in r4_resolver_graph_failure_codes(mutant)
        for expected, mutant in resolver_mutants
    )

    def make_stages(failed_index: int | None = None) -> list[dict[str, Any]]:
        rows = [
            {
                "ordinal": index,
                "predicate": predicate,
                "status": "PASS",
            }
            for index, predicate in enumerate(R4_NRM_STAGE_SEQUENCE, 1)
        ]
        if failed_index is not None:
            rows[failed_index]["status"] = "FAIL"
            for row in rows[failed_index + 1:]:
                row["status"] = "NOT_EVALUATED"
        return rows

    def make_seal(
        status: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        fields = (
            "unbound_primary_count",
            "unresolved_count",
            "candidate_set_count",
            "missing_typed_id_count",
            "missing_visibility_proof_count",
            "recovery_binding_count",
            "runtime_relookup_count",
            "overload_winner_count",
            "canonical_hir_overload_set_ref_count",
        )
        if status == "NOT_EVALUATED":
            counters: dict[str, Any] = {field: None for field in fields}
        else:
            counters = {field: 0 for field in fields}
        reason_counter = {
            "UNBOUND_PRIMARY": "unbound_primary_count",
            "UNRESOLVED_COUNT_NONZERO": "unresolved_count",
            "CANDIDATE_SET_COUNT_NONZERO": "candidate_set_count",
            "MISSING_TYPED_ID": "missing_typed_id_count",
            "MISSING_VISIBILITY_PROOF": (
                "missing_visibility_proof_count"
            ),
            "RUNTIME_RELOOKUP_RESIDUE": "runtime_relookup_count",
        }.get(reason)
        if reason_counter is not None:
            counters[reason_counter] = 1
        return {"seal_status": status, "counters": counters}

    def make_success_reference(
        suffix: str,
        namespace: str,
        identity: str,
        *,
        callable_deferred: bool = False,
    ) -> dict[str, Any]:
        result: dict[str, Any]
        if callable_deferred:
            result = {
                "kind": "RESOLVED_OVERLOAD_SET_REF_IN_ANALYSIS_HIR",
                "analysis_hir_overload_set_ref": (
                    f"ResolvedOverloadSetRef:{suffix}"
                ),
                "canonical_hir_projection": False,
                "winner_selected": False,
            }
        else:
            result = {
                "kind": "RESOLVED_NONCALL_REFERENCE",
                "resolved_identity": identity,
                "selected_count": 1,
                "rejection_reason_or_null": None,
            }
        return {
            "source_origin_id": f"SourceOriginId:{suffix}",
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": namespace,
            "source_spelling": suffix,
            "candidate_origin_ids": [identity],
            "visibility_proof_ids": (
                [] if callable_deferred
                else [f"VisibilityProofId:{suffix}"]
            ),
            "activation_origin_id_or_null": None,
            "evidence_origin_id_or_null": None,
            "import_binding_id_or_null": None,
            "stages": make_stages(),
            "result": result,
            "source_span": {"start": 0, "end": len(suffix)},
        }

    successful_references = [
        make_success_reference(
            "a-module", "MODULE", "ModuleId:root.lib"
        ),
        make_success_reference("b-type", "TYPE", "DeclId:Widget"),
        make_success_reference("c-value-decl", "VALUE", "DeclId:value"),
        make_success_reference(
            "d-value-local", "VALUE", "HirLocalId:body.local"
        ),
        make_success_reference(
            "e-callable",
            "CALLABLE_OVERLOAD_SET",
            "DeclId:callable",
            callable_deferred=True,
        ),
    ]
    trace: dict[str, Any] = {
        "schema": "deeplus.resolver-trace/r1",
        "resolver_graph_sha256": resolver_graph_full[
            "resolver_graph_sha256"
        ],
        "references": successful_references,
        "diagnostic_order": (
            "LOWEST_FAILED_STAGE_THEN_EXACT_OWNER_PRIMARY_THEN_"
            "LOWEST_SOURCE_ORIGIN_ID"
        ),
        "diagnostic_selection": {
            "winner_source_origin_id_or_null": None,
            "winner_rejection_reason_or_null": None,
            "suppressed_source_origin_ids": [],
        },
        "seal": make_seal("SEALED"),
        "trace_sha256": zero,
    }
    reseal(trace, "trace_sha256")

    rejected_traces: list[dict[str, Any]] = []
    for failed_index, (_, _, reasons) in enumerate(R4_NRM_PRECEDENCE):
        reason = reasons[0]
        candidate_ids = (
            [] if failed_index <= 4 else ["DeclId:rejected"]
        )
        proof_ids = (
            [] if failed_index <= 5
            else ["VisibilityProofId:rejected"]
        )
        reference = {
            "source_origin_id": (
                f"SourceOriginId:rejected-stage-{failed_index + 1}"
            ),
            "resolver_scope_id": "ResolverScopeId:package-root",
            "namespace": "VALUE",
            "source_spelling": "rejected",
            "candidate_origin_ids": candidate_ids,
            "visibility_proof_ids": proof_ids,
            "activation_origin_id_or_null": None,
            "evidence_origin_id_or_null": None,
            "import_binding_id_or_null": None,
            "stages": make_stages(failed_index),
            "result": {
                "kind": "REJECTED",
                "resolved_ref_or_null": None,
                "selected_count": 0,
                "rejection_reason": reason,
            },
            "source_span": {"start": 0, "end": 8},
        }
        if failed_index < 7:
            seal_status = "NOT_EVALUATED"
        elif failed_index == 7:
            seal_status = "REJECTED_AT_HIR_SEAL"
        else:
            seal_status = "SEALED"
        rejected_value = {
            "schema": "deeplus.resolver-trace/r1",
            "resolver_graph_sha256": resolver_graph_full[
                "resolver_graph_sha256"
            ],
            "references": [reference],
            "diagnostic_order": trace["diagnostic_order"],
            "diagnostic_selection": {
                "winner_source_origin_id_or_null": (
                    reference["source_origin_id"]
                ),
                "winner_rejection_reason_or_null": reason,
                "suppressed_source_origin_ids": [],
            },
            "seal": make_seal(seal_status, reason),
            "trace_sha256": zero,
        }
        reseal(rejected_value, "trace_sha256")
        rejected_traces.append(rejected_value)
    rejected_trace = rejected_traces[2]
    deferred_trace = {
        **trace,
        "references": [
            json.loads(json.dumps(successful_references[-1]))
        ],
    }
    reseal(deferred_trace, "trace_sha256")
    trace_swap = json.loads(json.dumps(trace))
    trace_swap["references"][0]["stages"][0]["predicate"] = (
        "ModuleInterfaceDigestVerified"
    )
    trace_after_fail = json.loads(json.dumps(rejected_trace))
    trace_after_fail["references"][0]["stages"][3]["status"] = "PASS"
    malformed_accepted = json.loads(json.dumps(trace))
    malformed_accepted["references"][0]["result"]["selected_count"] = 0
    malformed_rejected = json.loads(json.dumps(rejected_trace))
    del malformed_rejected["references"][0]["result"]["selected_count"]
    boolean_seal = json.loads(json.dumps(trace))
    boolean_seal["seal"]["counters"]["unresolved_count"] = False
    wrong_rejection_stage = json.loads(json.dumps(rejected_trace))
    wrong_rejection_stage["references"][0]["result"][
        "rejection_reason"
    ] = "PACKAGE_CYCLE"
    wrong_diagnostic_order = json.loads(json.dumps(trace))
    wrong_diagnostic_order["diagnostic_order"] = "SOURCE_ORDER"
    wrong_diagnostic_selection = json.loads(json.dumps(rejected_trace))
    wrong_diagnostic_selection["diagnostic_selection"][
        "winner_rejection_reason_or_null"
    ] = "PACKAGE_CYCLE"
    missing_reference_field = json.loads(json.dumps(trace))
    del missing_reference_field["references"][0]["source_origin_id"]
    activated_deferred_winner = json.loads(json.dumps(deferred_trace))
    activated_deferred_winner["references"][0]["result"][
        "winner_selected"
    ] = True
    wrong_accepted_domain = json.loads(json.dumps(trace))
    wrong_accepted_domain["references"][0]["result"][
        "resolved_identity"
    ] = "DeclId:not-a-module"
    wrong_deferred_domain = json.loads(json.dumps(deferred_trace))
    wrong_deferred_domain["references"][0]["result"][
        "analysis_hir_overload_set_ref"
    ] = "OverloadSetRef:not-canonical"
    wrong_optional_origin_domain = json.loads(json.dumps(trace))
    wrong_optional_origin_domain["references"][0][
        "activation_origin_id_or_null"
    ] = "ModuleId:not-an-activation-origin"
    empty_accepted_candidates = json.loads(json.dumps(trace))
    empty_accepted_candidates["references"][0]["candidate_origin_ids"] = []
    empty_accepted_proofs = json.loads(json.dumps(trace))
    empty_accepted_proofs["references"][0]["visibility_proof_ids"] = []
    unbound_import_candidate = json.loads(json.dumps(trace))
    unbound_import_candidate["references"][0][
        "import_binding_id_or_null"
    ] = "ImportBindingId:value"
    unsorted_references = json.loads(json.dumps(trace))
    unsorted_references["references"][0], unsorted_references[
        "references"
    ][1] = (
        unsorted_references["references"][1],
        unsorted_references["references"][0],
    )
    reseal(unsorted_references, "trace_sha256")
    unsorted_candidates = json.loads(json.dumps(deferred_trace))
    unsorted_candidates["references"][0]["candidate_origin_ids"] = [
        "DeclId:z",
        "DeclId:a",
    ]
    wrong_seal_counter_binding = json.loads(
        json.dumps(rejected_traces[7])
    )
    wrong_seal_counter_binding["seal"]["counters"][
        "unbound_primary_count"
    ] = 0
    trace_unknown_field = json.loads(json.dumps(trace))
    trace_unknown_field["not_in_schema"] = True
    reseal(trace_unknown_field, "trace_sha256")
    trace_unknown_nested = json.loads(json.dumps(trace))
    trace_unknown_nested["references"][0]["not_in_schema"] = True
    reseal(trace_unknown_nested, "trace_sha256")
    trace_digest_flip = json.loads(json.dumps(trace))
    trace_digest_flip["trace_sha256"] = "f" * 64
    trace_lone_surrogate = json.loads(json.dumps(trace))
    trace_lone_surrogate["references"][0][
        "source_spelling"
    ] = "\ud800"
    trace_mutants = [
        ("RESOLVER_TRACE_SCHEMA_SHAPE", trace_unknown_field),
        ("RESOLVER_TRACE_SCHEMA_SHAPE", trace_unknown_nested),
        ("RESOLVER_TRACE_DIGEST", trace_digest_flip),
        ("CANONICAL_JSON_NON_UNICODE_SCALAR", trace_lone_surrogate),
        ("STAGE_SEQUENCE", trace_swap),
        ("FAILURE_ORDER", trace_after_fail),
        ("ACCEPTED_RESULT", malformed_accepted),
        ("REJECTED_RESULT", malformed_rejected),
        ("HIR_SEAL", boolean_seal),
        ("REJECTION_REASON_STAGE", wrong_rejection_stage),
        ("DIAGNOSTIC_ORDER", wrong_diagnostic_order),
        ("DIAGNOSTIC_SELECTION", wrong_diagnostic_selection),
        ("REFERENCE_SHAPE", missing_reference_field),
        ("ACCEPTED_RESULT", activated_deferred_winner),
        ("ACCEPTED_RESULT", wrong_accepted_domain),
        ("ACCEPTED_RESULT", wrong_deferred_domain),
        ("REFERENCE_DOMAIN", wrong_optional_origin_domain),
        ("ACCEPTED_CANDIDATE_EVIDENCE", empty_accepted_candidates),
        ("ACCEPTED_CANDIDATE_EVIDENCE", empty_accepted_proofs),
        ("REFERENCE_ORIGIN_LINKAGE", unbound_import_candidate),
        ("REFERENCE_ORDER", unsorted_references),
        ("REFERENCE_DOMAIN", unsorted_candidates),
        ("HIR_SEAL_COUNTER_BINDING", wrong_seal_counter_binding),
    ]
    trace_pass = all(
        not r4_resolver_trace_failure_codes(value)
        for value in [trace, deferred_trace, *rejected_traces]
    )
    trace_mutants_pass = all(
        expected in r4_resolver_trace_failure_codes(mutant)
        for expected, mutant in trace_mutants
    )
    return [
        (
            source_role_pass and source_role_mutants_pass,
            "R4_NRM_SOURCE_ROLE_CARRIER_VALIDATOR_SELF_TEST",
            (
                f"baseline={source_role_pass} "
                f"mutants={len(source_role_mutants)} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            package_pass
            and package_mutants_pass
            and iterative_graph_pass
            and canonical_unicode_vector_pass
            and canonical_invalid_domain_pass,
            "R4_NRM_GRAPH_VALIDATOR_SELF_TEST",
            (
                f"baseline={package_pass} "
                f"mutants={len(package_mutants)} "
                f"iterative_deep_dag={iterative_graph_pass} "
                f"canonical_unicode={canonical_unicode_vector_pass} "
                f"canonical_invalid_domain={canonical_invalid_domain_pass} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            initialization_pass and initialization_mutants_pass,
            "R4_NRM_INITIALIZATION_VALIDATOR_SELF_TEST",
            (
                f"baseline={initialization_pass} "
                f"mutants={len(initialization_mutants)} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            receipt_pass and receipt_mutants_pass,
            "R4_NRM_DEPENDENCY_RECEIPT_VALIDATOR_SELF_TEST",
            (
                f"baseline={receipt_pass} "
                f"mutants={len(receipt_mutants)} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            visibility_pass and visibility_mutants_pass,
            "R4_NRM_VISIBILITY_CLOSURE_VALIDATOR_SELF_TEST",
            (
                f"baseline={visibility_pass} "
                f"mutants={len(visibility_mutants)} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            module_artifact_pass
            and module_artifact_mutants_pass
            and module_artifact_private_change_pass,
            "R4_NRM_MODULE_ARTIFACT_RELATIONAL_SELF_TEST",
            (
                f"baseline={module_artifact_pass} "
                "mutants=6 "
                f"private_change_matrix={module_artifact_private_change_pass} "
                "hash_domains=interface,implementation,compilation "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            resolver_pass and resolver_mutants_pass,
            "R4_NRM_RESOLVER_VALIDATOR_SELF_TEST",
            (
                f"baseline={resolver_pass} "
                f"mutants={len(resolver_mutants)} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            trace_pass and trace_mutants_pass,
            "R4_NRM_TRACE_VALIDATOR_SELF_TEST",
            (
                f"baselines={11 if trace_pass else 0}/11 "
                f"mutants={len(trace_mutants)} "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
        (
            True,
            "R4_NRM_MECHANICAL_EVIDENCE_BOUNDARY",
            (
                "scope=SYNTHETIC_HELPER_SELF_TEST "
                "repository_instance_execution=NOT_RUN "
                "evidence=E2 product=15/15_NOT_RUN"
            ),
        ),
    ]


def r4_nrm_integrated_contract_results(
    root: Path,
) -> list[tuple[bool, str, str]]:
    """Validate R4 integrated oracles and mechanical schema closure."""

    results: list[tuple[bool, str, str]] = []
    documents: dict[str, dict[str, Any]] = {}

    def record(condition: bool, code: str, detail: str) -> None:
        results.append((bool(condition), code, detail))

    for relative in R4_NRM_INTEGRATED_PATHS:
        try:
            value = json.loads((root / relative).read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("expected a JSON object")
            documents[relative] = value
            record(True, "R4_NRM_INTEGRATED_JSON", relative)
        except Exception as exc:  # noqa: BLE001
            documents[relative] = {}
            record(False, "R4_NRM_INTEGRATED_JSON", f"{relative}: {exc}")

    contract = documents[
        "spec/contracts/name-resolution-modules-current.json"
    ]
    fixture = documents[
        "tests/fixtures/current/name-resolution-modules-current-r1.json"
    ]
    fixture_schema = documents[
        "schemas/language/name-resolution-modules-current-fixtures.schema.json"
    ]

    open_feature_p1 = contract.get("open_feature_p1", {})
    observed_open_p1 = [
        item
        for key in (
            "class",
            "enumeration",
            "trait_conformance",
            "static_first_dynamic",
        )
        for item in open_feature_p1.get(key, [])
    ]
    record(
        contract.get("semantic_p0") == 0
        and open_feature_p1.get("total") == 22
        and observed_open_p1
        == SUCCESSOR_ACTION_IDS[len(EXPECTED_ACTION_IDS):]
        and contract.get("product_lanes") == "15/15_NOT_RUN"
        and contract.get("source_activation") == "none"
        and contract.get("current_binding") is False,
        "R4_NRM_STATE_FENCE",
        (
            f"semantic_p0={contract.get('semantic_p0')} "
            f"open_p1={open_feature_p1.get('total')} "
            f"product={contract.get('product_lanes')}"
        ),
    )

    graph_families = contract.get("graph_families", {})
    module_header = graph_families.get("module_header_import", {})
    static_graph = graph_families.get(
        "static_binding_value_dependency", {}
    )
    record(
        graph_families.get("package_dependency")
        == {
            "profile": "ACYCLIC",
            "self_loop": "REJECT",
            "nontrivial_scc": "REJECT",
        }
        and module_header.get("profile")
        == "HEADER_ONLY_SCC_ALLOWED_AFTER_COMPLETE_HEADER_COLLECTION"
        and module_header.get("admitted_scc_edges")
        == [
            "module_header_reference",
            "type_declaration_reference",
            "signature_reference",
        ]
        and module_header.get("forbidden_scc_edges")
        == [
            "static_value_dependency",
            "runtime_initializer_dependency",
            "reexport_dependency",
        ]
        and module_header.get("semantic_order_winner") is False
        and graph_families.get("reexport")
        == {
            "profile": "ACYCLIC",
            "self_loop": "REJECT",
            "nontrivial_scc": "REJECT",
        }
        and static_graph.get("profile")
        == "ACYCLIC_COMPILE_TIME_EVALUATION_ZERO_RUNTIME_INIT"
        and static_graph.get("self_loop") == "REJECT"
        and static_graph.get("nontrivial_scc") == "REJECT"
        and static_graph.get("commit")
        == "ONE_ATOMIC_COMMIT_AFTER_ALL_VALUES_SUCCEED"
        and static_graph.get("runtime_initializer_count") == 0
        and static_graph.get("semantic_order_winner") is False,
        "R4_NRM_GRAPH_CONTRACT",
        f"families={sorted(graph_families)}",
    )
    initialization_schema = documents[
        "schemas/language/module-initialization-plan.schema.json"
    ]
    initialization_binding_schema = (
        initialization_schema.get("$defs", {}).get("binding", {})
    )
    initialization_binding_properties = (
        initialization_binding_schema.get("properties", {})
    )
    record(
        set(initialization_binding_schema.get("required", []))
        == {
            "binding_decl_id",
            "dependency_decl_ids",
            "value_sha256",
            "evaluation_status",
        }
        and initialization_binding_properties.get(
            "binding_decl_id", {}
        ).get("$ref")
        == "#/$defs/declId"
        and initialization_binding_properties.get(
            "dependency_decl_ids", {}
        ).get("items", {}).get("$ref")
        == "#/$defs/declId"
        and initialization_schema.get("properties", {})
        .get("evaluation_order", {})
        .get("const")
        == "TOPOLOGICAL_THEN_CANONICAL_DECL_ID"
        and initialization_schema.get("properties", {})
        .get("receipt_order", {})
        .get("const")
        == "CANONICAL_DECL_ID_ORDER"
        and static_graph.get("receipt_order")
        == "CANONICAL_DECL_ID_ORDER",
        "R4_NRM_INITIALIZATION_SCHEMA_CLOSURE",
        (
            "identity=DeclId order=CANONICAL_DECL_ID_ORDER "
            "product=15/15_NOT_RUN"
        ),
    )

    lexical = contract.get("lexical_resolution", {})
    environments = contract.get("environment_separation", {})
    record(
        lexical.get("lookup_order")
        == "INNERMOST_NAME_ENV_TO_OUTERMOST_NAME_ENV"
        and lexical.get("stop_rule")
        == "STOP_AT_FIRST_NONEMPTY_FRAME_FOR_EXACT_NAMESPACE_AND_SPELLING"
        and lexical.get("same_frame_declaration_order_priority") is False
        and lexical.get("cross_frame_overload_merge") is False
        and lexical.get("match_probe")
        == "PROVISIONAL_BINDINGS_NEVER_ENTER_NAME_ENV"
        and lexical.get("match_commit") == "CREATE_FRESH_HIR_LOCAL_IDS"
        and lexical.get("failed_pattern") == "NO_COMMITTED_BINDING"
        and environments.get("cross_environment_creation_count") == 0
        and environments.get(
            "nested_use_order_or_depth_is_extension_winner"
        )
        is False,
        "R4_NRM_RESOLVER_CONTRACT",
        (
            f"lookup={lexical.get('lookup_order')} "
            f"cross_env={environments.get('cross_environment_creation_count')}"
        ),
    )

    oracles = contract.get("acceptance_oracles", [])
    oracle_ids = [
        row.get("test_id") for row in oracles if isinstance(row, dict)
    ]
    record(
        len(oracles) == 36
        and oracle_ids == list(R4_NRM_ACCEPTANCE_TEST_IDS)
        and len(set(oracle_ids)) == 36,
        "R4_NRM_ACCEPTANCE_TEST_IDS",
        f"count={len(oracles)} ids={oracle_ids}",
    )
    record(
        canonical_sha(oracles) == R4_NRM_ACCEPTANCE_ORACLE_SHA256,
        "R4_NRM_ACCEPTANCE_ORACLE_IDENTITY",
        f"sha256={canonical_sha(oracles)}",
    )

    cases = fixture.get("cases", [])
    case_ids = [
        row.get("acceptance_test_id")
        for row in cases
        if isinstance(row, dict)
    ]
    record(
        len(cases) == 36
        and case_ids == list(R4_NRM_ACCEPTANCE_TEST_IDS)
        and len(set(case_ids)) == 36,
        "R4_NRM_INTEGRATED_CASE_COUNT",
        f"count={len(cases)} ids={len(set(case_ids))}",
    )
    expected_gap_kind = [
        (
            gap_id,
            kind,
        )
        for gap_id in R4_NRM_GAP_IDS
        for kind in ("positive", "boundary", "negative")
    ]
    observed_gap_kind = [
        (row.get("gap_id"), row.get("kind"))
        for row in cases
        if isinstance(row, dict)
    ]
    record(
        observed_gap_kind == expected_gap_kind
        and len(set(observed_gap_kind)) == 36,
        "R4_NRM_GAP_KIND_COVERAGE",
        f"rows={len(observed_gap_kind)}",
    )

    oracle_binding = len(oracles) == len(cases) == 36
    artifact_refs_closed = True
    invariant_zero = True
    for oracle, case in zip(oracles, cases):
        if not isinstance(oracle, dict) or not isinstance(case, dict):
            oracle_binding = False
            continue
        expected = case.get("expected", {})
        case_input = case.get("input", {})
        oracle_binding = oracle_binding and (
            case.get("acceptance_test_id") == oracle.get("test_id")
            and [case.get("gap_id")] == oracle.get("gap_ids")
            and case.get("kind") == oracle.get("test_class")
            and case.get("scenario") == oracle.get("scenario")
            and case_input.get("description") == oracle.get("scenario")
            and expected.get("outcome")
            == oracle.get("expected_outcome")
            and expected.get("primary_diagnostic_or_null")
            == oracle.get("primary_diagnostic_or_null")
            and expected.get("primary_reason_or_null")
            == oracle.get("primary_reason_or_null")
            and expected.get("suppressed_diagnostics")
            == oracle.get("suppressed_diagnostics")
        )
        references = case_input.get("artifact_refs", [])
        expected_references = R4_NRM_ACCEPTANCE_ARTIFACT_REFS.get(
            (case.get("gap_id"), case.get("kind"))
        )
        artifact_refs_closed = artifact_refs_closed and (
            isinstance(references, list)
            and bool(references)
            and len(references) == len(set(references))
            and tuple(references) == expected_references
            and all(
                isinstance(relative, str)
                and not relative.startswith(("candidate/", "/"))
                and (root / relative).is_file()
                for relative in references
            )
        )
        invariants = expected.get("invariants", {})
        invariant_zero = invariant_zero and (
            isinstance(invariants, dict)
            and invariants
            and set(invariants.values()) == {0}
        )
    record(
        oracle_binding,
        "R4_NRM_ACCEPTANCE_ORACLE_BINDING",
        (
            f"statically_bound={len(oracles)}/36 "
            f"cases={len(cases)}/36 executed=0/36"
        ),
    )
    record(
        artifact_refs_closed,
        "R4_NRM_ORACLE_ARTIFACT_REFS",
        f"cases={len(cases)}",
    )
    record(
        invariant_zero,
        "R4_NRM_INVARIANT_ZERO",
        f"cases={len(cases)}",
    )
    record(
        fixture.get("semantic_p0") == 0
        and fixture.get("open_feature_p1") == 22
        and fixture.get("product_lanes") == "15/15_NOT_RUN",
        "R4_NRM_INTEGRATED_PRODUCT_NOT_RUN",
        (
            f"p0={fixture.get('semantic_p0')} "
            f"p1={fixture.get('open_feature_p1')} "
            f"product={fixture.get('product_lanes')}"
        ),
    )

    case_array_schema = (
        fixture_schema.get("properties", {}).get("cases", {})
    )
    case_id_schema = (
        fixture_schema.get("$defs", {})
        .get("case", {})
        .get("properties", {})
        .get("acceptance_test_id", {})
    )
    record(
        case_array_schema.get("minItems") == 36
        and case_array_schema.get("maxItems") == 36
        and case_id_schema.get("enum")
        == list(R4_NRM_ACCEPTANCE_TEST_IDS),
        "R4_NRM_INTEGRATED_SCHEMA_CARDINALITY",
        (
            f"min={case_array_schema.get('minItems')} "
            f"max={case_array_schema.get('maxItems')}"
        ),
    )

    domain_schema_paths = (
        "schemas/language/package-module-source-graph.schema.json",
        "schemas/language/module-compilation-dependency-receipt.schema.json",
        "schemas/language/module-initialization-plan.schema.json",
        "schemas/language/module-visibility-closure.schema.json",
        "schemas/language/resolver-graph.schema.json",
        "schemas/language/resolver-trace.schema.json",
    )
    generic_typed_id_pattern = r"^[A-Za-z][A-Za-z0-9]*:[^\s]+$"
    generic_typed_id_uses = {
        relative: scalar_occurrences(
            documents[relative], generic_typed_id_pattern
        )
        for relative in domain_schema_paths
    }
    record(
        all(count == 0 for count in generic_typed_id_uses.values())
        and all(
            "typedId" not in documents[relative].get("$defs", {})
            for relative in domain_schema_paths
        ),
        "R4_NRM_TYPED_ID_DOMAINS",
        f"generic_uses={generic_typed_id_uses}",
    )

    package_schema = documents[
        "schemas/language/package-module-source-graph.schema.json"
    ]
    package_properties = package_schema.get("properties", {})
    record(
        all(
            package_properties.get(name, {}).get("minItems") == 1
            for name in ("packages", "targets", "source_contributions")
        )
        and set(package_schema.get("$defs", {}))
        >= {
            "packageId",
            "targetId",
            "sourceFileId",
            "moduleId",
            "dependencyBindingId",
            "sourceOriginId",
        },
        "R4_NRM_GRAPH_SCHEMA_CLOSURE",
        (
            "required nonempty owner sets and domain-specific "
            "identity definitions"
        ),
    )

    resolver_trace_schema = documents[
        "schemas/language/resolver-trace.schema.json"
    ]
    stage_array = (
        resolver_trace_schema.get("$defs", {})
        .get("referenceTrace", {})
        .get("properties", {})
        .get("stages", {})
    )
    prefix_items = stage_array.get("prefixItems", [])
    observed_stage_ordinals = [
        nested_property_consts(item, "ordinal")
        for item in prefix_items
    ]
    observed_stage_predicates = [
        nested_property_consts(item, "predicate")
        for item in prefix_items
    ]
    record(
        stage_array.get("minItems") == 9
        and stage_array.get("maxItems") == 9
        and stage_array.get("items") is False
        and observed_stage_ordinals == [[index] for index in range(1, 10)]
        and observed_stage_predicates
        == [[predicate] for predicate in R4_NRM_STAGE_SEQUENCE],
        "R4_NRM_TRACE_STAGE_SCHEMA",
        (
            f"items={len(prefix_items)} "
            f"ordinals={observed_stage_ordinals}"
        ),
    )

    module_api_schema = documents[
        "schemas/language/module-api-digest.schema.json"
    ]
    module_api_profile = (
        module_api_schema.get("properties", {}).get("interface_profile", {})
    )
    r4_envelope_required = any(
        "r4_interface_envelope"
        in clause.get("then", {}).get("required", [])
        and "R4_NAME_RESOLUTION_MODULES"
        in nested_property_consts(clause.get("if", {}), "interface_profile")
        for clause in module_api_schema.get("allOf", [])
        if isinstance(clause, dict)
    )
    r4_envelope_forbidden_else = any(
        "r4_interface_envelope"
        in clause.get("else", {}).get("not", {}).get("required", [])
        and "R4_NAME_RESOLUTION_MODULES"
        in nested_property_consts(clause.get("if", {}), "interface_profile")
        for clause in module_api_schema.get("allOf", [])
        if isinstance(clause, dict)
    )
    r4_module_id_pattern = next(
        (
            clause.get("then", {})
            .get("properties", {})
            .get("module_id", {})
            .get("pattern")
            for clause in module_api_schema.get("allOf", [])
            if isinstance(clause, dict)
            and "R4_NAME_RESOLUTION_MODULES"
            in nested_property_consts(
                clause.get("if", {}), "interface_profile"
            )
        ),
        None,
    )
    r4_envelope_schema = (
        module_api_schema.get("$defs", {})
        .get("r4ModuleInterfaceEnvelope", {})
    )
    r4_envelope_fields = set(r4_envelope_schema.get("required", []))
    r4_export_schema = (
        module_api_schema.get("$defs", {}).get("r4PublicExportRow", {})
    )
    r4_export_properties = r4_export_schema.get("properties", {})
    r4_export_target_pattern = r4_export_properties.get(
        "referenced_identity_id", {}
    ).get("pattern")
    r4_export_namespace_domain = r4_export_properties.get(
        "namespace", {}
    ).get("enum")
    r4_export_module_target_pattern = None
    r4_export_decl_target_pattern = None
    for clause in r4_export_schema.get("allOf", []):
        if (
            nested_property_consts(clause.get("if", {}), "namespace")
            == ["MODULE"]
        ):
            r4_export_module_target_pattern = (
                clause.get("then", {})
                .get("properties", {})
                .get("referenced_identity_id", {})
                .get("pattern")
            )
            r4_export_decl_target_pattern = (
                clause.get("else", {})
                .get("properties", {})
                .get("referenced_identity_id", {})
                .get("pattern")
            )
    receipt_schema = documents[
        "schemas/language/module-compilation-dependency-receipt.schema.json"
    ]
    provider_resolver_schema = documents[
        "schemas/language/resolver-graph.schema.json"
    ]
    required_interface = (
        receipt_schema.get("$defs", {}).get("requiredInterface", {})
    )
    required_interface_fields = set(required_interface.get("required", []))
    required_profile_consts = nested_property_consts(
        required_interface, "interface_profile"
    )
    resolver_import_provider_fields = set(
        provider_resolver_schema.get("$defs", {})
        .get("importBinding", {})
        .get("required", [])
    )
    resolver_activation_provider_fields = set(
        provider_resolver_schema.get("$defs", {})
        .get("activationEntry", {})
        .get("required", [])
    )
    receipt_import_provider_fields = set(
        receipt_schema.get("$defs", {})
        .get("importBinding", {})
        .get("required", [])
    )
    receipt_activation_provider_fields = set(
        receipt_schema.get("$defs", {})
        .get("activationBinding", {})
        .get("required", [])
    )
    resolver_provider_contract = provider_resolver_schema.get(
        "x-deeplus-provider-provenance-contract", {}
    )
    receipt_provider_contract = receipt_schema.get(
        "x-deeplus-provider-provenance-contract", {}
    )
    record(
        set(module_api_profile.get("enum", []))
        >= {"LEGACY_R51F3", "R4_NAME_RESOLUTION_MODULES"}
        and r4_envelope_required
        and r4_module_id_pattern == "^ModuleId:[^\\s]+$"
        and r4_envelope_fields
        == {
            "activation_profile",
            "public_export_rows",
            "public_activation_reexport_rows",
            "opaque_facade_rows",
            "signature_relation",
            "opaque_facade_relation",
            "symbols_are_exact_effective_public_residue",
            "private_body_bytes_in_interface_hash",
        }
        and {
            "provider_binding_id_or_self",
            "provider_module_id",
            "interface_profile",
            "interface_sha256",
        }
        == required_interface_fields
        and required_profile_consts == ["R4_NAME_RESOLUTION_MODULES"],
        "R4_NRM_INTERFACE_ENVELOPE",
        (
            f"profile={module_api_profile.get('enum')} "
            f"module_id={r4_module_id_pattern} "
            f"envelope_required={sorted(r4_envelope_fields)} "
            f"receipt_required={sorted(required_interface_fields)}"
        ),
    )
    record(
        r4_envelope_forbidden_else,
        "R4_NRM_INTERFACE_PROFILE_EXCLUSIVITY",
        (
            "R4 requires the envelope; legacy or absent profile "
            "forbids it"
        ),
    )
    record(
        module_api_profile.get("enum")
        == [
            "LEGACY_R51F3",
            "R4_NAME_RESOLUTION_MODULES",
            "R41_ACTOR_PROTOCOL_BINDINGS",
        ],
        "R4_NRM_INTERFACE_PROFILE_DOMAIN",
        f"profile={module_api_profile.get('enum')}",
    )
    provider_fields = {
        "provider_binding_id_or_self",
        "provider_module_id",
    }
    record(
        provider_fields <= resolver_import_provider_fields
        and provider_fields <= resolver_activation_provider_fields
        and provider_fields <= receipt_import_provider_fields
        and provider_fields <= receipt_activation_provider_fields
        and resolver_provider_contract.get("self_meaning")
        == "PROVIDER_PACKAGE_EQUALS_CONSUMER_PACKAGE"
        and receipt_provider_contract.get("self_meaning")
        == "PROVIDER_PACKAGE_EQUALS_CONSUMER_PACKAGE"
        and receipt_provider_contract.get(
            "required_interface_relation"
        )
        == "EXACT_SET_NO_MISSING_OR_EXTRA_PAIR"
        and receipt_provider_contract.get(
            "required_interface_exclusion"
        )
        == "ONLY_PROVIDER_MODULE_ID_EQUAL_TO_CONSUMER_MODULE_ID",
        "R4_NRM_PROVIDER_PROVENANCE_CONTRACT",
        (
            "resolver/receipt import+activation provider pair required; "
            "self=same-package; exact external module interface set"
        ),
    )
    record(
        r4_export_namespace_domain
        == ["MODULE", "TYPE", "VALUE", "CALLABLE_OVERLOAD_SET"]
        and r4_export_target_pattern == "^(?:ModuleId|DeclId):[^\\s]+$"
        and r4_export_module_target_pattern == "^ModuleId:[^\\s]+$"
        and r4_export_decl_target_pattern == "^DeclId:[^\\s]+$",
        "R4_NRM_EXPORT_ID_DOMAINS",
        (
            f"namespaces={r4_export_namespace_domain} "
            f"target={r4_export_target_pattern} "
            f"module={r4_export_module_target_pattern} "
            f"declaration={r4_export_decl_target_pattern}"
        ),
    )

    r4_interface_contract = module_api_schema.get(
        "x-deeplus-r4-module-interface-contract", {}
    )
    excluded_interface_inputs = set(
        r4_interface_contract.get("excluded_identity_inputs", [])
    )
    module_implementation_schema = documents[
        "schemas/language/module-implementation-digest.schema.json"
    ]
    module_source_projection_schema = documents[
        "schemas/language/module-source-contribution-projection.schema.json"
    ]
    module_compilation_schema = documents[
        "schemas/language/module-compilation-receipt.schema.json"
    ]
    implementation_required = set(
        module_implementation_schema.get("required", [])
    )
    source_projection_required = set(
        module_source_projection_schema.get("required", [])
    )
    compilation_required = set(
        module_compilation_schema.get("required", [])
    )
    compilation_bindings = module_compilation_schema.get(
        "x-deeplus-artifact-bindings", {}
    )
    canonical_algorithm_ids = {
        module_api_schema.get(
            "x-deeplus-canonical-byte-algorithm", {}
        ).get("algorithm_id"),
        receipt_schema.get(
            "x-deeplus-digest-canonicalization", {}
        ).get("algorithm"),
        module_implementation_schema.get(
            "x-deeplus-digest-canonicalization", {}
        ).get("algorithm"),
        module_source_projection_schema.get(
            "x-deeplus-digest-canonicalization", {}
        ).get("algorithm"),
        module_compilation_schema.get(
            "x-deeplus-digest-canonicalization", {}
        ).get("algorithm"),
        documents[
            "schemas/language/module-initialization-plan.schema.json"
        ].get("x-deeplus-digest-canonicalization", {}).get("algorithm"),
        documents[
            "schemas/language/module-visibility-closure.schema.json"
        ].get("x-deeplus-digest-canonicalization", {}).get("algorithm"),
        documents[
            "schemas/language/package-module-source-graph.schema.json"
        ].get("x-deeplus-digest-canonicalization", {}).get("algorithm"),
        documents[
            "schemas/language/resolver-graph.schema.json"
        ].get("x-deeplus-digest-canonicalization", {}).get("algorithm"),
        documents[
            "schemas/language/resolver-trace.schema.json"
        ].get("x-deeplus-digest-canonicalization", {}).get("algorithm"),
    }
    canonical_self_hash_fields = {
        path: documents[path].get(
            "x-deeplus-digest-canonicalization", {}
        ).get("self_hash_field_excluded")
        for path in (
            "schemas/language/package-module-source-graph.schema.json",
            "schemas/language/resolver-graph.schema.json",
            "schemas/language/resolver-trace.schema.json",
        )
    }
    canonical_array_order_declarations = {
        path: documents[path].get(
            "x-deeplus-digest-canonicalization", {}
        ).get("array_order", {})
        for path in canonical_self_hash_fields
    }
    record(
        {
            "SourceFileId",
            "source_path",
            "SourceOriginId",
            "ActivationOriginId",
            "VisibilityProofId",
            "visibility_closure_sha256",
            "dependency_receipt_sha256",
            "private_hir_or_body_bytes",
            "debug_spans",
        }
        <= excluded_interface_inputs
        and r4_interface_contract.get("interface_sha256")
        == "TOP_LEVEL_CANONICAL_SHA256"
        and r4_interface_contract.get("semantic_comparison")
        == (
            "EXACT_PUBLIC_SEMANTIC_RESIDUE_EXCLUDING_PROVENANCE_BUILD_"
            "AND_PRIVATE_IMPLEMENTATION"
        )
        and {
            "schema",
            "interface_profile",
            "target_id",
            "target_kind",
            "module_id",
            "interface_sha256",
            "hir_semantic_sha256",
            "external_compatibility_identity",
            "implementation_sha256",
        }
        == implementation_required
        and {
            "schema",
            "target_id",
            "module_id",
            "source_contributions",
            "projection_sha256",
        }
        == source_projection_required
        and {
            "schema",
            "profile",
            "target_id",
            "target_kind",
            "module_id",
            "package_graph_sha256",
            "module_source_contribution_sha256",
            "dependency_receipt_sha256",
            "resolver_trace_sha256",
            "visibility_closure_sha256",
            "initialization_plan_sha256",
            "interface_sha256",
            "implementation_sha256",
            "compilation_receipt_sha256",
        }
        == compilation_required
        and set(compilation_bindings)
        == {
            "package_graph_sha256",
            "module_source_contribution_sha256",
            "dependency_receipt_sha256",
            "resolver_trace_sha256",
            "visibility_closure_sha256",
            "initialization_plan_sha256",
            "interface_sha256",
            "actor_protocol_binding_tables_sha256",
            "implementation_sha256",
        }
        and canonical_algorithm_ids
        == {"DEEPLUS_CANONICAL_JSON_UTF8_SHA256_V1"}
        and canonical_self_hash_fields
        == {
            "schemas/language/package-module-source-graph.schema.json":
                "canonical_graph_sha256",
            "schemas/language/resolver-graph.schema.json":
                "resolver_graph_sha256",
            "schemas/language/resolver-trace.schema.json":
                "trace_sha256",
        }
        and all(canonical_array_order_declarations.values()),
        "R4_NRM_MODULE_ARTIFACT_HASH_DOMAINS",
        (
            f"interface_exclusions={len(excluded_interface_inputs)} "
            f"implementation_fields={len(implementation_required)} "
            f"source_fields={len(source_projection_required)} "
            f"receipt_fields={len(compilation_required)} "
            f"bindings={sorted(compilation_bindings)} "
            f"canonical_algorithms={sorted(canonical_algorithm_ids)}"
        ),
    )

    visibility_schema = documents[
        "schemas/language/module-visibility-closure.schema.json"
    ]
    top_level_visibility_schema = documents[
        "schemas/language/top-level-type-visibility-descriptor.schema.json"
    ]
    visibility_domain = (
        visibility_schema.get("$defs", {})
        .get("visibility", {})
        .get("enum")
    )
    explicit_visibility_domain = (
        top_level_visibility_schema.get("properties", {})
        .get("explicit_visibility", {})
        .get("oneOf", [{}])[0]
        .get("enum")
    )
    dependency_visibility_domain = (
        top_level_visibility_schema.get("properties", {})
        .get("api_dependency_visibilities", {})
        .get("items", {})
        .get("enum")
    )
    common_boundary_case = next(
        (
            case
            for case in cases
            if case.get("id") == "IR-R4-MOD045-BOUND"
        ),
        {},
    )
    record(
        visibility_domain == ["private", "common", "public"]
        and visibility_domain == explicit_visibility_domain
        and visibility_domain == dependency_visibility_domain
        and "common" in str(common_boundary_case.get("scenario", ""))
        and common_boundary_case.get("expected", {}).get("outcome")
        == "ACCEPT_COMMON_INTERNAL_ONLY",
        "R4_NRM_VISIBILITY_VOCABULARY",
        (
            f"closure={visibility_domain} "
            f"descriptor={explicit_visibility_domain} "
            f"dependency={dependency_visibility_domain}"
        ),
    )
    visibility_predicates = json.loads(
        (
            root / "spec/types/predicates/chunks/part-0015.json"
        ).read_text(encoding="utf-8")
    )
    visibility_predicate = next(
        (
            row
            for row in visibility_predicates
            if row.get("predicate_id") == "TopLevelTypeVisibilityAdmitted"
        ),
        {},
    )
    visibility_fixture_rows = json.loads(
        (
            root
            / "tests/conformance/checker-predicates/chunks/part-0026.json"
        ).read_text(encoding="utf-8")
    )
    visibility_fixtures = {
        row.get("fixture_id"): row
        for row in visibility_fixture_rows
        if row.get("predicate_id") == "TopLevelTypeVisibilityAdmitted"
    }
    visibility_required = set(top_level_visibility_schema.get("required", []))
    expected_visibility_required = {
        "schema",
        "source_root",
        "declaration_kind",
        "type_producing_owner",
        "explicit_visibility",
        "module_identity",
        "package_identity",
        "source_contribution_id",
        "external_export_or_module_interface_admitted",
        "api_dependency_visibilities",
        "module_visibility_closure_sha256",
        "visibility_proof_ids",
    }
    visibility_axes = set(visibility_predicate.get("descriptor_axes", []))
    visibility_descriptor_rows = [
        row.get("descriptor", {}) for row in visibility_fixtures.values()
    ]
    visibility_semantic_failures = {
        fixture_id: r4_top_level_visibility_failure_codes(
            row.get("descriptor", {})
        )
        for fixture_id, row in visibility_fixtures.items()
    }
    visibility_descriptor_fields_ok = all(
        set(descriptor) == expected_visibility_required
        and is_typed_id(descriptor.get("module_identity"), "ModuleId")
        and is_typed_id(descriptor.get("package_identity"), "PackageId")
        and is_typed_id(
            descriptor.get("source_contribution_id"), "SourceFileId"
        )
        and re.fullmatch(
            r"[0-9a-f]{64}",
            str(descriptor.get("module_visibility_closure_sha256", "")),
        )
        is not None
        and all(
            is_typed_id(proof_id, "VisibilityProofId")
            for proof_id in descriptor.get("visibility_proof_ids", [])
        )
        for descriptor in visibility_descriptor_rows
    )
    record(
        visibility_required == expected_visibility_required
        and visibility_axes
        >= expected_visibility_required - {"schema"}
        and set(visibility_fixtures)
        == {
            "PF-TopLevelTypeVisibilityAdmitted-POS",
            "PF-TopLevelTypeVisibilityAdmitted-BOUNDARY",
            "PF-TopLevelTypeVisibilityAdmitted-NEG",
        }
        and visibility_descriptor_fields_ok
        and visibility_fixtures[
            "PF-TopLevelTypeVisibilityAdmitted-POS"
        ]
        .get("descriptor", {})
        .get("visibility_proof_ids")
        == ["VisibilityProofId:acme.geometry.public"]
        and visibility_semantic_failures
        == {
            "PF-TopLevelTypeVisibilityAdmitted-POS": set(),
            "PF-TopLevelTypeVisibilityAdmitted-BOUNDARY": set(),
            "PF-TopLevelTypeVisibilityAdmitted-NEG": {
                "TYPE_DECL_VISIBILITY_REQUIRED"
            },
        }
        and (
            visibility_fixtures[
                "PF-TopLevelTypeVisibilityAdmitted-POS"
            ].get("expected")
            == "admitted"
        )
        and (
            visibility_fixtures[
                "PF-TopLevelTypeVisibilityAdmitted-BOUNDARY"
            ].get("expected")
            == "admitted"
        )
        and (
            visibility_fixtures[
                "PF-TopLevelTypeVisibilityAdmitted-NEG"
            ].get("expected")
            == "rejected"
        )
        and (
            visibility_fixtures[
                "PF-TopLevelTypeVisibilityAdmitted-NEG"
            ].get("expected_primary_diagnostic")
            == "TYPE_DECL_VISIBILITY_REQUIRED"
        )
        and all(
            row.get("execution_status") == "DESIGN_STATIC_NOT_RUN"
            for row in visibility_fixtures.values()
        )
        and (
            top_level_visibility_schema.get("properties", {})
            .get("module_identity", {})
            .get("pattern")
            == r"^ModuleId:[^\s]+$"
        )
        and (
            top_level_visibility_schema.get("properties", {})
            .get("package_identity", {})
            .get("pattern")
            == r"^PackageId:[^\s]+$"
        )
        and (
            top_level_visibility_schema.get("properties", {})
            .get("visibility_proof_ids", {})
            .get("items", {})
            .get("pattern")
            == r"^VisibilityProofId:[^\s]+$"
        ),
        "R4_NRM_VISIBILITY_FIXTURE_BINDING",
        (
            f"required={len(visibility_required)} "
            f"axes={len(visibility_axes)} fixtures={len(visibility_fixtures)} "
            f"semantic={visibility_semantic_failures}"
        ),
    )
    resolver_graph_schema = documents[
        "schemas/language/resolver-graph.schema.json"
    ]
    activation_patterns = {
        "receipt": (
            receipt_schema.get("$defs", {})
            .get("activatedIdentity", {})
            .get("pattern")
        ),
        "visibility": (
            visibility_schema.get("$defs", {})
            .get("activationIdentityId", {})
            .get("pattern")
        ),
        "resolver": (
            resolver_graph_schema.get("$defs", {})
            .get("activatedIdentity", {})
            .get("pattern")
        ),
    }
    activation_kind_values = {
        "receipt": (
            receipt_schema.get("$defs", {})
            .get("activationBinding", {})
            .get("properties", {})
            .get("activation_kind", {})
            .get("const")
        ),
        "resolver": (
            resolver_graph_schema.get("$defs", {})
            .get("activationEntry", {})
            .get("properties", {})
            .get("activation_kind", {})
            .get("const")
        ),
    }
    frontend_model = documents["spec/frontend/frontend-model.json"]
    frontend_activation_domain = (
        frontend_model.get("r4_name_resolution_module_contract", {})
        .get("identity_recipes", {})
        .get("activation_kind_domain")
    )
    contract_activation_domain = (
        contract.get("identity_contract", {})
        .get("activation_kind_domain")
    )
    record(
        set(activation_patterns.values()) == {"^ExtensionSetId:[^\\s]+$"}
        and set(activation_kind_values.values()) == {"use"}
        and frontend_activation_domain == ["use"]
        and contract_activation_domain == ["use"],
        "R4_NRM_ACTIVATION_DOMAIN_SEPARATION",
        (
            f"patterns={activation_patterns} "
            f"kinds={activation_kind_values}"
        ),
    )
    witness_pattern = (
        resolver_graph_schema.get("$defs", {})
        .get("traitWitnessId", {})
        .get("pattern")
    )
    record(
        witness_pattern == "^TraitWitnessId:[^\\s]+$",
        "R4_NRM_WITNESS_DOMAIN_SEPARATION",
        f"pattern={witness_pattern}",
    )
    resolver_defs = resolver_graph_schema.get("$defs", {})
    name_binding_schema = resolver_defs.get("nameBinding", {})
    import_binding_schema = resolver_defs.get("importBinding", {})
    name_namespace_domain = resolver_defs.get("nameNamespace", {}).get("enum")
    binding_branches = {}
    for clause in name_binding_schema.get("allOf", []):
        namespace = (
            clause.get("if", {})
            .get("properties", {})
            .get("namespace", {})
            .get("const")
        )
        if namespace is not None:
            binding_branches[namespace] = clause.get("then", {})
    module_binding_properties = binding_branches.get("MODULE", {}).get(
        "properties", {}
    )
    type_binding_properties = binding_branches.get("TYPE", {}).get(
        "properties", {}
    )
    callable_binding_properties = binding_branches.get(
        "CALLABLE_OVERLOAD_SET", {}
    ).get("properties", {})
    value_binding_options = binding_branches.get("VALUE", {}).get(
        "oneOf", []
    )
    value_binding_pairs = {
        (
            option.get("properties", {})
            .get("binding_kind", {})
            .get("const"),
            option.get("properties", {})
            .get("typed_identity", {})
            .get("pattern"),
            option.get("properties", {})
            .get("visibility_start", {})
            .get("const"),
        )
        for option in value_binding_options
    }
    committed_pattern_visibility = next(
        (
            clause.get("then", {})
            .get("properties", {})
            .get("visibility_start", {})
            .get("const")
            for clause in name_binding_schema.get("allOf", [])
            if (
                clause.get("if", {})
                .get("properties", {})
                .get("binding_origin_kind", {})
                .get("const")
                == "COMMITTED_PATTERN_BINDING"
            )
        ),
        None,
    )
    record(
        name_namespace_domain
        == ["MODULE", "TYPE", "VALUE", "CALLABLE_OVERLOAD_SET"]
        and (
            name_binding_schema.get("properties", {})
            .get("namespace", {})
            .get("$ref")
            == "#/$defs/nameNamespace"
        )
        and (
            import_binding_schema.get("properties", {})
            .get("namespace", {})
            .get("$ref")
            == "#/$defs/nameNamespace"
        )
        and set(binding_branches)
        == {"MODULE", "TYPE", "VALUE", "CALLABLE_OVERLOAD_SET"}
        and module_binding_properties.get("binding_kind", {}).get("const")
        == "SINGLE"
        and module_binding_properties.get("typed_identity", {}).get("pattern")
        == r"^ModuleId:[^\s]+$"
        and type_binding_properties.get("binding_kind", {}).get("const")
        == "SINGLE"
        and type_binding_properties.get("typed_identity", {}).get("pattern")
        == r"^DeclId:[^\s]+$"
        and callable_binding_properties.get("binding_kind", {}).get("const")
        == "CALLABLE_OVERLOAD_SLOT"
        and callable_binding_properties.get("typed_identity", {}).get(
            "pattern"
        )
        == r"^DeclId:[^\s]+$"
        and value_binding_pairs
        == {
            ("SINGLE", r"^DeclId:[^\s]+$", None),
            (
                "HIR_LOCAL",
                r"^HirLocalId:[^\s]+$",
                None,
            ),
        }
        and committed_pattern_visibility == "AFTER_TRANSACTION_COMMIT"
        and environments.get("name_namespace_domain")
        == ["MODULE", "TYPE", "VALUE", "CALLABLE_OVERLOAD_SET"]
        and environments.get("control_label_environment")
        == "NOT_APPLICABLE_CURRENT_PROFILE_NO_CONTROL_LABEL_CARRIER"
        and contract.get("lexical_resolution", {}).get(
            "live_control_label_reuse"
        )
        == {
            "r4_status": "NOT_APPLICABLE_CURRENT_PROFILE",
            "reason": "NO_CURRENT_ROOT_CONNECTED_CONTROL_LABEL_SURFACE",
            "future_owner": "FLOW_CONTROL_PROFILE",
            "future_rule_if_activated": "REJECT_LIVE_ANCESTOR_REUSE",
        }
        and "control_label_bindings"
        not in resolver_graph_schema.get("properties", {})
        and "LabelId" not in json.dumps(
            resolver_graph_schema, sort_keys=True
        ),
        "R4_NRM_RESOLVER_ENVIRONMENT_SEPARATION",
        (
            f"namespaces={name_namespace_domain} "
            f"branches={sorted(str(key) for key in binding_branches)} "
            f"pattern_visibility={committed_pattern_visibility}"
        ),
    )

    trace_defs = resolver_trace_schema.get("$defs", {})
    resolved_identity_patterns = {
        "receiptImportTargetIdentity": (
            receipt_schema.get("$defs", {})
            .get("importTargetIdentity", {})
            .get("pattern")
        ),
        "resolverImportTargetIdentity": (
            resolver_graph_schema.get("$defs", {})
            .get("importTargetIdentity", {})
            .get("pattern")
        ),
        "resolverBoundIdentity": (
            resolver_graph_schema.get("$defs", {})
            .get("boundIdentity", {})
            .get("pattern")
        ),
        "traceResolvedIdentity": (
            trace_defs.get("resolvedIdentity", {}).get("pattern")
        ),
        "analysisHirOverloadSetRef": (
            trace_defs.get("analysisHirOverloadSetRef", {}).get("pattern")
        ),
    }
    record(
        resolved_identity_patterns
        == {
            "receiptImportTargetIdentity": (
                "^(?:ModuleId|DeclId):[^\\s]+$"
            ),
            "resolverImportTargetIdentity": (
                "^(?:ModuleId|DeclId):[^\\s]+$"
            ),
            "resolverBoundIdentity": (
                "^(?:ModuleId|DeclId|HirLocalId):[^\\s]+$"
            ),
            "traceResolvedIdentity": (
                "^(?:HirLocalId|DeclId|ModuleId):[^\\s]+$"
            ),
            "analysisHirOverloadSetRef": (
                "^ResolvedOverloadSetRef:[^\\s]+$"
            ),
        },
        "R4_NRM_RESOLVED_IDENTITY_DOMAINS",
        f"patterns={resolved_identity_patterns}",
    )
    candidate_origin_pattern = (
        trace_defs.get("candidateOriginId", {}).get("pattern")
    )
    record(
        candidate_origin_pattern
        == (
            "^(?:HirLocalId|DeclId|ModuleId|ImportBindingId|"
            "ActivationOriginId|EvidenceOriginId|ExtensionSetId|"
            "TraitWitnessId):[^\\s]+$"
        ),
        "R4_NRM_TRACE_CANDIDATE_DOMAINS",
        f"pattern={candidate_origin_pattern}",
    )

    reference_trace_schema = trace_defs.get("referenceTrace", {})
    coherence_branches = reference_trace_schema.get("oneOf", [])
    expected_status_sequences = [
        ["PASS"] * 9,
        *[
            ["PASS"] * failed_index
            + ["FAIL"]
            + ["NOT_EVALUATED"] * (8 - failed_index)
            for failed_index in range(9)
        ],
    ]
    observed_status_sequences: list[list[Any]] = []
    result_bindings_closed = len(coherence_branches) == 10
    for branch_index, branch in enumerate(coherence_branches):
        prefix = (
            branch.get("properties", {})
            .get("stages", {})
            .get("prefixItems", [])
        )
        status_sequence: list[Any] = []
        for item in prefix:
            status_values = nested_property_consts(item, "status")
            reference = item.get("$ref") if isinstance(item, dict) else None
            if (
                not status_values
                and isinstance(reference, str)
                and reference.startswith("#/$defs/")
            ):
                status_values = nested_property_consts(
                    trace_defs.get(reference.removeprefix("#/$defs/"), {}),
                    "status",
                )
            status_sequence.append(
                status_values[0] if len(status_values) == 1 else None
            )
        observed_status_sequences.append(status_sequence)
        result_schema = (
            branch.get("properties", {}).get("result", {})
        )
        if branch_index == 0:
            success_branches = branch.get("oneOf", [])
            accepted = (
                success_branches[0].get("properties", {})
                if len(success_branches) == 2
                and isinstance(success_branches[0], dict)
                else {}
            )
            deferred = (
                success_branches[1].get("properties", {})
                if len(success_branches) == 2
                and isinstance(success_branches[1], dict)
                else {}
            )
            result_bindings_closed = result_bindings_closed and (
                accepted.get("namespace", {})
                .get("not", {})
                .get("const")
                == "CALLABLE_OVERLOAD_SET"
                and accepted.get("result", {}).get("$ref")
                == "#/$defs/acceptedResult"
                and deferred.get("namespace", {}).get("const")
                == "CALLABLE_OVERLOAD_SET"
                and deferred.get("result", {}).get("$ref")
                == "#/$defs/deferredOverloadResult"
            )
        else:
            result_all_of = result_schema.get("allOf", [])
            reason_values = (
                result_all_of[1]
                .get("properties", {})
                .get("rejection_reason", {})
                .get("enum", [])
                if len(result_all_of) == 2
                and isinstance(result_all_of[1], dict)
                else []
            )
            result_bindings_closed = result_bindings_closed and (
                len(result_all_of) == 2
                and result_all_of[0].get("$ref")
                == "#/$defs/rejectedResult"
                and reason_values
                == list(R4_NRM_PRECEDENCE[branch_index - 1][2])
            )
    record(
        observed_status_sequences == expected_status_sequences
        and result_bindings_closed,
        "R4_NRM_TRACE_STATUS_RESULT_SCHEMA",
        (
            f"branches={len(coherence_branches)} "
            f"result_bindings={result_bindings_closed}"
        ),
    )
    seal_schema = trace_defs.get("seal", {})
    diagnostic_selection_schema = trace_defs.get(
        "diagnosticSelection", {}
    )
    seal_status_values = (
        seal_schema.get("properties", {})
        .get("seal_status", {})
        .get("enum", [])
    )
    seal_counter_fields = set(
        trace_defs.get("sealCounters", {})
        .get("properties", {})
    )
    zero_counter_all_of = trace_defs.get(
        "zeroSealCounters", {}
    ).get("allOf", [])
    zero_counter_properties = (
        zero_counter_all_of[1].get("properties", {})
        if len(zero_counter_all_of) > 1
        and isinstance(zero_counter_all_of[1], dict)
        else {}
    )
    not_evaluated_counter_all_of = trace_defs.get(
        "notEvaluatedSealCounters", {}
    ).get("allOf", [])
    not_evaluated_counter_properties = (
        not_evaluated_counter_all_of[1].get("properties", {})
        if len(not_evaluated_counter_all_of) > 1
        and isinstance(not_evaluated_counter_all_of[1], dict)
        else {}
    )
    rejected_counter_all_of = trace_defs.get(
        "rejectedSealCounters", {}
    ).get("allOf", [])
    rejected_counter_guard = (
        rejected_counter_all_of[1]
        if len(rejected_counter_all_of) > 1
        and isinstance(rejected_counter_all_of[1], dict)
        else {}
    )
    record(
        seal_status_values
        == ["SEALED", "REJECTED_AT_HIR_SEAL", "NOT_EVALUATED"]
        and seal_counter_fields
        == {
            "unbound_primary_count",
            "unresolved_count",
            "candidate_set_count",
            "missing_typed_id_count",
            "missing_visibility_proof_count",
            "recovery_binding_count",
            "runtime_relookup_count",
            "overload_winner_count",
            "canonical_hir_overload_set_ref_count",
        }
        and set(diagnostic_selection_schema.get("required", []))
        == {
            "winner_source_origin_id_or_null",
            "winner_rejection_reason_or_null",
            "suppressed_source_origin_ids",
        },
        "R4_NRM_TRACE_SEAL_DIAGNOSTIC_SHAPE",
        (
            f"seal_status={seal_status_values} "
            f"counter_fields={sorted(seal_counter_fields)}"
        ),
    )
    record(
        resolver_trace_schema.get("properties", {})
        .get("diagnostic_order", {})
        .get("const")
        == (
            "LOWEST_FAILED_STAGE_THEN_EXACT_OWNER_PRIMARY_THEN_"
            "LOWEST_SOURCE_ORIGIN_ID"
        )
        and len(diagnostic_selection_schema.get("oneOf", [])) == 2
        and set(zero_counter_properties) == seal_counter_fields
        and all(
            row.get("const") == 0
            for row in zero_counter_properties.values()
        )
        and set(not_evaluated_counter_properties)
        == seal_counter_fields
        and all(
            row.get("type") == "null"
            for row in not_evaluated_counter_properties.values()
        )
        and len(rejected_counter_guard.get("anyOf", [])) == 6
        and {
            key: row.get("const")
            for key, row in rejected_counter_guard.get(
                "properties", {}
            ).items()
        }
        == {
            "recovery_binding_count": 0,
            "overload_winner_count": 0,
            "canonical_hir_overload_set_ref_count": 0,
        },
        "R4_NRM_TRACE_SEAL_DIAGNOSTIC_SCHEMA",
        (
            "diagnostic_selection=EXACT "
            "sealed=ALL_ZERO rejected=REASON_BOUND "
            "not_evaluated=ALL_NULL"
        ),
    )

    hir_bridge_contract = documents[
        "spec/contracts/hir-h1-current-mir-bridge.json"
    ]
    hir_bridge_fixture = documents[
        "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json"
    ]
    hir_bridge_rows = hir_bridge_fixture.get(
        "r4_name_resolution_module_bridge_cases", []
    )
    expected_hir_bridge_rows = [
        {
            "fixture_id": "H1MB-R4-NRM-POS-001",
            "kind": "positive",
            "resolver_output": "RESOLVED_NONCALL_REFERENCE",
            "canonical_hir_projection": (
                "ResolvedRef::Local(HirLocalId)"
            ),
            "expected": "SEALED",
            "assertions": [
                "BodyLocalScope_projects_exact_HirScopeId=true",
                "committed_binding_projects_fresh_HirLocalId=true",
                "runtime_relookup_count=0",
            ],
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        },
        {
            "fixture_id": "H1MB-R4-NRM-POS-002",
            "kind": "positive",
            "resolver_output": "IMPORT_BINDING_TRACE",
            "canonical_hir_projection": (
                "MODULE target remains ModuleId without expression-HIR "
                "projection; declaration expression use projects "
                "ResolvedRef::DirectDecl(DeclId); ImportBindingId retained "
                "in trace"
            ),
            "expected": "SEALED",
            "assertions": [
                "ImportBindingId_creates_HirLocalId=false",
                "SourceOriginId_preserved=true",
                (
                    "module_target_is_ModuleId_and_nonmodule_target_is_"
                    "DeclId=true"
                ),
            ],
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        },
        {
            "fixture_id": "H1MB-R4-NRM-BOUND-003",
            "kind": "boundary",
            "resolver_output": (
                "RESOLVED_OVERLOAD_SET_REF_IN_ANALYSIS_HIR"
            ),
            "canonical_hir_projection": "NONE",
            "expected": "DEFERRED_TO_NEXT_CLUSTER",
            "assertions": [
                "overload_winner_selected=false",
                "canonical_HIR_overload_set_ref=false",
                (
                    "next_cluster=GENERIC_INFERENCE_AND_ORDINARY_"
                    "OVERLOAD_RESOLUTION"
                ),
            ],
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        },
        {
            "fixture_id": "H1MB-R4-NRM-NEG-004",
            "kind": "negative",
            "resolver_output": "REJECTED",
            "canonical_hir_projection": "NONE",
            "expected": "REJECTED_BEFORE_SEAL",
            "assertions": [
                (
                    "unresolved_or_ambiguous_reference_creates_"
                    "canonical_HIR=false"
                ),
                "recovery_binding_count=0",
                "runtime_relookup_count=0",
            ],
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        },
    ]
    hir_bridge_counts = hir_bridge_fixture.get("expected_counts", {})
    hir_machine_acceptance = hir_bridge_contract.get(
        "machine_acceptance", {}
    )
    record(
        hir_bridge_rows == expected_hir_bridge_rows
        and hir_bridge_counts.get(
            "r4_name_resolution_module_bridge_cases"
        )
        == 4
        and hir_machine_acceptance.get(
            "r4_name_resolution_module_bridge_fixture_count"
        )
        == 4
        and all(
            row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in hir_bridge_rows
        ),
        "R4_NRM_HIR_BRIDGE_EXACT_STATIC_BINDING",
        (
            f"rows={len(hir_bridge_rows)}/4 "
            "executed=0/4 product=15/15_NOT_RUN"
        ),
    )

    module_api_fixtures = documents[
        "tests/fixtures/imported/module-api-digest-fixtures.json"
    ]
    r4_fixture_rows = module_api_fixtures.get(
        "r4_interface_envelope_fixtures", []
    )
    r4_fixture_payloads = [
        row.get("payload", {}) for row in r4_fixture_rows
    ]
    record(
        module_api_fixtures.get("r4_interface_envelope_fixture_count") == 3
        and [row.get("fixture_class") for row in r4_fixture_rows]
        == ["positive", "boundary", "negative"]
        and {
            row.get("interface_profile") for row in r4_fixture_rows
        }
        == {"R4_NAME_RESOLUTION_MODULES"}
        and module_api_fixtures.get("product_compiler_execution")
        == "NOT_RUN"
        and all(
            not r4_module_api_failure_codes(payload)
            for payload in r4_fixture_payloads
        )
        and all(
            row.get("canonical_bytes_utf8")
            == json.dumps(
                {
                    key: value
                    for key, value in payload.items()
                    if key != "canonical_sha256"
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            and row.get("expected_canonical_sha256")
            == payload.get("canonical_sha256")
            for row, payload in zip(
                r4_fixture_rows, r4_fixture_payloads
            )
        )
        and len(r4_fixture_payloads) == 3
        and r4_fixture_payloads[0].get("canonical_sha256")
        == r4_fixture_payloads[1].get("canonical_sha256")
        and r4_fixture_payloads[0].get("canonical_sha256")
        != r4_fixture_payloads[2].get("canonical_sha256"),
        "R4_NRM_INTERFACE_FIXTURES",
        f"rows={len(r4_fixture_rows)}",
    )
    artifact_relation_fixture = documents[
        "tests/fixtures/current/module-compilation-artifact-relations-r1.json"
    ]
    artifact_relation_failures = (
        r4_module_artifact_relation_fixture_failure_codes(
            artifact_relation_fixture, module_api_fixtures
        )
    )
    record(
        not artifact_relation_failures,
        "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
        (
            "cases="
            f"{artifact_relation_fixture.get('case_count')} "
            f"failures={sorted(artifact_relation_failures)} "
            "evidence=E2 product=15/15_NOT_RUN"
        ),
    )
    artifact_relation_mutation_results = (
        r4_module_artifact_relation_fixture_mutation_results(
            artifact_relation_fixture, module_api_fixtures
        )
    )
    failed_artifact_relation_mutations = [
        f"{mutation_id}({details})"
        for passed, mutation_id, details
        in artifact_relation_mutation_results
        if not passed
    ]
    record(
        not failed_artifact_relation_mutations
        and len(artifact_relation_mutation_results) == 27,
        "R4_NRM_MODULE_ARTIFACT_RELATION_MUTATION_SELF_TEST",
        (
            "passed="
            f"{len(artifact_relation_mutation_results) - len(failed_artifact_relation_mutations)}"
            f"/{len(artifact_relation_mutation_results)} "
            f"failures={failed_artifact_relation_mutations} "
            "resealed=true evidence=E2 product=15/15_NOT_RUN"
        ),
    )
    return results



R5_OWNERSHIP_CHECK_IDS = (
    "R5_OWN_012_SURFACE_OWNER_PARTITION",
    "R5_OWN_012_CONTEXT_ANCHOR_EXACT_7",
    "R5_OWN_012_HIR_H1_BYTE_FENCE",
    "R5_OWN_013_PREDICATE_UNION_EXACT_2",
    "R5_OWN_013_PREDICATE_OVERRIDE_EXACT_3",
    "R5_OWN_013_SCHEMA_CLOSED_INPUT",
    "R5_OWN_013_FIXTURE_33_AND_CATALOG_19",
    "R5_OWN_013_PROFILE_B_EXACT",
    "R5_OWN_014_REASON_KEY_EXACT_4",
    "R5_OWN_014_PRIMARY_ROUTE_EXACT_1",
    "R5_OWN_014_BINDING_MUTATIONS_EXACT_7",
    "R5_OWN_014_RESIDUAL_DEBT_EXACT_12",
    "R5_OWN_GOVERNANCE_FENCE",
)

R9_DIAGNOSTIC_DISPATCH_CHECK_IDS = (
    "R9_DD_SCHEMA_CLOSED_UNION",
    "R9_DD_CONTRACT_EXACT",
    "R9_DD_BASE_CASES_18",
    "R9_DD_ADVERSARIAL_13",
    "R9_DD_MUTATIONS_12",
    "R9_DD_REASON_KEYS_12",
    "R9_DD_SCOPE_ORIENTATION_INVARIANT",
    "R9_DD_REGISTRY_DISPATCH_EXACT",
    "R9_DD_GOVERNANCE_FENCE",
)
R33_CLEANUP_BUDGET_CHECK_IDS = tuple(
    f"CBA-V{index:02d}_{suffix}"
    for index, suffix in enumerate(
        (
            "SCHEMA_AND_CONTRACT_CLOSED",
            "SURFACE_AND_CANONICAL_EXAMPLE",
            "TYPED_DECISION_MATRIX",
            "NORMALIZATION_ALGEBRA",
            "ABSENCE_AND_EXPLICIT_DEFAULTS",
            "TRANSITIVE_COMPOSITION",
            "INHERITANCE_SUBSTITUTABILITY",
            "RUNTIME_ORDER_UNCHANGED",
            "DIAGNOSTIC_AND_PREDICATE_BINDING",
            "HIR_TYPED_ENVELOPE",
            "MIR_AND_LOWERING_REUSE",
            "MODULE_API_RESIDUE",
            "FIXTURE_AND_MUTATION_MATRIX",
            "GLOBAL_EVIDENCE_FENCES",
        ),
        start=1,
    )
)
R26_PRIMARY_DIAGNOSTIC_CHECK_IDS = (
    "R26_CONTRACT_EXACT",
    "R26_FRONTEND_BINDINGS_EXACT_6",
    "R26_NO_GO_BINDINGS_EXACT_3",
    "R26_ACTIVE_REGISTRY_STAGE_BINDING",
    "R26_PRECEDENCE_EXACT_6",
    "R26_ACCEPTANCE_CASES_EXACT_18",
    "R26_MUTATIONS_EXACT_6",
    "R26_GOVERNANCE_FENCE",
)
R27_GRAMMAR_TOPOLOGY_CHECK_IDS = (
    "R27_CONTRACT_EXACT",
    "R77_RHS_REFERENCE_BINDING_656",
    "R77_EXTERNAL_SYMBOL_REGISTRY_EXACT_41",
    "R27_SIX_ROOT_REACHABILITY_EXACT",
    "R27_UNOWNED_ORPHAN_COUNT_ZERO",
    "R27_PROFILE_EDGE_FENCE",
    "R27_AGGREGATE_ENTRY_FENCE",
    "R27_ACCEPTANCE_CASES_EXACT_3",
    "R27_MUTATIONS_EXACT_6",
    "R27_GOVERNANCE_FENCE",
)
R28_FORMATTER_LSP_INCREMENTAL_CHECK_IDS = (
    "R28_CONTRACT_IDENTITY",
    "R28_SCHEMA_BINDING",
    "R77_FORMATTING_TOTAL_656",
    "R28_FORMATTING_DISJOINT_COUNTS",
    "R28_ACTOR_ROWS_EXACT_5",
    "R28_RECOVERY_RANGE_FENCE",
    "R28_IDENTITY_DOMAIN_SEPARATION",
    "R28_EDIT_SNAPSHOT_CONCURRENCY",
    "R28_LSP_COORDINATE_ACTION_FENCE",
    "R28_DIAGNOSTIC_PARITY_PRECEDENCE",
    "R28_ORACLE_CASES_9",
    "R28_ACCEPTANCE_MATRIX_34",
    "R28_MUTATIONS_12",
    "R28_GOVERNANCE_FENCE",
)
R40_MANUAL_GRAMMAR_COUNT_CHECK_IDS = (
    "R40_CONTRACT_EXACT",
    "R40_AUTHORITATIVE_PROJECTION_EXACT",
    "R40_MACHINE_CONSUMER_PARITY",
    "R40_PUBLISHED_CLAIMS_EXACT_3",
    "R40_ACCEPTANCE_CASES_EXACT_3",
    "R40_STALE_COUNT_MUTATION_REJECTED_1",
    "R40_NO_SOURCE_OR_FEATURE_DRIFT",
    "R40_GOVERNANCE_FENCE",
)
R41_ACTOR_PROTOCOL_CHECK_ID = "R41_ACTOR_PROTOCOL_DIRECT_CONFORMANCE"
R41_ACTOR_PROTOCOL_FOCUSED_CHECKS = [
    "contract and schema",
    "root-connected grammar and leak closure",
    "frontend identity residue",
    "actor coherence binding",
    "11 predicate fixture oracles",
    "diagnostic and feature trace",
    "HIR/MIR lowering residue",
    "26 cases and 8 mutation controls",
    "9 diagnostic mutations plus order permutation",
    "semantic text and governance fence",
]


def _r5_strict_receipt_json(payload: str) -> dict[str, Any]:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        keys = [key for key, _value in pairs]
        if len(keys) != len(set(keys)) or len(keys) != len(
            {key.casefold() for key in keys}
        ):
            raise ValueError("duplicate or case-fold duplicate receipt key")
        return dict(pairs)

    def reject_number(token: str) -> None:
        raise ValueError(f"noninteger receipt number: {token}")

    value = json.loads(
        payload,
        object_pairs_hook=pairs_hook,
        parse_float=reject_number,
        parse_constant=reject_number,
    )
    if not isinstance(value, dict):
        raise ValueError("receipt root is not an object")
    return value


def r5_ownership_workspace_checks(root: Path) -> list[dict[str, Any]]:
    """Return an exact ordered 13-row result or a fail-closed 13-row fallback."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R5_OWNERSHIP_CHECK_IDS
        ]

    runner = root / "tools/validators/run_r5_ownership_decision_mutation_tests.py"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(runner),
                "--root",
                str(root),
                "--workspace-checks-only",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R5 ownership runner nonzero exit "
                f"{completed.returncode}: {completed.stderr.strip()}"
            )
        if completed.stderr:
            return failed_rows("R5 ownership runner emitted unexpected stderr")
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("checks")
        expected_ids = list(R5_OWNERSHIP_CHECK_IDS)
        expected_passed_ids = [
            row["check_id"]
            for row in rows
            if isinstance(row, dict) and row.get("pass") is True
        ] if isinstance(rows, list) else []
        expected_result = (
            "PASS"
            if len(expected_passed_ids) == len(expected_ids)
            else "FAIL"
        )
        expected_static_execution = (
            "EXECUTED_PASS"
            if expected_result == "PASS"
            else "EXECUTED_FAIL"
        )
        if (
            receipt.get("schema")
            != "deeplus.r5-ownership-decision-workspace-validation/v1"
            or receipt.get("result") != expected_result
            or receipt.get("static_validation_execution")
            != expected_static_execution
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("passed_check_id_scope")
            != "R5_OWNERSHIP_EXACT_13"
            or receipt.get("workspace_check_id_count") != len(expected_ids)
            or not isinstance(rows, list)
            or len(rows) != len(expected_ids)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "pass", "detail"}
                or not isinstance(row.get("pass"), bool)
                or not isinstance(row.get("detail"), str)
                for row in rows
            )
            or receipt.get("passed_check_ids") != expected_passed_ids
        ):
            return failed_rows("R5 ownership runner receipt-contract drift")
        if receipt.get("canonical_implementation_validation") is not True:
            return failed_rows("R5 ownership canonical validation flag is not true")
        for row in rows:
            detail = _r5_strict_receipt_json(row["detail"])
            if (
                detail.get("canonical_implementation_validation") is not True
                or not detail.get("installed_canonical_paths")
                or "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY" in row["detail"]
            ):
                return failed_rows(
                    "R5 ownership check did not bind installed canonical inputs"
                )
        return rows
    except Exception as exc:  # noqa: BLE001
        return failed_rows(f"R5 ownership runner integration failure: {exc}")


def r9_diagnostic_dispatch_workspace_checks(
    root: Path,
) -> list[dict[str, Any]]:
    """Bind the exact R9 static runner receipt without claiming product support."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R9_DIAGNOSTIC_DISPATCH_CHECK_IDS
        ]

    runner = root / "tools/validators/run_diagnostic_dispatch_closure_tests.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R9 diagnostic-dispatch runner nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            return failed_rows(
                "R9 diagnostic-dispatch runner emitted unexpected stderr"
            )
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("checks")
        expected_ids = list(R9_DIAGNOSTIC_DISPATCH_CHECK_IDS)
        if not isinstance(rows, list):
            return failed_rows(
                "R9 diagnostic-dispatch runner checks are not an array"
            )
        passed_ids = [
            row.get("check_id")
            for row in rows
            if isinstance(row, dict) and row.get("status") == "PASS"
        ]
        expected_result = (
            "PASS" if len(passed_ids) == len(expected_ids) else "FAIL"
        )
        if (
            receipt.get("schema")
            != "deeplus.r9-diagnostic-dispatch-closure-test-receipt/v1"
            or receipt.get("result") != expected_result
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("check_scope")
            != "R9_DIAGNOSTIC_DISPATCH_CLOSURE_EXACT"
            or receipt.get("check_count") != len(expected_ids)
            or receipt.get("passed_check_count") != len(passed_ids)
            or receipt.get("base_case_count") != 18
            or receipt.get("adversarial_case_count") != 13
            or receipt.get("mutation_count") != 12
            or receipt.get("reason_key_count") != 12
            or len(rows) != len(expected_ids)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "status", "detail"}
                or row.get("status") not in {"PASS", "FAIL"}
                for row in rows
            )
            or not isinstance(receipt.get("errors"), list)
            or (expected_result == "PASS" and receipt.get("errors") != [])
        ):
            return failed_rows(
                "R9 diagnostic-dispatch runner receipt-contract drift"
            )
        return [
            {
                "check_id": row["check_id"],
                "pass": row["status"] == "PASS",
                "detail": (
                    row["detail"]
                    if isinstance(row["detail"], str)
                    else json.dumps(
                        row["detail"],
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                ),
            }
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        return failed_rows(
            f"R9 diagnostic-dispatch runner integration failure: {exc}"
        )


def r33_cleanup_budget_workspace_checks(root: Path) -> list[dict[str, Any]]:
    """Bind the exact R33 static receipt without claiming product support."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R33_CLEANUP_BUDGET_CHECK_IDS
        ]

    runner = root / "tools/validators/validate_cleanup_budget_algebra.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R33 cleanup-budget runner nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            return failed_rows("R33 cleanup-budget runner emitted unexpected stderr")
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("check_results")
        expected_ids = list(R33_CLEANUP_BUDGET_CHECK_IDS)
        if (
            receipt.get("schema")
            != "deeplus.cleanup-budget-algebra-validation-receipt/r1"
            or receipt.get("revision") != "R33-CLEANUP-BUDGET-ALGEBRA-R1"
            or receipt.get("result") != "PASS"
            or receipt.get("checks") != 14
            or receipt.get("passed") != 14
            or receipt.get("failed") != 0
            or receipt.get("mutation_count") != 12
            or receipt.get("mutation_rejections") != 12
            or receipt.get("new_mir_operation_kind_count") != 0
            or receipt.get("new_active_diagnostic_id_count") != 3
            or receipt.get("feature_p1") != "22_OPEN_UNCHANGED"
            or receipt.get("separate_actions") != "4_OPEN_UNCHANGED"
            or receipt.get("product_lanes") != "15_OF_15_NOT_RUN"
            or receipt.get("github_mutation") != "NOT_PERFORMED"
            or not isinstance(rows, list)
            or len(rows) != len(expected_ids)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "result", "detail"}
                or row.get("result") != "PASS"
                for row in rows
            )
        ):
            return failed_rows("R33 cleanup-budget runner receipt-contract drift")
        return [
            {
                "check_id": row["check_id"],
                "pass": True,
                "detail": (
                    row["detail"]
                    if isinstance(row["detail"], str)
                    else json.dumps(row["detail"], ensure_ascii=False, sort_keys=True)
                ),
            }
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        return failed_rows(f"R33 cleanup-budget runner integration failure: {exc}")


def frontend_readiness_workspace_checks(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def emit(check_id: str, condition: bool, detail: Any) -> None:
        rows.append(
            {
                "check_id": check_id,
                "pass": bool(condition),
                "detail": (
                    detail
                    if isinstance(detail, str)
                    else json.dumps(detail, ensure_ascii=False, sort_keys=True)
                ),
            }
        )

    try:
        grammar_path = root / "spec/grammar/deeplus.ebnf"
        grammar_bytes = grammar_path.read_bytes()
        grammar_text = grammar_bytes.decode("utf-8")
        grammar_sha = hashlib.sha256(grammar_bytes).hexdigest()
        output = list(grammar_text)
        comment_depth = 0
        quoted = False
        escaped = False
        index = 0
        while index < len(grammar_text):
            pair = grammar_text[index : index + 2]
            char = grammar_text[index]
            if comment_depth:
                if pair == "(*":
                    output[index] = output[index + 1] = " "
                    comment_depth += 1
                    index += 2
                    continue
                if pair == "*)":
                    output[index] = output[index + 1] = " "
                    comment_depth -= 1
                    index += 2
                    continue
                if char not in "\r\n":
                    output[index] = " "
                index += 1
                continue
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                index += 1
                continue
            if char == '"':
                quoted = True
                index += 1
                continue
            if pair == "(*":
                output[index] = output[index + 1] = " "
                comment_depth = 1
                index += 2
                continue
            index += 1
        without_comments = "".join(output)
        production_starts = list(
            re.finditer(
                r"(?m)^([A-Za-z_][A-Za-z0-9_]*)[ \t]*::=",
                without_comments,
            )
        )
        production_names = []
        production_rhs: dict[str, str] = {}
        for match_index, match in enumerate(production_starts):
            next_start = (
                production_starts[match_index + 1].start()
                if match_index + 1 < len(production_starts)
                else len(without_comments)
            )
            tail = without_comments[match.end() : next_start]
            tail_quoted = False
            tail_escaped = False
            terminator = None
            for offset, char in enumerate(tail):
                if tail_quoted:
                    if tail_escaped:
                        tail_escaped = False
                    elif char == "\\":
                        tail_escaped = True
                    elif char == '"':
                        tail_quoted = False
                    continue
                if char == '"':
                    tail_quoted = True
                elif char == ";":
                    terminator = offset
                    break
            if terminator is None:
                raise ValueError(
                    f"unterminated grammar production {match.group(1)}"
                )
            production_names.append(match.group(1))
            production_rhs[match.group(1)] = re.sub(
                r"\s+", " ", tail[:terminator].strip()
            )

        registry = json.loads(
            (
                root
                / "spec/contracts/grammar-production-disposition-registry-r1.json"
            ).read_text(encoding="utf-8")
        )
        contract = json.loads(
            (
                root
                / "spec/contracts/frontend-cst-boundary-recovery-contract.json"
            ).read_text(encoding="utf-8")
        )
        r13 = json.loads(
            (
                root
                / "spec/contracts/parser-boundary-match-arm-contract-r1.json"
            ).read_text(encoding="utf-8")
        )
        r14 = json.loads(
            (
                root
                / "spec/contracts/frontend-recovery-invalid-tree-contract-r1.json"
            ).read_text(encoding="utf-8")
        )
        r15 = json.loads(
            (
                root
                / "spec/contracts/closed-pratt-parse-goal-contract-r1.json"
            ).read_text(encoding="utf-8")
        )
        r16 = json.loads(
            (
                root
                / "spec/contracts/complete-token-lexical-goal-contract-r1.json"
            ).read_text(encoding="utf-8")
        )
        r17 = json.loads(
            (
                root
                / "spec/contracts/shorthand-interpolation-state-machine-contract-r1.json"
            ).read_text(encoding="utf-8")
        )
        r18 = json.loads(
            (
                root
                / "spec/contracts/multiline-interpolation-atomic-payload-contract-r1.json"
            ).read_text(encoding="utf-8")
        )
        frontend = json.loads(
            (root / "spec/frontend/frontend-model.json").read_text(
                encoding="utf-8"
            )
        )
        cst_fixture = json.loads(
            (
                root
                / "tests/fixtures/current/frontend-cst-boundary-recovery-r1.json"
            ).read_text(encoding="utf-8")
        )
        scanner_fixture = json.loads(
            (
                root
                / "tests/fixtures/current/frontend-pratt-scanner-interpolation-r1.json"
            ).read_text(encoding="utf-8")
        )
        source_roles = json.loads(
            (root / "spec/contracts/source-roles.json").read_text(
                encoding="utf-8"
            )
        )
        gate_map = json.loads(
            (root / "spec/features/gates.json").read_text(encoding="utf-8")
        )
        source_role_fixture = json.loads(
            (
                root
                / "tests/fixtures/current/source-role-profile-gate-r1.json"
            ).read_text(encoding="utf-8")
        )
        feature_rows: list[dict[str, Any]] = []
        for feature_chunk in sorted(
            (root / "spec/features/catalog/chunks").glob("part-*.json")
        ):
            chunk_rows = json.loads(feature_chunk.read_text(encoding="utf-8"))
            if isinstance(chunk_rows, list):
                feature_rows.extend(
                    row for row in chunk_rows if isinstance(row, dict)
                )

        production_rows = registry.get("production_rows", [])
        disposition_counts = Counter(
            row.get("disposition") for row in production_rows
        )
        emit(
            "FRONTEND_R12_GRAMMAR_IDENTITY",
            grammar_sha
            == "914399e4fd35f552cab3111613244cb6844b6313f8b9bd17ebbead0ad7df9bd9"
            and len(grammar_bytes) == 70409
            and len(production_names) == 656
            and registry.get("grammar", {}).get("sha256") == grammar_sha,
            {
                "sha256": grammar_sha,
                "bytes": len(grammar_bytes),
                "productions": len(production_names),
            },
        )
        emit(
            "FRONTEND_R12_DISPOSITION_TOTALITY",
            len(production_rows) == 656
            and [row.get("ordinal") for row in production_rows]
            == list(range(1, 657))
            and [row.get("production_id") for row in production_rows]
            == production_names
            and all(
                row.get("normalized_rhs")
                == production_rhs.get(row.get("production_id"))
                and row.get("rhs_sha256")
                == hashlib.sha256(
                    production_rhs.get(row.get("production_id"), "").encode(
                        "utf-8"
                    )
                ).hexdigest()
                for row in production_rows
            )
            and disposition_counts
            == Counter(
                {
                    "ast_node": 205,
                    "cst_only": 420,
                    "external_parser_entry": 19,
                    "normalize_to": 12,
                }
            ),
            {
                "rows": len(production_rows),
                "dispositions": dict(sorted(disposition_counts.items())),
            },
        )
        emit(
            "FRONTEND_R12_NORMALIZATION_RECOVERY_FENCE",
            len(registry.get("normalization_rules", [])) == 10
            and len(registry.get("recovery_kinds", [])) == 4
            and all(
                row.get("disposition") == "reject_before_ast"
                and row.get("ast_node_count") == 0
                for row in registry.get("recovery_kinds", [])
            )
            and contract.get("r12_cst_ast_normalization", {}).get(
                "production_count"
            )
            == 643,
            {
                "normalizations": len(registry.get("normalization_rules", [])),
                "recovery_kinds": len(registry.get("recovery_kinds", [])),
            },
        )
        emit(
            "FRONTEND_R13_BOUNDARY_MATCH_ARM_CLOSURE",
            r13.get("schema") == "deeplus.parser-boundary-match-arm-contract/r1"
            and len(r13.get("reason_codes", [])) == 5
            and r13.get("diagnostic_authority_fence", "").endswith(
                "IR-FE-P1-035"
            )
            and r13.get("surface_fence", {}).get(
                "new_source_spelling_count"
            )
            == 0,
            {
                "reason_codes": len(r13.get("reason_codes", [])),
                "new_source_spelling_count": r13.get(
                    "surface_fence", {}
                ).get("new_source_spelling_count"),
            },
        )
        emit(
            "FRONTEND_R14_RECOVERY_QUARANTINE",
            r14.get("schema")
            == "deeplus.frontend-recovery-invalid-tree-contract/r1"
            and len(r14.get("recovery_cst_kinds", [])) == 4
            and len(r14.get("insert_safe_tokens", [])) == 9
            and len(r14.get("recovery_classes", [])) == 9
            and r14.get("analysis_only_quarantine", {}).get(
                "canonical_hir_serialization"
            )
            is False
            and r14.get("progress_and_budget", {}).get(
                "infinite_loop_possible"
            )
            is False,
            {
                "recovery_kinds": len(r14.get("recovery_cst_kinds", [])),
                "insert_safe_tokens": len(r14.get("insert_safe_tokens", [])),
                "recovery_classes": len(r14.get("recovery_classes", [])),
            },
        )

        goal_domain = [row.get("goal") for row in r15.get("goal_registry", [])]
        postfix = next(
            row
            for row in frontend["pratt"]["expression"]["operators"]
            if row.get("id") == "postfix"
        )
        message_led = frontend["pratt"]["closed_parse_goal_contract"][
            "message_led"
        ]
        emit(
            "FRONTEND_R15_CLOSED_PRATT_GOALS",
            goal_domain
            == [
                "EXPRESSION",
                "PREDICATE",
                "SLICE_INDEX",
                "TYPE",
                "NON_FUNCTION_TYPE",
                "UNIT",
            ]
            and "message" not in postfix.get("structured", [])
            and message_led.get("~", {}).get("lbp") == 15
            and message_led.get(":~", {}).get("associativity")
            == "terminal_nonassociative",
            {
                "goals": goal_domain,
                "postfix_structured": postfix.get("structured", []),
                "message_led": message_led,
            },
        )
        emit(
            "FRONTEND_R16_TOKEN_LEXICAL_TOTALITY",
            len(r16.get("scanner_modes", [])) == 6
            and len(r16.get("lexical_goals", [])) == 10
            and len(r16.get("syntax_terminal_registry", [])) == 200
            and len(r16.get("atomic_token_registry", [])) == 22
            and len(r16.get("trivia_registry", [])) == 8
            and r16.get("token_transaction", {}).get(
                "failed_probe_source_byte_consumption"
            )
            == 0
            and r16.get("token_transaction", {}).get(
                "failed_probe_diagnostic_count"
            )
            == 0,
            {
                "scanner_modes": len(r16.get("scanner_modes", [])),
                "lexical_goals": len(r16.get("lexical_goals", [])),
                "terminals": len(r16.get("syntax_terminal_registry", [])),
                "atomic_tokens": len(r16.get("atomic_token_registry", [])),
                "trivia": len(r16.get("trivia_registry", [])),
            },
        )
        emit(
            "FRONTEND_R17_SHORTHAND_STATE_MACHINE",
            len(r17.get("state_registry", [])) == 14
            and len(r17.get("transition_registry", [])) == 20
            and r17.get("diagnostic_fence", {}).get(
                "new_final_diagnostic_id_count"
            )
            == 0
            and frontend["scanner"]["shorthand_interpolation_state_machine"][
                "final_diagnostic_owner_gap"
            ]
            == "IR-FE-P1-035",
            {
                "states": len(r17.get("state_registry", [])),
                "transitions": len(r17.get("transition_registry", [])),
            },
        )
        emit(
            "FRONTEND_R18_MULTILINE_ATOMIC_PAYLOAD",
            len(r18.get("outer_token", {}).get("payload_fields", [])) == 12
            and len(r18.get("part_variants", [])) == 4
            and len(r18.get("pipeline", [])) == 7
            and r18.get("scanner_parser_handshake", {}).get(
                "atomic_envelope_is_cst_leaf"
            )
            is False
            and r18.get("scanner_parser_handshake", {}).get(
                "payload_leaves_partition_source_exactly_once"
            )
            is True
            and frontend["scanner"]["multiline_string_phase_a"].get(
                "closer_on_own_line"
            )
            is True,
            {
                "payload_fields": len(
                    r18.get("outer_token", {}).get("payload_fields", [])
                ),
                "part_variants": len(r18.get("part_variants", [])),
                "pipeline": len(r18.get("pipeline", [])),
            },
        )

        cst_suites = cst_fixture.get("suites", {})
        scanner_suites = scanner_fixture.get("suites", {})
        emit(
            "FRONTEND_READINESS_FIXTURE_BINDING",
            set(cst_suites) == {"r12", "r13", "r14"}
            and set(scanner_suites) == {"r15", "r16", "r17", "r18"}
            and all(
                suite.get("counts", {}).get("total")
                == len(suite.get("tests", []))
                for suite in list(cst_suites.values())
                + list(scanner_suites.values())
            )
            and scanner_fixture.get("diagnostic_fence", {}).get(
                "new_final_diagnostic_id_count"
            )
            == 0,
            {
                "cst_suites": sorted(cst_suites),
                "scanner_suites": sorted(scanner_suites),
                "test_count": sum(
                    len(suite.get("tests", []))
                    for suite in list(cst_suites.values())
                    + list(scanner_suites.values())
                ),
            },
        )
        expected_role_profile_roots = [
            ("library", "stable", "LibrarySourceFile", "CURRENT"),
            ("library", "preview", "PreviewLibrarySourceFile", "EXPLICIT_PREVIEW"),
            ("executable", "stable", "ExecutableSourceFile", "CURRENT"),
            ("executable", "preview", "PreviewExecutableSourceFile", "EXPLICIT_PREVIEW"),
            ("script", "stable", "ScriptSourceFile", "CURRENT"),
            ("script", "preview", "PreviewScriptSourceFile", "EXPLICIT_PREVIEW"),
        ]
        actual_role_profile_roots = [
            (
                row.get("source_role"),
                row.get("activation_profile"),
                row.get("root"),
                row.get("normalized_hir_source_profile"),
            )
            for row in source_roles.get("role_profile_root_matrix", [])
        ]
        frontend_root_rows = [
            (
                row.get("role"),
                row.get("activation_profile"),
                root_name,
                row.get("normalized_hir_source_profile"),
            )
            for root_name, row in frontend.get("source_roots", {}).items()
        ]
        emit(
            "FRONTEND_R19_SOURCE_ROLE_PROFILE_ROOT_TOTALITY",
            source_roles.get("source_role_domain")
            == ["library", "executable", "script"]
            and source_roles.get("activation_profile_domain")
            == ["stable", "preview"]
            and actual_role_profile_roots == expected_role_profile_roots
            and sorted(frontend_root_rows) == sorted(expected_role_profile_roots)
            and source_role_fixture.get("source_role_domain")
            == ["library", "executable", "script"]
            and source_role_fixture.get("activation_profile_domain")
            == ["stable", "preview"],
            {
                "contract_rows": actual_role_profile_roots,
                "frontend_rows": frontend_root_rows,
            },
        )
        active_gate_ids = [
            row.get("feature_id") for row in gate_map.get("entries", [])
        ]
        nonactivatable_catalog_ids = sorted(
            row.get("feature_id")
            for row in feature_rows
            if row.get("source_activation") == "nonactivatable"
        )
        frontend_gate_ids = [
            row.get("feature_id")
            for row in frontend.get(
                "source_role_profile_gate_contract", {}
            ).get("active_gate_registry_projection", [])
        ]
        emit(
            "FRONTEND_R19_GATE_PROJECTION_AND_ATOMICITY",
            active_gate_ids
            == [
                "ffi_c_extern_unsafe_surface_msp",
                "ffi_minimum_sound_profile",
                "numeric_array_elementwise_power_msp",
            ]
            and frontend_gate_ids == active_gate_ids
            and gate_map.get("nonactivatable")
            == nonactivatable_catalog_ids
            and len(nonactivatable_catalog_ids) == 114
            and source_role_fixture.get("atomic_failure_result")
            == {
                "activated_features": [],
                "canonical_source_unit_ast": None,
            }
            and source_role_fixture.get("acceptance", {}).get(
                "new_diagnostic_id_count"
            )
            == 0,
            {
                "active_gate_ids": active_gate_ids,
                "frontend_gate_ids": frontend_gate_ids,
                "nonactivatable_count": len(nonactivatable_catalog_ids),
            },
        )
    except Exception as exc:  # noqa: BLE001
        emit(
            "FRONTEND_READINESS_VALIDATOR_INTEGRATION",
            False,
            f"{type(exc).__name__}: {exc}",
        )
    return rows


def r26_primary_diagnostic_workspace_checks(
    root: Path,
) -> list[dict[str, Any]]:
    """Bind the exact R26 diagnostic-identity receipt without product claims."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R26_PRIMARY_DIAGNOSTIC_CHECK_IDS
        ]

    runner = root / "tools/validators/validate_frontend_primary_diagnostic_identity.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R26 primary-diagnostic runner nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            return failed_rows(
                "R26 primary-diagnostic runner emitted unexpected stderr"
            )
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("checks")
        expected_ids = list(R26_PRIMARY_DIAGNOSTIC_CHECK_IDS)
        if (
            receipt.get("schema")
            != "deeplus.r26-frontend-primary-diagnostic-validation-receipt/r1"
            or receipt.get("result") != "PASS"
            or receipt.get("evidence_level") != "E2_STATIC_CLOSURE"
            or receipt.get("check_scope")
            != "R26_PRIMARY_DIAGNOSTIC_IDENTITY_EXACT"
            or receipt.get("check_count") != len(expected_ids)
            or receipt.get("passed_check_count") != len(expected_ids)
            or receipt.get("frontend_binding_count") != 6
            or receipt.get("no_go_binding_count") != 3
            or receipt.get("binding_family_count") != 6
            or receipt.get("acceptance_case_count") != 18
            or receipt.get("mutation_count") != 6
            or receipt.get("rejected_mutation_count") != 6
            or receipt.get("new_diagnostic_id_count") != 0
            or receipt.get("semantic_change_count") != 0
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("errors") != []
            or not isinstance(rows, list)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "pass"}
                or row.get("pass") is not True
                for row in rows
            )
        ):
            return failed_rows("R26 primary-diagnostic receipt-contract drift")
        detail = json.dumps(
            {
                "frontend_bindings": 6,
                "no_go_bindings": 3,
                "families": 6,
                "acceptance_cases": 18,
                "mutations_rejected": 6,
                "new_diagnostic_ids": 0,
                "semantic_changes": 0,
                "product_execution": "NOT_RUN",
            },
            sort_keys=True,
        )
        return [
            {"check_id": row["check_id"], "pass": True, "detail": detail}
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        return failed_rows(
            f"R26 primary-diagnostic runner integration failure: {exc}"
        )


def r27_grammar_topology_workspace_checks(
    root: Path,
) -> list[dict[str, Any]]:
    """Bind the exact R27 grammar-topology receipt without product claims."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R27_GRAMMAR_TOPOLOGY_CHECK_IDS
        ]

    runner = root / "tools/validators/validate_grammar_topology_closure.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R27 grammar-topology runner nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            return failed_rows(
                "R27 grammar-topology runner emitted unexpected stderr"
            )
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("checks")
        expected_ids = list(R27_GRAMMAR_TOPOLOGY_CHECK_IDS)
        if (
            receipt.get("schema")
            != "deeplus.r27-grammar-topology-validation-receipt/r1"
            or receipt.get("result") != "PASS"
            or receipt.get("evidence_level") != "E2_STATIC_CLOSURE"
            or receipt.get("check_scope")
            != "R27_GRAMMAR_TOPOLOGY_CLOSURE_EXACT"
            or receipt.get("check_count") != len(expected_ids)
            or receipt.get("passed_check_count") != len(expected_ids)
            or receipt.get("production_count") != 656
            or receipt.get("declared_reference_binding_count") != 656
            or receipt.get("external_symbol_count") != 41
            or receipt.get("source_root_count") != 6
            or receipt.get("six_root_union_count") != 506
            or receipt.get("six_root_shared_count") != 479
            or receipt.get("six_root_unreachable_count") != 150
            or receipt.get("aggregate_entry_root_count") != 2
            or receipt.get("unowned_orphan_count") != 0
            or receipt.get("illegal_cross_profile_edge_count") != 0
            or receipt.get("acceptance_case_count") != 3
            or receipt.get("mutation_count") != 6
            or receipt.get("rejected_mutation_count") != 6
            or receipt.get("grammar_production_change_count") != 0
            or receipt.get("post_closure_projection_addition_count") != 1
            or receipt.get("post_closure_projection_gap_id")
            != "IR-OWN-P1-018"
            or receipt.get("new_source_spelling_count") != 0
            or receipt.get("semantic_change_count") != 0
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("errors") != []
            or not isinstance(rows, list)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "pass"}
                or row.get("pass") is not True
                for row in rows
            )
        ):
            return failed_rows("R27 grammar-topology receipt-contract drift")
        detail = json.dumps(
            {
                "productions": 656,
                "external_symbols": 41,
                "source_roots": 6,
                "six_root_union": 506,
                "six_root_shared": 479,
                "unowned_orphans": 0,
                "illegal_profile_edges": 0,
                "mutations_rejected": 6,
                "post_closure_projection_additions": 1,
                "post_closure_projection_gap": "IR-OWN-P1-018",
                "semantic_changes": 0,
                "product_execution": "NOT_RUN",
            },
            sort_keys=True,
        )
        return [
            {"check_id": row["check_id"], "pass": True, "detail": detail}
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        return failed_rows(
            f"R27 grammar-topology runner integration failure: {exc}"
        )


def r28_formatter_lsp_incremental_workspace_checks(
    root: Path,
) -> list[dict[str, Any]]:
    """Bind the exact-main R28 tooling contract without product claims."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R28_FORMATTER_LSP_INCREMENTAL_CHECK_IDS
        ]

    runner = root / "tools/validators/validate_formatter_lsp_incremental_parsing.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R28 formatter/LSP/incremental runner nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            return failed_rows(
                "R28 formatter/LSP/incremental runner emitted unexpected stderr"
            )
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("checks")
        expected_ids = list(R28_FORMATTER_LSP_INCREMENTAL_CHECK_IDS)
        if (
            receipt.get("schema")
            != "deeplus.r28-formatter-lsp-incremental-validation-receipt/r1"
            or receipt.get("result") != "PASS"
            or receipt.get("mode") != "VALIDATE"
            or receipt.get("evidence_level") != "E2_STATIC_CLOSURE"
            or receipt.get("check_scope")
            != "R28_FORMATTER_LSP_INCREMENTAL_EXACT"
            or receipt.get("check_count") != len(expected_ids)
            or receipt.get("passed_check_count") != len(expected_ids)
            or receipt.get("grammar_production_count") != 656
            or receipt.get("formatting_rule_count") != 6
            or receipt.get("formatting_rule_counts")
            != {
                "FD-01": 54,
                "FD-02": 33,
                "FD-03": 333,
                "FD-04": 205,
                "FD-05": 12,
                "FD-06": 19,
            }
            or receipt.get("unclassified_production_count") != 0
            or receipt.get("multiply_classified_production_count") != 0
            or receipt.get("identity_domain_count") != 8
            or receipt.get("forbidden_identity_conflation_count") != 6
            or receipt.get("acceptance_case_count") != 9
            or receipt.get("acceptance_class_counts")
            != {"boundary": 3, "negative": 3, "positive": 3}
            or receipt.get("successor_acceptance_case_count") != 34
            or receipt.get("mutation_count") != 12
            or receipt.get("rejected_mutation_count") != 12
            or receipt.get("source_syntax_change_count") != 0
            or receipt.get("grammar_production_change_count") != 0
            or receipt.get("language_semantic_change_count") != 0
            or receipt.get("new_final_diagnostic_id_count") != 0
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("github_publication")
            != "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION"
            or receipt.get("errors") != []
            or not isinstance(rows, list)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "pass"}
                or row.get("pass") is not True
                for row in rows
            )
        ):
            return failed_rows(
                "R28 formatter/LSP/incremental receipt-contract drift"
            )
        detail = json.dumps(
            {
                "grammar_productions": 656,
                "formatting_rules": 6,
                "identity_domains": 8,
                "oracle_cases": 9,
                "successor_acceptance_cases": 34,
                "mutations_rejected": 12,
                "source_syntax_changes": 0,
                "semantic_changes": 0,
                "product_execution": "NOT_RUN",
            },
            sort_keys=True,
        )
        return [
            {"check_id": row["check_id"], "pass": True, "detail": detail}
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        return failed_rows(
            f"R28 formatter/LSP/incremental runner integration failure: {exc}"
        )


def r40_manual_grammar_count_workspace_checks(
    root: Path,
) -> list[dict[str, Any]]:
    """Bind the exact R40 manual grammar-count receipt without product claims."""

    def failed_rows(detail: str) -> list[dict[str, Any]]:
        return [
            {"check_id": check_id, "pass": False, "detail": detail}
            for check_id in R40_MANUAL_GRAMMAR_COUNT_CHECK_IDS
        ]

    runner = root / "tools/validators/validate_manual_grammar_count_authority.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            return failed_rows(
                "R40 manual grammar-count runner nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            return failed_rows(
                "R40 manual grammar-count runner emitted unexpected stderr"
            )
        receipt = _r5_strict_receipt_json(completed.stdout)
        rows = receipt.get("checks")
        expected_ids = list(R40_MANUAL_GRAMMAR_COUNT_CHECK_IDS)
        if (
            receipt.get("schema")
            != "deeplus.r40-manual-grammar-count-validation-receipt/r1"
            or receipt.get("result") != "PASS"
            or receipt.get("evidence_level") != "E2_STATIC_CLOSURE"
            or receipt.get("check_scope")
            != "R40_MANUAL_GRAMMAR_COUNT_AUTHORITY_EXACT"
            or receipt.get("check_count") != len(expected_ids)
            or receipt.get("passed_check_count") != len(expected_ids)
            or receipt.get("profile_counts")
            != {"LEXICAL": 87, "STABLE": 556, "PREVIEW": 13}
            or receipt.get("production_count") != 656
            or receipt.get("manual_claim_count") != 3
            or receipt.get("acceptance_case_count") != 3
            or receipt.get("mutation_count") != 1
            or receipt.get("rejected_mutation_count") != 1
            or receipt.get("grammar_production_change_count") != 0
            or receipt.get("new_source_spelling_count") != 0
            or receipt.get("semantic_change_count") != 0
            or receipt.get("feature_p1") != "22_OPEN_UNCHANGED"
            or receipt.get("m13_actions") != "4_OPEN_UNCHANGED"
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("errors") != []
            or not isinstance(rows, list)
            or [row.get("check_id") for row in rows] != expected_ids
            or any(
                not isinstance(row, dict)
                or set(row) != {"check_id", "pass"}
                or row.get("pass") is not True
                for row in rows
            )
        ):
            return failed_rows(
                "R40 manual grammar-count receipt-contract drift"
            )
        detail = json.dumps(
            {
                "profiles": {"LEXICAL": 87, "STABLE": 556, "PREVIEW": 13},
                "productions": 656,
                "manual_claims": 3,
                "mutations_rejected": 1,
                "semantic_changes": 0,
                "product_execution": "NOT_RUN",
            },
            sort_keys=True,
        )
        return [
            {"check_id": row["check_id"], "pass": True, "detail": detail}
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        return failed_rows(
            f"R40 manual grammar-count runner integration failure: {exc}"
        )


def r41_actor_protocol_workspace_check(root: Path) -> dict[str, Any]:
    """Bind the focused R41 design-static receipt without product claims."""

    runner = root / "tools/validators/validate_actor_protocol_direct_conformance.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            raise ValueError(
                "focused validator nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            raise ValueError("focused validator emitted unexpected stderr")
        receipt = _r5_strict_receipt_json(completed.stdout)
        if (
            set(receipt)
            != {
                "result",
                "checks",
                "predicate_fixtures",
                "acceptance_cases",
                "mutation_oracles",
                "diagnostics",
                "product_support",
            }
            or receipt.get("result") != "PASS"
            or receipt.get("checks") != R41_ACTOR_PROTOCOL_FOCUSED_CHECKS
            or receipt.get("predicate_fixtures") != 11
            or receipt.get("acceptance_cases") != 26
            or receipt.get("mutation_oracles") != 10
            or receipt.get("diagnostics") != 9
            or receipt.get("product_support") != "NOT_RUN"
        ):
            raise ValueError("focused receipt-contract drift")
        return {
            "check_id": R41_ACTOR_PROTOCOL_CHECK_ID,
            "pass": True,
            "detail": json.dumps(receipt, ensure_ascii=False, sort_keys=True),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "check_id": R41_ACTOR_PROTOCOL_CHECK_ID,
            "pass": False,
            "detail": f"R41 Actor Protocol integration failure: {exc}",
        }


def r23_actor_protocol_binding_workspace_check(root: Path) -> dict[str, Any]:
    """Bind the focused R23 design-static descriptor receipt."""

    runner = (
        root
        / "tools/validators/validate_actor_protocol_binding_descriptors.py"
    )
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            raise ValueError(
                "focused validator nonzero exit "
                f"{completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            raise ValueError("focused validator emitted unexpected stderr")
        receipt = _r5_strict_receipt_json(completed.stdout)
        if (
            receipt.get("result") != "PASS"
            or receipt.get("check_count") != 55
            or receipt.get("failed") != []
            or receipt.get("product_execution") != "NOT_RUN"
            or receipt.get("canonical_source_status")
            != "LOCAL_REBASED_PROJECTION"
        ):
            raise ValueError("focused receipt-contract drift")
        return {
            "check_id": "R23_ACTOR_PROTOCOL_BINDING_DESCRIPTOR",
            "pass": True,
            "detail": json.dumps(
                receipt, ensure_ascii=False, sort_keys=True
            ),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "check_id": "R23_ACTOR_PROTOCOL_BINDING_DESCRIPTOR",
            "pass": False,
            "detail": f"R23 Actor Protocol binding failure: {exc}",
        }


def r22_actor_lifecycle_workspace_check(root: Path) -> dict[str, Any]:
    """Run the exact-main R22 lifecycle validator without product overclaim."""

    runner = root / "tools/validators/validate_actor_minimum_lifecycle.py"
    expected = (
        "ACTOR_MINIMUM_LIFECYCLE_PASS: rules=20 fixtures=10 admit=5 "
        "reject=5 guards=12 trace=complete restart=0 interleaving=0 "
        "product=NOT_RUN"
    )
    try:
        completed = subprocess.run(
            [sys.executable, str(runner)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            raise ValueError(
                f"focused validator nonzero exit {completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr or completed.stdout.strip() != expected:
            raise ValueError("focused lifecycle receipt-contract drift")
        return {
            "check_id": "R22_ACTOR_MINIMUM_LIFECYCLE",
            "pass": True,
            "detail": expected,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "check_id": "R22_ACTOR_MINIMUM_LIFECYCLE",
            "pass": False,
            "detail": f"R22 Actor lifecycle integration failure: {exc}",
        }


def r51_actor_lifecycle_guard_workspace_check(root: Path) -> dict[str, Any]:
    """Run the exact 12-guard in-memory evidence partition."""

    runner = root / "tools/validators/run_actor_lifecycle_guard_mutation_tests.py"
    expected = (
        "ACTOR_LIFECYCLE_GUARD_MUTATION_PASS: guards=12 direct=5 "
        "mutation=7 uncovered=0 product=NOT_RUN"
    )
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            raise ValueError(
                f"guard mutation runner nonzero exit {completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr or completed.stdout.strip() != expected:
            raise ValueError("guard mutation receipt-contract drift")
        return {
            "check_id": "R51_ACTOR_LIFECYCLE_GUARD_PARTITION",
            "pass": True,
            "detail": expected,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "check_id": "R51_ACTOR_LIFECYCLE_GUARD_PARTITION",
            "pass": False,
            "detail": f"R51 Actor lifecycle guard integration failure: {exc}",
        }


def r75_actor_cranelift_projection_workspace_check(root: Path) -> dict[str, Any]:
    """Bind the R75 Actor-to-Cranelift design-static projection receipt."""

    runner = root / "tools/validators/validate_actor_cranelift_projection.py"
    try:
        completed = subprocess.run(
            [sys.executable, str(runner), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        if completed.returncode != 0:
            raise ValueError(
                f"focused validator nonzero exit {completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if completed.stderr:
            raise ValueError("focused validator emitted unexpected stderr")
        receipt = _r5_strict_receipt_json(completed.stdout)
        if (
            receipt.get("result") != "PASS"
            or receipt.get("checks") != 56
            or receipt.get("acceptance_cases") != 30
            or receipt.get("mutations") != 16
            or receipt.get("trace_features") != 3
            or receipt.get("base_receipt_inputs") != 23
            or receipt.get("owner_kinds") != 7
            or receipt.get("partial_order_invariants") != 7
            or receipt.get("diagnostic_guards") != 13
            or receipt.get("post_overlay_blocked_cells") != 1242
            or receipt.get("product_support") != "NOT_RUN"
            or receipt.get("github_publication") != "NOT_AUTHORIZED_FOR_R75"
            or receipt.get("errors") != []
        ):
            raise ValueError("focused receipt-contract drift")
        return {
            "check_id": "R75_ACTOR_CRANELIFT_PROJECTION",
            "pass": True,
            "detail": json.dumps(receipt, ensure_ascii=False, sort_keys=True),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "check_id": "R75_ACTOR_CRANELIFT_PROJECTION",
            "pass": False,
            "detail": f"R75 Actor Cranelift projection integration failure: {exc}",
        }


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

    r5_ownership_check_results = r5_ownership_workspace_checks(root)
    for row in r5_ownership_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r9_diagnostic_dispatch_check_results = (
        r9_diagnostic_dispatch_workspace_checks(root)
    )
    for row in r9_diagnostic_dispatch_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r33_cleanup_budget_check_results = r33_cleanup_budget_workspace_checks(root)
    for row in r33_cleanup_budget_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    frontend_readiness_check_results = frontend_readiness_workspace_checks(root)
    for row in frontend_readiness_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r26_primary_diagnostic_check_results = (
        r26_primary_diagnostic_workspace_checks(root)
    )
    for row in r26_primary_diagnostic_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r27_grammar_topology_check_results = (
        r27_grammar_topology_workspace_checks(root)
    )
    for row in r27_grammar_topology_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r28_formatter_lsp_incremental_check_results = (
        r28_formatter_lsp_incremental_workspace_checks(root)
    )
    for row in r28_formatter_lsp_incremental_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r40_manual_grammar_count_check_results = (
        r40_manual_grammar_count_workspace_checks(root)
    )
    for row in r40_manual_grammar_count_check_results:
        check(row["pass"], row["check_id"], row["detail"])
    r41_actor_protocol_check_result = r41_actor_protocol_workspace_check(root)
    check(
        r41_actor_protocol_check_result["pass"],
        r41_actor_protocol_check_result["check_id"],
        r41_actor_protocol_check_result["detail"],
    )
    r23_actor_protocol_binding_check_result = (
        r23_actor_protocol_binding_workspace_check(root)
    )
    check(
        r23_actor_protocol_binding_check_result["pass"],
        r23_actor_protocol_binding_check_result["check_id"],
        r23_actor_protocol_binding_check_result["detail"],
    )
    r22_actor_lifecycle_check_result = r22_actor_lifecycle_workspace_check(root)
    check(
        r22_actor_lifecycle_check_result["pass"],
        r22_actor_lifecycle_check_result["check_id"],
        r22_actor_lifecycle_check_result["detail"],
    )
    r51_actor_lifecycle_guard_check_result = (
        r51_actor_lifecycle_guard_workspace_check(root)
    )
    check(
        r51_actor_lifecycle_guard_check_result["pass"],
        r51_actor_lifecycle_guard_check_result["check_id"],
        r51_actor_lifecycle_guard_check_result["detail"],
    )
    r75_actor_cranelift_projection_check_result = (
        r75_actor_cranelift_projection_workspace_check(root)
    )
    check(
        r75_actor_cranelift_projection_check_result["pass"],
        r75_actor_cranelift_projection_check_result["check_id"],
        r75_actor_cranelift_projection_check_result["detail"],
    )

    try:
        revision = tomllib.loads(
            (root / "current/language-version.toml").read_text(encoding="utf-8")
        )["spec_revision"]
    except Exception as exc:  # noqa: BLE001
        revision = ""
        check(False, "REVISION_PARITY", str(exc))
    check(
        revision
        in {
            LEGACY_REVISION,
            POST_PR16_REVISION,
            LANGUAGE_COHERENCE_REVISION,
            *CURRENT_MACHINE_REVISIONS,
        },
        "REVISION_PARITY",
        revision,
    )
    inherited_component_revision = (
        LANGUAGE_COHERENCE_REVISION
        if revision in CURRENT_MACHINE_REVISIONS
        else revision
    )

    language_coherence_contract: dict[str, Any] = {}
    if revision in {
        LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS
    }:
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
                and fixed_counts.get("features") == 723
                and fixed_counts.get("predicates") == 283
                and fixed_counts.get("predicate_fixtures") == 877
                and fixed_counts.get("no_go") == 154
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
        "spec/language.md", "spec/grammar/deeplus.dpg",
        "spec/grammar/deeplus.parser-contexts.json",
        "spec/grammar/deeplus.ebnf",
        "spec/contracts/parser-grammar-differential-r1.json",
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
        "spec/contracts/manual-grammar-count-authority-r1.json",
        "tests/fixtures/current/manual-grammar-count-authority-r1.json",
        "tools/validators/validate_manual_grammar_count_authority.py",
        "schemas/language/actor-protocol-direct-conformance-descriptor.schema.json",
        "spec/contracts/actor-protocol-direct-conformance-r1.json",
        "tests/fixtures/current/actor-protocol-direct-conformance-r1.json",
        "schemas/language/actor-protocol-binding-table.schema.json",
        "spec/contracts/actor-protocol-binding-descriptor.json",
        "tests/fixtures/current/actor-protocol-binding-table-r1.json",
        "tools/generators/bind_actor_protocol_binding_tables.py",
        "tools/validators/validate_actor_protocol_binding_descriptors.py",
        "tools/validators/validate_actor_minimum_lifecycle.py",
        "tools/validators/run_actor_lifecycle_guard_mutation_tests.py",
        "spec/contracts/actor-minimum-lifecycle-trace-r1.json",
        "tests/conformance/actor-lifecycle-guards-r1.json",
        "decisions/language/Design_Deeplus_Actor_Minimum_Lifecycle_Implementation_Handoff_R1.md",
        "spec/contracts/actor-cranelift-projection-r1.json",
        "schemas/language/actor-cranelift-projection-receipt-r1.schema.json",
        "tests/conformance/actor-cranelift-projection-r1.json",
        "tools/validators/validate_actor_cranelift_projection.py",
        "governance/reports/Design_Deeplus_R75_Actor_Cranelift_Projection_Rebase_R1.md",
        "spec/diagnostics/catalog/chunks/part-0029.json",
        "spec/diagnostics/relations/chunks/part-0009.json",
        "tests/conformance/checker-predicates/chunks/part-0031.json",
        "tools/validators/validate_actor_protocol_direct_conformance.py",
        "docs/tutorial/README.md",
        "docs/tutorial/SUMMARY.md",
        "docs/tutorial/coverage-manifest.json",
        "spec/contracts/tutorial-r1.json",
        "spec/contracts/trait-conformance-surface.json",
        "spec/contracts/ownership-type-qualifier-r1.json",
        "tests/fixtures/current/trait-conformance-surface-r1.json",
        "tests/fixtures/current/ownership-type-qualifier-r1.json",
        "schemas/language/ownership-type-qualifier-r1.schema.json",
        "schemas/language/tutorial-coverage.schema.json",
        "tools/generators/generate_tutorial.py",
        "tools/validators/run_tutorial_generator_tests.py",
        "tools/validators/run_r5_ownership_decision_mutation_tests.py",
        "tools/validators/validate_ownership_type_qualifier.py",
        "schemas/language/diagnostic-dispatch-closure-input-r1.schema.json",
        "schemas/language/diagnostic-dispatch-closure-fixtures-r1.schema.json",
        "spec/contracts/diagnostic-dispatch-closure-r1.json",
        "tests/fixtures/current/diagnostic-dispatch-closure-r1.json",
        "tests/conformance/diagnostic-dispatch-closure/catalog-metadata.json",
        "tests/conformance/diagnostic-dispatch-closure/chunks/part-0001.json",
        "tools/validators/run_diagnostic_dispatch_closure_tests.py",
        "tools/generators/generate_current_integrity.py",
        "tools/generators/current-integrity.contract.json",
        "tools/validators/run_current_integrity_generator_tests.py",
        "migration/current-document-consistency-repair-r2.3-manifest.json",
        "governance/policies/management-policy.yaml",
        "release/evidence/current-publication-m1.3-source-snapshot-receipt.json",
        "release/evidence/current-publication-m1.3-predecessor-receipt.json",
        "release/evidence/current-publication-m1.3-git-binding-receipt.json",
        "release/evidence/current-publication-m1.3-role-review-index.json",
        "decisions/language/Design_Deeplus_Ownership_Tooling_Projection_R1.md",
        "spec/contracts/ownership-tooling-obligations-r1.json",
        "schemas/language/ownership-tooling-obligations-r1.schema.json",
        "schemas/language/ownership-tooling-obligations-fixtures-r1.schema.json",
        "tests/fixtures/current/ownership-tooling-obligations-r1.json",
        "spec/diagnostics/catalog/chunks/part-0033.json",
        "tools/validators/validate_ownership_tooling_obligations.py",
        "decisions/language/Design_Deeplus_Contract_Authority_Status_Reconciliation_R1.md",
        "spec/contracts/current-contract-authority-status-r1.json",
        "schemas/language/current-contract-authority-status-r1.schema.json",
        "tools/validators/validate_current_contract_authority_status.py",
        "tools/validators/run_current_contract_authority_status_mutation_tests.py",
        "spec/traceability/implementation-target-profile-r1/catalog-metadata.json",
        "schemas/language/implementation-target-traceability-r1.schema.json",
        "tools/generators/build_implementation_target_traceability.py",
        "tools/validators/validate_implementation_target_traceability.py",
        "tools/validators/run_implementation_target_traceability_mutation_tests.py",
        "spec/contracts/implementation-target-global-trace-closure-r1.json",
        "schemas/language/implementation-target-global-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/global-trace-closure-evidence-r1.json",
        "schemas/language/implementation-target-global-trace-evidence-r1.schema.json",
        "tools/generators/build_global_implementation_target_trace_closure.py",
        "tools/validators/validate_global_implementation_target_trace_closure.py",
        "tools/validators/run_global_implementation_target_trace_closure_mutation_tests.py",
        "governance/reports/Design_Deeplus_R76_Global_Implementation_Target_Trace_Publication_Closure_R1.md",
        "release/evidence/r76-global-implementation-target-trace-publication-closure-receipt.json",
        "release/evidence/r76-global-implementation-target-trace-independent-verification.json",
        "governance/reports/Design_Deeplus_G4_Independent_Implementation_Readiness_Publication_Closure_R1.md",
        "release/evidence/g4-independent-implementation-readiness-publication-closure-receipt.json",
        "release/evidence/g4-independent-implementation-readiness-independent-verification.json",
        "decisions/language/Design_Deeplus_G4_Independent_Implementation_Readiness_Audit_R1.md",
        "spec/contracts/implementation-readiness-g4-audit-r1.json",
        "schemas/language/implementation-readiness-g4-audit-r1.schema.json",
        "tools/validators/validate_implementation_readiness_g4_audit.py",
        "spec/traceability/implementation-target-profile-r1/scalar-numeric-fixed-operator-evidence-r1.json",
        "schemas/language/scalar-numeric-fixed-operator-evidence-r1.schema.json",
        "tools/validators/validate_scalar_numeric_fixed_operator_trace.py",
        "tools/validators/run_scalar_numeric_fixed_operator_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R54_Scalar_Numeric_Fixed_Operator_Trace_Closure_R1.md",
        "spec/contracts/lexical-trivia-source-root-attachment-r1.json",
        "schemas/language/lexical-trivia-source-root-attachment-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json",
        "schemas/language/lexical-trivia-source-root-evidence-r1.schema.json",
        "tools/generators/build_lexical_trivia_source_root_evidence.py",
        "tools/validators/validate_lexical_trivia_source_root_trace.py",
        "tools/validators/run_lexical_trivia_source_root_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R55_Lexical_Trivia_Source_Root_Closure_R1.md",
        "spec/contracts/numeric-array-shape-inferred-literal-r1.json",
        "schemas/language/numeric-array-shape-inferred-literal-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json",
        "schemas/language/numeric-array-shape-inferred-evidence-r1.schema.json",
        "tools/generators/build_numeric_array_shape_inferred_evidence.py",
        "tools/validators/validate_numeric_array_shape_inferred_trace.py",
        "tools/validators/run_numeric_array_shape_inferred_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R56_NumericArray_Shape_Inferred_Trace_Closure_R1.md",
        "spec/contracts/unified-call-tilde-trace-closure-r1.json",
        "schemas/language/unified-call-tilde-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json",
        "schemas/language/unified-call-tilde-evidence-r1.schema.json",
        "tools/generators/build_unified_call_tilde_evidence.py",
        "tools/validators/validate_unified_call_tilde_trace.py",
        "tools/validators/run_unified_call_tilde_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R57_Unified_Call_Tilde_Trace_Closure_R1.md",
        "spec/contracts/member-visibility-trace-closure-r1.json",
        "schemas/language/member-visibility-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json",
        "schemas/language/member-visibility-evidence-r1.schema.json",
        "tools/generators/build_member_visibility_evidence.py",
        "tools/validators/validate_member_visibility_trace.py",
        "tools/validators/run_member_visibility_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R58_Member_Visibility_Trace_Closure_R1.md",
        "spec/contracts/pattern-dynamic-lowering-trace-closure-r1.json",
        "schemas/language/pattern-dynamic-lowering-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/pattern-dynamic-lowering-evidence-r1.json",
        "schemas/language/pattern-dynamic-lowering-evidence-r1.schema.json",
        "tools/generators/build_pattern_dynamic_lowering_evidence.py",
        "tools/validators/validate_pattern_dynamic_lowering_trace.py",
        "tools/validators/run_pattern_dynamic_lowering_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R59_Pattern_Dynamic_Lowering_Trace_Closure_R1.md",
        "spec/contracts/pattern-match-ownership-split-trace-closure-r1.json",
        "schemas/language/pattern-match-ownership-split-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/pattern-match-ownership-split-evidence-r1.json",
        "schemas/language/pattern-match-ownership-split-evidence-r1.schema.json",
        "tools/generators/build_pattern_match_ownership_split_evidence.py",
        "tools/validators/validate_pattern_match_ownership_split_trace.py",
        "tools/validators/run_pattern_match_ownership_split_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R60_Pattern_Match_Ownership_Split_Trace_Closure_R1.md",
        "spec/contracts/pattern-clause-exhaustiveness-trace-closure-r1.json",
        "schemas/language/pattern-clause-exhaustiveness-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/pattern-clause-exhaustiveness-evidence-r1.json",
        "schemas/language/pattern-clause-exhaustiveness-evidence-r1.schema.json",
        "tools/generators/build_pattern_clause_exhaustiveness_evidence.py",
        "tools/validators/validate_pattern_clause_exhaustiveness_trace.py",
        "tools/validators/run_pattern_clause_exhaustiveness_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R61_Pattern_Clause_Exhaustiveness_Trace_Closure_R1.md",
        "spec/contracts/trait-qualified-associated-static-selection-trace-closure-r1.json",
        "schemas/language/trait-qualified-associated-static-selection-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/trait-qualified-associated-static-selection-evidence-r1.json",
        "schemas/language/trait-qualified-associated-static-selection-evidence-r1.schema.json",
        "tools/generators/build_trait_qualified_associated_static_selection_evidence.py",
        "tools/validators/validate_trait_qualified_associated_static_selection_trace.py",
        "tools/validators/run_trait_qualified_associated_static_selection_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R62_Trait_Qualified_Associated_Static_Selection_Dynamic_Trace_Closure_R1.md",
        "spec/contracts/associated-requirement-phase-a-trace-closure-r1.json",
        "schemas/language/associated-requirement-phase-a-trace-closure-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/associated-requirement-phase-a-evidence-r1.json",
        "schemas/language/associated-requirement-phase-a-evidence-r1.schema.json",
        "tools/validators/validate_associated_requirement_phase_a_trace_closure.py",
        "tools/validators/run_associated_requirement_phase_a_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R64_Associated_Requirement_Phase_A_Trace_Closure_R1.md",
        "spec/traceability/implementation-target-profile-r1/associated-requirement-ast-diagnostic-parity-evidence-r1.json",
        "schemas/language/associated-requirement-ast-diagnostic-parity-evidence-r1.schema.json",
        "tools/validators/validate_associated_requirement_ast_diagnostic_parity.py",
        "tools/validators/run_associated_requirement_ast_diagnostic_parity_mutation_tests.py",
        "decisions/language/Design_Deeplus_R65_Associated_Requirement_AST_Diagnostic_Parity_R1.md",
        "spec/traceability/implementation-target-profile-r1/responsibility-identity-dynamic-trace-evidence-r1.json",
        "schemas/language/responsibility-identity-dynamic-trace-evidence-r1.schema.json",
        "tools/validators/validate_responsibility_identity_dynamic_trace.py",
        "tools/validators/run_responsibility_identity_dynamic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R66_Responsibility_Identity_Dynamic_Trace_Closure_R1.md",
        "spec/traceability/implementation-target-profile-r1/closure-capture-dynamic-trace-evidence-r1.json",
        "schemas/language/closure-capture-dynamic-trace-evidence-r1.schema.json",
        "tools/validators/validate_closure_capture_dynamic_trace.py",
        "tools/validators/run_closure_capture_dynamic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R67_Closure_Capture_Dynamic_Trace_Closure_R1.md",
        "spec/contracts/region-lifetime-mir-projection-r1.json",
        "schemas/language/region-lifetime-mir-projection-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/region-lifetime-dynamic-trace-evidence-r1.json",
        "schemas/language/region-lifetime-dynamic-trace-evidence-r1.schema.json",
        "tools/validators/validate_region_lifetime_dynamic_trace.py",
        "tools/validators/run_region_lifetime_dynamic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R68_Region_Lifetime_Dynamic_Trace_Closure_R1.md",
        "spec/contracts/managed-reference-dynamic-projection-r1.json",
        "schemas/language/managed-reference-dynamic-projection-r1.schema.json",
        "schemas/language/managed-reference-runtime-root-receipt-r1.schema.json",
        "tests/fixtures/current/managed-reference-dynamic-projection-r1.json",
        "schemas/language/managed-reference-dynamic-projection-fixtures-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/managed-reference-dynamic-trace-evidence-r1.json",
        "schemas/language/managed-reference-dynamic-trace-evidence-r1.schema.json",
        "tools/validators/validate_managed_reference_dynamic_trace.py",
        "tools/validators/run_managed_reference_dynamic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R69_Managed_Reference_Dynamic_Trace_Closure_R1.md",
        "spec/contracts/static-runtime-member-boundary-trace-closure-r1.json",
        "schemas/language/static-runtime-member-boundary-trace-closure-r1.schema.json",
        "tests/fixtures/current/static-runtime-member-boundary-trace-closure-r1.json",
        "schemas/language/static-runtime-member-boundary-trace-closure-fixtures-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/static-runtime-member-boundary-evidence-r1.json",
        "schemas/language/static-runtime-member-boundary-evidence-r1.schema.json",
        "tools/validators/validate_static_runtime_member_boundary_trace.py",
        "tools/validators/run_static_runtime_member_boundary_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R70_Static_Runtime_Member_Boundary_Trace_Closure_R1.md",
        "spec/contracts/method-extension-resolution-dynamic-trace-closure-r1.json",
        "schemas/language/method-extension-resolution-dynamic-trace-closure-r1.schema.json",
        "tests/fixtures/current/method-extension-resolution-dynamic-trace-closure-r1.json",
        "schemas/language/method-extension-resolution-dynamic-trace-closure-fixtures-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/method-extension-resolution-dynamic-evidence-r1.json",
        "schemas/language/method-extension-resolution-dynamic-evidence-r1.schema.json",
        "tools/validators/validate_method_extension_resolution_dynamic_trace.py",
        "tools/validators/run_method_extension_resolution_dynamic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R71_Method_Extension_Resolution_Dynamic_Trace_Closure_R1.md",
        "spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json",
        "schemas/language/member-extension-collision-dynamic-trace-closure-r1.schema.json",
        "tests/fixtures/current/member-extension-collision-dynamic-trace-closure-r1.json",
        "schemas/language/member-extension-collision-dynamic-trace-closure-fixtures-r1.schema.json",
        "spec/traceability/implementation-target-profile-r1/member-extension-collision-dynamic-evidence-r1.json",
        "schemas/language/member-extension-collision-dynamic-evidence-r1.schema.json",
        "tools/validators/validate_member_extension_collision_dynamic_trace.py",
        "tools/validators/run_member_extension_collision_dynamic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R72_Member_Extension_Collision_Dynamic_Trace_Closure_R1.md",
        "spec/traceability/implementation-target-profile-r1/member-extension-collision-conformance-evidence-r1.json",
        "schemas/language/member-extension-collision-conformance-evidence-r1.schema.json",
        "tools/validators/validate_member_extension_collision_conformance_trace.py",
        "tools/validators/run_member_extension_collision_conformance_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R73_Member_Extension_Collision_Conformance_Trace_Closure_R1.md",
        "tools/validators/validate_member_extension_collision_diagnostic_trace.py",
        "tools/validators/run_member_extension_collision_diagnostic_trace_mutation_tests.py",
        "decisions/language/Design_Deeplus_R74_Member_Extension_Collision_Diagnostic_Trace_Closure_R1.md",
        "spec/traceability/implementation-target-profile-r1/actor-cranelift-projection-dynamic-evidence-r1.json",
        "schemas/language/actor-cranelift-projection-dynamic-evidence-r1.schema.json",
        "tools/validators/validate_trait_associated_static_stale_diagnostic_removal.py",
        "tools/validators/run_trait_associated_static_stale_diagnostic_removal_mutation_tests.py",
    ]
    if revision == POST_PR16_REVISION:
        required.extend([
            "tools/generators/generate_post_pr16_current_integrity.py",
            "tools/generators/post-pr16-current-integrity.contract.json",
            "tools/validators/run_post_pr16_current_integrity_tests.py",
        ])
    elif revision in {
        LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS
    }:
        required.extend([
            "tools/generators/generate_language_coherence_current_integrity.py",
            LANGUAGE_COHERENCE_CONTRACT_REL,
        ])
    if revision in CURRENT_MACHINE_REVISIONS:
        required.extend([
            "decisions/language/Design_Deeplus_HIR_MIR_Machine_Contract_R1.md",
            "decisions/language/Design_Deeplus_Closure_Capture_Plan_R1.md",
            "schemas/language/canonical-hir-h1.schema.json",
            "schemas/language/continuation-interface-fixtures-r1.schema.json",
            "schemas/language/continuation-interface-r1.schema.json",
            "schemas/language/continuation-receipt-r1.schema.json",
            "schemas/language/deeplus-mir.schema.json",
            "schemas/language/deferred-call-plan-input-r1.schema.json",
            "schemas/language/hir-mir-lowering-row.schema.json",
            "schemas/language/hir-mir-machine-contract-fixtures.schema.json",
            "schemas/language/mir-capability-receipt.schema.json",
            "schemas/language/suspension-frame-responsibility.schema.json",
            "spec/contracts/hir-h1-current-mir-bridge.json",
            "spec/contracts/continuation-interface-r1.json",
            "spec/contracts/hir-h1-identity-catalog.json",
            "spec/contracts/hir-mir-lowering-registry.json",
            "spec/contracts/hir-mir-machine-diagnostic-contract.json",
            "spec/contracts/mir-machine-registry.json",
            "spec/contracts/suspension-frame-responsibility-r1.json",
            "spec/diagnostics/catalog/catalog-metadata.json",
            "spec/diagnostics/catalog/chunks/part-0028.json",
            "tests/fixtures/current/hir-mir-machine-contract-r1.json",
            "tests/fixtures/current/continuation-interface-r1.json",
            "tests/fixtures/current/suspension-frame-responsibility-r1.json",
            "tools/generators/rebind_continuation_interface.py",
            "tools/generators/refresh_source_tree_manifest.py",
            "tools/validators/validate_hir_mir_machine_contract.py",
            "tools/validators/validate_continuation_interface.py",
            "decisions/language/Design_Deeplus_Internal_Runtime_ABI_R1.md",
            "schemas/language/internal-runtime-abi-r1.schema.json",
            "schemas/language/runtime-helper-registry-r1.schema.json",
            "schemas/language/internal-runtime-target-projection-r1.schema.json",
            "schemas/language/internal-runtime-artifact-binding-receipt-r1.schema.json",
            "schemas/language/internal-runtime-abi-fixtures-r1.schema.json",
            "spec/contracts/internal-runtime-abi-r1.json",
            "spec/contracts/runtime-helper-registry-r1.json",
            "spec/features/catalog/chunks/part-0026.json",
            "spec/diagnostics/catalog/chunks/part-0030.json",
            "tests/fixtures/current/internal-runtime-abi-r1.json",
            "tools/validators/validate_internal_runtime_abi.py",
        ])
    required.append("release/candidate-state.json" if args.candidate else "current/current-pointer.json")
    for rel in required:
        check((root / rel).is_file(), "REQUIRED_PATH", rel)
    check(not (root / ("current/current-pointer.json" if args.candidate else "release/candidate-state.json")).exists(),
          "RELEASE_STATE_EXCLUSIVE", "candidate and published current states are mutually exclusive")

    r69_validator = (
        root / "tools/validators/validate_managed_reference_dynamic_trace.py"
    )
    r69_process = subprocess.run(
        [sys.executable, str(r69_validator), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r69_detail = (
        r69_process.stdout.strip()
        if r69_process.returncode == 0
        else r69_process.stderr.strip() or r69_process.stdout.strip()
    )
    check(
        r69_process.returncode == 0,
        "R69_MANAGED_REFERENCE_DYNAMIC_TRACE",
        r69_detail[-4000:],
    )

    r69_mutation_runner = (
        root
        / "tools/validators/run_managed_reference_dynamic_trace_mutation_tests.py"
    )
    r69_mutation_process = subprocess.run(
        [sys.executable, str(r69_mutation_runner)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r69_mutation_detail = (
        r69_mutation_process.stdout.strip()
        if r69_mutation_process.returncode == 0
        else r69_mutation_process.stderr.strip()
        or r69_mutation_process.stdout.strip()
    )
    check(
        r69_mutation_process.returncode == 0,
        "R69_MANAGED_REFERENCE_DYNAMIC_TRACE_MUTATIONS",
        r69_mutation_detail[-4000:],
    )

    r70_validator = (
        root / "tools/validators/validate_static_runtime_member_boundary_trace.py"
    )
    r70_process = subprocess.run(
        [sys.executable, str(r70_validator), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r70_detail = (
        r70_process.stdout.strip()
        if r70_process.returncode == 0
        else r70_process.stderr.strip() or r70_process.stdout.strip()
    )
    check(
        r70_process.returncode == 0,
        "R70_STATIC_RUNTIME_MEMBER_BOUNDARY_TRACE",
        r70_detail[-4000:],
    )

    r70_mutation_runner = (
        root
        / "tools/validators/run_static_runtime_member_boundary_trace_mutation_tests.py"
    )
    r70_mutation_process = subprocess.run(
        [sys.executable, str(r70_mutation_runner), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r70_mutation_detail = (
        r70_mutation_process.stdout.strip()
        if r70_mutation_process.returncode == 0
        else r70_mutation_process.stderr.strip()
        or r70_mutation_process.stdout.strip()
    )
    check(
        r70_mutation_process.returncode == 0,
        "R70_STATIC_RUNTIME_MEMBER_BOUNDARY_TRACE_MUTATIONS",
        r70_mutation_detail[-4000:],
    )

    r71_validator = (
        root
        / "tools/validators/validate_method_extension_resolution_dynamic_trace.py"
    )
    r71_process = subprocess.run(
        [sys.executable, str(r71_validator), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r71_detail = (
        r71_process.stdout.strip()
        if r71_process.returncode == 0
        else r71_process.stderr.strip() or r71_process.stdout.strip()
    )
    check(
        r71_process.returncode == 0,
        "R71_METHOD_EXTENSION_RESOLUTION_DYNAMIC_TRACE",
        r71_detail[-4000:],
    )

    r71_mutation_runner = (
        root
        / "tools/validators/run_method_extension_resolution_dynamic_trace_mutation_tests.py"
    )
    r71_mutation_process = subprocess.run(
        [sys.executable, str(r71_mutation_runner), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r71_mutation_detail = (
        r71_mutation_process.stdout.strip()
        if r71_mutation_process.returncode == 0
        else r71_mutation_process.stderr.strip()
        or r71_mutation_process.stdout.strip()
    )
    check(
        r71_mutation_process.returncode == 0,
        "R71_METHOD_EXTENSION_RESOLUTION_DYNAMIC_TRACE_MUTATIONS",
        r71_mutation_detail[-4000:],
    )

    r72_validator = (
        root / "tools/validators/validate_member_extension_collision_dynamic_trace.py"
    )
    r72_process = subprocess.run(
        [sys.executable, str(r72_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r72_detail = (
        r72_process.stdout.strip()
        if r72_process.returncode == 0
        else r72_process.stderr.strip() or r72_process.stdout.strip()
    )
    check(
        r72_process.returncode == 0,
        "R72_MEMBER_EXTENSION_COLLISION_DYNAMIC_TRACE",
        r72_detail[-4000:],
    )

    r72_mutation_runner = (
        root
        / "tools/validators/run_member_extension_collision_dynamic_trace_mutation_tests.py"
    )
    r72_mutation_process = subprocess.run(
        [sys.executable, str(r72_mutation_runner), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r72_mutation_detail = (
        r72_mutation_process.stdout.strip()
        if r72_mutation_process.returncode == 0
        else r72_mutation_process.stderr.strip()
        or r72_mutation_process.stdout.strip()
    )
    check(
        r72_mutation_process.returncode == 0,
        "R72_MEMBER_EXTENSION_COLLISION_DYNAMIC_TRACE_MUTATIONS",
        r72_mutation_detail[-4000:],
    )

    r73_validator = (
        root / "tools/validators/validate_member_extension_collision_conformance_trace.py"
    )
    r73_process = subprocess.run(
        [sys.executable, str(r73_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r73_detail = (
        r73_process.stdout.strip()
        if r73_process.returncode == 0
        else r73_process.stderr.strip() or r73_process.stdout.strip()
    )
    check(
        r73_process.returncode == 0,
        "R73_MEMBER_EXTENSION_COLLISION_CONFORMANCE_TRACE",
        r73_detail[-4000:],
    )

    r73_mutation_runner = (
        root
        / "tools/validators/run_member_extension_collision_conformance_trace_mutation_tests.py"
    )
    r73_mutation_process = subprocess.run(
        [sys.executable, str(r73_mutation_runner), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r73_mutation_detail = (
        r73_mutation_process.stdout.strip()
        if r73_mutation_process.returncode == 0
        else r73_mutation_process.stderr.strip()
        or r73_mutation_process.stdout.strip()
    )
    check(
        r73_mutation_process.returncode == 0,
        "R73_MEMBER_EXTENSION_COLLISION_CONFORMANCE_TRACE_MUTATIONS",
        r73_mutation_detail[-4000:],
    )

    r74_validator = (
        root / "tools/validators/validate_member_extension_collision_diagnostic_trace.py"
    )
    r74_process = subprocess.run(
        [sys.executable, str(r74_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r74_detail = (
        r74_process.stdout.strip()
        if r74_process.returncode == 0
        else r74_process.stderr.strip() or r74_process.stdout.strip()
    )
    check(
        r74_process.returncode == 0,
        "R74_MEMBER_EXTENSION_COLLISION_DIAGNOSTIC_TRACE",
        r74_detail[-4000:],
    )

    r74_mutation_runner = (
        root
        / "tools/validators/run_member_extension_collision_diagnostic_trace_mutation_tests.py"
    )
    r74_mutation_process = subprocess.run(
        [sys.executable, str(r74_mutation_runner), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r74_mutation_detail = (
        r74_mutation_process.stdout.strip()
        if r74_mutation_process.returncode == 0
        else r74_mutation_process.stderr.strip()
        or r74_mutation_process.stdout.strip()
    )
    check(
        r74_mutation_process.returncode == 0,
        "R74_MEMBER_EXTENSION_COLLISION_DIAGNOSTIC_TRACE_MUTATIONS",
        r74_mutation_detail[-4000:],
    )

    r76_validator = (
        root
        / "tools/validators/validate_global_implementation_target_trace_closure.py"
    )
    r76_process = subprocess.run(
        [sys.executable, str(r76_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r76_detail = (
        r76_process.stdout.strip()
        if r76_process.returncode == 0
        else r76_process.stderr.strip() or r76_process.stdout.strip()
    )
    check(
        r76_process.returncode == 0,
        "R76_GLOBAL_IMPLEMENTATION_TARGET_TRACE_CLOSURE",
        r76_detail[-4000:],
    )

    r77_target_validator = (
        root / "tools/validators/validate_implementation_target_traceability.py"
    )
    r77_target_process = subprocess.run(
        [sys.executable, str(r77_target_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r77_target_detail = (
        r77_target_process.stdout.strip()
        if r77_target_process.returncode == 0
        else r77_target_process.stderr.strip() or r77_target_process.stdout.strip()
    )
    check(
        r77_target_process.returncode == 0,
        "R77_CURRENT_IMPLEMENTATION_TARGET_REBIND",
        r77_target_detail[-4000:],
    )

    r77_validator = root / "tools/validators/validate_integrated_surface_atomic_cutover_r77.py"
    r77_process = subprocess.run(
        [sys.executable, str(r77_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r77_detail = (
        r77_process.stdout.strip()
        if r77_process.returncode == 0
        else r77_process.stderr.strip() or r77_process.stdout.strip()
    )
    check(
        r77_process.returncode == 0,
        "R77_CURRENT_SURFACE_PUBLICATION_POLICY",
        r77_detail[-4000:],
    )

    g4_validator = root / "tools/validators/validate_implementation_readiness_g4_audit.py"
    g4_process = subprocess.run(
        [sys.executable, str(g4_validator), "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    g4_detail = (
        g4_process.stdout.strip()
        if g4_process.returncode == 0
        else g4_process.stderr.strip() or g4_process.stdout.strip()
    )
    check(
        g4_process.returncode == 0,
        "G4_INDEPENDENT_IMPLEMENTATION_READINESS_AUDIT",
        g4_detail[-4000:],
    )

    r76_mutation_runner = (
        root
        / "tools/validators/run_global_implementation_target_trace_closure_mutation_tests.py"
    )
    r76_mutation_process = subprocess.run(
        [sys.executable, str(r76_mutation_runner)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    r76_mutation_detail = (
        r76_mutation_process.stdout.strip()
        if r76_mutation_process.returncode == 0
        else r76_mutation_process.stderr.strip()
        or r76_mutation_process.stdout.strip()
    )
    check(
        r76_mutation_process.returncode == 0,
        "R76_GLOBAL_IMPLEMENTATION_TARGET_TRACE_CLOSURE_MUTATIONS",
        r76_mutation_detail[-4000:],
    )

    if revision in CURRENT_MACHINE_REVISIONS:
        r10_validator = (
            root / "tools/validators/validate_hir_mir_machine_contract.py"
        )
        process = subprocess.run(
            [sys.executable, str(r10_validator), "--root", str(root)],
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
            "R10_HIR_MIR_MACHINE_CONTRACT",
            detail[-4000:],
        )
        r38_validator = root / "tools/validators/validate_continuation_interface.py"
        process = subprocess.run(
            [sys.executable, str(r38_validator), "--root", str(root)],
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
            "R38_CONTINUATION_INTERFACE",
            detail[-4000:],
        )
        r38_rebinder = root / "tools/generators/rebind_continuation_interface.py"
        process = subprocess.run(
            [sys.executable, str(r38_rebinder), "--root", str(root), "--check"],
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
            "R38_CONTINUATION_INTERFACE_REBIND_BYTES",
            detail[-4000:],
        )

        r37_validator = root / "tools/validators/validate_internal_runtime_abi.py"
        process = subprocess.run(
            [sys.executable, str(r37_validator), "--root", str(root)],
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
            "R37_INTERNAL_RUNTIME_ABI",
            detail[-4000:],
        )

        r32_validator = root / "tools/validators/validate_deferred_call_plan.py"
        process = subprocess.run(
            [sys.executable, str(r32_validator), "--root", str(root)],
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
            "R32_DEFERRED_CALL_PLAN",
            detail[-4000:],
        )

        r34_validator = root / "tools/validators/validate_loan_close_operation.py"
        r34_process = subprocess.run(
            [sys.executable, str(r34_validator), "--root", str(root)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        r34_detail = (
            r34_process.stdout.strip()
            if r34_process.returncode == 0
            else (r34_process.stderr.strip() or r34_process.stdout.strip())
        )
        check(
            r34_process.returncode == 0,
            "R34_LOAN_CLOSE_OPERATION",
            r34_detail[-4000:],
        )

        r35_validator = (
            root / "tools/validators/validate_shared_mutex_payload_bound.py"
        )
        r35_process = subprocess.run(
            [sys.executable, str(r35_validator), "--root", str(root)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        r35_detail = (
            r35_process.stdout.strip()
            if r35_process.returncode == 0
            else (r35_process.stderr.strip() or r35_process.stdout.strip())
        )
        check(
            r35_process.returncode == 0,
            "R35_SHARED_MUTEX_PAYLOAD_BOUND",
            r35_detail[-4000:],
        )

    ownership_tooling_validator = (
        root / "tools/validators/validate_ownership_tooling_obligations.py"
    )
    if ownership_tooling_validator.is_file():
        process = subprocess.run(
            [
                sys.executable,
                str(ownership_tooling_validator),
                "--root",
                str(root),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="strict",
            timeout=120,
        )
        detail = process.stdout.strip() if process.returncode == 0 else (
            process.stderr.strip() or process.stdout.strip()
        )
        try:
            receipt = json.loads(process.stdout)
        except (json.JSONDecodeError, TypeError):
            receipt = {}
        receipt_ok = (
            process.returncode == 0
            and not process.stderr
            and receipt.get("schema")
            == "deeplus.r39-ownership-tooling-validation/r1"
            and receipt.get("result") == "PASS"
            and receipt.get("evidence_level") == "E2_STATIC_CLOSURE"
            and receipt.get("check_scope")
            == "R39_OWNERSHIP_TOOLING_OBLIGATIONS_EXACT"
            and receipt.get("check_count") == 37
            and receipt.get("passed_check_count") == 37
            and receipt.get("failed") == 0
            and receipt.get("mutation_count") == 10
            and receipt.get("rejected_mutation_count") == 10
            and receipt.get("semantic_change_count") == 0
            and receipt.get("product_execution") == "NOT_RUN"
            and receipt.get("errors") == []
        )
        check(
            receipt_ok,
            "R39_OWNERSHIP_TOOLING_OBLIGATIONS",
            detail[-4000:],
        )

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

    parser_grammar_validator = (
        root / "tools/validators/validate_parser_grammar_differential.py"
    )
    if parser_grammar_validator.is_file():
        process = subprocess.run(
            [
                sys.executable,
                str(parser_grammar_validator),
                "--root",
                str(root),
                "--mutations",
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
            "PARSER_GRAMMAR_DIFFERENTIAL_CHECK",
            detail[-4000:],
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

    if revision in {LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS}:
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
    current_integrity_generator = (
        root / current_integrity_generator_rel
        if current_integrity_generator_rel is not None else None
    )
    if current_integrity_generator is not None and current_integrity_generator.is_file():
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
    for condition, code, detail in r4_nrm_contract_results(root):
        check(condition, code, detail)
    for condition, code, detail in r4_nrm_integrated_contract_results(root):
        check(condition, code, detail)
    for condition, code, detail in r4_nrm_mechanical_self_test_results():
        check(condition, code, detail)
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
        if revision in CURRENT_MACHINE_REVISIONS:
            return relative in R10_SEMANTIC_DELTA_PATHS or relative in R38_SEMANTIC_DELTA_PATHS or (
                language_identity_exemptions.get(relative) == current_sha256
            )
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
    check(len(reconstructed) == 14, "CATALOG_COUNT", str(len(reconstructed)))

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
        "grammar": len(
            re.findall(
                r"(?m)^[A-Za-z_][A-Za-z0-9_]*[ \t]*::=",
                (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8"),
            )
        ),
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
        if revision in {LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS}
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
        if revision in CURRENT_MACHINE_REVISIONS and rel == "spec/frontend/frontend-model.json":
            continue
        if revision in {LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS}:
            if rel == "spec/grammar/deeplus.ebnf" and (
                "spec/grammar/deeplus.dpg" in successor_semantic_files
            ):
                for grammar_rel in (
                    "spec/grammar/deeplus.dpg",
                    "spec/grammar/deeplus.parser-contexts.json",
                ):
                    check(
                        successor_semantic_files.get(grammar_rel)
                        == file_sha(root / grammar_rel),
                        "SUCCESSOR_SEMANTIC_FILE_IDENTITY",
                        grammar_rel,
                    )
                continue
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
        numeric_contract.get("revision") == inherited_component_revision
        and numeric_fixture.get("revision") == inherited_component_revision
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
        companion_contract.get("revision") == inherited_component_revision
        and companion_fixture.get("revision") == inherited_component_revision
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
    hir_bridge_component_revision = (
        R10_HIR_MIR_REVISION
        if revision in FRONTEND_SUCCESSOR_REVISIONS
        else revision
    )
    check(
        hir_contract.get("revision") == hir_bridge_component_revision
        and hir_fixture.get("revision") == hir_bridge_component_revision
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
        cranelift_contract.get("revision") == inherited_component_revision
        and cranelift_fixture.get("revision") == inherited_component_revision
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
        and len(cranelift_contract.get("required_receipt_inputs", [])) == 23
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
        and cranelift_managed.get("memory_profile_id")
        == "STW_NONMOVING_TRACING_WITH_OPAQUE_STABLE_HANDLES_R1"
        and cranelift_managed.get("managed_memory_plan_schema")
        == "deeplus.managed-memory-plan/r1"
        and cranelift_managed.get("missing_or_invalid_plan")
        == "BLOCK_NATIVE_LOWERING"
        and cranelift_managed.get("native_root_strategy")
        == "EXPLICIT_SHADOW_ROOT_FRAMES"
        and len(
            cranelift_managed.get(
                "required_native_projection_receipt_fields", []
            )
        )
        == 13
        and cranelift_managed.get("raw_pointer_fallback") is False
        and cranelift_debug.get("separate_debug_digest") is True
        and cranelift_debug.get("debug_info_is_semantic_authority") is False
        and cranelift_contract.get("internal_runtime_abi_guard", {}).get(
            "logical_abi_id"
        ) == "RuntimeAbiId:DEEPLUS_INTERNAL_RUNTIME_ABI_R1"
        and cranelift_contract.get("internal_runtime_abi_guard", {}).get(
            "outcome_tags"
        ) == ["NORMAL", "ERROR", "DEFECT", "CANCELLATION"]
        and cranelift_contract.get("internal_runtime_abi_guard", {}).get(
            "exact_digest_compatibility_only"
        ) is True
        and cranelift_contract.get("internal_runtime_abi_guard", {}).get(
            "host_unwind_across_boundary"
        ) is False
        and cranelift_contract.get("internal_runtime_abi_guard", {}).get(
            "canonical_promotion_ready"
        ) is True
        and (root / "crates/deeplus-codegen-cranelift/Cargo.toml").is_file(),
        "CRANELIFT_HIR_MIR_PROJECTION_BOUNDARY",
        (
            f"toolchain={cranelift_toolchain} hir={cranelift_hir} "
            f"module={cranelift_projection.get('module_kinds')}"
        ),
    )

    r36_validator = root / "tools/validators/validate_managed_reference_memory_profile.py"
    r36_process = subprocess.run(
        [sys.executable, str(r36_validator), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    r36_detail = (
        r36_process.stdout.strip()
        if r36_process.returncode == 0
        else (r36_process.stderr.strip() or r36_process.stdout.strip())
    )
    check(
        r36_process.returncode == 0,
        "R36_MANAGED_REFERENCE_MEMORY_PROFILE",
        r36_detail[-4000:],
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
        and len(psm_contract.get("stable_design", [])) == 21
        and len(psm_contract.get("preview_gated", [])) == 13
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
        == 18
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
        voi_contract.get("revision") == inherited_component_revision
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
        and warning_example.get("expected_warnings") == [],
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
        trn.get("revision") == inherited_component_revision
        and trn_contract.get("revision") == inherited_component_revision
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
        edc.get("revision") == inherited_component_revision
        and edc_contract.get("revision") == inherited_component_revision
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
        ) == "public trait#operator Eq<Rhs> { +def equals.(borrow rhs: Rhs) -> Bool throws Never effects {}; }"
        and edc_contract.get("trait_contracts", {}).get("Ord<Rhs>", {}).get(
            "canonical_signature"
        ) == "public trait#operator Ord<Rhs>\nderives Eq<Rhs> {\n    +def compare.(borrow rhs: Rhs) -> Int throws Never effects {}\n}"
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
        ) == "public trait#interpolation Display { +def display.() -> String throws Never effects {}; }"
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
        lstc.get("revision") == inherited_component_revision
        and lstc_contract.get("revision") == inherited_component_revision
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
    mutable_list_signatures = current_prelude.get("MutableList<T>", {}).get(
        "signatures", []
    )
    mutable_list_edit_operations = {
        "insertBefore", "insertAfter", "prepend", "append",
        "insertAllBefore", "insertAllAfter", "prependAll", "appendAll",
        "removeAt", "removeRange", "removeSelected", "popFirst", "popLast",
    }
    check(
        mutable_list_signatures[:3]
        == [
            "prelude intrinsic mutable resource type MutableList<T>",
            "prelude intrinsic def MutableList::snapshot<T>(borrow self: MutableList<T>) -> ListSnapshot<T> throws AllocationError effects allocate",
            "prelude intrinsic def#consume MutableList::freeze<T>(move self: MutableList<T>) -> FrozenList<T> throws AllocationError effects allocate",
        ]
        and len(mutable_list_signatures) == 16
        and all(
            any(f"MutableList::{operation}<T>" in signature for signature in mutable_list_signatures)
            for operation in mutable_list_edit_operations
        )
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
        "TRN-R1-NEG-058": "PATTERN_PIN_REQUIRES_STABLE_VALUE",
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
        "PCTX-ASSERTIVE-LET", "PCTX-ASSERTIVE-VAR",
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
    decision_index_text = (
        root / "current/decision-index.yaml"
    ).read_text(encoding="utf-8")
    indexed_decision_paths = re.findall(
        r"^  - path: (decisions/language/\S+)$",
        decision_index_text,
        re.MULTILINE,
    )
    indexed_decision_rows = re.findall(
        (
            r"^  - path: (decisions/language/\S+)\r?\n"
            r"    authority: (\S+)$"
        ),
        decision_index_text,
        re.MULTILINE,
    )
    expected_decision_rows = [
        (
            relative,
            (
                "imported_current_decisions"
                if relative == "decisions/language/current-decisions.json"
                else "current_user_delegated_design_adoption"
            ),
        )
        for relative in CURRENT_DECISION_INDEX_PATHS
        + ([R10_DECISION_PATH] if revision in CURRENT_MACHINE_REVISIONS else [])
        + (R11_R19_DECISION_PATHS if revision in FRONTEND_SUCCESSOR_REVISIONS else [])
        + (
            R47_DECISION_PATHS
            if revision in {
                R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
                R74_IMPLEMENTATION_READINESS_REVISION,
                R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
                R76_GLOBAL_TRACE_CLOSURE_REVISION,
                G4_INDEPENDENT_READINESS_REVISION,
                R77_PUBLICATION_POLICY_CLOSURE_REVISION,
            }
            else []
        )
        + (
            R48_R74_DECISION_PATHS
            if revision in {
                R74_IMPLEMENTATION_READINESS_REVISION,
                R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
                R76_GLOBAL_TRACE_CLOSURE_REVISION,
                G4_INDEPENDENT_READINESS_REVISION,
                R77_PUBLICATION_POLICY_CLOSURE_REVISION,
            }
            else []
        )
        + ([R76_DECISION_PATH] if revision in {R76_GLOBAL_TRACE_CLOSURE_REVISION, G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION} else [])
        + ([G4_DECISION_PATH] if revision in {G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION} else [])
    ]
    indexed_governance_paths = re.findall(
        r"^  - (governance/\S+)$",
        decision_index_text,
        re.MULTILINE,
    )
    expected_governance_paths = [
        "governance/policies/management-policy.yaml",
        AUTHORITY_TRANSITION_REPORT,
        R4_PUBLICATION_CLOSURE_REPORT,
        R8_PUBLICATION_CLOSURE_REPORT,
        R9_PUBLICATION_CLOSURE_REPORT,
    ] + (
        [R10_PUBLICATION_CLOSURE_REPORT]
        if revision in CURRENT_MACHINE_REVISIONS
        else []
    ) + (
        [
            "governance/reports/"
            "Design_Deeplus_R11_R19_Frontend_Readiness_"
            "Publication_Closure_R1.md",
            R25_R27_PUBLICATION_CLOSURE_REPORT,
        ]
        if revision in FRONTEND_SUCCESSOR_REVISIONS
        else []
    ) + (
        [R41_PUBLICATION_CLOSURE_REPORT]
        if revision in {
            R41_ACTOR_PROTOCOL_REVISION,
            R23_ACTOR_PROTOCOL_BINDING_REVISION,
            R46_MANAGED_ROOT_RUNTIME_REVISION,
            R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
            R74_IMPLEMENTATION_READINESS_REVISION,
            R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
            R76_GLOBAL_TRACE_CLOSURE_REVISION,
            G4_INDEPENDENT_READINESS_REVISION,
            R77_PUBLICATION_POLICY_CLOSURE_REVISION,
        }
        else []
    ) + (
        [R23_PUBLICATION_CLOSURE_REPORT]
        if revision in {
            R23_ACTOR_PROTOCOL_BINDING_REVISION,
            R46_MANAGED_ROOT_RUNTIME_REVISION,
            R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
            R74_IMPLEMENTATION_READINESS_REVISION,
            R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
            R76_GLOBAL_TRACE_CLOSURE_REVISION,
            G4_INDEPENDENT_READINESS_REVISION,
            R77_PUBLICATION_POLICY_CLOSURE_REVISION,
        }
        else []
    ) + (
        [R46_PUBLICATION_CLOSURE_REPORT]
        if revision in {
            R46_MANAGED_ROOT_RUNTIME_REVISION,
            R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
            R74_IMPLEMENTATION_READINESS_REVISION,
            R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
            R76_GLOBAL_TRACE_CLOSURE_REVISION,
            G4_INDEPENDENT_READINESS_REVISION,
            R77_PUBLICATION_POLICY_CLOSURE_REVISION,
        }
        else []
    ) + (
        [R47_PUBLICATION_CLOSURE_REPORT]
        if revision in {
            R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
            R74_IMPLEMENTATION_READINESS_REVISION,
            R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
            R76_GLOBAL_TRACE_CLOSURE_REVISION,
            G4_INDEPENDENT_READINESS_REVISION,
            R77_PUBLICATION_POLICY_CLOSURE_REVISION,
        }
        else []
    ) + (
        [R74_PUBLICATION_CLOSURE_REPORT]
        if revision in {
            R74_IMPLEMENTATION_READINESS_REVISION,
            R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
            R76_GLOBAL_TRACE_CLOSURE_REVISION,
            G4_INDEPENDENT_READINESS_REVISION,
            R77_PUBLICATION_POLICY_CLOSURE_REVISION,
        }
        else []
    ) + (
        [R75_SEMANTIC_REPORT, R75_PUBLICATION_CLOSURE_REPORT]
        if revision in {
            R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
            R76_GLOBAL_TRACE_CLOSURE_REVISION,
            G4_INDEPENDENT_READINESS_REVISION,
            R77_PUBLICATION_POLICY_CLOSURE_REVISION,
        }
        else []
    ) + (
        [R76_PUBLICATION_CLOSURE_REPORT]
        if revision in {R76_GLOBAL_TRACE_CLOSURE_REVISION, G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION}
        else []
    ) + (
        [G4_PUBLICATION_CLOSURE_REPORT]
        if revision in {G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION}
        else []
    ) + (
        [R77_PUBLICATION_CLOSURE_REPORT]
        if revision == R77_PUBLICATION_POLICY_CLOSURE_REVISION
        else []
    )
    check(
        indexed_decision_paths == CURRENT_DECISION_INDEX_PATHS
        + ([R10_DECISION_PATH] if revision in CURRENT_MACHINE_REVISIONS else [])
        + (R11_R19_DECISION_PATHS if revision in FRONTEND_SUCCESSOR_REVISIONS else [])
        + (
            R47_DECISION_PATHS
            if revision in {
                R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
                R74_IMPLEMENTATION_READINESS_REVISION,
                R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
                R76_GLOBAL_TRACE_CLOSURE_REVISION,
                G4_INDEPENDENT_READINESS_REVISION,
                R77_PUBLICATION_POLICY_CLOSURE_REVISION,
            }
            else []
        )
        + (
            R48_R74_DECISION_PATHS
            if revision in {
                R74_IMPLEMENTATION_READINESS_REVISION,
                R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
                R76_GLOBAL_TRACE_CLOSURE_REVISION,
                G4_INDEPENDENT_READINESS_REVISION,
                R77_PUBLICATION_POLICY_CLOSURE_REVISION,
            }
            else []
        )
        + ([R76_DECISION_PATH] if revision in {R76_GLOBAL_TRACE_CLOSURE_REVISION, G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION} else [])
        + ([G4_DECISION_PATH] if revision in {G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION} else [])
        and indexed_decision_rows == expected_decision_rows
        and all((root / relative).is_file() for relative in CURRENT_DECISION_INDEX_PATHS
                + ([R10_DECISION_PATH] if revision in CURRENT_MACHINE_REVISIONS else [])
                + (R11_R19_DECISION_PATHS if revision in FRONTEND_SUCCESSOR_REVISIONS else [])
                + (
                    R47_DECISION_PATHS
                    if revision in {
                        R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
                        R74_IMPLEMENTATION_READINESS_REVISION,
                        R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
                        R76_GLOBAL_TRACE_CLOSURE_REVISION,
                        G4_INDEPENDENT_READINESS_REVISION,
                        R77_PUBLICATION_POLICY_CLOSURE_REVISION,
                    }
                    else []
                )
                + (
                    R48_R74_DECISION_PATHS
                    if revision in {
                        R74_IMPLEMENTATION_READINESS_REVISION,
                        R75_ACTOR_CRANELIFT_PROJECTION_REVISION,
                        R76_GLOBAL_TRACE_CLOSURE_REVISION,
                        G4_INDEPENDENT_READINESS_REVISION,
                        R77_PUBLICATION_POLICY_CLOSURE_REVISION,
                    }
                    else []
                )
                + ([R76_DECISION_PATH] if revision in {R76_GLOBAL_TRACE_CLOSURE_REVISION, G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION} else [])
                + ([G4_DECISION_PATH] if revision in {G4_INDEPENDENT_READINESS_REVISION, R77_PUBLICATION_POLICY_CLOSURE_REVISION} else []))
        and indexed_governance_paths == expected_governance_paths
        and all(
            (root / relative).is_file()
            for relative in expected_governance_paths
        ),
        "CURRENT_DECISION_INDEX_BINDING",
        repr(
            {
                "decisions": indexed_decision_rows,
                "governance": indexed_governance_paths,
            }
        ),
    )
    r4_closure_receipt = parsed.get(
        root / R4_PUBLICATION_CLOSURE_RECEIPT, {}
    )
    r4_semantic_publication = r4_closure_receipt.get(
        "semantic_publication", {}
    )
    r4_semantic_ci = r4_closure_receipt.get(
        "semantic_pr_github_ci", []
    )
    r4_semantic_validation = r4_closure_receipt.get(
        "semantic_pr_validation", {}
    )
    r4_closure_pr_evidence = r4_closure_receipt.get(
        "closure_pr_evidence", {}
    )
    r4_gap_transition = r4_closure_receipt.get("gap_transition", {})
    r4_action_ledger = r4_closure_receipt.get("action_ledger", {})
    r4_independent_test = r4_closure_receipt.get(
        "independent_test_verification", {}
    )
    r4_governance = r4_closure_receipt.get("governance", {})
    r4_pointer_target = r4_closure_receipt.get("pointer_target", {})
    expected_r4_gap_rows = [
        {
            "id": gap_id,
            "severity": R4_PUBLICATION_CLOSURE_GAP_SEVERITIES[gap_id],
            "from": "APPROVED_NOT_INTEGRATED",
            "at_semantic_merge": "INTEGRATED_UNVERIFIED",
            "after_closure_readback": "VERIFIED_CLOSED",
        }
        for gap_id in R4_PUBLICATION_CLOSURE_GAP_IDS
    ]
    check(
        r4_closure_receipt.get("schema")
        == "deeplus.r4-name-resolution-modules-publication-closure-receipt/v1"
        and r4_closure_receipt.get("recorded_at")
        == "2026-07-30T11:48:21+09:00"
        and r4_closure_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r4_closure_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r4_semantic_publication
        == {
            "pull_request": 46,
            "url": "https://github.com/howork/Deeplus/pull/46",
            "branch": "codex/r4-name-resolution-modules",
            "source_commit": (
                "86669e990e4ad15cd4dd7e9034bf0c34c62cc8d6"
            ),
            "merge_commit": R4_SEMANTIC_PUBLICATION_COMMIT,
            "tree": "1cc3ff5c5813678b5cc9c3465ceacd922bb63d06",
            "parents": [
                "53464e47bc280d4f431440eb7538d9d97c0a7aa7",
                "86669e990e4ad15cd4dd7e9034bf0c34c62cc8d6",
            ],
            "merged_at": "2026-07-30T02:44:17Z",
            "post_merge_readback": "PASS",
        }
        and r4_semantic_ci
        == [
            {
                "workflow": "Canonical integrity",
                "run_id": 30508985918,
                "job": "validate",
                "job_id": 90764770995,
                "head_sha": (
                    "86669e990e4ad15cd4dd7e9034bf0c34c62cc8d6"
                ),
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30508985918/job/90764770995"
                ),
                "conclusion": "SUCCESS",
                "duration": "5m27s",
            },
            {
                "workflow": "Rust workspace",
                "run_id": 30508985919,
                "job": "scaffold",
                "job_id": 90764771028,
                "head_sha": (
                    "86669e990e4ad15cd4dd7e9034bf0c34c62cc8d6"
                ),
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30508985919/job/90764771028"
                ),
                "conclusion": "SUCCESS",
                "duration": "22s",
            },
        ]
        and r4_semantic_validation
        == {
            "workspace_validator": "2990_OF_2990_PASS",
            "bootstrap_mutations": "39_OF_39_PASS",
            "r4_mutations": "73_OF_73_PASS",
            "actual_relation_probes": "27_OF_27_PASS",
            "integrated_contract": "58_OF_58_PASS",
            "helper_selftests": "9_OF_9_PASS",
            "parallel_isolation": "7_OF_7_PASS",
            "deterministic_archive": {
                "bytes": 3141662,
                "sha256": (
                    "a46c180e7225d89702a59b759bab435c7f025cb2349ae889c"
                    "8332ef351c0d1ce"
                ),
                "content_tree_sha256": (
                    "9f32573c62ad00e1e15ddd0fd902a56266cb4e8c5d8e5b3fd"
                    "b4253c11a538dc3"
                ),
                "clean_head_binding": "EXACT_CLEAN_WORKTREE_HEAD",
            },
        }
        and r4_closure_pr_evidence
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R4_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r4_semantic_publication,
                "semantic_pr_github_ci": r4_semantic_ci,
                "semantic_pr_validation": r4_semantic_validation,
                "closure_pr_evidence": r4_closure_pr_evidence,
            }
        ),
    )
    check(
        r4_gap_transition
        == {
            "initial_state": "APPROVED_NOT_INTEGRATED",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 12,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 12,
            "open_audit_gaps_before_closure": {
                "P0": 14,
                "P1": 32,
                "P2": 5,
            },
            "rows": expected_r4_gap_rows,
            "remaining_audit_gaps_after_closure": {
                "P0": 12,
                "P1": 23,
                "P2": 4,
            },
            "source_ledger": {
                "scope": (
                    "PERSISTENT_AUDIT_WORKSPACE_OUTSIDE_CANONICAL_GIT_TREE"
                ),
                "path": (
                    "audit/implementation-readiness-state/"
                    "CUMULATIVE_GAP_REGISTER.json"
                ),
                "schema": (
                    "deeplus.implementation-readiness-cumulative-gap-"
                    "register/r1"
                ),
                "bytes": 283888,
                "sha256": (
                    "6b420087a9679d5b01c56a4015395e9a57a52d78bfdf32c061245"
                    "7dd9b0cdfa2"
                ),
                "baseline_through_r4": (
                    "cfd5946c52571119564b9c8beb430f8dd0356750"
                ),
                "pre_transition_status_counts": {
                    "DECISION_PENDING": 35,
                    "EXPLICITLY_DEFERRED": 1,
                    "DISCOVERED": 3,
                    "APPROVED_NOT_INTEGRATED": 12,
                },
            },
        }
        and r4_action_ledger
        == {
            "source": "current/current-pointer.json#/open_actions",
            "total_open_actions": 26,
            "separate_m13_actions": EXPECTED_ACTION_IDS,
            "canonical_feature_p1_open": SUCCESSOR_ACTION_IDS[
                len(EXPECTED_ACTION_IDS):
            ],
            "canonical_id_array_sha256": (
                "582fa3d9649c380a7a9bf4532fc303626eb9837aeb7f4ed68ce46"
                "f2bc02fc296"
            ),
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r4_independent_test
        == {
            "path": R4_INDEPENDENT_TEST_VERIFICATION_RECEIPT,
            "bytes": 3518,
            "sha256": (
                "6cf010313f5391261efb28c9709a1243c20cb348abb589d61ca6e8"
                "81e9361238"
            ),
            "required_verdict": "PASS_INDEPENDENT_PRE_MERGE_CLOSURE_GATE",
            "closure_effect": (
                "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK"
            ),
        }
        and r4_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
        }
        and r4_pointer_target
        == {
            "role": "publication_authority_source",
            "semantic_merge_commit": R4_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        },
        "R4_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "gap_transition": r4_gap_transition,
                "action_ledger": r4_action_ledger,
                "independent_test_verification": r4_independent_test,
                "governance": r4_governance,
                "pointer_target": r4_pointer_target,
            }
        ),
    )
    r8_closure_receipt = parsed.get(
        root / R8_PUBLICATION_CLOSURE_RECEIPT, {}
    )
    r8_semantic_publication = r8_closure_receipt.get(
        "semantic_publication", {}
    )
    r8_semantic_ci = r8_closure_receipt.get(
        "semantic_pr_github_ci", []
    )
    r8_semantic_validation = r8_closure_receipt.get(
        "semantic_pr_validation", {}
    )
    r8_closure_pr_evidence = r8_closure_receipt.get(
        "closure_pr_evidence", {}
    )
    r8_gap_transition = r8_closure_receipt.get("gap_transition", {})
    r8_action_ledger = r8_closure_receipt.get("action_ledger", {})
    r8_independent_test = r8_closure_receipt.get(
        "independent_test_verification", {}
    )
    r8_governance = r8_closure_receipt.get("governance", {})
    r8_pointer_target = r8_closure_receipt.get("pointer_target", {})
    expected_r8_gap_rows = [
        {
            "id": gap_id,
            "severity": "P0",
            "from": "APPROVED_NOT_INTEGRATED",
            "at_semantic_merge": "INTEGRATED_UNVERIFIED",
            "after_closure_readback": "VERIFIED_CLOSED",
        }
        for gap_id in R8_PUBLICATION_CLOSURE_GAP_IDS
    ]
    check(
        r8_closure_receipt.get("schema")
        == (
            "deeplus.r8-ownership-canonical-promotion-publication-"
            "closure-receipt/v1"
        )
        and r8_closure_receipt.get("recorded_at")
        == "2026-07-31T03:33:54+09:00"
        and r8_closure_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r8_closure_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r8_semantic_publication
        == {
            "pull_request": 48,
            "url": "https://github.com/howork/Deeplus/pull/48",
            "branch": "codex/r5-ownership-place-loan",
            "source_commit": (
                "8efc9ef3e1b60723fe5f0fa15ec638479fbed64e"
            ),
            "merge_commit": R8_SEMANTIC_PUBLICATION_COMMIT,
            "tree": "26ca3acb8377c860482bf21aa646155377fe81af",
            "parents": [
                "1053902449aedccb110cef5bcfe76e5b1af9df01",
                "8efc9ef3e1b60723fe5f0fa15ec638479fbed64e",
            ],
            "merged_at": "2026-07-30T18:25:29Z",
            "post_merge_readback": "PASS",
        }
        and r8_semantic_ci
        == [
            {
                "workflow": "Canonical integrity",
                "run_id": 30569813548,
                "job": "validate",
                "job_id": 90963367240,
                "head_sha": (
                    "8efc9ef3e1b60723fe5f0fa15ec638479fbed64e"
                ),
                "started_at": "2026-07-30T18:18:20Z",
                "completed_at": "2026-07-30T18:24:52Z",
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30569813548/job/90963367240"
                ),
                "conclusion": "SUCCESS",
            },
            {
                "workflow": "Rust workspace",
                "run_id": 30569813457,
                "job": "scaffold",
                "job_id": 90963366897,
                "head_sha": (
                    "8efc9ef3e1b60723fe5f0fa15ec638479fbed64e"
                ),
                "started_at": "2026-07-30T18:18:20Z",
                "completed_at": "2026-07-30T18:18:43Z",
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30569813457/job/90963366897"
                ),
                "conclusion": "SUCCESS",
            },
        ]
        and r8_semantic_validation
        == {
            "freeze_pack": {
                "filename": (
                    "Codex_Design_Deeplus_R8_Ownership_Canonical_"
                    "Promotion_Source_Candidate_Pack_R8.zip"
                ),
                "bytes": 9701905,
                "sha256": (
                    "ae730ce57b8985d69d150f4eba9b21609bbfee5003b86016909a"
                    "04cf68327f3c"
                ),
                "member_count": 161,
            },
            "source_operations": {
                "total": 70,
                "create": 17,
                "replace": 53,
                "delete": 0,
            },
            "independent_command_matrix": "23_OF_23_PASS",
            "ownership_checks": "13_OF_13_PASS",
            "workspace_checks": "3739_OF_3739_PASS",
            "clippy_baseline_parity": "4_OF_4_PASS",
            "preparer_normal_path": "PASS",
            "preparer_mutation_rejection": "PASS",
            "applicator_normal_path": "PASS",
            "applicator_mutation_rejection": "PASS",
            "control_patch_self_validation": "PASS",
            "pack_integrity": "PASS",
            "canonical_source_mutation_during_freeze": 0,
            "github_mutation_during_freeze": 0,
        }
        and r8_closure_pr_evidence
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R8_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r8_semantic_publication,
                "semantic_pr_github_ci": r8_semantic_ci,
                "semantic_pr_validation": r8_semantic_validation,
                "closure_pr_evidence": r8_closure_pr_evidence,
            }
        ),
    )
    check(
        r8_gap_transition
        == {
            "initial_state": "APPROVED_NOT_INTEGRATED",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 3,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 3,
            "open_audit_gaps_before_closure": {
                "P0": 13,
                "P1": 23,
                "P2": 4,
            },
            "rows": expected_r8_gap_rows,
            "remaining_audit_gaps_after_closure": {
                "P0": 10,
                "P1": 23,
                "P2": 4,
            },
            "source_ledger": {
                "scope": (
                    "PERSISTENT_AUDIT_WORKSPACE_OUTSIDE_CANONICAL_GIT_TREE"
                ),
                "path": (
                    "audit/implementation-readiness-state/"
                    "CUMULATIVE_GAP_REGISTER.json"
                ),
                "schema": (
                    "deeplus.implementation-readiness-cumulative-gap-"
                    "register/r1"
                ),
                "bytes": 296938,
                "sha256": (
                    "d43d150e2d810fdbf3b2a8c178c79c9c3b2b5728171d8530e74"
                    "b0aaabcf36855"
                ),
                "baseline_through_r4": (
                    "1053902449aedccb110cef5bcfe76e5b1af9df01"
                ),
                "pre_transition_status_counts": {
                    "DECISION_PENDING": 35,
                    "EXPLICITLY_DEFERRED": 1,
                    "DISCOVERED": 4,
                    "VERIFIED_CLOSED": 12,
                },
                "count_correction": (
                    "The previous checkpoint omitted discovered "
                    "IR-DIAG-P0-052; the correct nonclosed P0 count is 13 "
                    "before R8 closure and 10 after it."
                ),
            },
        }
        and r8_action_ledger
        == {
            "source": "current/current-pointer.json#/open_actions",
            "total_open_actions": 26,
            "separate_m13_actions": EXPECTED_ACTION_IDS,
            "canonical_feature_p1_open": SUCCESSOR_ACTION_IDS[
                len(EXPECTED_ACTION_IDS):
            ],
            "canonical_id_array_sha256": (
                "582fa3d9649c380a7a9bf4532fc303626eb9837aeb7f4ed68ce46"
                "f2bc02fc296"
            ),
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r8_independent_test
        == {
            "path": R8_INDEPENDENT_TEST_VERIFICATION_RECEIPT,
            "bytes": 3867,
            "sha256": (
                "7431be68b0f844f29e8530ff575732d3869a549552578b29b28ad8"
                "edee34efe2"
            ),
            "required_verdict": "PASS_INDEPENDENT_PRE_MERGE_CLOSURE_GATE",
            "closure_effect": (
                "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK"
            ),
        }
        and r8_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
        }
        and r8_pointer_target
        == {
            "role": "publication_authority_source",
            "semantic_merge_commit": R8_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r8_closure_receipt.get("next_checkpoint")
        == {
            "baseline": "CLOSURE_MERGE_SHA_FROM_POST_MERGE_READBACK",
            "candidate_cluster": "R9_DIAGNOSTIC_DISPATCH_CLOSURE",
            "gap_scope": ["IR-DIAG-P0-052"],
            "activation": (
                "AFTER_CLOSURE_READBACK_AND_STANDARD_CLUSTER_"
                "BASELINE_OBSERVATION"
            ),
        }
        and r8_closure_receipt.get("r8_only_scope_freeze")
        == {
            "directive_state_after_r8_final_report": "EXPIRED",
            "subsequent_cluster_procedure": "STANDARD_CLUSTER_PROCEDURE",
        },
        "R8_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "gap_transition": r8_gap_transition,
                "action_ledger": r8_action_ledger,
                "independent_test_verification": r8_independent_test,
                "governance": r8_governance,
                "pointer_target": r8_pointer_target,
            }
        ),
    )
    r9_report_path = root / R9_PUBLICATION_CLOSURE_REPORT
    r9_receipt_path = root / R9_PUBLICATION_CLOSURE_RECEIPT
    r9_closure_receipt = parsed.get(r9_receipt_path, {})
    r9_semantic_publication = r9_closure_receipt.get(
        "semantic_publication", {}
    )
    r9_semantic_ci = r9_closure_receipt.get(
        "semantic_pr_github_ci", []
    )
    r9_semantic_validation = r9_closure_receipt.get(
        "semantic_pr_validation", {}
    )
    r9_closure_pr_evidence = r9_closure_receipt.get(
        "closure_pr_evidence", {}
    )
    r9_gap_transition = r9_closure_receipt.get("gap_transition", {})
    r9_action_ledger = r9_closure_receipt.get("action_ledger", {})
    r9_independent_test = r9_closure_receipt.get(
        "independent_test_verification", {}
    )
    r9_governance = r9_closure_receipt.get("governance", {})
    r9_pointer_target = r9_closure_receipt.get("pointer_target", {})
    expected_r9_gap_rows = [
        {
            "id": "IR-DIAG-P0-052",
            "severity": "P0",
            "from": "APPROVED_NOT_INTEGRATED",
            "at_semantic_merge": "INTEGRATED_UNVERIFIED",
            "after_closure_readback": "VERIFIED_CLOSED",
        }
    ]
    check(
        r9_report_path.is_file()
        and r9_report_path.stat().st_size
        == R9_PUBLICATION_CLOSURE_REPORT_BYTES
        and file_sha(r9_report_path)
        == R9_PUBLICATION_CLOSURE_REPORT_SHA256
        and r9_receipt_path.is_file()
        and r9_receipt_path.stat().st_size
        == R9_PUBLICATION_CLOSURE_RECEIPT_BYTES
        and file_sha(r9_receipt_path)
        == R9_PUBLICATION_CLOSURE_RECEIPT_SHA256
        and r9_closure_receipt.get("schema")
        == "deeplus.r9-diagnostic-dispatch-publication-closure-receipt/v1"
        and r9_closure_receipt.get("recorded_at")
        == "2026-07-31T06:51:12+09:00"
        and r9_closure_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r9_closure_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r9_semantic_publication
        == {
            "pull_request": 50,
            "url": "https://github.com/howork/Deeplus/pull/50",
            "branch": "codex/r9-diagnostic-dispatch-closure",
            "source_commit": R9_SEMANTIC_SOURCE_COMMIT,
            "merge_commit": R9_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R9_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "336e7b9919dbd6bdcccca71a7be32d3ed7a88b5b",
                R9_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-07-31T06:48:41+09:00",
            "post_merge_readback": "PASS",
        }
        and r9_semantic_ci
        == [
            {
                "workflow": "Canonical integrity",
                "run_id": 30584366374,
                "job": "validate",
                "job_id": 91012139929,
                "head_sha": R9_SEMANTIC_SOURCE_COMMIT,
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30584366374/job/91012139929"
                ),
                "conclusion": "SUCCESS",
            },
            {
                "workflow": "Rust workspace",
                "run_id": 30584366320,
                "job": "scaffold",
                "job_id": 91012139727,
                "head_sha": R9_SEMANTIC_SOURCE_COMMIT,
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30584366320/job/91012139727"
                ),
                "conclusion": "SUCCESS",
            },
        ]
        and r9_semantic_validation
        == {
            "freeze_pack": {
                "filename": (
                    "Codex_Design_Deeplus_R9_Diagnostic_Dispatch_Closure_"
                    "Candidate_Freeze_Pack_R5.zip"
                ),
                "bytes": 116490,
                "sha256": (
                    "541da4136e420d80f068fa72dc48b468cd8e8ad551c3ced32c8f"
                    "881d00e932e0"
                ),
                "semantic_delta_count": 0,
                "implementation_path_count": {"r4": 44, "r5": 45},
                "generator_derived_added_path": (
                    "tests/conformance/checker-predicates/chunks/"
                    "part-0029.json"
                ),
            },
            "diagnostic_dispatch_static_reference": {
                "schema": (
                    "deeplus.r9-diagnostic-dispatch-closure-test-receipt/v1"
                ),
                "result": "PASS",
                "checks": "9_OF_9_PASS",
                "base_cases": 18,
                "adversarial_cases": 13,
                "mutation_rows": 12,
                "ordered_reason_keys": 12,
                "product_execution": "NOT_RUN",
            },
            "registry_postimage": {
                "predicates": 277,
                "diagnostics": 1436,
                "relations": 559,
                "dispatch_rows": 226,
                "undefined_or_unlisted_dispatch": 0,
            },
            "grammar_reference_generator": {
                "result": "PASS",
                "cases": 33,
                "mutations": 32,
                "deterministic_output_count": 8,
                "repository_write": False,
            },
            "tutorial_generator": {
                "result": "TUTORIAL_MUTATION_TEST_PASS",
                "rejection_mutations": 12,
            },
            "canonical_source_mutation_during_freeze": 0,
            "github_mutation_during_freeze": 0,
        }
        and r9_closure_pr_evidence
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R9_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r9_semantic_publication,
                "semantic_pr_github_ci": r9_semantic_ci,
                "semantic_pr_validation": r9_semantic_validation,
                "closure_pr_evidence": r9_closure_pr_evidence,
            }
        ),
    )
    check(
        r9_gap_transition
        == {
            "initial_state": "APPROVED_NOT_INTEGRATED",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 1,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 1,
            "rows": expected_r9_gap_rows,
        }
        and r9_action_ledger
        == {
            "source": "current/current-pointer.json#/open_actions",
            "total_open_actions": 26,
            "separate_m13_actions": EXPECTED_ACTION_IDS,
            "canonical_feature_p1_open": SUCCESSOR_ACTION_IDS[
                len(EXPECTED_ACTION_IDS):
            ],
            "canonical_id_array_sha256": (
                "582fa3d9649c380a7a9bf4532fc303626eb9837aeb7f4ed68ce46"
                "f2bc02fc296"
            ),
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r9_independent_test
        == {
            "path": R9_INDEPENDENT_TEST_VERIFICATION_RECEIPT,
            "bytes": R9_INDEPENDENT_TEST_VERIFICATION_BYTES,
            "sha256": R9_INDEPENDENT_TEST_VERIFICATION_SHA256,
            "required_verdict": "PASS_INDEPENDENT_PRE_MERGE_CLOSURE_GATE",
            "closure_effect": (
                "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK"
            ),
        }
        and r9_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "canonical_source_mutation_during_closure": 0,
            "github_mutation_during_closure": 0,
        }
        and r9_pointer_target
        == {
            "role": "publication_authority_source",
            "semantic_merge_commit": R9_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r9_closure_receipt.get("next_checkpoint")
        == {
            "baseline": "CLOSURE_MERGE_SHA_FROM_POST_MERGE_READBACK",
            "candidate_cluster": "DEPENDENCY_ORDERED_R10_SELECTION",
            "gap_scope": [],
            "activation": (
                "AFTER_CLOSURE_READBACK_AND_STANDARD_CLUSTER_"
                "BASELINE_OBSERVATION"
            ),
        },
        "R9_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "gap_transition": r9_gap_transition,
                "action_ledger": r9_action_ledger,
                "independent_test_verification": r9_independent_test,
                "governance": r9_governance,
                "pointer_target": r9_pointer_target,
            }
        ),
    )
    r10_report_path = root / R10_PUBLICATION_CLOSURE_REPORT
    r10_receipt_path = root / R10_PUBLICATION_CLOSURE_RECEIPT
    r10_closure_receipt = parsed.get(r10_receipt_path, {})
    r10_semantic_publication = r10_closure_receipt.get(
        "semantic_publication", {}
    )
    r10_semantic_ci = r10_closure_receipt.get(
        "semantic_pr_github_ci", []
    )
    r10_semantic_validation = r10_closure_receipt.get(
        "semantic_validation", {}
    )
    r10_closure_pr_evidence = r10_closure_receipt.get(
        "closure_pr_evidence", {}
    )
    r10_gap_transition = r10_closure_receipt.get("gap_transition", {})
    r10_action_ledger = r10_closure_receipt.get("action_ledger", {})
    r10_independent_test = r10_closure_receipt.get(
        "independent_test_verification", {}
    )
    r10_governance = r10_closure_receipt.get("governance", {})
    r10_pointer_target = r10_closure_receipt.get("pointer_target", {})
    expected_r10_gap_rows = [
        {
            "id": "IR-OWN-P0-015",
            "severity": "P0",
            "persistent_pre_state": "DECISION_PENDING",
            "at_candidate_freeze": "APPROVED_NOT_INTEGRATED",
            "at_semantic_merge": "INTEGRATED_UNVERIFIED",
            "after_closure_readback": "VERIFIED_CLOSED",
        }
    ]
    check(
        r10_report_path.is_file()
        and r10_report_path.stat().st_size
        == R10_PUBLICATION_CLOSURE_REPORT_BYTES
        and file_sha(r10_report_path)
        == R10_PUBLICATION_CLOSURE_REPORT_SHA256
        and r10_receipt_path.is_file()
        and r10_receipt_path.stat().st_size
        == R10_PUBLICATION_CLOSURE_RECEIPT_BYTES
        and file_sha(r10_receipt_path)
        == R10_PUBLICATION_CLOSURE_RECEIPT_SHA256
        and r10_closure_receipt.get("schema")
        == "deeplus.r10-hir-mir-machine-contract-publication-closure-receipt/v1"
        and r10_closure_receipt.get("recorded_at")
        == "2026-07-31T18:49:43+09:00"
        and r10_closure_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r10_closure_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r10_semantic_publication
        == {
            "pull_request": 52,
            "url": "https://github.com/howork/Deeplus/pull/52",
            "branch": "codex/r10-hir-mir-machine-contract",
            "source_commit": R10_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R10_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R10_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R10_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "7632a2943e3e70dd4c6adffd53977671aec0f6c5",
                R10_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-07-31T18:45:19+09:00",
            "post_merge_readback": "PASS",
        }
        and r10_semantic_ci
        == [
            {
                "workflow": "Canonical integrity",
                "run_id": 30620572323,
                "job": "validate",
                "job_id": 91123899542,
                "head_sha": R10_SEMANTIC_SOURCE_COMMIT,
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30620572323/job/91123899542"
                ),
                "conclusion": "SUCCESS",
            },
            {
                "workflow": "Rust workspace",
                "run_id": 30620572327,
                "job": "scaffold",
                "job_id": 91123899548,
                "head_sha": R10_SEMANTIC_SOURCE_COMMIT,
                "url": (
                    "https://github.com/howork/Deeplus/actions/runs/"
                    "30620572327/job/91123899548"
                ),
                "conclusion": "SUCCESS",
            },
        ]
        and r10_semantic_validation
        == {
            "change_scope": {
                "changed_file_count": 50,
                "production_crate_change_count": 0,
                "grammar_change_count": 0,
                "source_syntax_activation_count": 0,
            },
            "focused": {
                "command": (
                    "py -3 tools/validators/"
                    "validate_hir_mir_machine_contract.py --root ."
                ),
                "result": "PASS",
                "hir_identities": 128,
                "structural_plan_contracts": 12,
                "lowering_rows_current": 102,
                "lowering_rows_explicit_preview_maximum": 111,
                "mir_operations": 29,
                "mir_terminators": 17,
                "mir_linear_tokens": 12,
                "mir_capabilities": 26,
                "call_mode_target_pairs": 10,
                "argument_kinds": 7,
                "fixture_bindings": 43,
                "new_release_verifier_diagnostics": 5,
                "new_source_diagnostics": 0,
            },
            "workspace": {
                "command": "py -3 tools/validators/validate_workspace.py --root .",
                "result": "PASS",
                "checks": "5729_OF_5729_PASS",
                "json_files_parsed": 354,
                "catalogs_reassembled": 14,
                "rust_scaffold_crates": 15,
            },
            "source_manifest": {
                "path": "release/source-tree-manifest.json",
                "bytes": 126380,
                "sha256": (
                    "eaa76380331f89e7c4d8fc054d8bae5638d876ac8c6a6c4f"
                    "9171f2dd15dd7376"
                ),
                "file_count_excluding_manifest": 663,
                "total_bytes_excluding_manifest": 22014997,
                "tree_sha256": (
                    "6df5ab342deed3a37ed5e9d5c73dc69254a7586345c0be57a0"
                    "fab6d884e8118e"
                ),
                "binding": "WORKTREE_AND_INDEX_BOUND",
            },
            "evidence_level": "E2_DESIGN_STATIC",
            "production_execution": "NOT_RUN",
        }
        and r10_closure_receipt.get("validation_efficiency")
        == {
            "intermediate_archive_count": 0,
            "intermediate_crc_or_pack_checksum_count": 0,
            "repeated_unchanged_gate_count": 0,
            "semantic_pr_focused_gate_count": 1,
            "semantic_pr_full_workspace_gate_count": 1,
            "closure_rule": (
                "Run only the closure-specific checks and one final workspace "
                "gate after all closure bytes are bound."
            ),
        }
        and r10_closure_pr_evidence
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R10_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r10_semantic_publication,
                "semantic_pr_github_ci": r10_semantic_ci,
                "semantic_validation": r10_semantic_validation,
                "closure_pr_evidence": r10_closure_pr_evidence,
            }
        ),
    )
    check(
        r10_gap_transition
        == {
            "persistent_pre_state": "DECISION_PENDING",
            "candidate_freeze_state": "APPROVED_NOT_INTEGRATED",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 1,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 1,
            "rows": expected_r10_gap_rows,
        }
        and r10_action_ledger
        == {
            "source": "current/current-pointer.json#/open_actions",
            "total_open_actions": 26,
            "separate_m13_actions": EXPECTED_ACTION_IDS,
            "canonical_feature_p1_open": SUCCESSOR_ACTION_IDS[
                len(EXPECTED_ACTION_IDS):
            ],
            "canonical_id_array_sha256": (
                "582fa3d9649c380a7a9bf4532fc303626eb9837aeb7f4ed68ce46"
                "f2bc02fc296"
            ),
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r10_independent_test
        == {
            "path": R10_INDEPENDENT_TEST_VERIFICATION_RECEIPT,
            "bytes": R10_INDEPENDENT_TEST_VERIFICATION_BYTES,
            "sha256": R10_INDEPENDENT_TEST_VERIFICATION_SHA256,
            "required_verdict": (
                "CONDITIONAL_PASS_READY_FOR_PUBLICATION_CLOSURE"
            ),
            "closure_effect": (
                "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK"
            ),
        }
        and r10_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "canonical_source_mutation_during_closure": 0,
            "github_mutation_during_closure": 0,
        }
        and r10_pointer_target
        == {
            "role": "publication_authority_source",
            "semantic_merge_commit": R10_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r10_closure_receipt.get("next_checkpoint")
        == {
            "baseline": "CLOSURE_MERGE_SHA_FROM_POST_MERGE_READBACK",
            "candidate_cluster": "DEPENDENCY_ORDERED_R11_SELECTION",
            "gap_scope": [],
            "activation": (
                "AFTER_CLOSURE_READBACK_AND_STANDARD_CLUSTER_"
                "BASELINE_OBSERVATION"
            ),
        },
        "R10_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "gap_transition": r10_gap_transition,
                "action_ledger": r10_action_ledger,
                "independent_test_verification": r10_independent_test,
                "governance": r10_governance,
                "pointer_target": r10_pointer_target,
            }
        ),
    )
    r25_r27_report_path = root / R25_R27_PUBLICATION_CLOSURE_REPORT
    r25_r27_receipt_path = root / R25_R27_PUBLICATION_CLOSURE_RECEIPT
    r25_r27_receipt = parsed.get(r25_r27_receipt_path, {})
    r25_r27_semantic_publication = r25_r27_receipt.get(
        "semantic_publication", {}
    )
    r25_r27_pr_ci = r25_r27_receipt.get("semantic_pr_github_ci", [])
    r25_r27_main_ci = r25_r27_receipt.get(
        "semantic_merge_main_ci", []
    )
    r25_r27_validation = r25_r27_receipt.get("semantic_validation", {})
    r25_r27_gap_transition = r25_r27_receipt.get("gap_transition", {})
    r25_r27_governance = r25_r27_receipt.get("governance", {})
    r25_r27_pointer_target = r25_r27_receipt.get("pointer_target", {})
    check(
        r25_r27_report_path.is_file()
        and r25_r27_receipt_path.is_file()
        and r25_r27_receipt.get("schema")
        == (
            "deeplus.r25-r27-frontend-trace-diagnostic-grammar-topology-"
            "publication-closure-receipt/v1"
        )
        and r25_r27_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r25_r27_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r25_r27_semantic_publication
        == {
            "pull_request": 56,
            "url": "https://github.com/howork/Deeplus/pull/56",
            "branch": "codex/r27-grammar-topology-closure",
            "source_commit": R25_R27_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R25_R27_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R25_R27_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R25_R27_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "3f0077dd8f021718dc87b3b239f417e5d3f770a6",
                R25_R27_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-01T23:47:09+09:00",
            "post_merge_readback": "PASS",
        }
        and len(r25_r27_pr_ci) == 2
        and {row.get("workflow") for row in r25_r27_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R25_R27_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r25_r27_pr_ci
        )
        and len(r25_r27_main_ci) == 2
        and {row.get("workflow") for row in r25_r27_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R25_R27_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r25_r27_main_ci
        )
        and r25_r27_receipt.get("closure_pr_evidence")
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R25_R27_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r25_r27_semantic_publication,
                "semantic_pr_github_ci": r25_r27_pr_ci,
                "semantic_merge_main_ci": r25_r27_main_ci,
            }
        ),
    )
    check(
        r25_r27_validation.get("change_scope")
        == {
            "changed_file_count": 50,
            "production_crate_change_count": 0,
            "grammar_production_change_count": 0,
            "source_spelling_change_count": 0,
            "semantic_change_count": 0,
            "new_diagnostic_id_count": 0,
        }
        and r25_r27_validation.get("focused", {}).get("r25_checks")
        == "36_OF_36_PASS"
        and r25_r27_validation.get("focused", {}).get("r26_checks")
        == "8_OF_8_PASS"
        and r25_r27_validation.get("focused", {}).get("r27_checks")
        == "10_OF_10_PASS"
        and r25_r27_validation.get("workspace", {}).get("result") == "PASS"
        and r25_r27_validation.get("workspace", {}).get("checks")
        == "5965_OF_5965_PASS"
        and r25_r27_validation.get("evidence_level")
        == "E2_DESIGN_STATIC"
        and r25_r27_validation.get("production_execution") == "NOT_RUN"
        and r25_r27_gap_transition
        == {
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 5,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 5,
            "gap_ids": R25_R27_PUBLICATION_CLOSURE_GAP_IDS,
        }
        and r25_r27_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r25_r27_pointer_target
        == {
            "role": "publication_authority_source",
            "semantic_merge_commit": R25_R27_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r25_r27_receipt.get("next_checkpoint")
        == {
            "baseline": "CLOSURE_MERGE_SHA_FROM_POST_MERGE_READBACK",
            "candidate_cluster": "DEPENDENCY_ORDERED_LOCAL_SELECTION",
            "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION",
            "activation": (
                "AFTER_CLOSURE_READBACK_AND_STANDARD_CLUSTER_"
                "BASELINE_OBSERVATION"
            ),
        },
        "R25_R27_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "validation": r25_r27_validation,
                "gap_transition": r25_r27_gap_transition,
                "governance": r25_r27_governance,
                "pointer_target": r25_r27_pointer_target,
            }
        ),
    )
    r41_report_path = root / R41_PUBLICATION_CLOSURE_REPORT
    r41_receipt_path = root / R41_PUBLICATION_CLOSURE_RECEIPT
    r41_independent_path = root / R41_INDEPENDENT_VERIFICATION_RECEIPT
    r41_receipt = parsed.get(r41_receipt_path, {})
    r41_semantic_publication = r41_receipt.get("semantic_publication", {})
    r41_pr_ci = r41_receipt.get("semantic_pr_github_ci", [])
    r41_main_ci = r41_receipt.get("semantic_merge_main_ci", [])
    r41_validation = r41_receipt.get("semantic_validation", {})
    r41_gap_transition = r41_receipt.get("gap_transition", {})
    r41_governance = r41_receipt.get("governance", {})
    r41_pointer_target = r41_receipt.get("pointer_target", {})
    r41_independent = parsed.get(r41_independent_path, {})
    check(
        r41_report_path.is_file()
        and r41_receipt_path.is_file()
        and r41_independent_path.is_file()
        and r41_receipt.get("schema")
        == (
            "deeplus.r41-actor-protocol-direct-conformance-"
            "publication-closure-receipt/v1"
        )
        and r41_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r41_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r41_semantic_publication
        == {
            "pull_request": 59,
            "url": "https://github.com/howork/Deeplus/pull/59",
            "branch": "codex/r41-actor-direct-conformance-rebase",
            "source_commit": R41_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R41_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R41_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R41_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "b6ff0f80d74e93bc7b25c54cfde08f8b40ca54e3",
                R41_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-02T03:22:14Z",
            "post_merge_readback": "PASS",
        }
        and len(r41_pr_ci) == 2
        and {row.get("workflow") for row in r41_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R41_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r41_pr_ci
        )
        and len(r41_main_ci) == 2
        and {row.get("workflow") for row in r41_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R41_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r41_main_ci
        )
        and r41_receipt.get("closure_pr_evidence")
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R41_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r41_semantic_publication,
                "semantic_pr_github_ci": r41_pr_ci,
                "semantic_merge_main_ci": r41_main_ci,
            }
        ),
    )
    check(
        r41_validation.get("change_scope")
        == {
            "changed_file_count": 68,
            "production_crate_change_count": 0,
            "grammar_production_change_count": 5,
            "source_spelling_change_count": 0,
            "semantic_change_count": 1,
            "new_diagnostic_id_count": 9,
        }
        and r41_validation.get("focused", {}).get("actor_protocol_checks")
        == "10_OF_10_PASS"
        and r41_validation.get("focused", {}).get(
            "actor_protocol_predicate_fixtures"
        ) == "11_OF_11_PASS"
        and r41_validation.get("focused", {}).get(
            "actor_protocol_acceptance_cases"
        ) == "26_OF_26_PASS"
        and r41_validation.get("focused", {}).get("actor_protocol_mutations")
        == "10_OF_10_REJECTED"
        and r41_validation.get("workspace", {}).get("result") == "PASS"
        and r41_validation.get("workspace", {}).get("checks")
        == "6051_OF_6051_PASS"
        and r41_validation.get("source_manifest", {}).get(
            "file_count_excluding_manifest"
        ) == 720
        and r41_validation.get("source_manifest", {}).get("tree_sha256")
        == "fc317635d5fa7555a0c352520cc9d2a40aadb8923ed6786d87d2832b78f939df"
        and r41_validation.get("evidence_level") == "E2_DESIGN_STATIC"
        and r41_validation.get("production_execution") == "NOT_RUN"
        and r41_gap_transition
        == {
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 4,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 4,
            "gap_ids": R41_PUBLICATION_CLOSURE_GAP_IDS,
        }
        and r41_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r41_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": R41_ACTOR_PROTOCOL_REVISION,
            "semantic_merge_commit": R41_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r41_independent.get("schema")
        == (
            "deeplus.r41-actor-protocol-direct-conformance-"
            "independent-verification/v1"
        )
        and r41_independent.get("semantic_merge_commit")
        == R41_SEMANTIC_PUBLICATION_COMMIT
        and r41_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and r41_independent.get("product_execution") == "NOT_RUN"
        and r41_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R41_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "validation": r41_validation,
                "gap_transition": r41_gap_transition,
                "governance": r41_governance,
                "pointer_target": r41_pointer_target,
                "independent": r41_independent,
            }
        ),
    )
    r23_report_path = root / R23_PUBLICATION_CLOSURE_REPORT
    r23_receipt_path = root / R23_PUBLICATION_CLOSURE_RECEIPT
    r23_independent_path = root / R23_INDEPENDENT_VERIFICATION_RECEIPT
    r23_receipt = parsed.get(r23_receipt_path, {})
    r23_semantic_publication = r23_receipt.get(
        "semantic_publication", {}
    )
    r23_pr_ci = r23_receipt.get("semantic_pr_github_ci", [])
    r23_main_ci = r23_receipt.get("semantic_merge_main_ci", [])
    r23_validation = r23_receipt.get("semantic_validation", {})
    r23_gap_transition = r23_receipt.get("gap_transition", {})
    r23_governance = r23_receipt.get("governance", {})
    r23_pointer_target = r23_receipt.get("pointer_target", {})
    r23_independent = parsed.get(r23_independent_path, {})
    check(
        r23_report_path.is_file()
        and r23_receipt_path.is_file()
        and r23_independent_path.is_file()
        and r23_receipt.get("schema")
        == (
            "deeplus.r23-actor-protocol-binding-"
            "publication-closure-receipt/v1"
        )
        and r23_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r23_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r23_semantic_publication
        == {
            "pull_request": 61,
            "url": "https://github.com/howork/Deeplus/pull/61",
            "branch": "codex/r43-actor-protocol-binding-rebase",
            "source_commit": R23_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R23_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R23_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R23_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "53bbc11cf4b4b5980ae07c04f97a41d7bdd12012",
                R23_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-02T04:53:26Z",
            "post_merge_readback": "PASS",
        }
        and len(r23_pr_ci) == 2
        and {row.get("workflow") for row in r23_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R23_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r23_pr_ci
        )
        and len(r23_main_ci) == 2
        and {row.get("workflow") for row in r23_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R23_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r23_main_ci
        )
        and r23_receipt.get("closure_pr_evidence")
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R23_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r23_semantic_publication,
                "semantic_pr_github_ci": r23_pr_ci,
                "semantic_merge_main_ci": r23_main_ci,
            }
        ),
    )
    check(
        r23_validation.get("change_scope")
        == {
            "changed_file_count": 23,
            "production_crate_change_count": 0,
            "grammar_production_change_count": 0,
            "source_spelling_change_count": 0,
            "semantic_change_count": 1,
            "new_diagnostic_id_count": 0,
        }
        and r23_validation.get("focused", {}).get(
            "actor_protocol_binding_checks"
        ) == "55_OF_55_PASS"
        and r23_validation.get("focused", {}).get(
            "legacy_module_mutations"
        ) == "73_OF_73_REJECTED"
        and r23_validation.get("workspace", {}).get("result") == "PASS"
        and r23_validation.get("workspace", {}).get("checks")
        == "6129_OF_6129_PASS"
        and r23_validation.get("source_manifest", {}).get(
            "file_count_excluding_manifest"
        ) == 729
        and r23_validation.get("source_manifest", {}).get("tree_sha256")
        == "4c6a2e9ee6ca8193e96d796a7b509c57ea03a99bcac3600e711657bf14ec0107"
        and r23_validation.get("evidence_level") == "E2_DESIGN_STATIC"
        and r23_validation.get("production_execution") == "NOT_RUN"
        and r23_gap_transition
        == {
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 1,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 1,
            "gap_ids": R23_PUBLICATION_CLOSURE_GAP_IDS,
        }
        and r23_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r23_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": R23_ACTOR_PROTOCOL_BINDING_REVISION,
            "semantic_merge_commit": R23_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit":
                "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r23_independent.get("schema")
        == (
            "deeplus.r23-actor-protocol-binding-"
            "independent-verification/v1"
        )
        and r23_independent.get("semantic_merge_commit")
        == R23_SEMANTIC_PUBLICATION_COMMIT
        and r23_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and r23_independent.get("product_execution") == "NOT_RUN"
        and r23_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R23_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "validation": r23_validation,
                "gap_transition": r23_gap_transition,
                "governance": r23_governance,
                "pointer_target": r23_pointer_target,
                "independent": r23_independent,
            }
        ),
    )
    r46_report_path = root / R46_PUBLICATION_CLOSURE_REPORT
    r46_receipt_path = root / R46_PUBLICATION_CLOSURE_RECEIPT
    r46_independent_path = root / R46_INDEPENDENT_VERIFICATION_RECEIPT
    r46_receipt = parsed.get(r46_receipt_path, {})
    r46_semantic_publication = r46_receipt.get("semantic_publication", {})
    r46_pr_ci = r46_receipt.get("semantic_pr_github_ci", [])
    r46_main_ci = r46_receipt.get("semantic_merge_main_ci", [])
    r46_validation = r46_receipt.get("semantic_validation", {})
    r46_gap_transition = r46_receipt.get("gap_transition", {})
    r46_governance = r46_receipt.get("governance", {})
    r46_pointer_target = r46_receipt.get("pointer_target", {})
    r46_independent = parsed.get(r46_independent_path, {})
    check(
        r46_report_path.is_file()
        and r46_receipt_path.is_file()
        and r46_independent_path.is_file()
        and r46_receipt.get("schema")
        == "deeplus.r46-managed-root-runtime-fusion-publication-closure-receipt/v1"
        and r46_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r46_receipt.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r46_semantic_publication
        == {
            "pull_request": 63,
            "url": "https://github.com/howork/Deeplus/pull/63",
            "branch": "codex/r46-managed-root-runtime-fusion",
            "source_commit": R46_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R46_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R46_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R46_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "e680568057ec9c6b02218dbe153758471734cf44",
                R46_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-02T18:52:47Z",
            "post_merge_readback": "PASS",
        }
        and len(r46_pr_ci) == 2
        and {row.get("workflow") for row in r46_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R46_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r46_pr_ci
        )
        and len(r46_main_ci) == 2
        and {row.get("workflow") for row in r46_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R46_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r46_main_ci
        )
        and r46_receipt.get("closure_pr_evidence")
        == {
            "status": "PENDING_THIS_PUBLICATION_CLOSURE_PR",
            "merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "ci": "TO_BE_BOUND_IN_EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        },
        "R46_PUBLICATION_CLOSURE_IDENTITY",
        repr(
            {
                "semantic_publication": r46_semantic_publication,
                "semantic_pr_github_ci": r46_pr_ci,
                "semantic_merge_main_ci": r46_main_ci,
            }
        ),
    )
    r46_fused_identity = r46_validation.get("fused_identity", {})
    check(
        r46_validation.get("change_scope")
        == {
            "changed_file_count": 89,
            "production_crate_change_count": 0,
            "grammar_production_change_count": 0,
            "source_spelling_change_count": 0,
            "semantic_change_count": 1,
            "new_diagnostic_id_count": 0,
        }
        and r46_fused_identity
        == {
            "continuation_interface_sha256":
                "fd5c28412c49c0405943f4ea13c9a196073de23030a9381f5d0bcb4a12b10ff1",
            "managed_reference_profile_sha256":
                "4e4a0145319db64f1857f8619dddffffba7c5f0be1de3c69c385290e3a2a20b3",
            "runtime_helper_registry_sha256":
                "622c8bdbe71d27709b69b544cba556dc256e5eda0083b3c22ceb7884ccd4c5e2",
            "runtime_abi_sha256":
                "26206926f0b6033ed520f4acd0277445bf583d32ae6d678e8281d6734539bf1c",
            "base_helper_count": 22,
            "managed_helper_count": 3,
            "active_helper_count": 25,
        }
        and r46_validation.get("workspace", {}).get("result") == "PASS"
        and r46_validation.get("workspace", {}).get("checks")
        == "6820_OF_6820_PASS"
        and r46_validation.get("source_manifest", {}).get(
            "file_count_excluding_manifest"
        ) == 770
        and r46_validation.get("source_manifest", {}).get(
            "total_bytes_excluding_manifest"
        ) == 23780120
        and r46_validation.get("source_manifest", {}).get("tree_sha256")
        == "1467ff62e7e787ef34a96bb39093d08190ebe52e44ed6cc32d3ea5f374e934b1"
        and r46_validation.get("evidence_level") == "E2_DESIGN_STATIC"
        and r46_validation.get("production_execution") == "NOT_RUN"
        and r46_gap_transition
        == {
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 3,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 3,
            "gap_ids": R46_PUBLICATION_CLOSURE_GAP_IDS,
        }
        and r46_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r46_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": R46_MANAGED_ROOT_RUNTIME_REVISION,
            "semantic_merge_commit": R46_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r46_independent.get("schema")
        == "deeplus.r46-managed-root-runtime-fusion-independent-verification/v1"
        and r46_independent.get("semantic_merge_commit")
        == R46_SEMANTIC_PUBLICATION_COMMIT
        and r46_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and r46_independent.get("product_execution") == "NOT_RUN"
        and r46_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R46_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "validation": r46_validation,
                "gap_transition": r46_gap_transition,
                "governance": r46_governance,
                "pointer_target": r46_pointer_target,
                "independent": r46_independent,
            }
        ),
    )
    r47_report_path = root / R47_PUBLICATION_CLOSURE_REPORT
    r47_receipt_path = root / R47_PUBLICATION_CLOSURE_RECEIPT
    r47_independent_path = root / R47_INDEPENDENT_VERIFICATION_RECEIPT
    r47_receipt = parsed.get(r47_receipt_path, {})
    r47_publication = r47_receipt.get("semantic_publication", {})
    r47_validation = r47_receipt.get("semantic_validation", {})
    r47_gap_transition = r47_receipt.get("gap_transition", {})
    r47_governance = r47_receipt.get("governance", {})
    r47_pointer_target = r47_receipt.get("pointer_target", {})
    r47_independent = parsed.get(r47_independent_path, {})
    r47_pr_ci = r47_receipt.get("semantic_pr_github_ci", [])
    r47_main_ci = r47_receipt.get("semantic_merge_main_ci", [])
    check(
        r47_report_path.is_file()
        and r47_receipt_path.is_file()
        and r47_independent_path.is_file()
        and r47_receipt.get("schema")
        == "deeplus.r47-ownership-contract-fusion-publication-closure-receipt/v1"
        and r47_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r47_publication.get("pull_request") == 65
        and r47_publication.get("source_commit") == R47_SEMANTIC_SOURCE_COMMIT
        and r47_publication.get("source_tree") == R47_SEMANTIC_PUBLICATION_TREE
        and r47_publication.get("merge_commit")
        == R47_SEMANTIC_PUBLICATION_COMMIT
        and r47_publication.get("tree") == R47_SEMANTIC_PUBLICATION_TREE
        and r47_publication.get("parents")
        == [
            "ab7fb2fd356262eeaf0b0bbdeb4d81e4d63d84e5",
            R47_SEMANTIC_SOURCE_COMMIT,
        ]
        and r47_publication.get("post_merge_readback") == "PASS"
        and len(r47_pr_ci) == 2
        and {row.get("workflow") for row in r47_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R47_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r47_pr_ci
        )
        and len(r47_main_ci) == 2
        and {row.get("workflow") for row in r47_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R47_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r47_main_ci
        ),
        "R47_PUBLICATION_CLOSURE_IDENTITY",
        repr(r47_publication),
    )
    check(
        r47_validation.get("change_scope")
        == {
            "changed_file_count": 194,
            "production_crate_change_count": 0,
            "bound_contract_count": 7,
            "grammar_production_count": 644,
            "feature_registry_count": 722,
            "diagnostic_registry_count": 1482,
        }
        and r47_validation.get("fused_identity")
        == {
            "continuation_interface_sha256":
                "0dc4891d1d23da397012f1ec1956ba1a3b52e884dbec604d27c8561a09941271",
            "managed_reference_profile_sha256":
                "feff3c021d4b77e64e4e9f00f797b0ce2c465a5b60709d86d0baf7bded72c7f7",
            "runtime_helper_registry_sha256":
                "990c6deb866b436f01c4961e307d84fe0b4ddc183082367f99e32246406deefc",
            "runtime_abi_sha256":
                "e2675436420814e9e4af6c3a7f530321f8c829c7d31d95533f371cbd9ba56146",
            "base_helper_count": 22,
            "managed_helper_count": 3,
            "active_helper_count": 25,
        }
        and r47_validation.get("workspace", {}).get("result") == "PASS"
        and r47_validation.get("source_manifest", {}).get(
            "file_count_excluding_manifest"
        ) == 815
        and r47_validation.get("source_manifest", {}).get(
            "total_bytes_excluding_manifest"
        ) == 24794736
        and r47_validation.get("source_manifest", {}).get("tree_sha256")
        == "f0466495d2cdc88bd09874f1b47fe5bcf23f34d1d79cf626c81ba3895a703fb6"
        and r47_gap_transition
        == {
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "transition_candidate_count": 7,
            "closed_count_before_closure_readback": 0,
            "eligible_closed_count_after_readback": 7,
            "gap_ids": R47_PUBLICATION_CLOSURE_GAP_IDS,
        }
        and r47_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "candidate_binding": False,
            "source_snapshot": None,
            "closed_by_candidate": 0,
            "new_feature_p1": 0,
        }
        and r47_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": R47_OWNERSHIP_CONTRACT_FUSION_REVISION,
            "semantic_merge_commit": R47_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r47_independent.get("schema")
        == "deeplus.r47-ownership-contract-fusion-independent-verification/v1"
        and r47_independent.get("semantic_merge_commit")
        == R47_SEMANTIC_PUBLICATION_COMMIT
        and r47_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and r47_independent.get("product_execution") == "NOT_RUN"
        and r47_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R47_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "validation": r47_validation,
                "gap_transition": r47_gap_transition,
                "governance": r47_governance,
                "pointer_target": r47_pointer_target,
                "independent": r47_independent,
            }
        ),
    )
    r74_report_path = root / R74_PUBLICATION_CLOSURE_REPORT
    r74_receipt_path = root / R74_PUBLICATION_CLOSURE_RECEIPT
    r74_independent_path = root / R74_INDEPENDENT_VERIFICATION_RECEIPT
    r74_receipt = parsed.get(r74_receipt_path, {})
    r74_publication = r74_receipt.get("semantic_publication", {})
    r74_traceability = r74_receipt.get("traceability", {})
    r74_transition = r74_receipt.get("publication_transition", {})
    r74_governance = r74_receipt.get("governance", {})
    r74_pointer_target = r74_receipt.get("pointer_target", {})
    r74_independent = parsed.get(r74_independent_path, {})
    r74_pr_ci = r74_receipt.get("semantic_pr_github_ci", [])
    r74_main_ci = r74_receipt.get("semantic_merge_main_ci", [])
    check(
        r74_report_path.is_file()
        and r74_receipt_path.is_file()
        and r74_independent_path.is_file()
        and r74_receipt.get("schema")
        == "deeplus.r48-r74-implementation-readiness-trace-publication-closure-receipt/v1"
        and r74_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r74_publication
        == {
            "pull_request": 67,
            "url": "https://github.com/howork/Deeplus/pull/67",
            "branch": "codex/r74-member-extension-collision-diagnostic-trace",
            "source_commit": R74_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R74_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R74_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R74_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "39a5d50cc770341c4b9776d00d84520b780d0c62",
                R74_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-03T20:51:58Z",
            "post_merge_readback": "PASS",
        }
        and len(r74_pr_ci) == len(r74_main_ci) == 2
        and {row.get("workflow") for row in r74_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and {row.get("workflow") for row in r74_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R74_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r74_pr_ci
        )
        and all(
            row.get("head_sha") == R74_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r74_main_ci
        ),
        "R74_PUBLICATION_CLOSURE_IDENTITY",
        repr(r74_publication),
    )
    check(
        r74_traceability
        == {
            "target_feature_rows": 469,
            "stage_cells": 3283,
            "test_outcome_cells": 1407,
            "bound_direct_cells": 2470,
            "bound_delegated_cells": 4,
            "not_applicable_cells": 502,
            "applicable_blocked_cells": 1245,
            "evidence_overlays": 19,
            "evidence_bindings": 136,
            "evidence_registry_entries": 3148,
        }
        and r74_transition
        == {
            "publication_unit": "R48_R74_CUMULATIVE_LINEAGE",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "umbrella_gap": "IR-XCUT-P1-054_OPEN_UNCHANGED",
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
        }
        and r74_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "current_binding": False,
        }
        and r74_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": R74_IMPLEMENTATION_READINESS_REVISION,
            "semantic_merge_commit": R74_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r74_independent.get("schema")
        == "deeplus.r48-r74-implementation-readiness-trace-independent-verification/v1"
        and r74_independent.get("semantic_merge_commit")
        == R74_SEMANTIC_PUBLICATION_COMMIT
        and r74_independent.get("verdict") == "PASS"
        and r74_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and r74_independent.get("product_execution") == "NOT_RUN"
        and r74_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R74_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "traceability": r74_traceability,
                "transition": r74_transition,
                "governance": r74_governance,
                "pointer_target": r74_pointer_target,
                "independent": r74_independent,
            }
        ),
    )
    r76_report_path = root / R76_PUBLICATION_CLOSURE_REPORT
    r76_receipt_path = root / R76_PUBLICATION_CLOSURE_RECEIPT
    r76_independent_path = root / R76_INDEPENDENT_VERIFICATION_RECEIPT
    r76_receipt = parsed.get(r76_receipt_path, {})
    r76_publication = r76_receipt.get("semantic_publication", {})
    r76_validation = r76_receipt.get("semantic_validation", {})
    r76_traceability = r76_receipt.get("traceability", {})
    r76_transition = r76_receipt.get("publication_transition", {})
    r76_gap_disposition = r76_receipt.get("gap_disposition", {})
    r76_governance = r76_receipt.get("governance", {})
    r76_pointer_target = r76_receipt.get("pointer_target", {})
    r76_independent = parsed.get(r76_independent_path, {})
    r76_pr_ci = r76_receipt.get("semantic_pr_github_ci", [])
    r76_main_ci = r76_receipt.get("semantic_merge_main_ci", [])
    check(
        r76_report_path.is_file()
        and r76_receipt_path.is_file()
        and r76_independent_path.is_file()
        and r76_receipt.get("schema")
        == "deeplus.r76-global-implementation-target-trace-publication-closure-receipt/v1"
        and r76_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and r76_publication
        == {
            "pull_request": 71,
            "url": "https://github.com/howork/Deeplus/pull/71",
            "branch": "codex/r76-global-trace-closure",
            "source_commit": R76_SEMANTIC_SOURCE_COMMIT,
            "source_tree": R76_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": R76_SEMANTIC_PUBLICATION_COMMIT,
            "tree": R76_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "40a826af29410af1a14c6a7dec3193cd59ba9b12",
                R76_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-04T04:14:37Z",
            "post_merge_readback": "PASS",
        }
        and len(r76_pr_ci) == len(r76_main_ci) == 2
        and {row.get("workflow") for row in r76_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and {row.get("workflow") for row in r76_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == R76_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r76_pr_ci
        )
        and all(
            row.get("head_sha") == R76_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in r76_main_ci
        ),
        "R76_PUBLICATION_CLOSURE_IDENTITY",
        repr(r76_publication),
    )
    check(
        r76_validation
        == {
            "change_scope": {
                "changed_file_count": 23,
                "production_crate_change_count": 0,
            },
            "focused_validation": {
                "global_gate_count": 8,
                "global_mutation_control_count": 8,
                "cumulative_mutation_control_count": 14,
                "predecessor_mutation_control_count": 84,
                "verdict": "PASS",
            },
            "workspace_validation": {
                "errors": 0,
                "warnings": 0,
                "verdict": "PASS",
            },
            "source_manifest": {
                "path": "release/source-tree-manifest.json",
                "file_count_excluding_manifest": 1028,
                "total_bytes_excluding_manifest": 32559800,
                "tree_sha256": (
                    "cf0c1e89997c45612edd0e0c53d3aee4cfca28b6c431a39b0a2b4bfc010a9823"
                ),
                "binding": "SEMANTIC_MERGE_TREE_BOUND",
                "hash_domain": "SHA256_CANONICAL_BYTES",
            },
            "evidence_level": "E2_DESIGN_STATIC",
            "production_execution": "NOT_RUN",
        }
        and r76_traceability
        == {
            "target_feature_rows": 469,
            "stage_cells": 3283,
            "test_outcome_cells": 1407,
            "atomic_cells": 4221,
            "bound_direct_cells": 3709,
            "bound_delegated_cells": 4,
            "not_applicable_cells": 508,
            "applicable_blocked_cells": 0,
            "evidence_overlays": 21,
            "evidence_bindings": 1381,
            "evidence_registry_entries": 4393,
        }
        and r76_transition
        == {
            "publication_unit": "R76_GLOBAL_IMPLEMENTATION_TARGET_TRACE_CLOSURE",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "closed_audit_gap": "IR-XCUT-P1-054_AFTER_CLOSURE_READBACK",
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
        }
        and r76_gap_disposition
        == {
            "verified_closed_after_closure_readback": ["IR-XCUT-P1-054"],
            "remaining_open_audit_p0_p1": [],
            "explicitly_deferred": ["IR-ACTOR-P2-008"],
        }
        and r76_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "current_binding": False,
        }
        and r76_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": R76_GLOBAL_TRACE_CLOSURE_REVISION,
            "semantic_merge_commit": R76_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and r76_independent.get("schema")
        == "deeplus.r76-global-implementation-target-trace-independent-verification/v1"
        and r76_independent.get("semantic_merge_commit")
        == R76_SEMANTIC_PUBLICATION_COMMIT
        and r76_independent.get("verdict") == "PASS"
        and r76_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and r76_independent.get("product_execution") == "NOT_RUN"
        and r76_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R76_PUBLICATION_CLOSURE_GOVERNANCE",
        repr(
            {
                "validation": r76_validation,
                "traceability": r76_traceability,
                "transition": r76_transition,
                "gap_disposition": r76_gap_disposition,
                "governance": r76_governance,
                "pointer_target": r76_pointer_target,
                "independent": r76_independent,
            }
        ),
    )
    g4_report_path = root / G4_PUBLICATION_CLOSURE_REPORT
    g4_receipt_path = root / G4_PUBLICATION_CLOSURE_RECEIPT
    g4_independent_path = root / G4_INDEPENDENT_VERIFICATION_RECEIPT
    g4_receipt = parsed.get(g4_receipt_path, {})
    g4_publication = g4_receipt.get("semantic_publication", {})
    g4_pr_ci = g4_receipt.get("semantic_pr_github_ci", [])
    g4_main_ci = g4_receipt.get("semantic_merge_main_ci", [])
    g4_validation = g4_receipt.get("semantic_validation", {})
    g4_readiness = g4_receipt.get("readiness", {})
    g4_transition = g4_receipt.get("publication_transition", {})
    g4_governance = g4_receipt.get("governance", {})
    g4_pointer_target = g4_receipt.get("pointer_target", {})
    g4_independent = parsed.get(g4_independent_path, {})
    check(
        g4_report_path.is_file()
        and g4_receipt_path.is_file()
        and g4_independent_path.is_file()
        and g4_receipt.get("schema")
        == "deeplus.g4-independent-implementation-readiness-publication-closure-receipt/v1"
        and g4_receipt.get("candidate_verdict")
        == "READY_FOR_PUBLICATION_CLOSURE_MERGE"
        and g4_publication
        == {
            "pull_request": 73,
            "url": "https://github.com/howork/Deeplus/pull/73",
            "branch": "codex/g4-independent-readiness-audit",
            "source_commit": G4_SEMANTIC_SOURCE_COMMIT,
            "source_tree": G4_SEMANTIC_PUBLICATION_TREE,
            "merge_commit": G4_SEMANTIC_PUBLICATION_COMMIT,
            "tree": G4_SEMANTIC_PUBLICATION_TREE,
            "parents": [
                "6782bcb576b7685a706b410620db8ea495aab901",
                G4_SEMANTIC_SOURCE_COMMIT,
            ],
            "merged_at": "2026-08-04T05:50:53Z",
            "post_merge_readback": "PASS",
        }
        and len(g4_pr_ci) == len(g4_main_ci) == 2
        and {row.get("workflow") for row in g4_pr_ci}
        == {"Canonical integrity", "Rust workspace"}
        and {row.get("workflow") for row in g4_main_ci}
        == {"Canonical integrity", "Rust workspace"}
        and all(
            row.get("head_sha") == G4_SEMANTIC_SOURCE_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in g4_pr_ci
        )
        and all(
            row.get("head_sha") == G4_SEMANTIC_PUBLICATION_COMMIT
            and row.get("conclusion") == "SUCCESS"
            for row in g4_main_ci
        ),
        "G4_PUBLICATION_CLOSURE_IDENTITY",
        repr(g4_publication),
    )
    check(
        g4_validation
        == {
            "change_scope": {
                "changed_file_count": 7,
                "production_crate_change_count": 0,
                "language_semantic_change_count": 0,
            },
            "focused_validation": {
                "g4_gate_count": 5,
                "workspace_checks": 7725,
                "verdict": "PASS",
            },
            "source_manifest": {
                "path": "release/source-tree-manifest.json",
                "file_count_excluding_manifest": 1035,
                "total_bytes_excluding_manifest": 32600586,
                "tree_sha256": (
                    "5e92e493cd41adc5978084bf9dd7b4bd89228627ea111f7571ae7e6d9288fef2"
                ),
                "binding": "SEMANTIC_MERGE_TREE_BOUND",
                "hash_domain": "SHA256_CANONICAL_BYTES",
            },
            "evidence_level": "E2_DESIGN_STATIC",
            "production_execution": "NOT_RUN",
        }
        and g4_readiness
        == {
            "catalog_features": 723,
            "target_feature_rows": 469,
            "excluded_feature_rows": 254,
            "stage_cells": 3283,
            "test_outcome_cells": 1407,
            "atomic_cells": 4221,
            "bound_direct_cells": 3709,
            "bound_delegated_cells": 4,
            "not_applicable_cells": 508,
            "missing_cells": 0,
            "conflict_cells": 0,
            "applicable_blocked_cells": 0,
            "gates": "5_OF_5_PASS_E2",
            "target_profile_unresolved_p0": 0,
            "target_profile_unresolved_p1": 0,
        }
        and g4_transition
        == {
            "publication_unit": "G4_INDEPENDENT_IMPLEMENTATION_READINESS_AUDIT",
            "semantic_merge_state": "INTEGRATED_UNVERIFIED",
            "closure_state_after_closure_merge_readback": "VERIFIED_CLOSED",
            "goal_verdict_after_closure_readback": (
                "IMPLEMENTATION_TARGET_PROFILE_SPECIFICATION_READY"
            ),
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
        }
        and g4_governance
        == {
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN_UNCHANGED_OUTSIDE_TARGET_PROFILE",
            "separate_m13_actions": "4_OPEN_UNCHANGED",
            "nonblocking_p2": "IR-ACTOR-P2-008_EXPLICITLY_DEFERRED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "current_binding": False,
        }
        and g4_pointer_target
        == {
            "role": "publication_authority_source",
            "revision": G4_INDEPENDENT_READINESS_REVISION,
            "semantic_merge_commit": G4_SEMANTIC_PUBLICATION_COMMIT,
            "closure_merge_commit": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
            "self_binding_forbidden": True,
        }
        and g4_independent.get("schema")
        == "deeplus.g4-independent-implementation-readiness-independent-verification/v1"
        and g4_independent.get("semantic_merge_commit")
        == G4_SEMANTIC_PUBLICATION_COMMIT
        and g4_independent.get("verdict") == "PASS"
        and g4_independent.get("evidence_level") == "E2_DESIGN_STATIC"
        and g4_independent.get("product_execution") == "NOT_RUN"
        and g4_independent.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "G4_PUBLICATION_CLOSURE_GOVERNANCE",
        repr({"validation": g4_validation, "readiness": g4_readiness}),
    )
    current_decisions = parsed.get(
        root / "decisions/language/current-decisions.json", {}
    )
    current_laws = current_decisions.get("laws", [])
    r4_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R4_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r25_r27_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R25_R27_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r41_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R41_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r23_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R23_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r46_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R46_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r47_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R47_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r74_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R74_PUBLICATION_CLOSURE_DECISION_ID
    ]
    r76_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R76_PUBLICATION_CLOSURE_DECISION_ID
    ]
    g4_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == G4_PUBLICATION_CLOSURE_DECISION_ID
    ]
    check(
        len(g4_closure_laws) == 1
        and g4_closure_laws[0].get("status") == "CURRENT"
        and g4_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and g4_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and g4_closure_laws[0].get("effective_revision")
        == G4_INDEPENDENT_READINESS_REVISION
        and G4_PUBLICATION_CLOSURE_REPORT
        in g4_closure_laws[0].get("source_evidence", "")
        and G4_PUBLICATION_CLOSURE_RECEIPT
        in g4_closure_laws[0].get("source_evidence", "")
        and G4_INDEPENDENT_VERIFICATION_RECEIPT
        in g4_closure_laws[0].get("source_evidence", "")
        and G4_SEMANTIC_SOURCE_COMMIT in g4_closure_laws[0].get("law", "")
        and G4_SEMANTIC_PUBLICATION_COMMIT in g4_closure_laws[0].get("law", "")
        and G4_SEMANTIC_PUBLICATION_TREE in g4_closure_laws[0].get("law", "")
        and "5/5 PASS_E2" in g4_closure_laws[0].get("law", "")
        and "22 canonical feature P1 actions remain OPEN"
        in g4_closure_laws[0].get("law", "")
        and "15 product lanes remain NOT_RUN"
        in g4_closure_laws[0].get("law", ""),
        "G4_PUBLICATION_CLOSURE_DECISION",
        repr(g4_closure_laws),
    )
    check(
        len(r76_closure_laws) == 1
        and r76_closure_laws[0].get("status") == "CURRENT"
        and r76_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r76_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r76_closure_laws[0].get("effective_revision")
        == R76_GLOBAL_TRACE_CLOSURE_REVISION
        and R76_PUBLICATION_CLOSURE_REPORT
        in r76_closure_laws[0].get("source_evidence", "")
        and R76_PUBLICATION_CLOSURE_RECEIPT
        in r76_closure_laws[0].get("source_evidence", "")
        and R76_INDEPENDENT_VERIFICATION_RECEIPT
        in r76_closure_laws[0].get("source_evidence", "")
        and R76_SEMANTIC_SOURCE_COMMIT
        in r76_closure_laws[0].get("law", "")
        and R76_SEMANTIC_PUBLICATION_COMMIT
        in r76_closure_laws[0].get("law", "")
        and R76_SEMANTIC_PUBLICATION_TREE
        in r76_closure_laws[0].get("law", "")
        and "IR-XCUT-P1-054" in r76_closure_laws[0].get("law", "")
        and "3,709 BOUND_DIRECT" in r76_closure_laws[0].get("law", "")
        and "0 APPLICABLE_BLOCKED_BY_GAP"
        in r76_closure_laws[0].get("law", "")
        and "22 OPEN" in r76_closure_laws[0].get("law", "")
        and "15 product lanes NOT_RUN"
        in r76_closure_laws[0].get("law", ""),
        "R76_PUBLICATION_CLOSURE_DECISION",
        repr(r76_closure_laws),
    )
    check(
        len(r74_closure_laws) == 1
        and r74_closure_laws[0].get("status") == "CURRENT"
        and r74_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r74_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r74_closure_laws[0].get("effective_revision")
        == R74_IMPLEMENTATION_READINESS_REVISION
        and R74_PUBLICATION_CLOSURE_REPORT
        in r74_closure_laws[0].get("source_evidence", "")
        and R74_PUBLICATION_CLOSURE_RECEIPT
        in r74_closure_laws[0].get("source_evidence", "")
        and R74_INDEPENDENT_VERIFICATION_RECEIPT
        in r74_closure_laws[0].get("source_evidence", "")
        and R74_SEMANTIC_PUBLICATION_COMMIT
        in r74_closure_laws[0].get("law", "")
        and "IR-XCUT-P1-054" in r74_closure_laws[0].get("law", "")
        and "1,245 trace cells remain APPLICABLE_BLOCKED_BY_GAP"
        in r74_closure_laws[0].get("law", "")
        and "22 OPEN" in r74_closure_laws[0].get("law", "")
        and "15 product lanes remain NOT_RUN"
        in r74_closure_laws[0].get("law", ""),
        "R74_PUBLICATION_CLOSURE_DECISION",
        repr(r74_closure_laws),
    )
    check(
        len(r47_closure_laws) == 1
        and r47_closure_laws[0].get("status") == "CURRENT"
        and r47_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r47_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r47_closure_laws[0].get("effective_revision")
        == R47_OWNERSHIP_CONTRACT_FUSION_REVISION
        and R47_PUBLICATION_CLOSURE_REPORT
        in r47_closure_laws[0].get("source_evidence", "")
        and R47_PUBLICATION_CLOSURE_RECEIPT
        in r47_closure_laws[0].get("source_evidence", "")
        and R47_INDEPENDENT_VERIFICATION_RECEIPT
        in r47_closure_laws[0].get("source_evidence", "")
        and all(
            gap_id in r47_closure_laws[0].get("law", "")
            for gap_id in R47_PUBLICATION_CLOSURE_GAP_IDS
        )
        and "22 base plus three managed helpers"
        in r47_closure_laws[0].get("law", "")
        and "15 product lanes NOT_RUN"
        in r47_closure_laws[0].get("law", ""),
        "R47_PUBLICATION_CLOSURE_DECISION",
        repr(r47_closure_laws),
    )
    check(
        len(r46_closure_laws) == 1
        and r46_closure_laws[0].get("status") == "CURRENT"
        and r46_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r46_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r46_closure_laws[0].get("effective_revision")
        == R46_MANAGED_ROOT_RUNTIME_REVISION
        and R46_PUBLICATION_CLOSURE_REPORT
        in r46_closure_laws[0].get("source_evidence", "")
        and R46_PUBLICATION_CLOSURE_RECEIPT
        in r46_closure_laws[0].get("source_evidence", "")
        and R46_INDEPENDENT_VERIFICATION_RECEIPT
        in r46_closure_laws[0].get("source_evidence", "")
        and all(
            gap_id in r46_closure_laws[0].get("law", "")
            for gap_id in R46_PUBLICATION_CLOSURE_GAP_IDS
        )
        and "25" in r46_closure_laws[0].get("law", "")
        and "15 product lanes NOT_RUN" in r46_closure_laws[0].get("law", ""),
        "R46_PUBLICATION_CLOSURE_DECISION",
        repr(r46_closure_laws),
    )
    check(
        len(r23_closure_laws) == 1
        and r23_closure_laws[0].get("status") == "CURRENT"
        and r23_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r23_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r23_closure_laws[0].get("effective_revision")
        == R23_ACTOR_PROTOCOL_BINDING_REVISION
        and R23_PUBLICATION_CLOSURE_REPORT
        in r23_closure_laws[0].get("source_evidence", "")
        and R23_PUBLICATION_CLOSURE_RECEIPT
        in r23_closure_laws[0].get("source_evidence", "")
        and R23_INDEPENDENT_VERIFICATION_RECEIPT
        in r23_closure_laws[0].get("source_evidence", "")
        and all(
            gap_id in r23_closure_laws[0].get("law", "")
            for gap_id in R23_PUBLICATION_CLOSURE_GAP_IDS
        ),
        "R23_PUBLICATION_CLOSURE_DECISION",
        repr(r23_closure_laws),
    )
    check(
        len(r41_closure_laws) == 1
        and r41_closure_laws[0].get("status") == "CURRENT"
        and r41_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r41_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r41_closure_laws[0].get("effective_revision")
        == R41_ACTOR_PROTOCOL_REVISION
        and R41_PUBLICATION_CLOSURE_REPORT
        in r41_closure_laws[0].get("source_evidence", "")
        and R41_PUBLICATION_CLOSURE_RECEIPT
        in r41_closure_laws[0].get("source_evidence", "")
        and R41_INDEPENDENT_VERIFICATION_RECEIPT
        in r41_closure_laws[0].get("source_evidence", "")
        and all(
            gap_id in r41_closure_laws[0].get("law", "")
            for gap_id in R41_PUBLICATION_CLOSURE_GAP_IDS
        ),
        "R41_PUBLICATION_CLOSURE_DECISION",
        repr(r41_closure_laws),
    )
    check(
        len(r25_r27_closure_laws) == 1
        and r25_r27_closure_laws[0].get("status") == "CURRENT"
        and r25_r27_closure_laws[0].get("authority_origin")
        == "CODEX_DESIGN_USER_DELEGATED"
        and r25_r27_closure_laws[0].get("ratification_status")
        == "CURRENT_USER_DELEGATED_AUTHORITY"
        and r25_r27_closure_laws[0].get("effective_revision")
        == R11_R19_FRONTEND_REVISION
        and R25_R27_PUBLICATION_CLOSURE_REPORT
        in r25_r27_closure_laws[0].get("source_evidence", "")
        and R25_R27_PUBLICATION_CLOSURE_RECEIPT
        in r25_r27_closure_laws[0].get("source_evidence", "")
        and all(
            gap_id in r25_r27_closure_laws[0].get("law", "")
            for gap_id in R25_R27_PUBLICATION_CLOSURE_GAP_IDS
        ),
        "R25_R27_PUBLICATION_CLOSURE_DECISION",
        repr(r25_r27_closure_laws),
    )
    check(
        current_decisions.get("law_count") == len(current_laws)
        == (
            69
            if revision == R77_PUBLICATION_POLICY_CLOSURE_REVISION
            else 68
            if revision == G4_INDEPENDENT_READINESS_REVISION
            else 66
            if revision == R76_GLOBAL_TRACE_CLOSURE_REVISION
            else 65
            if revision == R75_ACTOR_CRANELIFT_PROJECTION_REVISION
            else 64
            if revision == R74_IMPLEMENTATION_READINESS_REVISION
            else 63
            if revision == R47_OWNERSHIP_CONTRACT_FUSION_REVISION
            else 61
            if revision == R46_MANAGED_ROOT_RUNTIME_REVISION
            else 60
            if revision == R23_ACTOR_PROTOCOL_BINDING_REVISION
            else 59
            if revision == R41_ACTOR_PROTOCOL_REVISION
            else 58
            if revision == R11_R19_FRONTEND_REVISION
            else 46
            if revision == R10_HIR_MIR_REVISION
            else 44
        )
        and r4_closure_laws
        == [
            {
                "id": R4_PUBLICATION_CLOSURE_DECISION_ID,
                "law": (
                    "The R4 Name Resolution, Modules, Package and Visibility "
                    "contract is canonically integrated by PR #46 at semantic "
                    "merge commit "
                    "8d81d6747488055cb76da8bda1350b96e576b7b1. Its exact 12 "
                    "implementation-readiness audit gaps move from "
                    "APPROVED_NOT_INTEGRATED to INTEGRATED_UNVERIFIED at that "
                    "semantic merge and become VERIFIED_CLOSED only after the "
                    "separate publication-closure PR is merged, live main is "
                    "read back, and the bound independent Test_ verification "
                    "passes. This governance transition changes no language "
                    "semantics, closes or creates no canonical feature P1, "
                    "leaves the exact feature P1 set at 22 OPEN, and leaves "
                    "all 15 product lanes NOT_RUN."
                ),
                "status": "CURRENT",
                "authority_origin": "DESIGNER_ACCEPTED",
                "ratification_status": "CURRENT_USER_DELEGATED_AUTHORITY",
                "source_evidence": (
                    "governance/reports/"
                    "Design_Deeplus_R4_Name_Resolution_Module_"
                    "Publication_Closure_R1.md; "
                    "release/evidence/"
                    "r4-name-resolution-modules-publication-closure-"
                    "receipt.json"
                ),
                "effective_revision": LANGUAGE_COHERENCE_REVISION,
            }
        ],
        "R4_PUBLICATION_CLOSURE_DECISION",
        repr(r4_closure_laws),
    )
    r8_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R8_PUBLICATION_CLOSURE_DECISION_ID
    ]
    check(
        r8_closure_laws
        == [
            {
                "id": R8_PUBLICATION_CLOSURE_DECISION_ID,
                "law": (
                    "The frozen R8 promotion of the R5 Ownership Surface and "
                    "Place/Loan contract is canonically integrated by PR #48 "
                    "at semantic merge commit "
                    "9bc2e8694bc44cea28efe34541ce465a9bf2c109. Its exact three "
                    "implementation-readiness audit gaps IR-OWN-P0-012, "
                    "IR-OWN-P0-013, and IR-OWN-P0-014 moved to "
                    "INTEGRATED_UNVERIFIED at that semantic merge and become "
                    "VERIFIED_CLOSED only after the separate publication-"
                    "closure PR is merged, live main is read back, and the "
                    "bound independent verification passes. This governance "
                    "transition changes no language semantics, closes or "
                    "creates no canonical feature P1, leaves the exact feature "
                    "P1 set at 22 OPEN, leaves the four M13 actions separate "
                    "and OPEN, and leaves all 15 product lanes NOT_RUN."
                ),
                "status": "CURRENT",
                "authority_origin": "DESIGNER_ACCEPTED",
                "ratification_status": "CURRENT_USER_DELEGATED_AUTHORITY",
                "source_evidence": (
                    "governance/reports/"
                    "Design_Deeplus_R8_Ownership_Canonical_Promotion_"
                    "Publication_Closure_R1.md; "
                    "release/evidence/"
                    "r8-ownership-canonical-promotion-publication-"
                    "closure-receipt.json"
                ),
                "effective_revision": LANGUAGE_COHERENCE_REVISION,
            }
        ],
        "R8_PUBLICATION_CLOSURE_DECISION",
        repr(r8_closure_laws),
    )
    r9_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R9_PUBLICATION_CLOSURE_DECISION_ID
    ]
    check(
        r9_closure_laws
        == [
            {
                "id": R9_PUBLICATION_CLOSURE_DECISION_ID,
                "law": (
                    "The R9 Diagnostic Dispatch Closure for implementation-"
                    "readiness gap IR-DIAG-P0-052 is canonically integrated "
                    "by semantic PR #50: source commit "
                    "94b4d369213ec3ce829c70b66f15301cf3c7039c was merged at "
                    "fd752f560d30a9cbe61f04b24b0e58abdbc150a3 with exact tree "
                    "3afc92cae7f8cf7232e30944d6516aec811e6981. "
                    "IR-DIAG-P0-052 moved to INTEGRATED_UNVERIFIED at that "
                    "semantic merge and becomes VERIFIED_CLOSED at "
                    "design/static evidence level E2 only after the separate "
                    "publication-closure PR is merged, live main is read "
                    "back, and the external post-merge receipt records the "
                    "actual closure commit; no future closure commit SHA is "
                    "predicted here. Production implementation and product "
                    "execution remain NOT_RUN. This governance transition "
                    "closes or creates no canonical feature P1, leaves the "
                    "exact feature P1 set at 22 OPEN, leaves the four M13 "
                    "actions separate and OPEN, and leaves all 15 product "
                    "lanes NOT_RUN."
                ),
                "status": "CURRENT",
                "authority_origin": "DESIGNER_ACCEPTED",
                "ratification_status": "CURRENT_USER_DELEGATED_AUTHORITY",
                "source_evidence": (
                    "governance/reports/"
                    "Design_Deeplus_R9_Diagnostic_Dispatch_Publication_"
                    "Closure_R1.md; release/evidence/"
                    "r9-diagnostic-dispatch-publication-closure-receipt.json; "
                    "release/evidence/"
                    "r9-diagnostic-dispatch-independent-verification.json; "
                    "external audit/implementation-readiness-state "
                    "post-merge readback receipt"
                ),
                "effective_revision": LANGUAGE_COHERENCE_REVISION,
            }
        ],
        "R9_PUBLICATION_CLOSURE_DECISION",
        repr(r9_closure_laws),
    )
    r10_closure_laws = [
        row
        for row in current_laws
        if row.get("id") == R10_PUBLICATION_CLOSURE_DECISION_ID
    ]
    check(
        r10_closure_laws
        == [
            {
                "id": R10_PUBLICATION_CLOSURE_DECISION_ID,
                "law": (
                    "The R10 HIR/MIR Machine Contract for implementation-"
                    "readiness gap IR-OWN-P0-015 is canonically integrated "
                    "by semantic PR #52: source commit "
                    "6460e8127620d495e055cd0b800198fb6f7e1a06 was merged at "
                    "7d609678bdb8c94f2a365e89be578e595bb394b6 with exact tree "
                    "76189fb47e75d4faeb3f2f975f51df265dc42146. "
                    "IR-OWN-P0-015 moved to INTEGRATED_UNVERIFIED at that "
                    "semantic merge and becomes VERIFIED_CLOSED at "
                    "design/static evidence level E2 only after the separate "
                    "publication-closure PR is merged, live main is read back, "
                    "and the external post-merge receipt records the actual "
                    "closure commit; no future closure commit SHA is predicted "
                    "here. Production implementation and product execution "
                    "remain NOT_RUN. This governance transition closes or "
                    "creates no canonical feature P1, leaves the exact feature "
                    "P1 set at 22 OPEN, leaves the four M13 actions separate "
                    "and OPEN, and leaves all 15 product lanes NOT_RUN."
                ),
                "status": "CURRENT",
                "authority_origin": "DESIGNER_ACCEPTED",
                "ratification_status": "CURRENT_USER_DELEGATED_AUTHORITY",
                "source_evidence": (
                    "governance/reports/"
                    "Design_Deeplus_R10_HIR_MIR_Machine_Contract_"
                    "Publication_Closure_R1.md; release/evidence/"
                    "r10-hir-mir-machine-contract-publication-closure-"
                    "receipt.json; release/evidence/"
                    "r10-hir-mir-machine-contract-independent-verification."
                    "json; external audit/implementation-readiness-state "
                    "post-merge readback receipt"
                ),
                "effective_revision": R10_HIR_MIR_REVISION,
            }
        ],
        "R10_PUBLICATION_CLOSURE_DECISION",
        repr(r10_closure_laws),
    )
    r4_test_verification = parsed.get(
        root / R4_INDEPENDENT_TEST_VERIFICATION_RECEIPT, {}
    )
    r4_test_path = root / R4_INDEPENDENT_TEST_VERIFICATION_RECEIPT
    check(
        r4_test_path.is_file()
        and r4_test_path.stat().st_size == r4_independent_test.get("bytes")
        and file_sha(r4_test_path) == r4_independent_test.get("sha256")
        and r4_test_verification.get("schema")
        == (
            "deeplus.r4-name-resolution-modules-independent-test-"
            "verification/v1"
        )
        and r4_test_verification.get("role") == "Test_"
        and r4_test_verification.get("reviewer_identity")
        == (
            "Codex Test_ independent closure auditor / "
            "r4_visibility_init_dependency_audit"
        )
        and r4_test_verification.get("repository_write") is False
        and r4_test_verification.get("verdict")
        == r4_independent_test.get("required_verdict")
        and r4_test_verification.get("merge_readiness")
        == "HOLD_PENDING_RECEIPT_AND_SOURCE_MANIFEST_BINDING"
        and r4_test_verification.get("semantic_merge_commit")
        == R4_SEMANTIC_PUBLICATION_COMMIT
        and r4_test_verification.get("semantic_merge_tree")
        == "1cc3ff5c5813678b5cc9c3465ceacd922bb63d06"
        and r4_test_verification.get("semantic_merge_parents")
        == [
            "53464e47bc280d4f431440eb7538d9d97c0a7aa7",
            "86669e990e4ad15cd4dd7e9034bf0c34c62cc8d6",
        ]
        and r4_test_verification.get("reviewed_gap_ids")
        == R4_PUBLICATION_CLOSURE_GAP_IDS
        and r4_test_verification.get("reviewed_acceptance_oracle")
        == {
            "scope": (
                "PERSISTENT_AUDIT_WORKSPACE_OUTSIDE_CANONICAL_GIT_TREE"
            ),
            "path": (
                "audit/implementation-readiness-r4-name-resolution-modules/"
                "Codex_Design_Deeplus_Name_Resolution_Module_"
                "Acceptance_Spec_R4.json"
            ),
            "bytes": 95844,
            "sha256": (
                "bfbe4ba3d4447835fc6e8f692bbf44125edc2923e7ad68c77b555"
                "1c505b5aa38"
            ),
            "structured_outlines": 150,
            "gap_outlines": 36,
            "gap_oracle_array_sha256": (
                "454cbbdfaa62cd8892c93c7eb812e9ad1b21dd4eceb3fb3711bee4"
                "8728b32be3"
            ),
            "executed_product_count": 0,
        }
        and r4_test_verification.get("verified_ledger")
        == {
            "gap_transition_candidates": 12,
            "severity_counts": {"P0": 2, "P1": 9, "P2": 1},
            "closed_before_closure_readback": 0,
            "eligible_after_closure_readback": 12,
            "semantic_p0": 0,
            "open_actions": 26,
            "canonical_feature_p1": "22_OPEN",
            "separate_m13_actions": 4,
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
            "current_binding": False,
        }
        and len(r4_test_verification.get("executed_commands", [])) == 8
        and all(
            row.get("result", "").startswith("PASS")
            or row.get("result") in {
                "316_OF_316_PASS",
                "36_OF_36_PASS",
                "73_OF_73_REJECTED_AS_REQUIRED",
            }
            for row in r4_test_verification.get("executed_commands", [])
        )
        and r4_test_verification.get("product_lanes")
        == "15_OF_15_NOT_RUN"
        and r4_test_verification.get("product_support") == "NOT_RUN"
        and r4_test_verification.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R4_INDEPENDENT_TEST_VERIFICATION",
        repr(r4_test_verification),
    )
    r8_test_verification = parsed.get(
        root / R8_INDEPENDENT_TEST_VERIFICATION_RECEIPT, {}
    )
    r8_test_path = root / R8_INDEPENDENT_TEST_VERIFICATION_RECEIPT
    check(
        r8_test_path.is_file()
        and r8_test_path.stat().st_size == r8_independent_test.get("bytes")
        and file_sha(r8_test_path) == r8_independent_test.get("sha256")
        and r8_test_verification.get("schema")
        == (
            "deeplus.r8-ownership-canonical-promotion-independent-"
            "verification/v1"
        )
        and r8_test_verification.get("recorded_at")
        == "2026-07-31T03:33:54+09:00"
        and r8_test_verification.get("role") == "Test_"
        and r8_test_verification.get("reviewer_identity")
        == (
            "Codex Test_ independent R8 final-validation audit / "
            "R8_FINAL_VALIDATION_INDEPENDENT_AUDIT_R1"
        )
        and r8_test_verification.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r8_test_verification.get("repository_write") is False
        and r8_test_verification.get("verdict")
        == r8_independent_test.get("required_verdict")
        and r8_test_verification.get("merge_readiness")
        == "HOLD_PENDING_PUBLICATION_CLOSURE_MERGE_AND_READBACK"
        and r8_test_verification.get("semantic_merge_commit")
        == R8_SEMANTIC_PUBLICATION_COMMIT
        and r8_test_verification.get("semantic_merge_tree")
        == "26ca3acb8377c860482bf21aa646155377fe81af"
        and r8_test_verification.get("semantic_merge_parents")
        == [
            "1053902449aedccb110cef5bcfe76e5b1af9df01",
            "8efc9ef3e1b60723fe5f0fa15ec638479fbed64e",
        ]
        and r8_test_verification.get("reviewed_gap_ids")
        == R8_PUBLICATION_CLOSURE_GAP_IDS
        and r8_test_verification.get("frozen_candidate_pack")
        == {
            "scope": (
                "PERSISTENT_AUDIT_WORKSPACE_OUTSIDE_CANONICAL_GIT_TREE"
            ),
            "path": (
                "audit/implementation-readiness-r8-ownership-canonical-"
                "promotion/final-freeze-r8/"
                "Codex_Design_Deeplus_R8_Ownership_Canonical_Promotion_"
                "Source_Candidate_Pack_R8.zip"
            ),
            "filename": (
                "Codex_Design_Deeplus_R8_Ownership_Canonical_Promotion_"
                "Source_Candidate_Pack_R8.zip"
            ),
            "bytes": 9701905,
            "sha256": (
                "ae730ce57b8985d69d150f4eba9b21609bbfee5003b86016909a04"
                "cf68327f3c"
            ),
            "member_count": 161,
        }
        and r8_test_verification.get("bound_independent_audit_member")
        == {
            "path": (
                "inputs/execution/"
                "R8_FINAL_VALIDATION_INDEPENDENT_AUDIT_R1.json"
            ),
            "bytes": 9921,
            "sha256": (
                "7b2ba7f5941968b086903ff0adb5d9f981d1999aaeb58b3f5681e"
                "968d6e05be4"
            ),
            "result": "PASS_WITH_NONBLOCKING_BASELINE_P2",
        }
        and r8_test_verification.get("verified_ledger")
        == {
            "gap_transition_candidates": 3,
            "severity_counts": {"P0": 3, "P1": 0, "P2": 0},
            "closed_before_closure_readback": 0,
            "eligible_after_closure_readback": 3,
            "remaining_audit_gaps_after_closure": {
                "P0": 10,
                "P1": 23,
                "P2": 4,
            },
            "semantic_p0": 0,
            "open_actions": 26,
            "canonical_feature_p1": "22_OPEN",
            "separate_m13_actions": 4,
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
            "current_binding": False,
        }
        and r8_test_verification.get("verified_evidence", {}).get(
            "command_matrix", {}
        ).get("passed") == 23
        and r8_test_verification.get("verified_evidence", {}).get(
            "ownership", {}
        ).get("passed") == 13
        and r8_test_verification.get("verified_evidence", {}).get(
            "workspace", {}
        ).get("passed") == 3739
        and r8_test_verification.get("verified_evidence", {}).get(
            "clippy_baseline_parity", {}
        ).get("passed") == 4
        and r8_test_verification.get("product_lanes")
        == "15_OF_15_NOT_RUN"
        and r8_test_verification.get("product_support") == "NOT_RUN"
        and r8_test_verification.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK",
        "R8_INDEPENDENT_TEST_VERIFICATION",
        repr(r8_test_verification),
    )
    r9_test_path = root / R9_INDEPENDENT_TEST_VERIFICATION_RECEIPT
    r9_test_verification = parsed.get(r9_test_path, {})
    check(
        r9_test_path.is_file()
        and r9_test_path.stat().st_size
        == R9_INDEPENDENT_TEST_VERIFICATION_BYTES
        and file_sha(r9_test_path)
        == R9_INDEPENDENT_TEST_VERIFICATION_SHA256
        and r9_test_path.stat().st_size == r9_independent_test.get("bytes")
        and file_sha(r9_test_path) == r9_independent_test.get("sha256")
        and r9_test_verification.get("schema")
        == "deeplus.r9-diagnostic-dispatch-independent-verification/v1"
        and r9_test_verification.get("recorded_at")
        == "2026-07-31T06:51:12+09:00"
        and r9_test_verification.get("role") == "Test_"
        and r9_test_verification.get("reviewer_identity")
        == "Codex Test_ independent R9 publication-closure audit"
        and r9_test_verification.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r9_test_verification.get("repository_write") is False
        and r9_test_verification.get("verdict")
        == r9_independent_test.get("required_verdict")
        and r9_test_verification.get("merge_readiness")
        == "HOLD_PENDING_PUBLICATION_CLOSURE_MERGE_AND_READBACK"
        and r9_test_verification.get("semantic_pull_request") == 50
        and r9_test_verification.get("semantic_source_commit")
        == R9_SEMANTIC_SOURCE_COMMIT
        and r9_test_verification.get("semantic_merge_commit")
        == R9_SEMANTIC_PUBLICATION_COMMIT
        and r9_test_verification.get("semantic_merge_tree")
        == R9_SEMANTIC_PUBLICATION_TREE
        and r9_test_verification.get("semantic_merge_parents")
        == [
            "336e7b9919dbd6bdcccca71a7be32d3ed7a88b5b",
            R9_SEMANTIC_SOURCE_COMMIT,
        ]
        and r9_test_verification.get("post_semantic_merge_readback")
        == "PASS"
        and r9_test_verification.get("reviewed_gap_ids")
        == R9_PUBLICATION_CLOSURE_GAP_IDS
        and r9_test_verification.get("frozen_candidate_pack")
        == {
            "scope": (
                "PERSISTENT_AUDIT_WORKSPACE_OUTSIDE_CANONICAL_GIT_TREE"
            ),
            "filename": (
                "Codex_Design_Deeplus_R9_Diagnostic_Dispatch_Closure_"
                "Candidate_Freeze_Pack_R5.zip"
            ),
            "bytes": 116490,
            "sha256": (
                "541da4136e420d80f068fa72dc48b468cd8e8ad551c3ced32c8f"
                "881d00e932e0"
            ),
            "semantic_predecessor": "R4_BYTE_BOUND_UNCHANGED",
            "semantic_delta_count": 0,
            "implementation_path_count": {"r4": 44, "r5": 45},
            "generator_derived_added_path": (
                "tests/conformance/checker-predicates/chunks/"
                "part-0029.json"
            ),
        }
        and r9_test_verification.get("verified_semantic_contract")
        == {
            "closed_input_union_variant_count": 3,
            "rcts_fallback_count": 0,
            "predicate_count": 3,
            "ordered_reason_key_count": 12,
            "base_fixture_count": 18,
            "adversarial_fixture_count": 13,
            "mutation_count": 12,
            "static_reference_checks": {
                "passed": 9,
                "total": 9,
                "result": "PASS",
            },
            "registry_postimage": {
                "predicates": 277,
                "diagnostics": 1436,
                "relations": 559,
                "dispatch_rows": 226,
                "undefined_or_unlisted_dispatch": 0,
            },
            "grammar_reference_generator": {
                "result": "PASS",
                "cases": 33,
                "mutations": 32,
                "deterministic_output_count": 8,
                "deterministic_roots": 2,
                "repository_write": False,
            },
            "tutorial_generator": {
                "result": "TUTORIAL_MUTATION_TEST_PASS",
                "baseline_check_count": 1,
                "deterministic_write_count": 2,
                "rejection_mutation_count": 12,
            },
        }
        and r9_test_verification.get("semantic_pr_github_ci")
        == r9_semantic_ci
        and r9_test_verification.get("verified_ledger")
        == {
            "gap_transition_candidate_count": 1,
            "gap_state_at_semantic_merge": "INTEGRATED_UNVERIFIED",
            "closed_before_closure_readback": 0,
            "eligible_after_closure_readback": 1,
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN",
            "separate_m13_actions": "4_OPEN",
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
        }
        and r9_test_verification.get("product_lanes")
        == "15_OF_15_NOT_RUN"
        and r9_test_verification.get("product_support") == "NOT_RUN"
        and r9_test_verification.get(
            "canonical_source_mutation_during_closure_verification"
        ) == 0
        and r9_test_verification.get(
            "github_mutation_during_closure_verification"
        ) == 0
        and r9_test_verification.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK"
        and r9_test_verification.get("future_closure_commit")
        == "NOT_RECORDED_BEFORE_MERGE",
        "R9_INDEPENDENT_TEST_VERIFICATION",
        repr(r9_test_verification),
    )
    r10_test_path = root / R10_INDEPENDENT_TEST_VERIFICATION_RECEIPT
    r10_test_verification = parsed.get(r10_test_path, {})
    check(
        r10_test_path.is_file()
        and r10_test_path.stat().st_size
        == R10_INDEPENDENT_TEST_VERIFICATION_BYTES
        and file_sha(r10_test_path)
        == R10_INDEPENDENT_TEST_VERIFICATION_SHA256
        and r10_test_path.stat().st_size == r10_independent_test.get("bytes")
        and file_sha(r10_test_path) == r10_independent_test.get("sha256")
        and r10_test_verification.get("schema")
        == "deeplus.r10-hir-mir-machine-contract-independent-verification/v1"
        and r10_test_verification.get("recorded_at")
        == "2026-07-31T18:49:43+09:00"
        and r10_test_verification.get("role") == "Test_"
        and r10_test_verification.get("reviewer_identity")
        == "Codex Test_ independent R10 publication-closure audit"
        and r10_test_verification.get("repository")
        == "https://github.com/howork/Deeplus.git"
        and r10_test_verification.get("repository_write") is False
        and r10_test_verification.get("verdict")
        == r10_independent_test.get("required_verdict")
        and r10_test_verification.get("static_gate")
        == "PASS_INDEPENDENT_PRE_MERGE_CLOSURE_GATE"
        and r10_test_verification.get("merge_readiness")
        == "HOLD_PENDING_PUBLICATION_CLOSURE_MERGE_AND_READBACK"
        and r10_test_verification.get("semantic_pull_request") == 52
        and r10_test_verification.get("semantic_source_commit")
        == R10_SEMANTIC_SOURCE_COMMIT
        and r10_test_verification.get("semantic_source_tree")
        == R10_SEMANTIC_PUBLICATION_TREE
        and r10_test_verification.get("semantic_merge_commit")
        == R10_SEMANTIC_PUBLICATION_COMMIT
        and r10_test_verification.get("semantic_merge_tree")
        == R10_SEMANTIC_PUBLICATION_TREE
        and r10_test_verification.get("semantic_merge_parents")
        == [
            "7632a2943e3e70dd4c6adffd53977671aec0f6c5",
            R10_SEMANTIC_SOURCE_COMMIT,
        ]
        and r10_test_verification.get("post_semantic_merge_readback") == "PASS"
        and r10_test_verification.get("reviewed_gap_ids")
        == R10_PUBLICATION_CLOSURE_GAP_IDS
        and r10_test_verification.get("verified_change_scope")
        == {
            "changed_file_count": 50,
            "source_and_merge_tree_equal": True,
            "production_crate_change_count": 0,
            "grammar_change_count": 0,
            "source_syntax_activation_count": 0,
        }
        and r10_test_verification.get("verified_semantic_contract")
        == {
            "hir_identity_count": 128,
            "structural_plan_contract_count": 12,
            "lowering_rows_current": 102,
            "lowering_rows_explicit_preview_maximum": 111,
            "mir_operation_count": 29,
            "mir_terminator_count": 17,
            "mir_linear_token_kind_count": 12,
            "mir_capability_count": 26,
            "capability_graph": "ACYCLIC",
            "responsibility_axis_count": 11,
            "call_mode_target_pair_count": 10,
            "argument_kind_count": 7,
            "fixture_binding_count": 43,
            "new_release_verifier_diagnostic_count": 5,
            "new_source_diagnostic_count": 0,
        }
        and r10_test_verification.get("executed_static_validation")
        == {
            "focused": {
                "command": (
                    "py -3 tools/validators/"
                    "validate_hir_mir_machine_contract.py --root ."
                ),
                "result": "PASS",
            },
            "workspace": {
                "command": "py -3 tools/validators/validate_workspace.py --root .",
                "result": "PASS",
                "passed": 5729,
                "total": 5729,
                "failed": 0,
                "json_files_parsed": 354,
                "catalogs_reassembled": 14,
                "rust_scaffold_crates": 15,
            },
            "evidence_level": "E2_DESIGN_STATIC",
        }
        and r10_test_verification.get("semantic_pr_github_ci")
        == r10_semantic_ci
        and r10_test_verification.get("verified_ledger")
        == {
            "persistent_pre_state": "DECISION_PENDING",
            "candidate_freeze_state": "APPROVED_NOT_INTEGRATED",
            "gap_state_at_semantic_merge": "INTEGRATED_UNVERIFIED",
            "closed_before_closure_readback": 0,
            "eligible_after_closure_readback": 1,
            "semantic_p0": 0,
            "canonical_feature_p1": "22_OPEN",
            "separate_m13_actions": "4_OPEN",
            "closed_feature_p1": 0,
            "new_feature_p1": 0,
        }
        and r10_test_verification.get("product_lanes")
        == "15_OF_15_NOT_RUN"
        and r10_test_verification.get("product_support") == "NOT_RUN"
        and r10_test_verification.get("current_binding") is False
        and r10_test_verification.get(
            "canonical_source_mutation_during_closure_verification"
        ) == 0
        and r10_test_verification.get(
            "github_mutation_during_closure_verification"
        ) == 0
        and r10_test_verification.get("closure_effect")
        == "CONDITIONAL_ON_CLOSURE_MERGE_AND_LIVE_MAIN_READBACK"
        and r10_test_verification.get("future_closure_commit")
        == "NOT_RECORDED_BEFORE_MERGE",
        "R10_INDEPENDENT_TEST_VERIFICATION",
        repr(r10_test_verification),
    )
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
        r77_publication_closure = revision == R77_PUBLICATION_POLICY_CLOSURE_REVISION
        check(
            publication_source == ({
                "kind": "git-commit",
                "commit": "da734c608c0d583a671c0da9e14da00bff42affd",
                "role": "r77_semantic_publication_target",
                "repository": "https://github.com/howork/Deeplus.git",
            } if r77_publication_closure else {
                "kind": "git-commit",
                "commit": CURRENT_PUBLICATION_TARGET_COMMIT,
                "role": "publication_authority_source",
                "repository": "https://github.com/howork/Deeplus.git",
            }),
            "POINTER_PUBLICATION_SOURCE",
            str(publication_source),
        )
        check(
            audited_baseline == ({
                "kind": "git-commit",
                "commit": "10e64f492f0529610673846139afcf0d95175663",
                "repository": "https://github.com/howork/Deeplus.git",
                "branch": "main",
                "role": "r77_publication_closure_readback_base",
            } if r77_publication_closure else {
                "kind": "git-commit",
                "commit": HISTORICAL_DOCUMENT_CONSISTENCY_BASE_COMMIT,
                "repository": "https://github.com/howork/Deeplus.git",
                "branch": "main",
                "role": "document_consistency_repair_base",
            }),
            "POINTER_AUDITED_BASELINE",
            str(audited_baseline),
        )
        check(
            candidate_binding == ({
                "mode": "semantic_publication_target_bound_by_external_post_merge_receipt",
                "receipt_location": "release/evidence/r77-integrated-surface-publication-closure-readback.json",
                "current_binding": False,
                "self_binding_forbidden": True,
            } if r77_publication_closure else {
                "mode": "external_post_commit_receipt_required",
                "receipt_location": "external_result_pack",
                "current_binding": False,
                "self_binding_forbidden": True,
            }),
            "POINTER_EXTERNAL_BINDING",
            str(candidate_binding),
        )
        snapshot = pointer.get("source_snapshot")
        check(snapshot is None, "POINTER_SOURCE_SNAPSHOT", str(snapshot))
        git_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-git-binding-receipt.json", {})
        check(
            file_sha(
                root
                / "release/evidence/current-publication-m1.3-git-binding-receipt.json"
            )
            == HISTORICAL_RECEIPT_SHA256[
                "release/evidence/current-publication-m1.3-git-binding-receipt.json"
            ]
            and git_receipt.get("result") == "PASS_REVIEWED_HEAD"
            and git_receipt.get("scope") == "historical_reviewed_head"
            and git_receipt.get("current_binding") is False
            and git_receipt.get("reviewed_head") == "989bef9da472348971e56fafb2c9abc550100226"
            and git_receipt.get("pull_request") == 7
            and publication_source.get("repository") == git_receipt.get("repository")
            and git_receipt.get("source_authority_commit")
            == HISTORICAL_PUBLICATION_SOURCE_COMMIT
            and git_receipt.get("repository")
            == "https://github.com/howork/Deeplus.git",
            "HISTORICAL_PUBLICATION_RECEIPT",
            str(git_receipt),
        )
        if (root / ".git").exists():
            git_base = [
                "git",
                "-c",
                f"safe.directory={root.as_posix()}",
                "-C",
                str(root),
            ]
            publication_object_check = subprocess.run(
                [
                    *git_base, "cat-file", "-e",
                    f"{CURRENT_PUBLICATION_TARGET_COMMIT}^{{commit}}",
                ],
                capture_output=True,
                check=False,
            )
            publication_ancestor_check = subprocess.run(
                [
                    *git_base, "merge-base", "--is-ancestor",
                    CURRENT_PUBLICATION_TARGET_COMMIT, "HEAD",
                ],
                capture_output=True,
                check=False,
            )
            authority_transition_object_check = subprocess.run(
                [
                    *git_base, "cat-file", "-e",
                    f"{AUTHORITY_TRANSITION_BASE_COMMIT}^{{commit}}",
                ],
                capture_output=True,
                check=False,
            )
            r4_semantic_object_check = subprocess.run(
                [
                    *git_base, "cat-file", "-e",
                    f"{R4_SEMANTIC_PUBLICATION_COMMIT}^{{commit}}",
                ],
                capture_output=True,
                check=False,
            )
            audited_object_check = subprocess.run(
                [
                    *git_base, "cat-file", "-e",
                    f"{HISTORICAL_DOCUMENT_CONSISTENCY_BASE_COMMIT}^{{commit}}",
                ],
                capture_output=True,
                check=False,
            )
            audited_to_authority_transition_check = subprocess.run(
                [
                    *git_base, "merge-base", "--is-ancestor",
                    HISTORICAL_DOCUMENT_CONSISTENCY_BASE_COMMIT,
                    AUTHORITY_TRANSITION_BASE_COMMIT,
                ],
                capture_output=True,
                check=False,
            )
            authority_transition_to_publication_check = subprocess.run(
                [
                    *git_base, "merge-base", "--is-ancestor",
                    AUTHORITY_TRANSITION_BASE_COMMIT,
                    CURRENT_PUBLICATION_TARGET_COMMIT,
                ],
                capture_output=True,
                check=False,
            )
            r4_semantic_to_publication_check = subprocess.run(
                [
                    *git_base, "merge-base", "--is-ancestor",
                    R4_SEMANTIC_PUBLICATION_COMMIT,
                    CURRENT_PUBLICATION_TARGET_COMMIT,
                ],
                capture_output=True,
                check=False,
            )
            check(
                publication_object_check.returncode == 0
                and publication_ancestor_check.returncode == 0
                and authority_transition_object_check.returncode == 0
                and r4_semantic_object_check.returncode == 0
                and audited_object_check.returncode == 0
                and audited_to_authority_transition_check.returncode == 0
                and authority_transition_to_publication_check.returncode == 0
                and r4_semantic_to_publication_check.returncode == 0,
                "POINTER_PUBLICATION_COMMIT_AVAILABLE",
                (
                    f"audited={HISTORICAL_DOCUMENT_CONSISTENCY_BASE_COMMIT} "
                    f"authority_transition={AUTHORITY_TRANSITION_BASE_COMMIT} "
                    f"r4_semantic={R4_SEMANTIC_PUBLICATION_COMMIT} "
                    f"publication={CURRENT_PUBLICATION_TARGET_COMMIT}"
                ),
            )
        snapshot_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-source-snapshot-receipt.json", {})
        snapshot_object = snapshot_receipt.get("object", {})
        check(
            file_sha(
                root
                / "release/evidence/current-publication-m1.3-source-snapshot-receipt.json"
            )
            == HISTORICAL_RECEIPT_SHA256[
                "release/evidence/current-publication-m1.3-source-snapshot-receipt.json"
            ]
            and snapshot_receipt.get("result") == "PASS_DIRECT_BYTES"
            and bool(snapshot_object.get("library_file_id"))
            and bool(
                re.fullmatch(
                    r"[0-9a-f]{64}",
                    snapshot_object.get("sha256", ""),
                )
            ),
            "HISTORICAL_SOURCE_SNAPSHOT_RECEIPT",
            str(snapshot_object),
        )
        predecessor_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-predecessor-receipt.json", {})
        check(
            file_sha(
                root
                / "release/evidence/current-publication-m1.3-predecessor-receipt.json"
            )
            == HISTORICAL_RECEIPT_SHA256[
                "release/evidence/current-publication-m1.3-predecessor-receipt.json"
            ],
            "HISTORICAL_PREDECESSOR_RECEIPT",
            str(predecessor_receipt.get("pointer_object", {})),
        )
        if revision == R77_PUBLICATION_POLICY_CLOSURE_REVISION:
            expected_predecessor = G4_INDEPENDENT_READINESS_REVISION
        elif revision == G4_INDEPENDENT_READINESS_REVISION:
            expected_predecessor = R76_GLOBAL_TRACE_CLOSURE_REVISION
        elif revision == R76_GLOBAL_TRACE_CLOSURE_REVISION:
            expected_predecessor = R75_ACTOR_CRANELIFT_PROJECTION_REVISION
        elif revision == R75_ACTOR_CRANELIFT_PROJECTION_REVISION:
            expected_predecessor = R74_IMPLEMENTATION_READINESS_REVISION
        elif revision == R74_IMPLEMENTATION_READINESS_REVISION:
            expected_predecessor = R47_OWNERSHIP_CONTRACT_FUSION_REVISION
        elif revision == R47_OWNERSHIP_CONTRACT_FUSION_REVISION:
            expected_predecessor = R46_MANAGED_ROOT_RUNTIME_REVISION
        elif revision == R46_MANAGED_ROOT_RUNTIME_REVISION:
            expected_predecessor = R23_ACTOR_PROTOCOL_BINDING_REVISION
        elif revision == R23_ACTOR_PROTOCOL_BINDING_REVISION:
            expected_predecessor = R41_ACTOR_PROTOCOL_REVISION
        elif revision == R41_ACTOR_PROTOCOL_REVISION:
            expected_predecessor = R11_R19_FRONTEND_REVISION
        elif revision == R11_R19_FRONTEND_REVISION:
            expected_predecessor = R10_HIR_MIR_REVISION
        elif revision == R10_HIR_MIR_REVISION:
            expected_predecessor = LANGUAGE_COHERENCE_REVISION
        elif revision == LANGUAGE_COHERENCE_REVISION:
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
            R77_ACTION_IDS
            if revision == R77_PUBLICATION_POLICY_CLOSURE_REVISION
            else SUCCESSOR_ACTION_IDS
            if revision
            in {
                POST_PR16_REVISION,
                LANGUAGE_COHERENCE_REVISION,
                *CURRENT_MACHINE_REVISIONS,
            }
            else EXPECTED_ACTION_IDS
        )
        check(
            action_ids == expected_action_ids
            and (
                next_review_ids == action_ids
                if revision == LEGACY_REVISION
                else pointer.get("required_next_reviews")
                == (R77_EXPECTED_NEXT_REVIEWS if r77_publication_closure else EXPECTED_NEXT_REVIEWS)
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
        sfd_action = next(
            (row for row in actions if row.get("id") == "SFD-P1-009"),
            {},
        )
        check(
            sfd_action.get("priority") == "P1"
            and sfd_action.get("owner") == "Impl_ + Test_"
            and "closure authority: Codex Design_ after target-bound receipts"
            in sfd_action.get("target", "")
            and "ChatGPT Design_" not in sfd_action.get("target", "")
            and all(status == "NOT_RUN" for status in pointer.get("product_lanes", {}).values()),
            "SFD_P1_009_AUTHORITY_TRANSITION",
            str(sfd_action),
        )
        check(
            pointer.get("required_next_reviews")
            == (R77_EXPECTED_NEXT_REVIEWS if r77_publication_closure else EXPECTED_NEXT_REVIEWS),
            "POINTER_NEXT_REVIEW_BINDING",
            str(pointer.get("required_next_reviews")),
        )
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
        frontend.get("revision")
        == (
            G4_INDEPENDENT_READINESS_REVISION
            if revision == R77_PUBLICATION_POLICY_CLOSURE_REVISION
            else revision
        )
        and trait_surface.get("revision") == R77_INTEGRATED_SURFACE_REVISION
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
    positional_collect_token = next(
        (
            row
            for row in frontend.get("boundary_policies", [])
            if row.get("id") == "POSITIONAL_COLLECT_SUFFIX"
        ),
        {},
    )
    literal_rule = re.search(r"^Literal ::= (.+)$", grammar, re.MULTILINE)
    vocabulary = parsed.get(root / "spec/grammar/keyword-vocabulary.json", {})
    check(
        literal_rule is not None
        and "NullLiteral" not in literal_rule.group(1)
        and "RecoveryNullLiteral" not in grammar
        and 'UnfoldClause ::= "for" Pattern "in" "*" Expr ;' in grammar
        and 'IndexSuffix ::= "[" SliceAxisList "]" ;' in grammar
        and 'BoundedListLiteral ::= "[" StaticIntLiteral ".." StaticIntLiteral'
        in grammar
        and range_operator.get("tokens") == [[".."], ["..<"], ["..."]]
        and "rejected_reserved_spellings" not in range_operator
        and assignment_operator.get("tokens")
        == [["="], ["+="], ["-="], ["*="], ["/="], ["%="]]
        and slice_index_owner.get("entry") == "SLICE_INDEX_PRATT_ENTRY"
        and slice_index_owner.get("bounds_required") is False
        and slice_index_owner.get("axis_separator") == ","
        and slice_index_owner.get("full_axis")
        == "[..] generally; [*] is a NumericArray-only equivalent full axis"
        and slice_index_owner.get("empty_axis") == "INDEX_SUFFIX_REQUIRES_AXIS"
        and slice_index_owner.get("anchor_outside_slice_bound_diagnostic")
        == {
            "diagnostic": "SLICE_ANCHOR_OUTSIDE_SLICE",
            "stage": "parser",
            "semantic_anchor_node_count": 0,
        }
        and ellipsis_stage.get("cst_roles") == ["OneSidedRangeMarker"]
        and ellipsis_stage.get("ast_roles") == ["OneSidedRange"]
        and positional_collect_token.get("surface") == ".."
        and positional_collect_token.get("contexts")
        == ["parameter", "function_type", "list_pattern"]
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
        if revision in {LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS}
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
        == ["public trait#interpolation Display { +def display.() -> String throws Never effects {}; }"]
        and eq_entry.get("signatures")
        == ["public trait#operator Eq<Rhs> { +def equals.(borrow rhs: Rhs) -> Bool throws Never effects {}; }"]
        and ord_entry.get("signatures")
        == ["public trait#operator Ord<Rhs>\nderives Eq<Rhs> {\n    +def compare.(borrow rhs: Rhs) -> Int throws Never effects {}\n}"]
        and unary_plus_entry.get("signatures")
        == ["public trait#operator UnaryPlus { type Output; +def positive.() -> <Self as UnaryPlus>::Output throws Never effects {}; }"]
        and unary_minus_entry.get("signatures")
        == ["public trait#operator UnaryMinus { type Output; +def negate.() -> <Self as UnaryMinus>::Output throws Never effects {}; }"]
        and add_entry.get("signatures")
        == ["public trait#operator Add<Rhs> { type Output; +def add.(borrow rhs: Rhs) -> <Self as Add<Rhs>>::Output throws Never effects {}; }"]
        and subtract_entry.get("signatures")
        == ["public trait#operator Subtract<Rhs> { type Output; +def subtract.(borrow rhs: Rhs) -> <Self as Subtract<Rhs>>::Output throws Never effects {}; }"]
        and multiply_entry.get("signatures")
        == ["public trait#operator Multiply<Rhs> { type Output; +def multiply.(borrow rhs: Rhs) -> <Self as Multiply<Rhs>>::Output throws Never effects {}; }"]
        and divide_entry.get("signatures")
        == ["public trait#operator Divide<Rhs> { type Output; +def divide.(borrow rhs: Rhs) -> <Self as Divide<Rhs>>::Output throws Never effects {}; }"]
        and remainder_entry.get("signatures")
        == ["public trait#operator Remainder<Rhs> { type Output; +def remainder.(borrow rhs: Rhs) -> <Self as Remainder<Rhs>>::Output throws Never effects {}; }"]
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
    check(
        "| `*` | owner-bounded structural unfold" in language
        and 'PositionalUnfoldArgument ::= "*" Expr ;' in grammar
        and 'NamedUnfoldArgument ::= "**" Expr ;' in grammar,
        "STRUCTURAL_UNFOLD_OWNER",
        "owner-bounded positional and static-named unfold in spec and grammar",
    )
    check("repeated positional parameter/type residue and positional unfold" not in language, "POSITIONAL_UNFOLD_NO_ELLIPSIS", "... is not call-side unfold")
    probes = ["options** requires {", "NamedPack**", "**value", "let#lazy", "sealed class"]
    for probe in probes:
        check(probe in language, "CURRENT_SURFACE_PROBE", probe)
    check('Identifier "**" NamedRestRequirementClause?' in grammar, "NAMED_REST_GRAMMAR", "**")
    check('Identifier ".." TypeAnnotation' in grammar, "POSITIONAL_REST_GRAMMAR", "..")

    instruction_chars = len((root / "governance/project-instructions.txt").read_text(encoding="utf-8"))
    check(instruction_chars <= 8000, "PROJECT_INSTRUCTION_LIMIT", str(instruction_chars))
    memories = sorted((root / "roles/current-memory").glob("*.json"))
    check(len(memories) == 5, "ROLE_MEMORY_COUNT", str(len(memories)))
    for path in memories:
        capsule = parsed.get(path, {})
        check(len(capsule.get("current_facts", [])) <= 50 and len(capsule.get("open_actions", [])) <= 30 and len(capsule.get("watch_items", [])) <= 20 and path.stat().st_size <= 102400, "ROLE_MEMORY_CAP", path.name)
        check(capsule.get("source_revision") == inherited_component_revision and all(not row.get("id", "").startswith("MIG-M1-") for row in capsule.get("open_actions", [])), "ROLE_MEMORY_CURRENT", path.name)
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
            set(facts_by_id)
            == (
                {
                    "ARCH-001", "EVID-001", "PUB-001", "PUB-002", "P1-001",
                    "CMA-001", "MIRX1-001", "EXPR-001", "AUTH-001",
                }
                | ({"PUB-003"} if revision in CURRENT_MACHINE_REVISIONS else set())
                if path.name == "Design_Deeplus_Current_Memory.json"
                else {
                    "ARCH-001", "EVID-001", "PUB-001", "P1-001",
                    "CMA-001", "MIRX1-001", "EXPR-001",
                }
            )
            and "22 total" in facts_by_id.get("P1-001", {}).get("statement", "")
            and "15 product lanes remain NOT_RUN" in facts_by_id.get("EVID-001", {}).get("statement", "")
            and facts_by_id.get("CMA-001", {}).get("introduced")
            == (
                POST_PR16_REVISION
                if revision
                in {LANGUAGE_COHERENCE_REVISION, *CURRENT_MACHINE_REVISIONS}
                else revision
            )
            and "Issue #24 remains open" in facts_by_id.get("MIRX1-001", {}).get("statement", "")
            and "current backend authority is xVM with Cranelift ObjectModule AOT and later Cranelift JITModule"
            in facts_by_id.get("MIRX1-001", {}).get("statement", "")
            and (
                (
                    facts_by_id.get("AUTH-001", {}).get("authority")
                    == "explicit user delegation for the active implementation-readiness Goal"
                    and facts_by_id.get("AUTH-001", {}).get("source")
                    == "governance/reports/Design_Deeplus_Codex_Design_Authority_Transition_R1.md"
                    and "does not rewrite historical evidence"
                    in facts_by_id.get("AUTH-001", {}).get("statement", "")
                    and "NOT_RUN product lane"
                    in facts_by_id.get("AUTH-001", {}).get("statement", "")
                )
                if path.name == "Design_Deeplus_Current_Memory.json"
                else "AUTH-001" not in facts_by_id
            )
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
    design_facts = {
        row.get("id"): row
        for row in design_memory.get("current_facts", [])
        if isinstance(row, dict)
    }
    r4_release_rows = [
        row
        for row in design_history
        if row.get("release")
        == "github-pr-46-r4-name-resolution-modules-semantic-publication"
    ]
    check(
        len(r4_release_rows) == 1
        and r4_release_rows[0].get("report")
        == R4_PUBLICATION_CLOSURE_REPORT
        and all(
            term in r4_release_rows[0].get("verdict", "")
            for term in (
                R4_SEMANTIC_PUBLICATION_COMMIT,
                "INTEGRATED_UNVERIFIED",
                "independent Test_ verification",
                "22 OPEN",
                "15/15 NOT_RUN",
            )
        ),
        "R4_PUBLICATION_CLOSURE_MEMORY",
        repr(
            {
                "recent_release": r4_release_rows,
            }
        ),
    )
    r8_release_rows = [
        row
        for row in design_history
        if row.get("release")
        == "github-pr-48-r8-ownership-canonical-semantic-publication"
    ]
    r8_pub_statement = design_facts.get("PUB-001", {}).get(
        "statement", ""
    )
    check(
        design_facts.get("PUB-001", {}).get("source")
        == R8_PUBLICATION_CLOSURE_REPORT
        and design_facts.get("PUB-001", {}).get("introduced")
        == LANGUAGE_COHERENCE_REVISION
        and all(
            term in r8_pub_statement
            for term in (
                "PR #48",
                R8_SEMANTIC_PUBLICATION_COMMIT,
                "exact three audit P0 gaps are INTEGRATED_UNVERIFIED",
                "independent verification passes",
                "22 OPEN",
                "four M13 actions remain separate and OPEN",
                "15 product lanes remain NOT_RUN",
            )
        )
        and len(r8_release_rows) == 1
        and r8_release_rows[0].get("report")
        == R8_PUBLICATION_CLOSURE_REPORT
        and all(
            term in r8_release_rows[0].get("verdict", "")
            for term in (
                R8_SEMANTIC_PUBLICATION_COMMIT,
                "INTEGRATED_UNVERIFIED",
                "independent verification passed",
                "22 OPEN",
                "four M13 actions separate and OPEN",
                "15/15 NOT_RUN",
            )
        ),
        "R8_PUBLICATION_CLOSURE_MEMORY",
        repr(
            {
                "PUB-001": design_facts.get("PUB-001"),
                "recent_release": r8_release_rows,
            }
        ),
    )
    r9_release_rows = [
        row
        for row in design_history
        if row.get("release")
        == "github-pr-50-r9-diagnostic-dispatch-semantic-publication"
    ]
    r9_pub_statement = design_facts.get("PUB-002", {}).get(
        "statement", ""
    )
    check(
        design_memory.get("updated_at")
        == (
            "2026-07-31T18:49:43+09:00"
            if revision in CURRENT_MACHINE_REVISIONS
            else "2026-07-31T06:51:51+09:00"
        )
        and design_facts.get("PUB-002", {}).get("source")
        == R9_PUBLICATION_CLOSURE_REPORT
        and design_facts.get("PUB-002", {}).get("introduced")
        == LANGUAGE_COHERENCE_REVISION
        and design_facts.get("PUB-002", {}).get("review_after")
        == "publication-closure merge and external post-merge readback receipt"
        and all(
            term in r9_pub_statement
            for term in (
                "PR #50",
                R9_SEMANTIC_SOURCE_COMMIT,
                R9_SEMANTIC_PUBLICATION_COMMIT,
                R9_SEMANTIC_PUBLICATION_TREE,
                "IR-DIAG-P0-052",
                "INTEGRATED_UNVERIFIED",
                "No future closure SHA is asserted",
                "22 OPEN",
                "four M13 actions remain separate and OPEN",
                "15 product lanes remain NOT_RUN",
            )
        )
        and len(r9_release_rows) == 1
        and r9_release_rows[0].get("report")
        == R9_PUBLICATION_CLOSURE_REPORT
        and all(
            term in r9_release_rows[0].get("verdict", "")
            for term in (
                R9_SEMANTIC_SOURCE_COMMIT,
                R9_SEMANTIC_PUBLICATION_COMMIT,
                R9_SEMANTIC_PUBLICATION_TREE,
                "IR-DIAG-P0-052",
                "INTEGRATED_UNVERIFIED",
                "design/static E2",
                "22 OPEN",
                "four M13 actions separate and OPEN",
                "15/15 NOT_RUN",
            )
        ),
        "R9_PUBLICATION_CLOSURE_MEMORY",
        repr(
            {
                "PUB-002": design_facts.get("PUB-002"),
                "recent_release": r9_release_rows,
            }
        ),
    )
    r10_release_rows = [
        row
        for row in design_history
        if row.get("release")
        == "github-pr-52-r10-hir-mir-machine-contract-semantic-publication"
    ]
    r10_pub_statement = design_facts.get("PUB-003", {}).get(
        "statement", ""
    )
    check(
        design_facts.get("PUB-003", {}).get("source")
        == R10_PUBLICATION_CLOSURE_REPORT
        and design_facts.get("PUB-003", {}).get("introduced")
        == R10_HIR_MIR_REVISION
        and design_facts.get("PUB-003", {}).get("review_after")
        == "publication-closure merge and external post-merge readback receipt"
        and all(
            term in r10_pub_statement
            for term in (
                "PR #52",
                R10_SEMANTIC_SOURCE_COMMIT,
                R10_SEMANTIC_PUBLICATION_COMMIT,
                R10_SEMANTIC_PUBLICATION_TREE,
                "IR-OWN-P0-015",
                "INTEGRATED_UNVERIFIED",
                "No future closure SHA is asserted",
                "22 OPEN",
                "four M13 actions remain separate and OPEN",
                "15 product lanes remain NOT_RUN",
            )
        )
        and len(r10_release_rows) == 1
        and r10_release_rows[0].get("report")
        == R10_PUBLICATION_CLOSURE_REPORT
        and all(
            term in r10_release_rows[0].get("verdict", "")
            for term in (
                R10_SEMANTIC_SOURCE_COMMIT,
                R10_SEMANTIC_PUBLICATION_COMMIT,
                R10_SEMANTIC_PUBLICATION_TREE,
                "IR-OWN-P0-015",
                "INTEGRATED_UNVERIFIED",
                "design/static E2",
                "22 OPEN",
                "four M13 actions separate and OPEN",
                "15/15 NOT_RUN",
            )
        ),
        "R10_PUBLICATION_CLOSURE_MEMORY",
        repr(
            {
                "PUB-003": design_facts.get("PUB-003"),
                "recent_release": r10_release_rows,
            }
        ),
    )

    crates = sorted(path for path in (root / "crates").iterdir() if path.is_dir())
    check(len(crates) == 15, "CRATE_BOUNDARY_COUNT", str(len(crates)))
    for crate in crates:
        check((crate / "Cargo.toml").is_file() and bool(list((crate / "src").glob("*.rs"))), "CRATE_SCAFFOLD", crate.name)
    manifest = parsed.get(root / "release/source-tree-manifest.json", {})
    listed = manifest.get("files", [])
    source_manifest_process = subprocess.run(
        [
            sys.executable,
            str(root / "tools/generators/refresh_source_tree_manifest.py"),
            "--root",
            str(root),
            "--check",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    source_manifest_detail = (
        source_manifest_process.stdout.strip()
        if source_manifest_process.returncode == 0
        else source_manifest_process.stderr.strip()
        or source_manifest_process.stdout.strip()
    )
    check(
        source_manifest_process.returncode == 0,
        "SOURCE_TREE_INDEX_PROJECTION",
        source_manifest_detail[-4000:],
    )
    worktree_index_process = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            "diff",
            "--quiet",
            "--",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    check(
        worktree_index_process.returncode == 0,
        "SOURCE_TREE_WORKTREE_INDEX_PARITY",
        worktree_index_process.stderr.strip()
        or "Git clean-filter parity between worktree and index",
    )
    actual_files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and not any(part in EXCLUDED_TREE_PARTS for part in p.relative_to(root).parts)
        and p.relative_to(root).as_posix() != "release/source-tree-manifest.json"
    )
    listed_map = {row["path"]: row for row in listed}
    check(set(listed_map) == {p.relative_to(root).as_posix() for p in actual_files}, "SOURCE_TREE_MEMBERSHIP", f"listed={len(listed_map)} actual={len(actual_files)}")
    tree_material = "\n".join(f"{row['path']}\0{row['sha256']}" for row in sorted(listed, key=lambda x: x["path"])).encode()
    check(manifest.get("revision") == revision and manifest.get("tree_sha256") == hashlib.sha256(tree_material).hexdigest(), "SOURCE_TREE_AGGREGATE", str(manifest.get("tree_sha256")))

    result = "PASS" if not errors else "FAIL"
    receipt = {
        "schema": "deeplus.canonical-workspace-validation-receipt/v1.1",
        "revision": revision, "mode": "candidate" if args.candidate else "published-current",
        "result": result, "evidence_level": "E2_STATIC_CLOSURE",
        "checks": len(checks), "passed": sum(row["pass"] for row in checks),
        "failed": sum(not row["pass"] for row in checks), "canonical_counts": actual,
        "passed_check_ids": [
            check_id
            for check_id in R5_OWNERSHIP_CHECK_IDS
            if any(
                row["code"] == check_id and row["pass"]
                for row in checks
            )
        ],
        "r5_ownership_check_count": len(R5_OWNERSHIP_CHECK_IDS),
        "passed_check_id_scope": "R5_OWNERSHIP_EXACT_13",
        "r5_ownership_check_results": r5_ownership_check_results,
        "r9_diagnostic_dispatch_check_scope":
            "R9_DIAGNOSTIC_DISPATCH_CLOSURE_EXACT",
        "r9_diagnostic_dispatch_check_count":
            len(R9_DIAGNOSTIC_DISPATCH_CHECK_IDS),
        "r9_diagnostic_dispatch_passed_check_ids": [
            row["check_id"]
            for row in r9_diagnostic_dispatch_check_results
            if row["pass"]
        ],
        "r9_diagnostic_dispatch_check_results":
            r9_diagnostic_dispatch_check_results,
        "frontend_readiness_check_scope": "R12_R19_EXACT_DESIGN_STATIC",
        "frontend_readiness_check_count":
            len(frontend_readiness_check_results),
        "frontend_readiness_passed_check_ids": [
            row["check_id"]
            for row in frontend_readiness_check_results
            if row["pass"]
        ],
        "frontend_readiness_check_results":
            frontend_readiness_check_results,
        "r26_primary_diagnostic_check_scope":
            "R26_PRIMARY_DIAGNOSTIC_IDENTITY_EXACT",
        "r26_primary_diagnostic_check_count":
            len(R26_PRIMARY_DIAGNOSTIC_CHECK_IDS),
        "r26_primary_diagnostic_passed_check_ids": [
            row["check_id"]
            for row in r26_primary_diagnostic_check_results
            if row["pass"]
        ],
        "r26_primary_diagnostic_check_results":
            r26_primary_diagnostic_check_results,
        "r27_grammar_topology_check_scope":
            "R27_GRAMMAR_TOPOLOGY_CLOSURE_EXACT",
        "r27_grammar_topology_check_count":
            len(R27_GRAMMAR_TOPOLOGY_CHECK_IDS),
        "r27_grammar_topology_passed_check_ids": [
            row["check_id"]
            for row in r27_grammar_topology_check_results
            if row["pass"]
        ],
        "r27_grammar_topology_check_results":
            r27_grammar_topology_check_results,
        "r28_formatter_lsp_incremental_check_scope":
            "R28_FORMATTER_LSP_INCREMENTAL_EXACT",
        "r28_formatter_lsp_incremental_check_count":
            len(R28_FORMATTER_LSP_INCREMENTAL_CHECK_IDS),
        "r28_formatter_lsp_incremental_passed_check_ids": [
            row["check_id"]
            for row in r28_formatter_lsp_incremental_check_results
            if row["pass"]
        ],
        "r28_formatter_lsp_incremental_check_results":
            r28_formatter_lsp_incremental_check_results,
        "r40_manual_grammar_count_check_scope":
            "R40_MANUAL_GRAMMAR_COUNT_AUTHORITY_EXACT",
        "r40_manual_grammar_count_check_count":
            len(R40_MANUAL_GRAMMAR_COUNT_CHECK_IDS),
        "r40_manual_grammar_count_passed_check_ids": [
            row["check_id"]
            for row in r40_manual_grammar_count_check_results
            if row["pass"]
        ],
        "r40_manual_grammar_count_check_results":
            r40_manual_grammar_count_check_results,
        "r41_actor_protocol_check_scope":
            "R41_ACTOR_PROTOCOL_DIRECT_CONFORMANCE_EXACT",
        "r41_actor_protocol_check_result":
            r41_actor_protocol_check_result,
        "r23_actor_protocol_binding_check_scope":
            "R23_REBASED_CLOSED_STATIC_BINDING_TABLE",
        "r23_actor_protocol_binding_check_result":
            r23_actor_protocol_binding_check_result,
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
