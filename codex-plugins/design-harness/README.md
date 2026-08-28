# design-harness

프로젝트/워크스페이스의 목적에 맞는 AI 작업 환경(harness)을 설계·생성하는
에이전트 스킬. **Claude Code**와 **Codex CLI** 두 런타임을 각각 전용 변형판으로
지원한다.

지침(CLAUDE.md/AGENTS.md)은 "무엇을 하라"고 말하고, harness는 그것이 실제로
지켜지게 만든다 — 도구·강제(permissions·approval 정책)·검증 체계. 이 스킬의
핵심은 **Capability Gap 분석**이다:

```
Task Requirements − Model Capabilities − Runtime Capabilities = Harness Requirements
```

모델·런타임·기존 설정이 이미 하는 것을 다시 지시하지 않고, 부족한 부분과
반드시 보장해야 할 조건만 차집합으로 채운다.

Harness는 많을수록 좋은 것이 아니다 — 파일 하나가 늘 때마다 컨텍스트 비용·
유지보수·규칙 충돌 가능성이 같이 는다. 그래서 이 스킬은 Gap 분석에 더해
다음을 강제한다:

- **실측 근거** — 관측된 실패/반복 또는 명시된 Invariant만 항목이 된다.
  "혹시 몰라서"는 근거가 아니다.
- **역할 단일성** — 하나의 역할은 harness 전체에서 정확히 한 곳에만 산다.
  지침·커맨드·훅에 같은 규칙을 나눠 놓거나 역할이 겹치는 파일을 둘 만들지
  않는다.
- **체급 맞춤 + 파일 예산** — 프로젝트 규모·단계·팀·개발 방향과 모델의 실측
  특성으로 체급(S/M/L)을 정하고, 그 체급의 신규 파일 상한 안에서만 만든다.
  0개 생성도 정상 결과다.
- **가장 가벼운 충분 수단** — 기존 파일 한 줄 > 지침 한 줄 > 기존 검증 >
  커맨드/스킬 > 훅/정책 순으로 배치한다.

## 구조

```
design-harness/
├── SKILL.md          # Claude Code 전용
└── codex/
    └── SKILL.md      # Codex CLI 전용
```

같은 원칙·절차이며, 각 런타임의 구성 요소(CLAUDE.md·`.claude/`·hooks ↔
AGENTS.md·`$HOME/.agents/skills`·approval 정책)에 맞춰 내용만 다르다.

## 설치 — Claude Code

```bash
git clone https://github.com/jsj9346/design-harness ~/.claude/skills/design-harness
```

사용: `/design-harness` 또는 "이 프로젝트 작업 환경 설계해줘" 등 자연어 호출.

## 설치 — Codex CLI

```bash
git clone https://github.com/jsj9346/design-harness /tmp/design-harness
mkdir -p ~/.agents/skills
cp -r /tmp/design-harness/codex ~/.agents/skills/design-harness
```

사용: `/skills`에서 선택, `$design-harness`로 명시 호출, 또는 작업 설명이
description과 매칭되면 자동 호출.

## 절차 요약

1. **목적 인터뷰** — 목적·실패 모드(겪은 것/우려 구분)·완료 판정·Invariants·
   우선순위·**프로젝트 프로파일**(규모·단계·팀·개발 방향·모델)
2. **기존 능력 인벤토리** — 프로젝트 설정(파일별 역할 한 문장)·런타임 기본기·
   모델 기본기와 실측 약점 (실측만)
3. **Gap 분석 → 체급 → 배치** — 근거 없는 행은 보류, 체급으로 파일 상한 확정,
   Gap 하나에 집 하나(가장 가벼운 수단), 역할 중복 검사·병합
4. **설계안 제시** — 지침층·도구층·강제층·검증층 4층 + **파일 매니페스트**
   (파일·역할·Gap·기존 파일로 안 되는 이유) + 예산 대비 수치·제거 후보·보류
   목록, 승인 대기
5. **적합성 감사 → 검증 설계 → 생성** — 자체 감사 체크리스트 통과 후 판정
   신호·Kill Criteria 확정, 파일 생성

자세한 내용은 각 [SKILL.md](SKILL.md) / [codex/SKILL.md](codex/SKILL.md).

## 관련 스킬

- **[review-harness](https://github.com/jsj9346/review-harness)** — 구축된
  하네스를 **진단·최적화**한다. 하네스는 만들 때가 아니라 모델이 좋아질 때
  낡는다 — 작년에 정당했던 규칙이 올해는 모델 능력과 중복이 되므로, 모델 교체
  주기에 맞춰 여기로 되돌아온다.
- **[design-graph](https://github.com/jsj9346/design-graph)** — 여러 실행 단위를
  **연결**하는 그래프를 설계한다. Harness가 한 Node를 잘 일하게 만든다면,
  Graph는 그 Node들이 함께 일하게 만든다.

## License

[MIT](LICENSE)
