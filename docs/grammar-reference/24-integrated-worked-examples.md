# 통합 실전 예제와 전체 판정 추적

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->
<!-- deeplus-status-fence: CURRENT -->

## 1. 이 장을 읽는 방법

이 장은 기능 하나의 문법만 보여 주는 조각 예제집이 아니다.
하나의 프로그램이 source root에서 시작하여 parser, resolver, checker,
typed HIR, MIR 및 실행 관측 규칙을 통과하는 전체 판정 경로를 따라간다.

각 사례는 다음 순서로 고정되어 있다.

1. 요구사항과 전제
2. 전체 코드
3. 컴파일러 판정 순서
4. 평가 추적
5. 실패 변형과 진단
6. 다른 기능과의 상호작용

예제 코드는 현행 문법을 설명하기 위한 `CURRENT_EXPLANATORY` 자료다.
각 코드 블록은 바로 앞의 marker가 가리키는 정본 source에 근거한다.
실제 Rust frontend, checker, MIR, xVM, LLVM, formatter 및 LSP 실행은
이 장에서 수행하지 않았으므로 제품 지원은 `NOT_RUN`이다.

정확한 권위는 다음 문서에 분산되어 있다.

- token 순서와 구조:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- source role, admission, parser goal:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 언어 전체 설명:
  [`spec/language.md`](../../spec/language.md)
- type, ownership, effect 책임:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- 관측 가능한 평가와 lowering:
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- Prelude identity:
  [`library/prelude/prelude.md`](../../library/prelude/prelude.md)
- Rational, Complex와 scalar power:
  [`spec/contracts/rational-complex-numeric-coherence.json`](../../spec/contracts/rational-complex-numeric-coherence.json)
- 닫힌 HIR-H1/MIR bridge 설계:
  [`spec/contracts/hir-h1-current-mir-bridge.json`](../../spec/contracts/hir-h1-current-mir-bridge.json)

## 2. 사례 1 — executable module과 entry 함수

### 2.1 요구사항과 전제

명령행 인자를 받아 출력하고 정상 종료하는 executable target을 만든다.
이 사례가 만족해야 하는 조건은 다음과 같다.

- build manifest가 `executable` source role을 선택한다.
- source에는 정확히 하나의 admitted entry 함수가 있다.
- entry parameter와 return type이 launcher ABI에 맞는다.
- 출력 효과가 callable의 effect row에 드러난다.
- recoverable error가 없음을 `throws Never`로 보존한다.

`module` 선언은 파일의 논리 경로를 정한다.
`def#entry`는 단순한 이름 있는 함수 profile이 아니라 executable root가
소유하는 `EntryFunctionDecl` 후보다.

### 2.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
module demo::hello

def#entry launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    print("argument-count=${args.length}")
    print(args)
    return ExitCode::success
}
```

### 2.3 컴파일러 판정 순서

1. **source role 선택**
   manifest가 `ExecutableSourceFile` parser를 선택한다.
   parser는 token 내용만으로 library/script/executable을 추측하지 않는다.

2. **module 구조**
   `ModuleDecl`이 `demo::hello`를 `QualifiedPath`로 읽고
   `StatementBoundary`에서 끝난다.

3. **entry owner 선택**
   `def#entry`의 `DefIntroducer`와 이름 `launch`를 읽은 뒤
   `EntryFunctionRest`로 들어간다.

4. **signature 구조**
   `ParameterList`, `ReturnClause`, `ThrowsClause`, `EffectsClause`,
   `FunctionBody` 순으로 CST를 만든다.

5. **이름과 type 해석**
   `Sequence`, `String`, `ExitCode`, `print`를 Prelude/module scope에서
   해석한다.

6. **entry admission**
   target 안 entry 수가 정확히 하나인지,
   signature가 허용 ABI shape인지 검사한다.

7. **effect/error 검사**
   `print`의 `io` 요구가 선언된 `{io}`에 포함되고,
   body가 recoverable Error를 흘리지 않는지 검사한다.

8. **HIR/MIR lowering**
   entry identity, argument acquisition, 두 출력 호출과 명시적 return을
   source order로 보존한다.

9. **launcher handoff**
   ordinary `ExitCode` 값이 entry boundary에서만 process termination
   결과로 해석된다.
   일반 함수가 `ExitCode`를 반환한다고 process가 종료되지는 않는다.

### 2.4 평가 추적

| 순서 | 관측 동작 | 보존해야 할 값/책임 |
|---:|---|---|
| 1 | launcher가 `Sequence<String>`을 만든다 | 인자 순서와 String owner |
| 2 | `args.length`를 한 번 읽는다 | argument sequence borrow |
| 3 | 첫 interpolation을 구성한다 | 표시용 String |
| 4 | 첫 `print`를 실행한다 | `io` effect |
| 5 | `args`를 두 번째 `print`에 전달한다 | source order |
| 6 | `ExitCode::success`를 만든다 | entry result identity |
| 7 | `return`으로 entry를 끝낸다 | cleanup 뒤 launcher handoff |

optimizer는 두 `print`를 합치거나 순서를 바꿀 수 없다.
첫 호출이 실패·중단될 수 있는 target profile이라면 둘째 호출은 그 뒤에만
도달한다.

### 2.5 실패 변형과 진단

entry가 없으면 target-level `NO_EXECUTABLE_ENTRY`가 발생한다.
둘 이상이면 `ENTRY_DECL_DUPLICATE` 또는 source-role entry-count 진단이
발생한다.
library source role에 같은 선언을 넣으면
`ENTRY_NOT_ALLOWED_IN_LIBRARY_SOURCE`다.

다음은 script root와 entry declaration을 섞은 잘못된 source-role
사례다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
#! /usr/bin/env deeplus

def#entry launch(args: Sequence<String>) -> ExitCode = {
    return ExitCode::success
}
// SCRIPT_ROOT_AND_ENTRY_DECL_CONFLICT
```

### 2.6 상호작용

- source role은 함수 profile보다 먼저 결정된다.
- entry ABI와 ordinary callable compatibility는 같은 규칙이 아니다.
- `effects {io}`는 출력 권한 자체가 아니라 관측 effect row다.
- `throws Never`와 Defect/Cancellation은 같은 축이 아니다.
- entry body의 resource와 `defer`는 launcher handoff 전에 정리되어야 한다.

## 3. 사례 2 — generic, context, witness, 호출 호환성

### 3.1 요구사항과 전제

임의의 `T` 값을 환경에 맞게 표시한다.
형식 지정 환경은 explicit context channel로,
`Display<T>` 구현 증거는 explicit witness channel로 전달한다.

요구사항은 다음과 같다.

- type parameter `T`는 value parameter에서 추론한다.
- context는 ordinary positional argument로 대체하지 않는다.
- witness는 first-class 저장 값이 아니라 borrowed evidence다.
- callable identity에 context/witness channel이 남는다.
- 모든 인자는 source order로 한 번만 평가한다.

예제의 `RenderEnvironment`, `Display<T>`, `renderValue`,
`userDisplay`는 imported module이 제공한다고 가정한다.

### 3.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
module demo::render

private def renderOne<T>(
    value: T,
    context environment: RenderEnvironment,
    using display: witness Display<T>,
) -> String
    throws RenderError
    effects {render}
= {
    return renderValue(
        value,
        context environment,
        using display,
    )
}

private def renderUser(
    user: User,
    context environment: RenderEnvironment,
    using userDisplay: witness Display<User>,
) -> String
    throws RenderError
    effects {render}
= {
    return renderOne(
        user,
        context environment,
        using userDisplay,
    )
}
```

### 3.3 컴파일러 판정 순서

1. **generic header parse**
   `TypeParameterList`가 `T`를 type parameter로 bind한다.

2. **parameter channel parse**
   첫 parameter는 `ValueParameter`,
   둘째는 `ContextParameter`,
   셋째는 `WitnessParameter`다.

3. **function type identity**
   parameter order, label, role, ownership mode, effect/error row와
   return type이 callable compatibility에 남는다.

4. **call argument 분류**
   `user`는 ordinary expression,
   `context environment`는 `ContextArgument`,
   `using userDisplay`는 `WitnessArgument`다.

5. **type inference**
   `renderOne`의 첫 formal과 `User` actual을 맞추어 `T = User`를 얻는다.
   inference 결과가 고정된 뒤 context와 witness의 normalized type을
   검사한다.

6. **witness coherence**
   `userDisplay`가 정확히 `Display<User>`의 허용된 evidence이며,
   모호하거나 overlapping하지 않는지 확인한다.

7. **effect/error forwarding**
   callee의 `throws RenderError`, `effects {render}`가
   caller signature에 보존되는지 검사한다.

8. **escape 검사**
   `display`와 `userDisplay`를 반환·저장·escaping closure capture하지
   않는지 확인한다.

9. **lowering**
   witness는 runtime 일반 값 lookup이 아니라 고정 evidence identity로
   HIR/MIR에 전달된다.

### 3.4 평가 추적

호출 `renderOne(user, context environment, using userDisplay)`의
관측 순서는 다음과 같다.

