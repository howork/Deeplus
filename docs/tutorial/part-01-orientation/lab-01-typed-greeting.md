# Lab 01. 타입이 있는 인사말

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

## 목표

ModulePath, 명시적 타입 alias, 순수 함수, immutable binding, 문자열
보간을 한 library source에 합친다. 결과는 design-static source이며
terminal 출력이나 runtime 실행을 가정하지 않는다.

## 준비

- [첫 설계 정적 프로그램](01-03-first-design-static-program.md)
- [Package와 Module](01-04-package-module-source.md)
- [이름과 바인딩](01-05-names-bindings-blocks.md)

완성할 함수는 이름과 반복 횟수를 받아 typed greeting 값을 만든다.
횟수는 `1..10` 범위로 제한한다.

## 단계별 구현

### 1단계: Module과 타입 경계 만들기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::labs::greeting

private type GreetingCount = 1..10
```

`GreetingCount`는 runtime wrapper를 발명하는 것이 아니라 정적 범위
identity를 가진 alias다. alias는 type-producing owner이므로 명시적
가시성 `private`를 붙인다.

### 2단계: 순수 변환 함수 추가하기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure typedGreeting(
    name: String,
    count: GreetingCount,
) -> String
= {
    return "[$count] 안녕하세요, $name"
}

let sample: String = typedGreeting(
    name: "Mina",
    count: 3,
)
```

layout argument form은 둘 이상의 all-named row에서 사용할 수 있다.
label은 runtime String이 아니라 선택된 callable의 parameter identity다.
인수 expression은 source order로 한 번씩 평가된다.

## 판정 trace

이 실습의 source를 검토할 때는 다음 순서로 기록한다.

1. `module tutorial::labs::greeting`이 library source의 ModulePath를
   완성하는지 확인한다. 이 이름을 파일 시스템 경로로 자동 변환하지
   않는다.
2. `GreetingCount`가 명시적 `private` visibility와 닫힌 `1..10`
   identity를 갖는지 확인한다.
3. `typedGreeting`의 두 parameter label과 argument label을 결합하고,
   각 argument expression은 source order로 한 번만 평가한다.
4. 문자열 보간 결과가 `String`인지, 정상 경로가 명시적 `return`으로
   끝나는지 확인한다.
5. body에 숨은 I/O나 authority가 없어 `def#pure`가 정규화한
   `throws Never effects {}`와 일치하는지 확인한다.

이 trace는 실행 순서를 흉내 내는 것이 아니라 어느 정적 owner가 어떤
결정을 내리는지 정리한다. 한 단계가 실패하면 뒤 단계의 제품 실행을
상상하지 않는다.

## 중간 점검

- ModulePath는 `tutorial::labs::greeting`인가?
- `GreetingCount`에 명시적 가시성이 있는가?
- 함수 정상 경로가 `String`을 명시적으로 `return`하는가?
- 생략해 표시한 빈 error/effect row가 순수 profile과 맞는가?
- I/O나 존재가 확인되지 않은 `print`/`readLine`을 사용하지 않았는가?

## 실패 실험

범위 밖 literal은 정적으로 허용되지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: REFINEMENT_* -->
```deeplus
let invalidCount: GreetingCount = 0
```

checker가 exact literal 모순을 증명하면 binding을 만들지 않는다. 실패를
runtime clamp로 바꾸거나 `1`로 자동 보정해서는 안 된다.

## 흔한 오해와 미니 사례

첫 번째 오해는 `GreetingCount`를 단순 설명용 주석처럼 보는 것이다.
`0`이나 `11`은 이름이 친절하지 않아서가 아니라 declared range와 exact
literal이 모순이어서 거부된다. 두 번째 오해는 all-named call을 Record
하나를 넘기는 호출로 보는 것이다. 여기서는 `name`과 `count`라는 두
formal parameter에 label이 각각 결합한다. Record/named-rest는 뒤의
Part에서 별도 구조로 배운다.

미니 사례로 `typedGreeting(count: 3, name: "Mina")`처럼 source 순서를
바꾸어도 label binding은 동일하다. 하지만 argument expression의 평가는
적힌 순서를 따른다. literal만 있을 때는 차이가 관찰되지 않지만 나중의
effectful expression에서도 이 원칙은 유지된다. 이 실습에서는 label
결합과 평가 순서를 표의 서로 다른 열에 적어 보라.

## 확장 과제

1. **따라 하기:** `sample`의 이름과 횟수를 바꾸고 설계상 만들어질
   문자열을 적는다.
2. **빈칸 완성:** `private def#pure title(name: String) -> ___`의 반환
   타입과 `return "학습자: $name"` body를 완성한다.
3. **스스로 설계하기:** `CourseName` alias와 이름을 추가해
   `"[3] Mina - Deeplus"` 모양의 값을 만드는 순수 함수를 설계한다.
   모든 parameter와 return type을 명시한다.
4. **심화:** raw `Int`를 `GreetingCount`로 검사할 때 숨은 clamp 대신
   `raw as? GreetingCount`가 만드는 `Option<GreetingCount>` 경계를
   설명한다.

## 누적 프로젝트 연결

| 구분 | 이 실습의 artifact |
|---|---|
| 이전 입력 | Part 1에서 만든 ModulePath, 명시적 type visibility, pure callable 규칙 |
| 이번 출력 | I/O와 분리된 `typedGreeting` 값 변환과 `GreetingCount` 경계 |
| 다음 handoff | Lab 02가 이 pure core를 보존한 채 exact numeric 값과 평가 순서를 추가 |

다음 실습에서 이 파일을 실제로 import하거나 실행했다고 가정하지 않는다.
누적되는 것은 먼저 설계한 경계와 설명 가능한 판정 trace다. 새 기능을
더할 때도 기존 pure core의 error/effect 책임을 넓혔다면 그 변화를
명시적으로 기록한다.

## 완료 체크리스트

- [ ] 지정된 ModulePath를 사용했다.
- [ ] Package와 Module을 같은 개념으로 설명하지 않았다.
- [ ] 명시적 type visibility를 보존했다.
- [ ] local 값은 기본적으로 `let`을 사용했다.
- [ ] non-Unit 경로에 명시적 `return`이 있다.
- [ ] 예제 상태가 CURRENT design-static/product NOT_RUN으로 표시되었다.
- [ ] 실행 PASS나 product support를 주장하지 않았다.

## 정본 근거

- [통합 문법](../../../spec/grammar/deeplus.dpg)
- [프로그램과 Module](../../grammar-reference/02-programs-modules-and-imports.md)
- [타입·refinement](../../grammar-reference/04-types-generics-and-refinement.md)
- [함수와 호출](../../grammar-reference/05-functions-methods-closures-and-calls.md)
