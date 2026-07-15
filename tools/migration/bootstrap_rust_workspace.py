#!/usr/bin/env python3
"""Create the responsibility-boundary crate skeleton; it is not product support."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CRATES = {
    "deeplus-source": "source text, spans, source maps, and immutable source identity",
    "deeplus-lexer": "tokenization, trivia, lexical modes, and recovery tokens",
    "deeplus-parser": "root-connected parsing and lossless CST construction",
    "deeplus-ast": "typed AST facade over the lossless CST",
    "deeplus-hir": "contextual admission and normalized typed HIR",
    "deeplus-types": "RCTS constraints, ownership, effects, errors, and checker laws",
    "deeplus-mir": "canonical Deeplus MIR model, verifier, and observable semantics",
    "deeplus-lowering": "HIR-to-MIR lowering with explicit responsibility preservation",
    "deeplus-xbc": "xVM bytecode model, encoding, decoding, and verifier",
    "deeplus-xvm": "xVM interpreter, debugger hooks, and REPL execution runtime",
    "deeplus-codegen-llvm": "shared MIR-to-LLVM lowering for AOT and later ORC JIT",
    "deeplus-diagnostics": "stable diagnostic identity, rendering, ordering, and fix-its",
    "deeplus-testkit": "fixtures, mutation, differential, and receipt helpers",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


for name, responsibility in CRATES.items():
    crate = ROOT / "crates" / name
    write(
        crate / "Cargo.toml",
        f'''[package]\nname = "{name}"\nversion.workspace = true\nedition.workspace = true\nlicense.workspace = true\nrust-version.workspace = true\n\n[lints]\nworkspace = true\n''',
    )
    const_name = name.replace("-", "_").upper()
    write(
        crate / "src/lib.rs",
        f'''//! Deeplus responsibility-boundary scaffold: {responsibility}.\n//!\n//! This crate has no product execution receipt at migration M1.\n\n#![forbid(unsafe_code)]\n\n/// The architecture responsibility assigned by Management System R1.1.\npub const RESPONSIBILITY: &str = "{responsibility}";\n/// A compiled scaffold must not be confused with language support.\npub const PRODUCT_STATUS: &str = "NOT_RUN";\n/// Stable marker used by repository-structure tests only.\npub struct {''.join(part.title() for part in name.split('-'))}Scaffold;\n\n#[cfg(test)]\nmod tests {{\n    use super::*;\n\n    #[test]\n    fn scaffold_is_evidence_honest() {{\n        assert_eq!(PRODUCT_STATUS, "NOT_RUN");\n        assert!(!RESPONSIBILITY.is_empty());\n    }}\n}}\n''',
    )

cli = ROOT / "crates/deeplusc"
write(
    cli / "Cargo.toml",
    '''[package]\nname = "deeplusc"\nversion.workspace = true\nedition.workspace = true\nlicense.workspace = true\nrust-version.workspace = true\n\n[lints]\nworkspace = true\n''',
)
write(
    cli / "src/main.rs",
    '''//! Deeplus compiler CLI boundary. No compiler product is implemented at M1.\n\n#![forbid(unsafe_code)]\n\nfn main() {\n    eprintln!("deeplusc: repository scaffold only; product status NOT_RUN");\n}\n''',
)

xtask = ROOT / "crates/deeplus-xtask"
write(
    xtask / "Cargo.toml",
    '''[package]\nname = "deeplus-xtask"\nversion.workspace = true\nedition.workspace = true\nlicense.workspace = true\nrust-version.workspace = true\n\n[lints]\nworkspace = true\n''',
)
write(
    xtask / "src/main.rs",
    '''//! Repository automation entry point. Product lanes remain independent.\n\n#![forbid(unsafe_code)]\n\nfn main() {\n    println!("Product status: NOT_RUN");\n    println!("Use tools/validators/validate_workspace.py for migration M1 checks.");\n}\n''',
)

print(f"created {len(CRATES) + 2} Rust crate scaffolds")
