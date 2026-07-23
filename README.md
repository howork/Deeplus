# Deeplus 정본 작업공간

이 저장소는 Deeplus 언어 설계와 그 검증 자료의 일상 작업 정본이다.
현행 언어 버전은 `0.1.2-internal`, 명세 리비전은
`r51f3-current-grammar-reference-semantic-coherence-r1`이다. 정확한 값은
[`current/language-version.toml`](current/language-version.toml)에서
기계적으로 확인한다.

Deeplus는 프로그래머의 의도를 쉽고 일관되며 책임 있게 소스로 옮기는
표현력을 우선한다. 제한을 추가할 때에는 모호성을 숨기기보다 소유권,
효과, 실패, 격리 경계와 대안을 명시한다.

## 처음 읽는 순서

1. [문법 명세 및 언어 참조서](docs/grammar-reference/README.md)에서
   현행 문법과 의미론, Preview Design 및 예제를 주제별로 읽는다.
2. [현행 포인터](current/current-pointer.json)에서 버전, 상태와 열린
   action을 확인한다.
3. [언어 명세](spec/language.md)와 필요한 정확 정본을 대조한다.
   - [정확 문법](spec/grammar/deeplus.ebnf)
   - [Frontend 수용 모델](spec/frontend/frontend-model.json)
   - [타입 시스템](spec/types/type-system.md)
   - [MIR 관측 의미론](spec/mir/semantics.md)
4. [예제](examples/)와 [테스트 계약](tests/)으로 수용·거부 경계를
   확인한다.

참조서는 정본을 읽기 쉽게 묶은 생성·검증 문서 projection이다. 정본과
충돌하면 각 domain의 정확 정본이 우선한다. Preview Design의 문서화는
도입 검토를 돕지만, 그 자체로 활성화나 구현 지원을 뜻하지 않는다.

## 현재 검증 경계

- 문법 생성 규칙: `560`
  - `LEXICAL 89`
  - `STABLE 443`
  - `PREVIEW 13`
  - `RECOVERY 15`
- 기능 레지스트리: `688`
- 진단 레지스트리: `1,281`
- 타입 predicate: `247`
- Prelude 서명: `56`
- 예제 결과: `703`
- semantic P0: `0`
- 기능 P1: `22 OPEN`
- 별도 action: `M13-A002..005` 네 건 `OPEN`
- 제품 레인: `15/15 NOT_RUN`
- current binding: `false`

Rust crate는 lexer, parser, checker, MIR, xVM 또는 LLVM 제품 지원을
입증하는 구현물이 아니라 현재 책임 경계를 고정한 골격이다. 독립적인
target-bound 실행 확인서가 없는 제품 주장은 허용하지 않는다.

## 기본 검증

```text
python3 tools/generators/generate_grammar_reference.py --root . --check
python3 tools/validators/run_grammar_reference_generator_tests.py --root .
python3 tools/validators/validate_workspace.py
python3 tools/generators/generate_language_coherence_current_integrity.py --root . --check
python3 tools/generators/generate_language_coherence_current_integrity.py --root . --self-test
cargo check --workspace --locked
cargo test --workspace --locked
```

첫 두 명령은 한국어 참조서와 정확 정본의 결합 및 생성 결정성을
검사한다. workspace 검증기는 registry, schema, authority, 경로와
source-tree 폐쇄성을 검사한다. Cargo 명령은 저장소의 Rust 골격만
검사하며 제품 적합성 증거가 아니다.

대형 feature, diagnostic, predicate 및 example registry는 source
shard로 관리한다. R51f3 호환 projection이 필요하면 다음처럼 저장소
밖의 출력 경로에 재조립한다.

```text
python3 tools/generators/export_legacy_catalogs.py --output <output-directory>
```

## 변경 원칙

- 문법, 타입 또는 MIR 관측 동작을 바꾸면 해당 domain 정본과 추적
  registry를 함께 갱신한다.
- generated projection은 직접 편집하지 않는다.
- 언어의 design status와 product implementation status를 분리한다.
- `CURRENT`, `PREVIEW`, `RECOVERY_ONLY`, `REMOVED` 경계를 섞지 않는다.
- source, 문서, binary와 실행 evidence는 서로 다른 artifact identity로
  관리한다.

변경·검토·발행 규칙의 상세 내용은 [governance](governance/)에 있다.
