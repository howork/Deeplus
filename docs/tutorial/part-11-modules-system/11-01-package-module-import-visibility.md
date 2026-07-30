# 11-01 — Package, Module, import와 visibility

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

소스 역할과 name/visibility contract는 current design이다. Package manager,
manifest 문법과 linker 제품 실행은 확정되었다고 주장하지 않는다.

## 2. 학습 목표

- Package와 Module의 책임을 분리한다.
- 여섯 source root와 build-selected role을 설명한다.
- `import`, `use`, `export`의 정적 역할을 구분한다.
- public/common/private와 member visibility를 적용한다.

## 3. 선수 지식

선언, qualified path, scope, top-level과 member declaration을 알아야 한다.

## 4. 문제에서 출발하기

file directory를 namespace로, module을 배포 package로 간주하면 파일 이동과
dependency update가 같은 identity change처럼 보인다. Deeplus는 build
graph의 PackageId와 source의 ModulePath를 분리한다.

## 5. 핵심 모델

- Package: distribution, dependency resolution, build configuration,
  artifact/supply-chain identity.
- Module: namespace, visibility boundary, static resolution, source
  composition.
- fully resolved module: `(PackageId, ModulePath)`.
- source role: library, executable, script; 각 Preview 대응 root까지 여섯.
- manifest가 role/path를 공급하며 parser가 root를 추측하지 않는다.

한 Module은 여러 source contribution을 가질 수 있고 directory와
ModulePath가 달라도 된다.

## 6. 단계별 예제

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module acme::transport::http

public def request(url: String) -> Response
    throws NetworkError
    effects network
= {
    return sendRequest(url)
}
```

다른 Module은 exact qualified path를 import한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module acme::application
import acme::transport::http::{request}

private def load() -> Response
    throws NetworkError
    effects network
= {
    return request("https://example.invalid")
}
```

`import`는 runtime dynamic loading이 아니라 compile-time name graph 입력이다.

### R4: graph와 import binding을 닫기

다음 네 graph를 한 규칙으로 뭉치지 않는다.

| graph | cycle law |
|---|---|
| Package dependency | acyclic |
| re-export | acyclic |
| Module header | complete header collection 뒤 header/type/signature-only SCC 허용 |
| immutable static value | acyclic compile-time evaluation, atomic commit |

static value graph에는 runtime initializer가 없고, Module header SCC에는
static-value/runtime-initializer/re-export edge가 들어갈 수 없다.

한 import binding의 key는 scope, namespace, local name이다. 같은 target을
`as left`와 `as right`로 가져오면 두 binding이지만, 같은 scope에서
`as left`를 두 번 쓰면 duplicate다. declaration/dependency order는
우선순위가 아니다.

## 7. 허용·거부·경계 사례

scoped import/use는 block 안의 lexical frame만 만든다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def calculate(value: Decimal) -> Decimal = {
    use finance::rounding in {
        return value ~ rounded
    }
}
```

거부: public API가 narrower identity를 노출한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
common class PackageOnly {
}

public def reveal() -> PackageOnly = {
    return PackageOnly!()
}
```

type-producing top-level owner 9개는 explicit visibility를 요구한다. 그 밖의
optional top-level visibility omission은 private로 normalize될 수 있다.
member visibility `+`, `-`, `#`은 top-level words와 다른 domain이다.

## 8. 다른 기능과의 연결

- module API digest는 labels, responsibility, ErrorSet/effects를 보존한다.
- active extension set과 Trait evidence도 static name/link graph에 남는다.
- Package dependency graph는 ModulePath spelling만으로 identity를 합치지 않는다.
- `array`와 `case`는 ordinary identifier이며 path segment로도 사용할 수 있다.

### 판정 추적

하나의 source를 읽을 때 parser가 directory 이름으로 Module을 추측하게
두지 않는다. build graph가 먼저 PackageId, source role과 source path를
선택하고, source root의 `module` 선언이 ModulePath를 공급한다. 여러
source contribution이 같은 `(PackageId, ModulePath)`에 들어오면 선언
identity와 중복·visibility 규칙을 정적으로 결합한다. 그 다음에야
`import`/`use`가 lexical name frame을 만들고 `export`가 공개 표면을
재노출하는지 검사한다.