| 순서 | 평가 | 비고 |
|---:|---|---|
| 1 | callee `renderOne` 해석 | overload candidate set 고정 |
| 2 | `user` 평가 | `T = User` 제약 생성 |
| 3 | `environment` 평가 | context value reusable/shareable 검사 |
| 4 | `userDisplay` evidence 선택 | ordinary value conversion 금지 |
| 5 | call compatibility 확정 | role residue까지 일치 |
| 6 | body 진입 | 선언된 effect/error 책임 활성 |
| 7 | `renderValue` 호출 | 같은 channel을 명시적으로 forwarding |
| 8 | String 반환 | witness borrow는 call region에서 끝남 |

context parameter는 자동 dynamic lookup이 아니다.
source가 `context` argument를 쓰고 정확한 binding을 공급한다.

### 3.5 실패 변형과 진단

ordinary argument가 context channel을 채우려 하면
`CONTEXT_ARGUMENT_REQUIRED` 또는 `CONTEXT_FUNCTION_TYPE_MISMATCH`다.
witness를 빼면 `EXPLICIT_WITNESS_PARAMETER_REQUIRED`다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
let text = renderOne(user, environment, userDisplay)
// context와 witness role이 사라져 call compatibility 실패
```

witness를 local value처럼 저장하는 것도 거부된다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def keepEvidence(
    using display: witness Display<User>,
) -> Unit = {
    let saved = display
}
// RAW_WITNESS_VALUE_NOT_CURRENT
```

### 3.6 상호작용

- generic inference는 witness search의 무제한 역추론 권한이 아니다.
- active extension은 `Display<User>` witness가 아니다.
- context value가 effect authority를 기술하더라도 effect row는 별도로
  선언한다.
- witness는 borrowed evidence이므로 task/actor/storage boundary를
  마음대로 넘지 않는다.
- overload source order는 tie-breaker가 아니다.

## 4. 사례 3 — closed Union, refinement, guard, pattern

### 4.1 요구사항과 전제

`Int | String` 입력에서 양의 정수만 `Positive` refinement로 바꾸고,
나머지는 `Option::none`으로 정규화한다.

이 사례는 다음 기능을 함께 사용한다.

- closed Union type alias
- refinement type alias와 predicate
- clause function의 implicit subject
- typed binding pattern
- positive guard
- checked cast `as?`
- expected-type enum case shorthand `::none`

### 4.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-refinement-narrowing-coherence.json -->
```deeplus
module demo::normalize

public type Positive = Int where this > 0
public type TextOrNumber = Int | String

public def positive(value: TextOrNumber) -> Option<Positive>
    throws Never
    effects {}
= {{
    number: Int if number > 0 => number as? Positive
    number: Int               => ::none
    text: String              => ::none
}}
```

### 4.3 컴파일러 판정 순서

1. **type alias 정규화**
   `Positive`의 RHS는 `Int`와 `RefinementClause`다.
   `TextOrNumber`는 disjointness를 판정할 closed Union 후보가 된다.

2. **predicate admission**
   `this > 0`은 refinement sample `this`를 읽고,
   순수하고 nonthrowing이며 허용된 R0 predicate인지 검사한다.

3. **function signature**
   parameter type과 `Option<Positive>` return을 정규화한다.

4. **clause body parse**
   `ClauseFunctionBody`와 `MatchArmSequence`를 만든다.
   match subject는 parent function parameter `value`가 공급한다.

5. **typed pattern 검사**
   `number: Int`와 `text: String`이 Union의 정확한 alternative인지
   확인한다.

6. **guard 검사**
   첫 arm guard가 Bool이고 effect/error가 없으며 binding `number`를
   볼 수 있는지 확인한다.

7. **arm result 통합**
   `number as? Positive`는 `Option<Positive>`다.
   각 `::none`은 expected return type에서 `Option<Positive>::none`으로
   해석된다.

8. **exhaustiveness**
   Int의 guard 성공/실패와 String arm을 합쳐 모든 alternative가
   terminal인지 검사한다.

9. **flow lowering**
   subject를 한 번 평가하고 injection identity를 읽은 뒤,
   binding과 refinement proof를 성공 edge에만 commit한다.

### 4.4 평가 추적

입력이 `Int(7)`일 때:

1. `value`를 한 번 읽는다.
2. closed Union injection이 `Int`인지 확인한다.
3. `number` binding을 arm-local transaction에 만든다.
4. guard `number > 0`을 평가한다.
5. guard 성공 edge에서 binding을 commit한다.
6. `as? Positive`가 refinement predicate를 확인한다.
7. `Option::some(Positive(7))` 결과를 반환한다.

입력이 `Int(-2)`일 때:

1. 첫 typed pattern은 성공한다.
2. guard가 false이므로 첫 arm 결과는 평가하지 않는다.
3. 두 번째 `number: Int` arm으로 간다.
4. `::none`을 반환한다.

입력이 `String("7")`일 때:

1. 두 Int arm은 injection identity에서 실패한다.
2. partial `number` binding은 만들어지지 않는다.
3. String arm이 `text`를 bind하고 `::none`을 반환한다.

### 4.5 실패 변형과 진단

refinement는 암시적으로 통과하지 않는다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/type-refinement-narrowing-coherence.json -->
```deeplus
public def assumePositive(value: Int) -> Positive
    throws Never
    effects {}
= {
    return value
}
// REFINEMENT_PROOF_REQUIRED
```

Union 전체나 Union에 없는 type을 typed alternative로 쓰면
`UNION_PATTERN_ALTERNATIVE_NOT_EXACT`다.
effectful guard는 `MATCH_GUARD_EFFECT_NOT_ALLOWED`다.

### 4.6 상호작용

- refinement predicate와 match guard는 모두 Bool처럼 보이지만
  서로 다른 owner와 허용 effect 규칙을 갖는다.
- `as?`는 실패를 `Option`으로 표현하고 `throws`를 추가하지 않는다.
- pattern binding은 성공 edge에서만 보이고 source owner 이동도 그때
  commit된다.
- `::none`은 expected `Option` pattern/value 문맥에서만 의미가 닫힌다.
- strict `and`와 sequential `and then`은 Union narrowing 전달이 다르다.

## 5. 사례 4 — Class, Trait, conformance, extension

### 5.1 요구사항과 전제

`UserId`를 명목 class로 만들고,
`Display` Trait의 명시적 conformance를 제공하며,
감사 로그용 편의 기능은 별도 extension set으로 활성화한다.

이 사례의 핵심은 다섯 identity domain을 섞지 않는 것이다.

- class member
- class dispatch marker
- Trait requirement
- conformance witness
- extension member

### 5.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
module demo::identity

public class UserId {
    +let raw: Int

    +def! new(raw: Int)
        : super!()
    = {
        self.raw = raw
    }

    +def value.() -> Int
        throws Never
        effects {}
    = {
        return raw
    }
}

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
        return "UserId(${self.raw})"
    }
}

public extension UserId as audit {
    +def auditLabel() -> String
        throws Never
        effects {}
    = {
        return "user-id:${self.raw}"
    }
}

use UserId::audit

private def describe(id: UserId) -> String
    throws Never
    effects {}
= {
    let ordinary = id ~ display()
    let qualified = id ~ UserId::audit::auditLabel()
    return "${ordinary} / ${qualified}"
}
```

### 5.3 컴파일러 판정 순서

1. **class declaration**
   explicit `public` visibility와 명목 identity `UserId`를 만든다.

2. **field와 constructor**
   `+let raw`는 public stored field다.
   `+def! new`는 constructor owner이고 header delegation `super!()`를
   본문보다 먼저 검사한다.

3. **member dispatch**
   `value.`의 `.`는 final instance dispatch marker다.
   앞의 `+` member visibility와 별도 field다.

4. **Trait requirement**
   `display+`의 `+`는 open witness marker다.
   class dispatch marker와 같은 glyph라도 AST enum이 다르다.

5. **conformance identity**
   `UserId conforms Display`의 evidence를 coherence domain에 등록한다.
   requirement signature가 Trait과 정확히 호환되는지 검사한다.

6. **extension identity**
   `UserId::audit::auditLabel`을 target type, set id, member id로
   완전히 식별한다.

7. **activation**
   `use UserId::audit`가 unqualified extension lookup을 lexical scope에
   활성화하지만 conformance evidence를 만들지는 않는다.

8. **call resolution**
   `id ~ display()`는 nominal member/Trait witness domain에서,
   qualified selector는 지정 extension domain에서 해석한다.

9. **lowering**
   direct member/witness/extension 선택 결과를 HIR identity로 고정한다.
   runtime 문자열 lookup이나 source-order fallback을 만들지 않는다.

### 5.4 평가 추적

`describe(id)`는 다음 순서로 동작한다.

1. parameter `id`를 얻는다.
2. 첫 message/member call receiver `id`를 한 번 평가한다.
3. coherent `Display` witness의 `display` implementation을 호출한다.
4. 반환 String을 `ordinary`에 bind한다.
5. 둘째 receiver `id`를 다시 source에 적힌 대로 평가한다.
6. 정확한 extension selector를 호출한다.
7. 반환 String을 `qualified`에 bind한다.
8. interpolation이 왼쪽부터 두 값을 읽는다.
9. 최종 String을 반환한다.

extension activation 순서는 overload priority가 아니다.
동일 rank candidate가 둘이면 모호성 진단을 내며 마지막 `use`를
승자로 삼지 않는다.

### 5.5 실패 변형과 진단

class가 비슷한 이름의 메서드를 가진다는 이유로 Trait conformance가
자동으로 생기지 않는다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public class Logger {
    +def display.() -> String = {
        return "logger"
    }
}

private def needsDisplay<T>(value: T) -> String
    where T conforms Display
= {
    return value ~ display()
}

let text = needsDisplay(Logger!())
// STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN
```

