# Deeplus 0.1.2-baseline.r51f3 Example Review Corpus

This current-only design corpus is generated from one source model. Product parser/checker execution is `NOT_RUN`.

## EX-R48-001 — Column-vector semicolon stable shorthand

- **source_feature_ids:** `numeric_array_shape_inferred_column_vector_semicolon_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let row = #[1, 2, 3]
let column = #[1; 2; 3]
let explicit = #3,1[
    1;
    2;
    3;
]
```
## EX-R48-002 — Column-vector malformed mixed separator rejected

- **source_feature_ids:** `numeric_array_shape_inferred_column_vector_semicolon_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = #[1, 2; 3]
// COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED
```
## EX-R48-003 — NumericArray same-shape elementwise arithmetic

- **source_feature_ids:** `numeric_array_elementwise_arithmetic_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a = #2,2[
    1, 2;
    3, 4;
]
let b = #2,2[
    10, 20;
    30, 40;
]
let sum = a + b
let hadamard = a * b
```
## EX-R48-004 — Vector dot product stable operator

- **source_feature_ids:** `vector_dot_product_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let u = #[1, 2, 3]
let v = #[4, 5, 6]
let d = u *+ v
```
## EX-R48-005 — Matrix multiplication stable operator

- **source_feature_ids:** `matrix_multiplication_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a = #2,3[
    1, 2, 3;
    4, 5, 6;
]
let b = #3,2[
    7, 8;
    9, 10;
    11, 12;
]
let product = a ** b
```
## EX-R48-006 — Caret power stable operator

- **source_feature_ids:** `caret_power_operator_msp`, `measure_static_power_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si
let scalar = 2 ^ 10
let area = 3[m] ^ 2
```
## EX-R48-007 — Basic index operator stable core

- **source_feature_ids:** `index_operator`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let xs = #[10, 20, 30]
let second = xs[2]
```
## EX-R48-008 — NumericArray context anchor stable MSP

- **source_feature_ids:** `numeric_array_context_anchor_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let matrix = #2,3[
    1, 2, 3;
    4, 5, 6;
]
let row = #[10, 20, 30]
let adjusted = &matrix + row
```
## EX-R48-009 — Measure literal and unit catalog stable core

- **source_feature_ids:** `measure_literal_msp`, `unit_catalog_resolution_msp`, `qualified_unit_symbol_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si
let distance = 13[cm]
let time = 2[s]
let speed = distance / time
```
## EX-R48-010 — Unit operation policy exact conversion stable core

- **source_feature_ids:** `unit_operation_policy_msp`, `exact_ratio_unit_conversion_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si
let d = 2500[m]
let km = d ~ asUnit(1[km])
let scalar = d ~ scalarIn(1[m])
```
## EX-R48-011 — Type schema construction and derivation

- **source_feature_ids:** `named_constructor_external_call_msp`, `prototype_derivation_without_dollar`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(id: UserId!(1), name: "Kim")
let renamed = user!{
    name: "Lee"
}
```
## EX-R48-012 — Map unfold double star current

- **source_feature_ids:** `map_unfold_double_star_current`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let defaults = #map{
    "host": "localhost"
    "port": "8080"
}
let actual = #map{
    **defaults
    "port": "443"
}
```
## EX-R48-013 — Declarative function clause with otherwise

- **source_feature_ids:** `declarative_function_clause_block_msp`, `clause_otherwise_default_head`, `guard_function_for_clause_predicates`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def sign(n: Int) -> Int = {{
    n if n < 0  => -1
    n if n == 0 => 0
    otherwise => 1
}}
```
## EX-R48-014 — Clause pattern heads stable

- **source_feature_ids:** `clause_pattern_heads`, `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def safeHead<T>(xs: List<T>) -> Option<T> = {{
    []       => ::none
    [x, .._] => ::some(x)
}}
```
## EX-R48-015 — Explicit context parameter stable phase A

- **source_feature_ids:** `explicit_context_parameter_msp`, `explicit_context_argument_keyword_spelling`, `context_keyword_contextual_token`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def format(value: Float64, context pattern: FormatPattern) -> String = {
    return pattern ~ render value
}
let s = format(3.14, context FormatPattern!("{:.2f}"))
```
## EX-R48-016 — Named extension set and qualified selector

- **source_feature_ids:** `named_extension_set_block_msp`, `qualified_extension_selector_call_msp`, `scoped_extension_activation_use`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension Int as metric {
    +def m() -> Length = { return Length!(value: self, unit: Unit::meter) }
}
use Int::metric
let a = 3 ~ m
let b = 3 ~ Int::metric::m
```
## EX-R48-017 — Member/extension collision is error

- **source_feature_ids:** `member_extension_collision_error_policy`, `method_extension_resolution_policy`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MEMBER_EXTENSION_COLLISION`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use text::extensions::words
let words = text ~ words
// MEMBER_EXTENSION_COLLISION
```
## EX-R48-018 — Generic responsibility quantification

- **source_feature_ids:** `generic_parameter_model_phase_a`, `generic_invariance_default_law`, `where_conforms_constraint_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def render<T>(x: T) -> String
    throws Never
    effects {}
    where T conforms Display
= {
    return x ~ display
}
```
## EX-R48-020 — Effect and error row polymorphism stable

- **source_feature_ids:** `effect_error_row_polymorphism_phase_a`, `named_effect_capability_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def withLog<T, E, ρ>(body: () -> T throws E effects ρ) -> T
    throws E
    effects ρ | {io}
= {
    log("start")
    return body()
}
```
## EX-R48-021 — At-control expression restored

- **source_feature_ids:** `at_control_expression_family`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let status = @if ready {
    200
} else {
    503
}
```
## EX-R48-022 — Generator expression restored

- **source_feature_ids:** `generator_expression_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let positives = @for n in numbers {
    if n > 0 {
        yield n
    }
}
```
## EX-R48-023 — Refinement and as? Option law

- **source_feature_ids:** `refinement_type_phase_a`, `range_literal_refinement_type`, `as_question_returns_option`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type Port = 0..65_535
let maybePort: Option<Port> = raw as? Port
```
## EX-R48-024 — Closure capture descriptor stable current law

- **source_feature_ids:** `closure_capture_descriptor_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = [once token] { value =>
    ret token ~ consumeWith value
}
```
## EX-R48-025 — Nested local function stable

- **source_feature_ids:** `nested_function_local_def_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def outer(x: Int) -> Int = {
    def#pure inner(y: Int) -> Int = return y + 1
    return inner(x)
}
```
## EX-R48-026 — FFI remains preview-gated

- **source_feature_ids:** `ffi_minimum_sound_profile`, `ffi_c_extern_unsafe_surface_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept_with_gate`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```
## EX-R48-028 — Generic invariance rejects broad container covariance

- **source_feature_ids:** `generic_invariance_default_law`, `generic_parameter_model_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GENERIC_TYPE_CONSTRUCTOR_INVARIANT_BY_DEFAULT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let dogs: MutableList<Dog> = #mut[Dog!()]
let animals: MutableList<Animal> = dogs
// GENERIC_TYPE_CONSTRUCTOR_INVARIANT_BY_DEFAULT
```
## EX-R48-029 — Trait-only variance producer surface

- **source_feature_ids:** `generic_variance_phase_b_trait_only`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Source<out T> {
    +def next+() -> Option<T>
        throws Never
        effects {}
}
```
## EX-R48-030 — Trait variance consumer-position misuse rejected

- **source_feature_ids:** `generic_variance_phase_b_trait_only`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `VARIANCE_ONLY_ALLOWED_ON_TRAIT_TYPE_PARAMETER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait BadSource<out T> {
    +def put+(value: T) -> Unit
        throws Never
        effects {}
}
// VARIANCE_ONLY_ALLOWED_ON_TRAIT_TYPE_PARAMETER
```
## EX-R48-031 — Result and throws cannot duplicate recoverable error channel

- **source_feature_ids:** `result_throws_overlap_forbidden_law`, `result_error_set_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RESULT_THROWS_CHANNEL_OVERLAP`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def parse(text: String) -> Result<User, error ParseError>
    throws ParseError
    effects {}
= {
    return ::err(ParseError::invalid)
}
// RESULT_THROWS_CHANNEL_OVERLAP
```
## EX-R48-032 — Unsafe is not an EffectRow atom

- **source_feature_ids:** `unsafe_boundary_surface`, `effectrow_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EFFECTROW_UNSAFE_AXIS_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def read(ptr: RawPtr) -> Int
    throws Never
    effects {unsafe}
= {
    return 0
}
// EFFECTROW_UNSAFE_AXIS_FORBIDDEN
```
## EX-R48-033 — Context parameter role is part of function type identity

- **source_feature_ids:** `explicit_context_parameter_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def format(value: Float64, context fmt: FormatPattern) -> String
    throws Never
    effects {}
= { return fmt ~ render value }
```
## EX-R48-034 — Ordinary argument cannot satisfy context role

- **source_feature_ids:** `explicit_context_parameter_msp`, `context_value_admissibility`, `explicit_context_parameter_role_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONTEXT_ARGUMENT_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = format(3.14, FormatPattern!("{:.2f}"))
// CONTEXT_ARGUMENT_REQUIRED
```
## EX-R48-035 — Measure literal requires active unit catalog authority

- **source_feature_ids:** `measure_literal_msp`, `unit_catalog_resolution_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si
let length = 13[cm]
let area = 3[m] ^ 2
```
## EX-R48-036 — Active extension does not form trait witness

- **source_feature_ids:** `method_extension_resolution_policy`, `trait_witness_coherence_phase_a`, `extension_auto_witness_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXTENSION_CANNOT_FULFILL_TRAIT_REQUIREMENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use app::text::DisplayExtensions
let printable: Display = user
// EXTENSION_CANNOT_FULFILL_TRAIT_REQUIREMENT
```
## EX-R48-037 — as? returns Option and check returns Result

- **source_feature_ids:** `as_question_returns_option`, `refinement_checked_boundary`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let maybePort: Option<Port> = raw as? Port
let checkedPort: Result<Port, error RefinementError> = Port::check(raw)
```
## EX-R48-038 — typeof measure sample preserves UnitCatalog authority

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`, `measure_literal_msp`, `unit_catalog_resolution_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si

type Meter = typeof 1[m]
public def move(distance: Meter) -> Unit
    throws Never
    effects {}
= {
}
```
## EX-R48-040 — typeof invalid runtime/static-sample boundary

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type T = typeof 0
```
## EX-R48-041 — typeof call form is forbidden

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPEOF_CALL_FORM_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type T = typeof([0, ""])
// TYPEOF_CALL_FORM_FORBIDDEN
```
## EX-R48-042 — Ordinary trailing closure preserves call responsibility

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def squareWith(a: Int, body: (Int) -> Int) -> Int
    throws Never
    effects {}
= { return body(a) }

let y = squareWith 10 { x => x * x }
```
## EX-R48-043 — Message trailing closure omits only the comma

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let total = items ~ fold 0 { acc, x => acc + x }
```
## EX-R48-044 — Bare ordinary call remains not-current

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BARE_FUNCTION_CALL_REQUIRES_TRAILING_CLOSURE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let y = f 10
// BARE_FUNCTION_CALL_REQUIRES_TRAILING_CLOSURE
```
## EX-R48-045 — Named constructor external call uses new by default

- **source_feature_ids:** `named_constructor_surface_msp`, `named_constructor_external_call_msp`, `root_new_super_delegation_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class UserId {
    +let raw: Int

    +def! new(raw: Int)
        : super!()
    = {
        self.raw = raw
    }
}

let id = UserId!(1)
```
## EX-R48-046 — Header constructor delegation is post-init

- **source_feature_ids:** `named_constructor_surface_msp`, `constructor_delegation_decision_list_msp`, `primary_constructor_root_new_law`, `root_new_super_delegation_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class User {
    +let id: UserId
    +let name: String
    +var source: String

    +def! new(id: UserId, name: String)
        : super!()
    = {
        self.id = id
        self.name = name
        self.source = "new"
    }

    +def! fromPair(pair: Pair<UserId, String>)
        : new(pair.first, pair.second)
    = {
        self.source = "fromPair"
    }
}
```
## EX-R48-047 — Constructor delegation list cannot mix same-type and super targets

- **source_feature_ids:** `constructor_delegation_decision_list_msp`, `constructor_delegation_target_kind_separation_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONSTRUCTOR_DELEGATION_MIXES_SAME_TYPE_AND_SUPER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Bad {
    +def! new(data: Data)
        :
            new(data.id) if data.hasOwnFields
            super!(data.id)
    = {
    }
}
// CONSTRUCTOR_DELEGATION_MIXES_SAME_TYPE_AND_SUPER
```
## EX-R48B-048 — External named constructor call uses Type!name explicitly

- **source_feature_ids:** `named_constructor_surface_msp`, `named_constructor_external_call_msp`, `construction_responsibility_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class UserId {
    +let raw: Int

    +def! new(raw: Int)
        : super!()
    = {
        self.raw = raw
    }

    +def! fromText(text: String)
        : new(text ~ parseInt)
    = {
    }
}

let direct = UserId!(1)
let parsed = UserId!fromText("42")
```
## EX-R48B-050 — Trailing closure requires a closure parameter suffix

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRAILING_CLOSURE_REQUIRES_FUNCTION_PARAMETER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def g(a: Int) -> Int = { a }
let y = g 10 { x => x }
// TRAILING_CLOSURE_REQUIRES_FUNCTION_PARAMETER
```
## EX-R48B-051 — Constructor delegation cycle is rejected

- **source_feature_ids:** `constructor_delegation_decision_list_msp`, `primary_constructor_root_new_law`, `construction_responsibility_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONSTRUCTOR_DELEGATION_CYCLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Loop {
    +def! fromData(data: Data)
        : init(data.raw)
    = {
    }

    +def! init(raw: Bytes)
        : fromData(decodeData(raw))
    = {
    }
}
// CONSTRUCTOR_DELEGATION_CYCLE
```
## EX-R48B-052 — Option explicit flow stdlib profile replaces optional chaining

- **source_feature_ids:** `std_option_explicit_flow_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::option::flow

let name = userOpt ~ andThen { user => user.profile } ~ map { profile => profile.name }
```
## EX-R48B-055 — Option T? and double-colon case canonicalization

- **source_feature_ids:** `option_question_mark_type_surface`, `option_result_double_colon_case_surface`, `std_option_explicit_flow_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let present: Int? = ::some(13)
let absent: Int? = ::none
let normalized: Option<Int> = ::some(21)
```
## EX-R48B-056 — Canonical Option cases use double colon

- **source_feature_ids:** `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x: Int? = ::some(13)
let y: Int? = ::none
```
## EX-R48B-057 — Char/String current text law

- **source_feature_ids:** `unicode_char_literal_single_quote_msp`, `unicode_escape_scalar_braced_msp`, `no_string_char_bytes_implicit_conversion_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let c: Char = '가'
let smile: Char = '\u{1F642}'
let s: String = "가"
```
## EX-R48B-058 — Bytes literal current Stable form

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let magic: Bytes = #bytes"\x89PNG\x0D\x0A"
```
## EX-R48B-059 — Bytes literal is Stable and ungated

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let b: Bytes = #bytes"\x41\x42"
```
## EX-R48B-060 — Explicit return, def#pure, and lambda ret

- **source_feature_ids:** `named_function_explicit_return_policy`, `one_line_return_body`, `pure_function_profile_def_hash_pure`, `lambda_block_explicit_ret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#pure add(a: Int, b: Int) = return a + b
let inc = { x: Int => x + 1 }
let withLog = { x: Int =>
    log(x)
    ret x + 1
}
```
## EX-R48B-061 — Named function expression body is rejected

- **source_feature_ids:** `named_function_explicit_return_policy`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#pure add(a: Int, b: Int) = a + b
```
## EX-R48B-062 — Lambda block without ret is rejected

- **source_feature_ids:** `lambda_block_explicit_ret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LAMBDA_BLOCK_REQUIRES_RET`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = { x: Int =>
    log(x)
    x + 1
}
```
## EX-R48B-063 — Type schema construction restored as schema domain

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_construction_vs_constructor_domain_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User${
    id: UserId!(1)
    name: "Kim"
}

let constructed = User!(id: UserId!(1), name: "Kim")
```
## EX-R48B-064 — All-named argument layout preview

- **source_feature_ids:** `all_named_argument_layout_separator_msp`, `named_constructor_external_call_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(
    id: UserId!(1)
    name: "Kim"
)
```
## EX-R48B-065 — Rightward dollar local binding preview

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def parseAndPrint() -> Unit = {
    readLine() ~ trim ~ toInt -> $value
    print(value)
}
```
## EX-R48B-066 — Rightward dollar-local flow binding is current

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def readValue() -> String = {
    readLine() -> $value
    return value
}
```
## EX-R48B-067 — String interpolation stable core

- **source_feature_ids:** `string_interpolation_braced_expr_core`, `interpolation_path_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let s1 = "value:$value"
let s2 = "name:${user.name}"
```
## EX-R48B-068 — String interpolation factor and format current form

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`, `string_interpolation_format_spec_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let s = "$i-th value is $a[i]; padded=${name:<12}"
```
## EX-R48B-069 — String interpolation dot shorthand is accepted

- **source_feature_ids:** `interpolation_path_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let s = "$user.name"
```
## EX-R48C-070 — Module and static path boundary is stable

- **source_feature_ids:** `module_keyword_source_header`, `double_colon_static_qualified_path`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module app::main

import std::math::{sin, cos}
use std::units::si

let x = math::sin(1.0)
let d = 1[m]
```
## EX-R48C-071 — Dotted static path rejected

- **source_feature_ids:** `double_colon_static_qualified_path`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DOT_NOT_ALLOWED_IN_IMPORT_PATH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
import std::math
// DOT_NOT_ALLOWED_IN_IMPORT_PATH
```
## EX-R48C-072 — Strict and sequential Boolean forms

- **source_feature_ids:** `strict_boolean_word_operators_msp`, `sequential_boolean_control_words_msp`, `ordered_comparison_chain_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if isReady and isValid {
    commit()
}

if 1 <= i <= xs.length and then xs[i] == 0 {
    handleZero(i)
}

if cacheHit otherwise loadAllowed {
    serve()
}
```
## EX-R48C-073 — Bool && is not logical AND

- **source_feature_ids:** `legacy_logical_and_or_operator_removed`, `double_glyph_bitwise_operator_family_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LEGACY_LOGICAL_AND_OPERATOR_REMOVED_ON_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a: Bool = true
let b: Bool = false
let c = a && b
// LEGACY_LOGICAL_AND_OPERATOR_REMOVED_ON_BOOL
```
## EX-R48C-074 — Double-glyph bitwise operators stable

- **source_feature_ids:** `double_glyph_bitwise_operator_family_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a: UInt8 = 0b1010
let b: UInt8 = 0b1100

let c = a && b
let d = a || b
let e = a ^^ b
let f = ~~a
```
## EX-R48C-075 — Bitwise result is not Bool

- **source_feature_ids:** `double_glyph_bitwise_operator_family_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BITWISE_RESULT_USED_AS_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if flags && Mask::readable {
    allow()
}
// BITWISE_RESULT_USED_AS_BOOL
```
## EX-R48C-076 — Control-transfer guard clauses stable

- **source_feature_ids:** `control_transfer_guard_clause_msp`, `guard_condition_pure_predicate_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#pure clamp(x: Int) -> Int
= {
    return 0 if x < 0
    return 100 if x > 100
    return x
}
```
## EX-R48C-077 — Guard clause is not general postfix if

- **source_feature_ids:** `control_transfer_guard_clause_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GUARD_CLAUSE_NOT_ALLOWED_HERE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
print(x) if debug
// GUARD_CLAUSE_NOT_ALLOWED_HERE
```
## EX-R48C-079 — Loop outcome match tagged and exhaustive

- **source_feature_ids:** `loop_outcome_match_statement_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for x in xs {
    if x == 0 {
        break 1
    }
}
match {
    ::break(v) => print(v)
    ::completed => ()
}
```
## EX-R48C-080 — Raw payload in loop outcome match rejected

- **source_feature_ids:** `loop_outcome_match_statement_msp`, `loop_outcome_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for x in xs {
    if cond {
        break false
    }
}
match {
    false => handleFalse()
    otherwise => ()
}
// LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE
```
## EX-R48C-083 — Conformance declaration creates checker-visible witness

- **source_feature_ids:** `conformance_declaration_surface`, `trait_witness_formal_judgment_core`, `trait_witness_resolution_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Display {
    +def display+() -> String
        throws Never
        effects {}
}

public conformance UserId conforms Display {
    +def display+() -> String
        throws Never
        effects {}
    = {
        return self.raw
    }
}
```
## EX-R48C-085 — Associated projection requires explicit trait context

- **source_feature_ids:** `trait_associated_projection_explicit_context`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def first<I>(it: I) -> <I as Iterator>::Item?
    throws Never
    effects {}
    where I conforms Iterator
= {
    return it ~ next
}
```
## EX-R48C-086 — Bare associated projection rejected

- **source_feature_ids:** `trait_associated_projection_explicit_context`, `associated_projection_colon_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRAIT_ASSOCIATED_PROJECTION_REQUIRES_TRAIT_CONTEXT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def bad<I>(it: I) -> I.Item
    where I conforms Iterator
= {
    return it ~ next
}
// TRAIT_ASSOCIATED_PROJECTION_REQUIRES_TRAIT_CONTEXT
```
## EX-R48C-087 — Extension does not create trait witness

- **source_feature_ids:** `extension_auto_witness_forbidden_law`, `structural_conformance_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXTENSION_AUTO_WITNESS_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension User as DisplayExtension {
    +def display() -> String
        throws Never
        effects {}
    = {
        return "user"
    }
}

let s = render(User!())
// EXTENSION_AUTO_WITNESS_FORBIDDEN
```
## EX-R48C-088 — Explicit witness parameter cannot escape

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def leakOrd<T>(using ord: witness Ord<T>) -> Unit
    throws Never
    effects {}
= {
    return ord
}
// EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN
```
## EX-R48C-089 — any Trait existential requires safety and binding

- **source_feature_ids:** `any_trait_existential_minimal_core`, `trait_existential_safety_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let it: any Iterator where Item == Int = IntRange!(start: 0, end: 10)
let value = it ~ next
```
## EX-R48C-090 — some Trait remains gated

- **source_feature_ids:** `some_trait_opaque_result_preview`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def makeShape() -> some Drawable
= {
    return Circle!(radius: 10.0)
}
```
## EX-R48C-091 — Yield guard preview positive with gate

- **source_feature_ids:** `yield_guard_clause_preview`, `generator_expression_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let visibleValues = @for value in values {
    yield value if value.visible
}
```
## EX-R48E-001 — `typeof` stable static-sample type projection

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si

type Meter = typeof 1[m]
type Vec3 = typeof #[1, 2, 3]
public def move(distance: Meter) = return distance ~ scalarIn(1[m])
```
## EX-R48E-002 — `typeof` still rejects runtime/effectful samples

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPEOF_SAMPLE_REQUIRES_STATIC_SAMPLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x = 1
type Bad = typeof x
// TYPEOF_SAMPLE_REQUIRES_STATIC_SAMPLE
```
## EX-R48E-003 — Trailing closure is stable but bare ordinary parenless call remains rejected

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let squares = values ~ map { x => x * x }
let total = values ~ fold 0 { acc, x => acc + x }
```
## EX-R48E-005 — Rightward flow `$name` local binding is stable and statement-only

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def readCount() -> Int = {
    readLine() ~ trim ~ toInt -> $count
    return count
}
```
## EX-R48E-006 — Old rightward `-> let` target remains removed

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FLOW_BINDING_ARROW_LET_REMOVED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
readLine() -> let value
// FLOW_BINDING_ARROW_LET_REMOVED
```
## EX-R48E-007 — String interpolation factor and format spec are stable

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`, `string_interpolation_format_spec_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = "name:$userName score:${score:>3} item:$items[i]"
let member = "${user.profile.name}"
```
## EX-R48E-008 — Interpolation shorthand dot stops before member access

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`, `interpolation_path_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = "$user.name"
```
## EX-R48E-009 — Bytes literal and named Unicode escape are stable design

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`, `unicode_named_escape_msp`, `unicode_char_literal_single_quote_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let marker: Char = '\N{COPYRIGHT SIGN}'
let raw: Bytes = #bytes"\x41\x42"
```
## EX-R48E-010 — Option visible `::some` elision is stable only in explicit local target context

