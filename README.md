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

## 설치

**Claude Code**

```
/plugin marketplace add jsj9346/agent-skills
/plugin install design-harness@agent-skills
```

**Codex CLI**

```
codex plugin marketplace add jsj9346/agent-skills
codex plugin add design-harness@agent-skills
```

## 포함된 스킬

| 스킬 | Claude Code | Codex CLI |
| --- | --- | --- |
| design-graph | ✅ | ✅ |
| design-harness | ✅ | ✅ |
| design-loop | ✅ | ✅ |
| documentize-context | ✅ | – |
| explain | ✅ | ✅ |
| interview | ✅ | ✅ |
| make-agents | ✅ | ✅ |
| milestone | ✅ | ✅ |
| review-harness | ✅ | ✅ |

## 라이선스

MIT (전체 레포 및 각 플러그인 폴더 동일)
