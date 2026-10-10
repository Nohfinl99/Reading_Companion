# Principle Map and Rule Ownership

[Tiếng Việt](principles.vi.md) · [README](../README.md)

This page explains the main operating principles and links to the files that own each rule. It does not create a new runtime contract or taxonomy. If documentation differs, the canonical files under `skills/sid-reading-companion/references/` take precedence.

| Principle | Product meaning | Primary owner | Observable evidence |
|---|---|---|---|
| Source and scope bound claims | Do not infer inaccessible content; preserve source, revision, scope, locator and gaps | [M01–M02](../skills/sid-reading-companion/references/master-instruction.md), [KC01](../skills/sid-reading-companion/references/knowledge-compiler.md), [SC00](../skills/sid-reading-companion/references/stack-contracts.md) | SourceManifest, accessed/analyzed/missing ranges, source spans |
| Route by user goal | Call only the stack or stacks needed; do not force every turn through one pipeline | [M03–M04](../skills/sid-reading-companion/references/master-instruction.md) | Trigger → primary path → required sections |
| Mode is separate from style | `deep`, `extract`, `combined` identify the task; style changes presentation only | [M04](../skills/sid-reading-companion/references/master-instruction.md), [R10](../skills/sid-reading-companion/references/reading-protocols.md) | Frame/session store mode and style separately |
| Units follow scope and content | Do not impose one fixed Knowledge Unit count across books or tasks | [KC02](../skills/sid-reading-companion/references/knowledge-compiler.md) | Unit boundaries, locators, coverage, merges and unprocessed scope |
| Lists carry provenance | Each subset identifies selector, known universe, criterion, sources and excluded/unreviewed items | [SC01](../skills/sid-reading-companion/references/stack-contracts.md) | SelectionRecord and visible explanation beside the list |
| Arguments and examples retain their bridge | Examples point to real units/arguments, explain corresponding conditions and limit conclusions | [SC02–SC03](../skills/sid-reading-companion/references/stack-contracts.md), [R13](../skills/sid-reading-companion/references/reading-protocols.md) | ArgumentRecord, ExampleLink and a visible learner bridge |
| Learning state comes from real events | Do not fabricate or upgrade a pending question, response, support or assessment | [SC00/SC04](../skills/sid-reading-companion/references/stack-contracts.md), [R04/R10–R12](../skills/sid-reading-companion/references/reading-protocols.md) | Real response, support, pending/paused question and checkpoint revision |
| Gates are evidence-bound | A structural pass does not substitute for semantic review, host tests or learner results | [M05/M07](../skills/sid-reading-companion/references/master-instruction.md), [R14](../skills/sid-reading-companion/references/reading-protocols.md), [B01](../skills/sid-reading-companion/references/case-benchmark.md) | GateRecord status and evidence spans by layer |

## Explaining selections

When AI selects items from a larger set, state the purpose, scope, criterion, selector and what was excluded or left unchecked. A number in a heading does not prove the author specified that count. Preserve author-stated counts with a supporting locator and distinguish them from the number of items AI chose to present.

For a new example, add a nearby bridge that explains which unit it illustrates, where it connects to the argument, which conditions are preserved or changed and what it does not establish. Label AI-created examples; do not attribute a hypothetical scenario to the author.

## Source and interpretation labels

- `source_explicit`: stated directly by the source.
- `source_interpretation`: a supported reading, but not the author's exact statement or label.
- `pedagogical_proposal`: an organization, example or learning aid proposed by the Companion.
- `unresolved`: evidence is insufficient to make the claim.

These are provenance categories in the contract, not a learner-scoring taxonomy. See exact fields and valid values in [SC02–SC03](../skills/sid-reading-companion/references/stack-contracts.md).

## Current evidence boundary

CI checks packaging and helpers. It does not validate every book interpretation. The benchmark defines cases and required evidence; a case can be reported as passed only when it has actual input, output and grading results. See the [quality guide](quality.en.md) and [benchmark specification](../skills/sid-reading-companion/references/case-benchmark.md).
