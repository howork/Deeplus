# 부록 E — Deeplus 학습 용어집

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 간단한 학습 정의다. 정확한 normative definition은 contract와 언어
> 참조가 우선하며 product 상태는 `NOT_RUN`이다.

## A–H

**Actor**  
격리된 mutable state region과 mailbox identity를 소유하는 동시성
owner. 단순한 class나 thread의 별칭이 아니다.

**Admission**  
source role, grammar goal, status/gate, static rule을 통과해 다음 단계의
정상 node가 될 수 있는지 결정하는 과정.

**Artifact identity**  
ZIP 같은 byte artifact의 SHA-256 identity. 40자리 Git commit identity나
semantic type identity와 비교하지 않는다.

**Binding transaction**  
pattern의 구조·타입·guard가 모두 성공할 때만 부분 binding을 commit하는
규칙.

**Callable identity**  
parameter 순서·label·role·ownership mode, return, error/effect row 등으로
구성된 호출 가능 선언의 정체성.

**Cancellation**  
작업을 계속하지 말라는 구조적 신호. recoverable error, defect,
actor receiver closure와 구분한다.

**Conformance**  
명목 type이 Trait requirement를 만족한다는 명시적 증거 관계.

**Current**  
현행 semantic authority에 들어온 상태. product 구현·실행 PASS와
동의어가 아니다.

**Effect row**  
호출이 관찰할 수 있는 I/O, actor, async 등 책임을 signature에 드러내는
부분.

**EnumId / VariantId**  
Enum owner와 case를 나타내는 semantic identity. source ordinal,
serialization tag, runtime discriminant, ABI layout과 분리한다.

**HIR-H1**  
현행 source 의미와 MIR 사이에서 identity, type, ownership, effect,
diagnostic residue를 검증하는 고수준 bridge profile.

## I–P

**1-based indexing**  
일반 sequence의 첫 유효 index가 `1`인 규칙.

**Module**  
이름 공간·가시성·소스 구성 단위. 파일 시스템 경로와 완전히 동일할
필요가 없다.

**Narrowing**  
control-flow 증거에 따라 특정 edge에서 usable type를 더 정밀하게
만드는 과정. mutable/aliased place에서는 증거 유지 조건이 필요하다.

**Owner**  
값·자원·state의 생명주기와 정리 책임을 가진 identity.

**Package**  
배포·의존성·빌드 단위. Module과 다른 축이다.

**Place**  
값을 읽거나 쓸 수 있는 저장 위치를 나타내는 정적 개념.

**Prelude**  
명시 import 없이 제공되는 정본 최소 identity 집합. 예제에 자주
나온다는 이유만으로 API를 Prelude에 추가하지 않는다.

**Preview gated**  
exact gate 조건이 있어야 admission을 검토할 수 있는 Preview 상태.

**Preview Design**  
구체적인 설계 검토 문서가 있지만 source activation은 허용되지 않은
`NONACTIVATABLE` 상태.

## Q–Z

**Qualified path**  
하나 이상의 식별자를 `::`로 연결한 owner/name path.

**Recovery only**  
과거 또는 잘못된 surface를 진단·이행하기 위한 parser 경로. 정상
AST/HIR/MIR residue를 만들지 않는다.

**Refinement type**  
기반 type의 값 가운데 predicate를 만족한다는 proof를 가진 type.

**Semantic identity**  
언어 의미가 구분하는 type, declaration, case, witness 등의 identity.
serialization/layout/artifact identity와 분리한다.

**Stable design**  
정본 설계에서 수용된 표면. 구현 상태를 말하지 않는다.

**Stable place**  
narrowing 증거를 사용하는 동안 type-changing mutation이나 alias
write가 없다고 증명된 usable place.

**Trait witness**  
특정 type과 Trait conformance를 가리키는 증거 identity. ordinary
runtime value처럼 저장·합성한다고 가정하지 않는다.

**Union**  
닫힌 type alternative 가운데 하나의 injection identity를 보존하는
type. Enum case identity와 같지 않다.

## 정본 용어 자료

- `spec/contracts/normative-terminology.json`
- `spec/types/type-system.md`
- [상태와 authority](../../grammar-reference/00-status-authority-and-notation.md)

