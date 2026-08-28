# design-loop

하나의 목표(Goal)를 **Observe → Decide → Act → Verify → 재시도/종료**로 반복
실행하는 목표 실행 루프를 설계하고, 그 설계를 **복붙 가능한 `/goal` 명령어 한
줄**로 압축해 제안하는 에이전트 스킬. **Claude Code**와 **Codex CLI** 두
런타임을 각각 전용 변형판으로 지원한다.

[design-harness](https://github.com/jsj9346/design-harness) ·
[design-graph](https://github.com/jsj9346/design-graph)의 자매 스킬이다:

```
design-harness  =  한 Node가 일을 잘하게 만든다      (Node 내부: 지침·도구·강제·검증)
design-graph    =  Node들이 함께 일을 잘하게 만든다   (Node 연결: contract·state·governance)
design-loop     =  하나의 목표가 끝까지 도달하게 한다 (반복 제어: 성공 기준·재시도·탈출)
```

## 왜 필요한가

`/goal`은 Claude Code와 Codex CLI 양쪽의 **기본 탑재** 명령어다 — 조건을 걸면
충족될 때까지 여러 턴에 걸쳐 자율 실행한다. 강력한 만큼, 조건 텍스트가 부실한
채로 걸면 실패 모드가 그대로 증폭된다:

- 검증 증거가 없으면 → 에이전트의 자기보고("됐다")로 종료된다
- 탈출 조건이 성공뿐이면 → 외부 요인으로 막혔을 때 끝나지 못한다
- 재시도 규칙이 없으면 → 같은 실패를 같은 방법으로 반복한다
- 예산이 없으면 → 비용이 통제되지 않는다

이 스킬은 루프를 걸기 **전에** 그 네 가지를 확정하고, 결과를 코드블록 하나에
담긴 한 줄 명령어로 넘겨준다. **문서를 만들지 않는다** — 산출물은 복붙할
명령어 그 자체다.

## 대상 루프

```
          ┌─────────────┐
          │    Goal     │
          └──────┬──────┘
                 ↓
             Observe
                 ↓
              Decide
                 ↓
               Act
                 ↓
              Verify
                 ↓
        ┌── 성공했는가? ──┐
        │                 │
       No                Yes
        │                 │
        └──→ 수정/재시도   └──→ Stop
```

## 구조

```
design-loop/
├── SKILL.md          # Claude Code 전용
└── codex/
    └── SKILL.md      # Codex CLI 전용
```

같은 원칙·절차이며, 각 런타임의 `/goal` 문법 차이에 맞춰 산출 명령어만 다르다:

| | Claude Code | Codex CLI |
|---|---|---|
| 문법 | `/goal <조건 텍스트>` (최대 4,000자) | `/goal <objective>` |
| 완료 판정 | 매 턴 별도 판정 모델이 조건 충족 평가 | 실행 모델이 stopping condition 도달을 판단 |
| 라이프사이클 | 조건 충족·불가능 판정·해제 | `/goal`(상태)·`pause`·`resume`·`clear` |
| 토큰 예산 | `+Nk` 지시자, `claude --max-budget-usd` | **없음** → 예산을 objective 안에 중단 규칙으로 (soft) |
| 활성화 | 기본 | feature `goals` (미표시 시 `codex features enable goals`) |

## 설치 — Claude Code

```bash
git clone https://github.com/jsj9346/design-loop ~/.claude/skills/design-loop
```

사용: `/design-loop` 또는 "이 목표 루프 설계해줘", "goal 명령어 만들어줘" 등
자연어 호출.

## 설치 — Codex CLI

```bash
git clone https://github.com/jsj9346/design-loop /tmp/design-loop
mkdir -p ~/.agents/skills
cp -r /tmp/design-loop/codex ~/.agents/skills/design-loop
```

사용: `/skills`에서 선택, `$design-loop`로 명시 호출, 또는 작업 설명이
description과 매칭되면 자동 호출.

## 절차 요약

0. **루프 적합성 판정 (게이트)** — 입력된 작업이 루프 사이클로 구현 가능한지
   먼저 판정(종료 상태 정의 가능 · 관찰 가능 · 반복이 유효 · Agent 실행
   가능). 가능하면 설계 진행, 불가능하면 불가 판정 메시지와 이유를 출력하고
   설계 없이 종료
1. **Goal 인터뷰 → 성공 기준** — 자연어 목표를 검증 가능한 기준으로 변환하고
   기준마다 **증거**(실행 명령까지)를 확정. Invariants·사람 개입 지점·
   open-ended 목표의 Satisficing Condition
2. **단계별 계약** — Observe(무엇을 관찰) / Decide(판정 기준) / Act(허용 범위) /
   Verify(검증 명령)를 각각 한 구절로
3. **재시도 정책** — 최대 반복 횟수(권장 3–5회)·반복 간 **수정** 규칙·
   에스컬레이션 조건
4. **Budget** — 반복 1회 비용 추정 × (반복 상한 + 1) → `+Nk` (Codex는 시간·
   반복 상한을 텍스트 조항으로)
5. **명령어 조립** — 성공 기준을 맨 앞에 둔 **한 줄**로 압축, 자가 점검 4항목
   통과 후 코드블록 하나로 제시

## 하드 레일

- **판정 없는 설계 착수 금지** — 루프 적합성 판정(0단계) 통과 전에는 설계를
  시작하지 않고, 불가 판정 시 사유를 보고하고 종료한다
- **설계 없는 goal 실행 금지** — 성공 기준·탈출 조건·예산이 없으면 명령어를
  제안하지 않는다
- **증거 없는 Verify 금지** — 자기보고("됐다")는 Verify가 아니다
- **탈출 조건은 성공만이 아니다** — SUCCESS / BLOCKED(재시도 않고 중단) /
  FAILED / ESCALATED를 모두 조건에 반영
- **재시도는 반복이 아니라 수정이다** — 같은 Act를 그대로 다시 거는 재시도는
  설계 결함
- **예산 필수** — 반복 상한 없는 명령어는 제안하지 않는다
- **루프 하나 = 목표 하나** — 목표가 둘 이상이면 나누거나 design-graph로 승격
- **복붙 한 줄 원칙** — 줄바꿈 없이, 코드블록 안에 명령어 외 텍스트를 섞지
  않는다

자세한 내용은 각 [SKILL.md](SKILL.md) / [codex/SKILL.md](codex/SKILL.md).

## 관련 스킬

- **[design-harness](https://github.com/jsj9346/design-harness)** — 루프가
  도는 **환경**(지침·도구·권한·검증)을 설계한다. Verify 증거를 만들 수단이
  없으면 여기가 먼저다.
- **[design-graph](https://github.com/jsj9346/design-graph)** — 루프가 여러
  개거나 Decide 분기가 셋을 넘으면 루프가 아니라 그래프다.
- **[review-harness](https://github.com/jsj9346/review-harness)** — 구축된
  하네스를 진단·최적화한다.

## License

[MIT](LICENSE)
