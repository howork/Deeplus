//! Deeplus compiler CLI boundary.

#![forbid(unsafe_code)]

fn main() {
    std::process::exit(deeplusc::run(std::env::args_os()));
}
