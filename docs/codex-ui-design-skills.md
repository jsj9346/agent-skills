# Codex UI Design Skills 설계

- 상태: **설계 확정**
- 작성일: 2026-09-04
- 정본 범위: `agent-skills`에 추가할 Codex 전용 UI 디자인 플러그인의 역할 경계,
  스킬 계약, 산출물, 실패 처리, 패키지 구조와 검증 기준
- 불변: 하나의 플러그인에 `design-ui`·`review-ui` 두 스킬을 묶는 경계, 디자인
  정본 우선순위, 브라우저 근거 없는 Visual QA 합격 금지, `review-ui`의 기본
  비파괴성
- 조정 가능: 설명 문구, 기본 viewport 수치, 리포트 파일명, 체크리스트 표현과
  예시 프롬프트

## 1. 문제와 목표

Codex의 강점은 별도 디자인 캔버스에서 시안을 완성하는 데 있지 않고, 요구와 디자인
컨텍스트를 실제 UI 코드로 옮긴 뒤 렌더링 결과를 다시 고치는 짧은 루프에 있다. 이번
플러그인은 이 루프를 재사용 가능한 Codex 워크플로우로 만든다.

v1의 목표는 두 가지다.

1. `design-ui`: 요구사항·기존 UI·스크린샷·URL·Figma·무드보드 중 사용 가능한
   컨텍스트를 읽고, 프로젝트의 시각 규칙을 보존하거나 확장하면서 UI를 구현한다.
2. `review-ui`: 이미 구현된 UI를 실제 렌더링해 시각 품질과 반응형 동작을 근거와 함께
   판정하고, 명시적으로 요청받은 경우에만 결함을 수정한다.

이 설계는 `DESIGN.md = 제품이 어떻게 보여야 하는가`, `SKILL.md = Codex가 UI 작업을
어떻게 수행하는가`로 역할을 분리한다.

## 2. 제약과 전제

- 산출물은 Codex 전용이다. `codex-plugins/`와 Codex 카탈로그만 변경하고,
  `plugins/` 및 Claude Code 카탈로그에는 대응판을 만들지 않는다.
- v1은 instruction-only 플러그인이다. 브라우저·스크린샷·셸·프로젝트 테스트 등
  Codex와 대상 프로젝트에 이미 있는 능력을 사용하며, 자체 MCP 서버나 외부 서비스
  연결을 필수로 요구하지 않는다.
- 도구 이름을 고정하지 않는다. 동일한 능력이 Codex 앱·CLI·IDE에서 다른 도구로
  제공될 수 있으므로, 스킬은 능력 탐색과 대체 경로를 규정한다.
- 직접 실행 파일이나 런타임 import가 보이지 않는다는 사실만으로 능력 부재를 판정하지
  않는다. 프로젝트 스크립트, 로컬 의존성, 네트워크·설치 없이 package runner가 해석할
  수 있는 기존 CLI까지 비파괴적으로 확인한 뒤 blocker를 판정한다.
- 특정 프레임워크에 종속되지 않는다. React·Next.js·HTML/CSS 등 실제 저장소의
  스택과 실행 명령을 따른다.
- 외부 참고물은 브랜드·문구·저작물을 그대로 복제하는 허가로 간주하지 않는다.
  기본적으로 구조, 간격, 위계, 밀도, 상호작용 패턴만 번역한다.

## 3. 결정 사항

### 3.1 하나의 설치 단위, 두 개의 사용자 목표

플러그인 이름은 `design-ui`로 하고 그 안에 다음 두 스킬을 묶는다.

| 스킬 | 인식 가능한 사용자 목표 | 기본 변경 권한 |
|---|---|---|
| `design-ui` | 새 UI를 만들거나 기존 UI를 시각적으로 재설계·확장한다 | UI 소스와 필요한 디자인 정본을 변경 |
| `review-ui` | 실행 중인 UI의 시각 품질을 점검하고 근거 있는 판정을 받는다 | 보고서·스크린샷만 생성; 소스는 변경하지 않음 |

둘은 같은 디자인 정본을 소비하지만 트리거, 입력, 성공 기준이 다르므로 별도 스킬로
둔다. 반대로 screenshot-to-code, URL-to-code, Figma-to-code는 모두 “참고물을 UI로
번역한다”는 같은 목표와 성공 기준을 가지므로 별도 스킬이 아니라 `design-ui`의 입력
어댑터로 둔다.

