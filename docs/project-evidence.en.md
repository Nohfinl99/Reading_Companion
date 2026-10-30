# Project source evidence guide

**Use this guide when a user asks to find, compare or hand off evidence for a project.** This is not a checkpoint or retrieval engine. An additive audit profile outside learner state is documented in the [runtime reference](../skills/sid-reading-companion/references/project-evidence.md) and [SC00–SC01 owner](../skills/sid-reading-companion/references/stack-contracts.md); the packaged helper checks structure/freshness and renders the mandatory visible block, but does not verify semantic truth. Use only the source root, component, revision and access scope provided. If authority or revision is unclear, keep the conclusion unresolved and use only independently verifiable material.

## Canonical contracts

- [KC01](../skills/sid-reading-companion/references/knowledge-compiler.md) owns the source/task frame, actual access, locators and gaps.
- [SC00](../skills/sid-reading-companion/references/stack-contracts.md) owns the envelope, provenance, persistence boundary and state handoff; [SC01](../skills/sid-reading-companion/references/stack-contracts.md) owns selection criteria, exclusions and completeness within verified scope.
- [CE02 and CE04](../skills/sid-reading-companion/references/citation-evidence.md) handle source spans and claim support. A relevant citation may not support a claim; missing access does not prove a claim false. Keep unresolved contradictions visible.
- [R12 and R14](../skills/sid-reading-companion/references/reading-protocols.md) own continuity handoff and validation. Progress reads state; evidence handoff is a separate operation.

## Workflow

Use each phase's artifact as the next phase's context. Each phase has one cognitive task. Record decision facts and checkable locators, not private chain-of-thought. If the request is Progress only, stop after the read-only state check; do not invoke the compiler or CE. For a combined Progress and handoff request, report state first, then separately pass along evidence already available; do not infer reading state from external evidence.

### Stack A — Select sources and establish authority

| Phase | RTC-COE |
|---|---|
| A1 — Source admission | **Role:** source reviewer. **Task:** identify the source root/component and material authorized for the objective. **Context:** the exact request, available source roots, KC01/SC00 and actual access. **Constraints:** filename, modification time or a newer revision does not establish authority; snapshot hash/date identify the bytes or time of the snapshot read, not the implementation revision or current runtime; keep authority basis and scope distinct; do not expand access. If implementation revision/runtime is not source-confirmed, record unknown/not verified. **Output:** in the visible handoff, separate `Source snapshot identity` (path, hash, observed document date/version) from `Implementation revision/current runtime` (value with direct evidence, or unknown/not verified); include access/missing ranges. **Evaluation/stop:** R14 G-SOURCE; check that recipients see the two distinct items when an authority/revision claim is handed off; if authority or a source is missing, stop that dependency, keep it unresolved and continue independent work. |

### Stack B — Select evidence and handle corrections

| Phase | RTC-COE |
|---|---|
| B1 — Selection | **Role:** evidence selector. **Task:** select candidate spans for a fixed objective. **Context:** A1 output, verified source universe, CE02 and SC01. **Constraints:** state the criterion before concluding; distinguish relevance from support; list included, excluded and not examined material; completeness applies only within verified scope. **Output:** the visible answer/handoff must state the criterion, included/excluded/not examined items, searched boundary and an evidence-backed reason for stopping (for example, direct evidence for the objective was found, a budget cap was reached or an access gap blocked further search). Do not leave the boundary/reason only in a SelectionRecord or sidecar. Add the claim/source-locator/basis table and a SelectionRecord when needed under SC01. **Evaluation/stop:** inspect what the recipient actually sees for both boundary and stop reason; if universe or locators are missing, mark PARTIAL/unknown and make no whole-corpus claim. |
| B2 — Correction | **Role:** claim reviewer. **Task:** determine which claim/scope a correction or supersession applies to. **Context:** B1, earlier/later sources, correction locator and CE04. **Constraints:** a later date does not replace an earlier source by itself; change only the claim and scope explicitly covered by the correction; do not transfer one component's status to another; retain remaining contradictions. **Output:** before/after claim, source-supported relation, locator, conditions and remaining gaps. **Evaluation/stop:** if the relation or scope lacks support, mark unresolved; do not say the whole system was fixed. |

### Stack C — Keep evidence layers distinct and hand off

