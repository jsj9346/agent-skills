# Codex UI Workflow Skills 확장 설계

- 상태: **설계 확정**
- 작성일: 2026-09-04
- 최종 갱신일: 2026-09-05
- 정본 범위: `codex-plugins/design-ui`를 요구사항에서 사용자 승인까지 이어지는 UI
  개발 흐름으로 확장할 때 필요한 추가 스킬, 기존 스킬과의 경계, 단계 간 산출물 계약
- 선행 정본: `docs/codex-ui-design-skills.md`
- 불변: 사용자 목표가 다른 경우에만 스킬을 분리한다. `define-ui`는 제품 소스를
  구현하지 않고, `design-ui`는 구현과 maker Visual QA를 맡으며, `review-ui`는
  독립 판정을 맡는다. 사용자 승인과 공개 결정은 Codex가 대신하지 않는다.
- 조정 가능: UI 명세 기본 경로, 템플릿 표현, 예시 프롬프트, 기본 acceptance check 수

이 문서는 선행 정본의 v1 계약을 폐기하지 않는다. 추가되는 `define-ui` 계약과 그로 인해
바뀌는 패키지 파일 집합·정본 우선순위·handoff만 이 문서가 우선한다.

## 1. 문제와 목표

현재 `design-ui`는 요구를 실제 UI 코드로 구현하고 제작자 관점의 Visual QA까지 수행하며,
`review-ui`는 완성된 UI를 독립적으로 Audit하거나 명시적 요청에 따라 Repair한다. 두 스킬
사이의 구현·검토 경계는 확정되어 있다.

그러나 사용자가 다음과 같이 요청하는 경우를 맡는 스킬은 없다.

> 코드는 아직 만들지 말고, 이 기능에 필요한 화면·사용 흐름·상태·반응형 동작과 완료
> 기준부터 정리해줘.

`interview`는 무엇을 왜 만들지를 결정하지만 제품 UI의 화면 구조를 설계하지 않는다.
`make-design`은 시스템 경계와 인터페이스의 정본이지 제품 화면 설계가 아니다.
`design-ui`는 최종 산출물이 실행 가능한 UI 코드이므로 구현 없는 화면 정의 요청과 성공
기준이 다르다.

따라서 이번 확장의 목표는 **구현 전 UI 정의를 독립 산출물로 만드는 `define-ui` 하나를
추가**하고, 아래 흐름의 handoff를 끊김 없이 만드는 것이다.

```text
요구사항 확정
  ↓
기존 디자인·제품 맥락 확인
  ↓
화면·흐름·상태·완료 기준 정의    ← define-ui
  ↓
UI 구현·자동 검사·제작자 화면 확인 ← design-ui
  ↓
독립 검토·명시적 수정             ← review-ui
  ↓
사용자 승인·공개                  ← 사람/프로젝트 배포 절차
```

## 2. Capability Gap 판정

단계마다 스킬을 하나씩 만드는 것은 목표가 아니다. 사용자가 별도로 인식할 수 있는 목표,
입력, 성공 기준이 모두 갈릴 때만 스킬을 분리한다.

| UI 개발 단계 | 현재 담당 | 추가 스킬 | 판정 근거 |
|---|---|---|---|
| 요구사항의 무엇·왜 확정 | `interview` 또는 사용자의 명시적 요구 | 없음 | 범용 제품 결정과 중복된다. 방향이 명확하면 인터뷰도 생략한다. |
| 기존 디자인·컴포넌트 확인 | `define-ui`·`design-ui`·`review-ui`의 공통 선행 단계 | 없음 | 독립 사용자 목표가 아니라 각 작업의 입력 조사다. |
| 구현 전 화면·흐름·상태 정의 | 담당 없음 | **`define-ui`** | 코드 없는 UI 정의라는 별도 트리거·산출물·성공 기준이 있다. |
| UI 코드 구현 | `design-ui` | 없음 | 기존 계약으로 충족된다. |
| 테스트·린트·타입·빌드 | `design-ui`와 대상 프로젝트 검사 | 없음 | UI 전용 판단이 아니라 구현 완료 게이트다. |
| 제작자 화면 확인 | `design-ui` maker Visual QA | 없음 | 구현 루프와 분리하면 수정 왕복만 늘어난다. |
| 독립 검토·수정 | `review-ui` Audit/Repair | 없음 | 기존 계약으로 충족된다. |
| 사용자 승인 | 사용자, `define-ui`의 acceptance checks와 `review-ui` 근거가 지원 | 없음 | 승인 권한은 사람에게 있으며 스킬이 스스로 합격시킬 수 없다. |
| 공개·배포 | 대상 프로젝트의 배포 절차·호스팅 도구 | 없음 | UI 품질과 다른 권한·런타임·롤백 계약이다. |

이 판정은 공식 OpenAI 스킬 규약의 “인식 가능한 사용자 목표에 집중하고, 트리거·입력·
성공 기준이 다를 때 workflow를 분리한다”는 원칙을 적용한다.

## 3. 결정 사항

### 3.1 플러그인 하나, 세 가지 사용자 목표

플러그인 이름은 계속 `design-ui`다. 같은 디자인 정본을 소비하는 다음 세 스킬을 한 설치
단위에 둔다.

| 스킬 | 인식 가능한 사용자 목표 | 기본 변경 권한 | 성공 산출물 |
|---|---|---|---|
| `define-ui` | 구현 전에 화면·흐름·상태·완료 기준을 정한다 | UI 명세와 필요한 디자인 정본만 변경 | `ready-for-build` UI 명세 |
| `design-ui` | 정의·요구·참고물을 실제 UI 코드로 구현한다 | UI 소스와 필요한 디자인 정본 변경 | 실행 가능한 UI와 maker QA 근거 |
| `review-ui` | 구현된 UI를 독립적으로 검토하거나 명시적으로 수정한다 | Audit은 보고서만, Repair는 허용된 소스 변경 | 발견 보고서와 렌더 근거 |

다음 요청은 `define-ui`를 활성화한다.

- “구현 전에 화면 구성을 정의해줘”
- “이 기능의 사용자 흐름과 화면 상태를 설계해줘”
- “코드는 쓰지 말고 UI 명세부터 만들어줘”
- “모바일·데스크톱에서 이 화면이 어떻게 달라질지 정리해줘”

다음 요청은 `define-ui`가 아니다.

- “대시보드를 구현해줘” → `design-ui`
- “이 화면을 검토해줘” → `review-ui` Audit
- “무슨 제품을 만들지 같이 정하자” → 필요하면 `interview`
- “프론트엔드와 백엔드 경계를 설계해줘” → `make-design`
- “현재 화면을 이미지 시안으로만 그려줘” → 요청 산출물에 맞는 이미지 도구

### 3.2 `define-ui`는 선택적 선행 단계다

모든 UI 구현 앞에 `define-ui`를 강제하지 않는다. 작은 국소 변경이나 사용자의 요구가 이미
구체적인 작업은 `design-ui`로 바로 간다. 다음 중 하나면 분리된 UI 정의의 가치가 있다.

- 여러 화면이나 여러 사용자 단계가 연결된다.
- 로딩·빈 상태·오류·권한·반응형 변화 등 상태 계약이 구현 전에 합의되어야 한다.
- 구현 전에 화면 방향을 검토하거나 다른 사람에게 handoff해야 한다.
- “코드는 아직 만들지 말라”는 비구현 경계가 명시됐다.

`define-ui`가 없는 것은 오류가 아니다. 반대로 `ready-for-build` 명세가 존재하면
`design-ui`와 `review-ui`는 이를 대상 기능의 정본으로 소비해야 한다.

### 3.3 패키지 구조

기존 플러그인에 다음 세 파일을 추가한다.

