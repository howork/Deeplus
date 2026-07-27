# 5.4 패턴과 구조 분해

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. Pattern을 보는 관점

Deeplus의 Pattern은 값에서 몇 개의 항목을 편리하게 꺼내는 문법 설탕이
아니다. Pattern은 다음 질문에 대한 하나의 정적 계획이다.

1. subject를 어떤 구조로 관찰하는가?
2. 성공과 실패를 누가 처리하는가?
3. 어느 이름이 probe 단계에서 잠시 보이는가?
4. 어느 값이 최종적으로 move·borrow·bind되는가?
5. 실패했을 때 원래 owner와 지역 변수가 그대로 유지되는가?

모든 Pattern owner는 같은 AST를 사용하지만 실패 처리 방식은 다르다.
plain `let`과 함수 parameter는 성공이 정적으로 보장되어야 한다.
`if let`은 선택적인 분기이고, guarded `let`은 실패 시 현재 경로를
떠난다. `let!`은 실패를 명시적인 defect로 만든다.

## 2. Tuple과 bare product

괄호 하나만으로 Tuple이 되지는 않는다.

```deeplus
let grouped = (value)
let singleton = (value,)
let pair = (13, "Ada")
let id, name = pair
```

`(value)`는 grouping, `(value,)`는 1-Tuple이다. bare comma value,
return, binding과 지역 병렬 대입도 모두 Tuple로 정규화된다.

```deeplus
private def identity() -> Int, String = {
    return 13, "Ada"
}

let id, name = identity()
```

쉼표가 있다고 해서 임의의 `Sequence`를 분해하는 것은 아니다. 함수의
반환 type과 값, binding Pattern은 모두 같은 Tuple arity를 가져야 한다.

## 3. List rest를 방향으로 읽기

Sequence rest는 점의 위치가 방향을 나타낸다.

```deeplus
let [head, ..tail] = values
else return

if let [leadings.., last] = values {
    inspect(last)
}

if let [first, ..middle.., last] = values {
    inspect(first, middle, last)
}
```

- `..tail`: 뒤쪽 remainder
- `leadings..`: 앞쪽 remainder
- `..middle..`: 앞뒤 고정 child 사이의 remainder
- `.._`: remainder를 capture하지 않고 무시

한 Pattern에는 rest가 최대 하나다. `[.._]`도 유효하며 길이가 0인
List와 nonempty List를 모두 받아들인다.

borrowed List의 captured rest type은 `ListRestView<T>`다. 이 view는 원본
owner region과 1-based coordinate를 보존한다. 따라서 첫 remainder
항목의 coordinate를 무조건 1로 다시 쓰면 안 된다. 숨은 복사나 할당도
일어나지 않는다.

## 4. Record는 exact-by-default

다음 두 Pattern은 의미가 다르다.

```deeplus
let ${x, y} = exactPoint
let ${x, y, .._} = extensiblePoint
```

첫 Pattern은 field set이 정확히 `x`, `y`인지 확인한다. 둘째 Pattern은
두 field를 요구하되 추가 field를 명시적으로 허용한다. 나머지 Record가
필요하면 이름을 붙인다.

```deeplus
let ${x, y, ..metadata} = event
```

이 규칙은 schema가 바뀌었을 때 조용히 새 field를 무시할지, 재검토를
요구할지를 소스에서 선택하게 한다.

### 4.1 source field의 이름을 바꿔 받기

colon 왼쪽은 destination, 오른쪽은 source다.

```deeplus
let ${horizontal: x, vertical: y, .._} = point
```

`point.x`가 `horizontal`로, `point.y`가 `vertical`로 들어온다. nested
Pattern이나 typed destination은 괄호로 묶어 colon owner를 분명히 한다.

```deeplus
let ${(${city, zip}): address, .._} = user
let ${(userId: UserId): id, .._} = payload
```

## 5. Map Pattern

Map Pattern도 exact/open/rest를 명시하고 destination을 왼쪽에 둔다.

