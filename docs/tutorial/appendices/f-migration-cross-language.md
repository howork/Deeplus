# 부록 F — 다른 언어에서 Deeplus로 옮겨 오기

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 비교는 학습을 위한 직관이다. 다른 언어의 문법을 Deeplus authority로
> 가져오지 않으며 product 실행은 `NOT_RUN`이다.

## 1. 가장 먼저 바꿀 습관

| 익숙한 가정 | Deeplus에서 확인할 것 |
|---|---|
| index 0이 첫 원소 | 일반 index는 1부터 시작 |
| `.`이 모든 path/member 구분 | qualified owner path는 `::`; member 표면은 문맥별 규칙 |
| package와 namespace가 같은 축 | Package와 Module을 분리 |
| guard 함수 이름만으로 narrowing | 검증된 `GuardSummaryV1` direct truth-test와 stable actual만 narrowing |
| operator는 사용자가 새 glyph를 정의 | fixed admitted glyph conformance만 허용 |
| enum case는 `case` keyword 사용 | `case`는 ordinary identifier |
| raw string delimiter가 언어마다 다름 | Deeplus는 `#raw"..."`만 사용 |
| async 함수는 `async def` | current named spelling은 `def#async` |

## 2. C#/Java/Kotlin 계열에서

nullable reference를 하나의 특수 표면으로만 생각하지 말고
`Option`, closed Union, refinement, pattern을 어떤 failure contract에
쓸지 결정한다. extension-like syntax가 nominal member, named extension,
Trait witness 중 무엇을 뜻하는지도 구분한다.

Class static member에 익숙해도 Deeplus의 함수 `static { ... }`과 Class
Preview Design 표면을 합치지 않는다.

## 3. Rust에서

ownership과 borrow라는 큰 방향은 익숙할 수 있지만 Deeplus의 exact
parameter role, actor boundary, effect/error row, binding transaction을
Rust 문법으로 치환하지 않는다. Trait conformance도 implicit blanket
search나 specialization을 Current라고 가정하지 않는다.

## 4. Python/JavaScript에서

dynamic truthiness 대신 Bool 조건과 static type evidence를 사용한다.
Union을 runtime tag 없는 임의 값 묶음으로 생각하지 않는다. `Map`의
key absence와 `Option`, recoverable error를 sentinel `null` 하나로
합치지 않는다.

## 5. Swift/Kotlin에서

Enum/closed hierarchy와 exhaustive pattern 경험은 도움이 된다. 하지만
Deeplus의 current mixed Enum payload, marker reachability, semantic
`EnumId`/`VariantId` 분리는 exact reference를 따라야 한다. trailing
closure도 message-call surface와 ordinary call의 owner를 먼저 확인한다.

## 6. D/C++에서

operator overloading을 임의 glyph/precedence 확장으로 옮기지 않는다.
fixed-glyph conformance의 admitted set과 exact operand/result domain에
맞춘다. template/compile-time 기능을 Deeplus generic, context, witness,
static activation과 일대일 대응시키지 않는다.

## 7. 이행 체크리스트

1. index와 slice 경계를 다시 썼는가?
2. Package/Module/qualified path를 분리했는가?
3. error/effect/cancellation을 signature에 남겼는가?
4. implicit conversion 대신 exact numeric/type corridor를 확인했는가?
5. pattern binding의 commit 시점을 보존했는가?
6. Preview Design을 Current로 옮기지 않았는가?
7. compiler가 실행됐다고 근거 없이 쓰지 않았는가?

## 8. 다음 읽을 곳

- [첫 학습 Part](../part-01-orientation/README.md)
- [타입 시스템](../part-04-type-system/README.md)
- [Trait](../part-06-traits/README.md)
- [소유권](../part-07-ownership/README.md)
- [Preview와 진화](../part-12-preview-evolution/README.md)

이행은 다른 언어의 기능 이름을 바꾸는 작업이 아니라 책임의 위치를
다시 표현하는 작업이다. 자동 rewrite 전에 type, owner, effect,
failure, observation order가 모두 보존되는지 작은 acceptance 표로
확인한다.