```text
codex-plugins/design-ui/
├── .codex-plugin/plugin.json
├── README.md
├── LICENSE
└── skills/
    ├── define-ui/
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── ui-definition-contract.md
    │   └── assets/
    │       └── UI-SPEC.template.md
    ├── design-ui/
    │   └── ... 기존 파일
    └── review-ui/
        └── ... 기존 파일
```

플러그인 manifest의 `skills: "./skills/"`는 그대로이며 marketplace 항목도 늘리지 않는다.
README에는 세 역할과 대표 호출을 추가한다. v2에서도 MCP 서버, 스크립트,
`agents/openai.yaml`은 기본 범위에 넣지 않는다.

### 3.4 UI 명세와 제품 디자인 정본의 구분

| 문서 | 질문 | 범위 | 기본 소유자 |
|---|---|---|---|
| `DESIGN.md` 또는 동등 문서 | 제품 전체가 어떻게 보여야 하는가 | 토큰·타이포그래피·공용 컴포넌트·반복 규칙 | 제품/디자인 시스템 |
| UI 명세 | 이 기능의 화면과 상태가 어떻게 동작해야 하는가 | 특정 route·component·screen-set | 기능/작업 |
| `SKILL.md` | Codex가 그 작업을 어떻게 수행하는가 | 반복 실행 절차 | 플러그인 |

프로젝트에 UI 명세 위치 규약이 있으면 그것을 따른다. 없으면
`design/specs/<target-slug>.md`를 기본으로 한다. UI 명세 하나에서 처음 생긴 일회성 픽셀
값이나 취향을 `DESIGN.md`에 올리지 않는다. 여러 화면에서 재사용될 새 시각 규칙이
확정된 경우에만 제품 디자인 정본을 함께 갱신한다.

### 3.5 Acceptance 책임과 증거 조합

2026-09-04 사용자 승인으로 acceptance check는 다음 세 조합만 허용한다.

| 책임 주체 | 판정 증거 | 의미 |
|---|---|---|
| `codex` | `render` | Codex가 실제 화면 근거로 판정 |
| `codex` | `automated-check` | Codex가 프로젝트의 기존 자동 검사로 판정 |
| `user` | `user-decision` | 사용자가 결과를 보고 명시적으로 승인 또는 거절 |

`codex + user-decision`, `user + render`, `user + automated-check` 조합은 만들 수 없다.
사용자가 렌더링 결과를 보고 승인하는 경우에도 screenshot은 판단을 돕는 supporting
evidence이고 최종 판정 증거는 사용자의 명시적 결정이다. 사용자 소유 check는 결정 전
`awaiting-user-acceptance`, 승인 후 `pass`, 거절 후 `fail`이다.

여기서 `owner: codex`는 **판정 주체**를 뜻하며 브라우저 프로세스를 반드시 같은 Codex
sandbox가 직접 띄워야 한다는 뜻은 아니다. §8.2의 격리 평가에서는 신뢰된 outer runner가
동일한 immutable case snapshot을 렌더링할 수 있다. 다만 outer runner는 캡처만 생성하며
pass/fail을 정하지 않는다. 같은 대상 플러그인을 사용하는 후속 Codex adjudication이 실제
이미지를 열어 판정해야만 `codex + render` 근거가 완성된다. 캡처만 존재하거나 metadata만
읽은 상태는 `unverified`다.

### 3.6 동일 target의 UI 명세 선택

UI 명세를 파일명이나 표시 이름으로 비교하지 않는다. request와 `UiSpec`은 같은
`UiTarget` tagged union을 사용한다.

```text
UiTarget =
  | RouteTarget {
      kind: route,
      key: canonical project-router pattern
    }
  | ComponentTarget {
      kind: component,
      key: <owner-kind>:<owner-key>#<lowercase-kebab-case component slug>
    }
  | ScreenSetTarget {
      kind: screen-set,
      key: lowercase-kebab-case stable slug
    }
  | NewAppTarget {
      kind: new-app,
      key: lowercase-kebab-case project-local app slug
    }
```

route key는 query와 hash를 제거하고 `/`로 시작하는 대상 프로젝트 router의 route pattern을
그대로 사용한다. root가 아닌 route의 trailing slash는 제거하되 dynamic segment 표기법은
framework 사이에서 임의 변환하지 않는다. component owner는 `global` 또는 이를 소유하는
`route`·`screen-set`·`new-app` target이다. `global` owner key는 `project`로 고정하며 예시는
`global:project#button`, `route:/settings/profile#profile-form`이다. component key는 코드
파일·export 경로가 아니므로 구현 파일이 이동해도 유지한다. screen-set과 new-app slug도
생성 뒤 표시 이름이나 파일 경로가 바뀌어도 유지한다. key를 추측해야만 만들 수 있으면 §4.1의
`NeedsClarification`으로 끝낸다.

같은 target은 canonical `(kind, key)`가 case-sensitive exact match일 때뿐이다. 명세 ID,
파일 경로, 표시 이름, 수정 시각, alias 유사성은 target equality에 쓰지 않는다. 기본 명세
경로의 `<target-slug>`는 저장 위치를 위한 파생값일 뿐 target identity가 아니다.

명시 UI 명세 경로가 target의 유일한 입력이면 그 명세의 `UiTarget`을 request target으로
정규화할 수 있다. 사용자가 별도 target도 명시했는데 명세의 canonical `(kind, key)`와
다르면 다른 target을 선택하거나 명세 target을 고쳐 맞추지 않는다. 초기 명세를 만들기 전
§4.1의 응답 전용 `TargetConflict`로 보고하며, 이는 persistent
`UiSpec.status: design-conflict`가 아니다. `design-ui`와 `review-ui`에서 같은 불일치가
발견되면 두 canonical target과 명세 경로·영향·필요 결정을 담은 응답 전용
`Design conflict`로 중단하고 명세 선택·구현·Audit·Repair를 시작하지 않는다.

2026-09-04 사용자 승인으로 exact match인 같은 target에 여러 UI 명세가 있을 때 다음 순서를
적용한다.

1. 현재 요청에서 사용자가 명시한 정확한 명세 경로
2. 프로젝트 지침이나 기존 명세 인덱스가 해당 target의 active 명세로 지정한 정확한 경로
3. canonical target과 일치하는 `ready-for-build` 후보가 정확히 하나인 경우 그 경로
4. 위 조건으로 하나를 고를 수 없으면 `Needs input`과 후보 경로 목록

명시 경로의 명세가 미완성 또는 실패 상태이면 다른 명세로 조용히 갈아타지 않고 그 상태의
중단 계약을 적용한다. 수정 시각, 파일명에 포함된 날짜, 사전식 순서로 “최신”을 추측하지
않는다. 같은 target을 개정할 때는 선택된 기존 명세를 갱신하는 것이 기본이며, 복수 버전을
유지하려면 프로젝트가 active 명세를 명시해야 한다.

## 4. `define-ui` 계약

### 4.1 입력 모델

사용자에게 타입 이름을 요구하지 않지만 요청을 다음 구조로 정규화한다.

```text
DefineUiRequest = {
  target: UiTarget,
  intent: define | extend | revise,
  goal: user-visible outcome,
  requirements: user text,
  users?: described users or roles,
  references: Reference[],
  constraints: discovered project constraints + explicit user constraints
}

Reference =
  | Screenshot(local-path-or-attachment)
  | Url(http-url)
  | Figma(link-or-export)
  | ExistingUi(route-or-component)
  | ExistingUiSpec(path)
  | Moodboard(images-or-links)
```

대상과 사용자가 이루려는 일이 저장소·요청에서 합리적으로 특정되지 않고 선택에 따라
화면 구성이 크게 달라지면 질문한다. 무엇을 왜 만들지 자체가 갈리면 UI 명세에서 임의로
제품 결정을 내리지 않고 `interview`로 넘긴다.

