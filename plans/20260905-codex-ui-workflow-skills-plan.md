# Codex UI Workflow Skills 확장 실행 플랜

- 상태: **중단 (2026-09-05, T-005까지 완료 / T-006 inner browser gate `Operation not permitted`)**
- 실행 리포트: `plans/20260905-codex-ui-workflow-skills-execute-report.md`
- 작성일: 2026-09-05
- 정본 설계 문서: `docs/codex-ui-workflow-skills.md`
- 선행 정본: `docs/codex-ui-design-skills.md`

## 1. 개요

### 목표

기존 Codex 전용 `design-ui` 플러그인에 구현 전 UI 정의를 담당하는 `define-ui`를 추가하고,
`ready-for-build` UI 명세와 acceptance checks가 `design-ui` 구현 및 `review-ui` 독립
검토까지 손실 없이 전달되는 세 스킬 workflow를 완성한다.

### 전제한 기술 스택

- instruction-only Codex 플러그인: Markdown `SKILL.md`·reference·asset과 JSON manifest
- 기존 설치 단위: `codex-plugins/design-ui/`
- 기존 표준 링크 게이트: `python3 scripts/validate_skill_links.py`
- 기존 skill validator:
  `/home/13ruce/.codex/skills/.system/skill-creator/scripts/quick_validate.py`
- 런타임 평가는 현재 환경의 `codex exec`와 대상 fixture가 이미 제공하는 실행·브라우저
  능력을 우선 사용한다. 새 MCP나 브라우저 서버를 도입하지 않는다.

### 제약 조건

- Codex 전용 확장이다. `.claude-plugin/`과 `plugins/**`는 변경하지 않는다.
- 플러그인 이름과 marketplace 항목은 `design-ui` 하나를 유지한다.
- 새 스킬은 `define-ui` 하나뿐이다. `accept-ui`·`test-ui`·`deploy-ui`·`prototype-ui`는
  구현하지 않는다.
- `define-ui`는 제품 UI 소스·테스트·빌드 설정을 변경하지 않는다.
- UI 명세는 선택적 선행 산출물이다. 명세가 없는 구체적 구현을 막지 않는다.
- 사용자 소유 acceptance check와 공개 결정은 Codex가 대신 승인하지 않는다.
- 계약과 구현이 어긋나면 코드를 임의로 맞추지 않고 실행을 중단해 설계 변경으로
  승격한다.

### 현재 상태

- v1 `design-ui`·`review-ui` 플러그인 구현과 독립 검증은 완료되어 있다.
- 신규 확장 설계 문서 `docs/codex-ui-workflow-skills.md`가 작성되어 있으며 구현 전
  작업 변경으로 아직 추적되지 않은 상태다.
- `define-ui` 디렉터리와 세 supporting file은 아직 없다.
- 작업 원장(`kanban.md`·`workstate.md`)과 프로젝트 에이전트 로스터는 없다.

### 성공 기준

아래 조건을 모두 명령 또는 보존된 실행 근거로 확인한다.

1. 정본 §3.3의 신규 세 파일을 포함해 `codex-plugins/design-ui/`의 정확한 파일 집합이
   12개다.
2. `define-ui` frontmatter·입력·출력·상태 전이·비변경·완료 보고 계약이 정본 §4와
   일치한다.
3. `design-ui`와 `review-ui`가 정본 §5의 UI 명세 상태·authority·acceptance check
   handoff를 소비하며 기존 v1 불변 조건을 깨지 않는다.
4. manifest와 marketplace에는 `design-ui` 플러그인이 정확히 하나이며 README가 세
   스킬의 서로 다른 목표를 설명한다.
5. 정본 §8.2의 U1~U12·U11-T와 이 플랜의 하위 case를 모두 독립 실행해 활성화·비활성화·중단·
   handoff를 판정한다. 하나라도 실행할 수 없으면 완료로 세지 않고 플랜을 중단하며 원본
   오류와 재현 명령을 `미검증`으로 남긴다.
6. 정본 §8.3의 11개 행동 불변 조건에 계약 위반이 없다.
7. 링크, JSON, plugin/skill validator, protected Claude tree, whitespace와
   `git diff --check`가 모두 통과한다.
8. 독립 검증자가 정본에서 기대값을 다시 추출해 blocker·major·moderate·minor 어느
   등급에도 계약 위반이 없다고 판정한다.

## 2. 작업 목록

| 우선순위 | ID | 작업명 | 선행 | 산출물 |
|---|---|---|---|---|
| P0 | T-001 | `define-ui` 계약과 템플릿을 구현한다 | 없음 | 신규 skill·reference·asset 3개 |
| P1 | T-002 | `design-ui`에 UI 명세 handoff를 연결한다 | T-001 | 수정된 `design-ui/SKILL.md`와 정본 reference |
| P1 | T-003 | `review-ui`에 UI 명세·acceptance 판정을 연결한다 | T-001 | 수정된 `review-ui/SKILL.md`와 QA reference/template |
| P1 | T-004 | 플러그인 설명과 카탈로그 안내를 세 스킬 기준으로 갱신한다 | T-001 | plugin README·manifest·root README, marketplace 확인 |
| P2 | T-005 | 구조·계약·보호 트리를 정적으로 검사한다 | T-002, T-003, T-004 | 정적 대조표와 검사 출력 |
| P2 | T-006 | U1~U12·U11-T 활성화·handoff 행동을 평가한다 | T-005 | 격리 fixture와 런타임 평가 근거 |
| P2 | T-007 | 독립 재검증과 통합 게이트를 통과한다 | T-006 | 독립 판정과 최종 게이트 출력 |
| P3 | T-008 | 성공·중단 실행 기록을 닫고 temp를 정리한다 | T-001~T-007의 완료 또는 중단 | 실행 리포트·작업별 커밋 또는 staging 제안 |

## 3. 역할 분담

프로젝트에 표준 에이전트 로스터가 없으므로 이름이 붙은 임시 역할은 만들지 않는다.

| 구분 | 담당 범위 | 금지 사항 |
|---|---|---|
| 수행자 | T-001~T-006 구현·fixture 실행·1차 검사, T-007 발견 수정, T-008 기록·민감 temp/snapshot 정리 | 정본에 없는 계약 추가, Claude tree 변경, 미실행 사례의 성공 처리 |
| 독립 검증자 | T-007에서 정본 설계와 실물·원본 실행 근거를 역방향 대조 | 수행자의 기대값·요약을 그대로 채택, 구현 수정 |

독립 검증자는 구현 설명 없이 정본 경로, 검증 대상 경로, 실행 evidence 경로만 받는다.
발견 수정은 수행자가 맡고 같은 검증자가 수정된 실물을 재판정한다.

## 4. 상세 작업 명세

### T-001 — `define-ui` 계약과 템플릿을 구현한다

내용:

- `SKILL.md` frontmatter는 `name: define-ui`와 인식 가능한 사용자 목표가 앞부분에 있는
  description만 둔다.
- 본문에 `UiTarget`, `DefineUiRequest`, `DefineUiPreflight`, `UiSpecCommon`, lifecycle별
  `UiSpec`, `FailureContext`, `DefineUiPhase`, `ScreenSpec`, `AcceptanceCheck`를 사용자에게
  타입 입력을 강요하지 않는 정규화 계약으로 구현한다. `DefineUiRequest.target`은
  `UiTarget`, `goal`은 필수 user-visible outcome이며 `UiSpecCommon`은 같은 target과
  `intent`를 저장한다.
- `UiTarget`은 `route | component | screen-set | new-app`의 네 tagged union으로 구현한다.
  route는 query/hash와 non-root trailing slash를 제거하되 프로젝트 router의 dynamic
  segment 표기를 유지한다. component key는 구현 module/export가 아니라
  `<owner-kind>:<owner-key>#<lowercase-kebab component slug>`이다. owner-kind는 `global` 또는
  `route | screen-set | new-app`만 허용하고 `component` owner는 금지하며, global owner key는
  `project`다. screen-set과 new-app은 생성 뒤 표시 이름이나 파일 경로가 바뀌어도 유지되는
  lowercase-kebab stable slug를 쓴다.
- same-target은 case-sensitive canonical `(kind, key)` exact match로만 판정한다. 명세 ID,
  파일 경로, 표시 이름, 수정 시각, 날짜, 사전식 순서와 alias 유사성을 equality에 쓰지
  않으며 `<target-slug>`는 저장 경로용 파생값으로만 둔다.
- target 또는 goal이 식별되지 않으면 상태 machine 전 `NeedsClarification`으로 끝낸다.
  파악된 맥락·빠진 입력·화면 영향·집중 질문 하나·재개 조건과 명세 미생성을 보고하고,
  답을 받으면 preflight를 다시 평가한다. 이 경로에서는 명세 파일·ID·status를 만들지 않는다.
- target과 goal을 적을 수 있어도 제품의 대상 사용자·핵심 가치처럼 “무엇을 왜 만들지”가
  여러 방향으로 갈리면 화면 구조에서 임의 결정하지 않고 `interview`로 넘긴다. 이는
  입력 필드 누락의 `NeedsClarification`과 별도 경계로 표현한다.
- `AcceptanceCheck`는 `codex+render`, `codex+automated-check`,
  `user+user-decision` 세 tagged union만 표현하고, 책임 주체별 `AcceptanceResult` 상태를
  구분한다.