- **source_feature_ids:** `option_visible_some_elision_msp`, `option_question_mark_type_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let chosen: Int? = 13
let absent: Int? = ::none
```
## EX-R48E-011 — Broad Option implicit lift remains rejected outside visible local target

- **source_feature_ids:** `option_visible_some_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_IMPLICIT_LIFT_NOT_ALLOWED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
return 13
// OPTION_IMPLICIT_LIFT_NOT_ALLOWED
```
## EX-R48E-012 — Pure elision is stable only when the body is proven pure

- **source_feature_ids:** `pure_elision_return_body_msp`, `pure_function_profile_def_hash_pure`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def add(a: Int, b: Int) = return a + b
```
## EX-R48E-013 — Pure elision rejects hidden effects

- **source_feature_ids:** `pure_elision_return_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `IMPLICIT_PURE_FUNCTION_HAS_EFFECTS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def readName() = return readLine()
// IMPLICIT_PURE_FUNCTION_HAS_EFFECTS
```
## EX-R48E-014 — Type schema construction is distinct from constructor domain

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_construction_vs_constructor_domain_law`, `type_schema_declaration_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema UserRow {
    id: UserId
    name: String
    active: Bool = true
}

let row = UserRow${
    id: UserId!(13)
    name: "Sing"
}
```
## EX-R48E-015 — Type schema construction cannot target undeclared labels

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_declaration_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let row = UserRow${
    id: UserId!(13)
    unknown: "x"
}
// TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD
```
## EX-R48E-016 — Closure call modes are stable responsibility descriptors

- **source_feature_ids:** `r51e_package_current_canonical_authority`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def withLock<T>(lock: Lock, body: #scoped (Guard) -> T) -> T
    throws Never
    effects {}
= {
    return lock ~ scoped(body)
}
```
## EX-R48E-017 — Async/await minimal core is language-design stable

- **source_feature_ids:** `async_function_declaration_surface`, `await_expression_surface`, `async_task_control`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#async loadUser(id: UserId) -> User
    throws NetworkError
    effects { Network }
= {
    return await service ~ fetchUser(id)
}
```
## EX-R48E-018 — Structured task scope makes cancellation owner visible

- **source_feature_ids:** `structured_task_scope`, `deterministic_primary_suppressed_order`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
task scope {
    let profile = spawn async { => await loadProfile(id) }
    let settings = spawn async { => await loadSettings(id) }
    await profile
    await settings
}
```
## EX-R48E-019 — Actor protocol request/reply is not ordinary method dispatch

- **source_feature_ids:** `actor_declaration_grammar_closed`, `actor_protocol_family`, `actor_request_reply`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public protocol CounterProtocol {
    request get() -> Int
    send increment(by: Int)
}
```
## EX-R48E-021 — First-class raw Witness values are still not current source

- **source_feature_ids:** `trait_witness_coherence_phase_a`, `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RAW_WITNESS_VALUE_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let w = witness Display for UserId
// RAW_WITNESS_VALUE_NOT_CURRENT
```
## EX-R48E-022 — Opaque `some Trait` result is stable under single-concrete-return law

- **source_feature_ids:** `some_trait_opaque_result_preview`, `explicit_conformance`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def makeShape() -> some Drawable
    throws Never
    effects {}
= {
    return Circle!(radius: 10.0)
}
```
## EX-R48E-023 — Opaque `some Trait` rejects multiple concrete returns

- **source_feature_ids:** `some_trait_opaque_result_preview`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPAQUE_RESULT_CONCRETE_TYPE_MISMATCH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def makeShape(flag: Bool) -> some Drawable
    throws Never
    effects {}
= {
    if flag {
        return Circle!(radius: 10.0)
    }
    return Rect!(width: 4.0, height: 5.0)
}
// OPAQUE_RESULT_CONCRETE_TYPE_MISMATCH
```
## EX-R48E-024 — Loop outcome match is tagged and exhaustive

- **source_feature_ids:** `loop_outcome_match_statement_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for x in xs {
    if x == 0 {
        break x
    }
}
match {
    ::break(v) => print(v)
    ::completed => ()
}
```
## EX-R48E-092 — Schema construction requires schema authority

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `schema_construction_authority_and_visibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPE_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_AUTHORITY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
private class SecretHandle {
    -let raw: RawHandle
}

let bad = SecretHandle${ raw: RawHandle!(0) }
// TYPE_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_AUTHORITY
```
## EX-R48E-093 — Schema construction cannot call constructor-domain init

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_construction_vs_constructor_domain_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SCHEMA_CONSTRUCTION_CANNOT_INVOKE_CONSTRUCTOR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Socket {
    +def! new(path: String) throws IOError effects { IO } = {
        // opens an OS resource
    }
}

let bad = Socket${ path: "/tmp/sock" }
// SCHEMA_CONSTRUCTION_CANNOT_INVOKE_CONSTRUCTOR
```
## EX-R48E-094 — Schema construction preserves public API field residue

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `schema_construction_public_api_projection_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Config {
    +let endpoint: Url
    +let retryCount: Int
}

public let defaultConfig = Config${
    endpoint: Url!("https://example.com")
    retryCount: 3
}
```
## EX-R48E-095 — Schema construction and derivation remain separate

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `shallow_same_type_derivation`, `deep_same_type_derivation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let base = RetryPolicy${ attempts: 3, backoffMillis: 200 }
let adjusted = base!{ attempts: 5 }
let nested = serviceConfig!!{ retryPolicy: serviceConfig.retryPolicy!!{ attempts: 5 } }
```
## EX-R48E1-001 — Standalone Boolean negation uses word not

- **source_feature_ids:** `standalone_bang_not_current_not_word_law`, `strict_boolean_word_operators_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def checkReady(ready: Bool) -> Unit
    throws Never
    effects {}
= {
    if not ready {
    }
}
```
## EX-R48E1-002 — Standalone bang Boolean negation is rejected

- **source_feature_ids:** `standalone_bang_not_current_not_word_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `STANDALONE_BANG_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def checkReady(ready: Bool) -> Unit
    throws Never
    effects {}
= {
    if !ready {
    }
    // STANDALONE_BANG_NOT_CURRENT
}
```
## EX-R48E1-003 — Typed schema construction is current schema domain

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `schema_construction_authority_and_visibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema UserProfile {
    name: String
    age: Int?
}
let profile = UserProfile${
    name: "Kim"
    age: ::some(33)
}
```
## EX-R48E1-004 — Type dollar is not constructor alias for ordinary class

- **source_feature_ids:** `type_schema_construction_vs_constructor_domain_law`, `type_schema_construction_dollar_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPE_DOLLAR_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_TYPE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class User {
    +def! new(name: String) = { self.name = name }
}
let user = User${
    name: "Kim"
}
// TYPE_DOLLAR_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_TYPE
```
## EX-R48E1-005 — All named call layout separator stable

- **source_feature_ids:** `all_named_argument_layout_separator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(
    name: "Kim"
    age: ::some(33)
)
```
## EX-R48E1-006 — Positional layout argument separator is rejected

- **source_feature_ids:** `all_named_argument_layout_separator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LAYOUT_ARG_SEPARATOR_REQUIRES_ALL_NAMED_ARGUMENTS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let pair = Pair!(
    1
    2
)
// LAYOUT_ARG_SEPARATOR_REQUIRES_ALL_NAMED_ARGUMENTS
```
## EX-R48E1-007 — Rightward flow binding is stable dollar local

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def readTrimmedLine() -> String = {
    readLine() ~ trim -> $line
    return line
}
```
## EX-R48E1-008 — Old rightward let target is rejected

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FLOW_BINDING_ARROW_LET_REMOVED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
readLine() -> let line
// FLOW_BINDING_ARROW_LET_REMOVED
```
## EX-R48E1-009 — String interpolation factor and format are stable

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`, `string_interpolation_format_spec_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let name = "Dee"
let scores = #[10, 20, 30]
let line = "user:$name score:${scores[1]:>3}"
```
## EX-R48E1-010 — Interpolation member shorthand requires braces

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`, `interpolation_path_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let line = "$user.name"
```
## EX-R48E1-011 — Bytes and named Unicode escape are stable design

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`, `unicode_named_escape_msp`, `no_string_char_bytes_implicit_conversion_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let copyright: Char = '\N{COPYRIGHT SIGN}'
let magic: Bytes = #bytes"\x89PNG\x0D\x0A"
```
## EX-R48E1-012 — String to Bytes implicit conversion is rejected

- **source_feature_ids:** `no_string_char_bytes_implicit_conversion_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `STRING_NOT_IMPLICITLY_CONVERTIBLE_TO_BYTES`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let raw: Bytes = "ABC"
// STRING_NOT_IMPLICITLY_CONVERTIBLE_TO_BYTES
```
## EX-R48E1-013 — Visible Option some elision at explicit local target

- **source_feature_ids:** `option_visible_some_elision_msp`, `option_question_mark_type_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let count: Int? = 3
let missing: Int? = ::none
```
## EX-R48E1-014 — Broad Option lift remains rejected

- **source_feature_ids:** `option_result_double_colon_case_surface`, `option_visible_some_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_IMPLICIT_LIFT_NOT_ALLOWED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def takesMaybe(x: Int?) -> Unit = { }
takesMaybe(3)
// OPTION_IMPLICIT_LIFT_NOT_ALLOWED
```
## EX-R48E1-016 — Ordinary expression body remains rejected

- **source_feature_ids:** `named_function_explicit_return_policy`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def add(a: Int, b: Int) = a + b
// FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN
```
## EX-R48E1-017 — Trailing closure suffix is stable

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let doubled = items ~ map { x => x * 2 }
let total = items ~ fold 0 { acc, x => acc + x }
```
## EX-R48E1-020 — typeof call form remains rejected

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPEOF_CALL_FORM_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type Bad = typeof([0, ""])
// TYPEOF_CALL_FORM_FORBIDDEN
```
## EX-R48E1-021 — Ternary spacing law with ordinary operands

- **source_feature_ids:** `ternary_conditional_expression`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let min = a < b ? a : b
let selected = cond ? x : y
```
## EX-R48E1-023 — R0 guard and source Boolean use word operators

- **source_feature_ids:** `r0_guard_predicate_calculus`, `strict_boolean_word_operators_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def admissible(value: Int, stale: Bool) -> Bool = {{
    value if not stale and value >= 0 => true
    otherwise => false
}}
```
## EX-R48E1-024 — Bool double glyph operator rejected

- **source_feature_ids:** `legacy_logical_and_or_operator_removed`, `double_glyph_bitwise_operator_family_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LEGACY_LOGICAL_AND_OPERATOR_REMOVED_ON_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let c = ready && allowed
// LEGACY_LOGICAL_AND_OPERATOR_REMOVED_ON_BOOL
```
## EX-R48E1-025 — Bitwise double glyph family stable

- **source_feature_ids:** `double_glyph_bitwise_operator_family_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a: UInt8 = 0b1010
let b: UInt8 = 0b1100
let c = a && b
let d = a || b
let e = a ^^ b
let f = ~~a
```
## EX-R48E1-027 — Raw loop outcome arm rejected

- **source_feature_ids:** `loop_outcome_match_statement_msp`, `loop_outcome_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for x in xs {
    if stop {
        break false
    }
}
match {
    false => handleFalse()
    otherwise => ()
}
// LOOP_OUTCOME_MATCH_REQUIRES_OUTCOME_CASE
```
## EX-R48E1-028 — Conformance declaration and explicit associated projection

- **source_feature_ids:** `explicit_conformance`, `trait_associated_projection_explicit_context`, `where_conforms_constraint_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Source {
    type Item
    +def next+() -> <Self as Source>::Item?
        throws Never
        effects {}
}
public def first<S>(source: S) -> <S as Source>::Item?
    throws Never
    effects {}
    where S conforms Source
= {
    return source ~ next
}
```
## EX-R48E1-029 — Structural conformance remains forbidden

- **source_feature_ids:** `structural_conformance_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public struct Logger {
    +def display+() -> String = { return "logger" }
}
public def render<T>(x: T) -> String
    throws Never
    effects {}
    where T conforms Display
= { return x ~ display }
let text = render(Logger!())
// STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN
```
## EX-R48E1-030 — Async task actor minimum core stable design

- **source_feature_ids:** `async_function_declaration_surface`, `await_expression_surface`, `structured_task_scope`, `actor_declaration_grammar_closed`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public protocol Work {
    request compute(input: Job) -> Result
}
public actor Worker {
    +request compute(input: Job) -> Result = {
        return process(input)
    }
}
public def#async run(job: Job) -> Result
    throws ActorMessageError
    effects {task}
= {
    let Result::ok(task) = Worker!() ~ compute(job)
    else Result::err(error) => throw error
    return await task
}
```
## EX-R48E1-031 — Dynamic unit conversion provider under stdlib profile

- **source_feature_ids:** `dynamic_unit_conversion_provider_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let converted = price ~ asUnitUsing(provider, 1[USD])
```
## EX-R48E1-032 — Raw first class witness remains not current

- **source_feature_ids:** `first_class_witness_value_not_current`, `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RAW_WITNESS_VALUE_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let w = witness Display for User
storeGlobal(w)
// RAW_WITNESS_VALUE_NOT_CURRENT
```
## EX-R48E1-033 — Standalone not in guard clause

- **source_feature_ids:** `control_transfer_guard_clause_msp`, `standalone_bang_not_current_not_word_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def chooseVisible(items: Sequence<Item>, value: Value, stale: Bool) -> Value = {
    for item in items {
        continue !if item.active
        return value if not stale
    }
    return value
}
```
## EX-R48E1-034 — Yield guard and arrow binding cannot coexist

- **source_feature_ids:** `yield_guard_clause_preview`, `rightward_flow_dollar_local_binding_msp`, `control_transfer_guard_clause_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GUARD_AND_RIGHTWARD_BINDING_CANNOT_COEXIST`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
yield value if ready -> $response
// GUARD_AND_RIGHTWARD_BINDING_CANNOT_COEXIST
```
## EX-R48F-001 — @match direct expression arm result is current

- **source_feature_ids:** `at_match_arm_single_expression_result_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    ::ready => "ready"
    ::failed(msg) => "failed:${msg}"
    otherwise => "unknown"
}
```
## EX-R48F-002 — @match block arm uses local ret

- **source_feature_ids:** `at_match_block_arm_local_ret_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match token {
    ::identifier(name) => {
        audit(name)
        ret name
    }
    otherwise => "other"
}
```
## EX-R48F-003 — return is not an @match arm result

- **source_feature_ids:** `at_match_arm_single_expression_result_law`, `at_match_block_arm_local_ret_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `AT_MATCH_ARM_RETURN_IS_NOT_RESULT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    ::ready => return "ready"
    otherwise => "other"
}
// AT_MATCH_ARM_RETURN_IS_NOT_RESULT
```
## EX-R48F-004 — match guard pure predicate

- **source_feature_ids:** `match_arm_guard_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sign = @match x {
    n if n > 0 => "positive"
    n if n == 0 => "zero"
    n => "negative"
    otherwise => "other"
}
```
## EX-R48F-005 — guarded arm is not exhaustive alone

- **source_feature_ids:** `match_arm_guard_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MATCH_NONEXHAUSTIVE_AFTER_GUARDS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sign = @match x {
    n: Int if n > 0 => "positive"
}
// MATCH_NONEXHAUSTIVE_AFTER_GUARDS
```
## EX-R48F-006 — nullary lambda arrow elision with expected type

- **source_feature_ids:** `nullary_lambda_arrow_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let zero: () -> Int = { 0 }
let noop: () -> Unit = {}
```
## EX-R48F-007 — empty nullary lambda needs expected type

- **source_feature_ids:** `nullary_lambda_arrow_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EMPTY_NULLARY_LAMBDA_REQUIRES_EXPECTED_FUNCTION_TYPE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = {}
// EMPTY_NULLARY_LAMBDA_REQUIRES_EXPECTED_FUNCTION_TYPE
```
## EX-R48F-008 — implicit @ lambda placeholder stable one-parameter context

- **source_feature_ids:** `implicit_lambda_at_placeholder_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let positives = list ~ filter { @ > 0 }
let names = users ~ map { @.name }
```
## EX-R48F-009 — implicit @ requires expected one-parameter function context

- **source_feature_ids:** `implicit_lambda_at_placeholder_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `IMPLICIT_LAMBDA_ARG_REQUIRES_ONE_PARAM_CONTEXT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = { @ > 0 }
// IMPLICIT_LAMBDA_ARG_REQUIRES_ONE_PARAM_CONTEXT
```
## EX-R48F-010 — NumericArray postfix transpose is Stable

- **source_feature_ids:** `numeric_array_postfix_transpose_caret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let At = A^
let gram = A^ ** A
```
## EX-R48F-011 — Neutral vector transpose requires orientation witness

- **source_feature_ids:** `numeric_array_vector_orientation_witness_msp`, `numeric_array_postfix_transpose_caret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMARR_VECTOR_TRANSPOSE_REQUIRES_ORIENTATION`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = v^
// NUMARR_VECTOR_TRANSPOSE_REQUIRES_ORIENTATION
```
## EX-R48F-012 — Inclusive slice range canonical

- **source_feature_ids:** `inclusive_slice_range_canonical_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **expected_warnings:** `SLICE_HALF_OPEN_RANGE_NONCANONICAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let firstFour = xs[1..4]
let tail = xs[1..$]
let beforeLast = xs[1..<$]
```
## EX-R48F-013 — Half-open slice is noncanonical ordinary style

- **source_feature_ids:** `slice_half_open_noncanonical_warning_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **expected_warnings:** `SLICE_HALF_OPEN_RANGE_NONCANONICAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let window = xs[i..<j]
// warning: SLICE_HALF_OPEN_RANGE_NONCANONICAL
```
## EX-R48F-014 — Complex vector dot product law

- **source_feature_ids:** `linear_algebra_complex_inner_product_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let z = u *+ v
// For Complex Rep, *+ uses the current inner-product convention specified by std.numeric.complex.
```
## EX-R48F-015 — Drop-preserving existential packaging

- **source_feature_ids:** `drop_preserving_existential`, `explicit_existential_any_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let stream: any Readable = FileStream!(path: "data.txt")
// Packaging as any Readable preserves the underlying deterministic drop responsibility.
```
## EX-R48F-016 — Type schema construction is not constructor alias

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_construction_vs_constructor_domain_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema UserProfile {
    name: String
    age: Int?
}

let profile = UserProfile${
    name: "Kim"
    age: ::some(33)
}
```
## EX-R48F-017 — Type dollar is rejected when used as constructor alias

- **source_feature_ids:** `type_schema_construction_vs_constructor_domain_law`, `type_schema_construction_dollar_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPE_DOLLAR_IS_NOT_CONSTRUCTOR_ALIAS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User${
    id: UserId!(1)
    name: "Kim"
}
// TYPE_DOLLAR_IS_NOT_CONSTRUCTOR_ALIAS
```
## EX-R48F-018 — Ternary spacing law with ordinary operands

- **source_feature_ids:** `ternary_conditional_expression`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let min = a < b ? a : b
let chosen = cond ? x : y
```
## EX-R48F-020 — Stable typeof no preview gate

- **source_feature_ids:** `typeof_static_sample_type_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si

type Meter = typeof 1[m]
type Vec3 = typeof #[1, 2, 3]
```
## EX-R48F-021 — Stable trailing closure no preview gate

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let total = items ~ fold 0 { acc, x =>
    ret acc + x
}
```
## EX-R48F-022 — Stable #bytes literal

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let magic: Bytes = #bytes"\x89PNG\x0D\x0A\x1A\x0A"
```
## EX-R48F-025 — String interpolation factor and format are current

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`, `string_interpolation_format_spec_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let s = "$i-th value is $items[i]."
let row = "|${name:<12}| ${score:>3}"
```
## EX-R48F-027 — Async function and await are current design

- **source_feature_ids:** `async_function_declaration_surface`, `await_expression_surface`, `async_task_control`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#async loadUser(id: UserId) -> User
    throws NetworkError
    effects { Network }
= {
    return await client ~ fetchUser(id)
}
```
## EX-R48F-028 — Actor protocol request reply current design

- **source_feature_ids:** `actor_declaration_grammar_closed`, `actor_protocol_family`, `actor_request_reply`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public protocol CacheProtocol {
    request get(key: String) -> Bytes?
}
```
## EX-R48F-029 — Yield guard current design

- **source_feature_ids:** `yield_guard_clause_preview`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
@for item in items {
    yield item if item.visible
}
```
## EX-R48F-030 — Function semantic variance law current

- **source_feature_ids:** `function_type_variance_law_phase_a`, `generic_type_constructor_subtyping_law`, `associated_projection_variance_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
// This example is a design seed: variance is checked by responsibility position laws.
public trait Producer<out T> {
    +def get+() -> T
        throws Never
        effects {}
}
```
## EX-R48G-001 — R50b stable @match direct and block arm result

- **source_feature_ids:** `at_match_arm_single_expression_result_law`, `at_match_block_arm_local_ret_law`, `match_arm_guard_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match token {
    ::identifier(name) if name != "" => {
        audit(name)
        ret name
    }
    ::number(n) => "number:${n}"
    otherwise => "other"
}
```
## EX-R48G-003 — R50b nullary lambda expected context

- **source_feature_ids:** `nullary_lambda_arrow_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let zero: () -> Int = { 0 }
let makeUser: () -> User = {
    audit("make")
    ret User!new(name: "Kim")
}
let noop: () -> Unit = {}
```
## EX-R48G-004 — R50b implicit @ lambda is stable in expected one-parameter context

- **source_feature_ids:** `implicit_lambda_at_placeholder_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let positives = values ~ filter { @ > 0 }
```
## EX-R48G-005 — R50b NumericArray transpose is Stable

- **source_feature_ids:** `numeric_array_postfix_transpose_caret_msp`, `numeric_array_vector_orientation_witness_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let gram = A^ ** A
let row = col^
```
## EX-R48G-006 — NumericArray infix power requires current gate

- **source_feature_ids:** `numeric_array_elementwise_power_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let squared = A ^ 2
// NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE
```
## EX-R48G-007 — R50b inclusive slice canonical form

- **source_feature_ids:** `inclusive_slice_range_canonical_msp`, `slice_half_open_noncanonical_warning_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **expected_warnings:** `SLICE_HALF_OPEN_RANGE_NONCANONICAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let head4 = xs[1..4]
let tail = xs[1..$]
let beforeLast = xs[1..<$]
```
## EX-R48G-008 — R50b Type schema construction is not constructor call

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_construction_vs_constructor_domain_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema UserProfile {
    name: String
    age: Int?
}

let profile = UserProfile${
    name: "Kim"
    age: ::some(33)
}
let constructed = UserProfile!(name: "Kim", age: ::some(33))
```
## EX-R48G-009 — R50b current Option cases

- **source_feature_ids:** `option_question_mark_type_surface`, `option_result_double_colon_case_surface`, `option_visible_some_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let explicit: Int? = ::some(13)
let missing: Int? = ::none
let visible: Int? = 13
```
## EX-R48G-010 — R50b current return and lambda ret

- **source_feature_ids:** `named_function_explicit_return_policy`, `one_line_return_body`, `lambda_block_explicit_ret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#pure add(a: Int, b: Int) = return a + b

let logged = { x: Int =>
    audit(x)
    ret x + 1
}
```
## EX-R48G-011 — R50b bare Some and None remain rejected