이 식별 질문은 UI 명세 상태 machine에 들어가기 전 **preflight**다. 의미 없는 partial
spec이 누적되지 않도록 target과 user-visible goal이 특정되기 전에는 명세 파일·ID·status를
만들지 않는다. 명시 명세 target과 별도 target의 충돌도 초기 명세를 만들기 전에 판정한다.
preflight 결과는 다음 세 형태뿐이다.

```text
DefineUiPreflight =
  | Ready { request: DefineUiRequest }
  | NeedsClarification {
      known_context: discovered facts,
      missing: NonEmptyList<target.kind | target.key | user-visible-goal>,
      material_effect: why the missing choice changes the screen,
      question: one focused question,
      resume_condition: answer needed to restart preflight
    }
  | TargetConflict {
      explicit_target: UiTarget,
      spec_target: UiTarget,
      spec_path: exact user-specified UI spec path,
      material_effect: why the target mismatch changes the affected screen or flow,
      resolution_needed: choose explicit target | use spec target | provide matching spec,
      resume_condition: one canonical target and matching spec are selected
    }
```

`UiTarget`은 §3.6에서 정규화한다. kind 또는 canonical key를 추측해야 하거나 user-visible
goal이 식별되지 않으면 `Ready`가 될 수 없다.

`NeedsClarification`은 `UiSpec.status: needs-input`과 다른 결과다. 최종 응답에 파악된 맥락,
빠진 입력, 화면에 미치는 영향, 질문, 재개 조건과 “UI 명세를 생성하지 않음”을 보고하고
제품 소스를 변경하지 않는다. 답을 받으면 이전 상태를 재개하는 대신 preflight를 다시
평가한다.

`TargetConflict`도 저장되는 실패 status가 아니라 응답 전용 결과다. 최종 응답에 두
canonical target, 명시 명세 경로, 화면·흐름에 미치는 영향, 필요한 해소 결정과 재개 조건을
보고한다. 명세 target을 고쳐 맞추거나 다른 명세로 fallback하지 않고 UI 명세와 제품 소스를
변경하지 않는다. 사용자가 하나의 target과 일치하는 명세를 정하면 preflight를 처음부터
다시 평가한다. preflight가 `Ready`인 뒤에만 초기 UI 명세를 만들고 `Intake`로 들어간다.

`intent: revise`에서 기존 명세를 선택하거나 다른 intent에서 동일 target의 기존 명세를
재사용할 때는 §3.6을 적용한다. 복수 후보 중 하나를 수정 시각으로 추측하지 않는다.

참고물 부재만으로 멈추지 않는다. 다만 reference 번역이 주목적인데 해당 reference에
접근할 수 없으면 보이는 척하지 않고 `Reference blocked`로 종료한다. 사용자가 참고물과
독립적인 fallback 범위를 승인한 경우만 계속한다.

### 4.2 출력 모델

UI 명세는 최소한 다음 필드를 가진다.

```text
UiSpecCommon = {
  id: stable slug,
  target: UiTarget,
  intent: define | extend | revise,
  goal: user-visible outcome,
  users: relevant users or roles,
  authority: ordered source list,
  scope: included behavior and screens,
  non_goals: excluded behavior and screens,
  screen_inventory: ScreenSpec[],
  flows: UserFlow[],
  component_reuse: reuse | extend | new decisions,
  responsive_rules: ResponsiveRule[],
  acceptance_checks: AcceptanceCheck[]
}

AffectedScope =
  | KnownAffectedScope {
      screens_or_flows: NonEmptyList<stable screen-or-flow name>
    }
  | UnknownTargetScope {
      target: UiTarget,
      reason: why stable screen-or-flow names cannot be known without the blocked reference
    }

FailureContextCommon = {
  cause: visible reason,
  required_input: concrete user or reference input,
  resume_condition: observable condition
}

KnownFailureContextCommon = {
  ...FailureContextCommon,
  affected_scope: KnownAffectedScope
}

FailureContext =
  | NeedsInputFailure {
      ...KnownFailureContextCommon,
      phase: NeedsInput,
      last_completed_phase: DefinitionDrafting,
      resume_at: DecisionCheck
    }
  | ReferenceBlockedFailure {
      ...FailureContextCommon,
      affected_scope: KnownAffectedScope | UnknownTargetScope,
      phase: ReferenceBlocked,
      last_completed_phase: Intake,
      resume_at: AuthorityReady
    }
  | DesignConflictDuringDrafting {
      ...KnownFailureContextCommon,
      phase: DesignConflict,
      last_completed_phase: AuthorityReady,
      resume_at: DefinitionDrafting
    }
  | DesignConflictDuringDecisionCheck {
      ...KnownFailureContextCommon,
      phase: DesignConflict,
      last_completed_phase: DefinitionDrafting,
      resume_at: DecisionCheck
    }

UiSpec = UiSpecCommon & (
  | DraftUiSpec {
      status: draft,
      unresolved: UiDecision[],
      failure: absent
    }
  | NeedsInputUiSpec {
      status: needs-input,
      unresolved: NonEmptyList<UiDecision>,
      failure: NeedsInputFailure
    }
  | ReferenceBlockedUiSpec {
      status: reference-blocked,
      unresolved: UiDecision[],
      failure: ReferenceBlockedFailure
    }
  | DesignConflictUiSpec {
      status: design-conflict,
      unresolved: NonEmptyList<UiDecision>,
      failure: DesignConflictDuringDrafting | DesignConflictDuringDecisionCheck
    }
  | ReadyUiSpec {
      status: ready-for-build,
      unresolved: [],
      failure: absent
    }
)

ScreenSpec = {
  screen_or_region: stable name,
  purpose: user task served,
  content_hierarchy: ordered content and actions,
  states: default | loading | empty | error | disabled | permission | domain-specific,
  interactions: trigger + visible response,
  accessibility_expectations: keyboard, focus, semantics, contrast expectations
}

AcceptanceCheckCommon = {
  id: UI-AC-###,
  scenario: reproducible user action,
  viewport_or_condition: observable condition,
  expected: observable outcome
}

AcceptanceCheck =
  | CodexRenderCheck {
      ...AcceptanceCheckCommon,
      owner: codex,
      evidence: render
    }
  | CodexAutomatedCheck {
      ...AcceptanceCheckCommon,
      owner: codex,
      evidence: automated-check
    }
  | UserDecisionCheck {
      ...AcceptanceCheckCommon,
      owner: user,
      evidence: user-decision
    }

AcceptanceResult =
  | CodexAcceptanceResult {
      check_id: UI-AC-###,
      status: pass | fail | unverified
    }
  | UserAcceptanceResult {
      check_id: UI-AC-###,
      status: awaiting-user-acceptance | pass | fail
    }
```

`ready-for-build`은 다음과 동시에 존재할 수 없다.

- 제품 방향을 바꾸는 미결 항목
- 접근하지 못한 주 reference를 본 것처럼 작성한 규칙
- 기대 결과를 관측할 수 없는 acceptance check
- §3.5의 세 가지 유효 조합 밖에 있는 acceptance check
- 화면 목록에는 있지만 상태·흐름 어디에도 연결되지 않은 핵심 화면

`unresolved`가 남아 있으면 해당 항목의 영향에 따라 `needs-input` 또는
`design-conflict`이며 `ready-for-build`로 표시하지 않는다.

`KnownAffectedScope`는 정본 근거로 stable screen 또는 flow 이름을 특정할 수 있을 때만
사용한다. 주 reference에 접근해야 화면 목록 자체를 알 수 있는 `ReferenceBlockedFailure`는
`UnknownTargetScope`로 target 전체가 잠정 영향 범위임을 드러낸다. 빈 목록이나 접근하지
못한 reference에서 추측한 화면 이름은 허용하지 않는다. `NeedsInputFailure`와 두
`DesignConflict` 변형은 정의 초안 이후 발생하므로 `KnownAffectedScope`만 허용한다.

