//! Strict command grammar and atomic output publication for SFD-P1-009.

use deeplus_source::sfd_p1_009::REQUIRED_BASELINE;
use deeplus_testkit::sfd_p1_009::{
    ContractBundle, ContractError, ExecutionBindings, Selection, Value, canonical_line,
    canonical_ndjson, ensure_repo_relative, json, run_selection, sha256_hex,
};
use std::env;
use std::ffi::OsString;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const CONTRACT_ROOT: &str = "crates/deeplus-testkit/fixtures/sfd_p1_009";
const CURRENT_POINTER: &str = "current/current-pointer.json";
const IMPLEMENTATION_PATHS: &[&str] = &[
    "Cargo.lock",
    "crates/deeplus-source/Cargo.toml",
    "crates/deeplus-lexer/Cargo.toml",
    "crates/deeplus-parser/Cargo.toml",
    "crates/deeplus-ast/Cargo.toml",
    "crates/deeplus-types/Cargo.toml",
    "crates/deeplus-hir/Cargo.toml",
    "crates/deeplus-lowering/Cargo.toml",
    "crates/deeplus-mir/Cargo.toml",
    "crates/deeplus-diagnostics/Cargo.toml",
    "crates/deeplus-xbc/Cargo.toml",
    "crates/deeplus-xvm/Cargo.toml",
    "crates/deeplus-testkit/Cargo.toml",
    "crates/deeplusc/Cargo.toml",
    "crates/deeplus-source/src/lib.rs",
    "crates/deeplus-lexer/src/lib.rs",
    "crates/deeplus-parser/src/lib.rs",
    "crates/deeplus-ast/src/lib.rs",
    "crates/deeplus-types/src/lib.rs",
    "crates/deeplus-hir/src/lib.rs",
    "crates/deeplus-lowering/src/lib.rs",
    "crates/deeplus-mir/src/lib.rs",
    "crates/deeplus-diagnostics/src/lib.rs",
    "crates/deeplus-xbc/src/lib.rs",
    "crates/deeplus-xvm/src/lib.rs",
    "crates/deeplus-testkit/src/lib.rs",
    "crates/deeplusc/src/main.rs",
    "crates/deeplus-source/src/sfd_p1_009.rs",
    "crates/deeplus-lexer/src/sfd_p1_009.rs",
    "crates/deeplus-parser/src/sfd_p1_009.rs",
    "crates/deeplus-ast/src/sfd_p1_009.rs",
    "crates/deeplus-types/src/sfd_p1_009.rs",
    "crates/deeplus-hir/src/sfd_p1_009.rs",
    "crates/deeplus-lowering/src/sfd_p1_009.rs",
    "crates/deeplus-mir/src/sfd_p1_009.rs",
    "crates/deeplus-diagnostics/src/sfd_p1_009.rs",
    "crates/deeplus-xbc/src/sfd_p1_009.rs",
    "crates/deeplus-xvm/src/sfd_p1_009.rs",
    "crates/deeplus-testkit/src/sfd_p1_009.rs",
    "crates/deeplusc/src/lib.rs",
    "crates/deeplusc/src/sfd_cli.rs",
    "crates/deeplusc/tests/sfd_p1_009.rs",
    "crates/deeplus-testkit/fixtures/sfd_p1_009/Test_Deeplus_SFD_P1_009_Executable_Fixture_Manifest_R3.json",
    "crates/deeplus-testkit/fixtures/sfd_p1_009/Test_Deeplus_SFD_P1_009_Fixture_Payload_Bundle_R1.json",
    "crates/deeplus-testkit/fixtures/sfd_p1_009/Test_Deeplus_SFD_P1_009_Diagnostic_And_Trace_Oracle_R3.json",
    "crates/deeplus-testkit/fixtures/sfd_p1_009/Test_Deeplus_SFD_P1_009_Local_Candidate_Diagnostic_Registry_R1.json",
];

struct Arguments {
    contract_root: PathBuf,
    selection: Selection,
    output_dir: PathBuf,
    command: String,
}

