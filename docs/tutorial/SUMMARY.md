# Deeplus 튜토리얼 전체 목차

> 총 12개 부 · 60개 개념 장 · 12개 안내 실습 · 4개 종합 프로젝트 ·
> 8개 참조 부록 · 링크 target 96개 · 핵심 학습 단위 72개

## Part 01 — 언어와 학습 환경

- [Part 안내](part-01-orientation/README.md)
- [01-01. Deeplus의 목표와 상태 읽기](part-01-orientation/01-01-language-status.md)
- [01-02. 소스와 진단을 읽는 법](part-01-orientation/01-02-source-diagnostics.md)
- [01-03. 첫 design-static 프로그램](part-01-orientation/01-03-first-design-static-program.md)
- [01-04. Package, Module, 소스 역할](part-01-orientation/01-04-package-module-source.md)
- [01-05. 이름, 바인딩, 블록](part-01-orientation/01-05-names-bindings-blocks.md)
- [실습 01. 타입이 드러나는 인사말](part-01-orientation/lab-01-typed-greeting.md)

## Part 02 — 값, 리터럴, 식

- [Part 안내](part-02-values/README.md)
- [02-01. 값, 리터럴, 정체성](part-02-values/02-01-values-literals-identity.md)
- [02-02. Rational과 Complex 정확 수](part-02-values/02-02-rational-complex.md)
- [02-03. String, Char, Bytes, `#raw`](part-02-values/02-03-text-bytes-raw.md)
- [02-04. 연산자, 거듭제곱, Bool](part-02-values/02-04-operators-power-boolean.md)
- [02-05. 식과 평가 순서](part-02-values/02-05-expressions-evaluation-order.md)
- [실습 02. 예산과 복소 신호](part-02-values/lab-02-budget-complex-signal.md)

## Part 03 — 흐름 제어와 호출 가능 값

- [Part 안내](part-03-flow-callables/README.md)
- [03-01. 함수, 반환, 효과](part-03-flow-callables/03-01-functions-return-effects.md)
- [03-02. 매개변수, label, rest, unfold](part-03-flow-callables/03-02-parameters-labels-rest-unfold.md)
- [03-03. 메서드, 메시지 호출, trailing closure](part-03-flow-callables/03-03-methods-messages-trailing-closures.md)
- [03-04. 조건, match, 반복, `@` 제어](part-03-flow-callables/03-04-control-flow.md)
- [03-05. closure, capture, local function, 함수 static](part-03-flow-callables/03-05-closures-captures-static.md)
- [실습 03. 검증 파이프라인](part-03-flow-callables/lab-03-validation-pipeline.md)

## Part 04 — 타입 시스템

- [Part 안내](part-04-type-system/README.md)
- [04-01. 추론, alias, refinement](part-04-type-system/04-01-inference-aliases-refinement.md)
- [04-02. Union, Intersection, Option, Result](part-04-type-system/04-02-union-intersection-option-result.md)
- [04-03. narrowing, `is`, `!is`, stable place](part-04-type-system/04-03-narrowing-stable-place.md)
- [04-04. generic, variance, `where`](part-04-type-system/04-04-generics-variance-where.md)
- [04-05. callable identity, effect, error, cancellation](part-04-type-system/04-05-callable-identity-effects-cancellation.md)
- [실습 04. 타입이 보존되는 parser와 guard](part-04-type-system/lab-04-typed-parser-guard.md)

## Part 05 — 데이터 모델링과 패턴

- [Part 안내](part-05-data-modeling/README.md)
- [05-01. Record, Tuple, Map, Schema](part-05-data-modeling/05-01-record-tuple-map-schema.md)
- [05-02. Class, data class, 생성](part-05-data-modeling/05-02-class-data-class-constructors.md)
- [05-03. 현행 Enum 표면](part-05-data-modeling/05-03-enum-current-surface.md)
- [05-04. 패턴과 구조 분해](part-05-data-modeling/05-04-patterns-destructuring.md)
- [05-05. exhaustiveness, guard, transaction](part-05-data-modeling/05-05-exhaustiveness-guards-transactions.md)
- [실습 05. 도메인 workflow](part-05-data-modeling/lab-05-domain-workflow.md)

## Part 06 — Trait와 conformance

