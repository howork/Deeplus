# 09-01 — Error, Defect, Cancellation과 값 실패

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이 장의 “발생한다”와 “전파한다”는 현행 설계의 관찰 법칙을 뜻한다.
runtime 실행이 확인되었다는 뜻은 아니다.

## 2. 학습 목표

- recoverable `Error`와 intrinsic `Defect`를 구분한다.
- `Result<T, error E>`와 `throws E`의 위치를 설명한다.
- Cancellation이 ErrorSet 밖에 있는 이유를 설명한다.
- 실패 이전의 owner와 commit 상태를 추적한다.

## 3. 선수 지식

함수 signature, `Option`과 `Result`, Enum pattern, `return`과 `throw`를
알고 있어야 한다.

## 4. 문제에서 출발하기

파일을 읽지 못한 상황은 호출자가 다른 경로를 선택할 수 있다. 반면
정수 overflow나 0으로 나눈 상황은 그 연산의 정적·동적 불변식이
무너진 것이다. 작업 취소는 실패 값도 계산 결함도 아니며, 구조화된
scope가 중단을 요청한 별도 제어 결과다. 세 상황을 같은 catch 목록으로
보내면 cleanup과 API 호환성을 정확히 설명할 수 없다.

## 5. 핵심 모델

| 축 | 예 | 소유자 | 일반 처리 |
|---|---|---|---|
| 값 실패 | `Result<T, error E>` | 반환값 | pattern/match |
| recoverable Error | `throws E` | callable 경계 | `try`/`catch` 또는 전파 |
| Defect | `ArithmeticDefect` | intrinsic 불변식 | catch 대상 아님 |
| Cancellation | task/scope 제어 | 구조화된 동시성 owner | cleanup 후 별도 종료 |

`ArithmeticDefect`는 checked integer overflow, 정수 0 나눗셈 같은
intrinsic family다. `IndexError`는 recoverable family다. 이름이 “오류”
처럼 들리는지가 아니라 정본 identity가 어느 축에 속하는지가 중요하다.

## 6. 단계별 예제

값을 해석하지 못한 경우를 결과 안에 남기면 호출자는 정상 값처럼
분해할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum DecodeError {
    malformed
    unsupported(version: Int)
}

def decodeHeader(bytes: Bytes) -> Result<Header, error DecodeError>
= {
    return parseHeader(bytes)
}
```

반면 저장소에서 bytes를 얻지 못하는 일은 callable 경계를 벗어나는
recoverable Error로 선언할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def loadHeader(path: String, context files: FileStore)
    -> Result<Header, error DecodeError>
    throws IOError
    effects io
= {
    let bytes = files.read(path)
    return decodeHeader(bytes)
}
```

정적 판정 순서는 capability와 effect 확인, `files.read`의 ErrorSet 확인,
`decodeHeader` 결과 type 확인, 반환 channel 확인이다. 어느 단계도
`IOError`를 `DecodeError` case로 자동 변환하지 않는다.

## 7. 허용·거부·경계 사례

허용: Result의 두 대안을 명시적으로 분해한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let Result::ok(header) = decodeHeader(bytes)
else Result::err(error) => return error
useHeader(header)
```

거부 경계: Defect를 recoverable Error처럼 catch하려 한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
try {
    let quotient = numerator / denominator
    consume(quotient)
} catch ArithmeticDefect {
    recover()
}
// Defect는 ErrorSet residual이 아니므로 catch dispatch에 들어가지 않는다.
```

또 다른 경계는 Cancellation이다. `catch Cancellation`으로 정상값을
만들거나 `ActorMessageError`로 접으면 cancellation/cleanup identity가
사라져 거부된다.

## 8. 다른 기능과의 연결

- pattern matching은 Result 값을 분해하지만 throws channel을 자동
  소비하지 않는다.
- actor request는 admission Error와 reply task의 Error를 commit 전후로
  나눈다.
- `defer`와 resource cleanup은 네 terminal 축에서 실행되어야 한다.
- public API digest는 ErrorSet, Cancellation, suspension을 별도 field로
  보존한다.

### 판정 추적

한 실패를 보았을 때 먼저 “호출자가 이 상황을 정상적인 대안으로
분해하는가?”를 묻는다. 그렇다면 `Result` 값 후보다. 그 다음 “현재
callable이 회복하지 못해 호출 경계를 벗어나는가?”를 물어 `throws`
residual을 정한다. 연산 자체의 불변식이 무너졌다면 Defect이고, 바깥
task scope가 중단을 요청했다면 Cancellation이다. 마지막으로 commit
이전인지 이후인지 확인해야 owner와 재시도 가능성을 판정할 수 있다.

미니 사례로 설정 파일 읽기는 `IOError`를 `throws`에, 읽은 text의
형식 오류를 `Result<Config,error ParseError>`에 둘 수 있다. 정수
나눗셈의 0 제수는 이 둘로 자동 변환하지 않으며, 작업 취소도
`ParseError::cancelled` 같은 case로 합치지 않는다.

### 흔한 오해

이름에 `Error`가 붙으면 모두 catch할 수 있다는 생각은 틀리다. 반대로
사용자에게 보여 줄 메시지가 있다는 이유만으로 모든 실패가 `Result`가
되는 것도 아니다. 표면 이름이 아니라 정본 failure identity, 회복 owner,
commit 시점을 함께 읽어야 한다.

## 9. Deeplus다운 작성 관례

회복 주체가 누구인지 먼저 묻는다. 호출자가 재시도·대체 경로를 선택할
수 있으면 `throws`; 실패가 도메인 데이터이면 `Result`; 프로그래머가
정상 분기로 위장하면 안 되는 intrinsic 불변식 실패이면 Defect다.
Cancellation은 이 분류에 억지로 넣지 않는다.

## 10. 연습 문제

1. **따라 하기:** `Result<Config, error ParseError>`를 반환하는
   `parseConfig` signature를 적고 `throws Never effects {}`를 붙여라.
2. **빈칸 완성:** 네트워크에서 text를 가져온 뒤 parsing하는 함수에서
   `NetworkError`와 `ParseError`를 각각 어느 channel에 둘지 채워라.
3. **스스로 설계하기:** 사용자 취소, mailbox admission 실패, handler
   domain error가 동시에 가능한 actor workflow의 세 축을 표로 그려라.

## 11. 빠른 복습

- Result는 값, throws는 callable control channel이다.
- Defect와 Cancellation은 ErrorSet member가 아니다.
- 같은 recoverable family를 Result와 throws 양쪽에 중복 노출하지 않는다.
- 실패 전 commit이 없었다면 owner와 원래 값은 보존되어야 한다.

## 12. 정본 근거와 다음 장

- [오류와 cleanup 참조](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [Prelude failure identity](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)
- [MIR failure semantics](../../../spec/mir/semantics.md)

다음 장에서는 실패 channel과 observable effect, 실행 권한을 signature에
결합한다.