### 4.3 정본 우선순위

`define-ui`는 다음 순서로 근거를 해석한다.

1. 현재 사용자의 명시적 요구와 승인된 범위
2. 대상 저장소의 `AGENTS.md` 및 프로젝트 지침
3. §3.6에 따라 하나로 선택된 해당 target의 UI 명세
4. `DESIGN.md` 또는 동등한 제품 디자인 정본
5. 디자인 토큰과 공용 컴포넌트 계약
6. 현재 제품과 기존 UI 코드에서 반복 확인되는 패턴
7. 이번 작업의 접근 가능한 참고물
8. 일반적인 UI·사용성 휴리스틱

상위 근거와 하위 근거가 충돌하면 조용히 섞지 않는다. 사용자의 새 요구가 기존 제품
정본 변경을 뜻하면 영향과 승인 필요 여부를 드러낸다. `define-ui`가 일반 휴리스틱을
제품 요구처럼 확정하지 않는다.

### 4.4 상태 전이

§4.1의 preflight는 이 표 밖의 입력 gate다. `NeedsClarification`과 `TargetConflict`는 명세를
만들지 않는 응답 전용 결과이며, 다음 표는 `Ready` 결과를 받아 초기 UI 명세가 생성된 뒤에만
시작한다. workflow phase는 실행 중 위치이고 `UiSpec.status`는 파일에 저장하는 lifecycle
결과다. 둘을 같은 필드로 쓰지 않는다.

```text
DefineUiPhase =
  | Intake
  | AuthorityReady
  | DefinitionDrafting
  | DecisionCheck
  | ReadyForBuild
  | Done
  | NeedsInput
  | ReferenceBlocked
  | DesignConflict
```

| runtime phase | 통과 조건 | 다음 phase | 실패 phase | persistent `UiSpec.status` |
|---|---|---|---|---|
| `Intake` | preflight와 초기 명세의 target·intent·goal exact match | `AuthorityReady` | 해당 없음 | `draft` |
| `AuthorityReady` | 지침·디자인 정본·기존 명세·참고물 접근성 확인 | `DefinitionDrafting` | `ReferenceBlocked` | `draft` 또는 `reference-blocked` |
| `DefinitionDrafting` | 화면·흐름·상태·반응형·재사용 경계 초안 완성 | `DecisionCheck` | `DesignConflict` | `draft` 또는 `design-conflict` |
| `DecisionCheck` | 제품 결정을 요구하는 미결 0, acceptance checks가 관측 가능 | `ReadyForBuild` | `NeedsInput` 또는 `DesignConflict` | `draft`, `needs-input` 또는 `design-conflict` |
| `ReadyForBuild` | ready 불변 조건과 빈 `unresolved` 재확인 | `Done` | 해당 없음 | `ready-for-build` |
| `Done` | 명세 경로와 handoff 요약 보고 | 종료 | 해당 없음 | `ready-for-build` 유지 |

저장 규칙은 다음과 같다.

1. preflight `Ready` 뒤 `DraftUiSpec`을 만들고 runtime phase를 `Intake`로 시작한다.
2. `Intake`부터 `DecisionCheck`까지 정상 phase는 파일에 phase를 저장하지 않고 status를
   `draft`로 유지한다.
3. 실패 phase에 들어갈 때 대응 status와 `FailureContext`를 한 번에 기록한다.
   `resume_at`은 실패 원인을 다시 검사할 가장 이른 정상 phase다.
4. 재개 조건을 확인한 뒤에만 `failure`를 제거하고 status를 `draft`로 되돌린 다음
   `resume_at`에서 실행한다. status만 보고 완료 phase를 추측하지 않는다.
5. `ReadyForBuild` 진입 시 `unresolved: []`, `failure: absent`,
   `status: ready-for-build`을 한 번에 기록한다. `Done`은 저장 status를 바꾸지 않는다.
6. 정상 phase 도중 중단되어 `draft`만 남았으면 다음 실행은 `Intake`에서 정본과 입력을
   다시 대조한다. runtime phase를 파일명·mtime·부분 내용으로 복원하지 않는다.

상태 machine 안의 실패 상태는 빈 문서나 암묵적 성공이 아니다. `FailureContext`를 명세에
남기고 같은 원인·마지막 완료 phase·필요 입력·영향 범위·재개 phase와 조건을 최종 응답에도
보고한다. preflight의 `NeedsClarification`과 `TargetConflict`는 명세가 아직 없으므로
§4.1의 각 응답 계약을 따른다.

### 4.5 실행 절차

1. 제품 파일을 바꾸지 않고 저장소 지침, 제품 요구, 관련 코드와 실행 가능한 현재 화면을
   읽는다.
2. §3.6의 `UiTarget`과 user-visible goal을 정규화한다. 추측 없이는 `kind`·`key`·goal을
   채울 수 없으면 §4.1의 `NeedsClarification`, 명시 명세 target과 별도 target이 다르면
   `TargetConflict`로 끝낸다.
3. preflight가 `Ready`이면 `intent`를 포함한 `DraftUiSpec`을 만들고 `Intake`로 들어간다.
4. `DESIGN.md`, 기존 UI 명세, 토큰, 공용 컴포넌트와 참고물의 접근성을 확인한다.
5. 사용자의 핵심 작업을 시작 조건부터 성공·실패 종료까지 흐름으로 적는다.
6. 흐름에 필요한 화면·영역과 각 상태를 연결하고, 빠진 로딩·빈 상태·오류·권한 상태를
   명시한다. 제품에 존재하지 않는 상태를 억지로 추가하지 않는다.
7. 기존 컴포넌트 재사용, 확장, 신규 필요를 구분한다. 구현 파일이나 라이브러리는 이
   단계에서 선택하지 않는다.
8. 모바일·넓은 화면 등 실제 제품 조건에서 정보 우선순위와 동작 변화를 정의한다.
9. Codex가 렌더나 자동 검사로 확인할 항목과 사용자가 승인할 항목을 분리해 acceptance
   checks를 작성한다.
10. 제품 결정을 요구하는 미결을 사용자에게 회부한다. 모두 닫혔을 때만
   `ready-for-build`로 종료한다.

### 4.6 완료 보고

완료 응답에는 다음을 포함한다.

1. 작성하거나 갱신한 UI 명세 경로와 target
2. 화면·흐름·상태 범위 요약
3. 재사용·확장·신규 경계
4. Codex 검증 항목과 사용자 승인 항목
5. 제품 디자인 정본 변경 여부와 이유
6. 남은 미결; 없으면 `없음`
7. 다음 구현 요청 예시: `$design-ui <UI 명세 경로>`

`define-ui`는 제품 UI 소스, 테스트, 빌드 설정을 변경하지 않는다. 실제 브라우저를 현재
상태 파악과 근거 수집에 사용할 수는 있지만, 구현되지 않은 미래 화면을 렌더링했다고
주장하지 않는다.

## 5. 스킬 간 Handoff 계약

### 5.1 `define-ui` → `design-ui`

`design-ui`는 구현 전에 §3.6의 순서로 UI 명세를 선택한다. `NoSpec`은 target과 일치하는
명세가 없는 상태이며, 요구가 충분히 구체적이면 기존 `design-ui` 계약대로 구현할 수 있다.
선택 결과는 다음 세 형태뿐이다.

```text
UiSpecSelection =
  | Selected { path }
  | NoSpec
  | NeedsInput { candidate_paths }
```

`Selected`이면 해당 명세를 읽고 상태에 따라 처리한다.

- `ready-for-build`: 명세의 화면·상태·responsive rules·acceptance checks를 구현 범위와
  maker QA 행렬로 변환한다.
