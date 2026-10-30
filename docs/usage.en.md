# Using Reading Companion

Provide a source file or excerpt, then state your **goal, scope, and mode**. The assistant needs access to the relevant source before explaining it or checking its claims.

| Mode | Result |
|---|---|
| `deep` | Meaning, necessary background, and argument; standard style ends with one question and waits for your response. |
| `extract` | Source-linked knowledge units with conditions and exceptions; no quiz or assessment of understanding. |
| `combined` | Deep explanation plus complementary units using shared IDs; standard style keeps the one-question waiting point. |

## Recommended starting prompt

Attach the source, then send:

> Use Reading Companion in **combined** mode, **standard** style. My goal is to understand why the author concludes [X] and retain knowledge for [Y]. Scope: [section/pages/pasted passage]. Start with one meaningful passage. Explain the necessary background and premises → conclusion, preserving conditions and exceptions. Add source-linked units without repeating the explanation. Distinguish the author's statements, interpretation, and AI-created examples. End with one question, without its answer, and wait for me.

For extraction only:

> Use **extract** mode for [goal], limited to [scope] in this source. Preserve source locations, conditions, exceptions, and unknowns. No quiz. Let meaningful content determine the number of units. Report processed coverage and source gaps.

Quick, chill, and challenger are styles; they do not change the mode. Extract never adds a quiz. Time-sensitive claims being explained or applied receive a current-source check when suitable tools and sources are available; book claims, check dates, scope, and unresolved gaps remain visible.

## Check claim support with CiteGuard

You do not need to memorize CE codes. Supply the claims and the actual document:

> Apply CiteGuard's claim–source workflow to claims [C1…] using **the document I provided**, within [scope]. Read the relevant passages and context. Return a table with each claim, source/location, short evidence excerpt, support level, critical conditions, interpretation/assumptions, and unknowns. Distinguish supported, partially supported, unsupported, and unresolved. Missing access does not mean a claim is false. Do not search outside the document in this turn. Apply the findings to [explanation/unit table], then review the final result against the source. Preserve the current mode, pending question, and learning support history. State what can be used and what remains unresolved.

This checks support within the supplied source. Verifying truth beyond it is a separate task. Claim support differs from hints or worked examples received during learning. For an advanced review record, add: “Produce **G-CITATION-REVIEW** with evidence for CR01–CR06 and unchecked gaps; distinguish AI self-review from independent review.”

## Audit evidence for a project

This is a separate route when you ask to find/select/compare/hand off project evidence; it does not run during ordinary book reading. The 0.3.8 helper renders a required block from the audit record, while a reviewer still judges the meaning and basis of the stop reason. See the [full guide](project-evidence.en.md).

## Reading controls and continuity

| Request | Behavior |
|---|---|
| `Next` | Move using a verified chapter index; pause an unanswered question with its context and support history. |
| `Back` | Return using actual navigation history. |
| `Pause; keep this question` | Preserve the question, position, resume note, and support already received. |
| `Resume the paused question` | Restore its context without automatically grading it or reducing recorded support. |
| `Progress` | Read actual state: position, processed coverage, pending/paused questions, gaps, and next step. |

Opening a chapter does not mark it complete. Creating cards does not demonstrate understanding. Without an accessible state snapshot or handoff, progress and pending questions remain unknown. Missing index/history is not a basis for inventing a next chapter.

Before leaving, request a portable handoff:

> Prepare a handoff with goal, mode/style/scope, source identity/version/hash when available, unit IDs/revisions, position, coverage, assessments based on real responses, pending/paused questions, support history, gaps, and next step. List files actually saved. Include existing evidence, argument, example, question-criterion, and currency-comparison sidecars; keep pending-question answers and grading criteria outside the learner-visible handoff. If no files were saved, provide the handoff in chat and say so.

In the next chat, supply the source, handoff, and sidecars:

> Resume from this package. Check source identity and revisions first. Preserve mode, pending/paused questions, and support history. Do not invent progress. Identify missing inputs, then continue at [position/question].

There is no implicit account memory. A summary cannot replace the source for new content, and checkpoint export does not automatically include every sidecar. Source changes require comparison/reimport before related state updates. The research action name `search_text_snippet` does not install a search tool; the workflow uses tools actually available or searches the supplied file. Saving updated source or a release does not prove the host has activated it.

Runtime contracts: [controller](../skills/sid-reading-companion/references/master-instruction.md), [modes, state, and handoff](../skills/sid-reading-companion/references/reading-protocols.md), [citation/evidence](../skills/sid-reading-companion/references/citation-evidence.md), [sidecars](../skills/sid-reading-companion/references/stack-contracts.md).

## Technical checks with a repository checkout

New reviews use complete SC05 JSON sidecars bound to artifact/hash/revision. Structural validation does not check meaning. Development tools are not automatically available on the host. [0.3.7 synchronization record](citeguard/correction-plan.md).
