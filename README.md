# agent-skills

jsj9346의 에이전트 스킬 모음. **Claude Code**와 **Codex CLI**의 공식 플러그인
마켓플레이스 메커니즘을 이 레포 하나로 서빙하며, 스킬에 따라 양쪽 변형판 또는 한
런타임 전용판을 제공합니다.

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

먼저 이 레포를 마켓플레이스로 등록한 뒤 필요한 플러그인을 설치합니다.

**Claude Code**

```text
/plugin marketplace add jsj9346/agent-skills
/plugin install design-harness@jsj9346-skills
```

**Codex CLI**

```text
codex plugin marketplace add jsj9346/agent-skills
codex plugin add design-harness@jsj9346-skills
```

UI 작업용 Codex 전용 플러그인은 다음처럼 설치합니다.

```text
codex plugin add design-ui@jsj9346-skills
```

## 플러그인 카탈로그

### Claude Code와 Codex 공용

| 플러그인 | 설명 |
| --- | --- |
| [current-status](plugins/current-status) | 원장·기록·실물을 교차 검증해 현황을 판정하고 우선순위와 다음 명령을 제안 |
| [design-graph](plugins/design-graph) | Agent·Tool·Validator·사람을 연결하는 파이프라인과 워크플로 그래프를 설계 |
| [design-harness](plugins/design-harness) | 프로젝트 목적에 맞는 AI 작업 환경과 검증 체계를 설계 |
| [design-loop](plugins/design-loop) | Observe→Decide→Act→Verify 목표 루프를 설계해 실행 명령으로 압축 |
| [documentize-context](plugins/documentize-context) | 세션의 목표·결정·피드백·워크플로를 재사용 가능한 문서로 정리 |
| [execute](plugins/execute) | 확정된 플랜을 구현·검증하고 실행 리포트와 커밋으로 마무리 |
| [explain](plugins/explain) | 작업·문서·코드를 비개발자 눈높이로 설명하는 읽기 전용 스킬 |
| [interview](plugins/interview) | 설계 전에 무엇을 왜 만들지 인터뷰하고 결정 기록으로 확정 |
| [make-agents](plugins/make-agents) | 프로젝트에 맞는 서브에이전트 팀을 설계하고 스킬 호출을 라우팅 |
| [make-design](plugins/make-design) | 결정 기록이나 미결 항목을 경계와 계약이 명확한 설계 문서로 확정 |
| [make-plan](plugins/make-plan) | 설계 문서를 검증 조건·의존성·롤백이 포함된 실행 플랜으로 변환 |
| [milestone](plugins/milestone) | 명령으로 측정 가능한 종료 조건을 기준으로 활성 마일스톤을 관리 |
| [research](plugins/research) | 작업 중 생긴 질문을 출처가 포함된 조사 노트로 정리 |
| [review-harness](plugins/review-harness) | 기존 AI 작업 환경의 중복과 과최적화를 진단·정리 |
| [verify](plugins/verify) | 작업물을 정본 계약과 대조해 독립 판정 리포트를 작성 |

### Codex 전용

| 플러그인 | 포함 스킬 | 설명 |
| --- | --- | --- |
| [design-ui](codex-plugins/design-ui) | `define-ui`, `design-ui`, `review-ui` | 구현 전 UI 정의부터 코드 구현, 실제 렌더링 검토까지 연결하는 UI 워크플로 |

## UI 디자인 워크플로 (Codex)

`design-ui` 플러그인은 역할이 분리된 세 스킬을 제공합니다.

```text
요구사항
  ↓
define-ui     화면·흐름·상태·반응형 규칙과 완료 기준 정의 (선택)
  ↓
design-ui     실제 UI 코드 구현 + 제작자 Visual QA
  ↓
review-ui     독립 Audit, 명시적으로 요청된 경우 Repair
  ↓
사용자 승인·공개
```

- `$define-ui`: 구현 전에 target별 `ready-for-build` UI 명세가 필요할 때 사용합니다.
- `$design-ui`: 새 UI 제작, 재설계, 확장 또는 참고물의 프론트엔드 코드 번역에 사용합니다.
- `$review-ui`: 구현 결과를 독립적으로 검토합니다. 기본 Audit은 제품 소스를 수정하지 않습니다.

자세한 사용법과 예시는 [design-ui 플러그인 문서](codex-plugins/design-ui)를 참고하세요.

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
