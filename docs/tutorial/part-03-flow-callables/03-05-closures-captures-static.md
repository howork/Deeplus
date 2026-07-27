# 03-05. closure capture와 `static`

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **closure:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **function static activation:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 lambda/로컬 함수 capture와 이름 있는 동기 함수의
`static` activation을 분리해 설명한다.

## 2. 학습 목표

- lambda parameter와 capture list를 구분한다.
- 로컬 함수의 외부 이름 capture를 명시한다.
- `static`의 owner, 위치, 최초 호출 의미를 이해한다.
- 허용되지 않는 static owner와 activation failure 경계를 식별한다.

## 3. 선수 지식

앞 장의 named function body, function value와 effect/error row를 알고
있어야 한다.

### 미리 보는 최소 모델과 후속 심화

capture mode는 closure가 바깥 binding을 어떻게 사용할지 적는 계약이다.
`borrow`는 읽는 동안 owner를 빌리고 `move`는 closure 쪽으로 책임을
옮긴다는 최소 직관만 여기서 사용한다. place state, lifetime, escape와
consume의 정확한 증명은 Part 7에서 심화한다. 이 장의 목표는 ownership을
이미 안다고 가정하는 것이 아니라 implicit capture를 피하고 mode가
callable identity에 남는다는 사실을 먼저 익히는 것이다.

## 4. 문제에서 출발하기

closure가 바깥 변수를 암묵적으로 붙잡으면 lifetime과 mutation 책임이
보이지 않는다. 반대로 함수별 한 번 초기화를 module global로 흉내 내면
generic specialization, override, runtime instance별 identity가
무너진다. Deeplus는 capture list와 `static` prologue를 각각
명시적인 구조로 둔다.

## 5. 핵심 모델

- lambda는 `[capture] #profile { parameters => body }` 형태다.
- 명시적 nullary lambda는 `{ => body }`다.
- 단일 expression body가 lambda 결과이며 multiline 결과에는 `ret`를
  사용한다.
- 로컬 함수가 outer local을 쓰려면 `[borrow x] def inner...`처럼 적는다.
- `static { ... }`은 허용된 이름 있는 동기 함수 body에 최대 하나다.
- optional import/use 뒤, 첫 runtime semantic item 앞에 놓인다.
- 최종 구현이 실제 호출될 때 해당 `FunctionStaticOwnerId`마다 최초 한
  번 activation된다.

## 6. 단계별 예제

capture mode를 lambda와 로컬 함수에서 분명히 적는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let offset: Int = 10
let addOffset = [borrow offset] { value: Int => value + offset }

private def#pure outer(base: Int) -> Int
    throws Never
    effects {}
= {
    [borrow base] def inner(step: Int) -> Int = {
        return base + step
    }

    return inner(2)
}
```

lambda capture와 local function capture 모두 outer name 사용을 source에
남긴다. `[move token] #once { ... }`처럼 ownership과 callable profile을
함께 표현할 수도 있다.

function static activation은 capture가 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def decode(bytes: Bytes) -> Packet
    throws DecodeError
    effects {}
= {
    static {
        verifyDecoderTables()
    }

    return decodePacket(bytes)
}
```

인수 평가와 최종 callable 선택이 이루어진 뒤 activation barrier를
통과한다. 이 block은 persistent local value를 선언하는 표면이 아니라
owner별 activation 작업을 표현한다.

이전 철자 `scope#static { ... }`은
`FUNCTION_STATIC_SCOPE_HASH_DEPRECATED_USE_STATIC` migration 진단을 위한
recovery-only 표면이다. Block의 의미를 바꾸지 않고 `static`으로
치환하며, 두 철자는 migration 비교에서 같은 activation HIR와
`FunctionStaticOwnerId`를 뜻한다.

`static#slot name` persistent slot과 `static#slot::name` 참조는 별도
`PREVIEW_DESIGN_NONACTIVATABLE` 설계다. 아직 current parser 문법이 아니며
plain `let`/`var`는 계속 activation-local binding이다. 이 분리 덕분에
기존 activation code가 암묵적인 shared value로 바뀌지 않는다.

