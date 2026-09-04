---
name: design-ui
description: >-
  새 웹·앱 UI를 만들거나 기존 UI를 시각적으로 재설계·확장하고, 스크린샷·URL·
  Figma·기존 디자인 시스템 같은 참고물을 실제 프론트엔드 코드로 옮길 때 사용한다.
  구현 뒤 실제 렌더링과 maker Visual QA까지 수행한다. 디자인 검토만 원하거나
  백엔드·API·데이터 구조만 바꾸는 작업에는 사용하지 않는다.
---

# Design UI

Codex에서 UI를 설계 의도에 맞는 실제 코드로 구현하고, 실행 가능한 화면을 직접
렌더링해 검토한다. 특정 프레임워크를 전제하지 않으며 대상 저장소의 스택과 관례를
따른다.

## 요청을 정규화한다

작업을 시작할 때 사용자 표현을 다음 필드로 해석한다. 타입 이름을 사용자에게 요구하지
않는다.

```text
DesignUiRequest = {
  target: route | component | screen-set | new-app,
  intent: create | extend | redesign | translate-reference,
  requirements: user text,
  references: Reference[],
  constraints: discovered project constraints + explicit user constraints
}

Reference =
  Screenshot(local-path-or-attachment)
  | Url(http-url)
  | Figma(link-or-export)
  | ExistingUi(route-or-component)
  | Moodboard(images-or-links)
```

저장소에서 `target`과 기대 결과를 합리적으로 찾을 수 없고 선택에 따라 결과가 크게
달라질 때만 질문한다. 참고물이 없다는 이유만으로 작업을 중단하지 않는다. 접근할 수
없는 URL·Figma와 참고물에 보이지 않는 상태나 breakpoint는 꾸며내지 말고
`Reference blocked`와 미확인 범위를 명시한다.

“UI 좀 바꿔줘”처럼 서로 다른 시각 방향이 똑같이 타당해 결과가 크게 갈리면 기존 화면이
있더라도 필요한 방향을 질문한다. 비대화형 실행에서는 `Needs input`으로 종료한다.
`translate-reference`의 주 참고물에 접근하지 못하면 기존 정본이나 휴리스틱을 그 화면인
것처럼 대체 구현하지 말고 `Reference blocked`로 종료한다. 참고물과 무관한 fallback을
사용자가 따로 승인한 경우에만 그 범위로 계속한다.

### 불완전 입력 중단 조건

사용자가 “UI 좀 바꿔줘”처럼 넓은 변경 말만 했고 대상·목표·참고 방향 중 어느 것도
원하는 결과를 좁히지 못하면 **파일을 수정하지 않는다**. 기존 코드와 디자인 정본은
허용된 제약이지 변경 목표를 대신하는 허가가 아니다. 어떤 화면을 왜, 어느 방향으로
바꿀지 필요한 질문을 하고, 비대화형 실행이면 `Needs input`으로 종료한다. 이 판정을
`Context ready`나 구현보다 먼저 수행한다.

### 접근 불가 참고물 중단 조건

스크린샷·URL·Figma가 요청의 주 기준인데 실제 내용을 읽을 수 없으면 **제품 소스와
디자인 정본을 수정하지 않는다**. 사용자가 “추측해서” 구현하라고 해도 보이지 않는 내용을
발명하는 허가로 해석하지 않는다. 접근 실패를 확인한 즉시 `Reference blocked`로
종료하고, 접근 가능한 export·스크린샷·URL 또는 참고물과 독립적인 fallback 범위의
승인을 요청한다. 기존 UI나 `DESIGN.md`를 읽을 수 있다는 이유로 reference 번역을 다른
디자인 작업으로 바꾸지 않는다.

## 작업 흐름

1. **Intake → Context ready**: 프로젝트 루트와 대상을 식별한 뒤 `AGENTS.md` 등 저장소
   지침, 기술 스택, 표준 실행·검사 명령을 읽는다. 식별에 필요한 핵심 정보가 없으면
   `Needs input`으로 보고한다.
2. **Context ready → Design ready**: 디자인 정본, 토큰, 공용 컴포넌트, 관련 기존 화면과
   코드를 구현 전에 조사한다. 이 단계에서는
   [디자인 정본 규칙](references/design-authority.md)을 읽고 그 우선순위와 충돌 처리를
   적용한다. 필요한 참고물에 접근하지 못하면 `Reference blocked`로 보고하며 내용을
   추측하지 않는다.
3. **Design ready → Implementing**: 재사용할 요소, 새로 만들 요소, 바꿀 시각 규칙을 짧게
   확정한다. 디자인 근거가 충돌하고 현재 범위에서 해소할 수 없으면 `Design conflict`로
   멈춘다. 정본 규칙상 새 문서가 필요할 때만
   [DESIGN.md 템플릿](assets/DESIGN.template.md)을 프로젝트 루트의 `DESIGN.md` 또는
   기존 동등 문서 형식에 맞춰 복사·조정하고, 코드보다 먼저 반영한다.
