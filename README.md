# agent-skills

jsj9346의 에이전트 스킬 모음. **Claude Code**와 **Codex CLI** 양쪽의 공식 플러그인 마켓플레이스 메커니즘을 이 레포 하나로 서빙합니다.

이전에는 스킬마다 개별 공개 레포로 나뉘어 있었으나(`design-harness`, `interview`, `milestone` 등), 이 레포로 통합되었습니다. 개별 레포는 archive 처리되고 이 레포로 리다이렉트합니다.

## 왜 두 개의 트리인가

Claude Code와 Codex는 각자 `skills` 경로를 플러그인 루트 기준 `./skills/`로 고정합니다. 두 런타임의 매니페스트를 같은 플러그인 폴더에 두면 SKILL.md를 공유하게 되어, 런타임별로 다르게 쓴 내용을 유지할 수 없습니다. 그래서 트리를 완전히 분리했습니다:

```
agent-skills/
├── .claude-plugin/marketplace.json   # Claude Code 마켓플레이스 카탈로그
├── plugins/<name>/                   # Claude Code용 플러그인 (SKILL.md는 Claude Code 전용 문구)
│   ├── .claude-plugin/plugin.json
│   └── skills/<name>/SKILL.md
├── .agents/plugins/marketplace.json  # Codex 마켓플레이스 카탈로그 (repo/team)
└── codex-plugins/<name>/             # Codex용 플러그인 (SKILL.md는 Codex 전용 문구)
    ├── .codex-plugin/plugin.json
    └── skills/<name>/SKILL.md
```

같은 스킬이라도 두 런타임의 SKILL.md 내용은 서로 다를 수 있습니다(런타임별 메커니즘 차이 반영).

마켓플레이스 카탈로그 이름은 `jsj9346-skills`입니다 (`agent-skills`는 Anthropic 공식 마켓플레이스 전용 예약어라 Claude Code가 거부합니다). 레포 이름은 `agent-skills` 그대로입니다.

## 설치

**Claude Code**

```
/plugin marketplace add jsj9346/agent-skills
/plugin install design-harness@jsj9346-skills
```

**Codex CLI**

```
codex plugin marketplace add jsj9346/agent-skills
codex plugin add design-harness@jsj9346-skills
```

## 포함된 스킬

| 스킬 | 설명 | Claude Code | Codex CLI |
| --- | --- | --- | --- |
| [current-status](plugins/current-status) | 원장·기록·실물을 교차 검증해 현황을 판정하고 우선순위·다음 명령을 제안 | ✅ | ✅ |
| [design-graph](plugins/design-graph) | 여러 실행 단위(Agent·Tool·Validator·스크립트·사람)를 연결해 파이프라인/멀티 에이전트 워크플로우 그래프를 설계 | ✅ | ✅ |
| [design-harness](plugins/design-harness) | 프로젝트 목적에 맞는 AI 작업 환경(하네스) — CLAUDE.md/AGENTS.md·커맨드·훅·검증 체계를 설계 | ✅ | ✅ |
| [design-loop](plugins/design-loop) | 목표 실행 루프(Observe→Decide→Act→Verify)를 설계해 복붙 가능한 `/goal` 명령어 한 줄로 압축 제안 | ✅ | ✅ |
| [documentize-context](plugins/documentize-context) | 세션의 맥락(목표·결정·피드백·워크플로우)을 재사용 가능한 마크다운 문서로 정리 | ✅ | ✅ |
| [execute](plugins/execute) | 확정된 플랜을 실행하고 실행 리포트(작업 원장)·독립 검증·커밋으로 닫음 | ✅ | ✅ |
| [explain](plugins/explain) | 작업·문서·코드를 비개발자 눈높이로 쉽게 설명(읽기 전용, 대상 수정 없음) | ✅ | ✅ |
| [interview](plugins/interview) | 작업을 설계하기 전에 인터뷰 형식으로 "무엇을 왜 만들까"를 확정해 결정 기록으로 남김 | ✅ | ✅ |
| [make-agents](plugins/make-agents) | 프로젝트 목적에 맞는 서브에이전트/에이전트 팀을 설계·생성하고 스킬을 라우팅 | ✅ | ✅ |
| [make-design](plugins/make-design) | 확정된 방향(결정 기록·미결 항목)을 경계·계약의 정본 설계 문서로 확정 | ✅ | ✅ |
| [make-plan](plugins/make-plan) | 설계 문서를 실행 가능한 플랜(작업·검증 조건·의존성·롤백)으로 변환 | ✅ | ✅ |
| [milestone](plugins/milestone) | 프로젝트의 활성 마일스톤(하나)을 종료 조건 기준으로 설정·조회·종료 | ✅ | ✅ |
| [research](plugins/research) | 작업 중 막힌 질문을 출처 붙은 답으로 바꿔 조사 노트 문서로 남김(결정은 하지 않음) | ✅ | ✅ |
| [review-harness](plugins/review-harness) | 이미 구축된 AI 작업 환경의 중복 하네스·과최적화를 진단하고 걷어냄 | ✅ | ✅ |
| [verify](plugins/verify) | 작업물을 정본 문서에 대조해 독립 검증하고 판정 리포트 문서를 남김 | ✅ | ✅ |

