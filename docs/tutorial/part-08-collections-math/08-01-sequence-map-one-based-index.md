# 8.1 Sequence, Map과 1-based index

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

List, Set, Map, String, Bytes와 닫힌 built-in bracket carrier matrix는 현행
정본이다. value literal과 nonactivatable type-position sugar를 섞지 않는다.

## 2. 학습 목표

- List와 Map의 index domain을 구분한다.
- ordinary ordered value의 첫 index `1`을 사용한다.
- bounded List의 declared coordinate를 이해한다.
- Sequence evidence와 bracket capability를 분리한다.

## 3. 선수 지식

List/Map literal, exact type, IndexError의 기초가 필요하다.

## 4. 문제에서 출발하기

세 이름 중 첫 이름을 읽을 때 storage offset `0`을 노출하면 사용자가 보는
순서와 구현 배열의 주소 계산이 섞인다. Deeplus의 ordinary logical
coordinate는 `1..length`이고 backend offset은 별도 `index - 1` projection이다.

## 5. 핵심 모델

| carrier | index domain | 결과 |
|---|---|---|
| `List<T>` | `1..length` | read-only `T` |
| `String` | `1..UnicodeScalarCount` | `Char` |
| `Bytes` | `1..byteCount` | `UInt8` |
| bounded List | 선언 `L..U` | read-only element |
| `Map<K,V>` | exact `K` | `V` 또는 keyNotFound |
| NumericArray | axis별 `1..dimension` | element/view |

Set은 bracket이 없고 iteration order가 semantic API가 아니다. Tuple은
static `.1`, Record는 static label로 선택한다.

## 6. 단계별 예제

### 깊이 읽기: carrier, coordinate, offset을 분리한다

index 식을 읽을 때에는 세 identity를 한꺼번에 숫자 하나로 줄이지 않는다.
첫째는 `List`, bounded List, `Map`, `String`, `Bytes`, NumericArray 중
어느 carrier인가이다. 둘째는 그 carrier가 공개하는 logical coordinate
domain이다. 셋째는 구현이 내부에서 사용할 수 있는 storage offset이다.
ordinary List의 coordinate `1`이 내부 offset `0`에 대응할 수 있지만,
offset은 source contract가 아니며 프로그램이 관찰하거나 전달하는 값도
아니다. bounded List `10..12`의 첫 coordinate는 여전히 `10`이다.

판단 순서는 고정하면 쉽다. owner 식을 한 번 평가하고, index 식을 한 번
평가한 뒤, carrier별 domain에서 membership을 검사한다. 성공한 경우에만
backend projection과 element read를 수행한다. 실패하면 element access나
부분 mutation 없이 `IndexError` 경계로 나간다. `Map`에서는 숫자를
1-based로 바꾸는 단계 자체가 없고 exact key lookup만 있다.

흔한 오해는 `Sequence`를 만족하면 모든 대괄호 연산이 따라온다고 보는
것이다. iteration evidence는 bracket read, mutable update, freeze, view
capability를 자동 생성하지 않는다. `Set`에 index가 없는 것과 Tuple의
`.1`, Record의 label이 동적 bracket index가 아닌 것도 같은 분리 원칙의
결과다. 코드 리뷰에서는 “첫 원소는 1”이라는 구호보다 carrier와 domain을
함께 적어 잘못된 일반화를 막는다.

예를 들어 ordinary List 세 값의 trace는 `List<Int> → domain 1..3 →
index 2 admission → 내부 projection → 두 번째 값` 순서다. bounded List
`10..12`는 `domain 10..12 → index 11 admission`으로 읽으며 중간에
1..3으로 고치지 않는다. `Map<Int, String>`의 key `2`는 두 번째 항목이
아니라 exact integer key다. 세 경우에 같은 숫자 `2`가 등장해도
coordinate identity와 failure가 다르다.