extension을 witness로 쓰려 하면 `EXTENSION_AUTO_WITNESS_FORBIDDEN` 또는
`EXTENSION_CANNOT_FULFILL_TRAIT_REQUIREMENT`다.

### 5.6 상호작용

- constructor, member, witness, extension은 모두 `def` 계열이지만
  concrete owner가 다르다.
- visibility closure는 public signature가 private type/evidence를
  노출하지 못하게 한다.
- conformance coherence는 모듈 import/use 순서와 독립적이다.
- glyph operator는 arbitrary Trait/extension으로 overload하지 않는다.
  정확한 `Add`/`Subtract`/`Multiply` fixed-glyph conformance만 Stable이다.
- extension은 target type의 stored layout이나 private authority를
  바꾸지 못한다.

## 6. 사례 5 — Enum, 구조적 Record, schema materialization

### 6.1 요구사항과 전제

사용자 상태를 Enum으로 표현하고,
동적 key Map이 아닌 구조적 Record에 감사 metadata를 담은 뒤,
명시적 schema row를 materialize한다.

세 data plane을 구별한다.

- Enum case 선언/값/pattern payload
- 구조적 `Record`의 정적 label
- `SchemaDecl`이 권위를 부여한 typed materialization

### 6.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
module demo::profile

public enum ProfileState {
    draft
    active
    blocked(reason: String)
}

public schema UserRow {
    id: Int
    state: ProfileState
    metadata: Record
    enabled: Bool = true
}

private def makeRow(id: Int, state: ProfileState) -> UserRow
    throws Never
    effects {}
= {
    let metadata = ${
        source: "import"
        verified: true
    }

    return UserRow${
        id: id
        state: state
        metadata: metadata
    }
}

private def stateLabel(state: ProfileState) -> String = {
    return @match state {
        ::draft           => "draft"
        ::active          => "active"
        ::blocked(reason) => "blocked:${reason}"
    }
}

let row = makeRow(13, ProfileState::active)
```

### 6.3 컴파일러 판정 순서

1. **Enum declaration**
   `ProfileState`의 case는 `case` keyword 없이 bare declaration으로
   읽는다.

2. **payload plane**
   declaration의 `blocked(reason: String)`은 field declaration payload다.
   value construction의 `ProfileState::blocked(reason: "...")`는
   argument payload이고 pattern의 `::blocked(reason)`은 pattern payload다.

3. **schema declaration**
   `SchemaFieldDecl` 네 개를 읽고 label uniqueness, type, default 및
   visibility를 검사한다.

4. **Record materialization**
   bare `${...}`는 `MaterializationBody`로 구조적 Record를 만든다.
   `source`와 `verified`는 runtime Map key가 아니라 static label이다.

5. **typed materialization**
   `UserRow${...}`는 `TypedMaterializationExpr`다.
   target이 schema authority를 갖는지 검사한다.

6. **field completion**
   `id`, `state`, `metadata`를 explicit row에서 얻고,
   `enabled`는 admitted default로 채운다.

7. **match expected type**
   `@match state`가 subject를 명시한다.
   `::draft` 등은 expected `ProfileState`에서 case identity를 얻는다.

8. **exhaustiveness**
   세 case가 모두 있으므로 `otherwise` 없이 total하다.

9. **lowering**
   Record label order, schema field identity, default 평가 순서와 Enum
   injection identity를 보존한다.

### 6.4 평가 추적

`makeRow(13, ProfileState::active)`의 순서는 다음과 같다.

1. `id`와 `state` argument를 왼쪽부터 평가한다.
2. Record entry `source` 값을 평가한다.
3. Record entry `verified` 값을 평가한다.
4. 완성된 structural Record를 `metadata`에 bind한다.
5. `UserRow` schema authority를 확인한다.
6. `id`, `state`, `metadata` entry를 source order로 평가한다.
7. 누락된 `enabled` default를 schema-defined order로 평가한다.
8. 모든 field 검사가 성공한 뒤 row를 한 번 commit한다.
9. 중간 실패에서는 partial `UserRow`가 escape하지 않는다.

### 6.5 실패 변형과 진단

schema에 없는 label은 `TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD`다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let invalid = UserRow${
    id: 13
    state: ::active
    metadata: ${ source: "manual" }
    nickname: "Dee"
}
// TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD
```

일반 class를 `${...}`로 만들려 하면
`TYPE_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_AUTHORITY`다.
반대로 schema construction은 constructor `def!`를 호출하지 않는다.

Map은 static named-label source가 아니다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let values = #map{ "id": 13, "state": ProfileState::active }
let invalid = UserRow${ **values }
// Map의 runtime key는 schema named unfold가 아니다.
```

### 6.6 상호작용

- Enum value shorthand `::active`는 expected type이 있어야 한다.
- Record unfold `**record`는 static label을 보존한다.
- Map lookup과 Record member/label lookup은 다른 failure 및 identity를
  갖는다.
- schema default가 effectful이면 별도 admission과 effect 예산이 필요하다.
- resource constructor의 cleanup 책임을 schema materialization으로
  우회할 수 없다.

## 7. 사례 6 — 1-based collection과 NumericArray

### 7.1 요구사항과 전제

ordinary List와 NumericArray의 1-based 논리 좌표를 함께 사용한다.
List slice는 source coordinate를 보존하는 view이고,
matrix axis도 각 차원에서 1부터 시작한다.

요구사항은 다음과 같다.

- index `1`이 첫 element다.
- slice anchor `^`와 `$`는 index suffix 안에서만 쓴다.
- NumericArray exact shape와 element count가 일치한다.
- 다축 index는 semicolon으로 나눈다.
- matrix product shape가 호환되어야 한다.

### 7.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/value-operator-indexing-coherence.json -->
```deeplus
module demo::coordinates

let names = ["Ada", "Dee", "Lin"]
let firstName = names[1]
let lastName = names[names.length]
let middleNames = names[^ + 1 ..< $]

let row = #[1, 2, 3]
let column = #[4; 5; 6]
let matrix = #2,3[
    1, 2, 3;
    4, 5, 6;
]

let second = row[2]
let secondColumn = matrix[*; 2]
let product = matrix ** column
```

### 7.3 컴파일러 판정 순서

1. **List literal**
   plain `[...]`를 `ListLiteral`로 읽고 common element type `String`을
   확인한다.

2. **index suffix**
   `names[1]`에서 `IndexSuffix`와 `SliceIndexExpr`를 만든다.
   collection kind가 List이므로 logical domain은 `1..length`다.

3. **anchor parse**
   `$`와 `^ + 1 ..< $`는 `SliceBound` owner 안에서만 인정한다.

4. **view type**
   slice 결과는 source owner와 coordinate provenance를 가진
   `ReadonlyView<String>` 후보다.

5. **NumericArray sigil**
   `#[...]`, `#[...;...]`, `#2,3[...]`을 각 NumericArray literal
   production으로 구분한다.

6. **shape inference/check**
   `row`는 1차원 length 3,
   `column`은 column-vector shape,
   `matrix`는 exact 2×3 shape다.

7. **axis index**
   `matrix[*; 2]`는 첫 axis full selection과 둘째 axis coordinate 2를
   가진다.

8. **linear product**
   `matrix ** column`의 inner dimension이 3으로 일치하는지 검사한다.

9. **lowering**
   bounds check, element evaluation, view provenance, allocation/backend
   책임과 failure-before-commit을 보존한다.

### 7.4 평가 추적

`names[^ + 1 ..< $]`:

1. receiver `names`를 한 번 평가한다.
2. receiver length와 logical domain을 얻는다.
3. `^`를 첫 coordinate 1로 해석한다.
4. offset `+ 1`을 적용해 lower bound 2를 얻는다.
5. `$`를 마지막 coordinate 3으로 해석한다.
6. half-open delimiter `..<`를 적용한다.
7. bound validity를 검사한다.
8. source coordinate/provenance를 보존한 view를 만든다.

`matrix ** column`:

1. 왼쪽 matrix를 평가한다.
2. 오른쪽 column을 평가한다.
3. element domain과 rank/shape를 검사한다.
4. 결과 allocation 책임을 확보한다.
5. canonical row/column 순서로 곱셈과 합을 수행한다.
6. overflow/Defect가 있으면 partial 결과를 publish하지 않는다.
7. 성공 시 결과 owner를 한 번 commit한다.

### 7.5 실패 변형과 진단

0-based 습관을 그대로 쓰면 current coordinate law를 위반한다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/value-operator-indexing-coherence.json -->
```deeplus
let first = names[0]
// ZERO_BASED_INDEX_NOT_CURRENT 또는 INDEX_OUT_OF_LOGICAL_DOMAIN
```

