# Review UI Report — <target>

- Status: **in-progress** <!-- complete | blocked -->
- Date: YYYY-MM-DD
- Target: <route or component>
- Mode: <Audit | Repair>
- Baseline HEAD: <commit hash or not-applicable>
- Design authorities: <paths and sections, or none found>
- Report path: `reports/YYYYMMDD-review-ui-<target>.md`

## Authority conflicts and assumptions

- Authority conflict: <sources, conflict, and impact, or none>
- Heuristic-only areas: <areas without a design authority, or none>
- Design decisions required: <finding IDs or none>

## Execution

- App command: <command>
- Review command or method: <command/tool>
- Automated checks: <command and result, or not run with reason>
- Browser/render result: <rendered | blocked>

## Review matrix

| Route or component | Viewport | UI state | Result | Evidence |
|---|---|---|---|---|
| <target> | <width × height> | <default/loading/empty/error/disabled/interaction> | <reviewed/unverified> | <screenshot path or blocker> |

## Finding summary

| blocker | major | moderate | minor | Total open | fixed | design-decision-required | unverified |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Allowed severity values: `blocker`, `major`, `moderate`, `minor`.

Allowed status values: `open`, `fixed`, `design-decision-required`, `unverified`.

## Findings

### UI-### — <short title>

- id: `UI-###`
- severity: <blocker | major | moderate | minor>
- location: <route/component + viewport + UI state>
- expected: <authority source or `heuristic`>
- actual: <observed behavior>
- evidence: <screenshot path and reproduction steps>
- impact: <user-visible consequence>
- suggested_fix: <concise direction>
- status: <open | fixed | design-decision-required | unverified>

<!-- Repeat the complete nine-field block for every finding. If there are no findings after a
successful real render, replace this sample with "None" and retain the reviewed matrix evidence. -->

## Before evidence

| Route or component | Viewport | UI state | Screenshot | Reproduction |
|---|---|---|---|---|
| <target> | <width × height> | <state> | <path> | <steps> |

## Repair record

<!-- For Audit, write "Not applicable — Audit made no product-source or design-authority changes." -->

- Findings frozen before edits: <IDs and report revision/time>
- Changed files: <paths or none>
- Automated checks after repair: <command and result>

### After evidence and recheck

| Finding | Route or component | Same viewport | Same UI state | After screenshot | Recheck result |
|---|---|---|---|---|---|
| UI-### | <target> | <width × height> | <state> | <path> | <fixed/unverified/open> |

## Source and authority integrity

- Audit source comparison: <unchanged with diff/hash evidence | not applicable in Repair>
- Audit design-authority comparison: <unchanged with diff/hash evidence | not applicable in Repair>
- Repair left design-decision-required findings unchanged: <IDs or not applicable>

## Unreviewed scope

| Route or component | Viewport | UI state | Reason |
|---|---|---|---|
| <scope or none> | <viewport> | <state> | <reason> |

## Blocked closeout

<!-- Use this section and set Status to blocked when the app or browser cannot render. Do not claim
Visual QA passed or "no findings". -->

- Failed command or step: <command/step>
- Failure log: <path or concise output>
- Last confirmed point: <what was verified before the blocker>
- Required input or environment action: <action>
- Automated checks completed: <command and result>
- Unverified route/viewport/state combinations: <matrix rows and reasons>

## Final outcome

- Decision: <complete Audit | complete Repair | blocked>
- Remaining findings: <IDs by status, or none>
- Product source changes: <none for Audit | paths for Repair>
- Design authority changes: <none; review does not decide new visual rules>
- Unreviewed scope: <summary or none>
