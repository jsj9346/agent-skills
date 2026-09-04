# UI Spec — <stable title>

- ID: `<stable-slug>`
- Status: `<draft | needs-input | reference-blocked | design-conflict | ready-for-build>`
- Intent: `<define | extend | revise>`
- Target:
  - kind: `<route | component | screen-set | new-app>`
  - key: `<canonical key>`
- Goal: <user-visible outcome>
- Users: <relevant users or roles>

<!--
Target identity is the case-sensitive canonical (kind, key), not this file path, ID, title,
date, mtime, or target-slug. Component keys use global:project or a route/screen-set/new-app
owner plus a lowercase-kebab component slug; never use a module/export path.
-->

## Authority

1. <user requirement and approved scope>
2. <project instruction>
3. <selected target UI spec, if revising>
4. <DESIGN.md or equivalent>
5. <tokens and shared component contract>
6. <repeated existing UI pattern>
7. <accessible reference>
8. <heuristic, only where higher authority is silent>

### Conflicts

- <sources, conflict, impact, and required decision, or none>

## Scope

### Included

- <behavior, screen, or region>

### Non-goals

- <excluded behavior, screen, or region>

## Screen inventory

### <stable screen or region name>

- Purpose: <user task served>
- Content hierarchy:
  1. <content or action>
- States:
  - default: <observable state>
  - loading: <observable state or not applicable with reason>
  - empty: <observable state or not applicable with reason>
  - error: <observable state or not applicable with reason>
  - disabled: <observable state or not applicable with reason>
  - permission: <observable state or not applicable with reason>
  - domain-specific: <state or none>
- Interactions:
  - <trigger> → <visible response>
- Accessibility expectations:
  - Keyboard: <expectation>
  - Focus: <expectation>
  - Semantics: <expectation>
  - Contrast: <expectation>

## User flows

### <stable flow name>

1. <starting condition and screen/state>
2. <user action and visible response>
3. <success or failure ending and screen/state>

## Component reuse

| Element | Decision | Existing contract or required boundary | Reason |
|---|---|---|---|
| <element> | <reuse | extend | new> | <component/token contract; no implementation path> | <reason> |

## Responsive rules

| Viewport or condition | Information priority | Reflow or substitution | Observable behavior |
|---|---|---|---|
| <condition> | <priority> | <layout/action change> | <expected result> |

## Acceptance checks

<!--
Only these pairs are valid:
- owner: codex + evidence: render
- owner: codex + evidence: automated-check
- owner: user + evidence: user-decision
-->

### UI-AC-001 — <observable outcome>

- Scenario: <reproducible user action>
- Viewport or condition: <observable condition>
- Expected: <observable result>
- Owner: `<codex | user>`
- Evidence: `<render | automated-check | user-decision>`

## Unresolved decisions

<!-- ready-for-build requires the exact value "None" and an empty unresolved list. -->

- <decision, affected known screens/flows, and required input, or None>

## Failure context

<!--
Draft and ready-for-build: write "Absent" and do not retain a failure object.
Needs-input: unresolved must be non-empty; phase NeedsInput; last DefinitionDrafting;
resume DecisionCheck; KnownAffectedScope only.
Reference-blocked: phase ReferenceBlocked; last Intake; resume AuthorityReady;
KnownAffectedScope or UnknownTargetScope is allowed.
Design-conflict: unresolved must be non-empty; use one exact variant:
- during drafting: last AuthorityReady; resume DefinitionDrafting
- during decision check: last DefinitionDrafting; resume DecisionCheck
Both design-conflict variants require KnownAffectedScope.
-->

- Variant: <Absent | NeedsInputFailure | ReferenceBlockedFailure | DesignConflictDuringDrafting | DesignConflictDuringDecisionCheck>
- Cause: <visible reason or not applicable>
- Required input: <concrete input or not applicable>
- Affected scope:
  - Kind: <KnownAffectedScope | UnknownTargetScope | not applicable>
  - Screens or flows: <non-empty stable names when known>
  - Target: <canonical kind and key when unknown>
  - Unknown reason: <why names require the blocked primary reference>
- Resume condition: <observable condition or not applicable>
- Last completed phase: <Intake | AuthorityReady | DefinitionDrafting | not applicable>
- Resume at: <AuthorityReady | DefinitionDrafting | DecisionCheck | not applicable>

## Handoff

- Product design authority changed: <no | path, reusable rule, scope, and reason>
- Codex-owned checks: <UI-AC IDs>
- User-owned checks: <UI-AC IDs>
- Remaining unresolved: <none or IDs>
- Next implementation request: `$design-ui <this UI spec path>`
