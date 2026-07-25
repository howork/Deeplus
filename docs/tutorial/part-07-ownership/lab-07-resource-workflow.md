# Lab 7 — Resource workflow

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 목표

파일 session owner를 만들고 borrow로 읽으며, move로 archive 단계에
넘기고, 모든 failure path에서 cleanup을 정확히 한 번 수행하는 설계를
작성한다.

## 준비

- 7.1~7.5를 읽는다.
- Error, Defect, Cancellation, cleanup을 별도 축으로 기록한다.
- 예제를 실제 I/O PASS로 해석하지 않는다.

## 누적 프로젝트 연결

| 연결 | 내용 |
|---|---|
| input prior | Part 06 renderer가 borrow로 읽는 명목 값과 explicit evidence |
| output | FileSession owner의 borrow·move·cleanup이 드러나는 resource workflow |
| next | Part 08 view provenance와 NumericArray 임시 owner 책임 분석 |

## 1단계 — resource owner 선언

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public resource class FileSession {
    -let handle: Handle

    +def! new(handle: Handle)
        : super!()
    = {
        self.handle = handle
    }

    +def read.() -> Bytes
        throws IOError
        effects {io}
    = {
        return self.handle ~ readAll()
    }

    def#cleanup()
        throws CloseError
        effects {io}
    = {
        self.handle ~ close()
    }
}
```

constructor가 성공해야 session owner가 publish된다. cleanup responsibility는
그 owner에 붙는다.

## 2단계 — borrow와 move 경계

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def inspect(borrow session: FileSession) -> Int
    throws IOError
    effects {io}
= {
    let bytes = session ~ read()
    return bytes.length
}

private def archive(move session: FileSession) -> Unit
    throws IOError | CloseError
    effects {io}
= {
    let bytes = session ~ read()
    writeArchive(bytes)
}
```

`inspect`는 owner를 유지하고 `archive`는 owner와 최종 cleanup 책임을
받는다.

## 중간 점검

- [ ] `borrow` 함수는 session을 저장하거나 반환하지 않는다.
- [ ] move 성공 뒤 caller source place를 재사용하지 않는다.
- [ ] cleanup declaration의 effect/error를 숨기지 않는다.
- [ ] constructor 실패 시 partial session을 publish하지 않는다.

## End-to-end owner·failure trace

`run(path)`의 시작부터 종료까지 owner를 추적한다. 먼저 `openHandle`이
성공하면 construction session이 handle을 임시 소유한다. `FileSession!`
초기화와 invariant가 모두 성공해야 session owner가 한 번 publish된다.
constructor가 실패하면 handle을 정리하고 session publication은 영이다.
caller가 `inspect(borrow session)`을 호출하면 shared region만 열리며
owner와 최종 cleanup은 caller에 남는다.

`archive(move session)` admission 전 다른 argument나 준비 단계가
실패하면 source session은 live다. transfer commit 뒤에는 archive
callee가 owner와 cleanup을 책임지며 caller source를 다시 사용할 수
없다. archive body가 실패해도 owner를 caller로 되돌리는 척하지 않고
callee failure path에서 정확히 한 번 정리한다. 이 경계가 duplicate
close와 leak을 동시에 방지한다.

audit handle의 `defer audit ~ close()`는 등록 시 exact invocation과
place를 예약한다. 이후 main body가 정상 return, IOError, Cancellation
중 무엇으로 끝나도 cleanup은 정해진 LIFO 순서로 실행된다. body failure와
CloseError가 함께 생기면 primary/suppressed 정책을 보존하고 하나가
다른 하나를 조용히 지우지 않는다. cleanup 자체는 await하거나 spawn하지
않는다.

effect trace도 분리한다. open, read, archive write, close는 각각 `io`
책임을 갖고 signature budget 안에 있어야 한다. borrow 함수가 session을
저장하거나 callback에 넘겨 region을 연장하면 read 결과가 맞아도
ownership 판정은 실패다. 실제 filesystem 성공을 가정하지 않고 각
operation의 static error/effect row만 검토한다.

## Review rubric

1. **construction:** partial session publication이 영이고 handle cleanup이
   정확한가?
2. **borrow:** owner 유지, region, forbidden escape가 설명됐는가?
3. **move:** precommit failure와 postcommit callee 책임이 분리됐는가?
4. **cleanup:** 정상·Error·Cancellation에서 exactly once와 LIFO가
   유지되는가?