- **source_feature_ids:** `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_BARE_SOME_REMOVED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a: Int? = Some(13)
let b: Int? = None
// OPTION_BARE_SOME_REMOVED
```
## EX-R48H-001 — Trait witness slot markers open requirement and final helper

- **source_feature_ids:** `trait_witness_slot_method_markers_msp`, `dispatch_marker_dot_family_normalization`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Eq {
    +def equals+(other: Self) -> Bool
        throws Never
        effects {}

    +def notEquals.(other: Self) -> Bool
        throws Never
        effects {}
    = {
        return not self.equals(other)
    }
}
```
## EX-R48H-002 — Trait inherited witness slot override remains open

- **source_feature_ids:** `trait_witness_slot_method_markers_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Eq {
    +def equals+(other: Self) -> Bool
        throws Never
        effects {}
}

public trait Ord requires Eq {
    +def compare+(other: Self) -> Int
        throws Never
        effects {}

    +def equals*+(other: Self) -> Bool
        throws Never
        effects {}
    = {
        return self.compare(other) == 0
    }
}
```
## EX-R48H-003 — Bodyless final witness requirement is Stable

- **source_feature_ids:** `trait_final_witness_requirement_preview`, `trait_witness_slot_method_markers_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait StableHash {
    +def hash.() -> UInt64
        throws Never
        effects {}
}
```
## EX-R48H-004 — Trait method marker is required

- **source_feature_ids:** `trait_witness_slot_method_markers_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRAIT_METHOD_MARKER_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Eq {
    +def equals(other: Self) -> Bool
        throws Never
        effects {}
}
// TRAIT_METHOD_MARKER_REQUIRED
```
## EX-R48H-005 — Trait final slot cannot be overridden

- **source_feature_ids:** `trait_witness_slot_method_markers_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRAIT_FINAL_SLOT_CANNOT_BE_OVERRIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Eq {
    +def notEquals.(other: Self) -> Bool
        throws Never
        effects {}
    = {
        return not self.equals(other)
    }
}

public trait BadEq : Eq {
    +def notEquals*+(other: Self) -> Bool
        throws Never
        effects {}
    = {
        return false
    }
}
// TRAIT_FINAL_SLOT_CANNOT_BE_OVERRIDDEN
```
## EX-R48H-006 — Implicit @ lambda stable expected one-parameter context

- **source_feature_ids:** `implicit_lambda_at_placeholder_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let positives = values ~ filter { @ > 0 }
let names = users ~ map { @.name }
```
## EX-R48H-007 — NumericArray orientation witness and A caret are Stable

- **source_feature_ids:** `numeric_array_vector_orientation_witness_msp`, `numeric_array_postfix_transpose_caret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let col: ColVector<3, Float64> = #[1.0; 2.0; 3.0]
let row = col^
```
## EX-R48L-001 — Type-side call uses double colon

- **source_feature_ids:** `type_side_colon_colon_selector_call_surface`, `double_colon_static_qualified_path`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo::typeside

public class User {}

public def User::parse(text: String) -> Result<User, error ParseError>
    throws Never
    effects {}
= {
    return UserParser::parse(text)
}

let parsed = User::parse("Kim <kim@example.com>")
```
## EX-R48L-002 — Dotted type-side call is rejected

- **source_feature_ids:** `type_side_colon_colon_selector_call_surface`, `double_colon_static_qualified_path`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DOT_NOT_ALLOWED_FOR_TYPE_SIDE_SELECTOR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo::typeside
let parsed = User.parse("text")
// DOT_NOT_ALLOWED_FOR_TYPE_SIDE_SELECTOR
```
## EX-R48L-003 — Associated projection uses double colon

- **source_feature_ids:** `associated_projection_colon_colon_surface`, `trait_associated_projection_explicit_context`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo::associated

public trait Source {
    type Item
    +def next+() -> <Self as Source>::Item?
        throws Never
        effects {}
}

public def first<S>(source: S) -> <S as Source>::Item?
    throws Never
    effects {}
    where S conforms Source
= {
    return source ~ next()
}
```
## EX-R48L-004 — Dot associated projection is rejected

- **source_feature_ids:** `associated_projection_colon_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRAIT_ASSOCIATED_PROJECTION_USES_COLON_COLON`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo::associated
public type ItemOf<S> = <S as Source>.Item
// TRAIT_ASSOCIATED_PROJECTION_USES_COLON_COLON
```
## EX-R48L-005 — Qualified extension selector uses double colon

- **source_feature_ids:** `qualified_extension_selector_colon_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo::qualified_extension

public extension Int as metric {
    +def m() -> Length
        throws Never
        effects {}
    = {
        return Length!(value: self, unit: Unit::meter)
    }
}

use Int::metric
let distance = 3 ~ Int::metric::m
```
## EX-R48L-006 — Full enum case qualification uses double colon

- **source_feature_ids:** `full_enum_case_colon_colon_surface`, `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo::option_case
let a: Int? = ::some(13)
let b: Int? = ::none
let c: Option<Int> = Option<Int>::some(21)
```
## EX-R48L-007 — Numeric power is right-associative

- **source_feature_ids:** `caret_power_operator_msp`, `caret_power_right_associative_math_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let tower = 2 ^ 3 ^ 2
let explicit = 2 ^ (3 ^ 2)
```
## EX-R48L-008 — NumericArray postfix transpose is Stable

- **source_feature_ids:** `numeric_array_postfix_transpose_caret_msp`, `numeric_array_vector_orientation_witness_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a = #2,3[
    1, 2, 3;
    4, 5, 6;
]
let gram = a^ ** a
```
## EX-R48L-009 — NumericArray infix power requires the Preview gate

- **source_feature_ids:** `numeric_array_elementwise_power_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a = #2,2[
    1, 2;
    3, 4;
]
let bad = a ^ 2
// NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE
```
## EX-R48L-010 — NumericArray infix power gated Preview

- **source_feature_ids:** `numeric_array_elementwise_power_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept_with_gate`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(numeric_array_elementwise_power_msp)
let a = #2,2[
    1, 2;
    3, 4;
]
let squared = a ^ 2
```
## EX-R48L-011 — Trait bodyless final witness requirement Stable

- **source_feature_ids:** `trait_final_witness_requirement_preview`, `trait_witness_slot_method_markers_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait StableHash {
    +def hash.() -> UInt64
        throws Never
        effects {}
}

public conformance UserId conforms StableHash {
    +def hash.() -> UInt64
        throws Never
        effects {}
    = {
        return self.raw ~ hash64()
    }
}
```
## EX-R48L-012 — Trait associated item markers are Stable in the limited MSP

- **source_feature_ids:** `trait_associated_requirement_marker_absence`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait TableLike {
    type Row
    let:: defaultCapacity : Int
}
```
## EX-R48L-COMMENT-001 — Line comments are ignored to line end

- **source_feature_ids:** `line_comment_double_slash_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let time = 120 // seconds
let distance = 3
let speed = distance / time
```
## EX-R48L-COMMENT-002 — Nested block comments use //- and -//

- **source_feature_ids:** `nested_block_comment_slash_dash_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
//-------- outer block
   ignored text
   //---- inner block
      inner ignored text
   ----//
--------//
let index = 100 //- base index -// + 20 //- offset -//
```
## EX-R48L-COMMENT-003 — Documentation comments attach to declarations

- **source_feature_ids:** `documentation_comment_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
//! Parses a port number.
public def#pure parsePort(text: String) -> Port = return Port!(text)

//!!
The value constructor keeps validation visible in the constructor domain.
!!//
public value class Port(+let text: String) {}
```
## EX-R48L-COMMENT-004 — Shebang is allowed only as first-line script metadata

- **source_feature_ids:** `shebang_comment_first_line_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#!/usr/bin/env deeplus
module demo::script
public def main() -> Int = return 0
```
## EX-R48L-COMMENT-005 — Backtick word comments are Stable lossless trivia

- **source_feature_ids:** `word_comment_lossless_trivia`, `word_comment_tokenization_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
copy(a`from, b`to)
copy(a`를, b`로)
let speed = distance / time`초
```
## EX-R48L-COMMENT-006 — Backtick word comment cannot have whitespace after backtick

- **source_feature_ids:** `word_comment_lossless_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `WORD_COMMENT_WHITESPACE_FORBIDDEN_AFTER_BACKTICK`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
copy(a` 를, b` 로)
// WORD_COMMENT_WHITESPACE_FORBIDDEN_AFTER_BACKTICK
```
## EX-R48L-COMMENT-007 — Triple slash begins an ordinary line comment

- **source_feature_ids:** `line_comment_double_slash_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
/// This begins an ordinary // line comment, not documentation.
public type CommentedInt = Int
```
## EX-R48M-ENUM-001 — Enum cases use bare declarations and `::case` expected shorthand

- **source_feature_ids:** `enum_bare_case_declaration_canonical`, `enum_case_double_colon_expected_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum ProfileState {
    draft
    active
    blocked(reason: String)
}

let state: ProfileState = ::active
let blocked: ProfileState = ::blocked(reason: "policy")

let label = @match state {
    ::draft => "draft"
    ::active => "active"
    ::blocked(reason) => "blocked:${reason}"
    otherwise => "unknown"
}
```
## EX-R48M-ENUM-002 — Full enum case path uses `Type::case`

- **source_feature_ids:** `full_enum_case_colon_colon_surface`, `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a = Option<Int>::some(13)
let b = Option<Int>::none
let ok = Result<Int, error ParseError>::ok(1)
let bad = Result<Int, error ParseError>::err(ParseError::invalid)
```
## EX-R48M-ENUM-003 — Dot enum shorthand is no longer current

- **source_feature_ids:** `enum_dot_case_shorthand_removed`, `enum_case_double_colon_expected_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DOT_ENUM_CASE_SHORTHAND_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let state: ProfileState = .active
```
## EX-R48M-ENUM-004 — `case` keyword in enum body is not canonical

- **source_feature_ids:** `enum_bare_case_declaration_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ENUM_CASE_KEYWORD_NOT_CANONICAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum ProfileState {
    case draft
    case active
}
```
## EX-R48M-ENUM-005 — Loop outcome match uses `::break` and `::completed`

- **source_feature_ids:** `loop_outcome_double_colon_case_surface`, `loop_outcome_match_statement_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for x in xs {
    break x if x > 10
}
match {
    ::break(v) => print(v)
    ::completed => ()
}
```
## EX-R48M-SPREAD-001 — Record named-argument spread expands static labels

- **source_feature_ids:** `record_named_argument_spread_msp`, `record_spread_named_argument_label_matching_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def moveTo(x: Int, y: Int) -> Unit
    throws Never
    effects {io}
= {
    return print("move to (${x}, ${y})")
}

let point = ${ x: 10, y: 20 }
moveTo(**point)
```
## EX-R48M-SPREAD-002 — Explicit named argument may combine with record spread without duplicates

- **source_feature_ids:** `record_named_argument_spread_msp`, `record_spread_named_argument_label_matching_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def drawPoint(x: Int, y: Int, color: Color) -> Unit
    throws Never
    effects {io}
= {
    return renderer ~ point(x: x, y: y, color: color)
}

let point = ${ x: 10, y: 20 }
drawPoint(**point, color: Color::red)
```
## EX-R48M-SPREAD-003 — Map cannot be expanded into named arguments

- **source_feature_ids:** `map_named_argument_spread_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MAP_NAMED_ARGUMENT_SPREAD_NOT_ALLOWED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def connect(host: String, port: Int) -> Unit
    throws Never
    effects {io}
= {
    return net ~ connect(host: host, port: port)
}

let config = #map{ "host": "example.com", "port": 443 }
connect(**config)
```
## EX-R48M-SPREAD-004 — Duplicate named argument from record spread is rejected

- **source_feature_ids:** `record_named_argument_spread_msp`, `record_spread_named_argument_label_matching_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RECORD_SPREAD_DUPLICATE_NAMED_ARGUMENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let point = ${ x: 10, y: 20 }
moveTo(**point, x: 30)
```
## EX-R48M-SPREAD-005 — Record spread labels must match callable parameters

- **source_feature_ids:** `record_named_argument_spread_msp`, `record_spread_named_argument_label_matching_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RECORD_SPREAD_UNKNOWN_PARAMETER_LABEL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let badPoint = ${ left: 10, top: 20 }
moveTo(**badPoint)
```
## EX-R49-001 — Primary constructor promoted field visibility reaches current grammar

- **source_feature_ids:** `primary_ctor_promoted_field_visibility_sigil_msp`, `r49_primary_constructor_grammar_closure`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class UserProfile(
    +let name: String,
    +let age: Int,
    -let passwordHash: PasswordHash,
)
```
## EX-R49-002 — All-named argument layout separator is current only for all-named calls

- **source_feature_ids:** `all_named_argument_layout_separator_msp`, `r49_all_named_argument_layout_arglist_closure`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(
    id: id
    name: name
    email: email
)
```
## EX-R49-003 — Mixed positional layout remains rejected

- **source_feature_ids:** `all_named_argument_layout_separator_msp`, `r49_all_named_argument_layout_arglist_closure`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ALL_NAMED_ARGUMENT_LAYOUT_ROUTE_UNREACHABLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = makeUser(
    id
    name: name
)
// ALL_NAMED_ARGUMENT_LAYOUT_ROUTE_UNREACHABLE
```
## EX-R49-004 — Enum case expression payload is an argument list, not a declaration payload

- **source_feature_ids:** `r49_enum_case_payload_plane_split`, `full_enum_case_colon_colon_surface`, `enum_case_double_colon_expected_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum ProfileState {
    draft
    blocked(reason: String)
}

let state: ProfileState = ::blocked(reason: "policy")
let explicit = ProfileState::blocked(reason: "audit")
```
## EX-R49-005 — Enum pattern payload uses pattern payload plane

- **source_feature_ids:** `r49_enum_case_payload_plane_split`, `enum_case_pattern_double_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    ::blocked(reason) => reason
    ::draft => "draft"
    otherwise => "other"
}
```
## EX-R49-006 — Function type rest residue remains visible

- **source_feature_ids:** `call_shape_rest_type_residue_law`, `r49_function_type_rest_residue_projection`, `repeated_positional_parameter_msp`, `named_rest_parameter_record_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public type Logger = (LogLevel, String..., Record***) -> Unit

public def log(level: LogLevel, values...: String, options***: Record) -> Unit
    throws Never
    effects {io}
= {
    for value in values {
        print(value)
    }
}
```
## EX-R49-007 — Named rest rejects Map feed

- **source_feature_ids:** `named_rest_parameter_record_msp`, `map_named_argument_spread_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MAP_NAMED_REST_UNFOLD_NOT_ALLOWED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let m = #map{ "timeout": 30 }
configure(**m)
// MAP_NAMED_REST_UNFOLD_NOT_ALLOWED
```
## EX-R49-008 — Type schema construction is schema-only

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `type_schema_construction_vs_constructor_domain_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema UserSchema {
    id: UserId
    name: String
}

let checked = UserSchema${
    id: id
    name: name
}
```
## EX-R49-009 — Constructor-domain allocation still uses Type bang

- **source_feature_ids:** `named_constructor_surface_msp`, `named_constructor_external_call_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(id: id, name: name)
let guest = User!guest(name: "guest")
```
## EX-R49-ENUM-001 — Enum case pattern uses double colon shorthand

- **source_feature_ids:** `enum_case_pattern_double_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    ::active => "active"
    ::blocked(reason) => "blocked:${reason}"
    otherwise => "other"
}
```
## EX-R49-ENUM-002 — Dot enum case pattern is rejected

- **source_feature_ids:** `enum_case_pattern_double_colon_surface`, `enum_dot_case_shorthand_removed`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DOT_ENUM_CASE_PATTERN_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    .active => "active"
    otherwise => "other"
}
```
## EX-R49-PARAM-001 — Repeated positional parameter collects values

- **source_feature_ids:** `repeated_positional_parameter_msp`, `call_shape_rest_type_residue_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def log(level: LogLevel, values...: String) -> Unit
    throws Never
    effects {io}
= {
    for value in values {
        print(value)
    }
}

log(::info, "start", "loading", "done")
```
## EX-R49-PARAM-002 — Empty repeated call needs inference evidence

- **source_feature_ids:** `repeated_positional_parameter_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CANNOT_INFER_REST_ELEMENT_TYPE_FROM_EMPTY_ARGUMENTS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def makeList<T>(values...: T) -> List<T>
    throws Never
    effects {}
= {
    return values ~ toList
}

let xs = makeList()
```
## EX-R49-PARAM-003 — Positional unfolding into repeated parameter

- **source_feature_ids:** `call_side_positional_unfold_star_msp`, `repeated_positional_parameter_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let args = ["a.txt", "b.txt"]
command("copy", *args)
```
## EX-R49-PARAM-004 — Sequence unfolding into fixed parameters requires static arity

- **source_feature_ids:** `call_side_positional_unfold_star_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SEQUENCE_UNFOLD_REQUIRES_STATIC_ARITY_FOR_FIXED_PARAMETERS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def pair(x: Int, y: Int) -> Pair<Int, Int>
    throws Never
    effects {}
= {
    return Pair!(x: x, y: y)
}

let xs: Sequence<Int> = readNumbers()
let p = pair(*xs)
```
## EX-R49-PARAM-005 — Named rest parameter collects unmatched named arguments

- **source_feature_ids:** `named_rest_parameter_record_msp`, `record_named_argument_spread_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options***: Record) -> Unit
    throws Never
    effects {}
= {
    applyConfig(options)
}

configure(timeout: 30, verbose: true, mode: "fast")
```
## EX-R49-PARAM-006 — Named rest parameter must be last

- **source_feature_ids:** `named_rest_parameter_record_msp`, `data_shaping_callshape_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NAMED_REST_PARAMETER_MUST_BE_LAST`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def bad(options***: Record, x: Int) -> Unit
    throws Never
    effects {}
= {
}
```
## EX-R49-PARAM-007 — Combined repeated and named rest call shape

- **source_feature_ids:** `repeated_positional_parameter_msp`, `named_rest_parameter_record_msp`, `call_side_positional_unfold_star_msp`, `record_named_argument_spread_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def command(name: String, args...: String, options***: Record) -> Unit
    throws Never
    effects {io}
= {
    runCommand(name, args, options)
}

let args = ["a.txt", "b.txt"]
let opts = ${ overwrite: true, mode: "safe" }

command("copy", *args, **opts)
```
## EX-R49-PRIMARY-001 — Primary promoted field visibility sigils

- **source_feature_ids:** `primary_ctor_promoted_field_visibility_sigil_msp`, `primary_ctor_promoted_field_visibility_member_only_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class UserProfile(
    +let name: String
    +let age: Int
    -let passwordHash: PasswordHash
)
```
## EX-R49-PRIMARY-002 — Promoted field visibility applies to generated member only

- **source_feature_ids:** `primary_ctor_promoted_field_visibility_member_only_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let profile = UserProfile!(
    name: "Kim"
    age: 33
    passwordHash: PasswordHash::fromSecret(secret)
)

// profile.passwordHash is private outside the declaring visibility boundary.
```
## EX-R49-PRIMARY-003 — Promoted field visibility sigil must attach to storage keyword

- **source_feature_ids:** `primary_ctor_promoted_field_visibility_sigil_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `PRIMARY_CTOR_VISIBILITY_SIGIL_MUST_ATTACH_TO_STORAGE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class BadProfile(
    + let name: String
)
```
## EX-R49-SPREAD-001 — Map cannot feed named rest or named argument spread

- **source_feature_ids:** `map_named_argument_spread_forbidden_law`, `named_rest_parameter_record_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MAP_NAMED_ARGUMENT_SPREAD_NOT_ALLOWED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options***: Record) -> Unit
    throws Never
    effects {}
= {
    applyConfig(options)
}

let config = #map{ "timeout": 30, "verbose": true }
configure(**config)
```
## EX-R49B-CHAR-001 — BMP Unicode scalar Char

- **source_feature_ids:** `char_unicode_scalar_value_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let letter: Char = '가'
```
## EX-R49B-CHAR-002 — Supplementary-plane Unicode scalar Char

- **source_feature_ids:** `char_unicode_scalar_value_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let smile: Char = '\u{1F642}'
```
## EX-R49B-CHAR-003 — Multi-scalar grapheme is not Char

- **source_feature_ids:** `char_unicode_scalar_value_model`, `grapheme_text_model`, `unicode_char_literal_single_quote_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CHAR_LITERAL_REQUIRES_ONE_SCALAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let accented: Char = 'e\u{0301}'
// CHAR_LITERAL_REQUIRES_ONE_SCALAR
```
## EX-R49B-CHAR-004 — Surrogate escape is not a Unicode scalar

- **source_feature_ids:** `char_unicode_scalar_value_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CHAR_LITERAL_SURROGATE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad: Char = '\u{D800}'
// CHAR_LITERAL_SURROGATE_FORBIDDEN
```
## EX-R49B-CHAR-005 — Empty Char literal is rejected

- **source_feature_ids:** `char_unicode_scalar_value_model`, `unicode_char_literal_single_quote_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CHAR_LITERAL_EMPTY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let empty: Char = ''
// CHAR_LITERAL_EMPTY
```
## EX-R49B-CLASS-001 — Plain concrete class is final

- **source_feature_ids:** `class_final_by_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Token {
}
// Token is final without a modifier.
```
## EX-R49B-CLASS-002 — Subclassing a default-final class is rejected

- **source_feature_ids:** `class_final_by_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CLASS_IS_FINAL_BY_DEFAULT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Token {
}
public final class Derived : Token {
}
// CLASS_IS_FINAL_BY_DEFAULT
```
## EX-R49B-CLASS-003 — Open class explicitly admits subclasses

- **source_feature_ids:** `class_final_by_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public open class Node {
}
public final class Leaf : Node {
}
```
## EX-R49B-CLASS-004 — Abstract class is open and non-instantiable

- **source_feature_ids:** `class_final_by_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ABSTRACT_CLASS_INSTANTIATION_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public abstract class Shape {
    +def area+() -> Float64
}
let bad = Shape!()
// ABSTRACT_CLASS_INSTANTIATION_FORBIDDEN
```
## EX-R49B-DYNTRAIT-001 — Dynamic trait attach syntax remains non-current

- **source_feature_ids:** `dynamic_trait_attach_detach_stateless_preview_design`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DYNAMIC_TRAIT_ATTACH_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
attach Display to value
// DYNAMIC_TRAIT_ATTACH_NOT_CURRENT
```
## EX-R49B-ESC-001 — Escaped hard-keyword member

- **source_feature_ids:** `escaped_member_name`, `hard_keyword_escape_boundary`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let category = schema.\class
```
## EX-R49B-ESC-002 — Escaped external identifier member

- **source_feature_ids:** `escaped_member_name`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let size = payload.\length
```
## EX-R49B-ESC-003 — Plain-dot hard keyword member is rejected

- **source_feature_ids:** `hard_keyword_escape_boundary`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `HARD_KEYWORD_MEMBER_REQUIRES_ESCAPE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = schema.class
// HARD_KEYWORD_MEMBER_REQUIRES_ESCAPE
```
## EX-R49B-ESC-004 — Member escape requires adjacency

- **source_feature_ids:** `escaped_member_name`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ESCAPED_MEMBER_ADJACENCY_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = schema. \class
// ESCAPED_MEMBER_ADJACENCY_REQUIRED
```
## EX-R49B-ESC-005 — Member escape cannot declare a local