## 개발 사이클 체인

다섯 스킬이 논의→설계→계획→구현→검증의 개발 사이클을 이룬다. 각 단계의 산출물이 다음
단계의 입력이고, 각 스킬은 마무리에서 **권장 모델 + 다음 명령**(대상 경로 포함)을
제안해 사이클이 이어진다:

```
/interview <주제>                        → discussions/I-<slug>.md (결정 기록)
/make-design discussions/I-<slug>.md     → docs/<주제>.md (정본 설계 문서)
/make-plan docs/<주제>.md                → plans/YYYYMMDD-<주제>-plan.md
/execute plans/YYYYMMDD-<주제>-plan.md   → 코드 + plans/YYYYMMDD-<주제>-execute-report.md
/verify <대상 경로>                       → plans/YYYYMMDD-<대상>-verify-report.md
```

verify의 발견은 `/execute <리포트>`(소수·명확) 또는 `/make-plan <리포트>`(다수·얽힘)로
되돌아 사이클을 다시 돈다. 문서 결함이면 `/make-design`, 방향 자체가 갈리면
`/interview`가 재진입점이다. 각 스킬은 단독으로도 동작한다 — 전 단계 산출물이 없으면
그 단계를 먼저 제안하고 멈춘다.

사이클과 사이클 사이에는 관제 스킬 둘이 선다: **`/current-status`**가 원장·기록·실물을
교차 검증해 "다음에 무엇을"을 판정하고(각 스킬이 사이클을 닫으며 넘기는 수신처),
**`/milestone`**이 "그중 무엇이 이번 목표인가"의 범위 기준선(`MILESTONE.md`)을 든다 —
current-status는 그 범위 표 밖의 항목을 순위에 올리지 않는다.

어느 단계에서든 조사가 필요하면 **`/research <질문>`**이 곁가지로 선다 — 출처 붙은
답을 `research/R-<slug>.md`에 남기고, 발견이 닿는 단계(방향이면 `/interview`, 설계
계약이면 `/make-design`, 구현 세부면 원래 단계)로 되돌아갈 명령을 제안한다.
결정은 하지 않는다.

## 검증

모든 `SKILL.md`의 패키지 내부 상대 링크와 런타임 교차 링크가 실제 파일을
가리키는지 확인한다:

```bash
python3 scripts/validate_skill_links.py
```

같은 검사는 push와 pull request마다 GitHub Actions에서도 실행된다.

## 라이선스

MIT (전체 레포 및 각 플러그인 폴더 동일)