exact shape의 element 수가 맞지 않으면
`NUMARR_ELEMENT_COUNT_MISMATCH`다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
let invalid = #2,3[
    1, 2;
    3, 4;
]
// 선언 shape 2×3과 element layout 불일치
```

빈 suffix `values[]`는 current full slice가 아니다.
full axis는 `*`이며 빈 suffix는 `INDEX_SUFFIX_REQUIRES_AXIS`다.

### 7.6 상호작용

- List, String, Bytes는 기본 1-based domain을 공유하지만 element type과
  slicing 결과는 서로 다르다.
- bounded source나 기존 slice의 view는 원 source coordinate를 보존한다.
- `Sequence<T>` conformance만으로 `[]`가 자동 활성화되지 않는다.
- NumericArray `^` postfix transpose와 slice anchor `^`는 owner가 다르다.
- allocation, overflow, bounds failure는 Error/Defect/cleanup 축을
  지우지 않는다.

## 8. 사례 7 — effect, Error, defer cleanup

### 8.1 요구사항과 전제

파일을 열어 모든 bytes를 읽고,
정상 반환과 `IOError` 어느 경로에서도 handle을 정확히 한 번 닫는다.
`FileIO` capability description은 explicit context로 전달한다.

이 사례는 다음 책임을 한꺼번에 보여 준다.

- named effect capability declaration
- context authority carrier
- `throws IOError`
- `effects {io}`
- `defer`의 single cleanup invocation
- failure와 cleanup failure ordering

예제의 `openFile`, `readAll`, `closeFile`은 같은 module profile의
admitted callable이라고 가정한다.

### 8.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
module demo::files

public capability FileIO for {io}

public def load(
    path: String,
    context fileIO: FileIO,
) -> Bytes
    throws IOError
    effects {io}
= {
    let handle = openFile(path, context fileIO)
    defer closeFile(handle, context fileIO)
    return readAll(handle, context fileIO)
}
```

### 8.3 컴파일러 판정 순서

1. **capability declaration**
   `NamedEffectCapabilityDecl`이 nominal nonvalue identity `FileIO`와
   nonempty effect row `{io}`를 기록한다.

2. **signature**
   value/context parameter, return, error set, effect row를 정규화한다.

3. **open call**
   `openFile`의 argument role과 effect/error 요구를 검사한다.

4. **handle binding**
   성공한 open 결과의 resource/cleanup owner를 local `handle`에 둔다.

5. **defer registration**
   `DeferredCleanupInvocation`의 receiver와 argument를 등록 시점에
   owner-safe하게 고정한다.

6. **read call**
   `readAll`의 `io` effect와 `IOError`를 enclosing signature에
   포함하는지 확인한다.

7. **control-flow cleanup**
   normal return, throw, Defect, Cancellation edge마다 defer가 정확히
   한 번 실행되는지 검사한다.

8. **failure aggregation**
   body의 primary failure와 cleanup failure를 정해진 순서로 보존한다.

9. **MIR**
   open commit, defer registration, read outcome, LIFO cleanup,
   return/throw terminal을 관측 event로 남긴다.

### 8.4 평가 추적

정상 경로:

1. `path`를 평가한다.
2. `fileIO` context binding을 평가한다.
3. `openFile`을 호출한다.
4. 성공 commit에서 handle owner를 얻는다.
5. `closeFile(handle, context fileIO)` cleanup을 등록한다.
6. `readAll`을 호출해 Bytes owner를 얻는다.
7. return value를 임시 보존한다.
8. defer stack을 LIFO로 실행해 handle을 닫는다.
9. cleanup 성공 뒤 Bytes를 caller에 반환한다.

`readAll`이 `IOError`를 내는 경로:

1. error를 primary failure로 보존한다.
2. `closeFile` cleanup을 실행한다.
3. cleanup이 성공하면 원래 `IOError`를 throw한다.
4. cleanup도 실패할 수 있는 profile이면 원 error를 primary,
   cleanup failure를 suppressed로 정렬한다.

`openFile`이 실패하면 handle owner와 defer registration이 아직 없으므로
`closeFile`을 실행하지 않는다.

### 8.5 실패 변형과 진단

cleanup effect가 enclosing budget을 넘으면
`DEFER_EFFECT_EXCEEDS_FUNCTION_BUDGET`다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public def invalidLoad(
    path: String,
    context fileIO: FileIO,
) -> Bytes
    throws IOError
    effects {}
= {
    let handle = openFile(path, context fileIO)
    defer closeFile(handle, context fileIO)
    return readAll(handle, context fileIO)
}
// io effect가 signature에서 누락됨
```

`unsafe`를 effect atom으로 넣는 것은 다른 축의 오류이며
`EFFECTROW_UNSAFE_AXIS_FORBIDDEN`이다.

### 8.6 상호작용

- capability 이름은 effect row를 자동 추론하지 않는다.
- context carrier가 있다고 effect가 사라지지 않는다.
- `defer`는 arbitrary block을 받지 않고 bounded cleanup invocation을
  받는다.
- resource move가 일어나면 cleanup owner도 새 owner로 이동한다.
- Cancellation은 `catch IOError`로 회복되지 않지만 cleanup은 실행한다.

## 9. 사례 8 — borrow, inout, move와 owner commit

### 9.1 요구사항과 전제

label은 shared observation으로 읽고,
caller의 Buffer place를 exclusive하게 갱신하며,
replacement Buffer owner를 callee로 이전한다.

요구사항은 다음과 같다.

- `borrow`는 read-only view region을 만든다.
- `inout`은 정확한 caller place를 exclusive borrow한다.
- `move`는 replacement owner를 소비한다.
- assignment가 성공하기 전까지 failure atomicity를 지킨다.
- return 뒤 overlapping borrow가 남지 않는다.

### 9.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
module demo::buffers

public def replace(
    borrow label: String,
    inout target: Buffer,
    move replacement: Buffer,
) -> Unit
    throws BufferError
    effects {log}
= {
    log("replace:${label}")
    validate(replacement)
    target = move replacement
}

private def update() -> Unit
    throws BufferError
    effects {log}
= {
    var current = Buffer!(capacity: 16)
    let next = Buffer!(capacity: 64)
    replace("cache", current, move next)
    consume(move current)
}
```

### 9.3 컴파일러 판정 순서

1. **parameter mode parse**
   `borrow`, `inout`, `move`를 각 `ValueParameter`의 `ParameterMode`로
   기록한다.

2. **call place 검사**
   `"cache"`는 borrow 가능한 temporary/read value,
   `current`는 mutable exact place,
   `next`는 owned movable place인지 확인한다.

3. **alias 검사**
   `current`의 inout call region과 겹치는 live borrow/inout가 없는지
   검사한다.

4. **move 준비**
   `next`를 consume 후보로 표시하되 call admission/argument 준비가
   실패하기 전에는 source owner를 잃지 않는다.

5. **callee region**
   `label` borrow와 `target` exclusive region의 lifetime을 call에
   결합한다.

6. **validation**
   replacement를 소비하지 않는 observation으로 검사한다.

7. **assignment commit**
   `target = move replacement`에서 old target cleanup과 new owner commit의
   정확한 순서를 검사한다.

8. **post-call place state**
   `next`는 moved,
   `current`는 새 Buffer owner를 가진 initialized place다.

9. **final move**
   `consume(move current)`가 마지막 owner를 이전한다.

### 9.4 평가 추적

호출 전:

| place | 상태 |
|---|---|
| `"cache"` | immutable String value |
| `current` | initialized mutable Buffer owner |
| `next` | initialized Buffer owner |

호출 준비와 실행:

1. label 표현식을 평가하고 borrow region을 연다.
2. `current` place identity를 한 번 계산하고 exclusive reservation한다.
3. `next` owner를 move 준비 상태로 둔다.
4. 세 argument admission이 모두 성공하면 call을 commit한다.
5. `log`를 실행한다.
6. `validate`가 replacement를 검사한다.
7. validation 성공 시 replacement를 target으로 이동한다.
8. old target owner의 cleanup 계획을 exactly-once로 실행한다.
9. call region을 닫고 `current`를 caller에게 갱신된 상태로 돌려준다.

validation 실패:

1. assignment commit 전이므로 `current` 값은 바뀌지 않는다.
2. callee가 move parameter를 이미 획득한 call commit 뒤라면
   replacement cleanup 책임은 callee failure path에 있다.
3. caller는 `next`를 재사용할 수 없다.
4. `inout` region은 error unwind에서 닫힌다.

### 9.5 실패 변형과 진단

move 뒤 source를 다시 쓰면 use-after-move다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
let original = Buffer!(capacity: 64)
let moved = move original
consume(move original)
// moved source 재사용
```

borrow를 escaping closure에 저장하면
`CLOSURE_BORROW_CAPTURE_ESCAPES` 또는 `BORROW_ESCAPE_OWNER_REGION`이다.
같은 place를 두 `inout` argument에 겹쳐 전달하면 ownership admission이
실패한다.

### 9.6 상호작용

- parameter mode와 type ownership qualifier는 별도 identity field다.
- effect/error가 발생해도 owner balance는 모든 edge에서 맞아야 한다.
- pattern move는 pattern 성공 commit에서만 일어난다.
- actor message의 move는 enqueue commit에서 일어난다.
- task capture의 move는 child environment publish와 결합된다.

## 10. 사례 9 — async 함수와 구조화된 task

### 10.1 요구사항과 전제

profile과 설정을 동시에 불러오되 lexical `task scope`가 끝나기 전에
두 child를 모두 기다린다.
실패와 취소에서 child cleanup이 끝나기 전 scope가 escape하지 않는다.

요구사항은 다음과 같다.

- 이름 있는 async callable에는 `def#async`를 쓴다.
- suspension point는 source의 `await`로 보인다.
- child는 `spawn async { => ... }` task body를 쓴다.
- detached child를 만들지 않는다.
- primary/suppressed failure 순서는 scheduler 완료 순서가 아니다.

