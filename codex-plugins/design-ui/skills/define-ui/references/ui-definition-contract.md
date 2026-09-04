# UI 정의 계약

`define-ui`가 요청을 정규화하고 UI 명세를 작성·재개하거나 기존 명세를 선택할 때 읽는다.
타입 이름은 내부 계약이며 사용자에게 같은 형식의 입력을 요구하지 않는다.

## 요청과 target

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

Route key는 query와 hash를 제거하고 `/`로 시작하는 프로젝트 router pattern을 유지한다.
root가 아닌 route의 trailing slash만 제거하며 framework의 dynamic segment 표기를 다른
문법으로 바꾸지 않는다.

Component owner는 `global` 또는 `route`·`screen-set`·`new-app` target만 허용한다.
`global` owner key는 `project`다. 예: `global:project#button`,
`route:/settings/profile#profile-form`. component가 다른 component를 owner로 갖거나
module/export path를 identity로 쓰는 형태는 허용하지 않는다.

Screen-set과 new-app key는 lowercase-kebab stable slug다. 표시 이름이나 파일 위치가
바뀌어도 유지한다. 같은 target은 case-sensitive canonical `(kind, key)` exact match뿐이다.
명세 ID·파일 경로·표시 이름·mtime·날짜·사전식 순서·alias 유사성은 equality가 아니다.

## Preflight

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
      material_effect: why the mismatch changes the affected screen or flow,
      resolution_needed: choose explicit target | use spec target | provide matching spec,
      resume_condition: one canonical target and matching spec are selected
    }
```

명시 명세가 target의 유일한 입력이면 그 명세 target을 request target으로 정규화할 수
있다. 별도 target과 다르면 `TargetConflict`이며 target을 고쳐 맞추거나 다른 명세로
fallback하지 않는다. 두 non-Ready 결과는 명세 파일·ID·status와 제품 소스를 만들거나
변경하지 않는다. 해소 뒤 preflight를 처음부터 다시 평가한다.

## 같은 target의 명세 선택

canonical target이 같은 후보만 대상으로 다음 순서를 적용한다.

1. 현재 요청에서 사용자가 명시한 정확한 명세 경로
2. 프로젝트 지침이나 명세 인덱스가 해당 target의 active 명세로 지정한 정확한 경로
3. 같은 target의 `ready-for-build` 후보가 정확히 하나인 경우
4. 하나를 고를 수 없으면 `NeedsInput { candidate_paths }`

```text
UiSpecSelection =
  | Selected { path }
  | NoSpec
  | NeedsInput { candidate_paths }
```

명시 또는 active 명세가 non-ready이면 다른 ready 명세로 fallback하지 않는다. 같은 target을
개정할 때는 선택된 명세를 in-place 갱신한다. 여러 버전을 유지하려면 프로젝트가 active
명세를 지정해야 한다.

## UI 명세 lifecycle

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
      reason: why stable names cannot be known without the blocked reference
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
```

`UnknownTargetScope`는 접근 불가 주 reference 때문에 stable screen/flow 이름 자체를 알 수
없는 `ReferenceBlockedFailure`에만 쓴다. 나머지 세 failure variant는
`KnownAffectedScope`만 허용한다. 빈 목록이나 추측한 이름으로 채우지 않는다.

## 화면과 acceptance

```text
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

다른 owner/evidence 조합은 만들 수 없다. screenshot이 사용자 결정을 돕더라도 사용자 소유
check의 판정 증거는 `user-decision`이다. 사용자의 명시적 승인·거절 전에는 각각 pass·fail로
바꾸지 않는다.

화면과 flow는 서로 연결한다. 각 핵심 화면은 목적, content hierarchy, 실제 존재할 상태,
interaction, accessibility expectation을 가진다. responsive rule은 viewport 숫자만 쓰지
말고 정보 우선순위, reflow, 숨김·대체되는 행동을 관측 가능하게 적는다. component reuse는
기존 계약을 재사용하는지, 확장하는지, 신규가 필요한지를 구분하되 구현 파일이나 라이브러리를
선택하지 않는다.

## Runtime phase와 저장 규칙

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

| Runtime phase | 성공 시 다음 | 실패 phase | Persistent status |
|---|---|---|---|
| `Intake` | `AuthorityReady` | 없음 | `draft` |
| `AuthorityReady` | `DefinitionDrafting` | `ReferenceBlocked` | `draft` 또는 `reference-blocked` |
| `DefinitionDrafting` | `DecisionCheck` | `DesignConflict` | `draft` 또는 `design-conflict` |
| `DecisionCheck` | `ReadyForBuild` | `NeedsInput` 또는 `DesignConflict` | `draft`, `needs-input` 또는 `design-conflict` |
| `ReadyForBuild` | `Done` | 없음 | `ready-for-build` |
| `Done` | 종료 | 없음 | `ready-for-build` 유지 |

- preflight `Ready` 뒤 `DraftUiSpec`과 `Intake`를 시작한다.
- 정상 `Intake`~`DecisionCheck`는 runtime phase를 저장하지 않고 `draft`를 유지한다.
- 실패 진입 시 대응 status와 `FailureContext`를 한 번에 기록한다.
- 재개 조건을 확인한 뒤 failure를 제거하고 `draft`로 바꾼 다음 `resume_at`에서 실행한다.
- `ReadyForBuild` 진입 시 `unresolved: []`, `failure: absent`, `ready-for-build`을 한 번에
  기록한다.
- 정상 phase 도중 남은 draft는 다음 실행에서 `Intake`부터 다시 대조한다. 파일명·mtime·
  partial content로 runtime phase를 복원하지 않는다.

## Authority

아래 순서에서 숫자가 작은 근거가 우선한다.

1. 현재 사용자의 명시적 요구와 승인된 범위
2. 대상 저장소의 `AGENTS.md` 및 프로젝트 지침
3. 위 선택 규칙으로 하나로 정한 target UI 명세
4. `DESIGN.md` 또는 동등한 제품 디자인 정본
5. 디자인 토큰과 공용 컴포넌트 계약
6. 현재 제품과 기존 UI 코드에서 반복 확인되는 패턴
7. 이번 작업의 접근 가능한 참고물
8. 일반적인 UI·사용성 휴리스틱

상하위 근거를 조용히 섞거나 충돌을 숨기지 않는다. 일반 휴리스틱을 제품 요구로 승격하지
않는다. UI 명세 하나의 일회성 픽셀 값은 디자인 정본으로 올리지 않고, 여러 화면에 재사용될
새 규칙이 확정된 경우에만 적용 범위와 함께 갱신한다.

## Ready-for-build 불변 조건

다음과 공존할 수 없다.

- 제품 방향을 바꾸는 미결
- 접근하지 못한 주 reference를 본 것처럼 쓴 규칙
- 관측할 수 없는 acceptance check
- 허용된 세 조합 밖의 acceptance check
- 화면 목록에는 있지만 상태·flow 어디에도 연결되지 않은 핵심 화면

`unresolved`가 남아 있으면 영향에 따라 `needs-input` 또는 `design-conflict`다.