관련 스킬을 한 플러그인에 묶는 구조는 한 플러그인이 하나 이상의 스킬을 포함할 수
있다는 공식 규약과 맞고, 사용자가 제작과 검토를 한 번에 설치하게 한다.

### 3.2 패키지 구조

```text
codex-plugins/design-ui/
├── .codex-plugin/plugin.json
├── README.md
├── LICENSE
└── skills/
    ├── design-ui/
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── design-authority.md
    │   └── assets/
    │       └── DESIGN.template.md
    └── review-ui/
        ├── SKILL.md
        ├── references/
        │   └── visual-qa-rubric.md
        └── assets/
            └── REVIEW-UI.template.md
```

카탈로그에는 플러그인 하나만 등록한다. `plugin.json`의 `skills`는 `./skills/`를
가리킨다. 각 `SKILL.md`에는 필수 frontmatter인 `name`과 `description`만 두고, 세부
절차·형식·중단 조건은 본문과 인접 reference에 둔다. v1에는 스크립트와
`agents/openai.yaml`을 추가하지 않는다.

저장소 반영 대상은 다음과 같다.

| 파일 | 신규/수정 | 역할 |
|---|---|---|
| `codex-plugins/design-ui/**` | 신규 | 두 스킬과 설치 단위 |
| `.agents/plugins/marketplace.json` | 수정 | Codex 마켓플레이스 등록 |
| `README.md` | 수정 | Codex-only 지원 여부와 설치·역할 안내 |
| `.claude-plugin/marketplace.json` | 변경 없음 | Claude Code 배포 대상이 아님 |
| `plugins/**` | 변경 없음 | Claude Code 대응판을 만들지 않음 |

### 3.3 디자인 정본 우선순위

두 스킬은 아래 순서로 디자인 근거를 해석한다. 위 근거와 아래 근거가 충돌하면 아래
근거를 조용히 덮어쓰지 않고 충돌을 드러낸다.

1. 현재 사용자의 명시적 요구와 승인된 작업 범위
2. 대상 저장소의 `AGENTS.md` 및 프로젝트 지침
3. `DESIGN.md` 또는 같은 역할을 하는 프로젝트 디자인 문서
4. 디자인 토큰과 공용 컴포넌트 계약
5. 현재 렌더링된 제품과 기존 UI 코드에서 반복 확인되는 패턴
6. 이번 작업에 첨부된 스크린샷·URL·Figma·무드보드
7. 일반적인 디자인 휴리스틱

상위 근거가 기존 정본 변경을 요구하면 변경 이유와 영향을 기록한다. 접근하지 못한
Figma·URL이나 보이지 않는 화면 상태는 추측해 채우지 않는다.

### 3.4 `DESIGN.md` 생성과 갱신 규칙

먼저 같은 역할의 기존 문서를 찾고, 파일명이 다르다는 이유로 중복 `DESIGN.md`를 만들지
않는다.

| 상황 | 동작 |
|---|---|
| 디자인 정본이 존재 | 먼저 읽고 준수한다. 새 재사용 패턴이 확정될 때만 갱신한다. |
| greenfield 또는 여러 화면에 적용될 새 시각 체계 | 구현 전에 루트 `DESIGN.md`를 최소 형태로 생성한다. |
| 기존 제품의 국소 수정 | 기존 토큰·컴포넌트로 충분하면 새 문서를 만들지 않는다. |
| 기존 제품인데 정본이 없고 새 패턴이 필요 | 관측 사실과 이번에 결정한 규칙을 구분한 `DESIGN.md`를 구현 전에 만든다. |

`DESIGN.md`의 최소 계약은 다음 절을 가진다.

1. Scope and principles
2. Foundations: color, typography, spacing, radius, shadow
3. Layout and breakpoints
4. Components and reuse rules
5. Interaction and UI states
6. Responsive behavior
7. Accessibility constraints
8. Intentional exceptions and unresolved assumptions

일회성 픽셀 값이나 구현 우연은 문서화하지 않는다. 새 규칙이 한 번의 화면에서만 쓰이거나
의도가 확인되지 않았다면 디자인 시스템으로 승격하지 않는다.

## 4. `design-ui` 계약

### 4.1 트리거와 비트리거

frontmatter 설명은 앞부분만 남아도 핵심 트리거가 보이도록 다음 의미를 포함한다.

