# Deeplus 0.1.2 Baseline R51f3 — Fully Merged Current-Canonical Specification

Status: current language-design authority  
Publication date: 2026-07-14  
Product implementation evidence: `NOT_RUN` unless an artifact-bound product receipt states otherwise

R51f is a **fully merged package-level current-canonical artifact**, not an overlay. This document states the complete human-readable current language contract. The exact EBNF is maintained once, in `spec/grammar/deeplus.ebnf`, and is normatively incorporated by reference. Token ownership, contextual admission, input supply, CST/AST roles, and formatter boundaries are fixed by `spec/frontend/frontend-model.json`. Older releases are unnecessary for interpreting current source.

Normative words **must**, **must not**, **shall**, **shall not**, and **may** have their usual specification meaning. A code block marked accepted illustrates current source. A rejected block illustrates the exact invalid surface and does not make that surface current.

## 0. Authority, maturity, and evidence

The current authority order is:

1. this human-readable specification for language and semantic rules;
2. the separate exact Grammar for token order and structural nesting;
3. the Frontend Model for contextual token ownership, scanner boundaries, input supply, and CST/AST responsibilities;
4. the TypeSystem, Operational Semantics, and Prelude companions for formal implementation handoff;
5. active diagnostic registry and checker-predicate catalog;
6. current examples and machine projections.

Where an example or generated registry contradicts this document, the contradictory artifact is defective and must be regenerated. Non-current reports and diagnostic identities never override current rules.

Language-design maturity is separate from product support. `STABLE_DESIGN` means the rule is part of current language design; it does not mean that a Rust parser, checker, xVM, or LLVM backend has executed it. `PREVIEW` requires an explicit source gate. `PREVIEW_DESIGN` is nonactivatable. `STDLIB_PROFILE` and `OFFICIAL_TOOLING` do not create core syntax.

# Part I — Source text, lexical ownership, and files

## 1. Source files and source roles

Deeplus distinguishes library, executable, and script roots. Every selected root must consume the scanner's end-of-input token. A parser must not accept a valid prefix while ignoring trailing tokens.

- A library source contains declarations and no implicit top-level execution.
- An executable source identifies exactly one eligible `def#entry` or `def#entry#async` after target configuration.
- A script source may contain top-level executable statements under the script root contract.
- Module and package identity is static. Runtime strings never become static module paths, labels, witnesses, or type names.

The implementation must preserve source role through CST, AST/HIR, module API digest, and diagnostic reporting. Entry selection is a checker/linker responsibility; source order is not a tie-breaker.

## 2. Unicode, identifiers, and escaped names

Source text is Unicode. Ordinary identifiers follow the lexical XID policy of the exact Grammar. Hard keywords are reserved only where the scanner must commit. Contextual words remain identifiers outside their admitting owner.

An escaped member name is permitted only after member access:

```deeplus
obj.\class
map.\length
@.\trait
```

No whitespace, newline, or comment may appear between `.`, `\`, and the escaped name. A normal dot cannot select a hard keyword. No attached `?Identifier` logic-variable token exists or is reserved. The `?` glyph is owned only by current Grammar roles such as the spaced ternary operator; identifiers remain ordinary tokens.

## 3. Trivia, comments, and formatter convention

Whitespace and comments are trivia except where a boundary policy requires attachment. Line comments, block comments, documentation comments, and word comments follow scanner priority; comment openers win over operator decompositions.

The parser may admit horizontal whitespace and comments between `#` and a role word only on the same physical line. A physical line break is rejected. The formatter rehomes comments safely and prints canonical attached spelling such as `#get`, `#pure`, and `#entry`. Literal sigils are different: `#bytes`, collection literal sigils, and NumericArray literal sigils require the boundary declared for that literal and must not be reconstructed from a separated `#` plus identifier.

## 4. Numeric, character, string, and bytes literals

Every source value has a semantic type and value identity independent from storage address, serialization tag, runtime discriminant, backend layout, and ABI. This specification fixes source-observable values; it does not infer a representation contract from a literal spelling or a built-in type name.

The lexical authority includes decimal and supported radix integers, digit separators, suffixes, decimal exponents, floating forms, and the finite policy for special floating values. An underscore may separate digits only in admitted positions; it may not lead, trail, or touch a radix prefix, decimal point, exponent marker, or suffix unless the Grammar explicitly admits it. A sign is an AST prefix operator, never part of the numeric token. An unsuffixed integer has portable type `Int`, whose current mathematical domain is the signed 64-bit interval. Context may adapt a signless unsuffixed integer to one exact admitted `IntN` or `UIntN` domain only when its value is representable. In addition, with one independently fixed exact `Int`, `IntN`, or `UIntN` target, the checker recognizes only a direct `PrefixExpr(-, UnsuffixedIntegerLiteral)`, obtains the already validated token magnitude, computes the signed mathematical candidate `-magnitude`, and admits it only when representable. This contextual prefix-sign adapter performs no arbitrary constant folding, expression rewriting, or hidden widening/narrowing: `let xs: List<Int8> = [-128]` is admitted, while `let low: List<Int8> = [-129]` and `let unsigned: List<UInt8> = [-1]` are rejected with `LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE`. `ISize` and `USize` require their suffix or an explicit checked conversion. An unsuffixed floating literal remains `Float64`, and `Float32` requires `f32`. All of those types remain distinct. Integer arithmetic is checked: statically provable overflow is rejected, while dynamic overflow or integer division or remainder by zero raises a deterministic `ArithmeticDefect` before any enclosing place commit. Wrapping and saturating arithmetic require named APIs.

`Float32` and `Float64` have IEEE-754 binary32 and binary64 value behavior. Ordinary arithmetic rounds to nearest with ties to even. Non-finite values are type-side constants rather than numeric literal spellings. NaN is unordered and supplies neither implicit `Ord` nor `Keyable` evidence; signed zero compares equal. These value laws do not prescribe a backend storage or calling convention.

Character literals use single quotes and contain exactly one Unicode scalar value after escape processing. `''` is invalid. `Char` is not a byte and not a UTF-16 code unit. Plain strings use double quotes. A multiline Unicode String uses triple quotes: the opener is followed by a newline, the closer is on its own line, and the longest exact common indentation prefix of nonblank content lines is removed. Tabs and spaces are distinct prefix bytes; escapes and interpolation behave as in an ordinary String. One-line triple quotes and raw multiline strings are not current. Raw String Phase A has exactly one delimiter family, `raw"..."`; its body has no escape interpretation and no interpolation, produces `String`, preserves exact body text in the CST, lowers to `StringLiteral(raw=true)` and then `MIR::ConstString`, and invokes no provider or authority. Bytes literals produce byte sequences rather than text. Deeplus has no regex literal token or scanner mode; pattern engines are explicit library APIs receiving String or Bytes values.

An ordinary String direct segment admits Unicode scalars except the quote,
backslash, dollar, physical line terminators, and disallowed controls. Its
closed escape set is `\0`, `\n`, `\r`, `\t`, `\"`, `\\`, `\$`, ``\` ``,
`\u{H...}` with one through six hex digits, and `\N{UNICODE NAME}`. An
unescaped `$` begins either `${...}` or the exact shorthand interpolation path;
use `\$` for a literal dollar. A `#bytes"..."` body admits printable ASCII
direct bytes except quote and backslash, plus `\0`, `\n`, `\r`, `\t`, `\"`,
`\\`, and exactly two-digit `\xHH`. It admits neither interpolation nor Unicode
escapes.

String escape processing is Unicode-based. Invalid scalar values, unknown
Unicode names, unterminated escapes, and invalid delimiter nesting are lexical
diagnostics.

`null` is not a current Deeplus value and has no type, constant, AST/HIR value node, or MIR constant. The spelling remains reserved only for deterministic recovery with `NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE`. Recoverable absence is written as `::none` in an expected `Option` context or as `Option<T>::none` explicitly; it is never inferred from a null sentinel.

## 5. Punctuation responsibility table

The same glyph may have several roles only when the Grammar owner determines the role without semantic guessing.

| Glyph | Current owners |
|---|---|
| `...` | repeated positional parameter/type residue, or `for ... Pattern in Expr` comprehension unfold |
| `*` | call-side positional unfold where admitted; for example `f(*args)` |
| `***` | attached named-rest parameter suffix and function-type named-rest residue suffix only |
| `**` | attached named unfold prefix and linear-product operator |
| `.` | member access, class final dispatch marker, tuple ordinal punctuation where owned |
| `+` | addition/prefix plus and class open dispatch marker where owned |
| `*.` / `*+` | override-final / override-open class dispatch markers |
| `::` | static qualification, associated projection, enum case qualification, type-side declaration |
| `^` | attached NumericArray transpose suffix or spaced infix power |
| `#` | role/modifier introducer or an attached literal owner |
| `@` | annotations, exact value-control introducers, implicit-lambda placeholder, and current pseudo-keywords |

The scanner uses maximal munch, but maximal munch does not by itself admit a token in every grammar owner.

# Part II — Declarations, bindings, and callable surfaces

## 6. Declaration visibility and structural annotations

The type-producing top-level owner set is exactly `ClassDecl`, `TraitDecl`,
`EnumDecl`, `TypeAliasDecl`, `SchemaDecl`, `ActorDecl`, `ActorProtocolDecl`,
`TypestateResourceDecl`, and `BitfieldDecl`. Each of those nine owners requires
one explicit `public`, `common`, or `private` word in every
`LibrarySourceFile`, `ExecutableSourceFile`, `ScriptSourceFile`,
`PreviewLibrarySourceFile`, `PreviewExecutableSourceFile`, and
`PreviewScriptSourceFile`. This admission rule is uniform across all six roots;
a preview gate changes neither the explicit-visibility requirement for these
nine owners nor the `private` default for other top-level visibility owners.

The exact Grammar keeps `TopLevelVisibility?` on these owners for deterministic
recovery. If the word is omitted, the parser may retain a structural candidate,
but the checker emits `TYPE_DECL_VISIBILITY_REQUIRED` and admits zero HIR type
declaration nodes, type identities, or API-digest entries from that candidate.
This recovery form is never an implicit `private` type declaration.

Other top-level owners that grammatically carry `TopLevelVisibility?` are not
type-producing owners. Their omitted word normalizes to `private`; an explicit
word is preserved. `public` is eligible to enter external package API only
through an admitted export or module interface. `common` is visible across
modules of the declaring package but is excluded from external package API and
re-export. `private` is visible only in the declaring module. Package identity
comes from the build/module graph; `common` introduces no package-declaration
syntax. API closure is checked after normalization: a wider visibility domain
cannot expose a dependency identity from a narrower domain, and a `public`
declaration is not externally exported merely because it is public.

Member declarations use `+`, `-`, and `#`, not top-level visibility words. The
hierarchy-protected `#` member visibility is visible in the declaring nominal
type and its nominal subclasses, not in arbitrary conforming or structurally
similar types. Public API residue records visibility exactly. The structural
Grammar accepts an omitted type-producing-owner visibility only for the
recovery path described above.

Annotations are structural attachments and must not float to a different declaration across recovery. Modifier sequences are closed by declaration owner. Duplicate or reordered modifiers that are not in the owner matrix are rejected.

## 7. Bindings, mutability, lazy values, and properties

`let` introduces an immutable binding; `var` introduces a mutable binding. A `var` cannot acquire lazy or guard semantics by decoration. Current lazy binding uses `let#lazy`, not `let@lazy`. Lazy initialization has one owner, one initialization result, deterministic failure caching policy, and no hidden repeated evaluation.

Rightward local binding is surface sugar, not a separate semantic statement:

```deeplus
loadConfig() -> $config: Config   // let config: Config = loadConfig()
openCounter() -> $$counter        // var counter = openCounter()
```

The CST preserves the arrow, `$`/`$$`, annotation, spans, and trivia. Before semantic checking, `$` normalizes to ordinary `let` and `$$` to ordinary `var`. The initializer is evaluated exactly once under the pre-binding environment; the fresh name is committed only after successful initialization. Type inference, coercion, ownership, borrow regions, effects, failure, cleanup, shadowing, and scope are exactly those of ordinary local binding. Only one fresh identifier target is admitted, only as a statement; chaining, pattern/place/member/index targets and guard attachment are rejected. No flow-binding AST/HIR/MIR/xVM/LLVM node exists. A `yield ... -> $x` still owns its suspension/resume event, then performs the same ordinary response binding after resume.

Properties use the exact `get` and `set(name)` accessor productions. An
optional member-visibility sigil attaches to each accessor, so `+get`, `-get`,
`#get` and the corresponding `set` forms are visibility-plus-accessor
compositions rather than independent role tags. `#beforeSet`, `#afterSet`, and
`do#get` have no current production. A getter may use the recommended `_`
result convention, but that spelling is not globally mandatory. Property
initialization and accessor visibility must preserve field ownership and
mutation responsibility.

## 8. Functions and declaration profiles

Functions and methods use `def`. The current closed profile families include ordinary functions and the admitted `#entry`, `#async`, `#pure`, `#guard`, `#mut`, `#consume`, and `#cleanup` combinations declared by the Frontend Model. A profile valid for one owner is not automatically valid for another.

The terminal valueless `return` is omitted canonically. Recursive functions are ordinary `def` declarations; no `#tailrec` callable kind exists, and tail-call optimization is an implementation choice below Deeplus MIR equivalence. A named function body is a block, explicit `= return Expr` shorthand, or declarative clause body; bare `= Expr` is not current named-function source. `ret` is not a synonym for `return`; it is limited to value-body/lambda/value-match ownership.

Function signatures preserve parameter order, labels, context/witness channels, rest channels, effect/error rows, ownership profiles, and return types. Return type alone never selects an overload. Source order never resolves an otherwise ambiguous overload.

An ordinary parameter is always a named parameter slot, optionally with an explicit ownership mode; it is not a refutable Pattern. Decomposition belongs in the function body or in an exhaustive declarative clause head. Local functions have lexical visibility only after their declaration and must list every captured outer local explicitly. Closure literals have their own capture descriptor, call-right (`ordinary`, `#mut`, or `#once`), lifetime (`#scoped` where required), effects, errors, and isolation responsibilities. Lambda parameter lists contain identifiers, not general Patterns. Named-function `return` and local lambda/value-body `ret` remain different control owners.

## 9. Parameter channels

Ordinary value parameters, explicit context parameters, explicit witness parameters, repeated positional parameters, and one named-rest parameter are distinct channels.

- A repeated positional parameter is written `values...: T`. Its body binding is sequence-like, but its public function-type residue remains `T...`.
- A named-rest parameter is written `options***: Record`. It must be unique and final, and its carrier is exactly the canonical structural `Record` with static labels.
- Repeated positional parameters precede the optional named-rest parameter.
- Primary constructors may additionally own stored `let`/`var` parameters under their admission policy.
- Lambda parameters use the dedicated lambda parameter list; canonical typed source is `{ x: Int => ... }`.

## 10. Normative named-rest and unfold split

This is a user-ratified constitutional surface decision and applies to every role and artifact.

```deeplus
public def configure(options***: Record) -> Unit = {
    apply(**options)
}

public type Configure = (Record***) -> Unit
```

The responsibilities are disjoint:

| Owner | Canonical surface | Meaning |
|---|---|---|
| parameter declaration | attached suffix `***` | collect remaining statically labeled named arguments |
| function-type item | attached suffix `***` | preserve the named-rest call-shape residue |
| call/materialization entry | attached prefix `**` | unfold a structural Record into static labels |

The following are rejected:

```deeplus
def bad(options**: Record) -> Unit = { }  // parameter/type owner requires ***
private type Bad = (Record**) -> Unit     // type residue requires ***
configure(***options)                     // unfold owner requires **
```

Parameter/type `**` is removed completely and no current profile admits it. No feature gate, formatter preference, or role-specific interpretation may restore `**` as a named-rest parameter/type suffix. The `**` glyph remains current only for named unfold and its independent operator role.

Named unfold requires a structural Record whose label set is statically known. A `Map` has runtime keys and cannot feed named arguments. Overlapping unfolded labels, missing required labels, or indeterminate label disjointness are checker errors.

## 11. Calls, labels, and callable compatibility

Ordinary calls use parentheses. A bare parenless ordinary call is not current except for the one exact trailing-closure CallSuffix: one atomic argument followed by exactly one closure. This exception does not admit a general bare argument list and does not relax capture, ownership, effect, error, or overload rules. Positional unfold and named unfold are checked in separate channels. Labels are static identity, not strings. A runtime key cannot be materialized into a compile-time argument label.

Overload preference is fixed-arity before repeated positional before named rest. A remaining tie is an error. Callable compatibility includes effect, error, ownership, isolation, context, witness, and rest-residue profiles; arity and return type alone are insufficient.

# Part III — Nominal, trait, conformance, and extension systems

## 12. Classes and the five relationship domains

Concrete classes are final by default. `open class` permits subclassing. `abstract class` cannot be directly instantiated. `sealed class` limits direct subclass declarations to the sealed family scope fixed by the module contract. Invalid combinations such as mutually exclusive flavor/modifier sequences are rejected by the class modifier matrix.

The language keeps five relationships distinct:

1. nominal subclassing;
2. Trait conformance;
3. extension membership and activation;
4. object containment/association;
5. dynamic or tooling-only views.

Subclassing does not automatically create an unrelated Trait conformance. Conformance evidence is explicit and has a stable origin. Sealed-family exhaustiveness is recursive over the complete current family, not merely direct children.

## 13. Members and dispatch markers

Stored fields are nonvirtual and carry no dispatch marker. Every class-like instance method carries exactly one class dispatch marker:

- `.` final slot;
- `+` open slot;
- `*.` override and close;
- `*+` override and remain open.

Trait method requirements use the Trait witness marker domain. Associated types, associated values, and associated non-method functions do not acquire a witness marker. Class dispatch and Trait witness markers may share glyphs but must lower to different AST domains.

No leading `~` appears on declarations such as `def load.()`. Tilde belongs to structured names and message syntax where the Grammar assigns it.

## 14. Traits, associated requirements, and conformance

Traits define behavioral contracts and associated requirements. `any Trait` is the explicit existential minimum core; existential packaging preserves required cleanup/drop responsibility. Associated projection uses `::`, and an optional suffix applies directly to the projection without redundant parentheses.

Conformance declarations supply evidence. Evidence selection is deterministic and coherence-safe. Extensions cannot silently manufacture witness evidence. Dynamic Trait attach/detach, local Witness values, and first-class Witness values remain nonactivatable design families unless separately promoted.

## 15. Extensions and member resolution

Extensions are statically identified sets. Activation is lexical/module scoped. A scoped group uses `use a, b in { ... }` or `import a, b in { ... }`; it creates one compile-time frame for the block, does not leak, and never becomes runtime loading. Extension members use plain `def` inside the extension set unless another owner explicitly requires a marker. Member identity includes the extension-set identity; import/source order is not a tie-breaker.

`+forward { name, age, city } to profile` expands to the listed forwarding declarations in source order. The list is finite and explicit; wildcard, rename, hidden witness creation, duplicate and collision are forbidden.

Resolution considers nominal members, active extension sets, and conformance evidence in the declared order. It never performs hidden runtime provider lookup to decide a static member.

## 16. Operator policy

The operator token vocabulary and precedence table are closed. Every current
glyph is selected by the Grammar and Frontend Model and dispatches as
`INTRINSIC_ONLY`. A conformance, extension, witness, provider, import, source
order, or runtime lookup cannot create a glyph candidate or change its meaning.
User-defined behavior is expressed through named Trait methods and named APIs.
Arbitrary custom operator declarations and fixed-operator Trait/conformance
overloading remain `PREVIEW_DESIGN` and nonactivatable; this current closure
neither activates them nor closes any of `TCC-P1-002..008`.

`subject is Alternative` and adjacent `subject !is Alternative` are current
only when the subject's static type is one normalized closed Union and
the right operand parses through the `TypeRef` goal and is exactly one declared
alternative identity of that Union. The subject is evaluated once; the checker
reads the stored Union injection
identity once and produces `Bool`. The true and false edges carry the exact
complementary alternative facts into `Phi`, but the expression binds no value.
It performs no subclass search, refinement evaluation, reflection, Trait or
provider lookup. A non-Union subject is rejected with
`TYPE_TEST_SUBJECT_MUST_BE_CLOSED_UNION`; a target that is not one exact
declared alternative is rejected with
`UNION_TYPE_TEST_ALTERNATIVE_NOT_EXACT`. Direct comparison chaining remains
forbidden and emits `COMPARISON_CHAIN_OPERATOR_NOT_IN_PHASE_A`. This structural
chain diagnostic precedes the subject-domain diagnostic, which in turn
precedes the exact-target diagnostic; a rejected chain does not continue into
speculative type-test diagnostics. Conversions remain `as?` and `as!`, and a
typed pattern is used when the selected value must be bound.

For `is`, the true edge intersects the current alternative set with the target
and the false edge removes it; `!is` swaps those results. `and then` supplies
the left true-edge fact to its right operand, while `otherwise` supplies the
left false-edge fact. Strict `and` and `or` do not pre-narrow their right
operand. A durable fact requires a stable place and is killed by assignment,
mutation through an alias, exclusive borrow, escape or capture with possible
mutation, consume, or a call whose responsibility summary may mutate or
consume the subject. These flow facts never rewrite the declared type.

Scalar `+`, `-`, `*`, `/`, and integer `%` require one exact normalized operand domain after the bounded contextual adaptation of an unsuffixed integer. Hidden widening, narrowing, mixed signedness, mixed width, and witness-based mixed-domain dispatch are forbidden. Integer division truncates toward zero. Integer remainder exists only for integer domains and satisfies `a == trunc(a / b) * b + (a % b)`; the remainder is zero or has the dividend sign and its magnitude is less than the divisor magnitude. A zero divisor and the signed `MIN / -1` or `MIN % -1` cases raise `ArithmeticDefect` before commit. Floating `%` and floating glyph power are not current; a library may expose explicit named APIs.

Spaced infix `^` admits one exact integer domain on both operands only when the checker proves the exponent nonnegative, returns that domain, and checks overflow. A negative or not-statically-proven-nonnegative exponent is rejected with `NUMERIC_OPERATOR_CORE_REQUIRED`; it does not create a dynamic failure route. `Measure<Rep, Dim> ^ StaticInt` delegates to the separate exact measure-power law. NumericArray infix power remains Preview, while `**` and `*+` delegate to their closed shape-specific intrinsic laws. Float arithmetic and comparison otherwise use the IEEE value law from §4; a NaN comparison is unordered, and `+0.0 == -0.0` is true. Equality, ordering, bitwise, membership, identity, cast, Boolean, Option-coalescing, and range tokens are admitted only by their current built-in laws and checker predicates; a similarly named Trait does not activate punctuation.

Strict Boolean `and` and `or` evaluate both operands left-to-right. Sequential `and then` and `otherwise` evaluate the right operand only when required. `not` is the sole Boolean negation spelling; a standalone `!` is not a Boolean prefix operator. `?:` preserves its separate lazy one-layer Option law.

Linear product is left-folded over the exact operator family `**` and `*+`; the current abstract shape is `PowerExpr` followed by zero or more operator/right-power pairs. Numeric exponentiation uses spaced infix `^` and is right-associative where its numeric law applies. Attached `A^` is NumericArray transpose. Mixed attachment is rejected rather than guessed.

`..` and `..<` are the only current range/slice delimiters. `...` has exactly the closed structural owners repeated positional parameter/type residue and `for ... Pattern in Expr` comprehension unfold; it is never a range delimiter or inferred upper bound. `..>` is reserved recovery and is rejected with `RANGE_OPERATOR_SPELLING_NOT_CURRENT`. A bounded List literal uses exactly `[L..U: elements]`, preserves its declared inclusive logical domain, and requires the element count to equal `U - L + 1`.

# Part IV — Expressions and control flow

## 17. Expression ownership and Pratt parsing

The Grammar declares expression/type/unit entry points and parselet ownership; the Frontend Model declares binding power and attachment. Parenthesized expression, unit, singleton tuple, tuple, and trailing-comma tuple share one prefix owner. Implementations must preserve delimiters and trivia in the lossless CST.

Expression evaluation order is deterministic and left-to-right except where a specific operator law states otherwise. Optimizations may not alter observable failure, cleanup, suspension, message, or provider order.

Assignment evaluates the target place once and then the right-hand expression once. Compound assignment evaluates that same place once, reads its original value once, evaluates the right operand once, completes the intrinsic operation, and performs at most one final write. Target, read, and right operand observations occur left-to-right. Any failure, including `ArithmeticDefect` or `IndexError`, before the final write preserves the original owner and value. `=`, `+=`, `-=`, `*=`, `/=`, and `%=` all produce `Unit`; no pre/post mutation value is synthesized.

## 18. Conditional, match, and value-control expressions

Statement `match` and value `@match` are distinct owners. `MatchExpr` is represented only by `@match`; no second ordinary expression spelling is current. Match subjects may be explicit or supplied only by a named InputSupply policy such as loop outcome or clause-function input.

An `@match` expression arm contains one expression result, or a block whose local `ret` supplies the arm result. Ordinary `return` exits the function and is not an arm result.

Conditions are exactly `Bool`; Deeplus has no truthiness conversion. A statement `try` owns either one or more `catch` clauses with an optional `finally`, or one `finally` clause. Bare `try` blocks and `try Expr` statements are not current. Value `@try` has the same nonempty handler/finalizer requirement, and value `@if` is total: omission of `else` is recovery-only. `catch` handles recoverable Error values and cannot absorb Defect or Cancellation.

The spaced conditional expression `condition ? whenTrue : whenFalse` evaluates
the Bool condition once and exactly one arm once. Its two arms must have the
same normalized result type or independently check against one already fixed
expected type; the checker does not synthesize an anonymous Union to make them
join. Ownership, places, effects, errors, cancellation, suspension, and cleanup
obligations join only when the resulting state is valid on both edges. MIR
therefore contains one condition branch, two lazy arm regions, and one explicit
responsibility join. A long or multiline form should use total `@if`, but that
style guidance does not change semantics.

A `catch` header admits only a binder, wildcard, or checker-proven
irrefutable transactional Pattern for the caught ErrorSet. It is not a runtime
pattern-dispatch list: a refutable variant, value, List, or guarded Pattern
cannot silently skip to the next `catch`. Once an irrefutable catch covers the
remaining declared ErrorSet, every later catch is unreachable. Refutable typed
multi-handler dispatch is not current and would require a separately admitted
closed ErrorSet partition. Defect and Cancellation remain outside every catch
partition.

## 19. Loops and structured transfer

`for`, `while`, and `repeat` follow their exact Grammar roots. Every admitting owner accepts at most one pure `if` or `!if` GuardClause. Guard chains are removed. A refutable `for let` first creates nonowning probe binders; the optional header guard may read those binders, but may not move, escape, suspend, mutate through, or acquire authority from them. Only a true guard commits final bindings and ownership. Pattern mismatch or a false guard skips exactly that candidate with no body event or component move. Structured break depth is expressed by repeated `break` words and the admitted continue form; label/depth aliases are not current unless explicitly listed.

The checker owns target depth, payload type, and cleanup order. A control transfer cannot skip required cleanup. Loop-outcome match receives its subject through InputSupply rather than an optional global grammar slot.

## 20. Declarative clause functions

Declarative clause functions partition a finite normalized subject domain.
Phase A admits the pattern carriers that have exact current productions and
context rows: Enum, Option, and Result variants; literal equality; and exact
closed-Union alternative binders. Sealed-Class constructor patterns and
scalar-interval patterns have no current production and are not inferred from
type closure or range expressions. Guards must be R0-pure and terminating.

The checker constructs a finite partition, intersects each source-ordered arm, rejects the first nonempty overlap, subtracts covered cells, lets one final `otherwise` cover the exact remainder, and rejects a nonempty remainder. Option, Result, and `throws` do not add implicit arms.

## 21. Laws, contracts, and assertions

`requires` and `ensures` describe callable contracts. Conformance `law` bodies admit only the restricted pure predicate assertion subset. Law bodies do not execute as ordinary MIR statements and cannot perform mutation, I/O, await, spawn, throw, or arbitrary calls. Tooling may attach property-generation evidence, but evidence absence does not change the current law text.

# Part V — Construction, data, and collection planes

## 22. Construction and primary constructors

Constructors use `def!`. Primary constructor lowering preserves stored parameters, initialization order, visibility, ownership, and failure cleanup. Constructor delegation uses the closed decision-list/guard model; target kind and selection are deterministic.

Generated data-class construction is a construction profile, not a runtime map conversion. Labels remain static. Constructor result and cleanup obligations are represented in MIR.

## 23. Records, maps, schemas, and materialization

Records have statically known labels. Maps have runtime keys. These domains are not interchangeable. A Map key is accessed by indexing or an explicit Map API; `.name` never projects the String key `"name"`.

- `**record` may unfold static labels into a call or materialization owner.
- `${ id, name }` and `source!{ id, name }` are same-name field puns; each binding is resolved lexically and evaluated exactly once.
- `**map` is rejected for named arguments.
- Schema materialization checks required labels, duplicate labels, unknown labels, type compatibility, and construction authority.
- Runtime strings cannot become static field labels.

Typed labeled materialization and schema unfolding must preserve the target construction row and projection row in public/API metadata.

## 24. Collections, comprehensions, and indexing

List, set, map, tuple, Record, String, Bytes, ReadonlyView, and NumericArray owners remain distinct. Comprehension iteration and filters preserve evaluation and failure order. The Stable `for ... Pattern in Expr` clause is a structural comprehension-unfold owner; it never forms a range. Async comprehension remains Preview-design. Collection behavior outside the closed built-in syntax owners uses named methods; conformance to `Sequence`, `Indexable`, or `LogicalIndexDomain` does not activate `[]`.

`#set{...}` constructs the current immutable `Set<T>` identity. All elements
must normalize to one exact element domain with the required equality and
keyability evidence. A duplicate literal element is rejected rather than
silently discarded. Membership is intrinsic over that exact domain, and Set
iteration order is not semantic or observable API residue. A Set
comprehension uses `SetComprehensionExpr`; it does not inherit List ordering or
Map key/value behavior.

A Map literal first builds one `MapLiteralPlan`. Its direct entries and
`**base` unfolds are evaluated exactly once in left-to-right source order.
Every unfolded base must have the same normalized key and value domains.
Within the plan a later occurrence of an equal key replaces the earlier value;
the displaced owner is cleaned exactly once. No hidden clone, key
stringification, widening, or conversion occurs. The selected `Keyable`
equality/hash contract is nonconsuming and synchronous and contributes
`throws Never effects {}`, no cancellation, and no authority; it therefore
cannot hide an additional failure channel. Construction is failure-atomic:
before final publication, a failed key/value or unfold evaluation—including
any Error, Defect, effect, cancellation, authority, ownership, or cleanup
responsibility declared by that expression—publishes no partial Map and cleans
acquired temporaries in reverse order. `**base` in a Map literal is therefore
a runtime immutable-map unfold and remains distinct from call-site `**record`,
which expands static labels.

The built-in default logical index domain of `List`, `String`, and `Bytes` is exactly `1..length`, and its storage projection is `index - 1`. Every `ReadonlyView` preserves its source owner's declared logical coordinates and provenance: a view of one of those ordinary owners is therefore one-based, while a view of a bounded or sliced owner retains that source domain and mapping. Index zero in a default one-based domain, a negative-from-end spelling, and an index greater than the applicable domain are never rewritten. Current bracket access yields a read-only value or borrow and never an assignable place; compound assignment applies only to independently admitted mutable places. `String[index]` selects one Unicode scalar and returns `Char`; it never selects a byte, UTF-16 code unit, or grapheme. `Bytes[index]` returns `UInt8`. A failed type-correct dynamic lookup raises `IndexError::outOfLogicalDomain`; a statically known invalid index is rejected by the corresponding exact diagnostic.

An explicitly bounded List `[L..U: elements]` preserves the declared `L..U` logical domain rather than rebasing to one. `Map<K,V>[key]` requires the exact normalized key type `K` and raises `IndexError::keyNotFound` for an absent key. Tuple elements use compile-time one-based `.1` ordinals, and Record fields use static labels; neither tuple nor Record admits runtime bracket indexing. A List literal without an expected element type infers one homogeneous normalized type and never synthesizes a Union. Under a fixed exact integer `List<T>` context, the sole prefix-sign exception is the direct `-` plus unsuffixed-integer-literal adapter from §4; all other element expressions use ordinary typing without hidden folding or conversion. Heterogeneous elements require an explicit expected type such as `List<Int | String>`.

Prefix/postfix `++` and `--` expressions do not exist. Mutation is written as an explicit assignment under the single-place transaction law in §17. NumericArray axes, suffix coordinates, and shape coordinates are separate typed domains. Each built-in default source-visible NumericArray axis nevertheless has the explicit domain `1..dimension`; its axis type is not supplied by an ordinary sequence witness. A complete rank-matching coordinate list selects one element. Wrong axis type/count is rejected statically, and a dynamic coordinate outside its axis domain raises `IndexError::outOfLogicalDomain`.

The obsolete legacy `#array{...}` constructor is completely removed; current NumericArray literals remain `#[...]` and rank-qualified `#N[...]`. `array` and `case` are ordinary identifiers with no special token, parser role, resolver namespace, checker intrinsic, or formatter rule. Deeplus supplies no predeclared or intrinsic `Array<T>` or `Case` type binding, but either spelling may be introduced by an ordinary user declaration and then resolves normally. There is no `case` declaration keyword. Enum alternatives remain variants identified by their declared name and nominal enum path. No Stable, Preview, Recovery, formatter, AST/HIR, or diagnostic path may reintroduce the removed legacy constructor.

## 25. Strings, interpolation, and rendering

Interpolation shorthand admits a read-only path rooted at the interpolation value and followed by admitted member/index selectors. Calls, mutation, await, assignment, and arbitrary operators require an explicit braced expression.

```deeplus
let text = "name=$user.profile.name"
let rendered = "value=${compute()}"
```

A path terminates at a delimiter or format boundary; a member dot that belongs to the path is not prematurely rejected. `String::render` is an explicit structured-value library helper with its own trailing renderer closure; it is not the hidden implementation hook for interpolation. Basic interpolation uses the selected `Display` evidence described below. Rendering must not become hidden locale/provider authority.

An interpolated String evaluates its direct segments and holes from left to
right. Each braced expression is evaluated once; each shorthand path evaluates
its root once and performs only admitted read-only projections. Before runtime
evaluation the checker selects one `Display` witness for every non-String hole.
Rendering borrows the value, is synchronous and nonconsuming, declares
`throws Never effects {}`, and produces one fresh String segment. No locale,
serialization, parsing, provider, reflection, redaction, or authority lookup is
implicit. `Secret` or `Redacted` values must first pass through an explicit
redaction API. Failure while evaluating a braced expression occurs before the
final String is published and cleans temporary segments in reverse order.

The scanner preserves the text after the colon in `${expr:format}`, but the
internal format-text grammar, its mapping to a rendering argument, width unit,
padding and truncation behavior, and invalid-format outcome are not yet
ratified. That format-spec core remains `DEFERRED_PRODUCT_HANDOFF`.
Implementations must not borrow another language's format mini-language,
silently ignore the text, or infer locale/provider authority. A hole without a
colon follows the closed `Display` plan above.

## 26. NumericArray

NumericArray has explicit shape, rank, orientation, element type, and coordinate laws. Attached postfix `^` transposes under its admitted shape law. Infix `^` is power and requires the spacing/attachment boundary. Elementwise power remains Preview unless its broadcast and result-shape law is activated by the current profile.

Stable postfix transpose evaluates its NumericArray operand once and returns a
semantic nonowning, owner-bounded read-only coordinate view; it authorizes no
implicit element copy, language-observable allocation, mutation, or inferred
shareability. For an abstract rank-two shape tuple `(R,C)` the result shape
tuple is `(C,R)` and the logical coordinate projection is `(i,j) -> (j,i)`.
A rank-one value
requires an explicit row or column orientation witness and flips that
orientation. The view preserves the element owner, logical one-based
coordinates, provenance, effects, and lifetime and cannot outlive or cross the
isolation boundary of its source. Backend representation and incidental
storage strategy remain unselected. Transpose is not complex adjoint.

