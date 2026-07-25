# 09-02 — effects, throws, Result와 capability

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이 장은 signature의 정적 책임을 설명한다. 실제 I/O provider와 runtime
호출은 검증되지 않았다.

## 2. 학습 목표

- `effects`, `throws`, `Result`의 서로 다른 질문을 구분한다.
- effect row와 effect를 수행할 capability를 분리한다.
- context parameter가 ambient authority를 막는 방식을 이해한다.
- callable compatibility가 이 축을 보존하는 이유를 설명한다.

## 3. 선수 지식

09-01의 네 실패 축, context parameter, 함수 signature를 알고 있어야 한다.

## 4. 문제에서 출발하기

`effects {io}`는 “이 함수가 I/O를 관찰 가능하게 수행한다”는 설명이다.
그 문구 자체가 파일을 읽을 권한을 만들어 주지는 않는다. 반대로
`FileIO` capability를 가진 값이 있다고 해서 함수가 실제로 I/O를 했다는
증거도 아니다. Deeplus는 설명과 권한을 함께, 그러나 별도 축으로 쓴다.

## 5. 핵심 모델

- `effects R`: 성공·실패 어느 경로에서든 관찰될 수 있는 effect row.
- `throws E`: 호출 경계를 벗어날 recoverable ErrorSet.
- `Result<T,error D>`: 성공값 `T` 안에서 분해할 domain failure `D`.
- `context cap: Capability`: 해당 operation을 수행할 명시적 authority.
- Cancellation/suspension: 위 세 줄에 숨기지 않는 별도 책임.

한 operation의 동일한 recoverable error family를 Result와 throws에 동시에
넣지 않는다. callable overload도 return type, effect/error row만으로
애매한 승자를 고르지 않는다.

## 6. 단계별 예제

capability 선언은 nominal non-value identity를 만들 뿐 global 권한을
합성하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public capability FileIO for {io}

def load(path: String, context files: FileIO) -> Bytes
    throws IOError
    effects {io}
= {
    return readFile(path, context files)
}
```

pure parsing은 권한과 I/O effect가 필요 없다. domain failure를 값으로
돌려준다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def parsePort(text: String) -> Result<Int, error PortError>
    throws Never
    effects {}
= {
    return parsePortValue(text)
}
```

이 둘을 조합하는 함수는 외부 I/O Error와 내부 Result를 모두 보존한다.

## 7. 허용·거부·경계 사례

허용: explicit context channel과 effect row를 함께 보존한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def loadPort(path: String, context files: FileIO)
    -> Result<Int, error PortError>
    throws IOError
    effects {io}
= {
    let text = decodeUtf8(load(path, context files))
    return parsePort(text)
}
```

거부: effect 이름만 적고 capability를 ambient하게 찾는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
def hiddenRead(path: String) -> Bytes
    throws IOError
    effects {io}
= {
    return readFile(path)
}
// 필요한 capability channel이 없다.
```

경계: `#pure` callable은 `throws Never`, `effects {}`이고 suspension,
authority, mutable/resource capture가 없어야 한다. signature만 비워 놓고
body에서 effectful helper를 부르면 pure가 되지 않는다.

## 8. 다른 기능과의 연결

- context argument는 ordinary positional/named argument와 다른 channel이다.
- actor나 service value도 명시적 runtime owner이며 type name에서 singleton을
  합성하지 않는다.
- HIR-H1은 selected capability와 effect/error rows를 typed residue로
  고정한다.
- cleanup failure는 body의 primary failure를 덮지 않고 suppressed 순서를
  보존한다.

### 판정 추적

`loadPort`를 검사할 때 checker는 먼저 `files`가 요구 capability와
일치하는지 결합한다. 이어 호출된 operation의 `{io}`가 선언된 effect
row의 부분집합인지, `IOError`가 현재 body에서 처리되거나 `throws`에
남는지, `parsePort`의 domain failure가 반환 `Result`에 보존되는지를
차례로 확인한다. 네 검사는 서로 대신할 수 없고, 하나라도 빠지면
signature 책임이 닫히지 않는다.

미니 사례로 memory cache hit 경로는 pure helper가 값을 돌려줄 수 있다.
cache miss 경로가 network adapter를 호출한다면 그 바깥 callable에는
network capability와 `effects {network}`, transport ErrorSet이 여전히
필요하다. “대부분 pure”라는 통계는 정적 effect row를 줄이지 않는다.

### 흔한 오해

`effects {io}`를 적으면 파일 권한이 생긴다고 생각하거나, capability
값을 받았으니 effect 표기를 생략해도 된다고 생각하기 쉽다. 전자는
관찰 설명을 권한으로, 후자는 권한을 실제 관찰로 바꾼 오류다. 또한
`throws Never`는 body가 임의의 Error를 삼켜도 된다는 뜻이 아니라,
모든 recoverable residual이 값으로 처리되거나 존재하지 않음을
증명해야 한다는 뜻이다.

## 9. Deeplus다운 작성 관례

signature를 “함수 이름과 값 type”으로만 보지 않는다. 값 channel,
authority, effects, errors, cancellation, suspension, ownership을 하나의
책임 계약으로 읽는다. 권한을 숨기지 않되 effect row와 같은 것으로
취급하지 않는다.

## 10. 연습 문제

1. **따라 하기:** `NetworkIO for {network}` capability와 이를 context로
   받는 `fetch` signature를 작성하라.
2. **빈칸 완성:** decoding은 `Result`, transport는 `throws`로 남기는
   `fetchConfig`의 반환형과 ErrorSet을 채워라.
3. **스스로 설계하기:** cache 조회가 pure이고 cache miss 때만 network를
   쓰는 API를 두 함수로 나누어 authority가 드러나게 설계하라.

## 11. 빠른 복습

- effect row는 설명이고 capability는 권한이다.
- Result와 throws는 서로 다른 failure channel이다.
- `#pure`는 signature와 body 책임을 모두 제한한다.
- context/witness/value channel을 서로 대체하지 않는다.

## 12. 정본 근거와 다음 장

- [효과·오류 참조](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [callable 책임](../../../spec/contracts/type-flow-callable-coherence.json)
- [타입 시스템](../../../spec/types/type-system.md)

다음 장에서는 Error를 처리하는 statement `try`와 값을 만드는 `@try`를
비교한다.
