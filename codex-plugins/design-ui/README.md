# design-ui

UI를 실제 코드로 만들고 렌더링 결과를 검토하는 **Codex 전용** 플러그인이다. Claude
Code 대응판은 포함하지 않는다.

## 포함된 스킬

- `design-ui`: 새 UI 제작, 기존 UI의 시각적 재설계·확장, 스크린샷·URL·Figma·기존
  디자인 시스템의 프론트엔드 코드 번역을 맡는다.
- `review-ui`: 구현된 UI를 브라우저에서 감사한다. 기본 Audit은 소스를 바꾸지 않으며,
  사용자가 수정까지 명시한 경우에만 Repair를 수행한다.

두 스킬은 사용자 요구, 프로젝트 지침, 디자인 정본, 토큰과 공용 컴포넌트 순으로
근거를 확인한다. `design-ui`는 구현 뒤 maker Visual QA까지 수행하고, 독립적인 2차
시각 판정이 필요하면 `review-ui`를 이어서 사용한다.

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
