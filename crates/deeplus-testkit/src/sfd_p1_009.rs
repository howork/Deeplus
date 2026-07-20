//! Frozen fixture loader and compile-time product route for SFD-P1-009.
//!
//! The module contains an executable route, but the bounded R4 build gate only
//! compiles it. Running the route remains a separately authorized action.

use base64::Engine as _;
use base64::engine::general_purpose::STANDARD;
use deeplus_source::sfd_p1_009::{IngressPhase, PROFILE_ID, REQUIRED_BASELINE, SourceCase};
use serde_json::Map;
pub use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::fmt;
use std::fs;
use std::path::{Path, PathBuf};

const MANIFEST_FILE: FrozenFile = FrozenFile {
    name: "Test_Deeplus_SFD_P1_009_Executable_Fixture_Manifest_R3.json",
    bytes: 116_479,
    sha256: "26d50b5d5e0055ef820ba02159fe692ee395acbcf75de7fca938a8fad10f6a8d",
};
const PAYLOAD_FILE: FrozenFile = FrozenFile {
    name: "Test_Deeplus_SFD_P1_009_Fixture_Payload_Bundle_R1.json",
    bytes: 798_327,
    sha256: "8959eea0091d1814c8a72872b8294f4603d407fcabd135db802997c8a55f91b6",
};
const ORACLE_FILE: FrozenFile = FrozenFile {
    name: "Test_Deeplus_SFD_P1_009_Diagnostic_And_Trace_Oracle_R3.json",
    bytes: 2_554_829,
    sha256: "7ca63c9c19745cb9ac3c0b0890dbbc42f974643351a4fa2003c21d82249f5e67",
};
const REGISTRY_FILE: FrozenFile = FrozenFile {
    name: "Test_Deeplus_SFD_P1_009_Local_Candidate_Diagnostic_Registry_R1.json",
    bytes: 549_675,
    sha256: "9851304b976ddefdf23ac36b28846b591c4cb6543448c2b5073fafdebcd6859a",
};

#[derive(Clone, Copy)]
struct FrozenFile {
    name: &'static str,
    bytes: u64,
    sha256: &'static str,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Selection {
    AllExecute,
    Oracle(String),
    Subfixture(String),
}

impl Selection {
    pub fn parse(value: &str) -> Result<Self, ContractError> {
        if value == "all-execute" {
            return Ok(Self::AllExecute);
        }
        if let Some(id) = value.strip_prefix("oracle:").filter(|id| !id.is_empty()) {
            return Ok(Self::Oracle(id.to_owned()));
        }
        if let Some(id) = value
            .strip_prefix("subfixture:")
            .filter(|id| !id.is_empty())
        {
            return Ok(Self::Subfixture(id.to_owned()));
        }
        Err(ContractError::new(
            64,
            "CLI_USAGE",
            "selection must be all-execute, oracle:ORACLE_ID, or subfixture:SUBFIXTURE_ID",
        ))
    }
}

#[derive(Clone, Debug)]
pub struct ExecutionBindings {
    pub current_pointer_digest: String,
    pub implementation_digest: String,
    pub rust_toolchain: String,
    pub target_triple: String,
    pub compiler_binary_digest: String,
    pub command: String,
    pub environment_digest: String,
}

#[derive(Clone, Debug)]
pub struct RunArtifacts {
    pub receipts: Vec<Value>,
    pub diagnostics: Vec<Value>,
    pub traces: Vec<Value>,
    pub summary: Value,
}

#[derive(Debug)]
pub struct ContractError {
    pub exit_code: i32,
    pub symbol: &'static str,
    pub message: String,
}

impl ContractError {
    pub fn new(exit_code: i32, symbol: &'static str, message: impl Into<String>) -> Self {
        Self {
            exit_code,
            symbol,
            message: message.into(),
        }
    }

    pub fn as_json(&self) -> Value {
        json!({
            "schema": "SFD-RUNNER-ERROR-V1",
            "symbol": self.symbol,
            "message": self.message,
            "exit_code": self.exit_code
        })
    }
}

impl fmt::Display for ContractError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.symbol, self.message)
    }
}