| Phase | RTC-COE |
|---|---|
| C1 — Evidence layer | **Role:** evidence-layer reviewer. **Task:** assign each result to its actual layer and scope. **Context:** claim/evidence table, conditions and project outputs. **Constraints:** separate offline, device, product pilot and project/global gate; a result in one layer does not promote another. **Output:** scoped conclusion, observed status, conditions/gaps and NOT_RUN areas. **Evaluation/stop:** without evidence from the relevant layer, do not claim acceptance at that layer. |
| C2 — Handoff | **Role:** continuity editor. **Task:** hand off a re-checkable evidence artifact. **Context:** SC00/R12, source/access/hash/revision, claims/locators, gaps and supplied consumer acceptance criteria. **Constraints:** name the next owner; consumer ACK/acceptance stays unknown without a record; do not invent persisted state, admission, checkpoint or restored new chat. If source hash/revision changes, stop dependent reuse and request comparison; preserve Q/support from any available reading snapshot without erasing or lowering support. If the snapshot is missing, state is unknown. **Output:** the template below, with actual refs/sidecars when available. **Evaluation/stop:** R14 G-HANDOFF; without consumer acknowledgement, do not mark accepted/admitted. |

### Stack D — Review coverage and build a backlog

| Phase | RTC-COE |
|---|---|
| D1 — Evidence inventory | **Role:** evidence librarian. **Task:** classify actual evidence by layer. **Context:** artifacts/outputs/revisions from A–C and available review records. **Constraints:** separate design/case, mechanical, model, semantic review, host/device, independent and learner evidence; do not count fixtures as runs. **Output:** known/unknown coverage with locator and layer; missing records are NOT_RUN. **Evaluation/stop:** classify only artifacts that exist; infer no performance. |
| D2 — Backlog | **Role:** priority planner. **Task:** order unanswered questions by prerequisite and owner. **Context:** D1, impact/scope and sources or environment needed to close each gap. **Constraints:** set no reliability threshold; do not replace host/learner tests with instructions or synthetic cases. **Output:** backlog with gap, evidence needed, prerequisite, owner and expected layer. **Evaluation/stop:** defer items that need unavailable sources/environment; do not claim completion. |
| D3 — Coverage review | **Role:** evidence reviewer. **Task:** state the coverage that can be reported. **Context:** backlog, actual records, revisions and checks run. **Constraints:** self-review is not independent; do not combine PASS across layers; fixture scope does not expand to corpus/project scope. **Output:** coverage statement, checks/NOT_RUN and unresolved gaps. **Evaluation/stop:** conclude only for evidenced scope/layer; keep other areas unknown. |

## Short claim and handoff template

```text
Objective:
Scope: source root | component | authority basis | access
Source snapshot identity: path | SHA-256 | document date/version (observed or unknown)
Implementation revision/current runtime: value + direct evidence locator, or unknown/not verified
Selection: criterion | included refs | excluded/not examined | verified universe | stop reason
Claims:
- Claim and condition:
  Evidence locator/hash:
  Claim support (supported / partial / unsupported / unresolved):
  Epistemic basis (Fact / Interpretation / Assumption / Hypothesis / Recommendation):
  Evidence layer and scope:
  Gap / NOT_RUN:
Correction/supersession: affected claim/scope | basis/locator | unresolved relation
Next owner:
Consumer prerequisites/acceptance criteria:
Consumer ACK: unknown unless an acknowledgement record is present
State/persistence: unknown unless an actual snapshot/record is supplied
```

This audit/handoff sits outside the reading checkpoint. When using the helper, create a 0.3.8 audit record and render its mandatory block; do not replace the block with separate prose. An R14 reviewer judges stop-reason and claim meaning with a separate record bound to exact hashes. Do not put evaluator criteria or answers in learner-visible handoff while a question is pending. Do not add fields to checkpoint, reading-session, unit or pending-question schemas.

## Evidence backlog and review layers

Keep a backlog separate from reading content: unanswered question, needed source/scope, owner, prerequisite and the evidence layer that would resolve it. Track **design/case specification**, **mechanical validation**, **model output**, **semantic review**, **installed-host/device**, **independent review** and **learner outcome** separately. Do not count fixtures or self-review as independent runs; record unrun work as `NOT_RUN`. Do not infer accuracy/reliability from case counts. Advance backlog items only with an actual artifact, revision and evidence scope appropriate to the question.

## Tools and limits

A file browser/terminal and the `project_evidence.py` helper can check the exported bundle's path allowlist, structure, locators and SHA-256. These are mechanical checks; they do not establish rights, authority, claim support, stop-reason sufficiency, consumer ACK or project acceptance. The helper does not sandbox the agent's other tools or filesystem access. State what was not accessed or checked and do not promote a mechanical PASS.
