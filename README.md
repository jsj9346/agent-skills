# documentize-context

An [Agent Skill](https://agentskills.io) that documents the context of a user–AI
collaboration session into a structured, reusable markdown record — so the
session's decisions, feedback, and workflow can later be turned into a new skill.

유저와 AI가 협업한 대화의 컨텍스트(목표·결정·피드백·워크플로우·실패 경로)를
구조화된 문서로 남기는 스킬입니다. 이 문서를 토대로 새로운 스킬(`SKILL.md`)을
만들 수 있도록 설계되었습니다.

Works with both **Claude Code** and **Codex** — both support the open
`SKILL.md` agent-skills format.

## What it produces

A standalone markdown document (default: `docs/context/YYYY-MM-DD-<topic>.md`)
containing:

- **Objective** — what the user set out to do, and how the goal evolved
- **Constraints** — explicit and discovered
- **Decisions** — with alternatives considered and rationale
- **User feedback & corrections** — the highest-value signal for skill authoring
- **Working workflow** — the step sequence that actually worked, with verification
- **Pitfalls & dead ends** — so a future run skips them
- **Skill candidate** — an honest verdict plus a draft (name, trigger,
  inputs, steps, verification) detailed enough to write a `SKILL.md` from

## Install

### Claude Code

```bash
git clone https://github.com/jsj9346/documentize-context.git \
  ~/.claude/skills/documentize-context
```

Or per-project: clone into `<project>/.claude/skills/documentize-context`.

### Codex

```bash
git clone https://github.com/jsj9346/documentize-context.git \
  ~/.codex/skills/documentize-context
```

Or per-project: clone into `<project>/.codex/skills/documentize-context`.

## Usage

Ask your agent, in any language:

- `/documentize-context`
- "이 대화 문서화해줘" / "이 세션을 스킬로 만들 수 있게 정리해줘"
- "Documentize this session so we can turn it into a skill"

The agent scans the conversation, distills it into the template, saves the
document, and reports the path with a short summary. The output language
follows the conversation's dominant language.

## Notes

- Secrets/tokens that appeared in the session are never written to the
  document (recorded as "credential redacted").
- If a session has nothing repeatable, the skill says so instead of producing
  an empty document.

## License

[MIT](LICENSE)