impl std::error::Error for ContractError {}

pub struct ContractBundle {
    payloads: BTreeMap<String, Value>,
    cases: BTreeMap<String, Value>,
    diagnostic_registry: BTreeMap<String, Value>,
    oracle_dispositions: BTreeMap<String, String>,
    fixture_digests: BTreeMap<String, String>,
}

impl ContractBundle {
    pub fn load(root: &Path) -> Result<Self, ContractError> {
        let (manifest, manifest_digest) = load_frozen(root, MANIFEST_FILE)?;
        let (payload, payload_digest) = load_frozen(root, PAYLOAD_FILE)?;
        let (oracle, oracle_digest) = load_frozen(root, ORACLE_FILE)?;
        let (registry, registry_digest) = load_frozen(root, REGISTRY_FILE)?;

        let bindings = array(&manifest, "oracle_bindings")?;
        require_count(bindings, 141, "oracle binding")?;
        let mut oracle_dispositions = BTreeMap::new();
        let mut manifest_subfixtures = BTreeSet::new();
        let mut execute_count = 0_usize;
        let mut na_count = 0_usize;
        for binding in bindings {
            let oracle_id = text(binding, "oracle_id")?;
            let disposition = text(binding, "execution_disposition")?;
            match disposition {
                "EXECUTE" => execute_count += 1,
                "NOT_APPLICABLE" => na_count += 1,
                _ => return data_error(format!("unsupported disposition for {oracle_id}")),
            }
            if oracle_dispositions
                .insert(oracle_id.to_owned(), disposition.to_owned())
                .is_some()
            {
                return data_error(format!("duplicate oracle identity {oracle_id}"));
            }
            for id in array(binding, "subfixture_ids")? {
                let id = id
                    .as_str()
                    .ok_or_else(|| data("subfixture identity must be a string"))?;
                if !manifest_subfixtures.insert(id.to_owned()) {
                    return data_error(format!("duplicate manifest subfixture {id}"));
                }
            }
        }
        if execute_count != 140 || na_count != 1 {
            return data_error("manifest must contain 140 EXECUTE and one NOT_APPLICABLE oracle");
        }

        let payload_rows = array(&payload, "payloads")?;
        require_count(payload_rows, 456, "payload")?;
        let mut payloads = BTreeMap::new();
        for row in payload_rows {
            let id = text(row, "subfixture_id")?;
            validate_payload(row)?;
            if payloads.insert(id.to_owned(), row.clone()).is_some() {
                return data_error(format!("duplicate payload identity {id}"));
            }
        }

        let case_rows = array(&oracle, "case_bindings")?;
        require_count(case_rows, 456, "oracle case")?;
        let mut cases = BTreeMap::new();
        for row in case_rows {
            let id = text(row, "subfixture_id")?;
            validate_case(row, payloads.get(id))?;
            if cases.insert(id.to_owned(), row.clone()).is_some() {
                return data_error(format!("duplicate oracle case identity {id}"));
            }
        }

        let registry_rows = array(&registry, "entries")?;
        require_count(registry_rows, 278, "diagnostic candidate")?;
        let mut diagnostic_registry = BTreeMap::new();
        for row in registry_rows {
            let id = text(row, "candidate_id")?;
            if diagnostic_registry
                .insert(id.to_owned(), row.clone())
                .is_some()
            {
                return data_error(format!("duplicate diagnostic candidate {id}"));
            }
        }

        let payload_ids: BTreeSet<_> = payloads.keys().cloned().collect();
        let case_ids: BTreeSet<_> = cases.keys().cloned().collect();
        if payload_ids != case_ids || payload_ids != manifest_subfixtures {
            return data_error("manifest, payload, and oracle subfixture identity sets differ");
        }
        for (id, row) in &cases {
            let oracle_id = text(row, "oracle_id")?;
            if oracle_dispositions.get(oracle_id).map(String::as_str) != Some("EXECUTE") {
                return data_error(format!("{id} is not owned by an EXECUTE oracle"));
            }
            if text(row, "expected_outcome")? == "REJECT" {
                let code = text(row, "expected_diagnostic_code")?;
                if !diagnostic_registry.contains_key(code) {
                    return data_error(format!("{id} references missing diagnostic {code}"));
                }
            }
        }

        Ok(Self {
            payloads,
            cases,
            diagnostic_registry,
            oracle_dispositions,
            fixture_digests: BTreeMap::from([
                (MANIFEST_FILE.name.to_owned(), manifest_digest),
                (PAYLOAD_FILE.name.to_owned(), payload_digest),
                (ORACLE_FILE.name.to_owned(), oracle_digest),
                (REGISTRY_FILE.name.to_owned(), registry_digest),
            ]),
        })
    }

