# Lab 09 — 회복 가능한 import pipeline

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이 실습은 외부 bytes 획득과 domain parsing, 검증, cleanup을 분리한다.
`FileStore`, `ImportRow`, `ImportError`는 실습 application이 정의했다고
가정한 ordinary identity다. canonical console이나 실제 file runtime을
주장하지 않는다.

## 목표

- transport Error와 parse Result를 분리한다.
- effect와 capability를 signature에 드러낸다.
- `@try` fallback과 `finally` cleanup을 추적한다.
- 실패 전후의 owner와 publish 지점을 설명한다.

## 준비

09-01부터 09-05까지 읽고 `Result::ok/err`, context parameter, `defer`,
`@try`를 복습한다.

### 누적 프로젝트 연결

| 연결 | 이 실습에서 이어 받거나 넘기는 것 |
|---|---|
| input | 앞 Part에서 만든 typed row와 pattern 검증 규칙을 import 입력 모델로 받는다. |
| output | transport Error, domain Result, cleanup event, publish commit을 분리한 pipeline 책임표를 만든다. |
| next | Part 10에서 이 pipeline을 bounded worker에 넣고 admission·Cancellation owner를 추가한다. |

먼저 성공 경로만 그리지 말고 다섯 terminal을 적는다. 파일 획득 실패,
decode 값 실패, 검증 실패, Cancellation, cleanup 실패가 각각 어느
channel을 쓰는지 표시한다. 각 terminal에서 lease owner가 남아 있는지,
row collection이 아직 local인지, 외부 catalog에 publish되었는지도 함께
기록한다. 이 표가 코드보다 먼저 있어야 fallback이 실수로 domain 오류를
삼키지 않는다.

## 단계별 구현

### 1단계 — pure decoder

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum ImportError {
    malformed(row: Int)
    duplicate(key: String)
}

def decodeRows(bytes: Bytes) -> Result<List<ImportRow>, error ImportError>
    throws Never
    effects {}
= {
    return parseRows(bytes)
}
```

decoder는 filesystem authority를 받지 않는다. malformed input은 값
failure다.

### 2단계 — 외부 획득 경계

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public capability ImportIO for {io}

def loadRows(path: String, context store: ImportIO)
    -> Result<List<ImportRow>, error ImportError>
    throws IOError
    effects {io}
= {
    let bytes = readImportFile(path, context store)
    return decodeRows(bytes)
}
```

transport는 throws, parsing은 Result에 남는다.

### 3단계 — fallback과 cleanup

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def importOrEmpty(path: String, context store: ImportIO)
    -> Result<List<ImportRow>, error ImportError>
    throws Never
    effects {io}
= {
    return @try {
        loadRows(path, context store)
    } catch error {
        Result<List<ImportRow>, error ImportError>::ok([])
    } finally {
        releaseImportLease(path)
    }
}
```

이 설명용 정책은 `IOError`만 empty 결과로 회복한다. parse error를
자동으로 삼키지 않으며 finally는 결과를 만들지 않는다.

### 4단계 — 검증과 단일 publish commit

`Result::ok(rows)` 뒤에도 곧바로 shared catalog를 갱신하지 않는다. 모든
row의 key refinement, duplicate policy와 referential constraint를 local
collection에서 끝낸 다음 한 번의 named publish operation을 호출한다.
검증 중 실패하면 외부 관찰 상태는 그대로이고 local owner만 cleanup된다.
publish가 시작된 뒤의 실패는 같은 입력을 단순 재시도해도 안전하다고
가정하지 말고 application transaction identity로 구분한다.

판정 trace는 `capability 결합 → read effect/error → decode Result →
row 검증 → publish commit → cleanup` 순서다. 각 화살표에서 owner,
ErrorSet, effect row를 한 줄씩 적으면 “I/O가 끝났으니 이후는 모두
pure” 같은 오해를 막을 수 있다. publish adapter가 I/O를 수행한다면
마지막 단계에도 해당 effect와 authority가 남는다.

## 중간 점검

- `decodeRows`에 `effects {io}`가 없는가?
- `loadRows`가 context capability와 effect를 모두 표시하는가?
- `ImportError`가 throws에도 중복되지 않는가?
- publish 전에 모든 row가 검증되는가?
- body가 실패하고 lease release도 실패할 때 body가 primary로 남는가?
- Cancellation 뒤 partial row가 외부에 관찰되지 않는가?

## 실패 실험

bare try와 block defer는 거부된다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
try {
    loadRows(path, context store)
}
defer {
    releaseImportLease(path)
}
```

첫 조각에는 handler/finally가 없고, 두 번째 조각은 단일 cleanup
invocation이 아니다.

또 하나의 실패 실험은 decode 오류를 transport catch에서 empty list로
바꾸는 것이다. 그렇게 하면 손상된 입력과 “파일 없음”이 같은 관찰값이
되어 호출자가 재시도·신고 정책을 선택할 수 없다. 흔한 오해는
`throws Never`를 만들면 API가 더 안전하다고 보는 것이다. 실패 identity를
지운 signature는 단순해 보여도 책임 계약은 오히려 불완전할 수 있다.

실습 보고서에는 최소 세 trace를 나란히 둔다. 정상 입력은 read, decode,
validate, publish, release를 모두 지난다. malformed 입력은 publish
전에 멈추고 `ImportError` 값을 보존한 뒤 release한다. transport 실패는
decode를 시작하지 않고 `IOError`를 전파한 뒤 release한다. 각 trace에서
동일한 cleanup이 한 번만 등장하는지와 외부 catalog 변경이 성공 trace에만
있는지를 확인한다. 실행 순서를 임의 로그 문자열로 비교하지 말고
operation identity와 commit 여부로 적는다.

이 표를 작성하면 fallback이 적용되는 정확한 residual도 보인다. 이
예제의 empty fallback은 `IOError` 정책일 뿐 모든 `ImportError`,
Cancellation, Defect를 회복시키는 catch-all이 아니다.

## 확장 과제

1. **따라 하기:** `decodeRows`의 Result를 explicit pattern으로 풀어라.
2. **빈칸 완성:** `loadRows`의 `throws ___`, `effects ___`,
   `context ___`를 채워라.
3. **스스로 설계하기:** duplicate row만 보고서로 수집하고 malformed
   row는 전체 import를 실패시키는 policy를 별도 값 type으로 설계하라.
4. **경계 분석:** Cancellation이 import 중 관측될 때 cleanup과 partial
   publication이 어떻게 되어야 하는지 event 순서를 적어라.

## 완료 체크리스트

- [ ] 값 실패, Error, Defect, Cancellation을 섞지 않았다.
- [ ] effect와 capability를 둘 다 드러냈다.
- [ ] `try`와 `@try`의 owner를 구분했다.
- [ ] cleanup이 모든 terminal path에서 한 번 실행된다.
- [ ] static 설명을 runtime PASS로 표현하지 않았다.

## 정본 근거

- [오류·효과·cleanup](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [callable coherence](../../../spec/contracts/type-flow-callable-coherence.json)
- [MIR cleanup](../../../spec/mir/semantics.md)
