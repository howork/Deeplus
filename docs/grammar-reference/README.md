<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# Deeplus 문법 명세 및 언어 참조서

이 참조서는 독자가 현행 Deeplus 언어 설계를 한눈에 파악하도록 만든
안내서다. 별도의 언어 권위를 만들지 않으면서 정확한 문법, 수용
규칙, 정적 의미론, 관측 가능한 동작과 실제 예제를 한곳에 모은다.

현행 언어 버전은 `0.1.2-internal`이다. 정확한 현행 리비전은
[`current/language-version.toml`](../../current/language-version.toml)에
기록된다. 독립적인 대상 결합 실행 확인서(target-bound receipt)가 달리
입증하지 않는 한 컴파일러, 런타임, 도구 및 모든 제품 레인은
`NOT_RUN` 상태다.

## 권위 및 충돌 해소

두 서술이 서로 모순되는 것처럼 보이면 다음 순서로 해소한다.

1. 승인된 현행 결정
2. [`spec/language.md`](../../spec/language.md)
3. [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)의 정확한 문법
4. [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)의
   프런트엔드 수용 모델
5. [`spec/types/type-system.md`](../../spec/types/type-system.md)와
   [`spec/mir/semantics.md`](../../spec/mir/semantics.md)의 타입 및 MIR 권위
6. 현행 레지스트리, 계약, Prelude 시그니처, 예제 및 테스트 고정 자료
7. 이 문서 투영

이 참조서는 위 원천을 설명하고 해당 원천으로 연결한다. 이 문서만으로
Preview 문법을 활성화하거나 OPEN P1을 폐쇄하거나 제품 지원을
입증해서는 안 된다.

## 목적별 읽기 경로

| 목적 | 시작할 문서 |
|---|---|
| 무엇이 현행 Deeplus인지 확인 | [상태, 권위 및 표기법](00-status-authority-and-notation.md) |
| 소스 파일 작성 | [어휘 구조](01-lexical-structure.md)를 읽은 뒤 [프로그램과 모듈](02-programs-modules-and-imports.md) |
| 선언과 이름 이해 | [선언, 바인딩 및 이름](03-declarations-bindings-and-names.md) |
| 타입과 내로잉 이해 | [타입, 제네릭 및 리파인먼트](04-types-generics-and-refinement.md) |
| 동작 정의 또는 호출 | [함수, 메서드, 클로저 및 호출](05-functions-methods-closures-and-calls.md) |
| 명목적 동작 모델링 | [클래스, Trait, 적합성 및 확장](06-classes-traits-conformance-and-extensions.md) |
| 데이터 모델링 | [Enum, Record, 스키마, 비트필드 및 단위](07-enums-records-schemas-bitfields-and-units.md) |
| 표현식 해석 | [표현식 및 연산자](08-expressions-and-operators.md) |
| 컬렉션 사용 | [컬렉션, 인덱싱 및 슬라이싱](09-collections-indexing-and-slicing.md) |
| 구조 분해 또는 패턴 매칭 | [패턴, 구조 분해 및 패턴 매칭](10-patterns-destructuring-and-matching.md) |
| 제어 및 실패 흐름 추적 | [제어 흐름, 오류, 효과 및 정리](11-control-flow-errors-effects-and-cleanup.md) |
| 값의 책임 추적 | [소유권, 대여 및 책임](12-ownership-borrowing-and-responsibility.md) |
| 비동기 또는 액터 코드 사용 | [비동기, 태스크, 액터 및 동시성](13-async-tasks-actors-and-concurrency.md) |
| 외부 경계 이해 | [FFI, unsafe, 컴파일러 트리 및 프로필](14-ffi-unsafe-metaprogramming-and-profiles.md) |
| 제안되었거나 거부된 표기 확인 | [Preview, 복구 및 제거된 표면](15-preview-recovery-and-removed-surfaces.md) |
| 정확한 production이 쓰이는 문맥 찾기 | [문맥별 구문과 production 길잡이](16-contextual-syntax-and-production-guide.md) |
| 이름·generic·호출 판정 순서 추적 | [이름 해석, 타입 추론 및 호출 판정](17-name-resolution-type-inference-and-calls.md) |
| 평가·소유권·MIR·백엔드 관찰 추적 | [평가, 소유권, MIR 및 백엔드](18-evaluation-ownership-mir-and-backends.md) |
| Prelude·공급자·진단·검증 증거 이해 | [Prelude, 공급자, 진단 및 적합성](19-prelude-providers-diagnostics-and-conformance.md) |
| 실제 gate가 있는 Preview 3건 검토 | [Preview Gated 상세 참조](20-preview-gated-reference.md) |
| 타입·객체·Trait Preview Design 검토 | [Preview Design — 타입, 객체 및 Trait](21-preview-design-types-objects-and-traits.md) |
| 컬렉션·문맥·제어 Preview Design 검토 | [Preview Design — 컬렉션, 문맥 및 제어](22-preview-design-collections-context-and-control.md) |
| 동시성·FFI·런타임 Preview Design 검토 | [Preview Design — 동시성, FFI 및 런타임](23-preview-design-concurrency-ffi-and-runtime.md) |
| 여러 기능이 만나는 전체 예제 읽기 | [통합 예제로 읽는 현행 Deeplus](24-integrated-worked-examples.md) |

