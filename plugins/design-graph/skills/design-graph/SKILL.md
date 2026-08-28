---
name: design-graph
description: >-
  여러 실행 단위(Agent·Tool·Validator·스크립트·사람)를 연결해 하나의 작업
  시스템을 만드는 그래프(graph)를 설계·생성하는 스킬. 다단계 파이프라인·
  멀티 에이전트 워크플로우·검증 게이트가 있는 작업 흐름을 셋업하거나, 기존
  워크플로우의 연결 구조를 재설계·진단할 때 사용한다. 핵심은 Node 간
  Contract — 그래프 모양보다 Edge마다의 입출력 계약·실패 행선지·상태 전달을
  먼저 확정하고, 라우팅은 deterministic을 기본값으로 한다. "그래프 만들어줘",
  "파이프라인 설계", "에이전트 연결/오케스트레이션 설계", "워크플로우 구조
  잡아줘" 등을 다룰 때 반드시 사용할 것.
---

# Design Graph — 실행 단위 연결 구조 설계

> **Claude Code 전용 스킬이다** — 절차가 Claude Code의 구성 요소(서브에이전트·
> 커스텀 커맨드·Workflow·hooks)를 전제한다. Codex CLI 사용자는 변형판
> [codex/SKILL.md](codex/SKILL.md)를 사용할 것.