- `draft`, `needs-input`, `design-conflict`: 영향받는 범위를 임의 구현하지 않는다. 필요한
  결정을 요청하거나 명세 재개를 안내한다.
- `reference-blocked`: 보이지 않는 reference를 다른 디자인으로 대체하지 않는다.
- 명세 없음: 요구가 충분히 구체적이면 현재 `design-ui` 계약대로 바로 구현할 수 있다.

`NeedsInput`이면 후보 경로를 나열하고 사용자가 하나를 지정할 때까지 구현하지 않는다.
사용자가 명시한 경로가 미완성인데 다른 `ready-for-build` 명세가 있더라도 자동 fallback
하지 않는다.

현재 사용자 요구가 기존 UI 명세와 충돌하면 사용자의 요구를 조용히 무시하거나 명세를
몰래 고치지 않는다. 충돌과 영향 범위를 보고하고, 이번 요청이 명세 개정까지 승인하는지
확인한다.

### 5.2 `define-ui` → `review-ui`

`review-ui`도 §3.6의 순서로 UI 명세를 선택한다. 선택된 명세가 `ready-for-build`이면
이를 디자인 정본 다음이 아니라
**target 전용 기대값**으로 사용한다. §3.5의 세 유효 `AcceptanceCheck`를 다음처럼 소비한다.

- `owner: codex`, `evidence: render`: viewport·state 행렬과 화면 근거로 판정한다.
- `owner: codex`, `evidence: automated-check`: 대상 프로젝트의 기존 검사로 판정한다.
- `owner: user`, `evidence: user-decision`: Codex가 대신 합격시키지 않고
  `awaiting-user-acceptance`로 남긴다. 사용자의 명시적 승인 뒤에만 `pass`, 거절 뒤에만
  `fail`로 바꾼다.

세 조합 밖의 입력은 기본값으로 보정하지 않고 명세 계약 오류로 보고한다.

선택된 명세가 `draft`, `needs-input`, `design-conflict`, `reference-blocked`이면 다른 ready
명세나 하위 authority로 조용히 전환하지 않는다. 기본 결과는 다음 `HaltForSpec`이며,
target-specific verdict·acceptance 판정·Repair를 시작하지 않는다.

```text
NonReadyReviewHandling =
  | HaltForSpec {
      selected_path,
      selected_status,
      affected_target,
      required_input,
      choices: [resume-spec, request-general-audit]
    }
  | GeneralAudit {
      trigger: explicit-user-request,
      authority: existing review authority excluding the non-ready spec as expected,
      acceptance_results: none,
      repair_allowed: false
    }
```

사용자가 선택된 명세와 독립적인 **일반 Visual Audit**을 명시적으로 요청한 경우에만
`GeneralAudit`으로 진행할 수 있다. 이 Audit은 기존 제품 디자인 정본과 관측 가능한 화면,
일반 휴리스틱을 근거로 하며 non-ready 명세를 `expected`로 인용하지 않는다. 그 명세의
acceptance check를 판정하거나 Repair를 수행하지 않고, 보고서에 `general-audit` 범위와
명세 기반 판정을 하지 않은 이유를 표시한다. Repair는 이 `GeneralAudit` 경로에서 허용하지
않으며, 명세를 `ready-for-build`로 완성한 뒤 별도 요청으로 시작한다.

review 발견의 `expected`에는 UI 명세의 절 또는 acceptance check ID를 기록할 수 있어야
한다. 명세가 없으면 기존 `review-ui`의 authority와 heuristic 분리 규칙을 그대로 쓴다.

### 5.3 `review-ui` → 사용자 승인

사용자에게 승인 판단을 요청할 때 최소한 다음이 함께 보여야 한다.

- 구현된 target과 실제 확인한 viewport·state
- open blocker/major/moderate/minor 수
- `UI-AC-*`별 pass/fail/unverified/awaiting-user-acceptance 상태
- 알려진 차이와 미검증 범위
- Repair가 있었다면 같은 조건의 before/after 근거

`GeneralAudit`에서는 UI 명세 기반 acceptance 상태를 만들지 않고 “non-ready 명세로 인해
미평가”라고 표시한다. 이것은 `unverified` 결과를 임의 생성하는 것과 구분한다.

Codex가 추천 의견을 낼 수는 있지만 `owner: user` 항목을 자동으로 `pass` 처리하거나 공개를
실행하지 않는다. 사용자의 명시적 승인 뒤 실제 배포는 대상 프로젝트의 배포 절차가 맡는다.

### 5.4 범용 스킬과의 경계

| 상황 | 담당 |
|---|---|
| 무엇을 왜 만들지 갈림 | `interview` |
| 제품 UI의 화면·흐름·상태를 구현 전에 정의 | `define-ui` |
| 시스템 경계·데이터·인터페이스 설계 | `make-design` |
| UI 코드 구현과 maker QA | `design-ui` |
| 독립 Visual QA와 명시적 Repair | `review-ui` |
| UI 외 계약까지 포함한 전체 구현 감사 | `verify` |
| 실제 공개 | 프로젝트별 배포·호스팅 절차 |

## 6. 대표 요청 라우팅

| 요청 | 선택 | 이유 |
|---|---|---|
| “결제 설정 흐름의 화면과 상태부터 정의해줘. 구현은 하지 마.” | `define-ui` | 비구현 UI 정의가 목표다. |
| “이 요구사항으로 설정 화면을 만들어줘.” | `design-ui` | 코드가 성공 산출물이다. 명세가 있으면 소비한다. |
| “설정 화면을 만들기 전에 설계하고 이어서 구현해줘.” | `define-ui` 후 `design-ui` | 두 성공 산출물을 순서대로 요구한다. |
| “이 화면이 모바일에서 깨지는지 봐줘.” | `review-ui` Audit | 구현된 화면의 독립 판정이다. |
| “이 draft 명세 기준으로 화면을 검토해줘.” | `review-ui` `HaltForSpec` | non-ready 명세를 기대값으로 사용하지 않는다. |
| “draft 명세와 독립적인 일반 Visual Audit만 해줘.” | `review-ui` `GeneralAudit` | 명시된 일반 Audit만 수행하며 명세 acceptance·Repair는 제외한다. |
| “검토하고 명백한 문제는 수정해줘.” | `review-ui` Repair | before 고정과 수정 후 같은 조건 검증이 필요하다. |
| “어떤 사용자를 위한 제품인지부터 정하자.” | `interview` | UI 구조 이전의 제품 방향 결정이다. |
| “출시해줘.” | 배포 절차 | UI 스킬의 권한과 성공 기준 밖이다. |

## 7. 의도적 배제

