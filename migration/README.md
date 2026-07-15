# R51f3 Migration M1

이 디렉터리는 기존 immutable R51f3 release에서 안정 경로 작업공간으로 옮긴 방법과 추적성을 기록한다. 이전 release ZIP을 중첩하지 않는다.

- `import-manifest.json`: 원본 파일, 해시, disposition, current path
- `path-aliases.json`: legacy filename을 stable path 또는 import provenance로 해석하는 규칙
- `catalog-reassembly.json`: source shard가 원본 registry object와 동일함을 검사하는 계약
- `migration-receipt.json`: migration validator 결과

`ARCHIVE_ONLY_*` disposition은 정보 폐기를 뜻하지 않는다. 기존 immutable R51f3 release가 archival authority이며, 새 workspace에서는 중복 projection을 작업 정본으로 복제하지 않는다는 뜻이다.