> 새 웹·앱 UI를 만들거나 기존 UI를 시각적으로 재설계·확장하고, 스크린샷·URL·Figma·
> 기존 디자인 시스템을 실제 프론트엔드 코드로 옮길 때 사용한다. 렌더링과 Visual QA까지
> 포함한다. 디자인 검토만 원하거나 백엔드·데이터 구조만 바꾸는 작업에는 사용하지 않는다.

직접 트리거 예시는 “UI 만들어줘”, “이 스크린샷처럼 구현해줘”, “대시보드 리디자인”,
“Figma를 코드로 옮겨줘”다. “API 설계”, “DB 스키마 디자인”, “코드만 설명”, “구현은
하지 말고 UI를 검토”에는 트리거하지 않는다.

### 4.2 입력 모델

```text
DesignUiRequest = {
  target: route | component | screen-set | new-app,
  intent: create | extend | redesign | translate-reference,
  requirements: user text,
  references: Reference[],
  constraints: discovered project constraints + explicit user constraints
}

Reference =
  | Screenshot(local-path-or-attachment)
  | Url(http-url)
  | Figma(link-or-export)
  | ExistingUi(route-or-component)
  | Moodboard(images-or-links)
```

사용자가 타입 이름을 써야 한다는 뜻이 아니라, 스킬이 입력을 이 구조로 정규화해야 한다는
계약이다. `target`과 기대 결과를 저장소에서 합리적으로 찾을 수 없고 선택에 따라 결과가
크게 달라질 때만 질문한다. 참고물이 없다는 이유만으로 작업을 막지는 않는다.
다만 “UI 좀 바꿔줘”처럼 여러 시각 방향이 똑같이 타당하고 어떤 선택인지에 따라 결과가
크게 갈리면, 기존 화면이 있다는 이유만으로 임의의 방향을 고르지 않고 필요한 질문 또는
`Needs input`으로 전환한다. `translate-reference`의 주 참고물에 접근하지 못하면 기존
정본이나 휴리스틱으로 그 내용을 대체하지 않고 `Reference blocked`로 전환한다. 사용자가
참고물과 무관한 fallback 범위를 따로 승인한 경우에만 그 범위로 계속할 수 있다.
이 불완전 입력 판정은 구현 전 중단 조건이다. 기존 코드나 디자인 정본은 허용된 제약을
알려줄 뿐 사용자가 원하는 변경 목표를 대신 정하지 않으므로, 대상·목표·참고 방향 중
어느 것도 변경 의도를 좁히지 못하면 파일을 수정하지 않는다.

### 4.3 상태 전이

| 현재 상태 | 통과 조건 | 다음 상태 | 실패 상태 |
|---|---|---|---|
| Intake | 대상·의도·프로젝트 루트 식별 | Context ready | Needs input |
| Context ready | 지침·디자인 정본·토큰·공용 컴포넌트·실행법 확인 | Design ready | Reference blocked |
| Design ready | 변경할 시각 규칙과 재사용 경계 확정, 필요 시 `DESIGN.md` 선반영 | Implementing | Design conflict |
| Implementing | 대상 코드와 관련 상태 구현, 프로젝트 자동 검사 통과 | Renderable | Build blocked |
| Renderable | 실제 앱 실행 및 대상 상태 캡처 | Self-review | Render blocked |
| Self-review | 필수 viewport·상태에서 maker check 통과 | Done | Implementing으로 회귀 |

실패 상태는 침묵 종료가 아니다. 무엇이 없거나 충돌했는지, 어디까지 완료됐는지, 사용자가
제공해야 할 것과 검증하지 못한 범위를 최종 응답에 남긴다.

### 4.4 실행 절차

1. 저장소 지침, 기술 스택, 표준 실행·검사 명령을 읽는다.
2. §3.3 순서대로 디자인 정본, 토큰, 공용 컴포넌트, 기존 화면을 조사한다.
3. 참고물마다 접근 가능 여부와 사용할 요소를 구분한다. 브랜드·문구의 그대로 복제를
   요청받지 않았다면 layout, spacing, hierarchy, density, behavior만 추출한다.
4. 재사용할 것, 새로 만들 것, 바꿀 디자인 규칙을 구현 전에 짧게 확정한다. §3.4 조건이면
   먼저 디자인 정본을 생성·갱신한다.
5. 기존 컴포넌트와 토큰을 우선 사용해 구현한다. 새로운 의존성은 현재 스택으로 요구를
   충족할 수 없을 때만 추가한다.