```deeplus
if let #map{
    userId: "id"
    displayName: "name"
    ..rest
} = payload {
    show(userId, displayName)
}
```

오른쪽 key에는 literal 또는 `^stableValue`만 쓴다. 함수 호출로 key를
만들거나 iteration order에서 원소 하나를 고르는 Pattern은 허용하지
않는다.

## 6. nominal product와 Enum payload

schema, data class와 명시적으로 transparent인 nominal product는 field
identity로 분해한다.

```deeplus
let Point${x, y} = point
let User${displayName: name, .._} = user
```

ordinary Class는 `sealed` 또는 `final`이어도 내부 field가 자동 공개되지
않는다. 데이터를 Pattern으로 공개하려면 transparent data carrier나
명시적인 Record view를 제공해야 한다.

Enum은 positional payload와 labeled payload를 구분한다.

```deeplus
let message = @match result {
    ::ok(value) => "ok: ${value}"
    ::error${message, code, .._} => "${code}: ${message}"
}
```

case identity를 확인하기 전에는 payload를 읽지 않는다. 성공 case의
active payload만 probe하고 최종 commit한다.

## 7. pin, range와 relational Pattern

이미 존재하는 stable value와 비교하려면 pin을 쓴다.

```deeplus
let expected = 200

match status {
    ^expected => report("expected")
    200..<300 => report("success")
    >= 500 => report("server error")
    otherwise => report("other")
}
```

`^expected`는 새 이름을 만드는 binder가 아니다. mutable place와
arbitrary call은 pin operand가 될 수 없다. range/relational Pattern은
`Int`, `UInt`, `Char`, ordered Enum처럼 닫힌 total-order domain에서
사용한다. Float range는 Preview다.

## 8. 실패 owner 선택

### 8.1 plain binding

```deeplus
let (x, y) = fixedPair
```

checker가 `fixedPair`의 Tuple arity를 알기 때문에 irrefutable이다.

### 8.2 guarded binding

```deeplus
let [head, ..tail] = values
else return
```

List가 비어 있으면 `else`가 실행되며 `head`와 `tail`은 만들어지지
않는다.

### 8.3 assertive binding

```deeplus
let! [head, ..tail] = protocolGuaranteedNonempty
```

호출자가 불변식을 assert하고 mismatch를 `PatternMatchDefect`로
처리한다. ordinary 입력 검증에는 guarded `let` 또는 `if let`이 더
알맞다.

### 8.4 condition chain

```deeplus
if let ::some(user) = lookup(id)
    and then let ${email, .._} = user.profile
    and then isVerified(email)
{
    publish(user)
}
```

뒤 condition은 앞 binder를 읽을 수 있다. 어느 단계든 실패하면 뒤
표현식은 평가하지 않고 tentative binding은 모두 폐기한다.

## 9. 함수와 lambda parameter Pattern

함수는 call channel 이름을 유지하면서 body-entry에서 irrefutable
구조를 분해할 수 있다.

```deeplus
private def distance(point Point${x, y}: Point) -> Float = {
    return sqrt(x ^ 2 + y ^ 2)
}
```

`point`는 call label과 whole-value local이다. Pattern은 overload identity
또는 외부 call shape를 바꾸지 않는다. refutable parameter Pattern은
거부한다.

lambda의 괄호도 arity를 분명히 한다.

```deeplus
let sumPair = { (x, y): (Int, Int) => x + y }
let add = { x: Int, y: Int => x + y }
```

첫째는 Tuple 하나, 둘째는 인수 두 개다.

## 10. refutable catch

catch는 Error를 순서대로 Pattern match한다.

```deeplus
try {
    loadConfiguration()
}
catch IOError${path, .._} if isConfigPath(path) {
    useDefaults(path)
}
catch error: IOError {
    throw error
}
```

