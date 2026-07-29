# 11-03 — Prelude, provider와 정직한 console adapter

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

Prelude 63 entries와 provider separation은 current design이다. 현재
signature catalog에는 `print`와 `readLine`이 없다. 이 장은 둘을 canonical
Prelude처럼 가르치지 않는다.

## 2. 학습 목표

- keyword, Prelude identity, provider, runtime service를 구분한다.
- Prelude signature catalog의 authority를 찾는다.
- pure core와 application-owned I/O adapter를 분리한다.
- 문서 예시의 편의 이름을 canonical API로 오인하지 않는다.

## 3. 선수 지식

Module import, context capability, effects/throws, Trait associated static을
알고 있어야 한다.

## 4. 문제에서 출발하기

튜토리얼의 “Hello” 예제는 흔히 `print`부터 시작한다. 그러나 이름을
보여 주는 순간 독자는 그 함수의 type, effect, error, encoding, authority가
정의되었다고 기대한다. 현재 Deeplus Prelude catalog에는 그 계약이 없다.
따라서 pure program core와 host/application adapter를 분리해 정직하게
설명한다.

## 5. 핵심 모델

- keyword: scanner/parser가 소유.
- Prelude: canonical language-facing type/protocol/signature identity.
- compile-time provider: source/tooling artifact를 만들되 runtime authority를
  주입하지 않음.
- runtime service: ordinary constructed/injected value와 lifecycle.
- application adapter: project가 소유한 explicit boundary; Prelude가 아님.

`Task`, `String`, `Result`가 Prelude에 있어도 keyword가 되지 않는다.
Prelude 이름이 없으면 tutorial convenience function으로 몰래 승격하지
않는다.

## 6. 단계별 예제

먼저 pure core를 작성한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def greeting(name: String) -> String
    throws Never
    effects {}
= {
    return String::render("안녕하세요, ${name}")
}
```

I/O가 필요하면 application-owned capability와 adapter signature를
명시한다. 아래 `AppConsole`과 helper는 이 예제 package가 정의한 것이며
Prelude가 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public capability AppConsole for {io}

public def writeGreeting(name: String, context console: AppConsole) -> Unit
    throws ConsoleError
    effects io
= {
    return appWriteLine(greeting(name), context console)
}
```

pure test는 console 없이 `greeting("Dee")`의 String 결과를 판정할 수 있다.

## 7. 허용·거부·경계 사례

허용: application adapter라는 owner를 명시한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::adapter::console

public def normalizeInput(text: String) -> String
    throws Never
    effects {}
= {
    return text ~ trim
}
```

거부되는 문서 주장:

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let name = readLine()
print(greeting(name))
// 이 두 이름의 canonical Prelude signature가 있다고 이 튜토리얼은 주장하지 않는다.
```

기존 review corpus의 편의 예시가 language surface를 보여 주더라도 Prelude
contract와 target execution을 자동 증명하지 않는다.

## 8. 다른 기능과의 연결

- `<T as Trait>::item`은 selected conformance의 associated static이며
  runtime service fallback이 아니다.
- `Type::item`, named extension, Trait-qualified static, runtime owner는
  네 lookup domain이다.
- provider output은 ordinary source로 재검사되어야 하며 hidden witness나
  capability를 만들지 않는다.
- console adapter가 effect/error/capability를 숨기면 public API identity도
  불완전하다.

### 판정 추적

익숙한 이름을 보았다고 곧바로 Prelude에서 찾지 않는다. 먼저 keyword
domain인지, 현재 Module/import의 value인지, canonical Prelude catalog
entry인지 확인한다. type-associated static, Trait-qualified static,
named extension member, constructed runtime service도 각자의 lookup
domain에서만 찾는다. 어느 domain에도 exact identity가 없으면 host가
알아서 제공한다고 가정하지 않는다.

I/O adapter를 설계할 때는 pure core의 input/output을 먼저 닫고, 바깥
Module에 capability, effect row, ErrorSet, encoding과 lifecycle을 드러낸
ordinary API를 둔다. test에서는 in-memory adapter가 같은 contract를
구현할 수 있지만 그 사실이 host console 제품 실행이나 canonical
Prelude 승격을 뜻하지 않는다.

### 흔한 오해와 미니 사례

provider가 compile time에 artifact를 만들 수 있으므로 runtime capability도
주입할 수 있다고 생각하는 것은 잘못이다. provider output은 ordinary
source로 다시 검사되며 hidden witness, ambient service와 I/O 권한을
합성하지 않는다. 튜토리얼 fixture의 `print`/`readLine` host adapter와
`assert` test oracle도 fixture owner가 명시될 때만 사용할 수 있다.

미니 사례로 점수 계산은 `formatScore(score) -> String`인 pure core에
둔다. 화면 출력은 `writeScore(..., context console: AppConsole)`이
소유하고 `{io}`와 `ConsoleError`를 기록한다. unit test는 첫 함수의
String만 비교하며 host output 순서나 console availability를 언어
보장으로 만들지 않는다.

adapter contract에는 이름 외에도 encoding, newline policy, flush,
end-of-input, resource lifecycle을 기록한다. `readLine`이라는 편의 이름만
쓰면 EOF가 Option인지 Error인지, newline을 포함하는지, decoding 실패를
어디에 두는지 알 수 없다. project-owned API는 이 선택을 반환 type,
ErrorSet과 문서에 명시하고 pure parser에는 이미 decode된 String만
전달한다.

test double도 authority를 숨기지 않는다. in-memory console은 입력 queue와
출력 collection을 application fixture가 소유하고, deterministic oracle은
그 collection을 비교한다. 이 test가 통과해도 terminal encoding, 실제
flush, OS error 경로는 별도 host execution receipt가 필요하다. fixture의
친숙한 helper 이름을 Prelude catalog에 등록된 것처럼 문서화하지 않는다.

이 경계를 문서와 example metadata에도 반복해 독자가 convenience API를
정본 언어 surface로 복사하지 않게 한다.

## 9. Deeplus다운 작성 관례

핵심 계산은 pure 함수로, 외부 세계와의 통신은 좁은 explicit adapter로
분리한다. 아직 정본화되지 않은 친숙한 이름을 편의상 사용하기보다
authority와 책임을 드러낸 project-owned API를 선언한다.

## 10. 연습 문제

1. **따라 하기:** pure `formatScore` 함수를 만들고 String을 반환하라.
2. **빈칸 완성:** application console adapter에 필요한 context capability,
   `effects ___`, `throws ___`를 채워라.
3. **스스로 설계하기:** test용 in-memory adapter와 host adapter가 같은
   pure core를 공유하도록 module 경계를 설계하라.

## 11. 빠른 복습

- Prelude name과 keyword는 다르다.
- `print`/`readLine`은 현재 canonical Prelude entry가 아니다.
- pure core와 explicit adapter를 분리한다.
- provider/runtime service/capability는 서로 fallback하지 않는다.

## 12. 정본 근거와 다음 장

- [Prelude/provider reference](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)
- [Prelude catalog](../../../library/prelude/signatures/catalog-metadata.json)
- [companion capability contract](../../../spec/contracts/companion-capability-coherence.json)

다음 장은 external ABI와 unsafe authority를 current core에서 격리한다.