### 10.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
module demo::dashboard

public def#async loadDashboard(id: UserId) -> Dashboard
    throws NetworkError
    effects {io}
= {
    task scope {
        let profileTask = spawn async { =>
            await loadProfile(id)
        }
        let settingsTask = spawn async { =>
            await loadSettings(id)
        }

        let profile = await profileTask
        let settings = await settingsTask
        return Dashboard!(profile: profile, settings: settings)
    }
}
```

### 10.3 컴파일러 판정 순서

1. **callable profile**
   module function owner가 `#async` profile을 허용하는지 확인한다.

2. **signature**
   suspension/effect/error residue를 callable identity에 남긴다.

3. **task scope**
   `StructuredTaskScope`를 lexical child owner로 만든다.

4. **spawn body**
   각 `SpawnExpr`가 제한된 `TaskBody`를 사용하고,
   capture가 `Transferable`/lifetime 규칙을 만족하는지 검사한다.

5. **await operands**
   `loadProfile(id)`, `loadSettings(id)`,
   `profileTask`, `settingsTask`가 각각 awaitable인지 검사한다.

6. **borrow/isolation**
   suspension을 가로지르는 live borrow나 exclusive inout가 안전한지
   확인한다.

7. **join completeness**
   모든 child handle이 scope 안에서 terminal로 관찰되는지 검사한다.

8. **failure algebra**
   body, child, cleanup failure와 Cancellation의 서로 다른 축을
   보존한다.

9. **MIR identity**
   `scope_id`, lexical `spawn_index`, child/task identity,
   await-resume edge와 cleanup region을 만든다.

### 10.4 평가 추적

1. `id`를 parent frame에서 얻는다.
2. task scope를 연다.
3. 첫 child environment를 준비하고 `spawn_index = 0`으로 publish한다.
4. 둘째 child를 `spawn_index = 1`로 publish한다.
5. scheduler가 어느 child를 먼저 실행할지는 보장하지 않는다.
6. parent가 `await profileTask`에서 중단한다.
7. profile child terminal과 cleanup 뒤 parent가 resume한다.
8. parent가 `await settingsTask`에서 필요하면 다시 중단한다.
9. settings child terminal과 cleanup 뒤 resume한다.
10. Dashboard constructor argument를 왼쪽부터 평가한다.
11. Dashboard owner를 commit한다.
12. 모든 child가 terminal이고 cleanup이 끝났음을 확인하고 scope를 닫는다.
13. Dashboard를 반환한다.

두 child가 모두 실패하면 lexical spawn index가 작은 failure가 primary다.
나머지는 spawn index 순으로 suppressed된다.
scheduler가 둘째 child failure를 먼저 관찰했다고 primary가 바뀌지 않는다.

### 10.5 실패 변형과 진단

child handle을 scope 밖으로 반환해 detached authority를 만들 수 없다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
public def#async detached(id: UserId) -> Task<Profile> = {
    task scope {
        let child = spawn async { => await loadProfile(id) }
        return child
    }
}
// child가 lexical task scope 밖으로 escape
```

live non-shareable borrow가 suspension을 가로지르면 borrow/task boundary
진단이 발생한다.
async owner 밖의 `await`는 `AWAIT_REQUIRES_ASYNC_TASK_CONTROL`이다.

### 10.6 상호작용

- async는 effect/error/ownership을 지우지 않는다.
- `await`는 task를 생성하지 않고 이미 awaitable인 operand를 기다린다.
- spawn capture의 move commit과 child publish는 원자적이어야 한다.
- Cancellation은 Error가 아니며 `catch NetworkError`로 소비되지 않는다.
- defer/resource cleanup은 child와 parent terminal edge 모두에서
  exactly-once다.

## 11. 사례 10 — actor request, mailbox, owner 이전

### 11.1 요구사항과 전제

bounded mailbox를 가진 Counter actor에 두 add 메시지를 보내고,
현재 값을 request한 뒤 reply task를 명시적으로 기다린다.

요구사항은 다음과 같다.

- one-way send 결과는 `Result<Unit, error ActorMessageError>`다.
- request 결과는 즉시 `Result<Task<Int>, error ActorMessageError>`다.
- request expression을 곧바로 `await`하지 않는다.
- mailbox full은 enqueue precommit failure다.
- actor state는 한 turn에서만 변경한다.

### 11.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
module demo::counter

public protocol CounterProtocol {
    send add(value: Int)
    request current() -> Int
}

public actor #mailbox(capacity: 8) Counter {
    -var value: Int = 0

    on add(value: Int) = {
        self.value += value
    }

    request current() -> Int = {
        return self.value
    }
}

public def#async observe(counter: Counter) -> Int
    throws ActorMessageError
    effects {task}
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

### 11.3 컴파일러 판정 순서

1. **protocol**
   `send add`와 `request current` requirement identity를 만든다.

2. **actor declaration**
   explicit visibility, `#mailbox(capacity: 8)`, state field와 handler를
   읽는다.

3. **mailbox profile**
   capacity가 양의 `StaticIntLiteral`인지 확인하고
   `bounded_reject_v1`을 선택한다.

4. **handler compatibility**
   `on add`와 `request current` signature가 protocol requirement와
   맞는지 검사한다.

5. **message selector**
   `counter ~ add`와 `counter ~ current`를 actor domain에서 정적으로
   해석한다.

6. **admission result**
   send와 request에 서로 다른 Result payload type을 부여한다.

7. **guarded binding**
   각 `let Result::ok(...) = ... else ...`가 성공 edge에서만 payload를
   bind한다.

8. **reply await**
   마지막 성공 edge의 `replyTask: Task<Int>`만 `await`한다.

9. **MIR**
   sender, receiver, mailbox profile, message,
   channel sequence와 request correlation identity를 보존한다.

### 11.4 평가 추적

첫 send:

1. receiver `counter`를 한 번 평가한다.
2. argument `1`을 평가한다.
3. mailbox open/capacity를 precommit 검사한다.
4. 성공하면 enqueue commit과 channel sequence를 만든다.
5. `Result::ok(Unit)`을 반환한다.

request:

1. receiver를 평가한다.
2. mailbox admission을 검사한다.
3. enqueue commit에서 correlation identity를 만든다.
4. 즉시 `Result::ok(Task<Int>)`를 반환한다.
5. guarded binding이 `replyTask`를 commit한다.
6. `await replyTask`가 actor reply, handler Error 또는 Cancellation을
   기다린다.

actor turn:

1. 같은 sender/receiver/profile key의 committed message를 FIFO로
   dequeue한다.
2. `add` turn이 state를 exclusive하게 갱신한다.
3. turn 종료 뒤 다음 message가 state를 관찰한다.
4. `current` turn이 값을 읽고 correlation에 reply한다.

### 11.5 실패 변형과 진단

request admission Result를 풀지 않고 바로 await하면 type이 맞지 않는다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
let value = await counter ~ current()
// operand는 Task<Int>가 아니라 Result<Task<Int>, error ActorMessageError>
```

mailbox가 가득 차면 message와 channel sequence가 생기지 않는다.
move payload가 있었다면 sender가 owner를 유지한다.
capacity 0이나 동적 expression은
`ACTOR_MAILBOX_CAPACITY_REQUIRES_STATIC_INT` 계열 진단이다.

### 11.6 상호작용

- actor message는 ordinary method fallback이 아니다.
- actor reference만으로 protocol conformance가 생기지 않는다.
- actor 경계의 borrow/inout payload는 isolation을 위반한다.
- enqueue commit 뒤 Cancellation이 payload owner를 sender에게 돌려주지
  않는다.
- actor turn의 `await`도 state authority를 암시적으로 다른 turn에
  풀어 주지 않는다.

## 12. 사례 11 — SharedCell과 SharedMutex의 현재 library profile

### 12.1 요구사항과 전제

여러 작업이 공유하는 plain configuration을 관찰·교체하고,
counter는 receiver-bound mutex scope에서만 변경한다.

이 사례는 core syntax 추가가 아니라 Prelude/library profile을 사용한다.
`SharedCell<T>`와 `SharedMutex<T>`의 API contract가 활성화된 target을
전제로 한다.

요구사항은 다음과 같다.

- `SharedCell<T>` payload는 normalized Plain이다.
- observation borrow는 scope 밖으로 escape/suspend하지 않는다.
- `replace`는 새 owner를 한 번 commit하고 이전 owner를 반환한다.
- mutex access는 non-reentrant, nonsuspending `inout` scope다.
- unlock은 모든 terminal edge에서 정확히 한 번 일어난다.

### 12.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/shared-state-coherence.json -->
```deeplus
module demo::shared

private def refresh(
    cell: SharedCell<Config>,
    mutex: SharedMutex<Int>,
    move next: Config,
) -> Config
    throws Never
    effects {state} | {log}