- [Part 안내](part-06-traits/README.md)
- [06-01. Trait 요구사항](part-06-traits/06-01-trait-requirements.md)
- [06-02. conformance와 witness](part-06-traits/06-02-conformance-witness.md)
- [06-03. extension과 named extension](part-06-traits/06-03-extensions-named-extensions.md)
- [06-04. associated type과 명시적 한정](part-06-traits/06-04-associated-types-qualification.md)
- [06-05. fixed-glyph conformance](part-06-traits/06-05-fixed-glyph-conformance.md)
- [실습 06. generic renderer](part-06-traits/lab-06-generic-renderer.md)

## Part 07 — 소유권과 책임

- [Part 안내](part-07-ownership/README.md)
- [07-01. value, place, owner](part-07-ownership/07-01-value-place-owner.md)
- [07-02. borrow, `mut`, `inout`](part-07-ownership/07-02-borrow-mut-inout.md)
- [07-03. move, copy, clone, consume](part-07-ownership/07-03-move-copy-clone-consume.md)
- [07-04. capture, lifetime, escape](part-07-ownership/07-04-capture-lifetime-escape.md)
- [07-05. cleanup, failure, transaction](part-07-ownership/07-05-cleanup-failure-transaction.md)
- [실습 07. 자원 workflow](part-07-ownership/lab-07-resource-workflow.md)

## Part 08 — 컬렉션과 수치 계산

- [Part 안내](part-08-collections-math/README.md)
- [08-01. Sequence, Map, 1-based index](part-08-collections-math/08-01-sequence-map-one-based-index.md)
- [08-02. slice, view, provenance](part-08-collections-math/08-02-slicing-view-provenance.md)
- [08-03. comprehension과 generator](part-08-collections-math/08-03-comprehensions-generators.md)
- [08-04. NumericArray와 선형대수](part-08-collections-math/08-04-numeric-array-linear-algebra.md)
- [08-05. measure, unit, exact numeric](part-08-collections-math/08-05-measures-units-exact-numeric.md)
- [실습 08. 과학 계산 파이프라인](part-08-collections-math/lab-08-scientific-pipeline.md)

## Part 09 — 실패, 효과, 계약

- [Part 안내](part-09-failure-effects-contracts/README.md)
- [09-01. error와 defect](part-09-failure-effects-contracts/09-01-errors-defects.md)
- [09-02. effect, throws, Result](part-09-failure-effects-contracts/09-02-effects-throws-result.md)
- [09-03. `try`, `@try`, `finally`](part-09-failure-effects-contracts/09-03-try-at-try-finally.md)
- [09-04. law, contract, assert, `def#guard`](part-09-failure-effects-contracts/09-04-law-contract-assert-guard.md)
- [09-05. 진단과 recovery](part-09-failure-effects-contracts/09-05-diagnostics-recovery.md)
- [실습 09. 복원 가능한 입력 처리](part-09-failure-effects-contracts/lab-09-resilient-import.md)

## Part 10 — 비동기와 actor 동시성

- [Part 안내](part-10-concurrency/README.md)
- [10-01. async, await, task](part-10-concurrency/10-01-async-await-tasks.md)
- [10-02. structured scope와 cancellation](part-10-concurrency/10-02-structured-scope-cancellation.md)
- [10-03. actor, protocol, message](part-10-concurrency/10-03-actor-protocol-messages.md)
- [10-04. mailbox, request/reply, isolation](part-10-concurrency/10-04-mailbox-request-reply-isolation.md)
- [10-05. shared state, ordering, test](part-10-concurrency/10-05-shared-state-ordering-testing.md)
- [실습 10. 용량이 제한된 worker](part-10-concurrency/lab-10-bounded-worker.md)

## Part 11 — 모듈, 경계, 시스템 모델

- [Part 안내](part-11-modules-system/README.md)
- [11-01. Package, Module, import, visibility](part-11-modules-system/11-01-package-module-import-visibility.md)
- [11-02. 공개 API, Schema, 직렬화](part-11-modules-system/11-02-public-api-schema-serialization.md)
- [11-03. Prelude, provider, console adapter](part-11-modules-system/11-03-prelude-provider-console-adapter.md)
- [11-04. FFI, unsafe, quarantine](part-11-modules-system/11-04-ffi-unsafe-quarantine.md)
- [11-05. HIR-H1, MIR, backend, tooling](part-11-modules-system/11-05-hir-mir-backends-tooling.md)
- [실습 11. 라이브러리 Package 설계](part-11-modules-system/lab-11-library-package.md)