Broadcasting, fill/repeat, slicing, and matrix-like operations must produce deterministic shape diagnostics. NumericArray coordinate domains are not ordinary labels or runtime map keys.

Current range slicing is admitted only for the closed built-in slice carriers. `List`, `String`, `Bytes`, and `ReadonlyView` accept exactly one bounded range axis; semicolon-separated multi-axis selection and the full-axis `*` wildcard are NumericArray-only. `MutableList`, `FrozenList`, and `ListSnapshot` are outside this closed bracket matrix and do not acquire `[]` from a family resemblance or Trait conformance. An axis range is canonical inclusive `i..j` or explicit exclusive-end `i..<j`. `^` and `$` are slice-only first/last anchors. Empty `[]`, omitted range bounds, descending ranges, and step syntax are not current. The half-open spelling is accepted but reports `SLICE_HALF_OPEN_RANGE_NONCANONICAL`; canonical source uses inclusive bounds.

A slice result is a read-only owner-bounded view that preserves the selected source logical coordinates and owner provenance. It does not implicitly rebase, copy, become mutable, cross isolation, or outlive its source. Mutable slice assignment is forbidden. Code requiring coordinates beginning at one or independent ownership must call an explicit named rebase/copy operation whose cost and ownership transfer are visible.

## 27. Bitfield and flags

Bitfield declarations use unsigned strict layout. `#flags` supplies the finite-universe flags specialization. Unknown bits, duplicate masks, width overflow, signed ambiguity, and layout mismatch are rejected. Public layout digest tooling records width, masks, endianness/layout policy, and feature identity without claiming runtime implementation.

## 28. Measures and units

Measure types preserve dimension and exact-ratio conversions. Unit product and quotient use the current unit operator owners. Calendar units are a `STDLIB_PROFILE`: month/year conversions require an explicit calendar/provider context and are never implicit core exact-ratio conversions. The same source and activation profile must have one outcome.

# Part VI — Type system and responsibility

## 29. Judgments, normalization, and identity

Type checking normalizes aliases, optional layers, unions/intersections, associated projections, rows, ownership modes, effects, errors, cancellation, labels, measures, and witness identities before comparing types. Normalization must terminate, perform an occurs check, and must not erase responsibility-bearing distinctions. Inference is bidirectional and local; it does not invent implicit generics, anonymous unions, hidden authorities, or a runtime type test.

The core judgments cover well-formedness, expression typing, subtyping, conformance evidence, call-shape admission, ownership/place access, effect/error rows, construction, pattern coverage, and MIR handoff.

## 30. Nominal types, generics, and variance

Nominal class identity is distinct from structural Record identity and Trait evidence. Generic parameters range over the closed current kind family: type, `StaticInt`, `EffectRow`, and `ErrorSet`; rows and labels remain checker identities rather than additional user generic kinds. Generic constructors are invariant by default. Declared variance is restricted to the currently admitted Trait/type parameter positions and cannot invalidate ownership or mutation safety.

Inference must not use hidden runtime values, result type alone, or source-order tie-breaking. Unsatisfied or ambiguous constraints produce deterministic diagnostics.

Phase-A generic inference creates fresh variables only for the parameters
declared by the selected generic owner. It gathers constraints from explicit
value arguments in left-to-right source order, normalizes them, performs the
occurs and kind checks, and requires one unique substitution. A fixed expected
result type may verify that substitution after argument solving; it cannot
choose an overload or become the sole source of an otherwise unconstrained
parameter. The checker then applies `where` constraints and selects explicit
conformance evidence. `StaticInt`, `EffectRow`, and `ErrorSet` parameters must
be supplied explicitly unless the preceding argument constraints determine one
exact normalized value. No unresolved variable is generalized, replaced by an
anonymous Union, or guessed from source order.

## 31. Union, intersection, Option, and Result

Anonymous unions are closed alternatives. Contract intersections combine compatible obligations. Option represents presence/absence; Result represents success/failure. A Result use always spells its error-channel argument as `Result<T, error E>`; the generic declaration may name `E: ErrorSet` without repeating the use-site role marker. Compact optional suffix denotes one layer. `?:` is the Option-coalescing operator and does not silently consume Result/error effects.

Union injection must select a unique admissible alternative after normalization. Intersection construction must satisfy every constituent responsibility. Exhaustiveness covers all explicit alternatives; no implicit catch-all is supplied.

## 32. Function types and call-shape residue

Function types include parameter channels, callable profile, ownership, effect/error rows, isolation, and return type. Repeated positional residue is written `T...`. Named-rest residue is written `Record***`. Public module API digests preserve these exact residues; erasing them to `Sequence<T>`, plain `Record`, `Map`, a count, or omission is invalid.

Call compatibility checks each channel independently and then checks the combined responsibility profile. A function accepting named rest is not equivalent to a function accepting a Map.

Call admission first resolves one declaration identity without consulting the
return type. It then partitions actual arguments into positional, labeled,
repeated positional, named unfold, explicit `context`, and explicit `using`
evidence channels. Each ordinary actual is evaluated once from left to right;
`*expr` can supply only a statically known tuple or the admitted `Sequence`
residue and cannot satisfy fixed parameters when its arity is unknown.
`context expr` supplies one declared context parameter and never performs an
ambient lookup. `using evidence` supplies checker-visible, borrowed,
nonescaping conformance evidence and cannot be replaced with an ordinary
runtime value. Only after every channel, generic substitution, ownership mode,
effect row, error set, isolation profile, and return obligation agrees is the
call committed.

## 33. Ownership, borrowing, move, inout, and cleanup

Values may carry move, borrow, inout, resource, isolation, and cleanup responsibilities. Borrowed values must not escape their admitted region. Inout requires exclusive mutable access. Move invalidates the source place according to the place-typing model.

For an ordinary parameter, `mut name: T` creates a callee-owned mutable local
place. The argument is acquired once; an affine owner moves into that place,
the caller receives no write-back alias, and cleanup remains with the callee.
This differs from `inout`, which borrows one caller place exclusively and
commits observable writes back to that same place, and from explicit `move`,
which emphasizes transfer without itself granting mutation. A `mut T` type
qualifier denotes a unique mutable owner/view responsibility and is never an
alternate spelling for an `inout` channel.

Closure capture is independent from callable multiplicity. `borrow` captures a
nonescaping shared observation, `inout` captures one exclusive nonescaping
place, and `move` transfers the owner into the environment. `copy` requires
the admitted bit/value-copy responsibility and leaves the source valid;
`clone` invokes one explicit `Clone` witness and therefore retains that
witness's declared effects and errors; `deep` requires a distinct deep-copy
profile rather than recursively guessing cloneability. Capture `once` transfers
an owner and makes reading that environment field a one-shot operation; it
does not by itself turn a reusable closure into a `#once` callable. Capture
acquisition is left-to-right and failure-atomic: before environment commit,
acquired temporaries are cleaned in reverse order and no partial closure
escapes.

`defer` captures one admitted invocation and executes exactly once in deterministic LIFO cleanup order. Trailing closures, arbitrary inline callable construction, await, spawn, guards, and blocks are not silently converted into defer invocations. Cleanup during failure, cancellation, and normal return follows the cleanup budget algebra.

Facet borrow packaging is current. Owned and inout Facet packages remain Preview-design until escape, alias, cleanup, and ABI laws close.

## 34. Effects, errors, defects, and cancellation

Effect rows and error sets use visible union structure. Errors, defects,
cancellation, suspension, and isolation are distinct axes. Cancellation is
never an ErrorSet member, and suspension is never hidden in an EffectRow.

`capability Name for EffectRow` declares one nominal, non-value capability
identity and binds it to one normalized nonempty effect row. The declaration
does not perform an effect, create a global value, grant authority, or make a
Trait conformance. A callable that needs the permission carries the capability
through an explicit `context` parameter and still declares its observable
`effects` row; the two axes are checked independently. Capability declarations
end at `StatementBoundary`, obey top-level visibility, and cannot be
constructed, forged, or inferred from an effect name.

`#pure` forbids observable effect and hidden authority. `#guard` is a
terminating, nonsuspending, nonconsuming pure Bool predicate profile. Failure
propagation and primary/suppressed ordering are deterministic.

Cancellation must not bypass cleanup. Async failure aggregation preserves the declared primary and suppressed ordering in MIR.

## 35. Patterns and exhaustiveness

One lossless Pattern CST and one normalized Pattern AST are shared by every admitting owner; a context-policy row, not a second semantic grammar, decides refutability, guard admission, failure disposition, and exhaustiveness. Plain `let`/`var`, bare `for`, and ordinary callable parameters are irrefutable owners. Guarded `let`, statement `if let`/`while let`/`for let`, and `match` are refutable owners. Callable clause heads may be refutable only when their declared clause family is statically disjoint and exhaustive. Enum cases use `::case` or `Type::case`; dot-case shorthand is removed. A local `BindingPattern` owns its optional whole-pattern type annotation once and excludes a second top-level typed-binder derivation; recursive child patterns retain `Identifier : TypeRef`. The Binding owner carries that whole-pattern annotation through normalized AST and HIR in the nullable `binding_owner_expected_subject_type` field. This field constrains the independently evaluated subject before Pattern admission and never creates a runtime type-test Pattern node. Typed-pattern colon ownership never collides with a parameter type annotation because ordinary parameters contain an Identifier rather than a Pattern.

Every refutable owner follows one phase order: evaluate the subject once; acquire its place/owner; build and execute a nonconsuming structural TestPlan; expose nonowning probe binders; evaluate zero or one terminating pure Bool guard; atomically commit moves/borrows/bindings; expose final binders; run the body; then perform the owner-specific exit or join. A failed structural test or guard performs no component move, irreversible borrow, authority acquisition, escape, suspension, or partial binding. Mismatch disposition belongs to the context: skip a loop candidate, choose the next match arm or clause, take the false branch, or emit the irrefutability diagnostic.

The current destructuring carriers are nominal variant payloads, statically known Record labels, and List. Record patterns require a statically known label subset and do not contribute an open-tail/rest fact to coverage. List patterns are exact-length or end in one ignored final `.._`; captured, middle, and multiple rests are not current. Tuple-pattern syntax is not current. An Or-pattern requires identical observable binders with the same canonical types, ownership modes, mutability, and regions on every branch; path/source order is not identity. `pattern as name` creates a borrow alias rather than a clone, and it cannot coexist with a moved or exclusive descendant. Cross-arm place joins preserve only capabilities valid on every incoming arm.

Ordinary `match` chooses the first admitted arm in source order after structural admission and its optional guard; source order never repairs overlap in a declarative callable-clause family. Option, Result, union, enum, List exactness, Record required-label subsets, and loop outcome each use their explicit current alternatives. Sealed-Class closure may inform subtype analysis but supplies no constructor-pattern syntax. An undecidable or incomplete partition is rejected rather than assumed exhaustive. Pattern opening does not directly inspect Class, Dyn, Facet, FFI, or user-defined extractor internals, and it never performs backtracking.

`Identifier : TypeRef` remains an irrefutable static typed binder except in a refutable owner over an already normalized closed Union. There, and only when `TypeRef` is exactly one declared alternative identity, the checker elaborates it to a union-alternative binder and tests the Union's stored injection identity. This bounded discriminator read is not a general runtime type test: it performs no subtyping search, refinement execution, reflection, provider lookup, or Trait discovery.

The checker maintains a flow-proof environment `Phi` separately from each binding's declared semantic type. A successful structural pattern intersects `Phi` with its exact enum case or union alternative; an inline admitted R0 guard may add finite facts on its true edge. Ordinary Bool calls, including calls to `def#guard`, add no narrowing fact. Joins retain only facts present on every incoming edge, and assignment, aliasing mutation, exclusive borrow, escape, capture, consume, or a call permitted to mutate the subject kills affected facts.

Usefulness and exhaustiveness are one ordered finite-partition pass. An arm with no new structural cell is `MATCH_ARM_UNREACHABLE`. A guard is checked for usefulness but never subtracts coverage; a witness left only because all covering arms are guarded is `MATCH_NONEXHAUSTIVE_AFTER_GUARDS`. `otherwise` after an empty residual is `OTHERWISE_UNREACHABLE`; any other final residual is `MATCH_NOT_EXHAUSTIVE`.

Enum pattern admission resolves the `VariantId` in the scrutinee's Enum owner and checks the active payload arity, labels or positions, and child-pattern types before any guard or ownership commit. A foreign or unknown case and any inactive-payload projection reject at that boundary. Or-pattern alternatives must bind identical names, canonical types, modes, mutability, usable lifetimes, and capabilities; projection paths may differ. Structural failure and false guards commit no binding, move, exclusive borrow, or authority.

## 36. RCTS-V5 and dynamic boundary

RCTS-V5 is the closed design descriptor family for checker/reference handoff. It records source kind, normalized type, call shape, ownership, effects, errors, cancellation, labels, shape/rank/orientation, evidence, and MIR responsibility as required by each predicate. Static validator PASS is design-static evidence only.

Dyn-RCTS remains `PREVIEW_DESIGN` and nonactivatable. Dynamic inspection cannot manufacture a static type, label, conformance, or authority. Any future activation requires a closed runtime representation, type-erasure law, cast/failure model, MIR events, and independent product evidence.

# Part VII — Async, actors, metaprogramming, and external boundaries

## 37. Async functions, tasks, and suspension

Current async declarations use the admitted `def#async` owner. Await is explicit. Task spawning through `~ spawn` has one syntax owner: the ordinary MessageSuffix shape, with HIR deciding the reserved spawn selector semantics. A second TaskSpawnSuffix owner is forbidden.

Every current task belongs to a lexical structured scope. A scope records parent task, child-set, cancellation state, failure order, and cleanup obligations; it cannot return until admitted children reach a terminal state and required cleanup completes. Deeplus has no detached-task authority. Cancellation is an explicit control axis and terminal task outcome, never an Error value. Delivery is monotonic and idempotent, cleanup cannot be bypassed, and a later secondary failure is retained in deterministic suppressed order rather than replacing the primary outcome.

Suspension points preserve borrow/ownership rules, cleanup obligations, actor isolation, cancellation responsibility, and failure ordering. A borrow or probe binding may cross suspension only when its region and isolation proof explicitly permit it. Async callable literals and async comprehensions remain Preview-design.

## 38. Actors and messages

An actor owns one isolated mutable state region and one mailbox. Exactly one admitted message turn mutates that state at a time. An actor turn is non-reentrant across `await`: while the turn is suspended, another message may be accepted into the mailbox but cannot observe or mutate the actor state until the suspended turn terminates. A request await whose statically proven dependency cycle requires that same active turn to progress is rejected; the checker does not add reentrancy or release actor authority to break the cycle. Message send is an asynchronous transfer operation, not an ordinary method call. An omitted mailbox clause selects `logical_unbounded_v1`, which has no language-level capacity rejection. `#mailbox(capacity: N)` requires a positive static integer and selects `bounded_reject_v1`: a full mailbox rejects immediately without blocking, retrying, suspending, or dropping. Because the intended bound is semantic input, diagnostics never guess or synthesize `N`; the programmer chooses the positive `StaticInt` value.

`ActorMessageError` is the closed current error family `{ mailboxFull, receiverClosedBeforeAdmission, receiverClosedBeforeReply }`. A one-way message expression has exact type `Result<Unit, error ActorMessageError>`. A request for reply type `T` has exact immediate type `Result<Task<T>, error ActorMessageError>`; source extracts the admitted task and only then applies `await`. Only that successfully admitted actor-request `Task<T>` spelling is accompanied in typed HIR, module API digest, and MIR by a non-forgeable `TaskResponsibility` descriptor containing the normalized result type, exact handler ErrorSet, cancellation axis, isolation owner, request correlation identity, and terminal transport failure; an ordinary async `Task<T>` carries no actor transport descriptor. The module API digest records the static `correlation_id = per_value_non_forgeable` policy marker rather than a concrete runtime identity; each committed request obtains its distinct value-level correlation identity in typed HIR/MIR. Consequently awaiting a request declared `throws E` exposes exactly normalized `E | ActorMessageError::receiverClosedBeforeReply`; the error set is not erased merely because it is not a second visible `Task` type parameter. `mailboxFull` and `receiverClosedBeforeAdmission` are precommit admission errors. If the receiver closes after an admitted request but before reply, that task terminates through its declared `ActorMessageError::receiverClosedBeforeReply` failure axis. Cancellation is never converted into this error family.

The current asynchronous sequence profile is `AsyncSequence<T, E: ErrorSet>`. Its `next` channel throws the bound source failure set `E`; cancellation is a separate control outcome. `AsyncCollector::list<T, U, ES, ET>` accepts a finite `AsyncSequence<T, ES>` and a named asynchronous transform that throws `ET`, and the collection call exposes exactly the normalized error-set union `throws ES | ET`. It cannot erase either failure channel or fold cancellation into that union.

The current ordering guarantee is FIFO only for successfully committed messages with the same exact `(sender identity, receiver actor identity, admitted mailbox profile identity)` key. Commit transfers each moved owner exactly once and allocates the next `channel_sequence`; a rejected attempt retains every moved owner and has no sequence. There is no global ordering, fairness, exactly-once delivery, distributed delivery, or session guarantee. Cancellation observed before commit aborts without transfer; cancellation after commit does not retract the actor-owned payload or rewrite an already returned admission result. Actor handlers cannot leak isolated references, synthesize reply authority, or convert Cancellation/Defect into a recoverable Error. Cross-actor waiting must preserve structured task ownership and cannot form an implicit detached cycle. Product lanes remain `15/15_NOT_RUN` until the target-execution gate has receipts.

Shared mutable state is admitted only through an explicit stdlib profile. `SharedCell<T>` requires normalized Plain payload and supplies sequentially consistent `withValue` scoped observation and `replace` owner exchange. The observation cannot escape or suspend; replacement commits once and returns the old owner. Plain does not imply byte-copy, raw layout, lock-free implementation, or a progress guarantee, and no weaker-order source surface exists. `SharedMutex<T>` supplies receiver-bound, non-reentrant, non-suspending scoped exclusive mutation; unlock executes exactly once on return, Error, Defect, or Cancellation and happens-before the next successful lock on that mutex. Neither profile infers poisoning, fairness, lock ordering, transferability, or erasure of effects, cancellation, isolation, or cleanup.

## 39. Compiler tree boundary

Source AST quote and logic-variable surfaces are completely removed. `@ast`, its mode spellings, attached `^{...}`, and attached `?Identifier` have no Stable, Preview, Recovery, no-go, formatter, AST/HIR, or MIR identity. This removal does not affect the compiler's internal Rust lossless CST, AST, typed HIR, or Deeplus MIR pipeline. The infix/postfix `^` and spaced ternary `?` keep only their independently declared current owners.

## 40. FFI, unsafe, and quarantine boundary

The proposed `@scope#dynamic` / `@scope#unsafe` quarantine family is retained only as nonactivatable Preview-design and a Recovery recognition probe. Its minimum sound profile requires typed immutable export, forbids outer mutation, suspension and every pointer/authority/borrow/resource/closure/task/actor escape, and preserves one Deeplus MIR meaning across xVM and LLVM. Source activation waits for provenance, authority, escape and backend-equivalence proof.

FFI/unsafe/native interop remains Preview. Foreign ABI, layout, provenance, callbacks, variadics, unwind behavior, ownership transfer, and cleanup must be explicit before promotion. No current Stable design implies that the LLVM backend alone makes an FFI sound.

# Part VIII — MIR, xVM, LLVM, Prelude, and profiles

## 41. Canonical implementation architecture

The implementation architecture is fixed:

```text
Deeplus source
  -> Rust scanner / handwritten recursive-descent + Pratt parser / lossless CST
  -> Rust AST, HIR, name/type/responsibility checker
  -> Deeplus MIR (canonical Deeplus semantic authority)
  -> Rust xVM bytecode + xVM interpreter for initial development, validation, and REPL
  -> LLVM AOT for the initial native backend
  -> LLVM ORC JIT for later high-performance execution
```

Rust source, xVM bytecode, and LLVM IR are not semantic authorities. Every backend must preserve MIR-observable evaluation order, failure, cleanup, suspension, message, provider, ownership, and result behavior.

## 42. MIR handoff

MIR represents normalized call channels, construction, witness calls, extension resolution, ownership/place operations, cleanup regions, effects/errors, match partitions, async suspension, actor messages, measures, NumericArray operations, and RCTS responsibility events. Surface sugar must be gone or explicitly represented by a responsibility-bearing MIR node.

Named rest lowers with `***` declaration/type residue identity; named unfold lowers from `**record`. The lowered call shape must retain static labels and must never convert runtime Map keys into labels.

## 43. Prelude and standard library

Prelude supplies canonical identities for primitive numbers, `Bool`, `Char`, `String`, bytes, collections, `Record`, Option, Result, iterator protocols, callable/protocol surfaces, measures, and fixed operator contracts. Prelude names are not hard keywords unless the lexical authority says so.

Public Prelude signatures use current syntax, including `Record***` function-type residue where named rest is present. Calendar support belongs to an explicit stdlib/provider profile. Prelude and stdlib artifacts do not claim implementation until target receipts exist.

## 44. Tooling profiles

Formatter/LSP, module API digests, schema validators, conformance corpora, UML export, and design galleries are separate evidence/tooling planes. UML OCL subset, component/deployment mapping, and sequence/activity test generation are `OFFICIAL_TOOLING`; they do not add core language syntax.

The formatter must preserve semantics and normalize only declared conventions. It prints attached `#word`, preserves the `***` named-rest/type suffix and `**` unfold prefix, and never rewrites one owner into the other.


## 44.1 Bounded tooling and library promotions in R51f3

R51f3 promotes four narrowly owned contracts without claiming product execution:

- `xvm_agent_framework` is OFFICIAL_TOOLING. It consumes immutable MIR/bytecode digests and emits evidence; it cannot alter semantics or authority.
- `tail_call_analysis_tooling` is OFFICIAL_TOOLING. Tail position and optimization refusal are MIR/backend evidence, never a source callable kind.
- `pattern_engine_library_profile` is a STDLIB_PROFILE over explicit `String`/`Bytes` calls with engine/version, flags, failure type, Unicode mode and resource budget. It adds no literal syntax or scanner mode.
- `uml_state_machine_provider` is OFFICIAL_TOOLING. It emits traced ordinary Deeplus source/tests that the Rust frontend rechecks; it injects no runtime or MIR semantics.

The exact minimum contracts and negative boundaries are in the tooling/profile contract artifact. Every related product lane remains `NOT_RUN`.

`session_protocol_lite_provider`, fixed operator conformance overloading, generic extension-set targets and sealed multimethods remain Preview design. The current actor admission contract is design-closed, but actor parser/checker/MIR/xVM execution remains `NOT_RUN`; no product promotion follows from the static contract.

## 45. Preview and noncurrent boundaries

Five families are removed without a compatibility gate: Map String-key dot projection, increment/decrement expressions, the `#tailrec` callable kind, regex literals, and automatic heterogeneous-List Union inference. Their current replacements are explicit Map indexing or APIs, explicit assignment, ordinary recursive functions, explicit pattern-library construction from String/Bytes, and an explicit expected `List<A | B>` type. No removed family has a feature row, Preview gate, scanner mode, special AST/HIR/MIR node, or callable residue. Rejected examples exist only to pin diagnostics.

The following families remain Preview or Preview-design unless their feature row explicitly says otherwise: dynamic/unsafe quarantine scope, FFI, NumericArray elementwise power, owned/inout Facet packaging, async callable/comprehension, dynamic Trait state, local/first-class Witness values, specialization, weak atomics, solver-backed general refinements, arbitrary custom operators, static activation, Dyn-RCTS, and fixed operator conformance overloading.

Removed surfaces have no implicit compatibility entitlement because Deeplus has not yet had a public 0.3.x release. Recovery recognition is permitted only where the Recovery profile and active diagnostic explicitly require it. Recovery syntax never becomes current AST or MIR.

# Part IX — Exact Grammar authority and conformance

## 46. Exact Grammar incorporation

The exact syntax authority is `spec/grammar/deeplus.ebnf`. This specification
does not duplicate EBNF productions. `docs/grammar-reference` is a
generated-and-validated reader projection, not a second syntax authority. The
Grammar is an inseparable normative component of the R51f3 package and
contains four profiles:

- LEXICAL: scanner-level structure and external scanner contracts;
- STABLE: current source reachable from the declared Deeplus roots;
- PREVIEW: source admitted only by an explicit current feature gate;
- RECOVERY: diagnostic recognition only, never current AST/MIR admission.

The Frontend Model supplies the owner policies that EBNF deliberately delegates: Pratt binding, contextual words, exact introducer attachment, input supply, role admission, token/trivia boundary, CST/AST/HIR/MIR responsibility, and formatter convention. An implementation must consume both files with this specification.

## 47. Required current Grammar invariants

- Every Stable production is reachable from a declared Stable root or an explicitly declared parser entry.
- No current production has an undefined nonterminal except the declared external scanner/Pratt contracts.
- Parameter `***`, function-type residue `***`, and unfold `**` have distinct owners.
- `***` has no expression/unfold role.
- `**` has no named-rest parameter/type role.
- Source roots consume EOF.
- `@match` is the only MatchExpr surface.
- The obsolete legacy `#array{...}` constructor has no lexical, Stable, Preview, Recovery, diagnostic, example, or migration identity; current `#[...]` and `#N[...]` NumericArray literals are distinct.
- Class and Trait marker domains lower separately.
- Law bodies do not contain ordinary statements.
- Source AST quotes and attached logic variables have no production.
- Regex literals have no token, scanner mode, production, or literal AST kind.
- The callable profile table contains no tail-recursion kind.
- Every guard owner admits at most one GuardClause; GuardChain has no production.
- Ordinary callable parameters contain identifiers rather than refutable Patterns.
- List patterns are exact or end in one ignored `.._`; tuple patterns, captured rests, middle rests, and Record rest patterns have no current production.
- `array` and `case` are ordinary identifiers with no special token, declaration keyword, predeclared/intrinsic nominal-type binding, parser, checker, or formatter owner; ordinary user declarations of those spellings resolve normally.
- Statement `try` and value `@try` each own at least one catch or one finally; `try Expr` is not current.
- Value `@if` is total after recovery and every condition has type Bool.
- Multiline String, grouped forwarding, scoped activation groups, enum comma cases, field puns, and pattern-binding controls are root-connected Stable syntax.
- Quarantine scope appears only under RecoverySyntax and is nonactivatable Preview-design.

## 48. Example and conformance status

The Example Review Corpus is exhaustive design-static review material. Accepted and rejected outcomes are normative expectations, but all parser/checker fields remain `not_run` until a target Rust implementation executes them. Hash parity proves that manifests identify the shown code; it does not prove language execution.

Publication closure requires canonical hashes, ID parity, grammar closure, current diagnostic references, example block parity, no contradictory outcomes for identical source/profile, and honest `NOT_RUN` product lanes.

# Part X — Implementation and review responsibilities

## 49. Scanner, parser, and lossless CST obligations

The Rust scanner must preserve enough span and trivia information for a lossless CST and deterministic diagnostics. It tokenizes the longest admitted glyph, but it does not decide semantic admission. In particular, it may produce `TRIPLE_STAR` and `DOUBLE_STAR`; the parser owner decides whether that token is attached to a parameter, a function-type item, a call/materialization entry, or is an infix operator. Splitting `***` into `**` plus `*`, or reconstructing it from separated tokens, is forbidden.

The handwritten recursive-descent parser owns declaration and statement structure. A Pratt parser owns the expression precedence table declared by the Frontend Model. Neither parser may use type information to repair an otherwise ambiguous token stream. Stable, Preview, and Recovery entry points are distinct. Recovery nodes retain the offending spelling and diagnostic, but never masquerade as current Stable AST.

For the named-rest family, the parser must implement all four cells below rather than a single glyph substitution:

| Owner | Accepted | Rejected | Required recovery result |
|---|---|---|---|
| final named-rest parameter | `options***: Record` | `options**: Record` | retain source span, emit `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`, build no current parameter node |
| function-type named residue | `Record***` | `Record**` | retain source span, emit the same removal diagnostic, build no current type residue |
| call/materialization named unfold | `**options` | `***options` | emit `TRIPLE_STAR_ONLY_FOR_NAMED_REST_PARAMETER_OR_TYPE_RESIDUE`, build no current unfold node |
| linear product expression | spaced infix `a ** b` | owner-invalid attachment | follow expression/operator diagnostics, not the named-rest fix-it |

The CST must keep these owners distinguishable even if a downstream AST normalizes punctuation. Source roots must consume EOF, and a parser receipt must identify the exact Grammar hash, feature profile, source role, and input bytes.

## 50. AST, HIR, resolver, and checker obligations

AST construction removes recovery-only forms. HIR assigns static identities to modules, declarations, members, labels, associated items, witnesses, extensions, and entry candidates. Resolution must not convert runtime strings into any of those identities. The resolver records the selected evidence origin so that module API digests and MIR lowering do not repeat an unstable lookup.

The checker evaluates callable channels in this order: ordinary parameters, repeated positional residue, named-rest residue, ownership/place requirements, effect/error rows, isolation/context, and return compatibility. It then applies overload specificity. Named unfold first proves a structural Record with a statically known label row; it then contributes each label once. Duplicate or possibly overlapping labels are rejected before body lowering. A `Map` cannot pass this proof because its key set is a runtime value.

Function-type compatibility preserves `T...` and `Record***` as different residues. It must not erase either residue to a collection carrier. A public API digest records the residue, parameter label policy, effects, errors, ownership, and witness/extension requirements. Two digests that differ in any responsibility-bearing field are not equal merely because their machine ABI could be made identical.

## 51. MIR and backend preservation checklist

Deeplus MIR is the canonical semantic handoff. Each accepted source construct must lower once into an explicit MIR operation or into a documented desugaring whose observable order is fixed. MIR carries evaluation sequence, static label rows, selected conformance or extension evidence, ownership/place transitions, cleanup regions, effect/error edges, cancellation, actor/message responsibility, provider identity, and source provenance needed for diagnostics.

The named-rest declaration and `Record***` function-type residue lower to a named-rest call-shape channel. The `**record` unfold expression lowers to label-row expansion in source evaluation order. It does not lower to iteration over map entries, and it cannot invent or reorder labels. `***` has no unfold MIR node; parameter/type `**` has no current MIR node.

The xVM bytecode interpreter is the first executable oracle for development, validation, and REPL behavior, but it remains an implementation of MIR. LLVM AOT is the first native backend and LLVM ORC JIT is the later high-performance path. Backend optimization may erase representation details only after proving preservation of MIR-visible behavior. A passing design validator is not evidence that any of these products parsed, checked, lowered, or ran the feature.

## 52. Formatter, LSP, documentation, and API obligations

The formatter is syntax-aware and owner-aware. It prints named-rest parameters as `name***: Record`, function-type residue as `Record***`, and named unfold as `**value`. It must never offer a preference or compatibility setting that prints parameter/type `**`. It may issue a safe fix from removed parameter/type `**` to `***` only after the parser has identified that owner; a blind text replacement would corrupt legitimate unfold and linear-product expressions.

The LSP shares parser/checker identities. Completion for a final named-rest parameter inserts `***`; signature help displays `Record***`; unfold completion inserts `**`; hover text names the owner rather than calling both forms “spread.” Rename and formatting preserve static labels. Diagnostics expose the primary ID, exact span, owner-sensitive fix, and current profile.

Language guides, design galleries, examples, Prelude signatures, code actions, snippets, and generated API documentation must follow the same surface. Any role report that proposes named-rest parameter/type `**` conflicts with current law and must be rejected or rewritten before integration.

## 53. Test corpus and receipt requirements

Every feature family has positive, negative, boundary, and mutation evidence. For the named-rest split, the minimum deterministic set contains accepted parameter `***`, accepted type residue `Record***`, accepted unfold `**record`, rejected parameter `**`, rejected type residue `Record**`, and rejected unfold `***record`. Tests must also distinguish a spaced infix `**` expression so that an owner-insensitive ban cannot pass.

A design-static fixture states an expected outcome and checks registry/schema consistency. A parser receipt requires actual Rust parser execution over identified source bytes. A checker receipt additionally identifies diagnostics and normalized responsibility. A MIR receipt records canonical MIR or a stable digest. An xVM or LLVM receipt records runtime target, toolchain, exit/result behavior, and the MIR identity it executed. The publication must not synthesize a higher evidence lane from lower-lane success.

Mutation tests must flip one authority at a time: Grammar token, Frontend owner, feature diagnostic reference, predicate rule, no-go row, example outcome, or documentation invariant. The verifier passes only when the intended rule detects each mutation. Hash manifests bind every current artifact; they are integrity evidence, not semantic execution evidence.

## 54. Role-specific review directive

All Deeplus roles are bound by the following current-source directive:

- The language designer maintains the disjoint constitutional rule: named-rest parameter `***`, function-type residue `***`, named unfold `**`.
- Grammar and frontend owners reject parameter/type `**` in Recovery and admit no Stable or Preview route for it.
- Type-system and checker owners preserve `Record***` in callable compatibility, RCTS descriptors, public API digests, and diagnostics.
- Implementer and MIR owners create no AST, HIR, MIR, xVM, or LLVM current node from parameter/type `**`.
- Formatter/LSP owners print and suggest `***` for named rest and `**` only for unfold; no configuration may reverse them.
- Prelude, standard-library, example, and documentation owners publish only the current spelling.
- Tester and critic roles include both directions of negative evidence and search the entire release for contradictory current claims.
- Idea and promotion roles must rewrite or reject any proposal whose named-rest parameter or type surface is `**`; that surface is fully discarded.
- Release owners block publication unless the canonical spec, exact Grammar, Frontend Model, TypeSystem, examples, registries, schemas, and verifier all agree.

This directive does not prohibit the independent infix linear-product operator `**`. It prohibits using `**` as the declaration/type named-rest suffix and prohibits using `***` as unfold.

## 55. Human review procedure and conflict resolution

A reviewer begins with this specification and follows a rule to its single exact Grammar owner, Frontend policy, feature row, active diagnostic, checker predicate, and accepted/rejected examples. Repeated prose is not a second authority. The separate companions specialize implementation handoff without creating alternative syntax.

When artifacts disagree, classify the conflict before editing: lexical ownership, grammar reachability, contextual admission, type rule, evaluation order, maturity, diagnostic status, example drift, or evidence overclaim. Resolve the rule at its highest current authority, then regenerate every dependent projection. Do not add an overlay or an errata-only exception. A release is fully merged only when a reader can reconstruct every current decision without an external package.

Promotion is granted only to a closed design with deterministic source admission, type and runtime laws, diagnostics, examples, and evidence appropriate to the claimed lane. A useful proposal may remain `PREVIEW_DESIGN` without being rejected. `STDLIB_PROFILE` and `OFFICIAL_TOOLING` promotion are deliberately separate from core syntax. No product-support promotion occurs without artifact-bound execution receipts.

## 56. Canonical source synopsis

The following synopsis is illustrative current Deeplus and intentionally combines the responsibilities most likely to drift:

```deeplus
public sealed class Request {
    +let id: Int
}

public final class ConfigureRequest : Request {
    +let options: Record
}

public trait Configurable {
    +def configure+(options***: Record) -> Result<Unit, error ConfigError>
}

public def configure(options***: Record) -> Result<Unit, error ConfigError>
= return @match validate(**options) {
    ::ok(_) => apply(**options)
    ::err(error) => ::err(error)
}

public type Configure = (Record***) -> Result<Unit, error ConfigError>

public def classify(value: Option<Int>) -> String =
    @match value {
        Option::some(x) => "some ${x}",
        Option::none => "none",
    }
```

