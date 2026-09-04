---
name: review-ui
description: >-
  구현된 웹·앱 UI를 브라우저에서 렌더링해 시각 품질, 반응형 동작, overflow와
  주요 상태를 근거와 함께 검토할 때 사용한다. 기본은 제품 소스와 디자인 정본을
  바꾸지 않는 Audit이며, 사용자가 수정까지 명시한 경우에만 Repair로 전환한다.
  새 UI 제작이나 재설계에는 사용하지 않는다.
---

# Review UI

구현된 UI를 실제 브라우저 결과로 검토하고 재현 가능한 발견과 캡처 근거를 보고서에
남긴다. 브라우저 렌더링 없이 정적 코드만 보고 Visual QA가 통과했다고 판정하지 않는다.

## 요청과 모드를 정규화한다

사용자 표현을 다음 tagged union으로 해석한다. 타입 이름을 사용자에게 요구하지 않는다.

```text
ReviewUiRequest =
  | Audit  { target, baseline?, viewports?, states? }
  | Repair { target, baseline?, viewports?, states?, explicit_fix_request: true }
```

- “검토해줘”, “Visual QA”, “반응형 깨짐 찾아줘”는 `Audit`이다.
- “검토하고 고쳐줘”, “Visual QA 후 수정까지”처럼 명시적 fix 요청이 있을 때만
  `Repair`다.
- 모드가 애매하면 반드시 비파괴적인 `Audit`을 선택한다.
- `target`을 저장소나 실행 중인 앱에서 합리적으로 찾을 수 없고 선택에 따라 결과가 크게
  달라지면 질문한다. 질문에 답할 수 없는 비대화형 실행이면 대상 부재를 blocker로 남긴다.

## 판정 근거를 먼저 확정한다

기대값은 아래에서 숫자가 작은 근거를 우선해 도출한다.

1. 현재 사용자의 명시적 요구와 승인된 작업 범위
2. 대상 저장소의 `AGENTS.md` 및 프로젝트 지침
3. `DESIGN.md` 또는 같은 역할을 하는 프로젝트 디자인 문서
4. 디자인 토큰과 공용 컴포넌트 계약
5. 현재 렌더링된 제품과 기존 UI 코드에서 반복 확인되는 패턴
6. 이번 작업에 첨부된 스크린샷·URL·Figma·무드보드
7. 일반적인 디자인 휴리스틱

상위 근거와 하위 근거가 충돌하면 조용히 덮어쓰지 말고 보고서에 근거, 충돌, 영향을
기록한다. 디자인 선택이 필요하면 발견 상태를 `design-decision-required`로 두며 review
단계에서 새 규칙을 정하지 않는다. 디자인 정본이 전혀 없을 때는 명백한 렌더링 결함과
일반 휴리스틱에 따른 제안을 구분하고, 취향을 계약 위반으로 표현하지 않는다. 접근하지
못한 URL·Figma나 보이지 않는 화면 상태는 추측하지 않는다.

## 실행 준비

1. 프로젝트 루트, 대상 route·component, 현재 HEAD, 저장소 지침, 실행·검사 명령을
   확인한다.
2. 디자인 정본, 토큰, 공용 컴포넌트, 관련 기존 화면을 읽어 기대값과 충돌을 기록한다.
3. 사용자·프로젝트가 지정한 viewport와 상태를 우선하고, 지정이 없으면
   [Visual QA 판정 기준](references/visual-qa-rubric.md)을 읽어 관련 행렬을 만든다.
4. 프로젝트 규약이 있으면 그 리포트 위치를 사용하고, 없으면
   `reports/YYYYMMDD-review-ui-<target>.md`에
   [리포트 템플릿](assets/REVIEW-UI.template.md)을 복사해 채운다. `<target>`은 경로에
   안전한 짧은 이름으로 바꾼다.
5. 앱을 실행하고 대상 행렬의 실제 브라우저 결과를 캡처한다. 자동 테스트나 정적 코드
   검사는 렌더링 증거를 대신하지 않는다.

## 상태 전이

- `Baseline ready`: Audit과 Repair 모두 before 캡처와 판정 행렬을 만든다.
- `Findings frozen`: 발견을 보고서에 확정한다. Audit은 여기서 `Done`으로 가고,
  Repair만 다음 단계로 간다.