생성된 [`SUMMARY.md`](SUMMARY.md)와 [`appendices/`](appendices/)는 모든
문법 생성 규칙, 기능 행, 진단, 검사기 술어, Prelude 항목과 검토된
예제를 이 참조서에 결합한다.

## 각 장의 구성

각 본문 장은 해당하는 범위에서 다음 순서를 따른다.

1. 상태 및 범위
2. 문법
3. 수용 규칙 및 정적 의미론
4. 평가, 소유권, 효과 및 실패
5. 현행 Deeplus 예제
6. 거부되었거나 상태 fence가 적용된 형식
7. 다른 기능과의 상호작용
8. 정확한 권위 추적

`00-status-authority-and-notation.md`는 표기법을 정의하는 메타 장이므로
이 순서의 적용 대상이 아니다. `02-programs-modules-and-imports.md`는
소스 루트에서 모듈·가져오기·가시성으로 이어지는 판정 순서를 보존하기
위해 문법과 정적 의미를 네 개의 주제 절로 펼친 구조적 예외다.
그 장의 “소스 루트”와 “모듈과 경로”는 문법, “import/use/export”와
“최상위 가시성”은 수용·정적 의미 및 범위 효과를 함께 담당한다.
`15-preview-recovery-and-removed-surfaces.md`는 현행 예제를 가르치는 장이
아니므로 다섯째 절의 이름을 “상태별 검토 예제”로 바꾸되 같은 증거
역할을 유지한다. 나머지 본문 장은 위 여덟 절을 그대로 사용한다.

문법만으로 판단할 수 있는 것은 토큰이 구조적 후보를 이룰 수
있는지까지다. 수용되는 Deeplus 프로그램은 소스 역할, 이름 해석,
타입, 소유권, 효과, 가시성 및 프로필 규칙도 모두 충족해야 한다.

## 상태 경계

| 레이블 | 의미 |
|---|---|
| `CURRENT` | 의미론 검사를 조건으로 안정 소스 루트가 수용하는 형식 |
| `PREVIEW_GATED` | 정확한 Preview 루트와 기능 gate를 통해서만 도달 가능한 형식 |
| `PREVIEW_NONACTIVATABLE` | 도입 검토에 필요한 설계는 갖추었지만 현행 소스 경로와 활성화 권위가 없는 형식 |
| `RECOVERY_ONLY` | 명확한 진단을 내기 위해서만 인식하며 수용된 AST/HIR/MIR 잔여물을 만들지 않는 형식 |
| `REMOVED` | 명시적인 현행 대안이 있는 역사적 또는 거부된 표기 |
| `LIBRARY` | 문법 키워드나 파서 내재 규칙이 아니라 Prelude 또는 제공자가 공급하는 항목 |
| `PRODUCT_NOT_RUN` | 설계 정적 증거만 존재하며 구현 지원을 주장하지 않는 상태 |

Preview 설계는 비활성 상태라는 이유로 이름만 나열해서는 안 된다. 도입
검토자가 현재 대안과 비교할 수 있도록 제안 동기, 정확한 구문 후보,
수용·의미 규칙, 다른 기능과의 상호작용, 진단·이행 영향, 미결정 사항 및
활성화 선행 조건을 기술한다. 그러나 이 문서화 자체는 구문, 구현 또는
제품 지원을 활성화하지 않는다.

## 작은 현행 예제

다음 소스는
[`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)의
`EX-R51a1-001`에서 수용된 현행 설계 예제로 분류된다. 파서와 검사기
실행은 여전히 `NOT_RUN`이다.

```deeplus
def#entry launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    print(args)
    return ExitCode::success
}
```

## 커버리지 보장

생성 규칙의 프로필별 수가 달라지거나, 생성된 색인이 오래되었거나,
레지스트리 구성원이 사라졌거나, 장 또는 링크가 누락되었거나, 생성된
부록을 직접 수정하면 참조서 생성기는 실패한다. 생성된
[`coverage-manifest.json`](coverage-manifest.json)은 현행 소스 트리의
정확한 바이트 식별값과 커버리지 기수를 기록한다.

기수 일치와 해시 결합은 “모든 행이 투영되었다”는 완전성 증거이지,
각 기능의 의미가 충분히 설명되었거나 제품에서 실행된다는 증거가
아니다. 이 판본은 그 차이를 줄이기 위해 production의 정확한 EBNF,
기능별 의존성·진단·예제 추적, 판정 알고리즘, 평가·실패·cleanup 추적과
Preview 50개 각각의 설명 예제를 별도로 제공한다. 그래도 대상 실행
확인서가 없는 구현·백엔드·도구 레인은 계속 `NOT_RUN`이다.