> [design-harness](https://github.com/jsj9346/design-harness)가 **한 Node가
> 일을 잘하게** 만든다면, 이 스킬은 **그 Node들이 함께 일을 잘하게** 만든다.
> Harness는 Graph의 기반 인프라다 — 불안정한 Node를 연결하면 Graph도
> 불안정하다.

## 원칙 (하드 레일)

1. **Harness 먼저** — 각 Node의 역할·입출력·검증이 정의되지 않았으면 연결하지
   않는다. 미비한 Node는 인벤토리에 표기하고 design-harness 선행을 권고한다.
2. **Contract 없는 Edge 금지** — 모든 Edge는 입출력 형태·실패 시 행선지를
   명시해야 한다. "자유 형식 텍스트 + 알아서 이해"는 Edge가 아니다.
3. **Terminal은 상태로, 증거로** — 종단점은 "마지막 Node가 답한 위치"가
   아니라 검증된 상태다(Last Node ≠ Terminal State). Agent의 자기보고("Done")는
   종단 조건이 될 수 없다 — 외부 검증 가능한 증거(테스트 출력·diff·상태
   조회)로 판정한다.
4. **Deterministic 기본** — 룰·코드로 고정할 수 있는 라우팅·검증은 LLM에게
   맡기지 않는다. Agentic 라우팅을 쓰는 Edge에는 왜 룰로 못 하는지 근거를
   단다. 골격은 deterministic, Node 내부만 agentic이 기본형이다.
5. **Governance는 위치로** — Invariant의 강제는 프롬프트가 아니라 그래프 상
   위치로 한다: 사전 게이트(실행 *전*에 Allow/Modify/Deny)가 기본이고, 사후
   검증만 있는 governance는 설계 결함으로 보고한다.
6. **Minimal 시작** — Node 하나가 늘 때마다 State·Routing·Failure 문제가 곱으로
   는다. 단일 Node + deterministic 스크립트로 충분하면 그래프를 만들지 않는
   것이 정답이며, 그렇게 보고한다.
7. **승인 후 생성** — 설계안 제시 → 사용자 승인 → 파일 생성. 기존 파일을
   덮어쓸 때는 반드시 diff를 먼저 보여준다.

## 절차

### 1. 목표 인터뷰 → Terminal Contract

사용자에게 묻고 (도메인에 맞게 적응형으로, 한 번에 몰아서), 답을 **Terminal
Contract**로 확정한다 — 그래프를 그리기 전에:

- **시스템 목표 → Postcondition**: 자연어 목표를 그대로 쓰지 않고 검증 가능한
  Postcondition 목록(Acceptance Criteria)으로 변환한다. 각 조건마다 그것을
  증명할 **Verification Evidence**(테스트 출력·diff·상태 조회 등)를 함께
  적는다 — 증거를 못 정하는 조건은 종단 조건이 될 수 없다.
- **종단 상태 4종**: SUCCESS(모든 필수 조건 PASS) / BLOCKED(외부 조건 —
  자격증명·권한·정보 부족) / FAILED(허용된 복구 범위 안에서 목표 미달) /
  ESCALATED(권한 경계 도달 — 실패가 아니라 경계의 정상 인식이다). 성공만
  정의된 그래프는 실전에서 끝나지 못한다.
- **Open-ended 목표**: "최대한 개선" 류에는 Satisficing Condition(충분히 좋은
  상태)과 Budget(반복·재시도·비용 상한)을 정의한다 — 더 *할 수 있는* 것과 더
  *해야 하는* 것은 다르다.
- **실패 대응**: 중간 Node가 실패하면? (재시도 / 이전 Node로 반환 / 사람
  에스컬레이션 / 중단 — Node별로 다를 수 있다)
- **Invariants**: 어떤 실행이 절대 일어나면 안 되는가? (여기서 나온 것만
  governance 게이트가 된다)
- **사람 개입 지점**: 어디서 사람의 승인·판정이 필요한가?
- **우선순위**: Accuracy / Cost / Speed 중 무엇이 중요한가? (병렬화·재시도
  상한·모델 티어 배분이 여기 걸린다)

사용자가 답하지 못하는 항목은 비워 둔다 — 지어내지 않는다.

### 2. Node 인벤토리

기존 실행 단위를 **실제로 읽고** 목록화한다:

- **기존 자산**: 서브에이전트(`.claude/agents/`)·커스텀 커맨드·스킬·훅·
  스크립트·CI 잡·MCP 도구. 이미 있는 것을 새 Node로 다시 만들지 않는다.
- **Node별 harness 상태**: 각 후보 Node의 역할·입출력·검증이 정의돼 있는가?
  미비하면 "harness 미비"로 표기 — 이 Node를 쓰는 설계는 design-harness
  선행을 전제로 한다.
- **Terminal Verification Capability**: 1단계 Terminal Contract의 각 증거를
  실제로 만들 수단이 있는가? (예: tests_pass가 종단 조건인데 테스트 실행
  도구가 없으면 그 조건은 검증 불가.) 없으면 harness 보강(design-harness)
  또는 종단 조건 재협상 — 둘 중 하나 없이 진행하지 않는다.
- **런타임 기본기**: Claude Code가 기본 제공하는 오케스트레이션 — Agent
  tool(서브에이전트 병렬 실행)·Workflow(deterministic 스크립트 + pipeline/
  parallel)·hooks(PreToolUse = 사전 게이트)·permission 체계. 버전에 따라
  다르므로 이번 세션에서 확인 가능한 것 기준, 확인 못 한 것은 "미확인" 표기.

Node는 Agent만이 아니다 — 함수·스크립트·검증기·CI·사람도 Node다. LLM이
필요 없는 자리에 Agent를 두지 않는다.

### 3. Graph 설계

**역방향으로 설계한다** — Terminal State에서 출발해 "이 증거를 만들려면 어떤
Verification이 필요한가 → 그 입력은 어떤 Node가 만드는가 → 그 Node는 무엇을
입력받는가"로 START까지 거슬러 온다(실행은 forward, 설계는 backward). 이렇게
나온 것만으로 셋을 확정한다:

**(a) Topology** — 순서·분기·병렬을 그림(텍스트 다이어그램)으로. 병렬 뒤의
barrier(전부 대기)는 정말 전 결과가 함께 필요한 곳에만 둔다. 모든 Node/Edge에
**존재 시험**을 적용한다: "이 Node가 Terminal Condition에 기여하는가?" —
기여하지 않으면 제거 후보다(Terminal Contract가 그래프 단순화 기준).

**(b) Edge Contract 표** — 표로 강제한다:

| Edge (A→B) | A의 출력 | B의 입력 | 실패 시 행선지 | 재시도/상한 | 라우팅 (det/agentic+근거) |
|---|---|---|---|---|---|

- Contract 열이 빈 Edge는 그래프에 넣을 수 없다.
- 구조화 출력(스키마)을 쓸 수 있는 Edge는 자유 텍스트 대신 스키마로 잠근다.

**(c) State** — Node 사이를 흐르는 작업 상태의 정의와 소유자. 두 Node가 같은
상태를 각자 들고 있게 하지 않는다(단일 진실원).

### 4. Governance 배치

1단계의 Invariant마다 게이트를 배치한다:

- **사전 게이트가 기본**: `Node → 게이트 → 실행` (Claude Code에서는 PreToolUse
  훅·permission deny가 이 자리다). `실행 → 사후 검증`만 있는 Invariant는 설계
  결함으로 보고하고 승격안을 제시한다.
- **폭주 방지**: 재시도 상한·루프 탈출 조건·Node/비용 상한을 명시한다.
  BLOCKED(외부 조건)에서는 재시도하지 않는다 — 무한 retry의 전형적 원천.
  Budget 소진은 기계적으로 FAILED가 아니라 상황에 따라 FAILED/BLOCKED/
  ESCALATED로 분류한다. 그래프가 스스로를 수정·확장할수록(동적 그래프)
  게이트는 더 강해야 한다.
- **사람 게이트**: 1단계에서 나온 사람 개입 지점을 그래프 상 위치로 박는다 —
  "필요하면 물어본다"가 아니라 어느 Edge에서 멈추는지를.

### 5. 검증 설계 + 생성

*실행*의 종료 판정은 1단계 Terminal Contract가 담당한다 — 이 단계의 평가
기준은 그것이 아니라 **설계 자체의 메타 평가**다(이 그래프를 유지할 가치가
있는가). 파일을 만들기 **전에** 사용자와 확정한다:

- **판정 신호**: 이 그래프가 작동한다를 무엇으로 관측하는가? (끝까지 도달률·
  재시도 빈도·사람 개입 빈도 등)
- **Kill Criteria**: 무엇이 보이면 그래프를 줄이거나 되돌리는가?
  (증상 예: Contract 위반이 잦아 Edge마다 땜질, barrier 대기가 병렬 이득을
  잠식, 단일 Node로 했을 때보다 느리거나 비쌈, 디버깅 불가)
- **재검토 시점**: 언제 다시 보는가? (Node 추가·모델 교체 시 Edge Contract
  재검토)

승인 후 파일을 생성한다 — 서브에이전트 정의(`.claude/agents/*.md`)·커맨드·
Workflow 스크립트·훅 설정 등, 설계에서 확정된 것만. 생성한 파일 목록과 각
파일이 그래프의 어느 Node/Edge/게이트인지 요약을 보고한다.

## 산출물이 아닌 것

- Node **내부**를 설계하지 않는다 — 개별 Node의 지침·도구·검증은
  design-harness의 몫이다. 이 스킬은 연결·계약·배치만 다룬다.
- Multi-Agent를 전제하지 않는다 — 설계 결과가 "Agent 하나 + 스크립트"라면
  그것이 정답이고, 그래프를 만들지 않는 것도 유효한 산출이다.
- 미래 확장을 위한 빈 Node·빈 분기를 미리 만들지 않는다.
