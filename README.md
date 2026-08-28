# design-graph

여러 실행 단위(Agent·Tool·Validator·스크립트·사람)를 연결해 하나의 작업
시스템을 만드는 그래프(graph)를 설계·생성하는 에이전트 스킬. **Claude Code**와
**Codex CLI** 두 런타임을 각각 전용 변형판으로 지원한다.

[design-harness](https://github.com/jsj9346/design-harness)의 자매 스킬이다:

```
design-harness  =  각 Node가 일을 잘하게 만든다   (Node 내부: 지침·도구·강제·검증)
design-graph    =  그 Node들이 함께 일을 잘하게 만든다 (Node 연결: topology·contract·state·governance)
```

이 스킬의 핵심은 **Terminal Contract와 Node 간 Contract**다 — 그래프를
그리기 전에 "무엇이 검증된 종단 상태인가"(Postcondition + 증거, 종단 상태
4종)를 먼저 확정하고, 거기서 역방향으로 설계하며, Edge마다의 입출력 계약·
실패 행선지·상태 전달을 잠근다. 라우팅은 deterministic이 기본값이고(골격은
코드, Node 내부만 agentic), Invariant의 강제는 프롬프트가 아니라 그래프 상
위치(사전 게이트)로 한다.

## 구조

```
design-graph/
├── SKILL.md          # Claude Code 전용
└── codex/
    └── SKILL.md      # Codex CLI 전용
```

같은 원칙·절차이며, 각 런타임의 오케스트레이션 수단(서브에이전트·Workflow·
hooks ↔ `codex exec` 체이닝·approval 정책·파일 매체 Edge)에 맞춰 내용만
다르다.

## 설치 — Claude Code

```bash
git clone https://github.com/jsj9346/design-graph ~/.claude/skills/design-graph
```

사용: `/design-graph` 또는 "이 워크플로우 그래프 설계해줘" 등 자연어 호출.

## 설치 — Codex CLI

```bash
git clone https://github.com/jsj9346/design-graph /tmp/design-graph
mkdir -p ~/.agents/skills
cp -r /tmp/design-graph/codex ~/.agents/skills/design-graph
```

사용: `/skills`에서 선택, `$design-graph`로 명시 호출, 또는 작업 설명이
description과 매칭되면 자동 호출.

## 절차 요약

1. **목표 인터뷰 → Terminal Contract** — 목표를 Postcondition + Verification Evidence로 변환, 종단 상태 4종(SUCCESS/BLOCKED/FAILED/ESCALATED), open-ended면 Satisficing+Budget
2. **Node 인벤토리** — 기존 자산·Node별 harness 상태·**Terminal Verification Capability**·런타임 오케스트레이션 기본기 (실측만)
3. **Graph 설계** — Terminal State에서 **역방향 설계** + Node 존재 시험("Terminal Condition에 기여하는가"). Topology + Edge Contract 표 + State 단일 진실원
4. **Governance 배치** — Invariant별 사전 게이트·폭주 방지(BLOCKED에서 retry 금지)·사람 게이트를 그래프 상 위치로
5. **검증 설계 + 생성** — 설계 자체의 메타 평가(판정 신호·Kill Criteria) 확정 후 파일 생성. 실행의 종료 판정은 1단계 Terminal Contract 소관

## 하드 레일

- **Harness 먼저** — 불안정한 Node를 연결하지 않는다 (미비 Node는 design-harness 선행)
- **Contract 없는 Edge 금지** — "자유 형식 텍스트 + 알아서 이해"는 Edge가 아니다
- **Terminal은 상태로, 증거로** — Last Node ≠ Terminal State. 자기보고("Done")는 종단 조건이 아니다
- **Deterministic 기본** — agentic 라우팅에는 근거 필수
- **Governance는 위치로** — 사후 검증만 있는 Invariant는 설계 결함
- **Minimal 시작** — 그래프를 만들지 않는 것도 유효한 산출

자세한 내용은 각 [SKILL.md](SKILL.md) / [codex/SKILL.md](codex/SKILL.md).

## 관련 스킬

- **[design-harness](https://github.com/jsj9346/design-harness)** — 각 Node의
  작업 환경을 **설계**한다. 불안정한 Node를 연결하면 Graph도 불안정하므로
  미비한 Node는 여기가 먼저다.
- **[review-harness](https://github.com/jsj9346/review-harness)** — 구축된
  하네스를 **진단·최적화**한다. Node 하네스가 모델 능력과 중복되어 비대해졌을 때.

## License

[MIT](LICENSE)
