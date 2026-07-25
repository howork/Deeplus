# 01-04. Package, Module과 source role

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 Stable source root, ModulePath, `import`/`use`, 최상위 가시성의
현행 설계를 설명한다. Package manifest 형식과 실제 build 실행은 이
정적 언어 문법과 별도의 제품 영역이다.

## 2. 학습 목표

- Package와 Module의 책임을 구분한다.
- ModulePath와 파일 시스템 경로가 같을 필요가 없음을 설명한다.
- library, executable, script source role의 차이를 안다.
- 한정 경로와 import 선택 목록을 읽는다.

## 3. 선수 지식

이름 있는 함수와 상태 표식을 알고 있어야 한다.

## 4. 문제에서 출발하기

파일 `src/network/client.dp`가 있다고 해서 그 Module 이름이 자동으로
`src::network::client`인 것은 아니다. 배포와 의존성은 Package가,
이름 공간과 가시성은 Module이 소유한다. build graph가 파일과
ModulePath의 대응을 정할 수 있지만 그 대응은 언어의 이름 동등성
규칙이 아니다.

## 5. 핵심 모델

| 개념 | 핵심 책임 |
|---|---|
| Package | 배포, dependency, build, artifact와 supply-chain identity |
| Module | namespace, visibility, static lookup, source 구성 |
| Source role | 한 파일이 최상위에 둘 수 있는 항목의 종류 |

Stable source root는 `LibrarySourceFile`, `ExecutableSourceFile`,
`ScriptSourceFile` 세 개다. ModulePath는 하나 이상의 identifier를
`::`로 연결한다. 완전한 Module identity는 PackageId와 ModulePath를
함께 가진다.

## 6. 단계별 예제

다음 library source는 Module을 선언하고 이름 하나를 선택 import한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::orientation

import tutorial::shared::{CourseName}

private def#pure courseLabel(name: CourseName) -> CourseName
    throws Never
    effects {}
= {
    return name
}
```

`module` 선언은 source 항목보다 앞에 온다. `import`는 이름을 가져오며,
`use`는 허용된 provider/extension 표면을 활성화하는 별도 역할이다.

`array`와 `case`는 일반 identifier다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure combine(array: Int, case: Int) -> Int
    throws Never
    effects {}
= {
    return array + case
}
```

두 단어를 keyword로 분류해서는 안 된다. Prelude의 `String`, `Record`,
`Sequence`도 language keyword가 아니라 정적으로 공급되는 binding이다.

### 판정 trace, 미니 사례와 흔한 오해

새 파일을 배치할 때는 먼저 배포 단위인 Package를 고르고, 그 안에서
선언이 소속될 ModulePath와 source role을 별도로 판정한다. 그다음
visibility가 어느 Module 경계를 넘어야 하는지 확인한다. 마지막으로
실제 파일 경로는 build manifest와 project convention이 정한다. 이
순서를 거꾸로 해 파일 이름에서 ModulePath를 자동 추론하면 source
재배치가 API identity를 바꾸는 잘못된 결과가 생긴다.

미니 사례로 하나의 Package가 `catalog::model`과 `catalog::service`
Module을 가진다고 하자. 구현 파일을 한 폴더에 두거나 여러 폴더로
나누더라도 Module declaration과 build mapping이 같으면 이름 공간
계층은 유지될 수 있다. 반대로 같은 디렉터리의 두 파일도 서로 다른
Module을 선언할 수 있다. 흔한 오해는 Package를 namespace, Module을
폴더 별칭으로만 이해하는 것이다. 의존성·artifact version은 Package,
이름 접근과 source 구성은 Module이 소유한다.

## 7. 허용·거부·경계 사례

명시적 가시성이 필요한 type owner에서 이를 생략하면 거부한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: TYPE_DECL_VISIBILITY_* -->
```deeplus
module tutorial::broken

type Label = String
```

`TypeAliasDecl`에는 `public`, `common`, `private` 중 하나가 필요하다.
반면 일반 module 함수는 가시성을 생략하면 `private`로 정규화될 수 있다.
script shebang이 library source에 script 문 권한을 주지는 않는다.

## 8. 다른 기능과의 연결

Module identity는 public API digest, conformance locality, extension
lookup과 연결된다. Package 경계는 `common` 가시성과 left-owner
fixed-glyph conformance의 locality를 결정한다. 지역 `import ... in {}`와
`use ... in {}`는 compile-time lexical frame이며 runtime 동적 로딩이
아니다.

## 9. Deeplus다운 작성 관례

- source 첫머리에서 ModulePath를 분명히 한다.
- directory convention은 편의를 위한 build mapping으로만 설명한다.
- dependency를 추가하는 일과 이름을 import하는 일을 구분한다.
- Package/Module을 한 단어처럼 쓰지 않는다.
- 유효한 `::` 경로를 중심으로 가르치고 잘못된 구두점은 필요할 때만
  진단한다.

## 10. 연습 문제

1. **따라 하기:** `module tutorial::math`와 `private def#pure identity`
   하나를 가진 library snippet을 작성한다.
2. **빈칸 완성:** Package는 `배포·___·build` 단위이고 Module은
   `namespace·___·source 구성` 단위다.
3. **스스로 설계하기:** 한 Package 안에 `catalog::model`과
   `catalog::service` 두 Module을 배치한다고 가정하고, 파일 경로와
   ModulePath mapping이 달라도 되는 예를 표로 만든다.

## 11. 빠른 복습

- Package와 Module은 같은 단위가 아니다.
- ModulePath와 디렉터리 계층은 동일할 필요가 없다.
- Stable source root는 library, executable, script 세 개다.
- 한정 경로는 identifier를 `::`로 연결한다.
- `array`와 `case`는 ordinary identifier다.

## 12. 정본 근거와 다음 장

- [source root와 Module EBNF](../../../spec/grammar/deeplus.ebnf)
- [프로그램·Module·import 참고서](../../grammar-reference/02-programs-modules-and-imports.md)
- [frontend source-role 모델](../../../spec/frontend/frontend-model.json)
- [current pointer](../../../current/current-pointer.json)

다음은 [이름, 바인딩, 블록](01-05-names-bindings-blocks.md)에서 Module
내부의 lexical scope를 배운다.