The class spelling is `sealed class`; `class#sealed` is removed. The MatchExpr owner is `@match`. Lambda parameters use their dedicated typed form. Value-less final `return` is omitted in canonical source. Associated projection uses direct `::` qualification without redundant parentheses. Declaration methods do not acquire a leading tilde. These surface choices, the numeric lexical policy, and the linear-product precedence in the exact Grammar are current even though product execution remains `NOT_RUN`.

Current R51f consolidated examples are illustrated without changing the authority order:

```deeplus
public enum State { draft, active, blocked(reason: String) }

let id = 7
let name = "Ada"
let user = User${ id, name }

if let Option::some(value) = candidate {
    use text::render, metrics::format in {
        log("""
            value=${render(value)}
            """)
    }
}
```


## 57. Removed-surface boundary

The removal boundary is checked across all package authorities. `MemberSuffix` remains for real members, extensions, and witnesses but acquires no Map-key rule. `DefIntroducer` remains structurally generic while the Frontend Model supplies the closed owner table without `tailrec`. The scanner has no regex mode. `ListLiteralElementJoinAdmitted` may check against an explicit expected union but cannot invent one. No current projection contains any of the five removed feature identities.


## Package self-containment law

The repository root is the complete current authority workspace and requires
no external authority package. Every current filename, schema identity,
fixture pointer, profile identifier, and checksum resolves through a tracked
path in this source tree. Historical external packs are provenance evidence
only. The exact Grammar and Frontend Model remain separate first-class
canonical artifacts, while `docs/grammar-reference` is their validated
documentation projection.

This edition consolidates terminology and removes non-normative version history without changing language surfaces, type rules, diagnostic status, example outcomes, Grammar productions or MIR behavior. Static validation is E2 evidence; product lanes remain `NOT_RUN`.

# Part XI — Active diagnostics

This is the sole human diagnostic atlas. Only active rows are reproduced; non-active and audit-only identities remain machine reference data.

## checker