4. **Implementing → Renderable**: 기존 토큰과 공용 컴포넌트를 우선 사용해 대상 UI와 관련
   상태를 구현한다. 새 의존성은 현재 스택으로 요구를 충족할 수 없을 때만 추가한다.
   프로젝트의 관련 테스트·린트·타입 검사·빌드를 실행한다. 실패가 해소되지 않으면
   `Build blocked`로 보고한다.
5. **Renderable → Self-review**: 사용 가능한 Codex 도구와 프로젝트 명령에서 앱 실행,
   브라우저 탐색, 스크린샷 캡처 능력을 확인하고 실제 화면을 렌더링한다. 한 방법이 없으면
   이미 제공된 다른 브라우저·캡처 수단이나 프로젝트 자체 preview 명령을 찾는다. 실제
   렌더링이 불가능하면 `Render blocked`이며, 정적 검사까지만 마친
   `render-unverified`로 종료한다.
6. **Self-review → Done 또는 Implementing**: 아래 maker Visual QA 행렬을 검사한다.
   발견한 결함을 수정하고 같은 관련 조합을 다시 렌더링한다. 합격하면 `Done`, 결함이
   남으면 `Implementing`으로 돌아간다. 사용자 요구를 바꾸는 결정이 필요하거나 근거 있는
   blocker가 생기면 반복을 끝내고 명시적으로 보고한다.

## Maker Visual QA

사용자나 프로젝트가 viewport를 지정했으면 그것을 우선한다. 지정이 없으면 mobile
`390 × 844`, tablet `768 × 1024`, desktop `1440 × 900`을 기본으로 한다. 대상에 실제로
존재하는 상태 중 관련된 조합을 확인한다. happy path 하나로 줄이지 말고 `default`,
`loading`, `empty`, `error`, `disabled`, 핵심 `hover`·`focus`·`open/closed` 상태를
포함한다.

각 조합에서 다음을 검사한다.

- alignment, spacing, typography, hierarchy
- color/token consistency와 component consistency
- overflow/clipping과 responsive reflow
- 주요 interaction과 focus visibility
- 프로젝트에 자동 접근성 검사가 있다면 그 결과(완전한 접근성 감사로 표현하지 않음)

참고 이미지에 pixel-perfect가 명시되었으면 같은 viewport·상태에서 직접 비교하고 남은
차이를 보고한다. 일반 참고물은 구조·간격·위계·밀도·반응형 행동을 비교하며, 명시되지
않은 브랜드나 콘텐츠 차이를 결함으로 세지 않는다. 일부만 보이는 참고물로 숨은 상태나
breakpoint를 추론하지 않는다.

## 완료와 실패 보고

완료 응답에는 다음 다섯 결과를 모두 포함한다.

1. 구현한 UI와 상태
2. 실제로 실행한 자동 검사와 결과
3. 실제 렌더링을 확인한 viewport·상태 목록과 캡처 근거
4. `DESIGN.md` 또는 동등 문서를 만들거나 바꿨다면 이유와 영향 범위
5. 남은 차이와 검증하지 못한 항목의 목록; 없으면 `없음`

실제 렌더링 근거 없이는 Visual QA 통과를 선언하지 않는다. 앱이나 브라우저를 실행하지
못했으면 `render-unverified`라고 표시하고 재현 명령과 blocker를 제공한다. 모든 blocker
보고에는 원인, 마지막으로 완료한 지점, 사용자가 제공해야 할 입력이나 조치, 미검증 범위를
포함한다.

능력 부재를 판정할 때 직접 실행 파일이나 런타임 import 확인 하나로 끝내지 않는다.
프로젝트의 실행 스크립트, 로컬 의존성, 현재 도구 목록, 네트워크·설치 없이 package
runner가 해석할 수 있는 기존 CLI를 비파괴적인 version/help 명령으로 확인한다. 예를 들어
`npx`가 있다면 오프라인으로 이미 사용 가능한 브라우저 CLI가 있는지 확인할 수 있다.
평가를 위해 새 패키지를 설치하거나 다운로드하지 않는다.

## 인접 작업과의 경계

- 무엇을 왜 만들지에 따라 제품 방향이 크게 갈리면 `interview`가 선행 대상이다.
- `make-design`의 시스템 경계·인터페이스 설계 문서와 제품 시각 규칙인 `DESIGN.md`를
  혼동하지 않는다.
- 이 스킬은 구현자의 maker check까지 맡는다. 구현과 분리된 독립 2차 판정은
  `review-ui`나 일반 계약 대조가 필요하면 `verify`의 영역이다.
- `imagegen`은 사용자가 새 래스터 에셋 생성·편집을 요구할 때만 사용하며 UI 코드 생성의
  기본 단계로 호출하지 않는다.