| 배제 | 판정 근거 | 재도입 트리거 |
|---|---|---|
| `accept-ui` | 사용자 승인은 사람의 권한이고, 근거 준비는 UI 명세와 review 보고서로 충족된다. | 여러 팀에서 동일한 사용자 인수 테스트 문서·승인 이력·전자 서명이 반복 요구됨 |
| `test-ui` | 프로젝트 자동 검사와 `design-ui` maker QA, `review-ui` Visual QA가 현재 범위를 맡는다. | 기능 브라우저 테스트나 접근성 감사가 별도 트리거·리포트·전문 판정 기준을 반복 요구함 |
| `deploy-ui` | 배포는 UI 품질이 아니라 인프라·권한·롤백 문제다. | UI 프리뷰 배포만의 공통 플랫폼 계약이 여러 프로젝트에서 반복됨 |
| `prototype-ui` | 현재 목표는 명세와 production UI 구현이며 별도 폐기형 프로토타입 산출물이 요구되지 않았다. | 구현 전 클릭형 프로토타입을 독립 산출물로 반복 요청함 |
| `inspect-design` | 기존 디자인 확인은 세 UI 스킬의 필수 선행 단계이지 독립 목표가 아니다. | 디자인 시스템 인벤토리 자체가 독립 보고서로 반복 요구됨 |
| MCP·전용 브라우저 서버 | 반복 blocker는 §8.2의 평가 전용 outer capture bridge로 먼저 해소하며 제품 플러그인에 새 runtime 의존성을 넣지 않는다. | bridge로 표현할 수 없는 지속적 interactive session이 여러 실제 프로젝트에서 반복 요구됨 |
| outer runner의 Visual QA 판정 | capture와 판정을 합치면 `owner: codex`와 독립 검토의 귀속이 사라진다. outer runner는 관측 자료만 만든다. | §3.5의 판정 주체 자체를 바꾸는 사용자 결정이 별도로 승인됨 |
| 결정론적 UI 명세 생성 스크립트 | 판단 중심 작업이라 정적 템플릿으로 충분하다. | 명세 schema lint나 누락 검사가 반복적으로 실패함 |
| 휴리스틱 target alias matching | 비슷한 이름·파일명으로 같은 target을 추측하면 다른 명세를 선택할 수 있다. | 프로젝트가 canonical key로 해석되는 명시적 alias registry를 제공함 |
| 정상 workflow phase의 영속 저장 | instruction-only 작업은 `draft`에서 안전하게 재검사할 수 있고 phase/status 이중 정본을 피한다. | 장시간 작업의 정상 phase를 세션 사이에 반복 재개해야 하고 별도 상태 저장 소유자가 정해짐 |

## 8. 검증 계약

### 8.1 정적 구조

- `codex-plugins/design-ui/skills/define-ui/SKILL.md`가 존재하고 frontmatter `name`은
  `define-ui`다.
- `references/ui-definition-contract.md`와 `assets/UI-SPEC.template.md`의 링크가
  유효하다.
- plugin manifest는 계속 `./skills/` 하나를 가리키며 marketplace의 plugin 항목은
  하나다.
- README가 `define-ui`·`design-ui`·`review-ui`의 서로 다른 목표와 대표 호출을 설명한다.
- `define-ui`가 제품 UI 소스 비변경, 실패 상태, `ready-for-build` 불변 조건을 명시한다.
- `DefineUiPreflight`가 target·goal 식별 전 `NeedsClarification`, 별도 target과 명시 명세
  target 불일치의 `TargetConflict`, 두 경우의 명세 미생성을 표현한다.
- request와 명세의 `UiTarget`이 kind별 canonical key를 가지며 same-target equality가 exact
  `(kind, key)` 비교로 제한된다.
- `UiSpec.intent`, lifecycle tagged union, known/unknown `AffectedScope`를 포함한
  `FailureContext`, runtime-only `DefineUiPhase`와 phase→persistent status mapping이
  구현된다.
- `AcceptanceCheck`가 §3.5의 세 tagged union 조합만 표현하고 각 결과 상태가 책임 주체와
  일치한다.
- UI 명세 선택이 §3.6의 네 단계 순서와 `Selected | NoSpec | NeedsInput` 결과를 구현한다.
- 기존 `design-ui`와 `review-ui`가 UI 명세 상태와 acceptance checks를 소비한다.

### 8.2 활성화·비활성화 사례

최소한 다음 사례를 독립 실행해 라우팅과 산출물을 평가한다.

| ID | 요청 유형 | 기대 결과 |
|---|---|---|
| U1 | “구현 말고 회원가입 흐름의 화면·상태를 정의해줘” | `define-ui`, UI 소스 불변, 명세 생성 |
| U2 | “모바일과 데스크톱에서 결제 설정이 어떻게 달라질지 정리해줘” | `define-ui`, responsive rules 포함 |
| U3 | 대상·사용자 목표가 없는 “UI 설계해줘” | preflight `NeedsClarification`, UI 명세 미생성, 소스 불변 |
| U4 | 접근 불가 Figma 번역 요청 | `reference-blocked`, 보이지 않는 내용 날조 없음 |
| U5 | “대시보드를 구현해줘” | `define-ui` 비활성, `design-ui` 선택 |
| U6 | “완성된 화면을 검토해줘” | `define-ui` 비활성, `review-ui` Audit 선택 |
| U7 | `ready-for-build` 명세를 경로로 주고 구현 요청 | `design-ui`가 화면·상태·checks를 소비 |
| U8 | 미결 명세를 주고 구현 요청 | 영향 범위 구현 중단, 필요한 결정 보고 |
| U9 | UI 명세가 있는 화면 Audit | finding expected가 명세 절 또는 `UI-AC-*`를 인용 |
| U10 | 사용자 소유 `user-decision` acceptance check | 명시 결정 전 Codex pass 금지, `awaiting-user-acceptance` 유지 |
| U11 | 명시 경로와 다른 동일 target 명세가 함께 있음 | canonical `(kind, key)` exact match만 후보; 명시 경로 우선; 미완성이면 `HaltForSpec`, 다른 명세·하위 authority로 자동 fallback 금지; 명시적 일반 Audit은 명세 기반 판정·Repair 없이 수행 |
| U11-T | 명시 명세 target과 별도 target이 다름 | `define-ui`는 preflight `TargetConflict`; `design-ui`·`review-ui`는 응답 전용 `Design conflict`; 명세·제품·Audit·Repair 변경 없음 |
| U12 | active 지정 없이 동일 target의 `ready-for-build` 명세가 둘 이상 | 후보를 나열한 `Needs input`, 구현 변경 없음 |

#### 8.2.1 렌더 실행 경계

U5~U7·U9와 maker QA·Audit·Repair처럼 실제 화면 근거가 필요한 case는 다음 두 경로 중
하나로만 검증한다.

```text
RuntimeRenderPath =
  | InnerRender {
      producer_call_id,
      capture: RenderCaptureEvidence,
      adjudication: same-call
    }
  | OrchestratedRender {
      producer_call_id,
      pending: RenderBridgePending,
      capture: RenderCaptureEvidence,
      adjudicator_call_id
    }
```

`InnerRender`는 대상 skill을 실행한 inner Codex가 브라우저를 띄우고 같은 호출에서 이미지를
확인하는 기본 경로다. 이 경로가 성공하면 outer bridge를 중복 실행하지 않는다.

`OrchestratedRender`는 평가용 `codex exec --sandbox workspace-write` 안에서 브라우저 생성
또는 loopback bind만 환경 정책으로 차단될 때 쓰는 대체 경로다. 제품 플러그인의 일반
runtime 계약이나 persistent 상태를 추가하지 않으며, 첫 호출의 `Render blocked`를 평가
harness의 `RenderBridgePending` checkpoint로 감싼다. 첫 호출을 나중에 성공으로 소급
변경하지 않는다.

```text
RenderBridgePending = {
  case_id,
  producer_call_id,
  skill: design-ui | review-ui,
  mode: maker-qa | audit | repair-before | repair-after | general-audit,
  blocker_class: sandbox-browser-startup | sandbox-loopback-bind,
  blocker_evidence_path,
  snapshot: ImmutableRenderSnapshot,
  matrix: NonEmptyList<RenderScenario>
}

ImmutableRenderSnapshot = {
  case_realpath,
  fixture_manifest_sha256,
  product_manifest_sha256,
  design_authority_manifest_sha256,
  ui_spec_manifest_sha256,
  plugin_inventory_sha256
}
```

bridge는 다음 조건을 모두 만족할 때만 시작한다.

1. plugin activation·target/spec selection과 필수 build/automated check가 blocker 없이 끝났다.
2. 실패가 앱 오류나 selector 오류가 아니라 원본 stderr로 확인되는 두 sandbox 환경 분류 중
   하나다.
