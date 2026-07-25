# 11-02 — Public API, schema와 serialization identity

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

schema/materialization과 API identity는 current design이다. 자동
serialization format이나 target ABI를 이 장이 추가하지 않는다.

## 2. 학습 목표

- structural Record, schema, Map을 구분한다.
- public API digest에 남는 semantic identity를 설명한다.
- serialization tag와 Enum declaration order를 분리한다.
- explicit codec boundary를 설계한다.

## 3. 선수 지식

Module visibility, Record row, schema materialization, Enum VariantId를 알아야
한다.

## 4. 문제에서 출발하기

source에 case를 위에서 아래로 적었다고 그 순서가 wire tag가 되는 것은
아니다. field layout도 serialization order가 아니다. API의 semantic
identity와 bytes representation을 섞으면 source refactor가 protocol
break가 된다.

## 5. 핵심 모델

- Record label: compile-time identifier identity.
- Map key: runtime exact key value.
- schema: required/default field, constraint, construction authority.
- API digest: selected declaration/type/label/responsibility identity.
- serialization tag/layout/ABI: 별도 explicit mapping과 target contract.
- Enum `VariantId`: declaration order, ordinal, raw tag와 다르다.

## 6. 단계별 예제

schema materialization은 static labels를 검사한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module ledger::api

public schema EntryRow {
    id: EntryId
    amount: Rational
    cleared: Bool = false
}

let row = EntryRow${
    id: EntryId!(13)
    amount: <5/2>
}
```

wire representation은 별도 user API로 드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def encodeEntry(row: EntryRow) -> Bytes
    throws EncodeError
    effects {}
= {
    return LedgerWireV1::encode(row)
}
```

`LedgerWireV1`은 application/library가 소유한 explicit codec owner다.
schema 선언만으로 JSON, field order, ABI가 생기지 않는다.

## 7. 허용·거부·경계 사례

Enum의 semantic cases:

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum PaymentState {
    pending
    settled(reference: String)
    failed(reason: String)
}
```

거부되는 추론:

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
def implicitTag(state: PaymentState) -> UInt8 = {
    return state.declarationOrder
}
// declaration order는 raw/serialization/ABI identity가 아니다.
```

wire tag가 필요하면 versioned codec mapping을 명시한다. one-case Enum도
semantic-only이며 자동 rewrite나 recommendation을 만들지 않는다.

## 8. 다른 기능과의 연결

- materialization `**record`는 static label row만 공급하며 Map은 대체하지
  못한다.
- public API는 ownership, errors/effects, cancellation, witness identity도
  보존한다.
- FFI ABI는 wire serialization과 또 다른 representation domain이다.
- HIR/MIR은 semantic identity를 유지하되 backend layout을 강제하지 않는다.

### 판정 추적

`EntryRow` 같은 public schema를 만나면 먼저 schema identity와 각 static
field label, required/default, constraint를 결합한다. materialization은
그 row를 정확히 만족하는지 검사하지만 bytes 순서를 만들지 않는다.
public API digest에는 schema와 callable responsibility가 들어가고,
versioned codec은 별도 mapping에서 wire field/tag/encoding을 정한다.
native FFI가 필요하면 다시 target ABI representability를 검증한다.

이 순서에서 semantic `VariantId`, serialization tag, runtime
discriminant, declaration-order ordinal, native layout은 각각 다른 열이다.
한 열의 정수값이 우연히 같아도 identity가 같아지는 것은 아니다.
codec 변경은 wire compatibility 검토 대상이고, case rename이나 API
responsibility 변경은 semantic API 검토 대상이다.

### 흔한 오해와 미니 사례

schema를 선언하면 자동으로 JSON codec과 reflection metadata가 생긴다고
생각하기 쉽다. 그러나 schema는 construction authority와 static row를
제공할 뿐 format, field order, unknown-field policy를 선택하지 않는다.
Record materialization과 runtime Map도 label shape가 비슷해 보여도
compile-time row와 runtime key lookup이라는 다른 domain이다.