- **source_feature_ids:** `escaped_member_name`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ESCAPED_MEMBER_CONTEXT_ONLY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let \class = 1
// ESCAPED_MEMBER_CONTEXT_ONLY
```
## EX-R49B-EXT-001 — Extension-set member uses plain def; call retains tilde

- **source_feature_ids:** `extension_set_member_plain_def_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension User as printable {
    +def display() -> String = {
        return self.name
    }
}
use User::printable
let text = user ~ display()
```
## EX-R49B-EXT-002 — Superseded tilde declaration inside extension set

- **source_feature_ids:** `extension_set_member_plain_def_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXTENSION_SET_MEMBER_TILDE_DECLARATION_REMOVED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension User as printable {
    +def display() -> String = { return self.name }
}
// EXTENSION_SET_MEMBER_TILDE_DECLARATION_REMOVED
```
## EX-R49B-EXT-003 — Extension does not auto-create witness

- **source_feature_ids:** `extension_auto_witness_forbidden_law`, `extension_conformance_resolution_identity_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXTENSION_AUTO_WITNESS_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension User as printable {
    +def display() -> String = { return self.name }
}
public def render<T>(value: T) -> String where T conforms Display = {
    return value ~ display()
}
let bad = render(User!(name: "Kim"))
// EXTENSION_AUTO_WITNESS_FORBIDDEN
```
## EX-R49B-EXT-004 — Conformance explicitly delegates to identified extension

- **source_feature_ids:** `explicit_conformance_extension_delegation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension User as printable {
    +def display() -> String = { return self.name }
}
public conformance User conforms Display {
    delegate display to User::printable::display
}
```
## EX-R49B-EXT-006 — Source and use order cannot break selector ambiguity

- **source_feature_ids:** `extension_conformance_resolution_identity_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXTENSION_RESOLUTION_ORDER_NOT_TIEBREAKER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use User::compact
use User::verbose
let bad = user ~ display()
// EXTENSION_RESOLUTION_ORDER_NOT_TIEBREAKER
```
## EX-R49B-OPTION-001 — Nested optionality is explicit

- **source_feature_ids:** `compact_optional_suffix_single_layer_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let nested: Option<Int?> = ::some(::none)
```
## EX-R49B-OPTION-002 — Repeated compact optional suffix is rejected

- **source_feature_ids:** `compact_optional_suffix_single_layer_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTIONAL_SUFFIX_REPEATED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ambiguous: Int?? = ::none
// OPTIONAL_SUFFIX_REPEATED
```
## EX-R49B-REST-001 — Named rest collects static Record labels

- **source_feature_ids:** `named_rest_parameter_record_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options***: Record) -> Unit = {
}
configure(host: "localhost", port: 443)
```
## EX-R49B-REST-002 — Map cannot feed named rest

- **source_feature_ids:** `named_rest_parameter_record_msp`, `record_named_argument_spread_msp`, `data_shaping_callshape_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NAMED_REST_REQUIRES_RECORD_LABEL_SOURCE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let dynamic = #map{ "host": "localhost" }
configure(**dynamic)
// NAMED_REST_REQUIRES_RECORD_LABEL_SOURCE
```
## EX-R49B-ROW-001 — Effect and error rows use visible bar union

- **source_feature_ids:** `effect_error_row_union_bar_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def load() -> Data
    throws NetworkError | IOError
    effects Eff | {network, io}
= {
    return fetch()
}
```
## EX-R49B-ROW-002 — Tokenless effect-row adjacency is rejected

- **source_feature_ids:** `effect_error_row_union_bar_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EFFECT_ROW_UNION_TOKEN_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def bad() -> Unit
    effects Eff {state}
= {
}
// EFFECT_ROW_UNION_TOKEN_REQUIRED
```
## EX-R49B-SEALED-001 — Sealed hierarchy closes direct subclasses to one module

- **source_feature_ids:** `sealed_class_module_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module expr
public sealed class Expr {
}
public final class Literal : Expr {
}
public open class Binary : Expr {
}
```
## EX-R49B-SEALED-002 — Sealed direct subclass outside module is rejected

- **source_feature_ids:** `sealed_class_module_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SEALED_DIRECT_SUBCLASS_OUTSIDE_MODULE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module plugin
public final class ForeignExpr : expr::Expr {
}
// SEALED_DIRECT_SUBCLASS_OUTSIDE_MODULE
```
## EX-R49B-SEALED-003 — Sealed direct subclass must state its disposition

- **source_feature_ids:** `sealed_class_module_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SEALED_DIRECT_SUBCLASS_DISPOSITION_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module expr
public class Child : Expr {
}
// SEALED_DIRECT_SUBCLASS_DISPOSITION_REQUIRED
```
## EX-R49C-COALESCE-001 — Option coalescing unwraps one layer lazily

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let port: Int = configuredPort ?: 8080
```
## EX-R49C-COALESCE-002 — Right-associated fallback chain

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let port = cliPort ?: envPort ?: configPort ?: 8080
```
## EX-R49C-COALESCE-003 — Nested Option removes exactly one layer

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let inner: Option<Int> = nested ?: ::none
```
## EX-R49C-COALESCE-004 — Coalescing does not discard Result failure

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_COALESCE_DOES_NOT_APPLY_TO_RESULT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = parseResult ?: 0
```
## EX-R49C-COALESCE-005 — Coalescing requires an Option left operand

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_COALESCE_REQUIRES_OPTION_LEFT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = 10 ?: 20
```
## EX-R49C-COALESCE-006 — Coalescing token is adjacent

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_COALESCE_TOKEN_MUST_BE_ADJACENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = maybe ? : fallback
```
## EX-R49C-COALESCE-007 — Affine payload extraction moves the owned Option

- **source_feature_ids:** `option_coalescing_ownership_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let file = move maybeFile ?: openDefaultFile()
```
## EX-R49C-COALESCE-008 — Borrowed affine Option cannot yield owned payload

- **source_feature_ids:** `option_coalescing_ownership_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OPTION_COALESCE_BORROWED_AFFINE_EXTRACTION`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def choose(maybe: borrow File?) -> File
    throws IOError
    effects {io}
= {
    return maybe ?: openDefaultFile()
}
```
## EX-R49C-ENTRY-001 — Explicit entry has no magic name

- **source_feature_ids:** `explicit_entry_function_surface`, `entry_target_uniqueness_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    return dispatch(args)
}
```
## EX-R49C-ENTRY-002 — Implicit script entry and explicit entry conflict

- **source_feature_ids:** `entry_target_uniqueness_law`, `source_role_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch() -> Unit
    throws Never
    effects {}
= { }
print("also a script")
```
## EX-R49C-LAMBDA-001 — Lambda-only unparenthesized parameter list

- **source_feature_ids:** `lambda_unparenthesized_parameter_list_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let add = { x: Int, y: Int => x + y }
let logged = [borrow audit] { x: Int =>
    audit(x)
    ret x + 1
}
```
## EX-R49C-LAMBDA-002 — Lambda list-level parentheses are removed

- **source_feature_ids:** `lambda_unparenthesized_parameter_list_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LAMBDA_PARAM_LIST_PARENS_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let inc = { (x: Int) => x + 1 }
```
## EX-R49C-LINALG-001 — Linear-product chain folds left

- **source_feature_ids:** `linear_algebra_minimal_operator_msp`, `matrix_multiplication_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let projected = matrix ** basis *+ weights
```
## EX-R49C-MAT-001 — Schema materialization and named unfolding

- **source_feature_ids:** `typed_labeled_materialization_family`, `schema_construction_projection_rows`, `schema_named_unfolding`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema RequestArgs {
    url: String
    timeout: Int = 30
}
let args = RequestArgs${ url: endpoint }
request(**args)
```
## EX-R49C-MAT-002 — Generated final data class materializes by labels

- **source_feature_ids:** `generated_data_class_materialization_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Point(+let x: Int, +let y: Int)
let point = Point${ x: 3, y: 4 }
```
## EX-R49C-MAT-003 — Data class has no automatic named unfolding

- **source_feature_ids:** `generated_data_class_materialization_msp`, `schema_named_unfolding`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DATA_CLASS_AUTOMATIC_UNFOLD_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class User(+let name: String)
let user = User${ name: "Kim" }
send(**user)
```
## EX-R49C-MAT-004 — Map is not static named-unfold evidence

- **source_feature_ids:** `schema_named_unfolding`, `map_named_argument_spread_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MAP_IS_NOT_NAMED_UNFOLD_SOURCE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let options = #map{ "timeout": 30 }
request(**options)
```
## EX-R49C-MATCH-001 — Value matching uses at-match only

- **source_feature_ids:** `match_exhaustiveness_phase_a`, `at_match_arm_single_expression_result_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    ::ready => "ready"
    ::failed(error) => error ~ display
}
```
## EX-R49C-MATCH-002 — Bare match cannot initialize a value

- **source_feature_ids:** `match_exhaustiveness_phase_a`, `statement_control_core_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MATCH_EXPR_REQUIRES_AT_PREFIX`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = match state {
    ::ready => "ready"
    otherwise => "other"
}
```
## EX-R49C-MATCH-003 — Bare match remains a statement with guards

- **source_feature_ids:** `match_arm_guard_msp`, `match_exhaustiveness_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
match state {
    ::ready if permitted => start()
    ::failed(error) !if ignored(error) => report(error)
    otherwise => logUnknown()
}
```
## EX-R49C-NUM-001 — Closed numeric literal positive matrix

- **source_feature_ids:** `numeric_literal_lexical_contract`, `numeric_literal_suffix`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let a = 1_000_000
let b: UInt8 = 0b1010_0110u8
let mode = 0o755u16
let mask = 0xDEAD_BEEFu32
let avogadro = 6.022_140_76e23f64
let small = 1e-9f64
let exactFloat = 1f64
```
## EX-R49C-NUM-002 — Invalid binary digit

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INVALID_DIGIT_FOR_NUMERIC_RADIX`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = 0b102
```
## EX-R49C-NUM-003 — Separator cannot follow radix prefix

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMERIC_DIGIT_SEPARATOR_POSITION_INVALID`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = 0x_1
```
## EX-R49C-NUM-004 — Consecutive numeric separators are invalid

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMERIC_DIGIT_SEPARATOR_POSITION_INVALID`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = 1__000
```
## EX-R49C-NUM-005 — Exponent requires digits

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MALFORMED_NUMERIC_EXPONENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = 1e+
```
## EX-R49C-NUM-006 — Integer suffix cannot follow decimal fraction

- **source_feature_ids:** `numeric_literal_lexical_contract`, `numeric_literal_suffix`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMERIC_SUFFIX_KIND_MISMATCH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = 1.0u8
```
## EX-R49C-NUM-007 — Radix float is not current

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMERIC_RADIX_FLOAT_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = 0x1.fp3
```
## EX-R49C-NUM-008 — Non-finite values use type-side constants

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let nan = Float64::nan
let pos = Float64::positiveInfinity
let neg = -Float64::positiveInfinity
```
## EX-R49C-PROJ-001 — Optional suffix attaches to associated projection

- **source_feature_ids:** `associated_projection_optional_suffix_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let item: <Self as Iterator>::Item? = iterator ~ next()
```
## EX-R49C-PROJ-002 — Associated projection parentheses are redundant

- **source_feature_ids:** `associated_projection_optional_suffix_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let item: (<Self as Iterator>::Item)? = iterator ~ next()
// warning: REDUNDANT_ASSOCIATED_PROJECTION_PARENS_BEFORE_OPTIONAL
```
## EX-R49C-RESULT-001 — Result error argument is a grammar-visible channel

- **source_feature_ids:** `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let result: Result<Int, error ParseError> = ::ok(42)
```
## EX-R49C-RETURN-001 — Canonical Unit fallthrough omits final return

- **source_feature_ids:** `final_valueless_return_omission_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def announce() -> Unit
    throws Never
    effects {io}
= {
    print("ready")
}
```
## EX-R49C-RETURN-002 — Early valueless return remains meaningful

- **source_feature_ids:** `final_valueless_return_omission_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def validate(x: Int) -> Unit
    throws Never
    effects {}
= {
    if x < 0 {
        return
    }
    audit(x)
}
```
## EX-R49C-SCRIPT-001 — Selected script root executes ordered top-level statements

- **source_feature_ids:** `top_level_script_root_msp`, `source_role_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module tools::hello
let name = readLine()
print("hello ${name}")
```
## EX-R49C-SCRIPT-002 — Library rejects loose top-level computation

- **source_feature_ids:** `source_role_contract`, `top_level_script_root_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `TOP_LEVEL_STATEMENT_REQUIRES_SCRIPT_ROOT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module lib::bad
print("import side effect")
```
## EX-R49C-SEALED-001 — Canonical sealed-class hierarchy

- **source_feature_ids:** `sealed_class_module_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module expr
public sealed class Expr { }
public final class Literal : Expr { }
public open class Composite : Expr { }
```
## EX-R49C-SEALED-002 — Removed hash-combined sealed spelling

- **source_feature_ids:** `sealed_class_module_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CLASS_HASH_SEALED_SPELLING_REMOVED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class#sealed Expr { }
```
## EX-R49C-STATIC-001 — Module static initializer is nonactivatable

- **source_feature_ids:** `module_static_entrance`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `MODULE_STATIC_INITIALIZER_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module cache
static {
    warm()
}
```
## EX-R49C-STRING-001 — Interpolation has explicit lexer-mode parts

- **source_feature_ids:** `string_interpolation_format_spec_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let message = "name:$name total=${total:>8}"
```
## EX-R49C-TILDE-001 — Extension member declares a plain selector

- **source_feature_ids:** `declaration_selector_tilde_absence_law`, `extension_set_member_plain_def_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public extension BlobStore as binary {
    +def load*.(key: Key) -> Bytes = {
        return backend ~ read(key)
    }
}
```
## EX-R49C-TILDE-002 — Leading tilde is forbidden in member declaration

- **source_feature_ids:** `declaration_selector_tilde_absence_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DECLARATION_TILDE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Loader {
    +def ~load*(key: Key) -> Bytes
}
```
## EX-R51a1-001 — role-specific executable entry

- **source_feature_ids:** `explicit_entry_function_surface`, `entry_signature_contract`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    print(args)
    return ExitCode::success
}
```
## EX-R51a1-002 — sealed class is the only current spelling

- **source_feature_ids:** `sealed_class_module_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public sealed class Node {
    +def value.() -> Int = { return 1 }
}
```
## EX-R51a1-003 — canonical lambda parameter list

- **source_feature_ids:** `lambda_unparenthesized_parameter_list_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let add = { x: Int, y: Int => x + y }
```
## EX-R51a1-004 — value @match and statement match

- **source_feature_ids:** `at_match_arm_single_expression_result_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @match state {
    ::ready => "ready"
    otherwise => "other"
}
match state {
    ::ready => start()
    otherwise => stop()
}
```
## EX-R51a1-005 — Unit terminal fallthrough

- **source_feature_ids:** `final_valueless_return_omission_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def announce() -> Unit = {
    print("ready")
}
```
## EX-R51a1-006 — closed numeric lexical matrix

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let mask = 0xDEAD_BEEFu32
let count = 0b1010_0101u8
let ratio = 6.022_140_76e23f64
let inf = Float64::positiveInfinity
```
## EX-R51a1-007 — Bytes mode and named Unicode escape

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`, `unicode_named_escape_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let png = #bytes"\x89PNG\x0D\x0A"
let mark: Char = '\N{COPYRIGHT SIGN}'
```
## EX-R51a1-008 — indexed interpolation shorthand and braced member access

- **source_feature_ids:** `string_interpolation_shorthand_factor_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let line = "first:$users[1] name=${users[1].name} total=${total:>8}"
```
## EX-R51a1-009 — ordinary immutable list literal

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let names: List<String> = ["Ada", "Grace", "Edsger"]
```
## EX-R51a1-010 — all-named newline argument layout

- **source_feature_ids:** `all_named_argument_layout_separator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(
    id: id
    name: name
    active: true
)
```
## EX-R51a1-011 — primary constructor promoted-field layout

- **source_feature_ids:** `primary_ctor_layout_promoted_field_separator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class User(
    +let name: String
    +let age: Int
)
```
## EX-R51a1-012 — annotation attaches structurally

- **source_feature_ids:** `annotation_structural_attachment`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
@deprecated("use open")
public def oldOpen() -> Unit = {
    open()
}
```
## EX-R51a1-013 — enum cases and enum members

- **source_feature_ids:** `enum_member_declaration_surface`, `enum_member_body_restoration`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum State {
    ready
    failed(reason: String)

    +def isReady.() -> Bool = {
        return self == ::ready
    }
}
```
## EX-R51a1-014 — narrow explicit witness parameter and coherent call channel

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`, `explicit_witness_argument_keyword_spelling`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def sort<T>(xs: List<T>, using order: witness Ord<T>) -> List<T> = {
    return stableSort(xs, using order)
}
def ordered(using intOrder: witness Ord<Int>) -> List<Int> = {
    return sort([3, 1, 2], using intOrder)
}
```
## EX-R51a1-015 — typed labeled materialization

- **source_feature_ids:** `typed_labeled_materialization_family`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema Request {
    url: String
    timeout: Int = 30
}
let request = Request${
    url: endpoint
}
```
## EX-R51a1-016 — prototype derivation body

- **source_feature_ids:** `shallow_same_type_derivation`, `deep_same_type_derivation`, `prototype_derivation_without_dollar`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let quick = base!{ timeout: 5 }
let detached = graph!!{ retries: 3 }
```
## EX-R51a1-017 — lazy Option coalescing

- **source_feature_ids:** `option_coalescing_unwrap_or_default`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let port: Int = configuredPort ?: discoverPort()
```
## EX-R51a1-018 — declarative clause body

- **source_feature_ids:** `declarative_function_clause_block_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def sign(n: Int) -> Int = {{
    n if n < 0 => -1
    n if n == 0 => 0
    otherwise => 1
}}
```
## EX-R51a1-019 — cleanup declaration has exact empty parameter list

- **source_feature_ids:** `throwing_drop_cleanup_failure_policy`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public resource class File {
    def#cleanup()
        throws Never
        effects {io}
    = { closeHandle() }
}
```
## EX-R51a1-020 — qualified static selector classification

- **source_feature_ids:** `type_side_colon_colon_selector_call_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let red = Color::red
let parsed = UserId::parse("42")
```
## EX-R51a1-021 — static-pure library binding

- **source_feature_ids:** `library_static_binding_initializer_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let protocolVersion: Int = 1
```
## EX-R51a1-022 — rank-three exact-shape separator runs

- **source_feature_ids:** `shaped_literal_separator_rank_law`, `shaped_semicolon_literal_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let tensor = #2,2,2[
    1, 2;
    3, 4;;

    5, 6;
    7, 8;;
]
```
## EX-R51a1-023 — comma plus newline materialization and map entries

- **source_feature_ids:** `type_schema_construction_dollar_surface`, `map_prefixed_literal`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let record = ${
    name: name,
    age: age,
}
let table = #map {
    "a": 1,
    "b": 2,
}
```
## EX-R51a1-024 — nested local function with explicit outer capture

- **source_feature_ids:** `nested_function_local_def_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def outer(x: Int) -> Int = {
    [borrow x] def inner(y: Int) -> Int = {
        return x + y
    }
    return inner(1)
}
```
## EX-R51a1-025 — task body owns a final await expression

- **source_feature_ids:** `task_body_minimum_grammar_slice`, `structured_task_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
task scope {
    let profile = spawn async { =>
        await loadProfile(id)
    }
    await profile
}
```
## EX-R51a1-026 — capture list attaches through an explicit closure mode

- **source_feature_ids:** `closure_capture_descriptor_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let consumeOnce = [move token] #once { value => consume(token, value) }
```
## EX-R51a1-027 — postfix transpose continues through every suffix boundary

- **source_feature_ids:** `numeric_array_postfix_transpose_caret_msp`, `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let first = matrix^[1]
let rows = matrix^.shape
let escaped = matrix^.\class
let mapped = matrix^ transform { value => value }
```
## EX-R51a1-028 — multiline named call remains comma-form when commas are present

- **source_feature_ids:** `named_argument_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User!(
    id: id,
    name: name,
)
```
## EX-R51a1-029 — multiline primary constructor and constrained schema remain comma-form

- **source_feature_ids:** `primary_constructor_let_var_promotion_only`, `type_schema_declaration_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Point(
    +let x: Int,
    +let y: Int,
)

public schema Pair {
    left: Int where true,
    right: Int where true,
}
```
## EX-R51a1-030 — ordinary function returns a lambda without entering clause-body mode

- **source_feature_ids:** `lambda_unparenthesized_parameter_list_surface`, `declarative_function_clause_block_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def identityFactory() -> ((Int) -> Int) = {
    return ({ x: Int => x })
}
```
## EX-R51a1-031 — layout schema gives every refinement to SchemaConstraint

- **source_feature_ids:** `type_schema_declaration_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public schema CheckedPair {
    left: Int where true
    right: Int where true where 0 < 1
}
```
## EX-R51a1-032 — layout call ignores commas owned by an exact-shape argument

- **source_feature_ids:** `all_named_argument_layout_separator_msp`, `numeric_array_sharp_shape_literal_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let batch = consume(
    tensor: #2,2[1, 2; 3, 4;]
    label: name
)
```
## EX-R51a1-033 — layout declarations ignore shape and generic child commas

- **source_feature_ids:** `primary_constructor_let_var_promotion_only`, `type_schema_declaration_core`, `numeric_array_sharp_shape_literal_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Tile(
    +let pixels: #2,2[Int]
    +let tag: Pair<Int, String>
)

public schema TileRow {
    pixels: #2,2[Int]
    tag: Pair<Int, String>
}
```
## EX-R51a1-034 — ordinary parameter binds an identifier before body pattern control

- **source_feature_ids:** `pattern_match_ownership_split`, `enum_case_pattern_double_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def accept(mut result: Result<Int, error ParseError>) -> Unit = {
    if let Result::ok(value) = result {
        print(value)
    }
}
```
## EX-R51a1-035 — implicit lambda receiver reuses common postfix suffixes

- **source_feature_ids:** `implicit_lambda_at_placeholder_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let firstNames = users ~ map { @.profile[1].name }
```
## EX-R51a1-036 — await has one unary-tier owner

- **source_feature_ids:** `await_expression_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let remoteName = await fetchUser().profile.name
let localName = (await fetchUser()).name
let total = (await fetchCount()) + 1
```
## EX-R51a1-037 — message suffix maximally owns immediate arguments and closures

- **source_feature_ids:** `instance_side_tilde_structured_names`, `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let nextValue = receiver ~ next(args)
let mapped = receiver ~ map values { value => value }
let invoked = (receiver ~ callback)(args)
```
## EX-R51a1-038 — same-line module signature head selects the signature declaration

- **source_feature_ids:** `module_signature_declaration`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module signature API {
    export Item
}
```
## EX-R51a1-039 — explicit terminator permits a module named signature

- **source_feature_ids:** `module_signature_declaration`, `source_role_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module signature;
public type Value = Int
```
## EX-R51a1-040 — newline breaks the contextual sealed-class phrase

- **source_feature_ids:** `sealed_class_module_scope`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
sealed
class OpenThing {}
```
## EX-R51a1-041 — optional data-class and trait braces belong to their declarations

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Empty {}
public trait Marker {}
```
## EX-R51a1-042 — parentheses separate a lambda from a bodyless declaration

- **source_feature_ids:** `lambda_unparenthesized_parameter_list_surface`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
data class Marker
({ x: Int => x })
```
## EX-R51a1-043 — cleanup budget maximally remains in the data-class header

- **source_feature_ids:** `header_cleanup_budget_surface`, `cleanup_budget_algebra`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
data class Tracked
cleanup budget {
    effects {io}
}
```
## EX-R51a1-044 — value-arm newline separates an open range from the next qualified pattern

- **source_feature_ids:** `declarative_function_clause_block_msp`, `runtime_range_step_expression`, `enum_case_pattern_double_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def choose(x: Input) -> Range<Int> = {{
    p => a..
    Q::ready => r
}}
```
## EX-R51a1-045 — associated where binds inside some-trait before an outer function where

- **source_feature_ids:** `some_trait_opaque_result_preview`, `explicit_existential_any_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def current(it: Iterator) -> some Iterator where Item == Int = {
    return it
}

def constrained<T>(it: Iterator) -> (some Iterator where Item == Int)
    where T conforms Marker