6. 프로젝트의 테스트·린트·타입 검사 등 관련 자동 검사를 실행한다.
7. 앱을 실행해 실제 브라우저 결과를 확인하고, §6의 viewport·상태 행렬에서 최소 한 번의
   maker Visual QA를 수행한다.
8. 발견을 수정하고 다시 렌더링한다. 합격, 근거 있는 blocker, 또는 사용자 요구를 바꾸는
   설계 결정 필요 중 하나가 될 때까지 반복한다.
9. 코드 변경, 디자인 정본 변경, 실행한 검사, 캡처한 화면, 남은 미검증 범위를 요약한다.

### 4.5 성공 출력

`design-ui`의 완료는 코드가 존재한다는 뜻만이 아니다. 다음 다섯 결과가 모두 있어야 한다.

- 요청한 UI와 필요한 상태가 구현됨
- 프로젝트 자동 검사 결과
- 실제 렌더링을 확인한 viewport·상태 목록
- `DESIGN.md`를 만들거나 바꿨다면 그 이유와 범위
- 남은 차이와 검증하지 못한 항목의 명시적 목록; 없으면 “없음”

브라우저를 사용할 수 없거나 앱이 실행되지 않으면 `Visual QA 통과`라고 보고할 수 없다.
정적 검사까지 완료한 `render-unverified` 상태로 종료하고 재현 명령과 blocker를 제공한다.

## 5. `review-ui` 계약

### 5.1 트리거와 모드

frontmatter 설명은 다음 의미를 포함한다.

> 구현된 웹·앱 UI를 브라우저에서 렌더링해 alignment, spacing, typography, hierarchy,
> color, component consistency, responsive behavior, overflow와 주요 상태를 시각적으로
> 검토할 때 사용한다. 기본은 소스를 바꾸지 않는 audit이며, 사용자가 수정까지 명시한
> 경우에만 repair 모드로 전환한다. 새 UI 제작에는 사용하지 않는다.

```text
ReviewUiRequest =
  | Audit  { target, baseline?, viewports?, states? }
  | Repair { target, baseline?, viewports?, states?, explicit_fix_request: true }
```

“검토해줘”, “Visual QA”, “반응형 깨짐 찾아줘”는 `Audit`이다. “검토하고 고쳐줘”,
“Visual QA 후 수정까지”만 `Repair`다. 모드를 추론하기 애매하면 비파괴적인 `Audit`을
선택한다.

### 5.2 판정 근거와 발견 스키마

기대값은 §3.3의 정본에서 가져온다. 디자인 정본이 전혀 없을 때는 명백한 렌더링 결함과
일반 휴리스틱 발견을 구분하며, 취향을 계약 위반으로 표현하지 않는다.

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

등급은 다음과 같다.

| 등급 | 기준 |
|---|---|
| blocker | 페이지·핵심 흐름을 볼 수 없거나 사용 자체가 불가능 |
| major | 핵심 위계·레이아웃·반응형·상호작용이 무너져 주요 사용을 방해 |
| moderate | 일관성이나 가독성을 분명히 해치지만 우회 가능 |
| minor | 국소적인 시각 다듬기 또는 낮은 영향의 불일치 |

### 5.3 상태 전이와 변경 경계

| 현재 상태 | Audit | Repair |
|---|---|---|
| Baseline ready | before 캡처와 판정 행렬 생성 | before 캡처와 판정 행렬 생성 |
| Findings frozen | 보고서에 발견을 확정하고 종료 | 보고서에 발견을 먼저 확정한 뒤 수정 시작 |
| Repairing | 도달하지 않음 | 디자인 결정이 필요 없는 open 발견만 수정 |
| Recheck | 도달하지 않음 | 같은 viewport·상태를 다시 캡처하고 발견 상태 갱신 |
| Done | 보고서·근거만 생성 | 보고서·before/after 근거·소스 변경 생성 |

`Audit`에서는 제품 소스와 `DESIGN.md`를 수정하지 않는다. `Repair`에서도 정본이 틀렸거나
미규정이라 선택이 필요한 항목은 `design-decision-required`로 남기고 임의 수정하지 않는다.
즉 repair는 명백한 정본 위반과 렌더링 결함을 닫는 모드이지 새 디자인을 정하는 우회로가
아니다.

### 5.4 리포트 계약