= {
    let label = cell.withValue() { borrow current =>
        describe(current)
    }

    mutex.withLock() { inout count =>
        count = count + 1
    }

    log(label)
    return cell.replace(move next)
}
```

### 12.3 컴파일러 판정 순서

1. **type capability**
   `Config`가 SharedCell payload에 필요한 Plain 책임을 만족하는지
   확인한다.

2. **call resolution**
   `withValue`, `withLock`, `replace`를 library profile의 named API로
   해석한다.

3. **closure parameter mode**
   첫 closure의 `borrow current`,
   둘째 closure의 `inout count`를 해당 scoped callback signature와
   맞춘다.

4. **escape/suspension**
   두 scoped reference가 return, storage, spawn, actor message,
   `await`로 escape하지 않는지 검사한다.

5. **effect**
   mutex가 요구하는 `{state}`와 `log(label)`의 `{log}` budget을 맞추고
   SharedCell callback의 effect row를 그대로 전달하는지 확인한다.

6. **replace ownership**
   `move next`를 commit 전까지 원 owner에 두고,
   성공 commit에서 cell로 이전한다.

7. **old owner return**
   cell의 이전 Config owner를 `refresh`의 return owner로 만든다.

8. **MIR events**
   observation begin/end,
   lock acquire/release,
   replace commit과 동일한 sync/operation/cleanup identity를 남긴다.

### 12.4 평가 추적

SharedCell observation:

1. `cell` receiver를 평가한다.
2. sequentially consistent observation을 시작한다.
3. scoped borrow `current`를 closure에 공급한다.
4. `describe(current)`를 실행한다.
5. closure 결과 String을 얻는다.
6. borrow를 끝내고 `observe_end`를 기록한다.

SharedMutex mutation:

1. receiver를 평가한다.
2. non-reentrant lock을 acquire한다.
3. scoped `inout count`를 공급한다.
4. RHS `count + 1`을 계산한다.
5. 같은 place에 assignment를 commit한다.
6. closure가 정상/실패 어느 경로로 끝나도 lock을 정확히 한 번 release한다.

SharedCell replace:

1. `next` owner를 준비한다.
2. cell operation admission을 검사한다.
3. 성공 시 하나의 `replace_commit`으로 새 owner를 저장한다.
4. old Config owner를 결과로 반환한다.
5. precommit 실패가 가능한 profile이라면 `next` owner를 caller가 유지한다.

### 12.5 실패 변형과 진단

scoped borrow를 task로 넘길 수 없다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/shared-state-coherence.json -->
```deeplus
cell.withValue() { borrow current =>
    task scope {
        let child = spawn async { => inspect(current) }
        await child
    }
}
// VIEW_CROSSES_TASK_BOUNDARY
```

mutex callback 안 `await`는 non-suspending contract를 위반한다.
resource/drop payload를 Plain이라고 가정해 SharedCell에 숨기는 것도
거부된다.

### 12.6 상호작용

- `Shared<T>`는 alias handle이고 `Shareable` evidence와 동일하지 않다.
- shared wrapper가 payload `Transferable`을 자동 합성하지 않는다.
- actor isolation과 shared-state API는 서로 독립된 authority domain이다.
- synchronization ordering은 source-level ordinary variable aliasing을
  허용하지 않는다.
- lock release도 cleanup ordering과 failure aggregation에 참여한다.

## 13. 사례 12 — unsafe, foreign boundary, profile 분리

### 13.1 요구사항과 전제

target별 trusted library가 제공한 `RawPtr<Byte>` binding에서 byte 하나를
읽는 current wrapper를 작성한다.
raw foreign declaration 자체는 현행 stable source root의 통합 사례로
쓰지 않는다.
그 선언의 target triple, ABI, symbol, layout, provenance receipt는
별도 외부 경계에서 먼저 닫혀 있다고 가정한다.

요구사항은 다음과 같다.

- unsafe operation은 명시적 `unsafe` block 안에 있다.
- `unsafe`를 EffectRow atom으로 쓰지 않는다.
- pointer provenance, lifetime, nullability를 계속 검사한다.
- foreign/library profile과 core syntax를 구별한다.
- xVM/LLVM lowering이 같은 evaluation/ownership/cleanup을 보존한다.

### 13.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
module demo::raw_read

public def readByte(
    pointer: RawPtr<Byte>,
) -> Byte
    throws PointerError
    effects {memory}
= {
    unsafe {
        return pointer ~ load()
    }
}
```

이 예제에서 `RawPtr`, `Byte`, `PointerError`, `load`의 실제 제공 여부와
target binding은 library/target manifest가 결정한다.
문법이 `unsafe BlockExpr`를 허용한다는 사실만으로 그 binding을
발명하지 않는다.

### 13.3 컴파일러 판정 순서

1. **source parse**
   ordinary `ModuleFunctionDecl`과 body의 `UnsafeBlockExpr`를 만든다.

2. **name resolution**
   `RawPtr`, `Byte`, `PointerError`, `load`가 target-bound trusted module에
   실제로 존재하는지 확인한다.

3. **profile binding**
   library/tooling/target profile의 identity와 current language revision이
   일치하는지 확인한다.

4. **pointer type**
   pointee type, provenance, nullability, alignment, mutability와 lifetime
   책임을 정규화한다.

5. **unsafe authority**
   `load` operation이 현재 lexical unsafe boundary 안에 있는지 검사한다.

6. **effect/error**
   memory observation effect와 recoverable pointer Error가 signature에
   보존되는지 확인한다.

7. **ownership/borrow**
   byte read가 pointer owner를 소비하는지 빌리는지 library signature와
   맞춘다.

8. **ABI receipt**
   외부 호출이 숨어 있다면 target triple, calling convention,
   layout/representability, symbol 및 unwind plan이 같은 artifact
   identity에 묶였는지 확인한다.

9. **backend parity**
   xVM과 LLVM이 argument evaluation, call commit, failure, cleanup,
   return 값을 동일하게 보존해야 한다.

### 13.4 평가 추적

1. caller가 `pointer` argument를 평가한다.
2. callee가 pointer provenance descriptor를 보존한다.
3. lexical unsafe boundary에 진입한다.
4. receiver `pointer`를 한 번 평가한다.
5. `load` selector를 정적으로 고정한다.
6. alignment/nullability/lifetime precondition을 검사한다.
7. 실제 memory read commit을 수행한다.
8. 실패하면 `PointerError` 또는 정해진 Defect 축을 보존한다.
9. 성공하면 Byte 값을 만든다.
10. unsafe lexical boundary를 나간다.
11. pointer의 원래 owner/lifetime 책임을 유지한 채 Byte를 반환한다.

unsafe block을 나간다는 사실은 pointer를 안전한 일반 reference로
변환하지 않는다.
provenance와 lifetime은 이후에도 type/checker 책임으로 남는다.

### 13.5 실패 변형과 진단

unsafe를 effect atom으로 쓰면 안 된다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public def invalidRead(pointer: RawPtr<Byte>) -> Byte
    throws Never
    effects {unsafe}
= {
    return 0
}
// EFFECTROW_UNSAFE_AXIS_FORBIDDEN
```

unsafe operation을 boundary 밖에서 호출하면
`UNSAFE_REQUIRES_UNSAFE_BOUNDARY`다.
`Plain`을 C-compatible layout 증거로 사용하면
`PLAIN_IS_NOT_LAYOUT_SAFE`다.
target receipt 없는 foreign binding은 executable support를 주장할 수
없다.

### 13.6 상호작용

- unsafe authority, EffectRow, ErrorSet은 세 독립 축이다.
- pointer spelling만으로 ABI width/alignment가 정해지지 않는다.
- foreign call도 argument를 source order로 정확히 한 번 평가한다.
- pre-call marshalling 실패가 move owner를 몰래 소비해서는 안 된다.
- callback/pointer/handle은 명시 lifetime 없이 task/actor 경계를 넘지
  않는다.
- official tooling certificate가 runtime witness나 권위 값이 되지 않는다.

## 14. 사례 13 — message payload와 공통 trailing closure

### 14.1 ordinary argument와 message payload

다음 두 괄호는 AST 책임이 다르다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
let ordinary = moveTo(x, y)
let message = worker ~ WorkerProtocol::moveTo (x, y)
```

첫 줄은 ordinary argument 두 개다. 둘째 줄은 selector 뒤의 Tuple payload
하나다. checker가 여러 positional handler parameter에 투영할 수 있지만
AST와 enqueue transport에는 payload가 하나뿐이다. 공백은 의미가 아니므로
`moveTo(x, y)`와 `moveTo (x, y)`는 message 문맥에서 같은 Tuple payload다.

all-named message payload는 하나의 structural Record다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
let configured = worker ~ WorkerProtocol::configure(
    name: "Ada",
    retries: 3,
)
```

`name`, `retries`는 runtime Map key가 아니라 static Record label이다.
positional entry와 섞거나 label을 중복하면 payload AST를 승인하지 않는다.

### 14.2 공통 trailing-closure group

ordinary call과 message call은 같은 group 구조를 쓴다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
let local = transaction()
    onCommit:{ => logCommit() }
    onRollback:{ error => log(error) }

let remote = worker ~ WorkerProtocol::process(job: move job)
    success:[move successToken] #once {
        value => publish(successToken, value)
    }
    failure:[move failureToken] #once {
        error => recover(failureToken, error)
    }
```

각 group에 closure가 두 개이므로 모든 item이 named다. label은 visible
function-typed formal에 결합하고 source order는 capture acquisition과
evaluation order로 남는다. message 예제의 `#once`와 move capture는
표면만으로 actor transfer를 승인하지 않는다. checker가 capture
environment의 transfer, isolation, suspension, effect, error, cleanup을
별도로 증명해야 한다.

### 14.3 phase trace

1. parser가 receiver, selector path, 0/1 payload, ordered closure list를
   보존한다.