## Part 12 — Preview와 언어 진화

- [Part 안내](part-12-preview-evolution/README.md)
- [12-01. 상태 모델과 증거](part-12-preview-evolution/12-01-status-model.md)
- [12-02. 세 가지 Preview gated 기능](part-12-preview-evolution/12-02-preview-gated.md)
- [12-03. Preview Design: 타입과 Trait](part-12-preview-evolution/12-03-preview-design-types-traits.md)
- [12-04. Preview Design: 컬렉션과 제어](part-12-preview-evolution/12-04-preview-design-collections-control.md)
- [12-05. Preview Design: 동시성, runtime, MIR-X1](part-12-preview-evolution/12-05-preview-design-concurrency-runtime.md)
- [실습 12. 설계 제안 검토](part-12-preview-evolution/lab-12-design-review.md)

## 과정 전체를 잇는 누적 산출물

각 Part의 실습은 별개의 예제 모음이 아니라 다음 산출물을 단계적으로
확장한다. 뒤 Part는 앞 Part의 모든 syntax를 다시 보여 주기보다 그
산출물의 type·owner·effect 경계를 더 정밀하게 만든다.

| 단계 | 앞 단계에서 받는 것 | 이번에 만드는 것 | 다음 단계로 넘기는 것 |
|---|---|---|---|
| Lab 01 | 이름과 상태 모델 | 순수 typed greeting | 명시적 값 변환 함수 |
| Lab 02 | 순수 함수 | exact numeric 계산 | 값·식·operator trace |
| Lab 03 | 값 변환 | Bool predicate와 closure pipeline | 호출·제어 흐름 |
| Lab 04 | 제어 흐름 | typed parse/guard 결과 | 검증된 domain value |
| Lab 05 | 검증된 값 | Record/Enum workflow | 닫힌 domain model |
| Lab 06 | domain model | Trait renderer와 exact witness | 명시적 behavior evidence |
| Lab 07 | behavior evidence | owned resource workflow | owner/cleanup ledger |
| Lab 08 | owner 규칙 | 1-based scientific pipeline | shape·view·numeric report |
| Lab 09 | 계산 보고서 | failure/effect contract | 복원 가능한 boundary |
| Lab 10 | boundary contract | bounded actor worker | isolation/message protocol |
| Lab 11 | protocol과 API | Package/Module 공개 경계 | 검토 가능한 library design |
| Lab 12 | 전체 design | 상태·authority review | 채택/보류 근거 |

이 표의 “넘긴다”는 실제 artifact나 제품 구현을 생성했다는 뜻이 아니다.
학습자가 다음 실습에서 재사용할 설계 정적 모델을 뜻하며 product 상태는
계속 `NOT_RUN`이다.

## 종합 프로젝트

- [A. Rational 원장](capstones/a-rational-ledger.md)
- [B. Complex/NumericArray 분석](capstones/b-complex-numeric-analysis.md)
- [C. 타입 검증과 패턴 파이프라인](capstones/c-typed-pattern-pipeline.md)
- [D. bounded actor worker](capstones/d-bounded-actor-worker.md)

종합 프로젝트는 Lab 01~12의 단일 누적 산출물을 다시 이어 쓰는 단계가
아니라, 여러 단계의 계약을 함께 검토하는 독립 통합 과제다. A는 Lab
02·04·05의 exact numeric·refinement·Enum을, B는 Lab 02·08·09의 수치
표현·shape·failure 경계를, C는 Lab 04·05·06의 검증·pattern·Trait
증거를, D는 Lab 07·09·10의 ownership·failure·actor 책임을 교차
검토한다. 파일의 존재나 정적 설명만으로 product PASS를 뜻하지 않는다.

## 참조 부록

- [A. 문법 빠른 찾기](appendices/a-syntax-quick-reference.md)
- [B. 상태와 feature 지도](appendices/b-status-feature-map.md)
- [C. 진단 읽기](appendices/c-diagnostics-guide.md)
- [D. 연습 문제 힌트](appendices/d-exercise-hints.md)
- [E. 용어집](appendices/e-glossary.md)
- [F. 다른 언어에서 옮겨 오기](appendices/f-migration-cross-language.md)
- [G. 문법과 튜토리얼 교차 색인](appendices/g-grammar-tutorial-index.md)
- [H. 조사 방법과 참고 자료](appendices/h-research-bibliography.md)
