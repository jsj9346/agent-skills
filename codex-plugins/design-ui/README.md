# design-ui

구현 전 UI 정의부터 실제 코드 구현과 독립 Visual QA까지 연결하는 **Codex 전용**
플러그인이다. Claude Code 대응판은 포함하지 않는다.

## 포함된 스킬

- `define-ui`: 코드를 쓰기 전에 특정 기능의 화면·흐름·상태·반응형 규칙과 완료 기준을
  `ready-for-build` UI 명세로 만든다.
- `design-ui`: 새 UI 제작, 기존 UI의 시각적 재설계·확장, 스크린샷·URL·Figma·기존
  디자인 시스템의 프론트엔드 코드 번역을 맡는다. UI 명세가 있으면 구현과 maker QA의
  target 전용 기대값으로 사용한다.
- `review-ui`: 구현된 UI를 브라우저에서 감사한다. 기본 Audit은 소스를 바꾸지 않으며,
  사용자가 수정까지 명시한 경우에만 Repair를 수행한다. ready UI 명세가 있으면 finding과
  acceptance 결과의 근거로 사용한다.

대표 흐름은 다음과 같다.

```text
define-ui → design-ui → review-ui → 사용자 승인
```

`define-ui`는 선택적 선행 단계다. 작은 국소 변경이나 이미 구체적인 구현 요청은
`design-ui`로 바로 시작할 수 있다. 세 스킬은 사용자 요구, 프로젝트 지침, target UI 명세,
디자인 정본, 토큰과 공용 컴포넌트 순으로 근거를 확인한다.

대표 호출:

```text
$define-ui 결제 설정 흐름의 화면과 상태를 구현 전에 정의해줘
$design-ui design/specs/payment-settings.md
$review-ui 구현된 결제 설정 화면을 독립적으로 검토해줘
```

브라우저나 앱 실행 수단이 없어 실제 화면을 렌더링하지 못한 경우에는 Visual QA 통과를
선언하지 않는다. 수행한 정적 검사와 재현 명령을 남기고 `render-unverified` 또는
`blocked`로 보고한다.

## 설치

```bash
codex plugin marketplace add jsj9346/agent-skills
codex plugin add design-ui@jsj9346-skills
```

## 라이선스

MIT
