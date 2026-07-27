# 5.1 Record, Tuple, Map, schema

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

이 장의 값·타입 표면은 현행 정본이다. 예제의 결과는 정적 설계가 정한
의미이며 제품 실행 영수증이 아니다. 특히 `${...}`, `#map{...}`,
`Type${...}`를 중괄호가 비슷하다는 이유로 같은 값으로 읽지 않는다.

## 2. 학습 목표

- Tuple의 위치 identity와 Record의 label identity를 구분한다.
- Map의 runtime key가 Record label이 될 수 없는 이유를 설명한다.
- schema declaration과 typed materialization을 사용한다.
- field pun, named unfold, 평가 순서와 failure atomicity를 이해한다.

## 3. 선수 지식

`let`, 기본 타입, 함수 호출, named argument `name: value`를 알고 있어야
한다. index의 첫 위치가 `1`이라는 규칙은 다음 부에서도 계속 사용한다.

## 4. 문제에서 출발하기

사용자 한 명을 `(13, "Ada")`로 표현하면 짧지만 첫 값과 둘째 값의 뜻을
기억해야 한다. `${id: 13, name: "Ada"}`는 label이 뜻을 보존한다.
반면 서버 설정처럼 key가 실행 중에 결정되면 `Map`이 알맞다. 그리고
필수 필드와 기본값까지 공개 계약으로 고정하려면 schema가 필요하다.

## 5. 핵심 모델

| 모델 | identity | 선택 | 대표 용도 |
|---|---|---|---|
| Tuple | 정적 위치 `.1`부터 `.arity` | compile-time ordinal | 작고 지역적인 다중 결과 |
| Record | 정적 identifier label | field/label projection | 구조적 payload와 named unfold |
| `Map<K,V>` | runtime `K` value | `map[key]` | 동적 사전과 lookup |
| schema | 선언된 field row와 authority | `Type${...}` | 검증된 외부 row와 DTO |

Record의 canonical label order는 API identity와 digest를 위한 것이다.
field expression은 소스에 적힌 순서대로 정확히 한 번 평가된다. Map도
key 다음 value를 소스 순서로 평가하지만, 그 key는 문자열을 포함한 실제
값이며 compile-time label이 아니다.

## 6. 단계별 예제

### 깊이 읽기: 모양보다 identity owner를 먼저 고르기

세 자료형을 고를 때 중괄호나 괄호의 모양부터 비교하면 판단이 흔들린다.
먼저 프로그램이 무엇을 안정적으로 기억해야 하는지 묻는다. “첫 번째와
두 번째”처럼 위치가 계약이면 Tuple, `name`과 `active`처럼 고정 label이
계약이면 Record, 실행 중 들어오는 key가 계약이면 Map이다. schema는
Record와 비슷한 label을 사용하지만 선언된 이름과 materialization
경계까지 포함하는 별도 authority다.

판정은 네 단계로 진행한다. 요구 identity가 위치·정적 label·runtime key
중 무엇인지 닫고, 각 component의 type과 가시성을 확인한다. 이어 child
expression을 source order로 한 번씩 평가하고 모든 검사와 변환이
성공했을 때 aggregate를 한 번 publish한다. 중간 child가 실패하면 앞서
계산한 임시 값을 정리하지만 부분 Tuple·Record·Map은 보이지 않는다.

작은 trace로 `${name: loadName(), active: loadFlag()}`를 보자.
`loadName()`이 성공하고 `loadFlag()`가 실패해도 `name`만 든 Record가
남지 않는다. formation 전체가 실패하고 첫 임시 결과의 책임을 정리한다.
schema default가 있더라도 required field와 constraint 검사는 생략되지
않는다.

흔한 오해는 Record를 문자열 key만 쓰는 빠른 Map으로 보는 것이다.
Record label은 resolver가 아는 정적 identity라 임의 String expression과
교체할 수 없다. 반대로 Map key는 runtime 값이므로 field pun이나 named
unfold 증거가 되지 않는다. 변환이 필요하면 누락·중복·평가 순서를
드러내는 명시적 adapter를 설계한다.

### 6.1 위치와 label을 선택한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let pair = (13, "Ada")
let id = pair.1
let name = pair.2

let profile = ${
    id: 13
    name: "Ada"
}
let profileName = profile.name
```

Tuple의 `.1`, `.2`는 1-based static ordinal이다. Record의 `.name`은
runtime String lookup이 아니라 정적 label projection이다. 둘 다
immutable owned default지만 identity가 서로 다르다.

### 6.2 schema로 construction row를 닫는다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public schema UserRow {
    id: Int
    name: String
    active: Bool = true
}

let id = 13
let name = "Ada"
let row = UserRow${
    id
    name
}
```