pub fn run(arguments: impl IntoIterator<Item = OsString>) -> Result<Value, ContractError> {
    let arguments = parse_arguments(arguments)?;
    let repository = repository_root()?;
    baseline_gate(&repository)?;

    let expected_root = Path::new(CONTRACT_ROOT);
    if arguments.contract_root != expected_root {
        return Err(ContractError::new(
            78,
            "UNSUPPORTED_BINDING",
            format!("contract root must be {CONTRACT_ROOT}"),
        ));
    }
    let contract_root = repository.join(&arguments.contract_root);
    let output_dir = repository.join(&arguments.output_dir);
    if output_dir.exists() {
        return Err(ContractError::new(
            73,
            "OUTPUT_PUBLICATION",
            format!("output directory already exists: {}", output_dir.display()),
        ));
    }

    let bundle = ContractBundle::load(&contract_root)?;
    let bindings = execution_bindings(&repository, &arguments.command)?;
    let artifacts = run_selection(&bundle, &arguments.selection, &bindings)?;
    publish(
        &output_dir,
        &canonical_ndjson(&artifacts.receipts)?,
        &canonical_ndjson(&artifacts.diagnostics)?,
        &canonical_ndjson(&artifacts.traces)?,
        &canonical_line(&artifacts.summary)?,
    )?;
    Ok(json!({
        "schema": "deeplus.sfd-p1-009-cli-result/v1",
        "result": "MATCH",
        "selected_cases": artifacts.receipts.len(),
        "diagnostic_cases": artifacts.diagnostics.len(),
        "output_dir": arguments.output_dir.to_string_lossy()
    }))
}

fn parse_arguments(
    arguments: impl IntoIterator<Item = OsString>,
) -> Result<Arguments, ContractError> {
    let values = arguments
        .into_iter()
        .map(|value| {
            value
                .into_string()
                .map_err(|_| usage("all arguments must be strict UTF-8"))
        })
        .collect::<Result<Vec<_>, _>>()?;
    let tail = values
        .get(1..)
        .ok_or_else(|| usage("missing executable argument vector"))?;
    if tail.len() != 8
        || tail[0] != "sfd-p1-009"
        || tail[1] != "execute"
        || tail[2] != "--contract-root"
        || tail[4] != "--selection"
        || tail[6] != "--output-dir"
    {
        return Err(usage(
            "expected: sfd-p1-009 execute --contract-root DIR --selection SELECTOR --output-dir DIR",
        ));
    }
    if tail.iter().any(|value| value.contains('=')) {
        return Err(usage("equals-form flags are forbidden"));
    }
    let contract_root = ensure_repo_relative(Path::new(&tail[3]), "contract root")?;
    let selection = Selection::parse(&tail[5])?;
    let output_dir = ensure_repo_relative(Path::new(&tail[7]), "output directory")?;
    let command = tail.join(" ");
    Ok(Arguments {
        contract_root,
        selection,
        output_dir,
        command,
    })
}

fn repository_root() -> Result<PathBuf, ContractError> {
    let output = Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .output()
        .map_err(|error| io_error(format!("cannot invoke git: {error}")))?;
    if !output.status.success() {
        return Err(unsupported("repository root is unavailable"));
    }
    let root = std::str::from_utf8(&output.stdout)
        .map_err(|_| unsupported("git repository root is not UTF-8"))?
        .trim();
    if root.is_empty() {
        return Err(unsupported("git repository root is empty"));
    }
    Ok(PathBuf::from(root))
}

fn baseline_gate(repository: &Path) -> Result<(), ContractError> {
    let output = Command::new("git")
        .current_dir(repository)
        .args(["rev-parse", "HEAD"])
        .output()
        .map_err(|error| io_error(format!("cannot invoke git baseline gate: {error}")))?;
    let head = std::str::from_utf8(&output.stdout)
        .map_err(|_| unsupported("git HEAD is not UTF-8"))?
        .trim();
    if !output.status.success() || head != REQUIRED_BASELINE {
        return Err(unsupported(format!(
            "baseline must be exactly {REQUIRED_BASELINE}; observed {head}"
        )));
    }
    Ok(())
}

fn execution_bindings(
    repository: &Path,
    command: &str,
) -> Result<ExecutionBindings, ContractError> {
    let rustc = Command::new("rustc")
        .arg("--version")
        .output()
        .map_err(|error| io_error(format!("cannot invoke rustc: {error}")))?;
    let rust_toolchain = std::str::from_utf8(&rustc.stdout)
        .map_err(|_| unsupported("rustc version output is not UTF-8"))?
        .trim()
        .to_owned();
    if !rustc.status.success() || !rust_toolchain.starts_with("rustc 1.85.0 ") {
        return Err(unsupported(format!(
            "required rustc 1.85.0; observed {rust_toolchain}"
        )));
    }
    let current_pointer_digest = file_digest(&repository.join(CURRENT_POINTER))?;
    let implementation_digest = implementation_digest(repository)?;
    let compiler_binary_digest = env::current_exe()
        .map_err(|error| io_error(format!("cannot identify compiler binary: {error}")))
        .and_then(|path| file_digest(&path))?;
    let target_triple = format!(
        "{}-pc-{}-{}",
        env::consts::ARCH,
        env::consts::OS,
        env::consts::FAMILY
    );
    let environment_digest = environment_digest()?;
    Ok(ExecutionBindings {
        current_pointer_digest,
        implementation_digest,
        rust_toolchain,
        target_triple,
        compiler_binary_digest,
        command: command.to_owned(),
        environment_digest,
    })
}