2. AST structural validation이 둘 이상의 closure에 label 누락·중복이
   없는지 검사한다.
3. resolution이 `WorkerProtocol::process`를 exact actor-protocol identity로
   고정한다. ordinary method fallback은 없다.
4. call matching이 Record payload label과 trailing label을 각 formal에
   한 번씩 결합한다.
5. HIR이 selector identity, payload projection, closure environment
   responsibility를 보존한다.
6. MIR prepare가 receiver → payload child → closure capture 순으로 한 번씩
   평가한다.
7. actor enqueue commit이 성공할 때만 payload와 closure owner를 이전한다.
8. xVM/LLVM은 같은 event order와 failure/cleanup 결과를 재현해야 한다.

거부 예:

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
worker ~ process(job, priority: 3)
// STATIC_CALL_SHAPE_NOT_ADMITTED: positional/named payload 혼합

worker ~ process job
    { value => publish(value) }
    failure:{ error => recover(error) }
// MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT
```

두 번째 진단 ID는 historical 이름을 유지하지만 현행 message는
“둘 이상이면 모두 unique named”라는 구조 규칙을 뜻한다.

## 15. 사례 14 — Rational, Complex, power와 HIR-H1 경계

### 15.1 요구사항과 전제

이 사례는 정확한 비율 계산, 복소수 principal power, power precedence를
한 프로그램에서 사용한다. 서로 다른 층의 상태를 먼저 구분해야 한다.

- `rational_exact_numeric_value`: `<p/q>` exact Rational value
- `complex_core_numeric_value`: 붙은 float-`i`와 `Complex<Rep>`
- `scalar_real_complex_power`: static matrix의 intrinsic `^`
- `hir_h1_current_mir_bridge_design`:
  `STABLE_DESIGN`, `source_activation: none`인 closed verifier 설계

네 기능의 source/검증 법칙은 current 문서 projection이지만, DP-RFC-0002의
구체 구현과 MIR-X1 lowering/activation은 별도의
`DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE`이다. 어느 층도 실제
lexer/parser/checker/HIR/MIR/xVM/LLVM 실행 receipt가 아니므로 제품 lane은
`15/15 NOT_RUN`이다.

### 15.2 전체 코드

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let reduced: Rational = <6/8>
let negativeRatio: Rational = -<2/3>

let cartesian: Complex = 3.0 + 4.0i
let compact: Complex<Float32> = 1.5f32 - 0.25f32i
let squared: Complex = cartesian ^ 2

let negatedSquare: Float64 = -2.0 ^ 2.0
let squareOfNegative: Float64 = (-2.0) ^ 2.0
let inverseCube: Float64 = 2.0 ^ -3
let tower: Float64 = 2.0 ^ 3.0 ^ 2.0

let above: Complex = Complex!(real: -1.0, imag: +0.0)
let below: Complex = Complex!(real: -1.0, imag: -0.0)
let rootAbove: Complex = above ^ 0.5
let rootBelow: Complex = below ^ 0.5

let computationalOne: Int = 0 ^ 0
```

### 15.3 scanner와 parser 판정

첫 두 줄의 `<`는 항상 Rational이라고 가정하지 않는다. parent가
expression-prefix goal을 연 뒤 scanner/parser가 checkpoint를 만들고
`<` decimal magnitude `/` decimal magnitude `>` 전체를
transactional하게 확인한다. `<6/8>`이 완성되면 Rational literal 후보를
하나 만들지만, 탐사가 실패하면 token을 0개 소비하여 ordinary `<`, `/`,
`>` 문법에 제어를 돌려준다. 부호는 literal 밖의 prefix `-`가 소유한다.

`4.0i`와 `0.25f32i`는 각각 admitted unsuffixed 또는 `f32` decimal
floating magnitude와 붙은 ASCII `i`가 만드는 하나의 imaginary literal
token이다. scanner는 `4i`의 정수 magnitude, `4.0f64i`의 suffix 연쇄,
`4.0 i`의 떨어진 identifier를 허수 literal로 보정하지 않는다.

power parselet의 `lbp`는 160, `rbp`는 159이고 numeric prefix `+`/`-`도
operand를 159에서 읽는다. 따라서 parser는 네 expression을 다음처럼
고정한다.

```text
-2.0 ^ 2.0       -> Prefix(-, Power(2.0, 2.0))
(-2.0) ^ 2.0     -> Power(Prefix(-, 2.0), 2.0)
2.0 ^ -3         -> Power(2.0, Prefix(-, 3))
2.0 ^ 3.0 ^ 2.0 -> Power(2.0, Power(3.0, 2.0))
```

이 시점에는 overload, expected result, runtime 부호, principal branch를
선택하지 않는다. parser의 책임은 source tree와 순서를 결정하는 데
그친다.

### 15.4 checker와 값 판정

Rational checker는 두 decimal component를 `BigInt`로 읽고 다음 invariant를
적용한다.

```text
denominator > 0
gcd(abs(numerator), denominator) == 1
zero == 0/1
```

따라서 `reduced`의 source provenance는 `<6/8>`이지만 값은 정확한 `3/4`다.
`negativeRatio`는 canonical `-2/3`이고, 두 계산 모두 고정 폭 overflow나
floating approximation을 거치지 않는다.

Complex checker는 `cartesian`에서 `3.0`과 `4.0i`를
`Float64`/`Complex<Float64>`의 sealed `BinaryAdd` row에 결합한다.
`compact`는 `Float32` component만 사용한다. 이 두 성공은 일반적인
implicit Float→Complex conversion을 열지 않는다.

power는 operand의 normalized static domain만으로 다음 계획을 고른다.

| binding | 정적 계획 | 결과 |
|---|---|---|
| `squared` | `ComplexPowInt` | `Complex<Float64>` |
| `negatedSquare` 내부 | `FloatPow` 후 prefix `-` | `-4.0` |
| `squareOfNegative` | `FloatPow` | `4.0` |
| `inverseCube` | `FloatPowInt` | `0.125` |
| `tower` inner/outer | `FloatPow`, `FloatPow` | `512.0` |
| `rootAbove`, `rootBelow` | `ComplexPowPrincipal` | branch-side가 반대인 principal root |
| `computationalOne` | `CheckedIntPow` | `Int` one |

real power는 runtime에서 base가 음수인 것을 보고 Complex로 자동 전환하지
않는다. 예를 들어 `(-1.0) ^ 0.5`는 bound real profile의 canonical quiet
NaN이다. Complex 결과를 원한다면 `above ^ 0.5`처럼 base의 정적 domain이
처음부터 Complex여야 한다.

`above`와 `below`는 equality에서는 같은 zero component로 보일 수 있지만,
imaginary `+0.0`/`-0.0` bit가 negative-real branch cut의 어느 쪽인지를
선택한다. `ComplexPowPrincipal`은 이 bit를 지우지 않고
`exp(w * Log0(z))`의 principal branch를 사용한다.

`computationalOne`은 error가 아니라 각 정적 result domain의 one이다.
compiler는 두 operand가 정적으로 0임을 보고
`ZERO_TO_ZERO_POWER_USES_COMPUTATIONAL_CONVENTION` warning을 낼 수 있다.
warning은 결과나 control flow를 바꾸지 않는다.

### 15.5 HIR-H1 verifier와 draft MIR handoff trace

다음 trace의 1~7단계는 `hir_h1_current_mir_bridge_design`의
`STABLE_DESIGN` verifier boundary를 설명한다. 상태는 current
documentation projection이지만 `source_activation: none`이고 제품
구현을 주장하지 않는다.

1. `LosslessCST`는 `<6/8>`, 붙은 `i`, 괄호, unary sign과 trivia를
   보존한다.
2. `NormalizedAST`는 Rational/imaginary literal과 오른쪽 결합 power tree를
   구조적으로 고정하되 overload를 고르지 않는다.
3. `HirSkeleton`은 owner와 body slot을 만들지만 unresolved slot을
   canonical output으로 내보내지 않는다.
4. `CheckSession`이 type, literal normalization, operator row, power
   operation, ownership/effect/cleanup responsibility를 fixed point로 닫는다.
5. `TypedHirDraft`는 모든 선택을 담고 verifier 전 상태로 남는다.
6. verifier는 recovery, unresolved, candidate, placeholder, generic
   operator가 0개일 때만 `Verified<CanonicalHirH1>`을 만든다.
7. exact `MirCapabilityReceipt`가 required/provided capability를 같은
   집합으로 증명하고 unsupported reachable variant 수가 0일 때만
   `ExecutableHirH1`을 만든다.
8. 어떤 허용된 MIR lowering도 이 결정을 구조적으로만 펼치며 resolver,
   witness search, expected-result selection을 다시 실행하지 않아야 한다.

Rational constant는 `RationalConst(ConstRational)`로 seal된다.
`Complex<Float64>` literal path는 real/imaginary IEEE binary64 component
bit와 signed zero를 포함한 `ComplexLiteral(ConstComplex64)`로 seal된다.
이 계약이 `compact`의 `Float32` Rep을 숨겨서 넓히는 authority는 아니다.
power plan은 다음 여섯 operation 중 정확히 하나를 가진다.

```text
CheckedIntPow
FloatPowInt
FloatPow
ComplexPowInt
ComplexPowPrincipal
MeasurePowStatic
```

adaptation도 다음 다섯 개뿐이다.

