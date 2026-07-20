# Decisions

언어 결정, 구현 ADR, 거버넌스 결정을 분리한다. current decision만 정본 우선순위에 참여하며 historical report는 current rule을 덮어쓰지 않는다.

`decisions/candidates/`는 Design_이 수용한 비정규·비활성 local candidate와 그 검토 영수증을 보존한다. 이 경로의 파일 존재는 `decisions/language/current-decisions.json`, current domain authority, source activation, implementation support 또는 product support를 변경하지 않는다.
