# 04-05. callable identity, effect와 cancellation

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 함수 타입 identity가 매개변수와 반환 타입 외에도 error, effect,
cancellation, call channel을 보존하는 이유를 설명한다.

## 2. 학습 목표

- function type의 parameter/return/error/effect 축을 읽는다.
- pure callable과 effectful/throwing callable의 호환성 경계를 이해한다.
- named capability와 effect row를 구분한다.
- Error, Defect, Cancellation, suspension을 별도 outcome으로 유지한다.

## 3. 선수 지식

이 Part의 generic kind와 Result, Part 3의 함수 서명·parameter channel을
알고 있어야 한다.

### 미리 보는 최소 모델과 후속 심화

ownership channel은 callable이 값을 빌리는지, 변경 권한을 받는지,
소유권을 넘겨받는지를 parameter identity에 남긴다는 최소 직관만
사용한다. place state, lifetime, cleanup의 정확한 증명은 Part 7에서
심화한다. Cancellation은 task/scope가 소유하는 별도 control outcome이며
상세 구조화 동시성은 Part 10에서 배운다. 이 장에서는 둘을 ErrorSet이나
EffectRow에 숨기지 않는 callable identity 원칙만 먼저 세운다.

## 4. 문제에서 출발하기

두 함수가 모두 `String`을 받아 `Bytes`를 돌려줘도 하나는 순수 계산이고
다른 하나는 파일 I/O와 `IOError`를 가질 수 있다. 둘을 같은 타입으로
취급하면 caller가 준비하지 않은 권한과 실패가 숨어 들어온다. Deeplus의
callable identity는 모든 responsibility-bearing 차이를 보존한다.

## 5. 핵심 모델

- 함수 타입은 `(parameters) -> Return throws Errors effects Effects`다.
- value/context/witness/rest channel과 ownership mode도 identity다.
- `throws Never effects {}`는 닫힌 순수 책임이다.
- effect row는 어떤 effect가 발생할 수 있는지 설명한다.
- capability는 그 effect를 수행할 nominal authority이며 context로 받는다.
- ErrorSet은 recoverable errors이고 Defect/Cancellation은 그 member가
  아니다.
- suspension과 cancellation responsibility를 effect row 안에 숨기지
  않는다.

## 6. 단계별 예제

서로 다른 책임의 함수 타입을 이름으로 분리한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private type PureParser =
    (String) -> Result<Int, error ParseError>
        throws Never
        effects {}

private type FileLoader =
    (String) -> Bytes
        throws IOError
        effects io

private type Command =
    (String, String..., Record***) -> Unit
        throws Never
        effects {}
```

반환 타입만 비교하면 세 타입의 실제 호출 책임을 잃는다. `Command`는
repeated/named-rest channel도 identity에 남긴다.

effect row와 capability는 함께 쓰되 같은 것이 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public capability FileIO for {io}

private def load(path: String, context fileIO: FileIO) -> Bytes
    throws IOError
    effects io
= {
    return readFile(path, context fileIO)
}
```

`effects io`가 권한 값을 만들어 주지 않고, `FileIO` context를 가졌다는
사실만으로 실제 effect가 발생했다고 간주하지도 않는다.

### 판정 trace, 미니 사례와 흔한 오해

function type을 비교할 때 fixed/repeated/named-rest value channel,
context/witness channel, ownership mode를 차례로 정규화한다. 이어 return
type, ErrorSet, EffectRow, cancellation/suspension/isolation/capture 책임을
비교한다. 한 축이라도 caller가 준비한 계약보다 크면 단순 assignment나
callback 전달을 거부한다. capability가 필요한 effect라면 row뿐 아니라
해당 context authority가 실제로 공급되는지도 확인한다.

미니 사례로 `String -> Bytes` 두 함수 중 하나가 `IOError`와 `{io}`를
가진다면 pure decoder 자리에 넣을 수 없다. 흔한 오해는 return type만
같으면 함수 값이 호환되거나, capability를 가졌다는 사실이 effect
실행을 뜻한다는 생각이다. row는 관찰 가능성, capability는 수행 권한이며
Cancellation은 어느 쪽에도 흡수되지 않는 별도 축이다.

## 7. 허용·거부·경계 사례

Cancellation을 recoverable ErrorSet으로 선언하거나 effectful callable을
pure callable 자리에 숨겨 넣지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: CALLABLE_RESPONSIBILITY_* -->
```deeplus
private type BadCancellation =
    () -> Unit
        throws Cancellation
        effects {}

let loader: FileLoader = obtainLoader()
let parser: PureParser = loader
```

첫 항목에서 Cancellation은 ErrorSet member가 아니다. 두 번째는
parameter/return/error/effect 계약이 모두 다르다. `catch`로
Cancellation을 Error처럼 회수하거나 Result로 자동 변환하는 것도
허용하지 않는다.

## 8. 다른 기능과의 연결

async/actor/task는 suspension, isolation, cancellation owner와 cleanup을
추가로 보존한다. actor request가 돌려주는 Task responsibility는 일반
async Task에 자동 부여되지 않는다. closure capture와 selected Trait
witness도 public callable identity 및 lowering evidence에 결합된다.

## 9. Deeplus다운 작성 관례

- 함수 값을 type alias로 공개할 때 error/effect row를 생략하지 않는다.
- capability를 context로 받고 effect row에도 실제 책임을 적는다.
- Result와 throws 중 한 오류의 owner를 하나로 정한다.
- Cancellation을 catchable Error의 편의 표현으로 바꾸지 않는다.
- callback API는 capture, ownership, effect와 error 책임을 끝까지
  전달한다.

## 10. 연습 문제

1. **따라 하기:** 순수 validator 함수 타입과 `{io}` loader 함수 타입을
   각각 작성한다.
2. **빈칸 완성:** `(String) -> Int throws ___ effects {}`에서 오류가 없는
   닫힌 ErrorSet을 채운다.
3. **스스로 설계하기:** named capability 하나와 이를 context로 받는
   effectful 함수를 설계하고 row와 authority의 차이를 설명한다.

## 11. 빠른 복습

- callable identity는 인수와 반환 타입만이 아니다.
- ErrorSet, EffectRow, capability는 서로 다른 역할이다.
- Cancellation과 Defect를 recoverable Error로 합치지 않는다.
- rest/context/witness/ownership 책임도 함수 타입에 남는다.

## 12. 정본 근거와 다음 장

- [function type](../../grammar-reference/04-types-generics-and-refinement.md)
- [error·effect·cancellation](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [타입 시스템 정본](../../../spec/types/type-system.md)

이제 [실습: typed parser와 guard 경계](lab-04-typed-parser-guard.md)에서
Result channel, refinement와 opaque guard를 함께 검증한다.