= {
    return it
}
```
## EX-R51a1-046 — refinement and contract predicates cannot absorb outer initialization or bodies

- **source_feature_ids:** `inline_refinement_type_annotation`, `contract_requires_ensures`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Box {
    +let value: Int where this >= 0 = 1
}

public trait Ready {
    +def check.() requires true = { }
}
```
## EX-R51a1-047 — measure and sharp-shape brackets use distinct opener tokens

- **source_feature_ids:** `measure_literal_msp`, `numeric_array_sharp_shape_literal_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si

public type Grid = #2,2[Int]
let tensor: Grid = #2,2[1, 2; 3, 4;]
let length = 13[cm]
```
## EX-R51a1-048 — adjacent double caret is xor rather than two transpose tokens

- **source_feature_ids:** `r51a1_machine_closed_lexical_modes`, `numeric_array_postfix_transpose_caret_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bits = a ^^ b
let restored = (matrix^)^
```
## EX-R51a1-049 — ordinary List inference and exact contextual integer adaptation

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let inferred = [1, 2, 3]
let bytes: List<UInt8> = [1, 2]
```
## EX-R51a1-050 — extension-pack module interface has a current rooted route

- **source_feature_ids:** `extension_pack_module_interface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
extension pack std::metric::Interface {
    use export Int::metric
}
```
## EX-R51a1-051 — lone wildcard and underscore-prefixed identifiers are lexically disjoint

- **source_feature_ids:** `r51a1_machine_closed_lexical_modes`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let _ = ignored()
let _name = 1
let __ = 2
```
## EX-R51a1-052 — control body owns its first brace and a condition trailing closure is parenthesized

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if ready() {
    start()
}
if (withValue() { value => value }) {
    start()
}
```
## EX-R51a1-053 — List suffix, target-size, boundary, empty-context, and nonnumeric identity admissions

- **source_feature_ids:** `ordinary_list_literal_surface`, `numeric_literal_suffix`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let floats: List<Float32> = [1.0f32]
let indexes: List<ISize> = [1isize]
let signed: List<Int8> = [-128, 127]
let emptyNames: List<String> = []
let names: List<String> = ["Ada", "Grace"]
```
## EX-R51a1-054 — entry no-argument Unit shape

- **source_feature_ids:** `entry_signature_contract`, `explicit_entry_function_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch() -> Unit = {
}
```
## EX-R51a1-055 — entry argv Unit shape

- **source_feature_ids:** `entry_signature_contract`, `explicit_entry_function_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch(args: Sequence<String>) -> Unit = {
    print(args)
}
```
## EX-R51a1-056 — entry no-argument ExitCode shape

- **source_feature_ids:** `entry_signature_contract`, `explicit_entry_function_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch() -> ExitCode = {
    return ExitCode::success
}
```
## EX-R51a1-057 — async entry uses the exact argv ExitCode shape

- **source_feature_ids:** `entry_signature_contract`, `explicit_entry_function_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry#async launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    print(args)
    return ExitCode::success
}
```
## EX-R51a1-058 — nested block comment dash-run mismatch remains valid

- **source_feature_ids:** `nested_block_comment_slash_dash_trivia`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
//--- outer
//- inner -//
--//
let value = 1
```
## EX-R51a1-059 — explicit borrow inout and move modes

- **source_feature_ids:** `inout_borrow_move_modes`, `region_lifetime_model_phase_a`, `place_view_owner_algebra`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def replace(borrow label: String, inout target: Buffer, move replacement: Buffer) -> Unit = {
    log(label)
    target = move replacement
}
```
## EX-R51a1-060 — Result and throws use disjoint recoverable error families

- **source_feature_ids:** `result_error_set_model`, `result_throws_overlap_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def decode(bytes: Bytes) -> Result<Image, error DecodeError>
    throws IOError
    effects {io}
= {
    return parseImage(bytes)
}
```
## EX-R51a1-061 — closed R0 refinement predicate

- **source_feature_ids:** `refinement_type_phase_a`, `r0_guard_predicate_calculus`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public type Port = Int where this >= 0 and this <= 65_535
```
## EX-R51a1-062 — exact normalized named call shape

- **source_feature_ids:** `named_argument_colon_surface`
- **checker_trace_ids:** `StaticCallShapeAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let request = Request!(url: endpoint, timeout: 30)
```
## EX-R51a1-063 — type token is used only by static selection

- **source_feature_ids:** `type_token_authority_law`, `type_side_colon_colon_selector_call_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let parsed = UserId::parse("42")
```
## EX-R51a1-064 — exact unit core normalizes equivalent linear dimensions

- **source_feature_ids:** `unit_canonicalization`, `measure_semantic_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si
let distance = 100[cm]
let meters = distance ~ asUnit(1[m])
```
## EX-R51a1-065 — explicit reusable authority-free context value

- **source_feature_ids:** `context_value_admissibility`, `explicit_context_parameter_role_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def format(value: Float64, context pattern: FormatPattern) -> String = {
    return pattern ~ render value
}
let text = format(3.14, context FormatPattern!("{:.2f}"))
```
## EX-R51a1-066 — stable async declaration and iteration need no preview gate

- **source_feature_ids:** `async_function_declaration_surface`, `async_iteration`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#async consume(stream: AsyncSequence<Int, Never>) -> Unit = {
    for await value in stream {
        print(value)
    }
}
```
## EX-R51a1-067 — terminal bare return is admitted with a noncanonical lint

- **source_feature_ids:** `final_valueless_return_omission_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def announceLegacy() -> Unit = {
    print("ready")
    // warning: REDUNDANT_FINAL_VALUELESS_RETURN
    return
}
```
## EX-R51a1-ACOLLECT-NG-001 — Stage-1 collector rejects an AsyncSequence without finite-source evidence

- **source_feature_ids:** `policy_visible_async_collector_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ASYNC_COLLECTOR_POLICY_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#async collectProfiles(stream: AsyncSequence<UserId, IOError>) -> List<Profile>
    throws IOError | NetworkError = {
    // checker evidence for `stream` is not finite
    // loadProfileForCollect: #async (UserId) -> Profile throws NetworkError
    return await AsyncCollector::list(
        source: stream,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
// ASYNC_COLLECTOR_POLICY_NOT_ADMITTED
```
## EX-R51a1-ACOLLECT-P-001 — Stable Stage-1 policy-visible async collector

- **source_feature_ids:** `policy_visible_async_collector_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#async collectProfiles(userIds: AsyncSequence<UserId, IOError>) -> List<Profile>
    throws IOError | NetworkError = {
    // checker evidence for `userIds` proves a finite source
    // loadProfileForCollect: #async (UserId) -> Profile throws NetworkError
    return await AsyncCollector::list(
        source: userIds,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
```
## EX-R51a1-AUD-NG-003 — context-free implicit nullary lambda

- **source_feature_ids:** `nullary_lambda_arrow_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONTEXTUAL_LAMBDA_EXPECTED_CALLABLE_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let answer = { 42 }
```
## EX-R51a1-AUD-NG-004 — flow binding cannot target a member

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FLOW_BINDING_TARGET_MUST_BE_NEW_LOCAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
load() -> $state.value
```
## EX-R51a1-AUD-NG-005 — two unlabeled trailing closures

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
transaction { => commit() } { error => rollback(error) }
```
## EX-R51a1-AUD-NG-006 — multi-statement local value body without ret