- `Repairing`: 디자인 결정이 필요 없는 `open` 발견만 수정한다.
- `Recheck`: before와 같은 viewport·상태를 다시 캡처해 발견 상태를 갱신한다.
- `Done`: Audit은 보고서·before 근거만, Repair는 보고서·before/after 근거·소스 변경을
  결과로 남긴다.

## Audit

`Audit`은 기본 경로이며 보고서와 캡처 근거만 생성한다.

1. 검토 전 HEAD와 제품 소스·`DESIGN.md` 또는 동등 정본의 상태를 기록한다.
2. 관련 viewport·상태 행렬을 실제로 렌더링하고 before 캡처를 남긴다.
3. 각 발견을 아래 `UiFinding` 스키마로 확정한 뒤 집계를 기록한다.
4. 제품 소스와 디자인 정본을 변경하지 않고 보고서를 닫는다. 필요하면 시작 전후 diff나
   hash를 비교해 비파괴성을 확인한다.

Audit 중 수정이 유익해 보여도 고치지 않는다. 사용자가 후속으로 Repair를 명시하면 이미
고정된 before 발견과 캡처를 그 입력으로 사용한다.

## Repair

`Repair`는 명시적 fix 요청이 있을 때만 실행한다.

1. Audit과 동일하게 before 화면을 캡처하고 모든 발견을 보고서에 먼저 고정한다.
2. 정본 위반이나 명백한 렌더링 결함으로 판정된 `open` 발견만 수정한다.
   `design-decision-required` 발견과 미규정 선택은 임의로 고치지 않는다.
3. 관련 프로젝트 자동 검사를 실행한다.
4. before와 정확히 같은 route·viewport·state 행렬을 다시 렌더링해 after 캡처를 남긴다.
5. 근거를 대조해 각 발견을 `fixed` 또는 `unverified` 등으로 갱신하고, 변경 파일·검사
   결과·남은 발견을 기록한다.

같은 행렬로 재검증하지 않았거나 after 근거가 없으면 Repair 완료라고 보고하지 않는다.

## 발견 계약

각 발견은 다음 아홉 필드를 모두 가진다.

```text
UiFinding = {
  id: UI-###,
  severity: blocker | major | moderate | minor,
  location: route/component + viewport + UI state,
  expected: authority source or "heuristic",
  actual: observed behavior,
  evidence: screenshot path and reproduction steps,
  impact: user-visible consequence,
  suggested_fix: concise direction,
  status: open | fixed | design-decision-required | unverified
}
```

severity 판정과 검사 범주, 참고물 비교 규칙은
[Visual QA 판정 기준](references/visual-qa-rubric.md)을 따른다. 근거가 없는 발견을
만들지 않고, heuristic 발견의 `expected`에는 반드시 `heuristic`이라고 표시한다.

## 렌더링 실패

앱이나 브라우저를 실행할 수 없으면 빈 green 리포트나 추정 발견을 만들지 않는다.
리포트 상태를 `blocked`로 닫고 다음을 기록한다.

- 실제로 실행한 명령과 자동 검사 결과
- 실패 로그와 재현 단계
- 마지막으로 확인한 지점
- 검토하지 못한 route·viewport·state와 이유
- 사용자가 제공해야 할 입력 또는 환경 조치

이 경우 `Visual QA 통과`, `발견 없음`, Audit/Repair 완료를 선언하지 않는다.

## 완료 보고

보고서는 대상·모드·기준 HEAD·디자인 정본, 실행 명령과 검토 행렬, 발견 집계와 상세,
before 캡처, Repair일 때 변경 파일·검사 결과·after 캡처와 재판정, 미검토 범위와 이유를
포함해야 한다. Audit은 소스·정본 불변 여부도 함께 보고한다.

## 인접 작업과 평가 경계

- 새 화면 제작, 기존 UI 재설계·확장, 구현자의 maker check는 `design-ui` 영역이다.
- 구현과 분리된 독립 2차 시각 판정은 `review-ui` 영역이다.
- “새 랜딩 페이지를 디자인하고 구현해줘”에는 이 스킬을 사용하지 않는다.
- “이 화면의 반응형 깨짐과 시각적 불일치를 찾아 보고해줘”에는 Audit을 사용한다.
- “Visual QA 후 명백한 결함은 수정까지 해줘”에는 before를 먼저 고정한 Repair를 사용한다.
- 앱이 없는 상태에서 “이 UI를 Visual QA 해줘”라고 하면 green을 만들지 않고 `blocked`로
  종료한다.