5. **effect/error:** I/O와 CloseError가 signature 및 ordering에
   드러나는가?
6. **상태:** 예제를 실제 filesystem/backend PASS로 해석하지 않는가?

각 항목을 `충족`, `부분 충족`, `재설계 필요`로 기록한다. 파일이 우연히
닫혔다는 한 번의 결과보다 모든 terminal path의 owner balance가
영인지가 중요하다. 이 rubric은 design-static 검토다.

## Rollback·owner·effect ledger

| 경계 | 실패 전 owner | 실패 효과 | 회수·cleanup 책임 |
|---|---|---|---|
| handle open | caller/path | session 미생성 | open API가 partial handle 회수 |
| constructor | construction session | `FileSession` publication 0 | 임시 handle 정리 |
| borrow inspect | caller session | owner 이동 0 | borrow region 종료 |
| move admission | caller session | transfer commit 0 | caller가 계속 책임 |
| move 이후 archive | archive callee | source 부활 금지 | callee가 exactly once 정리 |
| scope exit | audit owner | body failure 보존 | LIFO cleanup 후 suppressed 결합 |

ledger는 rollback을 owner 반환과 혼동하지 않게 한다. transfer commit 전
실패에서는 caller owner가 유지되지만, commit 뒤 실패에서는 callee가
책임을 끝낸다. 이미 수행한 archive write 같은 외부 `io` effect를
자동으로 되돌렸다고 주장하지 않으며, 보상이 필요하면 별도 operation과
error/effect 계약을 설계한다.

Cancellation도 각 경계에서 같은 owner balance를 요구한다. cleanup
barrier가 끝나기 전에 terminal cancellation을 publish하지 않고, close
실패가 생기면 정해진 primary/suppressed 순서를 따른다. 이 표는 실제
filesystem 동작을 증명하지 않으므로 모든 결과는 `NOT_RUN` 상태다.

검토 결과는 마지막에 owner 보존식으로 요약한다. 생성된 각 resource
owner는 정확히 한 terminal 책임자로 이어지고, move된 source와 이미
실행된 cleanup은 다시 세지 않는다. live owner가 남으면 누수이고 하나를
두 경로가 동시에 책임지면 중복 정리다. 이 보존식을 정상·오류·취소
경로에 각각 적용한 뒤에만 다음 단계로 넘긴다.

## 3단계 — 별도 audit handle을 defer로 관리

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def run(path: String) -> Unit
    throws IOError | CloseError
    effects {io}
= {
    let audit = openAudit()
    defer audit ~ close()

    let session = FileSession!(openHandle(path))
    let size = inspect(borrow session)
    audit ~ record size
    archive(move session)
}
```

audit cleanup은 scope exit에서 LIFO로 실행된다. session owner는 archive
call commit 뒤 callee로 이동한다.

## 실패 실험

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: OWNERSHIP_MODE_ADMISSION_FAILED; product: NOT_RUN -->
```deeplus
let session = FileSession!(openHandle(path))
archive(move session)
inspect(borrow session)
// OWNERSHIP_MODE_ADMISSION_FAILED
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL; product: NOT_RUN -->
```deeplus
defer {
    audit ~ flush()
    audit ~ close()
}
// 두 cleanup invocation으로 나누어 등록한다.
```

## 확장 과제

1. **복사:** audit `flush`와 `close`를 두 defer로 등록하고 실제 LIFO 순서를
   계산하라.
2. **빈칸 완성:** `archive`의 결과를
   `Result<___, error ___>`로 적고 `Unit`, `ArchiveError`를 채운 뒤,
   같은 실패를 `throws`에 중복하지 않는다.
3. **설계:** 이 workflow를 Actor에 넘길 때 enqueue commit 전후 owner,
   cancellation과 cleanup barrier를 표로 작성하라.

## 완료 체크리스트

- [ ] resource owner와 borrowed view를 분리했다.
- [ ] move commit 이후 source를 쓰지 않았다.
- [ ] defer는 단일 invocation이다.
- [ ] precommit failure에서 원 owner가 보존된다.
- [ ] body failure가 cleanup failure보다 primary다.
- [ ] product lanes `15/15 NOT_RUN`, OPEN P1 `22`를 유지했다.

## 정본 근거

- [소유권과 책임](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)
- [오류와 cleanup](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [MIR transaction](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
