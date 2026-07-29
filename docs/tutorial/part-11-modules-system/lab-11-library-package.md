# Lab 11 — Pure core와 adapter를 가진 library package

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이 실습은 build manifest syntax를 발명하지 않는다. PackageId와
file-to-Module mapping은 외부 build graph가 공급한다고 기록하고, source
Module/API만 설계한다.

## 목표

- 하나의 Package 안에 core, API, adapter Module을 나눈다.
- public/common/private visibility를 적용한다.
- schema와 codec을 분리한다.
- console convenience 이름 없이 pure core를 검증한다.

## 준비

Part 11의 앞 장과 Part 09의 capability/effects를 복습한다.

### 누적 프로젝트 연결

| 연결 | 이 실습에서 이어 받거나 넘기는 것 |
|---|---|
| input | Lab 10의 Worker protocol, owner-closed Job payload와 failure responsibility를 입력으로 받는다. |
| output | model/API/wire/host adapter Module graph와 public closure·codec·HIR evidence 표를 만든다. |
| next | Part 12에서 이 library의 current surface와 Preview 제안을 분리한 설계 검토 카드를 작성한다. |

먼저 PackageId 하나와 네 ModulePath를 별도 표에 적는다. model은 domain
type과 pure 계산, api는 public protocol/schema, wire는 versioned codec,
host는 console/file runtime adapter를 소유한다. source file path는 build
mapping 열에만 적고 ModulePath와 자동 동일시하지 않는다. import edge와
public export edge도 다른 화살표로 그린다.

## 단계별 구현

### 1단계 — pure model Module

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::ledger::model

public schema EntryRow {
    id: EntryId
    amount: Rational
}

public def total(entries: List<EntryRow>) -> Rational
    throws Never
    effects {}
= {
    return sumAmounts(entries)
}
```

### 2단계 — explicit wire adapter

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::ledger::wire
import tutorial::ledger::model::{EntryRow}

public def encode(row: EntryRow) -> Bytes
    throws EncodeError
    effects {}
= {
    return LedgerWireV1::encode(row)
}
```

schema field order를 wire tag로 사용하지 않는다.

### 3단계 — application console adapter

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::ledger::console
import tutorial::ledger::model::{EntryRow,total}

public capability AppConsole for {io}

public def renderTotal(entries: List<EntryRow>) -> String
    throws Never
    effects {}
= {
    return String::render("${total(entries)}")
}
```

host output 함수는 이 Module/package가 별도로 정의해야 한다. Prelude
`print` 존재를 가정하지 않는다.

### 4단계 — public closure와 evidence 경계

각 public callable에 parameter/result label, ownership, ErrorSet/effect,
context capability, selected conformance를 적은 API 표를 만든다. 표의
모든 referenced identity가 public이거나 consumer에게 허용된 visibility인지
closure를 따라 검사한다. codec의 wire tag와 field order는 별도 표에
두고 schema label 또는 Enum declaration order에서 파생하지 않는다.

그 다음 evidence를 static integrity와 execution으로 나눈다. source
archive digest, manifest binding, HIR-H1 verifier receipt는 artifact와
closed identity를 검증한다. backend build, target run, FFI/console
behavior는 별도 execution receipt가 있어야 한다. 앞의 표가 모두
정상이어도 제품 레인은 `NOT_RUN`으로 남는다.

## 중간 점검

- Package와 Module을 같은 것으로 설명하지 않았는가?
- pure model이 console/file authority를 참조하지 않는가?
- codec version이 explicit owner인가?
- public API가 private/common type을 노출하지 않는가?
- PackageId와 ModulePath가 별도 열에 있는가?
- API digest와 wire/ABI identity를 합치지 않았는가?

## 실패 실험

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
private schema InternalRow {
    value: Int
}

public def leak() -> InternalRow = {
    return InternalRow${ value: 1 }
}
```

public API residue가 private type을 노출하므로 visibility closure를
위반한다.