- 기존 명세의 revise·reuse에는 canonical target이 같은 후보에 한해 명시 경로 → 프로젝트
  active 지정 → 단일 `ready-for-build` 후보 → `Needs input` 순서의 선택 규칙을 적용한다.
  명시 UI 명세가 target의 유일한 입력이면 그 명세 target으로 정규화할 수 있지만, 별도
  target과 명세 target이 다르면 target을 고쳐 맞추거나 fallback하지 않고 draft 생성 전
  응답 전용 preflight `TargetConflict`로 끝낸다. explicit target·spec target·spec path·
  material effect·resolution needed·resume condition을 보고하며 명세와 제품을 변경하지 않는다.
- preflight `Ready` 뒤에만 `DraftUiSpec`을 만들고 runtime-only `DefineUiPhase`의
  `Intake → AuthorityReady → DefinitionDrafting → DecisionCheck → ReadyForBuild → Done`과
  `NeedsInput`·`ReferenceBlocked`·`DesignConflict` 실패 phase를 구현한다. `Intake`의 실패
  phase는 없다.
- `UiSpec`은 정본 §4.2의 lifecycle tagged union으로 구현한다. `draft`와
  `ready-for-build`에는 `failure`가 없고, `needs-input`·`design-conflict`는 non-empty
  `unresolved`를 요구하며, 세 실패 status는 허용된 `FailureContext` 변형만 가진다.
- `FailureContext`는 정본 §4.2의 네 변형과 exact `last_completed_phase`·`resume_at`을
  표현한다. `NeedsInputFailure`와 두 `DesignConflict` 변형은 `KnownAffectedScope`만,
  `ReferenceBlockedFailure`는 `KnownAffectedScope | UnknownTargetScope`를 허용한다. unknown은
  접근 불가 주 reference 때문에 stable screen/flow 이름을 알 수 없을 때 target과 이유를
  기록하며 빈 목록이나 추측한 이름을 허용하지 않는다. 정상
  `Intake`~`DecisionCheck`는 phase를 저장하지 않고 `draft`를
  유지하며 실패 진입과 `ReadyForBuild` 진입은 status·failure·unresolved를 원자적으로
  기록한다. 재개 조건 확인 뒤에만 failure를 지우고 `draft`로 돌려 `resume_at`에서
  재개하며, 정상 phase 도중 남은 draft는 다음 실행에서 `Intake`부터 다시 대조한다.
  파일명·mtime·부분 내용으로 runtime phase를 추측하지 않는다.
- `ready-for-build`과 공존할 수 없는 다섯 조건, UI 소스·테스트·빌드 설정 비변경, 사용자
  소유 check 자동 승인 금지를 명시한다.
- `references/ui-definition-contract.md`에 정본 우선순위, UI 명세와 `DESIGN.md` 구분,
  화면·흐름·상태·responsive·component reuse·acceptance 작성 기준을 둔다.
- authority는 정확히 사용자 요구·승인 범위 → 저장소 지침 → 선택된 target UI 명세 →
  제품 디자인 정본 → 토큰·공용 컴포넌트 계약 → 기존 UI 반복 패턴 → 접근 가능한 참고물 →
  일반 휴리스틱의 여덟 출처 순서로 평가한다. 상하위 출처를 조용히 섞거나, 충돌을 숨기거나,
  휴리스틱을 제품 요구로 승격하지 않는다.
- reference 번역이 작업의 주목적이고 그 reference에 접근할 수 없을 때만
  `Reference blocked`로 끝내고, 부차 reference가 없을 때는 계속 진행하며, 사용자가
  reference와 독립적인 fallback 범위를 승인한 경우는 그 승인 범위만 사용하는 세 분기를
  명시한다.
- `assets/UI-SPEC.template.md`는 canonical `UiTarget`, `intent`, `UiSpecCommon`과 정본 §4.2의
  lifecycle별 status·unresolved·failure 조합을 복사 가능한 UI 명세 골격으로 제공한다.
- 프로젝트 규약이 없을 때 기본 산출물 경로는 `design/specs/<target-slug>.md`다.
- 상태 machine 안에서 `Needs input`·`Reference blocked`·`Design conflict`로 전이한 실패는
  원인, 마지막 완료 지점, 필요한 사용자 입력, typed affected scope, 재개 조건을 UI 명세와
  최종 응답 양쪽에 남긴다. `NeedsClarification`과 `TargetConflict`는 명세를 만들지 않고
  각 preflight 응답 계약을 따른다.

산출물:

- `codex-plugins/design-ui/skills/define-ui/SKILL.md`
- `codex-plugins/design-ui/skills/define-ui/references/ui-definition-contract.md`
- `codex-plugins/design-ui/skills/define-ui/assets/UI-SPEC.template.md`

검증 조건:

- [ ] 아래 명령이 frontmatter name과 필요한 두 상대 링크를 검증한다.

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('codex-plugins/design-ui/skills/define-ui/SKILL.md')
text = p.read_text()
assert text.startswith('---\nname: define-ui\n')
for rel in (
    'references/ui-definition-contract.md',
    'assets/UI-SPEC.template.md',
):
    assert rel in text, rel
    assert (p.parent / rel).is_file(), rel