3. case realpath가 격리 evaluation root 아래이고 저장소 root와 다르다.
4. 화면·viewport·state 행렬이 non-empty이며 각 항목을 추측 없이 재현할 수 있다.
5. 제품·디자인 정본·UI 명세·plugin inventory의 snapshot hash가 고정됐다.

앱 자체의 build 실패, 예상 route 부재, 상태 재현 불가, 접근 불가 reference는 bridge로
우회하지 않는다. 각각 기존 `Build blocked`, `Render blocked`, `Reference blocked` 또는
`unverified` 계약을 유지한다.

#### 8.2.2 outer capture 계약

outer runner는 inner Codex sandbox 밖이지만 같은 실행 플랜이 소유한 격리 harness 안에서
동작한다. 입력은 `RenderBridgePending` 하나이며 출력은 다음 구조다.

```text
RenderCaptureEvidence = {
  request_sha256,
  producer_call_id,
  snapshot: ImmutableRenderSnapshot,
  browser: { engine, version, executable_sha256 },
  runner_argv,
  captures: NonEmptyList<{
    scenario_id,
    route_or_file,
    viewport: { width, height },
    state,
    image_path,
    image_sha256,
    exit_code
  }>,
  product_manifest_sha256_after,
  design_authority_manifest_sha256_after,
  ui_spec_manifest_sha256_after,
  fixture_manifest_sha256_after,
  plugin_inventory_sha256_after
}

RenderCaptureResult =
  | Captured { evidence: RenderCaptureEvidence }
  | StaleRenderRequest { mismatched_manifests: NonEmptyList<manifest-name> }
  | IncompleteCapture { missing_scenarios: NonEmptyList<scenario_id> }
  | CaptureBlocked { command, exit_code, stderr_path, affected_scenarios }
```

capture 전후 product·design authority·UI spec hash는 snapshot과 같아야 한다. outer runner는
지정된 evidence subtree에만 이미지와 실행 로그를 쓰며 제품·명세·리포트를 수정하지 않는다.
실행할 browser adapter와 argv는 평가 플랜이 미리 고정하고 hash로 기록한다. inner Codex가
case 안에 새로 작성한 임의 shell/script를 outer 권한으로 실행하지 않는다.

`RenderScenario`는 route 또는 case 내부 file, viewport, 이름 있는 state와 재현 절차만
가진다. 절차는 navigation, query/hash, click, fill with non-secret fixture data, press,
wait-for-visible, screenshot의 제한된 선언형 action만 허용한다. 임의 JavaScript·shell,
credential 입력, evaluation root 밖 file 접근, loopback 밖 network는 허용하지 않는다.

snapshot hash가 하나라도 달라졌거나 scenario가 빠졌거나 이미지가 비어 있거나 browser
exit code가 0이 아니면 `Captured`를 만들지 않고 대응 실패 variant로 끝낸다. 세 실패
variant는 모두 Visual QA와 `codex + render`를 `unverified`로 유지한다.

#### 8.2.3 Codex adjudication 계약

outer capture 뒤에는 under-test plugin의 같은 skill을 격리 Codex로 다시 호출한다. 후속
호출은 `producer_call_id`, `RenderBridgePending`, `RenderCaptureEvidence`의 정확한 경로와
hash를 입력으로 받고, 다음 gate를 통과해야 한다.

bridge case를 시작하기 전 같은 격리 Codex 설정으로 저비용 image adjudication probe를 한
번 실행한다. plan-owned runner가 파일명·크기·metadata로 답을 알 수 없는 단순 challenge
image를 만들고, Codex가 이미지를 열어 도형·색 또는 배치를 판별해야 한다. image-open tool
event가 JSONL에 직접 보이면 그것을 쓰고, schema가 노출하지 않으면 challenge의 숨은 기대값과
응답을 대조한다. 어느 방식으로도 실제 시각 입력 사용을 귀속할 수 없으면 outer capture를
시작하지 않고 `image-not-opened`로 전체 bridge case를 중단한다.

1. source·design authority·UI spec·plugin inventory hash가 capture 시점과 같다.
2. 요청 행렬과 capture의 `scenario_id`가 exact match하며 viewport·state 누락이 없다.
3. Codex가 각 실제 image를 시각 입력으로 열어 확인한다. 파일 존재·크기·hash·alt text만
   읽는 것은 판정이 아니다.
4. finding과 acceptance result는 확인한 capture 경로·scenario와 기존 authority를 인용한다.

```text
RenderAdjudicationResult =
  | Adjudicated {
      adjudicator_call_id,
      producer_call_id,
      snapshot: ImmutableRenderSnapshot,
      opened_images: NonEmptyList<{ scenario_id, image_path, image_sha256 }>,
      verdict_or_acceptance_results
    }
  | AdjudicationUnverified {
      adjudicator_call_id,
      reason: stale-snapshot | missing-scenario | image-not-opened | skill-attribution-missing,
      affected_scenarios
    }
```

gate 뒤 `design-ui`는 maker QA, `review-ui`는 Audit/GeneralAudit/Repair의 원래 판정 계약을
계속 수행한다. outer runner의 의견은 authority가 아니며 adjudicator가 독립적으로
`pass | fail | unverified`를 정한다. 후속 Codex가 이미지를 열 수 없으면 capture가 있어도
`unverified`다.

maker QA 또는 Repair adjudication이 소스를 수정하면 모든 이전 capture는 즉시 stale이다.
새 product hash로 `RenderBridgePending → capture → adjudication`을 다시 수행해야 한다.
Audit과 GeneralAudit은 기존 비파괴 계약을 유지한다. Repair는 before evidence와 findings를
먼저 고정하고 수정 뒤 새 snapshot의 같은 scenario 행렬로 after evidence를 만들어야 한다.

#### 8.2.4 평가 귀속과 종료 조건

- skill 활성화·구현·명세 선택 근거는 inner producer/adjudicator JSONL과 설치본 hash chain에
  귀속한다.
- browser 실행과 pixel output은 outer runner evidence에 귀속한다.
- Visual QA·finding·acceptance 판정은 이미지를 연 Codex adjudicator에 귀속한다.
- 세 귀속 중 하나라도 없으면 해당 render case는 성공이 아니다.
- direct inner render와 bridged render는 같은 case의 중복 성공으로 세지 않는다.
- browser가 inner와 outer 모두에서 불가하거나 adjudicator가 image를 볼 수 없으면
  원본 오류·재현 명령·미검증 행렬을 남기고 실행을 중단한다.

최소 bridge 회귀 사례는 다음을 추가한다.

| ID | 조건 | 기대 결과 |
|---|---|---|
| BR0 | 격리 Codex image adjudication challenge | 실제 image-open 귀속 성공; 불가하면 bridge case 시작 전 중단 |
| BR1 | inner browser render 성공 | bridge 미사용, same-call 판정 |
| BR2 | inner sandbox browser만 차단, outer와 image adjudication 가능 | 세 단계 lineage가 있는 유효 render 판정 |
| BR3 | capture 전 snapshot hash 불일치 | `StaleRenderRequest`, browser 미실행 |
| BR4 | capture 후 source/spec/design hash 변경 | adjudication 거부, `unverified` |
| BR5 | viewport·state 일부 누락 또는 image/exit 오류 | `IncompleteCapture` 또는 `CaptureBlocked` |
| BR6 | outer PNG만 있고 Codex image adjudication 없음 | Visual QA·`codex + render` 성공 금지 |
| BR7 | Audit/GeneralAudit bridge | report/evidence만 변경, source·design·spec 불변 |
| BR8 | Repair bridge | before 고정 → 허용 수정 → 새 hash의 같은 행렬 after → 재판정 |
| BR9 | case 작성 script의 outer 실행 요구 | 실행 거부; plan-owned hashed adapter만 사용 |
| BR10 | 외부 network·credential·evaluation root 밖 접근 요구 | 실행 거부와 명시적 blocker |