```text
Identity
DirectLiteralToF64Exact
F32ToF64
F32ToComplex64
F64ToComplex64
```

각 plan은 base를 먼저 한 번, exponent를 다음에 한 번 평가한다.
`math_profile_id`, `special_value_profile_id`, result type, responsibility,
selected static identities를 보존한다. generic `Pow`, power witness,
runtime fallback, expected-result 선택은 없다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

`DP-RFC-0002`의 구체 Rust 구현, 위 8단계의
`Verified<ProposedMirX1>` lowering 및 MIR-X1 activation은
`DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE`이다. 이 draft가 stable
verifier invariant를 소비한다고 해서 같은 authority 상태가 되지는
않는다. current backend authority는 xVM initial execution, LLVM AOT,
LLVM ORC JIT로 유지되며 Cranelift나 xVM-only 전환을 승인하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

### 15.6 실패 변형과 진단

#### Rational과 imaginary literal

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let zeroDenominator = <2/0>
// RATIONAL_LITERAL_DENOMINATOR_ZERO

let malformed = <2 / 3>
// RATIONAL_LITERAL_MALFORMED

let detached = 4.0 i
// IMAGINARY_LITERAL_MARKER_MUST_BE_ATTACHED

let integerImaginary = 4i
let chainedSuffix = 4.0f64i
// IMAGINARY_LITERAL_FORM_NOT_ADMITTED

let historical = 4.0j
// HISTORICAL_IMAGINARY_J_NOT_CURRENT
```

분모 0은 exact literal shape를 성공적으로 인식한 뒤 checker가 거부한다.
반면 malformed Rational과 잘못된 imaginary suffix는 canonical literal
node를 만들기 전에 끝난다. 어느 경우도 recovery node가 HIR/MIR value로
내려가지 않는다.

#### power domain과 result-directed 선택

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let rationalPower = <2/3> ^ 2
// POWER_OPERAND_DOMAIN_NOT_ADMITTED

let forcedByResult: Complex = 2 ^ 3
// POWER_EXPECTED_RESULT_SELECTION_FORBIDDEN
```

첫 식은 initial power matrix에 Rational row가 없기 때문에 거부된다.
둘째 식의 두 operand는 exact integer이므로 선택 가능한 operation은
`CheckedIntPow`뿐이다. result annotation `Complex`가
`ComplexPowPrincipal` 후보를 새로 만들 수 없다.

### 15.7 상호작용과 상태

- Rational normalization은 equality/hash의 exact value identity를
  제공하지만 source spelling을 formatter가 기약분수로 강제 rewrite하지
  않는다.
- Complex signed zero는 ordinary `==` 결과와 branch-sensitive
  transcendental semantics에서 역할이 다르다.
- fixed conformance는 `+`, `-`, `*`만 소유하고 `^`는 language intrinsic로
  남는다.
- power adaptation은 해당 plan 안에서만 유효하며 일반 call/operator
  conversion으로 퍼지지 않는다.
- HIR-H1 verifier boundary는 `STABLE_DESIGN`이지만 제품 support를
  증명하지 않으며, DP-RFC-0002/MIR-X1 구현·adoption은 별도의
  noncanonical/nonactivatable draft다.
- 관련 15개 제품 lane은 모두 `NOT_RUN`이다.

## 16. 사례 사이의 공통 compiler 판정 순서

앞의 14개 예제는 기능이 달라도 다음 공통 pipeline을 따른다.

| 단계 | 질문 | 대표 실패 |
|---:|---|---|
| 1 | source role과 source root가 맞는가 | entry/root conflict |
| 2 | token과 structural production이 완성되는가 | boundary/attachment 오류 |
| 3 | contextual owner와 parser goal이 맞는가 | parameter/argument 혼동 |
| 4 | 이름이 정확한 namespace에서 하나로 해석되는가 | unknown/ambiguous name |
| 5 | type과 generic constraint가 정규화되는가 | kind/variance/Union 오류 |
| 6 | call/pattern/member owner admission을 통과하는가 | role/witness/extension 오류 |
| 7 | ownership, borrow, isolation이 모든 edge에서 균형인가 | move/escape/alias 오류 |
| 8 | effect, Error, Defect, Cancellation이 보존되는가 | budget/overlap 오류 |
| 9 | cleanup과 commit 순서가 닫히는가 | double cleanup/partial commit |
| 10 | HIR/MIR identity와 관측 순서가 보존되는가 | lowering contract drift |
| 11 | target/profile receipt가 실제 support를 증명하는가 | `NOT_RUN` 또는 unbound |

이 순서는 “parser가 받았으니 실행 가능하다”는 잘못된 단축을 막는다.
특히 schema, witness, actor, shared state, unsafe/foreign boundary는
구문 뒤의 authority와 receipt가 핵심이다.

## 17. 통합 실패 분석법

### 17.1 첫 진단을 고르는 법

하나의 source가 여러 규칙을 위반해도 compiler는 owner가 정한
deterministic precedence로 첫 진단을 선택해야 한다.

예를 들어:

- executable root에 entry가 없으면 body type 추론보다 target entry
  진단이 우선한다.
- cast token attachment가 틀리면 cast type compatibility를 검사하지
  않는다.
- actor request admission `Result`를 풀지 않았다면 reply payload 내부의
  type 오류보다 outer call/await mismatch가 먼저다.
- schema authority가 없는 target에는 unknown field 검사를 적용하기 전에
  target-kind 진단이 우선한다.
- move source가 이미 소비되었다면 이후 overload 후보를 맞추어 그 사실을
  숨기지 않는다.

### 17.2 parse 오류와 checker 오류를 분리한다

| 예 | parse 결과 | checker 결과 |
|---|---|---|
| `names[]` | recovery CST | current index node 0 |
| class의 `out T` | 구조 CST 가능 | owner variance 거부 |
| ordinary arg로 context 전달 | call CST 가능 | role mismatch |
| schema unknown field | materialization CST 가능 | label admission 거부 |
| `effects {unsafe}` | effect-row CST 가능 | axis separation 거부 |

문서와 IDE는 이 차이를 사용자에게 보여 주어야 한다.
parser recovery가 source를 current program으로 승인한 것처럼 표시하거나,
checker 오류를 syntax highlighting 실패로 축소하면 안 된다.

### 17.3 실패 원자성 질문

각 mutation/transfer 예제에는 다음 질문을 적용한다.

1. commit 전 원 owner는 누구인가?
2. commit을 식별하는 정확한 event는 무엇인가?
3. precommit failure에서 원 value와 owner가 보존되는가?
4. postcommit Cancellation이 이미 일어난 transfer를 되돌리는가?
5. partial result가 관측 가능한가?
6. cleanup owner는 terminal edge마다 정확히 하나인가?

List/NumericArray construction, schema materialization, `inout` assignment,
task spawn, actor enqueue, SharedCell replace와 foreign marshalling은 모두
이 질문에 답해야 한다.

## 18. 통합 예제를 확장할 때의 규칙

새 예제를 추가할 때에는 다음 최소 정보를 함께 적는다.

- source role과 root
- 사용한 concrete production
- 필요한 Prelude/library/profile identity
- parse와 admission의 분리
- type/generic/overload 판정
- ownership과 borrow region
- effect/error/defect/cancellation
- source-order 평가
- commit과 cleanup
- positive/negative/boundary 결과
- 제품 receipt 상태

코드만 추가하고 이 정보를 생략하면 example corpus는 syntax gallery가
될 뿐 언어 참조서가 되지 못한다.

## 19. 마지막 종합 체크리스트

다음 질문에 모두 답할 수 있어야 통합 사례를 이해한 것이다.

1. 이 파일은 library, executable, script 중 어느 root인가?
2. 선언의 concrete owner는 무엇인가?
3. 같은 token이 다른 parser goal에서 어떤 뜻을 갖는가?
4. generic inference가 고정되는 시점은 언제인가?
5. context와 witness가 ordinary argument와 왜 다른가?
6. pattern binding과 move는 어느 edge에서 commit되는가?
7. Record label, Map key, schema field identity가 어떻게 다른가?
8. 첫 논리 index와 slice coordinate는 무엇인가?
9. effect capability와 effect row는 왜 둘 다 필요한가?
10. move/inout/borrow가 failure에서 어떻게 균형을 맞추는가?
11. task child와 actor payload owner는 언제 이전되는가?
12. shared-state operation의 release/observation 끝은 어디인가?
13. unsafe boundary가 숨기지 못하는 책임은 무엇인가?
14. MIR이 보존해야 할 관측 순서는 무엇인가?
15. 정적 설계와 실제 제품 support를 어떤 receipt로 구분하는가?
16. Rational source spelling과 canonical BigInt 값 identity가 어떻게
    분리되는가?
17. Complex signed zero가 equality와 principal branch에서 각각 어떤
    역할을 하는가?
18. power operation이 expected result나 runtime 값이 아니라 정적 operand
    domain으로 언제 고정되는가?
19. canonical HIR과 executable HIR을 capability receipt가 왜 분리하는가?
20. MIR-X1의 noncanonical 상태와 current xVM/LLVM backend authority를
    구분할 수 있는가?

답은 기능별 한 문장으로 끝나지 않는다.
source owner, 정적 admission, 평가 순서, commit, cleanup 및 target evidence를
한 흐름으로 연결해야 한다.
그 연결이 바로 이 장의 통합 예제가 제공하려는 언어 참조 관점이다.