- `ABSTRACT_CLASS_INSTANTIATION_FORBIDDEN` [error]: An abstract class cannot be instantiated.
- `ACCEPTED_NAMED_FUNCTION_BLOCK_REQUIRES_RETURN` [error]: Accepted ordinary named function blocks that produce a value must use explicit return; lambda/@match local results use ret.
- `ACCEPT_WITH_GATE_REQUIRES_PREVIEW_FEATURE` [error]: An accept_with_gate example must reference at least one PREVIEW feature with explicit_feature_gate source activation.
- `ACCESSOR_PROPERTY_HEADER_VISIBILITY_FORBIDDEN` [error]: Accessor property header must not carry member visibility; accessor visibility belongs on get/set.
- `ACCESSOR_PROPERTY_MULTIPLE_ACCESSORS_REQUIRE_BLOCK` [error]: Multiple accessors require an accessor block after :=.
- `ACCESSOR_PROPERTY_SEPARATOR_REQUIRED` [error]: Accessor property must use := between property header and accessor specification.
- `ACCESSOR_PROPERTY_VISIBILITY_ON_ACCESSOR_REQUIRED` [error]: Accessor property visibility must be on get/set, not on property header.
- `AFFINE_UNIT_NOT_IN_PHASE_A` [error]: Affine units such as degrees Celsius are not part of the current profile measure profile.
- `ALIASABLE_REJECTS_LIFECYCLE_OWNER` [error]: Aliasable is removed and lifecycle owners cannot be hidden behind alias vocabulary.
- `ALIASABLE_REMOVED` [error]: Aliasable is removed from current source vocabulary.
- `ALIASABLE_REMOVED_USE_SHARED_OR_PLAIN` [error]: Aliasable is not current-canonical public vocabulary. Use Plain for authority-free plain values, Shared<T> for alias creation, Shareable for observation safety, or explicit move/clone.
- `ALL_NAMED_ARGUMENT_LAYOUT_ROUTE_UNREACHABLE` [error]: All-named argument layout separator must be reachable through ArgList in all-named contexts; positional/mixed arguments still require commas.
- `AMBIGUOUS_EXTENSION_CANDIDATE` [error]: Multiple active extension candidates match and no deterministic specificity rule selects one.
- `AMBIGUOUS_EXTENSION_SELECTOR` [error]: Multiple extension selectors match; use a qualified selector.
- `AMBIGUOUS_NAMED_REST_OVERLOAD` [error]: Named rest overloads are ambiguous; source order and return type are not tie-breakers.
- `AMBIGUOUS_REST_PARAMETER_OVERLOAD` [error]: Repeated positional rest overloads are ambiguous; source order and return type are not tie-breakers.
- `AMBIGUOUS_UNIT_SYMBOL` [error]: Multiple active catalogs define the same unit symbol. Use a qualified unit symbol such as `alias::unit`.
- `AMPERSAND_POLARITY_UNRESOLVED` [error]: The `&` token is resolved by its closed current position: `context expr` is explicit context passing, while `&anchor` and infix `&` belong to their declared anchor/operand families.
- `ANY_REJECTS_SHARED_OWNER` [error]: Any minimum profile cannot erase Shared<T> owner responsibility.
- `ARRAY_SCALAR_OPERATION_REQUIRES_CONTEXT_ANCHOR` [error]: NumericArray and scalar operation requires an explicit context anchor or named API; no implicit scalar lift.
- `ARROW_ASSIGNMENT_TARGET_NOT_ALLOWED` [error]: Rightward flow binding cannot assign to an existing l-value.
- `ASSIGNMENT_NUMERIC_TO_MEASURE_REQUIRES_EXPLICIT_UNIT` [error]: Assigning a numeric value to a Measure requires an explicit unit.
- `ASSOCIATED_PROJECTION_REQUIRES_BOUND` [error]: Associated projection requires a trait bound declaring that associated requirement.
- `ASSOCIATED_REQUIREMENT_PROJECTION_UNRESOLVED` [error]: Associated requirement projection cannot be resolved under the current witness/conformance environment.
- `ASSOCIATED_REQUIREMENT_UNRESOLVED` [error]: Associated type/value requirement cannot be resolved in this witness or constraint environment.
- `ASYNC_COLLECTOR_POLICY_NOT_ADMITTED` [error]: the current profile Stage 1 admits only List + finite AsyncSequence<T, ES> + named def#async transform throwing ET + exact result throws ES | ET + sequential/source/failFast/cancelPending/buffer1.
- `ASYNC_CORE_PRODUCT_SUPPORT_NOT_RUN` [error]: Async/Task/Actor core is language-design stable but product support is NOT_RUN.
- `AT_CONTROL_EXPR_REQUIRES_AT_PREFIX` [error]: Value-producing control expression requires @if/@match/@try/@scope spelling.
- `AT_MATCH_ARM_RETURN_IS_NOT_RESULT` [error]: `return` exits the enclosing named function and is not an @match arm result.
- `AT_MATCH_BLOCK_ARM_REQUIRES_RET` [error]: A block arm in value-producing @match must produce its local result with `ret` on every normal path.
- `AT_MATCH_SINGLE_EXPR_ARM_DOES_NOT_USE_RET` [error]: A direct `@match` arm expression does not use `ret`; write `pattern => expr` or use a block arm with `ret expr`.
- `AWAIT_REQUIRED_FOR_ASYNC_CALL` [error]: Async function or async message result must be awaited in an async context.
- `BARE_CARET_IS_POWER_NOT_BITWISE_XOR` [error]: Bare infix `^` is the right-associative power operator, not bitwise XOR; current bitwise XOR is `^^`.
- `BARE_ENUM_CASE_NOT_ALLOWED` [error]: Bare enum case names are not injected into ordinary value namespace. Use `::case` or `EnumType::case`.
- `BARE_FUNCTION_CALL_REQUIRES_TRAILING_CLOSURE` [error]: Bare ordinary call without a trailing closure is not part of this feature; use parentheses.
- `BARE_FUNCTION_TYPE_REMOVED` [error]: Bare Function is not current source; use an exact function signature or the Stable Callable facade profile.
- `BASIC_INDEX_OPERATOR_STABLE_LAW` [note]: Basic index operator is stable design; advanced slicing/custom index surfaces remain separate features.
- `BITFIELD_BACKING_MUST_BE_UNSIGNED_FIXED_WIDTH` [error]: Bitfield backing must be UInt8, UInt16, UInt32, UInt64, or UInt128.
- `BITFIELD_C_ABI_NOT_IMPLIED` [error]: A Deeplus bitfield does not imply C compiler bitfield ABI compatibility.
- `BITFIELD_DIRECT_FIELD_MUTATION_FORBIDDEN` [error]: Bitfield fields are immutable; use same-type derivation.
- `BITFIELD_ENDIANNESS_REQUIRED` [error]: Bitfield byte encoding and decoding require an explicit endian argument.
- `BITFIELD_FIELD_VALUE_OUT_OF_RANGE` [error]: The bitfield field value does not fit its declared width.
- `BITFIELD_IMPLICIT_PADDING_FORBIDDEN` [error]: Bitfield padding must be written as an explicit reserved slot.
- `BITFIELD_IMPLICIT_RAW_CONVERSION_FORBIDDEN` [error]: Bitfield/raw conversion must use `.raw` or checked Type::fromRaw.
- `BITFIELD_LAYOUT_WIDTH_MISMATCH` [error]: Bitfield slot widths must sum exactly to the backing width.
- `BITFIELD_ORDER_NOT_ADMITTED` [error]: Phase-A bitfield order is exactly ::lsb0.
- `BITFIELD_REQUIRED_FIELD_MISSING` [error]: A required bitfield materialization field is missing.
- `BITFIELD_WIDTH_MUST_BE_POSITIVE_STATIC_INT` [error]: Bitfield slot width must be a positive compile-time integer.
- `BITWISE_COMPLEMENT_IS_PREFIX_ONLY` [error]: Bitwise complement is prefix-only: write `~~x`.
- `BITWISE_COMPLEMENT_REQUIRES_KNOWN_WIDTH` [error]: `~~` requires a known-width or finite-domain operand.
- `BITWISE_OPERATOR_DOES_NOT_ACCEPT_BOOL` [error]: Bool is not a bitwise operand domain.
- `BITWISE_OPERATOR_MIXED_DOMAIN_REQUIRES_EXPLICIT_CONVERSION` [error]: Bitwise operands require one exact normalized integer or finite-domain identity; use an explicit conversion.
- `BITWISE_OPERATOR_MIXED_WIDTH_REQUIRES_EXPLICIT_CAST` [error]: Mixed-width bitwise operands require explicit width conversion.
- `BITWISE_OPERATOR_REQUIRES_BITWISE_OPERANDS` [error]: Bitwise operators require known-width or finite-domain bitwise operands.
- `BITWISE_RESULT_USED_AS_BOOL` [error]: Bitwise operators produce bitwise values, not Bool; compare explicitly or use a flag query.
- `BODYLESS_MEMBER_MUST_BE_OPEN` [error]: Body-less member declaration must be an open slot and use the + suffix.
- `BORROW_ESCAPE_OWNER_REGION` [error]: Borrowed view escapes the owner region.
- `BOUNDED_INDEX_LENGTH_MISMATCH` [error]: The bounded list element count must equal the asserted closed logical-domain cardinality.
- `BOUND_LITERAL_LENGTH_MISMATCH` [error]: The number of elements does not equal the declared closed logical-domain cardinality.
- `BOX_OWNERSHIP_VIOLATION` [error]: Box is a unique owner; use-after-move, duplicate ownership, escaping borrow, or missing cleanup is forbidden.
- `BREAK_TARGET_NOT_IN_SCOPE` [error]: Break/continue target does not refer to an enclosing loop scope.
- `BREAK_VALUE_REQUIRES_LOOP_OUTCOME_MATCH` [error]: Value-carrying break requires an immediately following loop outcome match.
- `BROADCAST_MARKER_POLARITY_IS_CONTEXT_ANCHOR` [error]: In the current profile, `&` in NumericArray contextual operations marks the context-providing anchor operand, not the adapted operand. Use `&matrix + row`, not `matrix + &row`.
- `BYTES_LITERAL_INVALID_HEX_ESCAPE` [error]: #bytes literal requires two hex digits in \xHH escapes.
- `BYTES_LITERAL_NON_ASCII_DIRECT_CHAR` [error]: #bytes literal admits only ASCII direct characters and byte escapes.
- `BYTES_NOT_IMPLICITLY_CONVERTIBLE_TO_STRING` [error]: Bytes is not implicitly convertible to String.
- `BYTE_VIEW_PROFILE_NOT_ADMITTED` [error]: ByteView requires live Bytes-owner provenance, contiguous byte-addressable storage, and no assumed text encoding or String semantics.
- `CALLABLE_PROFILE_ONLY_OVERLOAD_FORBIDDEN` [error]: Callable responsibility profiles cannot be the sole overload discriminator.
- `CALLBACK_EFFECT_NOT_PROPAGATED` [error]: Callback effects must be propagated or handled explicitly.
- `CALLBACK_THROWS_NOT_PROPAGATED` [error]: Callback throws row must be propagated or handled explicitly.
- `CANNOT_INFER_REST_ELEMENT_TYPE_FROM_EMPTY_ARGUMENTS` [error]: The element type of an empty repeated-argument call cannot be inferred without an expected type or explicit generic argument.
- `CANONICAL_TYPE_NAME_INT` [warning]: `int` is not canonical Deeplus spelling; use `Int`.
- `CARET_INFIX_REQUIRES_SPACING` [error]: Infix `^` power uses spacing (`a ^ b`). Attached postfix transpose is written without spacing (`A^`).
- `CLASS_IS_FINAL_BY_DEFAULT` [error]: A concrete class is final unless declared open or sealed class; it cannot be subclassed here.
- `CLASS_MODIFIER_COMBINATION_INVALID` [error]: The selected class flavor and modifier combination is not admitted.
- `CLAUSE_LEVEL_DEFAULT_MUST_BE_OTHERWISE` [error]: Clause-level default must use `otherwise`; `_` remains pattern discard only.
- `CLEANUP_BUDGET_BODY_POSITION_REMOVED` [error]: cleanup budget is a class-level header clause, not an ordinary member.
- `CLEANUP_BUDGET_CAMELCASE_REMOVED` [error]: cleanupBudget spelling is removed; use cleanup budget block spelling.
- `CLEANUP_DECLARATION_DIRECT_CALL_FORBIDDEN` [error]: A def#cleanup declaration is invoked only by lifecycle semantics and cannot be called or referenced as a method value.
- `CLOSURE_CAPTURE_DESCRIPTOR_STABLE_BUT_PRODUCT_NOT_RUN` [info]: Closure capture descriptors are Stable design in the current profile, but production parser/checker support remains NOT_RUN.
- `CLOSURE_INOUT_CAPTURE_REQUIRES_SCOPED_MUT` [error]: An inout closure capture requires the #scoped#mut profile and cannot escape or overlap another mutable access.
- `CLOSURE_MUT_CALL_REQUIRES_MUTABLE_PLACE` [error]: A `#mut` callable invocation requires one exclusive mutable environment place; overlapping or reentrant environment access is not admitted.
- `CLOSURE_ONCE_USED_AFTER_CALL` [error]: A `#once` callable's call right was already consumed by its first invocation; a second call or later use is forbidden.
- `COLLECTION_FREEZE_TRANSITION_NOT_ADMITTED` [error]: freeze requires exclusive mutable ownership and an admitted immutable/shareable target representation.
- `COLLECTION_GET_REQUIRES_REUSABLE_VALUE` [error]: By-value collection get requires reusable value law.
- `COLLECTION_SNAPSHOT_PROFILE_NOT_ADMITTED` [error]: snapshot must produce an independent value with explicit copy or copy-on-write responsibility.
- `COLLECTION_TRAVERSAL_ROLE_MISMATCH` [error]: A collection value and a traversal handle are distinct responsibilities and are not automatically interchangeable.
- `COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED` [error]: Column-vector semicolon form must follow the current profile orientation law: `#[a,b]` is rank-1 `#N[T]`; `#[a;b]` is column `#N,1[T]`; explicit row matrix is `#1,N[...]`.
- `COMPARISON_CHAIN_MIXED_DIRECTION_REQUIRES_EXPLICIT_AND` [error]: Mixed-direction comparison chains require explicit `and`.
- `COMPARISON_CHAIN_OPERAND_HAS_EFFECTS` [error]: Comparison chain operands should not hide effects inside mathematical-looking predicates.
- `COMPARISON_CHAIN_OPERATOR_MUST_BE_PURE` [error]: Comparison chain operators must be pure and no-throw.
- `COMPARISON_CHAIN_OPERATOR_NOT_IN_PHASE_A` [error]: Comparison chains allow only <, <=, >, >= in the current profile.
- `COMPREHENSION_FOR_AWAIT_REQUIRES_ASYNC_ITERATION` [error]: `for await` requires the async iteration design profile and does not imply general async task support.
- `CONDITION_HAS_EFFECTFUL_OPERAND` [error]: A condition operand has effects; use explicit sequencing or a pure guard.
- `CONFORMANCE_EVIDENCE_ORIGIN_NOT_UNIQUE` [error]: A root conformance evidence selector must resolve to exactly one visible coherent nominal conformance.
- `CONFORMANCE_EXTENSION_DELEGATION_MUST_BE_EXPLICIT` [error]: Delegation from a conformance requirement to an extension selector must be explicit and fully identified.
- `CONFORMANCE_LAW_PROOF_BLOCK_REQUIRES_PREVIEW` [error]: Conformance proof blocks require a future proof preview; Stable law declarations are documentation contracts only.
- `CONFORMANCE_REQUIREMENT_BINDING_MISSING` [error]: A conformance must explicitly bind every required trait item.
- `CONSTRAINT_USED_AS_EXISTENTIAL` [error]: A responsibility constraint is not a value type. Use `any Trait` or `any Plain` for an existential boundary.
- `CONSTRUCTOR_CHAIN_TERMINAL_MUST_BE_NEW` [error]: A same-type constructor chain must terminate at root `new`.
- `CONSTRUCTOR_DELEGATION_ARGUMENT_EFFECT_NOT_DECLARED` [error]: Effects from selected constructor delegation arguments must be declared by the delegating constructor.
- `CONSTRUCTOR_DELEGATION_ARGUMENT_THROWS_NOT_DECLARED` [error]: Throws from selected constructor delegation arguments must be declared by the delegating constructor.
- `CONSTRUCTOR_DELEGATION_CYCLE` [error]: Same-type constructor delegation graph must be acyclic.
- `CONSTRUCTOR_DELEGATION_GRAPH_NOT_ADMITTED` [error]: A constructor delegation list must select exactly one target, keep same-type delegation acyclic, reach one root constructor, and make that root select exactly one superclass constructor without observing self in a guard.
- `CONSTRUCTOR_DELEGATION_GUARD_CANNOT_OBSERVE_SELF` [error]: Constructor delegation guards run before initialization and cannot observe `self`.
- `CONSTRUCTOR_DELEGATION_GUARD_NOT_PURE` [error]: Constructor delegation guards must be pure, synchronous, no-throw, and effect-free.
- `CONSTRUCTOR_DELEGATION_MIXES_SAME_TYPE_AND_SUPER` [error]: A constructor delegation decision list cannot mix same-type and super targets.
- `CONSTRUCTOR_DELEGATION_NOT_EXHAUSTIVE` [error]: Same-type constructor delegation must select exactly one target on every successful path.
- `CONSTRUCTOR_DELEGATION_TARGET_NOT_FOUND` [error]: Constructor header delegation target was not found.
- `CONTEXTUAL_LAMBDA_EXPECTED_CALLABLE_REQUIRED` [error]: A contextual { expr } lambda requires one already-selected expected callable type; otherwise write { => expr }.
- `CONTEXT_ANCHOR_EFFECTFUL_CONTEXT_NOT_ENABLED` [error]: Effectful context anchors such as transaction/retry/tracing are not part of the NumericArray context-anchor MSP.
- `CONTEXT_ANCHOR_MULTIPLE_ANCHORS_UNSUPPORTED` [error]: Multiple context anchors in one operation are not supported in the MSP.
- `CONTEXT_ANCHOR_NOT_A_VALUE` [error]: `&expr` is not a standalone value in the context-anchor MSP.
- `CONTEXT_ANCHOR_REQUIRES_ELIGIBLE_OPERATION` [error]: Context anchors are only valid as operands of an eligible contextual operation.
- `CONTEXT_ANCHOR_SCOPE_IS_NEAREST_OPERATION` [error]: The context anchor applies only to the nearest operation in the MSP.
- `CONTEXT_ARGUMENT_NOT_EXPECTED` [error]: An ordinary parameter does not accept a context-marked argument.
- `CONTEXT_ARGUMENT_REQUIRED` [error]: A context parameter requires a matching explicit context argument.
- `CONTEXT_EVIDENCE_ROLE_NOT_REGISTERED` [error]: &expr has no admitted context-evidence role at this source position.
- `CONTEXT_FUNCTION_TYPE_MISMATCH` [error]: Function types with context parameter roles are not interchangeable with ordinary function types.
- `CONTEXT_MARKER_NOT_A_VALUE` [error]: A context marker does not produce a first-class value.
- `CONTEXT_PARAMETER_DEFAULT_FORBIDDEN` [error]: Context parameters cannot have default arguments in the MSP.
- `CONTEXT_PARAMETER_LIMIT_EXCEEDED` [error]: The explicit context parameter MSP allows at most one context parameter per function.
- `CONTEXT_PARAMETER_NOT_APPLIED_AUTOMATICALLY` [error]: A context parameter is not automatically applied to body operations.
- `CONTEXT_ROLE_MISMATCH_IN_OVERRIDE` [error]: Override or witness parameter role does not match the requirement.
- `CONTEXT_VALUE_REQUIRES_REUSABLE_SHAREABLE` [error]: Context value must be reusable, Shareable, no-drop, and authority-free in the minimum profile.
- `CONTRAVARIANT_TYPE_PARAM_USED_IN_PRODUCER_POSITION` [error]: A contravariant type parameter cannot be used in a producer/output/read position.
- `COPYABLE_REMOVED_USE_PLAIN_OR_SHARED` [error]: Copyable is not current-canonical public vocabulary. Choose Plain, Shared<T>, explicit clone/derivation, or explicit move according to the responsibility you need.
- `COVARIANT_TYPE_PARAM_USED_IN_CONSUMER_POSITION` [error]: A covariant type parameter cannot be used in a consumer/input/write position.
- `CURRENCY_CONVERSION_REQUIRES_PROVIDER` [error]: Currency conversion requires an explicit FX/provider policy.
- `DATA_CLASS_AUTOMATIC_UNFOLD_NOT_CURRENT` [error]: Data classes do not receive an automatic ProjectionRow; unfold an explicit schema view instead.
- `DATA_CLASS_MATERIALIZATION_PROFILE_NOT_SATISFIED` [error]: This data class has custom initialization, mutable/resource state, effectful defaults, or hidden invariants and must use a constructor.
- `DECL_CLAUSE_BLOCK_REQUIRES_EQUALS_ATTACHMENT` [error]: Function clause block must be attached with `= {{ ... }}`.
- `DECL_CLAUSE_DISJOINTNESS_UNPROVEN` [error]: The compiler cannot prove that these declarative clauses are mutually exclusive.
- `DECL_CLAUSE_GUARD_NOT_GUARD_SAFE` [error]: Clause guard must be R0 guard-safe: sync, deterministic, throws Never, effects {}, and non-suspending.
- `DECL_CLAUSE_NONEXHAUSTIVE` [error]: Clause block does not cover all inputs. Ordinary clause blocks are exhaustive by default.
- `DECL_CLAUSE_NONEXHAUSTIVE_REQUIRES_PARTIAL_POLICY` [error]: Non-exhaustive clause block requires explicit partial policy and visible failure channel.
- `DECL_CLAUSE_OVERLAP` [error]: Declarative clauses overlap; source order is not a semantic tiebreaker.
- `DECL_CLAUSE_RESULT_TYPE_MISMATCH` [error]: Clause result is not assignable to the function return type.
- `DECL_PARAM_GUARD_SHORTHAND_NOT_CURRENT` [error]: Parameter guard shorthand such as `n: Nat == 0` is not current Deeplus source.
- `DEFER_CLEANUP_RESERVED_PLACE_MOVED` [error]: A place reserved by defer cannot be moved or rebound before scope exit.
- `DELEGATING_CONSTRUCTOR_CANNOT_INITIALIZE_STORED_FIELD` [error]: A same-type delegating constructor body is post-init; it cannot initialize stored fields.
- `DERIVATION_ENTRY_SEPARATOR_REQUIRED` [error]: Same-line derivation delta entries require comma; multi-line entries may use LayoutEntrySep when unambiguous.
- `DETERMINISTIC_PRIMARY_SUPPRESSED_ORDER_VIOLATION` [error]: Failure selection or cleanup suppression order differs from the required source-order/reverse-cleanup algorithm.
- `DETERMINISTIC_SUPPRESSED_ORDER_REQUIRED` [error]: Primary/suppressed failure ordering must be deterministic for cleanup, resource, and task aggregation profiles.
- `DIAGNOSTIC_VALUE_NOT_ADMISSIBLE` [error]: Diagnostic payload values must be Plain snapshots without owner, resource, authority, borrow, or cleanup responsibility.
- `DIAGNOSTIC_VALUE_REJECTS_AUTHORITY` [error]: Error/Defect payload cannot carry lifecycle/resource/raw/meta authority.
- `DIAGNOSTIC_VALUE_REJECTS_RESOURCE` [error]: Error/Defect diagnostic payload cannot carry Resource owner.
- `DIMENSION_MISMATCH` [error]: Measure operands have incompatible dimensions.
- `DOLLAR_CLASS_SIDE_SEPARATOR_REMOVED_USE_COLON_COLON` [error]: Type-side structured declaration uses Type::selector; Type$$selector is removed.
- `DOLLAR_CONSTRUCTION_LHS_MUST_BE_TYPE` [error]: A left-hand side before ${...} is valid only when it resolves as a TypeRef.
- `DOLLAR_DECLARATION_SIGIL_REMOVED_USE_LET_VAR` [error]: Dollar field/member promotion sigils are removed; use let or var.
- `DOLLAR_INSTANCE_SIDE_SEPARATOR_REMOVED_USE_TILDE` [error]: Instance-side structured declaration uses Type~selector; Type$selector is removed.
- `DOT_ENUM_CASE_PATTERN_NOT_CURRENT` [error]: Dot-prefixed enum case patterns are not current Deeplus source. Use `::case` or `EnumType::case`.
- `DOT_ENUM_CASE_SHORTHAND_NOT_CURRENT` [error]: Dot-prefixed enum case shorthand is not current Deeplus. Use `::case` with expected enum type or `EnumType::case`.
- `DOT_NOT_ALLOWED_FOR_TYPE_SIDE_SELECTOR` [error]: Type-side selectors and calls use `::`, not `.`. Write `Type::member` or `Type::member(...)`.
- `DOT_NOT_ALLOWED_IN_IMPORT_PATH` [error]: Static import paths use `::`; dotted import paths are not current source.
- `DOT_NOT_ALLOWED_IN_MODULE_PATH` [error]: Static module paths use `::`; `.` is runtime member access.
- `DOT_NOT_ALLOWED_IN_QUALIFIED_EXTENSION_SELECTOR` [error]: Qualified extension selectors use `::`, not `.`. Write `Int::metric::m`.
- `DOT_NOT_ALLOWED_IN_USE_PATH` [error]: Static use paths use `::`; dotted use paths are not current source.
- `DOT_PRODUCT_REQUIRES_RANK1_VECTORS` [error]: `*+` dot product requires rank-1 vector operands with equal static or proven length.
- `DUPLICABLE_REMOVED_USE_EXPLICIT_RESPONSIBILITY` [error]: Duplicable is not current-canonical public vocabulary. Choose Plain, Shared<T>, explicit clone/derivation, or explicit move.
- `DUPLICATE_NORMALIZED_SIGNATURE` [error]: Two declarations normalize to the same semantic signature.
- `DYNAMIC_CONVERSION_REQUIRES_PROVIDER` [error]: Dynamic unit conversion requires an explicit provider.
- `DYNAMIC_EXTENSION_DISPATCH_FORBIDDEN` [error]: Extension lookup uses receiver static type, not runtime receiver identity.
- `DYNAMIC_TRAIT_ATTACH_NOT_CURRENT` [error]: Dynamic trait attach/detach has no activatable the current profile source syntax.
- `DYNAMIC_UNIT_CONVERSION_POLICY_REQUIRED` [error]: Dynamic unit conversion requires explicit observation, rounding, failure, effect, cache and replay policies.
- `DYNAMIC_UNIT_CONVERSION_PROFILE_NOT_ACTIVE` [error]: Dynamic unit conversion requires an active stdlib/provider conversion profile.
- `DYNAMIC_UNIT_CONVERSION_PROVIDER_REQUIRED` [error]: Dynamic unit conversion requires an explicit provider identity and version.
- `DYN_RCTS_SOURCE_NOT_CURRENT` [error]: Dynamic RCTS source activation is not current; the design family is nonactivatable.
- `EFFECTFUL_OTHERWISE_RIGHT_OPERAND` [error]: Right operand of `otherwise` has effects and is conditionally evaluated; make that responsibility explicit.
- `EFFECTROW_UNSAFE_AXIS_FORBIDDEN` [error]: `unsafe` is a safety/authority axis, not an EffectRow atom; use an explicit unsafe boundary.
- `EFFECT_ROW_VARIABLE_UNBOUND` [error]: Effect row variable is not bound in the generic/effect environment.
- `EMPTY_NULLARY_LAMBDA_REQUIRES_EXPECTED_FUNCTION_TYPE` [error]: Empty `{}` can mean `() -> Unit` only with an expected function type.
- `ENTRY_DECL_DUPLICATE` [error]: An executable target has more than one explicit entry declaration.
- `ENTRY_SIGNATURE_NOT_ADMITTED` [error]: An entry function must have () or (Sequence<String>) parameters and return Unit or ExitCode.
- `ENUM_CASE_CONFLICTS_WITH_TYPE_SIDE_MEMBER` [error]: Enum case names share the enum type static case namespace and cannot conflict with type-side members.
- `ENUM_CASE_EXPRESSION_PAYLOAD_MUST_NOT_USE_DECLARATION_PAYLOAD` [error]: Enum case expression payload uses expression arguments, not enum case declaration field syntax.
- `ENUM_CASE_PATTERN_PAYLOAD_MUST_NOT_USE_DECLARATION_PAYLOAD` [error]: Enum case pattern payload uses pattern payload syntax, not enum case declaration field syntax.
- `ENUM_CASE_PATTERN_USES_COLON_COLON` [error]: Enum case patterns use `::case` or `EnumType::case`, not `.case`.
- `ESCAPED_MEMBER_CONTEXT_ONLY` [error]: Backslash identifier escape is permitted only in a member-access suffix.
- `EVIDENCE_SELECTOR_NOT_A_VALUE` [error]: A conformance evidence selector is not an ordinary value and cannot be stored, returned, captured, or runtime-selected.
- `EXISTENTIAL_ASSOC_TYPE_UNBOUND` [error]: Existential trait leaves an associated requirement unbound for an operation that needs it.
- `EXPECTED_ENUM_TYPE_REQUIRED_FOR_CASE_PATTERN_SHORTHAND` [error]: Leading `::case` pattern requires an expected enum subject type; use `EnumType::case` if the owner is not known.
- `EXPECTED_ENUM_TYPE_REQUIRED_FOR_CASE_SHORTHAND` [error]: Leading `::case` requires an expected enum type. Use `EnumType::case` or add a type annotation.
- `EXPLICIT_BROADCAST_MARKER_NOT_CURRENT` [error]: `operand op &adapted` is not current Deeplus source in the current profile; `&` marks the context-providing anchor. Use a named API or `&anchor op operand` when the NumericArray context-anchor law applies.
- `EXPLICIT_WITNESS_ARGUMENT_NOT_ADMITTED` [error]: The using argument must be a forwarded explicit witness Identifier or a unique coherent conformance(Type conforms Trait) selector; every ordinary/computed value is forbidden.
- `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN` [error]: Explicit witness parameters cannot escape, be stored, returned, or captured by escaping closures.
- `EXPLICIT_WITNESS_PARAMETER_REQUIRED` [error]: A declaration requiring an explicit witness parameter must receive a matching explicit witness argument.
- `EXPR_DOLLAR_DERIVATION_NOT_CURRENT` [error]: `expr${...}` is not current Deeplus source; use `expr!{...}` or `expr!!{...}` for same-type derivation.
- `EXTENSION_CANNOT_FULFILL_TRAIT_REQUIREMENT` [error]: Active extension selectors do not automatically form trait witnesses.
- `EXTENSION_CONFORMANCE_LOOKUP_DOMAIN_MIXED` [error]: The same call spelling cannot change between extension and witness lookup because a conformance is present.
- `EXTENSION_IMPORTED_BUT_NOT_ACTIVE` [error]: `import` does not activate extension selector lookup; use an extension activation.
- `EXTENSION_IMPORT_DOES_NOT_ACTIVATE_USE_REQUIRED` [error]: `import` does not activate extension lookup; use extension activation.
- `EXTENSION_NOT_ACTIVE` [error]: Import does not activate extension lookup; use `use`.
- `EXTENSION_RESOLUTION_ORDER_NOT_TIEBREAKER` [error]: Import, use, declaration, and source order are not extension-overload tie-breakers; qualify the selector or remove the ambiguity.
- `EXTENSION_SELECTOR_NOT_ORDINARY_NAME` [error]: An active extension selector is not introduced as an ordinary function name.
- `EXTENSION_SET_BLOCK_STABLE_BUT_PRODUCT_NOT_RUN` [info]: Named extension set blocks are Stable design in the current profile, but production parser/checker support remains NOT_RUN.
- `EXTENSION_SET_DOES_NOT_MODIFY_TARGET_TYPE` [error]: An extension set groups extension selectors; it does not add stored members or ordinary dot members to the target type.
- `EXTENSION_SET_MEMBER_ID_REQUIRES_EXTENSION_SET_ID` [error]: Named extension set members must include origin, target type, extension set name, and selector in their semantic identity.
- `EXTENSION_SET_MEMBER_ID_REQUIRES_SET_ID` [error]: Named extension set member semantic ID must include extension set identity.
- `EXTENSION_SET_MEMBER_TILDE_DECLARATION_REMOVED` [error]: Declare a body member selector with plain `def name`; tilde belongs to receiver calls, not immediately before the declared selector.
- `EXTENSION_SET_OPERATOR_MEMBER_UNSUPPORTED_IN_MSP` [error]: Operator members are not part of named extension set MSP.
- `EXTENSION_SET_PATH_AMBIGUOUS` [error]: Extension set activation path is ambiguous; qualify the origin.
- `EXTENSION_SET_PRIVATE_TARGET_ACCESS_FORBIDDEN` [error]: Extension set member cannot access target private representation outside visibility law.
- `EXTENSION_SET_RECEIVER_MODE_UNSUPPORTED_IN_MSP` [error]: Named extension set MSP supports borrow receiver only.
- `EXTENSION_SHADOWED_BY_MEMBER_COMPAT` [error]: the current profile compatibility profile selected the member slot while an active extension is shadowed; strict profile will require explicit selection.
- `EXTENSION_USE_REEXPORT_STABLE_BUT_PRODUCT_NOT_RUN` [warning]: `use export` is stable design in the current profile; product parser/checker support remains NOT_RUN.
- `FACET_BORROW_CROSSES_SUSPENSION` [error]: A Phase-A borrowed Facet cannot cross suspension, task, or actor boundaries.
- `FACET_BORROW_ESCAPE_FORBIDDEN` [error]: A borrowed Facet cannot outlive its payload borrow region or cross an isolation boundary.
- `FACET_CONCRETE_TYPE_SPELLING_FORBIDDEN` [error]: Facet<T as Trait> leaks the payload type; use Facet<borrow any Trait>.
- `FACET_DROP_PLAN_NOT_PRESERVED` [error]: Owned Facet packaging must preserve the concrete payload drop plan exactly.
- `FACET_MOVE_REQUIRES_OWNER` [error]: A move Facet requires one unique payload owner.
- `FACET_TYPE_REQUIRES_EXPLICIT_MODE` [error]: Facet source types require an explicit borrow, inout, or move mode.
- `FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE` [error]: This design-only or nonactivatable feature cannot be enabled in the current the current profile profile.
- `FEATURE_NOT_SOURCE` [error]: This feature is not an ordinary source feature in the current profile.
- `FEATURE_REQUIRES_PREVIEW_GATE` [error]: This Preview feature requires an explicit feature gate.
- `FFI_C_EXTERN_REQUIRES_PREVIEW_GATE` [error]: C extern unsafe declarations require #preview(ffi_c_extern_unsafe_surface_msp).
- `FFI_C_EXTERN_UNSAFE_REQUIRES_PREVIEW_GATE` [error]: C extern unsafe surface requires #preview(ffi_c_extern_unsafe_surface_msp).
- `FFI_MSP_REQUIRES_PREVIEW_GATE` [error]: Safe FFI MSP requires preview gate.
- `FFI_SIGNATURE_UNREPRESENTABLE` [error]: This type is not representable in the selected FFI profile.
- `FILL_REPEAT_ADMISSIBILITY_FAILED` [error]: The fill/repeat expression is not admissible for this shaped target and element responsibility.
- `FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT` [error]: Current operator glyph dispatch is intrinsic-only; a Trait, conformance, witness, extension, or provider cannot supply a glyph implementation.
- `FLAGS_OPERATION_REQUIRES_SAME_NOMINAL_TYPE` [error]: Flags operands must have the same nominal bitfield#flags type.
- `FLAGS_RESULT_IS_NOT_BOOL` [error]: A flags bitwise result is a flags value, not Bool.
- `FLAGS_SHIFT_OPERATOR_FORBIDDEN` [error]: Shift operations are forbidden on semantic flags values.
- `FLOW_BINDING_ARROW_LET_REMOVED` [error]: Rightward flow binding uses `expr -> $name` for a fresh immutable local or `expr -> $$name` for a fresh mutable local; `-> let` and `-> var` are not current source.
- `FLOW_BINDING_CANNOT_CHAIN` [error]: Rightward flow binding cannot be chained.
- `FLOW_BINDING_IS_STATEMENT_ONLY` [error]: Rightward flow binding is a statement, not an expression.
- `FLOW_BINDING_NAME_ALREADY_BOUND` [error]: A rightward `$name` or `$$name` target must be fresh in the current function/block-local Block; immutable and mutable flow bindings never assign to or shadow an existing local in that Block.
- `FLOW_BINDING_ONLY_ALLOWED_IN_LOCAL_BLOCK` [error]: Rightward flow binding is admitted only as a statement in a function/block-local Block; it is forbidden at source, type, or member scope and in expression position.
- `FLOW_BINDING_TARGET_MUST_BE_DOLLAR_LOCAL` [error]: A rightward flow target must be exactly `$Identifier` or `$$Identifier`, optionally followed by a type annotation.
- `FLOW_BINDING_TYPE_ANNOTATION_MISMATCH` [error]: The flow-binding value is not assignable to the optional target type annotation; no local binding is committed.
- `FORWARD_GROUP_COLLISION` [error]: A forwarded member collides with an existing or previously forwarded member.
- `FORWARD_GROUP_DUPLICATE_MEMBER` [error]: A grouped forwarding list names the same member more than once.
- `FOR_GUARD_PATTERN_BINDING_NOT_AVAILABLE` [note]: Retired diagnostic; a `for let` guard may read its nonowning probe bindings, while move, escape, suspension, mutation-through, and authority acquisition remain forbidden before commit.
- `FOR_LET_FILTER_GUARD_NOT_BOOL` [error]: The optional `for let` GuardClause must have type Bool.
- `FULL_ENUM_CASE_USES_COLON_COLON` [error]: Fully qualified enum cases use `::`. Expected-type shorthand also uses leading `::case`; dot-prefixed `.case` is not current Deeplus.
- `FUNCTION_SIGNATURE_MUST_PRESERVE_CONTROL_AXES` [note]: Function signatures must preserve throws/effects/suspension/call-domain axes; do not erase them into a bare callable façade.
- `FUNCTION_TYPE_REQUIRES_THIN_ARROW` [error]: Function/result/signature arrows use ->.
- `FUNCTION_TYPE_REST_RESIDUE_REQUIRED` [error]: Function types and public API digests must preserve `T...` and `Record***` call-shape residues; neither may be erased to `Sequence<T>` or `Record`.
- `GENERATOR_BORROW_CAPTURE_FORBIDDEN` [error]: Escaping generator expression cannot capture a borrowed owner that would outlive its region.
- `GENERATOR_CREATION_EFFECTS_VISIBLE` [error]: Generator creation effects must be visible at creation boundary.
- `GENERATOR_EXPR_IS_SINGLE_PASS_NOT_COLLECTION` [error]: @for/@while/@repeat produces a single-pass generator value, not an eager collection.
- `GENERATOR_INOUT_CAPTURE_FORBIDDEN` [error]: Escaping generator expression cannot capture inout state across iteration boundary.
- `GENERATOR_REFUTABLE_BINDER_FORBIDDEN` [error]: Generator binder must be irrefutable in the Phase A profile.
- `GENERIC_CONSTRAINT_UNSATISFIED` [error]: Generic where-clause conformance constraint is not satisfied.
- `GENERIC_PARAMETER_DEFAULTS_TO_INVARIANT` [note]: A generic parameter without an explicit variance marker is invariant; trait parameters may use the admitted `in` or `out` marker when every use position is valid.
- `GENERIC_PARAM_KIND_MISMATCH` [error]: Generic argument kind does not match the parameter kind.
- `GENERIC_TYPE_CONSTRUCTOR_INVARIANT` [error]: This generic type constructor is invariant in the given type argument.
- `GENERIC_TYPE_CONSTRUCTOR_INVARIANT_BY_DEFAULT` [error]: Generic type constructors are invariant by default in the current profile unless a narrow variance descriptor admits a safer role.
- `GUARDED_LET_RESIDUAL_NOT_EXHAUSTIVE` [error]: The failure pattern is not irrefutable for the exact residual domain.
- `GUARDED_RETURN_DOES_NOT_COMPLETE_ALL_PATHS` [error]: A guarded return does not complete all value paths; add an unconditional return or exhaustive control expression.
- `GUARD_AND_RIGHTWARD_BINDING_CANNOT_COEXIST` [error]: Guard clause and rightward `$` binding cannot coexist in one statement.
- `GUARD_CALLABLE_CONSUME_FORBIDDEN` [error]: A #guard callable cannot consume parameters or captures.
- `GUARD_CALLABLE_RESULT_MUST_BE_BOOL` [error]: A #guard callable must return exactly Bool on every normal path.
- `GUARD_CLAUSE_NOT_ALLOWED_HERE` [error]: Guard clauses are allowed only on approved control-transfer statements and loop headers.
- `GUARD_CONDITION_CONTROL_TRANSFER_NOT_ALLOWED` [error]: Guard condition must not contain control transfer.
- `GUARD_CONDITION_EFFECT_NOT_ALLOWED` [error]: Guard condition must have effects {}.
- `GUARD_CONDITION_NOT_BOOL` [error]: Guard condition must have type Bool.
- `GUARD_CONDITION_SUSPEND_NOT_ALLOWED` [error]: Guard condition must not suspend.
- `GUARD_CONDITION_THROWS_NOT_ALLOWED` [error]: Guard condition must not throw.
- `GUARD_EVALUATION_CONTRACT_VIOLATION` [error]: Guard evaluation must precede ownership commit and payload evaluation; a false guard leaves payload responsibilities unobserved.
- `IDENTITY_OPERATION_REQUIRES_IDENTITY_BEARING` [error]: The operation requires an identity-bearing descriptor.
- `IF_EXPR_REQUIRES_ELSE` [error]: A value-producing `@if` requires an `else` branch; the optional grammar tail exists only so recovery can emit this diagnostic.
- `IMPLICIT_AT_OUTSIDE_SINGLE_PARAMETER_CLOSURE` [error]: Implicit @ requires the nearest omitted-parameter closure to have one expected parameter.
- `IMPLICIT_AT_WITH_EXPLICIT_PARAMETER` [error]: An explicit closure parameter cannot be mixed with the implicit @ parameter.
- `IMPLICIT_LAMBDA_ARG_OUTSIDE_LAMBDA` [error]: Standalone `@` placeholder is allowed only inside implicit one-argument lambda bodies.
- `IMPLICIT_LAMBDA_ARG_REQUIRES_ONE_PARAM_CONTEXT` [error]: Implicit `@` lambda requires an expected one-parameter function context.
- `IMPLICIT_LAMBDA_ARG_WITH_EXPLICIT_PARAMS` [error]: Do not mix explicit lambda parameters with implicit `@` placeholder.
- `IMPLICIT_LAMBDA_EXPECTED_CALLABLE_AMBIGUOUS` [error]: Implicit @ cannot be checked until overload shape selects exactly one expected callable.
- `IMPLICIT_OWNER_TO_SHARED_FORBIDDEN` [error]: An owner cannot be implicitly promoted to Shared<T> or reused across a sharing boundary.
- `IMPLICIT_PURE_FUNCTION_HAS_EFFECTS` [error]: Implicit pure-elision function has effects and cannot elide #pure.
- `IMPLICIT_REUSE_REQUIRES_PLAIN_OR_SHARED_HANDLE` [error]: Value cannot be reused implicitly; use move, borrow, Plain, or Shared<T>.
- `IMPLICIT_SUPER_NEW_NOT_AVAILABLE` [error]: Implicit `: super!()` is available only when the base no-argument `new` is accessible.
- `INDEX_OPERATOR_MINIMUM_CORE_ONLY` [error]: the current profile index operator Stable law covers minimum indexing; effectful/custom index overloading is not enabled.
- `INDEX_OUT_OF_LOGICAL_DOMAIN` [error]: The index is outside the receiver's declared one-based logical domain.
- `INITIALIZED_LET_FIELD_CANNOT_BE_REASSIGNED_IN_POST_INIT_BODY` [error]: A post-init constructor body cannot reassign an already initialized `let` field.
- `INTERPOLATION_INDEX_OUT_OF_DOMAIN` [error]: The interpolation selector index is outside the value's logical index domain.
- `INTERPOLATION_MEMBER_NOT_FOUND` [error]: The selected interpolation member does not exist on the statically known value type.
- `INTERPOLATION_SECRET_REQUIRES_EXPLICIT_REDACTION` [error]: Secret/Redacted values require explicit redaction before interpolation.
- `INTERPOLATION_SHORTHAND_EXPECTED_IDENTIFIER` [error]: String interpolation shorthand requires an identifier after $.
- `INTERSECTION_BARE_CONTRACT_NOT_VALUE_TYPE` [error]: A bare Trait intersection is not a value carrier; use `any (...)` or a Facet.
- `INTERSECTION_MULTIPLE_CONCRETE_BASES_FORBIDDEN` [error]: A contract intersection may contain at most one concrete nominal base.
- `INTERSECTION_RESPONSIBILITY_CONFLICT` [error]: Intersection requirements impose incompatible ownership, effect, error, authority, or receiver responsibilities.
- `INTERSECTION_WITNESS_AMBIGUOUS` [error]: The contract intersection does not resolve one coherent witness per Trait.
- `ITERABLE_REMOVED_USE_TRAVERSAL_PROFILE` [error]: Iterable catch-all vocabulary is removed; use Iterator, Sequence, View, Stream, or Collection.
- `KEYABLE_REQUIRES_PLAIN_STABLE_HASH` [error]: Map/Set key must be Plain/stable-hash admissible or an explicitly approved key wrapper.
- `LAMBDA_BLOCK_REQUIRES_RET` [error]: Block lambda requires explicit ret on value paths.
- `LAMBDA_REQUIRES_FAT_ARROW` [error]: Lambda and executable match-arm bodies use =>.
- `LAW_BODY_ITEM_NOT_ADMITTED` [error]: Law bodies admit only pure predicate assertions.
- `LAYOUT_ARG_SEPARATOR_REQUIRES_ALL_NAMED_ARGUMENTS` [error]: Layout argument separator is only admitted in multiline all-named argument lists.
- `LAYOUT_SEPARATOR_AMBIGUOUS_CONTINUATION` [error]: This newline cannot be used as a labeled aggregate entry separator because the expression may continue.
- `LAYOUT_SEPARATOR_NOT_ALLOWED_HERE` [error]: A newline is not an element separator in this context.
- `LAZY_HIDDEN_FAILURE_CHANNEL_FORBIDDEN` [error]: A lazy binding cannot memoize a hidden failure channel; use an explicit Result value.
- `LAZY_INITIALIZATION_CYCLE` [error]: A lazy binding cannot directly or indirectly force itself before its first commit.
- `LAZY_LET_INITIALIZER_NOT_ADMITTED` [error]: The lazy initializer must be pure, synchronous, nonthrowing, authority-free, resource-free, and capture only reusable immutable values.
- `LEGACY_LOGICAL_AND_OPERATOR_REMOVED_ON_BOOL` [error]: `&&` on Bool is rejected because `&&` is bitwise in Deeplus.
- `LEGACY_LOGICAL_OR_OPERATOR_REMOVED_ON_BOOL` [error]: `||` on Bool is rejected because `||` is bitwise in Deeplus.
- `LEGACY_SHORT_CIRCUIT_AND_OPERATOR_REMOVED` [error]: `&&` is not logical AND in Deeplus; use `and then` for short-circuit or `and` for strict Boolean AND.
- `LEGACY_SHORT_CIRCUIT_OR_OPERATOR_REMOVED` [error]: `||` is not logical OR in Deeplus; use `otherwise` for short-circuit or `or` for strict Boolean OR.
- `LET_PROPERTY_CANNOT_HAVE_SETTER` [error]: let property cannot have setter.
- `LIBRARY_STATIC_BINDING_INITIALIZER_NOT_ADMITTED` [error]: A library top-level binding must be immutable, pure, synchronous, nonthrowing, effect/authority/resource/task/actor free, acyclic, and committed once.
- `LIBRARY_TARGET_CONTAINS_TOP_LEVEL_SCRIPT` [error]: A library target cannot contain script computation; split declarations into a library or select an executable script target.
- `LINEAR_ALGEBRA_STAR_PRODUCT_SPLIT` [error]: `*` is elementwise NumericArray multiplication, not rank-dependent matrix/vector product. Use `*+`, `**`, or a named API.
- `LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE` [error]: A List context may adapt an unsuffixed integer token or its direct prefix-minus mathematical candidate only when that candidate lies in the exact element domain.
- `LIST_LITERAL_ELEMENT_JOIN_FAILED` [error]: Without an explicit expected element type, an ordinary List literal requires one normalized element type; automatic heterogeneous Union inference is not performed.
- `LOCAL_IMPORT_RUNTIME_LOADING_FORBIDDEN` [error]: A block-local import is compile-time name visibility, never runtime module loading.
- `LOCAL_USE_RUNTIME_AUTHORITY_FORBIDDEN` [error]: A local use directive cannot acquire runtime authority or create evidence.
- `LOCAL_USE_TARGET_NOT_SCOPE_ADMISSIBLE` [error]: The local use target does not define an admissible lexical activation domain.
- `LOCAL_VALUE_BODY_REQUIRES_PATH_TOTAL_RET` [error]: A multi-statement local value body must produce a value with local ret on every reachable normal path.
- `LOCAL_WITNESS_NOT_CURRENT` [error]: Local witness remains Preview-design and is not current Stable source.
- `LOGICAL_INDEX_DOMAIN_MISMATCH` [error]: The receiver has no admitted built-in bracket domain, or the key, index, or axis type does not match that exact domain; conformance does not activate `[]`.
- `LOOP_LABEL_BREAK_NOT_STABLE` [error]: Label-based break is not Stable current surface; use break-chain.
- `LOOP_OUTCOME_BREAK_ARM_UNREACHABLE` [error]: The ::break arm is unreachable for this loop outcome descriptor.
- `LOOP_OUTCOME_COMPLETED_ARM_UNREACHABLE` [error]: The ::completed arm is unreachable for this loop outcome descriptor.
- `LOOP_OUTCOME_HANDLER_TARGET_MISMATCH` [error]: Only the final loop transfer target may run and observe its outcome handler.
- `LOOP_OUTCOME_MATCH_IS_STATEMENT_ONLY` [error]: Loop outcome match is a statement-only handler and does not produce a value.
- `LOOP_OUTCOME_MATCH_MUST_FOLLOW_LOOP` [error]: Subjectless loop outcome match must immediately follow a loop statement.
- `LOOP_OUTCOME_MATCH_NON_EXHAUSTIVE` [error]: Loop outcome match must cover ::completed and all reachable ::break payload domains.
- `LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE` [error]: Loop outcome match arms must use `::break(...)` or `::completed` patterns.
- `MAP_IS_NOT_NAMED_UNFOLD_SOURCE` [error]: Map keys are runtime values and cannot provide the static labels required by named unfolding.
- `MAP_NAMED_ARGUMENT_SPREAD_NOT_ALLOWED` [error]: Map values cannot be spread into named arguments because map keys are runtime values, not parameter labels.
- `MAP_NAMED_ARGUMENT_UNFOLD_REJECTED` [error]: Map values cannot be expanded into named arguments. Use a Record `${...}` for `**record`, or pass explicit named arguments.
- `MAP_NAMED_REST_UNFOLD_NOT_ALLOWED` [error]: Map values cannot feed named rest or named argument spread; use a Record with static labels.
- `MAP_PERCENT_LITERAL_REMOVED_USE_HASH_MAP` [error]: %{...} map literal is removed; use #map{...}.
- `MAP_UNFOLD_ELLIPSIS_NOT_CURRENT` [error]: `...expr` is not a current map unfold entry. Use `**expr` inside #map{...}.
- `MAP_UNFOLD_ONLY_IN_MAP_LITERAL` [error]: Map unfold `**expr` is allowed inside `#map{...}` but Map values cannot be spread as call named arguments. Record named-argument spread is a separate argument-list feature.
- `MATCH_GUARD_CONSUME_NOT_ALLOWED` [error]: match/@match guard may not consume or move tentative pattern bindings.
- `MATCH_GUARD_EFFECT_NOT_ALLOWED` [error]: match/@match arm guard must be pure and have effects {}.
- `MATCH_GUARD_NOT_BOOL` [error]: match/@match arm guard must have type Bool.
- `MATCH_GUARD_THROWS_NOT_ALLOWED` [error]: match/@match arm guard must not throw.
- `MATCH_NONEXHAUSTIVE_AFTER_GUARDS` [error]: Guarded arms do not count as unconditional coverage; add an unguarded arm or otherwise.
- `MATCH_NOT_EXHAUSTIVE` [error]: Match expression does not cover all cases of the subject type.
- `MATERIALIZATION_DUPLICATE_LABEL` [error]: A materialization label is supplied more than once after explicit and unfolded entries are normalized.
- `MATERIALIZATION_FIELD_PUN_DUPLICATE_LABEL` [error]: A field pun duplicates a label already supplied explicitly or by unfold.
- `MATERIALIZATION_FIELD_PUN_UNBOUND` [error]: A field-pun entry requires a same-name lexical binding.
- `MATERIALIZATION_REQUIRED_LABEL_MISSING` [error]: A required ConstructionRow label has no explicit, unfolded, or default value.
- `MATERIALIZATION_UNKNOWN_LABEL` [error]: A materialization label is not present in the target ConstructionRow.
- `MATRIX_PRODUCT_DIMENSION_MISMATCH` [error]: Matrix product inner dimensions must match statically or be checker-proven.
- `MATRIX_PRODUCT_REQUIRES_RANK2_MATRICES` [error]: `**` matrix product requires rank-2 matrix operands in Phase A.
- `MEASURE_NUMERIC_OPERATION_REQUIRES_ANCHOR_OR_EXPLICIT_UNIT` [error]: Measure plus bare number requires an explicit unit literal or enabled context anchor.
- `MEASURE_TO_NUMBER_REQUIRES_EXPLICIT_EXTRACTION` [error]: Measure does not convert to Number implicitly. Use `scalarIn 1[unit]`.
- `MEMBERSHIP_IN_PROTOCOL_NOT_SATISFIED` [error]: The right operand of `in` does not admit the checker-known membership protocol for the left operand.
- `MEMBER_DISPATCH_MARKER_ORDER_INVALID` [error]: Member dispatch markers must be ordered as *+.
- `MEMBER_EXTENSION_COLLISION` [error]: A member slot and an active extension candidate both apply to the same message call shape.
- `MEMBER_NOT_FOUND` [error]: No member, extension, or witness selector is available in the active lookup domain.
- `MISSING_EXPLICIT_RETURN` [error]: A normal non-Unit named-function path must return a value explicitly; Unit fallthrough is canonical.
- `MIXED_UNIT_ADDITION_REQUIRES_DISPLAY_UNIT_DECISION` [error]: Mixed-unit addition requires an explicit display-unit decision via `asUnit` or an enabled context anchor.
- `MODULE_IS_NOT_A_VALUE` [error]: A module/static path is not a runtime value.
- `MODULE_SIGNATURE_NOT_IMPLEMENTATION_RECEIPT` [warning]: A module signature declaration is language-design stable but does not imply product parser/checker support.
- `MULTIPLE_CANONICAL_UNITS_FOR_DIMENSION` [error]: A unit catalog may not declare multiple canonical units for one dimension.
- `MULTIPLE_NAMED_REST_PARAMETERS` [error]: A callable may declare at most one named rest parameter.
- `MULTIPLE_REPEATED_POSITIONAL_PARAMETERS` [error]: A callable may declare at most one repeated positional parameter.
- `MULTIPLE_ROOT_NEW_CONSTRUCTORS` [error]: Phase A permits only one root `new` per class profile.
- `MULTIPLE_UNIT_CONTEXT_ANCHORS_IN_OPERATION` [error]: Only one unit context anchor is allowed in one operation frame.
- `MUTABLE_ALIAS_REQUIRES_SHARED_WRAPPER` [error]: Mutable aliasing requires an admitted wrapper such as SharedMutex<T> or SharedCell<T>.
- `MUTABLE_MEMBER_FORBIDS_VARIANT_TYPE_PARAM` [error]: Mutable storage or write access makes this parameter invariant.
- `MUT_LITERAL_IS_FRESH_OWNER` [note]: #mut[...] constructs a fresh mutable collection owner.
- `NAMED_CONFORMANCE_AUTOMATIC_SEARCH_FORBIDDEN` [error]: A named conformance never participates in automatic witness search.
- `NAMED_CONFORMANCE_DUPLICATE_NAME` [error]: A named conformance identity must be unique for its nominal type, Trait and declaration scope.
- `NAMED_CONFORMANCE_NOT_AUTOMATIC` [error]: A named conformance never participates in automatic evidence search.
- `NAMED_CONSTRUCTOR_NOT_FOUND` [error]: No matching named constructor exists for `Type!name(...)`.
- `NAMED_REST_PARAMETER_MUST_BE_LAST` [error]: A named-rest parameter `options***: Record` must be the final parameter.
- `NAMED_REST_REQUIRES_RECORD_LABEL_SOURCE` [error]: Named rest and named-argument spread require a structural Record with static labels; Map is not admissible.
- `NAMED_UNFOLD_CONSUMING_REQUIRES_MOVE` [error]: A consuming named destination requires an ownership-preserving moved projection source.
- `NAMED_UNFOLD_REQUIRES_STATIC_PROJECTION_ROW` [error]: Named unfolding requires statically known labels from Record or a certified ProjectionRow.
- `NEGATIVE_IMPL_NOT_CURRENT` [error]: General negative impl remains Preview-design and is not current Stable source.
- `NESTED_DEF_CAPTURE_LIST_REQUIRED` [error]: A nested local function may use an outer local only when that capture is listed explicitly in its CaptureList.
- `NESTED_DEF_FORWARD_REFERENCE_FORBIDDEN` [error]: A local function is visible only after its declaration; forward reference and mutual-recursion groups are not current.
- `NESTED_IMPLICIT_LAMBDA_ARG_NONCANONICAL` [warning]: Nested implicit `@` lambda is noncanonical; name at least one parameter explicitly.
- `NONACTIVATABLE_DESIGN_PROJECTION_NOT_CURRENT` [error]: This feature is a nonactivatable design projection in the current profile package; ordinary source must reject it.
- `NONCOPYABLE_WORDING_DEPRECATED_USE_AFFINE` [warning]: Use affine ownership terminology instead of noncopyable wording.
- `NONE_IS_NOT_A_TYPE` [error]: None is not a type in Deeplus.
- `NOT_IF_MUST_BE_ADJACENT` [error]: `!if` must be adjacent with no whitespace/comment between `!` and `if`.
- `NOT_IF_NOT_ALLOWED_IN_CONSTRUCTOR_DELEGATION` [error]: Constructor delegation arms allow `if`, not `!if`.
- `NO_EXECUTABLE_ENTRY` [error]: An executable target requires exactly one `def#entry`, `def#entry#async`, or selected script root.
- `NULLARY_LAMBDA_BLOCK_REQUIRES_RET` [error]: A multi-statement nullary lambda block must use `ret` for its result.
- `NULLARY_LAMBDA_REQUIRES_EXPECTED_FUNCTION_CONTEXT` [error]: A nullary lambda without `=>` requires an expected zero-argument function type.
- `NUMARR_DIMENSION_MUST_BE_POSITIVE` [error]: NumericArray dimensions must be positive.
- `NUMARR_DIMENSION_STATIC_INT_REQUIRED` [error]: NumericArray dimensions must be StaticInt literals in Phase A.
- `NUMARR_ELEMENT_COUNT_MISMATCH` [error]: NumericArray literal element count does not match shape.
- `NUMARR_ELEMENT_NOT_NUMERIC` [error]: NumericArray element must be an admitted numeric type.
- `NUMARR_ELEMENT_NOT_PLAIN_NUMERIC` [error]: NumericArray element must satisfy numeric/plain/no-drop law.
- `NUMARR_ELEMENT_TYPE_REQUIRED` [error]: NumericArray type façade requires an element type.
- `NUMARR_EXPECTED_SHAPE_MISMATCH` [error]: NumericArray literal shape mismatches expected type.
- `NUMARR_INFIX_POWER_NOT_ADMITTED` [error]: NumericArray `A ^ B` infix power is not admitted; use `**`, `*+`, elementwise `^` where specified, or a named API.
- `NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE` [error]: NumericArray infix `^` elementwise power is Preview in the current profile. Stable NumericArray transpose is attached postfix `A^`; matrix multiplication is `**`.
- `NUMARR_LAYOUT_REQUIRES_FUTURE_PROFILE` [error]: Non-row-major or backend layout requires a future profile.
- `NUMARR_LIST_LITERAL_CONTEXT_REWRITE_UNSUPPORTED` [error]: Ordinary list literal is never context-rewritten into NumericArray.
- `NUMARR_LITERAL_ELEMENT_OUT_OF_RANGE` [error]: NumericArray literal element is outside element type range.
- `NUMARR_LITERAL_NO_WHITESPACE` [error]: No whitespace is allowed in NumericArray sharp-shape literal opener.
- `NUMARR_LITERAL_PREFIX_REQUIRED` [error]: NumericArray construction requires a sharp-shape literal prefix; ordinary List literal is not reinterpreted.
- `NUMARR_LITERAL_REQUIRES_EXPRESSIONS` [error]: NumericArray expression literal requires element expressions; #3[T] is type position only.
- `NUMARR_POSTFIX_TRANSPOSE_REQUIRES_NUMERIC_ARRAY` [error]: Postfix `^` transpose requires a NumericArray operand.
- `NUMARR_SHAPE_COLON_FORBIDDEN` [error]: NumericArray shape dimensions use comma, not colon.
- `NUMARR_SHAPE_INFERRED_VALUE_LITERAL_NOT_TYPE` [error]: #[...] is a value literal with inferred rank-1 shape, not a type façade.
- `NUMARR_SHAPE_SEMICOLON_FORBIDDEN` [error]: NumericArray shape dimensions use comma; semicolon separates slice axes.
- `NUMARR_TRANSPOSE_IS_NOT_ADJOINT` [warning]: `A^` is transpose, not complex adjoint; use `A ~ adjoint`.
- `NUMARR_UNKNOWN_SHARP_SHAPE_LITERAL` [error]: Unknown # shape literal head.
- `NUMARR_VECTOR_TRANSPOSE_REQUIRES_ORIENTATION` [error]: Rank-1 NumericArray transpose requires row/column orientation witness.
- `NUMERIC_ARRAY_CONTEXT_ANCHOR_NOT_FIRST_CLASS` [error]: `&expr` is an operand role marker in the NumericArray context-anchor MSP, not a first-class value.
- `NUMERIC_ARRAY_CONTEXT_ANCHOR_SINGLE_ANCHOR_REQUIRED` [error]: A NumericArray contextual operation may have at most one context-providing `&anchor` operand.
- `NUMERIC_ARRAY_ELEMENTWISE_REQUIRES_SAME_SHAPE` [error]: NumericArray elementwise arithmetic requires statically/proven same shape; implicit broadcasting is not performed.
- `NUMERIC_ARRAY_ELEMENTWISE_SHAPE_MISMATCH` [error]: Elementwise NumericArray arithmetic requires same static or checker-proven shape.
- `NUMERIC_ARRAY_SHAPE_MISMATCH_NO_IMPLICIT_BROADCAST` [error]: Ordinary NumericArray elementwise operations do not perform implicit broadcasting.
- `NUMERIC_LITERAL_OUT_OF_RANGE` [error]: Numeric literal is outside the representable or refined range.
- `NUMERIC_OPERATOR_CORE_REQUIRED` [error]: Numeric operator use requires the current profile numeric operator core law.
- `OPAQUE_RESULT_CONCRETE_TYPE_MISMATCH` [error]: some Trait function must return one hidden concrete type on all success paths.
- `OPEN_MEMBER_REQUIRES_INHERITABLE_TYPE` [error]: Open member requires an open, sealed, or abstract containing type.
- `OPERATOR_PRECEDENCE_TABLE_REQUIRED` [error]: Operator parsing requires the current profile operator precedence table.
- `OPTION_BARE_NONE_REMOVED` [error]: Bare None is not current Deeplus source; use `::none` with expected Option type or `Option<T>::none`.
- `OPTION_BARE_SOME_REMOVED` [error]: Bare Some(value) is not current Deeplus source; use `::some(value)` with expected Option type or `Option<T>::some(value)`.
- `OPTION_COALESCE_AFFINE_LHS_REQUIRES_MOVE` [error]: Extracting an affine payload requires moving the owned Option into `?:`.
- `OPTION_COALESCE_BORROWED_AFFINE_EXTRACTION` [error]: A borrowed Option cannot produce an owned affine payload through `?:`.
- `OPTION_COALESCE_CONDITIONAL_MOVE_NOT_STABLE` [error]: Moving an existing fallback local only on the none path requires a path-sensitive ownership profile that is not Stable.
- `OPTION_COALESCE_DOES_NOT_APPLY_TO_RESULT` [error]: `?:` cannot discard Result error evidence; handle Result explicitly.
- `OPTION_COALESCE_FALLBACK_TYPE_MISMATCH` [error]: The fallback must have the payload type T of the left Option<T>.
- `OPTION_COALESCE_LHS_TYPE_UNRESOLVED` [error]: The left Option payload type cannot be inferred; provide an expected type or full Option value.
- `OPTION_COALESCE_REQUIRES_OPTION_LEFT` [error]: The left operand of `?:` must have type Option<T> or T?.
- `OPTION_COLLECTION_ELEMENT_IMPLICIT_LIFT_NOT_ALLOWED` [error]: Collection elements are not implicitly lifted to Option<T>.
- `OPTION_IMPLICIT_LIFT_NOT_ALLOWED` [error]: T is not a subtype of Option<T>. Exactly one top-level `some` insertion is admitted only after an explicit local Option target is fixed; call arguments, returns, lambda results, collection elements, generic-driving inference, and nested lifts never insert it.
- `OPTION_NONE_REQUIRES_EXPECTED_TYPE` [error]: `::none` requires an expected Option<T> / T? type; otherwise use `Option<T>::none`.
- `OPTION_SOME_PAYLOAD_TYPE_MISMATCH` [error]: `::some` payload does not match the expected Option element type.
- `OTHERWISE_DUPLICATE_CLAUSE` [error]: A clause block or match may contain at most one `otherwise` arm.
- `OTHERWISE_MUST_BE_LAST` [error]: `otherwise` must be the last clause or match arm.
- `OTHERWISE_UNREACHABLE` [error]: The `otherwise` arm is unreachable because previous clauses already cover all cases.
- `OVERRIDE_VISIBILITY_CANNOT_NARROW` [error]: Overriding/fulfilling member cannot reduce base slot visibility.
- `OWNED_DOWNCAST_OWNER_NOT_PRESERVED` [error]: An owned downcast must return either the matched target owner or the original unmatched source owner.
- `OWNERSHIP_MODE_ADMISSION_FAILED` [error]: The borrow/inout/move mode violates exclusivity, lifetime, escape, suspension, or transfer responsibility.
- `OWN_CAST_REQUIRES_REUSABLE_SOURCE` [error]: Owning downcast via as? cannot duplicate affine ownership. Use owner-preserving consuming downcast.
- `PACKAGE_DECLARATION_RENAMED_TO_MODULE` [error]: `package` is not a Deeplus source namespace declaration; use `module`.
- `PATTERN_CONTROL_PARTIAL_BINDING_FORBIDDEN` [error]: Pattern-control failure must commit no partial binding or move.
- `PATTERN_CONTROL_REQUIRES_REFUTABLE_PATTERN` [error]: A pattern-binding control requires a refutable pattern.
- `PLACE_REPLACE_NOT_ADMITTED` [error]: replace requires one stable place, exclusive access, and a transaction that preserves exactly one old and one new owner.
- `PLAIN_HETEROGENEOUS_TOP_FORBIDDEN` [error]: `Plain` is not a heterogeneous dynamic top. Use an explicit union, JsonValue, Dyn, or a typed boundary wrapper.
- `PLAIN_IS_NOT_DERIVED_BY_ANNOTATION` [error]: Annotation cannot create Plain admissibility. Use Plain boundary type or satisfies Plain candidate.
- `PLAIN_IS_NOT_DYNAMIC` [error]: Plain is not a dynamic invocation boundary; use Dyn for dynamic inspection.
- `PLAIN_IS_NOT_JSONVALUE` [error]: Plain is not external JSON; use JsonValue for JSON data.
- `PLAIN_IS_NOT_LAYOUT_SAFE` [error]: Plain does not imply FFI-safe layout or byte-copy safety.
- `PLAIN_IS_NOT_RAW_LAYOUT` [note]: Plain is not a raw-layout, FFI-layout, byte-copy, or all-bit-pattern type.
- `PLAIN_IS_PLAINVALUE_ALIAS` [note]: Plain is a true alias of PlainValue.
- `PLAIN_OR_SHARED_REJECTS_LIFECYCLE_OWNER` [error]: Plain/Shared minimum profiles reject lifecycle owners.
- `PLAIN_REJECTS_CALLABLE` [error]: Callable values cannot be erased into Plain.
- `PLAIN_REJECTS_LIFECYCLE_OWNER` [error]: Lifecycle owner cannot be erased into Plain.
- `PLAIN_REJECTS_META_AUTHORITY` [error]: Reflection/meta authority values cannot be erased into PlainValue/Plain.
- `PLAIN_REJECTS_RAW_POINTER` [error]: Raw pointer/provenance values cannot be erased into Plain.
- `PLAIN_REJECTS_RESOURCE` [error]: Lifecycle/resource owners cannot be erased into PlainValue/Plain.
- `PLAIN_REJECTS_SHARED_HANDLE` [error]: Shared<T> is a shared owner/handle, not Plain data.
- `PLAIN_REJECTS_VIEW_OWNER_REGION` [error]: Plain rejects borrowed view owner-region values.
- `POSITIONAL_UNFOLD_REQUIRES_SEQUENCE_OR_TUPLE` [error]: `*expr` in an argument list requires Sequence evidence or a statically known tuple arity; NumericArray and runtime-sized collections do not supply positional call arity.
- `POSTFIX_TRANSPOSE_MUST_BE_ATTACHED` [error]: NumericArray postfix transpose is written attached as `A^`.
- `PREFER_AT_IF_FOR_MULTILINE_TERNARY` [warning]: Long or multiline ternary is clearer as @if.
- `PREFIXED_LITERAL_NO_WHITESPACE` [error]: No whitespace is allowed between #, prefix, and literal opener.
- `PREFIXED_LITERAL_PREFIX_REQUIRED` [error]: Stable prefixed literal families require their exact `#` prefix; the current prefix set is `#map`, `#set`, `#mut`, and `#bytes`.
- `PRIMARY_CONSTRUCTOR_BARE_PARAM_NOT_MEMBER` [error]: Bare primary constructor parameter is not a promoted member.
- `PRIMARY_CTOR_DOLLAR_PROMOTION_REMOVED_USE_LET_VAR` [error]: Primary constructor promotion uses let/var; $ and $* promotion are removed.
- `PRIMARY_CTOR_LAYOUT_REQUIRES_PROMOTED_FIELD` [error]: Primary-constructor layout separator is limited to promoted let/var fields.
- `PRIMARY_CTOR_VISIBILITY_SIGIL_MUST_ATTACH_TO_STORAGE` [error]: Primary-constructor promoted field visibility sigils must attach to `let` or `var`, for example `+let name: String`.
- `PRIMARY_GENERATED_NEW_CONSTRUCTOR_COLLISION` [error]: Primary-generated `new` collides with an explicit root `new` constructor.
- `PRIVATE_MEMBER_CANNOT_BE_OPEN` [error]: Private member cannot be open.
- `PROPERTY_VALUE_REQUIRES_REUSABLE_NODROP` [error]: Accessor property by-value result must be reusable, no-drop, and lifecycle-free in the Stable profile.
- `PROTOTYPE_DEEP_DERIVATION_REQUIRES_DEEP_CLONE_LAW` [error]: Deep prototype derivation requires a deep derivation/DeepClone law.
- `PROTOTYPE_DERIVATION_DOLLAR_REMOVED` [error]: Prototype derivation no longer uses $; write source!{...} or source!!{...}.
- `PROTOTYPE_DERIVATION_NO_WHITESPACE_BEFORE_DELTA` [error]: No whitespace is allowed between !/!! and the prototype delta block.
- `PROTOTYPE_DERIVATION_RESPONSIBILITY_MISMATCH` [error]: Prototype derivation must preserve the exact nominal type and satisfy its visible ConstructionRow and clone responsibilities.
- `PUBLIC_API_HIDDEN_WITNESS` [error]: Public API depends on a trait, associated item, or witness that is not public/exportable.
- `PURE_CALLABLE_MUTABLE_CAPTURE_FORBIDDEN` [error]: A #pure callable cannot capture var/inout/mutable shared state.
- `PURE_CALLABLE_PROFILE_VIOLATION` [error]: A #pure callable must be nonthrowing, effect-free, nonsuspending, authority-free, and free of mutable/resource captures.
- `PURE_FUNCTION_EFFECT_VIOLATION` [error]: def#pure body must have effects {}.
- `PURE_FUNCTION_THROWS_VIOLATION` [error]: def#pure body must throw Never.
- `QUALIFIED_EXTENSION_SELECTOR_REQUIRED` [error]: Ambiguity or collision requires an explicit qualified extension selector.
- `QUALIFIED_EXTENSION_SELECTOR_UNKNOWN` [error]: The qualified extension selector does not resolve to a visible extension function or set member.
- `QUARANTINE_EXPORT_REQUIRES_TYPED_IMMUTABLE_BINDING` [error]: A quarantine result may leave only through an explicitly typed immutable export.
- `QUARANTINE_OUTER_MUTATION_FORBIDDEN` [error]: A quarantine scope may not mutate an outer place.
- `QUARANTINE_RESOURCE_ESCAPE_FORBIDDEN` [error]: Pointers, authorities, borrows, resources, closures, tasks and actors may not escape a quarantine scope.
- `QUARANTINE_SUSPENSION_FORBIDDEN` [error]: A quarantine scope may not suspend, await, yield or spawn.
- `R0_GUARD_NOT_GUARD_SAFE` [error]: Declarative clause guards must be R0-safe: deterministic, sync, throws Never, effects {}, and built from the admitted R0 predicate subset.
- `R0_GUARD_USES_WORD_BOOLEAN_OPERATORS` [error]: R0 guard predicates use the Boolean words `not`, `and`, and `or`; symbolic `!`, `&&`, and `||` are different or non-current operator families.
- `R1_PROOF_PROFILE_OUTSIDE_INTRINSIC_SUBSET` [error]: The proof obligation is outside the stable R1 intrinsic-pure profile.
- `RANGE_CLOSED_END_NOT_ON_STEP_LATTICE` [lint]: Closed endpoint is not yielded by this step lattice.
- `RANGE_LITERAL_TYPE_POSITION_ONLY` [error]: Range literal refinement type is allowed only in type position.
- `RANGE_STEP_DIRECTION_MISMATCH` [error]: Range direction and step sign are inconsistent.
- `RANGE_STEP_ZERO` [error]: Range step must not be zero.
- `RANGE_UNSIGNED_DESCENDING_REQUIRES_SIGNED_DOMAIN` [error]: Unsigned descending ranges require an explicit signed delta/domain profile.
- `RAW_POINTER_ARITHMETIC_OPERATOR_FORBIDDEN` [error]: Use named unsafe pointer operations instead of ordinary arithmetic operators.
- `RAW_WITNESS_VALUE_NOT_CURRENT` [error]: Witness evidence is not an ordinary first-class type or value; the only source binding is an explicit borrowed `using name: witness Trait` parameter.
- `RCTS_API_DIGEST_INCOMPLETE` [error]: The public API digest omits a normalized responsibility residue.
- `RCTS_BITFIELD_DUPLICATE_SLOT_NAME` [error]: Bitfield and flags slot names must be unique.
- `RCTS_BORROW_REQUIRES_VIEW_RELEASE_CLEANUP` [error]: Borrow ownership requires view_release cleanup and cannot own drop cleanup.
- `RCTS_FACET_BORROW_REGION_REQUIRED` [error]: A borrowed Facet requires an explicit nonempty borrow region.
- `RCTS_FACET_BORROW_REQUIRES_VIEW_RELEASE` [error]: A borrowed Facet requires view_release cleanup owned by its region.
- `RCTS_FACET_EXISTENTIAL_SAFETY_REQUIRED` [error]: A Facet contract must be existential-safe under the selected mode.
- `RCTS_FLAGS_SLOT_WIDTH_MUST_BE_ONE` [error]: Every named flags slot has width exactly one.
- `RCTS_FLOW_STATE_EMBEDDED_IN_TYPE_DESCRIPTOR` [error]: Flow state belongs in Phi and cannot be embedded in a semantic type descriptor.
- `RCTS_GUARD_CALLABLE_INOUT_FORBIDDEN` [error]: A #guard callable cannot have an inout parameter.
- `RCTS_INTERSECTION_CONTRACT_MUST_BE_TRAIT` [error]: Every contract member of an intersection must resolve to a Trait.
- `RCTS_PURE_CALLABLE_EFFECTS_FORBIDDEN` [error]: A #pure callable must have an empty effect row.
- `RCTS_RESOURCE_REQUIRES_DROP_CLEANUP` [error]: Resource ownership requires drop_exactly_once cleanup.
- `RCTS_RESPONSIBILITY_AXIS_DROPPED` [error]: Normalization or API projection dropped a responsibility axis.
- `RCTS_V5_IMPOSSIBLE_FIELD_COMBINATION` [error]: The RCTS-V5 descriptor combines responsibility fields forbidden for this variant.
- `RCTS_V5_VARIANT_MISMATCH` [error]: The RCTS-V5 descriptor does not match its declared closed variant.
- `READONLY_VIEW_ESCAPE_FORBIDDEN` [error]: A readonly view cannot outlive, out-transfer, or survive move/drop of its owner.
- `RECEIVER_MODE_MISMATCH` [error]: The selected member or extension candidate requires a receiver mode that the call site cannot provide.
- `RECEIVER_OWNER_RESULT_MUST_BE_EXPLICIT` [error]: A consuming receiver result must explicitly return a Self-compatible owner.
- `RECEIVER_OWNER_RESULT_NOT_EXACTLY_ONCE` [error]: The consuming receiver owner must be returned exactly once on every successful path.
- `RECORD_ENTRY_SEPARATOR_REQUIRED` [error]: Same-line record entries require comma; multi-line entries may use LayoutEntrySep when unambiguous.
- `RECORD_FIELD_DUPLICATE` [error]: Record/schema literal contains a duplicate field key. Deeplus schema construction requires deterministic field ownership.
- `RECORD_NAMED_ARGUMENT_SPREAD_REQUIRES_RECORD` [error]: `**expr` in an argument list requires a structural Record with statically known labels.
- `RECORD_SPREAD_DUPLICATE_NAMED_ARGUMENT` [error]: Record spread creates a named argument label that is already supplied by another argument or spread.
- `RECORD_SPREAD_MISSING_REQUIRED_PARAMETER` [error]: Record spread plus explicit arguments do not provide all required named parameters.
- `RECORD_SPREAD_UNKNOWN_PARAMETER_LABEL` [error]: Record spread contains a field label that does not correspond to any parameter label in the selected callable.
- `RECORD_UNFOLD_LABEL_SET_NOT_STATICALLY_DISJOINT` [error]: A record spread in named arguments must be statically disjoint from explicit labels and other spreads.
- `RECORD_UNFOLD_MISSING_REQUIRED_LABEL_EVIDENCE` [error]: A record spread cannot satisfy required named parameters unless its label set is statically known.
- `REDUNDANT_ASSOCIATED_PROJECTION_PARENS_BEFORE_OPTIONAL` [lint]: Parentheses are redundant before an optional suffix on an associated projection; write `<T as Trait>::Assoc?`.
- `REDUNDANT_FINAL_VALUELESS_RETURN` [lint]: The final valueless return is redundant; normal Unit completion is canonical.
- `REFINEMENT_ASSERTION_MAY_DEFECT` [warning]: `as!` may raise RefinementAssertionDefect if the predicate fails.
- `REFINEMENT_DETAILED_CHECK_RETURNS_RESULT` [info]: Detailed validation uses `T::check(value)` or a named factory returning `Result<T, error E>`; `as?` returns `Option<T>`.
- `REFINEMENT_IMPLICIT_NARROWING_FORBIDDEN` [error]: Implicit narrowing to a refinement type is forbidden.
- `REFINEMENT_LITERAL_OUT_OF_RANGE` [error]: The literal value is outside the refinement range.
- `REFINEMENT_PREDICATE_EFFECT_FORBIDDEN` [error]: Refinement predicates must have effects {}.
- `REFINEMENT_PREDICATE_NOT_PHASE_A` [error]: This refinement predicate is outside Phase A.
- `REFINEMENT_PREDICATE_THROW_FORBIDDEN` [error]: Refinement predicates must throw Never.
- `REFINEMENT_PROOF_REQUIRED` [error]: The value is not statically known to satisfy the refinement. Use `as?` or `as!`.
- `REFINEMENT_R0_PREDICATE_NOT_ADMITTED` [error]: The refinement predicate is outside the closed pure and total R0 calculus.
- `REFINEMENT_RANGE_BOUND_STATIC_INT_REQUIRED` [error]: Range refinement bounds must be StaticInt literals in Phase A.
- `REFINEMENT_RANGE_EMPTY` [error]: The refinement range is empty because lower bound is greater than upper bound.
- `REFINEMENT_RESULT_REQUIRES_EXPLICIT_CHECK_BOUNDARY` [error]: Use an explicit check/factory boundary for Result-bearing refinement validation.
- `REFINEMENT_THIS_CAPTURE_FORBIDDEN` [error]: `this` in a refinement predicate is not an ordinary capturable variable.
- `REPEATED_POSITIONAL_PARAMETER_NOT_LAST_BEFORE_NAMED_REST` [error]: A repeated positional parameter must appear after ordinary positional parameters and before the optional named rest parameter.
- `RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT` [error]: Stable Resource inheritance requires a same-module sealed root and explicit cleanup budget.
- `RESPONSIBILITY_KIND_NOT_CLOSED` [error]: The descriptor does not inhabit exactly one admitted responsibility kind or mixes independent kind axes.
- `REST_ARGUMENTS_REQUIRE_COMMON_ELEMENT_TYPE` [error]: Repeated positional arguments must have a common element type unless an explicit union feature is admitted.
- `REST_ARGUMENTS_REQUIRE_EXPLICIT_UNION_FEATURE` [error]: Repeated and named-rest arguments must satisfy the current row type and position rules.
- `RESULT_ERROR_ARGUMENT_POSITION_INVALID` [error]: The `error E` type argument is admitted only in an error-channel parameter position such as Result<T, error E>.
- `RESULT_THROWS_CHANNEL_OVERLAP` [error]: The same recoverable error family cannot be exposed through both Result and throws for one operation.
- `RETURN_NOT_ALLOWED_IN_LAMBDA` [error]: return is for named functions; lambda blocks use ret.
- `RET_OUTSIDE_LAMBDA` [error]: `ret` is a local-result terminator only in a lambda block, a value match arm or declarative value-clause arm, or an `@if`/`@try`/`@scope` local-value block; it is not a named-function return.
- `SCHEMA_CONSTRUCTION_CANNOT_BYPASS_CONSTRUCTOR` [error]: `Type${...}` is typed schema construction and cannot bypass constructor-domain initialization or invariants.
- `SCHEMA_CONSTRUCTION_CANNOT_INVOKE_CONSTRUCTOR` [error]: Type${...} is schema construction and does not invoke constructor-domain def! bodies. Use Type!(...) or Type!name(...) for construction.
- `SCHEMA_CONSTRUCTION_FIELD_NOT_IN_SCHEMA` [error]: A Type${...} entry names a field that is not part of the visible schema.
- `SCHEMA_CONSTRUCTION_PRIVATE_FIELD_FORBIDDEN` [error]: Type${...} cannot initialize a private or inaccessible schema field.
- `SCHEMA_CONSTRUCTION_REQUIRED_FIELD_MISSING` [error]: A required schema entry is missing from Type${...}.
- `SCHEMA_CONSTRUCTION_RESOURCE_INITIALIZER_FORBIDDEN` [error]: Type${...} cannot construct resource/cleanup-bearing state unless the type exposes explicit schema authority.
- `SCHEMA_ENTRY_SEPARATOR_REQUIRED` [error]: Same-line schema construction entries require comma; multi-line entries may use LayoutEntrySep when unambiguous.
- `SCHEMA_PROJECTION_ROW_REQUIRED` [error]: Named unfolding requires a visible ProjectionRow for the schema value in this scope.
- `SCOPED_ACTIVATION_SPEC_DUPLICATE` [error]: A scoped activation group contains the same normalized spec more than once.
- `SCOPED_CALLABLE_ESCAPE_FORBIDDEN` [error]: A #scoped callable cannot be stored, returned, captured by an escaping continuation, or transferred to task/actor state.
- `SCOPED_CALLBACK_BORROW_ESCAPE_FORBIDDEN` [error]: #scoped callback borrow evidence cannot escape the receiving invocation region.
- `SCOPED_EXTENSION_ACTIVATION_AMBIGUOUS` [error]: The active extension sets contain equally applicable selectors; nesting depth is not a priority.
- `SCOPED_EXTENSION_USE_ORDER_IS_NOT_PRIORITY` [error]: Scoped extension activation is lexical; use order is not a priority or tie-breaker.
- `SCRIPT_FILE_IS_NOT_LIBRARY_IMPORT` [error]: A selected script unit is not an importable library computation; move reusable declarations to a library source.
- `SEALED_DIRECT_SUBCLASS_DISPOSITION_REQUIRED` [error]: A direct subclass of a sealed root must explicitly choose final, open, or sealed class.
- `SEALED_DIRECT_SUBCLASS_OUTSIDE_MODULE` [error]: A direct subclass of sealed class must be declared in the sealed root's module.
- `SELF_BANG_CONSTRUCTOR_DELEGATION_REMOVED_USE_HEADER_DELEGATION` [error]: Body-level `self!(...)` constructor delegation is not current source; use header delegation such as `: new(...)`.
- `SELF_UNAVAILABLE_IN_TYPE_SIDE_MEMBER` [error]: Type-side members declared with :: do not receive self.
- `SEQUENCE_REQUIRES_REPLAY_ITEM` [error]: Replayable sequence item must be Plain-admissible or an approved reusable handle.
- `SEQUENCE_UNFOLD_REQUIRES_STATIC_ARITY_FOR_FIXED_PARAMETERS` [error]: `*sequence` cannot target fixed parameters unless static arity evidence is known.
- `SEQUENTIAL_BOOLEAN_OPERAND_NOT_BOOL` [error]: `and then`/`otherwise` require Bool operands.
- `SETTER_VISIBILITY_CANNOT_EXCEED_GETTER` [error]: Setter visibility cannot exceed getter visibility.
- `SHAPED_LITERAL_EMPTY_ELEMENT` [error]: A shaped literal semicolon body must not contain an empty element.
- `SHAPED_LITERAL_EMPTY_SEGMENT` [error]: A shaped literal semicolon body must not contain an empty row/layer segment.
- `SHAPED_LITERAL_MIXED_NESTED_AND_SEMICOLON_FORBIDDEN` [error]: Explicit nested shaped initializer syntax and semicolon shaped body syntax cannot be mixed in the current profile MSP.
- `SHAPED_LITERAL_SEMICOLON_REQUIRES_EXACT_SHAPE` [error]: Semicolon shaped literal body separators are only admitted inside exact-shape `#StaticDimList[...]` NumericArray literals.
- `SHAPED_LITERAL_SEPARATOR_RANK_MISMATCH` [error]: A semicolon run of length k in an exact-shape NumericArray literal must close exactly k completed inner axes, with 1 <= k < rank; a trailing run must be rank - 1.
- `SHAPE_CONTEXT_ADAPTATION_FAILED` [error]: Operand cannot be adapted to the anchor shape context.
- `SHAREABLE_DOES_NOT_CREATE_ALIAS` [note]: Shareable proves alias observation safety, not alias creation. Use Shared<T> or another admitted shared owner to create aliases.
- `SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD` [error]: Minimum SharedMutex<T> cannot hide lifecycle or effectful cleanup owner.
- `SHARED_REJECTS_DROPPING_PAYLOAD` [error]: Minimum Shared<T> cannot own payload with user-visible cleanup.
- `SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN` [error]: NumericArray sharp-shape value literal must contain at least one element in the size-inferred or explicit-shape value form.
- `SHEBANG_MUST_BE_FIRST_LINE` [error]: Shebang `#!` is allowed only at the first line before any other source text.
- `SHEBANG_ONLY_ONE_ALLOWED` [error]: Only one shebang comment is allowed in a Deeplus source file.
- `SLICE_ANCHOR_OUTSIDE_SLICE` [error]: Slice anchors ^ and $ are valid only in slice-axis index context.
- `SLICE_AXIS_COUNT_MISMATCH` [error]: Slice axis count must match source rank.
- `SLICE_BOUND_ORDER_INVALID` [error]: Slice lower bound must not exceed upper bound for increasing ranges.
- `SLICE_BOUND_OUT_OF_RANGE_STATIC` [error]: Static slice bound is outside the source logical domain.
- `SLICE_FIRST_ANCHOR_OFFSET_REQUIRES_INTEGER` [error]: Offset from ^ must be an integer index expression.
- `SLICE_HALF_OPEN_RANGE_NONCANONICAL` [warning]: `i..<j` is accepted for explicit exclusive-end slices but is noncanonical in ordinary cases.
- `SLICE_LAST_ANCHOR_OFFSET_REQUIRES_INTEGER` [error]: Offset from $ must be an integer index expression.
- `SLICE_LAST_INDEX_DOLLAR_OUTSIDE_SLICE` [note]: This historical diagnostic is superseded by parser-owned `SLICE_ANCHOR_OUTSIDE_SLICE` and is not emitted by current Deeplus.
- `SLICE_LOGICAL_DOMAIN_REBASE_FORBIDDEN` [error]: A slice preserves selected logical coordinates; call an explicit rebase operation if new coordinates are required.
- `SLICE_MUTABLE_ALIAS_CONFLICT` [error]: Mutable slice would create an aliasing conflict.
- `SLICE_MUTABLE_ASSIGNMENT_UNSUPPORTED` [error]: Mutable slice assignment is not admitted in Phase A.
- `SLICE_RESULT_NONCONTIGUOUS_REQUIRES_EXPLICIT_COPY_FOR_BYTE_VIEW` [error]: Non-contiguous slice view requires explicit copy for byte-view/contiguous storage.
- `SLICE_SOURCE_REQUIRES_NUMERIC_ARRAY` [error]: Multi-axis slicing Phase A is NumericArray-only.
- `SLICE_VIEW_CROSSES_ISOLATION_WITHOUT_OWNED_COPY` [error]: A slice view cannot cross isolation without an explicit owned copy.
- `SLICE_VIEW_ESCAPES_OWNER` [error]: A slice view cannot outlive its source owner region.
- `SLICE_VIEW_REQUIRES_SHARED_SOURCE_PROFILE` [error]: Escaping read-only view requires a future Shared-source profile.
- `SOURCE_LEVEL_CONTEXT_ROLE_FORBIDDEN` [error]: ContextRole is checker-internal evidence, not a source trait.
- `SOURCE_LEVEL_UNIT_WITNESS_FORBIDDEN` [error]: UnitWitness is checker-internal evidence, not a user-implementable source trait.
- `SPECIALIZATION_NOT_CURRENT` [error]: Conformance specialization remains Preview-design and is not current Stable source.
- `STABLE_MEMBER_EXTENSION_COLLISION` [error]: Member/extension collision is a stable hard error in the current profile.
- `STATIC_ALIAS_CONFLICTS_WITH_LOCAL_BINDING` [error]: Static alias conflicts with an existing local binding.
- `STATIC_CALL_SHAPE_NOT_ADMITTED` [error]: The normalized call shape has a duplicate/unknown label, ambiguous ordering, or conflicting rest residue.
- `STATIC_EVIDENCE_SELECTOR_ESCAPE_FORBIDDEN` [error]: Static evidence cannot be stored, returned, captured, escaped or selected dynamically.
- `STATIC_EVIDENCE_SELECTOR_NOT_FOUND` [error]: The named static evidence selector is not visible for this type and Trait.
- `STATIC_INT_ARITHMETIC_OUT_OF_R0_PROFILE` [error]: StaticInt expression is outside the R0 static evaluator profile.
- `STATIC_INT_REQUIRES_COMPILE_TIME_LITERAL_OR_PROVEN_STATIC_VALUE` [error]: StaticInt requires a compile-time known integer.
- `STATIC_R0_EVALUATOR_NOT_SOURCE_FEATURE` [error]: R0 static evaluator is checker-internal and cannot be invoked as ordinary source code.
- `STATIC_SELECTOR_RESOLUTION_FAILED` [error]: The qualified `::` selector resolves to neither an enum case, type-side member, nor qualified extension selector.
- `STRICT_BOOLEAN_OPERAND_NOT_BOOL` [error]: `and`/`or` require Bool operands.
- `STRING_LITERAL_NOT_ASSIGNABLE_TO_CHAR` [error]: String is not implicitly assignable to Char.
- `STRING_MIXIN_NOT_SUPPORTED` [error]: String mixins are not supported in core Deeplus.
- `STRING_NOT_IMPLICITLY_CONVERTIBLE_TO_BYTES` [error]: String is not implicitly convertible to Bytes.
- `STRING_RENDERER_MUST_RETURN_STRING` [error]: String::render requires its trailing renderer closure to return String.
- `STRUCTURAL_CONFORMANCE_FORBIDDEN` [error]: Structural method matching does not create conformance.
- `STRUCTURAL_CONFORMANCE_NOT_CURRENT` [error]: The surface `structural conformance` is recognized but is not current Deeplus.
- `STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN` [error]: Structural shape coincidence does not form stable conformance.
- `STRUCTURED_BREAK_CHAIN_CANONICAL_FORM_REQUIRED` [error]: Structured break-chain uses chain spelling such as `break break` or `break break continue`; label/depth target forms are not the current profile canonical stable spelling.
- `STRUCTURED_BREAK_TARGET_AMBIGUOUS` [error]: Structured break/continue target is ambiguous; use a visible loop label or an unambiguous outer-loop depth.
- `STRUCTURED_LOOP_CONTROL_INVALID_CHAIN` [error]: Structured break-chain is invalid for the surrounding loop nesting.
- `SUPER_DELEGATION_MUST_BE_IN_CONSTRUCTOR_HEADER` [error]: `super!` constructor delegation must appear in the constructor header delegation clause.
- `SUPER_DELEGATION_NOT_EXHAUSTIVE` [error]: Root `new` must call exactly one super constructor on every successful path.
- `TERNARY_BRANCH_TYPE_MISMATCH` [error]: Ternary branch types do not have a permitted join.
- `TERNARY_CONDITION_NOT_BOOL` [error]: Ternary condition must have Bool type.
- `TERNARY_MISSING_COLON` [error]: Ternary expression requires a colon separating true and false arms.
- `TERNARY_QUESTION_REQUIRES_SPACING` [error]: Ternary `?` requires separating trivia from the condition and then-expression tokens.
- `THROWING_CLEANUP_FAILURE_POLICY_REQUIRED` [error]: A throwing cleanup path must preserve deterministic primary/suppressed failure order and cannot mask Cancellation as Error.
- `TOP_LEVEL_AWAIT_NOT_CURRENT` [error]: Top-level `await` is not admitted by the Stable script profile; use `def#entry#async`.
- `TOP_LEVEL_RETURN_NOT_ALLOWED` [error]: Top-level script computation cannot return; use an explicit entry function or process API.
- `TRAILING_CLOSURE_DEFAULT_SKIP_FORBIDDEN` [error]: Trailing closure syntax cannot skip defaulted parameters in Phase A.
- `TRAILING_CLOSURE_DOES_NOT_RELAX_CAPTURE_RULES` [error]: Trailing closure syntax does not relax capture, ownership, borrow, effect, throw, actor, or cleanup rules.
- `TRAILING_CLOSURE_OVERLOAD_AMBIGUOUS` [error]: Trailing closure call is overload-ambiguous; return type or source order must not select the overload.
- `TRAILING_CLOSURE_REQUIRES_FUNCTION_PARAMETER` [error]: A trailing closure must bind to a corresponding closure/function-typed parameter.
- `TRAIT_AMBIGUOUS_IMPORTED_WITNESS` [error]: Multiple visible canonical witnesses satisfy the same conformance obligation.
- `TRAIT_ASSOCIATED_PROJECTION_AMBIGUOUS` [error]: Associated projection is ambiguous without a trait witness context.
- `TRAIT_ASSOCIATED_PROJECTION_REQUIRES_TRAIT_CONTEXT` [error]: Associated projection requires an explicit witness/static trait context: write `<T as Trait>::Assoc`.
- `TRAIT_ASSOCIATED_PROJECTION_USES_COLON_COLON` [error]: Associated projection is a witness/static projection and uses `::`: write `<T as Trait>::Assoc`.
- `TRAIT_ASSOCIATED_REQUIREMENT_MISSING` [error]: Conformance body does not bind a required associated item.
- `TRAIT_ASSOCIATED_TYPE_CONSTRAINT_UNSATISFIED` [error]: Associated type equality constraint is not satisfied by the selected witness.
- `TRAIT_ASSOCIATED_TYPE_CYCLE` [error]: Associated type binding forms a cycle.
- `TRAIT_FINAL_SLOT_CANNOT_BE_OVERRIDDEN` [error]: A final trait witness slot cannot be overridden by a child trait or conformance.
- `TRAIT_FINAL_SLOT_CONFLICT` [error]: Distinct inherited final trait witness slots conflict in the same conformance surface.
- `TRAIT_FINAL_WITNESS_NOT_EFFECTIVELY_FINAL` [error]: A final trait witness requirement must be satisfied by an effectively final concrete witness.
- `TRAIT_MARKER_FAMILY_MISMATCH_WITH_CURRENT_DISPATCH_MARKER` [error]: Trait marker surface conflicts with the current dispatch marker family.
- `TRAIT_METHOD_AUTHORITY_TOO_WIDE` [error]: Witness method authority requirement is wider than the trait requirement allows.
- `TRAIT_METHOD_DUPLICATE_SLOT` [error]: Trait declares the same witness slot more than once.
- `TRAIT_METHOD_EFFECT_TOO_WIDE` [error]: Witness method effect row is wider than the trait requirement allows.
- `TRAIT_METHOD_ERRORSET_TOO_WIDE` [error]: Witness method ErrorSet is wider than the trait requirement allows.
- `TRAIT_METHOD_ISOLATION_MISMATCH` [error]: Witness method isolation responsibility does not match the trait requirement.
- `TRAIT_METHOD_MARKER_MUST_BE_ATTACHED` [error]: Trait method marker must be attached to the method selector with no whitespace/comment/newline gap.
- `TRAIT_METHOD_MARKER_NOT_OVERLOAD_KEY` [error]: Trait method markers are declaration metadata, not overload keys; marker-only duplicates are not allowed.
- `TRAIT_METHOD_MARKER_REQUIRED` [error]: Trait method declarations must carry a witness slot marker (`.`, `+`, `*.`, or `*+`).
- `TRAIT_METHOD_RECEIVER_MODE_MISMATCH` [error]: Witness method receiver mode is incompatible with the trait requirement.
- `TRAIT_METHOD_SUSPENSION_MISMATCH` [error]: Witness method suspension responsibility does not match the trait requirement.
- `TRAIT_METHOD_VIEW_ESCAPES_OWNER` [error]: Witness method returns a view that can escape the owner region without the required region exposure.
- `TRAIT_MISSING_WITNESS` [error]: cannot prove `{type} conforms {trait}`.
- `TRAIT_NOT_EXISTENTIAL_SAFE` [error]: Trait is not safe for any Trait existential packaging under the current bindings.
- `TRAIT_OPEN_DEFAULT_CONFLICT_REQUIRES_EXPLICIT_OVERRIDE` [error]: Inherited open default trait witness slots conflict; add an explicit `*+` or `*.` override.
- `TRAIT_OVERLAPPING_WITNESS` [error]: Multiple conformance declarations overlap for the same trait/type obligation.
- `TRAIT_OVERRIDE_MARKER_REQUIRES_INHERITED_SLOT` [error]: `*+` or `*.` requires a compatible inherited open trait witness slot.
- `TRAIT_OVERRIDE_SIGNATURE_INCOMPATIBLE` [error]: Trait witness slot override is not responsibility-compatible with the inherited slot.
- `TRAIT_REQUIREMENT_VISIBILITY_MISMATCH` [error]: Witness member visibility does not satisfy the trait requirement visibility.
- `TRAIT_SUPER_CYCLE` [error]: Supertrait graph contains a cycle.
- `TRAIT_SUPER_WITNESS_MISSING` [error]: Selected witness does not provide a required supertrait witness.
- `TRAIT_VARIANCE_POSITION_VIOLATION` [error]: Trait-only variance parameter appears in an invalid responsibility position.
- `TRY_REQUIRES_CATCH_OR_FINALLY` [error]: A statement `try` or value `@try` requires at least one `catch` clause or one `finally` clause.
- `TRY_EXPRESSION_STATEMENT_NOT_CURRENT` [error]: Statement `try` requires a block body; `try Expr` is not current Deeplus.
- `TUPLE_PATTERN_NOT_CURRENT` [error]: Tuple decomposition is not a current Pattern; parentheses group one Pattern only.
- `PATTERN_MULTIPLE_REST` [error]: A List pattern may contain at most one rest form.
- `PATTERN_REST_MUST_BE_FINAL_IGNORED` [error]: The only current List-pattern rest is one ignored `.._` in final position.
- `RECORD_PATTERN_DUPLICATE_FIELD` [error]: A Record pattern names the same required label more than once.
- `RECORD_PATTERN_UNKNOWN_FIELD` [error]: A Record pattern names a label outside the subject's statically known Record row.
- `RECORD_PATTERN_PRIVATE_FIELD` [error]: A Record pattern cannot project a label that is not visible in the current authority domain.
- `PATTERN_PRIVATE_REPRESENTATION_FORBIDDEN` [error]: Pattern decomposition cannot open a Class, Dyn, Facet, FFI, or opaque private representation.
- `REFUTABLE_PATTERN_IN_IRREFUTABLE_CONTEXT` [error]: This context requires the checker to prove the Pattern irrefutable for its admitted subject type.
- `ALIAS_PATTERN_OWNERSHIP_CONFLICT` [error]: A Pattern alias cannot coexist with a moved or exclusively borrowed descendant of the same subject.
- `PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH` [error]: Normally returning Pattern arms leave incompatible usable-place states at the join.
- `PATTERN_ANALYSIS_RESOURCE_LIMIT` [error]: Pattern analysis reached its deterministic resource limit before proving admission or exhaustiveness.
- `ACTOR_TURN_SELF_OR_CYCLIC_AWAIT_FORBIDDEN` [error]: An active actor turn cannot await a request whose statically proven dependency cycle requires the same actor turn to progress.
- `SHARED_CELL_REQUIRES_PLAIN_PAYLOAD` [error]: SharedCell<T> requires normalized Plain payload responsibility; Plain does not imply raw or lock-free representation.
- `SHARED_STATE_SCOPED_ACCESS_MAY_NOT_SUSPEND` [error]: A SharedCell observation or SharedMutex exclusive-access closure cannot suspend or escape its scoped access.
- `SHARED_MUTEX_REENTRANT_LOCK_FORBIDDEN` [error]: The current SharedMutex profile is non-reentrant; an owner cannot acquire the same mutex while its scoped lock is active.
- `SHARED_WRAPPER_DOES_NOT_IMPLY_TRANSFERABLE` [error]: Shared, SharedCell, and SharedMutex wrappers do not synthesize Transferable evidence for their payload.
- `ACTOR_CHANNEL_FIFO_ORDER_VIOLATION` [error]: Actor dequeue order does not preserve channel_sequence within one sender/receiver/mailbox-profile channel.
- `TUPLE_ORDINAL_OUT_OF_RANGE` [error]: The tuple ordinal exceeds the tuple arity.
- `TUPLE_ORDINAL_ZERO_FORBIDDEN` [error]: Tuple ordinals are one-based; `.0` is not admitted.
- `TYPED_MATERIALIZATION_REQUIRES_CONSTRUCTION_ROW` [error]: Typed materialization requires a checker-certified ConstructionRow for the target type.
- `TYPED_MATERIALIZATION_REQUIRES_TYPE_TARGET` [error]: The head of `target${...}` must resolve to a type with an admitted ConstructionRow; an ordinary expression target is not materializable.
- `TYPEOF_CALL_FORM_FORBIDDEN` [error]: `typeof(...)` is forbidden in Phase A; write `typeof <static-sample>` without call-like parentheses.
- `TYPEOF_MEASURE_UNIT_CATALOG_NOT_ACTIVE` [error]: Measure samples in `typeof` require a source-visible active UnitCatalog authority such as `use std::units::si`.
- `TYPEOF_OPERATOR_REQUIRES_TYPE_POSITION` [error]: `typeof` may appear only in type position, not as an expression or ordinary call.
- `TYPEOF_PUBLIC_API_PROJECTION_REQUIRED` [lint]: Public API use of `typeof` must preserve both compact spelling and expanded contract projection.
- `TYPEOF_SAMPLE_EFFECT_NOT_ALLOWED` [error]: `typeof` sample must not require runtime evaluation, effects, failure, provider calls, or authority execution.
- `TYPEOF_SAMPLE_HAS_NO_PRINCIPAL_TYPE` [error]: `typeof` sample has no single principal TypeResponsibilityDescriptor.
- `TYPEOF_SAMPLE_PROVIDER_AUTHORITY_FORBIDDEN` [error]: `typeof` samples cannot execute provider, Agent, reflection, unsafe, or FFI authority.
- `TYPEOF_SAMPLE_REQUIRES_STATIC_SAMPLE` [error]: `typeof` operand must be an admissible static sample, not a runtime expression.
- `TYPEOF_SAMPLE_RESOURCE_FORBIDDEN` [error]: `typeof` Phase A samples cannot allocate resources, invoke constructors, or introduce cleanup responsibility.
- `TYPE_BANG_REQUIRES_NEW_CONSTRUCTOR` [error]: `Type!(...)` resolves only to a matching `def! new(...)` constructor.
- `TYPE_DATA_REMOVED_USE_EXPLICIT_BOUNDARY` [error]: Data is not a plain-value erasure type name. Choose Plain, Dyn, JsonValue, or a domain-specific type; no automatic fix-it is provided.
- `TYPE_DECL_VISIBILITY_REQUIRED` [error]: A type-producing top-level declaration must explicitly use public, common, or private visibility.
- `TYPE_DESCRIPTOR_QUERY_RUNTIME_USE_FORBIDDEN` [error]: Compile-time type descriptors are not runtime reflective values.
- `TYPE_DOLLAR_IS_NOT_CONSTRUCTOR_ALIAS` [error]: `Type${...}` is typed schema construction, not a constructor-domain call. Use `Type!(...)` or `Type!name(...)` for nominal construction.
- `TYPE_DOLLAR_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_TYPE` [error]: `Type${...}` requires a resolved type with an admitted schema ConstructionRow and is never a constructor alias.
- `TYPE_DOLLAR_SCHEMA_DECLARATION_REQUIRED` [error]: Type${...} typed schema construction requires a visible schema declaration or schema descriptor.
- `TYPE_DOLLAR_SCHEMA_EFFECTFUL_DEFAULT_NOT_ALLOWED` [error]: Type${...} defaults must not hide effectful/provider evaluation.
- `TYPE_DOLLAR_SCHEMA_FIELD_MISSING` [error]: Type${...} is missing a required schema field.
- `TYPE_DOLLAR_SCHEMA_FIELD_REQUIRED` [error]: Typed schema construction requires all required schema fields or defaults.
- `TYPE_DOLLAR_SCHEMA_INVARIANT_VIOLATION` [error]: Type${...} violates a declared schema invariant or refinement.
- `TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD` [error]: Type${...} contains a label not declared by the schema descriptor.
- `TYPE_INTERNAL_PREDICATE_NOT_SOURCE_TRAIT` [error]: Checker-internal predicate cannot be implemented as an ordinary source trait.
- `TYPE_KEY_REQUIRES_COPYABLE_HASHABLE` [error]: Old Copyable & Hashable key law is removed; use Keyable.
- `TYPE_KEY_REQUIRES_KEYABLE` [error]: Map/Set key requires Keyable admissibility.
- `TYPE_KIND_HASH_SURFACE_REMOVED` [error]: Use public/private/common data/value/resource class, not class#data/class#value/class#resource.
- `TYPE_PLAINDATA_REMOVED_USE_PLAIN` [error]: `PlainData` removed spelling; use `Plain` or formal `PlainValue`.
- `TYPE_RELATION_SYMBOLIC_ALIAS_FORBIDDEN` [error]: Use derives/conforms keywords, not symbolic type relation aliases.
- `TYPE_SCHEMA_CONSTRUCTION_MUST_BE_SCHEMA_ONLY` [error]: Type${...} is typed schema construction, not nominal constructor-domain allocation or resource construction.
- `TYPE_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_AUTHORITY` [error]: Type${...} requires visible schema construction authority for the target type.
- `TYPE_SIDE_DISPATCH_MARKER_FORBIDDEN` [error]: def:: and let:: are type-side members, not instance dispatch slots; dispatch suffix markers are forbidden.
- `TYPE_SIDE_MUTABLE_REQUIRES_EFFECT_FOOTPRINT` [error]: var:: access/mutation must expose its effect footprint.
- `TYPE_SIDE_MUTABLE_REQUIRES_ISOLATION` [error]: var:: type-side mutable storage requires an explicit isolation law.
- `TYPE_SIDE_MUTABLE_STORAGE_UNSUPPORTED` [error]: var:: is recognized but unsupported in the default Stable profile; type-side mutable storage requires a separate effect/isolation law.
- `TYPE_TOKEN_RUNTIME_AUTHORITY_FORBIDDEN` [error]: A type token is compile-time identity only and cannot be used as a runtime reflective value or authority source.
- `UNFOLD_DUPLICATE_LABEL` [error]: Unfold/comprehension produced duplicate label without an admitted policy.
- `UNION_AUTOMATIC_JOIN_FORBIDDEN` [error]: Branch, return, overload, and generic inference cannot invent an anonymous union.
- `UNION_EXPECTED_TYPE_REQUIRED_FOR_INJECTION` [error]: Union injection requires an independently fixed expected union type.
- `UNION_INJECTION_AMBIGUOUS` [error]: The source value does not select one unique exact union alternative.
- `UNION_MEMBER_SUBSUMED` [error]: Phase-A closed union members must be pairwise disjoint; a subsumed alternative is forbidden.
- `UNION_VALUE_REQUIRES_NARROWING` [error]: A union value must be narrowed before member access, call, operator use, or extraction.
- `UNIT_BRACKET_ON_NON_LITERAL_IS_INDEXING` [error]: `[unit]` after a non-literal is indexing, not measure construction.
- `UNIT_CONTEXT_ANCHOR_NOT_A_VALUE` [error]: A unit context anchor is not a first-class value.
- `UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS` [error]: Unit context anchor requires a statically known unit witness.
- `UNIT_CONVERSION_APPROXIMATE_REQUIRES_POLICY` [error]: Approximate unit conversion requires an explicit approximation policy.
- `UNIT_CONVERSION_EXACT_RATIO_FORM_REQUIRED` [error]: Exact conversion must use an exact ratio form.
- `UNIT_CONVERSION_GRAPH_NOT_CLOSED` [error]: Unit conversion graph must be deterministic and closed for admitted static conversions.
- `UNIT_DECLARATION_DIMENSION_MISMATCH` [error]: Unit declaration conversion target has a dimension mismatch.
- `UNIT_DIMENSION_CANONICALIZATION_FAILED` [error]: The unit expression cannot be normalized to an exact dimension vector and rational scale under the Stable unit core.
- `UNIT_EXPR_REQUIRES_UNIT_NAMESPACE` [error]: Unit brackets contain only unit symbols, catalog qualifiers, powers, products, and divisions.
- `UNIT_LITERAL_BRACKET_MUST_BE_ATTACHED` [error]: No whitespace is allowed between numeric literal and unit bracket.
- `UNIT_PROVIDER_REQUIRES_UNIT_WITNESS_CARRIER` [error]: Provider endpoints must use unit witness carriers such as `1[USD]`.
- `UNIT_SYMBOL_NOT_ACTIVE` [error]: Unit symbol is known but no active catalog authority is in scope. Use the catalog, do not merely import it.
- `UNIT_WITNESS_LITERAL_MUST_BE_ONE` [error]: Unit witness argument must be `1[unit]`.
- `UNKNOWN_PREFIXED_LITERAL` [error]: Unknown #prefix literal; current prefixed literal families are #map, #set, #mut, and #bytes.
- `UNKNOWN_UNIT_SYMBOL` [error]: Unit symbol cannot be resolved in active unit catalogs.
- `UNSAFE_AUTHORITY_NOT_EFFECT` [error]: Unsafe authority must not be hidden as an ordinary runtime effect.
- `UNSAFE_REQUIRES_UNSAFE_BOUNDARY` [error]: Raw pointer, FFI, provider, or agent authority requires an explicit unsafe/authority boundary.
- `USE_SITE_VARIANCE_NOT_SUPPORTED_IN_PHASE_A` [error]: Use-site generic projection is not supported in the current profile.
- `VALUELESS_BREAK_MATCHED_AS_COMPLETED` [error]: A valueless break is ::break(()), not ::completed.
- `VARIANCE_NOT_SUPPORTED_FOR_ERRORSET_OR_EFFECTROW` [error]: ErrorSet and EffectRow parameters use row inclusion, not generic type variance.
- `VARIANCE_ONLY_ALLOWED_ON_TRAIT_TYPE_PARAMETER` [error]: the current profile Phase B generic variance is allowed only on trait/interface/view/function-like parameters.
- `VAR_COLON_COLON_NOT_CURRENT` [error]: var:: type-side mutable storage is not admitted in the clean current source profile; use explicit ordinary ownership, isolation, and effect responsibility.
- `WITNESS_COHERENCE_EVIDENCE_MISSING` [error]: Witness coherence requires a witness id, selected implementation id, coherence key, and at least one candidate implementation before selection.
- `WITNESS_DUPLICATE_IN_COHERENCE_DOMAIN` [error]: Multiple active witnesses exist for the same type/trait pair in one coherence domain.
- `WITNESS_IMPLEMENTATION_SELECTION_MISMATCH` [error]: The coherence key must equal the witness id and the sole selected candidate must equal the implementation id.
- `WITNESS_ORPHAN_RULE_VIOLATION` [error]: Witness declaration violates the trait/type ownership rule.
- `YIELD_RESPONSE_BINDING_NOT_ALLOWED_IN_GENERATOR` [error]: Yield guard and response binding are not both allowed in the same yield form.
- `ZERO_BASED_INDEX_NOT_CURRENT` [error]: Sequence index zero is not in the current one-based logical domain; use 1 for the first element.