첫 Pattern 또는 guard가 실패하면 다음 catch로 간다. 마지막까지 맞지
않은 recoverable Error는 바깥 error 경계로 전파된다. catch guard도
pure·nonthrowing·nonsuspending이어야 한다.

## 11. 실패 원자적인 지역 대입

```deeplus
var left = acquireLeft()
var right = acquireRight()
left, right = right, left
```

target place를 왼쪽부터 한 번 resolve하고 RHS를 한 번 평가한다. 모든
type, ownership, overlap 검사가 성공한 뒤에만 하나의 logical commit을
수행한다. `(left, left) = pair`처럼 target이 겹치거나 member/index/shared
target을 사용하는 형식은 Stable local assignment가 아니다.

## 12. transaction trace

refutable Pattern은 다음 순서로 동작한다.

1. subject를 한 번 평가한다.
2. 구조를 소비하지 않고 검사한다.
3. probe binder를 read-only로 노출한다.
4. guard가 있으면 한 번 평가한다.
5. 필요한 값과 owner를 private staging에 준비한다.
6. 성공할 때만 binding·move·borrow를 commit한다.

구조 실패, false guard 또는 staging 실패 전에는 partial binding, move,
exclusive borrow, assignment write와 authority 획득이 모두 0이다.

## 13. Preview와 Stable을 구분하기

다음 표면은 nonactivatable Preview로 보존된다. 별도 activation authority와
실행 증거 전에는 Stable source route를 만들지 않는다.

- And/Not Pattern
- `let? ... else ...`
- Set/NumericArray Pattern
- Pattern Synonym과 pure Pattern View
- completeness manifest와 find Pattern
- top-level destructuring
- member/index Pattern assignment
- Float range와 clone binder

Preview 예시는 설계를 이해하고 검토하기 위한 것이다. Stable source와
섞어 제품 지원을 주장하지 않는다.

## 14. 흔한 오류

```deeplus
if let [first, ..middle, last] = values {
    use(middle)
}
```

middle rest는 닫는 marker가 필요하므로 `..middle..`로 쓴다.

```deeplus
let ${x, y} = pointWithMetadata
```

추가 field를 허용하려는 의도라면 `${x, y, .._}`여야 한다.

```deeplus
private def first([head, .._]: List<Int>) -> Int = {
    return head
}
```

동적 List는 빈 값일 수 있어 parameter Pattern이 refutable하다. parameter
전체를 받고 guarded `let`으로 분해한다.

## 15. 연습 문제

1. **Sequence rest:** tail, prefix, middle rest를 각각 사용하는 guarded
   List Pattern을 작성하라.
2. **Record mapping:** `${localName: sourceName, .._}` 방향으로 payload
   Record를 분해하라.
3. **Map exactness:** `#map{value: "key", ..rest}` Pattern에서 exact와
   open의 차이를 설명하라.
4. **실패 처리:** `let!`을 guarded `let`으로 바꾸고 failure disposition
   차이를 적어라.
5. **Parameter 구조 분해:** 함수 Tuple parameter 하나와 ordinary
   parameter 둘을 받는 lambda를 각각 작성하라.

## 16. 빠른 복습

- Tuple과 bare comma product는 하나의 Tuple로 정규화된다.
- Sequence rest marker의 방향은 remainder 위치를 나타낸다.
- Record와 Map은 exact-by-default이고 destination이 colon 왼쪽이다.
- parameter Pattern은 irrefutable해야 한다.
- refutable catch는 다음 catch 또는 바깥 error 경계로 진행한다.
- 성공할 때만 binding과 ownership이 commit된다.

## 17. 정본 근거와 다음 장

- [Pattern 레퍼런스](../../grammar-reference/10-patterns-destructuring-and-matching.md)
- [Pattern 문법](../../../spec/grammar/deeplus.ebnf)
- [타입 시스템 Pattern 계약](../../../spec/types/type-system.md)
- [MIR 평가 법칙](../../../spec/mir/semantics.md)

다음 장에서는 coverage, guard와 transaction을 더 깊게 연결한다.
