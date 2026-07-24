<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# 프로그램, 모듈, 임포트 및 가시성

## 상태

여기에서 설명하는 소스 루트, 모듈 경로, import, use, export 및 최상위
가시성은 `CURRENT`다. 이는 정적 설계이며, 제품의 파싱, 이름 해석 및
링크 실행은 계속 `NOT_RUN`이다.

## 소스 루트

정확히 하나의 소스 역할 루트가 컴파일 단위를 소유하며 입력 끝까지
반드시 소비해야 한다.

| 루트 | 용도 | 최상위 허용 항목 |
|---|---|---|
| `LibrarySourceFile` | 재사용 가능한 라이브러리 단위 | import/use, 선언, 최상위 바인딩 |
| `ExecutableSourceFile` | 실행 단위 | import/use, 비결합 선언, 허용된 `def#entry` 표면 하나 |
| `ScriptSourceFile` | 스크립트 단위 | 선택적 shebang, import/use, 비결합 선언, 문 |
| `PreviewLibrarySourceFile` | gate가 있는 라이브러리 단위 | `PreviewGate` 뒤 허용된 Preview/Stable 라이브러리 항목 |
| `PreviewExecutableSourceFile` | gate가 있는 실행 단위 | `PreviewGate` 뒤 허용된 Preview/Stable 실행 항목 |
| `PreviewScriptSourceFile` | gate가 있는 스크립트 단위 | 선택적 shebang, `PreviewGate`, 허용된 Preview/Stable 스크립트 항목 |

소스 역할 루트는 위의 stable 3개와 Preview 3개, 정확히 6개다. Preview
파일은 대응하는 `Preview*SourceFile` 루트와 정확한 `#preview(...)`
gate를 사용한다. 복구 구문은 별도의 일곱 번째 프로그램 종류가 아니다.

```ebnf
Deeplus ::= LibrarySourceFile | ExecutableSourceFile | ScriptSourceFile ;
LibrarySourceFile ::= ModuleDecl? LibrarySourceItem* ;
ExecutableSourceFile ::= ModuleDecl? ExecutableSourceItem* ;
ScriptSourceFile ::= Shebang? ModuleDecl? ScriptSourceItem* ;
```

## 모듈과 경로

한정 경로는 하나 이상의 식별자 segment로 이루어지고, 둘 이상의
segment는 `::`로 연결한다. 따라서 `core`와 `acme::commerce::orders`는
모두 `QualifiedPath`다. 모듈 선언이 있다면 나머지 소스 항목보다 앞에
와야 한다.

```ebnf
ModuleDecl ::= "module" QualifiedPath StatementBoundary ;
QualifiedPath ::= Identifier ("::" Identifier)* ;
```

학습 경로에서는 위의 유효한 형태를 중심으로 설명한다. 잘못된 구두점
형태를 장마다 반복해 암기시키지 않으며, 실제 오류가 발생했을 때만
진단 카탈로그가 해당 source span과 정정안을 제시한다.

### Package와 Module은 다른 단위다

| 개념 | 소유하는 책임 |
|---|---|
| Package | 배포, 의존성 해석, build 설정, 산출물 및 supply-chain identity |
| Module | 이름 공간, 가시성 경계, 정적 이름 해석, source 구성 |

Package identity는 build manifest와 해석된 dependency graph가 부여한다.
소스의 `module` 선언은 Package를 선언하거나 배포 단위를 만들지 않는다.
반대로 하나의 Package는 여러 Module을 포함할 수 있다. 완전히 해석된
Module identity는 `(PackageId, ModulePath)`이므로, 서로 다른 Package가
같은 `ModulePath` 철자를 사용해도 같은 Module이 아니다.

ModulePath와 파일 시스템 경로는 별개다. 예를 들어 build manifest가
다음과 같이 대응시킬 수 있다.

```text
파일: src/network/client.dp
PackageId: acme.transport@2
ModulePath: transport::http
```

이때 파일의 directory가 `transport/http`와 같을 필요는 없다. 프로젝트는
directory convention을 기본 mapping으로 사용할 수 있지만 그것은 build
규칙이지 언어의 이름 동등성 규칙이 아니다. 파일 이동만으로 Module
identity가 바뀌어서도 안 된다.

한 Module은 build graph가 허용한 여러 source contribution으로 구성될 수
있다. 각 파일의 명시적 `module` 선언은 mapping된 ModulePath와 같아야
하고, 선언을 생략하면 mapping된 path를 사용한다. 여러 contribution의
중복 선언이나 충돌은 public API digest를 만들기 전에 거부하며 source
순서를 identity나 충돌 해소 규칙으로 사용하지 않는다.

`array`와 `case`는 일반 식별자다. 이를 키워드로 어휘 분석하거나
가르쳐서는 안 된다. `String`, `Record`, `Sequence`와 같은 Prelude 이름은
바인딩이며 키워드가 아니다.

## `import`, `use` 및 `export`

`import`는 모듈에서 이름을 가져온다. 별칭 또는 정확한 선택 목록을
지정할 수 있다. `use`는 허용된 제공자 또는 확장 표면을
활성화한다. `use export`는 그 권위가 허용하는 범위에서 해당 활성화를
다시 내보낸다.