- **source_feature_ids:** `local_value_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LOCAL_VALUE_BODY_REQUIRES_PATH_TOTAL_RET`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = @if ready {
    log()
    compute()
} else { 0 }
```
## EX-R51a1-AUD-NG-007 — old async declaration prefix

- **source_feature_ids:** `function_profile_introducer_family`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `PREFIX_FUNCTION_PROFILE_REMOVED_USE_DEF_HASH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
async def fetch() -> Bytes = { return bytes }
```
## EX-R51a1-AUD-NG-008 — old entry declaration prefix

- **source_feature_ids:** `function_profile_introducer_family`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **primary_diagnostic:** `PREFIX_FUNCTION_PROFILE_REMOVED_USE_DEF_HASH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
entry def launch() -> Unit = { }
```
## EX-R51a1-AUD-NG-009 — old drop spelling

- **source_feature_ids:** `def_hash_cleanup_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `DEF_HASH_DROP_REMOVED_USE_CLEANUP`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public resource class File { def#drop() = { close() } }
```
## EX-R51a1-AUD-NG-010 — old caller callable profile

- **source_feature_ids:** `scoped_callable_lifetime_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLER_PROFILE_REMOVED_USE_SCOPED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let callback: #caller (Int) -> Unit = #caller{ x => sink(x) }
```
## EX-R51a1-AUD-NG-011 — callable profile must attach to brace

- **source_feature_ids:** `callable_responsibility_profile_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_LITERAL_ATTACHMENT_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #pure { x => x + 1 }
```
## EX-R51a1-AUD-NG-012 — callable profile order is closed

- **source_feature_ids:** `callable_profile_compatibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_ORDER_NONCANONICAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #pure#scoped{ x => x + 1 }
```
## EX-R51a1-AUD-NG-013 — callable profile cannot repeat

- **source_feature_ids:** `callable_profile_compatibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_DUPLICATE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #once#once{ => 1 }
```
## EX-R51a1-AUD-NG-014 — mutable and pure profiles conflict

- **source_feature_ids:** `callable_profile_compatibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_COMBINATION_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #mut#pure{ => 1 }
```
## EX-R51a1-AUD-NG-015 — once mutable combination is not Phase A

- **source_feature_ids:** `callable_profile_compatibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_COMBINATION_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #once#mut{ => 1 }
```
## EX-R51a1-AUD-NG-016 — pure callable cannot throw

- **source_feature_ids:** `pure_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `PURE_CALLABLE_PROFILE_VIOLATION`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #pure{ => throw Failure!() }
```
## EX-R51a1-AUD-NG-017 — pure callable cannot capture mutable state

- **source_feature_ids:** `pure_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `PURE_CALLABLE_MUTABLE_CAPTURE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = [var count = 0] #pure{ => count += 1 }
```
## EX-R51a1-AUD-NG-018 — guard callable result is Bool

- **source_feature_ids:** `guard_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GUARD_CALLABLE_RESULT_MUST_BE_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f: #guard (Int) -> Int = #guard{ x => x + 1 }
```
## EX-R51a1-AUD-NG-019 — guard callable cannot consume

- **source_feature_ids:** `guard_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GUARD_CALLABLE_CONSUME_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #guard{ move value => true }
```
## EX-R51a1-AUD-NG-020 — scoped callable cannot escape

- **source_feature_ids:** `scoped_callable_lifetime_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `SCOPED_CALLABLE_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leak(cb: #scoped () -> Unit) -> #scoped () -> Unit = { return cb }
```
## EX-R51a1-AUD-NG-021 — profiles alone cannot distinguish overloads

- **source_feature_ids:** `callable_profile_compatibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_ONLY_OVERLOAD_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def apply(f: #pure (Int) -> Int) -> Int = { return f(1) }
def apply(f: (Int) -> Int) -> Int = { return f(1) }
```
## EX-R51a1-AUD-NG-022 — sync callable literal marker is redundant and absent

- **source_feature_ids:** `callable_responsibility_profile_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SYNC_CALLABLE_LITERAL_MARKER_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #sync{ => 1 }
```
## EX-R51a1-AUD-NG-023 — async callable literal remains nonactivatable

- **source_feature_ids:** `async_callable_literal_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ASYNC_CALLABLE_LITERAL_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let f = #async{ => await load() }
```
## EX-R51a1-AUD-NG-024 — cleanup declaration is not directly callable

- **source_feature_ids:** `def_hash_cleanup_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CLEANUP_DECLARATION_DIRECT_CALL_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
file ~ cleanup()
```
## EX-R51a1-AUD-NG-025 — context anchor requires a registered evidence role

- **source_feature_ids:** `context_evidence_anchor_framework`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONTEXT_EVIDENCE_ROLE_NOT_REGISTERED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = &ordinary
```
## EX-R51a1-AUD-NG-026 — conformance evidence must be unique

- **source_feature_ids:** `conformance_evidence_origin_bridge_msp`, `trait_witness_coherence_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONFORMANCE_EVIDENCE_ORIGIN_NOT_UNIQUE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sorted = sort(values, using conformance(T conforms Ord<T>))
```
## EX-R51a1-AUD-NG-027 — dynamic extension dispatch remains forbidden

- **source_feature_ids:** `method_extension_resolution_policy`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DYNAMIC_EXTENSION_DISPATCH_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let result = value ~ dynamicExtensionCall()
```
## EX-R51a1-AUD-NG-028 — explicit broadcast marker remains absent

- **source_feature_ids:** `numeric_array_elementwise_power_msp`, `explicit_broadcast_marker_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_BROADCAST_MARKER_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let result = matrix .^ 2
```
## EX-R51a1-AUD-NG-029 — generator borrow capture cannot escape

- **source_feature_ids:** `generator_expression_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GENERATOR_BORROW_CAPTURE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let g = [borrow owner] @for item in owner { yield item }
```
## EX-R51a1-AUD-NG-030 — named arguments use colon

- **source_feature_ids:** `named_argument_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NAMED_ARGUMENT_EQUALS_REMOVED_USE_COLON`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = User!(name = "Ada")
```
## EX-R51a1-AUD-NG-031 — empty slice range uses wildcard

- **source_feature_ids:** `inclusive_slice_range_canonical_msp`, `range_literal_refinement_type`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SLICE_EMPTY_RANGE_FORBIDDEN_USE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let all = values[..]
```
## EX-R51a1-AUD-NG-032 — bare parenless ordinary call remains forbidden

- **source_feature_ids:** `bare_parenless_ordinary_call_not_current`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BARE_PARENLESS_ORDINARY_CALL_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = transform input
```
## EX-R51a1-AUD-NG-033 — old dotted bitwise operator remains removed

- **source_feature_ids:** `old_dotted_bitwise_operator_removed`, `double_glyph_bitwise_operator_family_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `OLD_DOTTED_BITWISE_OPERATOR_REMOVED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bits = left .& right
```
## EX-R51a1-AUD-NG-034 — value-producing @if requires else

- **source_feature_ids:** `local_value_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `IF_EXPR_REQUIRES_ELSE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @if ready { "ready" }
```
## EX-R51a1-BITFIELD-NG-001 — Bitfield layout requires exact closure

- **source_feature_ids:** `bitfield_unsigned_strict_layout_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BITFIELD_LAYOUT_WIDTH_MISMATCH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public bitfield Broken backing UInt32 order ::lsb0 {
    +tag: 4
    _: 4
}
// BITFIELD_LAYOUT_WIDTH_MISMATCH
```
## EX-R51a1-BITFIELD-NG-002 — Implicit raw conversion forbidden

- **source_feature_ids:** `bitfield_checked_raw_codec_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BITFIELD_IMPLICIT_RAW_CONVERSION_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let raw: UInt32 = 7
let header: PacketHeader = raw
// BITFIELD_IMPLICIT_RAW_CONVERSION_FORBIDDEN
```
## EX-R51a1-BITFIELD-P-001 — Strict unsigned bitfield declaration

- **source_feature_ids:** `bitfield_unsigned_strict_layout_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public bitfield PacketHeader
    backing UInt32
    order ::lsb0
{
    +version: 4
    +kind: 4
    +length: 16
    _: 8
}
```
## EX-R51a1-BITFIELD-P-002 — Bitfield materialization and derivation

- **source_feature_ids:** `bitfield_unsigned_strict_layout_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let header = PacketHeader${ version: 1, kind: 2, length: 1024 }
let changed = header!{ length: 2048 }
assert(changed.length == 2048)
```
## EX-R51a1-BITFIELD-P-003 — Checked raw conversion with explicit result

- **source_feature_ids:** `bitfield_checked_raw_codec_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let raw: UInt32 = header.raw
let ::ok(decoded) = PacketHeader::fromRaw(raw)
else ::err(error) => throw error
```
## EX-R51a1-BOUND-NG-001 — Bounded list rejects call-only arguments

- **source_feature_ids:** `bounded_contiguous_index_domain_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BOUNDED_LIST_CALL_ARGUMENT_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = [1..2: name: "A", name: "B"]
// BOUNDED_LIST_CALL_ARGUMENT_FORBIDDEN
```
## EX-R51a1-BOUND-P-001 — Stable bounded one-based logical domain

- **source_feature_ids:** `bounded_contiguous_index_domain_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let days = [1..3: "Mon", "Tue", "Wed"]
assert(days[1] == "Mon")
assert(days[3] == "Wed")
```
## EX-R51a1-DEFER-001 — defer registers one cleanup invocation

- **source_feature_ids:** `single_action_defer_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let handle = open(path)
defer handle ~ close()
process(handle)
```
## EX-R51a1-DEFER-NG-001 — arbitrary defer block is removed

- **source_feature_ids:** `single_action_defer_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
defer {
    closeA()
    closeB()
}
// DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL
```
## EX-R51a1-EVIDENCE-NG-001 — named conformance is excluded from automatic search

- **source_feature_ids:** `named_conformance_selector_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NAMED_CONFORMANCE_NOT_AUTOMATIC`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sorted = sort(values)
// NAMED_CONFORMANCE_NOT_AUTOMATIC
```
## EX-R51a1-EVIDENCE-NG-002 — evidence selector is not a value

- **source_feature_ids:** `static_evidence_selector_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EVIDENCE_SELECTOR_NOT_A_VALUE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let evidence = conformance(String conforms Order)::caseInsensitive
// EVIDENCE_SELECTOR_NOT_A_VALUE
```
## EX-R51a1-EVIDENCE-P-001 — Stable named conformance declaration

- **source_feature_ids:** `named_conformance_selector_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
conformance String conforms Order as caseInsensitive {
    +def compare+(other: String) -> Int = return compareIgnoringCase(self, other)
}
```
## EX-R51a1-EVIDENCE-P-002 — Stable named static evidence selector

- **source_feature_ids:** `named_conformance_selector_msp`, `static_evidence_selector_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sorted = sort(values, using conformance(String conforms Order)::caseInsensitive)
```
## EX-R51a1-FACET-NG-001 — borrow Facet cannot escape its region

- **source_feature_ids:** `facet_borrow_pack_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `FACET_BORROW_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def escape(user: User) -> Facet<borrow any Printable>
= { return facet[borrow user as Printable] }
// FACET_BORROW_ESCAPE_FORBIDDEN
```
## EX-R51a1-FACET-P-001 — Stable Borrow Facet seals evidence without changing the object

- **source_feature_ids:** `facet_borrow_pack_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let printable: Facet<borrow any Printable> = facet[borrow user as Printable]
let text = printable ~ print()
```
## EX-R51a1-FLAGS-NG-001 — Flags result is not Bool

- **source_feature_ids:** `bitfield_flags_specialization_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FLAGS_RESULT_IS_NOT_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if Permission::read && Permission::write { open() }
// FLAGS_RESULT_IS_NOT_BOOL
```
## EX-R51a1-FLAGS-P-001 — Finite-universe flags declaration

- **source_feature_ids:** `bitfield_flags_specialization_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public bitfield#flags Permission backing UInt8 order ::lsb0 {
    +read
    +write
    +execute
    _: 5
}
```
## EX-R51a1-FLAGS-P-002 — Flags operations preserve nominal type

- **source_feature_ids:** `bitfield_flags_specialization_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let access = Permission::read || Permission::execute
let toggled = access ^^ Permission::write
let inverse = ~~toggled
```
## EX-R51a1-GLET-NG-001 — guarded let failure pattern must cover the residual domain

- **source_feature_ids:** `guarded_let_destructured_exit_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GUARDED_LET_RESIDUAL_NOT_EXHAUSTIVE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ::valid(value) = validate(input)
else ::missing => return false
// GUARDED_LET_RESIDUAL_NOT_EXHAUSTIVE
```
## EX-R51a1-GLET-P-001 — Stable guarded let preserves the failure payload

- **source_feature_ids:** `guarded_let_destructured_exit_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ::ok(document) = parse(text)
else ::err(error) => throw error
persist(document)
```
## EX-R51a1-GUARDED-NG-001 — Guarded let conditional exit is forbidden

- **source_feature_ids:** `guarded_let_destructured_exit_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `GUARDED_LET_EXIT_MUST_BE_UNCONDITIONAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ::some(value) = maybeValue else return if retrying
// GUARDED_LET_EXIT_MUST_BE_UNCONDITIONAL
```
## EX-R51a1-GUARDED-P-001 — Guarded let direct unconditional exit

- **source_feature_ids:** `guarded_let_destructured_exit_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ::some(value): Option<Int> = maybeValue else return
consume(value)
```
## EX-R51a1-GUARDED-P-002 — Guarded let exact residual exit

- **source_feature_ids:** `guarded_let_destructured_exit_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ::ok(value) = parse(text)
else ::err(error) => throw error
consume(value)
```
## EX-R51a1-IMPORT-NG-001 — local import cannot mean runtime loading

- **source_feature_ids:** `block_local_import_directive_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LOCAL_IMPORT_RUNTIME_LOADING_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if online {
    import runtime::plugin
}
// LOCAL_IMPORT_RUNTIME_LOADING_FORBIDDEN
```
## EX-R51a1-IMPORT-NG-002 — scoped import block is not an expression

- **source_feature_ids:** `scoped_import_block_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SCOPED_IMPORT_BLOCK_IS_STATEMENT_ONLY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = import std::codec::json in { decode(text) }
// SCOPED_IMPORT_BLOCK_IS_STATEMENT_ONLY
```
## EX-R51a1-IMPORT-P-001 — Stable block-local import is prologue-only

- **source_feature_ids:** `block_local_import_directive_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def ask() -> Int
= {
    import std::inout::input
    return input("n:") ~ toInt()
}
```
## EX-R51a1-IMPORT-P-002 — Stable scoped import limits name visibility

- **source_feature_ids:** `scoped_import_block_msp`, `block_local_import_directive_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
import std::codec::json in {
    let value = decode(text)
    print(value)
}
```
## EX-R51a1-INDEX-001 — ordinary sequences use one-based logical indices

- **source_feature_ids:** `one_based_sequence_logical_indexing`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let xs = [10, 20, 30]
let first = xs[1]
let last = xs[3]
```
## EX-R51a1-INDEX-NG-001 — sequence index zero is outside the logical domain

- **source_feature_ids:** `one_based_sequence_logical_indexing`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ZERO_BASED_INDEX_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let xs = [10, 20, 30]
let bad = xs[0]
// ZERO_BASED_INDEX_NOT_CURRENT
```
## EX-R51a1-INTERPOLATION-NG-001 — Ordinary sequence interpolation remains one-based

- **source_feature_ids:** `interpolation_path_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INTERPOLATION_INDEX_OUT_OF_DOMAIN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(interpolation_path_shorthand)
let text = "$items[0]"
// INTERPOLATION_INDEX_OUT_OF_DOMAIN
```
## EX-R51a1-INTERPOLATION-P-001 — Unicode interpolation boundary and read-only path

- **source_feature_ids:** `interpolation_path_shorthand`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sender = ${name: "민수"}
let object = ${title: "책"}
let message = "$sender.name`가 $object.title`를 보냄"
```
## EX-R51a1-INTERPOLATION-P-002 — Structured render with one-based collection selectors

- **source_feature_ids:** `interpolation_path_shorthand`, `string_render_structured_value_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = String::render(["first", "second"]) {
    "$@[1],$@[2]"
}
assert(text == "first,second")
```
## EX-R51a1-INTERSECT-NG-001 — two concrete bases cannot be intersected

- **source_feature_ids:** `closed_contract_intersection_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INTERSECTION_MULTIPLE_CONCRETE_BASES_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let impossible: File & Socket
// INTERSECTION_MULTIPLE_CONCRETE_BASES_FORBIDDEN
```
## EX-R51a1-INTERSECT-P-001 — Stable closed contract intersection

- **source_feature_ids:** `closed_contract_intersection_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def transmit<T>(value: T) -> Unit
    where T conforms Printable & Sendable
= { print(value) }
```
## EX-R51a1-LAZY-NG-001 — Lazy initialization cycle is rejected

- **source_feature_ids:** `lazy_let_call_by_need_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LAZY_INITIALIZATION_CYCLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let#lazy left = right + 1
let#lazy right = left + 1
// LAZY_INITIALIZATION_CYCLE
```
## EX-R51a1-LAZY-P-001 — Stable pure call-by-need binding

- **source_feature_ids:** `lazy_let_call_by_need_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let#lazy model: Result<Model, error ParseError> = parseResult(text)
inspect(model)
inspect(model)
```
## EX-R51a1-NAMEDREST-NG-001 — Old double-star collector is recovery-only

- **source_feature_ids:** `named_rest_parameter_record_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def configure(options**: Record) -> Unit { }
// NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR
```
## EX-R51a1-NAMEDREST-P-001 — Canonical named-rest collector uses triple star

- **source_feature_ids:** `named_rest_parameter_record_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def configure(options***: Record) -> Unit {
    log(options)
}
configure(**settings)
```
## EX-R51a1-NEW-002 — canonical asynchronous entry introducer

- **source_feature_ids:** `function_profile_introducer_family`, `entry_signature_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry#async launch() -> Unit
    throws Never
    effects {task}
= {
    await warmup()
}
```
## EX-R51a1-NEW-003 — named rest collector and named unfold are distinct

- **source_feature_ids:** `named_rest_parameter_record_msp`, `data_shaping_callshape_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def command(name: String, args...: String, options***: Record) -> Unit = {
    dispatch(name, *args, **options)
}
```
## EX-R51a1-NEW-004 — function type retains repeated and named rest channels

- **source_feature_ids:** `named_rest_parameter_record_msp`, `call_shape_rest_type_residue_law`, `data_shaping_callshape_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type Command = (String, String..., Record***) -> Unit
```
## EX-R51a1-NEW-005 — typed immutable flow binding

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def readPort() -> Int = {
    loadPort() -> $port: Int
    return port
}
```
## EX-R51a1-NEW-006 — typed mutable flow binding

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def incrementCount() -> Int = {
    loadCount() -> $$count: Int
    count += 1
    return count
}
```
## EX-R51a1-NEW-007 — single unlabeled trailing closure

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let names = users ~ map { user => user.name }
```
## EX-R51a1-NEW-008 — multiple callbacks are ordinary named arguments

- **source_feature_ids:** `trailing_closure_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = transaction(onCommit: { => logCommit() }, onRollback: { error => log(error) })
```
## EX-R51a1-NEW-009 — explicit nullary lambda without expected callable

- **source_feature_ids:** `nullary_lambda_arrow_elision_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let answer = { => 42 }
```
## EX-R51a1-NEW-010 — single-expression local value body

- **source_feature_ids:** `local_value_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = @if ready { "ready" } else { "waiting" }
```
## EX-R51a1-NEW-011 — multi-statement local value body uses ret

- **source_feature_ids:** `local_value_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = @try {
    let parsed = parse(text)
    ret parsed
} catch error {
    log(error)
    ret fallback
}
```
## EX-R51a1-NEW-012 — scoped callable lifetime profile

- **source_feature_ids:** `callable_responsibility_profile_core`, `scoped_callable_lifetime_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
withLock(#scoped{ state => inspect(state) })
```
## EX-R51a1-NEW-013 — pure callable behavior profile

- **source_feature_ids:** `callable_responsibility_profile_core`, `pure_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let increment: #pure (Int) -> Int = #pure{ x => x + 1 }
```
## EX-R51a1-NEW-014 — guard callable behavior profile

- **source_feature_ids:** `callable_responsibility_profile_core`, `guard_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let active: #guard (borrow User) -> Bool = #guard{ user => user.active }
```
## EX-R51a1-NEW-015 — mutable callable environment profile

- **source_feature_ids:** `callable_responsibility_profile_core`, `mutable_callable_environment_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let counter = [var n = 0] #mut{ => n += 1 }
```
## EX-R51a1-NEW-016 — closed composite callable profile

- **source_feature_ids:** `callable_responsibility_profile_core`, `callable_profile_compatibility_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let predicate: #scoped#once#guard (borrow Item) -> Bool = #scoped#once#guard{ item => item.valid }
```
## EX-R51a1-NEW-017 — async named declaration profile

- **source_feature_ids:** `function_profile_introducer_family`, `async_function_declaration_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#async fetch(url: String) -> Bytes
    throws NetworkError
    effects {io}
= {
    return await client ~ get(url)
}
```
## EX-R51a1-NEW-018 — guard named declaration profile

- **source_feature_ids:** `function_profile_introducer_family`, `guard_function_for_clause_predicates`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#guard validPort(port: Int) -> Bool = {
    return port >= 0 and port <= 65_535
}
```
## EX-R51a1-NEW-020 — cleanup declaration preserves failure policy

- **source_feature_ids:** `def_hash_cleanup_surface`, `throwing_drop_cleanup_failure_policy`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public resource class File {
    def#cleanup()
        throws CloseError
        effects {io}
    = {
        closeHandle()
    }
}
```
## EX-R51a1-NEW-021 — root conformance evidence selector

- **source_feature_ids:** `conformance_evidence_origin_bridge_msp`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public trait Rank<T> {
    +def before+(other: T) -> Bool
        throws Never
        effects {}
}
public conformance Int conforms Rank<Int> {
    +def before+(other: Int) -> Bool
        throws Never
        effects {}
    = {
        return self < other
    }
}
def sort<T>(xs: List<T>, using order: witness Rank<T>) -> List<T> = {
    return stableSort(xs, using order)
}
let sorted = sort([3, 1, 2], using conformance(Int conforms Rank<Int>))
```
## EX-R51a1-NEW-022 — readonly view lifetime

- **source_feature_ids:** `readonly_view`, `foundation_kind_separation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def inspect(view: ReadonlyView<Bytes>) -> Int = {
    return view ~ count
}
```
## EX-R51a1-NEW-023 — unique Box owner

- **source_feature_ids:** `box_ownership`, `foundation_kind_separation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let node: Box<Node> = Box!(Node!(value: 1))
let moved = move node
```
## EX-R51a1-NEW-024 — replace evaluates a place once

- **source_feature_ids:** `place_replace`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let old = replace(buffer[index()], replacement)
```
## EX-R51a1-NEW-025 — mutable-list snapshot precedes consuming freeze

- **source_feature_ids:** `collection_freeze_transition_profile`, `collection_snapshot_value_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def snapshotThenFreeze(move values: MutableList<Int>) -> FrozenList<Int> = {
    let snapshot: ListSnapshot<Int> = values ~ snapshot()
    observe(snapshot)
    return values ~ freeze()
}
```
## EX-R51a1-NEW-026 — owned downcast preserves unmatched source

- **source_feature_ids:** `owned_downcast_result`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let outcome: OwnedDowncast<Target, Source> = value ~ downcastOwned()
@match outcome {
    ::matched(target) => use(target)
    ::unmatched(original) => recover(original)
}
```
## EX-R51a1-NEW-027 — guarded transfer evaluates guard before payload

- **source_feature_ids:** `guard_first_payload_lazy_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def transfer(move resource: Resource, ready: Bool) -> Resource = {
    return move resource if ready
    return move resource
}
```
## EX-R51a1-NEW-028 — loop owns one outcome handler

- **source_feature_ids:** `loop_with_outcome_handler_ast_law`, `structured_break_chain_spelling`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
while ready {
    break result if finished
} match {
    ::completed => logDone()
    ::break(value) => consume(value)
}
```
## EX-R51a1-NEW-029 — implicit placeholder is checked after overload selection

- **source_feature_ids:** `implicit_lambda_at_placeholder_msp`, `implicit_lambda_overload_staging_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values = items ~ map(@.name)
```
## EX-R51a1-NEW-030 — scoped pure callback in Prelude

- **source_feature_ids:** `scoped_callable_lifetime_profile`, `pure_callable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let total = withBorrowed(values, #scoped#pure{ xs => xs ~ count })
```
## EX-R51a1-NEW-031 — ByteView remains owner-bounded

- **source_feature_ids:** `byte_view`, `readonly_view`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def checksum(borrow bytes: Bytes) -> UInt64 = {
    let view: ByteView = bytes ~ view()
    return hashBytes(view)
}
```
## EX-R51a1-NG-001 — rejected: optional chaining

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `optional_chaining_not_current_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `OPTIONAL_CHAINING_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x = user?.name
```
## EX-R51a1-NG-002 — rejected: optional callable invocation

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `optional_callable_invocation_not_current_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `OPTIONAL_CALLABLE_INVOCATION_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x = maybeFn?(1)
```
## EX-R51a1-NG-003 — rejected: dotted static path

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `DOTTED_STATIC_PATH_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x = Type.member
```
## EX-R51a1-NG-004 — rejected: where T : Trait

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `WHERE_COLON_TRAIT_CONSTRAINT_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def f<T>(x: T) where T : Hashable -> Int = { return 0 }
```
## EX-R51a1-NG-005 — rejected: structural conformance

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `STRUCTURAL_CONFORMANCE_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x: Printable = objectWithPrintMethod
```
## EX-R51a1-NG-006 — rejected: extension auto-witness

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `extension_auto_witness_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `EXTENSION_AUTO_WITNESS_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
extension User as printable { +def print() -> Unit = { } }
```
## EX-R51a1-NG-007 — rejected: raw first-class Witness value

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `RAW_WITNESS_VALUE_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let w: Witness<Ord<Int>> = makeWitness()
```
## EX-R51a1-NG-008 — rejected: ordinary `def = expr` body

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `FUNCTION_EXPRESSION_BODY_REQUIRES_RETURN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def inc(x: Int) -> Int = x + 1
```
## EX-R51a1-NG-009 — rejected: standalone !expr

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `standalone_bang_not_current_not_word_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `STANDALONE_BANG_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let x = !ready
```
## EX-R51a1-NG-010 — rejected: unnamed def!(...) constructor

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `named_constructor_surface_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `CONSTRUCTOR_REQUIRES_NAME`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class User { +def!(name: String) = { } }
```
## EX-R51a1-NG-011 — rejected: bodyless ordinary function

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `BODYLESS_ORDINARY_FUNCTION_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def declaredOnly(x: Int) -> Int
```
## EX-R51a1-NG-012 — rejected: standalone annotation statement

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `annotation_structural_attachment`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `ANNOTATION_TARGET_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
@deprecated("orphan")
```
## EX-R51a1-NG-013 — rejected: ordinary List literal without an admitted element join

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let numbers: List<Int> = [1, "two"]
```
## EX-R51a1-NG-014 — rejected: incoherent witness identity whose resolved trait does not match the explicit witness parameter

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`, `explicit_witness_argument_keyword_spelling`, `conformance_evidence_origin_bridge_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_ARGUMENT_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def wrongOrder(using stringOrder: witness Ord<String>) -> List<Int> = {
    return sort([3, 1, 2], using stringOrder)
}
```
## EX-R51a1-NG-015 — rejected: effectful or mutable library top-level binding

- **source_feature_ids:** `library_static_binding_initializer_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `LIBRARY_STATIC_BINDING_INITIALIZER_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
var session = connectNetwork()
```
## EX-R51a1-NG-016 — rejected: entry outside the four admitted signatures

- **source_feature_ids:** `entry_signature_contract`, `explicit_entry_function_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **primary_diagnostic:** `ENTRY_SIGNATURE_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch(code: Int) -> String = { return "bad" }
```
## EX-R51a1-NG-017 — rejected: stored field/constructor/drop inside enum

- **source_feature_ids:** `enum_member_declaration_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `ENUM_MEMBER_KIND_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum State { ready; +var count: Int = 0 }
```
## EX-R51a1-NG-018 — rejected: semicolon run that does not match the exact-shape NumericArray rank boundary

- **source_feature_ids:** `shaped_literal_separator_rank_law`, `shaped_semicolon_literal_body_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `SHAPED_LITERAL_SEPARATOR_RANK_MISMATCH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let broken = #2,2[1, 2;; 3, 4;;]
```
## EX-R51a1-NG-019 — rejected: computed expression after the using keyword

- **source_feature_ids:** `explicit_witness_argument_keyword_spelling`, `explicit_witness_argument_msp`, `conformance_evidence_origin_bridge_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_ARGUMENT_REQUIRES_IDENTIFIER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let sorted = sort(values, using makeOrder())
```
## EX-R51a1-NG-020 — rejected: entry declaration in a library source, including an annotated entry

- **source_feature_ids:** `entry_signature_contract`, `source_role_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `ENTRY_NOT_ALLOWED_IN_LIBRARY_SOURCE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
@deprecated("wrong role")
def#entry launch() -> Unit = { }
```
## EX-R51a1-NG-021 — rejected: top-level let/var in an executable source

- **source_feature_ids:** `source_role_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **primary_diagnostic:** `TOP_LEVEL_BINDING_NOT_ALLOWED_IN_EXECUTABLE_SOURCE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let session = connectNetwork()
def#entry launch() -> Unit = { }
```
## EX-R51a1-NG-022 — rejected: extern#C def#unsafe without its current gate

- **source_feature_ids:** `ffi_minimum_sound_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FFI_MINIMUM_SOUND_PROFILE_REQUIRES_FEATURE_GATE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
extern#C def#unsafe c_abs(x: Int) -> Int
```
## EX-R51a1-NG-023 — rejected: extern c block without its current gate

- **source_feature_ids:** `ffi_c_extern_unsafe_surface_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FFI_C_EXTERN_UNSAFE_SURFACE_MSP_REQUIRES_FEATURE_GATE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
extern c("sqlite3") {
    unsafe def sqlite3_close(db: RawPtr<sqlite3>) -> CInt
        effects {io}
}
```
## EX-R51a1-NG-024 — rejected: dynamic unit conversion without active stdlib profile

- **source_feature_ids:** `dynamic_unit_conversion_provider_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DYNAMIC_UNIT_CONVERSION_PROFILE_NOT_ACTIVE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let converted = price ~ asUnitUsing(provider, 1[USD])
```
## EX-R51a1-NG-026 — rejected: explicit entry declaration inside a script source

- **source_feature_ids:** `source_role_contract`, `entry_target_uniqueness_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
print("script boot")
def#entry launch() -> Unit = { }
```
## EX-R51a1-NG-027 — rejected: unknown feature id in #preview

- **source_feature_ids:** `preview_profile_root_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **primary_diagnostic:** `PREVIEW_GATE_UNKNOWN_FEATURE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(unknown_feature_id)
let value = 1
```
## EX-R51a1-NG-028 — rejected: PREVIEW_DESIGN id in #preview

- **source_feature_ids:** `preview_profile_root_contract`, `dynamic_unsafe_quarantine_scope_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **primary_diagnostic:** `PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(dynamic_unsafe_quarantine_scope_msp)
let value = 1
```
## EX-R51a1-NG-029 — rejected: duplicate feature id in #preview

- **source_feature_ids:** `preview_profile_root_contract`, `ffi_c_extern_unsafe_surface_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **primary_diagnostic:** `PREVIEW_GATE_DUPLICATE_FEATURE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_c_extern_unsafe_surface_msp)
let value = 1
```
## EX-R51a1-NG-030 — rejected: missing explicit Preview dependency

- **source_feature_ids:** `preview_profile_root_contract`, `ffi_c_extern_unsafe_surface_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **primary_diagnostic:** `PREVIEW_GATE_DEPENDENCY_MISSING`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp)
extern c("libc") { unsafe def puts(text: CString) -> Int }
```
## EX-R51a1-NG-031 — rejected: #preview after ModuleDecl or a source item

- **source_feature_ids:** `preview_profile_root_contract`, `ffi_c_extern_unsafe_surface_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `explicit_feature_gate`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `PreviewScriptSourceFile`
- **primary_diagnostic:** `PREVIEW_GATE_PLACEMENT_INVALID`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
module demo
#preview(ffi_c_extern_unsafe_surface_msp)
let converted = price ~ asUnitUsing(provider, 1[USD])
```
## EX-R51a1-NG-032 — rejected: top-level visibility modifier on a local function

- **source_feature_ids:** `nested_function_local_def_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NESTED_DEF_VISIBILITY_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def outer() -> Unit = {
    public def inner() -> Unit = { }
}
```
## EX-R51a1-NG-033 — rejected: implicit outer capture by a local function

- **source_feature_ids:** `nested_function_local_def_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NESTED_DEF_CAPTURE_LIST_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def outer(x: Int) -> Int = {
    def inner() -> Int = { return x }
    return inner()
}
```
## EX-R51a1-NG-034 — rejected: local function reference before declaration

- **source_feature_ids:** `nested_function_local_def_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NESTED_DEF_FORWARD_REFERENCE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def outer() -> Int = {
    let value = inner()
    def inner() -> Int = { return 1 }
    return value
}
```
## EX-R51a1-NG-035 — rejected: CaptureList separated from its owner by NEWLINE

- **source_feature_ids:** `nested_function_local_def_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NESTED_DEF_CAPTURE_LIST_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def outer(x: Int) -> Int = {
    [borrow x]
    def inner() -> Int = { return x }
    return inner()
}
```
## EX-R51a1-NG-036 — rejected: radix-prefixed NumericArray static dimension

- **source_feature_ids:** `numeric_array_sharp_shape_literal_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMARR_DIMENSION_STATIC_INT_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalidRadixShape = #0x2,2[1, 2; 3, 4;]
```
## EX-R51a1-NG-037 — rejected: suffixed NumericArray static dimension

- **source_feature_ids:** `numeric_array_sharp_shape_literal_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMARR_DIMENSION_STATIC_INT_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalidSuffixedShape = #2u8,2[1, 2; 3, 4;]
```
## EX-R51a1-NG-038 — rejected: numeric radix prefix without a digit

- **source_feature_ids:** `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MALFORMED_NUMERIC_RADIX_PREFIX`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalidRadix = 0x
```
## EX-R51a1-NG-039 — rejected: ordinary List literal mixing unsuffixed Int and suffixed u8 without context

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let mixed = [1, 2u8]
```
## EX-R51a1-NG-040 — rejected: ordinary List literal mixing suffixed i8 and unsuffixed Int without context

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let mixed = [1i8, 300]
```
## EX-R51a1-NG-041 — rejected: ordinary List literal mixing Int and Float64 without context

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let mixed = [1, 2.0]
```
## EX-R51a1-NG-042 — rejected: out-of-range unsuffixed integer in a fixed-width contextual List

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bytes: List<UInt8> = [0, 256]
```
## EX-R51a1-NG-043 — rejected: lone underscore used where a declaration Identifier is required

- **source_feature_ids:** `r51a1_machine_closed_lexical_modes`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPECTED_IDENTIFIER_FOUND_WILDCARD`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def _() -> Unit = { }
```
## EX-R51a1-NG-046 — rejected: explicit witness parameter returned as an ordinary value

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leakReturn<T>(using order: witness Ord<T>) -> Unit = {
    return order
}
```
## EX-R51a1-NG-047 — rejected: explicit witness parameter stored in a local binding

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leakStore<T>(using order: witness Ord<T>) -> Unit = {
    let leaked = order
}
```
## EX-R51a1-NG-048 — rejected: explicit witness parameter captured by a closure

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leakCapture<T>(using order: witness Ord<T>) -> Unit = {
    let comparator = [borrow order] { value: T => compare(value, value, using order) }
}
```
## EX-R51a1-NG-049 — rejected: explicit witness parameter passed through an ordinary argument channel

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`, `explicit_witness_argument_keyword_spelling`, `conformance_evidence_origin_bridge_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_ARGUMENT_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leakOrdinary<T>(using order: witness Ord<T>) -> Unit = {
    sink(order)
}
```
## EX-R51a1-NG-050 — rejected: ordinary forged value supplied as explicit witness evidence

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_argument_msp`, `explicit_witness_argument_keyword_spelling`, `conformance_evidence_origin_bridge_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_ARGUMENT_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let forged = 0
let sorted = sort([3, 1, 2], using forged)
```
## EX-R51a1-NG-051 — rejected: empty ordinary List literal without a fixed context

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let empty = []
```
## EX-R51a1-NG-052 — rejected: unsuffixed Float64 literal in a contextual List<Float32>

- **source_feature_ids:** `ordinary_list_literal_surface`, `numeric_literal_suffix`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values: List<Float32> = [1.0]
```
## EX-R51a1-NG-053 — rejected: unsuffixed Int literal in a contextual List<ISize>

- **source_feature_ids:** `ordinary_list_literal_surface`, `numeric_literal_suffix`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let indexes: List<ISize> = [1]
```
## EX-R51a1-NG-054 — rejected: out-of-range negative literal in a contextual List<Int8>

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values: List<Int8> = [-129]
```
## EX-R51a1-NG-055 — rejected: negative literal in a contextual List<UInt8>

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_CONTEXT_INTEGER_OUT_OF_RANGE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values: List<UInt8> = [-1]
```
## EX-R51a1-NG-056 — rejected: explicit witness parameter assigned into a field

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leakField<T>(using order: witness Ord<T>, holder: Holder) -> Unit = {
    holder.order = order
}
```
## EX-R51a1-NG-057 — rejected: explicit witness parameter inserted into a container

- **source_feature_ids:** `explicit_witness_parameter_msp`, `explicit_witness_parameter_narrow_stable_law`, `explicit_witness_argument_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `EXPLICIT_WITNESS_PARAMETER_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def leakContainer<T>(using order: witness Ord<T>) -> Unit = {
    let leaked = [order]
}
```
## EX-R51a1-NG-058 — rejected: cyclic library top-level let initializer graph

- **source_feature_ids:** `library_static_binding_initializer_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `LIBRARY_STATIC_BINDING_INITIALIZER_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let first: Int = second
let second: Int = first
```
## EX-R51a1-NG-059 — rejected: library top-level let initializer that creates a task

- **source_feature_ids:** `library_static_binding_initializer_msp`, `structured_task_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `LIBRARY_STATIC_BINDING_INITIALIZER_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let background = spawn async { => 1 }
```
## EX-R51a1-NG-060 — rejected: generic entry function

- **source_feature_ids:** `entry_signature_contract`, `explicit_entry_function_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **primary_diagnostic:** `ENTRY_SIGNATURE_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry launch<T>() -> Unit = {
}
```
## EX-R51a1-NG-061 — rejected: two selected entry declarations in one executable root

- **source_feature_ids:** `entry_signature_contract`, `entry_target_uniqueness_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `executable`
- **source_root:** `ExecutableSourceFile`
- **primary_diagnostic:** `ENTRY_DECL_DUPLICATE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#entry first() -> Unit = {
}
def#entry second() -> Unit = {
}
```
## EX-R51a1-NG-062 — rejected: constructor declaration inside an enum

- **source_feature_ids:** `enum_member_declaration_surface`, `enum_member_body_restoration`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `ENUM_MEMBER_KIND_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum BadConstructor {
    ready
    +def! new() = { }
}
```
## EX-R51a1-NG-063 — rejected: drop declaration inside an enum

- **source_feature_ids:** `enum_member_declaration_surface`, `enum_member_body_restoration`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `ENUM_MEMBER_KIND_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum BadDrop {
    ready
    def#cleanup() = { }
}
```
## EX-R51a1-NG-064 — rejected: assignment-compatible subtype in a contextual List without normalized-type identity

- **source_feature_ids:** `ordinary_list_literal_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let animals: List<Animal> = [dog]
```
## EX-R51a1-NG-065 — rejected: top-level static class declaration

- **source_feature_ids:** `class_static_activation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `STATIC_CLASS_DECLARATION_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public static class Cache { }
```
## EX-R51a1-NG-066 — rejected: top-level static def declaration

- **source_feature_ids:** `function_static_activation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `STATIC_FUNCTION_DECLARATION_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public static def warm() -> Unit = { }
```
## EX-R51a1-NG-067 — rejected: stored field inside an extension set

- **source_feature_ids:** `extension_set_member_plain_def_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `EXTENSION_SET_STORED_MEMBER_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
extension set UserFormatting {
    +let cached: String
}
```
## EX-R51a1-NG-068 — rejected: one recoverable error family exposed through both Result and throws

- **source_feature_ids:** `result_error_set_model`, `result_throws_overlap_forbidden_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `RESULT_THROWS_CHANNEL_OVERLAP`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def load() -> Result<Bytes, error IOError>
    throws IOError
    effects {io}
= { return read() }
```
## EX-R51a1-NG-069 — rejected: effectful or authority-bearing R0 refinement predicate

- **source_feature_ids:** `refinement_type_phase_a`, `r0_guard_predicate_calculus`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `REFINEMENT_R0_PREDICATE_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public type CurrentTick = Int where readClock() > 0
```
## EX-R51a1-NG-070 — rejected: duplicate or unknown named call shape

- **source_feature_ids:** `static_labelrow_argpack_callshape_model`, `data_shaping_callshape_model`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `STATIC_CALL_SHAPE_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let request = Request!(url: first, url: second, agge: 30)
```
## EX-R51a1-NG-071 — rejected: type token used as a runtime reflective value

- **source_feature_ids:** `type_token_authority_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TYPE_TOKEN_RUNTIME_AUTHORITY_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let reflected = User
```
## EX-R51a1-NG-072 — rejected: live inout borrow crossing await without proof

- **source_feature_ids:** `inout_borrow_move_modes`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `OWNERSHIP_MODE_ADMISSION_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def#async update(inout value: Int) -> Unit = {
    await checkpoint()
    value = value + 1
}
```
## EX-R51a1-NG-073 — rejected: dynamic unit exponent in the exact canonical core

- **source_feature_ids:** `unit_canonicalization`, `numeric_literal_lexical_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `UNIT_EXPONENT_REQUIRES_STATIC_INT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let powered = 1[m^runtimeExponent]
```
## EX-R51a1-NG-074 — rejected: resource or authority-bearing context value

- **source_feature_ids:** `context_value_admissibility`, `explicit_context_parameter_role_law`, `shared_owner_handle_minimum_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CONTEXT_VALUE_REQUIRES_REUSABLE_SHAREABLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = format(3.14, context openDatabaseSession())
```
## EX-R51a1-NG-075 — rejected: deep prototype derivation without deep-clone responsibility

- **source_feature_ids:** `nominal_prototype_derivation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `PROTOTYPE_DERIVATION_RESPONSIBILITY_MISMATCH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let detached = resourceGraph!!{ retries: 3 }
```
## EX-R51a1-NG-076 — rejected: automatic ConstructionRow requested for an ineligible data class

- **source_feature_ids:** `generated_data_class_materialization_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DATA_CLASS_MATERIALIZATION_PROFILE_NOT_SATISFIED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Session(+var handle: Handle)
let session = Session${ handle: openHandle() }
```
## EX-R51a1-NG-077 — rejected: matrix product with mismatched inner dimensions

- **source_feature_ids:** `matrix_multiplication_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `MATRIX_PRODUCT_DIMENSION_MISMATCH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = #2,3[1, 2, 3; 4, 5, 6;] ** #2,4[1, 2, 3, 4; 5, 6, 7, 8;]
```
## EX-R51a1-NG-078 — rejected: mixed linear-product fold whose matrix result is used as a dot-product vector

- **source_feature_ids:** `matrix_multiplication_operator_msp`, `vector_dot_product_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `DOT_PRODUCT_REQUIRES_RANK1_VECTORS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = (#2,3[1, 2, 3; 4, 5, 6;] ** #3,4[1, 2, 3, 4; 5, 6, 7, 8; 9, 10, 11, 12;]) *+ #[1, 2, 3, 4]
```
## EX-R51a1-RCTS-FACET-NG-001 — Concrete-payload Facet spelling removed

- **source_feature_ids:** `facet_borrow_pack_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FACET_CONCRETE_TYPE_SPELLING_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let printable: Facet<User as Printable>
// FACET_CONCRETE_TYPE_SPELLING_FORBIDDEN
```
## EX-R51a1-RCTS-FACET-P-001 — Canonical borrow Facet

- **source_feature_ids:** `facet_borrow_pack_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let printable: Facet<borrow any Printable> =
    facet[borrow user as Printable]
let text = printable ~ print()
```
## EX-R51a1-RCTS-INTERSECTION-NG-001 — Bare contract bundle is not a value carrier

- **source_feature_ids:** `closed_contract_intersection_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INTERSECTION_BARE_CONTRACT_NOT_VALUE_TYPE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value: Printable & Auditable
// INTERSECTION_BARE_CONTRACT_NOT_VALUE_TYPE
```
## EX-R51a1-RCTS-INTERSECTION-P-001 — Concrete contract intersection

- **source_feature_ids:** `closed_contract_intersection_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type PrintableDocument = Document & Printable & Auditable
```
## EX-R51a1-RCTS-LAZY-NG-001 — Lazy hidden throw channel forbidden

- **source_feature_ids:** `lazy_let_call_by_need_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LAZY_HIDDEN_FAILURE_CHANNEL_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let#lazy parsed = throwingParse(text)
// LAZY_HIDDEN_FAILURE_CHANNEL_FORBIDDEN
```
## EX-R51a1-RCTS-LAZY-P-001 — Fallible lazy computation uses explicit Result

- **source_feature_ids:** `lazy_let_call_by_need_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let#lazy parsed: Result<Model, error ParseError> = parseResult(text)
```
## EX-R51a1-RCTS-UNION-NG-001 — Automatic union join is forbidden

- **source_feature_ids:** `closed_anonymous_union_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `UNION_AUTOMATIC_JOIN_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = @if cond { 1 } else { "one" }
// UNION_AUTOMATIC_JOIN_FORBIDDEN
```
## EX-R51a1-RCTS-UNION-P-001 — Explicit closed union and exhaustive match

- **source_feature_ids:** `closed_anonymous_union_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
type TextOrNumber = Int | String
let value: TextOrNumber = 13
let text = @match value {
    n: Int => n ~ toString()
    s: String => s
}
```
## EX-R51a1-RECEIVER-001 — Explicit consuming receiver-owner result

- **source_feature_ids:** `receiver_owner_result_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#consume normalize+() -> Self = {
    return move self
}
```
## EX-R51a1-RECEIVER-NG-001 — Implicit receiver result forbidden

- **source_feature_ids:** `receiver_owner_result_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RECEIVER_OWNER_RESULT_MUST_BE_EXPLICIT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#consume normalize+() -> Self = {
    normalizeFields()
}
// RECEIVER_OWNER_RESULT_MUST_BE_EXPLICIT
```
## EX-R51a1-RENDER-NG-001 — Explicit and implicit renderer parameters cannot mix

- **source_feature_ids:** `string_render_structured_value_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `IMPLICIT_AT_WITH_EXPLICIT_PARAMETER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = String::render(person) { p =>
    "${@.name}"
}
// IMPLICIT_AT_WITH_EXPLICIT_PARAMETER
```
## EX-R51a1-RENDER-P-001 — String render through braced implicit-at expression

- **source_feature_ids:** `string_render_structured_value_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = String::render(${name: "John", age: 25}) {
    "${@.name}:${@.age}"
}
assert(text == "John:25")
```
## EX-R51a1-RENDER-P-002 — Nested render binds the nearest implicit at

- **source_feature_ids:** `string_render_structured_value_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = String::render(${name: "outer", inner: ${name: "inner"}}) { root =>
    String::render(root.inner) {
        "${root.name}/${@.name}"
    }
}
assert(text == "outer/inner")
```
## EX-R51a1-SLICE-001 — slice preserves selected logical coordinates

- **source_feature_ids:** `slice_logical_domain_preservation`, `one_based_sequence_logical_indexing`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values = [10, 20, 30, 40, 50]
let middle = values[2..4]
let sameCoordinate = middle[3]
```
## EX-R51a1-SLICE-NG-001 — preserved slice coordinates reject an out-of-domain index

- **source_feature_ids:** `slice_logical_domain_preservation`
- **checker_trace_ids:** `LogicalIndexDomainAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INDEX_OUT_OF_LOGICAL_DOMAIN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values = [10, 20, 30, 40, 50]
let middle = values[2..4]
let bad = middle[1]
// INDEX_OUT_OF_LOGICAL_DOMAIN
```
## EX-R51a1-TUPLE-001 — tuple ordinal projection is compile-time and one-based

- **source_feature_ids:** `tuple_ordinal_projection_1_based`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let pair = (7, "seven")
let number = pair.1
let text = pair.2
```
## EX-R51a1-TUPLE-NG-001 — tuple ordinal zero is rejected

- **source_feature_ids:** `tuple_ordinal_projection_1_based`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TUPLE_ORDINAL_ZERO_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let pair = (7, "seven")
let bad = pair.0
// TUPLE_ORDINAL_ZERO_FORBIDDEN
```
## EX-R51a1-UNION-NG-001 — union value requires narrowing

- **source_feature_ids:** `closed_anonymous_union_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `UNION_VALUE_REQUIRES_NARROWING`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value: Float64 | String = "Hello"
print(value.length)
// UNION_VALUE_REQUIRES_NARROWING
```
## EX-R51a1-UNION-P-001 — Stable closed anonymous union

- **source_feature_ids:** `closed_anonymous_union_type_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value: Float64 | String = "Hello"
let text = @match value {
    x: Float64 => x ~ display()
    s: String => s
}
```
## EX-R51a1-USE-001 — block-prologue use narrows lexical activation

- **source_feature_ids:** `block_local_use_activation_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def render(user: User) -> String
= {
    use app::formatting::compact
    return user ~ display()
}
```
## EX-R51a1-USE-002 — scoped use block is a lexical statement

- **source_feature_ids:** `scoped_use_block_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use std::units::si in {
    let distance = 2500[m]
    print(distance)
}
```
## EX-R51a1-USE-NG-001 — use cannot acquire runtime authority

- **source_feature_ids:** `block_local_use_activation_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LOCAL_USE_RUNTIME_AUTHORITY_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use system::network::authority {
    connect(endpoint)
}
// LOCAL_USE_RUNTIME_AUTHORITY_FORBIDDEN
```
## EX-R51a1-USE-NG-002 — scoped use cannot be used as a value

- **source_feature_ids:** `scoped_use_block_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SCOPED_USE_BLOCK_IS_STATEMENT_ONLY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let distance = use std::units::si in {
    2500[m]
}
// SCOPED_USE_BLOCK_IS_STATEMENT_ONLY
```

# R51b integrated Grammar examples
## EX-R51b-GRAM-P-001 — Named rest and named unfold have distinct markers

- **source_feature_ids:** `named_rest_parameter_record_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def configure(options***: Record) -> Unit = { apply(options) }
configure(**settings)
```
## EX-R51b-GRAM-NG-001 — Old double-star named-rest collector is recovery-only

- **source_feature_ids:** `named_rest_parameter_record_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def configure(options**: Record) -> Unit = { }
// NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR
```
## EX-R51b-GRAM-P-002 — Lazy binding uses the hash role

- **source_feature_ids:** `lazy_let_call_by_need_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let#lazy model: Result<Model, error ParseError> = parseResult(text)
inspect(model)
```
## EX-R51b-GRAM-NG-002 — At-sigil lazy spelling is recovery-only

- **source_feature_ids:** `lazy_let_call_by_need_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LAZY_BINDING_USE_HASH`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let@lazy model = loadModel()
// LAZY_BINDING_USE_HASH
```
## EX-R51b-GRAM-P-003 — Unit products use star and slash

- **source_feature_ids:** `unit_operation_policy_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let acceleration = 9.8[m/s^2]
```
## EX-R51b-GRAM-NG-004 — Unit middle dot is recovery-only

- **source_feature_ids:** `unit_operation_policy_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `UNIT_MULTIPLICATION_USE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let momentum = 3[kg·m/s]
// UNIT_MULTIPLICATION_USE_STAR
```
## EX-R51b-GRAM-P-004 — Data class may omit its body

- **source_feature_ids:** `class_final_by_default`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public data class Point(x: Int, y: Int)
```
## EX-R51b-GRAM-NG-005 — Ordinary class requires a body

- **source_feature_ids:** `class_final_by_default`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `CLASS_BODY_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Point(x: Int, y: Int)
// CLASS_BODY_REQUIRED
```
## EX-R51b-GRAM-NG-006 — Ret is not a generic block tail

- **source_feature_ids:** `local_value_body_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `RET_OUTSIDE_LAMBDA`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def answer() -> Int = {
    ret 42
}
// RET_OUTSIDE_LAMBDA
```
## EX-R51b-GRAM-P-005 — Typed binding pattern is current

- **source_feature_ids:** `pattern_decomposition`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value: Int = readValue()
```
## EX-R51b-GRAM-NG-007 — Guarded-let failure cannot use ret

- **source_feature_ids:** `guarded_let_destructured_exit_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `GUARDED_LET_EXIT_MUST_BE_UNCONDITIONAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def read() -> Int = {
    let ::some(value) = source else ret 0
    return value
}
// GUARDED_LET_EXIT_MUST_BE_UNCONDITIONAL
```
## EX-R51b-GRAM-P-006 — Defer registers one cleanup invocation

- **source_feature_ids:** `single_action_defer_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def write(file: File) -> Unit = {
    defer file ~ close()
    file ~ write(data)
}
```
## EX-R51b-GRAM-NG-008 — Defer block is not current

- **source_feature_ids:** `single_action_defer_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
defer { closeAll() }
// DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL
```
## EX-R51b-GRAM-NG-009 — Match arm admits at most one guard

- **source_feature_ids:** `match_arm_guard_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MATCH_ARM_SINGLE_GUARD_ONLY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
match value {
    x if ready if valid => use(x)
    otherwise => skip()
}
// MATCH_ARM_SINGLE_GUARD_ONLY
```
## EX-R51b-GRAM-P-007 — Subjectless match is owned by the preceding loop

- **source_feature_ids:** `loop_outcome_match_statement_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for item in items {
    if done(item) { break item }
}
match {
    ::break(item) => report(item)
    ::completed => reportDone()
}
```
## EX-R51b-GRAM-NG-010 — Standalone subjectless match is rejected

- **source_feature_ids:** `loop_outcome_match_statement_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LOOP_OUTCOME_MATCH_MUST_FOLLOW_LOOP`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
match { ::completed => done() }
// LOOP_OUTCOME_MATCH_MUST_FOLLOW_LOOP
```
## EX-R51b-GRAM-NG-011 — Async for does not own an outcome match

- **source_feature_ids:** `async_iteration`, `loop_outcome_match_statement_msp`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ASYNC_FOR_OUTCOME_MATCH_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for await item in stream { consume(item) }
match { ::completed => done() }
// ASYNC_FOR_OUTCOME_MATCH_NOT_ADMITTED
```
## EX-R51b-GRAM-P-008 — Checked cast and negated relations are attached parser sequences

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let parsed = value as? Int
if item !is Secret and item !in denied { use(item) }
```
## EX-R51b-GRAM-NG-012 — Cast modifier cannot contain trivia

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CAST_MODIFIER_MUST_BE_ADJACENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let parsed = value as ? Int
// CAST_MODIFIER_MUST_BE_ADJACENT
```
## EX-R51b-GRAM-NG-013 — Negated relation cannot contain trivia

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NEGATED_RELATION_MUST_BE_ADJACENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if item ! is Secret { use(item) }
// NEGATED_RELATION_MUST_BE_ADJACENT
```
## EX-R51b-GRAM-P-009 — Full interpolation shorthand path is current

- **source_feature_ids:** `interpolation_path_shorthand`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = "user=$user.profile.names[1] id=$pair.1"
```
## EX-R51b-GRAM-NG-014 — Interpolation shorthand call requires braces

- **source_feature_ids:** `interpolation_path_shorthand`, `r51e_frontend_grammar_current_canonical`, `string_interpolation_braced_expr_core`, `string_interpolation_shorthand_factor_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INTERPOLATION_COMPLEX_EXPRESSION_REQUIRES_BRACES`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = "value=$provider.load()"
// INTERPOLATION_COMPLEX_EXPRESSION_REQUIRES_BRACES
```
## EX-R51b-GRAM-P-010 — Hash role trivia is accepted and formatter-normalized

- **source_feature_ids:** `function_profile_introducer_family`, `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def # pure compute() -> Int = return 42
```
## EX-R51b-GRAM-NG-015 — Exact at introducer cannot cross a physical line

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `AT_EXACT_INTRODUCER_LINE_BREAK_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = @
match input { otherwise => 0 }
// AT_EXACT_INTRODUCER_LINE_BREAK_FORBIDDEN
```
## EX-R51c-001 — Named rest uses triple-star while named unfold uses double-star

- **source_feature_ids:** `named_rest_parameter_record_msp`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`, `NamedRestParameterRecordAndLastPosition`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options***: Record) -> Unit = {
    apply(**options)
}
public type Configure = (Record***) -> Unit
```
## EX-R51c-002 — Double-star named-rest parameter is removed

- **source_feature_ids:** `named_rest_parameter_record_msp`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options**: Record) -> Unit = { }
```
## EX-R51c-003 — Class instance methods require dispatch markers; fields do not

- **source_feature_ids:** `dispatch_marker_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
open class Counter {
    -var value: Int = 0
    +def increment.() -> Unit = { value += 1 }
    +def describe+() -> String = return "count=${value}"
}
```
## EX-R51c-004 — Missing class dispatch marker is rejected

- **source_feature_ids:** `dispatch_marker_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `CLASS_INSTANCE_METHOD_REQUIRES_DISPATCH_MARKER`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
class Bad {
    +def run() -> Unit = { }
}
```
## EX-R51c-005 — Stored fields cannot be virtual

- **source_feature_ids:** `dispatch_marker_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `FIELD_DISPATCH_MARKER_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
class BadField {
    +let name. : String
}
```
## EX-R51c-006 — Trait method marker and unmarked associated requirements

- **source_feature_ids:** `dispatch_marker_law`, `trait_associated_requirement_marker_absence`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
trait Iterator {
    type Item
    let:: empty: Bool
    def:: defaultBatch() -> Int
    def next.() -> Option<Item>
}
```
## EX-R51c-007 — Associated non-method marker is rejected

- **source_feature_ids:** `trait_associated_requirement_marker_absence`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `TRAIT_ASSOCIATED_ITEM_DISPATCH_MARKER_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
trait BadIterator {
    type Item+
}
```
## EX-R51c-008 — Full read-only interpolation path

- **source_feature_ids:** `interpolation_path_shorthand`
- **checker_trace_ids:** `InterpolationPathAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = "user=$user.profile.names[1] tuple=$pair.1"
```
## EX-R51c-009 — Interpolation calls require braces

- **source_feature_ids:** `interpolation_path_shorthand`
- **checker_trace_ids:** `InterpolationPathAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INTERPOLATION_COMPLEX_EXPRESSION_REQUIRES_BRACES`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = "value=$provider.load()"
```
## EX-R51c-010 — Caret transpose and power have distinct attachment

- **source_feature_ids:** `caret_attachment_policy`, `caret_power_operator_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let matrix = #2,2[1, 2; 3, 4]
let base: Int = 2
let transposed = matrix^
let powered = base ^ 3
```
## EX-R51c-011 — Mixed caret attachment is rejected

- **source_feature_ids:** `caret_attachment_policy`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CARET_ATTACHMENT_AMBIGUOUS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ambiguous = base^ exponent
```
## EX-R51c-012 — Declarative clauses explicitly cover Option

- **source_feature_ids:** `declarative_clause_finite_partition_algorithm`
- **checker_trace_ids:** `DeclarativeClausePartitionAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def label(value: Option<Int>) -> String = {{
    ::some(x) => "value=${x}"
    ::none => "missing"
}}
```
## EX-R51c-013 — Option does not supply an implicit missing arm

- **source_feature_ids:** `declarative_clause_finite_partition_algorithm`
- **checker_trace_ids:** `DeclarativeClausePartitionAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `DECL_CLAUSE_NONEXHAUSTIVE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def label(value: Option<Int>) -> String = {{
    ::some(x) => "value=${x}"
}}
```
## EX-R51c-014 — Law body contains pure assertions only

- **source_feature_ids:** `law_body_restricted_logic_subset`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
law Reflexive {
    invariant value == value
}
```
## EX-R51c-015 — Effectful law statement is rejected

- **source_feature_ids:** `law_body_restricted_logic_subset`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `LAW_BODY_ITEM_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
law BadLaw {
    print("not a proposition")
}
```
## EX-R51c-016 — Message spawn is owned by ordinary message syntax

- **source_feature_ids:** `async_task_control`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let task = worker ~ spawn { => worker ~ run(job) }
```
## EX-R51c-017 — Shallow and deep same-type derivation

- **source_feature_ids:** `shallow_same_type_derivation`, `deep_same_type_derivation`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let shallow = user!{ name: "Ada" }
let deep = graph!!{ root: replacement }
```
## EX-R51c-018 — Calendar conversion needs explicit stdlib provider context

- **source_feature_ids:** `calendar_unit_profile_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let due = calendar ~ addUsing(policy, 3[business_day], from: referenceDate)
```
## EX-R51c-019 — Dynamic RCTS source activation remains unavailable

- **source_feature_ids:** `dyn_rcts_family`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DYN_RCTS_SOURCE_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value: dyn Int = input
```
## EX-R51c-020 — Source root cannot ignore trailing tokens

- **source_feature_ids:** `source_root_full_consumption`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SOURCE_TRAILING_TOKENS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = 1
}
```

## EX-R51c1-001 — Named-rest parameter uses attached triple-star

- **source_feature_ids:** `named_rest_parameter_record_msp`, `r51e_package_current_canonical_authority`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`, `NamedRestParameterRecordAndLastPosition`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options***: Record) -> Unit = {
    apply(**options)
}
```
## EX-R51c1-002 — Function type preserves triple-star named-rest residue

- **source_feature_ids:** `named_rest_parameter_record_msp`, `call_shape_rest_type_residue_law`
- **checker_trace_ids:** `FunctionRestResiduePreserved`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public type Configure = (Record***) -> Unit
```
## EX-R51c1-003 — Named unfold alone uses prefix double-star

