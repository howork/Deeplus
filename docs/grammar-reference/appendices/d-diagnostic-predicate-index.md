<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 D — 진단 및 검사기 술어

## 진단

| 진단 ID | 단계 | 심각도 | 상태 | 메시지 |
|---|---|---|---|---|
| `ABSTRACT_CLASS_INSTANTIATION_FORBIDDEN` | `checker` | `error` | `active` | An abstract class cannot be instantiated. |
| `ACCEPTED_NAMED_FUNCTION_BLOCK_REQUIRES_RETURN` | `checker` | `error` | `active` | Accepted ordinary named function blocks that produce a value must use explicit return; lambda/@match local results use ret. |
| `ACCEPT_WITH_GATE_REQUIRES_PREVIEW_FEATURE` | `checker` | `error` | `active` | An accept_with_gate example must reference at least one PREVIEW feature with explicit_feature_gate source activation. |
| `ACCESSOR_PROPERTY_HEADER_VISIBILITY_FORBIDDEN` | `checker` | `error` | `active` | Accessor property header must not carry member visibility; accessor visibility belongs on get/set. |
| `ACCESSOR_PROPERTY_MULTIPLE_ACCESSORS_REQUIRE_BLOCK` | `checker` | `error` | `active` | Multiple accessors require an accessor block after :=. |
| `ACCESSOR_PROPERTY_SEPARATOR_REQUIRED` | `checker` | `error` | `active` | Accessor property must use := between property header and accessor specification. |
| `ACCESSOR_PROPERTY_VISIBILITY_ON_ACCESSOR_REQUIRED` | `checker` | `error` | `active` | Accessor property visibility must be on get/set, not on property header. |
| `ACTOR_CHANNEL_FIFO_ORDER_VIOLATION` | `runtime` | `error` | `active` | Actor dequeue order does not preserve channel_sequence within one sender/receiver/mailbox-profile channel. |
| `ACTOR_DECLARATION_GRAMMAR_CLOSED_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ACTOR_MAILBOX_CAPACITY_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ACTOR_MAILBOX_CAPACITY_REQUIRES_STATIC_INT` | `checker` | `error` | `active` | actor mailbox capacity must be a statically known positive integer in the minimum profile. |
| `ACTOR_PROTOCOL_FAMILY_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ACTOR_PROTOCOL_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ACTOR_REQUEST_REPLY_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ACTOR_REQUEST_REPLY_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ACTOR_TURN_SELF_OR_CYCLIC_AWAIT_FORBIDDEN` | `checker` | `error` | `active` | An active actor turn cannot await a request whose statically proven dependency cycle requires the same actor turn to progress. |
| `AFFINE_UNIT_NOT_IN_PHASE_A` | `checker` | `error` | `active` | Affine units such as degrees Celsius are not part of the current profile measure profile. |
| `ALIASABLE_REJECTS_LIFECYCLE_OWNER` | `checker` | `error` | `active` | Aliasable is removed and lifecycle owners cannot be hidden behind alias vocabulary. |
| `ALIASABLE_REMOVED` | `checker` | `error` | `active` | Aliasable is removed from current source vocabulary. |
| `ALIASABLE_REMOVED_USE_SHARED_OR_PLAIN` | `checker` | `error` | `active` | Aliasable is not current-canonical public vocabulary. Use Plain for authority-free plain values, Shared<T> for alias creation, Shareable for observation safety, or explicit move/clone. |
| `ALIAS_PATTERN_OWNERSHIP_CONFLICT` | `checker` | `error` | `active` | A Pattern alias cannot coexist with a moved or exclusively borrowed descendant of the same subject. |
| `ALL_NAMED_ARGUMENT_LAYOUT_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ALL_NAMED_ARGUMENT_LAYOUT_ROUTE_UNREACHABLE` | `checker` | `error` | `active` | All-named argument layout separator must be reachable through ArgList in all-named contexts; positional/mixed arguments still require commas. |
| `ALL_NAMED_ARGUMENT_LAYOUT_SEPARATOR_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `AMBIGUOUS_CARET_ATTACHMENT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `AMBIGUOUS_EXTENSION_CANDIDATE` | `checker` | `error` | `active` | Multiple active extension candidates match and no deterministic specificity rule selects one. |
| `AMBIGUOUS_EXTENSION_SELECTOR` | `checker` | `error` | `active` | Multiple extension selectors match; use a qualified selector. |
| `AMBIGUOUS_NAMED_REST_OVERLOAD` | `checker` | `error` | `active` | Named rest overloads are ambiguous; source order and return type are not tie-breakers. |
| `AMBIGUOUS_REST_PARAMETER_OVERLOAD` | `checker` | `error` | `active` | Repeated positional rest overloads are ambiguous; source order and return type are not tie-breakers. |
| `AMBIGUOUS_UNIT_SYMBOL` | `checker` | `error` | `active` | Multiple active catalogs define the same unit symbol. Use a qualified unit symbol such as \`alias::unit\`. |
| `AMPERSAND_POLARITY_FEATURES_MUTUALLY_EXCLUSIVE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `AMPERSAND_POLARITY_UNRESOLVED` | `checker` | `error` | `active` | The \`&\` token is resolved by its closed current position: \`context expr\` is explicit context passing, while \`&anchor\` and infix \`&\` belong to their declared anchor/operand families. |
| `AND_THEN_KEYWORD_PAIR_MUST_BE_ADJACENT` | `lexer` | `error` | `active` | \`and then\` must be an adjacent keyword pair in the same Boolean-control form. |
| `ANNOTATION_ATTACHMENT_UNREACHABLE` | `checker` | `error` | `seed` | Annotation attachment grammar must be reachable from SourceItem. |
| `ANNOTATION_TARGET_REQUIRED` | `parser` | `error` | `active` | An annotation must be structurally attached to an annotatable declaration. |
| `ANONYMOUS_UNION_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ANY_REJECTS_SHARED_OWNER` | `checker` | `error` | `active` | Any minimum profile cannot erase Shared<T> owner responsibility. |
| `ARRAY_SCALAR_OPERATION_REQUIRES_CONTEXT_ANCHOR` | `checker` | `error` | `active` | NumericArray and scalar operation requires an explicit context anchor or named API; no implicit scalar lift. |
| `ARROW_ASSIGNMENT_TARGET_NOT_ALLOWED` | `checker` | `error` | `active` | Rightward flow binding cannot assign to an existing l-value. |
| `ASSIGNMENT_NUMERIC_TO_MEASURE_REQUIRES_EXPLICIT_UNIT` | `checker` | `error` | `active` | Assigning a numeric value to a Measure requires an explicit unit. |
| `ASSOCIATED_PROJECTION_REQUIRES_BOUND` | `checker` | `error` | `active` | Associated projection requires a trait bound declaring that associated requirement. |
| `ASSOCIATED_REQUIREMENT_PROJECTION_UNRESOLVED` | `checker` | `error` | `active` | Associated requirement projection cannot be resolved under the current witness/conformance environment. |
| `ASSOCIATED_REQUIREMENT_UNRESOLVED` | `checker` | `error` | `active` | Associated type/value requirement cannot be resolved in this witness or constraint environment. |
| `ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED` | `checker` | `error` | `active` | The initial associated static value profile requires immutable, Shareable, no-drop, authority-free, acyclic, statically materializable data. |
| `ASYNC_CALLABLE_LITERAL_NOT_CURRENT` | `parser` | `error` | `active` | #async callable literals are PREVIEW_DESIGN/nonactivatable. |
| `ASYNC_CAPTURE_DESCRIPTOR_REQUIRES_ASYNC_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_COLLECTOR_POLICY_NOT_ADMITTED` | `checker` | `error` | `active` | the current profile Stage 1 admits only List + finite AsyncSequence<T, ES> + named def#async transform throwing ET + exact result throws ES \| ET + sequential/source/failFast/cancelPending/buffer1. |
| `ASYNC_COLLECTOR_REQUIRES_PREVIEW` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_CORE_PRODUCT_SUPPORT_NOT_RUN` | `checker` | `error` | `active` | Async/Task/Actor core is language-design stable but product support is NOT_RUN. |
| `ASYNC_FOR_OUTCOME_MATCH_NOT_ADMITTED` | `parser` | `error` | `active` | A \`for await\` loop does not own a subjectless outcome match in the current profile. |
| `ASYNC_FUNCTION_DECLARATION_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_FUNCTION_DECLARATION_SURFACE_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_ITERATION_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_ITERATION_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_ITERATOR_PROTOCOL_PREVIEW_REQUIRES_FEATURE_GATE` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_MARKER_FORBIDDEN_ON_STABLE_DECLARATION` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ASYNC_TASK_CONTROL_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `AT_CONTROL_EXPR_REQUIRES_AT_PREFIX` | `checker` | `error` | `active` | Value-producing control expression requires @if/@match/@try/@scope spelling. |
| `AT_EXACT_INTRODUCER_LINE_BREAK_FORBIDDEN` | `parser` | `error` | `active` | An exact @ introducer cannot cross a physical line break. |
| `AT_MATCH_ARM_RETURN_IS_NOT_RESULT` | `checker` | `error` | `active` | \`return\` exits the enclosing named function and is not an @match arm result. |
| `AT_MATCH_BLOCK_ARM_REQUIRES_RET` | `checker` | `error` | `active` | A block arm in value-producing @match must produce its local result with \`ret\` on every normal path. |
| `AT_MATCH_SINGLE_EXPR_ARM_DOES_NOT_USE_RET` | `checker` | `error` | `active` | A direct \`@match\` arm expression does not use \`ret\`; write \`pattern => expr\` or use a block arm with \`ret expr\`. |
| `AUTHORITY_TOKEN_NOT_IN_SCOPE` | `lexer` | `error` | `active` | Required authority token is not in scope; EffectRow does not grant permission by itself. |
| `AWAIT_EXPRESSION_SURFACE_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `AWAIT_REQUIRED_FOR_ASYNC_CALL` | `checker` | `error` | `active` | Async function or async message result must be awaited in an async context. |
| `AWAIT_REQUIRES_ASYNC_TASK_CONTROL` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `BARE_CALLABLE_TYPE_FORBIDDEN` | `checker` | `note` | `seed` | Bare Callable is not current source vocabulary. Use an exact function type or a named trait/preview façade. |
| `BARE_CALL_ARGUMENT_MUST_BE_ATOMIC_OR_PARENTHESIZED` | `parser` | `error` | `active` | The bare argument before a trailing closure must be atomic or parenthesized. |
| `BARE_CARET_IS_POWER_NOT_BITWISE_XOR` | `checker` | `error` | `active` | Bare infix \`^\` is the right-associative power operator, not bitwise XOR; current bitwise XOR is \`^^\`. |
| `BARE_ENUM_CASE_NOT_ALLOWED` | `checker` | `error` | `active` | Bare enum case names are not injected into ordinary value namespace. Use \`::case\` or \`EnumType::case\`. |
| `BARE_FUNCTION_CALL_REQUIRES_TRAILING_CLOSURE` | `checker` | `error` | `active` | Bare ordinary call without a trailing closure is not part of this feature; use parentheses. |
| `BARE_FUNCTION_TYPE_FORBIDDEN` | `checker` | `note` | `seed` | Bare function façade is not sufficient here; preserve exact parameter, throws, effects, and call-mode information. |
| `BARE_FUNCTION_TYPE_REMOVED` | `checker` | `error` | `active` | Bare Function is not current source; use an exact function signature or the Stable Callable facade profile. |
| `BARE_PARENLESS_ORDINARY_CALL_NOT_CURRENT` | `parser` | `error` | `active` | The surface \`bare parenless ordinary call\` is recognized but is not current Deeplus. |
| `BASIC_INDEX_OPERATOR_STABLE_LAW` | `checker` | `note` | `active` | Basic index operator is stable design; advanced slicing/custom index surfaces remain separate features. |
| `BITFIELD_BACKING_MUST_BE_UNSIGNED_FIXED_WIDTH` | `checker` | `error` | `active` | Bitfield backing must be UInt8, UInt16, UInt32, UInt64, or UInt128. |
| `BITFIELD_C_ABI_NOT_IMPLIED` | `checker` | `error` | `active` | A Deeplus bitfield does not imply C compiler bitfield ABI compatibility. |
| `BITFIELD_DIRECT_FIELD_MUTATION_FORBIDDEN` | `checker` | `error` | `active` | Bitfield fields are immutable; use same-type derivation. |
| `BITFIELD_ENDIANNESS_REQUIRED` | `checker` | `error` | `active` | Bitfield byte encoding and decoding require an explicit endian argument. |
| `BITFIELD_FIELD_VALUE_OUT_OF_RANGE` | `checker` | `error` | `active` | The bitfield field value does not fit its declared width. |
| `BITFIELD_IMPLICIT_PADDING_FORBIDDEN` | `checker` | `error` | `active` | Bitfield padding must be written as an explicit reserved slot. |
| `BITFIELD_IMPLICIT_RAW_CONVERSION_FORBIDDEN` | `checker` | `error` | `active` | Bitfield/raw conversion must use \`.raw\` or checked Type::fromRaw. |
| `BITFIELD_LAYOUT_DIGEST_INCOMPLETE` | `provider` | `error` | `active` | The bitfield layout digest omits a normative layout component. |
| `BITFIELD_LAYOUT_WIDTH_MISMATCH` | `checker` | `error` | `active` | Bitfield slot widths must sum exactly to the backing width. |
| `BITFIELD_ORDER_NOT_ADMITTED` | `checker` | `error` | `active` | Phase-A bitfield order is exactly ::lsb0. |
| `BITFIELD_REQUIRED_FIELD_MISSING` | `checker` | `error` | `active` | A required bitfield materialization field is missing. |
| `BITFIELD_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `BITFIELD_RESERVED_BITS_NONZERO` | `runtime` | `error` | `active` | Checked raw conversion rejected nonzero reserved bits. |
| `BITFIELD_WIDTH_MUST_BE_POSITIVE_STATIC_INT` | `checker` | `error` | `active` | Bitfield slot width must be a positive compile-time integer. |
| `BITWISE_COMPLEMENT_IS_PREFIX_ONLY` | `checker` | `error` | `active` | Bitwise complement is prefix-only: write \`~~x\`. |
| `BITWISE_COMPLEMENT_REQUIRES_KNOWN_WIDTH` | `checker` | `error` | `active` | \`~~\` requires a packed known-width/finite-domain value or an admitted exact-integer NumericArray carrier. |
| `BITWISE_OPERATOR_DOES_NOT_ACCEPT_BOOL` | `checker` | `error` | `active` | Scalar Bool is not a pointwise glyph operand domain; use not, and, or, and then, or otherwise. |
| `BITWISE_OPERATOR_MIXED_DOMAIN_REQUIRES_EXPLICIT_CONVERSION` | `checker` | `error` | `active` | Pointwise logical operands require one exact normalized packed domain or the same NumericArray shape and integer element domain; use an explicit conversion. |
| `BITWISE_OPERATOR_MIXED_WIDTH_REQUIRES_EXPLICIT_CAST` | `checker` | `error` | `active` | Mixed-width pointwise logical operands require explicit width conversion before the operation. |
| `BITWISE_OPERATOR_REQUIRES_BITWISE_OPERANDS` | `checker` | `error` | `active` | Pointwise logical glyphs require a packed known-width/finite-domain value or an exact same-shape NumericArray of one known-width integer element domain. |
| `BITWISE_RESULT_USED_AS_BOOL` | `checker` | `error` | `active` | Pointwise logical glyphs preserve their packed or shaped carrier and do not produce a Bool predicate; compare or query explicitly. |
| `BLOCK_COMMENT_DASH_RUN_STYLE_MISMATCH` | `lexer` | `warning` | `active` | The nested block comment closes correctly, but its dash-run length differs from the corresponding opener. |
| `BLOCK_COMMENT_NESTING_UNCLOSED` | `lexer` | `error` | `active` | Nested block comment was not completely closed. |
| `BLOCK_COMMENT_UNTERMINATED` | `lexer` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `BODYLESS_MEMBER_MUST_BE_OPEN` | `checker` | `error` | `active` | Body-less member declaration must be an open slot and use the + suffix. |
| `BODYLESS_ORDINARY_FUNCTION_NOT_CURRENT` | `parser` | `error` | `active` | Only a trait requirement or declared signature context may omit a function body. |
| `BORROW_ESCAPE_OWNER_REGION` | `checker` | `error` | `active` | Borrowed view escapes the owner region. |
| `BOUNDED_INDEX_LENGTH_MISMATCH` | `checker` | `error` | `active` | The bounded list element count must equal the asserted closed logical-domain cardinality. |
| `BOUNDED_INDEX_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `BOUNDED_LIST_CALL_ARGUMENT_FORBIDDEN` | `parser` | `error` | `active` | A bounded list contains expressions only; call labels, evidence arguments and unfolding are forbidden. |
| `BOUND_LITERAL_LENGTH_MISMATCH` | `checker` | `error` | `active` | The number of elements does not equal the declared closed logical-domain cardinality. |
| `BOX_OWNERSHIP_VIOLATION` | `checker` | `error` | `active` | Box is a unique owner; use-after-move, duplicate ownership, escaping borrow, or missing cleanup is forbidden. |
| `BREAK_TARGET_NOT_IN_SCOPE` | `checker` | `error` | `active` | Break/continue target does not refer to an enclosing loop scope. |
| `BREAK_VALUE_REQUIRES_LOOP_OUTCOME_MATCH` | `checker` | `error` | `active` | Value-carrying break requires an immediately following loop outcome match. |
| `BROADCAST_FORBIDDEN_FOR_DOT_PRODUCT` | `checker` | `error` | `seed` | Broadcast forbidden for dot product |
| `BROADCAST_FORBIDDEN_FOR_MATRIX_PRODUCT` | `checker` | `error` | `seed` | Broadcast forbidden for matrix product |
| `BROADCAST_MARKER_CONTEXT_FORBIDDEN` | `checker` | `error` | `seed` | Broadcast marker context forbidden |
| `BROADCAST_MARKER_NOT_A_VALUE` | `checker` | `error` | `seed` | Broadcast marker not a value |
| `BROADCAST_MARKER_POLARITY_IS_CONTEXT_ANCHOR` | `checker` | `error` | `active` | In the current profile, \`&\` in NumericArray contextual operations marks the context-providing anchor operand, not the adapted operand. Use \`&matrix + row\`, not \`matrix + &row\`. |
| `BYTES_LITERAL_HASH_BYTES_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `BYTES_LITERAL_INVALID_HEX_ESCAPE` | `checker` | `error` | `active` | #bytes literal requires two hex digits in \\xHH escapes. |
| `BYTES_LITERAL_NON_ASCII_DIRECT_CHAR` | `checker` | `error` | `active` | #bytes literal admits only ASCII direct characters and byte escapes. |
| `BYTES_LITERAL_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `BYTES_LITERAL_UNICODE_ESCAPE_NOT_ALLOWED` | `lexer` | `error` | `active` | Unicode escapes are not allowed in #bytes literals. |
| `BYTES_NOT_IMPLICITLY_CONVERTIBLE_TO_STRING` | `checker` | `error` | `active` | Bytes is not implicitly convertible to String. |
| `BYTE_LITERAL_NON_BYTE_SCALAR` | `lexer` | `error` | `active` | A Bytes literal admits ASCII direct bytes and byte escapes only; use \`\\xHH\` for arbitrary bytes. |
| `BYTE_VIEW_PROFILE_NOT_ADMITTED` | `checker` | `error` | `active` | ByteView requires live Bytes-owner provenance, contiguous byte-addressable storage, and no assumed text encoding or String semantics. |
| `CALLABLE_PROFILE_COMBINATION_NOT_ADMITTED` | `parser` | `error` | `active` | The callable profile combination is outside the closed Phase-A compatibility table. |
| `CALLABLE_PROFILE_DUPLICATE` | `parser` | `error` | `active` | A callable profile may occur at most once in a cluster. |
| `CALLABLE_PROFILE_LITERAL_ATTACHMENT_REQUIRED` | `lexer` | `error` | `active` | The final callable profile and literal { must be adjacent. |
| `CALLABLE_PROFILE_ONLY_OVERLOAD_FORBIDDEN` | `checker` | `error` | `active` | Callable responsibility profiles cannot be the sole overload discriminator. |
| `CALLABLE_PROFILE_ORDER_NONCANONICAL` | `parser` | `error` | `active` | Callable profiles must follow scoped, once, mut, pure-or-guard axis order. |
| `CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN` | `parser` | `error` | `active` | Member callables use +, -, or # visibility, and nested local functions have lexical visibility; public/common/private are top-level-only callable visibility words. |
| `CALLBACK_EFFECT_NOT_PROPAGATED` | `checker` | `error` | `active` | Callback effects must be propagated or handled explicitly. |
| `CALLBACK_THROWS_NOT_PROPAGATED` | `checker` | `error` | `active` | Callback throws row must be propagated or handled explicitly. |
| `CALLER_CALLBACK_BORROW_ESCAPE_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CALLER_PROFILE_REMOVED_USE_SCOPED` | `parser` | `error` | `active` | #caller is not current; invocation-bounded nonescape uses #scoped. |
| `CALL_ARGUMENT_SEPARATOR_REQUIRED` | `parser` | `error` | `active` | A comma is required unless this is the all-named newline layout; that layout admits only named or named-unfold arguments. |
| `CANCELLATION_IS_NOT_ERRORSET_MEMBER` | `checker` | `note` | `seed` | Cancellation is a control axis, not a member of ErrorSet. Do not put it in throws. |
| `CANNOT_INFER_REST_ELEMENT_TYPE_FROM_EMPTY_ARGUMENTS` | `checker` | `error` | `active` | The element type of an empty repeated-argument call cannot be inferred without an expected type or explicit generic argument. |
| `CANONICAL_TYPE_NAME_INT` | `checker` | `warning` | `active` | \`int\` is not canonical Deeplus spelling; use \`Int\`. |
| `CAPABILITY_CONFORMANCE_NOT_USER_AUTHORIZED` | `checker` | `note` | `seed` | This capability predicate is checker-internal and cannot be made true by ordinary user conformance. |
| `CARET_ATTACHMENT_AMBIGUOUS` | `parser` | `error` | `active` | Caret ownership is ambiguous; write attached \`A^\` for transpose or spaced \`a ^ b\` for power. |
| `CARET_INFIX_REQUIRES_SPACING` | `checker` | `error` | `active` | Infix \`^\` power uses spacing (\`a ^ b\`). Attached postfix transpose is written without spacing (\`A^\`). |
| `CARET_POWER_REQUIRES_EXPLICIT_PARENTHESES_FOR_CHAIN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CAST_MODIFIER_MUST_BE_ADJACENT` | `parser` | `error` | `active` | The \`?\` or \`!\` cast modifier must be adjacent to \`as\`. |
| `CATCHES_CANCELLATION_AS_ERROR_FORBIDDEN` | `checker` | `error` | `seed` | catch handles recoverable Error values and cannot absorb Cancellation as an Error. |
| `CHAINED_POWER_REQUIRES_PARENTHESES` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CHAR_IS_GRAPHEME_NOT_SCALAR` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CHAR_IS_NOT_CODE_UNIT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CHAR_LITERAL_EMPTY` | `lexer` | `error` | `active` | Char literal cannot be empty. |
| `CHAR_LITERAL_REQUIRES_ONE_SCALAR` | `lexer` | `error` | `active` | A Char literal must decode to exactly one Unicode scalar value. |
| `CHAR_LITERAL_SURROGATE_FORBIDDEN` | `lexer` | `error` | `active` | A Unicode surrogate is not a Unicode scalar value and cannot form Char. |
| `CHAR_LITERAL_TOO_MANY_GRAPHEMES` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CHECKER_INTERNAL_FEATURE_NOT_SOURCE` | `checker` | `error` | `seed` | checker_internal feature is not ordinary source syntax in R49. |
| `CHOICE_HARD_VALUE_UNION_PREVIEW_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CHOICE_REQUIRES_PREVIEW_FEATURE` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `CLASS_BODY_REQUIRED` | `parser` | `error` | `active` | An ordinary, value, or resource class requires a body; only a data class may omit it. |
| `CLASS_HASH_SEALED_SPELLING_REMOVED` | `parser` | `error` | `active` | The hash-combined sealed-class spelling is removed; write \`sealed class\`. |
| `CLASS_INSTANCE_METHOD_REQUIRES_DISPATCH_MARKER` | `parser` | `error` | `active` | A class-like instance method requires exactly one dispatch marker: \`.\`, \`+\`, \`*.\`, or \`*+\`. |
| `CLASS_IS_FINAL_BY_DEFAULT` | `checker` | `error` | `active` | A concrete class is final unless declared open or sealed class; it cannot be subclassed here. |
| `CLASS_MODIFIER_COMBINATION_INVALID` | `checker` | `error` | `active` | The selected class flavor and modifier combination is not admitted. |
| `CLAUSE_LEVEL_DEFAULT_MUST_BE_OTHERWISE` | `checker` | `error` | `active` | Clause-level default must use \`otherwise\`; \`_\` remains pattern discard only. |
| `CLAUSE_LEVEL_WILDCARD_PREFER_OTHERWISE` | `checker` | `warning` | `seed` | Use \`otherwise\` for a clause-level default; \`_\` remains pattern discard and legacy wildcard. |
| `CLEANUP_BUDGET_BODY_POSITION_REMOVED` | `checker` | `error` | `active` | cleanup budget is a class-level header clause, not an ordinary member. |
| `CLEANUP_BUDGET_CAMELCASE_REMOVED` | `checker` | `error` | `active` | cleanupBudget spelling is removed; use cleanup budget block spelling. |
| `CLEANUP_DECLARATION_DIRECT_CALL_FORBIDDEN` | `checker` | `error` | `active` | A def#cleanup declaration is invoked only by lifecycle semantics and cannot be called or referenced as a method value. |
| `CLEANUP_LEGACY_SPELLING_REMOVED_USE_DEF_HASH_CLEANUP` | `parser` | `error` | `active` | Legacy destructor/drop spellings are not current; use def#cleanup(). |
| `CLEANUP_VISIBILITY_SIGIL_FORBIDDEN` | `parser` | `error` | `active` | def#cleanup is a lifecycle hook and cannot carry a member visibility sigil. |
| `CLOSURE_ASYNC_AWAIT_IN_SYNC` | `checker` | `error` | `seed` | Closure async await in sync |
| `CLOSURE_BORROW_CAPTURE_ESCAPES` | `checker` | `error` | `seed` | Closure borrow capture escapes |
| `CLOSURE_CAPTURE_DESCRIPTOR_STABLE_BUT_PRODUCT_NOT_RUN` | `checker` | `info` | `active` | Closure capture descriptors are Stable design in the current profile, but production parser/checker support remains NOT_RUN. |
| `CLOSURE_CAPTURE_ESCAPES_REGION` | `checker` | `error` | `seed` | Closure capture would outlive the borrowed owner region. |
| `CLOSURE_CAPTURE_LIST_REQUIRED_FOR_ESCAPING` | `checker` | `error` | `seed` | Closure capture list required for escaping |
| `CLOSURE_CAPTURE_NOT_TRANSFERABLE_TO_TASK` | `checker` | `error` | `seed` | Closure capture not transferable to task |
| `CLOSURE_CAPTURE_SHORTHAND_REQUIRES_REUSABLE_VALUE` | `checker` | `error` | `seed` | Closure capture shorthand requires reusable value |
| `CLOSURE_INOUT_CAPTURE_REQUIRES_CALLER` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CLOSURE_INOUT_CAPTURE_REQUIRES_SCOPED_MUT` | `checker` | `error` | `active` | An inout closure capture requires the #scoped#mut profile and cannot escape or overlap another mutable access. |
| `CLOSURE_INOUT_CAPTURE_SUSPENDS` | `checker` | `error` | `seed` | Closure inout capture suspends |
| `CLOSURE_MOVE_CAPTURE_CONSUMES_SOURCE` | `checker` | `error` | `seed` | Closure move capture consumes source |
| `CLOSURE_MUT_CALL_REQUIRES_MUTABLE_PLACE` | `checker` | `error` | `active` | A \`#mut\` callable invocation requires one exclusive mutable environment place; overlapping or reentrant environment access is not admitted. |
| `CLOSURE_ONCE_CALL_CONSUMES_CLOSURE` | `checker` | `error` | `seed` | Closure once call consumes closure |
| `CLOSURE_ONCE_USED_AFTER_CALL` | `checker` | `error` | `active` | A \`#once\` callable's call right was already consumed by its first invocation; a second call or later use is forbidden. |
| `CLOSURE_SELF_CAPTURE_REQUIRES_EXPLICIT_MODE` | `checker` | `error` | `seed` | Closure self capture requires explicit mode |
| `CLOSURE_VAR_CAPTURE_REQUIRES_MUT_CALL_MODE` | `checker` | `error` | `seed` | Closure var capture requires mut call mode |
| `COLLECTION_FREEZE_TRANSITION_NOT_ADMITTED` | `checker` | `error` | `active` | freeze requires exclusive mutable ownership and an admitted immutable/shareable target representation. |
| `COLLECTION_GET_REQUIRES_REUSABLE_VALUE` | `checker` | `error` | `active` | By-value collection get requires reusable value law. |
| `COLLECTION_IS_NOT_SEQUENCE_BY_DEFAULT` | `checker` | `note` | `seed` | Collection and Sequence have different replay/ownership laws; a collection is not automatically a sequence façade. |
| `COLLECTION_OPERATOR_REQUIRES_NAMED_MESSAGE` | `checker` | `error` | `seed` | Collection operator requires named message |
| `COLLECTION_SNAPSHOT_PROFILE_NOT_ADMITTED` | `checker` | `error` | `active` | snapshot must produce an independent value with explicit copy or copy-on-write responsibility. |
| `COLLECTION_TRAVERSAL_ROLE_MISMATCH` | `checker` | `error` | `active` | A collection value and a traversal handle are distinct responsibilities and are not automatically interchangeable. |
| `COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED` | `checker` | `error` | `active` | Column-vector semicolon form must follow the current profile orientation law: \`#[a,b]\` is rank-1 \`#N[T]\`; \`#[a;b]\` is column \`#N,1[T]\`; explicit row matrix is \`#1,N[...]\`. |
| `COMPANION_OBJECT_NOT_CURRENT` | `checker` | `error` | `active` | Deeplus has no implicit companion object or singleton; use the exact nominal, extension, Trait-associated, or runtime owner domain. |
| `COMPARISON_CHAIN_MIXED_DIRECTION_REQUIRES_EXPLICIT_AND` | `checker` | `error` | `active` | Mixed-direction comparison chains require explicit \`and\`. |
| `COMPARISON_CHAIN_OPERAND_HAS_EFFECTS` | `checker` | `error` | `active` | Comparison chain operands should not hide effects inside mathematical-looking predicates. |
| `COMPARISON_CHAIN_OPERATOR_MUST_BE_PURE` | `checker` | `error` | `active` | Comparison chain operators must be pure and no-throw. |
| `COMPARISON_CHAIN_OPERATOR_NOT_IN_PHASE_A` | `checker` | `error` | `active` | Comparison chains allow only <, <=, >, >= in the current profile. |
| `COMPLEX_BITWISE_NOT_DEFINED` | `checker` | `error` | `active` | Bitwise and pointwise-logical glyphs are not defined for Complex values. |
| `COMPLEX_COMPONENT_REP_MISMATCH` | `checker` | `error` | `active` | Complex real and imaginary components must use one exact admitted Rep. |
| `COMPLEX_FOREIGN_VALUE_ABI_REQUIRES_TARGET_PROFILE` | `checker` | `error` | `active` | Passing Complex through a foreign ABI requires an explicit target ABI profile. |
| `COMPLEX_IEEE_VALUE_NOT_STRONG_EQ` | `checker` | `error` | `active` | A Float-profile Complex value cannot supply strong Eq because NaN remains unordered. |
| `COMPLEX_KEY_REQUIRES_EXPLICIT_POLICY` | `checker` | `error` | `active` | Using Complex as a key requires an explicit equality and hashing policy. |
| `COMPLEX_MIXED_REP_REQUIRES_EXPLICIT_CONVERSION` | `checker` | `error` | `active` | Mixed Complex<Float32> and Complex<Float64> operands require an explicit conversion. |
| `COMPLEX_ORDERING_NOT_DEFINED` | `checker` | `error` | `active` | Complex values have no intrinsic total ordering. |
| `COMPLEX_REMAINDER_NOT_DEFINED` | `checker` | `error` | `active` | Complex remainder is not defined; use an explicitly named domain operation. |
| `COMPLEX_REP_PROFILE_NOT_ADMITTED` | `checker` | `error` | `active` | The initial Complex profile admits only Float32 and Float64 component representations. |
| `COMPLEX_TYPED_INTEGER_REQUIRES_EXPLICIT_CONVERSION` | `checker` | `error` | `active` | A typed integer operand does not implicitly become a Complex component; convert it explicitly. |
| `COMPREHENSION_FOR_AWAIT_REQUIRES_ASYNC_ITERATION` | `checker` | `error` | `active` | \`for await\` requires the async iteration design profile and does not imply general async task support. |
| `CONDITION_HAS_EFFECTFUL_OPERAND` | `checker` | `error` | `active` | A condition operand has effects; use explicit sequencing or a pure guard. |
| `CONFORMANCE_DECLARATION_REQUIRES_CONFORMS_KEYWORD` | `lexer` | `error` | `active` | Conformance declarations use \`conformance Type conforms Trait\`, not \`impl Trait for Type\` or \`T: Trait\`. |
| `CONFORMANCE_EVIDENCE_ORIGIN_NOT_UNIQUE` | `checker` | `error` | `active` | A root conformance evidence selector must resolve to exactly one visible coherent nominal conformance. |
| `CONFORMANCE_EXTENSION_DELEGATION_MUST_BE_EXPLICIT` | `checker` | `error` | `active` | Delegation from a conformance requirement to an extension selector must be explicit and fully identified. |
| `CONFORMANCE_LAW_PROOF_BLOCK_REQUIRES_PREVIEW` | `checker` | `error` | `active` | Conformance proof blocks require a future proof preview; Stable law declarations are documentation contracts only. |
| `CONFORMANCE_LAW_UNCHECKED_BY_PRODUCT` | `checker` | `info` | `seed` | Conformance law declaration is language-design Stable but has no product checker receipt in this package. |
| `CONFORMANCE_REQUIREMENT_BINDING_MISSING` | `checker` | `error` | `active` | A conformance must explicitly bind every required trait item. |
| `CONFORMS_REQUIRES_KEYWORD` | `lexer` | `error` | `active` | Trait/capability conformance must use \`conforms\` in the stable profile. |
| `CONSTRAINTS_SOLVER_AGENT_REQUIRES_FEATURE_GATE` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CONSTRAINT_USED_AS_EXISTENTIAL` | `checker` | `error` | `active` | A responsibility constraint is not a value type. Use \`any Trait\` or \`any Plain\` for an existential boundary. |
| `CONSTRUCTOR_CHAIN_TERMINAL_MUST_BE_NEW` | `checker` | `error` | `active` | A same-type constructor chain must terminate at root \`new\`. |
| `CONSTRUCTOR_DELEGATION_ARGUMENT_EFFECT_NOT_DECLARED` | `checker` | `error` | `active` | Effects from selected constructor delegation arguments must be declared by the delegating constructor. |
| `CONSTRUCTOR_DELEGATION_ARGUMENT_THROWS_NOT_DECLARED` | `checker` | `error` | `active` | Throws from selected constructor delegation arguments must be declared by the delegating constructor. |
| `CONSTRUCTOR_DELEGATION_CYCLE` | `checker` | `error` | `active` | Same-type constructor delegation graph must be acyclic. |
| `CONSTRUCTOR_DELEGATION_GRAPH_NOT_ADMITTED` | `checker` | `error` | `active` | A constructor delegation list must select exactly one target, keep same-type delegation acyclic, reach one root constructor, and make that root select exactly one superclass constructor without observing self in a guard. |
| `CONSTRUCTOR_DELEGATION_GUARD_CANNOT_OBSERVE_SELF` | `checker` | `error` | `active` | Constructor delegation guards run before initialization and cannot observe \`self\`. |
| `CONSTRUCTOR_DELEGATION_GUARD_NOT_PURE` | `checker` | `error` | `active` | Constructor delegation guards must be pure, synchronous, no-throw, and effect-free. |
| `CONSTRUCTOR_DELEGATION_MIXES_SAME_TYPE_AND_SUPER` | `checker` | `error` | `active` | A constructor delegation decision list cannot mix same-type and super targets. |
| `CONSTRUCTOR_DELEGATION_NOT_EXHAUSTIVE` | `checker` | `error` | `active` | Same-type constructor delegation must select exactly one target on every successful path. |
| `CONSTRUCTOR_DELEGATION_TARGET_NOT_FOUND` | `checker` | `error` | `active` | Constructor header delegation target was not found. |
| `CONSTRUCTOR_OR_CLEANUP_DISPATCH_MARKER_FORBIDDEN` | `parser` | `error` | `active` | Constructors and def#cleanup declarations cannot use dispatch markers. |
| `CONSTRUCTOR_OR_DROP_DISPATCH_MARKER_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `CONSTRUCTOR_REQUIRES_NAME` | `parser` | `error` | `active` | Constructor declarations require a name: write \`def! new(...)\` or \`def! name(...)\`. |
| `CONSTRUCTOR_SPELLING_REMOVED_USE_DEF_BANG` | `parser` | `error` | `active` | Constructors use def! only; def#ctor, def#constructor, and $! are removed. |
| `CONTEXTUAL_LAMBDA_EXPECTED_CALLABLE_REQUIRED` | `checker` | `error` | `active` | A contextual { expr } lambda requires one already-selected expected callable type; otherwise write { => expr }. |
| `CONTEXT_ANCHOR_EFFECTFUL_CONTEXT_NOT_ENABLED` | `checker` | `error` | `active` | Effectful context anchors such as transaction/retry/tracing are not part of the NumericArray context-anchor MSP. |
| `CONTEXT_ANCHOR_MULTIPLE_ANCHORS_UNSUPPORTED` | `checker` | `error` | `active` | Multiple context anchors in one operation are not supported in the MSP. |
| `CONTEXT_ANCHOR_NOT_A_VALUE` | `checker` | `error` | `active` | \`&expr\` is not a standalone value in the context-anchor MSP. |
| `CONTEXT_ANCHOR_REQUIRES_ELIGIBLE_OPERATION` | `checker` | `error` | `active` | Context anchors are only valid as operands of an eligible contextual operation. |
| `CONTEXT_ANCHOR_SCOPE_IS_NEAREST_OPERATION` | `checker` | `error` | `active` | The context anchor applies only to the nearest operation in the MSP. |
| `CONTEXT_ARGUMENT_NOT_EXPECTED` | `checker` | `error` | `active` | An ordinary parameter does not accept a context-marked argument. |
| `CONTEXT_ARGUMENT_REQUIRED` | `checker` | `error` | `active` | A context parameter requires a matching explicit context argument. |
| `CONTEXT_EVIDENCE_ROLE_NOT_REGISTERED` | `checker` | `error` | `active` | &expr has no admitted context-evidence role at this source position. |
| `CONTEXT_FUNCTION_TYPE_MISMATCH` | `checker` | `error` | `active` | Function types with context parameter roles are not interchangeable with ordinary function types. |
| `CONTEXT_KEYWORD_RESERVED_FOR_CONTEXT_ROLE` | `lexer` | `error` | `active` | \`context\` is recognized only in the Stable explicit context parameter, argument, and function-type role positions; it never requests ambient lookup. |
| `CONTEXT_MARKER_NOT_A_VALUE` | `checker` | `error` | `active` | A context marker does not produce a first-class value. |
| `CONTEXT_PARAMETER_DEFAULT_FORBIDDEN` | `checker` | `error` | `active` | Context parameters cannot have default arguments in the MSP. |
| `CONTEXT_PARAMETER_LIMIT_EXCEEDED` | `checker` | `error` | `active` | The explicit context parameter MSP allows at most one context parameter per function. |
| `CONTEXT_PARAMETER_NOT_APPLIED_AUTOMATICALLY` | `checker` | `error` | `active` | A context parameter is not automatically applied to body operations. |
| `CONTEXT_ROLE_MISMATCH_IN_OVERRIDE` | `checker` | `error` | `active` | Override or witness parameter role does not match the requirement. |
| `CONTEXT_VALUE_REQUIRES_REUSABLE_SHAREABLE` | `checker` | `error` | `active` | Context value must be reusable, Shareable, no-drop, and authority-free in the minimum profile. |
| `CONTRAVARIANT_TYPE_PARAM_USED_IN_PRODUCER_POSITION` | `checker` | `error` | `active` | A contravariant type parameter cannot be used in a producer/output/read position. |
| `COPYABLE_REMOVED_USE_PLAIN_OR_SHARED` | `checker` | `error` | `active` | Copyable is not current-canonical public vocabulary. Choose Plain, Shared<T>, explicit clone/derivation, or explicit move according to the responsibility you need. |
| `COVARIANT_TYPE_PARAM_USED_IN_CONSUMER_POSITION` | `checker` | `error` | `active` | A covariant type parameter cannot be used in a consumer/input/write position. |
| `CROSSWALK_REFERENCE_UNRESOLVED` | `design_static` | `error` | `active` | Feature-grammar crosswalk references must resolve to grammar productions, alternatives, examples, or smoke snippets. |
| `CURRENCY_CONVERSION_REQUIRES_PROVIDER` | `checker` | `error` | `active` | Currency conversion requires an explicit FX/provider policy. |
| `CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT` | `parser` | `error` | `active` | Custom operator declarations are not current Deeplus; use a named Trait method or function. |
| `DATA_CLASS_AUTOMATIC_UNFOLD_NOT_CURRENT` | `checker` | `error` | `active` | Data classes do not receive an automatic ProjectionRow; unfold an explicit schema view instead. |
| `DATA_CLASS_MATERIALIZATION_PROFILE_NOT_SATISFIED` | `checker` | `error` | `active` | This data class has custom initialization, mutable/resource state, effectful defaults, or hidden invariants and must use a constructor. |
| `DECLARATION_TILDE_FORBIDDEN` | `parser` | `error` | `active` | A declared body selector has no leading tilde; retain tilde only on receiver calls or the top-level target separator. |
| `DECL_CLAUSE_BLOCK_NO_FEATURE_GATE_REQUIRED_IN_R48` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DECL_CLAUSE_BLOCK_REQUIRES_EQUALS_ATTACHMENT` | `checker` | `error` | `active` | Function clause block must be attached with \`= {{ ... }}\`. |
| `DECL_CLAUSE_DISJOINTNESS_UNPROVEN` | `checker` | `error` | `active` | The compiler cannot prove that these declarative clauses are mutually exclusive. |
| `DECL_CLAUSE_GUARD_NOT_GUARD_SAFE` | `checker` | `error` | `active` | Clause guard must be R0 guard-safe: sync, deterministic, throws Never, effects {}, and non-suspending. |
| `DECL_CLAUSE_NONEXHAUSTIVE` | `checker` | `error` | `active` | Clause block does not cover all inputs. Ordinary clause blocks are exhaustive by default. |
| `DECL_CLAUSE_NONEXHAUSTIVE_REQUIRES_PARTIAL_POLICY` | `checker` | `error` | `active` | Non-exhaustive clause block requires explicit partial policy and visible failure channel. |
| `DECL_CLAUSE_OVERLAP` | `checker` | `error` | `active` | Declarative clauses overlap; source order is not a semantic tiebreaker. |
| `DECL_CLAUSE_RESULT_TYPE_MISMATCH` | `checker` | `error` | `active` | Clause result is not assignable to the function return type. |
| `DECL_PARAM_GUARD_SHORTHAND_NOT_CURRENT` | `checker` | `error` | `active` | Parameter guard shorthand such as \`n: Nat == 0\` is not current Deeplus source. |
| `DECL_SEPARATE_FUNCTION_CLAUSE_NOT_CURRENT` | `design_static` | `warning` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL` | `parser` | `error` | `active` | A defer block is not current; register exactly one cleanup invocation. |
| `DEFER_CLEANUP_RESERVED_PLACE_MOVED` | `checker` | `error` | `active` | A place reserved by defer cannot be moved or rebound before scope exit. |
| `DEFER_EFFECT_EXCEEDS_FUNCTION_BUDGET` | `checker` | `error` | `seed` | defer cleanup effects exceed the enclosing function cleanup/effect budget. |
| `DEFER_REQUIRES_SINGLE_INVOCATION` | `parser` | `error` | `active` | Defer requires exactly one direct, message, or type-side invocation. |
| `DEFER_THROW_NOT_ACCOUNTED` | `checker` | `error` | `seed` | defer cleanup may throw but the enclosing signature or cleanup budget does not account for it. |
| `DEF_HASH_DROP_REMOVED_USE_CLEANUP` | `parser` | `error` | `active` | def#drop is not current; lifecycle declarations use def#cleanup(). |
| `DELEGATING_CONSTRUCTOR_CANNOT_INITIALIZE_STORED_FIELD` | `checker` | `error` | `active` | A same-type delegating constructor body is post-init; it cannot initialize stored fields. |
| `DERIVATION_ENTRY_SEPARATOR_REQUIRED` | `checker` | `error` | `active` | Same-line derivation delta entries require comma; multi-line entries may use LayoutEntrySep when unambiguous. |
| `DESIGN_GALLERY_METADATA_REQUIRED` | `checker` | `warning` | `seed` | Design Gallery entry is missing machine-readable metadata. |
| `DETERMINISTIC_PRIMARY_SUPPRESSED_ORDER_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DETERMINISTIC_PRIMARY_SUPPRESSED_ORDER_VIOLATION` | `checker` | `error` | `active` | Failure selection or cleanup suppression order differs from the required source-order/reverse-cleanup algorithm. |
| `DETERMINISTIC_SUPPRESSED_ORDER_REQUIRED` | `checker` | `error` | `active` | Primary/suppressed failure ordering must be deterministic for cleanup, resource, and task aggregation profiles. |
| `DIAGNOSTIC_ALIAS_PROJECTION_DRIFT` | `design_static` | `error` | `seed` | Diagnostic alias projection differs across artifacts. |
| `DIAGNOSTIC_ID_CANONICAL_UPPER_SNAKE_CASE` | `checker` | `error` | `seed` | Diagnostic IDs must use canonical UPPER_SNAKE_CASE. |
| `DIAGNOSTIC_VALUE_NOT_ADMISSIBLE` | `checker` | `error` | `active` | Diagnostic payload values must be Plain snapshots without owner, resource, authority, borrow, or cleanup responsibility. |
| `DIAGNOSTIC_VALUE_REJECTS_AUTHORITY` | `checker` | `error` | `active` | Error/Defect payload cannot carry lifecycle/resource/raw/meta authority. |
| `DIAGNOSTIC_VALUE_REJECTS_RESOURCE` | `checker` | `error` | `active` | Error/Defect diagnostic payload cannot carry Resource owner. |
| `DIMENSION_MISMATCH` | `checker` | `error` | `active` | Measure operands have incompatible dimensions. |
| `DIRECTED_COROUTINE_GROUP_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | Feature \`directed_coroutine_group\` is PREVIEW_DESIGN/nonactivatable and has no current source gate. |
| `DOCUMENTATION_ONLY_FEATURE_NOT_SOURCE` | `checker` | `error` | `seed` | documentation feature is not ordinary source syntax in R49. |
| `DOC_BLOCK_COMMENT_UNTERMINATED` | `lexer` | `error` | `active` | Documentation block comment opened by \`//!!\` was not closed by \`!!//\`. |
| `DOC_COMMENT_NOT_ATTACHED_TO_DECL` | `lexer` | `error` | `active` | Documentation comment is not attached to a documentable declaration. |
| `DOLLAR_CLASS_SIDE_SEPARATOR_REMOVED_USE_COLON_COLON` | `checker` | `error` | `active` | Type-side structured declaration uses Type::selector; Type$$selector is removed. |
| `DOLLAR_CONSTRUCTION_LHS_MUST_BE_TYPE` | `checker` | `error` | `active` | A left-hand side before ${...} is valid only when it resolves as a TypeRef. |
| `DOLLAR_DECLARATION_SIGIL_REMOVED_USE_LET_VAR` | `checker` | `error` | `active` | Dollar field/member promotion sigils are removed; use let or var. |
| `DOLLAR_INSTANCE_SIDE_SEPARATOR_REMOVED_USE_TILDE` | `checker` | `error` | `active` | Instance-side structured declaration uses Type~selector; Type$selector is removed. |
| `DOTTED_STATIC_PATH_NOT_CURRENT` | `parser` | `error` | `active` | The surface \`dotted static path\` is recognized but is not current Deeplus. |
| `DOT_ENUM_CASE_PATTERN_NOT_CURRENT` | `checker` | `error` | `active` | Dot-prefixed enum case patterns are not current Deeplus source. Use \`::case\` or \`EnumType::case\`. |
| `DOT_ENUM_CASE_SHORTHAND_NOT_CURRENT` | `checker` | `error` | `active` | Dot-prefixed enum case shorthand is not current Deeplus. Use \`::case\` with expected enum type or \`EnumType::case\`. |
| `DOT_NOT_ALLOWED_FOR_TYPE_SIDE_SELECTOR` | `checker` | `error` | `active` | Type-side selectors and calls use \`::\`, not \`.\`. Write \`Type::member\` or \`Type::member(...)\`. |
| `DOT_NOT_ALLOWED_IN_IMPORT_PATH` | `checker` | `error` | `active` | Static import paths use \`::\`; dotted import paths are not current source. |
| `DOT_NOT_ALLOWED_IN_MODULE_PATH` | `checker` | `error` | `active` | Static module paths use \`::\`; \`.\` is runtime member access. |
| `DOT_NOT_ALLOWED_IN_QUALIFIED_EXTENSION_SELECTOR` | `checker` | `error` | `active` | Qualified extension selectors use \`::\`, not \`.\`. Write \`Int::metric::m\`. |
| `DOT_NOT_ALLOWED_IN_USE_PATH` | `checker` | `error` | `active` | Static use paths use \`::\`; dotted use paths are not current source. |
| `DOT_PRODUCT_IS_NON_ASSOCIATIVE` | `checker` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DOT_PRODUCT_REQUIRES_RANK1_VECTORS` | `checker` | `error` | `active` | \`*+\` dot product requires rank-1 vector operands with equal static or proven length. |
| `DROP_SPELLING_REMOVED_USE_DEF_HASH_DROP` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DROP_VISIBILITY_SIGIL_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DUPLICABLE_REMOVED_USE_EXPLICIT_RESPONSIBILITY` | `checker` | `error` | `active` | Duplicable is not current-canonical public vocabulary. Choose Plain, Shared<T>, explicit clone/derivation, or explicit move. |
| `DUPLICATE_NORMALIZED_SIGNATURE` | `checker` | `error` | `active` | Two declarations normalize to the same semantic signature. |
| `DYNAMIC_CONVERSION_REQUIRES_PROVIDER` | `checker` | `error` | `active` | Dynamic unit conversion requires an explicit provider. |
| `DYNAMIC_EXTENSION_DISPATCH_FORBIDDEN` | `checker` | `error` | `active` | Extension lookup uses receiver static type, not runtime receiver identity. |
| `DYNAMIC_TRAIT_ATTACH_NOT_CURRENT` | `checker` | `error` | `active` | Dynamic trait attach/detach has no activatable source syntax in the current profile. |
| `DYNAMIC_UNIT_CONVERSION_POLICY_REQUIRED` | `checker` | `error` | `active` | Dynamic unit conversion requires explicit observation, rounding, failure, effect, cache and replay policies. |
| `DYNAMIC_UNIT_CONVERSION_PROFILE_NOT_ACTIVE` | `checker` | `error` | `active` | Dynamic unit conversion requires an active stdlib/provider conversion profile. |
| `DYNAMIC_UNIT_CONVERSION_PROVIDER_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `DYNAMIC_UNIT_CONVERSION_PROVIDER_REQUIRED` | `checker` | `error` | `active` | Dynamic unit conversion requires an explicit provider identity and version. |
| `DYN_INSPECTION_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | Feature \`dyn_inspection\` is PREVIEW_DESIGN/nonactivatable and has no current source gate. |
| `DYN_RCTS_SOURCE_NOT_CURRENT` | `checker` | `error` | `active` | Dynamic RCTS source activation is not current; the design family is nonactivatable. |
| `EFFECTFUL_OTHERWISE_RIGHT_OPERAND` | `checker` | `error` | `active` | Right operand of \`otherwise\` has effects and is conditionally evaluated; make that responsibility explicit. |
| `EFFECTROW_DOES_NOT_INCLUDE_SUSPENSION` | `checker` | `note` | `seed` | EffectRow does not include suspension/cancellation/isolation. Use async/await and control/isolation annotations instead. |
| `EFFECTROW_UNSAFE_AXIS_FORBIDDEN` | `checker` | `error` | `active` | \`unsafe\` is a safety/authority axis, not an EffectRow atom; use an explicit unsafe boundary. |
| `EFFECT_ROW_UNION_TOKEN_REQUIRED` | `lexer` | `error` | `active` | Effect-row alternatives require the visible \| token. |
| `EFFECT_ROW_VARIABLE_UNBOUND` | `checker` | `error` | `active` | Effect row variable is not bound in the generic/effect environment. |
| `ELLIPSIS_CONTEXT_DISAMBIGUATION_REQUIRED` | `checker` | `error` | `seed` | The \`...\` token is not a generic spread placeholder. In R49 it remains valid only for its explicitly admitted contexts such as range tail or gated comprehension unfold; map unfold uses \`**expr\`. |
| `EMPTY_NULLARY_LAMBDA_REQUIRES_EXPECTED_FUNCTION_TYPE` | `checker` | `error` | `active` | Empty \`{}\` can mean \`() -> Unit\` only with an expected function type. |
| `ENTRY_DECL_DUPLICATE` | `checker` | `error` | `active` | An executable target has more than one explicit entry declaration. |
| `ENTRY_NOT_ALLOWED_IN_LIBRARY_SOURCE` | `parser` | `error` | `active` | A library source file cannot contain an entry declaration, including through an annotation attachment. |
| `ENTRY_SIGNATURE_NOT_ADMITTED` | `checker` | `error` | `active` | An entry function must have () or (Sequence<String>) parameters and return Unit or ExitCode. |
| `ENUM_CASE_COMMA_REQUIRES_SINGLE_LINE` | `parser` | `error` | `active` | Comma-separated enum cases must form one physical-line case-only list. |
| `ENUM_CASE_CONFLICTS_WITH_TYPE_SIDE_MEMBER` | `checker` | `error` | `active` | Enum case names share the enum type static case namespace and cannot conflict with type-side members. |
| `ENUM_CASE_EXPRESSION_PAYLOAD_MUST_NOT_USE_DECLARATION_PAYLOAD` | `checker` | `error` | `active` | Enum case expression payload uses expression arguments, not enum case declaration field syntax. |
| `ENUM_CASE_KEYWORD_NOT_CANONICAL` | `parser` | `error` | `active` | Enum cases are declared directly inside enum bodies; remove the \`case\` keyword. |
| `ENUM_CASE_PATTERN_PAYLOAD_MUST_NOT_USE_DECLARATION_PAYLOAD` | `checker` | `error` | `active` | Enum case pattern payload uses pattern payload syntax, not enum case declaration field syntax. |
| `ENUM_CASE_PATTERN_USES_COLON_COLON` | `checker` | `error` | `active` | Enum case patterns use \`::case\` or \`EnumType::case\`, not \`.case\`. |
| `ENUM_CASE_SEPARATOR_MIXED` | `parser` | `error` | `active` | An enum body may not mix comma-list and layout separators for cases. |
| `ENUM_MEMBER_KIND_NOT_ADMITTED` | `parser` | `error` | `active` | An enum body may contain cases followed by methods, accessors, and type-side members; stored fields, constructors, and lifecycle cleanup declarations are not admitted. |
| `ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH` | `checker` | `error` | `retired` | The Enum pattern case must belong to the subject Enum and its active payload arity, labels, positions, and child types must match exactly. |
| `ERRORVALUE_REQUIRED_FOR_ERRORSET_PAYLOAD` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `ERROR_ROW_PRIVATE_TYPE_LEAK` | `checker` | `error` | `seed` | Error row inference leaks a private error type into a public signature. |
| `ERROR_SET_UNION_TOKEN_REQUIRED` | `lexer` | `error` | `active` | Error-set alternatives require the visible \| token. |
| `ESCAPED_MEMBER_ADJACENCY_REQUIRED` | `parser` | `error` | `active` | A member escape must be written as attached .\\\\name with no intervening trivia. |
| `ESCAPED_MEMBER_CONTEXT_ONLY` | `checker` | `error` | `active` | Backslash identifier escape is permitted only in a member-access suffix. |
| `EVIDENCE_ARTIFACT_NOT_SOURCE` | `checker` | `error` | `seed` | evidence feature is not ordinary source syntax in R49. |
| `EVIDENCE_SELECTOR_NOT_A_VALUE` | `checker` | `error` | `active` | A conformance evidence selector is not an ordinary value and cannot be stored, returned, captured, or runtime-selected. |
| `EXAMPLE_BLOCK_EXPECTED_OUTCOME_REQUIRED` | `design_static` | `error` | `active` | EXAMPLE_BLOCK_EXPECTED_OUTCOME_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `EXAMPLE_BLOCK_FENCE_COUNT_MISMATCH` | `checker` | `error` | `seed` | Example block manifest does not match the Deeplus code fences in the Example Review Corpus. |
| `EXAMPLE_BLOCK_HASH_MUST_MATCH_MARKDOWN` | `design_static` | `error` | `active` | EXAMPLE_BLOCK_HASH_MUST_MATCH_MARKDOWN: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `EXAMPLE_BLOCK_MANIFEST_REQUIRED` | `design_static` | `error` | `active` | EXAMPLE_BLOCK_MANIFEST_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `EXAMPLE_BUCKET_UNKNOWN` | `design_static` | `error` | `active` | EXAMPLE_BUCKET_UNKNOWN: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `EXAMPLE_CODE_BLOCK_NOT_CERTIFIED` | `design_static` | `note` | `active` | Example code blocks are design review corpus items until production parser/checker receipt is attached. |
| `EXAMPLE_EFFECTIVE_STATUS_FEATURE_GATE_DRIFT` | `checker` | `error` | `seed` | Example metadata must disclose preview or nonactivatable features in feature_activation_set/effective_status. |
| `EXAMPLE_FEATURE_STATUS_MISMATCH` | `checker` | `warning` | `seed` | Example bucket/source_activation is weaker than one of its referenced feature gates. |
| `EXAMPLE_FEATURE_TAG_MISSING_FOR_SURFACE` | `checker` | `warning` | `seed` | Example metadata appears to omit a feature required by its code surface. |
| `EXAMPLE_ID_DUPLICATE_FORBIDDEN_R48` | `design_static` | `error` | `active` | Example ids must be globally unique in the current profile managed review corpus. |
| `EXAMPLE_MANIFEST_BLOCK_MANIFEST_PARITY` | `design_static` | `error` | `active` | EXAMPLE_MANIFEST_BLOCK_MANIFEST_PARITY: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `EXAMPLE_MANIFEST_METADATA_MISMATCH` | `design_static` | `error` | `active` | EXAMPLE_MANIFEST_METADATA_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `EXAMPLE_PREVIEW_GATE_REQUIRED` | `checker` | `warning` | `seed` | Preview or Preview-design example must declare source_activation/effective_status. |
| `EXAMPLE_SOURCE_FEATURE_TAG_MISSING` | `design_static` | `error` | `active` | Example or gallery source uses a feature surface that is missing from its manifest feature tags. |
| `EXISTENTIAL_ASSOC_TYPE_UNBOUND` | `checker` | `error` | `active` | Existential trait leaves an associated requirement unbound for an operation that needs it. |
| `EXPECTED_ENUM_TYPE_REQUIRED_FOR_CASE_PATTERN_SHORTHAND` | `checker` | `error` | `active` | Leading \`::case\` pattern requires an expected enum subject type; use \`EnumType::case\` if the owner is not known. |
| `EXPECTED_ENUM_TYPE_REQUIRED_FOR_CASE_SHORTHAND` | `checker` | `error` | `active` | Leading \`::case\` requires an expected enum type. Use \`EnumType::case\` or add a type annotation. |
| `EXPECTED_IDENTIFIER_FOUND_WILDCARD` | `parser` | `error` | `active` | A lone underscore is WildcardToken and cannot name a declaration or member; use an underscore-prefixed Identifier such as \`_name\` when an identity is required. |
| `EXPLICIT_BROADCAST_MARKER_NOT_CURRENT` | `checker` | `error` | `active` | \`operand op &adapted\` is not current Deeplus source in the current profile; \`&\` marks the context-providing anchor. Use a named API or \`&anchor op operand\` when the NumericArray context-anchor law applies. |
| `EXPLICIT_WITNESS_ARGUMENT_NOT_ADMITTED` | `checker` | `error` | `active` | The using argument must be a forwarded explicit witness Identifier or a unique coherent conformance(Type conforms Trait) selector; every ordinary/computed value is forbidden. |
| `EXPLICIT_WITNESS_ARGUMENT_REQUIRES_IDENTIFIER` | `parser` | `error` | `active` | After using, write either an explicit witness Identifier or conformance(Type conforms Trait); calls, literals, and member chains are not evidence arguments. |
| `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | Explicit witness parameters cannot escape, be stored, returned, or captured by escaping closures. |
| `EXPLICIT_WITNESS_PARAMETER_REQUIRED` | `checker` | `error` | `active` | A declaration requiring an explicit witness parameter must receive a matching explicit witness argument. |
| `EXPR_DOLLAR_DERIVATION_NOT_CURRENT` | `checker` | `error` | `active` | \`expr${...}\` is not current Deeplus source; use \`expr!{...}\` or \`expr!!{...}\` for same-type derivation. |
| `EXTENSION_AUTO_WITNESS_FORBIDDEN` | `parser` | `error` | `active` | Extension methods do not create trait witnesses. |
| `EXTENSION_CANNOT_FULFILL_TRAIT_REQUIREMENT` | `checker` | `error` | `active` | Active extension selectors do not automatically form trait witnesses. |
| `EXTENSION_CONFORMANCE_LOOKUP_DOMAIN_MIXED` | `checker` | `error` | `active` | The same call spelling cannot change between extension and witness lookup because a conformance is present. |
| `EXTENSION_IMPORTED_BUT_NOT_ACTIVE` | `checker` | `error` | `active` | \`import\` does not activate extension selector lookup; use an extension activation. |
| `EXTENSION_IMPORT_DOES_NOT_ACTIVATE_USE_REQUIRED` | `checker` | `error` | `active` | \`import\` does not activate extension lookup; use extension activation. |
| `EXTENSION_NOT_ACTIVE` | `checker` | `error` | `active` | Import does not activate extension lookup; use \`use\`. |
| `EXTENSION_RESOLUTION_ORDER_NOT_TIEBREAKER` | `checker` | `error` | `active` | Import, use, declaration, and source order are not extension-overload tie-breakers; qualify the selector or remove the ambiguity. |
| `EXTENSION_SELECTOR_NOT_ORDINARY_NAME` | `checker` | `error` | `active` | An active extension selector is not introduced as an ordinary function name. |
| `EXTENSION_SET_BLOCK_STABLE_BUT_PRODUCT_NOT_RUN` | `checker` | `info` | `active` | Named extension set blocks are Stable design in the current profile, but production parser/checker support remains NOT_RUN. |
| `EXTENSION_SET_DOES_NOT_MODIFY_TARGET_TYPE` | `checker` | `error` | `active` | An extension set groups extension selectors; it does not add stored members or ordinary dot members to the target type. |
| `EXTENSION_SET_GENERIC_TARGET_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `EXTENSION_SET_MEMBER_ID_REQUIRES_EXTENSION_SET_ID` | `checker` | `error` | `active` | Named extension set members must include origin, target type, extension set name, and selector in their semantic identity. |
| `EXTENSION_SET_MEMBER_ID_REQUIRES_SET_ID` | `checker` | `error` | `active` | Named extension set member semantic ID must include extension set identity. |
| `EXTENSION_SET_MEMBER_TILDE_DECLARATION_REMOVED` | `checker` | `error` | `active` | Declare a body member selector with plain \`def name\`; tilde belongs to receiver calls, not immediately before the declared selector. |
| `EXTENSION_SET_OPERATOR_MEMBER_UNSUPPORTED_IN_MSP` | `checker` | `error` | `active` | Operator members are not part of named extension set MSP. |
| `EXTENSION_SET_PATH_AMBIGUOUS` | `checker` | `error` | `active` | Extension set activation path is ambiguous; qualify the origin. |
| `EXTENSION_SET_PRIVATE_TARGET_ACCESS_FORBIDDEN` | `checker` | `error` | `active` | Extension set member cannot access target private representation outside visibility law. |
| `EXTENSION_SET_RECEIVER_MODE_UNSUPPORTED_IN_MSP` | `checker` | `error` | `active` | Named extension set MSP supports borrow receiver only. |
| `EXTENSION_SET_STORED_MEMBER_FORBIDDEN` | `parser` | `error` | `active` | An extension set may declare behavior but cannot own a stored field, initializer, layout, or cleanup responsibility. |
| `EXTENSION_SHADOWED_BY_MEMBER_COMPAT` | `checker` | `error` | `active` | the current profile compatibility profile selected the member slot while an active extension is shadowed; strict profile will require explicit selection. |
| `EXTENSION_USE_REEXPORT_STABLE_BUT_PRODUCT_NOT_RUN` | `checker` | `warning` | `active` | \`use export\` is stable design in the current profile; product parser/checker support remains NOT_RUN. |
| `FACET_BORROW_CROSSES_SUSPENSION` | `checker` | `error` | `active` | A Phase-A borrowed Facet cannot cross suspension, task, or actor boundaries. |
| `FACET_BORROW_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | A borrowed Facet cannot outlive its payload borrow region or cross an isolation boundary. |
| `FACET_BORROW_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FACET_CONCRETE_TYPE_SPELLING_FORBIDDEN` | `checker` | `error` | `active` | Facet<T as Trait> leaks the payload type; use Facet<borrow any Trait>. |
| `FACET_DROP_PLAN_NOT_PRESERVED` | `checker` | `error` | `active` | Owned Facet packaging must preserve the concrete payload drop plan exactly. |
| `FACET_MOVE_REQUIRES_OWNER` | `checker` | `error` | `active` | A move Facet requires one unique payload owner. |
| `FACET_TYPE_REQUIRES_EXPLICIT_MODE` | `checker` | `error` | `active` | Facet source types require an explicit borrow, inout, or move mode. |
| `FAILURE_CHANNEL_DUPLICATE` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FEATURE_AUTHORITY_ENUM_UNKNOWN` | `design_static` | `error` | `active` | Feature authority_set entry must be declared in declared_authority_enums. |
| `FEATURE_DEPENDENCY_CYCLE` | `design_static` | `error` | `active` | Feature registry dependency graph must be acyclic. |
| `FEATURE_GATE_MAP_MISSING_GATE_INFO` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FEATURE_GRAMMAR_CROSSWALK_MISSING` | `design_static` | `error` | `active` | FEATURE_GRAMMAR_CROSSWALK_MISSING: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE` | `checker` | `error` | `active` | This design-only or nonactivatable feature cannot be enabled in the current profile. |
| `FEATURE_NOT_SOURCE` | `checker` | `error` | `active` | This feature is not an ordinary source feature in the current profile. |
| `FEATURE_REQUIRES_PREVIEW_GATE` | `checker` | `error` | `active` | This Preview feature requires an explicit feature gate. |
| `FFI_C_EXTERN_REQUIRES_PREVIEW_GATE` | `checker` | `error` | `active` | C extern unsafe declarations require #preview(ffi_c_extern_unsafe_surface_msp). |
| `FFI_C_EXTERN_UNSAFE_REQUIRES_PREVIEW_GATE` | `checker` | `error` | `active` | C extern unsafe surface requires #preview(ffi_c_extern_unsafe_surface_msp). |
| `FFI_C_EXTERN_UNSAFE_SURFACE_MSP_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | The extern#C unsafe declaration surface requires its dedicated Preview syntax gate. |
| `FFI_LAYOUT_RECEIPT_REQUIRED` | `checker` | `error` | `seed` | FFI declaration requires ABI/layout/provenance receipt before activation. |
| `FFI_MINIMUM_SOUND_PROFILE_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | The FFI minimum-sound semantic profile requires its dedicated Preview profile gate. |
| `FFI_MSP_REQUIRES_PREVIEW_GATE` | `checker` | `error` | `active` | Safe FFI MSP requires preview gate. |
| `FFI_SIGNATURE_UNREPRESENTABLE` | `checker` | `error` | `active` | This type is not representable in the selected FFI profile. |
| `FIELD_DISPATCH_MARKER_FORBIDDEN` | `parser` | `error` | `active` | Stored fields are nonvirtual and cannot carry a dispatch marker. |
| `FILL_FACTORY_REQUIRED_FOR_AFFINE_ELEMENT` | `checker` | `error` | `seed` | Fill factory required for affine element |
| `FILL_INITIALIZER_REQUIRES_SHAPED_TARGET` | `checker` | `error` | `seed` | Fill initializer requires shaped target |
| `FILL_REPEAT_ADMISSIBILITY_FAILED` | `checker` | `error` | `active` | The fill/repeat expression is not admissible for this shaped target and element responsibility. |
| `FILL_VALUE_REUSE_NOT_ADMISSIBLE` | `checker` | `error` | `seed` | Fill value reuse not admissible |
| `FIRST_CLASS_WITNESS_NOT_STABLE` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT` | `checker` | `note` | `retired` | Retired pre-promotion boundary: use the exact Stable fixed-operator conformance diagnostic. |
| `FLAGS_OPERATION_REQUIRES_SAME_NOMINAL_TYPE` | `checker` | `error` | `active` | Flags operands must have the same nominal bitfield#flags type. |
| `FLAGS_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLAGS_RESULT_IS_NOT_BOOL` | `checker` | `error` | `active` | A flags bitwise result is a flags value, not Bool. |
| `FLAGS_SHIFT_OPERATOR_FORBIDDEN` | `checker` | `error` | `active` | Shift operations are forbidden on semantic flags values. |
| `FLOAT_IS_NOT_KEYABLE_WITHOUT_CANONICAL_KEY_WRAPPER` | `checker` | `note` | `seed` | Floating values are not Keyable by default. Use a canonical key wrapper with explicit NaN/equality/hash law. |
| `FLOW_BINDING_ARROW_LET_REMOVED` | `checker` | `error` | `active` | Rightward flow binding uses \`expr -> $name\` for a fresh immutable local or \`expr -> $$name\` for a fresh mutable local; \`-> let\` and \`-> var\` are not current source. |
| `FLOW_BINDING_CANNOT_CHAIN` | `checker` | `error` | `active` | Rightward flow binding cannot be chained. |
| `FLOW_BINDING_DOLLAR_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_DOLLAR_TARGET_CANNOT_HAVE_TYPE_ANNOTATION` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_DOLLAR_TARGET_REMOVED_USE_LET_VAR` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_IS_STATEMENT_ONLY` | `checker` | `error` | `active` | Rightward flow binding is a statement, not an expression. |
| `FLOW_BINDING_NAME_ALREADY_BOUND` | `checker` | `error` | `active` | A rightward \`$name\` or \`$$name\` target must be fresh in the current function/block-local Block; immutable and mutable flow bindings never assign to or shadow an existing local in that Block. |
| `FLOW_BINDING_NOT_CHAINABLE` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_ONLY_ALLOWED_IN_LOCAL_BLOCK` | `checker` | `error` | `active` | Rightward flow binding is admitted only as a statement in a function/block-local Block; it is forbidden at source, type, or member scope and in expression position. |
| `FLOW_BINDING_REQUIRES_NEW_LOCAL` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_TARGET_MUST_BE_DOLLAR_LOCAL` | `checker` | `error` | `active` | A rightward flow target must be exactly \`$Identifier\` or \`$$Identifier\`, optionally followed by a type annotation. |
| `FLOW_BINDING_TARGET_MUST_BE_NEW_LOCAL` | `parser` | `error` | `active` | A rightward flow binding target must be a fresh statement-local $name[: Type] or $$name[: Type], not a place/member/index/pattern. |
| `FLOW_BINDING_TARGET_NOT_LOCAL` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_TARGET_REQUIRES_LET_OR_VAR` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FLOW_BINDING_TYPE_ANNOTATION_MISMATCH` | `checker` | `error` | `active` | The flow-binding value is not assignable to the optional target type annotation; no local binding is committed. |
| `FORWARD_GROUP_COLLISION` | `checker` | `error` | `active` | A forwarded member collides with an existing or previously forwarded member. |
| `FORWARD_GROUP_DUPLICATE_MEMBER` | `checker` | `error` | `active` | A grouped forwarding list names the same member more than once. |
| `FORWARD_GROUP_WILDCARD_NOT_CURRENT` | `parser` | `error` | `active` | Grouped forwarding requires an explicit finite member list; wildcard forwarding is not current. |
| `FOR_GUARD_PATTERN_BINDING_NOT_AVAILABLE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus; a \`for let\` GuardClause may read its noncommitted probe binders. |
| `FOR_LET_FILTER_GUARD_NOT_BOOL` | `checker` | `error` | `active` | The optional \`for let\` GuardClause must have type Bool. |
| `FOR_SOURCE_NOT_ITERABLE` | `checker` | `error` | `seed` | for-source expression does not satisfy the Iterator/Iterable protocol profile. |
| `FULL_ENUM_CASE_USES_COLON_COLON` | `checker` | `error` | `active` | Fully qualified enum cases use \`::\`. Expected-type shorthand also uses leading \`::case\`; dot-prefixed \`.case\` is not current Deeplus. |
| `FUNCTION_BODY_REQUIRES_BLOCK_RETURN_OR_CLAUSE` | `parser` | `error` | `active` | A named function body must be a block, explicit \`= return Expr\` shorthand, or declarative clause body; bare \`= Expr\` is not current. |
| `FUNCTION_EXPRESSION_BODY_FORBIDDEN_IN_STABLE` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN` | `parser` | `error` | `active` | One-line named function body must use = return expr, not = expr. |
| `FUNCTION_SIGNATURE_MUST_PRESERVE_CONTROL_AXES` | `checker` | `note` | `active` | Function signatures must preserve throws/effects/suspension/call-domain axes; do not erase them into a bare callable façade. |
| `FUNCTION_STATIC_ACTIVATION_CALLABLE_KIND_NOT_ADMITTED` | `checker` | `error` | `active` | This callable kind cannot own function static activation. |
| `FUNCTION_STATIC_ACTIVATION_CAPTURE_FORBIDDEN` | `checker` | `error` | `active` | Function static activation cannot observe receiver, parameters, defaults, Context, or caller execution identity. |
| `FUNCTION_STATIC_ACTIVATION_DEPENDENCY_FORBIDDEN` | `checker` | `error` | `active` | The initial Stable profile forbids a function static activation from calling another activation-bearing owner. |
| `FUNCTION_STATIC_ACTIVATION_DUPLICATE` | `parser` | `error` | `active` | A callable body may contain at most one scope#static activation prologue. |
| `FUNCTION_STATIC_ACTIVATION_DYNAMIC_CALL_FORBIDDEN` | `checker` | `error` | `active` | Function static activation may call only statically selected activation-safe helpers. |
| `FUNCTION_STATIC_ACTIVATION_EFFECT_FORBIDDEN` | `checker` | `error` | `active` | Function static activation must be effect-free, authority-free, and nonthrowing. |
| `FUNCTION_STATIC_ACTIVATION_FAILED` | `runtime` | `error` | `active` | The function static activation failed; all callers observe the same cached failure identity and no implicit retry occurs. |
| `FUNCTION_STATIC_ACTIVATION_OWNER_REQUIRED` | `checker` | `error` | `active` | scope#static is admitted only in a supported synchronous named callable owner. |
| `FUNCTION_STATIC_ACTIVATION_POSITION_INVALID` | `parser` | `error` | `active` | scope#static must follow the optional block import/use prologue and precede the first runtime semantic item. |
| `FUNCTION_STATIC_ACTIVATION_REENTRANCY` | `runtime` | `error` | `active` | A function static activation re-entered its own owner; the activation transitions to one canonical failed state. |
| `FUNCTION_STATIC_ACTIVATION_RESOURCE_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | Function static activation cannot publish a Resource, mutable persistent state, or needsDrop residue. |
| `FUNCTION_STATIC_ACTIVATION_SUSPENSION_FORBIDDEN` | `checker` | `error` | `active` | Function static activation cannot await, yield, suspend, or observe cancellation. |
| `FUNCTION_STATIC_METADATA_MISMATCH` | `runtime` | `error` | `active` | Imported function static activation metadata does not match the selected implementation contract. |
| `FUNCTION_STATIC_OWNER_ID_COLLISION` | `runtime` | `error` | `active` | Distinct function static owner recipes produced the same identity. |
| `FUNCTION_TYPE_REQUIRES_THIN_ARROW` | `checker` | `error` | `active` | Function/result/signature arrows use ->. |
| `FUNCTION_TYPE_REST_RESIDUE_REQUIRED` | `checker` | `error` | `active` | Function types and public API digests must preserve \`T...\` and \`Record***\` call-shape residues; neither may be erased to \`Sequence<T>\` or \`Record\`. |
| `GALLERY_FRAGMENT_FEATURE_TAG_REQUIRED` | `design_static` | `error` | `active` | GALLERY_FRAGMENT_FEATURE_TAG_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `GALLERY_FRAGMENT_MANIFEST_REQUIRED` | `design_static` | `error` | `active` | GALLERY_FRAGMENT_MANIFEST_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `GALLERY_ID_DUPLICATE_FORBIDDEN_R48` | `design_static` | `error` | `active` | Gallery ids must be globally unique in the current profile design gallery manifest. |
| `GALLERY_MANIFEST_FRAGMENT_PARITY_REQUIRED` | `design_static` | `error` | `active` | GALLERY_MANIFEST_FRAGMENT_PARITY_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `GALLERY_TRACE_METADATA_REQUIRED` | `design_static` | `error` | `active` | GALLERY_TRACE_METADATA_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `GENERAL_REJECTED_SOURCE_DIAGNOSTIC` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `GENERATOR_BORROW_CAPTURE_FORBIDDEN` | `checker` | `error` | `active` | Escaping generator expression cannot capture a borrowed owner that would outlive its region. |
| `GENERATOR_CREATION_EFFECTS_VISIBLE` | `checker` | `error` | `active` | Generator creation effects must be visible at creation boundary. |
| `GENERATOR_EXPR_IS_SINGLE_PASS_NOT_COLLECTION` | `checker` | `error` | `active` | @for/@while/@repeat produces a single-pass generator value, not an eager collection. |
| `GENERATOR_INOUT_CAPTURE_FORBIDDEN` | `checker` | `error` | `active` | Escaping generator expression cannot capture inout state across iteration boundary. |
| `GENERATOR_REFUTABLE_BINDER_FORBIDDEN` | `checker` | `error` | `active` | Generator binder must be irrefutable in the Phase A profile. |
| `GENERIC_CONSTRAINT_UNSATISFIED` | `checker` | `error` | `active` | Generic where-clause conformance constraint is not satisfied. |
| `GENERIC_PARAMETER_DEFAULTS_TO_INVARIANT` | `checker` | `note` | `active` | A generic parameter without an explicit variance marker is invariant; trait parameters may use the admitted \`in\` or \`out\` marker when every use position is valid. |
| `GENERIC_PARAM_KIND_MISMATCH` | `checker` | `error` | `active` | Generic argument kind does not match the parameter kind. |
| `GENERIC_TYPE_CONSTRUCTOR_INVARIANT` | `checker` | `error` | `active` | This generic type constructor is invariant in the given type argument. |
| `GENERIC_TYPE_CONSTRUCTOR_INVARIANT_BY_DEFAULT` | `checker` | `error` | `active` | Generic type constructors are invariant by default in the current profile unless a narrow variance descriptor admits a safer role. |
| `GOVERNANCE_ARTIFACT_NOT_SOURCE` | `checker` | `error` | `seed` | governance feature is not ordinary source syntax in R49. |
| `GRAMMAR_ALTERNATIVE_ACTIVATION_METADATA_REQUIRED` | `parser` | `error` | `active` | A grammar alternative that routes to preview, preview-design, recognized-unsupported, or tooling-only syntax must carry explicit activation metadata. |
| `GRAMMAR_METADATA_FEATURE_REF_MISSING` | `design_static` | `error` | `active` | Grammar production metadata references a feature_id that is not present in the canonical feature registry. |
| `GRAMMAR_METADATA_SOURCE_ACTIVATION_MISMATCH` | `parser` | `error` | `seed` | Grammar production metadata source_activation does not match canonical feature row. |
| `GRAMMAR_NONACTIVATABLE_MARKED_ORDINARY` | `parser` | `error` | `seed` | Nonactivatable preview-design grammar production is marked ordinary_source=true. |
| `GRAMMAR_PRODUCTION_METADATA_GATE_MISMATCH` | `parser` | `error` | `seed` | Grammar production metadata ordinary_source/parser_mode/source_activation is inconsistent with the referenced feature status. |
| `GRAMMAR_PRODUCTION_REACHABILITY_UNCLASSIFIED` | `parser` | `error` | `seed` | Grammar production lacks reachability classification. |
| `GRAMMAR_PROJECTION_ROOT_NOT_CLOSED` | `design_static` | `error` | `seed` | Grammar projection root is not closed. |
| `GUARDED_LET_DESTRUCTURED_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `GUARDED_LET_EXIT_MUST_BE_UNCONDITIONAL` | `parser` | `error` | `active` | A guarded-let failure branch requires one direct unconditional terminating exit. |
| `GUARDED_LET_RESIDUAL_NOT_EXHAUSTIVE` | `checker` | `error` | `active` | The failure pattern is not irrefutable for the exact residual domain. |
| `GUARDED_RETURN_DOES_NOT_COMPLETE_ALL_PATHS` | `checker` | `error` | `active` | A guarded return does not complete all value paths; add an unconditional return or exhaustive control expression. |
| `GUARD_AND_RIGHTWARD_BINDING_CANNOT_COEXIST` | `checker` | `error` | `active` | Guard clause and rightward \`$\` binding cannot coexist in one statement. |
| `GUARD_CALLABLE_CONSUME_FORBIDDEN` | `checker` | `error` | `active` | A #guard callable cannot consume parameters or captures. |
| `GUARD_CALLABLE_RESULT_MUST_BE_BOOL` | `checker` | `error` | `active` | A #guard callable must return exactly Bool on every normal path. |
| `GUARD_CLAUSE_NOT_ALLOWED_HERE` | `checker` | `error` | `active` | Guard clauses are allowed only on approved control-transfer statements and loop headers. |
| `GUARD_CONDITION_CONTROL_TRANSFER_NOT_ALLOWED` | `checker` | `error` | `active` | Guard condition must not contain control transfer. |
| `GUARD_CONDITION_EFFECT_NOT_ALLOWED` | `checker` | `error` | `active` | Guard condition must have effects {}. |
| `GUARD_CONDITION_NOT_BOOL` | `checker` | `error` | `active` | Guard condition must have type Bool. |
| `GUARD_CONDITION_SUSPEND_NOT_ALLOWED` | `checker` | `error` | `active` | Guard condition must not suspend. |
| `GUARD_CONDITION_THROWS_NOT_ALLOWED` | `checker` | `error` | `active` | Guard condition must not throw. |
| `GUARD_EVALUATION_CONTRACT_VIOLATION` | `checker` | `error` | `active` | Guard evaluation must precede ownership commit and payload evaluation; a false guard leaves payload responsibilities unobserved. |
| `HARD_KEYWORD_MEMBER_REQUIRES_ESCAPE` | `lexer` | `error` | `active` | A hard keyword used as a data member name must use the member-only escape, for example obj.\\\\class. |
| `HASH_ROLE_PHYSICAL_LINE_BREAK_FORBIDDEN` | `parser` | `error` | `active` | A role marker may contain horizontal trivia but cannot cross a physical line break between \`#\` and its role word. |
| `HIR_POWER_OPERATION_UNRESOLVED` | `verifier` | `error` | `active` | Canonical HIR-H1 cannot contain an unresolved or generic power operation. |
| `HIR_POWER_RESULT_OR_ADAPTATION_MISMATCH` | `verifier` | `error` | `active` | The HIR-H1 power result or operand adaptation does not match the closed static-domain matrix. |
| `HISTORICAL_IMAGINARY_J_NOT_CURRENT` | `lexer` | `error` | `active` | The historical imaginary marker j is not current; use an attached i marker. |
| `IDENTITY_OPERATION_REQUIRES_IDENTITY_BEARING` | `checker` | `error` | `active` | The operation requires an identity-bearing descriptor. |
| `IF_EXPR_REQUIRES_ELSE` | `checker` | `error` | `active` | A value-producing \`@if\` requires an \`else\` branch; the optional grammar tail exists only so recovery can emit this diagnostic. |
| `IMAGINARY_LITERAL_FORM_NOT_ADMITTED` | `lexer` | `error` | `active` | An imaginary literal requires an attached decimal floating form such as 4.0i or 4.0f32i. |
| `IMAGINARY_LITERAL_MARKER_MUST_BE_ATTACHED` | `lexer` | `error` | `active` | The imaginary marker i must be attached to its decimal floating literal. |
| `IMPLICIT_AT_OUTSIDE_SINGLE_PARAMETER_CLOSURE` | `checker` | `error` | `active` | Implicit @ requires the nearest omitted-parameter closure to have one expected parameter. |
| `IMPLICIT_AT_WITH_EXPLICIT_PARAMETER` | `checker` | `error` | `active` | An explicit closure parameter cannot be mixed with the implicit @ parameter. |
| `IMPLICIT_LAMBDA_ARG_OUTSIDE_LAMBDA` | `checker` | `error` | `active` | Standalone \`@\` placeholder is allowed only inside implicit one-argument lambda bodies. |
| `IMPLICIT_LAMBDA_ARG_REQUIRES_ONE_PARAM_CONTEXT` | `checker` | `error` | `active` | Implicit \`@\` lambda requires an expected one-parameter function context. |
| `IMPLICIT_LAMBDA_ARG_WITH_EXPLICIT_PARAMS` | `checker` | `error` | `active` | Do not mix explicit lambda parameters with implicit \`@\` placeholder. |
| `IMPLICIT_LAMBDA_EXPECTED_CALLABLE_AMBIGUOUS` | `checker` | `error` | `active` | Implicit @ cannot be checked until overload shape selects exactly one expected callable. |
| `IMPLICIT_OWNER_TO_SHARED_FORBIDDEN` | `checker` | `error` | `active` | An owner cannot be implicitly promoted to Shared<T> or reused across a sharing boundary. |
| `IMPLICIT_PURE_FUNCTION_HAS_EFFECTS` | `checker` | `error` | `active` | Implicit pure-elision function has effects and cannot elide #pure. |
| `IMPLICIT_REUSE_REQUIRES_PLAIN_OR_SHARED_HANDLE` | `checker` | `error` | `active` | Value cannot be reused implicitly; use move, borrow, Plain, or Shared<T>. |
| `IMPLICIT_SUPER_NEW_NOT_AVAILABLE` | `checker` | `error` | `active` | Implicit \`: super!()\` is available only when the base no-argument \`new\` is accessible. |
| `INDEX_OPERATOR_MINIMUM_CORE_ONLY` | `checker` | `error` | `active` | the current profile index operator Stable law covers minimum indexing; effectful/custom index overloading is not enabled. |
| `INDEX_OUT_OF_LOGICAL_DOMAIN` | `checker` | `error` | `active` | The index is outside the receiver's declared logical domain. |
| `INDEX_SUFFIX_REQUIRES_AXIS` | `parser` | `error` | `active` | An index suffix requires a scalar index, a bounded slice range whose bounds may use ^ or $, or an admitted NumericArray * axis. |
| `INITIALIZED_LET_FIELD_CANNOT_BE_REASSIGNED_IN_POST_INIT_BODY` | `checker` | `error` | `active` | A post-init constructor body cannot reassign an already initialized \`let\` field. |
| `INLINE_CONFORMANCE_HEADER_NOT_CURRENT_USE_CONFORMANCE_DECL` | `parser` | `error` | `active` | Inline class/enum header conformance is not current; conformance is an explicit nominal declaration. |
| `INOUT_ALIAS_CONFLICT` | `checker` | `error` | `seed` | inout access conflicts with an existing alias or shared observation. |
| `INTERPOLATION_BOUNDARY_OUTSIDE_PATH` | `lexer` | `error` | `active` | A backtick is a no-output boundary only immediately after a shorthand interpolation path in interpolated-string mode. |
| `INTERPOLATION_COMPLEX_EXPRESSION_REQUIRES_BRACES` | `parser` | `error` | `active` | Complex interpolation expression requires ${...}. |
| `INTERPOLATION_FACTOR_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `INTERPOLATION_FORMAT_REQUIRES_BRACED_FORM` | `parser` | `error` | `active` | Interpolation format spec is admitted only in braced form ${expr:format}. |
| `INTERPOLATION_FORMAT_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `INTERPOLATION_INDEX_OUT_OF_DOMAIN` | `checker` | `error` | `active` | The interpolation selector index is outside the value's logical index domain. |
| `INTERPOLATION_MEMBER_NOT_FOUND` | `checker` | `error` | `active` | The selected interpolation member does not exist on the statically known value type. |
| `INTERPOLATION_PATH_REQUIRES_PREVIEW` | `lexer` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `INTERPOLATION_SECRET_REQUIRES_EXPLICIT_REDACTION` | `checker` | `error` | `active` | Secret/Redacted values require explicit redaction before interpolation. |
| `INTERPOLATION_SHORTHAND_DOT_STOPS_BEFORE_MEMBER` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `INTERPOLATION_SHORTHAND_EXPECTED_IDENTIFIER` | `checker` | `error` | `active` | String interpolation shorthand requires an identifier after $. |
| `INTERSECTION_BARE_CONTRACT_NOT_VALUE_TYPE` | `checker` | `error` | `active` | A bare Trait intersection is not a value carrier; use \`any (...)\` or a Facet. |
| `INTERSECTION_DISTRIBUTION_NOT_CURRENT` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `INTERSECTION_MULTIPLE_CONCRETE_BASES_FORBIDDEN` | `checker` | `error` | `active` | A contract intersection may contain at most one concrete nominal base. |
| `INTERSECTION_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `INTERSECTION_RESPONSIBILITY_CONFLICT` | `checker` | `error` | `active` | Intersection requirements impose incompatible ownership, effect, error, authority, or receiver responsibilities. |
| `INTERSECTION_WITNESS_AMBIGUOUS` | `checker` | `error` | `active` | The contract intersection does not resolve one coherent witness per Trait. |
| `INVALID_DIGIT_FOR_NUMERIC_RADIX` | `lexer` | `error` | `active` | A digit is not valid for this numeric radix. |
| `ITERABLE_REMOVED_CHOOSE_TRAVERSAL_ROLE` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `ITERABLE_REMOVED_USE_TRAVERSAL_PROFILE` | `checker` | `error` | `active` | Iterable catch-all vocabulary is removed; use Iterator, Sequence, View, Stream, or Collection. |
| `ITERATOR_CLEANUP_EFFECT_NOT_ACCOUNTED` | `checker` | `error` | `seed` | Iterator cleanup effects are not accounted for on loop exit. |
| `KEYABLE_REQUIRES_PLAIN_STABLE_HASH` | `checker` | `error` | `active` | Map/Set key must be Plain/stable-hash admissible or an explicitly approved key wrapper. |
| `LAMBDA_BLOCK_REQUIRES_RET` | `checker` | `error` | `active` | Block lambda requires explicit ret on value paths. |
| `LAMBDA_PARAM_LIST_PARENS_NOT_CURRENT` | `parser` | `error` | `active` | Lambda parameters are written directly before \`=>\`; write \`{ x: T => ... }\`. |
| `LAMBDA_REQUIRES_FAT_ARROW` | `checker` | `error` | `active` | Lambda and executable match-arm bodies use =>. |
| `LAW_BODY_ITEM_NOT_ADMITTED` | `checker` | `error` | `active` | Law bodies admit only pure predicate assertions. |
| `LAW_CHECK_AGENT_PROFILE_REQUIRES_FEATURE_GATE` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `LAYOUT_ARG_SEPARATOR_REQUIRES_ALL_NAMED_ARGUMENTS` | `checker` | `error` | `active` | Layout argument separator is only admitted in multiline all-named argument lists. |
| `LAYOUT_SEPARATOR_AMBIGUOUS_CONTINUATION` | `checker` | `error` | `active` | This newline cannot be used as a labeled aggregate entry separator because the expression may continue. |
| `LAYOUT_SEPARATOR_NOT_ALLOWED_HERE` | `checker` | `error` | `active` | A newline is not an element separator in this context. |
| `LAZY_BINDING_USE_HASH` | `parser` | `error` | `active` | The current lazy-binding spelling is \`let#lazy\`; \`let@lazy\` is recovery-only. |
| `LAZY_HIDDEN_FAILURE_CHANNEL_FORBIDDEN` | `checker` | `error` | `active` | A lazy binding cannot memoize a hidden failure channel; use an explicit Result value. |
| `LAZY_INITIALIZATION_CYCLE` | `checker` | `error` | `active` | A lazy binding cannot directly or indirectly force itself before its first commit. |
| `LAZY_LET_INITIALIZER_NOT_ADMITTED` | `checker` | `error` | `active` | The lazy initializer must be pure, synchronous, nonthrowing, authority-free, resource-free, and capture only reusable immutable values. |
| `LAZY_LET_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `LAZY_REENTRANT_FORCE` | `runtime` | `error` | `active` | Reentrant forcing of an initializing lazy binding is rejected deterministically. |
| `LAZY_SINGLE_COMMIT_VIOLATION` | `runtime` | `error` | `active` | Concurrent lazy forcing must publish exactly one immutable committed value. |
| `LEGACY_LOGICAL_AND_OPERATOR_REMOVED_ON_BOOL` | `checker` | `error` | `active` | \`&&\` on Bool is rejected because \`&&\` is bitwise in Deeplus. |
| `LEGACY_LOGICAL_OR_OPERATOR_REMOVED_ON_BOOL` | `checker` | `error` | `active` | \`\|\|\` on Bool is rejected because \`\|\|\` is bitwise in Deeplus. |
| `LEGACY_SHORT_CIRCUIT_AND_OPERATOR_REMOVED` | `checker` | `error` | `active` | \`&&\` is not logical AND in Deeplus; use \`and then\` for short-circuit or \`and\` for strict Boolean AND. |
| `LEGACY_SHORT_CIRCUIT_OR_OPERATOR_REMOVED` | `checker` | `error` | `active` | \`\|\|\` is not logical OR in Deeplus; use \`otherwise\` for short-circuit or \`or\` for strict Boolean OR. |
| `LET_PROPERTY_CANNOT_HAVE_SETTER` | `checker` | `error` | `active` | let property cannot have setter. |
| `LIBRARY_STATIC_BINDING_INITIALIZER_NOT_ADMITTED` | `checker` | `error` | `active` | A library top-level binding must be immutable, pure, synchronous, nonthrowing, effect/authority/resource/task/actor free, acyclic, and committed once. |
| `LIBRARY_TARGET_CONTAINS_TOP_LEVEL_SCRIPT` | `checker` | `error` | `active` | A library target cannot contain script computation; split declarations into a library or select an executable script target. |
| `LINALG_BACKEND_TRANSFER_REQUIRES_NAMED_API` | `checker` | `error` | `seed` | Linear algebra operators cannot hide backend transfer. |
| `LINALG_COMPLEX_DOT_CONJUGATES_LEFT` | `checker` | `info` | `seed` | Complex NumericArray *+ conjugates the left operand under the current law; dotu is explicitly unconjugated, A^ is transpose, and A ~ adjoint is conjugate transpose. |
| `LINALG_CONTRACT_REQUIRES_NAMED_AXES` | `checker` | `error` | `seed` | Tensor contraction must use named axes, not an operator. |
| `LINALG_CROSS_REQUIRES_VEC3` | `checker` | `error` | `seed` | cross requires two rank-1 vectors of length 3. |
| `LINALG_DOT_ELEMENT_TYPE_MISMATCH` | `checker` | `error` | `seed` | Dot product element types do not match. |
| `LINALG_DOT_LENGTH_MISMATCH` | `checker` | `error` | `seed` | Dot product vector lengths do not match. |
| `LINALG_DOT_REQUIRES_RANK1_VECTORS` | `checker` | `error` | `seed` | Dot product requires rank-1 vector operands. |
| `LINALG_DYNAMIC_SHAPE_OPERATOR_REQUIRES_CHECKED_API` | `checker` | `error` | `seed` | Dynamic-shape linear algebra must use a named checked API returning Result. |
| `LINALG_HADAMARD_SHAPE_MISMATCH` | `checker` | `error` | `seed` | hadamard requires same shape operands. |
| `LINALG_KRONECKER_REQUIRES_MATRICES` | `checker` | `error` | `seed` | kronecker requires matrix operands in this profile. |
| `LINALG_MATRIX_PRODUCT_DIMENSION_MISMATCH` | `checker` | `error` | `seed` | Matrix product dimensions do not match. |
| `LINALG_MATRIX_VECTOR_DIMENSION_MISMATCH` | `checker` | `error` | `seed` | Matrix-vector product dimensions do not match. |
| `LINALG_MIXED_MATMUL_DOT_CHAIN_REQUIRES_PARENS` | `parser` | `lint` | `seed` | Mixed * and *+ chains should use parentheses. |
| `LINALG_OPERATOR_REQUIRES_NUMERIC_ARRAY` | `checker` | `error` | `seed` | Linear algebra operator operands must be admitted NumericArray values in this profile. |
| `LINALG_OPERATOR_REQUIRES_NUMERIC_ELEMENT` | `checker` | `error` | `seed` | Linear algebra operator elements must satisfy NumericArrayElement and numeric operator law. |
| `LINALG_OPERATOR_REQUIRES_STATIC_SHAPE` | `checker` | `error` | `seed` | Linear algebra operators require statically known compatible shapes. |
| `LINALG_OPERATOR_WITNESS_AMBIGUOUS` | `checker` | `error` | `seed` | Linear algebra operator witness is ambiguous. |
| `LINALG_OUTER_REQUIRES_VECTORS` | `checker` | `error` | `seed` | outer requires vector operands. |
| `LINALG_STAR_PLUS_NO_FALLBACK_TO_MULTIPLY_UNARY_PLUS` | `checker` | `error` | `seed` | *+ is a single dot-product candidate token and does not fall back to multiplication by unary plus. |
| `LINALG_VECTOR_MATRIX_REQUIRES_EXPLICIT_ROW_VIEW` | `checker` | `error` | `seed` | A rank-1 vector has no hidden row orientation. |
| `LINALG_VECTOR_PRODUCT_AMBIGUOUS_USE_DOT_OR_METHOD` | `checker` | `error` | `seed` | Vector * vector is ambiguous. |
| `LINEAR_ALGEBRA_STAR_PRODUCT_SPLIT` | `checker` | `error` | `active` | \`*\` is elementwise NumericArray multiplication, not rank-dependent matrix/vector product. Use \`*+\`, \`**\`, or a named API. |
| `LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE` | `checker` | `error` | `active` | A List context may adapt an unsuffixed integer token or its direct prefix-minus candidate only when the mathematical candidate lies in the exact element domain. |
| `LIST_LITERAL_ELEMENT_JOIN_FAILED` | `checker` | `error` | `active` | Without an explicit expected element type, an ordinary List literal requires one normalized element type; automatic heterogeneous Union inference is not performed. |
| `LOCAL_IMPORT_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `LOCAL_IMPORT_RUNTIME_LOADING_FORBIDDEN` | `checker` | `error` | `active` | A block-local import is compile-time name visibility, never runtime module loading. |
| `LOCAL_USE_RUNTIME_AUTHORITY_FORBIDDEN` | `checker` | `error` | `active` | A local use directive cannot acquire runtime authority or create evidence. |
| `LOCAL_USE_TARGET_NOT_SCOPE_ADMISSIBLE` | `checker` | `error` | `active` | The local use target does not define an admissible lexical activation domain. |
| `LOCAL_VALUE_BODY_REQUIRES_PATH_TOTAL_RET` | `checker` | `error` | `active` | A multi-statement local value body must produce a value with local ret on every reachable normal path. |
| `LOCAL_WITNESS_NOT_CURRENT` | `checker` | `error` | `active` | Local witness remains Preview-design and is not current Stable source. |
| `LOGICAL_INDEX_DOMAIN_MISMATCH` | `checker` | `error` | `active` | The receiver has no admitted built-in bracket domain, or the key, index, or axis type does not match that exact domain. |
| `LOOP_LABEL_BREAK_NOT_STABLE` | `checker` | `error` | `active` | Label-based break is not Stable current surface; use break-chain. |
| `LOOP_OUTCOME_BREAK_ARM_UNREACHABLE` | `checker` | `error` | `active` | The ::break arm is unreachable for this loop outcome descriptor. |
| `LOOP_OUTCOME_COMPLETED_ARM_UNREACHABLE` | `checker` | `error` | `active` | The ::completed arm is unreachable for this loop outcome descriptor. |
| `LOOP_OUTCOME_HANDLER_TARGET_MISMATCH` | `checker` | `error` | `active` | Only the final loop transfer target may run and observe its outcome handler. |
| `LOOP_OUTCOME_MATCH_IS_STATEMENT_ONLY` | `checker` | `error` | `active` | Loop outcome match is a statement-only handler and does not produce a value. |
| `LOOP_OUTCOME_MATCH_MUST_FOLLOW_LOOP` | `checker` | `error` | `active` | Subjectless loop outcome match must immediately follow a loop statement. |
| `LOOP_OUTCOME_MATCH_NON_EXHAUSTIVE` | `checker` | `error` | `active` | Loop outcome match must cover ::completed and all reachable ::break payload domains. |
| `LOOP_OUTCOME_MATCH_PRODUCTION_NOT_REACHABLE` | `design_static` | `error` | `active` | LOOP_OUTCOME_MATCH_PRODUCTION_NOT_REACHABLE: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE` | `checker` | `error` | `active` | Loop outcome match arms must use \`::break(...)\` or \`::completed\` patterns. |
| `MALFORMED_NUMERIC_EXPONENT` | `lexer` | `error` | `active` | A decimal exponent requires one or more digits after its optional sign. |
| `MALFORMED_NUMERIC_RADIX_PREFIX` | `lexer` | `error` | `active` | A 0b, 0o, or 0x radix prefix must be followed by at least one digit candidate before a suffix or delimiter. |
| `MAP_DOT_LOOKUP_REQUIRES_SCHEMA_KNOWN_KEY` | `checker` | `error` | `seed` | Map dot lookup requires schema known key |
| `MAP_ENTRY_EQUALS_REMOVED_USE_COLON` | `checker` | `error` | `seed` | Map entry equals removed use colon |
| `MAP_IS_NOT_NAMED_UNFOLD_SOURCE` | `checker` | `error` | `active` | Map keys are runtime values and cannot provide the static labels required by named unfolding. |
| `MAP_NAMED_ARGUMENT_SPREAD_NOT_ALLOWED` | `checker` | `error` | `active` | Map values cannot be spread into named arguments because map keys are runtime values, not parameter labels. |
| `MAP_NAMED_ARGUMENT_UNFOLD_REJECTED` | `checker` | `error` | `active` | Map values cannot be expanded into named arguments. Use a Record \`${...}\` for \`**record\`, or pass explicit named arguments. |
| `MAP_NAMED_REST_UNFOLD_NOT_ALLOWED` | `checker` | `error` | `active` | Map values cannot feed named rest or named argument spread; use a Record with static labels. |
| `MAP_PERCENT_LITERAL_REMOVED_USE_HASH_MAP` | `checker` | `error` | `active` | %{...} map literal is removed; use #map{...}. |
| `MAP_UNFOLD_ELLIPSIS_NOT_CURRENT` | `checker` | `error` | `active` | \`...expr\` is not a current map unfold entry. Use \`**expr\` inside #map{...}. |
| `MAP_UNFOLD_ONLY_IN_MAP_LITERAL` | `checker` | `error` | `active` | Map unfold \`**expr\` is allowed inside \`#map{...}\` but Map values cannot be spread as call named arguments. Record named-argument spread is a separate argument-list feature. |
| `MAP_UNFOLD_SPELLING_AMBIGUOUS` | `parser` | `error` | `active` | Map unfold spelling is \`**expr\` in admitted \`#map{...}\` unfold positions; \`...expr\` map unfold is not current source in the current profile. |
| `MAP_WILDCARD_KEY_REQUIRES_STRING_LITERAL` | `checker` | `error` | `seed` | Map wildcard key requires string literal |
| `MATCH_ARM_SINGLE_GUARD_ONLY` | `parser` | `error` | `active` | A match arm admits at most one \`if\` or attached \`!if\` guard. |
| `MATCH_ARM_UNREACHABLE` | `checker` | `error` | `active` | This match arm is unreachable because an earlier arm already covers it. |
| `MATCH_EXPR_REQUIRES_AT_PREFIX` | `parser` | `error` | `active` | A value-producing match expression must use \`@match\`; bare \`match\` is statement-only. |
| `MATCH_GUARD_CONSUME_NOT_ALLOWED` | `checker` | `error` | `active` | match/@match guard may not consume or move tentative pattern bindings. |
| `MATCH_GUARD_EFFECT_NOT_ALLOWED` | `checker` | `error` | `active` | match/@match arm guard must be pure and have effects {}. |
| `MATCH_GUARD_NOT_BOOL` | `checker` | `error` | `active` | match/@match arm guard must have type Bool. |
| `MATCH_GUARD_THROWS_NOT_ALLOWED` | `checker` | `error` | `active` | match/@match arm guard must not throw. |
| `MATCH_NONEXHAUSTIVE_AFTER_GUARDS` | `checker` | `error` | `active` | Guarded arms do not count as unconditional coverage; add an unguarded arm or otherwise. |
| `MATCH_NOT_EXHAUSTIVE` | `checker` | `error` | `active` | Match expression does not cover all cases of the subject type. |
| `MATERIALIZATION_DUPLICATE_LABEL` | `checker` | `error` | `active` | A materialization label is supplied more than once after explicit and unfolded entries are normalized. |
| `MATERIALIZATION_FIELD_PUN_DUPLICATE_LABEL` | `checker` | `error` | `active` | A field pun duplicates a label already supplied explicitly or by unfold. |
| `MATERIALIZATION_FIELD_PUN_UNBOUND` | `checker` | `error` | `active` | A field-pun entry requires a same-name lexical binding. |
| `MATERIALIZATION_REQUIRED_LABEL_MISSING` | `checker` | `error` | `active` | A required ConstructionRow label has no explicit, unfolded, or default value. |
| `MATERIALIZATION_UNKNOWN_LABEL` | `checker` | `error` | `active` | A materialization label is not present in the target ConstructionRow. |
| `MATRIX_MULTIPLICATION_REQUIRES_RANK2_INNER_DIMENSION_MATCH` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `MATRIX_PRODUCT_DIMENSION_MISMATCH` | `checker` | `error` | `active` | Matrix product inner dimensions must match statically or be checker-proven. |
| `MATRIX_PRODUCT_IS_NON_ASSOCIATIVE` | `checker` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `MATRIX_PRODUCT_REQUIRES_RANK2_MATRICES` | `checker` | `error` | `active` | \`**\` matrix product requires rank-2 matrix operands in Phase A. |
| `MEASURE_AUGMENTED_ASSIGNMENT_ANCHOR_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `MEASURE_AUGMENTED_ASSIGNMENT_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `MEASURE_CONTEXT_ANCHOR_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `MEASURE_CONTEXT_ANCHOR_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `MEASURE_NUMERIC_OPERATION_REQUIRES_ANCHOR_OR_EXPLICIT_UNIT` | `checker` | `error` | `active` | Measure plus bare number requires an explicit unit literal or enabled context anchor. |
| `MEASURE_TO_NUMBER_REQUIRES_EXPLICIT_EXTRACTION` | `checker` | `error` | `active` | Measure does not convert to Number implicitly. Use \`scalarIn 1[unit]\`. |
| `MEMBERSHIP_IN_PROTOCOL_NOT_SATISFIED` | `checker` | `error` | `active` | The right operand of \`in\` does not admit the checker-known membership protocol for the left operand. |
| `MEMBER_DISPATCH_MARKER_ORDER_INVALID` | `checker` | `error` | `active` | Member dispatch markers must be ordered as *+. |
| `MEMBER_EXTENSION_COLLISION` | `checker` | `error` | `active` | A member slot and an active extension candidate both apply to the same message call shape. |
| `MEMBER_NOT_FOUND` | `checker` | `error` | `active` | No member, extension, or witness selector is available in the active lookup domain. |
| `MISSING_EXPLICIT_RETURN` | `checker` | `error` | `active` | A normal non-Unit named-function path must return a value explicitly; Unit fallthrough is canonical. |
| `MIXED_STRICT_AND_SEQUENTIAL_BOOLEAN_REQUIRES_PARENTHESES` | `parser` | `error` | `active` | Mixing \`and\` with \`and then\` requires parentheses. |
| `MIXED_STRICT_OR_SEQUENTIAL_BOOLEAN_REQUIRES_PARENTHESES` | `parser` | `error` | `active` | Mixing \`or\` with \`otherwise\` requires parentheses. |
| `MIXED_UNIT_ADDITION_REQUIRES_DISPLAY_UNIT_DECISION` | `checker` | `error` | `active` | Mixed-unit addition requires an explicit display-unit decision via \`asUnit\` or an enabled context anchor. |
| `MODIFIER_NOT_ADMITTED_FOR_OWNER` | `parser` | `error` | `active` | This modifier or role sequence is not admitted for the owning declaration or expression. |
| `MODULE_API_DIGEST_CHANGED` | `checker` | `error` | `seed` | Public API digest changed and requires compatibility classification. |
| `MODULE_IS_NOT_A_VALUE` | `checker` | `error` | `active` | A module/static path is not a runtime value. |
| `MODULE_SIGNATURE_NOT_IMPLEMENTATION_RECEIPT` | `checker` | `warning` | `active` | A module signature declaration is language-design stable but does not imply product parser/checker support. |
| `MODULE_STATIC_INITIALIZER_NOT_CURRENT` | `parser` | `error` | `active` | Module-level \`static {}\` is nonactivatable Preview-design; use static-admissible top-level let or an explicit lifecycle API. |
| `MULTILINE_STRING_CLOSER_MUST_BE_OWN_LINE` | `lexer` | `error` | `active` | A triple-quoted String closer must appear on its own line after indentation. |
| `MULTILINE_STRING_OPENER_REQUIRES_NEWLINE` | `lexer` | `error` | `active` | A triple-quoted String opener must be followed immediately by a physical newline. |
| `MULTIPLE_CANONICAL_UNITS_FOR_DIMENSION` | `checker` | `error` | `active` | A unit catalog may not declare multiple canonical units for one dimension. |
| `MULTIPLE_GUARD_CLAUSES_NOT_CURRENT` | `parser` | `error` | `active` | This owner admits at most one \`if\` or \`!if\` GuardClause. |
| `MULTIPLE_NAMED_REST_PARAMETERS` | `checker` | `error` | `active` | A callable may declare at most one named rest parameter. |
| `MULTIPLE_REPEATED_POSITIONAL_PARAMETERS` | `checker` | `error` | `active` | A callable may declare at most one repeated positional parameter. |
| `MULTIPLE_ROOT_NEW_CONSTRUCTORS` | `checker` | `error` | `active` | Phase A permits only one root \`new\` per class profile. |
| `MULTIPLE_UNIT_CONTEXT_ANCHORS_IN_OPERATION` | `checker` | `error` | `active` | Only one unit context anchor is allowed in one operation frame. |
| `MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT` | `parser` | `error` | `active` | A trailing-closure group with two or more closures requires every closure to have a unique explicit label. |
| `MUTABLE_ALIAS_REQUIRES_SHARED_WRAPPER` | `checker` | `error` | `active` | Mutable aliasing requires an admitted wrapper such as SharedMutex<T> or SharedCell<T>. |
| `MUTABLE_MEMBER_FORBIDS_VARIANT_TYPE_PARAM` | `checker` | `error` | `active` | Mutable storage or write access makes this parameter invariant. |
| `MUT_LITERAL_IS_FRESH_OWNER` | `checker` | `note` | `active` | #mut[...] constructs a fresh mutable collection owner. |
| `NAMED_ARGUMENT_EQUALS_REMOVED_USE_COLON` | `parser` | `error` | `active` | Named arguments use \`label: value\`; \`label = value\` is not current call syntax. |
| `NAMED_ARGUMENT_NOT_IN_ARGLIST` | `checker` | `error` | `seed` | Named arguments must be integrated into ArgList through Argument. |
| `NAMED_CONFORMANCE_AUTOMATIC_SEARCH_FORBIDDEN` | `checker` | `error` | `active` | A named conformance never participates in automatic witness search. |
| `NAMED_CONFORMANCE_DUPLICATE_NAME` | `checker` | `error` | `active` | A named conformance identity must be unique for its nominal type, Trait and declaration scope. |
| `NAMED_CONFORMANCE_NOT_AUTOMATIC` | `checker` | `error` | `active` | A named conformance never participates in automatic evidence search. |
| `NAMED_CONFORMANCE_NOT_CURRENT` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NAMED_CONFORMANCE_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NAMED_CONSTRUCTOR_NOT_FOUND` | `checker` | `error` | `active` | No matching named constructor exists for \`Type!name(...)\`. |
| `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR` | `parser` | `error` | `active` | Double-star is not a named-rest parameter or function-type residue; use attached \`***\`. Double-star remains the named-unfold prefix. |
| `NAMED_REST_PARAMETER_MUST_BE_LAST` | `checker` | `error` | `active` | A named-rest parameter \`options***: Record\` must be the final parameter. |
| `NAMED_REST_REQUIRES_RECORD_LABEL_SOURCE` | `checker` | `error` | `active` | Named rest and named-argument spread require a structural Record with static labels; Map is not admissible. |
| `NAMED_REST_TRIPLE_STAR_REMOVED` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NAMED_REST_TRIPLE_STAR_REMOVED_USE_DOUBLE_STAR` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NAMED_UNFOLD_CONSUMING_REQUIRES_MOVE` | `checker` | `error` | `active` | A consuming named destination requires an ownership-preserving moved projection source. |
| `NAMED_UNFOLD_REQUIRES_STATIC_PROJECTION_ROW` | `checker` | `error` | `active` | Named unfolding requires statically known labels from Record or a certified ProjectionRow. |
| `NAMED_UNICODE_ESCAPE_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NAMED_UNICODE_ESCAPE_UNKNOWN` | `lexer` | `error` | `active` | Named Unicode escape is not known in the active Unicode name table. |
| `NEGATED_RELATION_MUST_BE_ADJACENT` | `parser` | `error` | `active` | The \`!\` prefix must be adjacent to \`in\`, \`is\`, or \`if\` in a negated relation or guard. |
| `NEGATIVE_FIXTURE_EXECUTION_RECEIPT_REQUIRED` | `checker` | `warning` | `seed` | Verifier negative fixtures must be either executed by a static mutation runner or explicitly marked NOT_RUN in the receipt. |
| `NEGATIVE_IMPL_NOT_CURRENT` | `checker` | `error` | `active` | General negative impl remains Preview-design and is not current Stable source. |
| `NESTED_BLOCK_COMMENT_DASH_MISMATCH` | `lexer` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NESTED_DEF_CAPTURE_LIST_REQUIRED` | `checker` | `error` | `active` | A nested local function may use an outer local only when that capture is listed explicitly in its CaptureList. |
| `NESTED_DEF_FORWARD_REFERENCE_FORBIDDEN` | `checker` | `error` | `active` | A local function is visible only after its declaration; forward reference and mutual-recursion groups are not current. |
| `NESTED_DEF_MUTUAL_RECURSION_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NESTED_DEF_VISIBILITY_FORBIDDEN` | `parser` | `error` | `active` | A nested local function has lexical visibility and cannot carry a public/private/common modifier. |
| `NESTED_IMPLICIT_LAMBDA_ARG_NONCANONICAL` | `checker` | `warning` | `active` | Nested implicit \`@\` lambda is noncanonical; name at least one parameter explicitly. |
| `NESTED_TERNARY_REQUIRES_PARENTHESES_OR_AT_IF` | `parser` | `warning` | `active` | Nested ternary should use parentheses or @if for readability. |
| `NEVER_IS_ERRORSET_NOT_VALUETYPE` | `checker` | `note` | `seed` | \`Never\` is the empty ErrorSet, not a ValueType. Use \`Nothing\` for no normal value or \`Unit\` for normal completion. |
| `NOMINAL_SCHEMA_CONSTRUCTION_REMOVED` | `checker` | `warning` | `deprecated` | This diagnostic is not emitted by current Deeplus. |
| `NONACTIVATABLE_DESIGN_PROJECTION_NOT_CURRENT` | `checker` | `error` | `active` | This feature is a nonactivatable design projection in the current profile package; ordinary source must reject it. |
| `NONCOPYABLE_WORDING_DEPRECATED_USE_AFFINE` | `checker` | `warning` | `active` | Use affine ownership terminology instead of noncopyable wording. |
| `NONE_IS_NOT_A_TYPE` | `checker` | `error` | `active` | None is not a type in Deeplus. |
| `NOT_IF_MUST_BE_ADJACENT` | `checker` | `error` | `active` | \`!if\` must be adjacent with no whitespace/comment between \`!\` and \`if\`. |
| `NOT_IF_NOT_ALLOWED_IN_CONSTRUCTOR_DELEGATION` | `checker` | `error` | `active` | Constructor delegation arms allow \`if\`, not \`!if\`. |
| `NO_EXECUTABLE_ENTRY` | `checker` | `error` | `active` | An executable target requires exactly one \`def#entry\`, \`def#entry#async\`, or selected script root. |
| `NULLARY_LAMBDA_BLOCK_REQUIRES_RET` | `checker` | `error` | `active` | A multi-statement nullary lambda block must use \`ret\` for its result. |
| `NULLARY_LAMBDA_REQUIRES_EXPECTED_FUNCTION_CONTEXT` | `checker` | `error` | `active` | A nullary lambda without \`=>\` requires an expected zero-argument function type. |
| `NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE` | `parser` | `error` | `active` | Deeplus has no null value; use ::none in an expected Option context or Option<T>::none explicitly. |
| `NUMARR_DIMENSION_MUST_BE_POSITIVE` | `checker` | `error` | `active` | NumericArray dimensions must be positive. |
| `NUMARR_DIMENSION_STATIC_INT_REQUIRED` | `checker` | `error` | `active` | NumericArray dimensions must be StaticInt literals in Phase A. |
| `NUMARR_ELEMENT_COUNT_MISMATCH` | `checker` | `error` | `active` | NumericArray literal element count does not match shape. |
| `NUMARR_ELEMENT_NOT_NUMERIC` | `checker` | `error` | `active` | NumericArray element must be an admitted numeric type. |
| `NUMARR_ELEMENT_NOT_PLAIN_NUMERIC` | `checker` | `error` | `active` | NumericArray element must satisfy numeric/plain/no-drop law. |
| `NUMARR_ELEMENT_TYPE_REQUIRED` | `checker` | `error` | `active` | NumericArray type façade requires an element type. |
| `NUMARR_EXPECTED_SHAPE_MISMATCH` | `checker` | `error` | `active` | NumericArray literal shape mismatches expected type. |
| `NUMARR_INFIX_POWER_NOT_ADMITTED` | `checker` | `error` | `active` | NumericArray \`A ^ B\` infix power is not admitted; use \`**\`, \`*+\`, elementwise \`^\` where specified, or a named API. |
| `NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE` | `checker` | `error` | `active` | NumericArray infix \`^\` elementwise power is Preview in the current profile. Stable NumericArray transpose is attached postfix \`A^\`; matrix multiplication is \`**\`. |
| `NUMARR_LAYOUT_REQUIRES_FUTURE_PROFILE` | `checker` | `error` | `active` | Non-row-major or backend layout requires a future profile. |
| `NUMARR_LIST_LITERAL_CONTEXT_REWRITE_UNSUPPORTED` | `checker` | `error` | `active` | Ordinary list literal is never context-rewritten into NumericArray. |
| `NUMARR_LITERAL_ELEMENT_OUT_OF_RANGE` | `checker` | `error` | `active` | NumericArray literal element is outside element type range. |
| `NUMARR_LITERAL_NO_WHITESPACE` | `checker` | `error` | `active` | No whitespace is allowed in NumericArray sharp-shape literal opener. |
| `NUMARR_LITERAL_PREFIX_REQUIRED` | `checker` | `error` | `active` | NumericArray construction requires a sharp-shape literal prefix; ordinary List literal is not reinterpreted. |
| `NUMARR_LITERAL_REQUIRES_EXPRESSIONS` | `checker` | `error` | `active` | NumericArray expression literal requires element expressions; #3[T] is type position only. |
| `NUMARR_POSTFIX_TRANSPOSE_REQUIRES_NUMERIC_ARRAY` | `checker` | `error` | `active` | Postfix \`^\` transpose requires a NumericArray operand. |
| `NUMARR_RANK_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NUMARR_SHAPE_COLON_FORBIDDEN` | `checker` | `error` | `active` | NumericArray shape dimensions use comma, not colon. |
| `NUMARR_SHAPE_ERASED_TYPE_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NUMARR_SHAPE_INFERRED_VALUE_LITERAL_NOT_TYPE` | `checker` | `error` | `active` | #[...] is a value literal with inferred rank-1 shape, not a type façade. |
| `NUMARR_SHAPE_SEMICOLON_FORBIDDEN` | `checker` | `error` | `active` | NumericArray shape dimensions use comma; semicolon separates slice axes. |
| `NUMARR_TRANSPOSE_IS_NOT_ADJOINT` | `checker` | `warning` | `active` | \`A^\` is transpose, not complex adjoint; use \`A ~ adjoint\`. |
| `NUMARR_TRANSPOSE_IS_STABLE_NOT_PREVIEW` | `checker` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `NUMARR_UNKNOWN_SHARP_SHAPE_LITERAL` | `checker` | `error` | `active` | Unknown # shape literal head. |
| `NUMARR_VECTOR_TRANSPOSE_REQUIRES_ORIENTATION` | `checker` | `error` | `active` | Rank-1 NumericArray transpose requires row/column orientation witness. |
| `NUMERIC_ARRAY_CONTEXT_ANCHOR_NOT_FIRST_CLASS` | `checker` | `error` | `active` | \`&expr\` is an operand role marker in the NumericArray context-anchor MSP, not a first-class value. |
| `NUMERIC_ARRAY_CONTEXT_ANCHOR_SINGLE_ANCHOR_REQUIRED` | `checker` | `error` | `active` | A NumericArray contextual operation may have at most one context-providing \`&anchor\` operand. |
| `NUMERIC_ARRAY_ELEMENTWISE_REQUIRES_SAME_SHAPE` | `checker` | `error` | `active` | NumericArray elementwise arithmetic requires statically/proven same shape; implicit broadcasting is not performed. |
| `NUMERIC_ARRAY_ELEMENTWISE_SHAPE_MISMATCH` | `checker` | `error` | `active` | Elementwise NumericArray arithmetic requires same static or checker-proven shape. |
| `NUMERIC_ARRAY_SHAPE_MISMATCH_NO_IMPLICIT_BROADCAST` | `checker` | `error` | `active` | Ordinary NumericArray elementwise operations do not perform implicit broadcasting. |
| `NUMERIC_DIGIT_SEPARATOR_POSITION_INVALID` | `lexer` | `error` | `active` | A numeric underscore must occur exactly between two digits of the same component. |
| `NUMERIC_LITERAL_OUT_OF_RANGE` | `checker` | `error` | `active` | Numeric literal is outside the representable or refined range. |
| `NUMERIC_OPERATOR_CORE_REQUIRED` | `checker` | `error` | `active` | Numeric operator use requires the current profile numeric operator core law. |
| `NUMERIC_RADIX_FLOAT_NOT_CURRENT` | `lexer` | `error` | `active` | Radix floating-point literals are not current Deeplus source; use a decimal float or an explicit conversion. |
| `NUMERIC_SUFFIX_KIND_MISMATCH` | `lexer` | `error` | `active` | The numeric suffix kind does not match the integer or decimal-float literal. |
| `OLD_ANYDATA_REMOVED_USE_PLAIN` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `OLD_CAPABILITY_NAME_REMOVED` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `OLD_DOTTED_BITWISE_OPERATOR_REMOVED` | `parser` | `error` | `active` | Old dotted bitwise operators .&. .\|. .^. .~. are not current source; use && \|\| ^^ ~~. |
| `OPAQUE_RESULT_CONCRETE_TYPE_MISMATCH` | `checker` | `error` | `active` | some Trait function must return one hidden concrete type on all success paths. |
| `OPEN_MEMBER_REQUIRES_INHERITABLE_TYPE` | `checker` | `error` | `active` | Open member requires an open, sealed, or abstract containing type. |
| `OPERATOR_CONFORMANCE_AMBIGUOUS` | `checker` | `error` | `active` | More than one admitted direct-global conformance matches the normalized fixed-operator key. |
| `OPERATOR_CONFORMANCE_EVIDENCE_ROUTE_NOT_ADMITTED` | `checker` | `error` | `active` | Fixed-operator conformance accepts only left-owner DIRECT_GLOBAL evidence. |
| `OPERATOR_CONFORMANCE_INTRINSIC_DOMAIN_RESERVED` | `checker` | `error` | `active` | This normalized operand pair is reserved to intrinsic dispatch and cannot declare a user operator conformance. |
| `OPERATOR_CONFORMANCE_LEFT_OWNER_REQUIRED` | `checker` | `error` | `active` | A fixed-operator conformance must be declared by the package defining the normalized left nominal operand type. |
| `OPERATOR_CONFORMANCE_MISSING` | `checker` | `error` | `active` | No admitted direct-global conformance exists for this non-intrinsic fixed-operator operand pair. |
| `OPERATOR_CONFORMANCE_REQUIRES_EXPLICIT_CONVERSION` | `checker` | `error` | `active` | Fixed-operator selection never inserts an implicit operand conversion. |
| `OPERATOR_CONFORMANCE_RESPONSIBILITY_MISMATCH` | `checker` | `error` | `active` | The selected fixed-operator witness violates the borrowed, pure, total, synchronous responsibility profile. |
| `OPERATOR_NOT_CONFORMANCE_OVERLOADABLE` | `checker` | `error` | `active` | Only existing binary +, -, and * are admitted for fixed-glyph conformance overloading. |
| `OPERATOR_PRECEDENCE_TABLE_REQUIRED` | `checker` | `error` | `active` | Operator parsing requires the current profile operator precedence table. |
| `OPTIONAL_CALLABLE_INVOCATION_NOT_CURRENT` | `parser` | `error` | `active` | Optional callable invocation \`callee?(args)\` is not current Deeplus source. Use explicit Option flow. |
| `OPTIONAL_CHAINING_NOT_CURRENT` | `parser` | `error` | `active` | Optional chaining is not current Deeplus source; use explicit Option handling, match/@match, if-let, or library combinators. |
| `OPTIONAL_SUFFIX_REPEATED` | `parser` | `error` | `active` | A compact optional suffix may occur once; write Option<T?> for nested optionality. |
| `OPTIONAL_TYPE_SUFFIX_REQUIRES_NO_WHITESPACE` | `parser` | `error` | `active` | The ? in T? must attach with no whitespace. |
| `OPTION_BARE_NONE_REMOVED` | `checker` | `error` | `active` | Bare None is not current Deeplus source; use \`::none\` with expected Option type or \`Option<T>::none\`. |
| `OPTION_BARE_SOME_REMOVED` | `checker` | `error` | `active` | Bare Some(value) is not current Deeplus source; use \`::some(value)\` with expected Option type or \`Option<T>::some(value)\`. |
| `OPTION_COALESCE_AFFINE_LHS_REQUIRES_MOVE` | `checker` | `error` | `active` | Extracting an affine payload requires moving the owned Option into \`?:\`. |
| `OPTION_COALESCE_BORROWED_AFFINE_EXTRACTION` | `checker` | `error` | `active` | A borrowed Option cannot produce an owned affine payload through \`?:\`. |
| `OPTION_COALESCE_CONDITIONAL_MOVE_NOT_STABLE` | `checker` | `error` | `active` | Moving an existing fallback local only on the none path requires a path-sensitive ownership profile that is not Stable. |
| `OPTION_COALESCE_CONTROL_TRANSFER_FALLBACK_FORBIDDEN` | `parser` | `error` | `active` | The fallback of \`?:\` is a value expression, not return/throw/break/continue control transfer. |
| `OPTION_COALESCE_DOES_NOT_APPLY_TO_RESULT` | `checker` | `error` | `active` | \`?:\` cannot discard Result error evidence; handle Result explicitly. |
| `OPTION_COALESCE_FALLBACK_TYPE_MISMATCH` | `checker` | `error` | `active` | The fallback must have the payload type T of the left Option<T>. |
| `OPTION_COALESCE_LHS_TYPE_UNRESOLVED` | `checker` | `error` | `active` | The left Option payload type cannot be inferred; provide an expected type or full Option value. |
| `OPTION_COALESCE_REQUIRES_OPTION_LEFT` | `checker` | `error` | `active` | The left operand of \`?:\` must have type Option<T> or T?. |
| `OPTION_COALESCE_TOKEN_MUST_BE_ADJACENT` | `lexer` | `error` | `active` | Option coalescing uses the adjacent compound token \`?:\`; separated \`? :\` belongs to ternary syntax. |
| `OPTION_COLLECTION_ELEMENT_IMPLICIT_LIFT_NOT_ALLOWED` | `checker` | `error` | `active` | Collection elements are not implicitly lifted to Option<T>. |
| `OPTION_IMPLICIT_LIFT_NOT_ALLOWED` | `checker` | `error` | `active` | T is not a subtype of Option<T>. Exactly one top-level \`some\` insertion is admitted only after an explicit local Option target is fixed; call arguments, returns, lambda results, collection elements, generic-driving inference, and nested lifts never insert it. |
| `OPTION_NONE_REQUIRES_EXPECTED_TYPE` | `checker` | `error` | `active` | \`::none\` requires an expected Option<T> / T? type; otherwise use \`Option<T>::none\`. |
| `OPTION_SOME_PAYLOAD_TYPE_MISMATCH` | `checker` | `error` | `active` | \`::some\` payload does not match the expected Option element type. |
| `OPTION_VISIBLE_SOME_ELISION_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `OPTION_VISIBLE_SOME_ELISION_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `ORDINARY_DEF_EXPRESSION_BODY_NOT_CURRENT` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `OR_PATTERN_BINDINGS_INCONSISTENT` | `checker` | `error` | `active` | All alternatives of an or-pattern must bind the same names with identical canonical types, modes, mutability, usable lifetimes, and capabilities. |
| `OTHERWISE_DUPLICATE_CLAUSE` | `checker` | `error` | `active` | A clause block or match may contain at most one \`otherwise\` arm. |
| `OTHERWISE_MUST_BE_LAST` | `checker` | `error` | `active` | \`otherwise\` must be the last clause or match arm. |
| `OTHERWISE_UNREACHABLE` | `checker` | `error` | `active` | The \`otherwise\` arm is unreachable because previous clauses already cover all cases. |
| `OVERRIDE_VISIBILITY_CANNOT_NARROW` | `checker` | `error` | `active` | Overriding/fulfilling member cannot reduce base slot visibility. |
| `OWNED_DOWNCAST_OWNER_NOT_PRESERVED` | `checker` | `error` | `active` | An owned downcast must return either the matched target owner or the original unmatched source owner. |
| `OWNERSHIP_MODE_ADMISSION_FAILED` | `checker` | `error` | `active` | The borrow/inout/move mode violates exclusivity, lifetime, escape, suspension, or transfer responsibility. |
| `OWN_CAST_REQUIRES_REUSABLE_SOURCE` | `checker` | `error` | `active` | Owning downcast via as? cannot duplicate affine ownership. Use owner-preserving consuming downcast. |
| `PACKAGE_ARCHIVE_SHA_MISMATCH` | `design_static` | `error` | `active` | PACKAGE_ARCHIVE_SHA_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `PACKAGE_DECLARATION_RENAMED_TO_MODULE` | `checker` | `error` | `active` | \`package\` is not a Deeplus source namespace declaration; use \`module\`. |
| `PATTERN_ANALYSIS_RESOURCE_LIMIT` | `checker` | `error` | `active` | Pattern analysis reached its deterministic resource limit before proving admission or exhaustiveness. |
| `PATTERN_BORROWED_MATCH_CANNOT_MOVE_PAYLOAD` | `checker` | `error` | `seed` | Borrowed match arm cannot move a payload out of the borrowed subject. |
| `PATTERN_CONTROL_PARTIAL_BINDING_FORBIDDEN` | `checker` | `error` | `active` | Pattern-control failure must commit no partial binding or move. |
| `PATTERN_CONTROL_REQUIRES_REFUTABLE_PATTERN` | `checker` | `error` | `active` | A pattern-binding control requires a refutable pattern. |
| `PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH` | `checker` | `error` | `active` | Normally returning Pattern arms leave incompatible usable-place states at the join. |
| `PATTERN_DUPLICATE_BINDING` | `checker` | `error` | `seed` | Pattern introduces the same binding name more than once in a single binding scope. |
| `PATTERN_FIELD_NOT_FOUND` | `checker` | `error` | `seed` | Record/schema pattern references a field that is not present in the matched type. |
| `PATTERN_MOVES_LIFECYCLE_TOKEN_IMPLICITLY` | `lexer` | `error` | `seed` | Pattern decomposition cannot implicitly move a lifecycle token or resource owner. |
| `PATTERN_MULTIPLE_REST` | `parser` | `error` | `active` | A List pattern may contain at most one rest form. |
| `PATTERN_PRIVATE_REPRESENTATION_FORBIDDEN` | `checker` | `error` | `active` | Pattern decomposition cannot open a Class, Dyn, Facet, FFI, or opaque private representation. |
| `PATTERN_REST_MUST_BE_FINAL_IGNORED` | `parser` | `error` | `active` | The only current List-pattern rest is one ignored \`.._\` in final position. |
| `PLACE_REPLACE_NOT_ADMITTED` | `checker` | `error` | `active` | replace requires one stable place, exclusive access, and a transaction that preserves exactly one old and one new owner. |
| `PLAIN_HETEROGENEOUS_TOP_FORBIDDEN` | `checker` | `error` | `active` | \`Plain\` is not a heterogeneous dynamic top. Use an explicit union, JsonValue, Dyn, or a typed boundary wrapper. |
| `PLAIN_IS_NOT_DERIVED_BY_ANNOTATION` | `checker` | `error` | `active` | Annotation cannot create Plain admissibility. Use Plain boundary type or satisfies Plain candidate. |
| `PLAIN_IS_NOT_DYNAMIC` | `checker` | `error` | `active` | Plain is not a dynamic invocation boundary; use Dyn for dynamic inspection. |
| `PLAIN_IS_NOT_JSONVALUE` | `checker` | `error` | `active` | Plain is not external JSON; use JsonValue for JSON data. |
| `PLAIN_IS_NOT_LAYOUT_SAFE` | `checker` | `error` | `active` | Plain does not imply FFI-safe layout or byte-copy safety. |
| `PLAIN_IS_NOT_RAW_LAYOUT` | `checker` | `note` | `active` | Plain is not a raw-layout, FFI-layout, byte-copy, or all-bit-pattern type. |
| `PLAIN_IS_PLAINVALUE_ALIAS` | `checker` | `note` | `active` | Plain is a true alias of PlainValue. |
| `PLAIN_OR_SHARED_REJECTS_LIFECYCLE_OWNER` | `checker` | `error` | `active` | Plain/Shared minimum profiles reject lifecycle owners. |
| `PLAIN_REJECTS_CALLABLE` | `checker` | `error` | `active` | Callable values cannot be erased into Plain. |
| `PLAIN_REJECTS_LIFECYCLE_OWNER` | `checker` | `error` | `active` | Lifecycle owner cannot be erased into Plain. |
| `PLAIN_REJECTS_META_AUTHORITY` | `checker` | `error` | `active` | Reflection/meta authority values cannot be erased into PlainValue/Plain. |
| `PLAIN_REJECTS_RAW_POINTER` | `checker` | `error` | `active` | Raw pointer/provenance values cannot be erased into Plain. |
| `PLAIN_REJECTS_RESOURCE` | `checker` | `error` | `active` | Lifecycle/resource owners cannot be erased into PlainValue/Plain. |
| `PLAIN_REJECTS_SHARED_HANDLE` | `checker` | `error` | `active` | Shared<T> is a shared owner/handle, not Plain data. |
| `PLAIN_REJECTS_VIEW_OWNER_REGION` | `checker` | `error` | `active` | Plain rejects borrowed view owner-region values. |
| `POSITIONAL_UNFOLD_REQUIRES_SEQUENCE_OR_TUPLE` | `checker` | `error` | `active` | \`*expr\` in an argument list requires a Sequence or statically known tuple; NumericArray and ordinary array-shaped storage do not supply positional-unfold arity evidence. |
| `POSTFIX_MUTATION_OPERATOR_NOT_CURRENT` | `parser` | `error` | `active` | Prefix/postfix increment and decrement expressions are not current Deeplus; write an explicit assignment. |
| `POSTFIX_TRANSPOSE_MUST_BE_ATTACHED` | `checker` | `error` | `active` | NumericArray postfix transpose is written attached as \`A^\`. |
| `POSTFIX_TRANSPOSE_NOT_CURRENT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `POWER_EXPECTED_RESULT_SELECTION_FORBIDDEN` | `checker` | `error` | `active` | An expected result type cannot create or choose a power operation. |
| `POWER_INTEGER_EXPONENT_NONNEGATIVE_PROOF_REQUIRED` | `checker` | `error` | `active` | An integer-result power requires a statically proven nonnegative exact integer exponent. |
| `POWER_LITERAL_ADAPTATION_NOT_EXACT` | `checker` | `error` | `active` | The power-local literal adaptation is not exact in the selected result domain. |
| `POWER_MATH_PROFILE_MISMATCH` | `linker` | `error` | `active` | Imported power semantics or special-value profile does not match the verified HIR-H1 plan. |
| `POWER_OPERAND_DOMAIN_NOT_ADMITTED` | `checker` | `error` | `active` | The operand types do not select one cell of the closed scalar power-domain matrix. |
| `PREFER_AT_IF_FOR_MULTILINE_TERNARY` | `checker` | `warning` | `active` | Long or multiline ternary is clearer as @if. |
| `PREFIXED_LITERAL_NO_WHITESPACE` | `checker` | `error` | `active` | No whitespace is allowed between #, prefix, and literal opener. |
| `PREFIXED_LITERAL_PREFIX_REQUIRED` | `checker` | `error` | `active` | Stable prefixed literal families require their exact \`#\` prefix; the current prefix set is \`#map\`, \`#set\`, \`#mut\`, \`#raw\`, and \`#bytes\`. |
| `PREFIX_FUNCTION_PROFILE_REMOVED_USE_DEF_HASH` | `parser` | `error` | `active` | Prefix async/guard/entry def spelling is not current; use the owner-appropriate closed def# introducer. |
| `PREFIX_UNARY_POWER_BASE_REQUIRES_PARENTHESES` | `parser` | `error` | `retired` | Historical diagnostic: current -2 ^ 2 parses as -(2 ^ 2), while (-2) ^ 2 keeps the explicit negative base. |
| `PRELUDE_SIGNATURE_CATALOG_REQUIRED` | `design_static` | `error` | `active` | PRELUDE_SIGNATURE_CATALOG_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `PREVIEW_ALTERNATIVE_LEAKS_THROUGH_STABLE_PARENT` | `parser` | `error` | `active` | A stable/ordinary grammar parent includes a gated alternative without alternative-level metadata. |
| `PREVIEW_GATE_DEPENDENCY_MISSING` | `parser` | `error` | `active` | A #preview list must explicitly contain the transitive closure of every PREVIEW dependency. |
| `PREVIEW_GATE_DUPLICATE_FEATURE` | `parser` | `error` | `active` | A #preview feature list must contain each feature id exactly once. |
| `PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE` | `parser` | `error` | `active` | A #preview entry may name only a PREVIEW feature whose source_activation is explicit_feature_gate; PREVIEW_DESIGN is nonactivatable. |
| `PREVIEW_GATE_PLACEMENT_INVALID` | `parser` | `error` | `active` | The Preview gate must be the first token of a library/executable source or the first non-shebang token of a script, before ModuleDecl and source items. |
| `PREVIEW_GATE_UNKNOWN_FEATURE` | `parser` | `error` | `active` | Every #preview entry must name a feature present in the current feature registry. |
| `PRIMARY_CONSTRUCTOR_BARE_PARAM_NOT_MEMBER` | `checker` | `error` | `active` | Bare primary constructor parameter is not a promoted member. |
| `PRIMARY_CONSTRUCTOR_PROMOTED_VISIBILITY_SIGIL_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PRIMARY_CONSTRUCTOR_PROMOTION_VISIBILITY_SIGIL_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PRIMARY_CTOR_DOLLAR_PROMOTION_REMOVED_USE_LET_VAR` | `checker` | `error` | `active` | Primary constructor promotion uses let/var; $ and $* promotion are removed. |
| `PRIMARY_CTOR_LAYOUT_PROMOTED_FIELD_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PRIMARY_CTOR_LAYOUT_PROMOTED_FIELD_SEPARATOR_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PRIMARY_CTOR_LAYOUT_REQUIRES_PROMOTED_FIELD` | `checker` | `error` | `active` | Primary-constructor layout separator is limited to promoted let/var fields. |
| `PRIMARY_CTOR_PROMOTED_FIELD_ROUTE_UNREACHABLE` | `design_static` | `error` | `active` | PRIMARY_CTOR_PROMOTED_FIELD_ROUTE_UNREACHABLE: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `PRIMARY_CTOR_PROMOTED_FIELD_VISIBILITY_APPLIES_TO_MEMBER` | `checker` | `warning` | `seed` | The visibility sigil on a promoted primary-constructor field applies to the generated member, not to the constructor input label. |
| `PRIMARY_CTOR_PUBLIC_NEW_EXPOSES_PRIVATE_FIELD_INPUT` | `checker` | `warning` | `seed` | A public root constructor can expose a private promoted field as an input label; this is allowed but should be documented in public API digest. |
| `PRIMARY_CTOR_VISIBILITY_SIGIL_MUST_ATTACH_TO_STORAGE` | `checker` | `error` | `active` | Primary-constructor promoted field visibility sigils must attach to \`let\` or \`var\`, for example \`+let name: String\`. |
| `PRIMARY_GENERATED_NEW_CONSTRUCTOR_COLLISION` | `checker` | `error` | `active` | Primary-generated \`new\` collides with an explicit root \`new\` constructor. |
| `PRIVATE_MEMBER_CANNOT_BE_OPEN` | `checker` | `error` | `active` | Private member cannot be open. |
| `PRODUCTION_PARSER_RECEIPT_NOT_INCLUDED` | `checker` | `info` | `seed` | This package does not include a production parser receipt. |
| `PRODUCTION_PARSER_RECEIPT_REQUIRED_FOR_HANDOFF` | `design_static` | `error` | `active` | PRODUCTION_PARSER_RECEIPT_REQUIRED_FOR_HANDOFF: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `PROJECTION_MARKDOWN_VALUE_DRIFT` | `design_static` | `error` | `active` | Generated Markdown projection rows differ from the canonical JSON registry values. |
| `PROPERTY_TEST_GENERATION_PROFILE_REQUIRES_FEATURE_GATE` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PROPERTY_VALUE_REQUIRES_REUSABLE_NODROP` | `checker` | `error` | `active` | Accessor property by-value result must be reusable, no-drop, and lifecycle-free in the Stable profile. |
| `PROTOTYPE_DEEP_DERIVATION_REQUIRES_DEEP_CLONE_LAW` | `checker` | `error` | `active` | Deep prototype derivation requires a deep derivation/DeepClone law. |
| `PROTOTYPE_DELTA_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | Feature \`prototype_delta\` is PREVIEW_DESIGN/nonactivatable and has no current source gate. |
| `PROTOTYPE_DERIVATION_BRACE_FORM_REQUIRED` | `parser` | `error` | `active` | Prototype derivation must use source!{...} or source!!{...}; dollar-brace and unbraced cover forms are not current source or invalid. |
| `PROTOTYPE_DERIVATION_DOLLAR_REMOVED` | `checker` | `error` | `active` | Prototype derivation no longer uses $; write source!{...} or source!!{...}. |
| `PROTOTYPE_DERIVATION_NO_WHITESPACE_BEFORE_DELTA` | `checker` | `error` | `active` | No whitespace is allowed between !/!! and the prototype delta block. |
| `PROTOTYPE_DERIVATION_RESPONSIBILITY_MISMATCH` | `checker` | `error` | `active` | Prototype derivation must preserve the exact nominal type and satisfy its visible ConstructionRow and clone responsibilities. |
| `PROVIDER_SIDECAR_NOT_RECHECKED` | `checker` | `error` | `seed` | Provider-generated sidecar must be materialized and rechecked as ordinary Deeplus source. |
| `PUBLIC_API_HIDDEN_WITNESS` | `checker` | `error` | `active` | Public API depends on a trait, associated item, or witness that is not public/exportable. |
| `PURE_CALLABLE_MUTABLE_CAPTURE_FORBIDDEN` | `checker` | `error` | `active` | A #pure callable cannot capture var/inout/mutable shared state. |
| `PURE_CALLABLE_PROFILE_VIOLATION` | `checker` | `error` | `active` | A #pure callable must be nonthrowing, effect-free, nonsuspending, authority-free, and free of mutable/resource captures. |
| `PURE_ELISION_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PURE_ELISION_RETURN_BODY_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `PURE_FUNCTION_EFFECT_VIOLATION` | `checker` | `error` | `active` | def#pure body must have effects {}. |
| `PURE_FUNCTION_THROWS_VIOLATION` | `checker` | `error` | `active` | def#pure body must throw Never. |
| `QUALIFIED_EXTENSION_SELECTOR_REQUIRED` | `checker` | `error` | `active` | Ambiguity or collision requires an explicit qualified extension selector. |
| `QUALIFIED_EXTENSION_SELECTOR_UNKNOWN` | `checker` | `error` | `active` | The qualified extension selector does not resolve to a visible extension function or set member. |
| `QUARANTINE_EXPORT_REQUIRES_TYPED_IMMUTABLE_BINDING` | `checker` | `error` | `seed` | A quarantine result may leave only through an explicitly typed immutable export. |
| `QUARANTINE_OUTER_MUTATION_FORBIDDEN` | `checker` | `error` | `seed` | A quarantine scope may not mutate an outer place. |
| `QUARANTINE_RESOURCE_ESCAPE_FORBIDDEN` | `checker` | `error` | `seed` | Pointers, authorities, borrows, resources, closures, tasks and actors may not escape a quarantine scope. |
| `QUARANTINE_SCOPE_NOT_ACTIVATABLE` | `parser` | `error` | `active` | Dynamic/unsafe quarantine scope is a nonactivatable design probe, not current source. |
| `QUARANTINE_SUSPENSION_FORBIDDEN` | `checker` | `error` | `seed` | A quarantine scope may not suspend, await, yield or spawn. |
| `R0_GUARD_NOT_GUARD_SAFE` | `checker` | `error` | `active` | Declarative clause guards must be R0-safe: deterministic, sync, throws Never, effects {}, and built from the admitted R0 predicate subset. |
| `R0_GUARD_USES_WORD_BOOLEAN_OPERATORS` | `checker` | `error` | `active` | R0 guard predicates use the Boolean words \`not\`, \`and\`, and \`or\`; symbolic \`!\`, \`&&\`, and \`\|\|\` are different or non-current operator families. |
| `R1_PROOF_PROFILE_OUTSIDE_INTRINSIC_SUBSET` | `checker` | `error` | `active` | The proof obligation is outside the stable R1 intrinsic-pure profile. |
| `R45G_RESTORED_EXAMPLE_REVIEW_SEED_NOT_PRODUCT_RECEIPT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R45H_RESTORED_EXAMPLE_REVIEW_SEED_NOT_PRODUCT_RECEIPT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R47_PROMOTION_CONFLICT_RESOLVED_TO_PREVIEW` | `checker` | `warning` | `seed` | A feature was requested as both Stable and Preview; R49 resolves the source-surface row to Preview and records stable semantic intent in the designer report. |
| `R48B_AUTHORITY_ENUM_UNDECLARED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_CHECKER_PREDICATE_DUPLICATE_ID` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_COVERAGE_BLOCK_REF_DANGLING` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_CROSSWALK_BLOCK_REF_DANGLING` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_GRAMMAR_PROFILE_COUNT_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_MARKDOWN_MACHINE_PROJECTION_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_NEGATIVE_FIXTURE_RUNNER_COUNT_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_PUBLICATION_RECEIPT_METADATA_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_SPEC_PROFILE_REGISTRY_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48B_STABLE_ONLY_GRAMMAR_NONCURRENT_LEAK` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_ACTIVE_DIAGNOSTIC_CURRENT_WORDING_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_AS_QUERY_RETURNS_OPTION` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_CHECKER_PREDICATE_SCHEMA_CURRENT_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_CHECKER_PREDICATE_SCHEMA_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_CHECKER_PREDICATE_STABLE_GATE_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_COMPANION_SIDECAR_STALE_STATUS` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_CROSSWALK_TRACE_KIND_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_CURRENT_ONLY_FRONT_MATTER_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_CURRENT_PROSE_STATUS_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_DISCARDED_PROPOSAL_BODY_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_EXAMPLE_MANIFEST_PARITY_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_EXAMPLE_MANIFEST_SOURCE_ACTIVATION_INVALID` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_EXAMPLE_MARKDOWN_MANIFEST_FEATURE_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_FEATURE_CROSSWALK_TRACE_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_FEATURE_GATE_DIAGNOSTIC_ACTIVE_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_FEATURE_REFERENCE_NOT_IN_REGISTRY` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_FILE_COUNT_RECEIPT_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_GALLERY_MANIFEST_HASH_MISMATCH` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_GATE_MAP_NON_PREVIEW_FEATURE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_GRAMMAR_METADATA_REGISTRY_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_GRAMMAR_METADATA_STATUS_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_HISTORY_PAYLOAD_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_PRODUCT_SUPPORT_NOT_RUN_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_PRODUCT_SUPPORT_OVERCLAIM_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_PROJECTION_PARITY_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_PUBLICATION_RECEIPT_COUNT_MISMATCH` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_RECEIPT_COUNT_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_SIDECAR_STALE_STATUS_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_SMOKE_CORPUS_EXPECTATION_REPAIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_SMOKE_FIXTURE_ID_COLLISION` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_SOURCE_TRUTH_PROJECTION_REGENERATED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_SPEC_PROFILE_REGISTRY_DRIFT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_STABLE_DEPENDS_ON_PREVIEW_FORBIDDEN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_STABLE_FEATURE_NOTE_STALE_TERM` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_STABLE_GRAMMAR_PRODUCTION_NAME_CURRENT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_STABLE_ONLY_GRAMMAR_CURRENT_SOURCE_ONLY` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_STABLE_ONLY_PREVIEW_FEATURE_LEAK` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_STATIC_PACKAGE_PASS_NOT_PRODUCT_SUPPORT` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_TYPESYSTEM_CURRENT_ONLY_COMPANION_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_TYPESYSTEM_EXAMPLE_COVERAGE_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_TYPESYSTEM_FORMAL_JUDGMENT_SECTION_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_TYPESYSTEM_STALE_STATUS_RESIDUE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `R48_TYPE_RESPONSIBILITY_DESCRIPTOR_V3_REQUIRED` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `RANGE_CLOSED_END_NOT_ON_STEP_LATTICE` | `checker` | `lint` | `active` | Closed endpoint is not yielded by this step lattice. |
| `RANGE_LITERAL_TYPE_POSITION_ONLY` | `checker` | `error` | `active` | Range literal refinement type is allowed only in type position. |
| `RANGE_OPERATOR_SPELLING_NOT_CURRENT` | `parser` | `error` | `active` | This range spelling is not current Deeplus; use .. or ..< in an admitted range owner. |
| `RANGE_STEP_DIRECTION_MISMATCH` | `checker` | `error` | `active` | Range direction and step sign are inconsistent. |
| `RANGE_STEP_ZERO` | `checker` | `error` | `active` | Range step must not be zero. |
| `RANGE_UNSIGNED_DESCENDING_REQUIRES_SIGNED_DOMAIN` | `checker` | `error` | `active` | Unsigned descending ranges require an explicit signed delta/domain profile. |
| `RATIONAL_INEXACT_MIX_REQUIRES_EXPLICIT_CONVERSION` | `checker` | `error` | `active` | Mixing Rational with Decimal, Float, or Complex requires an explicit named conversion. |
| `RATIONAL_LITERAL_COMPONENT_NOT_DECIMAL_INTEGER` | `lexer` | `error` | `active` | Each Rational literal component must be an unsigned decimal magnitude with no radix prefix or suffix. |
| `RATIONAL_LITERAL_DENOMINATOR_ZERO` | `checker` | `error` | `active` | A Rational literal denominator must be nonzero. |
| `RATIONAL_LITERAL_MALFORMED` | `lexer` | `error` | `active` | Rational literal must have the exact expression-prefix form <unsigned-decimal/unsigned-decimal>. |
| `RATIONAL_LITERAL_RESOURCE_LIMIT` | `checker` | `error` | `active` | Rational literal normalization exceeded the declared deterministic compile-time resource budget. |
| `RATIONAL_LITERAL_SIGN_MUST_BE_PREFIX` | `parser` | `error` | `active` | Write a Rational sign outside the literal, for example -<2/3>. |
| `RATIONAL_LITERAL_TRIVIA_FORBIDDEN` | `lexer` | `error` | `active` | Rational literal delimiters, numerator, slash, and denominator must be contiguous. |
| `RATIONAL_OVER_REQUIRES_EXACT_INTEGERS` | `checker` | `error` | `active` | Rational construction through over requires two exact integer operands. |
| `RAW_MULTILINE_STRING_NOT_CURRENT` | `lexer` | `error` | `active` | Raw multiline String syntax is not current; use the Unicode multiline String or \`#raw"..."\`. |
| `RAW_POINTER_ARITHMETIC_OPERATOR_FORBIDDEN` | `checker` | `error` | `active` | Use named unsafe pointer operations instead of ordinary arithmetic operators. |
| `RAW_STRING_DELIMITER_INVALID` | `lexer` | `error` | `active` | Stable raw String uses exactly the attached \`#raw"..."\` delimiter family. |
| `RAW_STRING_UNTERMINATED` | `lexer` | `error` | `active` | A raw String literal must end with its closing double quote. |
| `RAW_WITNESS_VALUE_FORBIDDEN` | `checker` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `RAW_WITNESS_VALUE_NOT_CURRENT` | `checker` | `error` | `active` | Witness evidence is not an ordinary first-class type or value; the only source binding is an explicit borrowed \`using name: witness Trait\` parameter. |
| `RCTS_API_DIGEST_INCOMPLETE` | `checker` | `error` | `active` | The public API digest omits a normalized responsibility residue. |
| `RCTS_BITFIELD_DUPLICATE_SLOT_NAME` | `checker` | `error` | `active` | Bitfield and flags slot names must be unique. |
| `RCTS_BORROW_REQUIRES_VIEW_RELEASE_CLEANUP` | `checker` | `error` | `active` | Borrow ownership requires view_release cleanup and cannot own drop cleanup. |
| `RCTS_FACET_BORROW_REGION_REQUIRED` | `checker` | `error` | `active` | A borrowed Facet requires an explicit nonempty borrow region. |
| `RCTS_FACET_BORROW_REQUIRES_VIEW_RELEASE` | `checker` | `error` | `active` | A borrowed Facet requires view_release cleanup owned by its region. |
| `RCTS_FACET_EXISTENTIAL_SAFETY_REQUIRED` | `checker` | `error` | `active` | A Facet contract must be existential-safe under the selected mode. |
| `RCTS_FLAGS_SLOT_WIDTH_MUST_BE_ONE` | `checker` | `error` | `active` | Every named flags slot has width exactly one. |
| `RCTS_FLOW_STATE_EMBEDDED_IN_TYPE_DESCRIPTOR` | `checker` | `error` | `active` | Flow state belongs in Phi and cannot be embedded in a semantic type descriptor. |
| `RCTS_GUARD_CALLABLE_INOUT_FORBIDDEN` | `checker` | `error` | `active` | A #guard callable cannot have an inout parameter. |
| `RCTS_INTERSECTION_CONTRACT_MUST_BE_TRAIT` | `checker` | `error` | `active` | Every contract member of an intersection must resolve to a Trait. |
| `RCTS_PURE_CALLABLE_EFFECTS_FORBIDDEN` | `checker` | `error` | `active` | A #pure callable must have an empty effect row. |
| `RCTS_RESOURCE_REQUIRES_DROP_CLEANUP` | `checker` | `error` | `active` | Resource ownership requires drop_exactly_once cleanup. |
| `RCTS_RESPONSIBILITY_AXIS_DROPPED` | `checker` | `error` | `active` | Normalization or API projection dropped a responsibility axis. |
| `RCTS_V5_IMPOSSIBLE_FIELD_COMBINATION` | `checker` | `error` | `active` | The RCTS-V5 descriptor combines responsibility fields forbidden for this variant. |
| `RCTS_V5_VARIANT_MISMATCH` | `checker` | `error` | `active` | The RCTS-V5 descriptor does not match its declared closed variant. |
| `READONLY_VIEW_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | A readonly view cannot outlive, out-transfer, or survive move/drop of its owner. |
| `RECEIPT_PRODUCT_LANE_OVERCLAIM` | `design_static` | `error` | `active` | Publication receipt must keep product support lanes NOT_RUN unless an actual product receipt is attached. |
| `RECEIVER_MODE_MISMATCH` | `checker` | `error` | `active` | The selected member or extension candidate requires a receiver mode that the call site cannot provide. |
| `RECEIVER_OWNER_RESULT_MUST_BE_EXPLICIT` | `checker` | `error` | `active` | A consuming receiver result must explicitly return a Self-compatible owner. |
| `RECEIVER_OWNER_RESULT_NOT_EXACTLY_ONCE` | `checker` | `error` | `active` | The consuming receiver owner must be returned exactly once on every successful path. |
| `RECORD_ENTRY_SEPARATOR_REQUIRED` | `checker` | `error` | `active` | Same-line record entries require comma; multi-line entries may use LayoutEntrySep when unambiguous. |
| `RECORD_FIELD_DUPLICATE` | `checker` | `error` | `active` | Record/schema literal contains a duplicate field key. Deeplus schema construction requires deterministic field ownership. |
| `RECORD_FIELD_EQUALS_REMOVED_USE_COLON` | `checker` | `error` | `seed` | Record field equals removed use colon |
| `RECORD_LITERAL_BRACE_COVER_REPAIRED` | `parser` | `error` | `seed` | Record literal cover grammar must parse \`${ field: value }\` with one brace pair. |
| `RECORD_NAMED_ARGUMENT_SPREAD_REQUIRES_RECORD` | `checker` | `error` | `active` | \`**expr\` in an argument list requires a structural Record with statically known labels. |
| `RECORD_PATTERN_DUPLICATE_FIELD` | `checker` | `error` | `active` | A Record pattern names the same required label more than once. |
| `RECORD_PATTERN_PRIVATE_FIELD` | `checker` | `error` | `active` | A Record pattern cannot project a label that is not visible in the current authority domain. |
| `RECORD_PATTERN_UNKNOWN_FIELD` | `checker` | `error` | `active` | A Record pattern names a label outside the subject's statically known Record row. |
| `RECORD_SPREAD_DUPLICATE_NAMED_ARGUMENT` | `checker` | `error` | `active` | Record spread creates a named argument label that is already supplied by another argument or spread. |
| `RECORD_SPREAD_MISSING_REQUIRED_PARAMETER` | `checker` | `error` | `active` | Record spread plus explicit arguments do not provide all required named parameters. |
| `RECORD_SPREAD_UNKNOWN_PARAMETER_LABEL` | `checker` | `error` | `active` | Record spread contains a field label that does not correspond to any parameter label in the selected callable. |
| `RECORD_UNFOLD_LABEL_SET_NOT_STATICALLY_DISJOINT` | `checker` | `error` | `active` | A record spread in named arguments must be statically disjoint from explicit labels and other spreads. |
| `RECORD_UNFOLD_MISSING_REQUIRED_LABEL_EVIDENCE` | `checker` | `error` | `active` | A record spread cannot satisfy required named parameters unless its label set is statically known. |
| `REDUNDANT_ASSOCIATED_PROJECTION_PARENS_BEFORE_OPTIONAL` | `checker` | `lint` | `active` | Parentheses are redundant before an optional suffix on an associated projection; write \`<T as Trait>::Assoc?\`. |
| `REDUNDANT_FINAL_VALUELESS_RETURN` | `checker` | `lint` | `active` | The final valueless return is redundant; normal Unit completion is canonical. |
| `REFINED_ELEMENT_TYPE_REQUIRES_WHERE_THIS` | `checker` | `error` | `seed` | Refined element type requires where this |
| `REFINEMENT_ASSERTION_MAY_DEFECT` | `checker` | `warning` | `active` | \`as!\` may raise RefinementAssertionDefect if the predicate fails. |
| `REFINEMENT_DETAILED_CHECK_RETURNS_RESULT` | `checker` | `info` | `active` | Detailed validation uses \`T::check(value)\` or a named factory returning \`Result<T, error E>\`; \`as?\` returns \`Option<T>\`. |
| `REFINEMENT_IMPLICIT_NARROWING_FORBIDDEN` | `checker` | `error` | `active` | Implicit narrowing to a refinement type is forbidden. |
| `REFINEMENT_LITERAL_OUT_OF_RANGE` | `checker` | `error` | `active` | The literal value is outside the refinement range. |
| `REFINEMENT_PREDICATE_CALL_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `REFINEMENT_PREDICATE_EFFECT_FORBIDDEN` | `checker` | `error` | `active` | Refinement predicates must have effects {}. |
| `REFINEMENT_PREDICATE_NOT_PHASE_A` | `checker` | `error` | `active` | This refinement predicate is outside Phase A. |
| `REFINEMENT_PREDICATE_THROW_FORBIDDEN` | `checker` | `error` | `active` | Refinement predicates must throw Never. |
| `REFINEMENT_PROOF_REQUIRED` | `checker` | `error` | `active` | The value is not statically known to satisfy the refinement. Use \`as?\` or \`as!\`. |
| `REFINEMENT_R0_PREDICATE_NOT_ADMITTED` | `checker` | `error` | `active` | The refinement predicate is outside the closed pure and total R0 calculus. |
| `REFINEMENT_RANGE_BOUND_STATIC_INT_REQUIRED` | `checker` | `error` | `active` | Range refinement bounds must be StaticInt literals in Phase A. |
| `REFINEMENT_RANGE_EMPTY` | `checker` | `error` | `active` | The refinement range is empty because lower bound is greater than upper bound. |
| `REFINEMENT_RESULT_REQUIRES_EXPLICIT_CHECK_BOUNDARY` | `checker` | `error` | `active` | Use an explicit check/factory boundary for Result-bearing refinement validation. |
| `REFINEMENT_THIS_CAPTURE_FORBIDDEN` | `checker` | `error` | `active` | \`this\` in a refinement predicate is not an ordinary capturable variable. |
| `REFUTABLE_PATTERN_IN_IRREFUTABLE_CONTEXT` | `checker` | `error` | `active` | This context requires the checker to prove the Pattern irrefutable for its admitted subject type. |
| `REFUTABLE_PATTERN_REQUIRES_ELSE` | `checker` | `error` | `seed` | Refutable pattern binding requires an explicit else block that owns the failure path. |
| `REJECTED_REVIEW_FIXTURE_EXPECTED_FAILURE` | `checker` | `error` | `seed` | This review-seed reject example is expected to fail under the current Deeplus source rules; a more specific diagnostic should replace this seed before product conformance certification. |
| `REPEATED_POSITIONAL_PARAMETER_NOT_LAST_BEFORE_NAMED_REST` | `checker` | `error` | `active` | A repeated positional parameter must appear after ordinary positional parameters and before the optional named rest parameter. |
| `RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT` | `checker` | `error` | `active` | Stable Resource inheritance requires a same-module sealed root and explicit cleanup budget. |
| `RESPONSIBILITY_KIND_NOT_CLOSED` | `checker` | `error` | `active` | The descriptor does not inhabit exactly one admitted responsibility kind or mixes independent kind axes. |
| `REST_ARGUMENTS_REQUIRE_COMMON_ELEMENT_TYPE` | `checker` | `error` | `active` | Repeated positional arguments must have a common element type unless an explicit union feature is admitted. |
| `REST_ARGUMENTS_REQUIRE_EXPLICIT_UNION_FEATURE` | `checker` | `error` | `active` | Repeated and named-rest arguments must satisfy the current row type and position rules. |
| `RESULT_AND_THROWS_DUPLICATE_ERROR_CHANNEL` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `RESULT_ERRORSET_KIND_REQUIRED` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `RESULT_ERROR_ARGUMENT_POSITION_INVALID` | `checker` | `error` | `active` | The \`error E\` type argument is admitted only in an error-channel parameter position such as Result<T, error E>. |
| `RESULT_ERROR_ROLE_REQUIRED` | `checker` | `error` | `active` | A Result use site must mark its error-channel argument explicitly as \`Result<T, error E>\`. |
| `RESULT_THROWS_AUTOCONVERSION_FORBIDDEN` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `RESULT_THROWS_CHANNEL_OVERLAP` | `checker` | `error` | `active` | The same recoverable error family cannot be exposed through both Result and throws for one operation. |
| `RETURN_NOT_ALLOWED_IN_LAMBDA` | `checker` | `error` | `active` | return is for named functions; lambda blocks use ret. |
| `RETURN_TYPE_DIRECTED_OPERATOR_RESOLUTION_FORBIDDEN` | `checker` | `error` | `active` | The expected result type cannot create, distinguish, or rank a fixed-operator conformance candidate. |
| `RET_OUTSIDE_LAMBDA` | `checker` | `error` | `active` | \`ret\` is a local-result terminator only in a lambda block, a value match arm or declarative value-clause arm, or an \`@if\`/\`@try\`/\`@scope\` local-value block; it is not a named-function return. |
| `RIGHTWARD_BINDING_SEMANTIC_NODE_FORBIDDEN` | `design_static` | `error` | `active` | Rightward local binding must normalize to an ordinary local binding before semantic AST/HIR and MIR. |
| `RIGHTWARD_FLOW_DOLLAR_LOCAL_BINDING_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SANITY_RECALCULATION_MISMATCH` | `design_static` | `error` | `active` | Sanity artifact count/line/byte fields must match the package produced on disk. |
| `SCHEMA_CONSTRUCTION_CANNOT_BYPASS_CONSTRUCTOR` | `checker` | `error` | `active` | \`Type${...}\` is typed schema construction and cannot bypass constructor-domain initialization or invariants. |
| `SCHEMA_CONSTRUCTION_CANNOT_INVOKE_CONSTRUCTOR` | `checker` | `error` | `active` | Type${...} is schema construction and does not invoke constructor-domain def! bodies. Use Type!(...) or Type!name(...) for construction. |
| `SCHEMA_CONSTRUCTION_FIELD_NOT_IN_SCHEMA` | `checker` | `error` | `active` | A Type${...} entry names a field that is not part of the visible schema. |
| `SCHEMA_CONSTRUCTION_PRIVATE_FIELD_FORBIDDEN` | `checker` | `error` | `active` | Type${...} cannot initialize a private or inaccessible schema field. |
| `SCHEMA_CONSTRUCTION_REQUIRED_FIELD_MISSING` | `checker` | `error` | `active` | A required schema entry is missing from Type${...}. |
| `SCHEMA_CONSTRUCTION_RESOURCE_INITIALIZER_FORBIDDEN` | `checker` | `error` | `active` | Type${...} cannot construct resource/cleanup-bearing state unless the type exposes explicit schema authority. |
| `SCHEMA_ENTRY_SEPARATOR_REQUIRED` | `checker` | `error` | `active` | Same-line schema construction entries require comma; multi-line entries may use LayoutEntrySep when unambiguous. |
| `SCHEMA_PROJECTION_ROW_REQUIRED` | `checker` | `error` | `active` | Named unfolding requires a visible ProjectionRow for the schema value in this scope. |
| `SCOPED_ACTIVATION_REQUIRES_IN_BLOCK` | `parser` | `error` | `active` | A scoped import/use group must be followed by \`in\` and a block. |
| `SCOPED_ACTIVATION_SPEC_DUPLICATE` | `checker` | `error` | `active` | A scoped activation group contains the same normalized spec more than once. |
| `SCOPED_CALLABLE_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | A #scoped callable cannot be stored, returned, captured by an escaping continuation, or transferred to task/actor state. |
| `SCOPED_CALLBACK_BORROW_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | #scoped callback borrow evidence cannot escape the receiving invocation region. |
| `SCOPED_EXTENSION_ACTIVATION_AMBIGUOUS` | `checker` | `error` | `active` | The active extension sets contain equally applicable selectors; nesting depth is not a priority. |
| `SCOPED_EXTENSION_USE_ORDER_IS_NOT_PRIORITY` | `checker` | `error` | `active` | Scoped extension activation is lexical; use order is not a priority or tie-breaker. |
| `SCOPED_IMPORT_BLOCK_IS_STATEMENT_ONLY` | `parser` | `error` | `active` | A scoped import block is a statement and cannot produce a value. |
| `SCOPED_IMPORT_BLOCK_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SCOPED_USE_BLOCK_IS_STATEMENT_ONLY` | `parser` | `error` | `active` | A scoped use block is a statement and cannot produce a value. |
| `SCRIPT_FILE_IS_NOT_LIBRARY_IMPORT` | `checker` | `error` | `active` | A selected script unit is not an importable library computation; move reusable declarations to a library source. |
| `SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT` | `parser` | `error` | `active` | A script source file cannot contain an explicit entry declaration; choose the executable root for an explicit entry. |
| `SEALED_DIRECT_SUBCLASS_DISPOSITION_REQUIRED` | `checker` | `error` | `active` | A direct subclass of a sealed root must explicitly choose final, open, or sealed class. |
| `SEALED_DIRECT_SUBCLASS_OUTSIDE_MODULE` | `checker` | `error` | `active` | A direct subclass of sealed class must be declared in the sealed root's module. |
| `SEALED_PREFIX_SPELLING_REMOVED` | `parser` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SELF_BANG_CONSTRUCTOR_DELEGATION_REMOVED_USE_HEADER_DELEGATION` | `checker` | `error` | `active` | Body-level \`self!(...)\` constructor delegation is not current source; use header delegation such as \`: new(...)\`. |
| `SELF_UNAVAILABLE_IN_TYPE_SIDE_MEMBER` | `checker` | `error` | `active` | Type-side members declared with :: do not receive self. |
| `SEQUENCE_REQUIRES_REPLAY_ITEM` | `checker` | `error` | `active` | Replayable sequence item must be Plain-admissible or an approved reusable handle. |
| `SEQUENCE_UNFOLD_REQUIRES_STATIC_ARITY_FOR_FIXED_PARAMETERS` | `checker` | `error` | `active` | \`*sequence\` cannot target fixed parameters unless static arity evidence is known. |
| `SEQUENTIAL_BOOLEAN_OPERAND_NOT_BOOL` | `checker` | `error` | `active` | \`and then\`/\`otherwise\` require Bool operands. |
| `SETTER_VISIBILITY_CANNOT_EXCEED_GETTER` | `checker` | `error` | `active` | Setter visibility cannot exceed getter visibility. |
| `SET_HASH_BRACE_LITERAL_REMOVED_USE_HASH_SET` | `parser` | `error` | `active` | #{...} set literal is removed; use #set{...}. |
| `SHAPED_LITERAL_EMPTY_ELEMENT` | `checker` | `error` | `active` | A shaped literal semicolon body must not contain an empty element. |
| `SHAPED_LITERAL_EMPTY_SEGMENT` | `checker` | `error` | `active` | A shaped literal semicolon body must not contain an empty row/layer segment. |
| `SHAPED_LITERAL_MIXED_NESTED_AND_SEMICOLON_FORBIDDEN` | `checker` | `error` | `active` | Explicit nested shaped initializer syntax and semicolon shaped body syntax cannot be mixed in the current profile MSP. |
| `SHAPED_LITERAL_SEMICOLON_REQUIRES_EXACT_SHAPE` | `checker` | `error` | `active` | Semicolon shaped literal body separators are only admitted inside exact-shape \`#StaticDimList[...]\` NumericArray literals. |
| `SHAPED_LITERAL_SEPARATOR_RANK_MISMATCH` | `checker` | `error` | `active` | A semicolon run of length k in an exact-shape NumericArray literal must close exactly k completed inner axes, with 1 <= k < rank; a trailing run must be rank - 1. |
| `SHAPE_CONTEXT_ADAPTATION_FAILED` | `checker` | `error` | `active` | Operand cannot be adapted to the anchor shape context. |
| `SHAREABLE_DOES_NOT_CREATE_ALIAS` | `checker` | `note` | `active` | Shareable proves alias observation safety, not alias creation. Use Shared<T> or another admitted shared owner to create aliases. |
| `SHARED_CELL_REQUIRES_PLAIN_PAYLOAD` | `checker` | `error` | `active` | SharedCell<T> requires normalized Plain payload responsibility; Plain does not imply raw or lock-free representation. |
| `SHARED_MUTEX_REENTRANT_LOCK_FORBIDDEN` | `checker` | `error` | `active` | The current SharedMutex profile is non-reentrant; an owner cannot acquire the same mutex while its scoped lock is active. |
| `SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD` | `checker` | `error` | `active` | Minimum SharedMutex<T> cannot hide lifecycle or effectful cleanup owner. |
| `SHARED_REJECTS_DROPPING_PAYLOAD` | `checker` | `error` | `active` | Minimum Shared<T> cannot own payload with user-visible cleanup. |
| `SHARED_STATE_SCOPED_ACCESS_MAY_NOT_SUSPEND` | `checker` | `error` | `active` | A SharedCell observation or SharedMutex exclusive-access closure cannot suspend or escape its scoped access. |
| `SHARED_WRAPPER_DOES_NOT_IMPLY_TRANSFERABLE` | `checker` | `error` | `active` | Shared, SharedCell, and SharedMutex wrappers do not synthesize Transferable evidence for their payload. |
| `SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN` | `checker` | `error` | `active` | NumericArray sharp-shape value literal must contain at least one element in the size-inferred or explicit-shape value form. |
| `SHEBANG_MUST_BE_FIRST_LINE` | `checker` | `error` | `active` | Shebang \`#!\` is allowed only at the first line before any other source text. |
| `SHEBANG_ONLY_ONE_ALLOWED` | `checker` | `error` | `active` | Only one shebang comment is allowed in a Deeplus source file. |
| `SLICE_ANCHOR_OUTSIDE_SLICE` | `parser` | `error` | `active` | Slice anchors ^ and $ are valid only in slice-axis index context. |
| `SLICE_AXIS_COUNT_MISMATCH` | `checker` | `error` | `active` | Slice axis count must match source rank. |
| `SLICE_BOUND_ORDER_INVALID` | `checker` | `error` | `active` | Slice lower bound must not exceed upper bound for increasing ranges. |
| `SLICE_BOUND_OUT_OF_RANGE_STATIC` | `checker` | `error` | `active` | Static slice bound is outside the source logical domain. |
| `SLICE_EMPTY_RANGE_FORBIDDEN_USE_STAR` | `parser` | `error` | `active` | A slice range requires both bounds; use ^/$ for endpoints, or * for an admitted NumericArray full axis. |
| `SLICE_EXPLICIT_STRIDE_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SLICE_FIRST_ANCHOR_OFFSET_REQUIRES_INTEGER` | `checker` | `error` | `active` | Offset from ^ must be an integer index expression. |
| `SLICE_HALF_OPEN_RANGE_NONCANONICAL` | `checker` | `warning` | `active` | \`i..<j\` is accepted for explicit exclusive-end slices but is noncanonical in ordinary cases. |
| `SLICE_LAST_ANCHOR_OFFSET_REQUIRES_INTEGER` | `checker` | `error` | `active` | Offset from $ must be an integer index expression. |
| `SLICE_LAST_INDEX_DOLLAR_OUTSIDE_SLICE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SLICE_LOGICAL_DOMAIN_REBASE_FORBIDDEN` | `checker` | `error` | `active` | A slice preserves selected logical coordinates; call an explicit rebase operation if new coordinates are required. |
| `SLICE_MUTABLE_ALIAS_CONFLICT` | `checker` | `error` | `active` | Mutable slice would create an aliasing conflict. |
| `SLICE_MUTABLE_ASSIGNMENT_UNSUPPORTED` | `checker` | `error` | `active` | Mutable slice assignment is not admitted in Phase A. |
| `SLICE_RANGE_REVERSED_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SLICE_RESULT_NONCONTIGUOUS_REQUIRES_EXPLICIT_COPY_FOR_BYTE_VIEW` | `checker` | `error` | `active` | Non-contiguous slice view requires explicit copy for byte-view/contiguous storage. |
| `SLICE_REVERSE_RANGE_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SLICE_SOURCE_REQUIRES_NUMERIC_ARRAY` | `checker` | `error` | `active` | Multi-axis slicing Phase A is NumericArray-only. |
| `SLICE_VIEW_CROSSES_ISOLATION_WITHOUT_OWNED_COPY` | `checker` | `error` | `active` | A slice view cannot cross isolation without an explicit owned copy. |
| `SLICE_VIEW_ESCAPES_OWNER` | `checker` | `error` | `active` | A slice view cannot outlive its source owner region. |
| `SLICE_VIEW_REQUIRES_SHARED_SOURCE_PROFILE` | `checker` | `error` | `active` | Escaping read-only view requires a future Shared-source profile. |
| `SMOKE_CORPUS_EXPECTATION_MISMATCH` | `design_static` | `error` | `active` | SMOKE_CORPUS_EXPECTATION_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `SMOKE_EXPECTED_OUTCOME_REQUIRED` | `design_static` | `error` | `active` | SMOKE_EXPECTED_OUTCOME_REQUIRED: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `SOFT_UNION_INFERENCE_FORBIDDEN` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `SOME_TRAIT_OPAQUE_RESULT_PREVIEW_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SOME_TRAIT_OPAQUE_RESULT_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SOURCE_LEVEL_CONTEXT_ROLE_FORBIDDEN` | `checker` | `error` | `active` | ContextRole is checker-internal evidence, not a source trait. |
| `SOURCE_LEVEL_UNIT_WITNESS_FORBIDDEN` | `checker` | `error` | `active` | UnitWitness is checker-internal evidence, not a user-implementable source trait. |
| `SOURCE_ROLE_CARRIER_CONFLICT` | `parser` | `error` | `active` | A normalized project-relative path occurs more than once, or the manifest and external carrier assign different source roles to one file. |
| `SOURCE_ROLE_ENTRY_COUNT_MISMATCH` | `parser` | `error` | `active` | The parser's explicit entry-declaration count must equal the source front end's selected entry-target count for the same normalized source root. |
| `SOURCE_TRAILING_TOKENS` | `parser` | `error` | `active` | The selected source root did not consume all input. |
| `SOURCE_TRUTH_PROJECTION_CONFLICT` | `design_static` | `error` | `active` | Spec text, Markdown projection, and machine registry disagree about which artifact is the canonical source for registry rows. |
| `SPECIALIZATION_NOT_CURRENT` | `checker` | `error` | `active` | Conformance specialization remains Preview-design and is not current Stable source. |
| `SPEC_PROJECTION_COUNT_DRIFT` | `design_static` | `error` | `active` | Spec projection counts must match machine registry counts. |
| `STABLE_EBNF_NONACTIVATABLE_HELPER_LEAK` | `design_static` | `error` | `active` | STABLE_EBNF_NONACTIVATABLE_HELPER_LEAK: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `STABLE_EBNF_PREVIEW_LEAK` | `checker` | `error` | `seed` | The integrated Grammar Stable profile must not admit Preview-only alternatives. |
| `STABLE_FEATURE_PREVIEW_GATE_ANNOTATION_FORBIDDEN_R48` | `design_static` | `error` | `active` | Stable design features must not be documented with \`@feature(..., preview)\` in current-accept examples. |
| `STABLE_GRAMMAR_PREVIEW_SURFACE_LEAK` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `STABLE_GRAMMAR_PROFILE_STATUS_DRIFT` | `design_static` | `error` | `active` | STABLE_GRAMMAR_PROFILE_STATUS_DRIFT: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `STABLE_GRAMMAR_REQUIRES_PROFILE_AWARE_REFERENCES` | `design_static` | `error` | `active` | STABLE_GRAMMAR_REQUIRES_PROFILE_AWARE_REFERENCES: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `STABLE_MEMBER_EXTENSION_COLLISION` | `checker` | `error` | `active` | Member/extension collision is a stable hard error in the current profile. |
| `STANDALONE_BANG_NOT_CURRENT` | `parser` | `error` | `active` | Standalone \`!expr\` is not current Deeplus Boolean negation; use \`not expr\`. |
| `STATIC_ACTIVATION_SCOPE_NOT_RESOLVED` | `checker` | `error` | `seed` | Static activation must resolve without import/use order tie-breaks. |
| `STATIC_ALIAS_CONFLICTS_WITH_LOCAL_BINDING` | `checker` | `error` | `active` | Static alias conflicts with an existing local binding. |
| `STATIC_CALL_SHAPE_NOT_ADMITTED` | `checker` | `error` | `active` | The normalized call shape has a duplicate/unknown label, ambiguous ordering, or conflicting rest residue. |
| `STATIC_CLASS_DECLARATION_NOT_CURRENT` | `parser` | `error` | `active` | Top-level \`static class\` has no current Deeplus declaration route. |
| `STATIC_EVIDENCE_SELECTOR_ESCAPE_FORBIDDEN` | `checker` | `error` | `active` | Static evidence cannot be stored, returned, captured, escaped or selected dynamically. |
| `STATIC_EVIDENCE_SELECTOR_NOT_FOUND` | `checker` | `error` | `active` | The named static evidence selector is not visible for this type and Trait. |
| `STATIC_EVIDENCE_SELECTOR_REQUIRES_PREVIEW` | `parser` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `STATIC_EXPR_HAS_EFFECT` | `checker` | `error` | `seed` | Static expression cannot perform effects. |
| `STATIC_EXPR_NOT_CONST` | `checker` | `error` | `seed` | Static expression is outside the Phase A deterministic static evaluator. |
| `STATIC_FUNCTION_DECLARATION_NOT_CURRENT` | `parser` | `error` | `active` | Top-level \`static def\` has no current Deeplus declaration route. |
| `STATIC_INT_ARITHMETIC_OUT_OF_R0_PROFILE` | `checker` | `error` | `active` | StaticInt expression is outside the R0 static evaluator profile. |
| `STATIC_INT_REQUIRES_COMPILE_TIME_LITERAL_OR_PROVEN_STATIC_VALUE` | `checker` | `error` | `active` | StaticInt requires a compile-time known integer. |
| `STATIC_R0_EVALUATOR_NOT_SOURCE_FEATURE` | `checker` | `error` | `active` | R0 static evaluator is checker-internal and cannot be invoked as ordinary source code. |
| `STATIC_RANGE_HALF_OPEN_TYPE_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `STATIC_SELECTOR_RESOLUTION_FAILED` | `checker` | `error` | `active` | The qualified \`::\` selector resolves to neither an enum case, type-side member, nor qualified extension selector. |
| `STATIC_SPELLING_REMOVED_USE_COLON_COLON` | `parser` | `error` | `active` | def#static/def#class spelling is removed; use def::. |
| `STATUS_ENUM_DECLARATION_DRIFT` | `checker` | `error` | `seed` | Declared status enum projection does not match registry/sanity. |
| `STDLIB_PROFILE_NOT_CORE_SYNTAX` | `parser` | `error` | `seed` | stdlib feature is not ordinary source syntax in R49. |
| `STEPPED_RANGE_TYPE_REQUIRES_PREVIEW_DESIGN` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `STRICT_BOOLEAN_OPERAND_NOT_BOOL` | `checker` | `error` | `active` | \`and\`/\`or\` require Bool operands. |
| `STRING_INTERPOLATION_FORMAT_SPEC_CORE_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `STRING_INTERPOLATION_SHORTHAND_FACTOR_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `STRING_LITERAL_NOT_ASSIGNABLE_TO_CHAR` | `checker` | `error` | `active` | String is not implicitly assignable to Char. |
| `STRING_MIXIN_NOT_SUPPORTED` | `checker` | `error` | `active` | String mixins are not supported in core Deeplus. |
| `STRING_NORMALIZATION_IS_EXPLICIT` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `STRING_NOT_IMPLICITLY_CONVERTIBLE_TO_BYTES` | `checker` | `error` | `active` | String is not implicitly convertible to Bytes. |
| `STRING_RENDERER_MUST_RETURN_STRING` | `checker` | `error` | `active` | String::render requires its trailing renderer closure to return String. |
| `STRUCTURAL_CONFORMANCE_FORBIDDEN` | `checker` | `error` | `active` | Structural method matching does not create conformance. |
| `STRUCTURAL_CONFORMANCE_NOT_CURRENT` | `checker` | `error` | `active` | The surface \`structural conformance\` is recognized but is not current Deeplus. |
| `STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN` | `checker` | `error` | `active` | Structural shape coincidence does not form stable conformance. |
| `STRUCTURAL_PROTOTYPE_EXTENSION_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | Feature \`structural_prototype_extension\` is PREVIEW_DESIGN/nonactivatable and has no current source gate. |
| `STRUCTURED_BREAK_CHAIN_CANONICAL_FORM_REQUIRED` | `checker` | `error` | `active` | Structured break-chain uses chain spelling such as \`break break\` or \`break break continue\`; label/depth target forms are not the current profile canonical stable spelling. |
| `STRUCTURED_BREAK_TARGET_AMBIGUOUS` | `checker` | `error` | `active` | Structured break/continue target is ambiguous; use a visible loop label or an unambiguous outer-loop depth. |
| `STRUCTURED_LOOP_CONTROL_INVALID_CHAIN` | `checker` | `error` | `active` | Structured break-chain is invalid for the surrounding loop nesting. |
| `STRUCTURED_TASK_SCOPE_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `SUPER_DELEGATION_MUST_BE_IN_CONSTRUCTOR_HEADER` | `checker` | `error` | `active` | \`super!\` constructor delegation must appear in the constructor header delegation clause. |
| `SUPER_DELEGATION_NOT_EXHAUSTIVE` | `checker` | `error` | `active` | Root \`new\` must call exactly one super constructor on every successful path. |
| `SUPPORT_LANE_VOCABULARY_MISMATCH` | `design_static` | `error` | `active` | SUPPORT_LANE_VOCABULARY_MISMATCH: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `SUPPORT_MARKDOWN_PROJECTION_OUT_OF_SYNC` | `design_static` | `error` | `seed` | Generated Markdown support projection does not match canonical support matrix feature ID set. |
| `SUPPORT_MATRIX_FEATURE_PARITY_DRIFT` | `design_static` | `error` | `active` | Production support matrix and feature registry have different feature ID sets or lane values. |
| `SYNC_CALLABLE_LITERAL_MARKER_NOT_CURRENT` | `parser` | `error` | `active` | #sync is redundant and not a current callable literal profile. |
| `TASK_BODY_MINIMUM_GRAMMAR_SLICE_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TASK_GROUP_CHILDREN_MUST_BE_JOINED_OR_COLLECTED` | `checker` | `error` | `seed` | A task group with spawned children must expose join/collect/implicit-join policy explicitly in this profile. |
| `TASK_GROUP_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TASK_SPAWN_BODY_REQUIRES_TASK_BODY_PROFILE` | `checker` | `error` | `seed` | Task spawn in the R49 preview slice uses TaskBody, not the general nonactivatable closure literal production. |
| `TERNARY_BRANCH_TYPE_MISMATCH` | `checker` | `error` | `active` | Ternary branch types do not have a permitted join. |
| `TERNARY_CONDITION_NOT_BOOL` | `checker` | `error` | `active` | Ternary condition must have Bool type. |
| `TERNARY_MISSING_COLON` | `checker` | `error` | `active` | Ternary expression requires a colon separating true and false arms. |
| `TERNARY_QUESTION_REQUIRES_SPACING` | `checker` | `error` | `active` | Ternary \`?\` requires separating trivia from the condition and then-expression tokens. |
| `THROWING_CLEANUP_FAILURE_POLICY_REQUIRED` | `checker` | `error` | `active` | A throwing cleanup path must preserve deterministic primary/suppressed failure order and cannot mask Cancellation as Error. |
| `THROWING_DROP_CLEANUP_FAILURE_POLICY_REQUIRED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TOKEN_PRECEDENCE_SCHEMA_PARITY_REQUIRED` | `design_static` | `error` | `active` | The integrated Grammar, Frontend Model Pratt registry, lifecycle and current corpus must agree. |
| `TOOLING_FEATURE_NOT_SOURCE` | `checker` | `error` | `seed` | tooling feature is not ordinary source syntax in R49. |
| `TOP_LEVEL_AWAIT_NOT_CURRENT` | `checker` | `error` | `active` | Top-level \`await\` is not admitted by the Stable script profile; use \`def#entry#async\`. |
| `TOP_LEVEL_BINDING_NOT_ALLOWED_IN_EXECUTABLE_SOURCE` | `parser` | `error` | `active` | Executable source files do not admit top-level let/var bindings; initialize state inside the selected entry. |
| `TOP_LEVEL_RETURN_NOT_ALLOWED` | `checker` | `error` | `active` | Top-level script computation cannot return; use an explicit entry function or process API. |
| `TOP_LEVEL_STATEMENT_REQUIRES_SCRIPT_ROOT` | `parser` | `error` | `active` | A top-level executable statement is admitted only by the selected script root; library and executable roots reject it. |
| `TRAILING_CLOSURE_ARGUMENT_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRAILING_CLOSURE_DEFAULT_SKIP_FORBIDDEN` | `checker` | `error` | `active` | Trailing closure syntax cannot skip defaulted parameters in Phase A. |
| `TRAILING_CLOSURE_DOES_NOT_RELAX_CAPTURE_RULES` | `checker` | `error` | `active` | Trailing closure syntax does not relax capture, ownership, borrow, effect, throw, actor, or cleanup rules. |
| `TRAILING_CLOSURE_OVERLOAD_AMBIGUOUS` | `checker` | `error` | `active` | Trailing closure call is overload-ambiguous; return type or source order must not select the overload. |
| `TRAILING_CLOSURE_REQUIRES_FUNCTION_PARAMETER` | `checker` | `error` | `active` | A trailing closure must bind to a corresponding closure/function-typed parameter. |
| `TRAILING_CLOSURE_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRAILING_CLOSURE_SUFFIX_REQUIRED` | `parser` | `error` | `active` | Trailing closures bind only to a suffix of formal closure parameters. |
| `TRAIT_AMBIGUOUS_IMPORTED_WITNESS` | `checker` | `error` | `active` | Multiple visible canonical witnesses satisfy the same conformance obligation. |
| `TRAIT_ASSOCIATED_ITEM_DISPATCH_MARKER_FORBIDDEN` | `parser` | `error` | `active` | A non-method associated requirement cannot carry a Trait witness marker. |
| `TRAIT_ASSOCIATED_ITEM_MARKER_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRAIT_ASSOCIATED_PROJECTION_AMBIGUOUS` | `checker` | `error` | `active` | Associated projection is ambiguous without a trait witness context. |
| `TRAIT_ASSOCIATED_PROJECTION_REQUIRES_TRAIT_CONTEXT` | `checker` | `error` | `active` | Associated projection requires an explicit witness/static trait context: write \`<T as Trait>::Assoc\`. |
| `TRAIT_ASSOCIATED_PROJECTION_USES_COLON_COLON` | `checker` | `error` | `active` | Associated projection is a witness/static projection and uses \`::\`: write \`<T as Trait>::Assoc\`. |
| `TRAIT_ASSOCIATED_REQUIREMENT_MISSING` | `checker` | `error` | `active` | Conformance body does not bind a required associated item. |
| `TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE` | `verifier` | `error` | `active` | Trait-associated static HIR/API residue is missing a required requirement, conformance, witness, implementation, substitution, or responsibility identity. |
| `TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH` | `checker` | `error` | `active` | The selected Trait-associated item kind does not match the type or expression goal. |
| `TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND` | `checker` | `error` | `active` | The explicitly qualified Trait has no associated item with this identity. |
| `TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION` | `checker` | `error` | `active` | Trait-associated static selection must use <T as Trait>::item. |
| `TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN` | `verifier` | `error` | `active` | Trait-associated static selection is resolved before execution and cannot perform runtime lookup or fallback. |
| `TRAIT_ASSOCIATED_TYPE_CONSTRAINT_UNSATISFIED` | `checker` | `error` | `active` | Associated type equality constraint is not satisfied by the selected witness. |
| `TRAIT_ASSOCIATED_TYPE_CYCLE` | `checker` | `error` | `active` | Associated type binding forms a cycle. |
| `TRAIT_BODYLESS_FINAL_REQUIREMENT_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRAIT_FINAL_SLOT_CANNOT_BE_OVERRIDDEN` | `checker` | `error` | `active` | A final trait witness slot cannot be overridden by a child trait or conformance. |
| `TRAIT_FINAL_SLOT_CONFLICT` | `checker` | `error` | `active` | Distinct inherited final trait witness slots conflict in the same conformance surface. |
| `TRAIT_FINAL_WITNESS_NOT_EFFECTIVELY_FINAL` | `checker` | `error` | `active` | A final trait witness requirement must be satisfied by an effectively final concrete witness. |
| `TRAIT_LAW_PROPERTY_TEST_RECEIPT_MISSING` | `design_static` | `error` | `active` | TRAIT_LAW_PROPERTY_TEST_RECEIPT_MISSING: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `TRAIT_MARKER_FAMILY_MISMATCH_WITH_CURRENT_DISPATCH_MARKER` | `checker` | `error` | `active` | Trait marker surface conflicts with the current dispatch marker family. |
| `TRAIT_METHOD_AUTHORITY_TOO_WIDE` | `checker` | `error` | `active` | Witness method authority requirement is wider than the trait requirement allows. |
| `TRAIT_METHOD_DUPLICATE_SLOT` | `checker` | `error` | `active` | Trait declares the same witness slot more than once. |
| `TRAIT_METHOD_EFFECT_TOO_WIDE` | `checker` | `error` | `active` | Witness method effect row is wider than the trait requirement allows. |
| `TRAIT_METHOD_ERRORSET_TOO_WIDE` | `checker` | `error` | `active` | Witness method ErrorSet is wider than the trait requirement allows. |
| `TRAIT_METHOD_ISOLATION_MISMATCH` | `checker` | `error` | `active` | Witness method isolation responsibility does not match the trait requirement. |
| `TRAIT_METHOD_MARKER_MUST_BE_ATTACHED` | `checker` | `error` | `active` | Trait method marker must be attached to the method selector with no whitespace/comment/newline gap. |
| `TRAIT_METHOD_MARKER_NOT_OVERLOAD_KEY` | `checker` | `error` | `active` | Trait method markers are declaration metadata, not overload keys; marker-only duplicates are not allowed. |
| `TRAIT_METHOD_MARKER_REQUIRED` | `checker` | `error` | `active` | Trait method declarations must carry a witness slot marker (\`.\`, \`+\`, \`*.\`, or \`*+\`). |
| `TRAIT_METHOD_RECEIVER_MODE_MISMATCH` | `checker` | `error` | `active` | Witness method receiver mode is incompatible with the trait requirement. |
| `TRAIT_METHOD_SUSPENSION_MISMATCH` | `checker` | `error` | `active` | Witness method suspension responsibility does not match the trait requirement. |
| `TRAIT_METHOD_VIEW_ESCAPES_OWNER` | `checker` | `error` | `active` | Witness method returns a view that can escape the owner region without the required region exposure. |
| `TRAIT_MISSING_WITNESS` | `checker` | `error` | `active` | cannot prove \`{type} conforms {trait}\`. |
| `TRAIT_NOT_EXISTENTIAL_SAFE` | `checker` | `error` | `active` | Trait is not safe for any Trait existential packaging under the current bindings. |
| `TRAIT_OPEN_DEFAULT_CONFLICT_REQUIRES_EXPLICIT_OVERRIDE` | `checker` | `error` | `active` | Inherited open default trait witness slots conflict; add an explicit \`*+\` or \`*.\` override. |
| `TRAIT_OPERATOR_MARKER_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRAIT_OVERLAPPING_WITNESS` | `checker` | `error` | `active` | Multiple conformance declarations overlap for the same trait/type obligation. |
| `TRAIT_OVERRIDE_MARKER_REQUIRES_INHERITED_SLOT` | `checker` | `error` | `active` | \`*+\` or \`*.\` requires a compatible inherited open trait witness slot. |
| `TRAIT_OVERRIDE_SIGNATURE_INCOMPATIBLE` | `checker` | `error` | `active` | Trait witness slot override is not responsibility-compatible with the inherited slot. |
| `TRAIT_REQUIREMENT_VISIBILITY_MISMATCH` | `checker` | `error` | `active` | Witness member visibility does not satisfy the trait requirement visibility. |
| `TRAIT_SUPER_CYCLE` | `checker` | `error` | `active` | Supertrait graph contains a cycle. |
| `TRAIT_SUPER_WITNESS_MISSING` | `checker` | `error` | `active` | Selected witness does not provide a required supertrait witness. |
| `TRAIT_VARIANCE_POSITION_VIOLATION` | `checker` | `error` | `active` | Trait-only variance parameter appears in an invalid responsibility position. |
| `TRANSPOSE_INFIX_CARET_FORBIDDEN` | `checker` | `error` | `seed` | Transpose infix caret forbidden |
| `TRANSPOSE_RANK1_REQUIRES_ROW_OR_COL_VIEW` | `checker` | `error` | `seed` | Transpose rank1 requires row or col view |
| `TRIPLE_SLASH_IS_NOT_WORD_COMMENT` | `lexer` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRIPLE_STAR_NOT_ALLOWED_OUTSIDE_NAMED_REST_DECLARATION` | `lexer` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRIPLE_STAR_ONLY_FOR_NAMED_REST_PARAMETER_OR_TYPE_RESIDUE` | `parser` | `error` | `active` | Triple-star is admitted only as the attached named-rest parameter suffix or function-type named-rest residue; named unfold uses prefix \`**\`. |
| `TRUSTED_DERIVE_VIA_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TRY_EXPRESSION_STATEMENT_NOT_CURRENT` | `parser` | `error` | `active` | Statement \`try\` requires a block body; \`try Expr\` is not current Deeplus. |
| `TRY_REQUIRES_CATCH_OR_FINALLY` | `parser` | `error` | `active` | A statement \`try\` or value \`@try\` requires at least one \`catch\` clause or one \`finally\` clause. |
| `TUPLE_ORDINAL_OUT_OF_RANGE` | `checker` | `error` | `active` | The tuple ordinal exceeds the tuple arity. |
| `TUPLE_ORDINAL_ZERO_FORBIDDEN` | `checker` | `error` | `active` | Tuple ordinals are one-based; \`.0\` is not admitted. |
| `TUPLE_PATTERN_NOT_CURRENT` | `parser` | `error` | `active` | Tuple decomposition is not a current Pattern; parentheses group one Pattern only. |
| `TYPED_MATERIALIZATION_REQUIRES_CONSTRUCTION_ROW` | `checker` | `error` | `active` | Typed materialization requires a checker-certified ConstructionRow for the target type. |
| `TYPED_MATERIALIZATION_REQUIRES_TYPE_TARGET` | `checker` | `error` | `active` | The head of \`target${...}\` must resolve to a type with an admitted ConstructionRow; an ordinary expression target is not materializable. |
| `TYPED_PROVIDER_NONDETERMINISTIC_OUTPUT` | `provider` | `error` | `active` | A typed provider must produce deterministic, content-addressed output. |
| `TYPEINFO_IS_PREVIEW_META_AUTHORITY` | `checker` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `TYPEOF_CALL_FORM_FORBIDDEN` | `checker` | `error` | `active` | \`typeof(...)\` is forbidden in Phase A; write \`typeof <static-sample>\` without call-like parentheses. |
| `TYPEOF_MEASURE_UNIT_CATALOG_NOT_ACTIVE` | `checker` | `error` | `active` | Measure samples in \`typeof\` require a source-visible active UnitCatalog authority such as \`use std::units::si\`. |
| `TYPEOF_OPERATOR_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TYPEOF_OPERATOR_REQUIRES_TYPE_POSITION` | `checker` | `error` | `active` | \`typeof\` may appear only in type position, not as an expression or ordinary call. |
| `TYPEOF_PUBLIC_API_PROJECTION_REQUIRED` | `checker` | `lint` | `active` | Public API use of \`typeof\` must preserve both compact spelling and expanded contract projection. |
| `TYPEOF_SAMPLE_EFFECT_NOT_ALLOWED` | `checker` | `error` | `active` | \`typeof\` sample must not require runtime evaluation, effects, failure, provider calls, or authority execution. |
| `TYPEOF_SAMPLE_HAS_NO_PRINCIPAL_TYPE` | `checker` | `error` | `active` | \`typeof\` sample has no single principal TypeResponsibilityDescriptor. |
| `TYPEOF_SAMPLE_PROVIDER_AUTHORITY_FORBIDDEN` | `checker` | `error` | `active` | \`typeof\` samples cannot execute provider, Agent, reflection, unsafe, or FFI authority. |
| `TYPEOF_SAMPLE_REQUIRES_EXPLICIT_UNION_FEATURE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TYPEOF_SAMPLE_REQUIRES_STATIC_SAMPLE` | `checker` | `error` | `active` | \`typeof\` operand must be an admissible static sample, not a runtime expression. |
| `TYPEOF_SAMPLE_RESOURCE_FORBIDDEN` | `checker` | `error` | `active` | \`typeof\` Phase A samples cannot allocate resources, invoke constructors, or introduce cleanup responsibility. |
| `TYPEOF_STATIC_SAMPLE_TYPE_OPERATOR_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TYPE_BANG_REQUIRES_NEW_CONSTRUCTOR` | `checker` | `error` | `active` | \`Type!(...)\` resolves only to a matching \`def! new(...)\` constructor. |
| `TYPE_DATA_REMOVED_USE_EXPLICIT_BOUNDARY` | `checker` | `error` | `active` | Data is not a plain-value erasure type name. Choose Plain, Dyn, JsonValue, or a domain-specific type; no automatic fix-it is provided. |
| `TYPE_DECL_VISIBILITY_REQUIRED` | `checker` | `error` | `active` | A top-level Class, Trait, Enum, type alias, schema, actor, actor protocol, typestate resource, or bitfield must explicitly use public, common, or private visibility. |
| `TYPE_DESCRIPTOR_QUERY_RUNTIME_USE_FORBIDDEN` | `checker` | `error` | `active` | Compile-time type descriptors are not runtime reflective values. |
| `TYPE_DOLLAR_IS_NOT_CONSTRUCTOR_ALIAS` | `checker` | `error` | `active` | \`Type${...}\` is typed schema construction, not a constructor-domain call. Use \`Type!(...)\` or \`Type!name(...)\` for nominal construction. |
| `TYPE_DOLLAR_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_TYPE` | `checker` | `error` | `active` | \`Type${...}\` requires a resolved type with an admitted schema ConstructionRow and is never a constructor alias. |
| `TYPE_DOLLAR_SCHEMA_DECLARATION_REQUIRED` | `checker` | `error` | `active` | Type${...} typed schema construction requires a visible schema declaration or schema descriptor. |
| `TYPE_DOLLAR_SCHEMA_EFFECTFUL_DEFAULT_NOT_ALLOWED` | `checker` | `error` | `active` | Type${...} defaults must not hide effectful/provider evaluation. |
| `TYPE_DOLLAR_SCHEMA_FIELD_MISSING` | `checker` | `error` | `active` | Type${...} is missing a required schema field. |
| `TYPE_DOLLAR_SCHEMA_FIELD_REQUIRED` | `checker` | `error` | `active` | Typed schema construction requires all required schema fields or defaults. |
| `TYPE_DOLLAR_SCHEMA_INVARIANT_VIOLATION` | `checker` | `error` | `active` | Type${...} violates a declared schema invariant or refinement. |
| `TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD` | `checker` | `error` | `active` | Type${...} contains a label not declared by the schema descriptor. |
| `TYPE_INTERNAL_PREDICATE_NOT_SOURCE_TRAIT` | `checker` | `error` | `active` | Checker-internal predicate cannot be implemented as an ordinary source trait. |
| `TYPE_KEY_REQUIRES_COPYABLE_HASHABLE` | `checker` | `error` | `active` | Old Copyable & Hashable key law is removed; use Keyable. |
| `TYPE_KEY_REQUIRES_KEYABLE` | `checker` | `error` | `active` | Map/Set key requires Keyable admissibility. |
| `TYPE_KIND_HASH_SURFACE_REMOVED` | `checker` | `error` | `active` | Use public/private/common data/value/resource class, not class#data/class#value/class#resource. |
| `TYPE_PLAINDATA_REMOVED_USE_PLAIN` | `checker` | `error` | `active` | \`PlainData\` removed spelling; use \`Plain\` or formal \`PlainValue\`. |
| `TYPE_RELATION_SYMBOLIC_ALIAS_FORBIDDEN` | `checker` | `error` | `active` | Use derives/conforms keywords, not symbolic type relation aliases. |
| `TYPE_RESPONSIBILITY_SCHEMA_VERSION_STALE` | `design_static` | `error` | `active` | TYPE_RESPONSIBILITY_SCHEMA_VERSION_STALE: the current corpus, lifecycle, grammar, and machine authorities must agree. |
| `TYPE_SCHEMA_CONSTRUCTION_MUST_BE_SCHEMA_ONLY` | `checker` | `error` | `active` | Type${...} is typed schema construction, not nominal constructor-domain allocation or resource construction. |
| `TYPE_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_AUTHORITY` | `checker` | `error` | `active` | Type${...} requires visible schema construction authority for the target type. |
| `TYPE_SIDE_COLON_COLON_CALL_UNSUPPORTED` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `TYPE_SIDE_DISPATCH_MARKER_FORBIDDEN` | `checker` | `error` | `active` | def:: and let:: are type-side members, not instance dispatch slots; dispatch suffix markers are forbidden. |
| `TYPE_SIDE_MUTABLE_REQUIRES_EFFECT_FOOTPRINT` | `checker` | `error` | `active` | var:: access/mutation must expose its effect footprint. |
| `TYPE_SIDE_MUTABLE_REQUIRES_ISOLATION` | `checker` | `error` | `active` | var:: type-side mutable storage requires an explicit isolation law. |
| `TYPE_SIDE_MUTABLE_STORAGE_UNSUPPORTED` | `checker` | `error` | `active` | var:: is recognized but unsupported in the default Stable profile; type-side mutable storage requires a separate effect/isolation law. |
| `TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN` | `checker` | `error` | `active` | Only a type-side function declared lexically inside the nominal owner may use that owner's private construction authority. |
| `TYPE_TEST_SUBJECT_MUST_BE_CLOSED_UNION` | `checker` | `error` | `active` | The is/!is subject must have one normalized closed Union static type. |
| `TYPE_TOKEN_HAS_NO_CONSTRUCTION_AUTHORITY` | `lexer` | `error` | `active` | Type<T> token has no construction or metaclass invocation authority. |
| `TYPE_TOKEN_IS_NOT_CONSTRUCTOR` | `lexer` | `note` | `seed` | 현행 규범 위반에 대한 seed diagnostic. |
| `TYPE_TOKEN_RUNTIME_AUTHORITY_FORBIDDEN` | `checker` | `error` | `active` | A type token is compile-time identity only and cannot be used as a runtime reflective value or authority source. |
| `UNANNOTATED_NULLARY_LAMBDA_REQUIRES_PREVIEW` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `UNFOLD_DUPLICATE_LABEL` | `checker` | `error` | `active` | Unfold/comprehension produced duplicate label without an admitted policy. |
| `UNICODE_ESCAPE_INVALID_DIGIT` | `lexer` | `error` | `active` | Unicode escape contains an invalid hex digit. |
| `UNICODE_ESCAPE_OUT_OF_RANGE` | `lexer` | `error` | `active` | Unicode scalar escape is above U+10FFFF. |
| `UNICODE_ESCAPE_SURROGATE_NOT_ALLOWED` | `lexer` | `error` | `active` | Unicode scalar escape cannot encode a surrogate. |
| `UNICODE_NAMED_ESCAPE_MSP_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `UNION_ALTERNATIVES_NOT_PROVEN_DISJOINT` | `checker` | `error` | `active` | Closed Union alternatives must be proven pairwise disjoint; this pair overlaps or its relation is unknown. |
| `UNION_AUTOMATIC_JOIN_FORBIDDEN` | `checker` | `error` | `active` | Branch, return, overload, and generic inference cannot invent an anonymous union. |
| `UNION_EXPECTED_TYPE_REQUIRED_FOR_INJECTION` | `checker` | `error` | `active` | Union injection requires an independently fixed expected union type. |
| `UNION_INJECTION_AMBIGUOUS` | `checker` | `error` | `active` | The source value does not select one unique exact union alternative. |
| `UNION_MEMBER_SUBSUMED` | `checker` | `error` | `active` | Phase-A closed union members must be pairwise disjoint; a subsumed alternative is forbidden. |
| `UNION_PATTERN_ALTERNATIVE_NOT_EXACT` | `checker` | `error` | `active` | A typed pattern over a closed Union must name exactly one declared alternative identity. |
| `UNION_TYPE_TEST_ALTERNATIVE_NOT_EXACT` | `checker` | `error` | `active` | An is/!is test over a closed Union must name exactly one declared alternative identity. |
| `UNION_VALUE_REQUIRES_NARROWING` | `checker` | `error` | `active` | A union value must be narrowed before member access, call, operator use, or extraction. |
| `UNIT_BRACKET_ON_NON_LITERAL_IS_INDEXING` | `checker` | `error` | `active` | \`[unit]\` after a non-literal is indexing, not measure construction. |
| `UNIT_CONTEXT_ANCHOR_NOT_A_VALUE` | `checker` | `error` | `active` | A unit context anchor is not a first-class value. |
| `UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS` | `checker` | `error` | `active` | Unit context anchor requires a statically known unit witness. |
| `UNIT_CONVERSION_APPROXIMATE_REQUIRES_POLICY` | `checker` | `error` | `active` | Approximate unit conversion requires an explicit approximation policy. |
| `UNIT_CONVERSION_EXACT_RATIO_FORM_REQUIRED` | `checker` | `error` | `active` | Exact conversion must use an exact ratio form. |
| `UNIT_CONVERSION_GRAPH_NOT_CLOSED` | `checker` | `error` | `active` | Unit conversion graph must be deterministic and closed for admitted static conversions. |
| `UNIT_DECLARATION_DIMENSION_MISMATCH` | `checker` | `error` | `active` | Unit declaration conversion target has a dimension mismatch. |
| `UNIT_DIMENSION_CANONICALIZATION_FAILED` | `checker` | `error` | `active` | The unit expression cannot be normalized to an exact dimension vector and rational scale under the Stable unit core. |
| `UNIT_EXPONENT_REQUIRES_STATIC_INT` | `parser` | `error` | `active` | A unit exponent must be a signed decimal StaticInt literal; a runtime expression, radix literal, suffixed integer, decimal point, or exponent-form number is not admitted. |
| `UNIT_EXPR_REQUIRES_UNIT_NAMESPACE` | `checker` | `error` | `active` | Unit brackets contain only unit symbols, catalog qualifiers, powers, products, and divisions. |
| `UNIT_LITERAL_BRACKET_MUST_BE_ATTACHED` | `checker` | `error` | `active` | No whitespace is allowed between numeric literal and unit bracket. |
| `UNIT_MIDDLE_DOT_RECOVERY_ONLY` | `parser` | `error` | `active` | Unit multiplication uses \`*\`; the middle dot is recognized only for recovery. |
| `UNIT_MULTIPLICATION_USE_STAR` | `parser` | `error` | `active` | The current unit multiplication spelling is \`*\`; the middle dot is recovery-only. |
| `UNIT_PROVIDER_REQUIRES_UNIT_WITNESS_CARRIER` | `checker` | `error` | `active` | Provider endpoints must use unit witness carriers such as \`1[USD]\`. |
| `UNIT_SYMBOL_NOT_ACTIVE` | `checker` | `error` | `active` | Unit symbol is known but no active catalog authority is in scope. Use the catalog, do not merely import it. |
| `UNIT_TYPE_IS_UNIT_NOT_NONE` | `checker` | `note` | `seed` | The unit return type is \`Unit\`. \`None\` is the Option case expression, not the unit type. |
| `UNIT_WITNESS_LITERAL_MUST_BE_ONE` | `checker` | `error` | `active` | Unit witness argument must be \`1[unit]\`. |
| `UNKNOWN_NUMERIC_LITERAL_SUFFIX` | `lexer` | `error` | `active` | Unknown numeric literal suffix; use the closed integer or float suffix table. |
| `UNKNOWN_PREFIXED_LITERAL` | `checker` | `error` | `active` | Unknown #prefix literal; current prefixed literal families are #map, #set, #mut, #raw, and #bytes. |
| `UNKNOWN_UNIT_SYMBOL` | `checker` | `error` | `active` | Unit symbol cannot be resolved in active unit catalogs. |
| `UNSAFE_AUTHORITY_NOT_EFFECT` | `checker` | `error` | `active` | Unsafe authority must not be hidden as an ordinary runtime effect. |
| `UNSAFE_BOUNDARY_GRAMMAR_REQUIRED` | `parser` | `error` | `seed` | Unsafe boundary prose/examples require an explicit \`unsafe Block\` grammar projection and crosswalk row. |
| `UNSAFE_REQUIRES_UNSAFE_BOUNDARY` | `checker` | `error` | `active` | Raw pointer, FFI, provider, or agent authority requires an explicit unsafe/authority boundary. |
| `UNSUPPORTED_FEATURE_ACCEPT_EXAMPLE_FORBIDDEN_R48` | `design_static` | `error` | `active` | Recognized-unsupported features may appear only in rejected/negative examples with deterministic diagnostics. |
| `USE_SITE_VARIANCE_NOT_SUPPORTED_IN_PHASE_A` | `checker` | `error` | `active` | Use-site generic projection is not supported in the current profile. |
| `VALUELESS_BREAK_MATCHED_AS_COMPLETED` | `checker` | `error` | `active` | A valueless break is ::break(()), not ::completed. |
| `VARIANCE_NOT_SUPPORTED_FOR_ERRORSET_OR_EFFECTROW` | `checker` | `error` | `active` | ErrorSet and EffectRow parameters use row inclusion, not generic type variance. |
| `VARIANCE_ONLY_ALLOWED_ON_TRAIT_TYPE_PARAMETER` | `checker` | `error` | `active` | the current profile Phase B generic variance is allowed only on trait/interface/view/function-like parameters. |
| `VAR_COLON_COLON_NOT_CURRENT` | `checker` | `error` | `active` | var:: type-side mutable storage is not admitted in the clean current source profile; use explicit ordinary ownership, isolation, and effect responsibility. |
| `VECTOR_DOT_PRODUCT_REQUIRES_RANK1_EQUAL_LENGTH` | `design_static` | `error` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `VIEW_CROSSES_ACTOR_BOUNDARY` | `checker` | `error` | `seed` | Region-bound view cannot cross an actor isolation boundary without an owned Transferable value or shared handle law. |
| `VIEW_CROSSES_TASK_BOUNDARY` | `checker` | `error` | `seed` | Region-bound view cannot cross a task boundary without an owned Transferable value or shared handle law. |
| `WEAK_ATOMIC_ORDERING_REQUIRES_FEATURE_GATE` | `parser` | `error` | `active` | Feature \`weak_atomic_ordering\` is PREVIEW_DESIGN/nonactivatable and has no current source gate. |
| `WHERE_CLAUSE_PRIVATE_TYPE_LEAK` | `checker` | `error` | `seed` | Where-clause constraint leaks a private type through a public API. |
| `WHERE_COLON_RELATION_AMBIGUOUS` | `parser` | `error` | `active` | \`where T : U\` is ambiguous in the current profile. Use \`where T conforms Trait\` for conformance or an explicit future subtype-bound relation. |
| `WHERE_COLON_TRAIT_CONSTRAINT_NOT_CURRENT` | `parser` | `error` | `active` | The surface \`where T : Trait\` is recognized but is not current Deeplus. |
| `WITNESS_COHERENCE_EVIDENCE_MISSING` | `checker` | `error` | `active` | Witness coherence requires a witness id, selected implementation id, coherence key, and at least one candidate implementation before selection. |
| `WITNESS_DUPLICATE_IN_COHERENCE_DOMAIN` | `checker` | `error` | `active` | Multiple active witnesses exist for the same type/trait pair in one coherence domain. |
| `WITNESS_IMPLEMENTATION_SELECTION_MISMATCH` | `checker` | `error` | `active` | The coherence key must equal the witness id and the sole selected candidate must equal the implementation id. |
| `WITNESS_ORPHAN_RULE_VIOLATION` | `checker` | `error` | `active` | Witness declaration violates the trait/type ownership rule. |
| `WITNESS_REQUIREMENT_MISSING` | `checker` | `error` | `seed` | Witness does not satisfy a required trait member. |
| `WITNESS_REQUIREMENT_SIGNATURE_MISMATCH` | `checker` | `error` | `seed` | Witness requirement signature does not exactly match required throws/effects/receiver contract. |
| `WORD_COMMENT_AMBIGUOUS_ATTACHMENT` | `lexer` | `error` | `active` | A Word Comment attachment is ambiguous; use line structure or explicit placement so lossless CST attachment is deterministic. |
| `WORD_COMMENT_EXPECTED_TEXT` | `lexer` | `error` | `active` | Backtick word comment requires a non-empty word comment body. |
| `WORD_COMMENT_LOSSLESS_TRIVIA_REQUIRED` | `lexer` | `error` | `active` | Word Comment trivia must be preserved by parser, formatter, and LSP projections. |
| `WORD_COMMENT_NOT_CALL_LABEL` | `lexer` | `error` | `active` | A word comment is lossless trivia, not a named argument label or overload selector. |
| `WORD_COMMENT_OPENER_PRIORITY_REQUIRED` | `design_static` | `note` | `seed` | The lexer recognizes a backtick word-comment opener at its declared priority; \`///\` is an ordinary \`//\` line comment. |
| `WORD_COMMENT_REQUIRES_PREVIEW_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `WORD_COMMENT_WHITESPACE_FORBIDDEN_AFTER_BACKTICK` | `lexer` | `error` | `active` | Whitespace is not allowed immediately after a backtick word comment opener. |
| `YIELD_GUARD_CLAUSE_PREVIEW_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `YIELD_GUARD_CLAUSE_REQUIRES_FEATURE_GATE` | `design_static` | `note` | `retired` | This diagnostic is not emitted by current Deeplus. |
| `YIELD_RESPONSE_BINDING_NOT_ALLOWED_IN_GENERATOR` | `checker` | `error` | `active` | Yield guard and response binding are not both allowed in the same yield form. |
| `ZERO_BASED_INDEX_NOT_CURRENT` | `checker` | `error` | `active` | Index zero is outside a built-in default one-based sequence or NumericArray axis; use logical coordinate 1 for its first element. |
| `ZERO_TO_ZERO_POWER_USES_COMPUTATIONAL_CONVENTION` | `checker` | `warning` | `active` | Infix zero to the zero power evaluates to one; use powChecked for an analytic indeterminate outcome. |

## 검사기 술어

| 술어 ID | 원천 이름 | 요약 | 증거 |
|---|---|---|---|
| `ActorProtocolGateAdmitted` | Actor protocol | Current actor protocol and message-admission design predicate; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `AllNamedArgumentLayoutOnlyAllNamed` | AllNamedArgumentLayoutOnlyAllNamed | the layout has at least two arguments; every argument is named or named-unfold; no positional, context, or witness argument occurs | `DESIGN_STATIC_NOT_RUN` |
| `ApiContractDigestProjection` | ApiContractDigestProjection | Project normalized public type and responsibility data into a deterministic API digest. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `AsQueryReturnsOption` | AsQueryReturnsOption | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `AssociatedProjectionResolution` | AssociatedProjectionResolution | <T as Trait>::Assoc resolves through selected witness | `DESIGN_STATIC_NOT_RUN` |
| `AssociatedProjectionUsesDoubleColon` | AssociatedProjectionUsesDoubleColon | Associated projection is \`<T as Trait>::Assoc\`. | `DESIGN_STATIC_NOT_RUN` |
| `AssociatedRequirementAdmitted` | AssociatedRequirementAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `AssociatedRequirementWitnessAdmitted` | AssociatedRequirementWitnessAdmitted | R51a1 closed design algorithm for AssociatedRequirementWitnessAdmitted; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `AsyncActorCoreAdmitted` | AsyncActorCoreAdmitted | Tracks async/task/actor design stability while product support remains NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `AsyncCollectorPolicyAdmitted` | AsyncCollectorPolicyAdmitted | Admits the Stage-1 policy-visible collector profile with explicit source and transform ErrorSets and exact union propagation, without activating async callable literals. | `DESIGN_STATIC_NOT_RUN` |
| `AsyncSurfaceGateAdmitted` | async/await/for-await | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `AtMatchArmResultAdmitted` | @match arm result | R51a1 closed design algorithm for AtMatchArmResultAdmitted; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `AuthorityRelationAdmitted` | AuthorityRelationAdmitted | Decide explicit authority requires/grants/delegates/borrows/consumes/isolation relations without conflation. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BasicIndexOperatorAdmitted` | BasicIndexOperatorAdmitted | intrinsic [] is read-only; conformance never activates it | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitfieldBackingAdmitted` | BitfieldBackingAdmitted | Admit exactly UInt8, UInt16, UInt32, UInt64, or UInt128 as portable backing. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitfieldConstructionRowAdmitted` | BitfieldConstructionRowAdmitted | Materialize required named fields exactly once and synthesize reserved zero slots. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitfieldDerivationAdmitted` | BitfieldDerivationAdmitted | Create a fresh same-type bitfield by atomic checked field updates. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitfieldFieldValueAdmitted` | BitfieldFieldValueAdmitted | Admit a field value exactly when 0 <= value < 2^width. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitfieldLayoutClosed` | BitfieldLayoutClosed | Validate positive static contiguous slots whose widths exactly close the backing. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitfieldRawAdmitted` | BitfieldRawAdmitted | Checked conversion accepts an exact backing value whose reserved mask is canonical. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BitwiseDomainAdmitted` | BitwiseDomainAdmitted | Historical predicate identity for the Stable built-in pointwise logical family. It preserves packed known-width integer and finite bitfield/#flags behavior and additionally admits exact same-shape NumericArray operands over one exact known-width integer element domain. Scalar Bool, NumericArray<Bool>, generic collections, dynamic/heterogeneous shapes, implicit broadcast or conversion, user-defined carriers, and result-as-control use reject deterministically. Binary operands evaluate left-to-right once with zero short circuit or flow narrowing. | `DESIGN_STATIC_NOT_RUN` |
| `BlockLocalImportAdmitted` | BlockLocalImportAdmitted | Admits current block-prologue compile-time name visibility with no runtime load or extension activation. | `DESIGN_STATIC_NOT_RUN` |
| `BlockLocalUseAdmitted` | BlockLocalUseAdmitted | Admits a block-prologue lexical use frame without name import, authority, evidence, or source-order priority. | `DESIGN_STATIC_NOT_RUN` |
| `BorrowEscapeAdmitted` | borrow/view escape | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `BoundedIndexDomainAdmitted` | BoundedIndexDomainAdmitted | Construct an exact bounded logical index domain from StaticInt bounds and expression-only elements. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `BoundedLogicalIndexDomainAdmitted` | BoundedLogicalIndexDomainAdmitted | Admits StaticInt closed logical bounds whose cardinality equals the literal element count. | `DESIGN_STATIC_NOT_RUN` |
| `BoxOwnershipAdmitted` | BoxOwnershipAdmitted | construct one unique owner under explicit allocation/failure responsibility; move invalidates source and forbids source_used_after_move; a completed owned lifecycle has payload_cleanup_count exactly one and every borrow has borrow_escapes=false while owner_alive | `DESIGN_STATIC_NOT_RUN` |
| `ByteViewAdmitted` | ByteViewAdmitted | apply ReadonlyViewAdmitted first and propagate its selected diagnostic unchanged; require a nonempty owner_provenance and owner_lifetime_valid=true for the borrowed Bytes owner; require contiguous_storage=true and byte_addressable=true; require text_encoding_assumed=false and string_semantics_assumed=false | `DESIGN_STATIC_NOT_RUN` |
| `CallSideUnfoldStaticEvidence` | CallSideUnfoldStaticEvidence | R51a1 closed design algorithm for CallSideUnfoldStaticEvidence; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `CallableProfileAdmitted` | CallableProfileAdmitted | normalize four orthogonal axes; require unique canonical profile order; admit only the closed combination table; reject profile-only overload identity | `DESIGN_STATIC_NOT_RUN` |
| `CanResolveUnitSymbol` | CanResolveUnitSymbol | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `CaretPowerAdmitted` | Caret power | Closed static integer, Float, Complex, and Measure power-domain algorithm; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `CharScalarAdmitted` | Char Unicode scalar | R51c current design predicate; integrated product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ClassDispositionAdmitted` | Class openness disposition | R51c current design predicate; integrated product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `CleanupDeclarationAdmitted` | CleanupDeclarationAdmitted | require exact def#cleanup() declaration shape; forbid direct call/value, suspension, dispatch, visibility, and parameters; execute exactly once for initialized nonmoved state while preserving partial construction and primary/suppressed failure order | `DESIGN_STATIC_NOT_RUN` |
| `ClosedAnonymousUnionAdmitted` | ClosedAnonymousUnionAdmitted | Admits a finite closed tagged union of pairwise-disjoint normalized alternatives. | `DESIGN_STATIC_NOT_RUN` |
| `ClosedContractIntersectionAdmitted` | ClosedContractIntersectionAdmitted | Admits one payload with at most one concrete nominal base and a finite compatible Trait evidence bundle. | `DESIGN_STATIC_NOT_RUN` |
| `ClosedUnionTypeTestAdmitted` | ClosedUnionTypeTestAdmitted | Admit is/!is only as a nonconsuming exact alternative identity test over one normalized closed Union and compute bounded complementary Phi facts. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ClosureCaptureDescriptorAdmitted` | CaptureDescriptor closure MSP | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ClosureCaptureDescriptorAdmittedCurrentGate` | CaptureDescriptor closure current gate | R51a1 Stable closure capture descriptor admission design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `CollectionFreezeAdmitted` | CollectionFreezeAdmitted | require exclusive mutable ownership; transition to a declared immutable/shareable representation; expose copy/allocation/effect residue and do not call this snapshot | `DESIGN_STATIC_NOT_RUN` |
| `CollectionSnapshotAdmitted` | CollectionSnapshotAdmitted | produce an independent point-in-time value; declare copy or copy-on-write cost; do not freeze or invalidate the source | `DESIGN_STATIC_NOT_RUN` |
| `CollectionTraversalRoleAdmitted` | CollectionTraversalRoleAdmitted | classify storage/shape/index ownership separately from traversal; retain single-pass/multipass and borrow/consume residue; reject automatic Collection-to-Iterator equivalence | `DESIGN_STATIC_NOT_RUN` |
| `ColumnVectorSemicolonGateAdmitted` | ColumnVectorSemicolonGateAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ColumnVectorSemicolonOrientationAdmitted` | Column-vector semicolon orientation | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ComplexLiteralAndOperatorAdmitted` | Complex literal and closed numeric operation | Admit attached floating i literals and the closed Float32/Float64 Complex numeric profile without implicit Rep conversion. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ComputeResidualUnion` | ComputeResidualUnion | Compute exact remaining alternatives after ordered pattern coverage. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ConformanceDeclProducesWitness` | ConformanceDeclProducesWitness | explicit conformance produces checker-visible evidence when all requirements are satisfied | `DESIGN_STATIC_NOT_RUN` |
| `ConformanceEvidenceOriginAdmitted` | ConformanceEvidenceOriginAdmitted | forwarded identifier must denote the matching explicit witness parameter; root selector must resolve to exactly one visible coherent conformance; both channels stay borrowed and non-first-class | `DESIGN_STATIC_NOT_RUN` |
| `ConformanceVisibilityOrphanAdmitted` | ConformanceVisibilityOrphanAdmitted | Check the named conformance visibility and orphan domain before publishing its evidence identity. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ConstructionRowAdmitted` | ConstructionRowAdmitted | the target is a resolved type; a visible ConstructionRow exists; labels/defaults/ownership/invariants admit every supplied field exactly once | `DESIGN_STATIC_NOT_RUN` |
| `ConstructorDelegationGraphAdmitted` | ConstructorDelegationGraphAdmitted | each constructor delegation list selects exactly one same-type or superclass target after pure guard selection; same-type delegation edges are acyclic and every path reaches a root constructor; each root selects exactly one superclass constructor, and a delegation guard cannot observe self; the first failed condition in this order emits CONSTRUCTOR_DELEGATION_GRAPH_NOT_ADMITTED | `DESIGN_STATIC_NOT_RUN` |
| `ConstructorNamingAndEntrypointAdmitted` | ConstructorNamingAndEntrypointAdmitted | R51a1 closed design algorithm for ConstructorNamingAndEntrypointAdmitted; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ContextAnchorOperandAdmitted` | context anchor operand checker | R51a1 closed design algorithm for ContextAnchorOperandAdmitted; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ContextMarkerNotValue` | ContextMarkerNotValue | R51a1 closed design algorithm for ContextMarkerNotValue; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ContextParameterRoleAdmitted` | ContextParameterRoleAdmitted | R51a1 closed design algorithm for ContextParameterRoleAdmitted; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ContextValueAdmitted` | ContextValueAdmitted | the argument is supplied through the explicit context channel and never inferred from an ordinary argument or ambient lookup; the context role remains in function type identity and override compatibility; the value is reusable and Shareable, has no drop responsibility, owns no resource, and carries no authority; context use does not relax capture, ownership, lifetime, isolation, or escape laws; the context marker itself is not a first-class storable or returnable value | `DESIGN_STATIC_NOT_RUN` |
| `DeclarativeClauseDisjointnessProven` | declarative clause overlap checker | Finite Phase-A clause partition decision procedure; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `DeclarativeClauseExhaustive` | clause block coverage checker | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `DeclarativeClausePartitionAdmitted` | declarative clause partition | Finite Phase-A clause partition decision procedure; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `DedentedMultilineStringAdmitted` | DedentedMultilineStringAdmitted | R51f3 owner-specific static design seed for dedented_multiline_unicode_string; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `DeterministicPrimarySuppressedOrderAdmitted` | primary/suppressed failure order | candidate operations are evaluated left-to-right in source order and stop ordinary evaluation at the first escaping failure; the first escaping failure is retained as primary; cleanup actions execute in reverse acquisition order even after failure; each cleanup failure is appended to primary.suppressed in cleanup execution order and never replaces primary; if ordinary evaluation succeeds but cleanup fails, the first cleanup failure becomes primary and later cleanup failures are suppressed in execution order | `DESIGN_STATIC_NOT_RUN` |
| `DisplayUnitDecisionVisible` | DisplayUnitDecisionVisible | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `DynamicUnitConversionProfileAdmitted` | DynamicUnitConversionProfileAdmitted | Separate stdlib profile activation, provider presence and conversion policy completeness; no source current gate is consulted. | `DESIGN_STATIC_NOT_RUN` |
| `EffectErrorRowPolymorphismAdmitted` | EffectErrorRowPolymorphismAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EffectErrorRowUnionAdmitted` | Effect/Error row visible union | R51c current design predicate; integrated product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EffectRowForwardingAdmitted` | higher-order effect forwarding | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EffectRowSubsumes` | EffectRowSubsumes | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EntrySignatureAdmitted` | EntrySignatureAdmitted | source_kind is FunctionType, source_role is executable, and entry_kind is exactly sync or async; the exact (parameters, result) pair is one of ([], Unit), ([Sequence<String>], Unit), ([], ExitCode), or ([Sequence<String>], ExitCode); generic and receiver are false and context_parameters, witness_parameters, rest_parameters, and default_parameters are all zero; error_set normalizes to the empty set (spelled throws Never when written); effect_row is a closed normalized row and does not alter signature-shape admission; call_shape.selected_entry_target_count is present and EntryTargetUnique admits the same descriptor before local signature admission succeeds | `DESIGN_STATIC_NOT_RUN` |
| `EntryTargetUnique` | EntryTargetUnique | call_shape.selected_entry_target_count is a nonnegative integer; an executable root is admitted exactly when selected_entry_target_count equals one; a zero count emits NO_EXECUTABLE_ENTRY and a count greater than one emits ENTRY_DECL_DUPLICATE; a library root with a nonzero selected count emits ENTRY_NOT_ALLOWED_IN_LIBRARY_SOURCE and a script root with a nonzero selected count emits SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT; library and script roots are admitted exactly when selected_entry_target_count equals zero | `DESIGN_STATIC_NOT_RUN` |
| `EnumCaseCommaListAdmitted` | EnumCaseCommaListAdmitted | R51f3 owner-specific static design seed for enum_case_comma_list; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EnumCaseDoubleColonAdmitted` | Enum case double-colon injection | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EnumPayloadPlaneSeparated` | EnumPayloadPlaneSeparated | Enum declaration, expression, and pattern payload planes are separated. | `DESIGN_STATIC_NOT_RUN` |
| `ErrorRowForwardingAdmitted` | higher-order error forwarding | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `EscapedMemberSuffixAdmitted` | Escaped member suffix | R51c current design predicate; integrated product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ExactRatioUnitConversionAdmitted` | ExactRatioUnitConversionAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ExistentialSafety` | ExistentialSafety | any Trait requires existential-safe trait and associated binding when required | `DESIGN_STATIC_NOT_RUN` |
| `ExplicitWitnessArgumentAdmitted` | ExplicitWitnessArgumentAdmitted | source_kind is exactly WitnessArgument; formal_parameter_surface independently parses as \`using formal_parameter_identity: witness formal_parameter_trait\` and the parsed identity/trait equal those descriptor fields; if evidence_origin is forwarded_parameter, argument_surface is exactly \`using \` plus argument_identifier, argument_identifier equals evidence_binding_identity, and evidence_binding_surface independently passes ExplicitWitnessParameterAdmitted; if evidence_origin is coherent_conformance, argument_surface is exactly \`using conformance(Type conforms Trait)\`, no ordinary evidence binding is created, and ConformanceEvidenceOriginAdmitted selects exactly one visible nominal conformance; the forwarded declared trait or root selector trait, resolved_evidence_trait, and formal_parameter_trait are exactly equal; escapes is false and ownership is borrowed; ExplicitWitnessParameterAdmitted is applied to the callee formal and, only for forwarding, separately to the caller evidence binding before WitnessCoherent | `DESIGN_STATIC_NOT_RUN` |
| `ExplicitWitnessParameterAdmitted` | ExplicitWitnessParameterAdmitted | source_kind is exactly WitnessParameter; formal_parameter_surface parses exactly as \`using formal_parameter_identity: witness formal_parameter_trait\`; the parsed Identifier and normalized TraitRef must equal those two descriptor fields; parameter_kind is explicit_witness; witness_use_context is explicit_parameter_declaration and evidence_origin is parameter_declaration; escapes is false and ownership is borrowed | `DESIGN_STATIC_NOT_RUN` |
| `ExtensionConformanceIdentitySeparated` | Extension and witness identity | R51c current design predicate; integrated product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ExtensionNotTraitWitness` | ExtensionNotTraitWitness | R51a1 closed design algorithm for ExtensionNotTraitWitness; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `FFIExternSurfaceDisposition` | extern#C / def#unsafe | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `FFIExternUnsafeSurfaceGateAdmitted` | FFI C extern unsafe current law | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `FacetEscapeAdmitted` | FacetEscapeAdmitted | Keep a borrowed Facet inside its payload region and synchronous lexical scope. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `FacetPackAdmitted` | FacetPackAdmitted | Admit a Phase-A borrow Facet after existential-safety and evidence closure. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `FacetPackageAdmitted` | FacetPackageAdmitted | Admits explicit borrowed existential packaging that seals coherent evidence and preserves payload identity and lifetime. | `DESIGN_STATIC_NOT_RUN` |
| `FacetTransferAdmitted` | FacetTransferAdmitted | Preview-design algorithm for future owned Facet transfer; nonactivatable in R51b. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `FeatureContractAdmitted` | Actor protocol | Checks the feature-class-specific current contract referenced by a crosswalk row. | `DESIGN_STATIC_NOT_RUN` |
| `FillRepeatAdmissible` | FillRepeatAdmissible | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `FlagsOperationAdmitted` | FlagsOperationAdmitted | Admit same-type finite-universe flags bitwise operations and mask the result. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `FlowBindingLocalAdmitted` | FlowBindingLocalAdmitted | Compatibility identity absorbed by RightwardLocalBindingNormalizesToOrdinaryBinding and OrdinaryLocalBindingAdmitted. | `DESIGN_STATIC_NOT_RUN` |
| `FlowDollarBindingAdmitted` | FlowDollarBindingAdmitted | Non-emitting predecessor predicate identity for statement-only \`$\`/\`$$\` fresh local flow binding; the current executable contract is FlowBindingLocalAdmitted. | `DESIGN_STATIC_NOT_RUN` |
| `ForSourceIterableAdmitted` | for source iterable profile | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `FunctionCompatibility` | FunctionCompatibility | Compare call shape, parameter variance, result, failure, effect, authority, suspension and ownership residue. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `FunctionProfileIntroducerAdmitted` | FunctionProfileIntroducerAdmitted | Admits exactly the owner-specific closed declaration-profile table; the removed tail-recursion kind is never admitted. | `DESIGN_STATIC_NOT_RUN` |
| `FunctionRestResiduePreserved` | FunctionRestResiduePreserved | Function types and public API digests preserve each repeated \`T...\` and named \`Record***\` residue exactly; Sequence, plain Record, Map, count, and omission erasure are rejected. | `DESIGN_STATIC_NOT_RUN` |
| `FunctionReturnAndLambdaRetAdmitted` | FunctionReturnAndLambdaRetAdmitted | ordered branch 1: return in a lambda emits RETURN_NOT_ALLOWED_IN_LAMBDA and ret in a named function emits RET_OUTSIDE_LAMBDA; ordered branch 2: a non-Unit lambda block path without ret emits LAMBDA_BLOCK_REQUIRES_RET; ordered branch 3: a non-Unit named-function block path without return emits MISSING_EXPLICIT_RETURN; ordered branch 4: a terminal valueless return in a Unit named function is admitted and emits only the REDUNDANT_FINAL_VALUELESS_RETURN lint; Unit fallthrough and early valueless return are admitted without that lint; an ordinary named \`= expr\` body has no current AST route and is rejected earlier by the parser with FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN | `DESIGN_STATIC_NOT_RUN` |
| `GeneratedDataMaterializationAdmitted` | GeneratedDataMaterializationAdmitted | parsing DataClassDecl deterministically normalizes class_kind=data and class_disposition=final; this implicit final disposition forbids subclasses and requires no source \`final\` token; every promoted stored field is let and there is no mutable stored field; custom_root_constructor, resource_semantics, effectful_default, throwing_default, hidden_invariant, and nontrivial_super_initialization are all false; the compiler generates exactly one ConstructionRow from visible promoted fields in declaration order; no ProjectionRow is generated automatically and named unfolding remains unavailable without an explicit ProjectionRow | `DESIGN_STATIC_NOT_RUN` |
| `GenericConstraintSatisfied` | generic/where clause | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `GenericConstructorVariance` | GenericConstructorVariance | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `GenericInvarianceAdmitted` | GenericInvarianceAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `GenericVarianceDescriptorAdmitted` | GenericVarianceDescriptorAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `GroupedMemberForwardingAdmitted` | GroupedMemberForwardingAdmitted | R51f3 owner-specific static design seed for grouped_member_forwarding_sugar; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `GuardCallableAdmitted` | GuardCallableAdmitted | apply PureCallableAdmitted; require exact Bool result; reject consume, mutation, external control transfer, and spawned/resource obligations | `DESIGN_STATIC_NOT_RUN` |
| `GuardPredicateAdmitted` | GuardPredicateAdmitted | A guard is exact Bool, pure, no-throw, nonsuspending, authority-free and cannot transfer control. | `DESIGN_STATIC_NOT_RUN` |
| `GuardedBindingCommitAdmitted` | GuardedBindingCommitAdmitted | Commit guarded-let bindings only after one successful pattern and one direct unconditional failure exit are proven. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `GuardedLetResidualExitAdmitted` | GuardedLetResidualExitAdmitted | Computes the residual closed domain after the success pattern and requires one irrefutable failure pattern plus one terminating exit. | `DESIGN_STATIC_NOT_RUN` |
| `GuardedTransferEvaluationAdmitted` | GuardedTransferEvaluationAdmitted | evaluate guards left-to-right once each; perform no ownership commit before all guards succeed; a false guard evaluates no payload or payload-created obligation | `DESIGN_STATIC_NOT_RUN` |
| `HasKnownUnitWitness` | HasKnownUnitWitness | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `IdentityNominalityAdmitted` | IdentityNominalityAdmitted | classify nominality and identity independently; permit identity operations only when identity-bearing is true; never infer Plain/Copy/shareable from identityless value-class status | `DESIGN_STATIC_NOT_RUN` |
| `ImplicitAtLambdaAdmitted` | implicit @ lambda | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ImplicitLambdaOverloadStagingAdmitted` | ImplicitLambdaOverloadStagingAdmitted | filter overloads by call shape and non-lambda arguments; require exactly one expected callable; check the implicit @ body once only after selection | `DESIGN_STATIC_NOT_RUN` |
| `InterpolationPathAdmitted` | InterpolationPathAdmitted | Resolve a gated read-only interpolation path and erase only its terminal boundary from semantic output. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `KeyableAdmissible` | Keyable | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `KindSeparationAdmitted` | KindSeparationAdmitted | require exactly one responsibility_kind_candidates entry; require that candidate to equal responsibility_kind; reject every nonempty kind_axis_conflicts list while preserving independent identity, ownership, copy, sharing, effect, and representation axes | `DESIGN_STATIC_NOT_RUN` |
| `LayoutEntrySepAdmitted` | LayoutEntrySepAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `LazyForceAdmitted` | LazyForceAdmitted | Admit pure synchronous call-by-need forcing with deterministic cycle rejection and exactly one published commit. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `LazyLetAdmitted` | LazyLetAdmitted | Admits a local nonescaping memoizing call-by-need immutable binding under the closed pure initializer profile. | `DESIGN_STATIC_NOT_RUN` |
| `LibraryStaticBindingInitializerAdmitted` | LibraryStaticBindingInitializerAdmitted | source_kind is Binding and source_role is library; call_shape.binding_kind is let, dependency_cycle is false, and commit_count is exactly one; error_set and effect_row are both empty normalized sets, suspension is none, and authority is empty; cleanup.acquires_resource and cleanup.escapes_resource are both false; call_shape.initializer_task_count and call_shape.initializer_actor_count are both zero; isolation is exactly local; no actor/global isolation boundary is crossed during initialization; the conjunction is evaluated left-to-right in the written order and the first failed conjunct emits LIBRARY_STATIC_BINDING_INITIALIZER_NOT_ADMITTED | `DESIGN_STATIC_NOT_RUN` |
| `LinearAlgebraOperatorAdmitted` | LinearAlgebraOperatorAdmitted | LinearProductExpr folds \`**\` and \`*+\` strictly left-to-right in source order and validates each intermediate result before the next step; for \`**\`, both operands are rank-2; a rank failure emits MATRIX_PRODUCT_REQUIRES_RANK2_MATRICES and an inner-dimension mismatch emits MATRIX_PRODUCT_DIMENSION_MISMATCH; for \`*+\`, both operands are rank-1 vectors of equal static or checker-proven length; any rank/length failure emits DOT_PRODUCT_REQUIRES_RANK1_VECTORS; mixed operator chains are not rejected for associativity alone; the first fold step whose current lhs/rhs ranks or shapes violate its operator emits that operator's exact diagnostic | `DESIGN_STATIC_NOT_RUN` |
| `LinearProductLeftFoldAdmitted` | LinearProductLeftFoldAdmitted | R51c current design predicate for LinearProductLeftFoldAdmitted; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ListLiteralElementJoinAdmitted` | ListLiteralElementJoinAdmitted | Checks ordinary List elements against one inferred homogeneous type or an explicit expected type, including an explicit closed union; it never synthesizes a Union. | `DESIGN_STATIC_NOT_RUN` |
| `LocalValueBodyAdmitted` | LocalValueBodyAdmitted | a value-producing @if has an else branch; the optional grammar tail is recovery-only; exactly one expression is admitted directly; otherwise every reachable normal path ends in local ret; return is an enclosing-function transfer and finally never creates the local value | `DESIGN_STATIC_NOT_RUN` |
| `LogicalIndexDomainAdmitted` | LogicalIndexDomainAdmitted | one closed intrinsic logical domain: List/String/Bytes and default NumericArray axes are one-based, bounded owners retain L..U, Map uses exact K, and ReadonlyView preserves its source owner's domain | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `LoopOutcomeExhaustive` | LoopOutcomeExhaustive | ordered branch 1: a value-carrying break without an immediately following outcome match emits BREAK_VALUE_REQUIRES_LOOP_OUTCOME_MATCH; ordered branch 2: a present outcome match using a pattern other than the admitted outcome cases emits LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE; ordered branch 3: a present correctly spelled match that omits any reachable outcome emits LOOP_OUTCOME_MATCH_NON_EXHAUSTIVE; only a present, correctly spelled, exhaustive outcome match admits the value-carrying loop result | `DESIGN_STATIC_NOT_RUN` |
| `LoopOutcomeHandlerAdmitted` | LoopOutcomeHandlerAdmitted | normalize loop and optional handler to one node; run intermediate cleanup/finally while skipping intermediate handlers; only the final break target handler observes ::break and a terminal continue observes none | `DESIGN_STATIC_NOT_RUN` |
| `MapUnfoldEntryAdmitted` | MapUnfoldEntryAdmitted | Validate one exact-K/V, source-ordered, failure-atomic MapLiteralPlan for direct entries and Map unfolds. | `DESIGN_STATIC_NOT_RUN` |
| `MatchExhaustive` | match exhaustiveness and usefulness | Compute match-arm usefulness and final exhaustiveness over one finite structural partition. | `DESIGN_STATIC_NOT_RUN` |
| `MatchGuardPurityAdmitted` | match arm guard purity | Apply the ordinary guard profile, then forbid consuming or escaping probe bindings before atomic commit. | `DESIGN_STATIC_NOT_RUN` |
| `MaterializationFieldPunAdmitted` | MaterializationFieldPunAdmitted | R51f3 owner-specific static design seed for materialization_derivation_field_punning; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `MatrixProductAdmitted` | Matrix product | both operands are rank-2; the left inner dimension equals the right inner dimension; \`**\` participates in the left-to-right LinearProductExpr fold and this predicate is applied independently at the current fold step | `DESIGN_STATIC_NOT_RUN` |
| `MeasureUnitWitnessAdmitted` | MeasureUnitWitnessAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `MemberExtensionCollisionPolicyAdmitted` | MemberExtensionCollisionPolicyAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `MemberExtensionCollisionRejected` | MemberExtensionCollisionRejected | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `MethodExtensionResolutionAdmitted` | method/extension message resolution | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `MutableCallableEnvironmentAdmitted` | MutableCallableEnvironmentAdmitted | require environment_receiver=mutable; acquire exactly one exclusive mutable environment place for the invocation; reject overlapping mutable access and reentrant invocation without a separately admitted proof | `DESIGN_STATIC_NOT_RUN` |
| `NamedConformanceAdmitted` | NamedConformanceAdmitted | Admit one static named conformance identity without adding it to automatic witness search. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NamedEvidenceExcludedFromAutomaticResolution` | NamedEvidenceExcludedFromAutomaticResolution | Keep named evidence out of the automatic WitnessResolution candidate set. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NamedExtensionSetAdmitted` | named extension set identity | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `NamedExtensionSetAdmitted_R48_48` | NamedExtensionSetCurrentAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `NamedRestCollectorAdmitted` | NamedRestCollectorAdmitted | Named-rest parameter and function-type residue use \`***\`; call/materialization named unfold uses \`**\`. Product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `NamedRestParameterRecordAndLastPosition` | NamedRestParameterRecordAndLastPosition | named_rest_parameter_count is exactly one; named_rest_parameter_type is exactly Record; named_rest_parameter_index equals parameter_count - 1; dispatch multiple-count before non-Record type before nonfinal position | `DESIGN_STATIC_NOT_RUN` |
| `NarrowUnionByPattern` | NarrowUnionByPattern | Refine Phi by the alternatives selected by a pattern without changing the declared semantic type. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NominalPrototypeDerivationAdmitted` | NominalPrototypeDerivationAdmitted | the result normalized_type is exactly the base nominal type; construction_domain is nominal_derivation and a visible ConstructionRow admits every label exactly once; derivation mode is shallow or deep and never changes conformance or nominal identity; shallow mode preserves declared field ownership responsibilities; deep mode requires deep-clone admission for every traversed field; resource, borrow, invariant, and cleanup responsibilities are rechecked before the fresh value is committed | `DESIGN_STATIC_NOT_RUN` |
| `NormalizeContractIntersection` | NormalizeContractIntersection | Normalize one optional concrete base plus coherent Trait contracts. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NormalizeSemanticType` | NormalizeSemanticType | Normalize source spelling into one closed RCTS-V5 semantic variant without dropping responsibility axes. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NormalizeUnion` | NormalizeUnion | Admit a closed Union only when every finite R0 alternative pair is proven disjoint. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NullaryLambdaExpectedContextAdmitted` | NullaryLambdaExpectedContextAdmitted | an arrow-elided contextual brace lambda requires an independently fixed zero-parameter callable type; empty body is admitted only when the expected result is Unit; a multiline non-Unit body ends in exactly one FinalRetStmt while a Unit body may fall through; without expected callable context the surface is rejected or uses the separately gated nullary inference route | `DESIGN_STATIC_NOT_RUN` |
| `NumericArrayContextAnchorAdmitted` | NumericArray context anchor | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `NumericArrayElementAdmitted` | NumericArrayElement | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `NumericArrayElementwiseSameShapeAdmitted` | NumericArrayElementwiseSameShapeAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `NumericArrayInfixPowerRequiresPreview` | NumericArrayInfixPowerRequiresPreview | NumericArray infix \`^\` requires Preview gate. | `DESIGN_STATIC_NOT_RUN` |
| `NumericArrayPostfixTransposeAdmitted` | NumericArray postfix transpose | Admit owner-bounded readonly NumericArray view. | `DESIGN_STATIC_NOT_RUN` |
| `NumericArrayPostfixTransposeStable` | NumericArrayPostfixTransposeStable | Attached \`A^\` is Stable NumericArray transpose. | `DESIGN_STATIC_NOT_RUN` |
| `NumericFillSliceIndexAdmitted` | NumericFillSliceIndexAdmitted | NumericArray fill/index/slice has exact rank and typed one-based axes; slices preserve owner and coordinates | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NumericLiteralAdmitted` | NumericLiteralAdmitted | exact value or magnitude admission for a lexer-validated signless numeric token | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `NumericOperatorCoreAdmitted` | NumericOperatorCoreAdmitted | intrinsic owner dispatch over exact literal results; failure precedes commit | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `OnceCallableAdmitted` | OnceCallableAdmitted | require call_right=once; consume the call right atomically at the first invocation; reject invocation_attempt_count greater than one or an attempt after once_right_consumed_before_attempt | `DESIGN_STATIC_NOT_RUN` |
| `OperatorPrecedenceTablePhaseAAdmitted` | OperatorPrecedenceTablePhaseAAdmitted | closed Pratt token, binding powers, associativity, parselet, and owner | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `OptionCoalescingAdmitted` | OptionCoalescingAdmitted | lhs normalizes to Option<T>; rhs is checked lazily against T; ownership permits one-layer extraction without hidden clone | `DESIGN_STATIC_NOT_RUN` |
| `OptionLocalTargetInsertionAdmitted` | OptionLocalTargetInsertionAdmitted | an explicit local binding or field target was independently fixed to exactly Option<T>; the insertion depth is exactly one; the context is not call, return, lambda, collection, generic-driving, or nested | `DESIGN_STATIC_NOT_RUN` |
| `OptionSurfaceCanonicalAdmitted` | OptionSurfaceCanonicalAdmitted | Option cases use ::some/::none and no bare or dot-case alias is present | `DESIGN_STATIC_NOT_RUN` |
| `OptionalSuffixSingleLayerAdmitted` | Single compact optional suffix | normalize one attached question mark to exactly Option<T>; reject a second compact attached question mark; express nested absence explicitly as Option<T?> | `DESIGN_STATIC_NOT_RUN` |
| `OrdinaryLocalBindingAdmitted` | OrdinaryLocalBindingAdmitted | Shared local binding checker for direct let/var and normalized rightward surfaces. | `DESIGN_STATIC_NOT_RUN` |
| `OwnedDowncastAdmitted` | OwnedDowncastAdmitted | attempt dynamic type test without consuming into an unrecoverable state; return matched Target or unmatched original Source exactly once | `DESIGN_STATIC_NOT_RUN` |
| `OwnershipModeAdmitted` | OwnershipModeAdmitted | ordinary mut acquires one argument into a callee-owned mutable local with no caller alias/writeback and retains the caller owner on precommit failure; borrow is a nonescaping shared region; inout is one exclusive caller-place borrow whose successful writes are visible to the caller; move transfers ownership once; cleanup remains with the current owner | `DESIGN_STATIC_NOT_RUN` |
| `PatternBindingControlAdmitted` | PatternBindingControlAdmitted | R51f3 owner-specific static design seed for pattern_binding_control_family; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `PlaceReplaceAdmitted` | PlaceReplaceAdmitted | evaluate place once and require exclusive access; on precommit_failure require transaction_committed=false and original_owner_preserved=true; on success require transaction_committed=true, one new-value write, and one old-owner return | `DESIGN_STATIC_NOT_RUN` |
| `PlainValueAdmissible` | Plain / PlainValue | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `PreviewFeatureGateAdmitted` | PreviewFeatureGateAdmitted | the selected root is exactly Preview{Role}SourceFile and the gate precedes ModuleDecl/source items; gate ids are scanned left-to-right; an unknown id emits PREVIEW_GATE_UNKNOWN_FEATURE; a known id whose lifecycle is not PREVIEW/explicit_feature_gate emits PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE; the first repeated id emits PREVIEW_GATE_DUPLICATE_FEATURE; the gate id set equals the explicit transitive Preview dependency closure of the requested feature set; omission emits PREVIEW_GATE_DEPENDENCY_MISSING; every requested feature is present and the parsed AST production occurs in its gate-map route set; after admission the checker applies the feature-local semantic predicate; no dependency is activated implicitly | `DESIGN_STATIC_NOT_RUN` |
| `PrimaryCtorPromotedFieldReachable` | PrimaryCtorPromotedFieldReachable | Primary constructor grammar route reaches PromotedFieldDecl including +let/-let/#let/#var visibility. | `DESIGN_STATIC_NOT_RUN` |
| `PrimaryCtorPromotedFieldVisibilityMemberOnly` | PrimaryCtorPromotedFieldVisibilityMemberOnly | R51a1 design predicate; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ProjectionRowAdmitted` | ProjectionRowAdmitted | the source provides a static ProjectionRow; all requested labels are visible and unique; move/borrow consumption is legal in the call scope | `DESIGN_STATIC_NOT_RUN` |
| `ProviderSupportsConversion` | ProviderSupportsConversion | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `PureCallableAdmitted` | PureCallableAdmitted | require throws Never, effects {}, no suspension and no unsafe authority; reject var/inout/mutable shared/authority/resource captures and external mutation; do not infer totality, determinism, CTFE, or allocation freedom | `DESIGN_STATIC_NOT_RUN` |
| `QualifiedExtensionSelectorAdmitted` | QualifiedExtensionSelectorAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `QualifiedExtensionSelectorAdmitted_R48_60` | QualifiedExtensionSelectorCurrentAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `QuarantineScopeDesignAdmitted` | QuarantineScopeDesignAdmitted | R51e design-static admission rule for dynamic_unsafe_quarantine_scope_msp; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `R0GuardSafe` | R0GuardSafe | Admit only a finite total, exact-Bool, responsibility-free R0 expression. | `DESIGN_STATIC_NOT_RUN` |
| `RationalLiteralAdmitted` | Rational compound literal | Admit one expression-prefix transactional <p/q> literal and normalize it to an exact BigInt pair. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ReadonlyViewAdmitted` | ReadonlyViewAdmitted | require nonowning nonmutating access with exact provenance; bound the view by owner lifetime and move/drop; reject suspension/task/actor/isolation transfer without shareability proof | `DESIGN_STATIC_NOT_RUN` |
| `ReceiverOwnerResultAdmitted` | ReceiverOwnerResultAdmitted | Admit exactly one explicit Self-compatible owner result from a consuming receiver. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `RecordNamedArgumentSpreadAdmitted` | Record named argument spread | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `RefinementCheckBoundaryAdmitted` | RefinementCheckBoundaryAdmitted | Apply three-valued proof at explicit refinement boundaries. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `RefinementR0PredicateAdmitted` | RefinementR0PredicateAdmitted | the predicate syntax belongs to the finite R0 operator/name whitelist; effect_row and authority are empty and suspension is none; the predicate is total for every value in the normalized input domain and cannot throw, allocate observable identity, mutate, perform I/O, query a provider, reflect, or search with a solver; evaluation occurs only at the declared construction, cast, argument, return, or pattern boundary | `DESIGN_STATIC_NOT_RUN` |
| `RepeatedParameterOrderAndElementType` | RepeatedParameterOrderAndElementType | R51a1 closed design algorithm for RepeatedParameterOrderAndElementType; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ResolveIntersectionEvidenceBundle` | ResolveIntersectionEvidenceBundle | Resolve a coherent evidence bundle for all intersection contracts. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ResponsibilitySubsumes` | ResponsibilitySubsumes | Compare ownership, effect, failure, authority, isolation and cleanup axes independently. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ResultErrorSetModelAdmitted` | ResultErrorSetModelAdmitted | Result value-channel error families and throws control-channel families are normalized independently as duplicate-free sets; source order is retained only for deterministic diagnostic presentation; the intersection of the two normalized recoverable-error sets is empty; Defect and Cancellation classifications are not silently inserted into either recoverable set | `DESIGN_STATIC_NOT_RUN` |
| `ResultThrowsOverlapForbidden` | Result/throws duplicate channel checker | collect recoverable error-family identities from the normalized \`Result<T, error E>\` value channel in source order; collect recoverable error-family identities from the normalized throws ErrorSet in source order; admit exactly when the two identity sets are disjoint; the first Result-family identity also present in throws emits RESULT_THROWS_CHANNEL_OVERLAP | `DESIGN_STATIC_NOT_RUN` |
| `RightwardLocalBindingNormalizesToOrdinaryBinding` | RightwardLocalBindingNormalizesToOrdinaryBinding | Classify \`$\`/\`$$\`, preserve CST, and normalize to ordinary immutable/mutable local binding before semantic checking. | `DESIGN_STATIC_NOT_RUN` |
| `SatisfiesConformance` | SatisfiesConformance | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ScopedActivationGroupAdmitted` | ScopedActivationGroupAdmitted | R51f3 owner-specific static design seed for scoped_import_use_grouping; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `ScopedCallableAdmitted` | ScopedCallableAdmitted | assign the receiver invocation region; require callable and borrowed captures not to outlive it; reject storage, return, continuation, task, actor, and isolation escape | `DESIGN_STATIC_NOT_RUN` |
| `ScopedImportBlockAdmitted` | ScopedImportBlockAdmitted | Admits a current statement-only import environment frame with compile-time body scope. | `DESIGN_STATIC_NOT_RUN` |
| `ScopedUseBlockAdmitted` | ScopedUseBlockAdmitted | Admits a statement-only scoped use frame and rejects priority by nesting depth. | `DESIGN_STATIC_NOT_RUN` |
| `SealedDirectSubclassAdmitted` | Sealed direct subclass | R51c current design predicate; integrated product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `SelectUnionInjection` | SelectUnionInjection | Select exactly one alternative of an independently fixed union. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `ShapedSemicolonBodyAdmitted` | ShapedSemicolonBodyAdmitted | shape is a nonempty positive dimension vector and rank equals its length; comma advances only the innermost coordinate; a semicolon run of length k closes exactly k completed inner axes and satisfies 1 <= k < rank; a nonfinal run advances the immediately enclosing axis and resets the closed axes; an optional trailing semicolon run has length rank - 1 and all coordinates and total element count equal the declared shape | `DESIGN_STATIC_NOT_RUN` |
| `ShareableObservationSafe` | Shareable | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `SharingTransitionAdmitted` | SharingTransitionAdmitted | admit implicit reuse only for Plain value or explicit Shared handle; reject implicit owner/resource/view-to-Shared promotion | `DESIGN_STATIC_NOT_RUN` |
| `SingleActionDeferAdmitted` | SingleActionDeferAdmitted | Admits exactly one non-suspending cleanup invocation and reserves captured cleanup places until scope exit. | `DESIGN_STATIC_NOT_RUN` |
| `SingleGuardClauseAdmitted` | SingleGuardClauseAdmitted | R51f3 owner-specific static design seed for single_guard_clause_unification; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `SliceLogicalDomainPreserved` | SliceLogicalDomainPreserved | Preserves the selected source logical coordinate interval in every view/copy slice. | `DESIGN_STATIC_NOT_RUN` |
| `SliceRangeAdmitted` | inclusive slice range | two-bound .. or ..< slice; static diagnostics and dynamic IndexError precede view creation | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `SliceViewLifetimeAdmitted` | readonly slice carrier view | a slice result is a readonly view tied to one live owner and retains the selected source logical coordinates; hidden copy, rebase, mutation, escape, and isolation crossing are forbidden | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `SourceRoleAdmitted` | SourceRoleAdmitted | ordered branch 1: normalize every manifest path to one project-root-relative lexical key before parsing; normalized_path_conflict true means the first repeated key emits SOURCE_ROLE_CARRIER_CONFLICT even when both rows name the same role; ordered branch 2: the manifest role is authoritative; source_role or an external CLI, API, or IDE role unequal to manifest_source_role emits SOURCE_ROLE_CARRIER_CONFLICT; ordered branch 3: a library target containing any script-classified source root emits LIBRARY_TARGET_CONTAINS_TOP_LEVEL_SCRIPT; ordered branch 4: an explicit entry in a library emits ENTRY_NOT_ALLOWED_IN_LIBRARY_SOURCE; a top-level statement in a library or executable root emits TOP_LEVEL_STATEMENT_REQUIRES_SCRIPT_ROOT; an executable top-level binding emits TOP_LEVEL_BINDING_NOT_ALLOWED_IN_EXECUTABLE_SOURCE; an explicit entry in a script emits SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT; ordered branch 5: explicit_entry_count unequal to selected_entry_target_count emits SOURCE_ROLE_ENTRY_COUNT_MISMATCH; after equality, executable zero/multiple counts emit NO_EXECUTABLE_ENTRY/ENTRY_DECL_DUPLICATE and library/script counts must both be zero; only after all branches pass does source_role choose exactly one Stable or Preview role root; trying roots to infer a role is forbidden | `DESIGN_STATIC_NOT_RUN` |
| `StableComprehensionScopedUseMembershipAdmitted` | Stable comprehension, scoped-use, and membership family | Design-static checker seed for comprehension, scoped activation and membership; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `StableOnlyGrammarProfileClosed` | stable-only grammar profile | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `StableStaticContractProofAdmitted` | StableStaticContractProofAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `StandardResponsibilityProfilesAdmitted` | StandardResponsibilityProfilesAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `StaticCallShapeAdmitted` | StaticCallShapeAdmitted | positional arguments precede named arguments and retain source order; label_row labels are unique and every supplied label exactly matches one visible formal label; context and explicit-witness channels bind only to corresponding formal channels; at most one repeated or named-rest residue captures each unbound argument and no argument is captured twice; shape admission completes before overload ranking and is independent of declaration ordering | `DESIGN_STATIC_NOT_RUN` |
| `StaticEvidenceNoEscapeAdmitted` | StaticEvidenceNoEscapeAdmitted | Ensure a static evidence selector never acquires value identity or escapes its call-site channel. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `StaticEvidenceSelectorAdmitted` | StaticEvidenceSelectorAdmitted | Resolve a named conformance selector as non-value static evidence. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `StaticEvidenceUsingChannelAdmitted` | StaticEvidenceUsingChannelAdmitted | Admit named static evidence only through the explicit using argument channel. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `StaticExprAdmissible` | static expression profile | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `StaticIntExpressionInR0` | StaticIntExpressionInR0 | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `StaticNamedEvidenceSelectorAdmitted` | StaticNamedEvidenceSelectorAdmitted | Admits one visible named conformance selected only in the explicit using evidence channel. | `DESIGN_STATIC_NOT_RUN` |
| `StrictSequentialBooleanAdmitted` | StrictSequentialBooleanAdmitted | strict Bool operands; sequential right operand is conditionally evaluated; product checker NOT_RUN | `DESIGN_STATIC_NOT_RUN` |
| `StringCharBytesBoundaryAdmitted` | StringCharBytesBoundaryAdmitted | Design seed for text/binary/display boundary. | `DESIGN_STATIC_NOT_RUN` |
| `StringRenderAdmitted` | StringRenderAdmitted | Type and lower String::render as single evaluation plus one nonescaping renderer invocation. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `StructuredControlTargetResolved` | StructuredControlTargetResolved | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `TerminalUnitReturnAdmitted` | TerminalUnitReturnAdmitted | a non-Unit named-function path that reaches the end without an explicit value return emits MISSING_EXPLICIT_RETURN; a terminal valueless return in a Unit function is semantically admitted but emits REDUNDANT_FINAL_VALUELESS_RETURN as a lint; Unit fallthrough is canonical and an early valueless return remains admitted control flow without the terminal-return lint | `DESIGN_STATIC_NOT_RUN` |
| `TernarySpacingAndArmJoinAdmitted` | TernarySpacingAndArmJoinAdmitted | Spaced ternary evaluates one strict-Bool condition once, evaluates exactly one lazy arm, and joins normalized type, place capability, ownership, effect row, recoverable errors, cancellation, and cleanup without synthesizing an anonymous Union. | `DESIGN_STATIC_NOT_RUN` |
| `TopLevelTypeVisibilityAdmitted` | TopLevelTypeVisibilityAdmitted | Normalize one top-level visibility domain while requiring an explicit word for exactly nine type-producing owners in all six stable and preview source roots. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `TrailingClosureArgumentAdmitted` | TrailingClosureArgumentAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `TrailingClosureCardinalityAdmitted` | TrailingClosureCardinalityAdmitted | one trailing closure may be unlabeled or labeled; two or more require every item to have a unique label | `DESIGN_STATIC_NOT_RUN` |
| `TrailingClosureSuffixAdmitted` | TrailingClosureSuffixAdmitted | a shared ordinary-or-message trailing-closure group is admitted only when every item binds to an exact closure/function-typed formal; without such a formal the suffix emits TRAILING_CLOSURE_REQUIRES_FUNCTION_PARAMETER | `DESIGN_STATIC_NOT_RUN` |
| `TraitAssociatedStaticSelectionAdmitted` | Trait-qualified associated static selection | Resolve <T as Trait>::item through exactly one static conformance and preserve all identity and responsibility residue. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `TraitVariancePositionAdmitted` | TraitVariancePositionAdmitted | a variance marker is admitted only on a trait type parameter in the current Stable profile; an \`out\` parameter occurs only in producer/covariant positions and an \`in\` parameter only in consumer/contravariant positions after alias expansion; unmarked parameters are invariant; any declaration-role or use-position violation emits VARIANCE_ONLY_ALLOWED_ON_TRAIT_TYPE_PARAMETER | `DESIGN_STATIC_NOT_RUN` |
| `TransferableAcrossIsolation` | Transferable | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `TupleOrdinalProjectionAdmitted` | TupleOrdinalProjectionAdmitted | Admits a compile-time one-based tuple ordinal in 1..arity. | `DESIGN_STATIC_NOT_RUN` |
| `TypeParamKindAdmitted` | TypeParamKindAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `TypeSchemaConstructionAdmitted` | TypeSchemaConstructionAdmitted | the materialization head resolves to a type; the type exposes an admitted ConstructionRow; schema labels and ownership pass ConstructionRowAdmitted | `DESIGN_STATIC_NOT_RUN` |
| `TypeSideSelectorUsesDoubleColon` | TypeSideSelectorUsesDoubleColon | Type-side selector and call resolve through \`::\`. | `DESIGN_STATIC_NOT_RUN` |
| `TypeTokenAuthorityAdmitted` | TypeTokenAuthorityAdmitted | source_kind is Type and normalized_type identifies a compile-time type identity; runtime_value_use, storage_use, static_sample_evaluation, and reflection_request are all false; authority is empty; a type token grants no constructor, provider, FFI, filesystem, network, or reflection authority; only type position, static selector, and descriptor projection contexts are admitted | `DESIGN_STATIC_NOT_RUN` |
| `TypedMaterializationTargetAdmitted` | TypedMaterializationTargetAdmitted | source_kind is Type; normalized_type is resolved; construction_domain is typed_materialization | `DESIGN_STATIC_NOT_RUN` |
| `TypeofStaticSampleAdmitted` | TypeofStaticSampleAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `UnitCanonicalizationAdmitted` | UnitCanonicalizationAdmitted | every base unit resolves to a declared dimension vector and exact rational scale; multiplication adds vectors and multiplies scales; division subtracts vectors and divides scales; only StaticInt powers are admitted and multiply dimension exponents while raising the exact scale; zero exponents are removed and dimension entries are sorted by canonical dimension identity; type equality compares the normalized vector and exact scale only; display aliases are excluded | `DESIGN_STATIC_NOT_RUN` |
| `UnitCatalogExactRatioAdmitted` | UnitCatalogExactRatioAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `UnitOperationPolicyCoreAdmitted` | UnitOperationPolicyCoreAdmitted | R51a1 closed design algorithm for UnitOperationPolicyCoreAdmitted; product checker NOT_RUN. | `DESIGN_ALGORITHM_STATIC_NOT_RUN` |
| `UnsafeAxisSeparated` | UnsafeAxisSeparated | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `UnsafeBoundaryAdmitted` | unsafe boundary | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `UserUnitCatalogAdmitted` | UserUnitCatalogAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `VectorDotProductAdmitted` | Vector dot product | both operands are rank-1; the vector lengths are equal; \`*+\` participates in the left-to-right LinearProductExpr fold and this predicate is applied independently at the current fold step | `DESIGN_STATIC_NOT_RUN` |
| `WherePredicateAdmitted` | WherePredicateAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `WhereRelationTaxonomyAdmitted` | WhereRelationTaxonomyAdmitted | R51a1 checker-predicate design seed; product checker NOT_RUN. | `DESIGN_STATIC_NOT_RUN` |
| `WitnessCoherent` | WitnessCoherent | ordered branch 1: a missing witness_id, implementation_id, coherence_key, or empty candidate_implementation_ids emits WITNESS_COHERENCE_EVIDENCE_MISSING; ordered branch 2: coherence_key unequal to witness_id, or candidate_implementation_ids has exactly one element and that sole candidate is unequal to implementation_id, emits WITNESS_IMPLEMENTATION_SELECTION_MISMATCH; ordered branch 3: more than one candidate implementation emits WITNESS_DUPLICATE_IN_COHERENCE_DOMAIN; ordered branch 4: orphan_rule_admitted is false or declaring_package equals neither type_owner nor trait_owner emits WITNESS_ORPHAN_RULE_VIOLATION; only after all four branches pass is the witness/implementation pair coherent | `DESIGN_STATIC_NOT_RUN` |
| `WitnessResolution` | WitnessResolution | resolve conformance obligations deterministically without structural or extension auto-witness | `DESIGN_STATIC_NOT_RUN` |
| `WitnessResponsibilityCompatibility` | WitnessResponsibilityCompatibility | witness method responsibility must not be wider than requirement | `DESIGN_STATIC_NOT_RUN` |
