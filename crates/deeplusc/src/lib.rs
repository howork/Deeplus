//! Library entry point for the bounded Deeplus compiler candidate.

pub mod sfd_cli;

use std::ffi::OsString;

pub fn run(arguments: impl IntoIterator<Item = OsString>) -> i32 {
    match sfd_cli::run(arguments) {
        Ok(summary) => match deeplus_testkit::sfd_p1_009::canonical_line(&summary) {
            Ok(line) => {
                print!("{}", String::from_utf8_lossy(&line));
                0
            }
            Err(error) => emit_error(&error),
        },
        Err(error) => emit_error(&error),
    }
}

fn emit_error(error: &deeplus_testkit::sfd_p1_009::ContractError) -> i32 {
    let line = deeplus_testkit::sfd_p1_009::canonical_line(&error.as_json())
        .unwrap_or_else(|_| b"{\"symbol\":\"INTERNAL_INVARIANT\",\"exit_code\":70}\n".to_vec());
    eprint!("{}", String::from_utf8_lossy(&line));
    error.exit_code
}
