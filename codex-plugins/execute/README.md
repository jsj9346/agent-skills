# execute

확정된 플랜(`plans/YYYYMMDD-*-plan.md`)을 실제로 실행하는 에이전트 스킬. **Claude
Code**와 **Codex CLI** 두 런타임을 각각 전용 변형판으로 지원한다.

```
/make-plan  =  어떤 순서로 실행할까
/execute    =  플랜대로 만들고, 원장·검증·커밋으로 닫는다
/verify     =  만든 것이 계약대로인지 독립 판정한다
```

## 왜 필요한가

실행 사이클은 컨텍스트가 가장 길어 유실도 가장 크다. 이 스킬은 **첫 작업에 손대기
전에** 실행 리포트(`plans/YYYYMMDD-<주제>-execute-report.md`)를 개설하고, 작업 하나가
끝날 때마다 원장에 한 행을 append한다 — 세션이 끊겨도 "어디까지 갔고 어디서
이어받는가"가 파일로 남는다. **재개 지점의 정본은 이 원장이다** — 플랜 체크박스도 커밋
로그도 아니다.

## 핵심 규칙

- **계약 없는 실행은 하지 않는다** — 플랜이 없으면 `/make-plan`, 설계가 없으면
  `/make-design`이 먼저다. 플랜의 서술은 계약이 아니다 — 기대값은 항상 정본 설계
  문서에서 나오고, 어긋나면 설계 문서가 이긴다.
- **검증 조건을 실행하고 결과를 확인한 뒤** 다음 작업으로 — "될 것이다"로 넘어가지
  않는다. 작업 단위 원자 커밋(메시지에 `T-00x`).
- **새 검사는 역검증까지** — 일부러 위반을 넣어 실제로 실패하는지 확인한다.
- **독립 검증은 산출물 기반으로** — 검증자에게 정본 경로만 넘기고 구현 의도는 넘기지
  않는다.
- **중단 시에도 리포트를 먼저 닫는다** — 계약과 어긋남·설계 결함·범위 초과를 만나면
  임의로 계속하지 않고 중단·보고한다.
- 종료 시 **`/verify` 권고 판정** — 이번 검증이 구조적으로 못 본 범위(계약 개정 후 검증,
  검증 미배정 구간, 플랜 밖 수동 변경 등)가 있을 때만 권한다. 매번 붙이면 신호가 죽는다.
- 마무리의 마지막 줄은 **권장 모델 + 다음 명령**(재개 지점 포함) 제안이다.

## 설치

```bash
# Claude Code
/plugin marketplace add jsj9346/agent-skills
/plugin install execute@jsj9346-skills

# Codex CLI
codex plugin marketplace add jsj9346/agent-skills
codex plugin add execute@jsj9346-skills
```

## 전제

interview→make-design→make-plan→execute→verify 체인의 구현 단계. 확정된 플랜이
입력이고, 없으면 `/make-plan`이 먼저다.

## 라이선스

MIT