```ebnf
ImportDecl ::= "import" QualifiedPath ImportTail? StatementBoundary ;
ImportAlias ::= NameAliasClause ;
ImportSelection ::= "::" "{" IdentifierList "}" ;
UseDecl ::= "use" QualifiedPath StatementBoundary ;
UseExportDecl ::= "use" "export" QualifiedPath StatementBoundary ;
```

블록 지역 `import ... in { ... }`과 `use ... in { ... }`는 컴파일 시간의
이름 또는 제공자 범위다. 모듈을 동적으로 불러오지 않는다. 독립적으로
허용된 값이 범위에 한정된 권위를 전혀 운반하지 않는 경우가 아니라면,
가져온 이름과 제공자 후보가 블록 밖으로 빠져나가서는 안 된다.

`export`는 공개 API 잔여물을 기록한다. 가시성, 소유권, 일관성 또는
모듈 시그니처 검사를 우회하지 않는다.

## 최상위 가시성

최상위 타입 선언은 다음 세 가지 명시적 영역 중 하나를 사용한다.

| 철자 | 가시성 영역 |
|---|---|
| `public` | 외부 패키지 API에 들어갈 수 있지만, 허용된 `export` 또는 모듈 인터페이스를 통해서만 가능 |
| `common` | 선언 패키지의 모듈 전체에서 보이지만, 외부 패키지 API와 재내보내기에서는 제외 |
| `private` | 선언한 모듈 내부에서만 보임 |

명시적 단어가 반드시 필요한 type-producing owner는 정확히 다음
9개다.

1. `ClassDecl`
2. `TraitDecl`
3. `EnumDecl`
4. `TypeAliasDecl`
5. `SchemaDecl`
6. `ActorDecl`
7. `ActorProtocolDecl`
8. `TypestateResourceDecl`
9. `BitfieldDecl`

이 법칙은 위의 6개 source root에 동일하게 적용된다. 이 9개 owner에서
가시성을 생략한 parse는 recovery에만 존재하며
`TYPE_DECL_VISIBILITY_REQUIRED`를 낸다. 그 결과에서 admitted HIR type
node, type identity, API-digest entry는 모두 0이다. 그 밖에
`TopLevelVisibility?`를 가진 최상위 owner는 단어를 생략하면
`private`로 정규화한다.

패키지 식별자는 빌드/모듈 그래프에서 오며, `common`은 새로운 패키지
선언 구문을 추가하지 않는다. 선언은 그 시그니처 의존성보다 넓은
영역에서 관찰되어서는 안 된다. 따라서 공개 API 잔여물은 `common`
또는 `private` 식별자를 노출하는 `public` 선언을 거부한다.

멤버 가시성은 최상위 단어 대신 `+`, `-`, `#`을 사용한다. `#`은 선언한
명목 타입과 그 명목 하위 클래스를 뜻한다. 관계없이 이를 준수하는
타입이나 구조적으로 비슷한 타입에 접근 권한을 부여하지 않는다.

## 현행 예제

`EX-R51a1-001`은 실행 루트 예제다.

```deeplus
def#entry launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    print(args)
    return ExitCode::success
}
```

`EX-R51a1-038`은 모듈 시그니처를 보여 준다.

```deeplus
module signature API {
    export Item
}
```

`EX-R51a1-IMPORT-P-001`은 블록 지역 import를 보여 준다.

```deeplus
def ask() -> Int
= {
    import std::inout::input
    return input("n:") ~ toInt()
}
```

이 예제들은
[`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)의
현행 정적 설계 예제이며, 제품 지원은 계속 `NOT_RUN`이다.

## 거부되거나 상태 경계로 격리된 형식

- 소스 역할 루트는 EOF까지 반드시 소비해야 하며, 뒤에 남는 소유되지
  않은 토큰은 거부된다.
- 라이브러리 단위가 shebang으로 시작하더라도 스크립트 전용 문 동작을
  얻을 수 없다.
- 지역 import는 실행 시간 로딩이 아니며 조건부 실행 시간 권위가 될 수
  없다.
- 중첩 지역 함수에는 `public`, `common`, `private`를 붙일 수 없다.
- 멤버에서 `+`, `-`, `#` 대신 최상위 가시성 단어를 사용할 수 없다.
- `common` 선언은 자신의 패키지 밖으로 내보낼 수 없다.
- Preview FFI 선언에는 Preview 루트와 gate가 필요하다. [FFI 및
  프로필](14-ffi-unsafe-metaprogramming-and-profiles.md)을 참조한다.

## 상호작용

- 소스 역할은 루트에 나타날 수 있는 선언과 문을 제한한다.
- 가시성은 명목 식별자와 공개 API 잔여물의 일부다.
- Trait 증거와 확장 후보는 이름 해석 지점과 링크 검증
  시점에서 보여야 한다.
- 범위가 있는 import와 use는 이름 해석에 영향을 주지만 소유자 사실,
  적합성 증거 또는 실행 시간 권위를 만들어 내지는 않는다.

## 권위 추적

- `spec/grammar/deeplus.ebnf`: `Deeplus`, `*SourceFile`, `ModuleDecl`,
  `ImportDecl`, `UseDecl`, `UseExportDecl`, `ExportDecl`,
  `TopLevelVisibility`
- `spec/frontend/frontend-model.json`: `source_roots`,
  소스 역할 및 가시성 허용
- `spec/language.md`: 소스 파일, 이름, 선언 가시성, 모듈
- `spec/types/type-system.md`: 링크 식별자 및 공개 API 잔여물