두 번째 실패 실험은 schema field order를 그대로 wire tag 1, 2로 쓰는
설계다. source field를 읽기 좋게 재배치하는 순간 protocol이 바뀌므로
명시적 codec mapping으로 고친다. 세 번째 실패 실험은 host adapter의
`AppConsole`을 pure model Module에 import하는 것이다. 사용하지 않더라도
잘못된 dependency 방향을 만들고 pure core의 검토 경계를 흐린다.

흔한 오해는 같은 package 안이므로 모든 Module이 `common` identity를
public API로 노출해도 된다는 생각이다. common은 package 내부 협력
가시성이고 외부 consumer의 public closure가 아니다. 또 test adapter가
동작했다는 사실을 canonical Prelude 또는 host runtime PASS로 확대하지
않는다.

완성된 검토 묶음에는 Module graph, visibility closure, schema/codec
crosswalk, API responsibility 표, HIR integrity/target execution 분리표가
있어야 한다. 어느 표에도 file-system hierarchy를 namespace 정본으로
쓰거나 noncanonical `print`를 Prelude entry로 기록하지 않는다.

Module graph에는 허용된 dependency 방향도 표시한다. model은 adapter를
모르고, wire와 host가 model/api를 소비하며, application composition
root가 concrete runtime service를 주입한다. model에서 host를 역으로
import하면 pure core가 특정 환경에 묶이므로 실패로 기록한다. 순환을
끊기 위해 ambient global service나 hidden provider를 만들지 않는다.

API 책임 표에는 `total`, `encode`, host write 같은 operation마다 value
parameter, context capability, ownership, Result/throws, effects, suspension을
채운다. 미니 사례로 `encode`가 pure bytes 변환이면 console capability가
없어야 하고, host write는 bytes를 받아 `{io}`와 host ErrorSet을 노출한다.
두 함수를 하나로 합치면 codec failure와 transport failure의 owner가
흐려진다.

마지막 review에는 세 시나리오를 넣는다. source field 순서만 바꾼 경우,
codec tag를 바꾼 경우, Module file을 다른 directory로 옮긴 경우다.
각각 semantic API, wire compatibility, build mapping 중 실제로 바뀐
열만 표시한다. 모든 열을 breaking으로 칠하거나 모든 변경을 cosmetic으로
보는 양극단을 피한다.

정적 산출물 검사가 끝나면 아직 실행하지 않은 항목을 명시한다. 실제
Package manager resolution, host console, FFI target, xVM/Cranelift backend,
formatter/LSP 제품 동작은 이 실습 범위 밖이다. 따라서 결과 문구는
“설계·결합 검사 완료”이지 “library 제품 지원 PASS”가 아니다.

그 범위 문구도 최종 산출물에 그대로 남긴다.
## 확장 과제

1. **따라 하기:** model과 wire Module의 import/export 관계를 그려라.
2. **빈칸 완성:** pure core, codec, runtime adapter가 각각 소유하는
   identity를 채워라.
3. **스스로 설계하기:** test adapter와 host adapter를 별도 Module로
   나누고 capability/effect/error signature를 작성하라.
4. **검증 설계:** HIR-H1/API digest/source archive integrity와 runtime
   test receipt를 구분한 체크리스트를 작성하라.

## 완료 체크리스트

- [ ] Package/Module/file path를 분리했다.
- [ ] schema/serialization/ABI를 분리했다.
- [ ] canonical하지 않은 console API를 Prelude로 주장하지 않았다.
- [ ] current HIR-H1과 draft RFC를 분리했다.
- [ ] product execution PASS를 주장하지 않았다.

## 정본 근거

- [Module reference](../../grammar-reference/02-programs-modules-and-imports.md)
- [Schema reference](../../grammar-reference/07-enums-records-schemas-bitfields-and-units.md)
- [Prelude/provider reference](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)
- [HIR/MIR reference](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