### 판정 trace, 미니 사례와 흔한 오해

closure를 판정할 때 capture list의 각 이름을 outer binding에 resolve하고
mode와 lifetime이 body 사용에 맞는지 확인한다. parameter와 capture를
분리한 뒤 callable profile, result, error/effect를 검사한다.
`static`은 이 trace와 별도로 owning named synchronous implementation,
prologue 위치, owner identity, 최초 activation barrier를 판정한다.

미니 사례에서 `[borrow rate] { value => value * rate }`는 rate를 parameter로
받지 않고 명시적으로 빌린다. 반면 `static` block은 값을 capture해
closure에 저장하는 표면이 아니다. 흔한 오해는 둘 다 “함수가 값을
기억한다”고 합치는 것이다. capture는 callable value 환경, activation은
허용된 named implementation의 once barrier이며 owner와 실패 법칙이
다르다. 이 장의 두 표면은 모두 CURRENT이고 제품은 `NOT_RUN`이다.

## 7. 허용·거부·경계 사례

implicit local capture와 허용되지 않은 owner의 static activation은
거부한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostics: NESTED_DEF_CAPTURE_LIST_REQUIRED, FUNCTION_STATIC_ACTIVATION_CALLABLE_KIND_NOT_ADMITTED -->
```deeplus
private def outer(base: Int) -> Int = {
    def inner(step: Int) -> Int = {
        return base + step
    }
    return inner(1)
}

let bad = { value: Int =>
    static {
        prepare()
    }
    value
}
```

첫 함수에는 `[borrow base]` 같은 capture contract가 없고, 두 번째는
lambda 안에 `static`을 놓았다. local function, lambda, async,
generator, guard, constructor, cleanup과 actor handler는 최초 Stable
owner matrix에서 static activation을 소유하지 않는다.

## 8. 다른 기능과의 연결

capture mode는 borrow/move/lifetime과 callable identity에 연결된다.
`#once` closure는 한 번 소비되는 callable 책임을 표현한다.
`static` owner identity는 selected implementation, generic
substitution, witness/helper digest와 runtime instance를 결합하며
inline/JIT clone이 새로운 source owner를 만들지는 않는다.

## 9. Deeplus다운 작성 관례

- 외부 값을 쓰는 closure와 local function은 capture를 항상 명시한다.
- 읽기만 하면 `borrow`, 소유 이전이면 `move`처럼 책임을 정확히 고른다.
- nullary lambda도 `{ => ... }`로 arrow를 생략하지 않는다.
- 함수별 activation과 module/type initialization을 같은 것으로 설명하지
  않는다.
- `static`은 prologue의 정해진 위치에 하나만 둔다.

## 10. 연습 문제

1. **따라 하기:** `borrow factor`를 capture해 값을 곱하는 lambda를 쓴다.
2. **빈칸 완성:** `[___ token] #once { value => consume(token, value) }`에서
   소유권 이전 mode를 채운다.
3. **스스로 설계하기:** decoder 함수에 static 검증 prologue를 설계하고,
   왜 lambda나 async 함수에 둘 수 없는지 설명한다.

## 11. 빠른 복습

- capture list와 parameter list는 역할이 다르다.
- 로컬 함수도 outer local 사용을 명시적으로 capture한다.
- `static`은 허용된 이름 있는 동기 구현의 activation prologue다.
- activation은 global value나 compile/JIT 시점 실행이 아니다.

## 12. 정본 근거와 다음 장

- [capture와 function static](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [ownership과 evaluation](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [function static 계약](../../../spec/contracts/function-static-activation.json)
- [function static namespace Preview 계약](../../../spec/contracts/function-static-namespace-preview-design.json)

이제 [실습: 검증 파이프라인](lab-03-validation-pipeline.md)에서 함수,
lambda, control과 Result를 한 흐름으로 묶는다.