### 8.3 행동 불변 조건

- `define-ui`는 제품 방향이 갈릴 때 UI 구조로 그 결정을 숨기지 않는다.
- `define-ui`는 제품 UI 소스·테스트·빌드 설정을 변경하지 않는다.
- 접근 불가 reference와 아직 구현되지 않은 화면을 본 것처럼 서술하지 않는다.
- `ready-for-build` 명세에는 제품 방향 미결과 관측 불가능한 acceptance check가 없다.
- 명세가 없어도 구체적인 소형 구현은 `design-ui`로 바로 갈 수 있다.
- `design-ui`는 미결 또는 충돌 상태의 명세를 조용히 구현하지 않는다.
- `review-ui`는 ready target 명세를 일반 휴리스틱보다 우선하며 근거를 인용한다. non-ready
  명세에서는 자동으로 하위 authority로 전환하지 않고, 명시적 일반 Audit만 명세 기반
  판정·Repair 없이 허용한다.
- `owner: user` acceptance check는 Codex가 대신 승인하지 않는다.
- acceptance check는 `codex+render`, `codex+automated-check`, `user+user-decision` 세
  조합만 존재한다.
- 동일 target의 UI 명세는 명시 경로 → 프로젝트 active 지정 → 단일 ready 후보 순서로
  선택한다. target은 canonical `(kind, key)` exact match만 같고 복수 후보를 alias나 최신
  추측으로 고르지 않는다. 명시 명세 target과 별도 target이 다르면 명세 생성·수정 없이
  preflight `TargetConflict`로 끝낸다.
- 공개·배포는 사용자의 명시적 승인과 프로젝트별 배포 권한 없이 실행하지 않는다.
- outer runner는 화면을 캡처할 뿐 Visual QA·finding·acceptance 결과를 판정하지 않는다.
- snapshot·scenario·image adjudication lineage가 끊기거나 stale이면 bridged render를
  합격 근거로 사용하지 않는다.

## 9. 호환성과 전환

- 기존 `design-ui`·`review-ui` 호출과 산출물은 그대로 유효하다.
- 기존 프로젝트에 UI 명세가 없어도 동작한다. 이번 확장은 강제 migration이 아니다.
- 선행 정본 §3.2의 9개 정확 파일 집합은 구현 시 이 문서 §3.3의 세 파일이 추가된
  12개 집합으로 대체된다.
- 선행 정본 §3.3의 디자인 정본 우선순위는 target 전용 `ready-for-build` UI 명세를
  프로젝트 디자인 정본 앞에 삽입하는 이 문서 §4.3·§5 계약으로 확장된다.
- 선행 정본의 브라우저 근거 없는 합격 금지, Audit 비파괴성, Repair before/after,
  Claude Code 트리 비변경 조건은 그대로 유지된다.
- §8.2의 outer capture bridge는 격리 runtime 평가 harness의 선택적 어댑터다. 제품
  플러그인에 MCP·브라우저 서버·상시 스크립트 의존성을 추가하지 않으며, outer PNG만으로
  기존 `Render blocked`를 성공으로 바꾸지 않는다.

## 10. 참고한 자료와 읽은 범위

- `docs/codex-ui-design-skills.md`: 전체 설계와 v1 경계·계약을 읽음.
- `codex-plugins/design-ui/skills/design-ui/SKILL.md`: 구현·maker QA·실패 계약을 읽음.
- `codex-plugins/design-ui/skills/review-ui/SKILL.md`: Audit·Repair·발견 계약을 읽음.
- 사용자 제공 `Codex UI Design Workflow 정리`: 전체 읽음. 아이디어 → 디자인 규칙 →
  구현 → 브라우저 확인 → Visual QA → 수정 흐름을 참고함.
- 이 저장소의 `interview`·`make-design`·`verify` 등 기존 스킬 frontmatter: 중복 경계
  판정에 필요한 범위를 읽음.
- `plans/20260905-codex-ui-workflow-skills-plan.md`: 독립 검토에서 드러난 D-001~D-006의
  경계와 권장안을 읽고 preflight·non-ready review·target identity·phase/status·failure
  affected scope 계약으로 확정함.
- `plans/20260905-codex-ui-workflow-skills-execute-report.md`: 전체 읽음. outer Chromium은
  같은 fixture를 렌더했지만 inner `workspace-write`에서는
  `sandbox_host_linux.cc ... Operation not permitted`가 반복된 실측과 미검증 범위를
  §8.2 render bridge의 입력 근거로 사용함.
- [OpenAI Docs — Build skills](https://developers.openai.com/plugins/build/skills):
  스킬을 인식 가능한 사용자 목표에 집중하고 트리거·입력·성공 기준이 다르면 분리하며,
  reference·asset·script를 역할에 따라 배치하는 현재 규약을 읽음(2026-09-04).

## 11. 미결 — 이 문서가 정하지 않은 것

없음.

2026-09-04에 이전 플랜 검토에서 발견된 두 미결을 §3.5·§3.6으로 확정했다.
AcceptanceCheck는 세 조합만 허용하고, 복수 UI 명세는 명시 경로 → 프로젝트 active 지정 →
단일 `ready-for-build` 후보 → `Needs input` 순서로 선택한다.

2026-09-05 사용자 요청으로 후속 플랜 독립 검토에서 발견된 두 경계를 확정했다. 불명확한
target·goal은 명세 상태 machine 밖의 preflight 질문으로 처리하며 partial spec을 만들지
않는다. `review-ui`가 non-ready 명세를 선택하면 기본적으로 `HaltForSpec`이고, 사용자가
명세와 독립적인 일반 Audit을 명시한 경우에만 명세 기반 판정·Repair 없이 제한적으로
진행한다.

같은 날 후속 독립 검토에서 드러난 두 계약도 확정했다. target은 §3.6의 kind별 canonical
key를 가진 `UiTarget`으로 정규화하고 exact `(kind, key)`만 같은 target으로 본다. UI 명세는
`intent`를 저장하는 lifecycle tagged union이며, 정상·실패 workflow 위치는 runtime-only
`DefineUiPhase`로 다루고 §4.4의 표대로 persistent status와 원자적으로 연결한다.
플랜의 component module-path 초안은 `define-ui`가 구현 파일을 선택하지 않는 경계와 파일
이동 안정성을 깨므로 채택하지 않고, owner target과 semantic slug로 구성한 key로 확정했다.

2026-09-05 사용자 승인으로 플랜 최종 독립 검토에서 드러난 두 계약 충돌도 닫았다. 명시
명세 target과 별도 target의 불일치는 draft 생성 전 응답 전용 `TargetConflict`로 처리해
`Intake` 무실패와 persistent failure variant를 유지한다. 실패 영향 범위는
`KnownAffectedScope | UnknownTargetScope` tagged union이며, 접근 불가 주 reference 때문에
screen/flow 이름을 알 수 없으면 target 전체의 unknown scope를 이유와 함께 기록하고 이름을
추측하지 않는다.

2026-09-05 T-006 실측에서 inner `workspace-write`의 Chromium 생성이 반복 차단됐지만 같은
snapshot의 outer Chromium 캡처는 가능했다. 이에 따라 §3.5의 `owner: codex`를 판정 주체로
명확히 하고, §8.2에 evaluation-only `producer → outer capture → Codex adjudicator` 계약을
확정했다. outer runner는 판정하지 않으며 immutable source/spec/design/plugin hash와 exact
scenario lineage가 없으면 성공으로 셀 수 없다. 이 bridge는 제품 플러그인 runtime이나
MCP 의존성을 추가하지 않는다.

`accept-ui`·`test-ui`·`deploy-ui`·`prototype-ui`는 현재 필요하지 않다고 판정했으며, §7의
재도입 트리거가 실제 사용에서 관측되면 별도 설계한다.
