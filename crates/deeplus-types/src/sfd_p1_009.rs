//! Bounded outcome classification for the frozen SFD-P1-009 mode vocabulary.

use deeplus_ast::sfd_p1_009::AstCase;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Outcome {
    Accept,
    Reject,
    AssertRelation,
    MutantKill,
}

impl Outcome {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Accept => "ACCEPT",
            Self::Reject => "REJECT",
            Self::AssertRelation => "ASSERT_RELATION",
            Self::MutantKill => "MUTANT_KILL",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TypedCase {
    pub ast: AstCase,
    pub outcome: Outcome,
    pub responsibility_visible: bool,
}

pub fn check(ast: AstCase) -> TypedCase {
    let outcome = classify_mode(&ast.selected_mode);
    TypedCase {
        ast,
        outcome,
        responsibility_visible: true,
    }
}

pub fn classify_mode(mode: &str) -> Outcome {
    if ACCEPT_MODES.contains(&mode) {
        Outcome::Accept
    } else if ASSERT_RELATION_MODES.contains(&mode) {
        Outcome::AssertRelation
    } else if MUTANT_KILL_MODES.contains(&mode) {
        Outcome::MutantKill
    } else {
        Outcome::Reject
    }
}

const ACCEPT_MODES: &[&str] = &[
    "admitted_positive_path",
    "alpha_equivalent_bindings_same_key",
    "equal_normalized_requirement_witness_rows",
    "nonescaping_callback_parameter",
    "ordinary_inspection_public_fields_only",
    "owned_share_all_components_and_authorities_proven",
    "owned_transfer_all_components_and_authorities_proven",
    "privileged_inspection_matching_scope_audited",
    "proven_nonescaping_callback_parameter",
    "same_place_shorter_region_nested_reborrow",
];

const ASSERT_RELATION_MODES: &[&str] = &[
    "abi_bridge_not_run_without_target_receipt",
    "absent_target_receipt_is_not_run",
    "adapter_commit_failure",
    "adapter_conformance_owns_witness_count",
    "adapter_prepare_failure",
    "adapter_validate_failure",
    "adapter_validation_failure_zero_commit_balanced_cleanup",
    "alpha_equivalent_bindings_normalize_equal",
    "alpha_rename_associated_binders",
    "body_failure_plus_cleanup",
    "body_failure_plus_view_release",
    "build_order_permutation",
    "commit_cancellation",
    "commit_drop",
    "commit_failure",
    "dyn_inserted_in_branch",
    "dyn_inserted_in_collection_element",
    "dyn_inserted_in_generic_candidate",
    "dyn_to_json_requires_named_adapter",
    "dyn_to_plain_requires_named_adapter",
    "empty_target_receipt_is_not_run",
    "entry_permutation_preserves_digest",
    "equal_raw_bytes_distinct_kind_tags_unequal",
    "equal_shaped_variants_create_zero_local_witnesses",
    "erased_tooling_result_separate",
    "facet_store_absence_blocks_zero_minimum_gates",
    "failed_borrow_projection_preserves_source_identity_and_ownership",
    "finite_static_trait_branch_returns_typed_results",
    "hash_order_permutation",
    "import_order_change",
    "import_order_permutation",
    "json_to_dyn_requires_named_adapter",
    "json_to_plain_requires_named_adapter",
    "matching_scope_privileged_reflection_audited",
    "new_projection_uses_new_snapshot_old_facet_sealed",
    "ordinary_borrow_reflection",
    "ordinary_inout_reflection",
    "ordinary_owned_reflection",
    "origin_does_not_change_compatibility",
    "plain_to_dyn_requires_named_adapter",
    "plain_to_json_requires_named_adapter",
    "precommit_failure_returns_exact_original_owner",
    "prepare_cancellation",
    "prepare_drop",
    "prepare_failure",
    "projection_failure_plus_cleanup",
    "projection_failure_plus_view_release",
    "provider_priority_change",
    "registry_epoch_change",
    "removed_route_future_projection_fails_existing_facet_unchanged",
    "reorder_normalized_binding_syntax",
    "repeat_projection_same_snapshot_payload_profile",
    "route_removed_in_successor_epoch",
    "runtime_payload_changes_result_trait_static",
    "same_facet_type_id_distinct_instances",
    "schema_mapping_independent_of_runtime_layout",
    "source_order_permutation",
    "successor_epoch_update_preserves_old_facet",
    "two_facet_instances_payload_descriptor_unchanged",
    "two_stores_distinct_owners_subject_unchanged",
    "unequal_ground_bindings_remain_distinct",
    "unique_route_import_order",
    "unique_route_package_build_order",
    "unique_route_source_order",
    "validate_cancellation",
    "validate_drop",
    "validate_failure",
    "virtual_slot_override_preserves_witness_identity",
];

const MUTANT_KILL_MODES: &[&str] = &[
    "associated_binding_omitted_from_type_key",
    "baseline_commit_receipt_deleted",
    "borrow_lifetime_erased",
    "borrow_region_extended",
    "borrow_view_marked_send_share",
    "cancellation_cleanup_omitted",
    "case_local_parent_witness_replacement",
    "class_slot_and_witness_ids_compared_equal",
    "class_slot_and_witness_tables_merged",
    "command_receipt_deleted",
    "commit_barrier_removed",
    "common_transfer_predicate_for_borrow",
    "common_transfer_predicate_for_inout",
    "common_transfer_predicate_for_owned",
    "concrete_drop_plan_removed",
    "concurrent_detach_first_wins",
    "dispatch_resolved_on_every_call",
    "duplicate_route_first_wins",
    "dyn_depends_on_facet_store",
    "entry_ownership_moved_into_subject",
    "exclusivity_release_skipped",
    "extension_helper_promoted_to_global_evidence",
    "facet_store_token_copied",
    "facet_type_id_used_as_abi_tag",
    "hidden_global_registry_lookup",
    "identity_kind_tag_erased",
    "implicit_authority_capture",
    "import_order_first_conformance",
    "incidental_layout_frozen",
    "input_digest_receipt_deleted",
    "inspection_authority_bypassed",
    "inspection_authority_removed",
    "live_view_check_skipped",
    "live_view_token_duplicated",
    "mandatory_registry_key_field_deleted",
    "mode_omitted_from_type_key",
    "mutate_lowering_to_write_one_payload_descriptor_field",
    "numeric_identity_payload_reused_cross_kind",
    "output_digest_receipt_deleted",
    "owner_bit_cloned",
    "parent_witness_moved_into_variant",
    "post_construction_binding_override",
    "precommit_resource_cleaned_twice",
    "provider_id_used_as_abi_tag",
    "provider_order_first_conformance",
    "raw_provenance_made_public",
    "registry_projection_depends_on_facet_store",
    "registry_row_promoted_to_global_evidence",
    "registry_snapshot_mutable",
    "required_binding_dropped_from_identity",
    "responsibility_field_omitted",
    "responsibility_subset_direction_reversed",
    "return_an_equal_copy_instead_of_the_original_owner_token",
    "runtime_type_id_used_as_abi_tag",
    "runtime_type_id_used_as_wire_tag",
    "silently_enable_partial_per_method_object_safety",
    "source_order_first_conformance",
    "store_role_exposed_as_subject_conformance",
    "synthesize_value_semantics_from_representation_identity",
    "target_receipt_deleted",
    "toolchain_receipt_deleted",
    "tooling_claims_product_support",
    "tooling_failure_field_deleted",
    "tooling_mode_field_deleted",
    "tooling_owner_field_deleted",
    "trait_witness_id_used_as_wire_tag",
    "treat_an_erased_dynfacet_tooling_handle_as_a_statically_callable_trait_value",
    "turn_an_extension_helper_into_an_automatic_witness_candidate",
    "two_drop_concrete_events",
    "variant_id_used_as_wire_tag",
];