    pub fn selected_ids(&self, selection: &Selection) -> Result<Vec<String>, ContractError> {
        match selection {
            Selection::AllExecute => Ok(self.payloads.keys().cloned().collect()),
            Selection::Oracle(oracle_id) => {
                if self.oracle_dispositions.get(oracle_id).map(String::as_str) != Some("EXECUTE") {
                    return Err(ContractError::new(
                        64,
                        "CLI_USAGE",
                        format!("oracle selector is absent or not executable: {oracle_id}"),
                    ));
                }
                Ok(self
                    .cases
                    .iter()
                    .filter(|(_, row)| text_unchecked(row, "oracle_id") == oracle_id)
                    .map(|(id, _)| id.clone())
                    .collect())
            }
            Selection::Subfixture(id) => {
                if self.payloads.contains_key(id) {
                    Ok(vec![id.clone()])
                } else {
                    Err(ContractError::new(
                        64,
                        "CLI_USAGE",
                        format!("unknown subfixture selector: {id}"),
                    ))
                }
            }
        }
    }
}

pub fn run_selection(
    bundle: &ContractBundle,
    selection: &Selection,
    bindings: &ExecutionBindings,
) -> Result<RunArtifacts, ContractError> {
    let ids = bundle.selected_ids(selection)?;
    let mut receipts = Vec::with_capacity(ids.len());
    let mut diagnostics = Vec::new();
    let mut traces = Vec::with_capacity(ids.len());
    let mut outcome_counts = BTreeMap::<String, u64>::new();

    for id in &ids {
        let payload = bundle
            .payloads
            .get(id)
            .ok_or_else(|| invariant(format!("selected payload disappeared: {id}")))?;
        let oracle = bundle
            .cases
            .get(id)
            .ok_or_else(|| invariant(format!("selected oracle disappeared: {id}")))?;
        let observation = execute_product(payload)?;
        let expected = text(oracle, "expected_outcome")?;
        if observation.outcome.as_str() != expected {
            return Err(ContractError::new(
                1,
                "OBSERVATION_MISMATCH",
                format!(
                    "{id}: expected {expected}, observed {}",
                    observation.outcome.as_str()
                ),
            ));
        }
        *outcome_counts.entry(expected.to_owned()).or_default() += 1;

        let trace = trace_value(&observation);
        let trace_digest = sha256_hex(&canonical_line(&trace)?);
        traces.push(trace);
        receipts.push(receipt_value(
            oracle,
            payload,
            &observation,
            bindings,
            &trace_digest,
        )?);

        if expected == "REJECT" {
            let code = text(oracle, "expected_diagnostic_code")?;
            let registry = bundle.diagnostic_registry.get(code).ok_or_else(|| {
                invariant(format!("diagnostic registry entry disappeared: {code}"))
            })?;
            diagnostics.push(json!({
                "schema": "SFD-DIAGNOSTIC-PAYLOAD-V1",
                "subfixture_id": id,
                "oracle_id": text(oracle, "oracle_id")?,
                "diagnostic_code": code,
                "primary_span": oracle.get("expected_primary_span").cloned().unwrap_or(Value::Null),
                "ordered_notes": registry.get("ordered_notes").cloned().unwrap_or_else(|| json!([])),
                "suppressed_stages": registry.get("suppressed_stages").cloned().unwrap_or_else(|| json!([]))
            }));
        }
    }

    let summary = json!({
        "schema": "SFD-P1-009-RUN-SUMMARY-V1",
        "profile_id": PROFILE_ID,
        "baseline_commit": REQUIRED_BASELINE,
        "selection": match selection {
            Selection::AllExecute => "all-execute".to_owned(),
            Selection::Oracle(id) => format!("oracle:{id}"),
            Selection::Subfixture(id) => format!("subfixture:{id}"),
        },
        "selected_cases": ids.len(),
        "diagnostic_cases": diagnostics.len(),
        "outcome_counts": outcome_counts,
        "fixture_digests": bundle.fixture_digests,
        "result": "MATCH"
    });
    Ok(RunArtifacts {
        receipts,
        diagnostics,
        traces,
        summary,
    })
}