미니 사례로 `EntryRow`에 default field `cleared`를 추가했을 때 source
construction은 기존 call site와 호환될 수 있다. 하지만 wire V1에서 새
field를 생략할지 명시적으로 encode할지는 `LedgerWireV1`이 결정한다.
반대로 codec tag만 바꾸고 schema가 같아도 wire break가 될 수 있다.

### 경계별 검토표

| 경계 | 보존할 identity | 여기서 추론하면 안 되는 것 |
|---|---|---|
| schema construction | field label, type, required/default, constraint | JSON 이름·bytes 순서 |
| public API digest | declaration과 observable responsibility | runtime layout·target ABI |
| versioned codec | wire tag, encoding, version policy | semantic Enum ordinal |
| FFI profile | target representation과 ownership | application serialization |

이 네 경계를 한 “데이터 모양”으로 합치지 않아야 source refactor,
protocol migration과 backend 변경을 독립적으로 판단할 수 있다.

API 진화도 경계별로 판정한다. required schema field 추가는 construction
call site에 새 의무를 만들 수 있고, default field 추가는 source
construction과 호환될 수 있다. 그러나 두 경우 모두 codec이 old reader와
new reader를 어떻게 다루는지는 별도 version rule이 필요하다. field
삭제·rename은 semantic label identity 변경이며 단순 wire alias로
숨기지 않는다.

Enum도 마찬가지다. 새 case 추가는 exhaustive match와 public semantic
set을 바꾸므로 source compatibility 검토가 필요하다. codec이 unknown
wire tag를 보존·거부·skip 중 무엇으로 처리하는지는 transport policy다.
한쪽이 안전하다고 다른 쪽까지 자동 승인하지 않는다. one-case Enum은
semantic 구분을 표현할 수 있으므로 wrapper로 자동 rewrite하거나
tooling recommendation을 만들지 않는다.

미니 사례로 V2 codec이 `cleared`를 새 wire field 7에 넣는다면 mapping
표에는 field label `cleared`, tag 7, default-on-absence, version 2를
명시한다. runtime discriminant나 declaration position을 tag 7의 근거로
쓰지 않는다. decoder가 V1 bytes를 읽는 정책은 codec evidence로
검증하고, schema materialization PASS만으로 bytes compatibility를
주장하지 않는다.

마지막으로 API digest는 callable의 label shape와 ownership channel도
포함한다. parameter를 value에서 `move`로, error를 Result에서 throws로,
ordinary argument를 context capability로 바꾸면 이름과 값 type이 같아도
observable responsibility가 달라진다. 이런 변경을 serialization-only
diff로 분류하지 않는다.

## 9. Deeplus다운 작성 관례

domain type과 transport type을 분리한다. semantic API는 의미를, codec은
bytes와 version을, FFI profile은 target ABI를 각각 소유하게 한다.

## 10. 연습 문제

1. **따라 하기:** required field 둘과 default field 하나인 schema를
   materialize하라.
2. **빈칸 완성:** Record label, Map key, serialization tag의 판정 시점을
   채워라.
3. **스스로 설계하기:** Enum case 세 개에 versioned wire tag를 부여하는
   named codec API를 설계하되 declaration order에 의존하지 마라.

## 11. 빠른 복습

- schema는 construction authority이지 serialization format이 아니다.
- semantic identity와 byte/layout identity를 분리한다.
- Enum order는 tag/ordinal/raw가 아니다.
- public digest는 observable responsibility를 보존한다.

## 12. 정본 근거와 다음 장

- [Enum/Record/schema](../../grammar-reference/07-enums-records-schemas-bitfields-and-units.md)
- [API/ABI identity](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [module API schema](../../../schemas/language/module-api-digest.schema.json)

다음 장은 canonical Prelude identity와 application/provider service를
분리한다.
