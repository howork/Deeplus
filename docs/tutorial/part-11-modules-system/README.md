# Part 11 — Module, Package, library boundary와 구현 파이프라인

> 상태: `MIXED_STATUS`
>
> Module/API/Prelude/HIR-H1 verifier boundary는 current design이다. FFI는
> 정확한 gate가 필요한 Preview이고 quarantine은 nonactivatable recovery
> probe다. compiler와 backend 제품 레인은 `15/15 NOT_RUN`이다.

이 Part는 source code만 보는 시야를 넓힌다. 이름은 어느 Module에서
보이는가, 어느 Package가 dependency를 소유하는가, public API가 어떤
identity를 남기는가, stdlib/provider와 언어 core는 어디서 갈라지는가,
source가 HIR-H1과 MIR을 거쳐 backend에 전달될 때 무엇을 보존해야 하는가를
다룬다.

읽을 때는 한 이름을 네 지도에 동시에 표시한다. Package graph에서는
배포·dependency owner, Module graph에서는 namespace·visibility owner,
API 표에서는 observable semantic responsibility, representation 표에서는
codec 또는 target ABI owner를 찾는다. 마지막으로 source→HIR-H1→MIR
단계에서 어느 결정이 닫히며 backend가 무엇을 재결정하면 안 되는지
추적한다. 이 네 지도를 합치지 않아야 file 이동, API 변경, wire migration,
backend 변경을 각각 정확한 검토 절차로 보낼 수 있다.

## 학습 순서

1. [Package, Module, import와 visibility](11-01-package-module-import-visibility.md)
2. [public API, schema와 serialization](11-02-public-api-schema-serialization.md)
3. [Prelude, provider와 console adapter](11-03-prelude-provider-console-adapter.md)
4. [FFI, unsafe와 quarantine](11-04-ffi-unsafe-quarantine.md)
5. [HIR-H1, MIR, backend와 tooling](11-05-hir-mir-backends-tooling.md)
6. [실습 — library package 설계](lab-11-library-package.md)

## 기준 예

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module acme::ledger::model

public schema EntryRow {
    id: EntryId
    amount: Rational
}
```

Module path는 namespace/visibility/source composition identity다. directory
path나 Package identity를 선언하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
private schema HiddenRow {
    value: Int
}

public def expose() -> HiddenRow = {
    return HiddenRow${ value: 1 }
}
// public API가 private identity를 노출한다.
```

## Part 불변 조건

- Package는 배포·의존성·빌드 단위, Module은 namespace·visibility·source
  composition 단위다.
- Module path와 file-system path는 같을 필요가 없다.
- `print`와 `readLine`은 canonical Prelude 63 entries에 없다.
- serialization identity를 Enum declaration order나 layout에서 추론하지 않는다.
- FFI는 exact Preview gate 없이는 current source가 아니다.
- HIR-H1 design boundary와 MIR-X1 draft implementation proposal을 섞지 않는다.

## 정본 지도

- [program/module/import](../../grammar-reference/02-programs-modules-and-imports.md)
- [Prelude/provider](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)
- [FFI/unsafe](../../grammar-reference/14-ffi-unsafe-metaprogramming-and-profiles.md)
- [evaluation/HIR/MIR/backend](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