## design_static

- `CROSSWALK_REFERENCE_UNRESOLVED` [error]: Feature-grammar crosswalk references must resolve to grammar productions, alternatives, examples, or smoke snippets.
- `EXAMPLE_BLOCK_EXPECTED_OUTCOME_REQUIRED` [error]: EXAMPLE_BLOCK_EXPECTED_OUTCOME_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `EXAMPLE_BLOCK_HASH_MUST_MATCH_MARKDOWN` [error]: EXAMPLE_BLOCK_HASH_MUST_MATCH_MARKDOWN: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `EXAMPLE_BLOCK_MANIFEST_REQUIRED` [error]: EXAMPLE_BLOCK_MANIFEST_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `EXAMPLE_BUCKET_UNKNOWN` [error]: EXAMPLE_BUCKET_UNKNOWN: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `EXAMPLE_CODE_BLOCK_NOT_CERTIFIED` [note]: Example code blocks are design review corpus items until production parser/checker receipt is attached.
- `EXAMPLE_ID_DUPLICATE_FORBIDDEN_R48` [error]: Example ids must be globally unique in the current profile managed review corpus.
- `EXAMPLE_MANIFEST_BLOCK_MANIFEST_PARITY` [error]: EXAMPLE_MANIFEST_BLOCK_MANIFEST_PARITY: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `EXAMPLE_MANIFEST_METADATA_MISMATCH` [error]: EXAMPLE_MANIFEST_METADATA_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `EXAMPLE_SOURCE_FEATURE_TAG_MISSING` [error]: Example or gallery source uses a feature surface that is missing from its manifest feature tags.
- `FEATURE_AUTHORITY_ENUM_UNKNOWN` [error]: Feature authority_set entry must be declared in declared_authority_enums.
- `FEATURE_DEPENDENCY_CYCLE` [error]: Feature registry dependency graph must be acyclic.
- `FEATURE_GRAMMAR_CROSSWALK_MISSING` [error]: FEATURE_GRAMMAR_CROSSWALK_MISSING: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `GALLERY_FRAGMENT_FEATURE_TAG_REQUIRED` [error]: GALLERY_FRAGMENT_FEATURE_TAG_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `GALLERY_FRAGMENT_MANIFEST_REQUIRED` [error]: GALLERY_FRAGMENT_MANIFEST_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `GALLERY_ID_DUPLICATE_FORBIDDEN_R48` [error]: Gallery ids must be globally unique in the current profile design gallery manifest.
- `GALLERY_MANIFEST_FRAGMENT_PARITY_REQUIRED` [error]: GALLERY_MANIFEST_FRAGMENT_PARITY_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `GALLERY_TRACE_METADATA_REQUIRED` [error]: GALLERY_TRACE_METADATA_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `GRAMMAR_METADATA_FEATURE_REF_MISSING` [error]: Grammar production metadata references a feature_id that is not present in the canonical feature registry.
- `LOOP_OUTCOME_MATCH_PRODUCTION_NOT_REACHABLE` [error]: LOOP_OUTCOME_MATCH_PRODUCTION_NOT_REACHABLE: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `PACKAGE_ARCHIVE_SHA_MISMATCH` [error]: PACKAGE_ARCHIVE_SHA_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `PRELUDE_SIGNATURE_CATALOG_REQUIRED` [error]: PRELUDE_SIGNATURE_CATALOG_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `PRIMARY_CTOR_PROMOTED_FIELD_ROUTE_UNREACHABLE` [error]: PRIMARY_CTOR_PROMOTED_FIELD_ROUTE_UNREACHABLE: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `PRODUCTION_PARSER_RECEIPT_REQUIRED_FOR_HANDOFF` [error]: PRODUCTION_PARSER_RECEIPT_REQUIRED_FOR_HANDOFF: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `PROJECTION_MARKDOWN_VALUE_DRIFT` [error]: Generated Markdown projection rows differ from the canonical JSON registry values.
- `RECEIPT_PRODUCT_LANE_OVERCLAIM` [error]: Publication receipt must keep product support lanes NOT_RUN unless an actual product receipt is attached.
- `RIGHTWARD_BINDING_SEMANTIC_NODE_FORBIDDEN` [error]: Rightward local binding must normalize to an ordinary local binding before semantic AST/HIR and MIR.
- `SANITY_RECALCULATION_MISMATCH` [error]: Sanity artifact count/line/byte fields must match the package produced on disk.
- `SMOKE_CORPUS_EXPECTATION_MISMATCH` [error]: SMOKE_CORPUS_EXPECTATION_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `SMOKE_EXPECTED_OUTCOME_REQUIRED` [error]: SMOKE_EXPECTED_OUTCOME_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `SOURCE_TRUTH_PROJECTION_CONFLICT` [error]: Spec text, Markdown projection, and machine registry disagree about which artifact is the canonical source for registry rows.
- `SPEC_PROJECTION_COUNT_DRIFT` [error]: Spec projection counts must match machine registry counts.
- `STABLE_EBNF_NONACTIVATABLE_HELPER_LEAK` [error]: STABLE_EBNF_NONACTIVATABLE_HELPER_LEAK: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `STABLE_FEATURE_PREVIEW_GATE_ANNOTATION_FORBIDDEN_R48` [error]: Stable design features must not be documented with `@feature(..., preview)` in current-accept examples.
- `STABLE_GRAMMAR_PROFILE_STATUS_DRIFT` [error]: STABLE_GRAMMAR_PROFILE_STATUS_DRIFT: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `STABLE_GRAMMAR_REQUIRES_PROFILE_AWARE_REFERENCES` [error]: STABLE_GRAMMAR_REQUIRES_PROFILE_AWARE_REFERENCES: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `SUPPORT_LANE_VOCABULARY_MISMATCH` [error]: SUPPORT_LANE_VOCABULARY_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `SUPPORT_MATRIX_FEATURE_PARITY_DRIFT` [error]: Production support matrix and feature registry have different feature ID sets or lane values.
- `TOKEN_PRECEDENCE_SCHEMA_PARITY_REQUIRED` [error]: The integrated Grammar, Frontend Model Pratt registry, lifecycle and current corpus must agree.
- `TRAIT_LAW_PROPERTY_TEST_RECEIPT_MISSING` [error]: TRAIT_LAW_PROPERTY_TEST_RECEIPT_MISSING: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `TYPE_RESPONSIBILITY_SCHEMA_VERSION_STALE` [error]: TYPE_RESPONSIBILITY_SCHEMA_VERSION_STALE: the current corpus, lifecycle, grammar, and machine authorities must agree.
- `UNSUPPORTED_FEATURE_ACCEPT_EXAMPLE_FORBIDDEN_R48` [error]: Recognized-unsupported features may appear only in rejected/negative examples with deterministic diagnostics.

