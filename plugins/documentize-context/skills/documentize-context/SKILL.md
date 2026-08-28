---
name: documentize-context
description: Document the context of a user–AI collaboration session into a structured, reusable markdown record. Use when the user asks to "documentize", capture, summarize-for-reuse, or export the conversation's context — goals, decisions, feedback, workflow, pitfalls — especially as groundwork for authoring a new skill from the session. Trigger phrases include "documentize-context", "이 대화 문서화해줘", "컨텍스트 문서로 남겨줘", "이 세션을 스킬로 만들 수 있게 정리해줘".
---

# documentize-context

Turn the current user–AI collaboration session into a durable context document.
The document's primary consumer is a **future skill author** (human or AI) who
was not present in this conversation — write for them, not for the participants.

## Why this exists

Valuable know-how emerges inside conversations: what the user actually wanted,
which approach worked, what the AI got wrong and how the user corrected it.
That knowledge evaporates when the session ends. This skill captures it in a
form structured enough to later be converted into a skill (`SKILL.md`).

## When to run

- The user explicitly asks to document/export the session context.
- A collaboration produced a repeatable workflow worth turning into a skill.
- Before ending a long session whose decisions would otherwise be lost.

Do NOT run for trivial Q&A sessions with no reusable process. If the session
contains nothing repeatable, say so instead of producing an empty document.

## Process

1. **Scan the full conversation**, oldest to newest. Collect:
   - The user's original goal, and how it evolved (goal drift is signal).
   - Constraints stated by the user (explicit) and discovered during work (implicit).
   - Every decision point: options considered, choice made, and *why*.
   - Every user correction or piece of feedback — these are the highest-value
     items. Record what the AI did, what the user said, and the corrected behavior.
   - The workflow that ultimately worked, as ordered steps.
   - Dead ends and pitfalls: what was tried and abandoned, and why.
   - Tools, commands, file paths, and external resources that were load-bearing.

2. **Distill, don't transcribe.** One decision = one entry. Drop small talk,
   retries with no lesson, and anything derivable from the artifacts themselves
   (code, commits). Keep the *why* — a decision without rationale is not reusable.

3. **Normalize for reuse:**
   - Convert relative dates ("yesterday", "next week") to absolute dates.
   - Replace session-specific values (usernames, one-off paths) with
     placeholders like `<project-root>` unless they are the point.
   - Never include secrets, tokens, API keys, or private personal data.
     If one appeared in the session, note "credential redacted" instead.

4. **Write the document** using the template below.
   - Default location: `docs/context/YYYY-MM-DD-<topic-slug>.md` under the
     current project. If there is no project (e.g., home directory), ask the
     user where to save, or use the path the user gave.
   - Output language: match the conversation's dominant language. Keep code,
     commands, and identifiers verbatim.

5. **Assess skill candidacy.** Fill the "Skill Candidate" section honestly:
   if the workflow is a one-off, say `verdict: not a skill` and why. If it is
   a candidate, the section must contain enough detail that a `SKILL.md`
   (name, description with trigger phrases, step-by-step instructions,
   verification) could be drafted from this document alone, without re-reading
   the original conversation.

6. **Report** the saved path and a 3–5 line summary of what was captured.

## Output template

```markdown
# Context: <topic>

- **Date:** YYYY-MM-DD
- **Participants:** user (<role if known>), AI (<tool/model>)
- **Session type:** <build | debug | design | research | ops | mixed>
- **Artifacts produced:** <files/repos/PRs, with paths or links>

## Objective
What the user set out to do, and how the goal evolved during the session.

## Constraints
- Explicit: stated by the user up front or along the way.
- Discovered: found during the work (environment limits, API quirks, etc.).

## Decisions
| # | Decision | Alternatives considered | Rationale |
|---|----------|------------------------|-----------|

## User feedback & corrections
For each: **What the AI did → What the user said → Corrected behavior → Why it matters.**
This section is the core training signal for a future skill. Do not summarize it away.

## Working workflow
The step sequence that actually worked, numbered, with the verification used
at each step (how did we know it worked?).

## Pitfalls & dead ends
What was tried and abandoned, and the reason — so a future run skips them.

## Load-bearing resources
Tools, commands, files, URLs, docs that the workflow depends on.

## Skill candidate
- **Verdict:** <skill-worthy | not a skill> — <one-line reason>
- **Proposed name:** <kebab-case>
- **Trigger (description draft):** when should an agent invoke this?
- **Inputs:** what the skill needs from the user or environment.
- **Steps:** condensed from "Working workflow", generalized.
- **Verification:** how the skill knows it succeeded.
- **Open questions:** what this session did NOT settle.
```

## Rules

- Facts over narrative: every claim in the document must be traceable to
  something that actually happened in the session. Do not invent rationale.
- If the conversation was summarized/compacted and details are missing, mark
  gaps explicitly as `[not recoverable from context]` rather than guessing.
- The document must stand alone: a reader with zero access to the original
  conversation must be able to reproduce the workflow and draft the skill.