기본 리포트 위치는 프로젝트 규약이 있으면 그곳을 따르고, 없으면
`reports/YYYYMMDD-review-ui-<target>.md`다. 리포트는 다음을 포함한다.

1. 대상, 모드, 기준 HEAD, 디자인 정본
2. 실행 명령과 검토한 route·viewport·상태 행렬
3. 발견 집계와 `UiFinding` 상세
4. before 캡처 경로
5. repair일 때 변경 파일·검사 결과·after 캡처와 재판정
6. 검토하지 못한 범위와 이유

화면을 실제로 렌더링하지 못했다면 빈 리포트나 추정 판정을 만들지 않는다. 리포트를
`blocked`로 닫고 자동 검사 결과, 실패 로그, 미확인 범위를 남긴다.

## 6. 공통 Visual QA 행렬

프로젝트나 사용자가 viewport를 정했다면 그것이 우선한다. 없으면 아래 세 개를 기본으로
한다.

| 분류 | 기본 viewport |
|---|---|
| mobile | 390 × 844 |
| tablet | 768 × 1024 |
| desktop | 1440 × 900 |

대상에 관련된 상태만 검토하되, 존재하는 상태를 happy path 하나로 축소하지 않는다.

- default
- loading
- empty
- error
- disabled
- hover, focus, open/closed 등 핵심 interaction

각 조합에서 alignment, spacing, typography, hierarchy, color/token consistency,
component consistency, overflow/clipping, responsive reflow, 주요 interaction, focus visibility를
확인한다. 자동 접근성 검사가 프로젝트에 있으면 함께 실행하되, 이 스킬을 완전한 접근성
감사로 표현하지 않는다.

참고 이미지가 있는 작업은 기준에 따라 다음처럼 판정한다.

- pixel-perfect가 명시된 경우: 같은 viewport와 상태에서 직접 비교하고 남은 차이를 보고
- 일반 참고인 경우: 구조·간격·위계·밀도·반응형 행동의 충실도를 보고, 브랜드와 콘텐츠
  차이는 결함으로 세지 않음
- 참고물이 일부만 보이는 경우: 보이지 않는 상태나 breakpoint를 참고물에서 추론하지 않음

## 7. 기존 스킬과의 경계

| 인접 기능 | 이 플러그인과의 경계 |
|---|---|
| `interview` | 제품 방향과 “무엇을 왜 만들지”가 갈리면 선행. `design-ui`는 정해진 목표의 시각 체계와 구현을 다룸. |
| `make-design` | 시스템 경계·인터페이스 정본을 설계. 제품의 시각 규칙인 `DESIGN.md`와는 다른 정본. |
| `verify` | 일반 계약 대조와 독립 판정. `review-ui`는 실제 렌더링의 시각·반응형 근거에 특화. |
| `imagegen` | 새 래스터 에셋 생성·편집 요청일 때만 사용. UI 코드 생성의 기본 단계가 아님. |
| 브라우저·스크린샷 도구 | 스킬에 내장하지 않고 사용 가능한 Codex 능력을 탐색해 사용. 없으면 미검증으로 보고. |

사용자 요청이 “새 화면을 만들고 검토까지”라면 `design-ui`가 구현과 maker check를 끝낸다.
독립적인 두 번째 판정을 명시적으로 원할 때 `review-ui`를 이어서 사용한다.

## 8. 의도적 배제

| 배제 항목 | 판정 근거 | 재도입 트리거 |
|---|---|---|
| `image-to-code`·`url-to-code`·`figma-to-code` 별도 스킬 | 목표·절차·출력이 `design-ui`와 같아 트리거와 규칙이 중복됨 | 입력마다 고유 인증·도구·산출물 계약이 필요해질 때 |
| 광범위한 `product-design` 스킬 | 제품 발견·UX 전략까지 포함하면 기존 `interview`와 경계가 흐려짐 | 반복 수요가 UI 구현과 다른 성공 기준으로 관측될 때 |
| 전용 MCP 서버·브라우저 자동화 서버 | 기존 Codex/프로젝트 도구로 v1 워크플로우 수행 가능 | 여러 환경에서 동일 도구 부재가 반복 blocker로 확인될 때 |
| 결정론적 스크립트 | 지금 필요한 판단은 프로젝트별·시각적이며 스크립트가 줄일 확정 반복이 없음 | viewport 캡처·리포트 생성의 동일 수작업이 반복될 때 |
| Claude Code 대응판 | 사용자가 Codex 전용을 명시함 | 별도 사용자 수요와 런타임별 계약을 승인할 때 |
| 자동 브랜드·콘텐츠 복제 | 참고와 복제의 경계를 흐리고 사용자 의도를 넘음 | 권리와 복제 범위가 명시적으로 제공될 때 |
| 항상 pixel-perfect 보장 | 참고물·폰트·viewport·상태가 불완전하면 검증 불가능 | 사용자가 정확한 기준과 실행 가능한 비교 환경을 제공할 때 |
| `review-ui`의 기본 자동 수정 | 독립 판정 전에 고치면 before 근거와 발견이 사라짐 | 사용자가 repair를 명시한 요청에 한해 이미 허용 |

