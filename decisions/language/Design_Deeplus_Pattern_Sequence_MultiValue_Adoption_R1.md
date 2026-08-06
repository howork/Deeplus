# Deeplus Pattern·Sequence Rest·Multi-Value 정본 수용 결정 R1

상태: `CURRENT_DESIGN_STATIC`
revision: `r51f3-current-pattern-sequence-multivalue-r1`
제품 실행: `15/15 NOT_RUN`

## 1. 입력과 우선순위

이 결정은 다음 검토 팩을 현재 `main`
`a6a7a3a606722a8f588f40d3d552c54a59c933cf`에 대조한 결과다.

| 입력 | bytes | SHA-256 | 통제 범위 |
|---|---:|---|---|
| `Design_Deeplus_Sequence_Rest_and_Multi_Value_Revision_R3.zip` | 23,760 | `6e4f9f433e2b6abe631b07427b9ffa9c6a9495d08dee93fa6765dfa652c7c60b` | Sequence rest 철자, residual, multi-value |
| `Design_Deeplus_Pattern_and_Destructuring_Revision_R2.zip` | 36,559 | `93b685e088f5de2aa4eafde9ca9161178b3c34456f3028b19adf5bf48b0cea20` | 나머지 Pattern/구조 분해 |

두 ZIP은 CRC, path safety, exact/case-fold duplicate, symlink, nested
archive, manifest와 `SHA256SUMS` 결합을 통과했다. Sequence rest와
multi-value가 충돌하는 경우 R3가 R2보다 우선한다는 당시 판정은 provenance로
남는다. 현행 R77 atomic cutover는 두 prefix/double-sided 후보를 모두
제거하고, 정확히 하나의 attached suffix rest `name..` 또는 `_..`만 List
Pattern의 시작·중간·끝 위치에 허용한다.

## 2. Deeplus다운 수용 원칙

수용의 중심은 “짧은 표면보다 책임이 닫힌 표면”이다.

1. 모든 owner는 하나의 Pattern CST/AST와 owner별 policy를 공유한다.
2. subject는 한 번만 평가한다.
3. probe는 pure, deterministic, nonconsuming, nonthrowing,
   nonsuspending이다.
4. 구조 검사와 guard가 모두 성공하기 전에는 move, borrow, binding,
   residual view, assignment 또는 authority를 공개하지 않는다.
5. 고정 위치의 이질적 결과는 `Tuple`, 동질적 순차 residual은
   명시적으로 허가된 `Sequence` carrier가 담당한다.
6. 같은 소스 표면을 runtime type에 따라 다르게 낮추지 않는다.
7. Preview는 검토 가능한 설계로 보존하되 Stable이나 제품 지원으로
   오해하지 않는다.

## 3. Stable 수용

### 3.1 Pattern carrier

- exact Tuple Pattern: `(p)`는 grouping, `(p,)`는 one-Tuple
- List exact 또는 정확히 하나의 suffix rest: `[tail..]`,
  `[first, middle.., last]`, `[head, tail..]`, `_..`
- Record-family exact-by-default, `_**` open-ignore, `name**` static-named
  residual, mapping은 `source label : destination Pattern`
- Map exact-by-default, `.._` open-ignore, `..name` dynamic residual,
  mapping은 `destination Pattern : key`
- schema/data/value 또는 명시적 pattern-transparent nominal product
- Enum positional payload와 declared named payload
- stable pin, closed exact-order range/relational Pattern

ordinary Class private state, getter/provider, Dyn, Facet, FFI/opaque
representation은 자동으로 열지 않는다.

### 3.2 owner

- checker-proven irrefutable plain `let`/`var`, bare `for`
- refutable guarded `let`/`var`, `if let`, `while let`, `for let`, `match`
- assertive `let!`/`var!`; mismatch는 `PatternMatchDefect`
- left-to-right short-circuit `and then` Pattern condition chain
- first-match refutable `catch`, unmatched error는 다음 catch 또는 바깥으로
  전파
- callable/lambda의 irrefutable body-entry decomposition
- distinct direct mutable local만 사용하는 failure-atomic Pattern assignment

함수 parameter의 첫 Identifier는 call label, whole-value local, overload,
public API와 ABI identity를 그대로 유지한다. 뒤의 Pattern binder는 body
local일 뿐이다.

### 3.3 Sequence rest carrier

borrowed List residual은 전용 `ListRestView<T>`다. 이 타입은
`SourceOwnerId`, `BorrowRegionId`, `RankSpan(start_rank, count)`, 원본
logical-coordinate projection과 명시적 intrinsic `Sequence<T>` witness를
가진다. 빈 residual은 `count = 0`으로 표현하며 존재하지 않는 empty
source Range를 만들지 않는다.

기존 `ReadonlyView<T>`에는 Sequence witness를 추가하지 않는다.
Sequence conformance 하나만으로 Pattern이나 indexing도 열리지 않는다.
Stable rest view는 임시 owner를 붙잡거나 owner보다 오래 살 수 없고,
좌표를 1부터 다시 매기거나 숨은 copy/allocation을 만들지 않는다.

### 3.4 고정 multi-value

다음 bare comma 표면만 기존 Tuple identity로 정규화한다.

```deeplus
public def split() -> String, Int = {
    return "ready", 1
}

let label, count = split()
left, right = right, left
```

일반 comma expression operator, `ValuePack`, Sequence multi-return,
별도 ABI identity는 없다. 병렬 대입은 distinct mutable direct
`LocalPlaceId`만 받고, RHS 전체를 왼쪽부터 한 번씩 stage한 뒤
`replace_group_commit` 하나를 수행한다. 이는 failure-atomic logical
commit이지 hardware/cross-thread atomicity가 아니다.

## 4. Preview 보존

다음은 Preview/Preview Design으로 남는다.

- And/Not Pattern
- Set/NumericArray Pattern
- Pattern Synonym, pure Pattern View, completeness manifest
- search/find Pattern
- generic/custom Sequence 자동 opening과 user descriptor
- temporary-owner-retaining/materializing residual
- affine/Resource permutation
- field/index/property/shared/actor/FFI/nonlocal multi-assignment
- top-level destructuring

Preview 파일과 설명은 삭제하지 않는다. 다만 별도 activation과
실행 증거 전에는 Stable source 또는 제품 지원을 주장하지 않는다.

## 5. 수용하지 않은 항목

- prefix/double-sided List rest 철자와 tuple rest
- effectful, throwing, suspending 또는 dynamic extractor
- arbitrary getter/provider 호출
- unbounded backtracking
- hidden copy/allocation/lifetime extension/ABI inference
- ordinary Class private representation 자동 opening
- type-dependent Tuple/Sequence dual lowering
- 일반 comma expression

잘못된 rest 철자는 일반 parser error일 뿐 별도 Historical/Recovery 사용자
표면이나 AST/HIR node를 만들지 않는다.

## 6. 권위와 증거 경계

이 수용은 문법·언어·타입·MIR·문서·정적 fixture의 현재 설계 권위를
갱신한다. Rust frontend, checker, MIR lowering, xVM, Cranelift,
formatter/LSP, conformance와 product lane 실행을 증명하지 않는다.
기존 semantic P0는 0이고 OPEN P1 22건 및 M13 action을 닫거나
재번호화하지 않는다.