R4 trace는 `ImportBindingId`, `ImportTargetIdentity`,
`SourceOriginId`를 기록한다. `MODULE` namespace의 target은
`ModuleId`, `TYPE`·`VALUE`·`CALLABLE_OVERLOAD_SET`의 target은
`DeclId`다. Module target은 expression HIR를 만들지 않는다. Declaration
target이 식으로 사용될 때만 `ResolvedRef::DirectDecl(DeclId)`로
투영되며, import binding identity는 compile-time provenance로 남는다.

public API closure는 반환형만 보는 검사가 아니다. parameter type, generic
constraint, ErrorSet, context capability, selected witness와 field type까지
따라가며 더 좁은 visibility identity가 밖으로 새지 않는지 확인한다.
`common` identity는 같은 package의 협력에는 보일 수 있어도 다른
PackageId의 public consumer에게 자동 공개되지 않는다.

### 흔한 오해와 미니 사례

`src/acme/http.dp` 파일이 있다고 ModulePath가 자동으로
`acme::http`가 되는 것은 아니다. build mapping이 이 파일을
`transport::http` Module contribution으로 선택할 수 있고, 반대로 한
Module이 platform별 두 source contribution을 가질 수도 있다. 이 유연성은
서로 다른 선언을 임의로 합치는 권한이 아니라 명시적 build-selected
composition 계약이다.

`import`를 package 설치나 runtime dynamic load로 이해하는 것도
잘못이다. dependency version과 artifact는 Package graph가, source에서
보이는 이름은 Module import graph가 소유한다. 미니 사례에서 같은
`logging` ModulePath가 두 Package에 있어도 `(PackageId, ModulePath)`가
다르므로 이름만 보고 하나로 합치지 않는다.

### 설계 점검표

Module을 추가할 때는 배포 단위가 바뀌는지, namespace만 바뀌는지,
file mapping만 바뀌는지를 세 줄로 분리한다. 이어 source role, top-level
visibility, scoped import lifetime, public closure를 점검한다. 이 표를
사용하면 단순 파일 이동을 API breaking change로 과장하거나, 실제
Package dependency 변경을 namespace rename으로 축소하는 실수를 막는다.

visibility normalization도 domain별로 읽는다. type-producing top-level
owner에는 explicit `public`/`common`/`private`가 필요하지만, member의
`+`/`#`/`-` glyph는 각각 다른 member domain이다. top-level word를 Class
body에 쓰거나 member glyph를 Module declaration 앞에 붙이지 않는다.
ordinary top-level helper의 생략이 private로 normalize되는 경우와
type owner의 명시 의무도 구분한다.

미니 사례에서 public `OrderService`가 common `InternalClock`을 parameter,
field, ErrorSet 어느 곳에서든 노출하면 API closure가 실패한다. private
helper body 안에서만 `InternalClock`을 쓰는 것은 public signature에
residue가 없으므로 별도 판정이다. “함수 이름이 public인가”만 확인하는
검사로는 이 차이를 잡지 못한다.

같은 원칙을 generic constraint와 selected Trait evidence에도 적용한다.
겉으로 보이지 않는 narrower identity가 public responsibility에 남으면
closure 위반이다.

## 9. Deeplus다운 작성 관례

module 이름은 domain namespace를 표현하고 directory convention은 build
편의를 위해 선택한다. public surface를 작게 유지하고, common은 package
내 협력, private은 module implementation detail에 쓴다.

## 10. 연습 문제

1. **따라 하기:** `shop::catalog` module과 public `Product` schema를
   선언하라.
2. **빈칸 완성:** Package와 Module의 네 책임을 올바른 열에 배치하라.
3. **스스로 설계하기:** 하나의 package 안에 model, service, adapter
   module을 나누고 visibility를 정하라.

## 11. 빠른 복습

- Package와 Module은 다른 identity domain이다.
- file path와 ModulePath는 동일할 필요가 없다.
- import/use는 compile-time scope다.
- public API는 narrower visibility identity를 노출하지 않는다.

## 12. 정본 근거와 다음 장

- [program/module/import reference](../../grammar-reference/02-programs-modules-and-imports.md)
- [source roles contract](../../../spec/contracts/source-roles.json)
- [frontend source roots](../../../spec/frontend/frontend-model.json)

다음 장은 module boundary에 남는 schema, API digest와 serialization을
분리한다.