fn implementation_digest(repository: &Path) -> Result<String, ContractError> {
    let mut digest_input = Vec::new();
    for relative in IMPLEMENTATION_PATHS {
        let bytes = fs::read(repository.join(relative))
            .map_err(|error| io_error(format!("{relative}: {error}")))?;
        digest_input.extend_from_slice(relative.as_bytes());
        digest_input.push(0);
        digest_input
            .extend_from_slice(&u64::try_from(bytes.len()).unwrap_or(u64::MAX).to_le_bytes());
        digest_input.extend_from_slice(&bytes);
    }
    Ok(sha256_hex(&digest_input))
}

fn environment_digest() -> Result<String, ContractError> {
    let mut entries = env::vars_os()
        .map(|(key, value)| {
            let key = key
                .into_string()
                .map_err(|_| unsupported("environment key is not UTF-8"))?;
            let value = value
                .into_string()
                .map_err(|_| unsupported(format!("environment value for {key} is not UTF-8")))?;
            Ok((key, value))
        })
        .collect::<Result<Vec<_>, ContractError>>()?;
    entries.sort();
    let mut digest_input = Vec::new();
    for (key, value) in entries {
        digest_input.extend_from_slice(key.as_bytes());
        digest_input.push(0);
        digest_input.extend_from_slice(value.as_bytes());
        digest_input.push(0xff);
    }
    Ok(sha256_hex(&digest_input))
}

fn file_digest(path: &Path) -> Result<String, ContractError> {
    let metadata = fs::symlink_metadata(path)
        .map_err(|error| io_error(format!("{}: {error}", path.display())))?;
    if metadata.file_type().is_symlink() || !metadata.file_type().is_file() {
        return Err(io_error(format!(
            "{} is not a regular non-symlink file",
            path.display()
        )));
    }
    let bytes = fs::read(path).map_err(|error| io_error(format!("{}: {error}", path.display())))?;
    Ok(sha256_hex(&bytes))
}

fn publish(
    output_dir: &Path,
    receipts: &[u8],
    diagnostics: &[u8],
    traces: &[u8],
    summary: &[u8],
) -> Result<(), ContractError> {
    let parent = output_dir
        .parent()
        .ok_or_else(|| publication("output directory has no parent"))?;
    fs::create_dir_all(parent)
        .map_err(|error| publication(format!("cannot create output parent: {error}")))?;
    let name = output_dir
        .file_name()
        .and_then(|value| value.to_str())
        .ok_or_else(|| publication("output directory name is not UTF-8"))?;
    let staging = parent.join(format!(".{name}.staging-{}", std::process::id()));
    if staging.exists() {
        return Err(publication(format!(
            "private staging path already exists: {}",
            staging.display()
        )));
    }
    fs::create_dir(&staging)
        .map_err(|error| publication(format!("cannot create staging directory: {error}")))?;
    let writes = [
        ("sfd-target-receipts-v2.ndjson", receipts),
        ("sfd-diagnostic-payloads-v1.ndjson", diagnostics),
        ("sfd-execution-traces-v1.ndjson", traces),
        ("sfd-run-summary-v1.json", summary),
    ];
    for (name, bytes) in writes {
        fs::write(staging.join(name), bytes)
            .map_err(|error| publication(format!("cannot write {name}: {error}")))?;
    }
    fs::rename(&staging, output_dir)
        .map_err(|error| publication(format!("atomic output publication failed: {error}")))?;
    Ok(())
}

fn usage(message: impl Into<String>) -> ContractError {
    ContractError::new(64, "CLI_USAGE", message)
}

fn unsupported(message: impl Into<String>) -> ContractError {
    ContractError::new(78, "UNSUPPORTED_BINDING", message)
}

fn publication(message: impl Into<String>) -> ContractError {
    ContractError::new(73, "OUTPUT_PUBLICATION", message)
}

fn io_error(message: impl Into<String>) -> ContractError {
    ContractError::new(74, "IO_ERROR", message)
}
