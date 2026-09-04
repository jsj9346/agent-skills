---
name: define-ui
description: >-
  제품 UI를 구현하기 전에 특정 route·component·screen set·새 앱의 화면 구조,
  사용자 흐름, 상태, 반응형 동작과 완료 기준을 UI 명세로 정의할 때 사용한다.
  코드를 바로 구현하거나 완성된 화면을 검토하거나 시스템·API 경계를 설계하는
  요청에는 사용하지 않는다.
---

# Define UI

구현 전에 화면·흐름·상태·반응형 규칙과 관측 가능한 acceptance checks를
`ready-for-build` UI 명세로 만든다. 제품 UI 소스·테스트·빌드 설정은 변경하지 않는다.

## 먼저 경계를 판정한다

- 무엇을 왜 만들지 자체가 갈리면 화면 구조로 결정하지 않고 `interview`로 넘긴다.
- 시스템 경계·데이터·인터페이스 설계는 `make-design`의 영역이다.
- 구현이 성공 산출물이면 `design-ui`, 구현된 UI의 독립 검토는 `review-ui`를 사용한다.
- 구현 없는 래스터 시안이 목표면 이미지 도구로 넘긴다.
- 공개·배포는 프로젝트 배포 절차와 사용자의 승인 영역이다.

작은 국소 구현이나 이미 충분히 구체적인 구현 요청에 UI 명세를 강제하지 않는다.

## 계약을 읽는다

요청 정규화, `UiTarget`, 명세 선택, lifecycle, authority와 acceptance schema는
[UI 정의 계약](references/ui-definition-contract.md)을 읽고 그대로 적용한다. 새 명세를
작성할 때는 [UI 명세 템플릿](assets/UI-SPEC.template.md)을 프로젝트 규약에 맞춰 복사한다.
프로젝트에 명세 위치 규약이 없으면 `design/specs/<target-slug>.md`를 사용한다.
`<target-slug>`는 저장 경로용 파생값이지 target identity가 아니다.

## Preflight

제품 파일을 바꾸지 않고 저장소 지침, 관련 디자인 정본, 기존 명세와 UI를 확인한 뒤
요청을 `DefineUiRequest`로 정규화한다. preflight 결과는 세 가지뿐이다.

1. `Ready`: canonical target과 user-visible goal이 특정되고 명시 명세 target과 충돌하지
   않는다.
2. `NeedsClarification`: `target.kind`, `target.key`, goal 중 하나 이상을 추측해야 한다.
   known context, non-empty missing 목록, 화면에 미치는 영향, 질문 하나, 재개 조건을
   보고한다.
3. `TargetConflict`: 별도 target과 명시 명세의 canonical target이 다르다. 두 target,
   명세 경로, 영향, 필요한 결정과 재개 조건을 보고한다.

`NeedsClarification`과 `TargetConflict`에서는 UI 명세 파일·ID·status를 만들지 않고 제품
소스도 변경하지 않는다. 답이나 해소 결정을 받으면 이전 phase를 추측하지 말고 preflight를
처음부터 다시 평가한다. `Ready` 뒤에만 `DraftUiSpec`을 만들고 `Intake`로 들어간다.

## 기존 명세를 선택한다

`intent: revise` 또는 같은 target 명세의 reuse는 canonical `(kind, key)` exact match인
후보에만 다음 순서를 적용한다.

1. 사용자가 명시한 정확한 명세 경로
2. 프로젝트가 해당 target의 active 명세로 지정한 정확한 경로
3. 같은 target의 `ready-for-build` 후보가 정확히 하나인 경우
4. 그 밖에는 `NeedsInput`과 후보 경로 목록

명시 경로가 non-ready이면 다른 ready 명세로 fallback하지 않는다. ID·파일명·표시 이름·
mtime·날짜·사전식 순서·alias로 같은 target이나 최신 명세를 추측하지 않는다. 선택된 기존
명세를 in-place 갱신하며, active 지정은 사용자 요구나 프로젝트 계약 없이 바꾸지 않는다.