## 9. 구현 검증 계약

구현 완료는 다음 검사를 모두 만족해야 한다.

### 9.1 구조 검사

- `codex-plugins/design-ui/.codex-plugin/plugin.json`이 유효한 JSON이고 `skills`가
  `./skills/`를 가리킨다.
- 두 `SKILL.md`의 frontmatter에 `name`·`description`이 있으며 이름이 디렉터리와
  일치한다.
- `.agents/plugins/marketplace.json`에는 `design-ui` 플러그인이 정확히 한 번만 있다.
- Claude Code 카탈로그와 `plugins/` 트리는 변경되지 않는다.
- `python3 scripts/validate_skill_links.py`가 통과한다.

### 9.2 트리거 평가

각 스킬은 대표 요청으로 다음 다섯 종류를 평가한다.

1. 명시 호출과 직접 요청이 올바른 스킬을 활성화
2. 같은 목표의 간접 표현도 활성화
3. 불완전 입력은 필요한 질문 또는 명시적 blocker로 전환
4. 비트리거 요청은 활성화하지 않음
5. 접근 불가 참고물·브라우저 부재·미규정 디자인에서 정보를 꾸며내지 않음

최소 사례에는 greenfield, 기존 디자인 시스템 확장, screenshot reference, URL/Figma 접근
불가, 브라우저 실행 실패, `review-ui` Audit, `review-ui` Repair를 포함한다.

### 9.3 행동 불변 조건

- `design-ui`는 존재하는 디자인 정본과 공용 컴포넌트를 읽기 전에 구현하지 않는다.
- reusable한 새 시각 규칙이 생기지 않으면 `DESIGN.md`를 불필요하게 바꾸지 않는다.
- 두 스킬 모두 실제 렌더링 근거 없이 Visual QA 통과를 선언하지 않는다.
- `review-ui` Audit은 제품 소스와 디자인 정본을 변경하지 않는다.
- `review-ui` Repair는 before 발견을 먼저 고정하고 같은 행렬로 after를 재검증한다.
- 미규정 디자인 선택은 review에서 조용히 확정하지 않는다.

## 10. 참고한 자료와 읽은 범위

- 사용자 제공 `Codex UI Design Workflow 정리`: 전체 읽음. Codex UI 구현 루프,
  `DESIGN.md`/`SKILL.md` 역할 분리, 제작/리뷰 분리 제안을 입력으로 사용함.
  원본: `/home/13ruce/.codex/attachments/81d55eb2-6f7e-458d-9dbd-2b7f02562624/pasted-text.txt`
- 저장소 `README.md`, `.agents/plugins/marketplace.json`, 기존 Codex 플러그인의
  `plugin.json`·`SKILL.md`·README, `scripts/validate_skill_links.py`: 구조와 관례를
  확인할 만큼 읽음.
- [OpenAI Docs — Build skills](https://learn.chatgpt.com/docs/build-skills): skill의
  progressive disclosure, 필수 파일·metadata, explicit/implicit activation, 플러그인
  배포 구조 확인.
- [OpenAI Plugins — Build skills](https://developers.openai.com/plugins/build/skills):
  목표별 스킬 경계, 입력·절차·출력·추론 금지·중단 조건, supporting resources와 대표
  activation test 계약 확인.
- [OpenAI Plugins — Plugin architecture](https://developers.openai.com/plugins/concepts/plugins):
  한 플러그인에 관련 스킬을 묶는 구조와 instruction-only 플러그인의 타당성 확인.

## 11. 미결 — 이 문서가 정하지 않은 것

없음. 아이콘·`agents/openai.yaml`·결정론적 캡처 스크립트는 v1 범위에서 의도적으로
배제했으며, §8의 재도입 트리거가 관측될 때 별도 설계한다.