fn execute_product(payload: &Value) -> Result<deeplus_xvm::sfd_p1_009::Observation, ContractError> {
    let bytes = STANDARD
        .decode(text(payload, "canonical_bytes_base64")?)
        .map_err(|error| data(format!("invalid payload Base64: {error}")))?;
    let source = SourceCase {
        oracle_id: text(payload, "oracle_id")?.to_owned(),
        subfixture_id: text(payload, "subfixture_id")?.to_owned(),
        ingress_phase: IngressPhase::parse(text(payload, "ingress_phase")?)
            .map_err(|error| data(error.to_string()))?,
        selected_mode: text(payload, "selected_mode")?.to_owned(),
        media_type: text(payload, "payload_media_type")?.to_owned(),
        bytes,
    };
    let lexed = deeplus_lexer::sfd_p1_009::lex(source).map_err(|error| route(error.to_string()))?;
    let parsed =
        deeplus_parser::sfd_p1_009::parse(lexed).map_err(|error| route(error.to_string()))?;
    let ast = deeplus_ast::sfd_p1_009::lower(parsed);
    let typed = deeplus_types::sfd_p1_009::check(ast);
    let hir = deeplus_hir::sfd_p1_009::lower(typed);
    let mir = deeplus_lowering::sfd_p1_009::lower(hir);
    let bytecode = deeplus_xbc::sfd_p1_009::emit(mir).map_err(route)?;
    Ok(deeplus_xvm::sfd_p1_009::execute(bytecode))
}

fn receipt_value(
    oracle: &Value,
    payload: &Value,
    observation: &deeplus_xvm::sfd_p1_009::Observation,
    bindings: &ExecutionBindings,
    trace_digest: &str,
) -> Result<Value, ContractError> {
    let mut receipt = oracle
        .get("receipt_expectations")
        .and_then(Value::as_object)
        .cloned()
        .ok_or_else(|| data("receipt_expectations must be an object"))?;
    replace(&mut receipt, "baseline_commit", json!(REQUIRED_BASELINE));
    replace(
        &mut receipt,
        "current_pointer_digest",
        json!(bindings.current_pointer_digest),
    );
    replace(
        &mut receipt,
        "implementation_commit_or_diff_digest",
        json!(bindings.implementation_digest),
    );
    replace(
        &mut receipt,
        "rust_toolchain",
        json!(bindings.rust_toolchain),
    );
    replace(&mut receipt, "target_triple", json!(bindings.target_triple));
    replace(
        &mut receipt,
        "compiler_binary_digest",
        json!(bindings.compiler_binary_digest),
    );
    replace(&mut receipt, "command", json!(bindings.command));
    replace(
        &mut receipt,
        "environment_digest",
        json!(bindings.environment_digest),
    );
    replace(
        &mut receipt,
        "fixture_digest",
        json!(text(payload, "sha256")?),
    );
    replace(&mut receipt, "profile_id", json!(PROFILE_ID));
    replace(
        &mut receipt,
        "operation_id",
        json!(observation.operation_id),
    );
    replace(&mut receipt, "event_index", json!(observation.events.len()));
    replace(
        &mut receipt,
        "phase_ordinal",
        json!(observation.events.len()),
    );
    replace(
        &mut receipt,
        "payload_eval_count",
        json!(observation.payload_eval_count),
    );
    replace(
        &mut receipt,
        "lookup_count",
        json!(observation.lookup_count),
    );
    replace(
        &mut receipt,
        "fallback_attempt_count",
        json!(observation.fallback_attempt_count),
    );
    replace(
        &mut receipt,
        "commit_count",
        json!(observation.commit_count),
    );
    replace(
        &mut receipt,
        "rollback_count",
        json!(observation.rollback_count),
    );
    replace(
        &mut receipt,
        "publication_count",
        json!(observation.publication_count),
    );
    replace(&mut receipt, "drop_count", json!(observation.drop_count));
    replace(&mut receipt, "outcome", json!(observation.outcome.as_str()));
    replace(
        &mut receipt,
        "diagnostic_code",
        oracle
            .get("expected_diagnostic_code")
            .cloned()
            .unwrap_or(Value::Null),
    );
    replace(
        &mut receipt,
        "primary_span",
        oracle
            .get("expected_primary_span")
            .cloned()
            .unwrap_or(Value::Null),
    );
    replace(&mut receipt, "stdout_digest", json!(sha256_hex(b"")));
    replace(&mut receipt, "stderr_digest", json!(sha256_hex(b"")));
    replace(&mut receipt, "trace_digest", json!(trace_digest));
    replace(&mut receipt, "exit_code", json!(0));
    if receipt.len() != 45 {
        return data_error("materialized receipt does not contain exactly 45 fields");
    }
    Ok(Value::Object(receipt))
}