PY
```

- [ ] 입력의 필수 `target: UiTarget`·goal·네 target·세 intent·여섯 Reference 변형과
      출력의 `DefineUiPreflight`·`UiSpecCommon`·lifecycle별 `UiSpec`·`FailureContext`·
      `DefineUiPhase`·`ScreenSpec`·`AcceptanceCheck` 필드가 본문 또는 reference/template에
      모두 대응된다.
- [ ] route·component·screen-set·new-app 각각의 canonical key 규칙이 있고 component key는
      module/export path가 아니라 semantic owner+slug다. equality는 case-sensitive exact
      `(kind, key)`뿐이며 ID·경로·표시 이름·mtime·날짜·alias와 파생 `<target-slug>`를
      identity로 쓰지 않는다.
- [ ] component owner matrix는 `global:project`, route, screen-set, new-app owner를 모두
      허용하고 component owner와 그 밖의 owner kind를 만들 수 없다.
- [ ] `NeedsClarification`의 다섯 필드와 명세 파일·ID·status 미생성, 제품 소스 비변경,
      답변 후 preflight 재평가가 구현된다.
- [ ] 입력 누락과 제품의 무엇·왜 결정 분기를 구분하고, 후자는 UI 명세 생성 없이
      `interview`로 넘기는 정본 §4.1·§5.4 경계가 구현된다.
- [ ] acceptance check는 세 유효 owner/evidence 조합만 표현하고,
      `codex+user-decision`·`user+render`·`user+automated-check`를 만들 수 없다.
- [ ] Codex 결과는 `pass | fail | unverified`, 사용자 결과는
      `awaiting-user-acceptance | pass | fail`로 제한된다.
- [ ] 기존 UI 명세 선택이 canonical target exact match 후보에 대해 정본 §3.6의 네 단계
      순서와 `Selected | NoSpec | NeedsInput` 결과를 따른다. 명시 명세만 target 입력인 경우의
      정규화와 별도 target 불일치의 preflight `TargetConflict`도 구현된다.
- [ ] 정본 §4.3의 authority 여덟 출처가 정확한 순서로 있고, silent mixing·충돌 은폐·
      heuristic의 제품 요구 승격을 금지한다.
- [ ] `Ready | NeedsClarification | TargetConflict`의 세 preflight 결과, 여섯 정상 runtime
      phase와 세 실패 phase,
      `Intake` 실패 없음, lifecycle tagged union과 `ready-for-build` 금지 조합 다섯 가지가
      표현된다.
- [ ] 네 `FailureContext` 변형의 `last_completed_phase`·`resume_at`, known-only 세 변형과
      known-or-unknown `ReferenceBlockedFailure`의 affected scope 조합, 정상 phase의
      `draft` 유지, 실패/ready의 원자 기록, 조건 확인 뒤 resume, 중단 draft의 `Intake`
      재시작이 정본 §4.4와 1:1로 대응한다.
- [ ] reference 번역이 작업의 주목적인 경우의 접근 실패, 부차 reference 부재, 승인된
      독립 fallback의 세 분기가 과도한 중단이나 추측 없이 구분된다.
- [ ] 세 실패 상태로 전이하면 명세와 최종 응답에 원인·마지막 완료 지점·필요 입력·
      typed 영향 범위·재개 조건 다섯 payload가 있다. `NeedsClarification`과
      `TargetConflict`는 UI 명세를 만들지 않고 각 preflight 응답 payload만 낸다.
- [ ] 제품 UI 소스·테스트·빌드 설정 비변경과 “미래 화면을 렌더링했다고 주장하지 않음”이
      명시된다.
- [ ] 현재 실행 화면은 현황 근거로만 확인하고, 존재하지 않는 상태를 억지로 추가하지
      않으며, 구현 파일·라이브러리를 선택하지 않는 경계가 있다.
- [ ] 일회성 규칙을 `DESIGN.md`에 올리지 않고 여러 화면에 재사용될 규칙이 확정된
      경우에만 갱신한다.
- [ ] 완료 보고 일곱 항목과 기본 명세 경로가 구현된다.
- [ ] 아래 quick validator가 통과한다.

```bash
python3 /home/13ruce/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex-plugins/design-ui/skills/define-ui
```

커밋 경계: T-001의 신규 세 파일만 원자 커밋 후보로 묶는다.

### T-002 — `design-ui`에 UI 명세 handoff를 연결한다

내용:

- 구현 전에 request와 명세의 `UiTarget`을 정본 §3.6대로 canonicalize하고 exact
  `(kind, key)`가 같은 후보에 한해 명시 경로 → 프로젝트 active 지정 → 단일
  `ready-for-build` 후보 순서로 선택한다. 결과는 `Selected | NoSpec | NeedsInput`으로
  제한한다.
- 명세 ID·파일 경로·표시 이름·수정 시각·날짜·사전식 순서·alias 유사성을 same-target
  근거로 쓰거나 최신을 추측하지 않는다. 명시 경로가 target의 유일한 입력이면 명세 target을
  정규화해 사용할 수 있지만, 별도 target과 다르면 두 canonical target·명세 경로·영향·
  필요 결정을 담은 응답 전용 `Design conflict`로 중단하고 명세 선택·구현을 시작하지 않는다.
  명시 경로가 미완성 상태면 다른 ready 명세로 자동 fallback하지 않는다.
- `ready-for-build` 명세의 화면·상태·responsive rules·acceptance checks를 구현 범위와
  maker QA 행렬로 변환한다.
- `draft`·`needs-input`·`design-conflict`·`reference-blocked`를 각각 정본 §5.1대로
  처리하고 영향 범위를 조용히 구현하지 않는다.
- 명세가 없고 요구가 충분히 구체적인 소형 구현은 기존 흐름으로 계속 허용한다.
- 현재 사용자 요구와 명세가 충돌하면 충돌·영향을 보고하고 명세 개정 권한을 확인한다.
- `references/design-authority.md`에 target 전용 `ready-for-build` 명세를 제품
  `DESIGN.md` 앞에 삽입한 확장 authority와 일회성 규칙 비승격을 반영한다.
- 기존 render 근거, maker QA, 접근 불가 reference, `DESIGN.md` 갱신 규칙은 유지한다.

산출물:

- `codex-plugins/design-ui/skills/design-ui/SKILL.md`
- `codex-plugins/design-ui/skills/design-ui/references/design-authority.md`

검증 조건:

- [ ] 다섯 UI 명세 상태 각각의 소비 또는 중단 경로가 있다.
- [ ] 정본 §3.6의 네 `UiTarget` canonicalization과 case-sensitive exact `(kind, key)`
      equality, 명세 선택 순서, 세 선택 결과, 복수 후보 `NeedsInput`과 후보 목록이 구현된다.
- [ ] 명시 명세만 target 입력인 경우 그 target을 사용하고, 별도 target과 명세 target이
      다르면 두 target·명세 경로·영향·필요 결정을 담은 응답 전용 `Design conflict`이며
      명세 target 수정·다른 target fallback·구현이 없다.
- [ ] 명시한 미완성 명세에서 다른 ready 명세로 fallback하지 않고 최신 추측을 금지한다.
- [ ] 명세 없음이 blocker가 아니며 구체적인 구현 요청은 바로 진행한다고 명시한다.
- [ ] `AcceptanceCheck`가 구현 범위·자동 검사·maker QA로 연결된다.
- [ ] 사용자 요구와 명세 충돌 시 명세를 몰래 바꾸거나 요구를 무시하지 않는다.
- [ ] 기존 v1 상태 전이, maker Visual QA 행렬, 완료 보고, failure 보고 계약이 유지된다.
- [ ] 아래 두 검사가 통과한다.

```bash
python3 /home/13ruce/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex-plugins/design-ui/skills/design-ui
python3 scripts/validate_skill_links.py
```

커밋 경계: T-002의 두 수정 파일만 원자 커밋 후보로 묶는다.

### T-003 — `review-ui`에 UI 명세·acceptance 판정을 연결한다

내용:

- review도 request와 명세의 `UiTarget`을 정본 §3.6대로 canonicalize하고 exact
  `(kind, key)`가 같은 후보에 한해 명시 경로 → 프로젝트 active 지정 → 단일
  `ready-for-build` 후보 순서로 선택한다. 복수 후보면 `NeedsInput`으로 중단하며 선택된
  ready 명세만 target 전용 기대값으로 읽는다.
- 명시 명세가 target의 유일한 입력이면 그 target을 정규화할 수 있지만, 별도 target과
  canonical 값이 다르면 두 canonical target·명세 경로·영향·필요 결정을 담은 응답 전용
  `Design conflict`로 중단하고 명세 선택·Audit·Repair를 시작하지 않는다. ID·경로·표시
  이름·mtime·날짜·alias 유사성으로 same-target이나 최신 명세를 추측하지 않는다.
- 명시 경로나 active 지정으로 선택된 명세가 `draft`·`needs-input`·`design-conflict`·
  `reference-blocked`이면 정본 §3.6의 no-fallback과 §5.2의 non-ready 처리 계약을 적용한다.
  기본 `HaltForSpec`은 선택 경로·상태·target·필요 입력과
  `resume-spec | request-general-audit` 선택지를 보고하고 target-specific verdict·acceptance
  판정·Repair를 시작하지 않는다.
- 사용자가 선택된 non-ready 명세와 독립적인 일반 Visual Audit을 명시한 경우에만
  `GeneralAudit`을 허용한다. 기존 review authority만 사용하고 non-ready 명세를 expected로
  인용하지 않으며 acceptance result를 만들거나 Repair하지 않는다. 보고서에
  `general-audit` 범위와 명세 기반 판정 제외 이유를 표시한다.
  UI 명세 기반 상태는 `non-ready 명세로 인해 미평가`로 보고하되 이를 `unverified`
  acceptance result로 만들지 않는다.
- 명시·active 지정이 없고 같은 target에 non-ready 명세만 하나 있더라도 자동 선택하거나
  `NoSpec`으로 무시하지 않고 그 후보를 포함한 `NeedsInput`으로 중단한다.
- `codex+render`, `codex+automated-check`, `user+user-decision` 세 유효 조합만 표현하고
  각 조합을 서로 다른 판정 경로로 둔다.
- Codex 소유 check는 `pass | fail | unverified`, 사용자 소유 check는 결정 전
  `awaiting-user-acceptance`, 명시적 승인 뒤 `pass`, 명시적 거절 뒤 `fail`만 허용한다.
  Codex 결과에 `awaiting-user-acceptance`, 사용자 결과에 `unverified`를 기록하지 않는다.
- `UiFinding.expected`가 UI 명세 절 또는 `UI-AC-*` ID를 인용할 수 있게 reference와
  template을 갱신한다.
- 완료 보고에 acceptance check별 `pass | fail | unverified |
  awaiting-user-acceptance`와 open severity 집계를 추가한다.
- 기존 Audit 비파괴성, Repair before 고정·동일 행렬 after, 미규정 디자인 결정 금지,
  렌더 실패 blocked 계약은 유지한다.

산출물:

- `codex-plugins/design-ui/skills/review-ui/SKILL.md`
- `codex-plugins/design-ui/skills/review-ui/references/visual-qa-rubric.md`
- `codex-plugins/design-ui/skills/review-ui/assets/REVIEW-UI.template.md`

검증 조건:

- [ ] 세 acceptance owner/evidence 조합의 처리와 네 결과 상태가 표현되며 무효 조합을
      만들 수 없다.
- [ ] review의 명세 선택도 정본 §3.6의 네 target canonicalization, exact `(kind, key)`,
      선택 순서와 `Selected | NoSpec | NeedsInput`을 따르며 복수 후보를 최신 추측으로
      고르지 않는다.
- [ ] 명시 명세만 target 입력인 경우의 정규화와 별도 target 불일치의 `Design conflict`가
      두 target·명세 경로·영향·필요 결정을 보고하며 명세 target 수정·다른 target fallback·
      Audit·Repair가 없다.
- [ ] 선택된 non-ready 명세는 상태별 중단 payload를 내고 다른 명세로 fallback하지 않으며,
      기본 `HaltForSpec`의 다섯 필드와 두 선택지를 제공한다.
- [ ] `GeneralAudit`은 명시적 사용자 요청에서만 활성화되고 non-ready 명세 expected 인용,
      acceptance result, Repair를 허용하지 않으며 범위와 제외 이유 및 `non-ready 명세로
      인해 미평가`를 보고한다. 이 표시는 `unverified` 결과와 구분된다.
- [ ] 명시·active 지정 없이 단일 non-ready 후보만 있는 경우 후보를 나열한
      `NeedsInput`이며 `NoSpec`으로 처리하지 않는다.
- [ ] `owner: user`의 자동 pass와 Codex의 공개 실행을 금지한다.
- [ ] Codex 결과는 `pass | fail | unverified`, 사용자 결과는
      `awaiting-user-acceptance | pass | fail`로 제한되고, 사용자 승인·거절이 각각
      `pass`·`fail`로 전이한다.
- [ ] 명세가 없을 때 기존 authority·heuristic 분리 규칙으로 동작한다.
- [ ] finding의 expected가 명세 절 또는 acceptance ID를 담을 자리가 template에 있다.
- [ ] 사용자 승인 handoff에 실제 target·viewport·state, 알려진 차이, 미검증 범위,
      open severity 집계와 acceptance 상태가 모두 포함된다. Repair가 있었다면 같은
      viewport·state·data 조건의 before/after 근거도 함께 표시된다.
- [ ] Audit과 Repair의 기존 경계·상태·렌더 근거 계약이 유지된다.
- [ ] 아래 두 검사가 통과한다.

```bash
python3 /home/13ruce/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex-plugins/design-ui/skills/review-ui
python3 scripts/validate_skill_links.py
```

커밋 경계: T-003의 세 수정 파일만 원자 커밋 후보로 묶는다.

### T-004 — 플러그인 설명과 카탈로그 안내를 세 스킬 기준으로 갱신한다

내용:

- plugin README의 포함 스킬·workflow·대표 호출을
  `define-ui → design-ui → review-ui → 사용자 승인` 기준으로 현행화한다.
- plugin manifest의 description·interface.shortDescription·longDescription·defaultPrompt가
  구현 전 정의와 구현, 검토를 모두 표현하도록 갱신하되 name·skills 경로·capability
  budget은 바꾸지 않는다.
  metadata 각각은 `define-ui`를 강제 선행처럼 표현하지 않고 세 스킬의 서로 다른 목표를
  보존하며 U1·U5·U6 routing 평가 대상에 포함한다.
- root README의 Codex-only 행에 세 스킬 이름과 역할을 표시한다.
- marketplace에는 새 항목을 추가하지 않고 기존 `design-ui` 항목 하나와 source를
  검증한다.
- `.claude-plugin/marketplace.json`과 `plugins/**`는 수정하지 않는다.

산출물:

- `codex-plugins/design-ui/README.md`
- `codex-plugins/design-ui/.codex-plugin/plugin.json`
- `README.md`
- `.agents/plugins/marketplace.json`은 내용 변경 없이 검증 대상

검증 조건:

- [ ] 두 JSON이 파싱된다.

```bash
python3 -m json.tool codex-plugins/design-ui/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

- [ ] 아래 명령이 manifest와 marketplace의 단일 설치 단위를 검증한다.

```bash
python3 - <<'PY'
import json
manifest = json.load(open('codex-plugins/design-ui/.codex-plugin/plugin.json'))
assert manifest['name'] == 'design-ui'
assert manifest['skills'] == './skills/'
assert manifest['interface']['capabilities'] == []
market = json.load(open('.agents/plugins/marketplace.json'))
items = [p for p in market['plugins'] if p['name'] == 'design-ui']
assert len(items) == 1, items
assert items[0]['source'] == {
    'source': 'local', 'path': './codex-plugins/design-ui'
}
PY
```

- [ ] plugin README·manifest의 description·interface.shortDescription·longDescription·
      defaultPrompt와 root README에 `define-ui`, `design-ui`, `review-ui`가 모두 나타나고
      각 역할이 구분되며,
      `define-ui`를 모든 구현의 강제 선행 단계처럼 표현하지 않는다.
- [ ] root README의 해당 행은 Claude Code `–`, Codex CLI `✅`를 유지한다.
- [ ] `agents/openai.yaml`, scripts, MCP/app 의존성이 추가되지 않는다.

커밋 경계: T-004의 세 실제 수정 파일만 원자 커밋 후보로 묶는다. marketplace가
불변이면 커밋에 포함하지 않는다.

### T-005 — 구조·계약·보호 트리를 정적으로 검사한다

내용:

- 정본 §3.3과 실제 plugin 파일 집합을 정확히 비교한다.
- 세 `SKILL.md`의 frontmatter key가 `name`, `description`뿐이며 디렉터리 이름과
  일치하는지 확인한다.
- request·명세·세 consumer에 공통인 `UiTarget` 네 변형, kind별 canonical key,
  case-sensitive exact `(kind, key)` equality와 금지된 휴리스틱을 정본 §3.6에 1:1
  대조한다. 별도 target 불일치는 `define-ui`의 preflight `TargetConflict`와
  `design-ui`·`review-ui`의 응답 전용 `Design conflict`로 분리됐는지도 확인한다.
- `UiSpecCommon.target`·`intent`, 다섯 lifecycle tagged union, 네 `FailureContext`,
  `KnownAffectedScope | UnknownTargetScope`, runtime-only `DefineUiPhase`와
  phase→persistent status·resume mapping을 정본 §4.1·§4.2·§4.4에 1:1 대조한다.
- 정본 §8.3의 11개 행동 불변 조건을 구현 파일과 1:1 대조해 실행 리포트에 표로 남긴다.
- 폐기·배제한 스킬 디렉터리, MCP/app/scripts/agent dependency가 없는지 확인한다.
- 실행 착수 시 저장한 `.claude-plugin/`·`plugins/` snapshot과 현재 tree의 경로·type·
  mode·symlink target·일반 파일 SHA-256을 비교한다.
- 신규·수정 작업 파일의 trailing whitespace와 탭 들여쓰기를 검사한다.

산출물:

- `plans/20260905-codex-ui-workflow-skills-execute-report.md`의 정적 검사 절

검증 조건:

- [ ] 아래 파일 집합 검사가 통과한다.

```bash
python3 - <<'PY'
from pathlib import Path
root = Path('codex-plugins/design-ui')
expected = {
    '.codex-plugin/plugin.json',
    'README.md',
    'LICENSE',
    'skills/define-ui/SKILL.md',
    'skills/define-ui/references/ui-definition-contract.md',
    'skills/define-ui/assets/UI-SPEC.template.md',
    'skills/design-ui/SKILL.md',
    'skills/design-ui/references/design-authority.md',
    'skills/design-ui/assets/DESIGN.template.md',
    'skills/review-ui/SKILL.md',
    'skills/review-ui/references/visual-qa-rubric.md',
    'skills/review-ui/assets/REVIEW-UI.template.md',
}
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
assert actual == expected, {'missing': expected-actual, 'extra': actual-expected}
PY
```

- [ ] 아래 frontmatter 검사가 통과한다.

```bash
python3 - <<'PY'
from pathlib import Path
for expected in ('define-ui', 'design-ui', 'review-ui'):
    p = Path('codex-plugins/design-ui/skills') / expected / 'SKILL.md'
    text = p.read_text()
    front = text.split('---', 2)[1]
    keys = [line.split(':', 1)[0] for line in front.splitlines() if line and not line[0].isspace()]
    assert keys == ['name', 'description'], (p, keys)
    assert f'name: {expected}' in front, p
PY
```

- [ ] `python3 scripts/validate_skill_links.py`가 통과한다.
- [ ] 아래 plugin validator와 세 skill quick validator가 모두 통과한다.

```bash
python3 /home/13ruce/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  codex-plugins/design-ui
for skill_dir in codex-plugins/design-ui/skills/*; do
  python3 /home/13ruce/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
    "$skill_dir"
done
```
- [ ] `find codex-plugins/design-ui -type d`에 `accept-ui`·`test-ui`·`deploy-ui`·
      `prototype-ui`·`scripts`·`agents`가 없다.
- [ ] protected Claude tree가 착수 snapshot과 일치한다.
- [ ] `UiTarget` 네 변형의 canonicalization, exact equality, 명시 명세 target 정규화와
      별도 target 불일치의 skill별 응답 전용 결과·비변경 계약이 정본 §3.6과 일치한다.
- [ ] `UiSpec.intent`, lifecycle별 status·unresolved·failure 조합, 네 failure resume 조합,
      세 known-only failure와 reference-blocked의 known/unknown affected scope,
      정상 phase의 `draft` 유지와 interrupted draft의 `Intake` 재시작이 정본 §4.2·§4.4와
      일치한다.
- [ ] 정본 §8.3의 11개 행 모두 `적합/부적합`으로 판정되고 `미대조`가 없다.

### T-006 — U1~U12·U11-T 활성화·handoff 행동을 평가한다

내용:

- `mktemp -d`로 저장소 밖 `<ui_workflow_eval_root>`를 만들고 그 아래에 격리 marketplace,
  격리 Codex config/install root, case별 최소 UI fixture와 evidence 디렉터리를 둔다.
- 평가 대상 플러그인은 설치된 과거 cache가 아니라 **현재 worktree의 수정 내용**으로
  고정한다. `git clone`·`git archive` 대신 `.agents/plugins/marketplace.json`과
  `codex-plugins/design-ui/`를 격리 marketplace에 `cp -a`로 복사하고, 원본과 복사본의
  파일 목록·SHA-256을 기록한다.
- local cachebuster는 격리 복사본의 manifest에만 적용한다. 원본 manifest의 전후
  SHA-256이 같아야 하며, marketplace name은 helper로 읽는다.
- 격리 Codex root를 `CODEX_HOME`으로 지정해 임시 marketplace를 등록하고
  `design-ui@<marketplace-name>`을 설치한다. `codex plugin list --json`과 격리 root의
  설치 실물을 대조해 `define-ui`·`design-ui`·`review-ui`가 정확히 하나씩 존재하는지,
  설치된 각 `SKILL.md`가 격리 복사본과 같은 SHA-256인지 확인한다. cachebuster 때문에
  달라지는 manifest는 별도로 기록한다.
- 전역 `config.toml`은 복사하지 않는다. inner Codex 인증은 환경에 이미 있는 API key를
  우선하고, 없으면 현재 `auth.json`만 격리 root로 권한 `0600` 복사한다. credential
  내용·hash는 evidence에 넣거나 출력하지 않는다.
- 각 재개 가능한 subrun은 activation과 담당 runtime case를 하나의 shell wrapper 안에서
  실행하고 `EXIT`·`INT`·`TERM`·`HUP` trap을 가장 먼저 등록한다. 성공·실패·중단 어느
  경로에서도 정확한 격리
  `auth.json` 복사본을 즉시 삭제한다. 설치된 12-file snapshot·경로·hash·plugin list 등
  비민감 근거는 먼저 evidence로 복사하고, 격리 config/install root 자체는 해당 subrun
  종료 시 폐기한다.
- 위 활성화 gate를 통과하지 못하면 U1~U12·U11-T를 시작하지 않고 T-006을 실패로 닫는다.
  모든 `codex exec --json`은 같은 격리 `CODEX_HOME`을 명시한다. under-test plugin은
  기록한 CLI schema가 실제 제공하는 설치 경로(`plugin add`의 `installedPath` 또는
  `plugin list`의 `installed[].source.path`)를 realpath로 해석하고, 격리 root에 설치된
  유일한 plugin/skill inventory와 12-file hash chain에 교차해 귀속한다. 특정 field 이름을
  고정 전제로 삼지 않는다.
- 첫 activation 뒤 저비용 probe 한 건으로 `codex --version`과 JSONL event type·field 경로를
  기록한다. event가 실제 선택 skill 이름이나 읽은 `SKILL.md` 경로를 노출하면 직접 근거로
  사용한다. 노출하지 않으면 설치본 단일성·hash chain과 각 스킬 고유 output/비변경 계약
  assertion을 합친 대체 귀속 근거를 사용한다. 어떤 경로로도 귀속하지 못한 case만
  `미검증`으로 중단하며, CLI가 보장하지 않은 field 부재 자체로 전체 평가를 중단하지 않는다.
- inner Codex는 case directory를 `-C`로 고정하고 `--sandbox workspace-write`·`--ephemeral`·
  `--ignore-rules`로 실행한다. 전역 config는 복사하지 않되 임시 marketplace/plugin CLI가
  격리 root에 생성한 최소 `config.toml`은 읽어 방금 설치한 플러그인을 활성화한다.
  `--add-dir`는 사용하지 않으며 격리 `codex mcp list --json`이 빈 목록인지 확인해 사용자
  MCP·connector를 상속하지 않는다.
- 각 사례는 같은 pristine fixture에서 `cp -a`한 별도 case working tree에서 실행해 앞
  사례의 변경이 뒤 사례에 영향을 주지 않게 한다.
- `codex exec --json` 실행 전후에 제품 UI 소스·테스트·빌드 파일의 SHA-256을 저장한다.
- U1~U4에서 `define-ui`가 제품 소스를 변경하지 않는지, U4는 세 분기 fixture로 나눠
  차단·계속·승인 fallback을 각각 확인하고, U5·U6에서 비트리거인지,
  U7~U12와 U11-T에서 명세 상태·acceptance handoff·명세 선택을 실제 tool event와 최종 응답으로
  판정한다. U11·U12는 세 consumer의 선택 행렬과 non-ready 상태를 하위 case로 실행한다.
- U1 하위 case에서 route·component·screen-set·new-app 네 target을 모두 생성한다. route의
  query/hash·non-root trailing slash 제거와 dynamic segment 보존, global/owned component의
  semantic owner+slug, 두 stable slug를 명세에 저장된 canonical target과 `intent`로
  확인한다. module/export path는 component identity로 쓰지 않는다.
- U11-T target equality matrix는 case-sensitive exact `(kind, key)`만 같은 target으로 인정하고,
  명세 ID·파일 경로·표시 이름·mtime·날짜·alias가 닮거나 같아도 다른 canonical pair를
  후보에 포함하지 않는 사례를 세 consumer에서 실행한다. 명시 명세가 유일한 target 입력인
  사례는 그 target을 사용한다. 별도 target과 명세 target이 다르면 `define-ui`는 preflight
  `TargetConflict`, `design-ui`·`review-ui`는 응답 전용 `Design conflict`로 끝나며 명세·제품·
  Audit·Repair 보호 대상을 변경하지 않는지 확인한다.
- U3 하위 case는 `target.kind`, `target.key`, user-visible goal의 각 누락을 실행해 모두
  preflight `NeedsClarification`이고 명세 미생성인지 확인한다.
- 제품의 대상 사용자나 핵심 가치가 갈리는 별도 routing case는 preflight
  `NeedsClarification`으로 처리하지 않고 곧바로 `interview`로 넘기며, 명세·제품 보호
  대상을 변경하지 않는지
  확인한다.
- 정본 §6의 경계를 위해 연속 `define-ui → design-ui`, 시스템 경계 요청의 `make-design`,
  구현 없는 이미지 시안의 이미지 도구, 명시적 `review-ui` Repair, 출시 요청의 프로젝트
  배포 절차를 각각 독립 routing case로 실행한다. UI 스킬이 다른 성공 산출물이나 공개
  권한을 가로채지 않아야 한다.
- 격리 환경에는 under-test plugin만 설치하므로 `interview`·`make-design`·이미지 도구·배포
  절차 자체의 실제 실행을 양성 근거로 요구하지 않는다. 이 외부 담당 사례는 세 UI 스킬의
  비활성·보호 대상 비변경·정확한 담당 이름과 handoff 이유가 있는 최종 응답으로 판정한다.
  연속 define+implement와 `review-ui` Repair처럼 plugin 내부 담당은 실제 skill 귀속과 고유
  산출물·변경 집합으로 양성 판정한다.
- lifecycle matrix는 정상 `Intake`~`DecisionCheck`에서 저장 status가 `draft`인지,
  `NeedsInputFailure`·`ReferenceBlockedFailure`·두 `DesignConflict` 변형이 exact status·
  `last_completed_phase`·`resume_at` 조합으로 원자 저장되는지, `ReadyForBuild`와 `Done`이
  `ready-for-build`을 유지하는지 실행한다. 각 실패는 재개 조건 확인 전에는 재개하지 않고,
  확인 뒤 failure 제거·`draft` 복귀·`resume_at` 재개를 보인다. 정상 phase 도중 중단된
  draft는 다음 실행에서 `Intake`로 돌아가며 filename·mtime·partial content로 phase를
  복원하지 않는 사례를 포함한다.
- browser capability는 실행 파일 하나만 보지 않고 fixture script, 로컬 dependency, 현재
  도구, 오프라인 package runner까지 비파괴적으로 확인한다.
- 브라우저나 인증·비용 제약으로 실행하지 못한 사례는 성공으로 세지 않는다. `미검증`
  이유, 원본 stderr, exit code와 복붙 가능한 재현 명령을 남긴다.
- U6 Audit과 U9 Audit의 실행 전후에는 검토 대상 UI 소스·테스트·빌드 설정·명세의
  SHA-256을 각각 비교해 비변경을 증명한다.
- T-006은 `A 활성화`, `B U1~U6·§6 라우팅·target·lifecycle`,
  `C U7·U8·U11-D/I·U12-D/I design handoff`,
  `D U9·U10·U11-R·U12-R review/acceptance`의 네 재개 가능한 subrun으로
  checkpoint한다. 실행 전 case manifest에 모든 subcase의 ID·fixture·prompt·기대 변경
  파일 집합·assertion·예상 호출 수를 고정한다. primary inner Codex 호출은 64회 이하,
  원인이 바뀐 실패에 한한 재시도까지 총 96회 이하로 제한한다. 한도를 넘기면 성공으로
  축소하지 않고 T-006을 중단한다.
- 각 subrun은 같은 source inventory hash와 cachebuster 입력으로 격리 설치를 재생성하고
  activation hash gate를 다시 통과한 뒤 시작한다. 재개 시 완료 case는 immutable evidence
  manifest hash가 일치할 때만 재사용하고, 마지막 완료 checkpoint 다음의 미실행 case부터
  진행한다. source hash가 달라지면 이전 runtime evidence를 재사용하지 않는다.
- evidence는 T-007이 끝날 때까지 보존하고, 정확한 temp 경로·baseline HEAD·Codex CLI
  version과 event schema·case manifest·평가 대상 source/복사본/설치본 hash·plugin list
  JSON·각 명령 argv와 prompt 원문·stdout/stderr·exit code·fixture source hash를 manifest로
  고정한다.

평가 대상 고정 절차:

```bash
umask 077
ui_workflow_eval_root=$(mktemp -d)
ui_eval_market_root="$ui_workflow_eval_root/marketplace"
ui_eval_codex_root="$ui_workflow_eval_root/codex-config"
cleanup_ui_eval_secrets() {
  test -n "$ui_workflow_eval_root" || return 1
  case "$ui_workflow_eval_root" in /tmp/*) ;; *) return 1 ;; esac
  test "$ui_eval_codex_root" = "$ui_workflow_eval_root/codex-config" || return 1
  if test -f "$ui_eval_codex_root/auth.json"; then
    test ! -L "$ui_eval_codex_root/auth.json" || return 1
    unlink -- "$ui_eval_codex_root/auth.json"
  fi
  if test -d "$ui_eval_codex_root"; then
    test ! -L "$ui_eval_codex_root" || return 1
    gio trash "$ui_eval_codex_root"
  fi
}
trap cleanup_ui_eval_secrets EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
mkdir -p "$ui_eval_market_root/.agents/plugins" \
  "$ui_eval_market_root/codex-plugins" "$ui_eval_codex_root" \
  "$ui_workflow_eval_root/evidence"
if test -z "${OPENAI_API_KEY:-}"; then
  test -f /home/13ruce/.codex/auth.json || exit 1
  install -m 600 /home/13ruce/.codex/auth.json "$ui_eval_codex_root/auth.json"
fi
cp -a .agents/plugins/marketplace.json \
  "$ui_eval_market_root/.agents/plugins/marketplace.json"
cp -a codex-plugins/design-ui "$ui_eval_market_root/codex-plugins/design-ui"
ui_market_name=$(python3 \
  /home/13ruce/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py \
  --marketplace-path "$ui_eval_market_root/.agents/plugins/marketplace.json")
python3 /home/13ruce/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  "$ui_eval_market_root/codex-plugins/design-ui"
CODEX_HOME="$ui_eval_codex_root" codex plugin marketplace add \
  "$ui_eval_market_root" --json
CODEX_HOME="$ui_eval_codex_root" codex plugin add \
  "design-ui@$ui_market_name" --json
CODEX_HOME="$ui_eval_codex_root" codex plugin list --json
CODEX_HOME="$ui_eval_codex_root" codex mcp list --json
```

설치 위치는 CLI JSON과 격리 root 실물에서 해석하며 전역 cache 경로를 가정하지 않는다.
각 runtime 명령은 다음 고정 형태를 사용한다.

```bash
CODEX_HOME="$ui_eval_codex_root" codex exec --json --ephemeral \
  --ignore-rules --skip-git-repo-check --sandbox workspace-write \
  -C "$ui_case_root" "$ui_case_prompt"
```

각 case 직전 `realpath "$ui_case_root"`가 `<ui_workflow_eval_root>/cases/` 아래인지,
현재 저장소 root와 다른지, pristine fixture hash가 일치하는지 gate로 확인한다. 실행 전
`codex exec --help`에 `--skip-git-repo-check`가 있는지도 기록하고, 없다면 비-Git fixture에서
평가를 시작하지 않고 T-006을 중단한다.

산출물:

- `plans/20260905-codex-ui-workflow-skills-execute-report.md`의 U1~U12·U11-T 평가 표
- 실행 중 생성한 `<ui_workflow_eval_root>/evidence/`

검증 조건:

- [ ] U1은 `define-ui`를 선택하고 UI 소스 불변 상태로 canonical `target`과 `intent`가 있는
      UI 명세를 생성한다.
- [ ] U1 생성 artifact에 `UiSpecCommon`의 모든 필드, screen의 purpose·hierarchy·states·
      interactions·accessibility, flow와 screen/state 연결, acceptance common 필드와 유효
      owner/evidence 조합이 실제로 존재한다.
- [ ] U1의 target matrix는 route·component·screen-set·new-app canonicalization을 모두
      통과한다. route는 query/hash·non-root trailing slash만 제거하고 dynamic syntax를
      유지하며 component는 module/export path가 아닌 global 또는 target owner+slug를 쓴다.
- [ ] U1 component owner matrix는 `global:project`와 route·screen-set·new-app owner를 각각
      canonicalize하고, component owner와 미허용 owner kind는 `Ready`나 명세 생성 없이
      거부한다.
- [ ] U2는 responsive rules를 포함한다.
- [ ] U3의 `target.kind`·`target.key`·goal 누락은 각각 preflight `NeedsClarification`으로
      끝나며 UI 명세 파일·ID·status와 제품 소스를
      만들거나 변경하지 않는다. 응답에는 known context·non-empty missing 목록·material
      effect·집중 질문 하나·resume condition이 있고, 답변 후 preflight를 다시 평가한다.
- [ ] 제품의 무엇·왜가 갈리는 case는 명세·제품 변경 없이 `interview`로 넘어가며 입력
      누락의 `NeedsClarification`과 혼동되지 않는다.
- [ ] 정본 §6의 연속 define+implement, 시스템 설계, 이미지 시안, Repair, 출시 routing
      case가 각각 지정된 담당으로 간다. plugin 내부 담당은 실제 skill 귀속·산출물로,
      외부 담당은 세 UI 스킬 비활성·비변경과 정확한 handoff 문구로 판정하며 설치되지 않은
      외부 capability의 실제 실행을 요구하지 않는다.
- [ ] U4-a는 reference 번역이 작업의 주목적이라 `reference-blocked`이며 접근 불가 Figma
      내용을 꾸며내지 않는다.
- [ ] U4-b는 부차 reference가 없어도 나머지 근거로 계속하고 과도하게 중단하지 않는다.
- [ ] U4-c는 사용자가 승인한 reference 독립 fallback 범위만 사용한다.
- [ ] U5는 `design-ui`, U6는 `review-ui` Audit을 선택하며 `define-ui`를 잘못 활성화하지
      않는다.
- [ ] U6 Audit 전후의 UI 소스·테스트·빌드 설정·UI 명세 hash가 모두 같다.
- [ ] U7은 `ready-for-build` 명세의 화면·상태·acceptance checks를 구현과 maker QA에
      연결하고 responsive rules를 실제 구현 범위에 반영한다.
- [ ] U8은 미결 영향 범위를 구현하지 않고 필요한 결정을 보고한다.
- [ ] U9의 finding expected가 명세 절 또는 `UI-AC-*`를 인용한다.
- [ ] U9 Audit 전후의 UI 소스·테스트·빌드 설정·UI 명세 hash가 모두 같다.
- [ ] U10-a는 결정 전 사용자 소유 check를 `awaiting-user-acceptance`로 남기며, 명시적
      사용자 승인 뒤 `pass`, 명시적 사용자 거절 뒤 `fail`로 각각 전이한다.
- [ ] U10-a의 승인·거절은 같은 `UI-AC-*`와 `awaiting-user-acceptance` review artifact
      snapshot에서 각각 분기한다. 후속 ephemeral 호출에 이전 artifact 경로와 사용자 결정을
      명시해 세 독립 결과 생성이 아니라 동일 check의 상태 전이임을 증명한다.
- [ ] U10-b는 Codex 결과에 `awaiting-user-acceptance`, 사용자 결과에 `unverified`를
      허용하지 않는다.
- [ ] U10의 무효 owner/evidence 조합은 기본값으로 보정되지 않고 명세 계약 오류가 된다.
- [ ] target equality matrix에서 case-sensitive exact `(kind, key)`만 같은 target이며 명세
      ID·경로·표시 이름·mtime·날짜·alias 유사성은 후보 선택에 영향을 주지 않는다.
- [ ] 명시 명세만 target 입력인 case는 명세의 canonical target을 사용하고, 별도 target과
      불일치하는 U11-T case는 `define-ui`의 preflight `TargetConflict`와
      `design-ui`·`review-ui`의 응답 전용 `Design conflict`이며 명세 target 수정·다른 target
      fallback·제품·Audit·Repair 변경이 없다. 세 응답 모두 두 canonical target·명세 경로·
      material effect·resolution needed를 포함하고 define-ui 결과에는 resume condition도 있다.
- [ ] lifecycle matrix에서 정상 `Intake`~`DecisionCheck`는 `draft`, 네 failure 변형은
      정본의 exact status·`last_completed_phase`·`resume_at`, `ReadyForBuild`·`Done`은
      `ready-for-build`로 저장된다. failure/status/unresolved 전이는 원자적이다.
- [ ] 실패 재개는 조건 확인 뒤 failure 제거·`draft` 복귀·`resume_at` 시작 순서이며,
      interrupted draft는 filename·mtime·partial content와 무관하게 `Intake`에서 재시작한다.
- [ ] U11-D(`define-ui` revise/reuse), U11-I(`design-ui`), U11-R(`review-ui`) 각각에서
      명시 경로 → active 지정 → 단일 ready 후보의 우선순위를 실행하고 선택된 정확한
      경로를 확인한다.
- [ ] U11-D revise는 선택된 기존 명세를 in-place 갱신하고 새 spec 파일을 추가하지 않는다.
      기존 active 지정은 사용자 요구나 프로젝트 계약 없이 자동 변경하지 않는다.
- [ ] U11-D/I/R 각각에서 명시 경로가 non-ready이면 다른 ready 명세로 fallback하지 않는다.
      `define-ui`는 상태별 재개 입력을, `design-ui`는 구현 중단을 보고한다. `review-ui`의
      기본 결과는 다섯 필드와 두 선택지를 가진 `HaltForSpec`이고 target-specific verdict·
      acceptance 판정·Repair와 보호 대상 변경이 없다.
- [ ] U11-D와 U11-I도 명시 또는 active로 선택된 `draft | needs-input | design-conflict |
      reference-blocked` 각 상태의 재개 입력·구현 중단 경로를 모두 실행한다.
- [ ] U11-R은 명시 또는 active로 선택된 `draft | needs-input | design-conflict |
      reference-blocked` 각 상태의 중단 경로를 모두 실행한다.
- [ ] U11-R `GeneralAudit`은 선택된 non-ready 명세와 독립적인 일반 Audit을 명시한 별도
      case에서만 실행한다. 기존 authority만 사용하고 non-ready 명세 expected 인용·
      acceptance result·Repair 없이 `general-audit` 범위, 제외 이유와 `non-ready 명세로
      인해 미평가`를 보고하며 `unverified` 결과를 만들지 않는다.
- [ ] U12-D/I/R 각각에서 active 지정 없이 ready 후보가 둘 이상이면 후보 경로를 나열한
      `NeedsInput`으로 끝나고 보호 대상을 변경하지 않는다.
- [ ] U12-D/I/R 각각에서 명시·active 지정 없이 non-ready 후보만 하나 있으면 이를
      `NoSpec`으로 무시하지 않고 후보를 나열한 `NeedsInput`으로 끝난다.
- [ ] U4-a는 UI 명세와 최종 응답 양쪽에 원인·마지막 완료 지점·필요 입력·
      `UnknownTargetScope { target, reason }`·재개 조건을 항상 가지며 화면 이름을 추측하지
      않는다. 화면 이름을 정본으로 아는 reference-blocked case는 `KnownAffectedScope`를 쓴다.
- [ ] `NeedsInputFailure`와 두 `DesignConflict` 변형은 `KnownAffectedScope`만 허용하고
      `UnknownTargetScope`를 만들지 않는다.
- [ ] U1~U4·U6·U8·U9·U11 non-ready·U11-T·U12의 보호 대상 source hash 검사가 통과한다.
- [ ] source plugin 원본 manifest는 cachebuster 설치 전후 동일하다. 정본의 정확한 12-file
      inventory 전체가 source→격리 복사본→설치본에서 일치하고, cachebuster manifest만
      허용된 내용 차이로 따로 기록된다.
- [ ] `codex plugin list --json`, 설치 경로, 세 skill의 단일성, under-test path/hash가
      activation gate에 보존되며 모든 runtime case가 같은 격리 `CODEX_HOME`을 사용한다.
- [ ] 격리 설치를 위해 전역 Codex marketplace·plugin 설정을 변경하지 않았고 credential
      내용·hash가 evidence나 명령 출력에 포함되지 않는다.
- [ ] 정상 종료와 activation/runtime 강제 실패 fixture 모두에서 trap 이후 격리
      config/install root 전체가 없고, 전역 config를 복사하지 않았으며, MCP 목록이 비어 있다.
- [ ] 각 case의 realpath가 격리 `cases/` 아래이고 실제 저장소 root와 다르며, 시작 fixture
      hash가 pristine baseline과 일치한다.
- [ ] 비-Git 격리 case에서도 현재 CLI가 제공하는 `--skip-git-repo-check`를 사용해 repo
      gate에서 실패하지 않는다.
- [ ] case manifest의 모든 subcase에 fixture·prompt·기대 mutation set·assertion·예상 호출
      수가 있고, 네 subrun checkpoint와 실제 호출 수가 기록되며 primary 64회·총 96회
      상한을 넘지 않는다.
- [ ] 모든 case에 exact argv·prompt, stdout, stderr, exit code, baseline, fixture source hash,
      설치본 귀속 근거가 존재한다.
- [ ] Codex CLI version과 실제 JSONL event type·field 경로가 기록되고, 각 case의 직접 또는
      대체 skill 귀속 방식이 명시된다.
- [ ] 렌더하지 못한 사례를 Visual QA green이나 acceptance pass로 기록하지 않는다.

평가 evidence는 T-007 독립 검증이 소비할 때까지 정리하지 않는다. 실제 정리는 T-008의
기록 종결 후처리에서만 수행한다.

### T-007 — 독립 재검증과 통합 게이트를 통과한다

내용:

- 읽기 전용 독립 검증자에게 다음 경로만 전달한다.
  - `docs/codex-ui-workflow-skills.md`
  - `docs/codex-ui-design-skills.md`
  - `codex-plugins/design-ui/`
  - `.agents/plugins/marketplace.json`
  - `README.md`
  - `plans/20260905-codex-ui-workflow-skills-execute-report.md`
  - 실행 리포트에 기록된 baseline HEAD와 protected-tree snapshot 경로
  - 실행 리포트에 기록된 정확한 `<ui_workflow_eval_root>/evidence/` 경로
- 검증자는 정본 §2~§9에서 기대값을 직접 추출해 구현·문서·U1~U12·U11-T 원본 근거를
  대조한다.
- 검증자는 runtime evidence가 현재 worktree에서 복사·설치된 플러그인의 exact path/hash를
  가리키는지 먼저 확인하며, activation gate가 불충분하면 U1~U12·U11-T 결과를 인정하지
  않는다.
- 발견은 `blocker/major/moderate/minor`, 정본 절, 파일·근거와 함께 반환한다.
- 등급과 무관하게 계약 위반은 수행자가 수정하고 T-005와 영향받은 T-006 사례를 다시
  실행한 뒤 같은 검증자가 재판정한다.
- 설계가 틀렸거나 미규정인 발견은 구현으로 해결하지 않고 `$make-design` 대상으로
  승격한다.
- 최종 판정 후 프로젝트 표준 링크 게이트와 구조·JSON·diff 검사를 통합 실행한다.

산출물:

- 실행 리포트의 독립 검증 절과 최종 통합 게이트 출력
- 검증자 발견 → 수행자 수정 → 동일 검증자 재판정의 기록과 필요 시 수정된 산출물

검증 조건:

- [ ] 독립 검증의 계약 위반이 blocker·major·moderate·minor 모두 0건이다.
- [ ] 정본 §8.2 U1~U12·U11-T의 모든 하위 case와 §8.3의 11개 불변 조건에 `미대조`·`미검증`이
      없다. 환경상 실행 불가는 근거 있는 `미검증`으로 기록하되 gate 실패이며 green이나
      완료로 합치지 않는다.
- [ ] `python3 scripts/validate_skill_links.py`가 통과한다.
- [ ] plugin validator와 세 skill quick validator가 모두 통과한다.
- [ ] 두 JSON 파싱과 marketplace 단일 항목 검사가 통과한다.
- [ ] 정확한 12-file set, protected Claude tree, 작업 파일 whitespace,
      `git diff --check`가 통과한다.
- [ ] evidence manifest의 모든 파일 hash가 일치한다.
- [ ] activation gate의 source→격리 복사본→설치본 hash chain과 모든 case의 격리
      `CODEX_HOME` 사용이 확인된다.

### T-008 — 실행 기록을 닫고 원자 커밋을 준비한다

내용:

- 성공 경로와 T-001~T-007 어느 단계의 중단 경로에서도 반드시 실행하는 always-run
  closeout이다. 중단 뒤에는 미실행 후속 작업을 `중단(선행 실패)`로 닫고 커밋은 만들지
  않더라도 evidence 보존과 민감 temp/snapshot 정리를 수행한다.
- 실행 리포트에 기록된 exact temp/snapshot 경로만 정리한다. 해당 root가 만들어지기 전에
  중단됐다면 미생성을 기록하고 unset 값을 cleanup target으로 사용하지 않는다.
- 실행 리포트에 T-001~T-008 결과, 검사 명령·출력, 독립 판정, 미검증 범위를 기록한다.
- 이 플랜의 상태를 실제 실행 종료일을 사용한 `완료 (YYYY-MM-DD)` 또는 정확한
  `중단 (YYYY-MM-DD, T-00x까지 / 사유)`로 닫는다.
- `완료`는 T-006의 모든 필수 하위 case가 실행·판정되고 T-007의 `미대조`·`미검증`이
  0건일 때만 허용한다. 환경·인증·비용·호출 상한으로 한 case라도 남으면 근거와 재현
  명령을 기록하고 `중단`으로 닫는다.
- 설계 문서와 플랜, 실행 리포트도 이번 확장의 추적 대상에 포함한다.
- 작업 경계별 정확한 파일만 stage하고 `git diff --cached --check`를 실행한다. 이미 만든
  커밋은 `git show --check --oneline <commit>`으로 다시 확인한다.
- 사용자 소유의 무관한 변경을 stage하거나 고치지 않는다.
- push는 사용자 확인 없이 실행하지 않는다.
- 독립 검증 결과와 비민감 evidence hash를 실행 리포트에 옮긴 뒤에만 평가 temp를 정리한다.
  격리 Codex root의 credential은 리포트·evidence에 복사하지 않는다. 실행을 위해 만든
  정확한 `auth.json` 복사본은 경로·권한을 확인해 먼저 삭제하고, 나머지 temp는 복구 가능한
  trash로 정리한다.

```bash
test -n "$ui_workflow_eval_root"
case "$ui_workflow_eval_root" in /tmp/*) ;; *) exit 1 ;; esac
test -d "$ui_workflow_eval_root/evidence"
test "$ui_eval_codex_root" = "$ui_workflow_eval_root/codex-config"
test ! -e "$ui_eval_codex_root"
gio trash "$ui_workflow_eval_root"
```

착수 snapshot은 실행 리포트에 경로·hash를 옮긴 뒤 수행자가 정확한 snapshot root를 같은
경로 검증과 `gio trash` 절차로 정리한다. 중단 시에도 credential은 T-006 trap에서 즉시
삭제하고, 비민감 evidence와 snapshot의 보존·정리 여부를 실행 리포트에 명시한다.

산출물:

- `plans/20260905-codex-ui-workflow-skills-execute-report.md`
- T-001~T-004와 기록을 구분한 원자 커밋 또는 커밋 직전 staging 제안

검증 조건:

- [ ] `git status --short`의 모든 변경이 정본 또는 이 플랜 산출물로 설명된다.
- [ ] 실행 리포트의 T-001~T-008이 모두 `완료/중단` 중 하나로 닫힌다.
- [ ] T-001~T-007 어느 단계에서 중단해도 T-008이 실행되고, 미실행 후속 작업과 temp/
      snapshot의 보존·정리 상태가 기록된다.
- [ ] 최종 통합 게이트 출력과 독립 검증 판정이 실행 리포트에 보존된다.
- [ ] staged diff 또는 각 원자 커밋의 whitespace 검사가 통과한다.
- [ ] push가 수행되지 않는다.

## 5. 의존성 그래프

```text
T-001 define-ui 계약·템플릿
  ├── T-002 design-ui handoff ─────┐
  ├── T-003 review-ui handoff ─────┤
  └── T-004 설명·카탈로그 안내 ───┤
                                    ▼
                            T-005 정적 계약 검사
                                    ▼
                            T-006 U1~U12·U11-T 평가
                                    ▼
                            T-007 독립 검증·통합 게이트
                                    ▼
                            T-008 기록·커밋 준비

T-001~T-007 어느 단계든 중단 ──────▶ T-008 중단 기록·민감 temp/snapshot 정리
```

- 병렬 가능: T-002와 T-003. 두 작업이 서로 다른 skill tree를 수정한다.
- 조건부 병렬 가능: T-004 문안은 T-001 뒤 작성할 수 있으나 세 스킬의 최종 표현은
  T-002·T-003 결과와 대조한다.
- 임계 경로: T-001 → max(T-002, T-003, T-004) → T-005 → T-006 → T-007 → T-008
- 실패 경로: T-001~T-007 어느 단계에서든 다음 작업을 건너뛰고 T-008 closeout을 반드시
  실행한다. 중단은 기록·민감정보 정리 의존성을 끊지 않는다.

## 6. 검증 실행 계획

### 6.1 수행자 1차 검증

각 구현 작업 직후 해당 quick validator와 링크 검사를 실행한다. T-005에서 파일 구조와
불변 조건을 정적으로 모두 대조하고, T-006에서 정적 문구가 아니라 실제 Codex 활성화와
handoff를 원본 event·응답·source hash로 판정한다. 실패한 검사는 해당 작업으로 되돌린다.

### 6.2 검증자 독립 재검증

T-007 검증자는 정본 설계에서 기대값을 새로 추출한다. 수행자의 체크리스트나 실행 리포트
요약만으로 green을 내리지 않고 구현 파일과 U1~U12·U11-T 원본 evidence를 직접 확인한다.
검증자는 제품 소스나 플러그인을 수정하지 않는다.

### 6.3 통합 게이트

프로젝트 표준 통합 게이트는 다음 명령이다.

```bash
python3 scripts/validate_skill_links.py
```

이 게이트에 포함되지 않는 정확한 파일 집합, JSON, skill/plugin validator, protected tree,
evidence hash, whitespace와 diff 검사는 T-007의 명시적 계약 검사로 한 번 묶어 실행한다.

## 7. 롤백 플랜

### 착수 전 스냅샷

1. `git status --short --branch`와 `git rev-parse HEAD`를 실행 리포트에 기록한다.
2. 현재 미추적 상태인 `docs/codex-ui-workflow-skills.md`와 이 플랜은 사용자 승인으로
   생성된 in-scope 문서이므로 삭제·복원 대상으로 취급하지 않고 SHA-256을 기록한다.
3. `ui_workflow_snapshot_root=$(mktemp -d)`로 snapshot directory를 만들고
   `.claude-plugin/`·`plugins/`의
   경로·type·mode·symlink target·일반 파일 SHA-256을 보존한다.
4. 기존 수정 대상 여덟 파일의 SHA-256과 현재 내용을 snapshot directory에 보존한다.

### 롤백 트리거와 처리

| 트리거 | 처리 |
|---|---|
| T-001 신규 파일만 실패 | 검증한 정확한 `skills/define-ui/`만 `gio trash`로 이동 |
| T-002~T-004 기존 파일 회귀 | snapshot의 해당 파일과 diff를 확인한 뒤 그 파일만 복원 |
| 커밋 후 구현 결함 | 이번 실행이 만든 정확한 커밋만 `git revert <commit>` |
| 사용자 소유 변경과 충돌 | 수정·stage를 중단하고 사용자에게 대상 경로와 충돌 보고 |
| 설계 계약 자체의 결함 | revert로 숨기지 않고 실행을 중단해 `$make-design docs/codex-ui-workflow-skills.md`로 승격 |

`git reset --hard`, broad checkout, 저장소 전체 삭제는 사용하지 않는다. 신규 파일을 정리할
때도 정확한 경로와 파일 집합을 먼저 출력하고 복구 가능한 trash를 우선한다.

## 8. 리스크 및 미결

### 기술 리스크

| 리스크 | 영향 | 실측 작업 | 처리 |
|---|---|---|---|
| `define-ui`와 `design-ui`가 “설계” 표현에서 함께 활성화 | 잘못된 비구현/구현 경로 선택 | T-006 U1·U3·U5 | description 앞부분과 비트리거를 조정하고 재평가 |
| UI 명세가 작은 구현의 의무 문서로 변질 | 기존 단순 요청의 회귀 | T-002, T-006 U5·U7 | 명세 없음 허용과 선택적 선행 조건을 직접 검증 |
| 기존 v1 정본과 확장 authority가 충돌 | 구현·review 기대값 혼선 | T-002·T-003·T-005 | target UI 명세의 위치와 충돌 보고를 1:1 대조 |
| inner Codex 환경에서 브라우저 실행 불가 | U9 시각 finding과 Repair 근거 미검증 | T-006 | 대체 능력 탐색 후에도 불가하면 blocked·미검증과 재현 명령 보존; green 금지 |
| 설치된 과거 plugin cache를 평가 | 변경한 스킬이 아닌 다른 버전에서 거짓 green | T-006·T-007 | 현재 worktree 복사본을 격리 설치하고 source→install hash gate를 선행 |
| 사용자 acceptance를 Codex가 자동 승인 | 공개 권한 침범 | T-003, T-006 U10 | `awaiting-user-acceptance`와 자동 pass 금지를 런타임 검증 |
| 정확한 12-file set과 선행 v1의 9-file 검사가 공존 | 오래된 검사가 거짓 실패 | T-005·T-007 | 실행 리포트에서 확장 설계 §9가 해당 범위를 대체함을 명시 |
| 복수 UI 명세를 최신 추측으로 선택 | 잘못된 명세 구현·감사 | T-002·T-003, T-006 U11·U12 | canonical target과 선택 순서·`NeedsInput`을 원본 event로 검증 |
| 무효 acceptance 조합을 자동 보정 | 판정 책임과 증거가 뒤섞임 | T-001·T-003, T-006 U10 | 세 tagged union 밖 입력을 계약 오류로 검증 |
| 세 스킬이 target canonicalization을 다르게 구현 | 같은 명세를 서로 다른 target으로 선택 | T-001·T-002·T-003·T-005·T-006 | 공통 네 `UiTarget`과 exact `(kind, key)` matrix를 정적·runtime 대조 |
| runtime phase와 저장 lifecycle mapping 불일치 | 실패 상태·재개 지점 오염 또는 거짓 ready | T-001·T-005·T-006 | tagged union과 phase→status·resume matrix를 정적·runtime 대조 |
| preflight target 불일치를 persistent failure로 저장 | `Intake` 무실패와 lifecycle union 위반 | T-001·T-005·T-006 U11-T | 응답 전용 `TargetConflict`, 명세 미생성·비변경을 정적·runtime 대조 |
| unknown affected scope가 다른 failure로 누출 | `NeedsInput`·`DesignConflict` 영향 근거 약화 | T-001·T-005·T-006 U4·lifecycle matrix | `UnknownTargetScope`를 reference-blocked에만 허용하는 타입과 fixture 검증 |

### `[추정]` 항목

없음. 파일 구조, 스킬 이름, 기본 명세 경로, 상태와 handoff는 정본에서 확정됐다.
브라우저 가용성은 계약 결정이 아니라 T-006에서 실측할 실행 환경 리스크다.

### 착수 전 사용자 결정

없음. D-001~D-006은 모두 2026-09-05 사용자 승인 뒤 정본에 반영되어 닫혔다.

닫힌 결정 기록:

| ID | 확정 결정 | 정본 반영 위치 |
|---|---|---|
| D-001 | target 또는 user-visible goal이 불명확하면 명세 생성 전 `NeedsClarification`으로 끝내고 답변 뒤 preflight를 다시 평가한다. | §4.1 |
| D-002 | non-ready 명세 review는 기본 `HaltForSpec`; 명시적 spec-independent 요청만 기존 authority의 `GeneralAudit`으로 허용한다. | §5.2 |
| D-003 | 네 `UiTarget`의 kind별 stable key와 case-sensitive exact `(kind, key)` equality를 사용한다. component는 module/export path가 아니라 semantic owner+slug다. | §3.6·§4.1·§4.2 |
| D-004 | runtime-only `DefineUiPhase`와 persistent lifecycle을 분리하고, `intent`·failure resume mapping·interrupted draft의 `Intake` 재시작을 저장 규칙으로 사용한다. | §4.1·§4.2·§4.4 |
| D-005 | 명시 명세 target과 별도 target이 다르면 draft 생성 전 응답 전용 preflight `TargetConflict`로 중단한다. persistent failure를 만들지 않고 `Intake` 무실패를 유지한다. | §3.6·§4.1·§4.2·§4.4 |
| D-006 | failure 영향 범위는 `KnownAffectedScope | UnknownTargetScope`이며 unknown은 접근 불가 주 reference 때문에 stable 이름을 알 수 없는 `ReferenceBlockedFailure`에만 허용한다. | §4.2·§4.4 |

### 독립 검토 결과

2026-09-05 읽기 전용 독립 검토자가 D-005·D-006이 반영된 정본과 이 플랜만 역방향
대조했다.

- 반영한 blocker 1건: `design-ui`·`review-ui`의 target mismatch 응답과 U11-T에 두
  canonical target·명세 경로·영향·필요 결정을 명시했다.
- 반영한 보강 2건: component owner의 `global:project`·route·screen-set·new-app 허용과
  component/기타 owner 금지 행렬을 추가했다. 격리 환경에 없는 `interview`·`make-design`·
  이미지 도구·배포 절차는 실제 호출이 아니라 세 UI 스킬 비활성·비변경·정확한 handoff로
  판정하도록 evidence 계약을 분명히 했다.
- 같은 검토자의 재검토 결과는 blocker 0건, 미반영 enhancement 0건,
  design-rediscussion 0건으로 **실행 착수 가능** 판정이다.
