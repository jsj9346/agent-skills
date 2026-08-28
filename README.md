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
| [design-graph](plugins/design-graph) | 여러 실행 단위(Agent·Tool·Validator·스크립트·사람)를 연결해 파이프라인/멀티 에이전트 워크플로우 그래프를 설계 | ✅ | ✅ |
| [design-harness](plugins/design-harness) | 프로젝트 목적에 맞는 AI 작업 환경(하네스) — CLAUDE.md/AGENTS.md·커맨드·훅·검증 체계를 설계 | ✅ | ✅ |
| [design-loop](plugins/design-loop) | 목표 실행 루프(Observe→Decide→Act→Verify)를 설계해 복붙 가능한 `/goal` 명령어 한 줄로 압축 제안 | ✅ | ✅ |
| [documentize-context](plugins/documentize-context) | 세션의 맥락(목표·결정·피드백·워크플로우)을 재사용 가능한 마크다운 문서로 정리 | ✅ | – |
| [explain](plugins/explain) | 작업·문서·코드를 비개발자 눈높이로 쉽게 설명(읽기 전용, 대상 수정 없음) | ✅ | ✅ |
| [interview](plugins/interview) | 작업을 설계하기 전에 인터뷰 형식으로 "무엇을 왜 만들까"를 확정해 결정 기록으로 남김 | ✅ | ✅ |
| [make-agents](plugins/make-agents) | 프로젝트 목적에 맞는 서브에이전트/에이전트 팀을 설계·생성하고 스킬을 라우팅 | ✅ | ✅ |
| [milestone](plugins/milestone) | 프로젝트의 활성 마일스톤(하나)을 종료 조건 기준으로 설정·조회·종료 | ✅ | ✅ |
| [review-harness](plugins/review-harness) | 이미 구축된 AI 작업 환경의 중복 하네스·과최적화를 진단하고 걷어냄 | ✅ | ✅ |
| [verify](plugins/verify) | 작업물을 정본 문서에 대조해 독립 검증하고 판정 리포트 문서를 남김 | ✅ | ✅ |

## 라이선스

MIT (전체 레포 및 각 플러그인 폴더 동일)