- **source_feature_ids:** `record_named_argument_spread_msp`, `named_rest_parameter_record_msp`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`, `RecordNamedArgumentSpreadAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let options = ${ timeout: 30, retries: 2 }
configure(**options)
```
## EX-R51c1-004 — Double-star named-rest parameter is removed

- **source_feature_ids:** `named_rest_parameter_record_msp`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def configure(options**: Record) -> Unit = { }
```
## EX-R51c1-005 — Double-star function-type residue is removed

- **source_feature_ids:** `named_rest_parameter_record_msp`, `call_shape_rest_type_residue_law`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`, `FunctionRestResiduePreserved`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public type Configure = (Record**) -> Unit
```
## EX-R51c1-006 — Triple-star cannot be used as named unfold

- **source_feature_ids:** `named_rest_parameter_record_msp`, `record_named_argument_spread_msp`
- **checker_trace_ids:** `NamedRestCollectorAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRIPLE_STAR_ONLY_FOR_NAMED_REST_PARAMETER_OR_TYPE_RESIDUE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
configure(***options)
```
## EX-R51d-001 — Raw String Phase A preserves body text

- **source_feature_ids:** `raw_string_prefixed_literal`, `r51e_package_current_canonical_authority`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let path = raw"C:\temp\$name"
```
## EX-R51d-002 — Alternate raw delimiter family is not current

- **source_feature_ids:** `raw_string_prefixed_literal`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RAW_STRING_DELIMITER_INVALID`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let path = raw#"C:\temp"#
```
## EX-R51d-003 — Rightward immutable binding normalizes to let

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`, `r51e_package_current_canonical_authority`
- **checker_trace_ids:** `RightwardLocalBindingNormalizesToOrdinaryBinding`, `OrdinaryLocalBindingAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
loadConfig() -> $config: Config
```
## EX-R51d-004 — Rightward mutable binding normalizes to var

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `RightwardLocalBindingNormalizesToOrdinaryBinding`, `OrdinaryLocalBindingAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
openCounter() -> $$counter: Counter
```
## EX-R51d-005 — Rightward binding evaluates a move-only initializer once

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `RightwardLocalBindingNormalizesToOrdinaryBinding`, `OrdinaryLocalBindingAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
move socket -> $owned: Socket
```
## EX-R51d-006 — Rightward target must be a fresh identifier

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `OrdinaryLocalBindingAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FLOW_BINDING_TARGET_MUST_BE_NEW_LOCAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let value = 0
compute() -> $value
```
## EX-R51d-007 — Hash role admits same-line trivia

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def# /* role */ pure identity(value: Int) -> Int = return value
```
## EX-R51d-008 — Hash role cannot cross a physical newline

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `HASH_ROLE_PHYSICAL_LINE_BREAK_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#
pure identity(value: Int) -> Int = return value
```
## EX-R51d-009 — Rightward chaining is rejected

- **source_feature_ids:** `rightward_flow_dollar_local_binding_msp`
- **checker_trace_ids:** `RightwardLocalBindingNormalizesToOrdinaryBinding`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FLOW_BINDING_CANNOT_CHAIN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
produce() -> $first -> $second
```
## EX-R51d-010 — Named function value uses explicit return shorthand

