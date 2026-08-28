# milestone

프로젝트의 **활성 마일스톤 하나**를 설정·조회·종료하는 에이전트 스킬. **Claude Code**와
**Codex CLI** 두 런타임을 각각 전용 변형판으로 지원한다.

```
/current-status  =  지금 무엇이 열려 있고 무엇부터 할까
/milestone       =  그중 무엇이 이번 목표이고, 목표는 언제 끝나는가
```

## 왜 필요한가

design → plan → execute → verify 체인이 잘 돌아도 **기준선**이 없으면 두 가지가 안 된다 —
우선순위가 보드 내부에서만 매겨지고("무엇이 급한가"는 답해도 "무엇이 목표인가"는 못 답한다),
"얼마나 남았나"를 실물로 잴 수 없다. 그 상태에서 열린 항목은 자기 자신을 먹이로 자란다
(한 프로젝트에서 18일간 플랜 359개, 대부분이 기록 체계를 재는 메타 작업이었다).

이 스킬은 `MILESTONE.md` 한 파일로 그 기준선을 두고, `/current-status`가 **범위 밖 작업을
순위에서 빼게** 만든다. 목표를 적는 것이 아니라 **목표 밖을 순위에서 빼는 것**이 실제 효과다.

## 핵심 규칙

- **종료 조건은 명령으로 잰다** — 각 조건에 `검증:` 줄(셸 명령 / 파일 상태 / 카드 닫힘).
  "웹 UI 완성" 같은 산문은 `set`이 거부하고 되묻는다.
- **숫자를 손으로 적지 않는다** — "3/7"은 파일에 없다. `status`가 매번 검증 줄을 실행해 센다.
- **소속은 범위 표로** — 카드·항목마다 필드를 달지 않고 `MILESTONE.md`의 표 하나가 정본이다.
  이 표가 곧 "이번엔 안 한다"의 기록이다.
- **활성 마일스톤은 하나** — 둘을 열고 싶으면 그것은 우선순위 미결이다.
- **기존 기록 규약을 건드리지 않는다** — 칸반·devlog·plan은 각 프로젝트 스킬이 쓴다.

## 동작

| 인자 | 하는 일 | 쓰기 |
|---|---|---|
| `set <이름>` | 목표 한 문장·종료 조건 3~7개·범위 표를 대화로 확정. 검증 줄은 **실제로 실행해** 본다 | `MILESTONE.md` |
| `status` | 모든 검증 줄 실행 → 남은 조건 수 · 범위 작업 상태 · **범위 밖인데 최근 손댄 것**(목표 이탈 신호) | 없음 |
| `close` | `status` 전부 통과일 때만. 미달이 있으면 거부 — "그래도 닫자"는 범위 변경이지 종료가 아니다 | `milestones/` 아카이브 |

## `/current-status`와의 계약

프로젝트의 `/current-status`에 세 줄을 통합한다: ① `MILESTONE.md`를 소스로 읽는다 ② 게이트 **G0** —
범위 표에 없는 항목은 순위에 올리지 않고 «마일스톤 외» 표로 보낸다(범위 안 조건을 직접 블록하는
항목만 «범위 밖·블로커»로 예외) ③ 출력 첫머리에 "M1 · 남은 조건 N개".

## 설치

```bash
# Claude Code
git clone https://github.com/jsj9346/milestone ~/.claude/skills/milestone

# Codex CLI
git clone https://github.com/jsj9346/milestone /tmp/milestone && \
  mkdir -p ~/.agents/skills/milestone && cp /tmp/milestone/codex/SKILL.md ~/.agents/skills/milestone/
```

## 전제

열린 작업의 정본으로 프로젝트 루트에 `kanban.md`(칸반 카드형) 또는 `workstate.md`(작업 상태 원장형)
하나를 두는 design→plan→execute→verify→devnote 스킬 체인. 둘 다 없으면 `set`이 `workstate.md`
신설을 제안한다.

## 라이선스

MIT
