# make-plan

확정된 설계 문서를 **실행 가능한 플랜**(우선순위·검증 조건·의존성·롤백)으로 변환하는
에이전트 스킬. **Claude Code**와 **Codex CLI** 두 런타임을 각각 전용 변형판으로
지원한다.

```
/make-design  =  무엇을 만들지의 계약
/make-plan    =  어떤 순서로, 무엇으로 검증하며 실행할까
/execute      =  플랜대로 만든다
```

## 왜 필요한가

계약 없는 플랜은 근거가 없고, 플랜 없는 실행은 검증 조건이 없다. 이 스킬은 설계 문서의
계약을 **작업 단위 + 잴 수 있는 검증 조건**으로 번역해, 실행이 "될 것이다"가 아니라
명령의 결과로 진행되게 만든다. 산출물은 `plans/YYYYMMDD-<주제>-plan.md` 문서 하나다 —
**플랜은 실행하지 않는다.**

## 핵심 규칙

- **정본 설계 문서 없이는 짜지 않는다** — 없으면 `/make-design`을 먼저 제안한다.
  verify 리포트를 입력으로 받아도 계약은 리포트가 인용한 정본 문서다.
- **검증 조건은 복붙 실행 가능한 명령으로** — "정상 동작 확인" 금지. 잴 수 없는 검증
  조건은 검증하지 않은 것과 같다.
- **수행자·검증자 분리** — 검증자는 구현이 아니라 정본 설계 문서를 보고 테스트를 쓴다.
- **상태 어휘 셋** — `초안` / `완료` / `중단 (T-00x까지 / 사유)`. 전이는 `/execute`가
  한다.
- **전달 전 독립 검토** — 플랜 초안 + 정본 문서만 넘긴다(의도 설명을 넘기면 독립 검토가
  아니다). 블로커 미반영은 착수 전 사용자 결정으로 올린다 — 말없이 기각하지 않는다.
- 마무리의 마지막 줄은 **권장 모델 + 다음 명령**(방금 만든 플랜의 실제 경로) 제안이다.

## 설치

```bash
# Claude Code
/plugin marketplace add jsj9346/agent-skills
/plugin install make-plan@jsj9346-skills

# Codex CLI
codex plugin marketplace add jsj9346/agent-skills
codex plugin add make-plan@jsj9346-skills
```

## 전제

interview→make-design→make-plan→execute→verify 체인의 계획 단계. 확정된 설계 문서가
입력이고, 없으면 `/make-design`이 먼저다.

## 라이선스

MIT