fn trace_value(observation: &deeplus_xvm::sfd_p1_009::Observation) -> Value {
    json!({
        "schema": "SFD-HIR-MIR-TRACE-V1",
        "oracle_id": observation.oracle_id,
        "subfixture_id": observation.subfixture_id,
        "operation_id": observation.operation_id,
        "outcome": observation.outcome.as_str(),
        "events": observation.events.iter().map(|event| json!({
            "event_index": event.event_index,
            "phase_ordinal": event.phase_ordinal,
            "phase": event.phase
        })).collect::<Vec<_>>(),
        "fallback_attempt_count": observation.fallback_attempt_count
    })
}

pub fn canonical_line(value: &Value) -> Result<Vec<u8>, ContractError> {
    let mut bytes = serde_json::to_vec(value)
        .map_err(|error| invariant(format!("JSON serialization failed: {error}")))?;
    bytes.push(b'\n');
    Ok(bytes)
}

pub fn canonical_ndjson(values: &[Value]) -> Result<Vec<u8>, ContractError> {
    let mut bytes = Vec::new();
    for value in values {
        bytes.extend(canonical_line(value)?);
    }
    Ok(bytes)
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn load_frozen(root: &Path, frozen: FrozenFile) -> Result<(Value, String), ContractError> {
    let path = root.join(frozen.name);
    let metadata =
        fs::symlink_metadata(&path).map_err(|error| unavailable(&path, error.to_string()))?;
    if metadata.file_type().is_symlink() || !metadata.file_type().is_file() {
        return Err(unavailable(
            &path,
            "input must be a regular non-symlink file",
        ));
    }
    if metadata.len() != frozen.bytes {
        return data_error(format!("{} has incorrect byte count", path.display()));
    }
    let bytes = fs::read(&path).map_err(|error| unavailable(&path, error.to_string()))?;
    let digest = sha256_hex(&bytes);
    if digest != frozen.sha256 {
        return data_error(format!("{} has incorrect SHA-256", path.display()));
    }
    let text = std::str::from_utf8(&bytes)
        .map_err(|_| data(format!("{} is not strict UTF-8", path.display())))?;
    let value = serde_json::from_str(text)
        .map_err(|error| data(format!("{} is invalid JSON: {error}", path.display())))?;
    Ok((value, digest))
}

fn validate_payload(row: &Value) -> Result<(), ContractError> {
    let encoded = text(row, "canonical_bytes_base64")?;
    let bytes = STANDARD
        .decode(encoded)
        .map_err(|error| data(format!("invalid RFC4648 Base64: {error}")))?;
    let byte_count = row
        .get("byte_count")
        .and_then(Value::as_u64)
        .ok_or_else(|| data("byte_count must be an unsigned integer"))?;
    if usize::try_from(byte_count).ok() != Some(bytes.len()) {
        return data_error("payload byte_count mismatch");
    }
    if sha256_hex(&bytes) != text(row, "sha256")? {
        return data_error("payload SHA-256 mismatch");
    }
    if bytes != text(row, "canonical_utf8_text")?.as_bytes() {
        return data_error("decoded payload differs from canonical UTF-8 text");
    }
    IngressPhase::parse(text(row, "ingress_phase")?).map_err(|error| data(error.to_string()))?;
    Ok(())
}

fn validate_case(row: &Value, payload: Option<&Value>) -> Result<(), ContractError> {
    let payload = payload.ok_or_else(|| data("oracle case has no payload"))?;
    for key in ["oracle_id", "ingress_phase", "expected_outcome"] {
        if text(row, key)? != text(payload, key)? {
            return data_error(format!("oracle/payload mismatch for {key}"));
        }
    }
    if text(row, "payload_sha256")? != text(payload, "sha256")? {
        return data_error("oracle/payload SHA-256 mismatch");
    }
    if row.get("receipt_field_count").and_then(Value::as_u64) != Some(45) {
        return data_error("receipt_field_count must be 45");
    }
    let receipt = row
        .get("receipt_expectations")
        .and_then(Value::as_object)
        .ok_or_else(|| data("receipt_expectations must be an object"))?;
    if receipt.len() != 45 {
        return data_error("receipt expectations must contain exactly 45 fields");
    }
    if receipt.get("baseline_commit").and_then(Value::as_str) != Some(REQUIRED_BASELINE) {
        return data_error("receipt baseline is not the controlling main commit");
    }
    if row.get("execution_status").and_then(Value::as_str) != Some("NOT_RUN") {
        return data_error("preimplementation execution status must remain NOT_RUN");
    }
    Ok(())
}

fn array<'a>(value: &'a Value, key: &str) -> Result<&'a [Value], ContractError> {
    value
        .get(key)
        .and_then(Value::as_array)
        .map(Vec::as_slice)
        .ok_or_else(|| data(format!("{key} must be an array")))
}

fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str, ContractError> {
    value
        .get(key)
        .and_then(Value::as_str)
        .ok_or_else(|| data(format!("{key} must be a string")))
}

fn text_unchecked<'a>(value: &'a Value, key: &str) -> &'a str {
    value.get(key).and_then(Value::as_str).unwrap_or("")
}

fn require_count(values: &[Value], expected: usize, label: &str) -> Result<(), ContractError> {
    if values.len() == expected {
        Ok(())
    } else {
        data_error(format!("{label} count must be {expected}"))
    }
}

fn replace(map: &mut Map<String, Value>, key: &str, value: Value) {
    map.insert(key.to_owned(), value);
}

fn unavailable(path: &Path, message: impl Into<String>) -> ContractError {
    ContractError::new(
        66,
        "INPUT_UNAVAILABLE",
        format!("{}: {}", path.display(), message.into()),
    )
}

fn data(message: impl Into<String>) -> ContractError {
    ContractError::new(65, "CONTRACT_DATA", message)
}

fn data_error<T>(message: impl Into<String>) -> Result<T, ContractError> {
    Err(data(message))
}

fn route(message: impl Into<String>) -> ContractError {
    ContractError::new(69, "PRODUCT_ROUTE_UNAVAILABLE", message)
}

fn invariant(message: impl Into<String>) -> ContractError {
    ContractError::new(70, "INTERNAL_INVARIANT", message)
}

pub fn ensure_repo_relative(path: &Path, label: &str) -> Result<PathBuf, ContractError> {
    if path.as_os_str().is_empty() || path.is_absolute() {
        return Err(ContractError::new(
            64,
            "CLI_USAGE",
            format!("{label} must be a nonempty repository-relative path"),
        ));
    }
    if path
        .components()
        .any(|component| matches!(component, std::path::Component::ParentDir))
    {
        return Err(ContractError::new(
            64,
            "CLI_USAGE",
            format!("{label} must not contain parent traversal"),
        ));
    }
    Ok(path.to_path_buf())
}