## lexer

- `AND_THEN_KEYWORD_PAIR_MUST_BE_ADJACENT` [error]: `and then` must be an adjacent keyword pair in the same Boolean-control form.
- `AUTHORITY_TOKEN_NOT_IN_SCOPE` [error]: Required authority token is not in scope; EffectRow does not grant permission by itself.
- `BLOCK_COMMENT_DASH_RUN_STYLE_MISMATCH` [warning]: The nested block comment closes correctly, but its dash-run length differs from the corresponding opener.
- `BLOCK_COMMENT_NESTING_UNCLOSED` [error]: Nested block comment was not completely closed.
- `BYTES_LITERAL_UNICODE_ESCAPE_NOT_ALLOWED` [error]: Unicode escapes are not allowed in #bytes literals.
- `BYTE_LITERAL_NON_BYTE_SCALAR` [error]: A Bytes literal admits ASCII direct bytes and byte escapes only; use `\xHH` for arbitrary bytes.
- `CALLABLE_PROFILE_LITERAL_ATTACHMENT_REQUIRED` [error]: The final callable profile and literal { must be adjacent.
- `CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN` [error]: A callable nested in a type uses member visibility `+`, `-`, or `#`; a nested local function has lexical visibility. Top-level callables may use `public`, `common`, or `private`, and omission normalizes to `private`.
- `CHAR_LITERAL_EMPTY` [error]: Char literal cannot be empty.
- `CHAR_LITERAL_REQUIRES_ONE_SCALAR` [error]: A Char literal must decode to exactly one Unicode scalar value.
- `CHAR_LITERAL_SURROGATE_FORBIDDEN` [error]: A Unicode surrogate is not a Unicode scalar value and cannot form Char.
- `CONFORMANCE_DECLARATION_REQUIRES_CONFORMS_KEYWORD` [error]: Conformance declarations use `conformance Type conforms Trait`, not `impl Trait for Type` or `T: Trait`.
- `CONFORMS_REQUIRES_KEYWORD` [error]: Trait/capability conformance must use `conforms` in the stable profile.
- `CONTEXT_KEYWORD_RESERVED_FOR_CONTEXT_ROLE` [error]: `context` is recognized only in the Stable explicit context parameter, argument, and function-type role positions; it never requests ambient lookup.
- `DOC_BLOCK_COMMENT_UNTERMINATED` [error]: Documentation block comment opened by `//!!` was not closed by `!!//`.
- `DOC_COMMENT_NOT_ATTACHED_TO_DECL` [error]: Documentation comment is not attached to a documentable declaration.
- `EFFECT_ROW_UNION_TOKEN_REQUIRED` [error]: Effect-row alternatives require the visible | token.
- `ERROR_SET_UNION_TOKEN_REQUIRED` [error]: Error-set alternatives require the visible | token.
- `HARD_KEYWORD_MEMBER_REQUIRES_ESCAPE` [error]: A hard keyword used as a data member name must use the member-only escape, for example obj.\\class.
- `INTERPOLATION_BOUNDARY_OUTSIDE_PATH` [error]: A backtick is a no-output boundary only immediately after a shorthand interpolation path in interpolated-string mode.
- `INVALID_DIGIT_FOR_NUMERIC_RADIX` [error]: A digit is not valid for this numeric radix.
- `MALFORMED_NUMERIC_EXPONENT` [error]: A decimal exponent requires one or more digits after its optional sign.
- `MALFORMED_NUMERIC_RADIX_PREFIX` [error]: A 0b, 0o, or 0x radix prefix must be followed by at least one digit candidate before a suffix or delimiter.
- `MULTILINE_STRING_CLOSER_MUST_BE_OWN_LINE` [error]: A triple-quoted String closer must appear on its own line after indentation.
- `MULTILINE_STRING_OPENER_REQUIRES_NEWLINE` [error]: A triple-quoted String opener must be followed immediately by a physical newline.
- `NAMED_UNICODE_ESCAPE_UNKNOWN` [error]: Named Unicode escape is not known in the active Unicode name table.
- `NUMERIC_DIGIT_SEPARATOR_POSITION_INVALID` [error]: A numeric underscore must occur exactly between two digits of the same component.
- `NUMERIC_RADIX_FLOAT_NOT_CURRENT` [error]: Radix floating-point literals are not current Deeplus source; use a decimal float or an explicit conversion.
- `NUMERIC_SUFFIX_KIND_MISMATCH` [error]: The numeric suffix kind does not match the integer or decimal-float literal.
- `NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE` [error]: `null` is reserved recovery spelling, not a Deeplus value; use `::none` in an expected `Option` context or `Option<T>::none` explicitly.
- `OPTION_COALESCE_TOKEN_MUST_BE_ADJACENT` [error]: Option coalescing uses the adjacent compound token `?:`; separated `? :` belongs to ternary syntax.
- `RAW_MULTILINE_STRING_NOT_CURRENT` [error]: Raw multiline String syntax is not current; use the Unicode multiline String or `raw"..."`.
- `RAW_STRING_DELIMITER_INVALID` [error]: Raw String Phase A uses exactly the raw"..." delimiter family.
- `RAW_STRING_UNTERMINATED` [error]: A raw String literal must end with its closing double quote.
- `TYPE_TOKEN_HAS_NO_CONSTRUCTION_AUTHORITY` [error]: Type<T> token has no construction or metaclass invocation authority.
- `UNICODE_ESCAPE_INVALID_DIGIT` [error]: Unicode escape contains an invalid hex digit.
- `UNICODE_ESCAPE_OUT_OF_RANGE` [error]: Unicode scalar escape is above U+10FFFF.
- `UNICODE_ESCAPE_SURROGATE_NOT_ALLOWED` [error]: Unicode scalar escape cannot encode a surrogate.
- `UNKNOWN_NUMERIC_LITERAL_SUFFIX` [error]: Unknown numeric literal suffix; use the closed integer or float suffix table.
- `WORD_COMMENT_AMBIGUOUS_ATTACHMENT` [error]: A Word Comment attachment is ambiguous; use line structure or explicit placement so lossless CST attachment is deterministic.
- `WORD_COMMENT_EXPECTED_TEXT` [error]: Backtick word comment requires a non-empty word comment body.
- `WORD_COMMENT_LOSSLESS_TRIVIA_REQUIRED` [error]: Word Comment trivia must be preserved by parser, formatter, and LSP projections.
- `WORD_COMMENT_NOT_CALL_LABEL` [error]: A word comment is lossless trivia, not a named argument label or overload selector.
- `WORD_COMMENT_WHITESPACE_FORBIDDEN_AFTER_BACKTICK` [error]: Whitespace is not allowed immediately after a backtick word comment opener.

## parser

- `ANNOTATION_TARGET_REQUIRED` [error]: An annotation must be structurally attached to an annotatable declaration.
- `ASYNC_CALLABLE_LITERAL_NOT_CURRENT` [error]: #async callable literals are PREVIEW_DESIGN/nonactivatable.
- `ASYNC_FOR_OUTCOME_MATCH_NOT_ADMITTED` [error]: A `for await` loop does not own a subjectless outcome match in the current profile.
- `AT_EXACT_INTRODUCER_LINE_BREAK_FORBIDDEN` [error]: An exact @ introducer cannot cross a physical line break.
- `BARE_CALL_ARGUMENT_MUST_BE_ATOMIC_OR_PARENTHESIZED` [error]: The bare argument before a trailing closure must be atomic or parenthesized.
- `BARE_PARENLESS_ORDINARY_CALL_NOT_CURRENT` [error]: The surface `bare parenless ordinary call` is recognized but is not current Deeplus.
- `BODYLESS_ORDINARY_FUNCTION_NOT_CURRENT` [error]: Only a trait requirement or declared signature context may omit a function body.
- `BOUNDED_LIST_CALL_ARGUMENT_FORBIDDEN` [error]: A bounded list contains expressions only; call labels, evidence arguments and unfolding are forbidden.
- `CALLABLE_PROFILE_COMBINATION_NOT_ADMITTED` [error]: The callable profile combination is outside the closed Phase-A compatibility table.
- `CALLABLE_PROFILE_DUPLICATE` [error]: A callable profile may occur at most once in a cluster.
- `CALLABLE_PROFILE_ORDER_NONCANONICAL` [error]: Callable profiles must follow scoped, once, mut, pure-or-guard axis order.
- `CALLER_PROFILE_REMOVED_USE_SCOPED` [error]: #caller is not current; invocation-bounded nonescape uses #scoped.
- `CALL_ARGUMENT_SEPARATOR_REQUIRED` [error]: A comma is required unless this is the all-named newline layout; that layout admits only named or named-unfold arguments.
- `CARET_ATTACHMENT_AMBIGUOUS` [error]: Caret ownership is ambiguous; write attached `A^` for transpose or spaced `a ^ b` for power.
- `CAST_MODIFIER_MUST_BE_ADJACENT` [error]: The `?` or `!` cast modifier must be adjacent to `as`.
- `CLASS_BODY_REQUIRED` [error]: An ordinary, value, or resource class requires a body; only a data class may omit it.
- `CLASS_HASH_SEALED_SPELLING_REMOVED` [error]: The hash-combined sealed-class spelling is removed; write `sealed class`.
- `CLASS_INSTANCE_METHOD_REQUIRES_DISPATCH_MARKER` [error]: A class-like instance method requires exactly one dispatch marker: `.`, `+`, `*.`, or `*+`.
- `CLEANUP_LEGACY_SPELLING_REMOVED_USE_DEF_HASH_CLEANUP` [error]: Legacy destructor/drop spellings are not current; use def#cleanup().
- `CLEANUP_VISIBILITY_SIGIL_FORBIDDEN` [error]: def#cleanup is a lifecycle hook and cannot carry a member visibility sigil.
- `CONSTRUCTOR_OR_CLEANUP_DISPATCH_MARKER_FORBIDDEN` [error]: Constructors and def#cleanup declarations cannot use dispatch markers.
- `CONSTRUCTOR_REQUIRES_NAME` [error]: Constructor declarations require a name: write `def! new(...)` or `def! name(...)`.
- `CONSTRUCTOR_SPELLING_REMOVED_USE_DEF_BANG` [error]: Constructors use def! only; def#ctor, def#constructor, and $! are removed.
- `CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT` [error]: Custom operator declarations are nonactivatable Preview-design; express user-defined behavior with a named Trait method or API.
- `DECLARATION_TILDE_FORBIDDEN` [error]: A declared body selector has no leading tilde; retain tilde only on receiver calls or the top-level target separator.
- `DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL` [error]: A defer block is not current; register exactly one cleanup invocation.
- `DEFER_REQUIRES_SINGLE_INVOCATION` [error]: Defer requires exactly one direct, message, or type-side invocation.
- `DEF_HASH_DROP_REMOVED_USE_CLEANUP` [error]: def#drop is not current; lifecycle declarations use def#cleanup().
- `DIRECTED_COROUTINE_GROUP_REQUIRES_FEATURE_GATE` [error]: Feature `directed_coroutine_group` is PREVIEW_DESIGN/nonactivatable and has no current source gate.
- `DOTTED_STATIC_PATH_NOT_CURRENT` [error]: The surface `dotted static path` is recognized but is not current Deeplus.
- `DYN_INSPECTION_REQUIRES_FEATURE_GATE` [error]: Feature `dyn_inspection` is PREVIEW_DESIGN/nonactivatable and has no current source gate.
- `ENTRY_NOT_ALLOWED_IN_LIBRARY_SOURCE` [error]: A library source file cannot contain an entry declaration, including through an annotation attachment.
- `ENUM_CASE_COMMA_REQUIRES_SINGLE_LINE` [error]: Comma-separated enum cases must form one physical-line case-only list.
- `ENUM_CASE_KEYWORD_NOT_CANONICAL` [error]: Enum cases are declared directly inside enum bodies; remove the `case` keyword.
- `ENUM_CASE_SEPARATOR_MIXED` [error]: An enum body may not mix comma-list and layout separators for cases.
- `ENUM_MEMBER_KIND_NOT_ADMITTED` [error]: An enum body may contain cases followed by methods, accessors, and type-side members; stored fields, constructors, and lifecycle cleanup declarations are not admitted.
- `ESCAPED_MEMBER_ADJACENCY_REQUIRED` [error]: A member escape must be written as attached .\\name with no intervening trivia.
- `EXPECTED_IDENTIFIER_FOUND_WILDCARD` [error]: A lone underscore is WildcardToken and cannot name a declaration or member; use an underscore-prefixed Identifier such as `_name` when an identity is required.
- `EXPLICIT_WITNESS_ARGUMENT_REQUIRES_IDENTIFIER` [error]: After using, write either an explicit witness Identifier or conformance(Type conforms Trait); calls, literals, and member chains are not evidence arguments.
- `EXTENSION_AUTO_WITNESS_FORBIDDEN` [error]: Extension methods do not create trait witnesses.
- `EXTENSION_SET_STORED_MEMBER_FORBIDDEN` [error]: An extension set may declare behavior but cannot own a stored field, initializer, layout, or cleanup responsibility.
- `FFI_C_EXTERN_UNSAFE_SURFACE_MSP_REQUIRES_FEATURE_GATE` [error]: The extern#C unsafe declaration surface requires its dedicated Preview syntax gate.
- `FFI_MINIMUM_SOUND_PROFILE_REQUIRES_FEATURE_GATE` [error]: The FFI minimum-sound semantic profile requires its dedicated Preview profile gate.
- `FIELD_DISPATCH_MARKER_FORBIDDEN` [error]: Stored fields are nonvirtual and cannot carry a dispatch marker.
- `FLOW_BINDING_TARGET_MUST_BE_NEW_LOCAL` [error]: A rightward flow binding target must be a fresh statement-local $name[: Type] or $$name[: Type], not a place/member/index/pattern.
- `FORWARD_GROUP_WILDCARD_NOT_CURRENT` [error]: Grouped forwarding requires an explicit finite member list; wildcard forwarding is not current.
- `FUNCTION_BODY_REQUIRES_BLOCK_RETURN_OR_CLAUSE` [error]: A named function body must be a block, explicit `= return Expr` shorthand, or declarative clause body; bare `= Expr` is not current.
- `FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN` [error]: One-line named function body must use = return expr, not = expr.
- `GRAMMAR_ALTERNATIVE_ACTIVATION_METADATA_REQUIRED` [error]: A grammar alternative that routes to preview, preview-design, recognized-unsupported, or tooling-only syntax must carry explicit activation metadata.
- `GUARDED_LET_EXIT_MUST_BE_UNCONDITIONAL` [error]: A guarded-let failure branch requires one direct unconditional terminating exit.
- `HASH_ROLE_PHYSICAL_LINE_BREAK_FORBIDDEN` [error]: A role marker may contain horizontal trivia but cannot cross a physical line break between `#` and its role word.
- `INLINE_CONFORMANCE_HEADER_NOT_CURRENT_USE_CONFORMANCE_DECL` [error]: Inline class/enum header conformance is not current; conformance is an explicit nominal declaration.
- `INDEX_SUFFIX_REQUIRES_AXIS` [error]: An index suffix requires a scalar index, a bounded slice range whose bounds may use `^` or `$`, or an admitted NumericArray `*` axis; empty `[]` never implies a full slice.
- `INTERPOLATION_COMPLEX_EXPRESSION_REQUIRES_BRACES` [error]: Complex interpolation expression requires ${...}.
- `INTERPOLATION_FORMAT_REQUIRES_BRACED_FORM` [error]: Interpolation format spec is admitted only in braced form ${expr:format}.
- `LAMBDA_PARAM_LIST_PARENS_NOT_CURRENT` [error]: Lambda parameters are written directly before `=>`; write `{ x: T => ... }`.
- `LAZY_BINDING_USE_HASH` [error]: The current lazy-binding spelling is `let#lazy`; `let@lazy` is recovery-only.
- `MAP_UNFOLD_SPELLING_AMBIGUOUS` [error]: Map unfold spelling is `**expr` in admitted `#map{...}` unfold positions; `...expr` map unfold is not current source in the current profile.
- `MATCH_ARM_SINGLE_GUARD_ONLY` [error]: A match arm admits at most one `if` or attached `!if` guard.
- `MATCH_EXPR_REQUIRES_AT_PREFIX` [error]: A value-producing match expression must use `@match`; bare `match` is statement-only.
- `MIXED_STRICT_AND_SEQUENTIAL_BOOLEAN_REQUIRES_PARENTHESES` [error]: Mixing `and` with `and then` requires parentheses.
- `MIXED_STRICT_OR_SEQUENTIAL_BOOLEAN_REQUIRES_PARENTHESES` [error]: Mixing `or` with `otherwise` requires parentheses.
- `MODIFIER_NOT_ADMITTED_FOR_OWNER` [error]: This modifier or role sequence is not admitted for the owning declaration or expression.
- `MODULE_STATIC_INITIALIZER_NOT_CURRENT` [error]: Module-level `static {}` is nonactivatable Preview-design; use static-admissible top-level let or an explicit lifecycle API.
- `MULTIPLE_GUARD_CLAUSES_NOT_CURRENT` [error]: This owner admits at most one `if` or `!if` GuardClause.
- `MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT` [error]: At most one closure may appear as an unlabeled trailing suffix.
- `NAMED_ARGUMENT_EQUALS_REMOVED_USE_COLON` [error]: Named arguments use `label: value`; `label = value` is not current call syntax.
- `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR` [error]: Double-star is not a named-rest parameter or function-type residue; use attached `***`. Double-star remains the named-unfold prefix.
- `NEGATED_RELATION_MUST_BE_ADJACENT` [error]: The `!` prefix must be adjacent to `in`, `is`, or `if` in a negated relation or guard.
- `NESTED_DEF_VISIBILITY_FORBIDDEN` [error]: A nested local function has lexical visibility and cannot carry a public/private/common modifier.
- `NESTED_TERNARY_REQUIRES_PARENTHESES_OR_AT_IF` [warning]: Nested ternary should use parentheses or @if for readability.
- `OLD_DOTTED_BITWISE_OPERATOR_REMOVED` [error]: Old dotted bitwise operators .&. .|. .^. .~. are not current source; use && || ^^ ~~.
- `OPTIONAL_CALLABLE_INVOCATION_NOT_CURRENT` [error]: Optional callable invocation `callee?(args)` is not current Deeplus source. Use explicit Option flow.
- `OPTIONAL_CHAINING_NOT_CURRENT` [error]: Optional chaining is not current Deeplus source; use explicit Option handling, match/@match, if-let, or library combinators.
- `OPTIONAL_SUFFIX_REPEATED` [error]: A compact optional suffix may occur once; write Option<T?> for nested optionality.
- `OPTIONAL_TYPE_SUFFIX_REQUIRES_NO_WHITESPACE` [error]: The ? in T? must attach with no whitespace.
- `OPTION_COALESCE_CONTROL_TRANSFER_FALLBACK_FORBIDDEN` [error]: The fallback of `?:` is a value expression, not return/throw/break/continue control transfer.
- `POSTFIX_MUTATION_OPERATOR_NOT_CURRENT` [error]: Prefix/postfix increment and decrement expressions are not current Deeplus; write an explicit assignment.
- `PREFIX_FUNCTION_PROFILE_REMOVED_USE_DEF_HASH` [error]: Prefix async/guard/entry def spelling is not current; use the owner-appropriate closed def# introducer.
- `PREFIX_UNARY_POWER_BASE_REQUIRES_PARENTHESES` [error]: Unary-prefixed power base requires explicit parentheses.
- `PREVIEW_ALTERNATIVE_LEAKS_THROUGH_STABLE_PARENT` [error]: A stable/ordinary grammar parent includes a gated alternative without alternative-level metadata.
- `PREVIEW_GATE_DEPENDENCY_MISSING` [error]: A #preview list must explicitly contain the transitive closure of every PREVIEW dependency.
- `PREVIEW_GATE_DUPLICATE_FEATURE` [error]: A #preview feature list must contain each feature id exactly once.
- `PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE` [error]: A #preview entry may name only a PREVIEW feature whose source_activation is explicit_feature_gate; PREVIEW_DESIGN is nonactivatable.
- `PREVIEW_GATE_PLACEMENT_INVALID` [error]: The Preview gate must be the first token of a library/executable source or the first non-shebang token of a script, before ModuleDecl and source items.
- `PREVIEW_GATE_UNKNOWN_FEATURE` [error]: Every #preview entry must name a feature present in the current feature registry.
- `PROTOTYPE_DELTA_REQUIRES_FEATURE_GATE` [error]: Feature `prototype_delta` is PREVIEW_DESIGN/nonactivatable and has no current source gate.
- `PROTOTYPE_DERIVATION_BRACE_FORM_REQUIRED` [error]: Prototype derivation must use source!{...} or source!!{...}; dollar-brace and unbraced cover forms are not current source or invalid.
- `QUARANTINE_SCOPE_NOT_ACTIVATABLE` [error]: Dynamic/unsafe quarantine scope is a nonactivatable design probe, not current source.
- `RANGE_OPERATOR_SPELLING_NOT_CURRENT` [error]: Current range and slice delimiters are `..` and `..<`; `...` belongs only to repeated-positional or comprehension-unfold structural owners, and `..>` is rejected recovery spelling.
- `SCOPED_ACTIVATION_REQUIRES_IN_BLOCK` [error]: A scoped import/use group must be followed by `in` and a block.
- `SCOPED_IMPORT_BLOCK_IS_STATEMENT_ONLY` [error]: A scoped import block is a statement and cannot produce a value.
- `SCOPED_USE_BLOCK_IS_STATEMENT_ONLY` [error]: A scoped use block is a statement and cannot produce a value.
- `SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT` [error]: A script source file cannot contain an explicit entry declaration; choose the executable root for an explicit entry.
- `SET_HASH_BRACE_LITERAL_REMOVED_USE_HASH_SET` [error]: #{...} set literal is removed; use #set{...}.
- `SLICE_EMPTY_RANGE_FORBIDDEN_USE_STAR` [error]: A slice range requires both bounds; use ^/$ for endpoints, or * for an admitted NumericArray full axis.
- `SOURCE_ROLE_CARRIER_CONFLICT` [error]: A normalized project-relative path occurs more than once, or the manifest and external carrier assign different source roles to one file.
- `SOURCE_ROLE_ENTRY_COUNT_MISMATCH` [error]: The parser's explicit entry-declaration count must equal the source front end's selected entry-target count for the same normalized source root.
- `SOURCE_TRAILING_TOKENS` [error]: The selected source root did not consume all input.
- `STANDALONE_BANG_NOT_CURRENT` [error]: Standalone `!expr` is not current Deeplus Boolean negation; use `not expr`.
- `STATIC_CLASS_DECLARATION_NOT_CURRENT` [error]: Top-level `static class` has no current Deeplus declaration route.
- `STATIC_FUNCTION_DECLARATION_NOT_CURRENT` [error]: Top-level `static def` has no current Deeplus declaration route.
- `STATIC_SPELLING_REMOVED_USE_COLON_COLON` [error]: def#static/def#class spelling is removed; use def::.
- `STRUCTURAL_PROTOTYPE_EXTENSION_REQUIRES_FEATURE_GATE` [error]: Feature `structural_prototype_extension` is PREVIEW_DESIGN/nonactivatable and has no current source gate.
- `SYNC_CALLABLE_LITERAL_MARKER_NOT_CURRENT` [error]: #sync is redundant and not a current callable literal profile.
- `TOP_LEVEL_BINDING_NOT_ALLOWED_IN_EXECUTABLE_SOURCE` [error]: Executable source files do not admit top-level let/var bindings; initialize state inside the selected entry.
- `TOP_LEVEL_STATEMENT_REQUIRES_SCRIPT_ROOT` [error]: A top-level executable statement is admitted only by the selected script root; library and executable roots reject it.
- `TRAILING_CLOSURE_SUFFIX_REQUIRED` [error]: Trailing closures bind only to a suffix of formal closure parameters.
- `TRAIT_ASSOCIATED_ITEM_DISPATCH_MARKER_FORBIDDEN` [error]: A non-method associated requirement cannot carry a Trait witness marker.
- `TRIPLE_STAR_ONLY_FOR_NAMED_REST_PARAMETER_OR_TYPE_RESIDUE` [error]: Triple-star is admitted only as the attached named-rest parameter suffix or function-type named-rest residue; named unfold uses prefix `**`.
- `UNIT_EXPONENT_REQUIRES_STATIC_INT` [error]: A unit exponent must be a signed decimal StaticInt literal; a runtime expression, radix literal, suffixed integer, decimal point, or exponent-form number is not admitted.
- `UNIT_MIDDLE_DOT_RECOVERY_ONLY` [error]: Unit multiplication uses `*`; the middle dot is recognized only for recovery.
- `UNIT_MULTIPLICATION_USE_STAR` [error]: The current unit multiplication spelling is `*`; the middle dot is recovery-only.
- `WEAK_ATOMIC_ORDERING_REQUIRES_FEATURE_GATE` [error]: Feature `weak_atomic_ordering` is PREVIEW_DESIGN/nonactivatable and has no current source gate.
- `WHERE_COLON_RELATION_AMBIGUOUS` [error]: `where T : U` is ambiguous in the current profile. Use `where T conforms Trait` for conformance or an explicit future subtype-bound relation.
- `WHERE_COLON_TRAIT_CONSTRAINT_NOT_CURRENT` [error]: The surface `where T : Trait` is recognized but is not current Deeplus.

## provider

- `BITFIELD_LAYOUT_DIGEST_INCOMPLETE` [error]: The bitfield layout digest omits a normative layout component.
- `TYPED_PROVIDER_NONDETERMINISTIC_OUTPUT` [error]: A typed provider must produce deterministic, content-addressed output.

## runtime

- `BITFIELD_RESERVED_BITS_NONZERO` [error]: Checked raw conversion rejected nonzero reserved bits.
- `LAZY_REENTRANT_FORCE` [error]: Reentrant forcing of an initializing lazy binding is rejected deterministically.
- `LAZY_SINGLE_COMMIT_VIOLATION` [error]: Concurrent lazy forcing must publish exactly one immutable committed value.

# Part XII — Post-PR16 Nonactivatable Preview Design

> Status fence: this Part is the current preimplementation Preview design snapshot. Deeplus grammar, syntax, and language design remain unsettled; current behavior remains authoritative. Every successor rule below is nonactivatable, implementation begins only after Deeplus 0.1.3 is established, all 22 feature P1 items remain OPEN, and all 15 product lanes remain NOT_RUN.

<!-- POST_PR16_UNIT_BEGIN:TC-R001 -->
### TC-R001 — requirement and overload identity

`RequirementId` is `(OriginalDeclaringTraitId, RequirementKind, MemberName, CanonicalOverloadSlotKey)`. The slot key contains canonical binder arity/kinds, receiver channel, ordered external labels and normalized input types, channel kinds, and repeated/rest shape. Result type, responsibility-profile-only differences, marker state, defaults, local names, order, and generated ordinals do not create a slot. Those excluded obligations remain in `RequirementContract`. Equal IDs are duplicates; return-only or callable-profile-only overloads reject; alpha-renaming and declaration/file/import permutations preserve identity.
<!-- POST_PR16_UNIT_END:TC-R001 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R002 -->
### TC-R002 — unique parent evidence

Every child record has exactly one `SupertraitLink` for each direct parent goal and reuses the sole canonical parent record. An implied parent may be materialized only once and all diamond paths reuse it. A child cannot own a shadow parent record or replace a parent-owned binding. A permitted redundant compatible spelling normalizes to the parent's exact binding; an incompatible replacement rejects deterministically. Parent/refinement evidence is acyclic, and associated bindings obey the same rule. Current marker semantics are not reinterpreted; their successor mapping is `OPEN_P1`.
<!-- POST_PR16_UNIT_END:TC-R002 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R003 -->
### TC-R003 — canonical conformance identity

A ground conformance is identified by normalized target, normalized instantiated Trait, and coherence-domain authority—not spelling, alias path, location, route, or discovery order. Equal keys intern to one record or incompatible summaries reject. DIRECT, current lowercase `via`, and any future route cannot create distinct semantic conformances for one ground key.
<!-- POST_PR16_UNIT_END:TC-R003 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R004 -->
### TC-R004 — global coherence

An admitted image has at most one applicable record and one compatible binding for each required `RequirementId`. Multiple records, requirement bindings, associated bindings, or parent records are errors; source, import, allocation, schedule, and link order never select a winner.
<!-- POST_PR16_UNIT_END:TC-R004 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R005 -->
### TC-R005 — locality and retroactivity

A declaring package owns the target nominal type or the Trait. A third package cannot conform a foreign target to a foreign Trait. The owned side is recorded and link-verified. Module placement inside an owning package remains subject to visibility. Expression-preserving alternatives are an owned nominal wrapper, an owned Trait, or upstream ownership.
<!-- POST_PR16_UNIT_END:TC-R005 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R006 -->
### TC-R006 — overlap

Normalized target and Trait heads overlap when jointly unifiable to any ground key. Positive conditions do not prove head disjointness in the initial profile. Every potentially co-linkable overlap rejects. Exact summaries deduplicate only when semantic digests and authority identities are equal.
<!-- POST_PR16_UNIT_END:TC-R006 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R007 -->
### TC-R007 — conditional construction

Every binder is substituted and normalized before ground identity, contracts, projections, and parent goals form. Evidence is finite. A recursive cycle is admitted only when every cycle edge has a registered, machine-checkable strict decrease; otherwise it rejects. Failed conditions mean not applicable and cannot authorize an overlapping fallback. Runtime values and order are not conditions.
<!-- POST_PR16_UNIT_END:TC-R007 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R008 -->
### TC-R008 — no specialization or priority

Specificity, source/import/module/package order, annotations, and fallback priority cannot resolve overlap. Specialization is rejected in the initial profile. Any future proposal needs an explicit partial order, unique-maximal proof, separate-compilation proof, and deterministic diagnostics.
<!-- POST_PR16_UNIT_END:TC-R008 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R009 -->
### TC-R009 — substitution stability

Alpha-equivalent schemas and substitutions yield equal heads, requirement IDs, and ground keys. Transparent aliases normalize; nominal wrappers remain distinct. Inference/allocation order is not persistent identity.
<!-- POST_PR16_UNIT_END:TC-R009 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R010 -->
### TC-R010 — associated requirements

Each associated requirement has exactly one compatible explicit or canonical inherited binding. Missing, duplicate, ambiguous, incompatible, or cyclic bindings reject before MIR. A projection retains exact record and requirement identity. Same-name nested items do not synthesize bindings. Defaults, generic associated items, and associated override remain outside the minimum unless separately authorized.
<!-- POST_PR16_UNIT_END:TC-R010 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R011 -->
### TC-R011 — refinement and dispatch separation

Trait refinement creates parent proof obligations and links, not a second dispatch domain. Class subtyping/vtable evidence and Trait conformance/witness evidence stay structurally distinct. Subclasses do not automatically inherit unrelated conformance. Any adapter preserves responsibility and API residue or rejects.
<!-- POST_PR16_UNIT_END:TC-R011 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R012 -->
### TC-R012 — visibility closure

An exported conformance does not expose a less-visible target, Trait, requirement, witness, associated binding, condition, or parent evidence. Private helpers participate only when current export law can represent them without leaking inaccessible identity. Imports change visible summaries, not priority.
<!-- POST_PR16_UNIT_END:TC-R012 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R013 -->
### TC-R013 — separate compilation

Each link-relevant schema emits a deterministic summary with authority, normalized head/binders/conditions, locality, visibility, record/requirement/binding digests, associated bindings, and parent links. The whole-image verifier checks duplicates, overlap, locality, visibility, parent interning, and digest compatibility independent of object/package/import/schedule order. No profile claim is permitted without this link check.
<!-- POST_PR16_UNIT_END:TC-R013 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R014 -->
### TC-R014 — frontend closure

One root-connected grammar route must construct one normalized semantic route. This candidate selects no spelling. Current `ConformanceDecl` and current `ConformanceViaClause` remain unchanged and isolated. A future surface needs exact EBNF, reachability, lossless CST ownership, AST/HIR mapping, profile gates, recovery, and diagnostics. Selection closes before MIR.
<!-- POST_PR16_UNIT_END:TC-R014 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R015 -->
### TC-R015 — MIR and runtime closure

MIR carries closed record, requirement, witness, associated-binding, and parent-link identities or lossless equivalents. Lowering performs no source/provider/default/specialization/fallback search and preserves responsibility, visibility, and API residue. Runtime strings, names, iteration, or registration order are not evidence authority.
<!-- POST_PR16_UNIT_END:TC-R015 -->

<!-- POST_PR16_UNIT_BEGIN:TC-R016 -->
### TC-R016 — deterministic diagnostics

Primary failures use this exact rank, then full canonical semantic identity:

1. malformed/unadmitted surface or unresolved canonical identity;
2. duplicate requirement, return-only, or callable-profile-only overload;
3. locality/orphan violation;
4. duplicate or overlapping conformance head;
5. non-well-founded conditional proof;
6. supertrait evidence or inherited-binding conflict;
7. visibility/export failure;
8. missing, ambiguous, or incompatible witness;
9. associated-binding failure;
10. unresolved MIR evidence closure.

The primary span identifies the rejecting declaration or binding. Notes use canonical conflicting identities, normalized keys/heads, and authorities in stable order. File/import/link permutations do not change family or semantic note order. The exact one-to-one Test_ binding is in `proposed-deltas/diagnostic-binding-ledger.json`.
<!-- POST_PR16_UNIT_END:TC-R016 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-001 -->
## TCC-DG-001 — Witness compatibility

One total, origin-independent predicate `WitnessCompatible(R,D,C)` is used at every admission tier. Normalize the ground context, `Self`, Trait arguments, aliases, associated projections, binders, and types. Associated bindings must close without recursive selection. Requirement kind and call input must match, the complete requirement contract must be checked, and unratified fields remain invariant. A witness may not introduce stronger preconditions, stronger constraints, or broader obligations.

The controlling component relations are:

```text
Normalize(Effects(W,C)) subset_of Normalize(Effects(R,C))
Normalize(Errors(W,C)) subset_of Normalize(Errors(R,C))
DeclaredObligations(R,C) proves DeclaredObligations(W,C)
origin_reads = 0
```

| Requirement | Witness | Result |
|---|---|---|
| effects `{E1,E2}` | effects `{E1}` | compatible component |
| effects `{E1}` | effects `{E1,E2}` | incompatible |
| obligations `P & Q` | obligation `P` | compatible when the requirement environment proves `P` |
| obligation `P` | obligations `P & Q` | incompatible unless the requirement environment independently proves `Q` |
| equal normalized contracts | equal normalized contracts | compatible |

An explicit witness mismatch is final at the explicit tier and has fallback count zero.
<!-- POST_PR16_UNIT_END:TCC-DG-001 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-002 -->
## TCC-DG-002 — Deterministic tiered admission

If the explicit set is nonempty, the tier is committed: success requires exactly one member and that sole member must be compatible. Any explicit cardinality or compatibility failure is final; ordinary and default tiers are `NOT_EVALUATED`, and fallback count is zero. With no explicit witness, exactly one compatible ordinary witness binds; more than one is ambiguous and zero continues. Only an independently authorized default set may then use the same cardinality rule; otherwise the result is missing. Private helpers are excluded. Provider identity and declaration or import order are never rank. `DefaultSet` remains empty until a marker/default mapping is separately ratified.
<!-- POST_PR16_UNIT_END:TCC-DG-002 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-003 -->
## TCC-DG-003 — Fixed-goal inference and projection order

Authorized expected context may participate in ordinary call-site inference only to fix a different pre-proof goal. The fixed pipeline is:

```text
ordinary inference
-> fixed ground or symbolic goal
-> proof without reverse conformance enumeration
-> selected record
-> closed projection reduction
```

Generic-definition HIR and abstract obligations remain stable under downstream conformance additions. Reverse enumeration count is zero. Associated projections reduce only after record selection and cannot feed back into candidate discovery, ranking, or goal mutation.

Mutation controls require the pre-proof goal digest, definition HIR digest, abstract obligation digest, reverse-enumeration count, selected-record identity, and projection-order trace. Adding an unrelated conformance may not change a previously fixed ordinary call goal or definition summary; a genuine explicit source edit or changed authorized expected context is a distinct input, not reverse inference.
<!-- POST_PR16_UNIT_END:TCC-DG-003 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-004 -->
## TCC-DG-004 — Evidence identity and inheritance

Evidence preserves its original owner. A child namespace does not re-key inherited evidence. Equal normalized instantiations intern to the same evidence identity; different Trait arguments remain distinct. Expected type, subtyping, and current variance may not select, synthesize, merge, or rank evidence. A binding is scoped to the exact record and requirement. One source satisfying two requirements produces two binding identities. A diamond reuses the same parent evidence rather than creating child-local replacements.
<!-- POST_PR16_UNIT_END:TCC-DG-004 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-005 -->
## TCC-DG-005 — Evidence privacy boundary

`EvidenceScope` admits only authorized evidence, associated material, and private helpers needed by that evidence. It excludes unrelated public API, storage/layout, constructors, general-extension bodies, and foreign private state. A private helper is never a candidate, binding, conformance-summary item, or public API residue.

An explicitly admitted legal witness may call a helper under ordinary access laws. The helper-body dependency remains in nonpublic HIR/MIR and its behavior cannot be dropped. These fields are independent:

```text
private_helper_call_from_explicit_witness_allowed_under_ordinary_access
candidate_count = 0
witness_binding_count = 0
conformance_summary_evidence_count = 0
public_api_residue_count = 0
nonpublic_body_dependency_count >= 0
```
<!-- POST_PR16_UNIT_END:TCC-DG-005 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-006 -->
## TCC-DG-006 — Dormant value-profile law

This law is conditional and dormant until the exact value `RequirementKind`, profile, AST/HIR, diagnostics, and accessor contract are separately ratified. In the inactive state: `PROFILE_UNAVAILABLE`, `RequirementKindId` is `ABSENT`, evidence count is zero, and MIR/API residue is zero.

In a separately authorized future profile, a read-only requirement may be met by an immutable field, computed property, or read-write getter, but does not expose a setter. A read-write requirement needs compatible getter and setter identities checked by TCC-DG-001. Accessor identities are closed. External evidence may compute from pre-existing accessible state but may not add or synthesize storage/layout or access foreign private state. The layout digest before and after admission must be identical. No source form is activated here.
<!-- POST_PR16_UNIT_END:TCC-DG-006 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-007 -->
## TCC-DG-007 — Source admission and whole-image coherence

The controlling sequence is:

```text
authorized graph/import/re-export/visibility
-> SourceAdmission
-> conformance summary or source rejection
-> WholeImageCoherence
-> link
```

Linking cannot repair rejected source admission, manufacture source evidence, or turn hidden graph presence into authority. Source-admission and link-coherence traces remain distinct and order-invariant, with stable diagnostics for the same authorized graph.
<!-- POST_PR16_UNIT_END:TCC-DG-007 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-008 -->
## TCC-DG-008 — Trait-conformance evolution lanes

The exact Trait-conformance evolution lanes are `SOURCE`, `RESOLUTION`,
`BEHAVIOR`, and `BINARY_ABI`. Each stores its predicate and version,
scope/inputs, target, evidence identity, result, and reason. No result
propagates between lanes. This four-lane set is scoped to TCC evolution and
does not replace or abbreviate the eight CE compatibility lanes in PC-10.

Decision precedence is:

1. evaluator or target not invoked: `NOT_RUN`;
2. a claim with unverifiable inputs, predicate, identity, output, or receipt: `NOT_AUDITABLE`;
3. valid evaluation with a counterexample: `FAIL`;
4. complete valid evaluation satisfying the predicate: `PASS`;
5. complete valid evaluation whose predicate is explicitly indeterminate: `UNKNOWN`.

`BINARY_ABI` remains `NOT_RUN` without an exact target-bound execution receipt.
<!-- POST_PR16_UNIT_END:TCC-DG-008 -->

<!-- POST_PR16_UNIT_BEGIN:TCC-DG-P2-009 -->
## TCC-DG-P2-009 — Teaching and tooling split

Progressive tutorial order is: explicit DIRECT; ordinary exact witness; explicit Trait qualification only when the active profile defines it; conformance grouping/associated binding; inheritance/coherence; dormant provider/AUTO. Reference documentation may use another order, but examples must label profile and activation. Current lowercase `via` remains separate from successor VIA.

Only active forms may enter formatter/LSP behavior. No semantic auto-rewrite is authorized. A future formatter must preserve parse identity, declaration identity, comments, and trivia, and a second pass must be byte-identical. Evidence labels distinguish prose review, design static fixtures, and compiler-executed examples; the last requires a complete target-bound receipt.

`TCC-DG-P2-009A` is the static tutorial classification/order/label/dormant-placement/receipt-schema contract, depends on `TCC-P1-008`, and remains `NOT_RUN`. `TCC-DG-P2-009B` is the product formatter/idempotence/completion/action/semantic-identity contract, depends on `TCC-P1-002` and `TCC-P1-008` plus separate product authority, and remains `NOT_RUN`. The aggregate dependency projection is `[TCC-P1-002, TCC-P1-008]`.
<!-- POST_PR16_UNIT_END:TCC-DG-P2-009 -->

<!-- POST_PR16_UNIT_BEGIN:C-01 -->
1. `C-01`: every admitted Class maps to one owner-tagged `ClassResponsibilityDescriptor`. Move, borrow, explicit clone, reusable value, managed sharing, and cleanup authority are independent capability fields with explicit cross-constraints. Flavor spelling does not imply synthesis, layout, or ABI.
<!-- POST_PR16_UNIT_END:C-01 -->

<!-- POST_PR16_UNIT_BEGIN:C-02 -->
2. `C-02`: sealed partition cells include every instantiable concrete sealed root/intermediate self-cell; abstract nodes have no self-cell; an admitted open direct child contributes one owner-qualified opaque subtree cell. Declaration/import order cannot change the cell set.
<!-- POST_PR16_UNIT_END:C-02 -->

<!-- POST_PR16_UNIT_BEGIN:C-03 -->
3. `C-03`: stored fields, promoted inputs, accessors, and type-side state remain distinct. Each stored field has one owner-scoped identity and definite-initialization state.
<!-- POST_PR16_UNIT_END:C-03 -->

<!-- POST_PR16_UNIT_BEGIN:C-04 -->
4. `C-04`: one construction session has one commit owner. The phase order is `PRE_DELEGATION -> BASE_INITIALIZED -> STORAGE_INITIALIZING -> POST_INIT -> LIVE`; failure is `ABORTING -> FAILED_UNPUBLISHED`. Delegated targets return prepublication completion. Success publishes once and failure publishes zero. Failure requires `acquired = discharged`; success requires `acquired = discharged_temporaries + transferred_to_live`; terminal balance is zero.
<!-- POST_PR16_UNIT_END:C-04 -->

<!-- POST_PR16_UNIT_BEGIN:C-05 -->
5. `C-05`: `ClassSlotId` is based on the declaring root, selector, normalized input channels, binder identity, and receiver responsibility. Override inputs/channels/generics/ownership/isolation/effects/errors are exact; only result covariance with an explicit subtype proof is admitted. A forwarder owns a distinct final identity from its target and target slot.
<!-- POST_PR16_UNIT_END:C-05 -->

<!-- POST_PR16_UNIT_BEGIN:C-06 -->
6. `C-06`: forwarding names a finite selector list, evaluates its receiver once, preserves argument/effect/error/responsibility order, and creates no subtype edge, Trait witness, storage, or cleanup owner.
<!-- POST_PR16_UNIT_END:C-06 -->

<!-- POST_PR16_UNIT_BEGIN:C-07 -->
7. `C-07`: every cleanup obligation has exactly one live owner or is discharged. Move transfers authority, borrow does not, and failure/cancellation/suspension cannot bypass cleanup.
<!-- POST_PR16_UNIT_END:C-07 -->

<!-- POST_PR16_UNIT_BEGIN:C-08 -->
8. `C-08`: Class variance remains `REJECT_AT_CLASS_OWNER_ADMISSION`; rejected or recovery syntax creates zero admitted AST/HIR/MIR/API residue. Explicit Trait views or adapters are the alternatives.
<!-- POST_PR16_UNIT_END:C-08 -->

<!-- POST_PR16_UNIT_BEGIN:C-09 -->
9. `C-09`: flavor and responsibility never imply equality, hashing, ordering, display, cloning, serialization, or Trait evidence. Any future synthesis needs an operation manifest, termination/law proof, responsibility exclusions, and one whole-Class evidence origin.
<!-- POST_PR16_UNIT_END:C-09 -->

<!-- POST_PR16_UNIT_BEGIN:C-10 -->
10. `C-10`: Class residue is owner-complete and compatibility uses only the eight independent PC-10 records.
<!-- POST_PR16_UNIT_END:C-10 -->

<!-- POST_PR16_UNIT_BEGIN:C-11 -->
11. `C-11`: logical diagnostic families and stable fields may be materialized locally, but final registry codes remain null. Recovery cannot create admitted semantic residue and tooling cannot perform an unproved rewrite.
<!-- POST_PR16_UNIT_END:C-11 -->

<!-- POST_PR16_UNIT_BEGIN:E-01 -->
1. `E-01`: one `EnumDescriptor` owns one `EnumId`, normalized binders, an exact case universe, and one distinct stable `VariantId` per case. Source order is not raw value, tag, ordinal, layout, ABI, or priority. Empty Enum remains nonactivatable; one-case Enum is semantic-only.
<!-- POST_PR16_UNIT_END:E-01 -->

<!-- POST_PR16_UNIT_BEGIN:E-02 -->
2. `E-02`: current mixed payload remains current authority. The successor is uniform within each case. Migration has no default: the user selects label-all, unlabel-all, or one Record payload after a complete use-site inventory. Automatic rewrite count is zero.
<!-- POST_PR16_UNIT_END:E-02 -->

<!-- POST_PR16_UNIT_BEGIN:E-03 -->
3. `E-03`: one `VariantFormationPlanId` and owner/case binding are fixed before any argument evaluation. Arguments evaluate left-to-right exactly once; failed formation cleans successful temporaries in reverse acquisition order and publishes zero values.
<!-- POST_PR16_UNIT_END:E-03 -->

<!-- POST_PR16_UNIT_BEGIN:E-04 -->
4. `E-04`: guards refine admitted cells but do not cover unguarded residuals. Any future external residual remains owner-relative and does not manufacture an unknown runtime case or activate spelling.
<!-- POST_PR16_UNIT_END:E-04 -->

<!-- POST_PR16_UNIT_BEGIN:E-05 -->
5. `E-05`: the inline-size dependency graph itself is acyclic; hidden boxing is forbidden.
<!-- POST_PR16_UNIT_END:E-05 -->

<!-- POST_PR16_UNIT_BEGIN:E-06 -->
6. `E-06`: current `.`, `+`, `*.`, `*+` reachability remains current. The successor admits final trailing `.` only before slot/witness allocation. Migration has no default: the user selects final match behavior, sealed Class, visitor/strategy Trait, or payload object. Marker-to-dot automatic rewrite count is zero.
<!-- POST_PR16_UNIT_END:E-06 -->

<!-- POST_PR16_UNIT_BEGIN:E-07 -->
7. `E-07`: only active semantic payload places exist. Reserved bytes are representation, not inactive semantic places. Responsibility joins component-wise; a resource partial move cannot leave a generally usable Enum. Failed replacement leaves the old value live; successful replacement has one source-observable MIR ownership commit.
<!-- POST_PR16_UNIT_END:E-07 -->

<!-- POST_PR16_UNIT_BEGIN:E-08 -->
8. `E-08`: Enum use as an error, state, or message creates no implicit transitions, conversions, or protocol law. `E08-M` is `EXCLUDED_DEFERRED_A3`.
<!-- POST_PR16_UNIT_END:E-08 -->

<!-- POST_PR16_UNIT_BEGIN:E-09 -->
9. `E-09`: ordinary Enum is raw-free. Semantic identity is distinct from raw value, serialization tag, runtime discriminant, ordinal, layout, and foreign ABI.
<!-- POST_PR16_UNIT_END:E-09 -->

<!-- POST_PR16_UNIT_BEGIN:E-10 -->
10. `E-10`: Trait evidence belongs to the whole Enum. Case membership creates and replaces zero witnesses. Current lowercase `via` remains unchanged.
<!-- POST_PR16_UNIT_END:E-10 -->

<!-- POST_PR16_UNIT_BEGIN:E-11 -->
11. `E-11`: public residue records every stable owner fact and eight independent compatibility records. Source aliases, serialization aliases, representation mappings, and semantic identity remain separate.
<!-- POST_PR16_UNIT_END:E-11 -->

<!-- POST_PR16_UNIT_BEGIN:E-12 -->
12. `E-12`: one-case Enum is `SEMANTIC_ONLY_ONE_CASE_NO_TOOLING_ADVICE`; no warning, recommendation, or rewrite is produced. Empty and advanced profiles remain inactive.
<!-- POST_PR16_UNIT_END:E-12 -->

<!-- POST_PR16_UNIT_BEGIN:E-13 -->
13. `E-13`: logical owner diagnostic families and their field contract are materialized without inventing final registry IDs. Recovery creates zero admitted AST/HIR/MIR/API residue.
<!-- POST_PR16_UNIT_END:E-13 -->

### Enum-derived capabilities: accepted Preview design, not current syntax

The following three facilities are accepted as one coordinated `PREVIEW_DESIGN`
contract under `CE-E-P1-004`, `CE-E-P1-007`, `CE-E-P1-008`, and the open TCC
gates. They are canonical design decisions but are `nonactivatable`: the current
`EnumDecl`, current `.`, `+`, `*.`, `*+` reachability, current lowercase `via`,
and current parser/checker/runtime behavior do not change. Static files or
fixtures close no P1 and establish no product support.

1. A future declaration may select exactly one owner-specific order role,
   `enum#increasing` or `enum#decreasing`. The first form means declaration
   order is strictly increasing; the second means it is strictly decreasing.
   The minimum profile is nominal, nonempty, payload-free, and nongeneric. It
   synthesizes exactly one whole-Enum `Ord<E>` witness. `SemanticOrderRank` and
   the ordered `VariantId` vector are not source-visible ordinals and are
   independent of raw values, tags, discriminants, serialization, layout, ABI,
   match priority, ranges, iteration, or transitions. Comparison observes only
   sign, borrows both operands, is pure, synchronous, `throws Never`, consumes
   nothing, and returns zero exactly for the same `EnumId` and `VariantId`.
   An explicit same-ground `Ord<E>` conformance conflicts; no priority,
   specialization, provider lookup, fallback, or comparison-glyph activation is
   inferred.
2. A future enum case may own `~>` followed by a restricted String template.
   If one inhabitable case maps, every inhabitable case maps exactly once. Named
   payload fields are read-only borrowed binders inside that case's template;
   an unlabeled payload gets no invented `$1` or `it` name. Every interpolation
   hole requires one already selected `Display` witness. The template cannot
   move, mutate, throw, suspend, spawn, escape a binder, call an arbitrary
   provider, or perform hidden locale lookup. The complete mapping synthesizes
   exactly one whole-Enum `Display` witness and zero case witnesses. It is not
   serialization, parsing, localization, redaction, raw identity, or a reverse
   map. Partial mapping has no case-name fallback, and an explicit same-ground
   `Display` conformance conflicts.
3. A future enum body may contain an explicit associated alias such as
   `+type Weekend = Sat | Sun`; the bare spelling `Weekend = ...` is not
   admitted. A payload-free exact variant is the finite identity
   `(EnumId, VariantId)`, not an open runtime subtype. A named subset is a frozen
   same-owner `VariantId` set plus an enum-universe digest. It creates no case,
   constructor, wrapper, storage, allocation, tag, raw mapping, layout, or Trait
   witness. An exact variant or subset widens to its owner by a bounded
   `VariantOwnerWidening` proof; owner-to-subset and unrelated subset narrowing
   require `as?`, an admitted pattern, or another explicit checked boundary.
   Exhaustiveness and unreachability operate on the frozen allowed-variant set,
   not general subtyping search. Alias order is semantically irrelevant, subset
   inclusion is the only implicit subset conversion, and aliases reuse the
   owner's one nominal witness. If a normalized subset contains the complete
   frozen variant universe, its canonical type is the nominal owner Enum; the
   associated alias remains a non-identifying source spelling.

PC-10 keeps exactly eight independent top-level records: `source`, `resolution`,
`behavior`, `serialization`, `runtime_layout`, `foreign_ABI`,
`tooling_reflection`, and `product`. Order and Display are independent
subrecords of `behavior`; subset membership and owner widening are independent
subrecords of `resolution`; raw identity is a `serialization` subrecord and
never aliases semantic identity. Reordering preserves stable `VariantId` values
but changes the order vector and order-behavior digest. Changing a display
template changes only Display behavior residue. Adding a case does not silently
expand an explicit subset. Incompatible order, generated-witness, subset, or
enum-universe summaries reject at import/link validation instead of choosing by
source order. No sibling status propagation or `overall_pass` is introduced.
Payload ordering, payload-bearing exact-variant types, generic conditional
synthesis, automatic reverse parsing, subset iteration/ranges, and bundled Trait
derivation remain deferred.

### Literal-shaped collection types and immutable-first ownership: accepted Preview design

The Library proposal's Markdown entry and ZIP member carry the same report. Its
two design axes are accepted once, with bounded repairs, as
`PREVIEW_DESIGN` and `nonactivatable`. The current grammar contains none of the
following type-position productions and remains authoritative. No parser,
checker, MIR, runtime, formatter/LSP, Prelude-signature, diagnostic-registry, or
product route is activated by this section.

In a future type parser goal only, `[T]`, `#mut[T]`, `#set{T}`, `#map{K: V}`,
and `${label: T, ...}` may be lossless source sugar for `List<T>`,
`MutableList<T>`, `Set<T>`, `Map<K,V>`, and a closed required-label structural
Record row. The source spelling belongs to CST and formatting identity; HIR,
type identity, API digest, ABI, and serialization use the canonical named or
row identity. The sigils are attached with no intervening trivia. `#N[T]`
remains the NumericArray `SharpShapeType` owner. Type, value, pattern, and index
parser goals never repair or reinterpret one another. `[T | U]` contains the
already explicit Union `T | U`; it does not infer a heterogeneous Union.

The minimum Record type profile has closed, required, static Identifier labels,
deterministic duplicate rejection, and the current order-normalized row
identity. Open or optional rows, rest, string labels, row variance, and empty
row identity remain deferred. A Map key is a runtime exact `K`; a Record label
is a static Identifier. Neither converts to the other, and the sugar introduces
no Map dot-key projection or named unfold.

The spelling of a type grants no operation or capability. In particular it
does not activate brackets, mutation, operator glyphs, Trait witnesses, Copy,
deep freeze, shareability, transferability, or actor crossing. The current
one-based List/String/Bytes domains, bounded coordinates, slice provenance,
Map exact-key lookup, Tuple and Record projections, NumericArray axes, and
closed bracket-carrier matrix are unchanged. `MutableList`, `FrozenList`, and
`ListSnapshot` remain outside that matrix.

Owned collection naming is immutable-first: `List`, `Map`, `Set`, `String`,
`Bytes`, Tuple, and Record denote immutable owners; mutation uses a distinct
explicit mutable owner and never an implicit subtype conversion. `Sequence`
remains a traversal protocol only and creates no bracket, mutation, freeze,
snapshot, or view route. `MutableMap`, `MutableSet`, `StringBuilder`, and
`ByteBuffer` are reserved successor owner names without a current Prelude
identity. `MutableSequence`, `MutableTuple`, general `MutableRecord`, and
`MutableString` remain absent or deferred.

Current `MutableList<T>::freeze` and `snapshot` continue to return the distinct
current identities `FrozenList<T>` and `ListSnapshot<T>`. Replacing either with
ordinary `List<T>` would change indexing, public API, ABI, serialization, and
actor-shareability residue and therefore requires an explicit successor
migration; no alias or automatic rewrite is admitted here.

The successor responsibility split is nevertheless fixed. `freeze` moves a
mutable owner but consumes it exactly once only after a successful commit. It
rejects an outstanding borrow or view, preserves the exact owner and value
state on failure, is shallow with respect to payload capabilities, and never
proves `ShareSafe` or `Transferable`. `snapshot` borrows and preserves its
source and produces an independent point-in-time immutable result; later source
mutation cannot change it, while allocation and representation cost remain
visible and implementation-dependent. A `view` is a borrowed, owner-bounded,
nonowning projection that preserves logical domain, coordinates, and
provenance; it cannot escape or cross isolation and conflicts with owner
mutation, move, or freeze. No common or collection-specific successor view
carrier name is selected by this decision. These three message surfaces use
the no-argument receiver form without parentheses only after separate source
activation authority.

All 22 feature P1 items and the four separate M13 actions retain their current
status. The grammar/type-system/implementation/test/tooling/migration work
listed in `spec/contracts/literal-shaped-collection-design.json` is an internal
activation-gate ledger, not a new P1 set. Semantic P0 is zero and every product
lane remains `NOT_RUN`.

<!-- POST_PR16_UNIT_BEGIN:X-01 -->
```json
{
    "id":  "X-01",
    "target":  "construct selection guidance",
    "controlling_rule":  "selection uses identity, openness, multiplicity, lifecycle, and structural intent and yields one owner or explicit composition",
    "guard":  "guidance-only; no syntax or identity generation",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-01 -->

<!-- POST_PR16_UNIT_BEGIN:X-02 -->
```json
{
    "id":  "X-02",
    "target":  "sealed Class versus Enum coverage",
    "controlling_rule":  "shared coverage algebra preserves owner identity; a Class subtype cell never equals a VariantId",
    "guard":  "equal coverage does not imply equal construction, layout, dispatch, or evolution",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-02 -->

<!-- POST_PR16_UNIT_BEGIN:X-03 -->
```json
{
    "id":  "X-03",
    "target":  "data/value Class versus one-case Enum",
    "controlling_rule":  "each retains its nominal owner and intent; crossing uses an explicit conversion",
    "guard":  "no transparent ABI, synthesis, zero-cost, or recommendation follows",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-03 -->

<!-- POST_PR16_UNIT_BEGIN:X-04 -->
```json
{
    "id":  "X-04",
    "target":  "Class field versus active Enum payload",
    "controlling_rule":  "Class lifetime fields and Variant-active payload places retain distinct owner states",
    "guard":  "shared vocabulary cannot merge visibility, initialization, mutability, or inactive-place rules",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-04 -->

<!-- POST_PR16_UNIT_BEGIN:X-05 -->
```json
{
    "id":  "X-05",
    "target":  "construction domains",
    "controlling_rule":  "Class construction, Enum formation, and schema materialization use distinct plan IDs and failure/cleanup contracts",
    "guard":  "shared labeled-input vocabulary cannot alias authorities",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-05 -->

<!-- POST_PR16_UNIT_BEGIN:X-06 -->
```json
{
    "id":  "X-06",
    "target":  "dispatch domains",
    "controlling_rule":  "ClassSlotId virtual dispatch, VariantId partition/switch, direct final Enum calls, and TraitWitnessId calls remain distinct",
    "guard":  "matching creates no slot and virtual calls establish no finite partition",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-06 -->

<!-- POST_PR16_UNIT_BEGIN:X-07 -->
```json
{
    "id":  "X-07",
    "target":  "Trait evidence across owners",
    "controlling_rule":  "one whole-nominal evidence origin; subclass and Enum case membership create or replace zero witnesses",
    "guard":  "current lowercase via unchanged; AUTO/VIA/specialization/child-case replacement inactive",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-07 -->

<!-- POST_PR16_UNIT_BEGIN:X-08 -->
```json
{
    "id":  "X-08",
    "target":  "nominal, structural, and extension boundary",
    "controlling_rule":  "crossing identity domains is explicit and states ownership transfer and failure",
    "guard":  "shape equality creates no nominal identity; extensions add no storage/case/subtype/replacement/witness",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-08 -->

<!-- POST_PR16_UNIT_BEGIN:X-09 -->
```json
{
    "id":  "X-09",
    "target":  "shared partition core",
    "controlling_rule":  "PatternPartitionCore consumes owner ID, universe, owner-tagged cells, deconstruction, and guards and computes algebra only",
    "guard":  "no owner universe, construction, evaluation, ownership, cleanup, lifecycle, layout, dispatch, or evolution authority",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-09 -->

<!-- POST_PR16_UNIT_BEGIN:X-10 -->
```json
{
    "id":  "X-10",
    "target":  "typed identity and residue",
    "controlling_rule":  "semantic, representation, artifact, and Git identities remain disjoint except by explicit typed mapping; eight lanes remain independent",
    "guard":  "VariantId is not ordinal/tag/discriminant/layout/ABI; hashes are not semantic IDs",
    "consumes_owner_closed_input":  true
}
```
<!-- POST_PR16_UNIT_END:X-10 -->

<!-- POST_PR16_UNIT_BEGIN:PC-09 -->
```json
{
    "id":  "PC-09",
    "disposition":  "AMEND",
    "preliminary_disposition":  "AMEND",
    "selected_option":  "OWNER_COLLISION_PLUS_TRAIT_FAIL_CLOSED_TIERS",
    "controlling_rule":  "same reached-tier multiplicity is ambiguity; explicit failure or ambiguity is terminal; lower tiers are NOT_EVALUATED; fallback and order-winner counts are zero",
    "current_guard":  "current lowercase via remains unchanged and provider/source/import/discovery order never ranks",
    "successor_guard":  "DefaultSet remains empty and AUTO/VIA/specialization remain inactive until separate authority",
    "source_evidence_trace":  [
                                  "Spec Normative Rule PC-09",
                                  "Wave1 refinement CE-W1-R009",
                                  "Final Controlling Delta pc09",
                                  "R1 PC09/PC10 Schema pc09"
                              ]
}
```
<!-- POST_PR16_UNIT_END:PC-09 -->

<!-- POST_PR16_UNIT_BEGIN:PC-10 -->
```json
{
    "id":  "PC-10",
    "disposition":  "AMEND",
    "preliminary_disposition":  "AMEND",
    "selected_option":  "PROFILE_SCOPED_EIGHT_INDEPENDENT_LANES",
    "controlling_rule":  "source, resolution, behavior, serialization, runtime_layout, foreign_ABI, tooling_reflection, and product are independent records",
    "current_guard":  "no current semantic or representation promise is inferred across lanes",
    "successor_guard":  "no overall_pass or sibling propagation; every PASS requires its own profile and receipt; product remains NOT_RUN",
    "source_evidence_trace":  [
                                  "Spec Normative Rule PC-10",
                                  "Wave1 refinement CE-W1-R010",
                                  "Final Controlling Delta pc10_lane_keys",
                                  "R1 PC09/PC10 Schema pc10"
                              ]
}
```
<!-- POST_PR16_UNIT_END:PC-10 -->

<!-- POST_PR16_UNIT_BEGIN:SFD-N001 -->
```json
{
    "schema":  "deeplus.codex-design.static-first-dynamic-decision-map.r1",
    "status":  "LOCAL_NONCANONICAL_NONACTIVATABLE",
    "teaching_rule":  "Choose the narrowest mechanism whose precondition matches source intent; evaluate only the mechanism and authority written in source.",
    "decision_law":  {
                         "source_selected_mechanism_count_per_row":  1,
                         "compiler_retry_count":  0,
                         "automatic_fallback_count":  0,
                         "expected_type_route_selection_count":  0,
                         "order_winner_count":  0
                     },
    "rows":  [
                 {
                     "id":  "UC-01",
                     "intent":  "represent known finite alternatives",
                     "selected_source_mechanism":  "Enum, closed union, or sealed Class",
                     "dynamic_necessity":  "NONE",
                     "explicit_authority":  "type definition and match owner",
                     "failure":  "static exhaustiveness error",
                     "cleanup":  "ordinary lexical cleanup",
                     "user_selected_alternative":  "sealed Class when hierarchy identity is intended",
                     "impossible_case":  "implicit type erasure or automatic heterogeneous join",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-02",
                     "intent":  "use a known capability without concrete identity",
                     "selected_source_mechanism":  "current borrow Facet or any Trait",
                     "dynamic_necessity":  "NONE",
                     "explicit_authority":  "admitted nominal conformance and source lifetime",
                     "failure":  "static formation rejection",
                     "cleanup":  "view ends without owning the payload",
                     "user_selected_alternative":  "nominal adapter",
                     "impossible_case":  "raw witness or bare Trait value",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-03",
                     "intent":  "share reusable helper behavior",
                     "selected_source_mechanism":  "lexical extension",
                     "dynamic_necessity":  "NONE",
                     "explicit_authority":  "import and lexical scope",
                     "failure":  "static missing or ambiguous member error",
                     "cleanup":  "none beyond underlying value",
                     "user_selected_alternative":  "adapter plus Facet when capability must be carried as data",
                     "impossible_case":  "extension becoming a runtime witness or dynamic dispatch authority",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-04",
                     "intent":  "decode JSON-shaped data",
                     "selected_source_mechanism":  "JsonValue or schema decoder",
                     "dynamic_necessity":  "DATA_LEVEL_ONLY",
                     "explicit_authority":  "decoder or schema",
                     "failure":  "Result with path-aware decode error",
                     "cleanup":  "partial construction cleans normally",
                     "user_selected_alternative":  "generated schema or command model",
                     "impossible_case":  "Plain, Map, or object acting as universal Dyn",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-05",
                     "intent":  "receive an unknown value from a plugin",
                     "selected_source_mechanism":  "explicit owned Dyn pack",
                     "dynamic_necessity":  "REQUIRED",
                     "explicit_authority":  "pack operation plus owner, provenance and drop contract",
                     "failure":  "transactional pack returns exact owner or cleans exactly once",
                     "cleanup":  "named allocator and drop authority",
                     "user_selected_alternative":  "owned Facet when capability is known; remains nonactivatable",
                     "impossible_case":  "unknown allocator or drop authority",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-06",
                     "intent":  "project a known capability from an unknown plugin value",
                     "selected_source_mechanism":  "explicit immutable FacetRegistry\u003cTrait\u003e borrow projection",
                     "dynamic_necessity":  "REQUIRED",
                     "explicit_authority":  "registry parameter/context, static Trait, unique route and immutable snapshot",
                     "failure":  "Result or Option; owner state explicit",
                     "cleanup":  "borrow projection failure does not consume owner",
                     "user_selected_alternative":  "nominal adapter at plugin boundary",
                     "impossible_case":  "hidden global lookup, structural conformance, or runtime Trait-to-Facet creation",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-07",
                     "intent":  "inspect or recover a known concrete type",
                     "selected_source_mechanism":  "checked concrete borrow or owner-preserving downcast",
                     "dynamic_necessity":  "ONLY_AFTER_EXPLICIT_DYN_PACK",
                     "explicit_authority":  "static target type plus descriptor or owner authority",
                     "failure":  "borrow returns checked failure; owned mismatch returns exact original owner",
                     "cleanup":  "no owner loss and no double drop",
                     "user_selected_alternative":  "closed union match",
                     "impossible_case":  "unchecked recovery or owner destruction on failed recovery",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-08",
                     "intent":  "associate stateful per-instance behavior",
                     "selected_source_mechanism":  "explicit nominal adapter Facet",
                     "dynamic_necessity":  "NONE_BY_DEFAULT",
                     "explicit_authority":  "adapter owner and admitted conformance",
                     "failure":  "explicit adapter construction error when applicable",
                     "cleanup":  "drop or release the distinct Facet or adapter",
                     "user_selected_alternative":  "caller-owned map; FacetStore only after necessity proof",
                     "impossible_case":  "hidden original-object fields or global conformance mutation",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-09",
                     "intent":  "invoke a runtime string-named operation",
                     "selected_source_mechanism":  "command Enum or Trait; otherwise privileged reflection service",
                     "dynamic_necessity":  "ONLY_FOR_RUNTIME_LABEL",
                     "explicit_authority":  "reflection service and inspection authority",
                     "failure":  "unknown, denied, ambiguous, or invocation error returned",
                     "cleanup":  "service-defined and visible",
                     "user_selected_alternative":  "visitor, strategy, or command adapter",
                     "impossible_case":  "ordinary dynamic member lookup or static-looking completion",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-10",
                     "intent":  "hot reload a provider route",
                     "selected_source_mechanism":  "immutable registry snapshot",
                     "dynamic_necessity":  "REQUIRED",
                     "explicit_authority":  "plugin manager and registry snapshot lineage/epoch",
                     "failure":  "build and validate before atomic snapshot publication",
                     "cleanup":  "old snapshot and provider lease survive while referenced",
                     "user_selected_alternative":  "new process or module",
                     "impossible_case":  "retargeting an already-created Facet",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-11",
                     "intent":  "transfer an open-world value across task or actor boundary",
                     "selected_source_mechanism":  "owned carrier plus Transferable or Shareable proof",
                     "dynamic_necessity":  "REQUIRED_FOR_OPEN_WORLD_PAYLOAD",
                     "explicit_authority":  "boundary proof and owner",
                     "failure":  "failed send retains owner; cancellation cleans exactly once",
                     "cleanup":  "single-owner or explicit sharing law",
                     "user_selected_alternative":  "serialize closed data",
                     "impossible_case":  "borrow or inout Facet escape",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 },
                 {
                     "id":  "UC-12",
                     "intent":  "cross an FFI boundary",
                     "selected_source_mechanism":  "opaque handle wrapper",
                     "dynamic_necessity":  "ONLY_AT_FOREIGN_BOUNDARY",
                     "explicit_authority":  "named bridge, allocator, deallocator and target descriptor",
                     "failure":  "retain or return handle, or clean exactly once",
                     "cleanup":  "bridge-owned explicit rule",
                     "user_selected_alternative":  "closed wrapper or nominal adapter",
                     "impossible_case":  "numeric ID or ABI layout establishing Deeplus type identity",
                     "compiler_retry_count":  0,
                     "fallback_count":  0
                 }
             ],
    "counts":  {
                   "unique_use_cases":  12,
                   "rows_with_one_selected_mechanism":  12,
                   "compiler_retry":  0,
                   "automatic_fallback":  0
               },
    "source_trace":  [
                         "Devel_ UX Diagnostic Matrix use_cases UC-01..12",
                         "Final Cross-Role Reconciliation sections 5, 6.6 and 7",
                         "Controlling gate AT-SFD-UC"
                     ]
}
```
<!-- POST_PR16_UNIT_END:SFD-N001 -->

<!-- POST_PR16_UNIT_BEGIN:SFD-N007 -->
```json
{
    "schema":  "deeplus.codex-design.static-first-dynamic-diagnostic-oracle-binding.r1",
    "status":  "LOCAL_NONCANONICAL_NONACTIVATABLE",
    "immutable_source":  {
                             "filename":  "Test_Deeplus_Static_First_Dynamic_Facet_Independent_Review_Pack_R1.zip",
                             "bytes":  33472,
                             "sha256":  "34a1864d555b45f8088d4c8d91685b8d424a91ea526135a422965e882e5a5536",
                             "member":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json"
                         },
    "binding_policy":  "Each local row binds an exact immutable Test_ row identity to controlling Design_ precedence and, for core rows, the positive semantic-event phase crosswalk for the same guard. Source content is referenced, not reauthored.",
    "diagnostic_authority":  "LOGICAL_FAMILY_AND_PRECEDENCE_ONLY_NO_ACTIVE_REGISTRY_CODES",
    "precedence":  [
                       {
                           "rank":  1,
                           "check":  "profile, source-surface and recovery admission",
                           "suppresses":  "all later stages"
                       },
                       {
                           "rank":  2,
                           "check":  "static type, Trait, label, identity and ProjectionGoal formation",
                           "suppresses":  "registry, ownership and escape stages"
                       },
                       {
                           "rank":  3,
                           "check":  "explicit dynamic boundary and registry/inspection authority presence",
                           "suppresses":  "route/no-route and structural diagnostics"
                       },
                       {
                           "rank":  4,
                           "check":  "admitted conformance/adapter, normalized key, duplicate and unique route",
                           "suppresses":  "mode/loan/result checks"
                       },
                       {
                           "rank":  5,
                           "check":  "mode, PlaceId, owner, region, transaction and lifetime",
                           "suppresses":  "responsibility/failure postconditions"
                       },
                       {
                           "rank":  6,
                           "check":  "effects, errors, suspension, isolation and cleanup",
                           "suppresses":  "visible failure selection"
                       },
                       {
                           "rank":  7,
                           "check":  "visible failure/result handling",
                           "suppresses":  "reflection/ABI/product diagnostics"
                       },
                       {
                           "rank":  8,
                           "check":  "reflection, serialization, ABI privacy and product-claim boundary",
                           "suppresses":  "none"
                       }
                   ],
    "tie_break":  "canonical semantic identity; never traversal/provider/import/source order",
    "blocked_not_auditable_ids":  [
                                      "SFD-FG-10-B",
                                      "SFD-FG-11-B",
                                      "SFD-FG-12-B",
                                      "SFD-FG-18-B",
                                      "SFD-FG-18-M",
                                      "SFD-FG-21-B",
                                      "SFD-FG-24-B",
                                      "SFD-FG-28-B",
                                      "SFD-PROP-001",
                                      "SFD-PROP-006",
                                      "SFD-PROP-010",
                                      "SFD-PROP-017",
                                      "SFD-PROP-018",
                                      "SFD-PROP-019",
                                      "SFD-PROP-021"
                                  ],
    "rows":  [
                 {
                     "oracle_id":  "SFD-FG-01-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-01",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-01-P",
                     "controlling_rule_ref":  "SFD-FG-01-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-01-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-01-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-01-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-01",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-01-N",
                     "controlling_rule_ref":  "SFD-FG-01-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-01-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-01-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-01-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-01",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-01-B",
                     "controlling_rule_ref":  "SFD-FG-01-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-01-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-01-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-01-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-01",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-01-M",
                     "controlling_rule_ref":  "SFD-FG-01-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-01-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-01-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-02-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-02",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-02-P",
                     "controlling_rule_ref":  "SFD-FG-02-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-02-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-02-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-02-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-02",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-02-N",
                     "controlling_rule_ref":  "SFD-FG-02-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-02-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-02-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-02-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-02",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-02-B",
                     "controlling_rule_ref":  "SFD-FG-02-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-02-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-02-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-02-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-02",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-02-M",
                     "controlling_rule_ref":  "SFD-FG-02-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-02-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-02-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-03-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-03",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-03-P",
                     "controlling_rule_ref":  "SFD-FG-03-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-03-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-03-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-03-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-03",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-03-N",
                     "controlling_rule_ref":  "SFD-FG-03-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-03-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-03-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-03-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-03",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-03-B",
                     "controlling_rule_ref":  "SFD-FG-03-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-03-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-03-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-03-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-03",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-03-M",
                     "controlling_rule_ref":  "SFD-FG-03-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-03-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-03-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-04-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-04",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-04-P",
                     "controlling_rule_ref":  "SFD-FG-04-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-04-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-04-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-04-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-04",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-04-N",
                     "controlling_rule_ref":  "SFD-FG-04-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-04-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-04-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-04-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-04",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-04-B",
                     "controlling_rule_ref":  "SFD-FG-04-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-04-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-04-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-04-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-04",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-04-M",
                     "controlling_rule_ref":  "SFD-FG-04-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-04-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-04-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-05-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-05",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-05-P",
                     "controlling_rule_ref":  "SFD-FG-05-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-05-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-05-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-05-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-05",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-05-N",
                     "controlling_rule_ref":  "SFD-FG-05-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-05-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-05-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-05-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-05",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-05-B",
                     "controlling_rule_ref":  "SFD-FG-05-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-05-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-05-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-05-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-05",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-05-M",
                     "controlling_rule_ref":  "SFD-FG-05-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-05-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-05-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-06-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-06",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-06-P",
                     "controlling_rule_ref":  "SFD-FG-06-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-06-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-06-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-06-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-06",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-06-N",
                     "controlling_rule_ref":  "SFD-FG-06-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-06-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-06-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-06-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-06",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-06-B",
                     "controlling_rule_ref":  "SFD-FG-06-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-06-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-06-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-06-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-06",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-06-M",
                     "controlling_rule_ref":  "SFD-FG-06-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-06-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-06-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-07-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-07",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-07-P",
                     "controlling_rule_ref":  "SFD-FG-07-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-07-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-07-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-07-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-07",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-07-N",
                     "controlling_rule_ref":  "SFD-FG-07-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-07-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-07-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-07-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-07",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-07-B",
                     "controlling_rule_ref":  "SFD-FG-07-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-07-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-07-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-07-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-07",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-07-M",
                     "controlling_rule_ref":  "SFD-FG-07-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-07-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-07-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-08-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-08",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-08-P",
                     "controlling_rule_ref":  "SFD-FG-08-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-08-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-08-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-08-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-08",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-08-N",
                     "controlling_rule_ref":  "SFD-FG-08-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-08-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-08-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-08-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-08",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-08-B",
                     "controlling_rule_ref":  "SFD-FG-08-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-08-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-08-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-08-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-08",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-08-M",
                     "controlling_rule_ref":  "SFD-FG-08-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-08-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-08-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-09-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-09",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-09-P",
                     "controlling_rule_ref":  "SFD-FG-09-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-09-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-09-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-09-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-09",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-09-N",
                     "controlling_rule_ref":  "SFD-FG-09-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-09-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-09-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-09-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-09",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-09-B",
                     "controlling_rule_ref":  "SFD-FG-09-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-09-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-09-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-09-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-09",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-09-M",
                     "controlling_rule_ref":  "SFD-FG-09-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-09-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-09-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-10-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-10",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-10-P",
                     "controlling_rule_ref":  "SFD-FG-10-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-10-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-10-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-10-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-10",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-10-N",
                     "controlling_rule_ref":  "SFD-FG-10-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-10-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-10-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-10-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-10",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-10-B",
                     "controlling_rule_ref":  "SFD-FG-10-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-10-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-10-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-10-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-10",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-10-M",
                     "controlling_rule_ref":  "SFD-FG-10-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-10-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-10-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-11-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-11",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-11-P",
                     "controlling_rule_ref":  "SFD-FG-11-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-11-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-11-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-11-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-11",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-11-N",
                     "controlling_rule_ref":  "SFD-FG-11-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-11-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-11-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-11-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-11",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-11-B",
                     "controlling_rule_ref":  "SFD-FG-11-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-11-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-11-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-11-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-11",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-11-M",
                     "controlling_rule_ref":  "SFD-FG-11-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-11-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-11-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-12-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-12",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-12-P",
                     "controlling_rule_ref":  "SFD-FG-12-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-12-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-12-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-12-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-12",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-12-N",
                     "controlling_rule_ref":  "SFD-FG-12-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-12-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-12-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-12-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-12",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-12-B",
                     "controlling_rule_ref":  "SFD-FG-12-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-12-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-12-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-12-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-12",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-12-M",
                     "controlling_rule_ref":  "SFD-FG-12-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-12-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-12-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-13-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-13",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-13-P",
                     "controlling_rule_ref":  "SFD-FG-13-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-13-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-13-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-13-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-13",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-13-N",
                     "controlling_rule_ref":  "SFD-FG-13-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-13-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-13-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-13-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-13",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-13-B",
                     "controlling_rule_ref":  "SFD-FG-13-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-13-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-13-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-13-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-13",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-13-M",
                     "controlling_rule_ref":  "SFD-FG-13-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-13-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-13-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-14-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-14",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-14-P",
                     "controlling_rule_ref":  "SFD-FG-14-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-14-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-14-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-14-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-14",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-14-N",
                     "controlling_rule_ref":  "SFD-FG-14-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-14-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-14-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-14-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-14",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-14-B",
                     "controlling_rule_ref":  "SFD-FG-14-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-14-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-14-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-14-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-14",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-14-M",
                     "controlling_rule_ref":  "SFD-FG-14-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-14-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-14-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-15-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-15",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-15-P",
                     "controlling_rule_ref":  "SFD-FG-15-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-15-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-15-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-15-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-15",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-15-N",
                     "controlling_rule_ref":  "SFD-FG-15-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-15-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-15-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-15-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-15",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-15-B",
                     "controlling_rule_ref":  "SFD-FG-15-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-15-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-15-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-15-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-15",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-15-M",
                     "controlling_rule_ref":  "SFD-FG-15-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-15-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-15-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-16-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-16",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-16-P",
                     "controlling_rule_ref":  "SFD-FG-16-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-16-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-16-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-16-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-16",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-16-N",
                     "controlling_rule_ref":  "SFD-FG-16-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-16-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-16-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-16-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-16",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-16-B",
                     "controlling_rule_ref":  "SFD-FG-16-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-16-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-16-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-16-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-16",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-16-M",
                     "controlling_rule_ref":  "SFD-FG-16-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-16-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-16-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-17-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-17",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-17-P",
                     "controlling_rule_ref":  "SFD-FG-17-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-17-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-17-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-17-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-17",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-17-N",
                     "controlling_rule_ref":  "SFD-FG-17-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-17-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-17-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-17-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-17",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-17-B",
                     "controlling_rule_ref":  "SFD-FG-17-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-17-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-17-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-17-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-17",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-17-M",
                     "controlling_rule_ref":  "SFD-FG-17-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-17-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-17-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-18-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-18",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-18-P",
                     "controlling_rule_ref":  "SFD-FG-18-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-18-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-18-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-18-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-18",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-18-N",
                     "controlling_rule_ref":  "SFD-FG-18-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-18-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-18-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-18-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-18",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-18-B",
                     "controlling_rule_ref":  "SFD-FG-18-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-18-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-18-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-18-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-18",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-18-M",
                     "controlling_rule_ref":  "SFD-FG-18-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-18-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-18-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-19-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-19",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-19-P",
                     "controlling_rule_ref":  "SFD-FG-19-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-19-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-19-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-19-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-19",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-19-N",
                     "controlling_rule_ref":  "SFD-FG-19-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-19-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-19-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-19-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-19",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-19-B",
                     "controlling_rule_ref":  "SFD-FG-19-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-19-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-19-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-19-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-19",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-19-M",
                     "controlling_rule_ref":  "SFD-FG-19-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-19-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-19-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-20-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-20",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-20-P",
                     "controlling_rule_ref":  "SFD-FG-20-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-20-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-20-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-20-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-20",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-20-N",
                     "controlling_rule_ref":  "SFD-FG-20-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-20-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-20-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-20-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-20",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-20-B",
                     "controlling_rule_ref":  "SFD-FG-20-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-20-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-20-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-20-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-20",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-20-M",
                     "controlling_rule_ref":  "SFD-FG-20-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-20-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-20-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-21-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-21",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-21-P",
                     "controlling_rule_ref":  "SFD-FG-21-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-21-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-21-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-21-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-21",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-21-N",
                     "controlling_rule_ref":  "SFD-FG-21-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-21-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-21-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-21-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-21",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-21-B",
                     "controlling_rule_ref":  "SFD-FG-21-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-21-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-21-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-21-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-21",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-21-M",
                     "controlling_rule_ref":  "SFD-FG-21-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-21-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-21-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-22-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-22",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-22-P",
                     "controlling_rule_ref":  "SFD-FG-22-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-22-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-22-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-22-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-22",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-22-N",
                     "controlling_rule_ref":  "SFD-FG-22-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-22-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-22-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-22-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-22",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-22-B",
                     "controlling_rule_ref":  "SFD-FG-22-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-22-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-22-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-22-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-22",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-22-M",
                     "controlling_rule_ref":  "SFD-FG-22-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-22-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-22-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-23-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-23",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-23-P",
                     "controlling_rule_ref":  "SFD-FG-23-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-23-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-23-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-23-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-23",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-23-N",
                     "controlling_rule_ref":  "SFD-FG-23-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-23-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-23-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-23-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-23",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-23-B",
                     "controlling_rule_ref":  "SFD-FG-23-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-23-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-23-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-23-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-23",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-23-M",
                     "controlling_rule_ref":  "SFD-FG-23-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-23-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-23-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-24-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-24",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-24-P",
                     "controlling_rule_ref":  "SFD-FG-24-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-24-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-24-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-24-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-24",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-24-N",
                     "controlling_rule_ref":  "SFD-FG-24-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-24-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-24-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-24-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-24",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-24-B",
                     "controlling_rule_ref":  "SFD-FG-24-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-24-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-24-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-24-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-24",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-24-M",
                     "controlling_rule_ref":  "SFD-FG-24-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-24-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-24-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-25-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-25",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-25-P",
                     "controlling_rule_ref":  "SFD-FG-25-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-25-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-25-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-25-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-25",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-25-N",
                     "controlling_rule_ref":  "SFD-FG-25-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-25-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-25-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-25-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-25",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-25-B",
                     "controlling_rule_ref":  "SFD-FG-25-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-25-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-25-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-25-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-25",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-25-M",
                     "controlling_rule_ref":  "SFD-FG-25-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-25-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-25-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-26-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-26",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-26-P",
                     "controlling_rule_ref":  "SFD-FG-26-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-26-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-26-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-26-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-26",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-26-N",
                     "controlling_rule_ref":  "SFD-FG-26-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-26-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-26-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-26-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-26",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-26-B",
                     "controlling_rule_ref":  "SFD-FG-26-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-26-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-26-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-26-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-26",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-26-M",
                     "controlling_rule_ref":  "SFD-FG-26-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-26-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-26-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-27-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-27",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-27-P",
                     "controlling_rule_ref":  "SFD-FG-27-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-27-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-27-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-27-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-27",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-27-N",
                     "controlling_rule_ref":  "SFD-FG-27-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-27-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-27-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-27-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-27",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-27-B",
                     "controlling_rule_ref":  "SFD-FG-27-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-27-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-27-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-27-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-27",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-27-M",
                     "controlling_rule_ref":  "SFD-FG-27-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-27-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-27-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-28-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-28",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-28-P",
                     "controlling_rule_ref":  "SFD-FG-28-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-28-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-28-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-28-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-28",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-28-N",
                     "controlling_rule_ref":  "SFD-FG-28-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-28-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-28-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-28-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-28",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-28-B",
                     "controlling_rule_ref":  "SFD-FG-28-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-28-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-28-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-28-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-28",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-28-M",
                     "controlling_rule_ref":  "SFD-FG-28-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-28-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-28-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-29-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-29",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-29-P",
                     "controlling_rule_ref":  "SFD-FG-29-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-29-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-29-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-29-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-29",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-29-N",
                     "controlling_rule_ref":  "SFD-FG-29-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-29-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-29-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-29-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-29",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-29-B",
                     "controlling_rule_ref":  "SFD-FG-29-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-29-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-29-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-29-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-29",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-29-M",
                     "controlling_rule_ref":  "SFD-FG-29-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-29-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-29-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-30-P",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-30",
                     "kind":  "positive",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-30-P",
                     "controlling_rule_ref":  "SFD-FG-30-P.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-30-P.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-30-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-30-N",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-30",
                     "kind":  "negative",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-30-N",
                     "controlling_rule_ref":  "SFD-FG-30-N.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-30-N.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-30-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-30-B",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-30",
                     "kind":  "boundary",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-30-B",
                     "controlling_rule_ref":  "SFD-FG-30-B.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-30-B.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-30-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-FG-30-M",
                     "source_kind":  "CORE",
                     "guard_id":  "FG-30",
                     "kind":  "mutation",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/core_oracles/SFD-FG-30-M",
                     "controlling_rule_ref":  "SFD-FG-30-M.guard_rule",
                     "owner_dependency_acceptance_ref":  "SFD-FG-30-M.authority_owner+dependencies+expected_outcome",
                     "event_crosswalk_ref":  "07_Semantic_Event_Impl_Phase_Crosswalk_R1.json#/SFD-FG-30-P",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-001",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-001",
                     "controlling_rule_ref":  "SFD-PROP-001.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-001.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-001",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-002",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-002",
                     "controlling_rule_ref":  "SFD-PROP-002.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-002.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-002",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-003",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-003",
                     "controlling_rule_ref":  "SFD-PROP-003.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-003.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-003",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-004",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-004",
                     "controlling_rule_ref":  "SFD-PROP-004.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-004.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-004",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-005",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-005",
                     "controlling_rule_ref":  "SFD-PROP-005.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-005.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-005",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-006",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-006",
                     "controlling_rule_ref":  "SFD-PROP-006.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-006.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-006",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-007",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-007",
                     "controlling_rule_ref":  "SFD-PROP-007.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-007.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-007",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-008",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-008",
                     "controlling_rule_ref":  "SFD-PROP-008.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-008.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-008",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-009",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-009",
                     "controlling_rule_ref":  "SFD-PROP-009.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-009.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-009",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-010",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-010",
                     "controlling_rule_ref":  "SFD-PROP-010.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-010.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-010",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-011",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-011",
                     "controlling_rule_ref":  "SFD-PROP-011.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-011.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-011",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-012",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-012",
                     "controlling_rule_ref":  "SFD-PROP-012.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-012.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-012",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-013",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-013",
                     "controlling_rule_ref":  "SFD-PROP-013.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-013.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-013",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-014",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-014",
                     "controlling_rule_ref":  "SFD-PROP-014.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-014.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-014",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-015",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-015",
                     "controlling_rule_ref":  "SFD-PROP-015.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-015.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-015",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-016",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-016",
                     "controlling_rule_ref":  "SFD-PROP-016.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-016.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-016",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-017",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-017",
                     "controlling_rule_ref":  "SFD-PROP-017.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-017.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-017",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-018",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-018",
                     "controlling_rule_ref":  "SFD-PROP-018.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-018.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-018",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-019",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-019",
                     "controlling_rule_ref":  "SFD-PROP-019.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-019.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-019",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-020",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-020",
                     "controlling_rule_ref":  "SFD-PROP-020.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-020.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-020",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "STATIC_LOGICAL_BINDING",
                     "execution_status":  "NOT_RUN"
                 },
                 {
                     "oracle_id":  "SFD-PROP-021",
                     "source_kind":  "PROPERTY",
                     "immutable_source_row_ref":  "Test_Deeplus_Static_First_Dynamic_Facet_Oracle_Matrix_R1.json#/metamorphic_property_tests/SFD-PROP-021",
                     "controlling_rule_ref":  "SFD-PROP-021.property+transformation+expected",
                     "owner_dependency_acceptance_ref":  "SFD-PROP-021.dependency+expected",
                     "event_crosswalk_ref":  null,
                     "property_binding_ref":  "PROPERTY:SFD-PROP-021",
                     "diagnostic_binding_ref":  "FINAL_CONTROLLING_PRECEDENCE_PLUS_EXACT_TEST_ROW",
                     "future_registry_code_or_null":  null,
                     "binding_state":  "NOT_AUDITABLE",
                     "execution_status":  "NOT_RUN"
                 }
             ],
    "counts":  {
                   "core":  120,
                   "property":  21,
                   "total":  141,
                   "unique":  141,
                   "static_judgeable":  126,
                   "not_auditable":  15,
                   "logical_binding_orphan_count":  0,
                   "event_crosswalk_core_orphan_count":  0,
                   "executed":  0,
                   "active_registry_codes":  0,
                   "product_pass":  0
               },
    "guards":  {
                   "designed_oracle_is_product_pass":  false,
                   "file_presence_closes_p1":  false,
                   "formatter_lsp_implementation_claim_count":  0
               }
}
```
<!-- POST_PR16_UNIT_END:SFD-N007 -->