- **source_feature_ids:** `named_function_body_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def answer() -> Int = return 42
```
## EX-R51d-011 — Named function bare expression body is rejected

- **source_feature_ids:** `named_function_body_contract`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `FUNCTION_BODY_REQUIRES_BLOCK_RETURN_OR_CLAUSE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def answer() -> Int = 42
```
## EX-R51d-012 — Dynamic unit profile must be active

- **source_feature_ids:** `dynamic_unit_conversion_provider_msp`
- **checker_trace_ids:** `DynamicUnitConversionProfileAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DYNAMIC_UNIT_CONVERSION_PROFILE_NOT_ACTIVE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let converted = price ~ asUnitUsing(provider, 1[USD])
```
## EX-R51d-013 — Dynamic unit profile needs an explicit provider

- **source_feature_ids:** `dynamic_unit_conversion_provider_msp`
- **checker_trace_ids:** `DynamicUnitConversionProfileAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `DYNAMIC_UNIT_CONVERSION_PROVIDER_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let converted = price ~ asUnit(1[USD])
```
## EX-R51e-001 — Materialization field pun

- **source_feature_ids:** `materialization_derivation_field_punning`
- **checker_trace_ids:** `MaterializationFieldPunAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let id = 7
let name = "Ada"
let user = User${ id, name }
```
## EX-R51e-002 — Unbound materialization field pun rejected

- **source_feature_ids:** `materialization_derivation_field_punning`
- **checker_trace_ids:** `MaterializationFieldPunAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MATERIALIZATION_FIELD_PUN_UNBOUND`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let user = User${ id, missing }
```
## EX-R51e-003 — Grouped forwarding

- **source_feature_ids:** `grouped_member_forwarding_sugar`
- **checker_trace_ids:** `GroupedMemberForwardingAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class PersonView {
    +forward { name, age, city } to profile
}
```
## EX-R51e-004 — Grouped forwarding collision rejected

- **source_feature_ids:** `grouped_member_forwarding_sugar`
- **checker_trace_ids:** `GroupedMemberForwardingAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FORWARD_GROUP_COLLISION`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class PersonView {
    +let name: String
    +forward { name, age } to profile
}
```
## EX-R51e-005 — Scoped grouped use

- **source_feature_ids:** `scoped_import_use_grouping`
- **checker_trace_ids:** `ScopedActivationGroupAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use math::vector, text::render in {
    let label = render(norm(v))
}
```
## EX-R51e-006 — Scoped activation requires in

- **source_feature_ids:** `scoped_import_use_grouping`
- **checker_trace_ids:** `ScopedActivationGroupAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SCOPED_ACTIVATION_REQUIRES_IN_BLOCK`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
use math::vector, text::render {
    let label = render(norm(v))
}
```
## EX-R51e-007 — Dedented multiline Unicode String

- **source_feature_ids:** `dedented_multiline_unicode_string`
- **checker_trace_ids:** `DedentedMultilineStringAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let message = """
    Hello, $user.name
    결과: ${compute()}
    """
```
## EX-R51e-008 — Multiline closer placement rejected

- **source_feature_ids:** `dedented_multiline_unicode_string`
- **checker_trace_ids:** `DedentedMultilineStringAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MULTILINE_STRING_CLOSER_MUST_BE_OWN_LINE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let bad = """
    text"""
```
## EX-R51e-009 — One-line enum case comma list

- **source_feature_ids:** `enum_case_comma_list`
- **checker_trace_ids:** `EnumCaseCommaListAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum State { draft, active, blocked(reason: String) }
```
## EX-R51e-010 — Multiline enum comma list rejected

- **source_feature_ids:** `enum_case_comma_list`
- **checker_trace_ids:** `EnumCaseCommaListAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ENUM_CASE_COMMA_REQUIRES_SINGLE_LINE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public enum State {
    draft,
    active,
}
```
## EX-R51e-011 — Single transfer guard

- **source_feature_ids:** `single_guard_clause_unification`
- **checker_trace_ids:** `SingleGuardClauseAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def emit(value: Int) -> Unit = {
    return if value < 0
    log(value)
}
```
## EX-R51e-012 — Guard chain rejected

- **source_feature_ids:** `single_guard_clause_unification`
- **checker_trace_ids:** `SingleGuardClauseAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MULTIPLE_GUARD_CLAUSES_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for item in items if item.ready !if item.cancelled {
    consume(item)
}
```
## EX-R51e-013 — If-let transactional binding

- **source_feature_ids:** `pattern_binding_control_family`
- **checker_trace_ids:** `PatternBindingControlAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if let Option::some(value) = candidate {
    consume(value)
}
```
## EX-R51e-014 — While-let transactional binding

- **source_feature_ids:** `pattern_binding_control_family`
- **checker_trace_ids:** `PatternBindingControlAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
while let Option::some(job) = queue.next() {
    process(job)
}
```
## EX-R51e-015 — For-let filters candidates

- **source_feature_ids:** `pattern_binding_control_family`
- **checker_trace_ids:** `PatternBindingControlAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for let Result::ok(value) in results if value > 0 {
    consume(value)
}
```
## EX-R51e-016 — Irrefutable pattern control rejected

- **source_feature_ids:** `pattern_binding_control_family`
- **checker_trace_ids:** `PatternBindingControlAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `PATTERN_CONTROL_REQUIRES_REFUTABLE_PATTERN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if let value = candidate { consume(value) }
```
## EX-R51e-017 — Quarantine scope is nonactivatable

- **source_feature_ids:** `dynamic_unsafe_quarantine_scope_msp`
- **checker_trace_ids:** `QuarantineScopeDesignAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `QUARANTINE_SCOPE_NOT_ACTIVATABLE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
@scope#dynamic {
    let value: Int = inspect(payload)
} -> $value: Int
```
## EX-R51e-018 — Quarantine escape design boundary

- **source_feature_ids:** `dynamic_unsafe_quarantine_scope_msp`
- **checker_trace_ids:** `QuarantineScopeDesignAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `QUARANTINE_RESOURCE_ESCAPE_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
@scope#unsafe {
    let ptr = rawPointer(buffer)
} -> $ptr: Pointer<Byte>
```

## EX-R51f-001 — Map String key uses explicit indexing

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `map_prefixed_literal`, `basic_index_operator`
- **checker_trace_ids:** `BasicIndexOperatorAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let options = #map{ "timeout": 30 }
let timeout = options["timeout"]
```

## EX-R51f-002 — Map dot-key projection is not member lookup

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `map_prefixed_literal`, `static_runtime_member_boundary_law`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `MEMBER_NOT_FOUND`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let options = #map{ "timeout": 30 }
let timeout = options.timeout
```

## EX-R51f-003 — Explicit assignment replaces increment

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `numeric_operator_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
var value = 0
value = value + 1
```

## EX-R51f-004 — Postfix increment is not current

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `numeric_operator_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `POSTFIX_MUTATION_OPERATOR_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
var value = 0
value++
```

## EX-R51f-005 — Ordinary recursive function

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `function_profile_introducer_family`
- **checker_trace_ids:** `FunctionProfileIntroducerAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def sumTo(n: Int) -> Int = {
    if n <= 0 { return 0 }
    return n + sumTo(n - 1)
}
```

## EX-R51f-006 — Tail-recursion callable kind is not current

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `function_profile_introducer_family`
- **checker_trace_ids:** `FunctionProfileIntroducerAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CALLABLE_PROFILE_COMBINATION_NOT_ADMITTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#tailrec sumTo(n: Int) -> Int = {
    return n
}
```

## EX-R51f-007 — Raw String can carry pattern text

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `raw_string_prefixed_literal`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let patternText = raw"[A-Z]+"
```

## EX-R51f-008 — Regex literal prefix is not current

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `set_prefixed_literal`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `UNKNOWN_PREFIXED_LITERAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let pattern = #regex"[A-Z]+"
```

## EX-R51f-009 — Explicit expected List union

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `ordinary_list_literal_surface`, `closed_anonymous_union_type_msp`
- **checker_trace_ids:** `ListLiteralElementJoinAdmitted`, `ClosedAnonymousUnionAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values: List<Int | String> = [1, "two"]
```

## EX-R51f-010 — Automatic heterogeneous List union is absent

- **source_feature_ids:** `r51f_removed_surface_boundary_law`, `ordinary_list_literal_surface`, `closed_anonymous_union_type_msp`
- **checker_trace_ids:** `ListLiteralElementJoinAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `LIST_LITERAL_ELEMENT_JOIN_FAILED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values = [1, "two"]
```

## EX-R51f3-R2-001 — Strict Boolean operands must be Bool

- **source_feature_ids:** `strict_boolean_word_operators_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `STRICT_BOOLEAN_OPERAND_NOT_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = true and 1
// STRICT_BOOLEAN_OPERAND_NOT_BOOL
```

## EX-R51f3-R2-002 — Sequential Boolean operands must be Bool

- **source_feature_ids:** `sequential_boolean_control_words_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SEQUENTIAL_BOOLEAN_OPERAND_NOT_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = true and then 1
// SEQUENTIAL_BOOLEAN_OPERAND_NOT_BOOL
```

## EX-R51f3-R2-003 — Ternary question mark requires spacing

- **source_feature_ids:** `ternary_conditional_expression`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TERNARY_QUESTION_REQUIRES_SPACING`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = ready? "yes" : "no"
// TERNARY_QUESTION_REQUIRES_SPACING
```

## EX-R51f3-R2-004 — Short single-line ternary is current

- **source_feature_ids:** `ternary_short_expression_stable_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let label = ready ? "yes" : "no"
```

## EX-R51f3-R2-005 — Bytes literal hex escape requires two hex digits

- **source_feature_ids:** `bytes_literal_hash_bytes_msp`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `BYTES_LITERAL_INVALID_HEX_ESCAPE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = #bytes"\xG1"
// BYTES_LITERAL_INVALID_HEX_ESCAPE
```

## EX-R51f3-R2-006 — Interpolation format requires braced form

- **source_feature_ids:** `string_interpolation_format_spec_core`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INTERPOLATION_FORMAT_REQUIRES_BRACED_FORM`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text = "name=$name:<12"
// INTERPOLATION_FORMAT_REQUIRES_BRACED_FORM
```

## EX-R51f3-COH-001 — List pattern commits only after an admitted final ignored remainder probe

- **source_feature_ids:** `pattern_binding_control_family`, `pattern_decomposition`, `pattern_match_ownership_split`
- **checker_trace_ids:** `PatternBindingControlAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if let [head, .._] = values {
    consume(head)
}
```

## EX-R51f3-COH-002 — For-let probe binder guard requires Bool before commit

- **source_feature_ids:** `pattern_binding_control_family`, `strict_boolean_word_operators_msp`
- **checker_trace_ids:** `PatternBindingControlAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `FOR_LET_FILTER_GUARD_NOT_BOOL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
for let Result::ok(value) in results if 1 {
    consume(value)
}
```

## EX-R51f3-COH-003 — Tuple decomposition pattern is not current

- **source_feature_ids:** `pattern_binding_control_family`, `pattern_decomposition`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TUPLE_PATTERN_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
if let (left, right) = pair {
    consume(left, right)
}
```

## EX-R51f3-COH-004 — Statement try may use finally as its required terminal owner

- **source_feature_ids:** `statement_control_core_phase_a`, `resource_cleanup`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
try {
    perform()
} finally {
    close()
}
```

## EX-R51f3-COH-005 — Bare statement try has no current failure owner

- **source_feature_ids:** `statement_control_core_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `TRY_REQUIRES_CATCH_OR_FINALLY`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
try {
    perform()
}
```

## EX-R51f3-COH-006 — Strict Boolean control accepts only Bool operands

- **source_feature_ids:** `strict_boolean_word_operators_msp`, `statement_control_core_phase_a`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ready: Bool = true
let stopped: Bool = false
if ready and not stopped {
    run()
}
```

## EX-R51f3-COH-007 — Array and case remain ordinary identifiers

- **source_feature_ids:** `r51e_frontend_grammar_current_canonical`, `ordinary_list_literal_surface`, `enum_case_pattern_double_colon_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let array = [1, 2]
let case = array[1]
enum Token { case }
let token: Token = Token::case
```

## EX-R51f3-COH-008 — Bounded actor channel keeps send order and explicit request reply

- **source_feature_ids:** `actor_declaration_grammar_closed`, `actor_mailbox_capacity`, `actor_protocol_family`, `actor_request_reply`, `async_task_control`, `structured_task_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public protocol CounterProtocol {
    send add(value: Int)
    request current() -> Int
}
actor #mailbox(capacity: 8) Counter {
    on add(value: Int) = { }
    request current() -> Int = { return 0 }
}
public def#async observe(counter: Counter) -> Int
    throws ActorMessageError
= {
    task scope {
        let Result::ok(_) = counter ~ add(value: 1)
        else Result::err(error) => throw error
        let Result::ok(_) = counter ~ add(value: 2)
        else Result::err(error) => throw error
        let Result::ok(replyTask) = counter ~ current()
        else Result::err(error) => throw error
        return await replyTask
    }
}
```

## EX-R51f3-COH-009 — Actor mailbox capacity must be a positive static bound

- **source_feature_ids:** `actor_declaration_grammar_closed`, `actor_mailbox_capacity`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ACTOR_MAILBOX_CAPACITY_REQUIRES_STATIC_INT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
actor #mailbox(capacity: 0) Counter { }
```

## EX-R51f3-COH-010 — Cancellation is not recoverable through catch

- **source_feature_ids:** `async_task_control`, `error_defect_cancellation_split`, `structured_task_scope`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `CATCHES_CANCELLATION_AS_ERROR_FORBIDDEN`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#async waitFor(task: Task<Int>) -> Int = {
    try {
        return await task
    } catch cancel: Cancellation {
        return 0
    }
}
```

## EX-R51f3-COH-011 — Structured task cleanup remains owned at cancellation boundary

- **source_feature_ids:** `async_task_control`, `structured_task_scope`, `single_action_defer_msp`, `deterministic_primary_suppressed_order`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public def#async supervise() -> Unit = {
    task scope {
        defer cleanup()
        let child = spawn async { => await work() }
        await child
    }
}
```

## EX-R51f3-COH-012 — Omitted mailbox clause selects logical-unbounded admission

- **source_feature_ids:** `actor_declaration_grammar_closed`, `actor_mailbox_capacity`, `actor_protocol_family`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
actor Worker {
    on run(job: Job) = { }
}
public def dispatch(worker: Worker, move job: Job)
    -> Result<Unit, error ActorMessageError>
= {
    return worker ~ run(move job)
}
```

## EX-R51COH-SHARED-001 — SharedCell scoped observation and owner replacement

- **source_feature_ids:** `shared_cell_plain_payload_profile`, `scoped_callable_lifetime_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let cell = SharedCell::new(move state)
let label = cell.withValue { borrow value => describe(value) }
let previous = cell.replace(move nextState)
```

## EX-R51COH-SHARED-002 — SharedMutex receiver-bound non-suspending scoped mutation

- **source_feature_ids:** `shared_mutex_no_drop_minimum_profile`, `scoped_callable_lifetime_profile`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `stdlib`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let mutex = SharedMutex::new(move state)
mutex.withLock { inout value => value = update(value) }
```

## EX-R51VOI-001 — Unsuffixed and suffixed numeric values keep exact domains

- **source_feature_ids:** `numeric_literal_lexical_contract`, `numeric_literal_suffix`, `numeric_operator_core`
- **checker_trace_ids:** `NumericLiteralAdmitted`, `NumericOperatorCoreAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let count: Int = 42
let exact: Int32 = 42i32
let ratio: Float64 = 1.5
let compact: Float32 = 1.5f32
let sum: Int = count + 1
```

## EX-R51VOI-002 — Compound assignment evaluates one mutable place and commits once

- **source_feature_ids:** `numeric_operator_core`
- **checker_trace_ids:** `NumericOperatorCoreAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
def nextDelta() -> Int = return 1
var total: Int = 10
total += nextDelta()
```

## EX-R51VOI-003 — Option none is the only current absence value

- **source_feature_ids:** `option_none_case_only`, `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let missing: Option<Int> = ::none
let present: Option<Int> = ::some(42)
```

## EX-R51VOI-004 — Ordinary and bounded logical domains remain explicit

- **source_feature_ids:** `one_based_sequence_logical_indexing`, `bounded_contiguous_index_domain_msp`, `basic_index_operator`
- **checker_trace_ids:** `LogicalIndexDomainAdmitted`, `BoundedLogicalIndexDomainAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ordinary = [10, 20, 30]
let first = ordinary[1]
let bounded = [3..5: 10, 20, 30]
let declaredFirst = bounded[3]
```

## EX-R51VOI-005 — String and Bytes indexing use one-based scalar coordinates

- **source_feature_ids:** `one_based_sequence_logical_indexing`, `char_unicode_scalar_value_model`, `no_string_char_bytes_implicit_conversion_law`, `bytes_literal_hash_bytes_msp`
- **checker_trace_ids:** `LogicalIndexDomainAdmitted`, `StringCharBytesBoundaryAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let text: String = "가A"
let scalar: Char = text[1]
let bytes: Bytes = #bytes"\x41\x42"
let firstByte: UInt8 = bytes[1]
```

## EX-R51VOI-006 — Map indexing remains in the exact key domain

- **source_feature_ids:** `index_operator`, `map_prefixed_literal`
- **checker_trace_ids:** `LogicalIndexDomainAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let ports = #map{ "https": 443 }
let secure = ports["https"]
```

## EX-R51VOI-007 — NumericArray built-in axes are typed and one-based

- **source_feature_ids:** `numeric_array_multiaxis_slice_readonly_view_msp`, `one_based_sequence_logical_indexing`, `index_operator`
- **checker_trace_ids:** `LogicalIndexDomainAdmitted`, `NumericFillSliceIndexAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let matrix = #2,2[1, 2; 3, 4]
let topLeft = matrix[1; 1]
let firstRow = matrix[1; *]
```

## EX-R51VOI-008 — Inclusive slices and anchors preserve source coordinates

- **source_feature_ids:** `inclusive_slice_range_canonical_msp`, `slicing_anchor_range_notation_msp`, `slice_logical_domain_preservation`
- **checker_trace_ids:** `SliceRangeAdmitted`, `SliceLogicalDomainPreserved`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values = [10, 20, 30, 40]
let middle = values[2..$]
let sameCoordinate = middle[3]
```

## EX-R51VOI-009 — Explicit exclusive slice end is accepted with a warning

- **source_feature_ids:** `inclusive_slice_range_canonical_msp`, `slice_half_open_noncanonical_warning_law`
- **checker_trace_ids:** `SliceRangeAdmitted`
- **expected_outcome:** `accept`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **expected_warnings:** `SLICE_HALF_OPEN_RANGE_NONCANONICAL`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let values = [10, 20, 30, 40]
let prefix = values[1..<4]
```

## EX-R51VOI-NG-001 — null is reserved recovery, not a value

- **source_feature_ids:** `option_none_case_only`, `option_result_double_colon_case_surface`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let missing: Option<Int> = null
// NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE
```

## EX-R51VOI-NG-002 — custom operator declarations are not current

- **source_feature_ids:** `custom_operator`, `closed_operator_symbols_open_named_extensions`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `nonactivatable`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
operator <+> precedence 130
// CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT
```

## EX-R51VOI-NG-003 — Trait conformance cannot activate a fixed glyph

- **source_feature_ids:** `fixed_operator_conformance_overloading`, `closed_operator_symbols_open_named_extensions`
- **checker_trace_ids:** `NumericOperatorCoreAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `nonactivatable`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `library`
- **source_root:** `LibrarySourceFile`
- **primary_diagnostic:** `FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
public class Amount {
    +let value: Int

    +def! new(value: Int)
        : super!()
    = {
        self.value = value
    }
}

public trait Additive {
    +def add+(rhs: Self) -> Self
        throws Never
        effects {}
}

public conformance Amount conforms Additive {
    +def add+(rhs: Self) -> Self
        throws Never
        effects {}
    = {
        return Amount!(self.value + rhs.value)
    }
}

let total = Amount!(1) + Amount!(2)
// FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT
```

## EX-R51VOI-NG-004 — descending range glyph is not current

- **source_feature_ids:** `operator_precedence_table_phase_a`, `range_step_expression_surface_clarification`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RANGE_OPERATOR_SPELLING_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let descending = 5..>1
// RANGE_OPERATOR_SPELLING_NOT_CURRENT
```

## EX-R51VOI-NG-005 — ellipsis is not an expression range operator

- **source_feature_ids:** `operator_precedence_table_phase_a`, `range_step_expression_surface_clarification`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `RANGE_OPERATOR_SPELLING_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = 1...5
// RANGE_OPERATOR_SPELLING_NOT_CURRENT
```

## EX-R51VOI-NG-006 — an empty index suffix never implies a full slice

- **source_feature_ids:** `basic_index_operator`, `index_operator`
- **checker_trace_ids:** `none`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `INDEX_SUFFIX_REQUIRES_AXIS`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = values[]
// INDEX_SUFFIX_REQUIRES_AXIS
```

## EX-R51VOI-NG-007 — NumericArray zero is outside every built-in positional axis

- **source_feature_ids:** `numeric_array_multiaxis_slice_readonly_view_msp`, `one_based_sequence_logical_indexing`, `index_operator`
- **checker_trace_ids:** `LogicalIndexDomainAdmitted`, `NumericFillSliceIndexAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `ZERO_BASED_INDEX_NOT_CURRENT`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let matrix = #2,2[1, 2; 3, 4]
let invalid = matrix[0; 1]
// ZERO_BASED_INDEX_NOT_CURRENT
```

## EX-R51VOI-NG-008 — mixed numeric widths require an explicit conversion

- **source_feature_ids:** `numeric_operator_core`, `numeric_literal_suffix`
- **checker_trace_ids:** `NumericOperatorCoreAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `NUMERIC_OPERATOR_CORE_REQUIRED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
let invalid = 1i32 + 2i64
// NUMERIC_OPERATOR_CORE_REQUIRED
```

## EX-R51VOI-NG-009 — mutable slice assignment is not current

- **source_feature_ids:** `inclusive_slice_range_canonical_msp`, `slice_logical_domain_preservation`
- **checker_trace_ids:** `SliceRangeAdmitted`, `SliceLogicalDomainPreserved`, `SliceViewLifetimeAdmitted`
- **expected_outcome:** `reject`
- **source_activation:** `none`
- **certification_status:** `design_static_product_not_run`
- **source_role:** `script`
- **source_root:** `ScriptSourceFile`
- **primary_diagnostic:** `SLICE_MUTABLE_ASSIGNMENT_UNSUPPORTED`
- **parser_status / checker_status:** `not_run` / `not_run`

```deeplus
var values = [10, 20, 30, 40, 50]
let replacements = [90, 91, 92]
values[2..4] = replacements
// SLICE_MUTABLE_ASSIGNMENT_UNSUPPORTED
```