String은 Unicode scalar coordinate, Bytes는 byte coordinate를 사용하므로
화면 글자 수와 저장 byte 수를 섞지 않는다. index 결과를 mutation
target으로 쓰려면 read capability 외에 해당 carrier의 별도 update
contract가 있어야 한다. 검사 실패 시 owner와 carrier 내용은 그대로
남고 성공한 element만 결과 value로 publish된다. 이 trace를 API 문서에
적으면 backend offset을 public 의미로 노출하지 않고도 비용과 오류
경계를 설명할 수 있다.

### 6.1 ordinary List의 첫 값

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let names: List<String> = ["Ada", "Grace", "Edsger"]
let first = names[1]
let last = names[names.length]
```

`first`의 설계상 값은 `"Ada"`다. owner와 index expression을 한 번씩
평가하고 동적 범위 실패는 `IndexError::outOfLogicalDomain`이다.

### 6.2 bounded List는 rebase하지 않는다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let bounded = [3..5: 10, 20, 30]
let declaredFirst = bounded[3]
let declaredLast = bounded[5]
```

storage에 세 element가 있어도 logical domain은 `3..5`다. `bounded[1]`로
자동 rebase하지 않는다.

### 6.3 Map은 exact key domain이다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let ports = #map{
    "http": 80
    "https": 443
}
let secure = ports["https"]
```

Map lookup은 `String` key identity를 사용한다. 없는 key를 `Option`이나
0-based index로 바꾸지 않는다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: INDEX_OUT_OF_LOGICAL_DOMAIN; product: NOT_RUN -->
```deeplus
let first = names[0]
// INDEX_OUT_OF_LOGICAL_DOMAIN
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: LOGICAL_INDEX_DOMAIN_MISMATCH; product: NOT_RUN -->
```deeplus
let ports = #set{80, 443}
let first = ports[1]
// Set iteration order는 bracket identity가 아님
```

negative-from-end index도 없다. from-end가 필요하면 slice bound의 `$`를
사용한다. user type이 `Sequence`나 `Indexable`을 만족해도 bracket route가
자동 활성화되지 않는다.

## 8. 다른 기능과의 연결

- comprehension은 Sequence traversal을 사용하지만 eager collection
  identity를 명시한다.
- slice 결과는 `ReadonlyView`이며 source coordinate를 보존한다.
- Map의 `**base` unfold와 Record named unfold는 서로 다르다.
- String index는 byte나 grapheme가 아니라 Unicode scalar `Char`다.

## 9. Deeplus다운 작성 관례

- loop counter와 collection coordinate를 1-based로 맞춘다.
- bounded domain을 가진 자료는 declared coordinate를 API에 보존한다.
- Map lookup 실패를 명시적으로 처리한다.
- Set 출력/serialization을 iteration order에 의존시키지 않는다.

## 10. 연습 문제

1. **복사:** 네 도시 List에서 `cities[1]`과 마지막 값을 읽어라.
2. **빈칸 완성:** `[10..12: a, b, c]`에서 유효 domain `___..___`와
   `values[___] == b`의 세 빈칸을 채워라.
3. **설계:** sparse sensor ID를 List와 Map 중 어디에 둘지 logical
   coordinate, missing key, ordering을 기준으로 결정하라.

## 11. 빠른 복습

- ordinary ordered index는 1부터 시작한다.
- bounded List는 declared domain을 보존한다.
- Map은 exact runtime key를 쓴다.
- Set에는 bracket과 semantic order가 없다.
- Sequence conformance는 bracket 증거가 아니다.

## 12. 정본 근거와 다음 장

- [컬렉션 레퍼런스](../../grammar-reference/09-collections-indexing-and-slicing.md)
- [언어 명세 §24](../../../spec/language.md)
- [값·index coherence](../../../spec/contracts/value-operator-indexing-coherence.json)

다음 장에서는 범위를 선택하면서도 source coordinate와 owner를 보존하는
view를 배운다.