## UI를 정의한다

runtime phase와 persistent status를 분리한다.

1. `Intake`: preflight와 초기 명세의 target·intent·goal을 대조한다.
2. `AuthorityReady`: 저장소 지침, target 명세, 디자인 정본, 토큰, 공용 컴포넌트, 기존 UI,
   참고물의 접근성을 우선순위대로 확인한다.
3. `DefinitionDrafting`: 사용자 흐름, 화면·영역, 실제 필요한 상태, interaction,
   accessibility expectation, responsive rules, reuse·extend·new 경계를 정의한다.
4. `DecisionCheck`: 제품 방향 미결을 회부하고 acceptance checks의 관측 가능성과 유효한
   owner/evidence 조합을 확인한다.
5. `ReadyForBuild`: `unresolved: []`, `failure: absent`, `status: ready-for-build`을 한 번에
   기록한다.
6. `Done`: 명세 경로와 handoff를 보고하며 저장 status는 바꾸지 않는다.

정상 `Intake`부터 `DecisionCheck`까지는 phase를 파일에 저장하지 않고 `status: draft`를
유지한다. 실패 진입 시 대응 status·failure·unresolved를 원자적으로 기록한다. 재개 조건을
확인한 뒤에만 failure를 제거하고 `draft`로 되돌려 계약의 `resume_at`에서 재개한다. 정상
phase 도중 남은 draft는 다음 실행에서 `Intake`부터 다시 대조하며 filename·mtime·부분
내용으로 phase를 복원하지 않는다.

## 참고물 접근 실패

- reference 번역이 주목적이고 주 reference에 접근할 수 없으면 `ReferenceBlockedFailure`로
  끝낸다. 보이지 않는 내용을 꾸며내지 않는다.
- 부차 reference가 없으면 나머지 authority로 계속한다.
- 사용자가 reference와 독립적인 fallback 범위를 명시적으로 승인한 경우에만 그 범위로
  계속한다.

접근 불가 주 reference 때문에 stable screen/flow 이름 자체를 알 수 없으면
`UnknownTargetScope { target, reason }`를 쓴다. 이름을 아는 경우에는 non-empty
`KnownAffectedScope`를 사용한다. 다른 failure variant에는 unknown scope를 쓰지 않는다.

## Ready gate

다음 중 하나라도 있으면 `ready-for-build`로 표시하지 않는다.

- 제품 방향을 바꾸는 미결
- 접근하지 못한 주 reference를 본 것처럼 쓴 규칙
- 관측할 수 없는 acceptance check
- 계약 밖 owner/evidence 조합
- 화면 목록에는 있지만 상태·흐름 어디에도 연결되지 않은 핵심 화면

현재 실행 화면은 현황 근거로 볼 수 있지만 구현되지 않은 미래 화면을 렌더링했다고
주장하지 않는다. 존재하지 않는 상태를 억지로 만들거나 구현 파일·라이브러리를 선택하지
않는다. 일회성 픽셀 값은 제품 디자인 정본으로 승격하지 않고, 둘 이상의 화면에 재사용될
규칙이 확정된 경우에만 `DESIGN.md` 또는 동등 정본을 함께 갱신한다.

## 완료와 실패 보고

완료 응답에는 다음을 모두 포함한다.

1. 작성·갱신한 명세 경로와 canonical target
2. 화면·흐름·상태 범위
3. reuse·extend·new 경계
4. Codex 검증 항목과 사용자 승인 항목
5. 제품 디자인 정본 변경 여부와 이유
6. 남은 미결 또는 `없음`
7. 다음 요청 예시: `$design-ui <UI 명세 경로>`

상태 machine 실패는 명세와 최종 응답 양쪽에 원인, 마지막 완료 phase, 필요한 입력,
typed affected scope, resume phase와 조건을 남긴다. preflight 실패는 명세를 만들지 않고
해당 응답 payload만 보고한다.
