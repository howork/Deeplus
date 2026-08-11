//! Compile-only integration contract. R4 does not authorize test execution.

use deeplus_source::sfd_p1_009::{EXECUTION_TARGET_BINDING, HISTORICAL_PROVENANCE_BASELINE};
use deeplus_testkit::sfd_p1_009::{Selection, ensure_repo_relative};
use std::path::Path;

#[test]
fn selector_grammar_is_closed() {
    assert_eq!(
        Selection::parse("all-execute").expect("frozen selector"),
        Selection::AllExecute
    );
    assert!(Selection::parse("all").is_err());
    assert!(Selection::parse("oracle:").is_err());
}

#[test]
fn repository_relative_paths_reject_parent_traversal() {
    assert!(ensure_repo_relative(Path::new("target/result"), "output").is_ok());
    assert!(ensure_repo_relative(Path::new("../target/result"), "output").is_err());
}

#[test]
fn historical_provenance_is_not_the_execution_target_policy() {
    assert_eq!(HISTORICAL_PROVENANCE_BASELINE.len(), 40);
    assert_eq!(EXECUTION_TARGET_BINDING, "OBSERVED_CLEAN_CHECKOUT_HEAD");
    assert_ne!(HISTORICAL_PROVENANCE_BASELINE, EXECUTION_TARGET_BINDING);
}
