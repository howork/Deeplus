# Deeplus Management R1.1 Prompt and Project Settings Amendment

## 1. 개정 결론

R1의 관리 원칙은 유지한다. R1.1은 다음 세 가지 혼동과 공백을 보완한다.

1. ChatGPT Project Settings에 넣을 8,000자 이하 영문 전역 지침을 별도
   텍스트로 제공한다. 이 영문 지침은 사용자 출력과 보고서를 한국어로
   작성하도록 명령한다.
2. 공통 Work 헌장과 보조 Chat 템플릿에서 Design_ 접두를 제거한다.
3. Design_이 release candidate마다 각 역할에 전달할 구체적 검토 요청문
   텍스트 pack을 의무적으로 만들게 한다.

## 2. Project Settings에 넣을 파일

**Deeplus_Project_Instructions_R1_1.txt**를 프로젝트 전역 지침으로 사용한다.

이 파일은 다음을 공통으로 강제한다.

- 사용자에게 보이는 결과와 보고서는 한국어
- 현재 pre-implementation 상태 유지
- Rust → typed HIR → Deeplus MIR → xVM → LLVM AOT/ORC JIT 아키텍처 고정
- receipt 없는 제품 lane은 NOT_RUN
- package-level modular authority와 source/generated/evidence 분리
- Work 5역할, 보조 Chat 역할, 역할별 메모리 경계
- 역할 Prefix·영문 파일명·상세 Markdown·중간파일·역할 범위 ZIP
- 매 릴리즈 역할별 보고서, 대안, 추가 감사자 지정, 다음 acceptance gate

## 3. 이전 Design_ 파일 세 개의 올바른 용도

| 이전 파일 | 실제 용도 | R1.1 처리 |
|---|---|---|
| Design_Deeplus_Shared_Work_Role_Charter_Prompt.txt | 5개 Work 역할 공통 헌장 | Deeplus_Shared_Work_Role_Charter_Prompt.txt로 이름 변경 |
| Design_Deeplus_Design_and_Release_Steward_Prompt.txt | Design_ 역할 전용 | 이름 유지 및 릴리즈 요청 pack 의무 추가 |
| Design_Deeplus_Auxiliary_Chat_Role_Template.txt | 보조 Chat 역할 범용 템플릿 | Deeplus_Auxiliary_Chat_Role_Template.txt로 이름 변경 |

즉, 실제 Design 역할 프롬프트는 두 번째 파일 하나다. 첫 번째와 세 번째는
Design이 관리할 수는 있어도 Design 역할 자체를 설명하지 않는다.

## 4. 사용 절차

### 4.1 평상시

1. ChatGPT Project Settings에 Deeplus_Project_Instructions_R1_1.txt를 넣는다.
2. Design_, Spec_, Impl_, Test_, Devel_ 각각의 Work 대화에 공통 Work 헌장과
   해당 역할 전용 프롬프트를 함께 넣는다.
3. 아이디어, 보안, 성능, FFI 등 보조 역할은 일반 Chat에서 보조 템플릿을
   범위에 맞춰 채워 사용한다.

### 4.2 릴리즈 후보

Design_은 RC identity와 source revision을 고정한 후, 다른 역할에 검토를
요청하기 전에 아래 요청문 pack을 만든다.

~~~text
Design_Deeplus_<release>_Review_Request_Pack.zip
├── Design_Deeplus_<release>_Review_Request_Design.txt
├── Design_Deeplus_<release>_Review_Request_Spec.txt
├── Design_Deeplus_<release>_Review_Request_Impl.txt
├── Design_Deeplus_<release>_Review_Request_Test.txt
├── Design_Deeplus_<release>_Review_Request_Devel.txt
└── Design_Deeplus_<release>_Auxiliary_Review_Assignment.txt
~~~

각 요청문은 반드시 다음을 적는다.

- release/RC identity와 source revision
- changed RFC, changed files, 필요한 입력
- 역할별 질문과 evidence boundary
- 실행했거나 아직 NOT_RUN인 lane
- 보고서 filename Prefix, deadline, handoff recipient
- 문제뿐 아니라 대안을 제출할 의무

보조 역할이 없으면 마지막 assignment 파일에 “없음”이라고만 쓰지 말고,
변경 위험과 matrix에 따라 불필요한 이유를 적는다.

## 5. Design_ 프롬프트의 새 의무

Design_은 이제 release decision을 통합하는 역할에 더해 다음을 책임진다.

1. role-specific review-request pack 생성
2. 5개 주요 역할에 정확한 입력과 질문 전달
3. 추가 Chat 역할의 필요성, blocking 여부, 이유 명시
4. release manifest에 pack path/digest와 assignment 기록
5. 보고서 제출 전 review pack을 바꾸면 변경 이력을 기록

이 절차는 모든 역할이 같은 RC를 검토하고, 서로 다른 baseline이나 불명확한
질문으로 인한 중복·누락을 줄이기 위한 것이다.

## 6. 검증 조건

- Project Settings 지침에 한국어, pre-implementation, 고정 아키텍처,
  NOT_RUN, Work/Chat, Library, 파일 및 릴리즈 규칙이 모두 존재한다.
- 공통 Work 헌장과 보조 Chat 템플릿은 Design_ 접두를 쓰지 않는다.
- Design 역할 프롬프트는 6개 release request 텍스트와 pack ZIP을 요구한다.
- 검증 도구는 새 전역 지침, 공통/보조 템플릿, 6개 요청문 템플릿의 존재를
  확인한다.