field pun `id`는 `id: id`로, `name`은 `name: name`으로 정규화된다.
각 lexical binding은 한 번만 읽힌다. `active`는 schema가 소유한 기본값으로
채워진다. 모든 field가 성공해야 `row`가 한 번 publish된다.

### 6.3 Map unfold와 Record unfold를 구별한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let defaults = #map{
    "host": "localhost"
    "port": "80"
}
let production = #map{
    **defaults
    "port": "443"
}

let request = ${ id: 13, active: true }
send(**request)
```

첫 `**defaults`는 같은 `K,V` domain의 Map entry를 펼친다. 뒤의 `"port"`
entry가 앞 값을 대체하며 displaced owner는 한 번 정리된다.
`send(**request)`의 `**request`는 정적 Record label을 named argument로
공급한다. 같은 glyph라도 parser owner와 lowering이 다르다.

## 7. 허용·거부·경계 사례

허용:

- `${ id, name }` field pun
- `Target${ id: value }` typed materialization
- `#map{ **base, key: value }` 같은 exact-domain Map unfold
- Tuple의 static `.1` projection

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: MAP_NAMED_ARGUMENT_UNFOLD_REJECTED; product: NOT_RUN -->
```deeplus
let options = #map{ "timeout": 30 }
configure(**options)
// MAP_NAMED_ARGUMENT_UNFOLD_REJECTED
```

runtime key `"timeout"`은 static label `timeout`이 아니다. schema에 없는
field는 `TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD`, ordinary Class에 `${...}`를
constructor alias처럼 쓰면
`TYPE_SCHEMA_CONSTRUCTION_REQUIRES_SCHEMA_AUTHORITY`다.

경계:

- `source!{ field: value }`와 `source!!{...}`는 같은 명목 타입의
  shallow/deep derivation이며 `${...}`와 다르다.
- Record row는 canonical order를 갖지만 evaluation order는 source order다.
- Map의 없는 key는 sentinel이 아니라 `IndexError::keyNotFound`다.

## 8. 다른 기능과의 연결

Record는 named-rest `Record***`, schema materialization, 그리고 call에
명시적으로 전달하는 하나의 Record expression과 연결된다. Named message
arguments는 ordered call labels이지 자동 생성된 Record가 아니다.
Pattern의 `${name}`은 Record value literal이 아니라 별도 parser goal이다.
Class constructor와 schema construction의 차이는 다음 장에서 다룬다.

## 9. Deeplus다운 작성 관례

- 위치 자체가 의미일 때만 Tuple을 쓴다.
- 공개 경계에서는 label이 의미를 설명하도록 Record나 schema를 선호한다.
- 동적 key가 정말 필요할 때만 Map을 쓴다.
- Map을 Record처럼, Record를 Map처럼 보이게 하는 helper를 만들지 않는다.
- 실패할 수 있는 field를 먼저 평가해도 partial aggregate가 publish되지
  않는다는 transaction 법칙을 API 설명에 명시한다.

## 10. 연습 문제

1. **복사:** `UserRow` 예제를 그대로 쓰고 `email: String` 필드를 추가하라.
2. **빈칸 완성:** `let pair = (width, height)`와
   `let row = ${___, ___}`의 빈칸을 채우고 `.1`과 `.width` 선택 차이를
   적어라.
3. **설계:** runtime locale key를 가진 번역 사전과 고정된 API 응답 row를
   각각 Map/schema 중 어디에 둘지 결정하고 failure atomicity를 설명하라.

## 11. 빠른 복습

- Tuple은 위치, Record는 정적 label, Map은 runtime key다.
- schema는 construction authority를 선언한다.
- `${...}`와 `#map{...}`는 서로 변환되지 않는다.
- aggregate는 모든 검사가 성공한 뒤 한 번 commit된다.
- product lanes는 `15/15 NOT_RUN`이다.

## 12. 정본 근거와 다음 장

- [언어 명세 §23~24](../../../spec/language.md)
- [정확한 문법](../../../spec/grammar/deeplus.ebnf)
- [Enum·Record·schema 레퍼런스](../../grammar-reference/07-enums-records-schemas-bitfields-and-units.md)
- [컬렉션 레퍼런스](../../grammar-reference/09-collections-indexing-and-slicing.md)

다음 장에서는 구조적 row와 달리 명목 identity·생성 책임을 소유하는
Class와 data class를 배운다.
